from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from app.schemas.recommendation import RecommendedListingItem


class ChatIntent(BaseModel):
    intent_type: Literal[
        "SEARCH_LISTINGS",
        "CLARIFICATION_NEEDED",
        "GENERAL_INQUIRY",
        "OUT_OF_SCOPE",
    ] = "SEARCH_LISTINGS"
    confidence: float = 1.0


class ExtractedCriteria(BaseModel):
    transaction_type: Optional[Literal["SALE", "RENT"]] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    bedrooms: Optional[int] = None
    features: List[str] = Field(default_factory=list)


class SendMessageRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="UUID phiên hội thoại. Nếu None hệ thống tự tạo mới.")
    message: str = Field(..., min_length=1, max_length=2000, description="Nội dung tin nhắn người dùng gửi")


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    sender: Literal["USER", "ASSISTANT"]
    message_text: str
    created_at: datetime
    listings: List[RecommendedListingItem] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    extracted_criteria: Optional[ExtractedCriteria] = None
    is_clarification: bool = False


class ChatSessionResponse(BaseModel):
    id: str
    session_title: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
