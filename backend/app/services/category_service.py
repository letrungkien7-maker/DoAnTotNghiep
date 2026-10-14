from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceException
from app.models.listing import Category
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_all(self) -> List[CategoryResponse]:
        categories = self.repo.get_all()
        return [CategoryResponse.model_validate(c) for c in categories]

    def create(self, req: CategoryCreate) -> CategoryResponse:
        if self.repo.get_by_name(req.name):
            raise DuplicateResourceException("Tên danh mục này đã tồn tại")
        if self.repo.get_by_slug(req.slug):
            raise DuplicateResourceException("Slug danh mục này đã tồn tại")

        cat = Category(
            name=req.name.strip(),
            slug=req.slug.strip().lower(),
            description=req.description.strip() if req.description else None
        )
        created = self.repo.create(cat)
        return CategoryResponse.model_validate(created)
