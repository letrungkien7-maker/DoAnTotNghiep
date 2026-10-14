from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient

from app.models.listing import Listing, ListingFeature, ListingStatus, TransactionType
from app.schemas.recommendation import RecommendationCriteria
from app.services.recommendation_engine import RecommendationEngine, RecommendationWeights


def test_engine_price_scoring():
    # 1. No preference
    assert RecommendationEngine.calculate_price_score(3_000_000_000) == 1.0

    # 2. In range
    assert RecommendationEngine.calculate_price_score(
        price=3_500_000_000,
        budget_min=3_000_000_000,
        budget_max=4_000_000_000,
    ) == 1.0

    # 3. Under budget (gentle decay, >= 0.60)
    score_under = RecommendationEngine.calculate_price_score(
        price=2_000_000_000,
        budget_min=3_000_000_000,
        budget_max=4_000_000_000,
    )
    assert 0.60 <= score_under < 1.0

    # 4. Slightly over budget (tolerance up to 25%)
    score_slight_over = RecommendationEngine.calculate_price_score(
        price=4_500_000_000,
        budget_min=3_000_000_000,
        budget_max=4_000_000_000,
    )
    assert 0.0 < score_slight_over < 1.0

    # 5. Excessively over budget (> 25% over 4B is > 5B) -> 0.0
    score_too_high = RecommendationEngine.calculate_price_score(
        price=5_500_000_000,
        budget_min=3_000_000_000,
        budget_max=4_000_000_000,
    )
    assert score_too_high == 0.0


def test_engine_location_scoring():
    # Exact match
    assert RecommendationEngine.calculate_location_score(
        listing_province="Hà Nội",
        listing_district="Nam Từ Liêm",
        target_province="Hà Nội",
        target_district="Nam Từ Liêm",
    ) == 1.0

    # Same province, different district
    assert RecommendationEngine.calculate_location_score(
        listing_province="Hà Nội",
        listing_district="Cầu Giấy",
        target_province="Hà Nội",
        target_district="Nam Từ Liêm",
    ) == 0.50

    # Different province
    assert RecommendationEngine.calculate_location_score(
        listing_province="Đà Nẵng",
        listing_district="Hải Châu",
        target_province="Hà Nội",
        target_district="Nam Từ Liêm",
    ) == 0.0


def test_engine_category_and_bedroom_scoring():
    # Category
    assert RecommendationEngine.calculate_category_score(1, 1) == 1.0
    assert RecommendationEngine.calculate_category_score(1, 2) == 0.0
    assert RecommendationEngine.calculate_category_score(1, None) == 1.0

    # Bedrooms
    assert RecommendationEngine.calculate_bedroom_score(2, 2) == 1.0
    assert RecommendationEngine.calculate_bedroom_score(2, 3) == 0.70
    assert RecommendationEngine.calculate_bedroom_score(2, 4) == 0.40
    assert RecommendationEngine.calculate_bedroom_score(1, 4) == 0.10


def test_engine_feature_scoring():
    listing_feats = ["Nội thất đầy đủ", "Sổ đỏ chính chủ", "Bể bơi"]
    target_feats = ["Nội thất đầy đủ", "Sổ đỏ chính chủ"]

    score = RecommendationEngine.calculate_feature_score(listing_feats, target_feats)
    assert score == 1.0

    target_feats_extra = ["Nội thất đầy đủ", "Sổ đỏ chính chủ", "Gara ô tô", "Sân vườn"]
    score_partial = RecommendationEngine.calculate_feature_score(listing_feats, target_feats_extra)
    assert score_partial == 0.50


def test_engine_composite_scoring_and_reasons():
    listing = SimpleNamespace(
        id=1,
        title="Căn hộ 2PN Vinhomes",
        price=3_200_000_000,
        area=65.0,
        bedrooms=2,
        province="Hà Nội",
        district="Nam Từ Liêm",
        category_id=1,
        category_name="Căn hộ chung cư",
        features=["Nội thất đầy đủ", "Sổ đỏ chính chủ"],
    )

    criteria = RecommendationCriteria(
        province="Hà Nội",
        district="Nam Từ Liêm",
        category_id=1,
        budget_min=3_000_000_000,
        budget_max=4_000_000_000,
        bedrooms=2,
        features=["Nội thất đầy đủ"],
    )

    breakdown, reasons = RecommendationEngine.score_listing(listing, criteria)
    assert breakdown.total_score == 1.0
    assert breakdown.match_percentage == 100.0
    assert len(reasons) >= 3
    assert any("Nam Từ Liêm" in r for r in reasons)
    assert any("ngân sách" in r for r in reasons)


def test_recommendation_search_api(client: TestClient, db_session):
    # Seed a verified listing in the test database
    now = datetime.now(timezone.utc)
    listing = Listing(
        user_id=1,
        category_id=1,
        title="Căn hộ 2PN cao cấp Mỹ Đình Pearl",
        description="Mô tả căn hộ cao cấp đầy đủ tiện ích và nội thất mới toanh.",
        transaction_type=TransactionType.SALE.value,
        price=3_800_000_000,
        price_unit="TOTAL",
        area=78.0,
        bedrooms=2,
        bathrooms=2,
        address_text="Số 1 Châu Văn Liêm",
        province="Hà Nội",
        district="Nam Từ Liêm",
        status=ListingStatus.APPROVED.value,
        published_at=now,
        expired_at=now + timedelta(days=30),
        view_count=20,
    )
    db_session.add(listing)
    db_session.flush()

    feat = ListingFeature(listing_id=listing.id, feature_name="Nội thất đầy đủ")
    db_session.add(feat)
    db_session.commit()

    # Search via recommendation endpoint
    payload = {
        "transaction_type": "SALE",
        "province": "Hà Nội",
        "district": "Nam Từ Liêm",
        "budget_min": 3_000_000_000,
        "budget_max": 4_000_000_000,
        "bedrooms": 2,
        "features": ["Nội thất đầy đủ"],
        "top_k": 5,
    }

    res = client.post("/api/v1/recommendations/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) >= 1

    item = data["data"]["items"][0]
    assert item["match_score"] > 0.8
    assert len(item["match_reasons"]) > 0
    assert item["score_breakdown"]["total_score"] > 0.8


def test_recommendation_personalized_and_similar_api(client: TestClient, db_session):
    now = datetime.now(timezone.utc)
    l1 = Listing(
        user_id=1,
        category_id=1,
        title="Căn hộ Vinhomes Smart City 2PN",
        description="Mô tả căn hộ 1",
        transaction_type=TransactionType.SALE.value,
        price=3_200_000_000,
        price_unit="TOTAL",
        area=65.0,
        bedrooms=2,
        address_text="Đại lộ Thăng Long",
        province="Hà Nội",
        district="Nam Từ Liêm",
        status=ListingStatus.APPROVED.value,
        published_at=now,
        expired_at=now + timedelta(days=30),
        view_count=50,
    )
    l2 = Listing(
        user_id=1,
        category_id=1,
        title="Căn hộ Masteri West Heights 2PN",
        description="Mô tả căn hộ 2",
        transaction_type=TransactionType.SALE.value,
        price=3_400_000_000,
        price_unit="TOTAL",
        area=68.0,
        bedrooms=2,
        address_text="Khu đô thị Tây Mỗ",
        province="Hà Nội",
        district="Nam Từ Liêm",
        status=ListingStatus.APPROVED.value,
        published_at=now,
        expired_at=now + timedelta(days=30),
        view_count=35,
    )
    db_session.add_all([l1, l2])
    db_session.commit()

    # Test Cold-Start Personalized feed (no history)
    res_perso = client.get("/api/v1/recommendations/personalized?limit=5")
    assert res_perso.status_code == 200
    data_perso = res_perso.json()
    assert data_perso["success"] is True
    assert data_perso["data"]["strategy"] == "POPULAR_COLD_START"
    assert len(data_perso["data"]["items"]) >= 2

    # Test Similar listings for listing l1
    res_similar = client.get(f"/api/v1/recommendations/similar/{l1.id}?limit=3")
    assert res_similar.status_code == 200
    data_similar = res_similar.json()
    assert data_similar["success"] is True
    assert data_similar["data"]["strategy"] == "ITEM_TO_ITEM_SIMILARITY"
    assert len(data_similar["data"]["items"]) >= 1
    assert data_similar["data"]["items"][0]["id"] == l2.id
    assert data_similar["data"]["items"][0]["match_score"] > 0.70
