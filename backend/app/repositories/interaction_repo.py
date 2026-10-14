from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.interaction import Favorite, Inquiry, UserViewHistory
from app.models.listing import Listing


class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    # 1. Favorites
    def is_favorited(self, user_id: int, listing_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def toggle_favorite(self, user_id: int, listing_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id
        )
        existing = self.db.execute(stmt).scalar_one_or_none()
        if existing:
            self.db.delete(existing)
            self.db.commit()
            return False
        else:
            new_fav = Favorite(user_id=user_id, listing_id=listing_id)
            self.db.add(new_fav)
            self.db.commit()
            return True

    def get_user_favorites(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 10
    ) -> Tuple[List[Listing], int]:
        stmt = (
            select(Listing)
            .join(Favorite, Favorite.listing_id == Listing.id)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images)
            )
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        count_stmt = (
            select(func.count(Favorite.id))
            .where(Favorite.user_id == user_id)
        )
        total = self.db.execute(count_stmt).scalar() or 0
        items = self.db.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return list(items), total

    # 2. View History
    def log_view(
        self,
        listing_id: int,
        user_id: Optional[int],
        session_id: str,
        duration_seconds: int = 0
    ) -> None:
        view_record = UserViewHistory(
            listing_id=listing_id,
            user_id=user_id,
            session_id=session_id,
            duration_seconds=duration_seconds
        )
        self.db.add(view_record)
        self.db.commit()

    # 3. Inquiries
    def create_inquiry(self, inquiry: Inquiry) -> Inquiry:
        self.db.add(inquiry)
        self.db.commit()
        self.db.refresh(inquiry)
        return inquiry

    def get_inquiry_by_id(self, inquiry_id: int) -> Optional[Inquiry]:
        stmt = (
            select(Inquiry)
            .options(selectinload(Inquiry.listing))
            .where(Inquiry.id == inquiry_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_inquiries_for_seller(
        self,
        seller_id: int,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10
    ) -> Tuple[List[Inquiry], int]:
        stmt = (
            select(Inquiry)
            .join(Listing, Listing.id == Inquiry.listing_id)
            .options(selectinload(Inquiry.listing))
            .where(Listing.user_id == seller_id)
        )
        count_stmt = (
            select(func.count(Inquiry.id))
            .join(Listing, Listing.id == Inquiry.listing_id)
            .where(Listing.user_id == seller_id)
        )

        if status:
            stmt = stmt.where(Inquiry.status == status.upper())
            count_stmt = count_stmt.where(Inquiry.status == status.upper())

        total = self.db.execute(count_stmt).scalar() or 0
        items = self.db.execute(
            stmt.order_by(Inquiry.created_at.desc()).offset(offset).limit(limit)
        ).scalars().all()
        return list(items), total

    def update_inquiry_status(self, inquiry: Inquiry, status: str) -> Inquiry:
        inquiry.status = status
        self.db.commit()
        self.db.refresh(inquiry)
        return inquiry
