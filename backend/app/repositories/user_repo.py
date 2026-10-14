from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == email.lower().strip())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_paginated(
        self,
        offset: int = 0,
        limit: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if role:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        if search:
            search_pattern = f"%{search.strip()}%"
            filter_cond = (
                User.full_name.ilike(search_pattern) |
                User.email.ilike(search_pattern) |
                User.phone_number.ilike(search_pattern)
            )
            stmt = stmt.where(filter_cond)
            count_stmt = count_stmt.where(filter_cond)

        total = self.db.execute(count_stmt).scalar() or 0
        users = self.db.execute(
            stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        ).scalars().all()

        return list(users), total
