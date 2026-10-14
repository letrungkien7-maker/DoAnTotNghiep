from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundException, PermissionDeniedException
from app.models.interaction import Inquiry
from app.models.listing import ListingStatus
from app.repositories.interaction_repo import InteractionRepository
from app.repositories.listing_repo import ListingRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.interaction import FavoriteToggleResponse, InquiryCreate, InquiryResponse
from app.schemas.listing import ListingCardResponse
from app.services.listing_service import to_listing_card


class InteractionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InteractionRepository(db)
        self.listing_repo = ListingRepository(db)

    def toggle_favorite(self, user_id: int, listing_id: int) -> FavoriteToggleResponse:
        listing = self.listing_repo.get_by_id(listing_id)
        if not listing or listing.status != ListingStatus.APPROVED.value:
            raise NotFoundException("Tin đăng không tồn tại hoặc chưa công khai")

        is_fav = self.repo.toggle_favorite(user_id, listing_id)
        msg = "Đã lưu tin vào danh sách yêu thích" if is_fav else "Đã xóa tin khỏi danh sách yêu thích"
        return FavoriteToggleResponse(
            listing_id=listing_id,
            is_favorited=is_fav,
            message=msg
        )

    def get_user_favorites(
        self,
        user_id: int,
        pagination: PaginationParams
    ) -> PaginatedResponse[ListingCardResponse]:
        items, total = self.repo.get_user_favorites(
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.size
        )
        total_pages = (total + pagination.size - 1) // pagination.size if total > 0 else 0
        return PaginatedResponse[ListingCardResponse](
            items=[to_listing_card(item) for item in items],
            total=total,
            page=pagination.page,
            size=pagination.size,
            total_pages=total_pages
        )

    def send_inquiry(
        self,
        seeker_id: Optional[int],
        req: InquiryCreate
    ) -> InquiryResponse:
        listing = self.listing_repo.get_by_id(req.listing_id)
        if not listing or listing.status != ListingStatus.APPROVED.value:
            raise NotFoundException("Tin đăng không tồn tại hoặc đã hết hạn")

        if seeker_id and listing.user_id == seeker_id:
            raise AppException(
                "Bạn không thể gửi yêu cầu tư vấn cho chính bất động sản của mình",
                code="SELF_INQUIRY_NOT_ALLOWED",
                status_code=400
            )

        inquiry = Inquiry(
            listing_id=req.listing_id,
            seeker_id=seeker_id,
            sender_name=req.sender_name.strip(),
            sender_phone=req.sender_phone.strip(),
            sender_email=req.sender_email.strip() if req.sender_email else None,
            message=req.message.strip()
        )
        created = self.repo.create_inquiry(inquiry)
        return InquiryResponse(
            id=created.id,
            listing_id=created.listing_id,
            listing_title=listing.title,
            seeker_id=created.seeker_id,
            sender_name=created.sender_name,
            sender_phone=created.sender_phone,
            sender_email=created.sender_email,
            message=created.message,
            status=created.status,
            created_at=created.created_at
        )

    def get_received_inquiries(
        self,
        seller_id: int,
        status: Optional[str],
        pagination: PaginationParams
    ) -> PaginatedResponse[InquiryResponse]:
        items, total = self.repo.get_inquiries_for_seller(
            seller_id=seller_id,
            status=status,
            offset=pagination.offset,
            limit=pagination.size
        )
        total_pages = (total + pagination.size - 1) // pagination.size if total > 0 else 0
        return PaginatedResponse[InquiryResponse](
            items=[
                InquiryResponse(
                    id=inq.id,
                    listing_id=inq.listing_id,
                    listing_title=inq.listing.title if inq.listing else "",
                    seeker_id=inq.seeker_id,
                    sender_name=inq.sender_name,
                    sender_phone=inq.sender_phone,
                    sender_email=inq.sender_email,
                    message=inq.message,
                    status=inq.status,
                    created_at=inq.created_at
                )
                for inq in items
            ],
            total=total,
            page=pagination.page,
            size=pagination.size,
            total_pages=total_pages
        )

    def update_inquiry_status(
        self,
        inquiry_id: int,
        seller_id: int,
        new_status: str
    ) -> InquiryResponse:
        inquiry = self.repo.get_inquiry_by_id(inquiry_id)
        if not inquiry:
            raise NotFoundException("Yêu cầu liên hệ không tồn tại")

        if not inquiry.listing or inquiry.listing.user_id != seller_id:
            raise PermissionDeniedException("Bạn không phải là chủ tin sở hữu yêu cầu liên hệ này")

        updated = self.repo.update_inquiry_status(inquiry, new_status)
        return InquiryResponse(
            id=updated.id,
            listing_id=updated.listing_id,
            listing_title=updated.listing.title if updated.listing else "",
            seeker_id=updated.seeker_id,
            sender_name=updated.sender_name,
            sender_phone=updated.sender_phone,
            sender_email=updated.sender_email,
            message=updated.message,
            status=updated.status,
            created_at=updated.created_at
        )
