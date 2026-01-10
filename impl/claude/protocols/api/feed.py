"""
Feed REST API: Frontend endpoints for algorithmic K-Block discovery and feedback.

Provides:
- GET /api/feed/cosmos - All K-Blocks (unfiltered)
- GET /api/feed/coherent - Low-loss K-Blocks
- GET /api/feed/personal - Personalized feed based on user interactions
- POST /api/feed/feedback/record - Record user interaction
- GET /api/feed/analytics - Engagement analytics
- GET /api/feed/config - Current ranking configuration

See: services/feed/ (Crown Jewel implementation)
See: plans/zero-seed-genesis-grand-strategy.md (Part IV)
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class RecordFeedbackRequest(BaseModel):
    """Request body for recording user feedback."""

    user_id: str = Field(..., description="User identifier")
    kblock_id: str = Field(..., description="K-Block identifier")
    action: str = Field(..., description="Action type: view, engage, dismiss, contradict")
    dwell_time_ms: int | None = Field(None, description="Time spent viewing (milliseconds)")
    interaction_type: str | None = Field(
        None, description="Specific interaction: edit, comment, link, copy"
    )
    metadata: dict[str, Any] | None = Field(None, description="Additional context")


class FeedbackRecordedResponse(BaseModel):
    """Response after recording feedback."""

    success: bool
    interaction_id: str


class KBlockSummary(BaseModel):
    """Summary of a K-Block for feed display."""

    id: str
    path: str
    content: str
    zero_seed_layer: int | None = None
    zero_seed_kind: str | None = None
    confidence: float
    attention_score: float | None = None


class FeedResponse(BaseModel):
    """Feed query response."""

    items: list[KBlockSummary]
    total: int
    has_more: bool
    offset: int
    limit: int


class EngagedKBlockStats(BaseModel):
    """Statistics for a single K-Block."""

    kblock_id: str
    attention_score: float
    view_count: int
    engage_count: int
    dismiss_count: int
    last_engaged_at: str | None = None


class FeedAnalyticsResponse(BaseModel):
    """Feed engagement analytics."""

    most_engaged_kblocks: list[EngagedKBlockStats]
    totals: dict[str, Any]
    recent_activity: dict[str, Any]


class FeedConfigResponse(BaseModel):
    """Current feed ranking configuration."""

    attention_weight: float
    principles_weight: float
    recency_weight: float
    coherence_weight: float
    enable_personalization: bool
    min_interactions_for_personalization: int


class PersonalFeedResponse(BaseModel):
    """Response for personalized feed."""

    feed_id: str
    name: str
    description: str
    ranking_weights: dict[str, float]
    items: list[KBlockSummary]
    total: int
    has_more: bool
    offset: int
    limit: int
    user_stats: dict[str, int]


# =============================================================================
# Router Factory
# =============================================================================


def create_feed_router() -> "APIRouter | None":
    """Create the feed API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/feed", tags=["feed"])

    @router.post("/feedback/record", response_model=FeedbackRecordedResponse)
    async def record_feedback(request: RecordFeedbackRequest) -> FeedbackRecordedResponse:
        """
        Record user interaction with a K-Block.

        Persists feedback to database for:
        - Personalized ranking
        - Analytics
        - ML training data

        Args:
            request: Feedback recording request
        """
        try:
            from services.feed.feedback import FeedbackAction
            from services.providers import get_feed_feedback_persistence

            persistence = await get_feed_feedback_persistence()  # type: ignore[no-untyped-call]

            # Parse action
            action_map = {
                "view": FeedbackAction.VIEW,
                "engage": FeedbackAction.ENGAGE,
                "dismiss": FeedbackAction.DISMISS,
                "contradict": FeedbackAction.CONTRADICT,
            }

            action = action_map.get(request.action.lower())
            if action is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {request.action}. Must be one of: view, engage, dismiss, contradict",
                )

            # Record interaction
            interaction_id = await persistence.record_interaction(
                user_id=request.user_id,
                kblock_id=request.kblock_id,
                action=action,
                dwell_time_ms=request.dwell_time_ms,
                interaction_type=request.interaction_type,
                metadata=request.metadata,
            )

            logger.debug(
                f"Recorded {action.value} feedback: user={request.user_id}, kblock={request.kblock_id}"
            )

            return FeedbackRecordedResponse(success=True, interaction_id=interaction_id)

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error recording feedback")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/config", response_model=FeedConfigResponse)
    async def get_feed_config_endpoint() -> FeedConfigResponse:
        """
        Get current feed ranking configuration.

        Returns the default ranking weights and personalization settings.
        These can be configured via environment variables:
        - KGENTS_FEED_ATTENTION_WEIGHT (default: 0.4)
        - KGENTS_FEED_PRINCIPLES_WEIGHT (default: 0.3)
        - KGENTS_FEED_RECENCY_WEIGHT (default: 0.2)
        - KGENTS_FEED_COHERENCE_WEIGHT (default: 0.1)
        - KGENTS_FEED_ENABLE_PERSONALIZATION (default: true)
        - KGENTS_FEED_MIN_INTERACTIONS (default: 5)
        """
        from services.feed.config import get_feed_config

        config = get_feed_config()

        return FeedConfigResponse(
            attention_weight=config.attention_weight,
            principles_weight=config.principles_weight,
            recency_weight=config.recency_weight,
            coherence_weight=config.coherence_weight,
            enable_personalization=config.enable_personalization,
            min_interactions_for_personalization=config.min_interactions_for_personalization,
        )

    @router.get("/personal", response_model=PersonalFeedResponse)
    async def get_personal_feed(
        user_id: str = Query(..., description="User identifier"),
        base_feed: str = Query(default="cosmos", description="Base feed to personalize"),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
    ) -> PersonalFeedResponse:
        """
        Get personalized feed based on user interaction history.

        The personalization algorithm:
        1. Analyzes user's view/engage/dismiss patterns
        2. Adjusts ranking weights based on behavior
        3. Filters out dismissed K-Blocks

        Requires at least min_interactions_for_personalization (default: 5)
        interactions before personalization activates. Until then, returns
        base feed with default weights.

        Args:
            user_id: User identifier for personalization
            base_feed: Base feed to personalize (cosmos, coherent, etc.)
            offset: Pagination offset
            limit: Maximum items to return
        """
        try:
            from services.feed.config import get_feed_config
            from services.feed.feedback import FeedbackSystem
            from services.feed.service import FeedService, MockUser
            from services.k_block.zero_seed_storage import ZeroSeedStorage

            config = get_feed_config()

            if not config.enable_personalization:
                raise HTTPException(
                    status_code=400,
                    detail="Personalization is disabled. Set KGENTS_FEED_ENABLE_PERSONALIZATION=true to enable.",
                )

            # Get or create feedback system
            feedback_system = FeedbackSystem()

            # Create personal feed
            personal_feed = await feedback_system.create_personal_feed(
                user_id=user_id,
                base_feed_id=base_feed,
            )

            # Get K-Blocks using the personal feed
            storage = ZeroSeedStorage()
            service = FeedService(storage)
            user = MockUser(id=user_id)

            result = await service.get_feed(
                feed=personal_feed,
                user=user,
                offset=offset,
                limit=limit,
            )

            # Get user stats
            user_stats = await feedback_system.get_user_stats(user_id)

            items = [
                KBlockSummary(
                    id=kb.id,
                    path=kb.path,
                    content=kb.content[:500],
                    zero_seed_layer=getattr(kb, "zero_seed_layer", None),
                    zero_seed_kind=getattr(kb, "zero_seed_kind", None),
                    confidence=kb.confidence,
                )
                for kb in result.items
            ]

            return PersonalFeedResponse(
                feed_id=personal_feed.id,
                name=personal_feed.name,
                description=personal_feed.description,
                ranking_weights={
                    "attention": personal_feed.ranking.attention_weight,
                    "principles": personal_feed.ranking.principles_weight,
                    "recency": personal_feed.ranking.recency_weight,
                    "coherence": personal_feed.ranking.coherence_weight,
                },
                items=items,
                total=result.total,
                has_more=result.has_more,
                offset=result.offset,
                limit=result.limit,
                user_stats=user_stats,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error getting personal feed")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/analytics", response_model=FeedAnalyticsResponse)
    async def get_feed_analytics(
        limit: int = Query(default=20, ge=1, le=100),
        min_interactions: int = Query(default=1, ge=1),
    ) -> FeedAnalyticsResponse:
        """
        Get feed engagement analytics.

        Returns:
        - Most engaged K-Blocks
        - Total interaction counts
        - Recent activity (24h)
        - Average dwell time

        Args:
            limit: Maximum number of K-Blocks to return
            min_interactions: Minimum interactions to include K-Block
        """
        try:
            from services.providers import get_feed_feedback_persistence

            persistence = await get_feed_feedback_persistence()  # type: ignore[no-untyped-call]

            analytics = await persistence.get_analytics(
                limit=limit,
                min_interactions=min_interactions,
            )

            return FeedAnalyticsResponse(
                most_engaged_kblocks=[
                    EngagedKBlockStats(**kb) for kb in analytics["most_engaged_kblocks"]
                ],
                totals=analytics["totals"],
                recent_activity=analytics["recent_activity"],
            )

        except Exception as e:
            logger.exception("Error getting feed analytics")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/cosmos", response_model=FeedResponse)
    async def get_cosmos_feed(
        user_id: str = Query(default="guest"),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
        ranking: str = Query(default="chronological"),
    ) -> FeedResponse:
        """
        Get cosmos feed (all K-Blocks from PostgreSQL).

        Args:
            user_id: User identifier for personalization
            offset: Pagination offset
            limit: Maximum items to return
            ranking: Ranking strategy (chronological, coherence, principles)
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()

            # Get all K-Blocks from PostgreSQL across all layers
            all_kblocks = []
            for layer_num in range(8):  # L0-L7
                layer_nodes = await storage.get_layer_nodes(layer_num)
                all_kblocks.extend(layer_nodes)

            # Sort by ranking
            if ranking == "chronological":
                all_kblocks.sort(
                    key=lambda kb: kb.created_at or "",
                    reverse=True,
                )
            elif ranking == "coherence":
                all_kblocks.sort(
                    key=lambda kb: kb.confidence or 0.5,
                    reverse=True,
                )

            # Paginate
            total = len(all_kblocks)
            paginated = all_kblocks[offset : offset + limit]
            has_more = (offset + limit) < total

            items = [
                KBlockSummary(
                    id=str(kb.id),
                    path=kb.path,
                    content=(kb.content or "")[:500],  # Truncate for feed
                    zero_seed_layer=kb.zero_seed_layer,
                    zero_seed_kind=kb.zero_seed_kind,
                    confidence=kb.confidence or 0.5,
                )
                for kb in paginated
            ]

            return FeedResponse(
                items=items,
                total=total,
                has_more=has_more,
                offset=offset,
                limit=limit,
            )

        except Exception as e:
            logger.exception("Error getting cosmos feed")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/coherent", response_model=FeedResponse)
    async def get_coherent_feed(
        user_id: str = Query(default="guest"),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
        max_loss: float = Query(default=0.2, ge=0.0, le=1.0),
    ) -> FeedResponse:
        """
        Get coherent feed (low-loss K-Blocks from PostgreSQL).

        Args:
            user_id: User identifier for personalization
            offset: Pagination offset
            limit: Maximum items to return
            max_loss: Maximum Galois loss threshold (confidence = 1 - loss)
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()

            # Get all K-Blocks from PostgreSQL across all layers
            all_kblocks = []
            for layer_num in range(8):  # L0-L7
                layer_nodes = await storage.get_layer_nodes(layer_num)
                all_kblocks.extend(layer_nodes)

            # Filter by max_loss (loss = 1 - confidence)
            min_confidence = 1.0 - max_loss
            filtered_kblocks = [
                kb for kb in all_kblocks if (kb.confidence or 0.5) >= min_confidence
            ]

            # Sort by coherence (confidence)
            filtered_kblocks.sort(
                key=lambda kb: kb.confidence or 0.5,
                reverse=True,
            )

            # Paginate
            total = len(filtered_kblocks)
            paginated = filtered_kblocks[offset : offset + limit]
            has_more = (offset + limit) < total

            items = [
                KBlockSummary(
                    id=str(kb.id),
                    path=kb.path,
                    content=(kb.content or "")[:500],  # Truncate for feed
                    zero_seed_layer=kb.zero_seed_layer,
                    zero_seed_kind=kb.zero_seed_kind,
                    confidence=kb.confidence or 0.5,
                )
                for kb in paginated
            ]

            return FeedResponse(
                items=items,
                total=total,
                has_more=has_more,
                offset=offset,
                limit=limit,
            )

        except Exception as e:
            logger.exception("Error getting coherent feed")
            raise HTTPException(status_code=500, detail=str(e))

    return router


__all__ = ["create_feed_router"]
