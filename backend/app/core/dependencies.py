import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import (
    CredentialsException,
    InactiveUserException,
    PermissionDeniedException,
    RateLimitExceededException,
)
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository

# Use HTTPBearer with auto_error=False so we can provide our standardized error JSON response
security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """Dependency that extracts and validates the Bearer token, returning the User entity."""
    if not credentials or not credentials.credentials:
        raise CredentialsException("Yêu cầu xác thực Bearer token")

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise CredentialsException("Token không hợp lệ hoặc đã hết hạn")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise CredentialsException("Thông tin định danh trong token không hợp lệ")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise CredentialsException("Mã người dùng trong token không hợp lệ")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise CredentialsException("Tài khoản liên kết với token này không tồn tại")

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency returning the authenticated user if valid token present, or None for guests."""
    if not credentials or not credentials.credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None
    user = UserRepository(db).get_by_id(user_id)
    return user if (user and user.is_active) else None


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency ensuring that the authenticated user's account is currently active."""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency restricting endpoint access to Quản trị viên (ADMIN) only."""
    if current_user.role != UserRole.ADMIN.value:
        raise PermissionDeniedException("Chức năng này yêu cầu quyền Quản trị viên (Admin)")
    return current_user


class LoginRateLimiter:
    """In-memory sliding window rate limiter to protect login endpoints against brute-force."""
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._records: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now(timezone.utc).timestamp()

        with self._lock:
            # Purge timestamps outside the sliding window
            valid_timestamps = [
                ts for ts in self._records[client_ip]
                if now - ts < self.window_seconds
            ]
            if len(valid_timestamps) >= self.max_attempts:
                raise RateLimitExceededException(
                    f"Bạn đã thực hiện quá nhiều lượt đăng nhập. Vui lòng chờ {self.window_seconds} giây."
                )
            valid_timestamps.append(now)
            self._records[client_ip] = valid_timestamps


login_rate_limiter = LoginRateLimiter(max_attempts=10, window_seconds=60)
