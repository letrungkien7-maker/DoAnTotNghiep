from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import Base, User, UserRole

# In-memory SQLite database specifically configured for fast, isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean isolated database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a TestClient with get_db overridden to use our test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create and return a standard test user."""
    user = User(
        email="user@test.com",
        password_hash=hash_password("UserPassword123!"),
        full_name="Nguyễn Văn User",
        phone_number="0912345678",
        role=UserRole.USER.value,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session) -> User:
    """Create and return an administrator test user."""
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("AdminPassword123!"),
        full_name="Trần Thị Admin",
        phone_number="0987654321",
        role=UserRole.ADMIN.value,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Create and return a locked / inactive test user."""
    user = User(
        email="inactive@test.com",
        password_hash=hash_password("UserPassword123!"),
        full_name="Lê Khóa Tài Khoản",
        phone_number="0900000000",
        role=UserRole.USER.value,
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token_headers(test_user: User) -> dict:
    """Generate Bearer Authorization header for regular user."""
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers(test_admin: User) -> dict:
    """Generate Bearer Authorization header for admin."""
    token = create_access_token(
        data={"sub": str(test_admin.id), "email": test_admin.email, "role": test_admin.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_2(db_session: Session) -> User:
    """Create and return a second independent regular user."""
    user = User(
        email="user2@test.com",
        password_hash=hash_password("User2Password123!"),
        full_name="Nguyễn Văn User 2",
        phone_number="0922334455",
        role=UserRole.USER.value,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user2_token_headers(test_user_2: User) -> dict:
    """Generate Bearer Authorization header for user 2."""
    token = create_access_token(
        data={"sub": str(test_user_2.id), "email": test_user_2.email, "role": test_user_2.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_category(db_session: Session):
    """Create and return a sample property category."""
    from app.models.listing import Category
    cat = Category(
        name="Căn hộ chung cư",
        slug="can-ho-chung-cu",
        description="Chung cư thương mại"
    )
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture
def approved_listing(db_session: Session, test_user: User, sample_category):
    """Create and return an approved listing with images."""
    from datetime import datetime, timedelta, timezone

    from app.models.listing import (
        Listing,
        ListingFeature,
        ListingImage,
        ListingStatus,
        TransactionType,
    )
    now = datetime.now(timezone.utc)
    listing = Listing(
        user_id=test_user.id,
        category_id=sample_category.id,
        title="Căn hộ cao cấp 2 phòng ngủ Royal City",
        description="Căn hộ tầng trung thoáng mát đầy đủ tiện nghi, view thành phố tuyệt đẹp.",
        transaction_type=TransactionType.SALE.value,
        price=4500000000.0,
        price_unit="TOTAL",
        area=75.0,
        bedrooms=2,
        bathrooms=2,
        address_text="72A Nguyễn Trãi",
        province="Hà Nội",
        district="Thanh Xuân",
        status=ListingStatus.APPROVED.value,
        published_at=now - timedelta(days=1),
        expired_at=now + timedelta(days=29)
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)

    db_session.add_all([
        ListingImage(listing_id=listing.id, image_url="https://cloudinary.com/img1.jpg", public_id="img1", is_thumbnail=True, display_order=0),
        ListingImage(listing_id=listing.id, image_url="https://cloudinary.com/img2.jpg", public_id="img2", is_thumbnail=False, display_order=1),
        ListingImage(listing_id=listing.id, image_url="https://cloudinary.com/img3.jpg", public_id="img3", is_thumbnail=False, display_order=2),
        ListingFeature(listing_id=listing.id, feature_name="Ban công rộng"),
    ])
    db_session.commit()
    db_session.refresh(listing)
    return listing

