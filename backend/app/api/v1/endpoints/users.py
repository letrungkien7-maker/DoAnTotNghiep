from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationParams, ResponseBase
from app.schemas.user import UserResponse, UserStatusUpdate, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=ResponseBase[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tài khoản hiện tại",
    description="Truy xuất hồ sơ của người dùng đang đăng nhập dựa trên Bearer token."
)
def get_my_profile(
    current_user: User = Depends(get_current_active_user)
) -> ResponseBase[UserResponse]:
    return ResponseBase[UserResponse](
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Lấy thông tin tài khoản thành công"
    )


@router.put(
    "/me",
    response_model=ResponseBase[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin tài khoản cá nhân",
    description="Cập nhật họ tên, số điện thoại, avatar của chính người dùng đăng nhập."
)
def update_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[UserResponse]:
    user_service = UserService(db)
    updated_user = user_service.update_profile(current_user.id, req)
    return ResponseBase[UserResponse](
        success=True,
        data=UserResponse.model_validate(updated_user),
        message="Cập nhật thông tin cá nhân thành công"
    )


@router.get(
    "",
    response_model=ResponseBase[PaginatedResponse[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Danh sách người dùng hệ thống",
    description="Dành riêng cho Quản trị viên: Tìm kiếm, lọc và phân trang danh sách tài khoản."
)
def admin_list_users(
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(10, ge=1, le=100, description="Số phần tử mỗi trang"),
    role: Optional[str] = Query(None, description="Lọc theo quyền (USER hoặc ADMIN)"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên, email, sđt"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[UserResponse]]:
    pagination = PaginationParams(page=page, size=size)
    user_service = UserService(db)
    result = user_service.admin_list_users(
        pagination=pagination,
        role=role,
        is_active=is_active,
        search=search
    )
    return ResponseBase[PaginatedResponse[UserResponse]](
        success=True,
        data=result,
        message="Lấy danh sách người dùng thành công"
    )


@router.patch(
    "/{user_id}/status",
    response_model=ResponseBase[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Khóa hoặc mở khóa tài khoản",
    description="Dành riêng cho Quản trị viên: Cập nhật cờ is_active của người dùng."
)
def admin_toggle_user_status(
    user_id: int,
    req: UserStatusUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> ResponseBase[UserResponse]:
    user_service = UserService(db)
    updated_user = user_service.admin_update_status(user_id, req.is_active)
    action_text = "kích hoạt" if req.is_active else "khóa"
    return ResponseBase[UserResponse](
        success=True,
        data=UserResponse.model_validate(updated_user),
        message=f"Đã {action_text} tài khoản thành công"
    )
