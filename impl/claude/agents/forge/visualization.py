"""
Coalition Forge Visualization: Making coalition dynamics visible.

From the Coalition Forge plan:
> *"Not just task completion—visible process."*
> "Kids on a playground" energy: watch them figure it out together.
> Coalition dynamics are the product, not just the task output.

This module provides:
1. CoalitionFormationView - who joins, why (eigenvector compatibility)
2. DialogueStream - SSE-based dialogue viewer for agent conversations
3. HandoffAnimation - visual transitions between agents

All widgets extend KgentsWidget[S] with multi-target projection.

AGENTESE Integration:
- world.coalition[id].subscribe - Real-time coalition updates
- world.coalition[id].dialogue.witness - Stream dialogue history
- world.coalition[id].manifest - Coalition state snapshot

Synergies:
- agents/town/coalition.py - Coalition detection via k-clique percolation
- agents/town/workshop.py - WorkshopFlux for streaming execution
- agents/i/reactive/projection/laws.py - Functor law compliance

OTEL Instrumentation:
- Formation events traced via SpanEmitter
- Dialogue messages span-tagged for debugging
- Handoff animations measured for latency
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from agents.town.coalition import Coalition as TownCoalition
    from agents.town.coalition import CoalitionManager
    from agents.town.workshop import WorkshopEvent, WorkshopFlux

# OTEL instrumentation - optional, gracefully degrade if not available
try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode

    _tracer = trace.get_tracer("kgents.forge.visualization")
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    _tracer = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# OTEL Instrumentation Helpers
# =============================================================================


def _trace_span(name: str, **attributes: Any) -> Any:
    """
    Context manager for OTEL tracing with graceful degradation.

    Usage:
        with _trace_span("formation.builder_joined", builder="Scout") as span:
            # do work
            span.set_attribute("result", "success")
    """
    if _OTEL_AVAILABLE and _tracer is not None:
        return _tracer.start_as_current_span(
            name,
            kind=SpanKind.INTERNAL,
            attributes={k: str(v) for k, v in attributes.items()},
        )
    else:
        # Null context manager
        from contextlib import nullcontext

        return nullcontext()


def _record_span_event(span: Any, event_name: str, **attributes: Any) -> None:
    """Record an event on a span if OTEL is available."""
    if _OTEL_AVAILABLE and span is not None and hasattr(span, "add_event"):
        span.add_event(
            event_name, attributes={k: str(v) for k, v in attributes.items()}
        )


def _set_span_error(span: Any, error: Exception) -> None:
    """Mark a span as errored if OTEL is available."""
    if _OTEL_AVAILABLE and span is not None and hasattr(span, "set_status"):
        span.set_status(Status(StatusCode.ERROR, str(error)))
        span.record_exception(error)


# =============================================================================
# Error Handling
# =============================================================================


class ForgeVisualizationError(Exception):
    """Base exception for forge visualization errors."""

    pass


class FormationStateError(ForgeVisualizationError):
    """Error in formation state transition."""

    pass


class SubscriptionError(ForgeVisualizationError):
    """Error in SSE subscription."""

    pass


def _safe_update(signal: Signal[Any], updater: Callable[[Any], Any]) -> bool:
    """
    Safely update a signal with error handling.

    Returns True if update succeeded, False otherwise.
    """
    try:
        signal.update(updater)
        return True
    except Exception as e:
        logger.error(f"Signal update failed: {e}")
        return False


# =============================================================================
# Formation Event Types
# =============================================================================


class FormationEventType(Enum):
    """Types of events during coalition formation."""

    FORMATION_STARTED = auto()  # Task submitted, formation beginning
    BUILDER_CONSIDERED = auto()  # A builder is being evaluated
    BUILDER_JOINED = auto()  # Builder joined the coalition
    BUILDER_REJECTED = auto()  # Builder didn't match (eigenvector)
    COMPATIBILITY_COMPUTED = auto()  # Eigenvector compatibility calculated
    FORMATION_COMPLETE = auto()  # Coalition fully formed
    TASK_STARTED = auto()  # Task execution beginning
    HANDOFF = auto()  # Control passed between builders
    ARTIFACT_PRODUCED = auto()  # Builder produced output
    TASK_COMPLETE = auto()  # Task finished


@dataclass(frozen=True)
class EigenvectorCompatibility:
    """
    Compatibility score between builders based on eigenvectors.

    The 7D eigenvector space captures builder personality:
    warmth, curiosity, trust, creativity, patience, resilience, ambition
    """

    builder_a: str
    builder_b: str

    # Individual dimension compatibility (0.0 - 1.0)
    warmth: float = 0.5
    curiosity: float = 0.5
    trust: float = 0.5
    creativity: float = 0.5
    patience: float = 0.5
    resilience: float = 0.5
    ambition: float = 0.5

    # Overall compatibility score
    overall: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON projection."""
        return {
            "builder_a": self.builder_a,
            "builder_b": self.builder_b,
            "dimensions": {
                "warmth": self.warmth,
                "curiosity": self.curiosity,
                "trust": self.trust,
                "creativity": self.creativity,
                "patience": self.patience,
                "resilience": self.resilience,
                "ambition": self.ambition,
            },
            "overall": self.overall,
        }


@dataclass(frozen=True)
class FormationEvent:
    """An event during coalition formation."""

    type: FormationEventType
    timestamp: datetime = field(default_factory=datetime.now)
    builder: str | None = None
    message: str = ""
    compatibility: EigenvectorCompatibility | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON projection."""
        return {
            "type": self.type.name,
            "timestamp": self.timestamp.isoformat(),
            "builder": self.builder,
            "message": self.message,
            "compatibility": self.compatibility.to_dict()
            if self.compatibility
            else None,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BuilderEntry:
    """A builder in the coalition formation view."""

    archetype: str
    name: str
    role: str  # e.g., "Research", "Analysis", "Documentation"
    joined: bool = False
    is_lead: bool = False
    compatibility_score: float = 0.0

    # Eigenvector summary (for display)
    eigenvector_summary: str = ""  # e.g., "High creativity, moderate patience"

    def to_dict(self) -> dict[str, Any]:
        return {
            "archetype": self.archetype,
            "name": self.name,
            "role": self.role,
            "joined": self.joined,
            "is_lead": self.is_lead,
            "compatibility_score": self.compatibility_score,
            "eigenvector_summary": self.eigenvector_summary,
        }


@dataclass(frozen=True)
class ForgeFormationState:
    """
    State for coalition formation visualization.

    Captures the entire formation process for reactive rendering.
    """

    # Task info
    task_id: str = ""
    task_description: str = ""
    task_type: str = ""  # research_report, code_review, etc.

    # Formation progress
    phase: str = "idle"  # idle, forming, formed, executing, complete
    progress_percent: float = 0.0

    # Builders
    builders: tuple[BuilderEntry, ...] = ()
    lead_builder: str | None = None

    # Formation events (for replay)
    events: tuple[FormationEvent, ...] = ()

    # Compatibility matrix
    compatibility_matrix: dict[str, dict[str, float]] = field(default_factory=dict)

    # Timing
    started_at: datetime | None = None
    estimated_completion: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "coalition_formation",
            "task_id": self.task_id,
            "task_description": self.task_description,
            "task_type": self.task_type,
            "phase": self.phase,
            "progress_percent": self.progress_percent,
            "builders": [b.to_dict() for b in self.builders],
            "lead_builder": self.lead_builder,
            "events": [e.to_dict() for e in self.events],
            "compatibility_matrix": self.compatibility_matrix,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "estimated_completion": self.estimated_completion.isoformat()
            if self.estimated_completion
            else None,
        }


# =============================================================================
# CoalitionFormationView Widget
# =============================================================================


class CoalitionFormationView(KgentsWidget[ForgeFormationState]):
    """
    Widget showing coalition formation with eigenvector compatibility.

    The crown jewel visualization: watch agents evaluate each other
    and form a team based on eigenvector compatibility.

    Features:
    - Builder grid with join animations
    - Eigenvector compatibility bars
    - Formation event timeline
    - Real-time progress updates via SSE

    AGENTESE Integration:
        world.coalition[id].manifest -> ForgeFormationState
        world.coalition[id].subscribe -> AsyncIterator[FormationEvent]

    Example:
        view = CoalitionFormationView()
        view.start_formation("Research competitors", "research_report")

        # Subscribe to updates
        async for event in view.subscribe():
            print(event.message)

        # Render
        print(view.to_cli())
    """

    def __init__(
        self,
        initial_state: ForgeFormationState | None = None,
        on_event: Callable[[FormationEvent], None] | None = None,
    ) -> None:
        """
        Initialize formation view.

        Args:
            initial_state: Optional initial state
            on_event: Callback for formation events
        """
        self._signal: Signal[ForgeFormationState] = Signal.of(
            initial_state or ForgeFormationState()
        )
        self._on_event = on_event
        self._event_queue: asyncio.Queue[FormationEvent] = asyncio.Queue()
        self._subscriptions: list[Callable[[], None]] = []

    @property
    def state(self) -> Signal[ForgeFormationState]:
        """The reactive state signal."""
        return self._signal

    def project(self, target: RenderTarget) -> Any:
        """Project to rendering target."""
        state = self._signal.value
        match target:
            case RenderTarget.CLI:
                return project_formation_to_ascii(state)
            case RenderTarget.JSON:
                return state.to_dict()
            case RenderTarget.TUI:
                # TUI: Return ASCII for now, can be enhanced
                return project_formation_to_ascii(state)
            case RenderTarget.MARIMO:
                return state.to_dict()
            case _:
                return state.to_dict()

    def widget_type(self) -> str:
        """Return widget type for projection hints."""
        return "coalition_formation"

    def ui_hint(self) -> str | None:
        """Return UI hint for projection."""
        return "stream"  # Formation is a streaming experience

    # --- Formation Control ---

    def start_formation(
        self,
        task_description: str,
        task_type: str,
        task_id: str | None = None,
    ) -> None:
        """
        Start coalition formation for a task.

        Args:
            task_description: What the task is
            task_type: Type of task (research_report, code_review, etc.)
            task_id: Optional task ID

        Raises:
            FormationStateError: If formation is already in progress
        """
        from uuid import uuid4

        # Validate state transition
        current_state = self._signal.value
        if current_state.phase not in ("idle", "complete"):
            raise FormationStateError(
                f"Cannot start formation: already in phase '{current_state.phase}'"
            )

        with _trace_span(
            "forge.formation.start",
            task_type=task_type,
            task_description=task_description[:50],
        ) as span:
            task_id = task_id or str(uuid4())[:8]
            now = datetime.now()

            # Create initial state
            new_state = ForgeFormationState(
                task_id=task_id,
                task_description=task_description,
                task_type=task_type,
                phase="forming",
                progress_percent=0.0,
                started_at=now,
                events=(
                    FormationEvent(
                        type=FormationEventType.FORMATION_STARTED,
                        timestamp=now,
                        message=f"Starting coalition formation for: {task_description}",
                        metadata={"task_type": task_type},
                    ),
                ),
            )

            self._signal.set(new_state)
            self._emit_event(new_state.events[-1])

            _record_span_event(span, "formation_started", task_id=task_id)

    def add_builder(
        self,
        archetype: str,
        name: str,
        role: str,
        is_lead: bool = False,
        compatibility_score: float = 0.8,
        eigenvector_summary: str = "",
    ) -> None:
        """
        Add a builder to the forming coalition.

        Args:
            archetype: Builder archetype (Scout, Sage, Spark, Steady, Sync)
            name: Display name for the builder
            role: Role in the coalition (Research, Analysis, etc.)
            is_lead: Whether this builder leads the coalition
            compatibility_score: Eigenvector compatibility (0.0-1.0)
            eigenvector_summary: Human-readable eigenvector summary

        Raises:
            FormationStateError: If not in forming phase
        """
        # Validate state
        current_state = self._signal.value
        if current_state.phase != "forming":
            raise FormationStateError(
                f"Cannot add builder: not in forming phase (phase='{current_state.phase}')"
            )

        # Validate compatibility score
        compatibility_score = max(0.0, min(1.0, compatibility_score))

        with _trace_span(
            "forge.formation.add_builder",
            archetype=archetype,
            role=role,
            is_lead=is_lead,
        ) as span:
            entry = BuilderEntry(
                archetype=archetype,
                name=name,
                role=role,
                joined=True,
                is_lead=is_lead,
                compatibility_score=compatibility_score,
                eigenvector_summary=eigenvector_summary,
            )

            def update_state(s: ForgeFormationState) -> ForgeFormationState:
                # Check for duplicate archetypes
                existing_archetypes = {b.archetype for b in s.builders}
                if archetype in existing_archetypes:
                    logger.warning(
                        f"Builder {archetype} already in coalition, skipping"
                    )
                    return s

                new_builders = s.builders + (entry,)
                new_event = FormationEvent(
                    type=FormationEventType.BUILDER_JOINED,
                    builder=archetype,
                    message=f"{name} ({archetype}) joined as {role}",
                    metadata={"compatibility_score": compatibility_score},
                )
                new_events = s.events + (new_event,)

                # Calculate progress
                target_builders = 3  # Typical coalition size
                progress = min(100.0, (len(new_builders) / target_builders) * 100)

                return ForgeFormationState(
                    task_id=s.task_id,
                    task_description=s.task_description,
                    task_type=s.task_type,
                    phase=s.phase,
                    progress_percent=progress,
                    builders=new_builders,
                    lead_builder=archetype if is_lead else s.lead_builder,
                    events=new_events,
                    compatibility_matrix=s.compatibility_matrix,
                    started_at=s.started_at,
                    estimated_completion=s.estimated_completion,
                )

            if _safe_update(self._signal, update_state):
                self._emit_event(self._signal.value.events[-1])
                _record_span_event(span, "builder_joined", archetype=archetype)

    def complete_formation(self) -> None:
        """Mark formation as complete."""

        def update_state(s: ForgeFormationState) -> ForgeFormationState:
            new_event = FormationEvent(
                type=FormationEventType.FORMATION_COMPLETE,
                message=f"Coalition formed with {len(s.builders)} builders",
                metadata={"builder_count": len(s.builders)},
            )
            return ForgeFormationState(
                task_id=s.task_id,
                task_description=s.task_description,
                task_type=s.task_type,
                phase="formed",
                progress_percent=100.0,
                builders=s.builders,
                lead_builder=s.lead_builder,
                events=s.events + (new_event,),
                compatibility_matrix=s.compatibility_matrix,
                started_at=s.started_at,
                estimated_completion=s.estimated_completion,
            )

        self._signal.update(update_state)
        self._emit_event(self._signal.value.events[-1])

    def add_compatibility(
        self,
        builder_a: str,
        builder_b: str,
        compatibility: EigenvectorCompatibility,
    ) -> None:
        """Add compatibility score between two builders."""

        def update_state(s: ForgeFormationState) -> ForgeFormationState:
            matrix = dict(s.compatibility_matrix)
            if builder_a not in matrix:
                matrix[builder_a] = {}
            matrix[builder_a][builder_b] = compatibility.overall

            new_event = FormationEvent(
                type=FormationEventType.COMPATIBILITY_COMPUTED,
                message=f"Compatibility {builder_a} <-> {builder_b}: {compatibility.overall:.0%}",
                compatibility=compatibility,
            )

            return ForgeFormationState(
                task_id=s.task_id,
                task_description=s.task_description,
                task_type=s.task_type,
                phase=s.phase,
                progress_percent=s.progress_percent,
                builders=s.builders,
                lead_builder=s.lead_builder,
                events=s.events + (new_event,),
                compatibility_matrix=matrix,
                started_at=s.started_at,
                estimated_completion=s.estimated_completion,
            )

        self._signal.update(update_state)
        self._emit_event(self._signal.value.events[-1])

    # --- Subscription ---

    async def subscribe(self) -> AsyncIterator[FormationEvent]:
        """
        Subscribe to formation events.

        Yields events as they occur, for SSE streaming.

        Example:
            async for event in view.subscribe():
                yield event.to_dict()  # SSE data
        """
        while True:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                # Yield keepalive
                yield FormationEvent(
                    type=FormationEventType.FORMATION_STARTED,
                    message="keepalive",
                    metadata={"keepalive": True},
                )

    def _emit_event(self, event: FormationEvent) -> None:
        """Emit an event to subscribers."""
        if self._on_event:
            self._on_event(event)

        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Drop if queue full

    # --- WorkshopFlux Integration ---

    def wire_to_flux(self, flux: "WorkshopFlux") -> Callable[[], None]:
        """
        Wire this view to a WorkshopFlux for real-time updates.

        Returns:
            Unsubscribe function
        """
        from agents.town.workshop import WorkshopEventType

        async def on_workshop_event(event: "WorkshopEvent") -> None:
            # Map workshop events to formation events
            try:
                match event.type:
                    case WorkshopEventType.TASK_ASSIGNED:
                        # Reset to idle first if needed
                        if self._signal.value.phase not in ("idle", "complete"):
                            self._signal.set(ForgeFormationState())
                        self.start_formation(
                            event.message,
                            event.metadata.get("task_type", "general"),
                            event.metadata.get("task_id"),
                        )
                    case WorkshopEventType.PHASE_STARTED:
                        if event.builder and self._signal.value.phase == "forming":
                            try:
                                self.add_builder(
                                    event.builder,
                                    event.builder,  # Name = archetype for now
                                    event.phase.name,
                                )
                            except FormationStateError:
                                pass  # Gracefully handle state issues
                    case WorkshopEventType.HANDOFF:
                        # Record handoff event
                        self._emit_event(
                            FormationEvent(
                                type=FormationEventType.HANDOFF,
                                builder=event.builder,
                                message=event.message,
                                metadata=event.metadata,
                            )
                        )
                    case WorkshopEventType.TASK_COMPLETED:
                        self._emit_event(
                            FormationEvent(
                                type=FormationEventType.TASK_COMPLETE,
                                message=event.message,
                            )
                        )
            except Exception as e:
                logger.error(f"Error processing workshop event: {e}")

        # Note: In production, this would subscribe to the flux event bus
        # For now, return a no-op unsubscribe
        return lambda: None

    def sync_from_coalition_manager(
        self,
        manager: "CoalitionManager",
        coalition_id: str,
    ) -> bool:
        """
        Sync visualization state from a town CoalitionManager.

        This bridges the k-clique percolation detection in agents/town/coalition.py
        with our visualization layer.

        Args:
            manager: The CoalitionManager from agents/town/coalition.py
            coalition_id: ID of the coalition to visualize

        Returns:
            True if sync succeeded, False if coalition not found

        Example:
            from agents.town.coalition import CoalitionManager
            manager = CoalitionManager(citizens, similarity_threshold=0.8)
            manager.detect()
            view.sync_from_coalition_manager(manager, coalition_id)
        """
        from agents.town.coalition import Coalition as TownCoalition

        coalition = manager.coalitions.get(coalition_id)
        if coalition is None:
            logger.warning(f"Coalition {coalition_id} not found in manager")
            return False

        with _trace_span(
            "forge.formation.sync_from_manager",
            coalition_id=coalition_id,
            member_count=coalition.size,
        ) as span:
            # Reset to idle and start fresh
            self._signal.set(ForgeFormationState())
            self.start_formation(
                coalition.purpose or f"Coalition {coalition.name}",
                "eigenvector_aligned",
                coalition.id,
            )

            # Add members as builders
            for member_id in coalition.members:
                self.add_builder(
                    archetype=member_id,  # Use member ID as archetype
                    name=member_id,
                    role="Member",
                    compatibility_score=coalition.strength,
                    eigenvector_summary=f"Aligned via k={manager._k} clique",
                )

            # Mark as complete
            self.complete_formation()

            _record_span_event(
                span,
                "sync_complete",
                member_count=len(coalition.members),
            )

        return True


# =============================================================================
# DialogueStream Widget
# =============================================================================


class DialogueSpeaker(Enum):
    """Who is speaking in the dialogue."""

    SCOUT = "Scout"
    SAGE = "Sage"
    SPARK = "Spark"
    STEADY = "Steady"
    SYNC = "Sync"
    SYSTEM = "System"
    USER = "User"


@dataclass(frozen=True)
class DialogueMessage:
    """A single message in the dialogue stream."""

    speaker: DialogueSpeaker | str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_handoff: bool = False
    is_artifact: bool = False
    artifact_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "speaker": self.speaker.value
            if isinstance(self.speaker, DialogueSpeaker)
            else self.speaker,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "is_handoff": self.is_handoff,
            "is_artifact": self.is_artifact,
            "artifact_type": self.artifact_type,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DialogueState:
    """State for the dialogue stream widget."""

    messages: tuple[DialogueMessage, ...] = ()
    is_streaming: bool = False
    active_speaker: DialogueSpeaker | str | None = None

    # Display options
    show_timestamps: bool = True
    show_handoffs: bool = True
    max_messages: int = 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "dialogue_stream",
            "messages": [m.to_dict() for m in self.messages],
            "is_streaming": self.is_streaming,
            "active_speaker": self.active_speaker.value
            if isinstance(self.active_speaker, DialogueSpeaker)
            else self.active_speaker,
            "message_count": len(self.messages),
        }


class DialogueStream(KgentsWidget[DialogueState]):
    """
    SSE-based dialogue viewer for agent conversations.

    Shows the conversation between builders as they work on a task.
    Messages stream in real-time via SSE.

    Features:
    - Real-time message streaming
    - Speaker identification with colors
    - Handoff indicators
    - Artifact markers
    - Message history with replay

    AGENTESE Integration:
        world.coalition[id].dialogue.witness -> AsyncIterator[DialogueMessage]

    Example:
        stream = DialogueStream()

        async for msg in coalition_dialogue():
            stream.add_message(msg)
            yield stream.to_json()  # SSE update
    """

    def __init__(
        self,
        initial_state: DialogueState | None = None,
    ) -> None:
        """Initialize dialogue stream."""
        self._signal: Signal[DialogueState] = Signal.of(
            initial_state or DialogueState()
        )
        self._message_queue: asyncio.Queue[DialogueMessage] = asyncio.Queue()

    @property
    def state(self) -> Signal[DialogueState]:
        """The reactive state signal."""
        return self._signal

    def project(self, target: RenderTarget) -> Any:
        """Project to rendering target."""
        state = self._signal.value
        match target:
            case RenderTarget.CLI:
                return project_dialogue_to_ascii(state)
            case RenderTarget.JSON:
                return state.to_dict()
            case RenderTarget.TUI:
                return project_dialogue_to_ascii(state)
            case RenderTarget.MARIMO:
                return state.to_dict()
            case _:
                return state.to_dict()

    def widget_type(self) -> str:
        return "dialogue_stream"

    def ui_hint(self) -> str | None:
        return "stream"

    # --- Message Control ---

    def add_message(
        self,
        speaker: DialogueSpeaker | str,
        content: str,
        is_handoff: bool = False,
        is_artifact: bool = False,
        artifact_type: str | None = None,
        **metadata: Any,
    ) -> None:
        """Add a message to the stream."""
        msg = DialogueMessage(
            speaker=speaker,
            content=content,
            is_handoff=is_handoff,
            is_artifact=is_artifact,
            artifact_type=artifact_type,
            metadata=metadata,
        )

        def update_state(s: DialogueState) -> DialogueState:
            messages = s.messages + (msg,)
            # Trim to max messages
            if len(messages) > s.max_messages:
                messages = messages[-s.max_messages :]

            return DialogueState(
                messages=messages,
                is_streaming=True,
                active_speaker=speaker,
                show_timestamps=s.show_timestamps,
                show_handoffs=s.show_handoffs,
                max_messages=s.max_messages,
            )

        self._signal.update(update_state)

        try:
            self._message_queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass

    def add_handoff(
        self, from_speaker: str, to_speaker: str, message: str = ""
    ) -> None:
        """Add a handoff transition message."""
        content = message or f"Handing off to {to_speaker}"
        self.add_message(
            speaker=from_speaker,
            content=content,
            is_handoff=True,
            to_speaker=to_speaker,
        )

    def add_artifact(
        self,
        speaker: DialogueSpeaker | str,
        artifact_type: str,
        description: str,
    ) -> None:
        """Add an artifact production message."""
        self.add_message(
            speaker=speaker,
            content=f"Produced: {description}",
            is_artifact=True,
            artifact_type=artifact_type,
        )

    def start_streaming(self) -> None:
        """Mark stream as active."""
        self._signal.update(
            lambda s: DialogueState(
                messages=s.messages,
                is_streaming=True,
                active_speaker=s.active_speaker,
                show_timestamps=s.show_timestamps,
                show_handoffs=s.show_handoffs,
                max_messages=s.max_messages,
            )
        )

    def stop_streaming(self) -> None:
        """Mark stream as inactive."""
        self._signal.update(
            lambda s: DialogueState(
                messages=s.messages,
                is_streaming=False,
                active_speaker=None,
                show_timestamps=s.show_timestamps,
                show_handoffs=s.show_handoffs,
                max_messages=s.max_messages,
            )
        )

    def clear(self) -> None:
        """Clear all messages."""
        self._signal.set(DialogueState())

    # --- Subscription ---

    async def subscribe(self) -> AsyncIterator[DialogueMessage]:
        """
        Subscribe to new messages.

        Yields messages as they arrive, for SSE streaming.
        """
        while True:
            try:
                msg = await asyncio.wait_for(self._message_queue.get(), timeout=30.0)
                yield msg
            except asyncio.TimeoutError:
                # Keepalive
                yield DialogueMessage(
                    speaker=DialogueSpeaker.SYSTEM,
                    content="keepalive",
                    metadata={"keepalive": True},
                )


# =============================================================================
# HandoffAnimation Widget
# =============================================================================


@dataclass(frozen=True)
class HandoffState:
    """State for handoff animation."""

    from_builder: str | None = None
    to_builder: str | None = None
    artifact: str | None = None  # What's being passed

    # Animation state
    is_active: bool = False
    progress: float = 0.0  # 0.0 to 1.0

    # History
    handoffs: tuple[
        tuple[str, str, str, datetime], ...
    ] = ()  # (from, to, artifact, when)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "handoff_animation",
            "from_builder": self.from_builder,
            "to_builder": self.to_builder,
            "artifact": self.artifact,
            "is_active": self.is_active,
            "progress": self.progress,
            "handoff_count": len(self.handoffs),
            "handoffs": [
                {"from": f, "to": t, "artifact": a, "when": w.isoformat()}
                for f, t, a, w in self.handoffs
            ],
        }


class HandoffAnimation(KgentsWidget[HandoffState]):
    """
    Visual transitions between agents during task execution.

    Shows the flow of control and artifacts between builders
    with animated transitions.

    Features:
    - Animated arrow between builders
    - Artifact visualization
    - Handoff history trail
    - Progress indicator

    ASCII Representation:
        Scout ─────➤ Sage
              [findings]

    Example:
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", "research findings")
        # ... animation plays
        anim.complete_handoff()
    """

    def __init__(
        self,
        initial_state: HandoffState | None = None,
    ) -> None:
        """Initialize handoff animation."""
        self._signal: Signal[HandoffState] = Signal.of(initial_state or HandoffState())

    @property
    def state(self) -> Signal[HandoffState]:
        """The reactive state signal."""
        return self._signal

    def project(self, target: RenderTarget) -> Any:
        """Project to rendering target."""
        state = self._signal.value
        match target:
            case RenderTarget.CLI:
                return project_handoff_to_ascii(state)
            case RenderTarget.JSON:
                return state.to_dict()
            case RenderTarget.TUI:
                return project_handoff_to_ascii(state)
            case RenderTarget.MARIMO:
                return state.to_dict()
            case _:
                return state.to_dict()

    def widget_type(self) -> str:
        return "handoff_animation"

    def ui_hint(self) -> str | None:
        return "graph"  # Handoffs are graph-like

    # --- Handoff Control ---

    def start_handoff(
        self,
        from_builder: str,
        to_builder: str,
        artifact: str | None = None,
    ) -> None:
        """Start a handoff animation."""
        self._signal.update(
            lambda s: HandoffState(
                from_builder=from_builder,
                to_builder=to_builder,
                artifact=artifact,
                is_active=True,
                progress=0.0,
                handoffs=s.handoffs,
            )
        )

    def update_progress(self, progress: float) -> None:
        """Update animation progress (0.0 to 1.0)."""
        self._signal.update(
            lambda s: HandoffState(
                from_builder=s.from_builder,
                to_builder=s.to_builder,
                artifact=s.artifact,
                is_active=s.is_active,
                progress=min(1.0, max(0.0, progress)),
                handoffs=s.handoffs,
            )
        )

    def complete_handoff(self) -> None:
        """Complete the current handoff animation."""

        def update_state(s: HandoffState) -> HandoffState:
            new_handoffs = s.handoffs
            if s.from_builder and s.to_builder:
                new_handoffs = s.handoffs + (
                    (s.from_builder, s.to_builder, s.artifact or "", datetime.now()),
                )

            return HandoffState(
                from_builder=None,
                to_builder=None,
                artifact=None,
                is_active=False,
                progress=0.0,
                handoffs=new_handoffs,
            )

        self._signal.update(update_state)

    def reset(self) -> None:
        """Reset animation state."""
        self._signal.set(HandoffState())


# =============================================================================
# ASCII Projection Functions
# =============================================================================


def project_formation_to_ascii(
    state: ForgeFormationState,
    width: int = 60,
) -> str:
    """
    Project formation state to ASCII art.

    Layout:
        ┌─────────────────────────────────────────────────────────┐
        │ COALITION FORMING                          [████░░] 67% │
        │ Task: Research competitors                              │
        ├─────────────────────────────────────────────────────────┤
        │                                                         │
        │  ✓ Scout (Research)     compat: ████████░░ 85%         │
        │  ✓ Sage (Analysis)      compat: ███████░░░ 72%         │
        │  ○ Scribe (Document)    compat: ─────────              │
        │                                                         │
        ├─────────────────────────────────────────────────────────┤
        │ Events:                                                 │
        │  → Scout joined as Research lead                       │
        │  → Compatibility Scout <-> Sage: 72%                   │
        └─────────────────────────────────────────────────────────┘
    """
    lines: list[str] = []

    # Top border
    border = "┌" + "─" * (width - 2) + "┐"
    lines.append(border)

    # Header with progress
    progress_bar_width = 6
    filled = int(state.progress_percent / 100 * progress_bar_width)
    progress_bar = "█" * filled + "░" * (progress_bar_width - filled)

    phase_display = state.phase.upper()
    header = f"│ COALITION {phase_display}"
    header_suffix = f"[{progress_bar}] {state.progress_percent:.0f}%"
    padding = width - len(header) - len(header_suffix) - 1
    lines.append(header + " " * padding + header_suffix + "│")

    # Task description
    task_line = f"│ Task: {state.task_description[: width - 10]}"
    lines.append(task_line + " " * (width - len(task_line) - 1) + "│")

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Builders section
    lines.append("│" + " " * (width - 2) + "│")

    for builder in state.builders:
        status = "✓" if builder.joined else "○"
        lead_marker = " (lead)" if builder.is_lead else ""

        # Compatibility bar
        if builder.compatibility_score > 0:
            compat_filled = int(builder.compatibility_score * 10)
            compat_bar = "█" * compat_filled + "░" * (10 - compat_filled)
            compat_display = f"{compat_bar} {builder.compatibility_score:.0%}"
        else:
            compat_display = "─" * 10

        builder_line = f"│  {status} {builder.archetype} ({builder.role}){lead_marker}"
        compat_section = f"compat: {compat_display}"
        padding = width - len(builder_line) - len(compat_section) - 2
        lines.append(builder_line + " " * max(1, padding) + compat_section + " │")

    # Padding if few builders
    for _ in range(max(0, 3 - len(state.builders))):
        lines.append("│" + " " * (width - 2) + "│")

    # Events section
    lines.append("├" + "─" * (width - 2) + "┤")
    lines.append("│ Events:" + " " * (width - 10) + "│")

    # Show last 3 events
    recent_events = state.events[-3:] if state.events else []
    for event in recent_events:
        event_line = f"│  → {event.message[: width - 8]}"
        lines.append(event_line + " " * (width - len(event_line) - 1) + "│")

    # Padding if few events
    for _ in range(max(0, 2 - len(recent_events))):
        lines.append("│" + " " * (width - 2) + "│")

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def project_dialogue_to_ascii(
    state: DialogueState,
    width: int = 60,
    max_lines: int = 15,
) -> str:
    """
    Project dialogue stream to ASCII.

    Layout:
        ┌─────────────────────────────────────────────────────────┐
        │ DIALOGUE STREAM                              [LIVE ●]   │
        ├─────────────────────────────────────────────────────────┤
        │                                                         │
        │ [Scout] Let me explore what we're working with...      │
        │                                                         │
        │ [Scout → Sage] Handing off research findings           │
        │                                                         │
        │ [Sage] Analyzing the structure here...                 │
        │                                                         │
        │ [Sage] *artifact* Design document produced             │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
    """
    lines: list[str] = []

    # Top border
    border = "┌" + "─" * (width - 2) + "┐"
    lines.append(border)

    # Header
    status = "[LIVE ●]" if state.is_streaming else "[PAUSED]"
    header = "│ DIALOGUE STREAM"
    padding = width - len(header) - len(status) - 1
    lines.append(header + " " * padding + status + "│")

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Messages
    lines.append("│" + " " * (width - 2) + "│")

    # Get recent messages
    messages = state.messages[-(max_lines - 6) :] if state.messages else []

    for msg in messages:
        speaker = (
            msg.speaker.value
            if isinstance(msg.speaker, DialogueSpeaker)
            else str(msg.speaker)
        )

        if msg.is_handoff:
            to_speaker = msg.metadata.get("to_speaker", "?")
            line = f"│ [{speaker} → {to_speaker}] {msg.content[: width - 20]}"
        elif msg.is_artifact:
            line = f"│ [{speaker}] *artifact* {msg.content[: width - 20]}"
        else:
            line = f"│ [{speaker}] {msg.content[: width - 15]}"

        # Truncate and pad
        if len(line) > width - 1:
            line = line[: width - 2] + "…"
        lines.append(line + " " * (width - len(line) - 1) + "│")
        lines.append("│" + " " * (width - 2) + "│")

    # Padding if few messages
    while len(lines) < max_lines - 1:
        lines.append("│" + " " * (width - 2) + "│")

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def project_handoff_to_ascii(
    state: HandoffState,
    width: int = 40,
) -> str:
    """
    Project handoff animation to ASCII.

    Layout (active):
        Scout ════════➤ Sage
              [findings]

    Layout (inactive):
        Handoffs: Scout→Sage→Spark (3)
    """
    if state.is_active and state.from_builder and state.to_builder:
        # Active handoff animation
        arrow_width = width - len(state.from_builder) - len(state.to_builder) - 4

        # Animate arrow based on progress
        filled = int(state.progress * arrow_width)
        arrow = "═" * filled + "─" * (arrow_width - filled) + "➤"

        line1 = f"{state.from_builder} {arrow} {state.to_builder}"

        if state.artifact:
            artifact_display = f"[{state.artifact}]"
            padding = (len(line1) - len(artifact_display)) // 2
            line2 = " " * padding + artifact_display
            return f"{line1}\n{line2}"

        return line1

    elif state.handoffs:
        # Show handoff history
        path_parts = []
        seen = set()
        for from_b, to_b, _, _ in state.handoffs:
            if from_b not in seen:
                path_parts.append(from_b)
                seen.add(from_b)
            if to_b not in seen:
                path_parts.append(to_b)
                seen.add(to_b)

        path = "→".join(path_parts[:4])
        if len(path_parts) > 4:
            path += "→..."

        return f"Handoffs: {path} ({len(state.handoffs)})"

    return "No handoffs yet"


# =============================================================================
# AGENTESE Path Handlers
# =============================================================================


async def handle_coalition_subscribe(
    coalition_id: str,
    view: CoalitionFormationView,
) -> AsyncIterator[dict[str, Any]]:
    """
    AGENTESE handler for world.coalition[id].subscribe

    Streams coalition formation events as SSE.

    Usage:
        async for event_dict in handle_coalition_subscribe(id, view):
            yield sse_format(event_dict)
    """
    async for event in view.subscribe():
        yield event.to_dict()


async def handle_dialogue_witness(
    coalition_id: str,
    stream: DialogueStream,
) -> AsyncIterator[dict[str, Any]]:
    """
    AGENTESE handler for world.coalition[id].dialogue.witness

    Streams dialogue messages as SSE.

    Usage:
        async for msg_dict in handle_dialogue_witness(id, stream):
            yield sse_format(msg_dict)
    """
    async for msg in stream.subscribe():
        yield msg.to_dict()


# =============================================================================
# Factory Functions
# =============================================================================


def create_formation_view(
    task_description: str = "",
    task_type: str = "general",
) -> CoalitionFormationView:
    """Create a CoalitionFormationView, optionally starting formation."""
    view = CoalitionFormationView()
    if task_description:
        view.start_formation(task_description, task_type)
    return view


def create_dialogue_stream() -> DialogueStream:
    """Create a DialogueStream widget."""
    return DialogueStream()


def create_handoff_animation() -> HandoffAnimation:
    """Create a HandoffAnimation widget."""
    return HandoffAnimation()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Event types
    "FormationEventType",
    "FormationEvent",
    "EigenvectorCompatibility",
    "BuilderEntry",
    # State types
    "ForgeFormationState",
    "DialogueSpeaker",
    "DialogueMessage",
    "DialogueState",
    "HandoffState",
    # Widgets
    "CoalitionFormationView",
    "DialogueStream",
    "HandoffAnimation",
    # ASCII projections
    "project_formation_to_ascii",
    "project_dialogue_to_ascii",
    "project_handoff_to_ascii",
    # AGENTESE handlers
    "handle_coalition_subscribe",
    "handle_dialogue_witness",
    # Factories
    "create_formation_view",
    "create_dialogue_stream",
    "create_handoff_animation",
]
