"""
AGENTESE World Workshop Context: Builder's Workshop API.

Migrates protocols/api/workshop.py to @node pattern (AD-009 Phase 3).

Routes migrated (16 total):
- GET /v1/workshop → world.workshop.manifest
- POST /v1/workshop/task → world.workshop.task
- GET /v1/workshop/stream → world.workshop.stream (SSE)
- GET /v1/workshop/status → world.workshop.status
- GET /v1/workshop/builders → world.workshop.builders
- GET /v1/workshop/builder/{archetype} → world.workshop.builder[archetype=...]
- POST /v1/workshop/builder/{archetype}/whisper → world.workshop.whisper
- POST /v1/workshop/perturb → world.workshop.perturb
- POST /v1/workshop/reset → world.workshop.reset
- GET /v1/workshop/artifacts → world.workshop.artifacts
- GET /v1/workshop/history → world.workshop.history
- GET /v1/workshop/history/{task_id} → world.workshop.task_detail
- GET /v1/workshop/history/{task_id}/events → world.workshop.task_events
- GET /v1/workshop/metrics/aggregate → world.workshop.metrics
- GET /v1/workshop/metrics/builder/{archetype} → world.workshop.builder_metrics
- GET /v1/workshop/metrics/flow → world.workshop.flow_metrics

AGENTESE: world.workshop.*

See: plans/agentese-router-consolidation.md (Phase 3.2)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncGenerator

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# Workshop affordances
WORKSHOP_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "task",
    "stream",
    "status",
    "builders",
    "builder",
    "whisper",
    "perturb",
    "reset",
    "artifacts",
    "history",
    "task_detail",
    "task_events",
    "metrics",
    "builder_metrics",
    "flow_metrics",
)

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


@node(
    "world.workshop",
    description="Builder's Workshop - multi-builder creative collaboration with Flux streaming",
)
@dataclass
class WorkshopNode(BaseLogosNode):
    """
    world.workshop - Builder's Workshop interface.

    Provides:
    - Task assignment and management
    - Builder control and whispers
    - SSE streaming of workshop events
    - History and metrics tracking
    """

    _handle: str = "world.workshop"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Workshop affordances - available to all archetypes."""
        return WORKSHOP_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get or create the default workshop",
        examples=["world.workshop.manifest"],
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get or create the default workshop."""
        try:
            state = _get_or_create_workshop()
            workshop = state["workshop"]
            flux = state["flux"]

            builders = [
                {
                    "archetype": b.archetype,
                    "name": b.name,
                    "phase": b.builder_phase.name,
                    "is_active": workshop.state.active_builder == b
                    if workshop.state.active_builder
                    else False,
                    "is_in_specialty": b.is_in_specialty,
                }
                for b in workshop.builders
            ]

            return {
                "id": state["id"],
                "phase": workshop.state.phase.name,
                "is_running": flux.is_running,
                "active_task": workshop.state.active_task.to_dict()
                if workshop.state.active_task
                else None,
                "builders": builders,
                "artifacts_count": len(workshop.state.artifacts),
                "metrics": flux.get_metrics().to_dict(),
            }
        except ImportError as e:
            logger.warning(f"Workshop not available: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshop")],
        help="Assign a task to the workshop",
        examples=["world.workshop.task[description='Build a feature', priority=2]"],
    )
    async def task(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Assign a task to the workshop.

        Args:
            description: Task description (required)
            priority: Task priority 1-3 (default: 1)

        Returns:
            WorkshopPlanResponse with task, assignments, estimated_phases, lead_builder
        """
        description = kwargs.get("description")
        priority = kwargs.get("priority", 1)

        if not description:
            return {"error": "description required"}

        try:
            state = _get_or_create_workshop()
            flux = state["flux"]

            # If already running, reset first
            if flux.is_running:
                flux.reset()

            try:
                plan = await flux.start(description, priority=priority)
            except RuntimeError as e:
                return {"error": str(e)}

            return {
                "task": plan.task.to_dict(),
                "assignments": plan.assignments,
                "estimated_phases": [p.name for p in plan.estimated_phases],
                "lead_builder": plan.lead_builder,
            }
        except ImportError as e:
            logger.warning(f"Workshop not available: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Stream workshop events via SSE",
        examples=["world.workshop.stream[speed=1.0]"],
    )
    async def stream(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream workshop events via Server-Sent Events.

        Args:
            speed: Playback speed multiplier (default: 1.0)

        Yields:
            Event dicts: workshop.start, workshop.event, workshop.phase, workshop.end
        """
        speed = kwargs.get("speed", 1.0)

        try:
            state = _get_or_create_workshop()
            flux = state["flux"]

            if not flux.is_running:
                yield {"type": "workshop.idle", "status": "idle"}
                return

            # Send start event
            yield {
                "type": "workshop.start",
                "task": flux.workshop.state.active_task.description
                if flux.workshop.state.active_task
                else None,
                "phase": flux.current_phase.name,
            }

            current_phase = flux.current_phase.name

            try:
                async for event in flux.run():
                    # Check for phase transition
                    if event.phase.name != current_phase:
                        current_phase = event.phase.name
                        yield {"type": "workshop.phase", "phase": current_phase}

                    # Send event
                    yield {"type": "workshop.event", **event.to_dict()}

                    # Add delay for visual effect
                    await asyncio.sleep(0.5 / speed)

            except asyncio.CancelledError:
                pass
            finally:
                # Send end event
                yield {
                    "type": "workshop.end",
                    "status": "completed",
                    "metrics": flux.get_metrics().to_dict(),
                }

        except ImportError as e:
            logger.warning(f"Workshop not available: {e}")
            yield {"type": "error", "error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get current workshop status including metrics",
        examples=["world.workshop.status"],
    )
    async def status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current workshop status including metrics."""
        return await self.manifest(observer, **kwargs)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all builders with their current state",
        examples=["world.workshop.builders"],
    )
    async def builders(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List all builders with their current state."""
        try:
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
        except ImportError as e:
            return {"error": str(e), "builders": [], "count": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get builder details at specified LOD",
        examples=["world.workshop.builder[archetype='Scout', lod=2]"],
    )
    async def builder(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get builder details at specified LOD.

        Args:
            archetype: Builder archetype (required)
            lod: Level of detail 0-2 (default: 1)

        Returns:
            Builder details with archetype, name, phase, and optional citizen info
        """
        archetype = kwargs.get("archetype")
        lod = kwargs.get("lod", 1)

        if not archetype:
            return {"error": "archetype required"}

        try:
            state = _get_or_create_workshop()
            workshop = state["workshop"]

            builder_obj = workshop.get_builder(archetype)
            if builder_obj is None:
                return {"error": f"Builder {archetype} not found"}

            # LOD 0: Basic info
            result: dict[str, Any] = {
                "archetype": builder_obj.archetype,
                "name": builder_obj.name,
                "phase": builder_obj.builder_phase.name,
            }

            # LOD 1: Status
            if lod >= 1:
                result["is_in_specialty"] = builder_obj.is_in_specialty
                result["is_active"] = (
                    workshop.state.active_builder == builder_obj
                    if workshop.state.active_builder
                    else False
                )

            # LOD 2: Citizen info (builder extends citizen)
            if lod >= 2:
                result["citizen"] = {
                    "id": builder_obj.id,
                    "region": builder_obj.region,
                    "citizen_phase": builder_obj.phase.name,
                    "eigenvectors": {
                        "warmth": builder_obj.eigenvectors.warmth,
                        "curiosity": builder_obj.eigenvectors.curiosity,
                        "trust": builder_obj.eigenvectors.trust,
                        "creativity": builder_obj.eigenvectors.creativity,
                        "patience": builder_obj.eigenvectors.patience,
                        "resilience": builder_obj.eigenvectors.resilience,
                        "ambition": builder_obj.eigenvectors.ambition,
                    },
                }

            return result
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshop")],
        help="Send a whisper to a specific builder",
        examples=["world.workshop.whisper[archetype='Scout', message='Focus on tests']"],
    )
    async def whisper(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Send a whisper to a specific builder.

        Args:
            archetype: Builder archetype (required)
            message: Message to whisper (required)

        Returns:
            Whisper confirmation with builder response
        """
        archetype = kwargs.get("archetype")
        message = kwargs.get("message")

        if not archetype:
            return {"error": "archetype required"}
        if not message:
            return {"error": "message required"}

        try:
            state = _get_or_create_workshop()
            workshop = state["workshop"]

            builder_obj = workshop.get_builder(archetype)
            if builder_obj is None:
                return {"error": f"Builder {archetype} not found"}

            # For now, whisper is recorded but doesn't change behavior
            return {
                "success": True,
                "builder": archetype,
                "message": f"Whispered to {builder_obj.name}: {message}",
                "response": f"*{builder_obj.name} acknowledges*",
            }
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshop")],
        help="Inject a perturbation into the workshop flux",
        examples=["world.workshop.perturb[action='advance']"],
    )
    async def perturb(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Inject a perturbation into the workshop flux.

        Args:
            action: Perturbation action (advance, handoff, complete, inject_artifact)
            builder: Target builder archetype (for handoff)
            artifact: Artifact content (for inject_artifact)

        Returns:
            Perturbation result with event details
        """
        action = kwargs.get("action")
        builder = kwargs.get("builder")
        artifact = kwargs.get("artifact")

        if not action:
            return {"error": "action required"}

        try:
            state = _get_or_create_workshop()
            flux = state["flux"]

            if not flux.is_running:
                return {"error": "Workshop is not running. Assign a task first."}

            try:
                event = await flux.perturb(
                    action=action,
                    builder=builder,
                    artifact=artifact,
                )
                return {
                    "success": True,
                    "event": event.to_dict(),
                }
            except ValueError as e:
                return {"error": str(e)}
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshop")],
        help="Reset workshop to initial state",
        examples=["world.workshop.reset"],
    )
    async def reset(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset workshop to initial state."""
        try:
            _reset_workshop()
            return {"status": "reset", "message": "Workshop reset to idle state"}
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all artifacts produced in current session",
        examples=["world.workshop.artifacts"],
    )
    async def artifacts(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List all artifacts produced in current session."""
        try:
            state = _get_or_create_workshop()
            workshop = state["workshop"]

            return {
                "artifacts": [a.to_dict() for a in workshop.state.artifacts],
                "count": len(workshop.state.artifacts),
            }
        except ImportError as e:
            return {"error": str(e), "artifacts": [], "count": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get paginated task history",
        examples=["world.workshop.history[page=1, page_size=10]"],
    )
    async def history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get paginated task history.

        Args:
            page: Page number (1-indexed, default: 1)
            page_size: Number of tasks per page (max 50, default: 10)
            status: Filter by status (completed, interrupted, all)

        Returns:
            Paginated task history
        """
        page = kwargs.get("page", 1)
        page_size = min(kwargs.get("page_size", 10), 50)
        status = kwargs.get("status")

        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            tasks, total = store.list_tasks(page=page, page_size=page_size, status=status)
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

            return {
                "tasks": [t.to_dict() for t in tasks],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        except ImportError as e:
            return {"error": str(e), "tasks": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get detailed task record including all events and artifacts",
        examples=["world.workshop.task_detail[task_id='abc123']"],
    )
    async def task_detail(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get detailed task record including all events and artifacts.

        Args:
            task_id: Task ID (required)

        Returns:
            Task details with artifacts and events
        """
        task_id = kwargs.get("task_id")
        if not task_id:
            return {"error": "task_id required"}

        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            record = store.get_task(task_id)

            if record is None:
                return {"error": f"Task {task_id} not found"}

            return {
                "task": record.to_dict(),
                "artifacts": [a.to_dict() for a in record.artifacts],
                "events": [e.to_dict() for e in record.events],
                "builder_contributions": record._compute_contributions(),
            }
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get all events for a task (for replay)",
        examples=["world.workshop.task_events[task_id='abc123']"],
    )
    async def task_events(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get all events for a task (for replay).

        Args:
            task_id: Task ID (required)

        Returns:
            List of events with count and duration
        """
        task_id = kwargs.get("task_id")
        if not task_id:
            return {"error": "task_id required"}

        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            record = store.get_task(task_id)

            if record is None:
                return {"error": f"Task {task_id} not found"}

            return {
                "task_id": task_id,
                "events": [e.to_dict() for e in record.events],
                "count": len(record.events),
                "duration_seconds": record.duration_seconds,
            }
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get aggregate workshop metrics for a time period",
        examples=["world.workshop.metrics[period='24h']"],
    )
    async def metrics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get aggregate workshop metrics for a time period.

        Args:
            period: Time period (24h, 7d, 30d, all). Default: 24h

        Returns:
            Aggregate metrics dict
        """
        period = kwargs.get("period", "24h")

        if period not in ("24h", "7d", "30d", "all"):
            return {"error": f"Invalid period: {period}. Use 24h, 7d, 30d, or all."}

        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            return store.get_aggregate_metrics(period)
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get metrics for a specific builder archetype",
        examples=["world.workshop.builder_metrics[archetype='Scout', period='24h']"],
    )
    async def builder_metrics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get metrics for a specific builder archetype.

        Args:
            archetype: Builder archetype (Scout, Sage, Spark, Steady, Sync)
            period: Time period (24h, 7d, 30d, all). Default: 24h

        Returns:
            Builder performance metrics
        """
        archetype = kwargs.get("archetype")
        period = kwargs.get("period", "24h")

        if not archetype:
            return {"error": "archetype required"}

        valid_archetypes = {"Scout", "Sage", "Spark", "Steady", "Sync"}
        if archetype not in valid_archetypes:
            return {"error": f"Invalid archetype: {archetype}. Use one of {valid_archetypes}."}

        if period not in ("24h", "7d", "30d", "all"):
            return {"error": f"Invalid period: {period}. Use 24h, 7d, 30d, or all."}

        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            return store.get_builder_metrics(archetype, period)
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get handoff flow metrics between builders",
        examples=["world.workshop.flow_metrics"],
    )
    async def flow_metrics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get handoff flow metrics between builders."""
        try:
            from agents.town.history import get_history_store

            store = get_history_store()
            return store.get_flow_metrics()
        except ImportError as e:
            return {"error": str(e)}

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle workshop-specific aspects."""
        match aspect:
            case "task":
                return await self.task(observer, **kwargs)
            case "stream":
                return await self.stream(observer, **kwargs)
            case "status":
                return await self.status(observer, **kwargs)
            case "builders":
                return await self.builders(observer, **kwargs)
            case "builder":
                return await self.builder(observer, **kwargs)
            case "whisper":
                return await self.whisper(observer, **kwargs)
            case "perturb":
                return await self.perturb(observer, **kwargs)
            case "reset":
                return await self.reset(observer, **kwargs)
            case "artifacts":
                return await self.artifacts(observer, **kwargs)
            case "history":
                return await self.history(observer, **kwargs)
            case "task_detail":
                return await self.task_detail(observer, **kwargs)
            case "task_events":
                return await self.task_events(observer, **kwargs)
            case "metrics":
                return await self.metrics(observer, **kwargs)
            case "builder_metrics":
                return await self.builder_metrics(observer, **kwargs)
            case "flow_metrics":
                return await self.flow_metrics(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# Factory functions
_workshop_node: WorkshopNode | None = None


def get_workshop_node() -> WorkshopNode:
    """Get the global WorkshopNode singleton."""
    global _workshop_node
    if _workshop_node is None:
        _workshop_node = WorkshopNode()
    return _workshop_node


def create_workshop_node() -> WorkshopNode:
    """Create a WorkshopNode."""
    return WorkshopNode()


__all__ = [
    "WORKSHOP_AFFORDANCES",
    "WorkshopNode",
    "get_workshop_node",
    "create_workshop_node",
]
