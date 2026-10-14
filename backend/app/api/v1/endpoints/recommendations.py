from typing import Optional

from fastapi import APIRouter, Depends, Header, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.recommendation import (
    RecommendationCriteria,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/search",
    response_model=ResponseBase[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Gợi ý bất động sản thông minh theo tiêu chí đa chiều",
    description="Thuật toán chấm điểm và xếp hạng (Content-Based + Soft-Constraint Scoring) dùng chung cho Frontend và Chatbot AI.",
)
def search_recommendations(
    criteria: RecommendationCriteria,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase[RecommendationResponse]:
    rec_service = RecommendationService(db)
    user_id = current_user.id if current_user else None
    result = rec_service.recommend_by_criteria(criteria=criteria, user_id=user_id)
    return ResponseBase[RecommendationResponse](
        success=True,
        data=result,
        message="Gợi ý bất động sản thành công",
    )


@router.get(
    "/personalized",
    response_model=ResponseBase[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Bảng tin gợi ý cá nhân hóa dựa trên lịch sử tương tác",
    description="Khám phá bất động sản theo hành vi xem và tin yêu thích. Tự động chuyển sang danh sách thịnh hành nếu người dùng mới (Cold Start).",
)
def get_personalized_feed(
    limit: int = Query(10, ge=1, le=50, description="Số lượng tin gợi ý"),
    x_session_id: Optional[str] = Header(None, description="Session ID ẩn danh"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase[RecommendationResponse]:
    rec_service = RecommendationService(db)
    user_id = current_user.id if current_user else None
    result = rec_service.get_personalized_feed(
        user_id=user_id, session_id=x_session_id, limit=limit
    )
    return ResponseBase[RecommendationResponse](
        success=True,
        data=result,
        message="Lấy bảng tin gợi ý cá nhân hóa thành công",
    )


@router.get(
    "/similar/{listing_id}",
    response_model=ResponseBase[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Gợi ý các bất động sản tương tự (Item-to-Item Similarity)",
    description="So sánh đặc trưng nội dung (Cosine Similarity) với bất động sản đang xem để đề xuất các lựa chọn thay thế phù hợp.",
)
def get_similar_listings(
    listing_id: int = Path(..., description="ID bất động sản đang xem"),
    limit: int = Query(6, ge=1, le=20, description="Số lượng tin tương tự"),
    db: Session = Depends(get_db),
) -> ResponseBase[RecommendationResponse]:
    rec_service = RecommendationService(db)
    result = rec_service.get_similar_listings(listing_id=listing_id, limit=limit)
    return ResponseBase[RecommendationResponse](
        success=True,
        data=result,
        message="Lấy bất động sản tương tự thành công",
    )
