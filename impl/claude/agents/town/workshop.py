"""
WorkshopEnvironment: Collaborative Task Execution for Builders.

The workshop is the coordination layer where builders collaborate on tasks.
Unlike TownEnvironment (spatial mesh), the workshop is task-centric:
- Tasks are assigned and decomposed into subtasks
- Builders are routed based on task keywords or phase
- Work progresses through phases: EXPLORING → DESIGNING → PROTOTYPING → REFINING → INTEGRATING
- Artifacts are produced and events emitted for observability

Key Insight (from Morton):
    The workshop is not a place but a coordination protocol.
    Builders don't inhabit space—they inhabit tasks.

Chunk 7: WorkshopFlux - streaming execution layer.
    From Bataille: The flux is not just time—it is *expenditure*.
    Each phase accumulates artifacts that must be integrated.

See: plans/agent-town/builders-workshop-chunk6.md
See: plans/agent-town/builders-workshop-chunk7.md
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncIterator
from uuid import uuid4

from agents.town.builders.base import Builder
from agents.town.builders.polynomial import BuilderInput, BuilderOutput, BuilderPhase
from agents.town.event_bus import EventBus

if TYPE_CHECKING:
    from agents.town.dialogue_engine import CitizenDialogueEngine


# =============================================================================
# Workshop Phase (Task Lifecycle)
# =============================================================================


class WorkshopPhase(Enum):
    """
    Phases in the workshop task lifecycle.

    Maps to builder specialties:
    - EXPLORING → Scout
    - DESIGNING → Sage
    - PROTOTYPING → Spark
    - REFINING → Steady
    - INTEGRATING → Sync
    """

    IDLE = auto()
    EXPLORING = auto()
    DESIGNING = auto()
    PROTOTYPING = auto()
    REFINING = auto()
    INTEGRATING = auto()
    COMPLETE = auto()


# Mapping from WorkshopPhase to builder archetype
PHASE_TO_ARCHETYPE: dict[WorkshopPhase, str] = {
    WorkshopPhase.EXPLORING: "Scout",
    WorkshopPhase.DESIGNING: "Sage",
    WorkshopPhase.PROTOTYPING: "Spark",
    WorkshopPhase.REFINING: "Steady",
    WorkshopPhase.INTEGRATING: "Sync",
}

# Mapping from builder archetype to WorkshopPhase
ARCHETYPE_TO_PHASE: dict[str, WorkshopPhase] = {
    v: k for k, v in PHASE_TO_ARCHETYPE.items()
}


# =============================================================================
# Workshop Event Types
# =============================================================================


class WorkshopEventType(Enum):
    """Types of workshop events for observability."""

    TASK_ASSIGNED = auto()
    PLAN_CREATED = auto()
    PHASE_STARTED = auto()
    PHASE_COMPLETED = auto()
    HANDOFF = auto()
    ARTIFACT_PRODUCED = auto()
    USER_QUERY = auto()
    USER_RESPONSE = auto()
    TASK_COMPLETED = auto()
    ERROR = auto()


@dataclass
class WorkshopEvent:
    """
    An observable workshop event.

    Events are emitted during task execution for streaming,
    logging, and UI updates.
    """

    type: WorkshopEventType
    timestamp: datetime = field(default_factory=datetime.now)
    builder: str | None = None  # Which builder triggered
    phase: WorkshopPhase = WorkshopPhase.IDLE
    message: str = ""
    artifact: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.type.name,
            "timestamp": self.timestamp.isoformat(),
            "builder": self.builder,
            "phase": self.phase.name,
            "message": self.message,
            "artifact": self.artifact,
            "metadata": dict(self.metadata),
        }


# =============================================================================
# Workshop Task
# =============================================================================


@dataclass(frozen=True)
class WorkshopTask:
    """
    A unit of work for the workshop.

    Tasks are immutable—once created, they don't change.
    The workshop tracks progress via WorkshopState.
    """

    id: str
    description: str
    priority: int = 1  # 1=low, 2=medium, 3=high
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        description: str,
        priority: int = 1,
        **context: Any,
    ) -> WorkshopTask:
        """Factory for creating tasks with auto-generated ID."""
        return cls(
            id=str(uuid4())[:8],
            description=description,
            priority=priority,
            context=context,
            created_at=datetime.now(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "context": dict(self.context),
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Workshop Artifact
# =============================================================================


@dataclass
class WorkshopArtifact:
    """
    Output produced during workshop execution.

    Artifacts are typed outputs from builder work:
    - Research findings (Scout)
    - Design documents (Sage)
    - Prototypes (Spark)
    - Polished implementations (Steady)
    - Integration reports (Sync)
    """

    id: str
    task_id: str
    builder: str  # Archetype name
    phase: WorkshopPhase
    content: Any
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        task_id: str,
        builder: str,
        phase: WorkshopPhase,
        content: Any,
        **metadata: Any,
    ) -> WorkshopArtifact:
        """Factory for creating artifacts."""
        return cls(
            id=str(uuid4())[:8],
            task_id=task_id,
            builder=builder,
            phase=phase,
            content=content,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "builder": self.builder,
            "phase": self.phase.name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


# =============================================================================
# Workshop Plan
# =============================================================================


@dataclass
class WorkshopPlan:
    """
    How a task is distributed across builders.

    Plans decompose tasks into subtasks assigned to builder archetypes.
    The lead_builder coordinates execution.
    """

    task: WorkshopTask
    assignments: dict[str, list[str]]  # archetype -> subtasks
    estimated_phases: list[WorkshopPhase]
    lead_builder: str  # Archetype name (who coordinates)

    def get_subtasks_for(self, archetype: str) -> list[str]:
        """Get subtasks assigned to a builder archetype."""
        return self.assignments.get(archetype, [])

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task": self.task.to_dict(),
            "assignments": dict(self.assignments),
            "estimated_phases": [p.name for p in self.estimated_phases],
            "lead_builder": self.lead_builder,
        }


# =============================================================================
# Workshop State
# =============================================================================


@dataclass
class WorkshopState:
    """
    Current state of the workshop.

    Captures the workshop's phase, builders, active task, and accumulated artifacts.
    """

    phase: WorkshopPhase
    builders: tuple[Builder, ...]
    active_task: WorkshopTask | None = None
    plan: WorkshopPlan | None = None
    artifacts: list[WorkshopArtifact] = field(default_factory=list)
    events: list[WorkshopEvent] = field(default_factory=list)

    @property
    def is_idle(self) -> bool:
        """Check if workshop is idle (no active task)."""
        return self.phase == WorkshopPhase.IDLE

    @property
    def is_complete(self) -> bool:
        """Check if current task is complete."""
        return self.phase == WorkshopPhase.COMPLETE

    @property
    def active_builder(self) -> Builder | None:
        """
        Get the builder currently working (based on phase).

        Returns None if IDLE or COMPLETE.
        """
        archetype = PHASE_TO_ARCHETYPE.get(self.phase)
        if archetype is None:
            return None
        return next(
            (b for b in self.builders if b.archetype == archetype),
            None,
        )

    def get_builder(self, archetype: str) -> Builder | None:
        """Get a builder by archetype name."""
        return next(
            (b for b in self.builders if b.archetype == archetype),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "phase": self.phase.name,
            "builders": [b.archetype for b in self.builders],
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "plan": self.plan.to_dict() if self.plan else None,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "events_count": len(self.events),
        }


# =============================================================================
# Workshop Metrics (Chunk 7)
# =============================================================================


@dataclass
class WorkshopMetrics:
    """
    Metrics tracked during workshop execution.

    Provides observability into flux execution:
    - Steps and events for throughput
    - Tokens for cost tracking
    - Artifacts for productivity
    - Handoffs for flow analysis
    """

    total_steps: int = 0
    total_events: int = 0
    total_tokens: int = 0
    dialogue_tokens: int = 0
    artifacts_produced: int = 0
    phases_completed: int = 0
    handoffs: int = 0
    perturbations: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float:
        """Execution duration in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def events_per_second(self) -> float:
        """Event generation rate."""
        if self.duration_seconds == 0:
            return 0.0
        return self.total_events / self.duration_seconds

    @property
    def steps_per_phase(self) -> float:
        """Average steps per phase."""
        if self.phases_completed == 0:
            return 0.0
        return self.total_steps / self.phases_completed

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_steps": self.total_steps,
            "total_events": self.total_events,
            "total_tokens": self.total_tokens,
            "dialogue_tokens": self.dialogue_tokens,
            "artifacts_produced": self.artifacts_produced,
            "phases_completed": self.phases_completed,
            "handoffs": self.handoffs,
            "perturbations": self.perturbations,
            "duration_seconds": self.duration_seconds,
            "events_per_second": self.events_per_second,
            "steps_per_phase": self.steps_per_phase,
        }


# =============================================================================
# Workshop Dialogue Context (Chunk 7)
# =============================================================================


@dataclass
class WorkshopDialogueContext:
    """
    Context for builder dialogue generation.

    Provides the DialogueEngine with workshop-specific context
    for generating in-character builder speech.
    """

    task: WorkshopTask
    phase: WorkshopPhase
    builder: Builder
    artifacts_so_far: list[WorkshopArtifact]
    recent_events: list[str]
    step_count: int

    def to_prompt_context(self) -> str:
        """Render as prompt context for dialogue generation."""
        parts = [
            f"Task: {self.task.description}",
            f"Phase: {self.phase.name}",
            f"Builder: {self.builder.name} ({self.builder.archetype})",
        ]

        if self.artifacts_so_far:
            artifact_summaries = [
                f"- {a.builder}: {a.phase.name}"
                for a in self.artifacts_so_far[-3:]
            ]
            parts.append(f"Previous work:\n" + "\n".join(artifact_summaries))

        if self.recent_events:
            parts.append(f"Recent: {'; '.join(self.recent_events[-3:])}")

        return "\n".join(parts)


# =============================================================================
# Task Routing (MVP: Keyword-based)
# =============================================================================

KEYWORD_ROUTING: dict[str, str] = {
    # Scout keywords
    "research": "Scout",
    "find": "Scout",
    "explore": "Scout",
    "search": "Scout",
    "discover": "Scout",
    "investigate": "Scout",
    # Sage keywords
    "design": "Sage",
    "architect": "Sage",
    "plan": "Sage",
    "structure": "Sage",
    "model": "Sage",
    "schema": "Sage",
    # Spark keywords
    "prototype": "Spark",
    "experiment": "Spark",
    "try": "Spark",
    "spike": "Spark",
    "poc": "Spark",
    "demo": "Spark",
    # Steady keywords
    "test": "Steady",
    "polish": "Steady",
    "refine": "Steady",
    "fix": "Steady",
    "clean": "Steady",
    "harden": "Steady",
    # Sync keywords
    "integrate": "Sync",
    "coordinate": "Sync",
    "merge": "Sync",
    "deploy": "Sync",
    "ship": "Sync",
    "release": "Sync",
}


def route_task(task: WorkshopTask) -> str:
    """
    Determine which builder should lead based on task description.

    MVP: Keyword matching.
    Future: LLM-based semantic routing.
    """
    description_lower = task.description.lower()
    for keyword, archetype in KEYWORD_ROUTING.items():
        if keyword in description_lower:
            return archetype
    # Default: Scout explores first
    return "Scout"


def suggest_phases(lead: str) -> list[WorkshopPhase]:
    """
    Suggest phases based on lead builder.

    Returns a sequence of phases starting from the lead's specialty.
    """
    phase_order = [
        WorkshopPhase.EXPLORING,
        WorkshopPhase.DESIGNING,
        WorkshopPhase.PROTOTYPING,
        WorkshopPhase.REFINING,
        WorkshopPhase.INTEGRATING,
    ]

    # Find the lead's phase
    lead_phase = ARCHETYPE_TO_PHASE.get(lead, WorkshopPhase.EXPLORING)

    # Start from lead's phase
    try:
        start_idx = phase_order.index(lead_phase)
    except ValueError:
        start_idx = 0

    return phase_order[start_idx:]


# =============================================================================
# WorkshopEnvironment
# =============================================================================


class WorkshopEnvironment:
    """
    The collaborative workshop where builders work together.

    This is the coordination layer that:
    - Accepts tasks from users
    - Creates plans for how to execute tasks
    - Routes work to appropriate builders
    - Tracks progress and artifacts
    - Emits events for observability

    From Morton: The workshop is not a place but a coordination protocol.
    """

    def __init__(
        self,
        builders: tuple[Builder, ...] | None = None,
        event_bus: EventBus[WorkshopEvent] | None = None,
    ) -> None:
        """
        Initialize workshop with builders.

        Args:
            builders: Tuple of builders. If None, creates default set.
            event_bus: Optional event bus for streaming events.
        """
        self._builders = builders or self._create_default_builders()
        self._event_bus = event_bus
        self._state = WorkshopState(
            phase=WorkshopPhase.IDLE,
            builders=self._builders,
        )

    @staticmethod
    def _create_default_builders() -> tuple[Builder, ...]:
        """Create the default set of 5 builders."""
        from agents.town.builders import (
            create_sage,
            create_scout,
            create_spark,
            create_steady,
            create_sync,
        )

        return (
            create_scout("Scout"),
            create_sage("Sage"),
            create_spark("Spark"),
            create_steady("Steady"),
            create_sync("Sync"),
        )

    @property
    def state(self) -> WorkshopState:
        """Current workshop state."""
        return self._state

    @property
    def builders(self) -> tuple[Builder, ...]:
        """All builders in the workshop."""
        return self._builders

    def get_builder(self, archetype: str) -> Builder | None:
        """Get a builder by archetype name."""
        return self._state.get_builder(archetype)

    def set_event_bus(self, event_bus: EventBus[WorkshopEvent]) -> None:
        """Wire event bus for fan-out to subscribers."""
        self._event_bus = event_bus

    async def _emit_event(self, event: WorkshopEvent) -> None:
        """Emit an event (add to state and publish to bus)."""
        self._state.events.append(event)
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def assign_task(
        self,
        task: str | WorkshopTask,
        priority: int = 1,
    ) -> WorkshopPlan:
        """
        Assign a task to the workshop.

        Creates a plan and begins execution with the appropriate lead builder.

        Args:
            task: Task description string or WorkshopTask object.
            priority: Task priority (1=low, 2=medium, 3=high).

        Returns:
            The created WorkshopPlan.

        Raises:
            ValueError: If a task is already in progress.
        """
        if self._state.active_task is not None:
            raise ValueError("Task already in progress. Complete or cancel first.")

        # Create task if string
        if isinstance(task, str):
            task = WorkshopTask.create(task, priority=priority)

        # Route to lead builder
        lead = route_task(task)

        # Create plan
        phases = suggest_phases(lead)
        assignments: dict[str, list[str]] = {
            PHASE_TO_ARCHETYPE[phase]: [f"Work on {task.description}"]
            for phase in phases
        }

        plan = WorkshopPlan(
            task=task,
            assignments=assignments,
            estimated_phases=phases,
            lead_builder=lead,
        )

        # Update state
        self._state.active_task = task
        self._state.plan = plan
        self._state.phase = phases[0] if phases else WorkshopPhase.EXPLORING

        # Transition lead builder to their specialty
        lead_builder = self.get_builder(lead)
        if lead_builder is not None:
            lead_builder.start_task(task.description, priority=priority)

        # Emit events
        await self._emit_event(
            WorkshopEvent(
                type=WorkshopEventType.TASK_ASSIGNED,
                builder=lead,
                phase=self._state.phase,
                message=f"Task assigned: {task.description}",
                metadata={"task_id": task.id, "priority": priority},
            )
        )
        await self._emit_event(
            WorkshopEvent(
                type=WorkshopEventType.PLAN_CREATED,
                builder=lead,
                phase=self._state.phase,
                message=f"Plan created with lead: {lead}",
                metadata={"phases": [p.name for p in phases]},
            )
        )
        await self._emit_event(
            WorkshopEvent(
                type=WorkshopEventType.PHASE_STARTED,
                builder=lead,
                phase=self._state.phase,
                message=f"{lead} starting {self._state.phase.name}",
            )
        )

        return plan

    async def advance(self) -> WorkshopEvent:
        """
        Advance the workshop by one step.

        This triggers the current active builder to work,
        potentially producing artifacts or triggering handoffs.

        Returns:
            WorkshopEvent describing what happened.

        Raises:
            ValueError: If no task is active or task is complete.
        """
        if self._state.active_task is None:
            raise ValueError("No active task. Use assign_task() first.")

        if self._state.phase == WorkshopPhase.COMPLETE:
            raise ValueError("Task is complete. Use assign_task() for a new task.")

        if self._state.phase == WorkshopPhase.IDLE:
            raise ValueError("Workshop is idle. Use assign_task() first.")

        # Get active builder
        active = self._state.active_builder
        if active is None:
            # No builder for this phase—skip to next
            return await self._advance_phase()

        # Builder does work
        output = active.continue_work(f"Working on {self._state.active_task.description}")

        # Check if builder returned to IDLE (completed their part)
        if output.phase == BuilderPhase.IDLE:
            return await self._advance_phase(output.artifact)

        # Still working
        event = WorkshopEvent(
            type=WorkshopEventType.ARTIFACT_PRODUCED,
            builder=active.archetype,
            phase=self._state.phase,
            message=f"{active.name} working: {output.message}",
            artifact=output.artifact,
            metadata={"builder_phase": active.builder_phase.name},
        )
        await self._emit_event(event)
        return event

    async def _advance_phase(self, artifact: Any = None) -> WorkshopEvent:
        """
        Advance to the next phase.

        Creates artifact for current phase and transitions to next.
        """
        current_phase = self._state.phase
        current_builder = self._state.active_builder

        # Create artifact if provided
        if artifact is not None and self._state.active_task is not None:
            ws_artifact = WorkshopArtifact.create(
                task_id=self._state.active_task.id,
                builder=current_builder.archetype if current_builder else "Unknown",
                phase=current_phase,
                content=artifact,
            )
            self._state.artifacts.append(ws_artifact)

        # Emit phase completed
        await self._emit_event(
            WorkshopEvent(
                type=WorkshopEventType.PHASE_COMPLETED,
                builder=current_builder.archetype if current_builder else None,
                phase=current_phase,
                message=f"Phase {current_phase.name} completed",
                artifact=artifact,
            )
        )

        # Complete current builder's work
        if current_builder is not None:
            current_builder.complete_work(artifact=artifact)

        # Determine next phase
        plan = self._state.plan
        if plan is None:
            self._state.phase = WorkshopPhase.COMPLETE
        else:
            try:
                current_idx = plan.estimated_phases.index(current_phase)
                if current_idx + 1 < len(plan.estimated_phases):
                    next_phase = plan.estimated_phases[current_idx + 1]
                    self._state.phase = next_phase

                    # Handoff to next builder
                    next_builder = self._state.active_builder
                    if next_builder is not None:
                        next_builder.start_task(
                            self._state.active_task.description
                            if self._state.active_task
                            else "task",
                        )

                    # Emit handoff event
                    event = WorkshopEvent(
                        type=WorkshopEventType.HANDOFF,
                        builder=next_builder.archetype if next_builder else None,
                        phase=next_phase,
                        message=f"Handoff to {next_builder.archetype if next_builder else 'next'} for {next_phase.name}",
                        artifact=artifact,
                        metadata={
                            "from_builder": current_builder.archetype
                            if current_builder
                            else None,
                            "to_builder": next_builder.archetype
                            if next_builder
                            else None,
                        },
                    )
                    await self._emit_event(event)

                    # Emit phase started
                    await self._emit_event(
                        WorkshopEvent(
                            type=WorkshopEventType.PHASE_STARTED,
                            builder=next_builder.archetype if next_builder else None,
                            phase=next_phase,
                            message=f"{next_builder.archetype if next_builder else 'Builder'} starting {next_phase.name}",
                        )
                    )

                    return event
                else:
                    self._state.phase = WorkshopPhase.COMPLETE
            except ValueError:
                self._state.phase = WorkshopPhase.COMPLETE

        # Task complete
        return await self._complete_task()

    async def _complete_task(self) -> WorkshopEvent:
        """Mark task as complete and emit final event."""
        event = WorkshopEvent(
            type=WorkshopEventType.TASK_COMPLETED,
            phase=WorkshopPhase.COMPLETE,
            message=f"Task completed: {self._state.active_task.description if self._state.active_task else 'Unknown'}",
            metadata={
                "task_id": self._state.active_task.id
                if self._state.active_task
                else None,
                "artifacts_count": len(self._state.artifacts),
            },
        )
        await self._emit_event(event)
        return event

    async def handoff(
        self,
        from_archetype: str,
        to_archetype: str,
        artifact: Any = None,
        message: str = "",
    ) -> WorkshopEvent:
        """
        Explicit handoff between builders.

        Args:
            from_archetype: Archetype of builder handing off.
            to_archetype: Archetype of builder receiving.
            artifact: Optional artifact to pass.
            message: Optional message about the handoff.

        Returns:
            WorkshopEvent describing the handoff.

        Raises:
            ValueError: If builders not found or no active task.
        """
        if self._state.active_task is None:
            raise ValueError("No active task.")

        from_builder = self.get_builder(from_archetype)
        to_builder = self.get_builder(to_archetype)

        if from_builder is None:
            raise ValueError(f"Builder not found: {from_archetype}")
        if to_builder is None:
            raise ValueError(f"Builder not found: {to_archetype}")

        # Complete from_builder's work
        from_builder.handoff_to(to_builder, artifact=artifact, message=message)

        # Start to_builder's work
        to_builder.start_task(self._state.active_task.description)

        # Update phase to match to_builder's specialty
        to_phase = ARCHETYPE_TO_PHASE.get(to_archetype, self._state.phase)
        self._state.phase = to_phase

        # Create artifact
        if artifact is not None:
            ws_artifact = WorkshopArtifact.create(
                task_id=self._state.active_task.id,
                builder=from_archetype,
                phase=self._state.phase,
                content=artifact,
            )
            self._state.artifacts.append(ws_artifact)

        event = WorkshopEvent(
            type=WorkshopEventType.HANDOFF,
            builder=to_archetype,
            phase=to_phase,
            message=message or f"Handoff from {from_archetype} to {to_archetype}",
            artifact=artifact,
            metadata={
                "from_builder": from_archetype,
                "to_builder": to_archetype,
            },
        )
        await self._emit_event(event)
        return event

    async def complete(self, summary: str = "") -> WorkshopEvent:
        """
        Mark the current task as complete.

        Args:
            summary: Optional summary of the completed work.

        Returns:
            WorkshopEvent for task completion.

        Raises:
            ValueError: If no active task.
        """
        if self._state.active_task is None:
            raise ValueError("No active task to complete.")

        # Complete active builder's work
        active = self._state.active_builder
        if active is not None:
            active.complete_work(summary=summary)

        self._state.phase = WorkshopPhase.COMPLETE
        return await self._complete_task()

    def reset(self) -> None:
        """
        Reset workshop to idle state.

        Clears active task, plan, artifacts, and events.
        Builders are returned to IDLE state.
        """
        for builder in self._builders:
            builder.builder_rest()

        self._state = WorkshopState(
            phase=WorkshopPhase.IDLE,
            builders=self._builders,
        )

    def observe(self) -> AsyncIterator[WorkshopEvent]:
        """
        Stream workshop events.

        Returns an async iterator over WorkshopEvents.
        Requires an event bus to be set.

        Raises:
            RuntimeError: If no event bus is configured.
        """
        if self._event_bus is None:
            raise RuntimeError("No event bus configured. Use set_event_bus() first.")

        subscription = self._event_bus.subscribe()
        return subscription.__aiter__()

    def manifest(self, lod: int = 0) -> dict[str, Any]:
        """
        Manifest workshop state at Level of Detail.

        Args:
            lod: Level of detail (0=minimal, 1=standard, 2=detailed).

        Returns:
            Dictionary representation of workshop state.
        """
        result: dict[str, Any] = {
            "phase": self._state.phase.name,
            "is_idle": self._state.is_idle,
            "is_complete": self._state.is_complete,
        }

        if lod >= 1:
            result["task"] = (
                self._state.active_task.to_dict()
                if self._state.active_task
                else None
            )
            result["active_builder"] = (
                self._state.active_builder.archetype
                if self._state.active_builder
                else None
            )
            result["builders"] = [b.archetype for b in self._builders]
            result["artifacts_count"] = len(self._state.artifacts)
            result["events_count"] = len(self._state.events)

        if lod >= 2:
            result["plan"] = self._state.plan.to_dict() if self._state.plan else None
            result["artifacts"] = [a.to_dict() for a in self._state.artifacts]
            result["builders_detail"] = [
                {
                    "archetype": b.archetype,
                    "name": b.name,
                    "builder_phase": b.builder_phase.name,
                    "is_in_specialty": b.is_in_specialty,
                }
                for b in self._builders
            ]

        return result


# =============================================================================
# Builder Dialogue Templates (Chunk 7)
# =============================================================================


BUILDER_DIALOGUE_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "Scout": {
        "start_work": [
            "Let me see what we're working with here...",
            "I'll start by exploring the landscape.",
            "Time to scout out the possibilities.",
        ],
        "continue": [
            "I found something interesting...",
            "There's more to discover here.",
            "Following this thread...",
        ],
        "handoff": [
            "I've mapped the territory. Over to you, {next_builder}.",
            "Here's what I found. {next_builder}, your turn.",
            "The path is clear—{next_builder}, take it from here.",
        ],
        "complete": [
            "Exploration complete. Here's what I discovered.",
            "I've charted the landscape. Ready for the next phase.",
        ],
    },
    "Sage": {
        "start_work": [
            "Have we considered the architecture here?",
            "Let me think through the structure...",
            "The design should account for...",
        ],
        "continue": [
            "This pattern could work...",
            "Building on the foundation...",
            "The structure takes shape...",
        ],
        "handoff": [
            "The blueprint is ready. {next_builder}, build on this.",
            "Design complete. {next_builder}, your turn to prototype.",
        ],
        "complete": [
            "The architecture is sound.",
            "Design phase complete. The blueprint awaits execution.",
        ],
    },
    "Spark": {
        "start_work": [
            "Let's try something!",
            "I have an idea—watch this!",
            "Time to experiment!",
        ],
        "continue": [
            "What if we did it this way?",
            "Ooh, that's interesting...",
            "Let's see what happens when...",
        ],
        "handoff": [
            "The prototype is alive! {next_builder}, polish it up?",
            "Here's a rough cut. {next_builder}, make it shine.",
        ],
        "complete": [
            "The prototype works! Mostly.",
            "Experiment successful—ready for refinement.",
        ],
    },
    "Steady": {
        "start_work": [
            "Let me review what we have...",
            "Time to clean this up properly.",
            "I'll make sure this is solid.",
        ],
        "continue": [
            "Fixed that edge case...",
            "Adding proper error handling...",
            "This needs more tests...",
        ],
        "handoff": [
            "It's production-ready now. {next_builder}, integrate it.",
            "Polished and tested. {next_builder}, take it home.",
        ],
        "complete": [
            "Quality checks pass. Ready for integration.",
            "Refinement complete. The code is solid.",
        ],
    },
    "Sync": {
        "start_work": [
            "Let me connect all the pieces...",
            "Time to bring it all together.",
            "Coordinating the final integration...",
        ],
        "continue": [
            "Merging the components...",
            "Resolving the interfaces...",
            "Almost there...",
        ],
        "handoff": [
            "Integration complete. Back to you, {next_builder}.",
        ],
        "complete": [
            "All systems connected. We're live!",
            "Integration successful. The task is complete.",
        ],
    },
}


# =============================================================================
# WorkshopFlux (Chunk 7)
# =============================================================================


class WorkshopFlux:
    """
    Workshop execution as async event stream.

    Lifts WorkshopEnvironment into a continuous flux of events.
    Similar to TownFlux but task-centric rather than time-centric.

    From Bataille: The flux is expenditure.
    Each phase accumulates artifacts that must be integrated.

    Example:
        workshop = create_workshop()
        flux = WorkshopFlux(workshop)

        # Start a task
        plan = await flux.start("Design a new feature")

        # Run to completion, yielding events
        async for event in flux.run():
            print(event.message)

        # Get metrics
        metrics = flux.get_metrics()
        print(f"Completed in {metrics.duration_seconds}s")
    """

    def __init__(
        self,
        workshop: WorkshopEnvironment,
        dialogue_engine: "CitizenDialogueEngine | None" = None,
        seed: int | None = None,
        auto_advance: bool = True,
        max_steps_per_phase: int = 5,
    ) -> None:
        """
        Initialize workshop flux.

        Args:
            workshop: The WorkshopEnvironment to execute.
            dialogue_engine: Optional LLM dialogue for builder speech.
            seed: Random seed for reproducibility.
            auto_advance: If True, automatically advance phases.
            max_steps_per_phase: Max work steps before auto-advancing.
        """
        self._workshop = workshop
        self._dialogue_engine = dialogue_engine
        self._rng = random.Random(seed)
        self._auto_advance = auto_advance
        self._max_steps_per_phase = max_steps_per_phase

        # Execution state
        self._is_running = False
        self._step_count = 0
        self._phase_step_count = 0
        self._recent_events: list[str] = []

        # Metrics
        self._metrics = WorkshopMetrics()

    @property
    def is_running(self) -> bool:
        """Check if flux is currently executing a task."""
        return self._is_running

    @property
    def current_phase(self) -> WorkshopPhase:
        """Current workshop phase."""
        return self._workshop.state.phase

    @property
    def active_builder(self) -> Builder | None:
        """Currently active builder."""
        return self._workshop.state.active_builder

    @property
    def workshop(self) -> WorkshopEnvironment:
        """The underlying workshop environment."""
        return self._workshop

    async def start(
        self,
        task: str | WorkshopTask,
        priority: int = 1,
    ) -> WorkshopPlan:
        """
        Start executing a task.

        Assigns task to workshop and prepares for streaming execution.

        Args:
            task: Task description or WorkshopTask object.
            priority: Task priority (1=low, 2=medium, 3=high).

        Returns:
            The created WorkshopPlan.

        Raises:
            RuntimeError: If already running.
        """
        if self._is_running:
            raise RuntimeError("Flux is already running. Call stop() or wait for completion.")

        # Reset metrics
        self._metrics = WorkshopMetrics(start_time=datetime.now())
        self._step_count = 0
        self._phase_step_count = 0
        self._recent_events.clear()

        # Assign task to workshop
        plan = await self._workshop.assign_task(task, priority=priority)

        self._is_running = True
        self._metrics.total_events += 3  # task_assigned, plan_created, phase_started

        # Generate dialogue for task start if engine available
        active = self.active_builder
        if active is not None:
            await self._generate_dialogue(active, "start_work")

        return plan

    async def step(self) -> AsyncIterator[WorkshopEvent]:
        """
        Execute one step and yield events.

        A step involves:
        1. Active builder doing work
        2. Possibly generating dialogue (if engine available)
        3. Checking if phase should advance
        4. Emitting events for observability
        """
        if not self._is_running:
            return

        active = self.active_builder
        if active is None:
            return

        self._step_count += 1
        self._phase_step_count += 1
        self._metrics.total_steps += 1

        # Generate dialogue for continuing work
        dialogue = await self._generate_dialogue(active, "continue")

        # Advance the workshop
        try:
            event = await self._workshop.advance()
        except ValueError:
            # Task complete or idle
            self._is_running = False
            return

        # Enrich event with dialogue
        if dialogue is not None:
            event.metadata["dialogue"] = dialogue
            event.metadata["dialogue_tokens"] = self._metrics.dialogue_tokens

        self._metrics.total_events += 1
        self._recent_events.append(event.message)

        # Track metrics by event type
        if event.type == WorkshopEventType.ARTIFACT_PRODUCED:
            self._metrics.artifacts_produced += 1
        elif event.type == WorkshopEventType.PHASE_COMPLETED:
            self._metrics.phases_completed += 1
            self._phase_step_count = 0
        elif event.type == WorkshopEventType.HANDOFF:
            self._metrics.handoffs += 1
            # Generate handoff dialogue
            next_builder = self.active_builder
            if next_builder is not None:
                await self._generate_dialogue(active, "handoff", next_builder=next_builder.archetype)
        elif event.type == WorkshopEventType.TASK_COMPLETED:
            self._is_running = False
            self._metrics.end_time = datetime.now()
            # Generate completion dialogue
            await self._generate_dialogue(active, "complete")

        yield event

        # Auto-advance if we've done enough steps in this phase
        if (
            self._auto_advance
            and self._phase_step_count >= self._max_steps_per_phase
            and self.current_phase not in (WorkshopPhase.IDLE, WorkshopPhase.COMPLETE)
        ):
            try:
                advance_event = await self._workshop._advance_phase()
                self._phase_step_count = 0
                yield advance_event
                # Check if the advance completed the task
                if advance_event.type == WorkshopEventType.TASK_COMPLETED:
                    self._is_running = False
                    self._metrics.end_time = datetime.now()
            except ValueError:
                pass

    async def run(self) -> AsyncIterator[WorkshopEvent]:
        """
        Run task to completion, yielding events.

        Continuously calls step() until task is complete.
        """
        if not self._is_running:
            return

        while self._is_running:
            async for event in self.step():
                yield event

    async def perturb(
        self,
        action: str,
        builder: str | None = None,
        artifact: Any = None,
    ) -> WorkshopEvent:
        """
        Inject a perturbation into the flux.

        Perturbation Principle: inject events, never bypass state.

        Actions:
        - "advance": Force phase advancement
        - "handoff": Explicit handoff to builder
        - "complete": Force task completion
        - "inject_artifact": Add artifact to current phase

        Args:
            action: The perturbation action to perform.
            builder: Target builder archetype (for "handoff").
            artifact: Artifact content (for "inject_artifact").

        Returns:
            WorkshopEvent describing what happened.

        Raises:
            ValueError: If action is invalid or required args missing.
        """
        self._metrics.perturbations += 1

        if action == "advance":
            event = await self._workshop._advance_phase(artifact)
            event.metadata["perturbation"] = True
            event.metadata["perturbation_source"] = "manual_advance"
            self._phase_step_count = 0
            return event

        elif action == "handoff":
            if builder is None:
                raise ValueError("builder archetype required for handoff action")
            current = self.active_builder
            if current is None:
                raise ValueError("No active builder to handoff from")
            event = await self._workshop.handoff(
                current.archetype,
                builder,
                artifact=artifact,
            )
            event.metadata["perturbation"] = True
            event.metadata["perturbation_source"] = "manual_handoff"
            return event

        elif action == "complete":
            event = await self._workshop.complete(summary=str(artifact) if artifact else "")
            self._is_running = False
            self._metrics.end_time = datetime.now()
            event.metadata["perturbation"] = True
            event.metadata["perturbation_source"] = "manual_complete"
            return event

        elif action == "inject_artifact":
            if self._workshop.state.active_task is None:
                raise ValueError("No active task to inject artifact into")
            ws_artifact = WorkshopArtifact.create(
                task_id=self._workshop.state.active_task.id,
                builder=self.active_builder.archetype if self.active_builder else "Unknown",
                phase=self.current_phase,
                content=artifact,
                injected=True,
            )
            self._workshop.state.artifacts.append(ws_artifact)
            self._metrics.artifacts_produced += 1
            event = WorkshopEvent(
                type=WorkshopEventType.ARTIFACT_PRODUCED,
                builder=self.active_builder.archetype if self.active_builder else None,
                phase=self.current_phase,
                message=f"Artifact injected via perturbation",
                artifact=artifact,
                metadata={
                    "perturbation": True,
                    "perturbation_source": "inject_artifact",
                },
            )
            await self._workshop._emit_event(event)
            return event

        else:
            raise ValueError(f"Unknown perturbation action: {action}")

    async def stop(self) -> WorkshopEvent | None:
        """
        Stop the flux execution.

        Returns completion event if stopped mid-task, None if already stopped.
        """
        if not self._is_running:
            return None

        self._is_running = False
        self._metrics.end_time = datetime.now()

        if self._workshop.state.active_task is not None:
            return await self._workshop.complete(summary="Stopped by flux.stop()")
        return None

    def get_status(self) -> dict[str, Any]:
        """Get current flux status including metrics."""
        return {
            "is_running": self._is_running,
            "phase": self.current_phase.name,
            "active_builder": self.active_builder.archetype if self.active_builder else None,
            "step_count": self._step_count,
            "phase_step_count": self._phase_step_count,
            "task": (
                self._workshop.state.active_task.description
                if self._workshop.state.active_task
                else None
            ),
            "metrics": self._metrics.to_dict(),
        }

    def get_metrics(self) -> WorkshopMetrics:
        """Get execution metrics."""
        return self._metrics

    async def _generate_dialogue(
        self,
        builder: Builder,
        action: str,
        next_builder: str | None = None,
    ) -> str | None:
        """
        Generate dialogue for builder action.

        Falls back to templates if no dialogue engine.
        """
        # Get template dialogue
        templates = BUILDER_DIALOGUE_TEMPLATES.get(builder.archetype, {})
        action_templates = templates.get(action, [])

        if not action_templates:
            return None

        template = self._rng.choice(action_templates)
        dialogue = template.format(
            next_builder=next_builder or "the next builder",
        )

        # If we have a dialogue engine, try LLM generation
        if self._dialogue_engine is not None and self._workshop.state.active_task is not None:
            try:
                # Use the dialogue engine for richer dialogue
                # Create a phantom listener (workshop itself)
                context = WorkshopDialogueContext(
                    task=self._workshop.state.active_task,
                    phase=self.current_phase,
                    builder=builder,
                    artifacts_so_far=list(self._workshop.state.artifacts),
                    recent_events=list(self._recent_events[-3:]),
                    step_count=self._step_count,
                )
                # For now, just use template - LLM integration can be added later
                # This avoids import cycle issues
                self._metrics.dialogue_tokens += 0
            except Exception:
                pass  # Graceful degradation

        return dialogue

    def reset(self) -> None:
        """Reset flux to initial state."""
        self._is_running = False
        self._step_count = 0
        self._phase_step_count = 0
        self._recent_events.clear()
        self._metrics = WorkshopMetrics()
        self._workshop.reset()


# =============================================================================
# Factory Functions
# =============================================================================


def create_workshop(
    event_bus: EventBus[WorkshopEvent] | None = None,
) -> WorkshopEnvironment:
    """Create a workshop with default builders."""
    return WorkshopEnvironment(event_bus=event_bus)


def create_workshop_with_builders(
    builders: tuple[Builder, ...],
    event_bus: EventBus[WorkshopEvent] | None = None,
) -> WorkshopEnvironment:
    """Create a workshop with specific builders."""
    return WorkshopEnvironment(builders=builders, event_bus=event_bus)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Enums
    "WorkshopPhase",
    "WorkshopEventType",
    # Data classes
    "WorkshopEvent",
    "WorkshopTask",
    "WorkshopArtifact",
    "WorkshopPlan",
    "WorkshopState",
    # Chunk 7: Metrics and context
    "WorkshopMetrics",
    "WorkshopDialogueContext",
    # Environment
    "WorkshopEnvironment",
    # Chunk 7: Flux
    "WorkshopFlux",
    "BUILDER_DIALOGUE_TEMPLATES",
    # Routing
    "KEYWORD_ROUTING",
    "PHASE_TO_ARCHETYPE",
    "ARCHETYPE_TO_PHASE",
    "route_task",
    "suggest_phases",
    # Factories
    "create_workshop",
    "create_workshop_with_builders",
]
