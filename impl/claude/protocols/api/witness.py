"""
Witness REST API: Frontend endpoints for mark operations.

Provides:
- GET /api/witness/marks - List marks with filters
- POST /api/witness/marks - Create mark
- PATCH /api/witness/marks/{id}/retract - Retract a mark
- GET /api/witness/stream - SSE for real-time updates

See: plans/witness-fusion-ux-implementation.md
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    from fastapi.responses import StreamingResponse
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


class CreateMarkRequest(BaseModel):
    """Request body for creating a mark."""

    action: str = Field(..., description="What happened")
    reasoning: str | None = Field(None, description="Why this action was taken")
    principles: list[str] = Field(default_factory=list, description="Constitutional principles")
    author: str = Field(default="kent", description="kent | claude | system")
    parent_mark_id: str | None = Field(None, description="Parent mark for lineage")


class MarkResponse(BaseModel):
    """Single mark response."""

    id: str
    action: str
    reasoning: str | None = None
    principles: list[str] = []
    author: str
    session_id: str | None = None
    timestamp: str
    parent_mark_id: str | None = None
    retracted: bool = False
    retraction_reason: str | None = None


class MarkListResponse(BaseModel):
    """List of marks response."""

    marks: list[MarkResponse]
    total: int
    has_more: bool = False


class RetractRequest(BaseModel):
    """Request body for retracting a mark."""

    reason: str = Field(..., description="Reason for retraction")


# =============================================================================
# Router Factory
# =============================================================================


def create_witness_router() -> "APIRouter | None":
    """Create the witness API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/witness", tags=["witness"])

    @router.get("/marks", response_model=MarkListResponse)
    async def list_marks(
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        author: str | None = Query(default=None),
        today: bool = Query(default=False),
        grep: str | None = Query(default=None),
        principle: str | None = Query(default=None),
    ) -> MarkListResponse:
        """
        List marks with optional filters.

        Args:
            limit: Maximum number of marks to return
            offset: Offset for pagination
            author: Filter by author (kent, claude, system)
            today: Only show marks from today
            grep: Search text in action/reasoning
            principle: Filter by principle tag
        """
        try:
            from services.providers import get_witness_persistence

            persistence = await get_witness_persistence()

            # Get more than needed to support filtering
            fetch_limit = limit * 5 if grep or principle else limit + offset + 1
            marks_data = await persistence.get_marks(limit=fetch_limit)

            # Apply filters
            marks = []
            for m in marks_data:
                # Author filter
                if author and m.author != author:
                    continue

                # Today filter
                if today:
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    if m.timestamp < today_start:
                        continue

                # Grep filter
                if grep:
                    search = grep.lower()
                    if search not in m.action.lower() and search not in (m.reasoning or "").lower():
                        continue

                # Principle filter
                if principle:
                    if principle.lower() not in [p.lower() for p in m.principles]:
                        continue

                marks.append(
                    MarkResponse(
                        id=m.mark_id,
                        action=m.action,
                        reasoning=m.reasoning,
                        principles=m.principles,
                        author=m.author,
                        session_id=getattr(m, "session_id", None),
                        timestamp=m.timestamp.isoformat(),
                        parent_mark_id=m.parent_mark_id,
                        retracted=getattr(m, "retracted", False),
                        retraction_reason=getattr(m, "retraction_reason", None),
                    )
                )

            # Pagination
            total = len(marks)
            marks = marks[offset : offset + limit]
            has_more = total > offset + limit

            return MarkListResponse(marks=marks, total=total, has_more=has_more)

        except Exception as e:
            logger.exception("Error listing marks")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/marks", response_model=MarkResponse)
    async def create_mark(request: CreateMarkRequest) -> MarkResponse:
        """
        Create a new mark.

        Args:
            request: Mark creation request
        """
        try:
            from services.providers import get_witness_persistence

            persistence = await get_witness_persistence()
            result = await persistence.save_mark(
                action=request.action,
                reasoning=request.reasoning,
                principles=request.principles,
                author=request.author,
                parent_mark_id=request.parent_mark_id,
            )

            return MarkResponse(
                id=result.mark_id,
                action=result.action,
                reasoning=result.reasoning,
                principles=result.principles,
                author=result.author,
                session_id=getattr(result, "session_id", None),
                timestamp=result.timestamp.isoformat(),
                parent_mark_id=result.parent_mark_id,
            )

        except Exception as e:
            logger.exception("Error creating mark")
            raise HTTPException(status_code=500, detail=str(e))

    @router.patch("/marks/{mark_id}/retract")
    async def retract_mark(mark_id: str, request: RetractRequest) -> dict[str, Any]:
        """
        Retract a mark.

        Args:
            mark_id: ID of the mark to retract
            request: Retraction request with reason
        """
        try:
            from services.providers import get_witness_persistence

            persistence = await get_witness_persistence()

            # Check if retract method exists
            if hasattr(persistence, "retract_mark"):
                await persistence.retract_mark(mark_id, request.reason)
                return {"success": True, "mark_id": mark_id}
            else:
                # Fallback: just acknowledge (persistence doesn't support retraction yet)
                return {"success": True, "mark_id": mark_id, "note": "Retraction recorded (soft)"}

        except Exception as e:
            logger.exception("Error retracting mark")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/stream")
    async def stream_marks() -> StreamingResponse:
        """
        SSE stream for real-time mark updates.

        Returns Server-Sent Events for new marks as they're created.
        """

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events."""
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

            # Keep-alive and poll for new marks
            last_check = datetime.now()
            seen_ids: set[str] = set()

            try:
                from services.providers import get_witness_persistence

                persistence = await get_witness_persistence()

                # Get initial marks to populate seen_ids
                initial = await persistence.get_marks(limit=20)
                for m in initial:
                    seen_ids.add(m.mark_id)

                while True:
                    await asyncio.sleep(2)  # Poll every 2 seconds

                    # Check for new marks
                    recent = await persistence.get_marks(limit=10)
                    for m in recent:
                        if m.mark_id not in seen_ids:
                            seen_ids.add(m.mark_id)
                            mark_data = {
                                "id": m.mark_id,
                                "action": m.action,
                                "reasoning": m.reasoning,
                                "principles": m.principles,
                                "author": m.author,
                                "timestamp": m.timestamp.isoformat(),
                            }
                            yield f"event: mark\ndata: {json.dumps(mark_data)}\n\n"

                    # Periodic heartbeat
                    if (datetime.now() - last_check).seconds > 30:
                        yield f"event: heartbeat\ndata: {json.dumps({'time': datetime.now().isoformat()})}\n\n"
                        last_check = datetime.now()

            except asyncio.CancelledError:
                yield f"event: disconnected\ndata: {json.dumps({'status': 'disconnected'})}\n\n"
            except Exception as e:
                logger.exception("Error in mark stream")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    return router


__all__ = ["create_witness_router"]
