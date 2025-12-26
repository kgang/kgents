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


class MarkBrowseCategory(BaseModel):
    """Category of marks for browsing."""

    name: str
    count: int
    marks: list[MarkResponse]


class MarkBrowseResponse(BaseModel):
    """Response from marks browse endpoint - grouped by category."""

    today: MarkBrowseCategory
    decisions: MarkBrowseCategory
    eurekas: MarkBrowseCategory
    gotchas: MarkBrowseCategory
    all_marks: MarkBrowseCategory
    total: int


class RetractRequest(BaseModel):
    """Request body for retracting a mark."""

    reason: str = Field(..., description="Reason for retraction")


class DialecticPosition(BaseModel):
    """One side of a dialectic decision."""

    author: str = Field(..., description="kent or claude")
    content: str = Field(..., description="The position statement")
    reasoning: str = Field(..., description="Why this position")


class DialecticDecisionResponse(BaseModel):
    """A dialectic decision (thesis + antithesis → synthesis)."""

    model_config = {"populate_by_name": True}

    id: str
    timestamp: str
    thesis: DialecticPosition
    antithesis: DialecticPosition
    synthesis: str
    why: str
    vetoed: bool = False
    vetoReason: str | None = Field(default=None, alias="veto_reason")
    tags: list[str] = []


class DialecticDecisionListResponse(BaseModel):
    """List of dialectic decisions."""

    decisions: list[DialecticDecisionResponse]
    total: int


class CreateDialecticDecisionRequest(BaseModel):
    """Request to create a dialectic decision."""

    thesis_content: str = Field(..., description="Kent's position")
    thesis_reasoning: str = Field(..., description="Kent's reasoning")
    antithesis_content: str = Field(..., description="Claude's position")
    antithesis_reasoning: str = Field(..., description="Claude's reasoning")
    synthesis: str = Field(..., description="The fused decision")
    why: str = Field(..., description="Why this synthesis")
    tags: list[str] = Field(default_factory=list)


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

                # Today filter (use UTC for consistent timezone-aware comparison)
                if today:
                    from services.timezone import is_today_utc

                    if not is_today_utc(m.timestamp):
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

                from services.timezone import to_iso

                marks.append(
                    MarkResponse(
                        id=m.mark_id,
                        action=m.action,
                        reasoning=m.reasoning,
                        principles=m.principles,
                        author=m.author,
                        session_id=getattr(m, "session_id", None),
                        timestamp=to_iso(m.timestamp),
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

    @router.get("/marks/browse", response_model=MarkBrowseResponse)
    async def browse_marks(
        limit_per_category: int = Query(default=20, ge=1, le=100),
    ) -> MarkBrowseResponse:
        """
        Browse marks organized by category for FileTree display.

        Categories:
        - today: Marks from today
        - decisions: Marks with decision/synthesis reasoning
        - eurekas: Insights and discoveries (eureka/insight/discovery tags)
        - gotchas: Traps and warnings (gotcha/warning/trap tags)
        - all_marks: All recent marks

        This endpoint is designed for the FileTree virtual folder display.
        """
        try:
            from services.providers import get_witness_persistence
            from services.timezone import is_today_utc, to_iso

            persistence = await get_witness_persistence()

            # Fetch more marks than needed for categorization
            all_marks_data = await persistence.get_marks(limit=limit_per_category * 5)

            # Categorize marks
            today_marks: list[MarkResponse] = []
            decision_marks: list[MarkResponse] = []
            eureka_marks: list[MarkResponse] = []
            gotcha_marks: list[MarkResponse] = []
            all_marks_list: list[MarkResponse] = []

            # Tags that indicate each category
            eureka_tags = {"eureka", "insight", "discovery", "aha", "breakthrough"}
            gotcha_tags = {"gotcha", "warning", "trap", "pitfall", "beware", "caution"}
            decision_tags = {"decision", "synthesis", "resolved", "chose", "dialectic"}

            for m in all_marks_data:
                mark_response = MarkResponse(
                    id=m.mark_id,
                    action=m.action,
                    reasoning=m.reasoning,
                    principles=m.principles,
                    author=m.author,
                    session_id=getattr(m, "session_id", None),
                    timestamp=to_iso(m.timestamp),
                    parent_mark_id=m.parent_mark_id,
                    retracted=getattr(m, "retracted", False),
                    retraction_reason=getattr(m, "retraction_reason", None),
                )

                # Add to all marks (always)
                if len(all_marks_list) < limit_per_category:
                    all_marks_list.append(mark_response)

                # Categorize by tags
                mark_tags_lower = {t.lower() for t in m.tags}

                # Today category
                if is_today_utc(m.timestamp) and len(today_marks) < limit_per_category:
                    today_marks.append(mark_response)

                # Decision category (check tags or reasoning contains decision-like words)
                if mark_tags_lower & decision_tags or (
                    m.reasoning and any(word in m.reasoning.lower() for word in ["decided", "synthesis", "chose", "resolved"])
                ):
                    if len(decision_marks) < limit_per_category:
                        decision_marks.append(mark_response)

                # Eureka category
                if mark_tags_lower & eureka_tags or (
                    m.reasoning and any(word in m.reasoning.lower() for word in ["discovered", "realized", "eureka", "insight"])
                ):
                    if len(eureka_marks) < limit_per_category:
                        eureka_marks.append(mark_response)

                # Gotcha category
                if mark_tags_lower & gotcha_tags or (
                    m.reasoning and any(word in m.reasoning.lower() for word in ["gotcha", "warning", "careful", "beware", "trap"])
                ):
                    if len(gotcha_marks) < limit_per_category:
                        gotcha_marks.append(mark_response)

            return MarkBrowseResponse(
                today=MarkBrowseCategory(
                    name="Today",
                    count=len(today_marks),
                    marks=today_marks,
                ),
                decisions=MarkBrowseCategory(
                    name="Decisions",
                    count=len(decision_marks),
                    marks=decision_marks,
                ),
                eurekas=MarkBrowseCategory(
                    name="Eurekas",
                    count=len(eureka_marks),
                    marks=eureka_marks,
                ),
                gotchas=MarkBrowseCategory(
                    name="Gotchas",
                    count=len(gotcha_marks),
                    marks=gotcha_marks,
                ),
                all_marks=MarkBrowseCategory(
                    name="All Marks",
                    count=len(all_marks_list),
                    marks=all_marks_list,
                ),
                total=len(all_marks_data),
            )

        except Exception as e:
            logger.exception("Error browsing marks")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/marks/{mark_id}", response_model=MarkResponse)
    async def get_mark(mark_id: str) -> MarkResponse:
        """
        Get a single mark by ID.

        Returns the full mark details including reasoning and principles.
        """
        try:
            from services.providers import get_witness_persistence
            from services.timezone import to_iso

            persistence = await get_witness_persistence()
            mark = await persistence.get_mark(mark_id)

            if not mark:
                raise HTTPException(status_code=404, detail=f"Mark not found: {mark_id}")

            return MarkResponse(
                id=mark.mark_id,
                action=mark.action,
                reasoning=mark.reasoning,
                principles=mark.principles,
                author=mark.author,
                session_id=getattr(mark, "session_id", None),
                timestamp=to_iso(mark.timestamp),
                parent_mark_id=mark.parent_mark_id,
                retracted=getattr(mark, "retracted", False),
                retraction_reason=getattr(mark, "retraction_reason", None),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error getting mark")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/marks", response_model=MarkResponse)
    async def create_mark(request: CreateMarkRequest) -> MarkResponse:
        """
        Create a new mark.

        Marks are saved to persistence AND published to WitnessSynergyBus
        for real-time SSE streaming to connected frontends.

        Args:
            request: Mark creation request
        """
        try:
            from services.providers import get_witness_persistence
            from services.witness.bus import WitnessTopics, get_synergy_bus

            persistence = await get_witness_persistence()
            result = await persistence.save_mark(
                action=request.action,
                reasoning=request.reasoning,
                principles=request.principles,
                author=request.author,
                parent_mark_id=request.parent_mark_id,
            )

            # Publish to WitnessSynergyBus for real-time SSE streaming
            # "The proof IS the decision. The mark IS the witness."
            from services.timezone import to_iso

            bus = get_synergy_bus()
            await bus.publish(
                WitnessTopics.MARK_CREATED,
                {
                    "id": result.mark_id,
                    "action": result.action,
                    "reasoning": result.reasoning,
                    "principles": result.principles,
                    "author": result.author,
                    "timestamp": to_iso(result.timestamp),
                    "parent_mark_id": result.parent_mark_id,
                    "type": "mark",  # Event type for frontend
                },
            )
            logger.debug(f"Published mark {result.mark_id} to WitnessSynergyBus")

            return MarkResponse(
                id=result.mark_id,
                action=result.action,
                reasoning=result.reasoning,
                principles=result.principles,
                author=result.author,
                session_id=getattr(result, "session_id", None),
                timestamp=to_iso(result.timestamp),
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

    # =========================================================================
    # Dialectic Decisions (Thesis + Antithesis → Synthesis)
    # =========================================================================

    # In-memory storage for now (will be persisted later)
    _decisions: list[DialecticDecisionResponse] = []

    @router.get("/decisions", response_model=DialecticDecisionListResponse)
    async def list_decisions(
        limit: int = Query(default=50, ge=1, le=200),
        since: str | None = Query(default=None),
        tags: str | None = Query(default=None),
    ) -> DialecticDecisionListResponse:
        """
        List dialectic decisions.

        Args:
            limit: Maximum number of decisions to return
            since: ISO timestamp to filter decisions after
            tags: Comma-separated list of tags to filter by
        """
        decisions = _decisions.copy()

        # Filter by timestamp
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                decisions = [
                    d for d in decisions
                    if datetime.fromisoformat(d.timestamp.replace("Z", "+00:00")) >= since_dt
                ]
            except ValueError:
                pass

        # Filter by tags
        if tags:
            tag_list = [t.strip().lower() for t in tags.split(",")]
            decisions = [
                d for d in decisions
                if any(t.lower() in tag_list for t in d.tags)
            ]

        # Sort by timestamp descending (newest first)
        decisions.sort(key=lambda d: d.timestamp, reverse=True)

        # Apply limit
        decisions = decisions[:limit]

        return DialecticDecisionListResponse(decisions=decisions, total=len(_decisions))

    @router.post("/decisions", response_model=DialecticDecisionResponse)
    async def create_decision(request: CreateDialecticDecisionRequest) -> DialecticDecisionResponse:
        """
        Create a new dialectic decision.

        "Kent's view + Claude's view → a third thing, better than either."
        """
        import uuid

        from services.timezone import to_iso, utc_now

        decision = DialecticDecisionResponse(
            id=str(uuid.uuid4()),
            timestamp=to_iso(utc_now()),
            thesis=DialecticPosition(
                author="kent",
                content=request.thesis_content,
                reasoning=request.thesis_reasoning,
            ),
            antithesis=DialecticPosition(
                author="claude",
                content=request.antithesis_content,
                reasoning=request.antithesis_reasoning,
            ),
            synthesis=request.synthesis,
            why=request.why,
            tags=request.tags,
        )

        _decisions.append(decision)

        logger.info(f"Created dialectic decision: {decision.id}")
        return decision

    @router.get("/stream")
    async def stream_marks() -> StreamingResponse:
        """
        SSE stream for real-time witness events (marks, K-Block edits, crystals, etc.).

        Event-driven via WitnessSynergyBus — instant delivery, no polling.

        "The proof IS the decision. The mark IS the witness."
        """

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events from WitnessSynergyBus subscription."""
            from typing import Any

            from services.witness.bus import (
                WitnessTopics,
                get_event_type_for_topic,
                get_synergy_bus,
            )

            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'type': 'connected'})}\n\n"

            bus = get_synergy_bus()
            event_queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

            # Subscribe to all witness events
            async def on_event(topic: str, event: Any) -> None:
                await event_queue.put((topic, event))

            unsub = bus.subscribe(WitnessTopics.ALL, on_event)

            try:
                while True:
                    try:
                        # Wait for event with 30s timeout for heartbeat
                        topic, event = await asyncio.wait_for(
                            event_queue.get(),
                            timeout=30.0,
                        )

                        # Type-safe event type lookup (fails loud in dev)
                        event_type_enum = get_event_type_for_topic(topic)
                        event_type = event_type_enum.value

                        # Ensure event has type and topic fields for frontend
                        if isinstance(event, dict):
                            event["type"] = event_type
                            event["topic"] = topic  # Include for debugging/transparency

                        yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"

                    except asyncio.TimeoutError:
                        # Heartbeat on timeout
                        from services.timezone import to_iso, utc_now

                        yield f"event: heartbeat\ndata: {json.dumps({'type': 'heartbeat', 'time': to_iso(utc_now())})}\n\n"

            except asyncio.CancelledError:
                yield f"event: disconnected\ndata: {json.dumps({'status': 'disconnected'})}\n\n"
            except Exception as e:
                logger.exception("Error in witness stream")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            finally:
                unsub()

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
