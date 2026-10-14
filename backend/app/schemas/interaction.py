from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FavoriteToggleResponse(BaseModel):
    listing_id: int
    is_favorited: bool
    message: str


class InquiryCreate(BaseModel):
    listing_id: int = Field(..., description="ID bất động sản cần liên hệ")
    sender_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên người gửi")
    sender_phone: str = Field(..., min_length=9, max_length=15, description="Số điện thoại liên hệ")
    sender_email: Optional[EmailStr] = Field(None, description="Email nhận phản hồi")
    message: str = Field(..., min_length=10, max_length=1000, description="Nội dung lời nhắn tư vấn")


class InquiryResponse(BaseModel):
    id: int
    listing_id: int
    listing_title: str
    seeker_id: Optional[int] = None
    sender_name: str
    sender_phone: str
    sender_email: Optional[str] = None
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InquiryStatusUpdate(BaseModel):
    status: Literal["CONTACTED", "CLOSED"] = Field(..., description="Đã liên hệ hoặc Đóng yêu cầu")
