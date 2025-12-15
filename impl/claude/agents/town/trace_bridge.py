"""
Trace Bridge: Connecting TownFlux to TraceMonoid for replay and braiding.

This module bridges:
- TownEvent (flux.py) → TraceEvent (weave/trace_monoid.py)
- Independence relations derived from citizen participation
- Replay scrubber state management

Design Philosophy:
- Events from different citizens are independent (can commute)
- Events involving the same citizen are dependent (ordered)
- Trace monoid enables replay with correct ordering

Heritage:
- S1: TraceMonoid (weave/trace_monoid.py)
- S2: TownEvent (agents/town/flux.py)
- S3: REPLSession (protocols/cli/repl.py)
- S4: Independence relations (Mazurkiewicz traces)

Crown Jewel: plans/micro-experience-factory.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from agents.town.flux import TownEvent
    from weave.trace_monoid import TraceMonoid

T = TypeVar("T")


# =============================================================================
# Town Trace Event
# =============================================================================


@dataclass(frozen=True)
class TownTraceEvent:
    """
    A TownEvent wrapped for TraceMonoid integration.

    Captures:
    - The original TownEvent
    - Participant IDs for independence relation computation
    - Timestamp for replay ordering
    - Optional REPL command that triggered this event

    Independence Relation:
    - Two events are independent iff participants ∩ participants = ∅
    - Events with disjoint participants can commute in the trace
    """

    # Unique event ID
    event_id: str

    # Original TownEvent data
    phase: str  # TownPhase.name
    operation: str
    participants: tuple[str, ...]  # Citizen IDs (frozen for hashability)
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    drama_contribution: float = 0.0

    # Optional: REPL command that triggered this event
    repl_command: str | None = None
    repl_session_id: str | None = None

    # Metadata for trace analysis
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "phase": self.phase,
            "operation": self.operation,
            "participants": list(self.participants),
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "tokens_used": self.tokens_used,
            "drama_contribution": self.drama_contribution,
            "repl_command": self.repl_command,
            "repl_session_id": self.repl_session_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_town_event(
        cls,
        event: "TownEvent",
        event_id: str,
        repl_command: str | None = None,
        repl_session_id: str | None = None,
    ) -> "TownTraceEvent":
        """Create from a TownEvent."""
        return cls(
            event_id=event_id,
            phase=event.phase.name,
            operation=event.operation,
            participants=tuple(event.participants),  # Convert list to tuple
            success=event.success,
            message=event.message,
            timestamp=event.timestamp,
            tokens_used=event.tokens_used,
            drama_contribution=event.drama_contribution,
            repl_command=repl_command,
            repl_session_id=repl_session_id,
            metadata=dict(event.metadata),
        )


# =============================================================================
# Independence Relation
# =============================================================================


def are_independent(event_a: TownTraceEvent, event_b: TownTraceEvent) -> bool:
    """
    Determine if two events are independent (can commute).

    Two events are independent iff they share no participants.
    Independent events can be reordered without changing meaning.

    Examples:
        - Alice greets Bob, Charlie greets Dana → INDEPENDENT
        - Alice greets Bob, Bob trades with Charlie → DEPENDENT (Bob in both)
    """
    participants_a = set(event_a.participants)
    participants_b = set(event_b.participants)
    return participants_a.isdisjoint(participants_b)


def compute_independence_relation(
    events: list[TownTraceEvent],
) -> frozenset[tuple[str, str]]:
    """
    Compute the independence relation for a set of events.

    Returns a frozenset of (event_id_a, event_id_b) pairs that are independent.
    This is the I ⊆ Σ × Σ in the trace monoid definition.
    """
    independence: set[tuple[str, str]] = set()

    for i, event_a in enumerate(events):
        for event_b in events[i + 1 :]:
            if are_independent(event_a, event_b):
                # Add both orderings (symmetric relation)
                independence.add((event_a.event_id, event_b.event_id))
                independence.add((event_b.event_id, event_a.event_id))

    return frozenset(independence)


# =============================================================================
# Town Trace (Wrapper around TraceMonoid)
# =============================================================================


@dataclass
class TownTrace:
    """
    A trace of TownEvents with independence-aware replay.

    Wraps TraceMonoid with TownEvent-specific operations.
    """

    # Event storage
    events: list[TownTraceEvent] = field(default_factory=list)

    # Event index by ID
    _events_by_id: dict[str, TownTraceEvent] = field(default_factory=dict)

    # Computed independence relation (lazy)
    _independence: frozenset[tuple[str, str]] | None = None

    # Counter for generating event IDs
    _event_counter: int = 0

    def append(
        self,
        event: "TownEvent",
        repl_command: str | None = None,
        repl_session_id: str | None = None,
    ) -> TownTraceEvent:
        """
        Add a TownEvent to the trace.

        Returns the wrapped TownTraceEvent with assigned ID.
        """
        # Generate event ID
        self._event_counter += 1
        event_id = f"town_{self._event_counter:06d}"

        # Wrap event
        trace_event = TownTraceEvent.from_town_event(
            event,
            event_id=event_id,
            repl_command=repl_command,
            repl_session_id=repl_session_id,
        )

        # Store
        self.events.append(trace_event)
        self._events_by_id[event_id] = trace_event

        # Invalidate cached independence
        self._independence = None

        return trace_event

    def get_event(self, event_id: str) -> TownTraceEvent | None:
        """Get an event by ID."""
        return self._events_by_id.get(event_id)

    @property
    def independence(self) -> frozenset[tuple[str, str]]:
        """Get the independence relation (computed lazily)."""
        if self._independence is None:
            self._independence = compute_independence_relation(self.events)
        return self._independence

    def can_commute(self, event_id_a: str, event_id_b: str) -> bool:
        """Check if two events can commute (are independent)."""
        return (event_id_a, event_id_b) in self.independence

    def replay_range(
        self,
        start_tick: int,
        end_tick: int,
    ) -> list[TownTraceEvent]:
        """
        Get events for replay between two ticks.

        A "tick" corresponds to an event index.
        Events within the range that are independent can be reordered.
        """
        start = max(0, start_tick)
        end = min(len(self.events), end_tick)
        return self.events[start:end]

    def find_dependent_chain(self, event_id: str) -> list[TownTraceEvent]:
        """
        Find all events dependent on a given event.

        Returns the causal chain of events that cannot be reordered
        with respect to the given event.
        """
        target_event = self.get_event(event_id)
        if not target_event:
            return []

        target_participants = set(target_event.participants)
        chain: list[TownTraceEvent] = []

        for event in self.events:
            if event.event_id == event_id:
                continue
            event_participants = set(event.participants)
            if not target_participants.isdisjoint(event_participants):
                chain.append(event)

        return chain

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "town_trace",
            "event_count": len(self.events),
            "events": [e.to_dict() for e in self.events],
            "independence_pairs": len(self.independence),
        }

    def create_replay_state(
        self,
        current_tick: int | None = None,
        is_playing: bool = False,
        playback_speed: float = 1.0,
    ) -> "ReplayState":
        """
        Create a ReplayState from the trace.

        Convenience method for initializing a replay scrubber widget.

        Args:
            current_tick: Starting tick (defaults to 0)
            is_playing: Whether playback is active
            playback_speed: Playback speed multiplier

        Returns:
            ReplayState configured for this trace
        """
        max_tick = len(self.events)
        tick = current_tick if current_tick is not None else 0

        # Get time bounds if events exist
        start_time = self.events[0].timestamp if self.events else None
        end_time = self.events[-1].timestamp if self.events else None

        return ReplayState(
            current_tick=tick,
            min_tick=0,
            max_tick=max_tick,
            is_playing=is_playing,
            playback_speed=playback_speed,
            start_time=start_time,
            end_time=end_time,
        )

    def events_at_tick(self, tick: int) -> list[TownTraceEvent]:
        """
        Get events at a specific tick.

        A tick corresponds to an event index.
        Returns [event] if tick is valid, [] otherwise.
        """
        if 0 <= tick < len(self.events):
            return [self.events[tick]]
        return []

    def events_for_replay_state(
        self,
        replay_state: "ReplayState",
    ) -> list[TownTraceEvent]:
        """
        Get events for a replay state.

        Returns the event at the current tick position.
        """
        return self.events_at_tick(replay_state.current_tick)


# =============================================================================
# Replay State (For Scrubber Widget)
# =============================================================================


@dataclass(frozen=True)
class ReplayState:
    """
    State for the replay scrubber widget.

    Captures the current position in the trace and replay controls.
    """

    # Current tick (event index)
    current_tick: int = 0

    # Trace bounds
    min_tick: int = 0
    max_tick: int = 0

    # Playback state
    is_playing: bool = False
    playback_speed: float = 1.0  # 1.0 = real time

    # Selection state
    selected_event_id: str | None = None

    # Display options
    show_dependent_chain: bool = True
    highlight_commuting_events: bool = True

    # Timestamp markers
    start_time: datetime | None = None
    end_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "replay_state",
            "current_tick": self.current_tick,
            "min_tick": self.min_tick,
            "max_tick": self.max_tick,
            "is_playing": self.is_playing,
            "playback_speed": self.playback_speed,
            "selected_event_id": self.selected_event_id,
            "show_dependent_chain": self.show_dependent_chain,
            "highlight_commuting_events": self.highlight_commuting_events,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
