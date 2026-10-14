from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import PK_BIGINT, Base

if TYPE_CHECKING:
    from app.models.interaction import Favorite, Inquiry, UserViewHistory
    from app.models.user import User


class TransactionType(str, Enum):
    SALE = "SALE"
    RENT = "RENT"


class ListingStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    HIDDEN = "HIDDEN"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    listings: Mapped[List["Listing"]] = relationship("Listing", back_populates="category")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(PK_BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(10), default=TransactionType.SALE.value, nullable=False)

    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    price_unit: Mapped[str] = mapped_column(String(20), default="TOTAL", nullable=False)
    area: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)

    bedrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    legal_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    address_text: Mapped[str] = mapped_column(String(255), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    ward: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default=ListingStatus.PENDING_APPROVAL.value, index=True, nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="listings")
    category: Mapped["Category"] = relationship("Category", back_populates="listings")
    images: Mapped[List["ListingImage"]] = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    features: Mapped[List["ListingFeature"]] = relationship("ListingFeature", back_populates="listing", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="listing", cascade="all, delete-orphan")
    inquiries: Mapped[List["Inquiry"]] = relationship("Inquiry", back_populates="listing", cascade="all, delete-orphan")
    views: Mapped[List["UserViewHistory"]] = relationship("UserViewHistory", back_populates="listing", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_listings_status_expired", "status", "expired_at"),
        Index("idx_listings_location", "province", "district"),
    )


class ListingImage(Base):
    __tablename__ = "listing_images"

    id: Mapped[int] = mapped_column(PK_BIGINT, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    public_id: Mapped[str] = mapped_column(String(100), nullable=False)
    is_thumbnail: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="images")


class ListingFeature(Base):
    __tablename__ = "listing_features"

    id: Mapped[int] = mapped_column(PK_BIGINT, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="features")
