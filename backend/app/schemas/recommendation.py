from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class RecommendationCriteria(BaseModel):
    transaction_type: Optional[Literal["SALE", "RENT"]] = Field(
        "SALE", description="Hình thức giao dịch: SALE (Bán) hoặc RENT (Cho thuê)"
    )
    category_id: Optional[int] = Field(None, description="ID loại hình bất động sản mong muốn")
    province: Optional[str] = Field(None, description="Tỉnh/Thành phố tìm kiếm")
    district: Optional[str] = Field(None, description="Quận/Huyện ưu tiên")

    budget_min: Optional[float] = Field(None, ge=0, description="Mức ngân sách tối thiểu (VNĐ)")
    budget_max: Optional[float] = Field(None, ge=0, description="Mức ngân sách tối đa (VNĐ)")
    target_price: Optional[float] = Field(None, ge=0, description="Giá mục tiêu kỳ vọng")

    area_min: Optional[float] = Field(None, ge=0, description="Diện tích tối thiểu (m²)")
    area_max: Optional[float] = Field(None, ge=0, description="Diện tích tối đa (m²)")
    target_area: Optional[float] = Field(None, ge=0, description="Diện tích mục tiêu kỳ vọng")

    bedrooms: Optional[int] = Field(None, ge=0, description="Số lượng phòng ngủ mong muốn")
    features: List[str] = Field(default_factory=list, description="Danh sách tiện ích ưu tiên")

    top_k: int = Field(10, ge=1, le=50, description="Số lượng kết quả gợi ý tối đa")


class ScoreBreakdown(BaseModel):
    price_score: float = Field(..., description="Điểm mức độ phù hợp ngân sách (0.0 - 1.0)")
    location_score: float = Field(..., description="Điểm mức độ phù hợp vị trí (0.0 - 1.0)")
    category_score: float = Field(..., description="Điểm mức độ phù hợp loại hình (0.0 - 1.0)")
    area_score: float = Field(..., description="Điểm mức độ phù hợp diện tích (0.0 - 1.0)")
    bedroom_score: float = Field(..., description="Điểm mức độ phù hợp phòng ngủ (0.0 - 1.0)")
    feature_score: float = Field(..., description="Điểm mức độ trùng khớp tiện ích (0.0 - 1.0)")
    total_score: float = Field(..., description="Điểm tổng hợp có trọng số (0.0 - 1.0)")
    match_percentage: float = Field(..., description="Tỷ lệ phù hợp quy đổi theo % (0.0 - 100.0%)")


class RecommendedListingItem(BaseModel):
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

    # Recommendation Intelligence attributes
    match_score: float
    match_percentage: float
    score_breakdown: ScoreBreakdown
    match_reasons: List[str] = Field(default_factory=list, description="Các lý do gợi ý dễ hiểu cho người dùng")


class RecommendationResponse(BaseModel):
    items: List[RecommendedListingItem]
    total: int
    strategy: str = Field(..., description="Chiến lược gợi ý áp dụng")
    user_profile_applied: bool = Field(False, description="Đã kết hợp hồ sơ hành vi cá nhân hóa hay chưa")
