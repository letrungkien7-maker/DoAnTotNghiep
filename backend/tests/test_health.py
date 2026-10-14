from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test that the root endpoint returns welcome payload and 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "health" in data
    assert "api_v1" in data


def test_health_check_endpoint(client: TestClient):
    """Test the health check endpoint returns 200 and standard schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "app_name" in data
    assert "environment" in data
    assert "database" in data
    assert "status" in data["database"]
    assert "dialect" in data["database"]
    assert "latency_ms" in data["database"]


def test_api_v1_health_endpoint(client: TestClient):
    """Test the /api/v1/health alias endpoint returns identical structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
