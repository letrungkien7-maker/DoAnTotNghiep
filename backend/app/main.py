import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.health import get_health
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.scripts.seed_demo_data import ensure_demo_data_seeded

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging on startup
    setup_logging()

    # Auto-seed demo data if database is empty (skipped during pytest)
    is_testing = "pytest" in sys.modules or bool(os.getenv("PYTEST_CURRENT_TEST"))
    if settings.AUTO_SEED_DEMO_DATA and not is_testing:
        try:
            ensure_demo_data_seeded(max_listings=settings.AUTO_SEED_LISTING_LIMIT)
        except Exception as exc:
            logger.warning(f"Bỏ qua auto-seed khi khởi động (DB chưa sẵn sàng): {exc}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Real Estate Platform with AI Chatbot and Recommendation Engine",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Exception Handlers
app.add_exception_handler(AppException, cast(Any, app_exception_handler))
app.add_exception_handler(RequestValidationError, cast(Any, validation_exception_handler))
app.add_exception_handler(Exception, global_exception_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"^https://.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static media uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Root level health endpoint
app.add_api_route("/health", get_health, methods=["GET"], tags=["Health"])

# API v1 routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/health",
        "api_v1": settings.API_V1_PREFIX,
    }
