from typing import Optional

from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    status: str = Field(..., description="connected or disconnected")
    dialect: str = Field(..., description="database dialect name (e.g. postgresql)")
    latency_ms: float = Field(..., description="round-trip ping latency in ms")
    error: Optional[str] = Field(None, description="error details if disconnected")


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    app_name: str
    environment: str
    version: str = "1.0.0"
    database: DatabaseHealth
    timestamp: str
