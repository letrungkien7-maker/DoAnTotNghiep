from app.core.database import check_db_connection


def test_database_connection_checker():
    """Verify check_db_connection returns expected diagnostic dictionary structure."""
    result = check_db_connection()
    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] in ["connected", "disconnected"]
    assert "dialect" in result
    assert "latency_ms" in result
    assert isinstance(result["latency_ms"], (int, float))
    if result["status"] == "disconnected":
        assert result["error"] is not None
    else:
        assert result["error"] is None
