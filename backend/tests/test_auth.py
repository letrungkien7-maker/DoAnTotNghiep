from fastapi.testclient import TestClient

from app.models.user import User


def test_register_success(client: TestClient):
    """Test successful user registration assigns role USER and hashes password."""
    payload = {
        "email": "newuser@domain.com",
        "password": "SecurePassword123!",
        "full_name": "Phạm Hoàng Mới",
        "phone_number": "0934567890"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "newuser@domain.com"
    assert data["data"]["role"] == "USER"
    assert "password" not in data["data"]
    assert "password_hash" not in data["data"]


def test_register_duplicate_email(client: TestClient, test_user: User):
    """Test registering an already existing email returns 409 Conflict."""
    payload = {
        "email": test_user.email,  # duplicate
        "password": "AnotherPassword123!",
        "full_name": "Trùng Lặp",
        "phone_number": "0999999999"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_CONFLICT"


def test_register_validation_error(client: TestClient):
    """Test registering with invalid email or too short password returns 422."""
    # Password too short (< 8 chars)
    payload = {
        "email": "invalid-email-format",
        "password": "short",
        "full_name": "A",
        "phone_number": "123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_FAILED"
    assert len(data["error"]["details"]) > 0


def test_login_success(client: TestClient, test_user: User):
    """Test login with correct credentials returns 200 OK and JWT access token."""
    payload = {
        "email": test_user.email,
        "password": "UserPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["email"] == test_user.email
    assert data["data"]["user"]["role"] == "USER"


def test_login_wrong_password(client: TestClient, test_user: User):
    """Test login with incorrect password returns 401 INVALID_CREDENTIALS."""
    payload = {
        "email": test_user.email,
        "password": "IncorrectPassword!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_email(client: TestClient):
    """Test login with non-existent email returns 401 without leaking existence."""
    payload = {
        "email": "doesnotexist@example.com",
        "password": "SomePassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_inactive_user(client: TestClient, inactive_user: User):
    """Test locked/inactive user cannot log in and returns 403 USER_INACTIVE."""
    payload = {
        "email": inactive_user.email,
        "password": "UserPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "USER_INACTIVE"


def test_logout(client: TestClient, user_token_headers: dict):
    """Test logout endpoint returns 200 OK for authenticated user."""
    response = client.post("/api/v1/auth/logout", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
