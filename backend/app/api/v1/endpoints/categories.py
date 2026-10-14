from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.common import ResponseBase
from app.services.category_service import CategoryService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseBase[List[CategoryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh mục loại hình bất động sản",
    description="Công khai: Lấy danh sách toàn bộ danh mục BĐS hiện có."
)
def list_categories(
    db: Session = Depends(get_db)
) -> ResponseBase[List[CategoryResponse]]:
    service = CategoryService(db)
    items = service.list_all()
    return ResponseBase[List[CategoryResponse]](
        success=True,
        data=items,
        message="Lấy danh mục thành công"
    )


@router.post(
    "",
    response_model=ResponseBase[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Tạo danh mục mới",
    description="Chỉ dành cho Quản trị viên: Thêm loại hình BĐS mới."
)
def create_category(
    req: CategoryCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> ResponseBase[CategoryResponse]:
    service = CategoryService(db)
    created = service.create(req)
    return ResponseBase[CategoryResponse](
        success=True,
        data=created,
        message="Tạo danh mục thành công"
    )
