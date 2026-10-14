from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, login_rate_limiter
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import ResponseBase
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseBase[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới",
    description="Tạo tài khoản mới. Quyền hạn mặc định luôn là USER. Không thể tự cấp quyền Admin qua API."
)
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db)
) -> ResponseBase[UserResponse]:
    auth_service = AuthService(db)
    user = auth_service.register(req)
    return ResponseBase[UserResponse](
        success=True,
        data=UserResponse.model_validate(user),
        message="Đăng ký tài khoản thành công"
    )


@router.post(
    "/login",
    response_model=ResponseBase[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản & Nhận JWT Token",
    description="Xác thực thông tin email và mật khẩu, trả về Bearer JWT token có thời hạn."
)
def login(
    req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> ResponseBase[TokenResponse]:
    # Apply brute-force rate limiter
    login_rate_limiter.check(request)

    auth_service = AuthService(db)
    token_response = auth_service.authenticate(req)
    return ResponseBase[TokenResponse](
        success=True,
        data=token_response,
        message="Đăng nhập thành công"
    )


@router.post(
    "/logout",
    response_model=ResponseBase[dict],
    status_code=status.HTTP_200_OK,
    summary="Đăng xuất tài khoản",
    description="Xác thực token hiện tại và xác nhận kết thúc phiên đăng nhập."
)
def logout(
    current_user: User = Depends(get_current_active_user)
) -> ResponseBase[dict]:
    return ResponseBase[dict](
        success=True,
        data={"user_id": current_user.id},
        message="Đăng xuất thành công"
    )
