"""
Constitutional API: Phase 1 Witness REST endpoints.

Provides:
- GET /api/witness/constitutional/{agent_id} - Constitutional health
- GET /api/witness/constitutional/{agent_id}/history - Alignment history
- GET /api/witness/constitutional/stream - SSE for constitutional events

Integration:
    - Uses ConstitutionalTrustComputer to compute trust levels
    - Reads from Crystal.constitutional_meta for history
    - Streams constitutional evaluations via WitnessSynergyBus

Philosophy:
    "Trust is earned through demonstrated alignment."
    — Article V: Trust Accumulation

See: spec/principles/CONSTITUTION.md → Article V
See: services/witness/trust/constitutional_trust.py
See: services/witness/crystal.py → ConstitutionalCrystalMeta
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator

try:
    from fastapi import APIRouter, HTTPException, Path, Query
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class PrincipleScore(BaseModel):  # type: ignore[misc]
    """Per-principle alignment score."""

    principle: str = Field(..., description="Principle name (e.g., ETHICAL, COMPOSABLE)")
    score: float = Field(..., description="Alignment score (0.0 - 1.0)")
    weight: float = Field(..., description="Principle weight in computation")


class ConstitutionalHealthResponse(BaseModel):  # type: ignore[misc]
    """Constitutional health for an agent."""

    agent_id: str
    trust_level: str = Field(
        ..., description="L0-L3 trust level (READ_ONLY, BOUNDED, SUGGESTION, AUTONOMOUS)"
    )
    trust_level_value: int = Field(..., description="Numeric trust level (0-3)")

    # Metrics
    total_marks_analyzed: int
    average_alignment: float = Field(..., description="Weighted average alignment (0.0 - 1.0)")
    violation_rate: float = Field(..., description="Proportion of marks below threshold")
    trust_capital: float = Field(..., description="Accumulated trust from high-alignment marks")

    # Per-principle breakdown
    principle_averages: dict[str, float] = Field(
        default_factory=dict,
        description="Average score per principle",
    )
    dominant_principles: list[str] = Field(
        default_factory=list,
        description="Top 3 principles by score",
    )

    # Reasoning
    reasoning: str = Field(..., description="Human-readable explanation of trust level")

    # Recommendations (future: from ConstitutionalAdvisor)
    recommendations: list[str] = Field(
        default_factory=list,
        description="Suggestions for improving alignment",
    )


class AlignmentHistoryPoint(BaseModel):  # type: ignore[misc]
    """Single point in alignment trajectory."""

    timestamp: str
    alignment: float
    crystal_id: str
    level: str = Field(..., description="SESSION, DAY, WEEK, EPOCH")


class ConstitutionalHistoryResponse(BaseModel):  # type: ignore[misc]
    """Alignment history for an agent."""

    agent_id: str
    days: int

    # Trajectory data (for sparkline)
    trajectory: list[AlignmentHistoryPoint]

    # Crystals with constitutional metadata
    crystals: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Crystals with constitutional_meta",
    )

    # Aggregate stats
    total_marks: int
    total_violations: int
    average_alignment: float


# =============================================================================
# Router Factory
# =============================================================================


def create_constitutional_router() -> "APIRouter | None":
    """Create the constitutional API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/witness/constitutional", tags=["witness", "constitutional"])

    @router.get("/{agent_id}", response_model=ConstitutionalHealthResponse)
    async def get_constitutional_health(
        agent_id: str = Path(..., description="Agent identifier (e.g., 'claude', 'witness')"),
    ) -> ConstitutionalHealthResponse:
        """
        Get constitutional health for an agent.

        Computes trust level based on constitutional history using
        ConstitutionalTrustComputer. Analyzes crystals (which contain
        aggregated constitutional metadata) to determine:
        - Trust level (L0-L3)
        - Alignment scores per principle
        - Violation rate
        - Trust capital

        Args:
            agent_id: Agent identifier

        Returns:
            ConstitutionalHealthResponse with trust level and metrics
        """
        try:
            from services.providers import get_witness_persistence
            from services.witness.trust.constitutional_trust import (
                ConstitutionalTrustComputer,
            )

            persistence = await get_witness_persistence()

            # Fetch recent crystals (last 30 days for trust computation)
            since = datetime.now() - timedelta(days=30)
            # Note: Using get_marks as proxy since get_crystals may not be implemented
            # In production, you'd want persistence.get_crystals(since=since)
            # For now, we'll compute from marks directly
            marks = await persistence.get_marks(limit=1000)

            # Filter marks by agent_id (if origin matches)
            agent_marks = [m for m in marks if m.origin == agent_id]

            # For now, create a session-level crystal on-the-fly from marks
            # In production, you'd query actual stored crystals
            if agent_marks:
                from services.witness.crystal import (
                    ConstitutionalCrystalMeta,
                    Crystal,
                    CrystalLevel,
                )

                # Create mock crystal with constitutional metadata
                meta = ConstitutionalCrystalMeta.from_marks(agent_marks)
                crystal = Crystal(
                    level=CrystalLevel.SESSION,
                    insight=f"Recent activity for {agent_id}",
                    significance="Constitutional evaluation",
                    constitutional_meta=meta,
                )
                crystals = [crystal]
            else:
                crystals = []

            # Compute trust
            computer = ConstitutionalTrustComputer()
            result = await computer.compute_trust(agent_id, crystals)

            # Generate recommendations based on trust level
            recommendations = []
            if result.trust_level.value < 3:
                if result.average_alignment < 0.9:
                    recommendations.append(
                        f"Improve average alignment from {result.average_alignment:.2f} to 0.9+ for L3"
                    )
                if result.violation_rate >= 0.01:
                    recommendations.append(
                        f"Reduce violation rate from {result.violation_rate:.1%} to <1% for L3"
                    )
                if result.trust_capital < 1.0:
                    recommendations.append(
                        f"Accumulate {1.0 - result.trust_capital:.2f} more trust capital for L3"
                    )

            return ConstitutionalHealthResponse(
                agent_id=agent_id,
                trust_level=result.trust_level.name,
                trust_level_value=result.trust_level.value,
                total_marks_analyzed=result.total_marks_analyzed,
                average_alignment=result.average_alignment,
                violation_rate=result.violation_rate,
                trust_capital=result.trust_capital,
                principle_averages=result.principle_averages,
                dominant_principles=list(result.dominant_principles),
                reasoning=result.reasoning,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.exception(f"Error computing constitutional health for {agent_id}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{agent_id}/history", response_model=ConstitutionalHistoryResponse)
    async def get_constitutional_history(
        agent_id: str = Path(..., description="Agent identifier"),
        days: int = Query(default=7, ge=1, le=90, description="Number of days to retrieve"),
        limit: int = Query(default=100, ge=1, le=500, description="Max trajectory points"),
    ) -> ConstitutionalHistoryResponse:
        """
        Get constitutional alignment history for an agent.

        Returns alignment trajectory over time, showing how constitutional
        compliance has evolved. Useful for sparkline visualizations and
        trend analysis.

        Args:
            agent_id: Agent identifier
            days: Number of days to retrieve (1-90)
            limit: Maximum trajectory points to return

        Returns:
            ConstitutionalHistoryResponse with trajectory and crystals
        """
        try:
            from services.providers import get_witness_persistence
            from services.witness.crystal import ConstitutionalCrystalMeta

            persistence = await get_witness_persistence()

            # Fetch marks from last N days
            since = datetime.now() - timedelta(days=days)
            marks = await persistence.get_marks(limit=1000)

            # Filter by agent and timeframe
            agent_marks = [m for m in marks if m.origin == agent_id and m.timestamp >= since]

            # Build trajectory from constitutional alignment in marks
            trajectory: list[AlignmentHistoryPoint] = []
            for mark in agent_marks[:limit]:
                if mark.constitutional:
                    trajectory.append(
                        AlignmentHistoryPoint(
                            timestamp=mark.timestamp.isoformat(),
                            alignment=mark.constitutional.weighted_total,
                            crystal_id=mark.id,  # Using mark_id as proxy
                            level="MARK",
                        )
                    )

            # Aggregate stats
            total_marks = len(agent_marks)
            alignments = [m.constitutional for m in agent_marks if m.constitutional]
            total_violations = sum(1 for a in alignments if not a.is_compliant)
            average_alignment = (
                sum(a.weighted_total for a in alignments) / len(alignments) if alignments else 0.0
            )

            # Convert marks to crystal-like format for response
            # In production, you'd return actual crystals with constitutional_meta
            crystals_data = []
            if agent_marks and agent_marks[0].constitutional:
                meta = ConstitutionalCrystalMeta.from_marks(agent_marks)
                crystals_data.append(
                    {
                        "id": f"session-{agent_id}-{int(datetime.now().timestamp())}",
                        "level": "SESSION",
                        "insight": f"{len(agent_marks)} marks analyzed",
                        "constitutional_meta": meta.to_dict(),
                    }
                )

            return ConstitutionalHistoryResponse(
                agent_id=agent_id,
                days=days,
                trajectory=trajectory,
                crystals=crystals_data,
                total_marks=total_marks,
                total_violations=total_violations,
                average_alignment=average_alignment,
            )

        except Exception as e:
            logger.exception(f"Error fetching constitutional history for {agent_id}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/stream")
    async def stream_constitutional_events() -> StreamingResponse:
        """
        SSE stream for constitutional events.

        Streams constitutional evaluations in real-time as marks are created
        and evaluated. Enables live constitutional dashboard updates.

        Event types:
        - constitutional_evaluated: New mark with constitutional alignment
        - trust_level_changed: Agent trust level escalated/de-escalated

        Returns:
            SSE StreamingResponse
        """

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events from WitnessSynergyBus subscription."""
            from services.witness.bus import WitnessTopics, get_synergy_bus

            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'type': 'connected'})}\n\n"

            bus = get_synergy_bus()
            event_queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

            # Subscribe to constitutional events
            async def on_event(topic: str, event: Any) -> None:
                await event_queue.put((topic, event))

            # Subscribe to MARK_CREATED (which may include constitutional metadata)
            unsub = bus.subscribe(WitnessTopics.MARK_CREATED, on_event)

            try:
                while True:
                    try:
                        # Wait for event with 30s timeout for heartbeat
                        topic, event = await asyncio.wait_for(
                            event_queue.get(),
                            timeout=30.0,
                        )

                        # Filter for events with constitutional metadata
                        if isinstance(event, dict) and "constitutional" in event:
                            # Ensure event has type field
                            event["type"] = "constitutional_evaluated"
                            yield f"event: constitutional_evaluated\ndata: {json.dumps(event)}\n\n"

                    except asyncio.TimeoutError:
                        # Heartbeat on timeout
                        yield f"event: heartbeat\ndata: {json.dumps({'type': 'heartbeat', 'time': datetime.now().isoformat()})}\n\n"

            except asyncio.CancelledError:
                yield f"event: disconnected\ndata: {json.dumps({'status': 'disconnected'})}\n\n"
            except Exception as e:
                logger.exception("Error in constitutional stream")
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


__all__ = ["create_constitutional_router"]
