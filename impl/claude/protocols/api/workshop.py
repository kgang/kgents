"""
Workshop API Endpoints (Chunk 8).

Exposes Builder's Workshop via REST/SSE API:
- GET /v1/workshop - Get or create default workshop
- POST /v1/workshop/task - Assign a new task
- GET /v1/workshop/stream - SSE stream of workshop events
- GET /v1/workshop/status - Current workshop status
- GET /v1/workshop/builders - List all builders
- GET /v1/workshop/builder/{archetype} - Get builder detail
- POST /v1/workshop/builder/{archetype}/whisper - Send whisper
- POST /v1/workshop/perturb - Inject perturbation

Synergy: patterns from protocols/api/town.py
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    StreamingResponse = None  # type: ignore
    BaseModel = object  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Pydantic Models ---


class AssignTaskRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to assign a task to the workshop."""

    description: str = Field(..., description="Task description")
    priority: int = Field(
        default=1,
        description="Task priority (1=low, 2=medium, 3=high)",
        ge=1,
        le=3,
    )


class PerturbRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to perturb the workshop flux."""

    action: str = Field(
        ...,
        description="Perturbation action: advance, handoff, complete, inject_artifact",
    )
    builder: Optional[str] = Field(
        default=None,
        description="Target builder archetype (for handoff)",
    )
    artifact: Optional[Any] = Field(
        default=None,
        description="Artifact content (for inject_artifact)",
    )


class WhisperRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to whisper to a builder."""

    message: str = Field(..., description="Message to whisper")


class BuilderSummaryResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Summary of a builder."""

    archetype: str = Field(..., description="Builder archetype")
    name: str = Field(..., description="Builder name")
    phase: str = Field(..., description="Current builder phase")
    is_active: bool = Field(..., description="Whether currently working")
    is_in_specialty: bool = Field(..., description="Whether in specialty phase")


class WorkshopStatusResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Workshop status response."""

    id: str = Field(..., description="Workshop ID")
    phase: str = Field(..., description="Current workshop phase")
    is_running: bool = Field(..., description="Whether flux is running")
    active_task: Optional[dict[str, Any]] = Field(
        default=None, description="Active task"
    )
    builders: list[BuilderSummaryResponse] = Field(..., description="Builder states")
    artifacts_count: int = Field(default=0, description="Number of artifacts")
    metrics: dict[str, Any] = Field(
        default_factory=dict, description="Execution metrics"
    )


class WorkshopPlanResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response when assigning a task."""

    task: dict[str, Any] = Field(..., description="Task details")
    assignments: dict[str, list[str]] = Field(..., description="Builder assignments")
    estimated_phases: list[str] = Field(..., description="Expected phases")
    lead_builder: str = Field(..., description="Lead builder archetype")


# --- In-Memory Storage ---


_workshop_state: dict[str, Any] = {}


def _get_or_create_workshop() -> dict[str, Any]:
    """Get or create the default workshop."""
    if "workshop" not in _workshop_state:
        from agents.town.event_bus import EventBus
        from agents.town.workshop import WorkshopEvent, WorkshopFlux, create_workshop

        event_bus: EventBus[WorkshopEvent] = EventBus()
        workshop = create_workshop(event_bus=event_bus)
        flux = WorkshopFlux(workshop)

        _workshop_state["workshop"] = workshop
        _workshop_state["flux"] = flux
        _workshop_state["event_bus"] = event_bus
        _workshop_state["id"] = "default"

    return _workshop_state


def _reset_workshop() -> dict[str, Any]:
    """Reset workshop to initial state."""
    from agents.town.event_bus import EventBus
    from agents.town.workshop import WorkshopEvent, WorkshopFlux, create_workshop

    # Close existing event bus if any
    if "event_bus" in _workshop_state:
        _workshop_state["event_bus"].close()

    event_bus: EventBus[WorkshopEvent] = EventBus()
    workshop = create_workshop(event_bus=event_bus)
    flux = WorkshopFlux(workshop)

    _workshop_state["workshop"] = workshop
    _workshop_state["flux"] = flux
    _workshop_state["event_bus"] = event_bus
    _workshop_state["id"] = "default"

    return _workshop_state


# --- Router Factory ---


def create_workshop_router() -> "APIRouter | None":
    """
    Create the workshop API router.

    Returns None if FastAPI is not available.
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/v1/workshop", tags=["workshop"])

    @router.get("", response_model=WorkshopStatusResponse)
    async def get_workshop() -> WorkshopStatusResponse:
        """Get or create the default workshop."""
        state = _get_or_create_workshop()
        workshop = state["workshop"]
        flux = state["flux"]

        builders = [
            BuilderSummaryResponse(
                archetype=b.archetype,
                name=b.name,
                phase=b.builder_phase.name,
                is_active=workshop.state.active_builder == b
                if workshop.state.active_builder
                else False,
                is_in_specialty=b.is_in_specialty,
            )
            for b in workshop.builders
        ]

        return WorkshopStatusResponse(
            id=state["id"],
            phase=workshop.state.phase.name,
            is_running=flux.is_running,
            active_task=workshop.state.active_task.to_dict()
            if workshop.state.active_task
            else None,
            builders=builders,
            artifacts_count=len(workshop.state.artifacts),
            metrics=flux.get_metrics().to_dict(),
        )

    @router.post("/task", response_model=WorkshopPlanResponse)
    async def assign_task(request: AssignTaskRequest) -> WorkshopPlanResponse:
        """Assign a task to the workshop."""
        state = _get_or_create_workshop()
        flux = state["flux"]

        # If already running, reset first
        if flux.is_running:
            flux.reset()

        try:
            plan = await flux.start(request.description, priority=request.priority)
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return WorkshopPlanResponse(
            task=plan.task.to_dict(),
            assignments=plan.assignments,
            estimated_phases=[p.name for p in plan.estimated_phases],
            lead_builder=plan.lead_builder,
        )

    @router.get("/stream")
    async def workshop_stream(speed: float = 1.0) -> StreamingResponse:
        """
        Stream workshop events via Server-Sent Events.

        Events:
        - workshop.start: Task started
        - workshop.event: WorkshopEvent
        - workshop.phase: Phase transition
        - workshop.end: Task completed
        """
        state = _get_or_create_workshop()
        flux = state["flux"]

        async def generate() -> AsyncIterator[str]:
            """Generate SSE events."""
            if not flux.is_running:
                yield f"event: workshop.idle\ndata: {json.dumps({'status': 'idle'})}\n\n"
                return

            # Send start event
            start_data = json.dumps(
                {
                    "task": flux.workshop.state.active_task.description
                    if flux.workshop.state.active_task
                    else None,
                    "phase": flux.current_phase.name,
                }
            )
            yield f"event: workshop.start\ndata: {start_data}\n\n"

            current_phase = flux.current_phase.name

            try:
                async for event in flux.run():
                    # Check for phase transition
                    if event.phase.name != current_phase:
                        current_phase = event.phase.name
                        phase_data = json.dumps({"phase": current_phase})
                        yield f"event: workshop.phase\ndata: {phase_data}\n\n"

                    # Send event
                    event_data = json.dumps(event.to_dict())
                    yield f"event: workshop.event\ndata: {event_data}\n\n"

                    # Add delay for visual effect
                    await asyncio.sleep(0.5 / speed)

            except asyncio.CancelledError:
                pass
            finally:
                # Send end event
                end_data = json.dumps(
                    {
                        "status": "completed",
                        "metrics": flux.get_metrics().to_dict(),
                    }
                )
                yield f"event: workshop.end\ndata: {end_data}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/status", response_model=WorkshopStatusResponse)
    async def workshop_status() -> WorkshopStatusResponse:
        """Get current workshop status including metrics."""
        return await get_workshop()

    @router.get("/builders")
    async def list_builders() -> dict[str, Any]:
        """List all builders with their current state."""
        state = _get_or_create_workshop()
        workshop = state["workshop"]

        builders = []
        for b in workshop.builders:
            builders.append(
                {
                    "archetype": b.archetype,
                    "name": b.name,
                    "phase": b.builder_phase.name,
                    "is_active": workshop.state.active_builder == b
                    if workshop.state.active_builder
                    else False,
                    "is_in_specialty": b.is_in_specialty,
                }
            )

        return {"builders": builders, "count": len(builders)}

    @router.get("/builder/{archetype}")
    async def get_builder(archetype: str, lod: int = 1) -> dict[str, Any]:
        """Get builder details at specified LOD."""
        state = _get_or_create_workshop()
        workshop = state["workshop"]

        builder = workshop.get_builder(archetype)
        if builder is None:
            raise HTTPException(
                status_code=404, detail=f"Builder {archetype} not found"
            )

        # LOD 0: Basic info
        result: dict[str, Any] = {
            "archetype": builder.archetype,
            "name": builder.name,
            "phase": builder.builder_phase.name,
        }

        # LOD 1: Status
        if lod >= 1:
            result["is_in_specialty"] = builder.is_in_specialty
            result["is_active"] = (
                workshop.state.active_builder == builder
                if workshop.state.active_builder
                else False
            )

        # LOD 2: Citizen info (builder extends citizen)
        if lod >= 2:
            result["citizen"] = {
                "id": builder.id,
                "region": builder.region,
                "citizen_phase": builder.phase.name,
                "eigenvectors": {
                    "warmth": builder.eigenvectors.warmth,
                    "curiosity": builder.eigenvectors.curiosity,
                    "trust": builder.eigenvectors.trust,
                    "creativity": builder.eigenvectors.creativity,
                    "patience": builder.eigenvectors.patience,
                    "resilience": builder.eigenvectors.resilience,
                    "ambition": builder.eigenvectors.ambition,
                },
            }

        return result

    @router.post("/builder/{archetype}/whisper")
    async def whisper_builder(
        archetype: str, request: WhisperRequest
    ) -> dict[str, Any]:
        """Send a whisper to a specific builder."""
        state = _get_or_create_workshop()
        workshop = state["workshop"]
        # flux available for future integration: state["flux"]

        builder = workshop.get_builder(archetype)
        if builder is None:
            raise HTTPException(
                status_code=404, detail=f"Builder {archetype} not found"
            )

        # For now, whisper is recorded but doesn't change behavior
        # Future: integrate with DialogueEngine
        return {
            "success": True,
            "builder": archetype,
            "message": f"Whispered to {builder.name}: {request.message}",
            "response": f"*{builder.name} acknowledges*",
        }

    @router.post("/perturb")
    async def perturb(request: PerturbRequest) -> dict[str, Any]:
        """Inject a perturbation into the workshop flux."""
        state = _get_or_create_workshop()
        flux = state["flux"]

        if not flux.is_running:
            raise HTTPException(
                status_code=400,
                detail="Workshop is not running. Assign a task first.",
            )

        try:
            event = await flux.perturb(
                action=request.action,
                builder=request.builder,
                artifact=request.artifact,
            )
            return {
                "success": True,
                "event": event.to_dict(),
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/reset")
    async def reset_workshop() -> dict[str, Any]:
        """Reset workshop to initial state."""
        _reset_workshop()
        return {"status": "reset", "message": "Workshop reset to idle state"}

    @router.get("/artifacts")
    async def list_artifacts() -> dict[str, Any]:
        """List all artifacts produced in current session."""
        state = _get_or_create_workshop()
        workshop = state["workshop"]

        return {
            "artifacts": [a.to_dict() for a in workshop.state.artifacts],
            "count": len(workshop.state.artifacts),
        }

    # =========================================================================
    # History Endpoints (Chunk 9)
    # =========================================================================

    @router.get("/history")
    async def get_task_history(
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get paginated task history.

        Args:
            page: Page number (1-indexed).
            page_size: Number of tasks per page (max 50).
            status: Filter by status (completed, interrupted, all).
        """
        from agents.town.history import get_history_store

        store = get_history_store()
        page_size = min(page_size, 50)  # Cap at 50

        tasks, total = store.list_tasks(page=page, page_size=page_size, status=status)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return {
            "tasks": [t.to_dict() for t in tasks],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @router.get("/history/{task_id}")
    async def get_task_detail(task_id: str) -> dict[str, Any]:
        """Get detailed task record including all events and artifacts."""
        from agents.town.history import get_history_store

        store = get_history_store()
        record = store.get_task(task_id)

        if record is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return {
            "task": record.to_dict(),
            "artifacts": [a.to_dict() for a in record.artifacts],
            "events": [e.to_dict() for e in record.events],
            "builder_contributions": record._compute_contributions(),
        }

    @router.get("/history/{task_id}/events")
    async def get_task_events(task_id: str) -> dict[str, Any]:
        """Get all events for a task (for replay)."""
        from agents.town.history import get_history_store

        store = get_history_store()
        record = store.get_task(task_id)

        if record is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return {
            "task_id": task_id,
            "events": [e.to_dict() for e in record.events],
            "count": len(record.events),
            "duration_seconds": record.duration_seconds,
        }

    # =========================================================================
    # Metrics Endpoints (Chunk 9)
    # =========================================================================

    @router.get("/metrics/aggregate")
    async def get_aggregate_metrics(period: str = "24h") -> dict[str, Any]:
        """
        Get aggregate workshop metrics for a time period.

        Args:
            period: Time period (24h, 7d, 30d, all).
        """
        from agents.town.history import get_history_store

        if period not in ("24h", "7d", "30d", "all"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period: {period}. Use 24h, 7d, 30d, or all.",
            )

        store = get_history_store()
        return store.get_aggregate_metrics(period)

    @router.get("/metrics/builder/{archetype}")
    async def get_builder_metrics(
        archetype: str, period: str = "24h"
    ) -> dict[str, Any]:
        """
        Get metrics for a specific builder archetype.

        Args:
            archetype: Builder archetype (Scout, Sage, Spark, Steady, Sync).
            period: Time period (24h, 7d, 30d, all).
        """
        from agents.town.history import get_history_store

        valid_archetypes = {"Scout", "Sage", "Spark", "Steady", "Sync"}
        if archetype not in valid_archetypes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid archetype: {archetype}. Use one of {valid_archetypes}.",
            )

        if period not in ("24h", "7d", "30d", "all"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period: {period}. Use 24h, 7d, 30d, or all.",
            )

        store = get_history_store()
        return store.get_builder_metrics(archetype, period)

    @router.get("/metrics/flow")
    async def get_flow_metrics() -> dict[str, Any]:
        """Get handoff flow metrics between builders."""
        from agents.town.history import get_history_store

        store = get_history_store()
        return store.get_flow_metrics()

    return router


# --- Exports ---


__all__ = [
    "create_workshop_router",
    "AssignTaskRequest",
    "PerturbRequest",
    "WhisperRequest",
    "BuilderSummaryResponse",
    "WorkshopStatusResponse",
    "WorkshopPlanResponse",
]
