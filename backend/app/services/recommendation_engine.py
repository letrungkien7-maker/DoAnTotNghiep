import math
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from app.schemas.recommendation import RecommendationCriteria, ScoreBreakdown


@dataclass
class RecommendationWeights:
    price: float = 0.30
    location: float = 0.25
    category: float = 0.15
    area: float = 0.15
    bedrooms: float = 0.05
    features: float = 0.10

    def normalize(self) -> "RecommendationWeights":
        """Ensure all weights sum to 1.0"""
        total = self.price + self.location + self.category + self.area + self.bedrooms + self.features
        if total <= 0:
            return RecommendationWeights()
        return RecommendationWeights(
            price=self.price / total,
            location=self.location / total,
            category=self.category / total,
            area=self.area / total,
            bedrooms=self.bedrooms / total,
            features=self.features / total,
        )


class RecommendationEngine:
    """Core mathematical algorithm for multi-criteria real estate scoring and recommendation."""

    @staticmethod
    def calculate_price_score(
        price: float,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> float:
        """
        Calculate normalized price fit score in [0.0, 1.0].
        - Perfect fit (1.0) if within [budget_min, budget_max] or close to target_price.
        - Gentle decay if price is below budget_min (cheaper is acceptable).
        - Steep decay if price exceeds budget_max (harder ceiling, max 25% tolerance).
        """
        if budget_min is None and budget_max is None and target_price is None:
            return 1.0  # No price preference specified

        # Derive effective min/max if target_price provided
        if target_price is not None and target_price > 0:
            if budget_min is None:
                budget_min = target_price * 0.85
            if budget_max is None:
                budget_max = target_price * 1.15

        b_min = budget_min if budget_min is not None else 0.0
        b_max = budget_max if budget_max is not None else float("inf")

        if b_min <= price <= b_max:
            return 1.0

        if price < b_min and b_min > 0:
            # Under budget: gently decrease score from 1.0 to 0.6
            deviation = (b_min - price) / b_min
            return max(0.60, round(1.0 - 0.40 * deviation, 4))

        if price > b_max and b_max > 0:
            # Over budget: allow up to 25% tolerance before dropping to 0
            tolerance = b_max * 0.25
            overage = price - b_max
            if overage >= tolerance:
                return 0.0
            score = 1.0 - (overage / tolerance)
            return max(0.0, round(score, 4))

        return 1.0

    @staticmethod
    def calculate_location_score(
        listing_province: str,
        listing_district: str,
        target_province: Optional[str] = None,
        target_district: Optional[str] = None,
    ) -> float:
        """
        Location fit score:
        - 1.0: Exact province and district match.
        - 0.5: Same province, different district.
        - 0.0: Different province.
        """
        if not target_province and not target_district:
            return 1.0  # No location preference specified

        lp = listing_province.strip().lower()
        ld = listing_district.strip().lower()

        tp = target_province.strip().lower() if target_province else None
        td = target_district.strip().lower() if target_district else None

        # If province specified, it must match
        if tp:
            if tp not in lp and lp not in tp:
                return 0.0

        # If district specified
        if td:
            if td in ld or ld in td:
                return 1.0
            return 0.50 if tp else 0.40

        # Only province specified and matched
        return 1.0

    @staticmethod
    def calculate_category_score(
        listing_category_id: int,
        target_category_id: Optional[int] = None,
    ) -> float:
        """Category fit: 1.0 if identical, 0.0 if different."""
        if target_category_id is None:
            return 1.0
        return 1.0 if listing_category_id == target_category_id else 0.0

    @staticmethod
    def calculate_area_score(
        listing_area: float,
        area_min: Optional[float] = None,
        area_max: Optional[float] = None,
        target_area: Optional[float] = None,
    ) -> float:
        """
        Area fit score in [0.0, 1.0].
        Within range: 1.0. Outside range: linear decay with 50% deviation margin.
        """
        if area_min is None and area_max is None and target_area is None:
            return 1.0

        if target_area is not None and target_area > 0:
            if area_min is None:
                area_min = target_area * 0.85
            if area_max is None:
                area_max = target_area * 1.15

        a_min = area_min if area_min is not None else 0.0
        a_max = area_max if area_max is not None else float("inf")

        if a_min <= listing_area <= a_max:
            return 1.0

        midpoint = (a_min + (a_max if a_max != float("inf") else a_min * 1.5)) / 2.0
        diff = abs(listing_area - midpoint)
        margin = midpoint * 0.50
        if margin <= 0:
            return 0.0

        score = max(0.0, 1.0 - (diff / margin))
        return round(score, 4)

    @staticmethod
    def calculate_bedroom_score(
        listing_bedrooms: Optional[int],
        target_bedrooms: Optional[int],
    ) -> float:
        """
        Bedroom closeness score:
        - Exact match: 1.0
        - Difference 1: 0.70
        - Difference 2: 0.40
        - Difference >= 3: 0.10
        """
        if target_bedrooms is None:
            return 1.0
        if listing_bedrooms is None:
            return 0.50

        diff = abs(listing_bedrooms - target_bedrooms)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.70
        elif diff == 2:
            return 0.40
        else:
            return 0.10

    @staticmethod
    def calculate_feature_score(
        listing_features: List[str],
        target_features: List[str],
    ) -> float:
        """
        Feature overlap ratio: |listing_features ∩ target_features| / |target_features|.
        """
        if not target_features:
            return 1.0

        lf_norm = {f.strip().lower() for f in listing_features}
        tf_norm = {f.strip().lower() for f in target_features if f.strip()}

        if not tf_norm:
            return 1.0

        overlap = lf_norm.intersection(tf_norm)
        return round(len(overlap) / len(tf_norm), 4)

    @classmethod
    def score_listing(
        cls,
        listing: Any,
        criteria: RecommendationCriteria,
        weights: Optional[RecommendationWeights] = None,
    ) -> Tuple[ScoreBreakdown, List[str]]:
        """
        Evaluate a single listing against recommendation criteria.
        Returns:
            - ScoreBreakdown object
            - List of human-readable explanation strings
        """
        w = (weights or RecommendationWeights()).normalize()

        # Extract listing features
        listing_features: List[str] = []
        if hasattr(listing, "features"):
            for feat in listing.features:
                if isinstance(feat, str):
                    listing_features.append(feat)
                elif hasattr(feat, "feature_name"):
                    listing_features.append(feat.feature_name)

        # 1. Price
        price_val = float(listing.price)
        s_price = cls.calculate_price_score(
            price=price_val,
            budget_min=criteria.budget_min,
            budget_max=criteria.budget_max,
            target_price=criteria.target_price,
        )

        # 2. Location
        s_loc = cls.calculate_location_score(
            listing_province=listing.province,
            listing_district=listing.district,
            target_province=criteria.province,
            target_district=criteria.district,
        )

        # 3. Category
        s_cat = cls.calculate_category_score(
            listing_category_id=listing.category_id,
            target_category_id=criteria.category_id,
        )

        # 4. Area
        area_val = float(listing.area)
        s_area = cls.calculate_area_score(
            listing_area=area_val,
            area_min=criteria.area_min,
            area_max=criteria.area_max,
            target_area=criteria.target_area,
        )

        # 5. Bedrooms
        s_bed = cls.calculate_bedroom_score(
            listing_bedrooms=listing.bedrooms,
            target_bedrooms=criteria.bedrooms,
        )

        # 6. Features
        s_feat = cls.calculate_feature_score(
            listing_features=listing_features,
            target_features=criteria.features,
        )

        # Weighted total
        total = (
            w.price * s_price
            + w.location * s_loc
            + w.category * s_cat
            + w.area * s_area
            + w.bedrooms * s_bed
            + w.features * s_feat
        )
        total_score = max(0.0, min(1.0, round(total, 4)))
        match_percentage = round(total_score * 100, 1)

        breakdown = ScoreBreakdown(
            price_score=s_price,
            location_score=s_loc,
            category_score=s_cat,
            area_score=s_area,
            bedroom_score=s_bed,
            feature_score=s_feat,
            total_score=total_score,
            match_percentage=match_percentage,
        )

        # Generate explainability reasons
        reasons = cls.generate_match_reasons(listing, criteria, breakdown, listing_features)

        return breakdown, reasons

    @staticmethod
    def generate_match_reasons(
        listing: Any,
        criteria: RecommendationCriteria,
        breakdown: ScoreBreakdown,
        listing_features: List[str],
    ) -> List[str]:
        """Produce clear, human-understandable explanation bullets."""
        reasons: List[str] = []

        # Location reason
        if breakdown.location_score == 1.0 and criteria.district:
            reasons.append(f"Vị trí đúng trọng tâm tại {listing.district}, {listing.province}")
        elif breakdown.location_score >= 0.5 and criteria.province:
            reasons.append(f"Cùng khu vực tỉnh/thành {listing.province}")

        # Price reason
        if breakdown.price_score == 1.0 and (criteria.budget_min or criteria.budget_max):
            reasons.append("Mức giá nằm trọn vẹn trong khoảng ngân sách dự kiến của bạn")
        elif breakdown.price_score >= 0.8 and criteria.budget_max:
            reasons.append("Giá bán hợp lý, chênh lệch không đáng kể so với ngân sách")

        # Category reason
        if breakdown.category_score == 1.0 and criteria.category_id:
            category_name = getattr(listing, "category_name", None)
            if not category_name and hasattr(listing, "category") and listing.category:
                category_name = listing.category.name
            reasons.append(f"Khớp chính xác loại hình: {category_name or 'BĐS mong muốn'}")

        # Area reason
        if breakdown.area_score >= 0.9 and (criteria.area_min or criteria.area_max or criteria.target_area):
            reasons.append(f"Diện tích tối ưu ({listing.area} m²)")

        # Bedroom reason
        if breakdown.bedroom_score == 1.0 and criteria.bedrooms:
            reasons.append(f"Đáp ứng đủ {listing.bedrooms} phòng ngủ theo tiêu chuẩn")

        # Features reason
        if criteria.features and breakdown.feature_score > 0:
            tf_norm = {f.strip().lower() for f in criteria.features if f.strip()}
            matched_features = [f for f in listing_features if f.strip().lower() in tf_norm]
            if matched_features:
                reasons.append(f"Trùng khớp tiện ích: {', '.join(matched_features[:3])}")

        if not reasons:
            reasons.append(f"Bất động sản phù hợp {breakdown.match_percentage}% theo tiêu chí tổng thể")

        return reasons

    @classmethod
    def calculate_item_similarity(cls, a: Any, b: Any) -> float:
        """
        Calculate Content-Based Cosine Similarity between two listings.
        Vectors: [log(price), area, bedrooms, category_match, feature_jaccard]
        """
        if a.id == b.id:
            return 1.0

        # Hard filters for similarity
        if a.transaction_type != b.transaction_type:
            return 0.0

        # Location factor
        loc_sim = 1.0 if a.province == b.province and a.district == b.district else (0.5 if a.province == b.province else 0.0)

        # Price log ratio
        p1 = max(1.0, float(a.price))
        p2 = max(1.0, float(b.price))
        price_diff = abs(math.log10(p1) - math.log10(p2))
        price_sim = max(0.0, 1.0 - price_diff)

        # Area ratio
        ar1 = max(1.0, float(a.area))
        ar2 = max(1.0, float(b.area))
        area_sim = min(ar1, ar2) / max(ar1, ar2)

        # Bedroom diff
        b1 = a.bedrooms or 2
        b2 = b.bedrooms or 2
        bed_sim = max(0.0, 1.0 - abs(b1 - b2) * 0.3)

        # Category
        cat_sim = 1.0 if a.category_id == b.category_id else 0.0

        # Feature overlap
        f1 = {getattr(f, "feature_name", str(f)).lower() for f in (getattr(a, "features", []) or [])}
        f2 = {getattr(f, "feature_name", str(f)).lower() for f in (getattr(b, "features", []) or [])}
        feat_sim = len(f1.intersection(f2)) / len(f1.union(f2)) if f1 and f2 else 0.5

        # Weighted combination
        sim = (
            0.25 * loc_sim
            + 0.25 * price_sim
            + 0.20 * cat_sim
            + 0.15 * area_sim
            + 0.05 * bed_sim
            + 0.10 * feat_sim
        )
        return round(sim, 4)
