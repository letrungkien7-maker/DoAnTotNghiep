import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSender, ChatSession
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionResponse,
    ExtractedCriteria,
    SendMessageRequest,
)
from app.schemas.recommendation import RecommendationCriteria, RecommendedListingItem
from app.services.chatbot_llm import ChatbotLLM
from app.services.recommendation_service import RecommendationService
from app.services.vietnamese_nlp import VietnameseEntityExtractor

logger = logging.getLogger(__name__)


class ChatbotService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatbotLLM()

    def send_message(
        self,
        req: SendMessageRequest,
        user_id: Optional[int] = None,
    ) -> ChatMessageResponse:
        """
        Process a user message through the complete Chatbot pipeline:
        1. Multi-turn session retrieval / creation
        2. Context accumulation across turns
        3. Intent and entity extraction
        4. Tool execution (Recommendation Engine querying real DB listings)
        5. Grounded natural response synthesis
        6. Message persistence
        """
        session = self._get_or_create_session(req.session_id, req.message, user_id)

        # 1. Save incoming user message
        user_msg = ChatMessage(
            session_id=session.id,
            sender=ChatSender.USER.value,
            message_text=req.message.strip(),
            structured_data=None,
        )
        self.db.add(user_msg)
        self.db.flush()

        # 2. Retrieve conversation context memory
        accumulated_criteria = self._retrieve_accumulated_criteria(session.id)

        # 3. Detect intent and extract new entities from current prompt
        intent = VietnameseEntityExtractor.detect_intent(req.message)
        new_criteria = VietnameseEntityExtractor.extract_criteria(req.message)

        # Merge new criteria into accumulated criteria (mutates with new updates)
        merged_criteria = self._merge_criteria(accumulated_criteria, new_criteria)

        # 4. Handle Out-Of-Scope
        if intent.intent_type == "OUT_OF_SCOPE":
            reply_text = self.llm.generate_out_of_scope_reply()
            return self._save_and_respond(
                session_id=session.id,
                reply_text=reply_text,
                listings=[],
                criteria=merged_criteria,
                is_clarification=False,
                suggestions=["Tìm căn hộ chung cư", "Bất động sản cho thuê", "Nhà đất dưới 3 tỷ"],
            )

        # 5. Handle General Greeting or severely underspecified request
        if intent.intent_type == "GENERAL_INQUIRY" or (
            VietnameseEntityExtractor.is_underspecified(merged_criteria)
            and not any([merged_criteria.district, merged_criteria.budget_max, merged_criteria.category_id])
        ):
            reply_text = self.llm.generate_clarification_prompt(merged_criteria)
            return self._save_and_respond(
                session_id=session.id,
                reply_text=reply_text,
                listings=[],
                criteria=merged_criteria,
                is_clarification=True,
                suggestions=[
                    "Căn hộ 2PN Nam Từ Liêm dưới 3.5 tỷ",
                    "Nhà riêng Hà Đông từ 8 đến 10 tỷ",
                    "Thuê căn hộ Cầu Giấy dưới 15 triệu",
                ],
            )

        # 6. Execute Tool: Query Recommendation Engine using Real DB data
        rec_criteria = RecommendationCriteria(
            transaction_type=merged_criteria.transaction_type or "SALE",
            category_id=merged_criteria.category_id,
            province=merged_criteria.province,
            district=merged_criteria.district,
            budget_min=merged_criteria.budget_min,
            budget_max=merged_criteria.budget_max,
            bedrooms=merged_criteria.bedrooms,
            features=merged_criteria.features,
            top_k=4,
        )

        rec_service = RecommendationService(self.db)
        rec_result = rec_service.recommend_by_criteria(criteria=rec_criteria, user_id=user_id)
        recommended_items: List[RecommendedListingItem] = rec_result.items

        # 7. Synthesize grounded answer
        reply_text = self.llm.generate_grounded_reply(
            user_message=req.message,
            criteria=merged_criteria,
            listings=recommended_items,
        )

        suggestions = [
            "Xem thêm căn hộ cùng khu vực",
            "Mở rộng ngân sách",
            "Tìm nhà đất cho thuê",
        ]

        return self._save_and_respond(
            session_id=session.id,
            reply_text=reply_text,
            listings=recommended_items,
            criteria=merged_criteria,
            is_clarification=False,
            suggestions=suggestions,
        )

    def _get_or_create_session(
        self,
        session_id: Optional[str],
        first_message: str,
        user_id: Optional[int],
    ) -> ChatSession:
        if session_id:
            existing = self.db.scalar(
                select(ChatSession).where(ChatSession.id == session_id)
            )
            if existing:
                return existing

        # Create new session
        title = first_message[:60].strip() if first_message else "Tư vấn bất động sản"
        new_session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_title=title,
        )
        self.db.add(new_session)
        self.db.flush()
        return new_session

    def _retrieve_accumulated_criteria(self, session_id: str) -> ExtractedCriteria:
        """Find the latest structured criteria saved in previous assistant turns."""
        last_assistant_msg = self.db.scalar(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.sender == ChatSender.ASSISTANT.value,
            )
            .order_by(desc(ChatMessage.created_at))
            .limit(1)
        )
        if last_assistant_msg and last_assistant_msg.structured_data:
            criteria_dict = last_assistant_msg.structured_data.get("accumulated_criteria")
            if criteria_dict:
                try:
                    return ExtractedCriteria(**criteria_dict)
                except Exception:
                    pass
        return ExtractedCriteria()

    def _merge_criteria(
        self,
        old: ExtractedCriteria,
        new: ExtractedCriteria,
    ) -> ExtractedCriteria:
        """Merge new entities into existing context."""
        merged = ExtractedCriteria(**old.model_dump())

        if new.transaction_type:
            merged.transaction_type = new.transaction_type
        if new.category_id:
            merged.category_id = new.category_id
            merged.category_name = new.category_name
        if new.province:
            merged.province = new.province
        if new.district:
            merged.district = new.district
        if new.budget_min is not None:
            merged.budget_min = new.budget_min
        if new.budget_max is not None:
            merged.budget_max = new.budget_max
        if new.area_min is not None:
            merged.area_min = new.area_min
        if new.area_max is not None:
            merged.area_max = new.area_max
        if new.bedrooms is not None:
            merged.bedrooms = new.bedrooms
        if new.features:
            # Union of features
            merged_feats = list(dict.fromkeys(merged.features + new.features))
            merged.features = merged_feats

        return merged

    def _save_and_respond(
        self,
        session_id: str,
        reply_text: str,
        listings: List[RecommendedListingItem],
        criteria: ExtractedCriteria,
        is_clarification: bool,
        suggestions: List[str],
    ) -> ChatMessageResponse:
        structured_data = {
            "accumulated_criteria": criteria.model_dump(),
            "listings_count": len(listings),
            "is_clarification": is_clarification,
            "listing_ids": [l.id for l in listings],
        }

        assistant_msg = ChatMessage(
            session_id=session_id,
            sender=ChatSender.ASSISTANT.value,
            message_text=reply_text,
            structured_data=structured_data,
        )
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(assistant_msg)

        return ChatMessageResponse(
            id=assistant_msg.id,
            session_id=session_id,
            sender="ASSISTANT",
            message_text=reply_text,
            created_at=assistant_msg.created_at,
            listings=listings,
            suggestions=suggestions,
            extracted_criteria=criteria,
            is_clarification=is_clarification,
        )

    def list_user_sessions(self, user_id: int) -> List[ChatSessionResponse]:
        sessions = list(
            self.db.scalars(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(desc(ChatSession.updated_at))
            ).all()
        )
        return [
            ChatSessionResponse(
                id=s.id,
                session_title=s.session_title,
                user_id=s.user_id,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=len(s.messages) if s.messages else 0,
            )
            for s in sessions
        ]

    def get_session_history(self, session_id: str, user_id: Optional[int] = None) -> List[ChatMessageResponse]:
        messages = list(
            self.db.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
            ).all()
        )

        responses: List[ChatMessageResponse] = []
        for m in messages:
            criteria = None
            if m.structured_data and "accumulated_criteria" in m.structured_data:
                try:
                    criteria = ExtractedCriteria(**m.structured_data["accumulated_criteria"])
                except Exception:
                    pass

            responses.append(
                ChatMessageResponse(
                    id=m.id,
                    session_id=m.session_id,
                    sender=m.sender,  # type: ignore
                    message_text=m.message_text,
                    created_at=m.created_at,
                    listings=[],  # Historical messages contain text summary
                    suggestions=[],
                    extracted_criteria=criteria,
                    is_clarification=m.structured_data.get("is_clarification", False) if m.structured_data else False,
                )
            )
        return responses

    def delete_session(self, session_id: str, user_id: Optional[int] = None) -> bool:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        if user_id:
            stmt = stmt.where(ChatSession.user_id == user_id)
        session = self.db.scalar(stmt)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
