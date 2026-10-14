from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ListingImageDto(BaseModel):
    id: int
    image_url: str
    public_id: str
    is_thumbnail: bool
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class ListingImageCreate(BaseModel):
    image_url: str = Field(..., description="URL ảnh lưu trữ trên Cloudinary hoặc CDN")
    public_id: str = Field(..., description="ID định danh ảnh trên Cloudinary")
    is_thumbnail: bool = False
    display_order: int = 0

    @field_validator("image_url")
    @classmethod
    def validate_image_extension(cls, v: str) -> str:
        clean = v.lower().split("?")[0]
        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        if not any(clean.endswith(ext) for ext in valid_exts) and "cloudinary.com" not in clean and "images" not in clean:
            raise ValueError("Định dạng ảnh không hợp lệ. Chỉ chấp nhận JPG, JPEG, PNG, WEBP.")
        return v


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=20, max_length=200, description="Tiêu đề tin từ 20 đến 200 ký tự")
    description: str = Field(..., min_length=50, max_length=3000, description="Mô tả chi tiết từ 50 đến 3000 ký tự")
    category_id: int = Field(..., description="ID danh mục BĐS")
    transaction_type: Literal["SALE", "RENT"] = Field("SALE", description="Bán hoặc Cho thuê")

    price: float = Field(..., gt=0, description="Mức giá niêm yết (phải lớn hơn 0)")
    price_unit: str = Field("TOTAL", description="Đơn vị tính: TOTAL (tổng giá), MONTH (thuê/tháng)")
    area: float = Field(..., gt=0, description="Diện tích tính bằng m² (phải lớn hơn 0)")

    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    direction: Optional[str] = Field(None, max_length=50)
    legal_status: Optional[str] = Field(None, max_length=100)

    address_text: str = Field(..., min_length=3, max_length=255)
    province: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    ward: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    features: List[str] = Field(default_factory=list, description="Danh sách tiện ích")
    images: List[ListingImageCreate] = Field(default_factory=list, description="Danh sách ảnh BĐS")
    is_draft: bool = Field(False, description="True nếu muốn lưu bản nháp, False nếu nộp duyệt")

    @model_validator(mode="after")
    def validate_submission_images(self) -> "ListingCreate":
        if not self.is_draft:
            if len(self.images) < 3:
                raise ValueError("Tin đăng nộp duyệt yêu cầu tối thiểu 3 hình ảnh minh họa.")
            if len(self.images) > 10:
                raise ValueError("Tin đăng cho phép tối đa 10 hình ảnh minh họa.")
        return self


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=20, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=3000)
    category_id: Optional[int] = None
    transaction_type: Optional[Literal["SALE", "RENT"]] = None

    price: Optional[float] = Field(None, gt=0)
    price_unit: Optional[str] = None
    area: Optional[float] = Field(None, gt=0)

    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    direction: Optional[str] = None
    legal_status: Optional[str] = None

    address_text: Optional[str] = Field(None, min_length=3, max_length=255)
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    features: Optional[List[str]] = None
    images: Optional[List[ListingImageCreate]] = None
    submit_for_approval: bool = Field(False, description="True nếu muốn nộp duyệt lại tin từ DRAFT hoặc REJECTED")

    @model_validator(mode="after")
    def validate_resubmission(self) -> "ListingUpdate":
        if self.submit_for_approval and self.images is not None:
            if len(self.images) < 3:
                raise ValueError("Nộp duyệt yêu cầu tối thiểu 3 hình ảnh.")
            if len(self.images) > 10:
                raise ValueError("Tối đa 10 hình ảnh.")
        return self


class ListingCardResponse(BaseModel):
    id: int
    title: str
    price: float
    price_unit: str
    area: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    address_text: str
    province: str
    district: str
    transaction_type: str
    category_id: int
    category_name: str
    thumbnail_url: Optional[str] = None
    status: str
    view_count: int
    published_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ListingDetailResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category_id: int
    category_name: str
    transaction_type: str

    price: float
    price_unit: str
    area: float

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    direction: Optional[str] = None
    legal_status: Optional[str] = None

    address_text: str
    province: str
    district: str
    ward: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    status: str
    rejection_reason: Optional[str] = None
    view_count: int
    published_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    images: List[ListingImageDto] = []
    features: List[str] = []

    # Seller info (Phone number can be masked for guests)
    owner_id: int
    owner_name: str
    owner_phone: str
    owner_avatar: Optional[str] = None
    is_favorite: bool = False

    model_config = ConfigDict(from_attributes=True)


class ListingModerateRequest(BaseModel):
    action: Literal["APPROVE", "REJECT"] = Field(..., description="Quyết định duyệt hoặc từ chối tin")
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Lý do từ chối nếu action là REJECT")

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "ListingModerateRequest":
        if self.action == "REJECT":
            if not self.rejection_reason or len(self.rejection_reason.strip()) < 5:
                raise ValueError("Vui lòng cung cấp lý do từ chối cụ thể (tối thiểu 5 ký tự).")
        return self


class ListingVisibilityUpdate(BaseModel):
    is_hidden: bool = Field(..., description="Ẩn (True) hoặc Hiển thị lại (False) tin đăng")
