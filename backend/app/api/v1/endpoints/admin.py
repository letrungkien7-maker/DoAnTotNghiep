from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationParams, ResponseBase
from app.schemas.listing import ListingCardResponse, ListingDetailResponse, ListingModerateRequest
from app.services.listing_service import ListingService

router = APIRouter()


@router.get(
    "/listings/pending",
    response_model=ResponseBase[PaginatedResponse[ListingCardResponse]],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Hàng đợi tin đăng chờ duyệt",
    description="Dành cho Quản trị viên: Lấy danh sách các tin đăng BĐS đang chờ phê duyệt."
)
def get_pending_listings(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> ResponseBase[PaginatedResponse[ListingCardResponse]]:
    pagination = PaginationParams(page=page, size=size)
    service = ListingService(db)
    result = service.get_pending_listings(pagination)
    return ResponseBase[PaginatedResponse[ListingCardResponse]](
        success=True,
        data=result,
        message="Lấy hàng đợi tin chờ duyệt thành công"
    )


@router.patch(
    "/listings/{listing_id}/moderate",
    response_model=ResponseBase[ListingDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Phê duyệt hoặc từ chối tin đăng",
    description="Dành cho Quản trị viên: Phê duyệt (APPROVED) hoặc Từ chối (REJECTED) kèm lý do cụ thể."
)
def moderate_listing(
    listing_id: int,
    req: ListingModerateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> ResponseBase[ListingDetailResponse]:
    service = ListingService(db)
    result = service.moderate_listing(
        listing_id=listing_id,
        action=req.action,
        rejection_reason=req.rejection_reason
    )
    action_text = "phê duyệt" if req.action == "APPROVE" else "từ chối"
    return ResponseBase[ListingDetailResponse](
        success=True,
        data=result,
        message=f"Đã {action_text} tin đăng thành công"
    )


@router.post(
    "/seed-data",
    response_model=ResponseBase[dict],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Nạp dữ liệu mẫu 63 tỉnh thành",
    description="Kích hoạt nạp dữ liệu mẫu bao phủ 63 tỉnh/thành phố trên toàn quốc."
)
def trigger_seed_data(
    _: User = Depends(require_admin),
) -> ResponseBase[dict]:
    from app.scripts.seed_demo_data import seed_database
    seed_database()
    return ResponseBase[dict](
        success=True,
        data={"status": "completed"},
        message="Đã khởi tạo thành công dữ liệu mẫu cho 63 tỉnh thành!"
    )
