from fastapi.testclient import TestClient

from app.models.listing import Category, Listing

# =====================================================================
# 1. CATEGORY TESTS
# =====================================================================

def test_list_categories(client: TestClient, sample_category: Category):
    """Test public endpoint returns category list with 200 OK."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert any(c["slug"] == sample_category.slug for c in data["data"])


def test_create_category_as_admin(client: TestClient, admin_token_headers: dict):
    """Admin can create new categories."""
    payload = {
        "name": "Biệt thự nghỉ dưỡng",
        "slug": "biet-thu-nghi-duong",
        "description": "Biệt thự biển và ven đồi"
    }
    response = client.post("/api/v1/categories", json=payload, headers=admin_token_headers)
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Biệt thự nghỉ dưỡng"


def test_create_category_as_user_forbidden(client: TestClient, user_token_headers: dict):
    """Regular user attempting to create category is rejected with 403 Forbidden."""
    payload = {"name": "Đất trang trại", "slug": "dat-trang-trai"}
    response = client.post("/api/v1/categories", json=payload, headers=user_token_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN_RESOURCE"


# =====================================================================
# 2. LISTING CREATION & VALIDATION TESTS
# =====================================================================

def test_create_listing_draft_success(client: TestClient, sample_category: Category, user_token_headers: dict):
    """User can create draft listing without image constraints."""
    payload = {
        "title": "Bản nháp nhà mặt ngõ kinh doanh sầm uất",
        "description": "Nhà mặt ngõ rộng 5m thông thoáng, giao thông thuận tiện đi lại khắp nơi trong thành phố.",
        "category_id": sample_category.id,
        "transaction_type": "SALE",
        "price": 2500000000.0,
        "area": 45.0,
        "address_text": "Số 10 ngõ 50 Hoàng Văn Thái",
        "province": "Hà Nội",
        "district": "Thanh Xuân",
        "is_draft": True,
        "images": []
    }
    response = client.post("/api/v1/listings", json=payload, headers=user_token_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "DRAFT"
    assert data["title"] == payload["title"]


def test_create_listing_submit_approval_success(client: TestClient, sample_category: Category, user_token_headers: dict):
    """User submits listing for approval with at least 3 valid images."""
    payload = {
        "title": "Bán nhà liền kề KĐT Geleximco Lê Trọng Tấn",
        "description": "Nhà xây thô hoàn thiện mặt ngoài 4 tầng hiện đại, đường trước nhà 13.5m có vỉa hè rộng rãi.",
        "category_id": sample_category.id,
        "transaction_type": "SALE",
        "price": 8500000000.0,
        "area": 100.0,
        "address_text": "Khu D Geleximco Lê Trọng Tấn",
        "province": "Hà Nội",
        "district": "Hà Đông",
        "is_draft": False,
        "features": ["Gara ô tô", "Đường 13m"],
        "images": [
            {"image_url": "https://cloudinary.com/front.jpg", "public_id": "p1", "is_thumbnail": True},
            {"image_url": "https://cloudinary.com/living.jpg", "public_id": "p2"},
            {"image_url": "https://cloudinary.com/bedroom.jpg", "public_id": "p3"},
        ]
    }
    response = client.post("/api/v1/listings", json=payload, headers=user_token_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "PENDING_APPROVAL"
    assert len(data["images"]) == 3
    assert len(data["features"]) == 2


def test_create_listing_submit_insufficient_images_error(client: TestClient, sample_category: Category, user_token_headers: dict):
    """Submitting for approval with fewer than 3 images fails validation with 422."""
    payload = {
        "title": "Bán nhà liền kề KĐT Geleximco Lê Trọng Tấn",
        "description": "Nhà xây thô hoàn thiện mặt ngoài 4 tầng hiện đại, đường trước nhà 13.5m có vỉa hè rộng rãi.",
        "category_id": sample_category.id,
        "price": 8500000000.0,
        "area": 100.0,
        "address_text": "Khu D Geleximco",
        "province": "Hà Nội",
        "district": "Hà Đông",
        "is_draft": False,
        "images": [
            {"image_url": "https://cloudinary.com/front.jpg", "public_id": "p1"}
        ]  # Only 1 image
    }
    response = client.post("/api/v1/listings", json=payload, headers=user_token_headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_FAILED"


def test_create_listing_unauthorized(client: TestClient, sample_category: Category):
    """Creating listing without token returns 401."""
    payload = {
        "title": "Tin đăng không đăng nhập",
        "description": "Mô tả tin đăng kiểm tra quyền truy cập không xác thực.",
        "category_id": sample_category.id,
        "price": 1000000000.0,
        "area": 50.0,
        "address_text": "123 Đường",
        "province": "Hà Nội",
        "district": "Cầu Giấy"
    }
    response = client.post("/api/v1/listings", json=payload)
    assert response.status_code == 401


# =====================================================================
# 3. PUBLIC SEARCH & FILTER TESTS
# =====================================================================

def test_search_public_listings_only_approved(client: TestClient, approved_listing: Listing):
    """Public search only returns listings with status APPROVED."""
    response = client.get("/api/v1/listings?keyword=Royal")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    assert all(item["status"] == "APPROVED" for item in data["items"])


def test_search_public_listings_filter_criteria(client: TestClient, approved_listing: Listing):
    """Search correctly filters by province, district, and price range."""
    # Match criteria
    res_match = client.get(
        "/api/v1/listings?province=Hà Nội&district=Thanh Xuân&min_price=4000000000&max_price=5000000000"
    )
    assert res_match.status_code == 200
    assert res_match.json()["data"]["total"] >= 1

    # Non-matching price criteria
    res_empty = client.get("/api/v1/listings?min_price=90000000000")
    assert res_empty.status_code == 200
    assert res_empty.json()["data"]["total"] == 0


# =====================================================================
# 4. DETAIL VIEW & PRIVACY RULES (BR-05)
# =====================================================================

def test_get_listing_detail_guest_masks_phone(client: TestClient, approved_listing: Listing):
    """Unauthenticated guests see masked phone number (e.g. 0912.xxx.xxx)."""
    response = client.get(f"/api/v1/listings/{approved_listing.id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert ".xxx.xxx" in data["owner_phone"]


def test_get_listing_detail_authenticated_full_phone(client: TestClient, approved_listing: Listing, user2_token_headers: dict):
    """Authenticated users see full phone number."""
    response = client.get(f"/api/v1/listings/{approved_listing.id}", headers=user2_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert ".xxx.xxx" not in data["owner_phone"]
    assert data["owner_phone"] == "0912345678"


def test_get_listing_detail_draft_hidden_from_stranger(client: TestClient, sample_category: Category, user_token_headers: dict, user2_token_headers: dict):
    """A draft listing is completely hidden (404) from other users and guests."""
    # User 1 creates draft
    create_res = client.post("/api/v1/listings", json={
        "title": "Nhà nháp bí mật của người dùng 1",
        "description": "Nội dung nháp chưa hoàn thiện về thông số kỹ thuật và giấy tờ pháp lý.",
        "category_id": sample_category.id,
        "price": 3000000000.0,
        "area": 50.0,
        "address_text": "Địa chỉ A",
        "province": "Hà Nội",
        "district": "Đống Đa",
        "is_draft": True
    }, headers=user_token_headers)
    draft_id = create_res.json()["data"]["id"]

    # Stranger (User 2) tries to view draft -> 404
    res_stranger = client.get(f"/api/v1/listings/{draft_id}", headers=user2_token_headers)
    assert res_stranger.status_code == 404

    # Owner (User 1) can view own draft -> 200
    res_owner = client.get(f"/api/v1/listings/{draft_id}", headers=user_token_headers)
    assert res_owner.status_code == 200
    assert res_owner.json()["data"]["status"] == "DRAFT"


# =====================================================================
# 5. OWNERSHIP, UPDATE & STATUS RESTRICTIONS
# =====================================================================

def test_update_listing_by_owner(client: TestClient, sample_category: Category, user_token_headers: dict):
    """Owner can update their draft listing."""
    create_res = client.post("/api/v1/listings", json={
        "title": "Nhà cần sửa đổi thông tin tiêu đề",
        "description": "Mô tả ban đầu trước khi được người dùng chỉnh sửa thông tin chi tiết.",
        "category_id": sample_category.id,
        "price": 2000000000.0,
        "area": 40.0,
        "address_text": "Số 1 Đường",
        "province": "Hà Nội",
        "district": "Hoàng Mai",
        "is_draft": True
    }, headers=user_token_headers)
    listing_id = create_res.json()["data"]["id"]

    update_payload = {"title": "Nhà đã được sửa đổi tiêu đề mới chính xác hơn"}
    res_update = client.put(f"/api/v1/listings/{listing_id}", json=update_payload, headers=user_token_headers)
    assert res_update.status_code == 200
    assert res_update.json()["data"]["title"] == update_payload["title"]


def test_update_listing_by_stranger_forbidden(client: TestClient, approved_listing: Listing, user2_token_headers: dict):
    """User cannot update another person's listing (403 Forbidden)."""
    response = client.put(
        f"/api/v1/listings/{approved_listing.id}",
        json={"title": "Cố tình chiếm quyền sửa đổi tin của người khác"},
        headers=user2_token_headers
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN_RESOURCE"


def test_update_listing_while_pending_blocked(client: TestClient, sample_category: Category, user_token_headers: dict):
    """Listing in PENDING_APPROVAL status cannot be edited directly by poster."""
    # Create pending listing with 3 images
    create_res = client.post("/api/v1/listings", json={
        "title": "Tin đăng gửi duyệt để kiểm tra trạng thái khóa",
        "description": "Mô tả chi tiết nhà phố đầy đủ tiện nghi, sẵn sàng giao dịch ngay trong ngày.",
        "category_id": sample_category.id,
        "price": 5000000000.0,
        "area": 60.0,
        "address_text": "123 Phố",
        "province": "Hà Nội",
        "district": "Hai Bà Trưng",
        "is_draft": False,
        "images": [
            {"image_url": "https://c.com/1.jpg", "public_id": "1"},
            {"image_url": "https://c.com/2.jpg", "public_id": "2"},
            {"image_url": "https://c.com/3.jpg", "public_id": "3"}
        ]
    }, headers=user_token_headers)
    listing_id = create_res.json()["data"]["id"]

    # Try to edit -> 400 LISTING_LOCKED_PENDING
    res = client.put(f"/api/v1/listings/{listing_id}", json={"title": "Thử sửa tin đang chờ duyệt"}, headers=user_token_headers)
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "LISTING_LOCKED_PENDING"


# =====================================================================
# 6. VISIBILITY & DELETION TESTS
# =====================================================================

def test_toggle_visibility_by_owner(client: TestClient, approved_listing: Listing, user_token_headers: dict):
    """Owner can hide approved listing and make it visible again."""
    # Hide listing
    res_hide = client.patch(
        f"/api/v1/listings/{approved_listing.id}/visibility",
        json={"is_hidden": True},
        headers=user_token_headers
    )
    assert res_hide.status_code == 200

    # Unhide listing
    res_unhide = client.patch(
        f"/api/v1/listings/{approved_listing.id}/visibility",
        json={"is_hidden": False},
        headers=user_token_headers
    )
    assert res_unhide.status_code == 200


def test_delete_listing_by_stranger_forbidden(client: TestClient, approved_listing: Listing, user2_token_headers: dict):
    """Stranger cannot delete listing (403 Forbidden)."""
    response = client.delete(f"/api/v1/listings/{approved_listing.id}", headers=user2_token_headers)
    assert response.status_code == 403


def test_delete_listing_by_owner(client: TestClient, sample_category: Category, user_token_headers: dict):
    """Owner can delete their own listing."""
    create_res = client.post("/api/v1/listings", json={
        "title": "Tin đăng tạo ra để kiểm tra xóa hoàn toàn",
        "description": "Nội dung tin đăng tạm thời phục vụ kiểm thử tính năng xóa tài nguyên.",
        "category_id": sample_category.id,
        "price": 1500000000.0,
        "area": 30.0,
        "address_text": "Ngõ 1",
        "province": "Hà Nội",
        "district": "Ba Đình",
        "is_draft": True
    }, headers=user_token_headers)
    listing_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/listings/{listing_id}", headers=user_token_headers)
    assert del_res.status_code == 200


# =====================================================================
# 7. ADMIN MODERATION TESTS
# =====================================================================

def test_admin_moderation_flow(client: TestClient, sample_category: Category, user_token_headers: dict, admin_token_headers: dict):
    """Test full moderation lifecycle: Pending -> Approve and Pending -> Reject with reason."""
    # 1. User submits listing for approval
    create_res = client.post("/api/v1/listings", json={
        "title": "Căn hộ chờ duyệt để Admin kiểm thử tính năng",
        "description": "Căn hộ cao cấp 3 phòng ngủ đầy đủ tiện nghi, view hồ điều hòa thoáng mát.",
        "category_id": sample_category.id,
        "price": 5500000000.0,
        "area": 90.0,
        "address_text": "KĐT Ngoại Giao Đoàn",
        "province": "Hà Nội",
        "district": "Bắc Từ Liêm",
        "is_draft": False,
        "images": [
            {"image_url": "https://c.com/1.jpg", "public_id": "1"},
            {"image_url": "https://c.com/2.jpg", "public_id": "2"},
            {"image_url": "https://c.com/3.jpg", "public_id": "3"}
        ]
    }, headers=user_token_headers)
    listing_id = create_res.json()["data"]["id"]

    # 2. Admin views pending queue
    queue_res = client.get("/api/v1/admin/listings/pending", headers=admin_token_headers)
    assert queue_res.status_code == 200
    assert any(item["id"] == listing_id for item in queue_res.json()["data"]["items"])

    # 3. Regular user tries to moderate -> 403 Forbidden
    forbid_res = client.patch(
        f"/api/v1/admin/listings/{listing_id}/moderate",
        json={"action": "APPROVE"},
        headers=user_token_headers
    )
    assert forbid_res.status_code == 403

    # 4. Admin rejects without reason -> 422 Validation Error
    bad_reject = client.patch(
        f"/api/v1/admin/listings/{listing_id}/moderate",
        json={"action": "REJECT"},
        headers=admin_token_headers
    )
    assert bad_reject.status_code == 422

    # 5. Admin rejects with valid reason -> 200 OK
    reject_res = client.patch(
        f"/api/v1/admin/listings/{listing_id}/moderate",
        json={"action": "REJECT", "rejection_reason": "Ảnh bị mờ và giá chưa rõ ràng"},
        headers=admin_token_headers
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["data"]["status"] == "REJECTED"
    assert reject_res.json()["data"]["rejection_reason"] == "Ảnh bị mờ và giá chưa rõ ràng"

    # 6. Admin approves listing -> 200 OK
    approve_res = client.patch(
        f"/api/v1/admin/listings/{listing_id}/moderate",
        json={"action": "APPROVE"},
        headers=admin_token_headers
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["data"]["status"] == "APPROVED"
    assert approve_res.json()["data"]["published_at"] is not None
    assert approve_res.json()["data"]["expired_at"] is not None
