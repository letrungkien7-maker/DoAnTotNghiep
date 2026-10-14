from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    CredentialsException,
    DuplicateResourceException,
    InactiveUserException,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, req: RegisterRequest) -> User:
        """Register a new user account. Role is strictly assigned as USER."""
        existing_user = self.user_repo.get_by_email(req.email)
        if existing_user:
            raise DuplicateResourceException("Email này đã được đăng ký trên hệ thống")

        user = User(
            email=req.email.lower().strip(),
            password_hash=hash_password(req.password),
            full_name=req.full_name.strip(),
            phone_number=req.phone_number.strip(),
            role=UserRole.USER.value,  # Strict assignment: Never trust client role
            is_active=True
        )
        return self.user_repo.create(user)

    def authenticate(self, req: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and return JWT bearer token."""
        user = self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise CredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=expires_minutes)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_minutes * 60,
            user=UserResponse.model_validate(user)
        )
