from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundException, PermissionDeniedException
from app.models.listing import Listing, ListingFeature, ListingImage, ListingStatus
from app.repositories.category_repo import CategoryRepository
from app.repositories.interaction_repo import InteractionRepository
from app.repositories.listing_repo import ListingRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.listing import (
    ListingCardResponse,
    ListingCreate,
    ListingDetailResponse,
    ListingImageDto,
    ListingUpdate,
)


def to_listing_card(listing: Listing) -> ListingCardResponse:
    """Helper to convert Listing model to ListingCardResponse."""
    thumbnail = None
    if listing.images:
        # Pick thumbnail if marked, else first image
        thumb_img = next((img for img in listing.images if img.is_thumbnail), listing.images[0])
        thumbnail = thumb_img.image_url

    return ListingCardResponse(
        id=listing.id,
        title=listing.title,
        price=float(listing.price),
        price_unit=listing.price_unit,
        area=float(listing.area),
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        address_text=listing.address_text,
        province=listing.province,
        district=listing.district,
        transaction_type=listing.transaction_type,
        category_id=listing.category_id,
        category_name=listing.category.name if listing.category else "",
        thumbnail_url=thumbnail,
        status=listing.status,
        view_count=listing.view_count,
        published_at=listing.published_at,
        created_at=listing.created_at
    )


class ListingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ListingRepository(db)
        self.cat_repo = CategoryRepository(db)
        self.interaction_repo = InteractionRepository(db)

    def create_listing(self, user_id: int, req: ListingCreate) -> ListingDetailResponse:
        """Create a new listing in DRAFT or PENDING_APPROVAL status."""
        cat = self.cat_repo.get_by_id(req.category_id)
        if not cat:
            raise NotFoundException("Danh mục bất động sản không tồn tại")

        initial_status = (
            ListingStatus.DRAFT.value if req.is_draft else ListingStatus.PENDING_APPROVAL.value
        )

        listing = Listing(
            user_id=user_id,
            category_id=req.category_id,
            title=req.title.strip(),
            description=req.description.strip(),
            transaction_type=req.transaction_type,
            price=req.price,
            price_unit=req.price_unit,
            area=req.area,
            bedrooms=req.bedrooms,
            bathrooms=req.bathrooms,
            direction=req.direction,
            legal_status=req.legal_status,
            address_text=req.address_text.strip(),
            province=req.province.strip(),
            district=req.district.strip(),
            ward=req.ward.strip() if req.ward else None,
            latitude=req.latitude,
            longitude=req.longitude,
            status=initial_status
        )
        self.db.add(listing)
        self.db.flush()

        # Add Features
        for feat in req.features:
            if feat.strip():
                f_obj = ListingFeature(listing_id=listing.id, feature_name=feat.strip())
                self.db.add(f_obj)

        # Add Images
        for idx, img_in in enumerate(req.images):
            img_obj = ListingImage(
                listing_id=listing.id,
                image_url=img_in.image_url.strip(),
                public_id=img_in.public_id.strip(),
                is_thumbnail=img_in.is_thumbnail or (idx == 0),
                display_order=img_in.display_order or idx
            )
            self.db.add(img_obj)

        self.db.commit()
        return self.get_detail(listing.id, current_user_id=user_id, session_id="owner")

    def update_listing(
        self,
        listing_id: int,
        user_id: int,
        is_admin: bool,
        req: ListingUpdate
    ) -> ListingDetailResponse:
        """Update listing. Ownership and status transition rules strictly enforced."""
        listing = self.repo.get_detail(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")

        # 1. Ownership check
        if listing.user_id != user_id and not is_admin:
            raise PermissionDeniedException("Bạn không có quyền chỉnh sửa tin đăng này")

        # 2. Status restriction: Cannot edit directly while in PENDING_APPROVAL
        if listing.status == ListingStatus.PENDING_APPROVAL.value and not is_admin:
            raise AppException(
                "Tin đăng đang chờ duyệt, không thể chỉnh sửa trực tiếp lúc này. "
                "Vui lòng đợi quản trị viên duyệt hoặc từ chối.",
                code="LISTING_LOCKED_PENDING",
                status_code=400
            )

        if req.category_id is not None:
            if not self.cat_repo.get_by_id(req.category_id):
                raise NotFoundException("Danh mục không tồn tại")
            listing.category_id = req.category_id

        if req.title is not None:
            listing.title = req.title.strip()
        if req.description is not None:
            listing.description = req.description.strip()
        if req.transaction_type is not None:
            listing.transaction_type = req.transaction_type
        if req.price is not None:
            listing.price = req.price
        if req.price_unit is not None:
            listing.price_unit = req.price_unit
        if req.area is not None:
            listing.area = req.area
        if req.bedrooms is not None:
            listing.bedrooms = req.bedrooms
        if req.bathrooms is not None:
            listing.bathrooms = req.bathrooms
        if req.direction is not None:
            listing.direction = req.direction
        if req.legal_status is not None:
            listing.legal_status = req.legal_status
        if req.address_text is not None:
            listing.address_text = req.address_text.strip()
        if req.province is not None:
            listing.province = req.province.strip()
        if req.district is not None:
            listing.district = req.district.strip()
        if req.ward is not None:
            listing.ward = req.ward.strip()
        if req.latitude is not None:
            listing.latitude = req.latitude
        if req.longitude is not None:
            listing.longitude = req.longitude

        # Update features if supplied
        if req.features is not None:
            listing.features.clear()
            for feat in req.features:
                if feat.strip():
                    listing.features.append(ListingFeature(listing_id=listing.id, feature_name=feat.strip()))

        # Update images if supplied
        if req.images is not None:
            listing.images.clear()
            for idx, img_in in enumerate(req.images):
                listing.images.append(ListingImage(
                    listing_id=listing.id,
                    image_url=img_in.image_url.strip(),
                    public_id=img_in.public_id.strip(),
                    is_thumbnail=img_in.is_thumbnail or (idx == 0),
                    display_order=img_in.display_order or idx
                ))

        # Check if re-submitting for approval from DRAFT or REJECTED
        if req.submit_for_approval:
            if len(listing.images) < 3:
                raise AppException(
                    "Nộp duyệt yêu cầu tối thiểu 3 hình ảnh.",
                    code="INSUFFICIENT_IMAGES",
                    status_code=422
                )
            listing.status = ListingStatus.PENDING_APPROVAL.value
            listing.rejection_reason = None

        self.db.commit()
        return self.get_detail(listing.id, current_user_id=user_id, session_id="owner")

    def delete_listing(self, listing_id: int, user_id: int, is_admin: bool) -> None:
        """Delete listing with ownership check."""
        listing = self.repo.get_by_id(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")
        if listing.user_id != user_id and not is_admin:
            raise PermissionDeniedException("Bạn không có quyền xóa tin đăng này")

        self.repo.delete(listing)

    def toggle_visibility(self, listing_id: int, user_id: int, is_hidden: bool) -> str:
        """Poster toggles hiding or unhiding their approved listing."""
        listing = self.repo.get_by_id(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")
        if listing.user_id != user_id:
            raise PermissionDeniedException("Chỉ chủ tin mới có quyền ẩn/hiện tin đăng này")

        if is_hidden:
            if listing.status != ListingStatus.APPROVED.value:
                raise AppException("Chỉ tin đang hoạt động (APPROVED) mới có thể chuyển sang ẩn")
            listing.status = ListingStatus.HIDDEN.value
            self.db.commit()
            return "Đã ẩn tin đăng khỏi trang tìm kiếm công khai"
        else:
            if listing.status != ListingStatus.HIDDEN.value:
                raise AppException("Chỉ tin đang ẩn (HIDDEN) mới có thể hiển thị lại")
            # If expired while hidden, don't allow unhiding without renewal
            now = datetime.now(timezone.utc)
            if listing.expired_at:
                exp = listing.expired_at if listing.expired_at.tzinfo else listing.expired_at.replace(tzinfo=timezone.utc)
                if exp <= now:
                    raise AppException("Tin đăng đã hết hạn, vui lòng gia hạn trước khi hiển thị lại")
            listing.status = ListingStatus.APPROVED.value
            self.db.commit()
            return "Đã hiển thị lại tin đăng trên sàn tìm kiếm"

    def renew_listing(self, listing_id: int, user_id: int) -> ListingDetailResponse:
        """Poster extends expired listing by 30 days."""
        listing = self.repo.get_by_id(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")
        if listing.user_id != user_id:
            raise PermissionDeniedException("Chỉ chủ tin mới có quyền gia hạn tin đăng này")

        now = datetime.now(timezone.utc)
        listing.published_at = now
        listing.expired_at = now + timedelta(days=30)
        listing.status = ListingStatus.APPROVED.value
        self.db.commit()
        return self.get_detail(listing.id, current_user_id=user_id, session_id="owner")

    def moderate_listing(
        self,
        listing_id: int,
        action: str,
        rejection_reason: Optional[str] = None
    ) -> ListingDetailResponse:
        """Admin moderates a pending listing."""
        listing = self.repo.get_detail(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")

        now = datetime.now(timezone.utc)
        if action == "APPROVE":
            listing.status = ListingStatus.APPROVED.value
            listing.published_at = now
            listing.expired_at = now + timedelta(days=30)
            listing.rejection_reason = None
        elif action == "REJECT":
            listing.status = ListingStatus.REJECTED.value
            listing.rejection_reason = rejection_reason
        else:
            raise AppException("Hành động duyệt không hợp lệ", code="INVALID_ACTION", status_code=400)

        self.db.commit()
        return self.get_detail(listing.id, current_user_id=None, session_id="admin")

    def get_detail(
        self,
        listing_id: int,
        current_user_id: Optional[int] = None,
        session_id: str = "guest"
    ) -> ListingDetailResponse:
        """Fetch listing detail, log view history, increment views, and mask seller phone for guests."""
        listing = self.repo.get_detail(listing_id)
        if not listing:
            raise NotFoundException("Tin đăng không tồn tại")

        # Visibility rule:
        # If not APPROVED, only the owner or an admin can view it
        if listing.status != ListingStatus.APPROVED.value:
            is_owner = (current_user_id is not None and current_user_id == listing.user_id)
            is_admin = (session_id == "admin")
            if not (is_owner or is_admin):
                raise NotFoundException("Tin đăng không tồn tại hoặc chưa được phê duyệt công khai")

        # Record view history and increment view_count
        if session_id not in ["owner", "admin"]:
            self.repo.increment_view_count(listing.id)
            self.interaction_repo.log_view(
                listing_id=listing.id,
                user_id=current_user_id,
                session_id=session_id
            )

        # Mask phone number for guest visitors (BR-05)
        raw_phone = listing.owner.phone_number if listing.owner else ""
        if current_user_id is not None:
            display_phone = raw_phone
        else:
            # Mask phone for guests (e.g. 0912.xxx.xxx)
            display_phone = f"{raw_phone[:4]}.xxx.xxx" if len(raw_phone) >= 4 else "0xxx.xxx.xxx"

        is_fav = False
        if current_user_id:
            is_fav = self.interaction_repo.is_favorited(current_user_id, listing.id)

        images_dto = [ListingImageDto.model_validate(img) for img in listing.images]
        features_list = [f.feature_name for f in listing.features]

        return ListingDetailResponse(
            id=listing.id,
            user_id=listing.user_id,
            title=listing.title,
            description=listing.description,
            category_id=listing.category_id,
            category_name=listing.category.name if listing.category else "",
            transaction_type=listing.transaction_type,
            price=float(listing.price),
            price_unit=listing.price_unit,
            area=float(listing.area),
            bedrooms=listing.bedrooms,
            bathrooms=listing.bathrooms,
            direction=listing.direction,
            legal_status=listing.legal_status,
            address_text=listing.address_text,
            province=listing.province,
            district=listing.district,
            ward=listing.ward,
            latitude=listing.latitude,
            longitude=listing.longitude,
            status=listing.status,
            rejection_reason=listing.rejection_reason,
            view_count=listing.view_count,
            published_at=listing.published_at,
            expired_at=listing.expired_at,
            created_at=listing.created_at,
            updated_at=listing.updated_at,
            images=images_dto,
            features=features_list,
            owner_id=listing.user_id,
            owner_name=listing.owner.full_name if listing.owner else "Chủ tin",
            owner_phone=display_phone,
            owner_avatar=listing.owner.avatar_url if listing.owner else None,
            is_favorite=is_fav
        )

    def search_public(
        self,
        keyword: Optional[str],
        category_id: Optional[int],
        transaction_type: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        min_area: Optional[float],
        max_area: Optional[float],
        province: Optional[str],
        district: Optional[str],
        bedrooms: Optional[int],
        sort_by: str,
        pagination: PaginationParams
    ) -> PaginatedResponse[ListingCardResponse]:
        items, total = self.repo.search_public(
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

    def get_my_listings(
        self,
        user_id: int,
        status: Optional[str],
        pagination: PaginationParams
    ) -> PaginatedResponse[ListingCardResponse]:
        items, total = self.repo.get_my_listings(
            user_id=user_id,
            status=status,
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

    def get_pending_listings(
        self,
        pagination: PaginationParams
    ) -> PaginatedResponse[ListingCardResponse]:
        items, total = self.repo.get_pending_listings(
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
