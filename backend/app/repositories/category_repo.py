from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.listing import Category
from app.repositories.base_repo import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_all(self) -> List[Category]:
        stmt = select(Category).order_by(Category.name.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_slug(self, slug: str) -> Optional[Category]:
        stmt = select(Category).where(Category.slug == slug.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Category]:
        stmt = select(Category).where(Category.name == name.strip())
        return self.db.execute(stmt).scalar_one_or_none()
