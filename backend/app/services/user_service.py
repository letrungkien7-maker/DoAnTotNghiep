from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Người dùng không tồn tại")
        return user

    def update_profile(self, user_id: int, req: UserUpdateRequest) -> User:
        user = self.get_user_by_id(user_id)
        if req.full_name is not None:
            user.full_name = req.full_name.strip()
        if req.phone_number is not None:
            user.phone_number = req.phone_number.strip()
        if req.avatar_url is not None:
            user.avatar_url = req.avatar_url.strip()
        return self.user_repo.update(user)

    def admin_list_users(
        self,
        pagination: PaginationParams,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse[UserResponse]:
        users, total = self.user_repo.get_paginated(
            offset=pagination.offset,
            limit=pagination.size,
            role=role,
            is_active=is_active,
            search=search
        )
        total_pages = (total + pagination.size - 1) // pagination.size if total > 0 else 0
        return PaginatedResponse[UserResponse](
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=pagination.page,
            size=pagination.size,
            total_pages=total_pages
        )

    def admin_update_status(self, user_id: int, is_active: bool) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = is_active
        return self.user_repo.update(user)
