from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone_number: str
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=9, max_length=15)
    avatar_url: Optional[str] = Field(None, max_length=255)


class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Khóa (false) hoặc Kích hoạt (true) tài khoản")
