import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")


class AppException(Exception):
    """Base application exception for handled domain and API errors."""
    def __init__(
        self,
        message: str,
        code: str = "BAD_REQUEST",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class CredentialsException(AppException):
    def __init__(self, message: str = "Email hoặc mật khẩu không chính xác"):
        super().__init__(
            message=message,
            code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class TokenExpiredException(AppException):
    def __init__(self, message: str = "Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại"):
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PermissionDeniedException(AppException):
    def __init__(self, message: str = "Bạn không có quyền thực hiện thao tác này"):
        super().__init__(
            message=message,
            code="FORBIDDEN_RESOURCE",
            status_code=status.HTTP_403_FORBIDDEN
        )


class InactiveUserException(AppException):
    def __init__(self, message: str = "Tài khoản của bạn đã bị khóa hoặc chưa kích hoạt"):
        super().__init__(
            message=message,
            code="USER_INACTIVE",
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Tài nguyên yêu cầu không tồn tại"):
        super().__init__(
            message=message,
            code="RECORD_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateResourceException(AppException):
    def __init__(self, message: str = "Tài nguyên đã tồn tại trên hệ thống"):
        super().__init__(
            message=message,
            code="RESOURCE_CONFLICT",
            status_code=status.HTTP_409_CONFLICT
        )


class RateLimitExceededException(AppException):
    def __init__(self, message: str = "Quá nhiều yêu cầu. Vui lòng thử lại sau"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Any] = None
) -> JSONResponse:
    """Format standard error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom application exceptions."""
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic input validation errors."""
    clean_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        clean_errors.append({
            "field": field,
            "message": error.get("msg", "Dữ liệu không hợp lệ")
        })
    return build_error_response(
        status_code=422,
        code="VALIDATION_FAILED",
        message="Dữ liệu đầu vào không hợp lệ",
        details=clean_errors
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected 500 errors to avoid leaking stack traces."""
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="Hệ thống đã xảy ra sự cố ngoài ý muốn. Vui lòng liên hệ quản trị viên."
    )
