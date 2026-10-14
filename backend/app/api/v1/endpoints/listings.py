from typing import Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationParams, ResponseBase
from app.schemas.listing import (
    ListingCardResponse,
    ListingCreate,
    ListingDetailResponse,
    ListingUpdate,
    ListingVisibilityUpdate,
)
from app.services.listing_service import ListingService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseBase[PaginatedResponse[ListingCardResponse]],
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm & lọc bất động sản công khai",
    description="Công khai: Chỉ hiển thị các tin ở trạng thái APPROVED và chưa hết hạn."
)
def search_listings(
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    category_id: Optional[int] = Query(None, description="Lọc theo loại hình BĐS"),
    transaction_type: Optional[str] = Query(None, description="SALE hoặc RENT"),
    min_price: Optional[float] = Query(None, ge=0, description="Mức giá tối thiểu"),
    max_price: Optional[float] = Query(None, ge=0, description="Mức giá tối đa"),
    min_area: Optional[float] = Query(None, ge=0, description="Diện tích tối thiểu m²"),
    max_area: Optional[float] = Query(None, ge=0, description="Diện tích tối đa m²"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố"),
    district: Optional[str] = Query(None, description="Quận / Huyện"),
    bedrooms: Optional[int] = Query(None, ge=0, description="Số phòng ngủ tối thiểu"),
    sort_by: str = Query("newest", description="Sắp xếp: newest, price_asc, price_desc, area_asc, area_desc"),
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(12, ge=1, le=50, description="Số lượng mỗi trang"),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[ListingCardResponse]]:
    pagination = PaginationParams(page=page, size=size)
    service = ListingService(db)
    result = service.search_public(
        keyword=keyword,
        category_id=category_id,
        transaction_type=transaction_type,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        province=province,
        district=district,
        bedrooms=bedrooms,
        sort_by=sort_by,
        pagination=pagination
    )
    return ResponseBase[PaginatedResponse[ListingCardResponse]](
        success=True,
        data=result,
        message="Tìm kiếm bất động sản thành công"
    )


@router.get(
    "/my/all",
    response_model=ResponseBase[PaginatedResponse[ListingCardResponse]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách tin đăng của cá nhân",
    description="Dành cho người đăng: Xem toàn bộ tin của mình (DRAFT, PENDING, APPROVED, REJECTED, EXPIRED, HIDDEN)."
)
def get_my_listings(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái cụ thể"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[ListingCardResponse]]:
    pagination = PaginationParams(page=page, size=size)
    service = ListingService(db)
    result = service.get_my_listings(
        user_id=current_user.id,
        status=status,
        pagination=pagination
    )
    return ResponseBase[PaginatedResponse[ListingCardResponse]](
        success=True,
        data=result,
        message="Lấy danh sách tin cá nhân thành công"
    )


@router.get(
    "/{listing_id}",
    response_model=ResponseBase[ListingDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết bất động sản",
    description="Xem chi tiết tin đăng. Số điện thoại người bán sẽ được che với khách vãng lai (BR-05)."
)
def get_listing_detail(
    listing_id: int,
    x_session_id: Optional[str] = Header(None, description="Client Session ID cho thống kê lượt xem"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> ResponseBase[ListingDetailResponse]:
    session_id = x_session_id or "web_guest"
    user_id = current_user.id if current_user else None
    service = ListingService(db)
    detail = service.get_detail(
        listing_id=listing_id,
        current_user_id=user_id,
        session_id=session_id
    )
    return ResponseBase[ListingDetailResponse](
        success=True,
        data=detail,
        message="Lấy chi tiết tin đăng thành công"
    )


@router.post(
    "",
    response_model=ResponseBase[ListingDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng tin bất động sản mới",
    description="Người dùng đăng tin mới. Nếu is_draft=True sẽ lưu nháp; nếu is_draft=False cần tối thiểu 3 ảnh và sẽ vào trạng thái PENDING_APPROVAL."
)
def create_listing(
    req: ListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[ListingDetailResponse]:
    service = ListingService(db)
    created = service.create_listing(user_id=current_user.id, req=req)
    return ResponseBase[ListingDetailResponse](
        success=True,
        data=created,
        message="Tạo tin đăng thành công"
    )


@router.put(
    "/{listing_id}",
    response_model=ResponseBase[ListingDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Chỉnh sửa tin đăng",
    description="Chỉ chủ sở hữu tin mới có quyền sửa. Tin đang ở trạng thái PENDING_APPROVAL bị khóa chỉnh sửa trực tiếp."
)
def update_listing(
    listing_id: int,
    req: ListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[ListingDetailResponse]:
    service = ListingService(db)
    updated = service.update_listing(
        listing_id=listing_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin(),
        req=req
    )
    return ResponseBase[ListingDetailResponse](
        success=True,
        data=updated,
        message="Cập nhật tin đăng thành công"
    )


@router.delete(
    "/{listing_id}",
    response_model=ResponseBase[dict],
    status_code=status.HTTP_200_OK,
    summary="Xóa tin đăng",
    description="Chỉ chủ sở hữu hoặc Quản trị viên mới có quyền xóa tin đăng."
)
def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[dict]:
    service = ListingService(db)
    service.delete_listing(
        listing_id=listing_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin()
    )
    return ResponseBase[dict](
        success=True,
        data={"deleted_listing_id": listing_id},
        message="Xóa tin đăng thành công"
    )


@router.patch(
    "/{listing_id}/visibility",
    response_model=ResponseBase[dict],
    status_code=status.HTTP_200_OK,
    summary="Ẩn hoặc hiển thị lại tin đăng",
    description="Chủ tin chủ động ẩn tin (khi đã bán/cho thuê) hoặc mở lại tin."
)
def toggle_visibility(
    listing_id: int,
    req: ListingVisibilityUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[dict]:
    service = ListingService(db)
    msg = service.toggle_visibility(
        listing_id=listing_id,
        user_id=current_user.id,
        is_hidden=req.is_hidden
    )
    return ResponseBase[dict](
        success=True,
        data={"is_hidden": req.is_hidden},
        message=msg
    )


@router.post(
    "/{listing_id}/renew",
    response_model=ResponseBase[ListingDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Gia hạn tin đăng hết hạn (+30 ngày)",
    description="Chủ tin gia hạn tin đăng đã hết hạn để tiếp tục hiển thị thêm 30 ngày."
)
def renew_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[ListingDetailResponse]:
    service = ListingService(db)
    renewed = service.renew_listing(listing_id=listing_id, user_id=current_user.id)
    return ResponseBase[ListingDetailResponse](
        success=True,
        data=renewed,
        message="Gia hạn tin đăng thành công thêm 30 ngày"
    )
