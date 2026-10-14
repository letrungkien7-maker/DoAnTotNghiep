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
