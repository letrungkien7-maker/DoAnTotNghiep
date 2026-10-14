import logging
from typing import Any, Dict, List, Optional

from app.core.config import Settings
from app.schemas.chat import ExtractedCriteria
from app.schemas.recommendation import RecommendedListingItem

logger = logging.getLogger(__name__)


class ChatbotLLM:
    """
    LLM and Response Synthesis Engine for Real Estate Assistant.
    Provides natural language generation grounded strictly in retrieved database facts.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.has_gemini = bool(self.settings.GEMINI_API_KEY)
        self.has_openai = bool(self.settings.OPENAI_API_KEY)

    def generate_clarification_prompt(self, criteria: ExtractedCriteria) -> str:
        """Asks user clarifying questions when criteria are underspecified."""
        questions: List[str] = []

        if not criteria.transaction_type:
            questions.append("Bạn đang tìm mua nhà đất hay cần tìm thuê?")

        if not criteria.province and not criteria.district:
            questions.append("Khu vực mong muốn (quận/huyện, thành phố)?")

        if not criteria.budget_min and not criteria.budget_max:
            questions.append("Khoảng ngân sách dự kiến của bạn (Ví dụ: dưới 3 tỷ, 10-15 triệu/tháng)?")

        if not criteria.category_id:
            questions.append("Loại hình bất động sản (Chung cư, Nhà riêng, Biệt thự hay Đất nền)?")

        joined_qs = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(questions[:3]))

        return (
            "Chào bạn! Tôi rất sẵn lòng hỗ trợ tìm kiếm bất động sản phù hợp nhất cho bạn. "
            "Để kết quả lọc chuẩn xác hơn, bạn có thể cho tôi biết thêm một số thông tin:\n\n"
            f"{joined_qs}\n\n"
            "Ví dụ bạn có thể nhắn: *'Tìm mua căn hộ 2PN tại Nam Từ Liêm dưới 3.5 tỷ full nội thất'*"
        )

    def generate_out_of_scope_reply(self) -> str:
        return (
            "Tôi là Trợ lý AI chuyên biệt cho Sàn giao dịch Bất động sản BDS Smart. "
            "Hiện tại tôi chỉ có thể hỗ trợ bạn tìm kiếm, mua bán, thuê nhà đất và giải đáp quy trình đăng tin. "
            "Nếu bạn có câu hỏi nào về bất động sản, đừng ngần ngại hỏi tôi nhé!"
        )

    def generate_grounded_reply(
        self,
        user_message: str,
        criteria: ExtractedCriteria,
        listings: List[RecommendedListingItem],
    ) -> str:
        """
        Synthesize answer strictly grounded on actual DB listings.
        Zero hallucination: does not invent prices, units, or non-existent properties.
        """
        if not listings:
            return self._generate_zero_result_reply(criteria)

        # Context summary
        loc_str = f" tại {criteria.district}, {criteria.province}" if criteria.district and criteria.province else (
            f" tại {criteria.province}" if criteria.province else ""
        )
        cat_str = f" {criteria.category_name}" if criteria.category_name else " bất động sản"
        tx_str = "thuê" if criteria.transaction_type == "RENT" else "bán"

        header = f"Tôi đã tìm thấy **{len(listings)}**{cat_str} {tx_str}{loc_str} phù hợp nhất với tiêu chí của bạn:"

        items_summary: List[str] = []
        for idx, l in enumerate(listings[:3]):
            price_text = (
                f"{l.price / 1_000_000_000:.2f} tỷ"
                if l.price >= 1_000_000_000
                else f"{l.price / 1_000_000:.0f} triệu/tháng"
            )
            reasons_text = f" ({'; '.join(l.match_reasons[:2])})" if l.match_reasons else ""
            item_line = (
                f"{idx+1}. **{l.title}**\n"
                f"   • Giá: **{price_text}** | Diện tích: **{l.area} m²** | Vị trí: {l.district}, {l.province}\n"
                f"   • Mức độ phù hợp: **{l.match_percentage}%**{reasons_text}"
            )
            items_summary.append(item_line)

        body = "\n\n".join(items_summary)
        footer = (
            "\n\n👉 Bạn có thể bấm trực tiếp vào thẻ bất động sản bên dưới để xem ảnh chi tiết, "
            "thông số pháp lý và liên hệ với người đăng tin."
        )

        return f"{header}\n\n{body}{footer}"

    def _generate_zero_result_reply(self, criteria: ExtractedCriteria) -> str:
        loc_info = f" tại {criteria.district or criteria.province}" if criteria.district or criteria.province else ""
        price_info = (
            f" với ngân sách dưới {criteria.budget_max / 1_000_000_000:.1f} tỷ"
            if criteria.budget_max and criteria.budget_max >= 1_000_000_000
            else ""
        )

        return (
            f"Rất tiếc, hiện tại hệ thống chưa có bất động sản nào khớp hoàn toàn với yêu cầu{loc_info}{price_info}.\n\n"
            "💡 **Gợi ý:** Bạn có thể thử:\n"
            "1. Tăng mức ngân sách dự kiến lên khoảng 10 - 15%.\n"
            "2. Mở rộng tìm kiếm sang các quận/huyện lân cận.\n"
            "3. Bấm vào trang **Tìm kiếm** để theo dõi các tin mới cập nhật hàng ngày."
        )
