from fastapi.testclient import TestClient

from app.models.listing import Listing
from app.models.user import User

# =====================================================================
# 1. FAVORITES TESTS
# =====================================================================

def test_toggle_favorite_lifecycle(client: TestClient, approved_listing: Listing, user2_token_headers: dict):
    """User can add listing to favorites, and toggle off to remove."""
    # 1. First toggle -> Adds to favorite
    res1 = client.post(f"/api/v1/favorites/{approved_listing.id}", headers=user2_token_headers)
    assert res1.status_code == 200
    assert res1.json()["data"]["is_favorited"] is True

    # Check favorites list
    res_list = client.get("/api/v1/favorites", headers=user2_token_headers)
    assert res_list.status_code == 200
    assert res_list.json()["data"]["total"] >= 1
    assert any(item["id"] == approved_listing.id for item in res_list.json()["data"]["items"])

    # 2. Second toggle -> Removes from favorite
    res2 = client.post(f"/api/v1/favorites/{approved_listing.id}", headers=user2_token_headers)
    assert res2.status_code == 200
    assert res2.json()["data"]["is_favorited"] is False

    # Check favorites list is now empty
    res_list_after = client.get("/api/v1/favorites", headers=user2_token_headers)
    assert res_list_after.json()["data"]["total"] == 0


def test_toggle_favorite_unauthenticated(client: TestClient, approved_listing: Listing):
    """Unauthenticated request to toggle favorite returns 401."""
    response = client.post(f"/api/v1/favorites/{approved_listing.id}")
    assert response.status_code == 401


def test_toggle_favorite_nonexistent_listing(client: TestClient, user2_token_headers: dict):
    """Toggling favorite on non-existent listing returns 404."""
    response = client.post("/api/v1/favorites/999999", headers=user2_token_headers)
    assert response.status_code == 404


# =====================================================================
# 2. INQUIRIES & LEAD GENERATION TESTS
# =====================================================================

def test_send_inquiry_as_guest(client: TestClient, approved_listing: Listing):
    """Guest visitor can submit inquiry with contact details."""
    payload = {
        "listing_id": approved_listing.id,
        "sender_name": "Khách Vãng Lai",
        "sender_phone": "0988112233",
        "sender_email": "guest@test.com",
        "message": "Tôi muốn đến xem trực tiếp căn hộ này vào sáng thứ Bảy."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["listing_id"] == approved_listing.id
    assert data["sender_name"] == payload["sender_name"]
    assert data["status"] == "NEW"


def test_send_inquiry_as_logged_in_user(client: TestClient, approved_listing: Listing, user2_token_headers: dict, test_user_2: User):
    """Logged in user submitting inquiry has seeker_id bound automatically."""
    payload = {
        "listing_id": approved_listing.id,
        "sender_name": "Người Mua Có Tài Khoản",
        "sender_phone": "0933778899",
        "message": "Tôi muốn trao đổi thêm về mức giá và phương thức thanh toán."
    }
    response = client.post("/api/v1/inquiries", json=payload, headers=user2_token_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["seeker_id"] == test_user_2.id


def test_send_inquiry_to_own_listing_blocked(client: TestClient, approved_listing: Listing, user_token_headers: dict):
    """Seller attempting to send inquiry to their own listing is rejected with 400."""
    payload = {
        "listing_id": approved_listing.id,  # Owned by test_user
        "sender_name": "Chính Chủ Tự Gửi",
        "sender_phone": "0911223344",
        "message": "Tin nhắn tự gửi cho chính mình không được phép."
    }
    response = client.post("/api/v1/inquiries", json=payload, headers=user_token_headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SELF_INQUIRY_NOT_ALLOWED"


def test_seller_manage_inquiries_lifecycle(
    client: TestClient,
    approved_listing: Listing,
    user_token_headers: dict,
    user2_token_headers: dict
):
    """Test full inquiry management: Buyer sends -> Seller views -> Seller marks CONTACTED."""
    # 1. Buyer sends inquiry
    create_res = client.post("/api/v1/inquiries", json={
        "listing_id": approved_listing.id,
        "sender_name": "Nguyễn Người Mua",
        "sender_phone": "0944556677",
        "message": "Căn này còn không bạn? Tôi muốn liên hệ xem nhà."
    })
    inquiry_id = create_res.json()["data"]["id"]

    # 2. Seller checks received inquiries
    inbox_res = client.get("/api/v1/inquiries/received", headers=user_token_headers)
    assert inbox_res.status_code == 200
    assert inbox_res.json()["data"]["total"] >= 1
    assert any(inq["id"] == inquiry_id for inq in inbox_res.json()["data"]["items"])

    # 3. Stranger tries to update inquiry status -> 403 Forbidden
    stranger_res = client.patch(
        f"/api/v1/inquiries/{inquiry_id}/status",
        json={"status": "CONTACTED"},
        headers=user2_token_headers
    )
    assert stranger_res.status_code == 403

    # 4. Seller updates inquiry status -> 200 OK
    update_res = client.patch(
        f"/api/v1/inquiries/{inquiry_id}/status",
        json={"status": "CONTACTED"},
        headers=user_token_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "CONTACTED"
