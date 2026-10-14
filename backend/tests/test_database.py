import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Category,
    Favorite,
    Inquiry,
    Listing,
    ListingImage,
    TransactionType,
    User,
)


def test_database_models_relationships(db_session: Session, test_user: User):
    """Test creating Category, Listing, ListingImage, and verifying ORM relationships."""
    # 1. Create Category
    cat = Category(
        name="Căn hộ chung cư",
        slug="can-ho-chung-cu",
        description="Chung cư thương mại"
    )
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)

    # 2. Create Listing owned by test_user
    listing = Listing(
        user_id=test_user.id,
        category_id=cat.id,
        title="Bán căn hộ 2 phòng ngủ Vinhomes",
        description="Căn hộ full nội thất cao cấp",
        transaction_type=TransactionType.SALE.value,
        price=3200000000.0,
        price_unit="TOTAL",
        area=68.5,
        bedrooms=2,
        bathrooms=2,
        address_text="Số 1 Đại lộ Thăng Long",
        province="Hà Nội",
        district="Nam Từ Liêm"
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)

    # 3. Add Image
    img = ListingImage(
        listing_id=listing.id,
        image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        public_id="sample_public_id",
        is_thumbnail=True,
        display_order=0
    )
    db_session.add(img)
    db_session.commit()

    # 4. Add Inquiry
    inquiry = Inquiry(
        listing_id=listing.id,
        seeker_id=test_user.id,
        sender_name="Khách Mua Nhà",
        sender_phone="0911223344",
        message="Tôi muốn đặt lịch xem nhà vào cuối tuần"
    )
    db_session.add(inquiry)
    db_session.commit()

    # Assertions on relationships
    db_session.refresh(listing)
    assert len(listing.images) == 1
    assert listing.images[0].public_id == "sample_public_id"
    assert listing.owner.email == test_user.email
    assert len(listing.inquiries) == 1


def test_favorite_unique_constraint(db_session: Session, test_user: User):
    """Test that a user cannot favorite the exact same listing twice."""
    cat = Category(name="Nhà Phố", slug="nha-pho")
    db_session.add(cat)
    db_session.commit()

    listing = Listing(
        user_id=test_user.id,
        category_id=cat.id,
        title="Nhà mặt phố Cầu Giấy",
        description="Vị trí đắc địa kinh doanh",
        price=12000000000.0,
        area=80.0,
        address_text="123 Cầu Giấy",
        province="Hà Nội",
        district="Cầu Giấy"
    )
    db_session.add(listing)
    db_session.commit()

    fav1 = Favorite(user_id=test_user.id, listing_id=listing.id)
    db_session.add(fav1)
    db_session.commit()

    # Adding a duplicate favorite must raise IntegrityError
    fav2 = Favorite(user_id=test_user.id, listing_id=listing.id)
    db_session.add(fav2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
