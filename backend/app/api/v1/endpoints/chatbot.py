from typing import List, Optional

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionResponse,
    SendMessageRequest,
)
from app.schemas.common import ResponseBase
from app.services.chatbot_service import ChatbotService

router = APIRouter()


@router.post(
    "/message",
    response_model=ResponseBase[ChatMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Gửi tin nhắn hội thoại đến Trợ lý Chatbot AI",
    description="Nhận câu hỏi tiếng Việt, trích xuất tiêu chí, gọi Recommendation Engine và trả lời dựa trên dữ liệu thật.",
)
def send_chat_message(
    req: SendMessageRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase[ChatMessageResponse]:
    service = ChatbotService(db)
    user_id = current_user.id if current_user else None
    response = service.send_message(req=req, user_id=user_id)
    return ResponseBase[ChatMessageResponse](
        success=True,
        data=response,
        message="Nhận phản hồi từ trợ lý AI thành công",
    )


@router.get(
    "/sessions",
    response_model=ResponseBase[List[ChatSessionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách các phiên hội thoại của người dùng",
    description="Dành cho người dùng đã đăng nhập để xem lại lịch sử các phiên chat trước đó.",
)
def list_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ResponseBase[List[ChatSessionResponse]]:
    service = ChatbotService(db)
    sessions = service.list_user_sessions(user_id=current_user.id)
    return ResponseBase[List[ChatSessionResponse]](
        success=True,
        data=sessions,
        message="Lấy danh sách phiên hội thoại thành công",
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ResponseBase[List[ChatMessageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy toàn bộ tin nhắn trong một phiên hội thoại",
    description="Truy xuất lịch sử tin nhắn của một phiên chat cụ thể theo session_id.",
)
def get_session_messages(
    session_id: str = Path(..., description="UUID của phiên hội thoại"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase[List[ChatMessageResponse]]:
    service = ChatbotService(db)
    user_id = current_user.id if current_user else None
    messages = service.get_session_history(session_id=session_id, user_id=user_id)
    return ResponseBase[List[ChatMessageResponse]](
        success=True,
        data=messages,
        message="Lấy lịch sử tin nhắn thành công",
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=ResponseBase[dict],
    status_code=status.HTTP_200_OK,
    summary="Xóa một phiên hội thoại",
    description="Xóa phiên chat và toàn bộ tin nhắn liên quan khỏi cơ sở dữ liệu.",
)
def delete_chat_session(
    session_id: str = Path(..., description="UUID của phiên hội thoại cần xóa"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase[dict]:
    service = ChatbotService(db)
    user_id = current_user.id if current_user else None
    deleted = service.delete_session(session_id=session_id, user_id=user_id)
    return ResponseBase[dict](
        success=deleted,
        data={"session_id": session_id, "deleted": deleted},
        message="Xóa phiên hội thoại thành công" if deleted else "Không tìm thấy phiên hội thoại",
    )
