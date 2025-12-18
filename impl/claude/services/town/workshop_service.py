"""
Workshop Service: Builder coordination for Town Crown Jewel.

Migrated from agents/town/workshop.py to services/town/ per AD-009 pattern.

The workshop is the coordination layer where builders collaborate on tasks.
Unlike TownEnvironment (spatial mesh), the workshop is task-centric:
- Tasks are assigned and decomposed into subtasks
- Builders are routed based on task keywords or phase
- Work progresses through phases: EXPLORING → DESIGNING → PROTOTYPING → REFINING → INTEGRATING
- Artifacts are produced and events emitted for observability

Key Insight (from Morton):
    The workshop is not a place but a coordination protocol.
    Builders don't inhabit space—they inhabit tasks.

AGENTESE Paths:
- world.town.workshop.manifest - Show workshop status
- world.town.workshop.assign - Assign a task
- world.town.workshop.advance - Advance workshop
- world.town.workshop.complete - Complete current task

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator

from agents.town.workshop import (
    # Constants
    ARCHETYPE_TO_PHASE,
    BUILDER_DIALOGUE_TEMPLATES,
    KEYWORD_ROUTING,
    PHASE_TO_ARCHETYPE,
    # Data classes
    WorkshopArtifact,
    WorkshopDialogueContext,
    # Classes
    WorkshopEnvironment,
    WorkshopEvent,
    # Enums
    WorkshopEventType,
    WorkshopFlux,
    WorkshopMetrics,
    WorkshopPhase,
    WorkshopPlan,
    WorkshopState,
    WorkshopTask,
    # Functions
    create_workshop,
    create_workshop_with_builders,
    route_task,
    suggest_phases,
)

if TYPE_CHECKING:
    from agents.town.builders.base import Builder
    from agents.town.dialogue_engine import CitizenDialogueEngine
    from agents.town.event_bus import EventBus
    from protocols.nphase.session import NPhaseSession


# =============================================================================
# Service View Types
# =============================================================================


@dataclass(frozen=True)
class WorkshopView:
    """View of workshop status for API/CLI rendering."""

    phase: str
    is_idle: bool
    is_complete: bool
    active_task: dict[str, Any] | None
    active_builder: str | None
    builders: list[str]
    artifacts_count: int
    events_count: int
    plan: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "is_idle": self.is_idle,
            "is_complete": self.is_complete,
            "active_task": self.active_task,
            "active_builder": self.active_builder,
            "builders": self.builders,
            "artifacts_count": self.artifacts_count,
            "events_count": self.events_count,
            "plan": self.plan,
        }

    def to_text(self) -> str:
        lines = [
            f"Workshop [{self.phase}]",
            "=" * 40,
            f"Status: {'idle' if self.is_idle else 'complete' if self.is_complete else 'active'}",
        ]

        if self.active_task:
            lines.append(f"Task: {self.active_task.get('description', 'Unknown')}")
            lines.append(f"Priority: {self.active_task.get('priority', 1)}")

        if self.active_builder:
            lines.append(f"Active Builder: {self.active_builder}")

        lines.append(f"Builders: {', '.join(self.builders)}")
        lines.append(f"Artifacts: {self.artifacts_count}")
        lines.append(f"Events: {self.events_count}")

        return "\n".join(lines)


@dataclass(frozen=True)
class WorkshopTaskView:
    """View of a workshop task."""

    id: str
    description: str
    priority: int
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class WorkshopPlanView:
    """View of a workshop plan."""

    task: WorkshopTaskView
    assignments: dict[str, list[str]]
    estimated_phases: list[str]
    lead_builder: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task.to_dict(),
            "assignments": self.assignments,
            "estimated_phases": self.estimated_phases,
            "lead_builder": self.lead_builder,
        }

    def to_text(self) -> str:
        lines = [
            "Workshop Plan",
            "=" * 40,
            f"Task: {self.task.description}",
            f"Lead: {self.lead_builder}",
            f"Phases: {' → '.join(self.estimated_phases)}",
            "",
            "Assignments:",
        ]
        for archetype, subtasks in self.assignments.items():
            for subtask in subtasks:
                lines.append(f"  {archetype}: {subtask}")
        return "\n".join(lines)


@dataclass(frozen=True)
class WorkshopEventView:
    """View of a workshop event."""

    type: str
    timestamp: str
    builder: str | None
    phase: str
    message: str
    artifact: Any
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "builder": self.builder,
            "phase": self.phase,
            "message": self.message,
            "artifact": self.artifact,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class WorkshopFluxView:
    """View of flux execution status."""

    is_running: bool
    phase: str
    active_builder: str | None
    step_count: int
    phase_step_count: int
    task_description: str | None
    metrics: dict[str, Any]
    nphase: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_running": self.is_running,
            "phase": self.phase,
            "active_builder": self.active_builder,
            "step_count": self.step_count,
            "phase_step_count": self.phase_step_count,
            "task_description": self.task_description,
            "metrics": self.metrics,
            "nphase": self.nphase,
        }

    def to_text(self) -> str:
        lines = [
            f"Workshop Flux [{'running' if self.is_running else 'stopped'}]",
            "=" * 40,
            f"Phase: {self.phase}",
        ]
        if self.active_builder:
            lines.append(f"Builder: {self.active_builder}")
        if self.task_description:
            lines.append(f"Task: {self.task_description}")
        lines.append(f"Steps: {self.step_count} (phase: {self.phase_step_count})")
        return "\n".join(lines)


# =============================================================================
# Workshop Service
# =============================================================================


class WorkshopService:
    """
    Service layer for Workshop operations.

    Wraps WorkshopEnvironment and WorkshopFlux with a service-friendly API.
    Follows the Metaphysical Fullstack pattern (AD-009).

    Example:
        service = WorkshopService()

        # Assign a task
        plan = await service.assign_task("Design a new feature", priority=2)

        # Get status
        status = await service.manifest()

        # Run with flux for streaming
        async for event in service.run_task("Research the problem"):
            print(event.message)
    """

    def __init__(
        self,
        workshop: WorkshopEnvironment | None = None,
        dialogue_engine: "CitizenDialogueEngine | None" = None,
    ) -> None:
        """
        Initialize workshop service.

        Args:
            workshop: Optional pre-configured workshop. Creates default if None.
            dialogue_engine: Optional dialogue engine for builder speech.
        """
        self._workshop = workshop or create_workshop()
        self._dialogue_engine = dialogue_engine
        self._flux: WorkshopFlux | None = None

    @property
    def workshop(self) -> WorkshopEnvironment:
        """Underlying workshop environment."""
        return self._workshop

    @property
    def is_active(self) -> bool:
        """Check if workshop has an active task."""
        return not self._workshop.state.is_idle and not self._workshop.state.is_complete

    # =========================================================================
    # Core Operations
    # =========================================================================

    async def manifest(self, lod: int = 1) -> WorkshopView:
        """
        Get workshop status.

        AGENTESE: world.town.workshop.manifest

        Args:
            lod: Level of detail (0=minimal, 1=standard, 2=detailed)

        Returns:
            WorkshopView with current status
        """
        state = self._workshop.state
        self._workshop.manifest(lod=lod)

        return WorkshopView(
            phase=state.phase.name,
            is_idle=state.is_idle,
            is_complete=state.is_complete,
            active_task=state.active_task.to_dict() if state.active_task else None,
            active_builder=state.active_builder.archetype if state.active_builder else None,
            builders=[b.archetype for b in state.builders],
            artifacts_count=len(state.artifacts),
            events_count=len(state.events),
            plan=state.plan.to_dict() if state.plan else None,
        )

    async def assign_task(
        self,
        task: str | WorkshopTask,
        priority: int = 1,
    ) -> WorkshopPlanView:
        """
        Assign a task to the workshop.

        AGENTESE: world.town.workshop.assign

        Args:
            task: Task description or WorkshopTask object
            priority: Task priority (1=low, 2=medium, 3=high)

        Returns:
            WorkshopPlanView with the created plan

        Raises:
            ValueError: If a task is already in progress
        """
        plan = await self._workshop.assign_task(task, priority)

        return WorkshopPlanView(
            task=WorkshopTaskView(
                id=plan.task.id,
                description=plan.task.description,
                priority=plan.task.priority,
                created_at=plan.task.created_at.isoformat(),
            ),
            assignments=plan.assignments,
            estimated_phases=[p.name for p in plan.estimated_phases],
            lead_builder=plan.lead_builder,
        )

    async def advance(self) -> WorkshopEventView:
        """
        Advance the workshop by one step.

        AGENTESE: world.town.workshop.advance

        Returns:
            WorkshopEventView describing what happened

        Raises:
            ValueError: If no task is active or task is complete
        """
        event = await self._workshop.advance()
        return self._event_to_view(event)

    async def complete(self, summary: str = "") -> WorkshopEventView:
        """
        Mark the current task as complete.

        AGENTESE: world.town.workshop.complete

        Args:
            summary: Optional summary of completed work

        Returns:
            WorkshopEventView for task completion

        Raises:
            ValueError: If no active task
        """
        event = await self._workshop.complete(summary)
        return self._event_to_view(event)

    async def handoff(
        self,
        from_archetype: str,
        to_archetype: str,
        artifact: Any = None,
        message: str = "",
    ) -> WorkshopEventView:
        """
        Explicit handoff between builders.

        Args:
            from_archetype: Builder handing off
            to_archetype: Builder receiving
            artifact: Optional artifact to pass
            message: Optional message

        Returns:
            WorkshopEventView describing the handoff
        """
        event = await self._workshop.handoff(from_archetype, to_archetype, artifact, message)
        return self._event_to_view(event)

    def reset(self) -> None:
        """Reset workshop to idle state."""
        self._workshop.reset()
        if self._flux:
            self._flux.reset()

    # =========================================================================
    # Flux Operations (Streaming)
    # =========================================================================

    def create_flux(
        self,
        nphase_session: "NPhaseSession | None" = None,
        auto_advance: bool = True,
        max_steps_per_phase: int = 5,
        seed: int | None = None,
    ) -> WorkshopFlux:
        """
        Create a WorkshopFlux for streaming execution.

        Args:
            nphase_session: Optional N-Phase session for tracking
            auto_advance: Auto-advance phases (default True)
            max_steps_per_phase: Max steps before auto-advance
            seed: Random seed for reproducibility

        Returns:
            Configured WorkshopFlux
        """
        self._flux = WorkshopFlux(
            workshop=self._workshop,
            dialogue_engine=self._dialogue_engine,
            seed=seed,
            auto_advance=auto_advance,
            max_steps_per_phase=max_steps_per_phase,
            nphase_session=nphase_session,
        )
        return self._flux

    async def run_task(
        self,
        task: str | WorkshopTask,
        priority: int = 1,
        nphase_session: "NPhaseSession | None" = None,
    ) -> AsyncIterator[WorkshopEventView]:
        """
        Run a task to completion with streaming events.

        Convenience method that creates flux, starts task, and yields events.

        Args:
            task: Task description or WorkshopTask
            priority: Task priority
            nphase_session: Optional N-Phase session

        Yields:
            WorkshopEventView for each event
        """
        flux = self.create_flux(nphase_session=nphase_session)
        await flux.start(task, priority)

        async for event in flux.run():
            yield self._event_to_view(event)

    def get_flux_status(self) -> WorkshopFluxView | None:
        """Get current flux status if active."""
        if self._flux is None:
            return None

        status = self._flux.get_status()
        return WorkshopFluxView(
            is_running=status["is_running"],
            phase=status["phase"],
            active_builder=status["active_builder"],
            step_count=status["step_count"],
            phase_step_count=status["phase_step_count"],
            task_description=status["task"],
            metrics=status["metrics"],
            nphase=status.get("nphase"),
        )

    def get_metrics(self) -> WorkshopMetrics | None:
        """Get flux execution metrics."""
        if self._flux is None:
            return None
        return self._flux.get_metrics()

    # =========================================================================
    # Builder Access
    # =========================================================================

    def get_builder(self, archetype: str) -> "Builder | None":
        """Get a builder by archetype name."""
        return self._workshop.get_builder(archetype)

    def list_builders(self) -> list[str]:
        """List all builder archetypes."""
        return [b.archetype for b in self._workshop.builders]

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _event_to_view(self, event: WorkshopEvent) -> WorkshopEventView:
        """Convert WorkshopEvent to WorkshopEventView."""
        return WorkshopEventView(
            type=event.type.name,
            timestamp=event.timestamp.isoformat(),
            builder=event.builder,
            phase=event.phase.name,
            message=event.message,
            artifact=event.artifact,
            metadata=dict(event.metadata),
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_workshop_service(
    builders: tuple["Builder", ...] | None = None,
    event_bus: "EventBus[WorkshopEvent] | None" = None,
    dialogue_engine: "CitizenDialogueEngine | None" = None,
) -> WorkshopService:
    """
    Create a configured WorkshopService.

    Args:
        builders: Optional custom builders
        event_bus: Optional event bus for streaming
        dialogue_engine: Optional dialogue engine

    Returns:
        Configured WorkshopService
    """
    if builders:
        workshop = create_workshop_with_builders(builders, event_bus)
    else:
        workshop = create_workshop(event_bus)

    return WorkshopService(workshop=workshop, dialogue_engine=dialogue_engine)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Service
    "WorkshopService",
    "create_workshop_service",
    # Views
    "WorkshopView",
    "WorkshopTaskView",
    "WorkshopPlanView",
    "WorkshopEventView",
    "WorkshopFluxView",
    # Re-exports from agents/town/workshop
    "WorkshopPhase",
    "WorkshopEventType",
    "WorkshopEvent",
    "WorkshopTask",
    "WorkshopArtifact",
    "WorkshopPlan",
    "WorkshopState",
    "WorkshopMetrics",
    "WorkshopDialogueContext",
    "WorkshopEnvironment",
    "WorkshopFlux",
    "KEYWORD_ROUTING",
    "PHASE_TO_ARCHETYPE",
    "ARCHETYPE_TO_PHASE",
    "BUILDER_DIALOGUE_TEMPLATES",
    "route_task",
    "suggest_phases",
    "create_workshop",
    "create_workshop_with_builders",
]
