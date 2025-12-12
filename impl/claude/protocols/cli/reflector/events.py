"""
Runtime Events - Events that flow through the Reflector.

These events represent significant happenings in the kgents runtime
that surfaces (CLI, TUI, web) need to know about.

Category Theory:
  Events are morphisms in the Time category.
  Each event transforms the observable state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(Enum):
    """Types of runtime events."""

    # Command lifecycle
    COMMAND_START = "command_start"
    COMMAND_END = "command_end"

    # Agent lifecycle
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_UPDATED = "agent_updated"
    AGENT_HEALTH_UPDATE = "agent_health_update"

    # Proposal system
    PROPOSAL_ADDED = "proposal_added"
    PROPOSAL_RESOLVED = "proposal_resolved"

    # Pheromone signals
    PHEROMONE_EMITTED = "pheromone_emitted"
    PHEROMONE_DECAYED = "pheromone_decayed"

    # System events
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Invoker(Enum):
    """Who invoked a command."""

    HUMAN = "human"
    AGENT = "agent"
    SCHEDULED = "scheduled"
    INTERNAL = "internal"


@dataclass(frozen=True)
class RuntimeEvent:
    """
    Base event from the runtime.

    Immutable to ensure events can be safely shared across
    multiple reflector implementations.
    """

    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""  # e.g., "cortex", "d-gent", "status-handler"
    data: dict[str, Any] = field(default_factory=dict)
    sequence: int = 0  # For ordering concurrent events

    def with_sequence(self, seq: int) -> RuntimeEvent:
        """Return a new event with the given sequence number."""
        return RuntimeEvent(
            event_type=self.event_type,
            timestamp=self.timestamp,
            source=self.source,
            data=self.data,
            sequence=seq,
        )


@dataclass(frozen=True)
class CommandStartEvent(RuntimeEvent):
    """Emitted when a command begins execution."""

    command: str = ""
    args: tuple[str, ...] = ()
    invoker: Invoker = Invoker.HUMAN
    trace_id: str = ""

    def __post_init__(self) -> None:
        # Validate event_type
        if self.event_type != EventType.COMMAND_START:
            object.__setattr__(self, "event_type", EventType.COMMAND_START)


@dataclass(frozen=True)
class CommandEndEvent(RuntimeEvent):
    """Emitted when a command completes."""

    command: str = ""
    exit_code: int = 0
    duration_ms: int = 0
    human_output: str = ""
    semantic_output: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""

    def __post_init__(self) -> None:
        if self.event_type != EventType.COMMAND_END:
            object.__setattr__(self, "event_type", EventType.COMMAND_END)


@dataclass(frozen=True)
class AgentHealthEvent(RuntimeEvent):
    """Emitted when agent health changes."""

    agent_id: str = ""
    agent_name: str = ""
    health: dict[str, float] = field(default_factory=dict)  # {"x": 0.9, "y": 0.8, "z": 0.7}
    phase: str = ""  # "active", "dormant", "waking", "waning", "void"
    activity: float = 0.0  # 0.0-1.0

    def __post_init__(self) -> None:
        if self.event_type != EventType.AGENT_HEALTH_UPDATE:
            object.__setattr__(self, "event_type", EventType.AGENT_HEALTH_UPDATE)


@dataclass(frozen=True)
class AgentRegisteredEvent(RuntimeEvent):
    """Emitted when a new agent registers with the system."""

    agent_id: str = ""
    agent_name: str = ""
    genus: str = ""  # e.g., "d-gent", "t-gent"
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.event_type != EventType.AGENT_REGISTERED:
            object.__setattr__(self, "event_type", EventType.AGENT_REGISTERED)


@dataclass(frozen=True)
class AgentUnregisteredEvent(RuntimeEvent):
    """Emitted when an agent unregisters from the system."""

    agent_id: str = ""
    agent_name: str = ""
    reason: str = ""  # "shutdown", "timeout", "error"

    def __post_init__(self) -> None:
        if self.event_type != EventType.AGENT_UNREGISTERED:
            object.__setattr__(self, "event_type", EventType.AGENT_UNREGISTERED)


@dataclass(frozen=True)
class ProposalAddedEvent(RuntimeEvent):
    """Emitted when an agent adds a proposal."""

    proposal_id: str = ""
    from_agent: str = ""
    action: str = ""
    reason: str = ""
    priority: str = "normal"  # "low", "normal", "high", "critical"
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.event_type != EventType.PROPOSAL_ADDED:
            object.__setattr__(self, "event_type", EventType.PROPOSAL_ADDED)


@dataclass(frozen=True)
class ProposalResolvedEvent(RuntimeEvent):
    """Emitted when a proposal is resolved."""

    proposal_id: str = ""
    resolution: str = ""  # "approved", "rejected", "expired"
    resolved_by: str = ""  # "human" or agent id

    def __post_init__(self) -> None:
        if self.event_type != EventType.PROPOSAL_RESOLVED:
            object.__setattr__(self, "event_type", EventType.PROPOSAL_RESOLVED)


@dataclass(frozen=True)
class PheromoneEvent(RuntimeEvent):
    """Emitted when pheromone activity occurs."""

    pheromone_type: str = ""
    level: float = 0.0
    agent_id: str = ""

    def __post_init__(self) -> None:
        if self.event_type not in (EventType.PHEROMONE_EMITTED, EventType.PHEROMONE_DECAYED):
            object.__setattr__(self, "event_type", EventType.PHEROMONE_EMITTED)


@dataclass(frozen=True)
class ErrorEvent(RuntimeEvent):
    """Emitted when an error occurs."""

    error_code: str = ""
    message: str = ""
    recoverable: bool = True
    suggestions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.event_type != EventType.ERROR:
            object.__setattr__(self, "event_type", EventType.ERROR)


# =============================================================================
# Factory Functions
# =============================================================================


def command_start(
    command: str,
    args: list[str] | None = None,
    invoker: Invoker = Invoker.HUMAN,
    trace_id: str = "",
    source: str = "cli",
) -> CommandStartEvent:
    """Create a CommandStartEvent."""
    return CommandStartEvent(
        event_type=EventType.COMMAND_START,
        source=source,
        command=command,
        args=tuple(args or []),
        invoker=invoker,
        trace_id=trace_id,
    )


def command_end(
    command: str,
    exit_code: int,
    duration_ms: int = 0,
    human_output: str = "",
    semantic_output: dict[str, Any] | None = None,
    trace_id: str = "",
    source: str = "cli",
) -> CommandEndEvent:
    """Create a CommandEndEvent."""
    return CommandEndEvent(
        event_type=EventType.COMMAND_END,
        source=source,
        command=command,
        exit_code=exit_code,
        duration_ms=duration_ms,
        human_output=human_output,
        semantic_output=semantic_output or {},
        trace_id=trace_id,
    )


def agent_health(
    agent_id: str,
    agent_name: str,
    health: dict[str, float],
    phase: str = "active",
    activity: float = 0.5,
    source: str = "o-gent",
) -> AgentHealthEvent:
    """Create an AgentHealthEvent."""
    return AgentHealthEvent(
        event_type=EventType.AGENT_HEALTH_UPDATE,
        source=source,
        agent_id=agent_id,
        agent_name=agent_name,
        health=health,
        phase=phase,
        activity=activity,
    )


def agent_registered(
    agent_id: str,
    agent_name: str,
    genus: str,
    capabilities: list[str] | None = None,
    source: str = "registry",
) -> AgentRegisteredEvent:
    """Create an AgentRegisteredEvent."""
    return AgentRegisteredEvent(
        event_type=EventType.AGENT_REGISTERED,
        source=source,
        agent_id=agent_id,
        agent_name=agent_name,
        genus=genus,
        capabilities=tuple(capabilities or []),
    )


def proposal_added(
    proposal_id: str,
    from_agent: str,
    action: str,
    reason: str = "",
    priority: str = "normal",
    confidence: float = 0.5,
    source: str = "proposal-queue",
) -> ProposalAddedEvent:
    """Create a ProposalAddedEvent."""
    return ProposalAddedEvent(
        event_type=EventType.PROPOSAL_ADDED,
        source=source,
        proposal_id=proposal_id,
        from_agent=from_agent,
        action=action,
        reason=reason,
        priority=priority,
        confidence=confidence,
    )


def error_event(
    error_code: str,
    message: str,
    recoverable: bool = True,
    suggestions: list[str] | None = None,
    source: str = "cli",
) -> ErrorEvent:
    """Create an ErrorEvent."""
    return ErrorEvent(
        event_type=EventType.ERROR,
        source=source,
        error_code=error_code,
        message=message,
        recoverable=recoverable,
        suggestions=tuple(suggestions or []),
    )
