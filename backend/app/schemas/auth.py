from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email đăng nhập của người dùng")
    password: str = Field(..., min_length=8, max_length=72, description="Mật khẩu tối thiểu 8 ký tự")
    full_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên người dùng")
    phone_number: str = Field(..., min_length=9, max_length=15, description="Số điện thoại liên hệ")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., min_length=1, max_length=72, description="Mật khẩu tài khoản")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
