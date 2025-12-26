"""
Meta REST API: Self-Reflection and Growth Tracking.

Provides endpoints for:
- GET /api/meta/timeline - Get coherence timeline with breakthroughs
- POST /api/meta/story - Generate narrative of coherence journey

Philosophy:
    "Watching yourself grow is itself a generative act."

This API implements Journey 5 (Meta) from the Zero Seed Creative Strategy.

See: plans/zero-seed-creative-strategy.md (Journey 5)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Query = None  # type: ignore

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

logger = logging.getLogger(__name__)

# =============================================================================
# Pydantic Models (API Request/Response)
# =============================================================================


class CoherencePointResponse(BaseModel):
    """A single point on the coherence timeline."""

    timestamp: str = Field(..., description="ISO timestamp")
    score: float = Field(..., description="Coherence score (0.0-1.0)")
    commit_id: str | None = Field(None, description="Git commit ID")
    layer_distribution: dict[int, int] = Field(..., description="Layer distribution at this point")
    total_nodes: int = Field(..., description="Total K-Blocks at this point")
    total_edges: int = Field(..., description="Total edges at this point")
    breakthrough: bool = Field(False, description="Whether this is a breakthrough moment")


class BreakthroughResponse(BaseModel):
    """A significant coherence jump."""

    timestamp: str = Field(..., description="ISO timestamp")
    old_score: float = Field(..., description="Score before breakthrough")
    new_score: float = Field(..., description="Score after breakthrough")
    delta: float = Field(..., description="Change in score")
    commit_id: str | None = Field(None, description="Git commit ID")
    description: str = Field(..., description="Breakthrough description")


class TimelineResponse(BaseModel):
    """Complete coherence timeline response."""

    points: list[CoherencePointResponse] = Field(..., description="Timeline points")
    breakthroughs: list[BreakthroughResponse] = Field(..., description="Breakthrough moments")
    current_score: float = Field(..., description="Current coherence score")
    average_score: float = Field(..., description="Average coherence across timeline")
    layer_distribution: dict[int, int] = Field(..., description="Total layer distribution")
    total_nodes: int = Field(..., description="Total K-Blocks")
    total_edges: int = Field(..., description="Total edges")
    start_date: str | None = Field(None, description="First data point timestamp")
    end_date: str | None = Field(None, description="Last data point timestamp")


class StoryRequest(BaseModel):
    """Request to generate coherence narrative."""

    since: str | None = Field(None, description="Start date (ISO)")
    until: str | None = Field(None, description="End date (ISO)")


class StoryResponse(BaseModel):
    """Narrative description of coherence journey."""

    story: str = Field(..., description="Prose narrative of growth journey")
    timeline: TimelineResponse = Field(..., description="Timeline data used for story")


# =============================================================================
# Router Factory
# =============================================================================


def create_meta_router() -> APIRouter | None:
    """Create the Meta API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Meta routes disabled")
        return None

    router = APIRouter(prefix="/api/meta", tags=["meta"])

    # =========================================================================
    # Get Coherence Timeline
    # =========================================================================

    @router.get("/timeline", response_model=TimelineResponse)
    async def get_coherence_timeline(
        since: str | None = Query(None, description="Start date (ISO)"),
        until: str | None = Query(None, description="End date (ISO)"),
    ) -> TimelineResponse:
        """
        Get coherence timeline with breakthroughs.

        Returns timeline showing coherence score evolution over time,
        including breakthrough moments (significant jumps).

        Args:
            since: Optional start date (ISO format)
            until: Optional end date (ISO format)

        Returns:
            TimelineResponse with points and analytics

        Raises:
            HTTPException: If timeline generation fails
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )
            from services.meta.timeline import TimelineService

            # Parse dates
            since_dt = datetime.fromisoformat(since) if since else None
            until_dt = datetime.fromisoformat(until) if until else None

            # Get storage
            storage = await get_postgres_zero_seed_storage()

            # Create service and get timeline
            service = TimelineService(storage)
            timeline = await service.get_timeline(since=since_dt, until=until_dt)

            # Convert to response
            points = [
                CoherencePointResponse(
                    timestamp=p.timestamp.isoformat(),
                    score=p.score,
                    commit_id=p.commit_id,
                    layer_distribution=p.layer_distribution,
                    total_nodes=p.total_nodes,
                    total_edges=p.total_edges,
                    breakthrough=any(
                        bt.timestamp == p.timestamp for bt in timeline.breakthroughs
                    ),
                )
                for p in timeline.points
            ]

            breakthroughs = [
                BreakthroughResponse(
                    timestamp=bt.timestamp.isoformat(),
                    old_score=bt.old_score,
                    new_score=bt.new_score,
                    delta=bt.delta,
                    commit_id=bt.commit_id,
                    description=bt.description,
                )
                for bt in timeline.breakthroughs
            ]

            return TimelineResponse(
                points=points,
                breakthroughs=breakthroughs,
                current_score=timeline.current_score,
                average_score=timeline.average_score,
                layer_distribution=timeline.layer_distribution,
                total_nodes=timeline.total_nodes,
                total_edges=timeline.total_edges,
                start_date=(
                    timeline.start_date.isoformat() if timeline.start_date else None
                ),
                end_date=timeline.end_date.isoformat() if timeline.end_date else None,
            )

        except Exception as e:
            logger.error(f"Timeline generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Timeline generation failed: {str(e)}",
            )

    # =========================================================================
    # Tell Story (Narrative Export)
    # =========================================================================

    @router.post("/story", response_model=StoryResponse)
    async def tell_story(request: StoryRequest | None = None) -> StoryResponse:
        """
        Generate narrative description of coherence journey.

        "Tell my story" - creates a prose summary of your growth,
        highlighting breakthroughs and epistemic evolution.

        Args:
            request: Optional date range filter

        Returns:
            StoryResponse with narrative and timeline data

        Raises:
            HTTPException: If story generation fails
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )
            from services.meta.timeline import TimelineService

            # Parse dates
            since_dt = None
            until_dt = None
            if request:
                since_dt = datetime.fromisoformat(request.since) if request.since else None
                until_dt = datetime.fromisoformat(request.until) if request.until else None

            # Get storage
            storage = await get_postgres_zero_seed_storage()

            # Create service and get timeline
            service = TimelineService(storage)
            timeline = await service.get_timeline(since=since_dt, until=until_dt)

            # Generate story
            story = await service.tell_story(timeline)

            # Convert timeline to response
            points = [
                CoherencePointResponse(
                    timestamp=p.timestamp.isoformat(),
                    score=p.score,
                    commit_id=p.commit_id,
                    layer_distribution=p.layer_distribution,
                    total_nodes=p.total_nodes,
                    total_edges=p.total_edges,
                    breakthrough=any(
                        bt.timestamp == p.timestamp for bt in timeline.breakthroughs
                    ),
                )
                for p in timeline.points
            ]

            breakthroughs = [
                BreakthroughResponse(
                    timestamp=bt.timestamp.isoformat(),
                    old_score=bt.old_score,
                    new_score=bt.new_score,
                    delta=bt.delta,
                    commit_id=bt.commit_id,
                    description=bt.description,
                )
                for bt in timeline.breakthroughs
            ]

            timeline_response = TimelineResponse(
                points=points,
                breakthroughs=breakthroughs,
                current_score=timeline.current_score,
                average_score=timeline.average_score,
                layer_distribution=timeline.layer_distribution,
                total_nodes=timeline.total_nodes,
                total_edges=timeline.total_edges,
                start_date=(
                    timeline.start_date.isoformat() if timeline.start_date else None
                ),
                end_date=timeline.end_date.isoformat() if timeline.end_date else None,
            )

            return StoryResponse(
                story=story,
                timeline=timeline_response,
            )

        except Exception as e:
            logger.error(f"Story generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Story generation failed: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_meta_router",
    # Request models
    "StoryRequest",
    # Response models
    "TimelineResponse",
    "CoherencePointResponse",
    "BreakthroughResponse",
    "StoryResponse",
]
