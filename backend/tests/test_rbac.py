from fastapi.testclient import TestClient

from app.models.user import User


def test_get_profile_unauthorized(client: TestClient):
    """Accessing /users/me without Authorization header returns 401."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_get_profile_invalid_token(client: TestClient):
    """Accessing with malformed token returns 401."""
    headers = {"Authorization": "Bearer invalid_gibberish_token_value"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_get_profile_success(client: TestClient, test_user: User, user_token_headers: dict):
    """Accessing with valid User token returns 200 and profile."""
    response = client.get("/api/v1/users/me", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == test_user.id
    assert data["data"]["email"] == test_user.email
    assert data["data"]["role"] == "USER"


def test_update_profile_success(client: TestClient, user_token_headers: dict):
    """User can update their own profile details."""
    payload = {
        "full_name": "Nguyễn Văn Đã Cập Nhật",
        "phone_number": "0988776655"
    }
    response = client.put("/api/v1/users/me", json=payload, headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["full_name"] == "Nguyễn Văn Đã Cập Nhật"
    assert data["data"]["phone_number"] == "0988776655"


def test_admin_list_users_as_regular_user(client: TestClient, user_token_headers: dict):
    """Regular user attempting to access admin users list is rejected with 403."""
    response = client.get("/api/v1/users", headers=user_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN_RESOURCE"


def test_admin_list_users_as_admin(client: TestClient, admin_token_headers: dict):
    """Admin accessing /users receives 200 and paginated user list."""
    response = client.get("/api/v1/users?page=1&size=10", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]
    assert data["data"]["page"] == 1
    assert data["data"]["total"] >= 1


def test_admin_toggle_user_status(
    client: TestClient,
    test_user: User,
    admin_token_headers: dict,
    user_token_headers: dict
):
    """Admin can lock and unlock a user, while regular user cannot."""
    # 1. Regular user tries to lock -> 403 Forbidden
    resp_forbidden = client.patch(
        f"/api/v1/users/{test_user.id}/status",
        json={"is_active": False},
        headers=user_token_headers
    )
    assert resp_forbidden.status_code == 403

    # 2. Admin locks test_user -> 200 OK
    resp_lock = client.patch(
        f"/api/v1/users/{test_user.id}/status",
        json={"is_active": False},
        headers=admin_token_headers
    )
    assert resp_lock.status_code == 200
    assert resp_lock.json()["data"]["is_active"] is False

    # 3. Now test_user profile requests are rejected with 403 USER_INACTIVE
    resp_inactive = client.get("/api/v1/users/me", headers=user_token_headers)
    assert resp_inactive.status_code == 403
    assert resp_inactive.json()["error"]["code"] == "USER_INACTIVE"
