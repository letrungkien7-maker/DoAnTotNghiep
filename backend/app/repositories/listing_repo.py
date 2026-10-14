from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.listing import Listing, ListingStatus
from app.repositories.base_repo import BaseRepository


class ListingRepository(BaseRepository[Listing]):
    def __init__(self, db: Session):
        super().__init__(Listing, db)

    def get_detail(self, listing_id: int) -> Optional[Listing]:
        """Fetch listing with eager-loaded category, images, features, and owner."""
        stmt = (
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images),
                selectinload(Listing.features),
                selectinload(Listing.owner)
            )
            .where(Listing.id == listing_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def search_public(
        self,
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        bedrooms: Optional[int] = None,
        sort_by: str = "newest",
        offset: int = 0,
        limit: int = 12
    ) -> Tuple[List[Listing], int]:
        """
        Search public listings:
        Must be APPROVED and (expired_at is NULL or expired_at > now).
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images)
            )
            .where(
                Listing.status == ListingStatus.APPROVED.value,
                or_(Listing.expired_at.is_(None), Listing.expired_at > now)
            )
        )
        count_stmt = select(func.count(Listing.id)).where(
            Listing.status == ListingStatus.APPROVED.value,
            or_(Listing.expired_at.is_(None), Listing.expired_at > now)
        )

        if keyword:
            kw_pattern = f"%{keyword.strip()}%"
            cond = or_(
                Listing.title.ilike(kw_pattern),
                Listing.description.ilike(kw_pattern),
                Listing.address_text.ilike(kw_pattern)
            )
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if category_id:
            stmt = stmt.where(Listing.category_id == category_id)
            count_stmt = count_stmt.where(Listing.category_id == category_id)

        if transaction_type:
            stmt = stmt.where(Listing.transaction_type == transaction_type.upper())
            count_stmt = count_stmt.where(Listing.transaction_type == transaction_type.upper())

        if min_price is not None:
            stmt = stmt.where(Listing.price >= min_price)
            count_stmt = count_stmt.where(Listing.price >= min_price)

        if max_price is not None:
            stmt = stmt.where(Listing.price <= max_price)
            count_stmt = count_stmt.where(Listing.price <= max_price)

        if min_area is not None:
            stmt = stmt.where(Listing.area >= min_area)
            count_stmt = count_stmt.where(Listing.area >= min_area)

        if max_area is not None:
            stmt = stmt.where(Listing.area <= max_area)
            count_stmt = count_stmt.where(Listing.area <= max_area)

        if province:
            stmt = stmt.where(Listing.province.ilike(f"%{province.strip()}%"))
            count_stmt = count_stmt.where(Listing.province.ilike(f"%{province.strip()}%"))

        if district:
            stmt = stmt.where(Listing.district.ilike(f"%{district.strip()}%"))
            count_stmt = count_stmt.where(Listing.district.ilike(f"%{district.strip()}%"))

        if bedrooms is not None:
            stmt = stmt.where(Listing.bedrooms >= bedrooms)
            count_stmt = count_stmt.where(Listing.bedrooms >= bedrooms)

        # Ordering
        if sort_by == "price_asc":
            stmt = stmt.order_by(Listing.price.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Listing.price.desc())
        elif sort_by == "area_asc":
            stmt = stmt.order_by(Listing.area.asc())
        elif sort_by == "area_desc":
            stmt = stmt.order_by(Listing.area.desc())
        else:
            # Default newest
            stmt = stmt.order_by(Listing.published_at.desc().nullslast(), Listing.created_at.desc())

        total = self.db.execute(count_stmt).scalar() or 0
        items = self.db.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return list(items), total

    def get_my_listings(
        self,
        user_id: int,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10
    ) -> Tuple[List[Listing], int]:
        """Fetch all listings owned by a specific user across any status."""
        stmt = (
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images)
            )
            .where(Listing.user_id == user_id)
        )
        count_stmt = select(func.count(Listing.id)).where(Listing.user_id == user_id)

        if status:
            stmt = stmt.where(Listing.status == status.upper())
            count_stmt = count_stmt.where(Listing.status == status.upper())

        total = self.db.execute(count_stmt).scalar() or 0
        items = self.db.execute(
            stmt.order_by(Listing.created_at.desc()).offset(offset).limit(limit)
        ).scalars().all()
        return list(items), total

    def get_pending_listings(
        self,
        offset: int = 0,
        limit: int = 10
    ) -> Tuple[List[Listing], int]:
        """Fetch listings waiting for Admin moderation."""
        stmt = (
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images),
                selectinload(Listing.owner)
            )
            .where(Listing.status == ListingStatus.PENDING_APPROVAL.value)
        )
        count_stmt = select(func.count(Listing.id)).where(
            Listing.status == ListingStatus.PENDING_APPROVAL.value
        )

        total = self.db.execute(count_stmt).scalar() or 0
        items = self.db.execute(
            stmt.order_by(Listing.created_at.asc()).offset(offset).limit(limit)
        ).scalars().all()
        return list(items), total

    def increment_view_count(self, listing_id: int) -> None:
        """Increment view_count atomically."""
        listing = self.get_by_id(listing_id)
        if listing:
            listing.view_count += 1
            self.db.commit()
