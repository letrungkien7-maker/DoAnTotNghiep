import re
from typing import Dict, List, Optional, Tuple

from app.schemas.chat import ChatIntent, ExtractedCriteria

DISTRICT_MAPPING = {
    # Hà Nội
    "nam từ liêm": ("Hà Nội", "Nam Từ Liêm"),
    "bắc từ liêm": ("Hà Nội", "Bắc Từ Liêm"),
    "cầu giấy": ("Hà Nội", "Cầu Giấy"),
    "hà đông": ("Hà Nội", "Hà Đông"),
    "thanh xuân": ("Hà Nội", "Thanh Xuân"),
    "ba đình": ("Hà Nội", "Ba Đình"),
    "đống đa": ("Hà Nội", "Đống Đa"),
    "hai bà trưng": ("Hà Nội", "Hai Bà Trưng"),
    "hoàn kiếm": ("Hà Nội", "Hoàn Kiếm"),
    "tây hồ": ("Hà Nội", "Tây Hồ"),
    "hoàng mai": ("Hà Nội", "Hoàng Mai"),
    "long biên": ("Hà Nội", "Long Biên"),
    "gia lâm": ("Hà Nội", "Gia Lâm"),
    "hoài đức": ("Hà Nội", "Hoài Đức"),
    "mỹ đình": ("Hà Nội", "Nam Từ Liêm"),
    "tây mỗ": ("Hà Nội", "Nam Từ Liêm"),
    "mễ trì": ("Hà Nội", "Nam Từ Liêm"),
    "trung hòa": ("Hà Nội", "Cầu Giấy"),
    # TP.HCM
    "quận 1": ("Hồ Chí Minh", "Quận 1"),
    "quận 2": ("Hồ Chí Minh", "Thủ Đức"),
    "quận 3": ("Hồ Chí Minh", "Quận 3"),
    "quận 7": ("Hồ Chí Minh", "Quận 7"),
    "bình thạnh": ("Hồ Chí Minh", "Bình Thạnh"),
    "thủ đức": ("Hồ Chí Minh", "Thủ Đức"),
    "phú nhuận": ("Hồ Chí Minh", "Phú Nhuận"),
    "tân bình": ("Hồ Chí Minh", "Tân Bình"),
    # Đà Nẵng
    "hải châu": ("Đà Nẵng", "Hải Châu"),
    "sơn trà": ("Đà Nẵng", "Sơn Trà"),
    "ngũ hành sơn": ("Đà Nẵng", "Ngũ Hành Sơn"),
    "cẩm lệ": ("Đà Nẵng", "Cẩm Lệ"),
    "liên chiểu": ("Đà Nẵng", "Liên Chiểu"),
}

PROVINCES = ["hà nội", "hồ chí minh", "sài gòn", "đà nẵng", "hải phòng", "bình dương", "đồng nai", "cần thơ"]

CATEGORY_KEYWORDS = {
    1: ["chung cư", "căn hộ", "tập thể", "apartment", "condo"],
    2: ["nhà riêng", "nhà phố", "liền kề", "nhà ở", "nhà ngõ", "shophouse"],
    3: ["biệt thự", "villa", "resort", "nghỉ dưỡng"],
    4: ["đất nền", "lô đất", "thổ cư", "mảnh đất", "đất dự án"],
    5: ["mặt bằng", "văn phòng", "cửa hàng", "kiot"],
}

CATEGORY_NAMES = {
    1: "Căn hộ chung cư",
    2: "Nhà riêng - Nhà phố",
    3: "Biệt thự nghỉ dưỡng",
    4: "Đất nền dự án",
    5: "Mặt bằng kinh doanh",
}

FEATURE_KEYWORDS = [
    ("Nội thất đầy đủ", ["nội thất đầy đủ", "full nội thất", "full đồ", "đầy đủ đồ", "full furniture"]),
    ("Sổ đỏ chính chủ", ["sổ đỏ", "sổ hồng", "chính chủ", "pháp lý rõ ràng", "sổ lâu dài"]),
    ("Gara ô tô", ["gara", "ô tô", "chỗ để xe", "oto", "ô tô đỗ cửa", "đường ô tô"]),
    ("Bể bơi", ["bể bơi", "hồ bơi", "swimming pool"]),
    ("Thang máy", ["thang máy", "elevator"]),
    ("View hồ", ["view hồ", "view sông", "view công viên", "thoáng mát"]),
]

OUT_OF_SCOPE_KEYWORDS = [
    "thời tiết", "nấu ăn", "công thức", "bài thơ", "viết code", "lập trình",
    "bóng đá", "tổng thống", "ca sĩ", "phim ảnh", "chứng khoán", "tiền ảo", "bitcoin"
]


class VietnameseEntityExtractor:
    """Deterministic NLP extractor for real estate criteria from natural Vietnamese text."""

    @classmethod
    def detect_intent(cls, text: str) -> ChatIntent:
        lower = text.lower().strip()

        # Check out of scope
        if any(kw in lower for kw in OUT_OF_SCOPE_KEYWORDS):
            return ChatIntent(intent_type="OUT_OF_SCOPE", confidence=0.95)

        # Greetings or trivial inputs
        if lower in ["xin chào", "chào bạn", "hello", "hi", "bot ơi", "alo", "bạn là ai"]:
            return ChatIntent(intent_type="GENERAL_INQUIRY", confidence=0.90)

        # Check search intent
        search_indicators = [
            "tìm", "mua", "thuê", "cần", "có căn", "có nhà", "giá", "tỷ", "triệu",
            "chung cư", "phòng ngủ", "khu vực", "quận", "đăng tin"
        ]
        if any(ind in lower for ind in search_indicators):
            return ChatIntent(intent_type="SEARCH_LISTINGS", confidence=0.90)

        return ChatIntent(intent_type="SEARCH_LISTINGS", confidence=0.70)

    @classmethod
    def extract_criteria(cls, text: str) -> ExtractedCriteria:
        lower = text.lower()
        criteria = ExtractedCriteria()

        # 1. Transaction Type
        if any(w in lower for w in ["cho thuê", "cần thuê", "thuê nhà", "thuê căn", "tìm thuê", "thuê phòng", "thuê"]):
            criteria.transaction_type = "RENT"
        elif any(w in lower for w in ["mua", "bán", "cần mua", "tìm mua", "mua bán"]):
            criteria.transaction_type = "SALE"

        # 2. Category
        for cat_id, kws in CATEGORY_KEYWORDS.items():
            if any(kw in lower for kw in kws):
                criteria.category_id = cat_id
                criteria.category_name = CATEGORY_NAMES[cat_id]
                break

        # 3. Location (District & Province)
        for dist_key, (prov, dist) in DISTRICT_MAPPING.items():
            # Use word boundary / contains
            if dist_key in lower:
                criteria.province = prov
                criteria.district = dist
                break

        if not criteria.province:
            for prov in PROVINCES:
                if prov in lower:
                    criteria.province = "Hồ Chí Minh" if prov in ["hồ chí minh", "sài gòn"] else prov.title()
                    break

        # 4. Bedrooms
        # "2pn", "3 pn", "2 phòng ngủ"
        bed_match = re.search(r"(\d+)\s*(?:pn|phòng ngủ|phòng)", lower)
        if bed_match:
            try:
                criteria.bedrooms = int(bed_match.group(1))
            except ValueError:
                pass

        # 5. Price / Budget
        criteria.budget_min, criteria.budget_max = cls._extract_price_range(lower, criteria.transaction_type)

        # 6. Area
        area_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:m2|m²|mét vuông)", lower)
        if area_match:
            try:
                area_val = float(area_match.group(1))
                if "dưới" in lower:
                    criteria.area_max = area_val
                elif "trên" in lower or "từ" in lower:
                    criteria.area_min = area_val
                else:
                    criteria.area_min = area_val * 0.9
                    criteria.area_max = area_val * 1.1
            except ValueError:
                pass

        # 7. Features
        for feat_name, kws in FEATURE_KEYWORDS:
            if any(kw in lower for kw in kws):
                if feat_name not in criteria.features:
                    criteria.features.append(feat_name)

        return criteria

    @staticmethod
    def _extract_price_range(lower: str, transaction_type: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        b_min = None
        b_max = None

        # Range pattern: "từ 2 đến 3.5 tỷ", "2 - 3 tỷ", "2-3 tỷ"
        range_ty_match = re.search(r"(?:từ\s*)?(\d+(?:\.\d+)?)\s*(?:đến|-|tới)\s*(\d+(?:\.\d+)?)\s*(?:tỷ|ty)", lower)
        if range_ty_match:
            b_min = float(range_ty_match.group(1)) * 1_000_000_000
            b_max = float(range_ty_match.group(2)) * 1_000_000_000
            return b_min, b_max

        # Range triệu: "từ 10 đến 15 triệu", "10-15 triệu"
        range_tr_match = re.search(r"(?:từ\s*)?(\d+(?:\.\d+)?)\s*(?:đến|-|tới)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr)", lower)
        if range_tr_match:
            b_min = float(range_tr_match.group(1)) * 1_000_000
            b_max = float(range_tr_match.group(2)) * 1_000_000
            return b_min, b_max

        # Compound pattern: "3 tỷ 5", "3 tỷ 2", "3 tỷ 500"
        comp_match = re.search(r"(\d+)\s*(?:tỷ|ty)\s*(\d+)", lower)
        if comp_match:
            base = float(comp_match.group(1)) * 1_000_000_000
            fraction = float(comp_match.group(2))
            if fraction < 10:
                fraction *= 100_000_000  # "3 tỷ 5" -> 3.5 tỷ
            elif fraction < 100:
                fraction *= 10_000_000
            else:
                fraction *= 1_000_000  # "3 tỷ 500" -> 3.5 tỷ
            exact_val = base + fraction

            if "dưới" in lower or "tối đa" in lower or "khoảng" in lower or "tầm" in lower:
                return None, exact_val * 1.05
            elif "trên" in lower or "từ" in lower:
                return exact_val * 0.95, None
            else:
                return exact_val * 0.85, exact_val * 1.15

        # Single Billion match: "3 tỷ", "dưới 4 tỷ", "tầm 3.5 tỷ"
        ty_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:tỷ|ty)", lower)
        if ty_match:
            val = float(ty_match.group(1)) * 1_000_000_000
            if "dưới" in lower or "tối đa" in lower or "<" in lower:
                return None, val
            elif "trên" in lower or "từ" in lower or ">" in lower:
                return val, None
            else:
                # "tầm 3 tỷ" -> tolerance +- 15%
                return val * 0.85, val * 1.15

        # Single Million match: "15 triệu", "12tr", "dưới 15 triệu"
        tr_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:triệu|tr|trieu)", lower)
        if tr_match:
            val = float(tr_match.group(1)) * 1_000_000
            if "dưới" in lower or "tối đa" in lower:
                return None, val
            elif "trên" in lower or "từ" in lower:
                return val, None
            else:
                return val * 0.90, val * 1.10

        return b_min, b_max

    @classmethod
    def is_underspecified(cls, criteria: ExtractedCriteria) -> bool:
        """
        Check if criteria are too vague (missing location, budget, and category).
        E.g., User just says: 'Tôi muốn mua nhà'
        """
        has_location = bool(criteria.province or criteria.district)
        has_budget = bool(criteria.budget_min or criteria.budget_max)
        has_category = bool(criteria.category_id)
        has_features = bool(criteria.features)

        # If zero specific filter attributes extracted
        count_specified = sum([has_location, has_budget, has_category, has_features, bool(criteria.bedrooms)])
        return count_specified <= 1
