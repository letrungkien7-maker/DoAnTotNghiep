from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Thao tác thành công"


class PaginationParams:
    """Dependency for extracting and validating pagination parameters."""
    def __init__(
        self,
        page: int = 1,
        size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ):
        self.page = max(1, page)
        self.size = min(max(1, size), 100)  # Clamp between 1 and 100
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "desc"

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int
