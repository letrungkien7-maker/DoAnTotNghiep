from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.chat import ChatMessage, ChatSender, ChatSession
from app.models.listing import Listing, ListingFeature, ListingStatus, TransactionType
from app.models.user import User
from app.schemas.chat import ExtractedCriteria, SendMessageRequest
from app.services.chatbot_llm import ChatbotLLM
from app.services.chatbot_service import ChatbotService
from app.services.vietnamese_nlp import VietnameseEntityExtractor


# ---------------------------------------------------------
# 1. NLP Entity Extraction & Intent Tests
# ---------------------------------------------------------

def test_nlp_intent_detection():
    # Out of scope
    intent_weather = VietnameseEntityExtractor.detect_intent("Thời tiết hôm nay thế nào bạn?")
    assert intent_weather.intent_type == "OUT_OF_SCOPE"

    intent_cooking = VietnameseEntityExtractor.detect_intent("Hướng dẫn tôi cách nấu ăn")
    assert intent_cooking.intent_type == "OUT_OF_SCOPE"

    # General greeting
    intent_hello = VietnameseEntityExtractor.detect_intent("Xin chào")
    assert intent_hello.intent_type == "GENERAL_INQUIRY"

    intent_hi = VietnameseEntityExtractor.detect_intent("chào bạn")
    assert intent_hi.intent_type == "GENERAL_INQUIRY"

    # Search listings
    intent_search = VietnameseEntityExtractor.detect_intent("Tìm mua chung cư 2 phòng ngủ tại Cầu Giấy")
    assert intent_search.intent_type == "SEARCH_LISTINGS"


def test_nlp_criteria_extraction_sale():
    text = "Tìm mua căn hộ 2pn tại Nam Từ Liêm dưới 3.5 tỷ full nội thất có thang máy"
    criteria = VietnameseEntityExtractor.extract_criteria(text)

    assert criteria.transaction_type == "SALE"
    assert criteria.category_id == 1  # Căn hộ chung cư
    assert criteria.province == "Hà Nội"
    assert criteria.district == "Nam Từ Liêm"
    assert criteria.bedrooms == 2
    assert criteria.budget_max is not None
    assert 3_400_000_000 <= criteria.budget_max <= 3_700_000_000
    assert "Nội thất đầy đủ" in criteria.features
    assert "Thang máy" in criteria.features


def test_nlp_criteria_extraction_rent():
    text = "Cần thuê nhà riêng tại Quận 1 từ 15 đến 20 triệu có gara ô tô"
    criteria = VietnameseEntityExtractor.extract_criteria(text)

    assert criteria.transaction_type == "RENT"
    assert criteria.category_id == 2  # Nhà riêng
    assert criteria.province == "Hồ Chí Minh"
    assert criteria.district == "Quận 1"
    assert criteria.budget_min == 15_000_000
    assert criteria.budget_max == 20_000_000
    assert "Gara ô tô" in criteria.features


def test_nlp_criteria_extraction_compound_price():
    # "3 tỷ 5"
    text1 = "tìm nhà 3 tỷ 5"
    crit1 = VietnameseEntityExtractor.extract_criteria(text1)
    assert crit1.budget_min is not None or crit1.budget_max is not None

    # "dưới 4 tỷ"
    text2 = "căn hộ dưới 4 tỷ"
    crit2 = VietnameseEntityExtractor.extract_criteria(text2)
    assert crit2.budget_max == 4_000_000_000


def test_nlp_underspecified_detection():
    vague_crit = VietnameseEntityExtractor.extract_criteria("tôi muốn mua nhà")
    assert VietnameseEntityExtractor.is_underspecified(vague_crit) is True

    specific_crit = VietnameseEntityExtractor.extract_criteria("căn hộ 2pn Nam Từ Liêm dưới 3 tỷ")
    assert VietnameseEntityExtractor.is_underspecified(specific_crit) is False


# ---------------------------------------------------------
# 2. LLM Groundedness & Anti-Hallucination Tests
# ---------------------------------------------------------

def test_llm_clarification_prompt():
    llm = ChatbotLLM()
    crit = ExtractedCriteria(transaction_type="SALE")
    prompt = llm.generate_clarification_prompt(crit)
    assert "bất động sản" in prompt.lower()
    assert "khu vực mong muốn" in prompt.lower() or "ngân sách" in prompt.lower()


def test_llm_out_of_scope_reply():
    llm = ChatbotLLM()
    reply = llm.generate_out_of_scope_reply()
    assert "BDS Smart" in reply
    assert "bất động sản" in reply


def test_llm_zero_result_reply():
    llm = ChatbotLLM()
    crit = ExtractedCriteria(
        province="Hà Nội",
        district="Cầu Giấy",
        budget_max=1_000_000_000,
    )
    reply = llm.generate_grounded_reply("tìm nhà 1 tỷ Cầu Giấy", crit, listings=[])
    assert "chưa có bất động sản nào" in reply.lower() or "chưa tìm thấy" in reply.lower() or "không tìm thấy" in reply.lower()
    assert "Cầu Giấy" in reply


# ---------------------------------------------------------
# 3. ChatbotService Multi-Turn Memory & Tool Calling Tests
# ---------------------------------------------------------

def test_chatbot_service_multi_turn_accumulation(db_session: Session):
    service = ChatbotService(db_session)

    # Turn 1: Specify location
    req1 = SendMessageRequest(message="Tôi muốn tìm mua căn hộ ở Nam Từ Liêm")
    res1 = service.send_message(req1)
    assert res1.session_id is not None
    session_id = res1.session_id
    assert res1.extracted_criteria is not None
    assert res1.extracted_criteria.district == "Nam Từ Liêm"
    assert res1.extracted_criteria.province == "Hà Nội"

    # Turn 2: Add price constraint
    req2 = SendMessageRequest(session_id=session_id, message="Tầm giá dưới 3 tỷ 5")
    res2 = service.send_message(req2)
    assert res2.session_id == session_id
    assert res2.extracted_criteria is not None
    # District persisted from Turn 1!
    assert res2.extracted_criteria.district == "Nam Từ Liêm"
    assert res2.extracted_criteria.budget_max is not None

    # Turn 3: Modify district to Cầu Giấy
    req3 = SendMessageRequest(session_id=session_id, message="Đổi sang quận Cầu Giấy nhé")
    res3 = service.send_message(req3)
    assert res3.session_id == session_id
    assert res3.extracted_criteria is not None
    assert res3.extracted_criteria.district == "Cầu Giấy"
    # Budget max persisted from Turn 2!
    assert res3.extracted_criteria.budget_max is not None


def test_chatbot_grounded_in_db_listings(db_session: Session, test_user: User):
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    # Seed approved listing in DB
    listing = Listing(
        user_id=test_user.id,
        category_id=1,
        title="Chung cư cao cấp Vinhomes Smart City 2PN",
        description="Căn hộ tầng trung thoáng mát",
        price=3_200_000_000,
        price_unit="TOTAL",
        area=65.0,
        address_text="Tây Mỗ, Nam Từ Liêm",
        province="Hà Nội",
        district="Nam Từ Liêm",
        transaction_type=TransactionType.SALE.value,
        status=ListingStatus.APPROVED.value,
        published_at=now,
        expired_at=now + timedelta(days=30),
        bedrooms=2,
        bathrooms=2,
    )
    db_session.add(listing)
    db_session.flush()

    feat = ListingFeature(listing_id=listing.id, feature_name="Nội thất đầy đủ")
    db_session.add(feat)
    db_session.commit()

    service = ChatbotService(db_session)
    req = SendMessageRequest(message="Tìm căn hộ 2pn tại Nam Từ Liêm tầm 3 tỷ full nội thất")
    res = service.send_message(req)

    assert len(res.listings) >= 1
    top_hit = res.listings[0]
    assert top_hit.id == listing.id
    assert "Vinhomes Smart City" in top_hit.title
    assert top_hit.price == 3_200_000_000
    assert "Vinhomes Smart City" in res.message_text


# ---------------------------------------------------------
# 4. API Endpoints Integration Tests
# ---------------------------------------------------------

def test_api_chatbot_message_anonymous(client: TestClient):
    payload = {"message": "Xin chào bot, tôi muốn tìm hiểu"}
    response = client.post("/api/v1/chatbot/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "session_id" in data["data"]
    assert data["data"]["sender"] == "ASSISTANT"
    assert data["data"]["is_clarification"] is True


def test_api_chatbot_out_of_scope(client: TestClient):
    payload = {"message": "Hôm nay thời tiết thế nào hả bạn?"}
    response = client.post("/api/v1/chatbot/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "BDS Smart" in data["data"]["message_text"]
    assert len(data["data"]["listings"]) == 0


def test_api_chatbot_user_sessions_history_and_delete(
    client: TestClient,
    test_user: User,
    db_session: Session,
):
    token = create_access_token(data={"sub": str(test_user.id), "role": test_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Send authenticated message
    res_msg = client.post(
        "/api/v1/chatbot/message",
        json={"message": "Tìm mua căn hộ tại Cầu Giấy dưới 4 tỷ"},
        headers=headers,
    )
    assert res_msg.status_code == 200
    session_id = res_msg.json()["data"]["session_id"]

    # 2. List sessions for user
    res_sessions = client.get("/api/v1/chatbot/sessions", headers=headers)
    assert res_sessions.status_code == 200
    sessions_list = res_sessions.json()["data"]
    assert len(sessions_list) >= 1
    found = any(s["id"] == session_id for s in sessions_list)
    assert found is True

    # 3. Get session messages
    res_history = client.get(f"/api/v1/chatbot/sessions/{session_id}/messages", headers=headers)
    assert res_history.status_code == 200
    messages = res_history.json()["data"]
    assert len(messages) >= 2  # 1 User msg, 1 Assistant msg
    assert messages[0]["sender"] == "USER"
    assert messages[1]["sender"] == "ASSISTANT"

    # 4. Delete session
    res_delete = client.delete(f"/api/v1/chatbot/sessions/{session_id}", headers=headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["success"] is True

    # Check session is removed
    res_history_after = client.get(f"/api/v1/chatbot/sessions/{session_id}/messages", headers=headers)
    assert len(res_history_after.json()["data"]) == 0
