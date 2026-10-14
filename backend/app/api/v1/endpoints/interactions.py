from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationParams, ResponseBase
from app.schemas.interaction import (
    FavoriteToggleResponse,
    InquiryCreate,
    InquiryResponse,
    InquiryStatusUpdate,
)
from app.schemas.listing import ListingCardResponse
from app.services.interaction_service import InteractionService

router = APIRouter()


@router.post(
    "/favorites/{listing_id}",
    response_model=ResponseBase[FavoriteToggleResponse],
    status_code=status.HTTP_200_OK,
    summary="Thêm hoặc xóa tin khỏi danh sách yêu thích",
    description="Người dùng đã đăng nhập: Bấm lần đầu là thêm vào yêu thích, bấm lần sau là hủy yêu thích."
)
def toggle_favorite(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[FavoriteToggleResponse]:
    service = InteractionService(db)
    result = service.toggle_favorite(user_id=current_user.id, listing_id=listing_id)
    return ResponseBase[FavoriteToggleResponse](
        success=True,
        data=result,
        message=result.message
    )


@router.get(
    "/favorites",
    response_model=ResponseBase[PaginatedResponse[ListingCardResponse]],
    status_code=status.HTTP_200_OK,
    summary="Xem danh sách tin bất động sản yêu thích",
    description="Người dùng đã đăng nhập: Lấy danh sách các tin BĐS đã lưu yêu thích."
)
def get_my_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[ListingCardResponse]]:
    pagination = PaginationParams(page=page, size=size)
    service = InteractionService(db)
    result = service.get_user_favorites(user_id=current_user.id, pagination=pagination)
    return ResponseBase[PaginatedResponse[ListingCardResponse]](
        success=True,
        data=result,
        message="Lấy danh sách yêu thích thành công"
    )


@router.post(
    "/inquiries",
    response_model=ResponseBase[InquiryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Gửi yêu cầu tư vấn / liên hệ cho người đăng",
    description="Khách xem (vãng lai hoặc đã đăng nhập) gửi form liên hệ cho chủ tin BĐS."
)
def send_inquiry(
    req: InquiryCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> ResponseBase[InquiryResponse]:
    seeker_id = current_user.id if current_user else None
    service = InteractionService(db)
    result = service.send_inquiry(seeker_id=seeker_id, req=req)
    return ResponseBase[InquiryResponse](
        success=True,
        data=result,
        message="Gửi yêu cầu tư vấn thành công. Người bán sẽ sớm liên hệ lại với bạn."
    )


@router.get(
    "/inquiries/received",
    response_model=ResponseBase[PaginatedResponse[InquiryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách khách hàng liên hệ tư vấn",
    description="Dành cho người đăng: Xem danh sách các yêu cầu tư vấn gửi đến các tin đăng của mình."
)
def get_received_inquiries(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: NEW, CONTACTED, CLOSED"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[InquiryResponse]]:
    pagination = PaginationParams(page=page, size=size)
    service = InteractionService(db)
    result = service.get_received_inquiries(
        seller_id=current_user.id,
        status=status,
        pagination=pagination
    )
    return ResponseBase[PaginatedResponse[InquiryResponse]](
        success=True,
        data=result,
        message="Lấy danh sách yêu cầu tư vấn thành công"
    )


@router.patch(
    "/inquiries/{inquiry_id}/status",
    response_model=ResponseBase[InquiryResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật trạng thái yêu cầu tư vấn",
    description="Dành cho người đăng: Đánh dấu yêu cầu tư vấn là CONTACTED (Đã liên hệ) hoặc CLOSED (Đóng)."
)
def update_inquiry_status(
    inquiry_id: int,
    req: InquiryStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ResponseBase[InquiryResponse]:
    service = InteractionService(db)
    result = service.update_inquiry_status(
        inquiry_id=inquiry_id,
        seller_id=current_user.id,
        new_status=req.status
    )
    return ResponseBase[InquiryResponse](
        success=True,
        data=result,
        message="Cập nhật trạng thái yêu cầu tư vấn thành công"
    )
