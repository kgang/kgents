"""
N-Phase Session Events.

Event types for N-Phase orchestration:
- PhaseTransitionEvent: Phase boundary crossed
- PhaseCheckpointEvent: Checkpoint created
- PhaseSignalDetectedEvent: Signal detected from output
- SessionCreatedEvent: New session started
- SessionEndedEvent: Session completed

Events integrate with agents/town/event_bus.py for fan-out.

See: plans/nphase-native-integration.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from protocols.nphase.detector import PhaseSignal
from protocols.nphase.operad import NPhase


class NPhaseEventType(Enum):
    """Types of N-Phase events."""

    SESSION_CREATED = auto()
    SESSION_ENDED = auto()
    PHASE_TRANSITION = auto()
    PHASE_CHECKPOINT = auto()
    SIGNAL_DETECTED = auto()
    HANDLE_ADDED = auto()
    ENTROPY_SPENT = auto()


@dataclass
class NPhaseEvent:
    """
    Base class for N-Phase events.

    All events carry:
    - Session ID for routing
    - Timestamp for ordering
    - Event type for dispatch
    - Metadata for extension
    """

    session_id: str
    event_type: NPhaseEventType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "event_type": self.event_type.name,
            "timestamp": self.timestamp.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass
class PhaseTransitionEvent(NPhaseEvent):
    """
    Event emitted when phase boundary is crossed.

    Carries from_phase, to_phase, and cycle count.
    Used for UI updates, logging, and orchestration.
    """

    from_phase: NPhase = NPhase.UNDERSTAND
    to_phase: NPhase = NPhase.ACT
    cycle_count: int = 0
    payload: Any = None

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.PHASE_TRANSITION

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "from_phase": self.from_phase.name,
            "to_phase": self.to_phase.name,
            "cycle_count": self.cycle_count,
            "payload": self.payload,
        })
        return base


@dataclass
class PhaseCheckpointEvent(NPhaseEvent):
    """
    Event emitted when checkpoint is created.

    Carries checkpoint ID and phase context.
    Used for recovery UI and audit logging.
    """

    checkpoint_id: str = ""
    phase: NPhase = NPhase.UNDERSTAND
    cycle_count: int = 0
    handle_count: int = 0

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.PHASE_CHECKPOINT

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "checkpoint_id": self.checkpoint_id,
            "phase": self.phase.name,
            "cycle_count": self.cycle_count,
            "handle_count": self.handle_count,
        })
        return base


@dataclass
class PhaseSignalDetectedEvent(NPhaseEvent):
    """
    Event emitted when phase signal is detected.

    Carries the detected signal for observability.
    Useful for debugging auto-detection behavior.
    """

    signal: PhaseSignal | None = None
    output_text: str = ""
    auto_advanced: bool = False

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.SIGNAL_DETECTED

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "signal": self.signal.to_dict() if self.signal else None,
            "output_text_preview": self.output_text[:200] if self.output_text else "",
            "auto_advanced": self.auto_advanced,
        })
        return base


@dataclass
class SessionCreatedEvent(NPhaseEvent):
    """
    Event emitted when a new session is created.

    Carries session title and initial configuration.
    """

    title: str = ""
    initial_phase: NPhase = NPhase.UNDERSTAND

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.SESSION_CREATED

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "title": self.title,
            "initial_phase": self.initial_phase.name,
        })
        return base


@dataclass
class SessionEndedEvent(NPhaseEvent):
    """
    Event emitted when session ends.

    Carries summary statistics for the session.
    """

    final_phase: NPhase = NPhase.REFLECT
    total_cycles: int = 0
    total_handles: int = 0
    total_checkpoints: int = 0
    total_entropy: dict[str, float] = field(default_factory=dict)
    reason: str = ""

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.SESSION_ENDED

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "final_phase": self.final_phase.name,
            "total_cycles": self.total_cycles,
            "total_handles": self.total_handles,
            "total_checkpoints": self.total_checkpoints,
            "total_entropy": dict(self.total_entropy),
            "reason": self.reason,
        })
        return base


@dataclass
class HandleAddedEvent(NPhaseEvent):
    """
    Event emitted when a handle is added.

    Tracks handle accumulation for observability.
    """

    path: str = ""
    phase: NPhase = NPhase.UNDERSTAND

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.HANDLE_ADDED

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "path": self.path,
            "phase": self.phase.name,
        })
        return base


@dataclass
class EntropySpentEvent(NPhaseEvent):
    """
    Event emitted when entropy is spent.

    Tracks resource consumption for budgeting.
    """

    category: str = ""
    amount: float = 0.0
    phase: NPhase = NPhase.UNDERSTAND

    def __post_init__(self) -> None:
        """Set event type."""
        self.event_type = NPhaseEventType.ENTROPY_SPENT

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "category": self.category,
            "amount": self.amount,
            "phase": self.phase.name,
        })
        return base


# =============================================================================
# Event Factory Functions
# =============================================================================


def phase_transition_event(
    session_id: str,
    from_phase: NPhase,
    to_phase: NPhase,
    cycle_count: int = 0,
    payload: Any = None,
    **metadata: Any,
) -> PhaseTransitionEvent:
    """Create a phase transition event."""
    return PhaseTransitionEvent(
        session_id=session_id,
        from_phase=from_phase,
        to_phase=to_phase,
        cycle_count=cycle_count,
        payload=payload,
        metadata=metadata,
    )


def checkpoint_event(
    session_id: str,
    checkpoint_id: str,
    phase: NPhase,
    cycle_count: int = 0,
    handle_count: int = 0,
    **metadata: Any,
) -> PhaseCheckpointEvent:
    """Create a checkpoint event."""
    return PhaseCheckpointEvent(
        session_id=session_id,
        checkpoint_id=checkpoint_id,
        phase=phase,
        cycle_count=cycle_count,
        handle_count=handle_count,
        metadata=metadata,
    )


def signal_detected_event(
    session_id: str,
    signal: PhaseSignal,
    output_text: str = "",
    auto_advanced: bool = False,
    **metadata: Any,
) -> PhaseSignalDetectedEvent:
    """Create a signal detected event."""
    return PhaseSignalDetectedEvent(
        session_id=session_id,
        signal=signal,
        output_text=output_text,
        auto_advanced=auto_advanced,
        metadata=metadata,
    )


def session_created_event(
    session_id: str,
    title: str = "",
    initial_phase: NPhase = NPhase.UNDERSTAND,
    **metadata: Any,
) -> SessionCreatedEvent:
    """Create a session created event."""
    return SessionCreatedEvent(
        session_id=session_id,
        title=title,
        initial_phase=initial_phase,
        metadata=metadata,
    )


def session_ended_event(
    session_id: str,
    final_phase: NPhase,
    total_cycles: int,
    total_handles: int,
    total_checkpoints: int,
    total_entropy: dict[str, float] | None = None,
    reason: str = "",
    **metadata: Any,
) -> SessionEndedEvent:
    """Create a session ended event."""
    return SessionEndedEvent(
        session_id=session_id,
        final_phase=final_phase,
        total_cycles=total_cycles,
        total_handles=total_handles,
        total_checkpoints=total_checkpoints,
        total_entropy=total_entropy or {},
        reason=reason,
        metadata=metadata,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enum
    "NPhaseEventType",
    # Base class
    "NPhaseEvent",
    # Event types
    "PhaseTransitionEvent",
    "PhaseCheckpointEvent",
    "PhaseSignalDetectedEvent",
    "SessionCreatedEvent",
    "SessionEndedEvent",
    "HandleAddedEvent",
    "EntropySpentEvent",
    # Factory functions
    "phase_transition_event",
    "checkpoint_event",
    "signal_detected_event",
    "session_created_event",
    "session_ended_event",
]
