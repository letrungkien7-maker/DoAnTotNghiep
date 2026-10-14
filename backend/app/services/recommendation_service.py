from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.interaction import Favorite, UserViewHistory
from app.models.listing import Listing, ListingStatus
from app.schemas.recommendation import (
    RecommendationCriteria,
    RecommendationResponse,
    RecommendedListingItem,
    ScoreBreakdown,
)
from app.services.recommendation_engine import RecommendationEngine, RecommendationWeights


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def _get_base_approved_query(self):
        """Query only active, approved, non-expired listings with relations loaded."""
        now = datetime.now(timezone.utc)
        return (
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images),
                selectinload(Listing.features),
            )
            .where(
                Listing.status == ListingStatus.APPROVED.value,
                Listing.expired_at > now,
            )
        )

    def _convert_to_dto(
        self,
        listing: Listing,
        match_score: float,
        breakdown: ScoreBreakdown,
        reasons: List[str],
    ) -> RecommendedListingItem:
        thumb_url = None
        for img in listing.images:
            if img.is_thumbnail:
                thumb_url = img.image_url
                break
        if not thumb_url and listing.images:
            thumb_url = listing.images[0].image_url

        return RecommendedListingItem(
            id=listing.id,
            title=listing.title,
            price=float(listing.price),
            price_unit=listing.price_unit,
            area=float(listing.area),
            bedrooms=listing.bedrooms,
            bathrooms=listing.bathrooms,
            address_text=listing.address_text,
            province=listing.province,
            district=listing.district,
            transaction_type=listing.transaction_type,
            category_id=listing.category_id,
            category_name=listing.category.name if listing.category else "",
            thumbnail_url=thumb_url,
            status=listing.status,
            view_count=listing.view_count,
            published_at=listing.published_at,
            match_score=match_score,
            match_percentage=breakdown.match_percentage,
            score_breakdown=breakdown,
            match_reasons=reasons,
        )

    def recommend_by_criteria(
        self,
        criteria: RecommendationCriteria,
        user_id: Optional[int] = None,
    ) -> RecommendationResponse:
        """
        Content-based multi-criteria scoring algorithm.
        Supports soft constraint relaxation to eliminate zero-result dead ends.
        """
        stmt = self._get_base_approved_query()

        # Hard filters: transaction type
        if criteria.transaction_type:
            stmt = stmt.where(Listing.transaction_type == criteria.transaction_type)

        # Soft filter on Province if provided (relax to all if fewer than 5 candidates in province)
        if criteria.province:
            province_stmt = stmt.where(Listing.province == criteria.province)
            candidates = list(self.db.scalars(province_stmt).all())
            if len(candidates) < 5:
                # Fallback to broader candidate pool if strict province yields too few candidates
                candidates = list(self.db.scalars(stmt).all())
        else:
            candidates = list(self.db.scalars(stmt).all())

        if not candidates:
            return RecommendationResponse(
                items=[],
                total=0,
                strategy="CONTENT_BASED_SCORING",
                user_profile_applied=False,
            )

        # Retrieve user profile if user is logged in
        user_implicit_profile = self._build_user_profile(user_id) if user_id else None
        user_profile_applied = user_implicit_profile is not None

        scored_items = []
        for listing in candidates:
            breakdown, reasons = RecommendationEngine.score_listing(listing, criteria)
            final_score = breakdown.total_score

            # Hybrid adjustment: if user has implicit profile, blend with 20% implicit weight
            if user_implicit_profile:
                implicit_score = self._score_implicit_affinity(listing, user_implicit_profile)
                final_score = round(0.80 * final_score + 0.20 * implicit_score, 4)
                breakdown.total_score = final_score
                breakdown.match_percentage = round(final_score * 100, 1)

            dto = self._convert_to_dto(listing, final_score, breakdown, reasons)
            scored_items.append(dto)

        # Rank descending by score, tie-break by view_count
        scored_items.sort(key=lambda x: (x.match_score, x.view_count), reverse=True)
        top_results = scored_items[: criteria.top_k]

        return RecommendationResponse(
            items=top_results,
            total=len(top_results),
            strategy="HYBRID_EXPLICIT_IMPLICIT" if user_profile_applied else "CONTENT_BASED_SCORING",
            user_profile_applied=user_profile_applied,
        )

    def get_personalized_feed(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> RecommendationResponse:
        """
        Generate personalized feed based on user view history and favorites.
        Falls back gracefully to Popular/Trending (Cold Start) if no history exists.
        """
        profile = self._build_user_profile(user_id=user_id, session_id=session_id)

        # Cold Start: return trending listings
        if not profile:
            return self._get_cold_start_recommendations(limit=limit)

        # Construct synthetic criteria based on user's implicit history
        criteria = RecommendationCriteria(
            transaction_type=profile.get("dominant_transaction_type", "SALE"),
            category_id=profile.get("dominant_category_id"),
            province=profile.get("dominant_province"),
            district=profile.get("dominant_district"),
            target_price=profile.get("avg_price"),
            target_area=profile.get("avg_area"),
            features=profile.get("top_features", []),
            top_k=limit,
        )

        res = self.recommend_by_criteria(criteria=criteria, user_id=user_id)
        res.strategy = "PERSONALIZED_BEHAVIORAL_FEED"
        res.user_profile_applied = True
        return res

    def get_similar_listings(self, listing_id: int, limit: int = 6) -> RecommendationResponse:
        """
        Find content-based similar listings for 'Bất động sản tương tự'.
        Uses multi-dimensional vector cosine similarity.
        """
        target = self.db.scalar(
            select(Listing)
            .options(
                selectinload(Listing.category),
                selectinload(Listing.images),
                selectinload(Listing.features),
            )
            .where(Listing.id == listing_id)
        )
        if not target:
            return RecommendationResponse(
                items=[], total=0, strategy="ITEM_TO_ITEM_SIMILARITY", user_profile_applied=False
            )

        # Candidates pool: approved listings in the same transaction type
        now = datetime.now(timezone.utc)
        candidates = list(
            self.db.scalars(
                select(Listing)
                .options(
                    selectinload(Listing.category),
                    selectinload(Listing.images),
                    selectinload(Listing.features),
                )
                .where(
                    Listing.id != listing_id,
                    Listing.status == ListingStatus.APPROVED.value,
                    Listing.expired_at > now,
                    Listing.transaction_type == target.transaction_type,
                )
            ).all()
        )

        scored = []
        for c in candidates:
            sim = RecommendationEngine.calculate_item_similarity(target, c)
            # Create synthetic breakdown
            breakdown = ScoreBreakdown(
                price_score=sim,
                location_score=sim,
                category_score=1.0 if c.category_id == target.category_id else 0.0,
                area_score=sim,
                bedroom_score=sim,
                feature_score=sim,
                total_score=sim,
                match_percentage=round(sim * 100, 1),
            )
            reasons = [
                f"Tương đồng {round(sim * 100)}% với bất động sản bạn đang xem",
                f"Cùng phân khúc tại {c.province}",
            ]
            dto = self._convert_to_dto(c, sim, breakdown, reasons)
            scored.append(dto)

        scored.sort(key=lambda x: x.match_score, reverse=True)
        top = scored[:limit]

        return RecommendationResponse(
            items=top,
            total=len(top),
            strategy="ITEM_TO_ITEM_SIMILARITY",
            user_profile_applied=False,
        )

    def _build_user_profile(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Aggregate user interaction history from favorites and views.
        Returns dictionary of inferred preferences.
        """
        interacted_listing_ids = set()

        if user_id:
            fav_ids = self.db.scalars(
                select(Favorite.listing_id).where(Favorite.user_id == user_id)
            ).all()
            interacted_listing_ids.update(fav_ids)

            view_ids = self.db.scalars(
                select(UserViewHistory.listing_id)
                .where(UserViewHistory.user_id == user_id)
                .order_by(desc(UserViewHistory.viewed_at))
                .limit(20)
            ).all()
            interacted_listing_ids.update(view_ids)
        elif session_id:
            view_ids = self.db.scalars(
                select(UserViewHistory.listing_id)
                .where(UserViewHistory.session_id == session_id)
                .order_by(desc(UserViewHistory.viewed_at))
                .limit(20)
            ).all()
            interacted_listing_ids.update(view_ids)

        if not interacted_listing_ids:
            return None

        # Fetch interacted listings
        listings = list(
            self.db.scalars(
                select(Listing)
                .options(selectinload(Listing.features))
                .where(Listing.id.in_(interacted_listing_ids))
            ).all()
        )
        if not listings:
            return None

        categories = [l.category_id for l in listings]
        provinces = [l.province for l in listings]
        districts = [l.district for l in listings]
        transaction_types = [l.transaction_type for l in listings]
        prices = [float(l.price) for l in listings]
        areas = [float(l.area) for l in listings]

        all_features = []
        for l in listings:
            for f in l.features:
                all_features.append(f.feature_name)

        dominant_cat = Counter(categories).most_common(1)[0][0] if categories else None
        dominant_prov = Counter(provinces).most_common(1)[0][0] if provinces else None
        dominant_dist = Counter(districts).most_common(1)[0][0] if districts else None
        dominant_tt = Counter(transaction_types).most_common(1)[0][0] if transaction_types else "SALE"
        avg_price = sum(prices) / len(prices) if prices else 0.0
        avg_area = sum(areas) / len(areas) if areas else 0.0
        top_feats = [feat for feat, _ in Counter(all_features).most_common(3)]

        return {
            "dominant_category_id": dominant_cat,
            "dominant_province": dominant_prov,
            "dominant_district": dominant_dist,
            "dominant_transaction_type": dominant_tt,
            "avg_price": avg_price,
            "avg_area": avg_area,
            "top_features": top_feats,
        }

    def _score_implicit_affinity(self, listing: Listing, profile: dict) -> float:
        """Measure how well a candidate listing fits user's implicit history."""
        score = 0.0
        if listing.category_id == profile.get("dominant_category_id"):
            score += 0.35
        if listing.province == profile.get("dominant_province"):
            score += 0.25
            if listing.district == profile.get("dominant_district"):
                score += 0.15

        avg_price = profile.get("avg_price", 0.0)
        if avg_price > 0:
            diff = abs(float(listing.price) - avg_price) / avg_price
            price_fit = max(0.0, 1.0 - diff)
            score += 0.25 * price_fit

        return min(1.0, score)

    def _get_cold_start_recommendations(self, limit: int = 10) -> RecommendationResponse:
        """Popularity-based fallback for cold start users."""
        now = datetime.now(timezone.utc)
        stmt = (
            self._get_base_approved_query()
            .order_by(desc(Listing.view_count), desc(Listing.published_at))
            .limit(limit)
        )
        popular = list(self.db.scalars(stmt).all())

        items = []
        for l in popular:
            breakdown = ScoreBreakdown(
                price_score=1.0,
                location_score=1.0,
                category_score=1.0,
                area_score=1.0,
                bedroom_score=1.0,
                feature_score=1.0,
                total_score=1.0,
                match_percentage=100.0,
            )
            reasons = ["Bất động sản nổi bật có lượt quan tâm cao nhất hệ thống"]
            items.append(self._convert_to_dto(l, 1.0, breakdown, reasons))

        return RecommendationResponse(
            items=items,
            total=len(items),
            strategy="POPULAR_COLD_START",
            user_profile_applied=False,
        )
