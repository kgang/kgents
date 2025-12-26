"""
Daily Lab REST API: Trail-to-Crystal journaling endpoints.

Provides:
- POST /api/witness/daily/capture - Capture a new mark (quick, tagged, or with reasoning)
- GET  /api/witness/daily/trail   - Get today's trail of marks
- POST /api/witness/daily/crystallize - Create a crystal from today's marks
- GET  /api/witness/daily/export  - Export the day's work

Joy Calibration:
    Primary: FLOW - "Lighter than a to-do list"
    Secondary: WARMTH - "Kind companion reviewing your day"

See: services/witness/daily_lab.py for the underlying service
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Literal

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class CaptureMarkRequest(BaseModel):
    """Request body for capturing a daily mark."""

    content: str = Field(..., description="What's on your mind?")
    tag: str | None = Field(
        None,
        description="Optional tag: eureka, gotcha, taste, friction, joy, veto",
    )
    reasoning: str | None = Field(None, description="What made this stand out to you?")


class CaptureMarkResponse(BaseModel):
    """Response after capturing a mark."""

    mark_id: str
    content: str
    tag: str | None = None
    timestamp: str
    warmth_response: str


class MarkItem(BaseModel):
    """Single mark in a trail response."""

    mark_id: str
    content: str
    tags: list[str] = []
    timestamp: str


class TimeGapItem(BaseModel):
    """Time gap between marks."""

    start: str
    end: str
    duration_minutes: int


class TrailResponse(BaseModel):
    """Response with trail data."""

    marks: list[MarkItem]
    gaps: list[TimeGapItem] = []  # Computed gaps between marks
    date: str
    total: int = 0
    position: int = 0
    gap_minutes: int = 0  # Time since last mark (legacy)
    review_prompt: str = ""


class CompressionHonestyResponse(BaseModel):
    """Disclosure of what was dropped during compression."""

    dropped_count: int
    dropped_tags: list[str]
    dropped_summaries: list[str]
    galois_loss: float


class CrystallizeResponse(BaseModel):
    """Response after crystallization."""

    crystal_id: str | None = None
    summary: str | None = None  # Alias for insight
    insight: str | None = None
    significance: str | None = None
    disclosure: str
    compression_honesty: CompressionHonestyResponse | None = None
    success: bool
    warmth_response: str


class ExportResponse(BaseModel):
    """Response with exported content."""

    content: str
    format: str
    date: str
    warmth_response: str


# =============================================================================
# Router Factory
# =============================================================================


def create_daily_lab_router() -> "APIRouter | None":
    """Create the daily lab API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/witness/daily", tags=["witness-daily"])

    @router.post("/capture", response_model=CaptureMarkResponse)
    async def capture_mark(request: CaptureMarkRequest) -> CaptureMarkResponse:
        """
        Capture a new daily mark.

        Low-friction mark capture with WARMTH calibration.
        Just say what's on your mind.

        Args:
            request: Mark capture request with content, optional tag and reasoning
        """
        try:
            from services.witness.daily_lab import (
                WARMTH_RESPONSES,
                DailyLab,
                DailyTag,
            )
            from services.witness.trace_store import get_mark_store

            # Get the mark store and create lab
            store = get_mark_store()
            lab = DailyLab(mark_store=store)

            # Parse tag if provided
            tag: DailyTag | None = None
            if request.tag:
                try:
                    tag = DailyTag(request.tag.lower())
                except ValueError:
                    valid_tags = [t.value for t in DailyTag]
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid tag: {request.tag}. Valid tags: {valid_tags}",
                    )

            # Capture the mark using the appropriate method
            if request.reasoning:
                daily_mark = lab.capture.with_reasoning(
                    request.content, request.reasoning, tag
                )
            elif tag:
                daily_mark = lab.capture.tagged(request.content, tag)
            else:
                daily_mark = lab.capture.quick(request.content)

            # Build warmth response
            if tag:
                warmth = WARMTH_RESPONSES["mark_captured_with_feeling"].format(
                    tag=tag.value
                )
            else:
                warmth = WARMTH_RESPONSES["mark_captured"]

            return CaptureMarkResponse(
                mark_id=str(daily_mark.mark.id),
                content=daily_mark.content,
                tag=daily_mark.tag.value if daily_mark.tag else None,
                timestamp=daily_mark.timestamp.isoformat(),
                warmth_response=warmth,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error capturing mark")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/trail", response_model=TrailResponse)
    async def get_trail(
        target_date: str | None = Query(
            None, description="ISO date (YYYY-MM-DD), defaults to today"
        ),
        important_only: bool = Query(False, description="Only show important marks"),
    ) -> TrailResponse:
        """
        Get today's trail of marks.

        Returns marks for the specified date (or today) in chronological order.

        Args:
            target_date: ISO date string (YYYY-MM-DD), defaults to today
            important_only: Filter to only important marks (eureka, veto, taste)
        """
        try:
            from services.witness.daily_lab import DailyLab, Trail
            from services.witness.trace_store import get_mark_store

            # Get the mark store and create lab
            store = get_mark_store()
            lab = DailyLab(mark_store=store)

            # Parse target date
            if target_date:
                try:
                    parsed_date = date.fromisoformat(target_date)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date format: {target_date}. Use ISO format (YYYY-MM-DD)",
                    )
            else:
                parsed_date = date.today()

            # Get trail for date
            position = lab.trail.for_date(parsed_date)

            # Filter by importance if requested
            if important_only:
                position = lab.trail.filter_by_importance(position)

            # Build marks list
            marks_data = []
            for mark in position.marks:
                marks_data.append(
                    MarkItem(
                        mark_id=str(mark.id),
                        content=mark.response.content,
                        tags=list(mark.tags),
                        timestamp=mark.timestamp.isoformat(),
                    )
                )

            # Calculate gaps between marks (gaps > 30 minutes)
            gaps_data: list[TimeGapItem] = []
            gap_threshold_minutes = 30
            gap_minutes = 0
            if len(position.marks) >= 2:
                sorted_marks = sorted(position.marks, key=lambda m: m.timestamp)
                for i in range(1, len(sorted_marks)):
                    prev_mark = sorted_marks[i - 1]
                    curr_mark = sorted_marks[i]
                    delta = curr_mark.timestamp - prev_mark.timestamp
                    diff_minutes = int(delta.total_seconds() / 60)
                    if diff_minutes >= gap_threshold_minutes:
                        gaps_data.append(
                            TimeGapItem(
                                start=prev_mark.timestamp.isoformat(),
                                end=curr_mark.timestamp.isoformat(),
                                duration_minutes=diff_minutes,
                            )
                        )
                # Legacy gap_minutes: time since second-to-last mark
                last_mark = position.marks[-1]
                second_last = position.marks[-2]
                legacy_delta = last_mark.timestamp - second_last.timestamp
                gap_minutes = int(legacy_delta.total_seconds() / 60)

            return TrailResponse(
                marks=marks_data,
                gaps=gaps_data,
                date=parsed_date.isoformat(),
                total=position.total,
                position=position.position,
                gap_minutes=gap_minutes,
                review_prompt=lab.review_prompt(position),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error getting trail")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/crystallize", response_model=CrystallizeResponse)
    async def crystallize_day(
        target_date: str | None = Query(
            None, description="ISO date (YYYY-MM-DD), defaults to today"
        ),
    ) -> CrystallizeResponse:
        """
        Create a crystal from the day's marks.

        Crystallizes marks into a compressed insight with honest disclosure
        of what was dropped (Amendment G: COMPRESSION_HONESTY).

        Args:
            target_date: ISO date string (YYYY-MM-DD), defaults to today
        """
        try:
            from services.witness.crystal_store import get_crystal_store
            from services.witness.daily_lab import (
                WARMTH_RESPONSES,
                DailyLab,
            )
            from services.witness.trace_store import get_mark_store

            # Get stores and create lab
            mark_store = get_mark_store()
            crystal_store = get_crystal_store()
            lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

            # Parse target date
            if target_date:
                try:
                    parsed_date = date.fromisoformat(target_date)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date format: {target_date}. Use ISO format (YYYY-MM-DD)",
                    )
            else:
                parsed_date = date.today()

            # Attempt crystallization
            crystal = lab.crystallize.crystallize_day(parsed_date)

            if crystal is None:
                return CrystallizeResponse(
                    crystal_id=None,
                    summary=None,
                    insight=None,
                    significance=None,
                    disclosure="Not enough marks to crystallize yet.",
                    compression_honesty=None,
                    success=False,
                    warmth_response=WARMTH_RESPONSES["nothing_to_compress"],
                )

            # Build compression honesty response
            honesty = CompressionHonestyResponse(
                dropped_count=crystal.honesty.dropped_count,
                dropped_tags=crystal.honesty.dropped_tags,
                dropped_summaries=crystal.honesty.dropped_summaries,
                galois_loss=crystal.honesty.galois_loss,
            )

            return CrystallizeResponse(
                crystal_id=str(crystal.crystal.id),
                summary=crystal.insight,  # Alias for insight
                insight=crystal.insight,
                significance=crystal.significance,
                disclosure=crystal.disclosure,
                compression_honesty=honesty,
                success=True,
                warmth_response=WARMTH_RESPONSES["crystal_created"],
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error crystallizing")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/export", response_model=ExportResponse)
    async def export_day(
        target_date: str | None = Query(
            None, description="ISO date (YYYY-MM-DD), defaults to today"
        ),
        format: Literal["markdown", "json"] = Query(
            "markdown", description="Export format: markdown or json"
        ),
        include_crystal: bool = Query(True, description="Include crystallized insights"),
    ) -> ExportResponse:
        """
        Export the day's work.

        Generates a shareable export of marks and crystals in the specified format.

        Args:
            target_date: ISO date string (YYYY-MM-DD), defaults to today
            format: Export format (markdown or json)
            include_crystal: Whether to include crystallized insights
        """
        try:
            from services.witness.crystal_store import get_crystal_store
            from services.witness.daily_lab import (
                WARMTH_RESPONSES,
                DailyLab,
            )
            from services.witness.trace_store import get_mark_store

            # Get stores and create lab
            mark_store = get_mark_store()
            crystal_store = get_crystal_store()
            lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

            # Parse target date
            if target_date:
                try:
                    parsed_date = date.fromisoformat(target_date)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date format: {target_date}. Use ISO format (YYYY-MM-DD)",
                    )
            else:
                parsed_date = date.today()

            # Create export
            export = lab.export.export_day(
                parsed_date,
                include_crystal=include_crystal,
                format=format,
            )

            # Get content based on format
            if format == "markdown":
                content = export.to_markdown()
            else:
                content = export.to_json()

            return ExportResponse(
                content=content,
                format=format,
                date=parsed_date.isoformat(),
                warmth_response=WARMTH_RESPONSES["export_ready"],
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error exporting")
            raise HTTPException(status_code=500, detail=str(e))

    return router


__all__ = [
    "create_daily_lab_router",
    "CaptureMarkRequest",
    "CaptureMarkResponse",
    "TrailResponse",
    "CrystallizeResponse",
    "ExportResponse",
    "MarkItem",
    "CompressionHonestyResponse",
]
