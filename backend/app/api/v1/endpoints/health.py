from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.core.config import settings
from app.core.database import check_db_connection
from app.schemas.health import DatabaseHealth, HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application and Database Health Check",
    description="Check the server runtime status and ping the database to verify connectivity."
)
def get_health() -> HealthResponse:
    db_info = check_db_connection()
    return HealthResponse(
        status="healthy" if db_info["status"] == "connected" else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
        database=DatabaseHealth(
            status=db_info["status"],
            dialect=db_info["dialect"],
            latency_ms=db_info["latency_ms"],
            error=db_info["error"]
        ),
        timestamp=datetime.now(timezone.utc).isoformat()
    )
