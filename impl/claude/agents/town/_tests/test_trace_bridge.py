"""
Tests for Trace Bridge (TownEvent → TraceMonoid).

Phase: DEVELOP (contract tests)
Crown Jewel: plans/micro-experience-factory.md

Test Categories:
1. TownTraceEvent creation and serialization
2. Independence relation computation
3. TownTrace append and query operations
4. Replay range selection
5. Dependent chain detection
"""

from __future__ import annotations

from datetime import datetime

import pytest
from agents.town.flux import TownEvent, TownPhase
from agents.town.trace_bridge import (
    ReplayState,
    TownTrace,
    TownTraceEvent,
    are_independent,
    compute_independence_relation,
)

# =============================================================================
# TownTraceEvent Tests
# =============================================================================


class TestTownTraceEvent:
    """Tests for TownTraceEvent."""

    def test_create_event(self) -> None:
        """Create a trace event with all fields."""
        event = TownTraceEvent(
            event_id="town_000001",
            phase="MORNING",
            operation="greet",
            participants=("alice", "bob"),
            success=True,
            message="Alice greeted Bob warmly.",
            tokens_used=50,
            drama_contribution=0.05,
        )

        assert event.event_id == "town_000001"
        assert event.operation == "greet"
        assert len(event.participants) == 2
        assert event.success is True

    def test_from_town_event(self) -> None:
        """Create from TownEvent."""
        town_event = TownEvent(
            phase=TownPhase.AFTERNOON,
            operation="gossip",
            participants=["charlie", "diana"],
            success=True,
            message="They shared rumors.",
            tokens_used=150,
            drama_contribution=0.3,
        )

        trace_event = TownTraceEvent.from_town_event(
            town_event,
            event_id="town_000002",
            repl_command="world.town.gossip",
        )

        assert trace_event.event_id == "town_000002"
        assert trace_event.phase == "AFTERNOON"
        assert trace_event.operation == "gossip"
        assert trace_event.participants == ("charlie", "diana")
        assert trace_event.repl_command == "world.town.gossip"

    def test_to_dict(self) -> None:
        """Event serializes correctly."""
        event = TownTraceEvent(
            event_id="town_000001",
            phase="MORNING",
            operation="greet",
            participants=("alice", "bob"),
            success=True,
        )
        data = event.to_dict()

        assert data["event_id"] == "town_000001"
        assert data["participants"] == ["alice", "bob"]  # List in JSON
        assert "timestamp" in data


# =============================================================================
# Independence Relation Tests
# =============================================================================


class TestIndependenceRelation:
    """Tests for independence relation computation."""

    def test_independent_events(self) -> None:
        """Events with disjoint participants are independent."""
        event_a = TownTraceEvent(
            event_id="a",
            phase="MORNING",
            operation="greet",
            participants=("alice", "bob"),
            success=True,
        )
        event_b = TownTraceEvent(
            event_id="b",
            phase="MORNING",
            operation="trade",
            participants=("charlie", "diana"),
            success=True,
        )

        assert are_independent(event_a, event_b) is True

    def test_dependent_events(self) -> None:
        """Events with shared participants are dependent."""
        event_a = TownTraceEvent(
            event_id="a",
            phase="MORNING",
            operation="greet",
            participants=("alice", "bob"),
            success=True,
        )
        event_b = TownTraceEvent(
            event_id="b",
            phase="AFTERNOON",
            operation="trade",
            participants=("bob", "charlie"),  # Bob in both
            success=True,
        )

        assert are_independent(event_a, event_b) is False

    def test_solo_independence(self) -> None:
        """Solo events with different citizens are independent."""
        event_a = TownTraceEvent(
            event_id="a",
            phase="NIGHT",
            operation="solo",
            participants=("alice",),
            success=True,
        )
        event_b = TownTraceEvent(
            event_id="b",
            phase="NIGHT",
            operation="solo",
            participants=("bob",),
            success=True,
        )

        assert are_independent(event_a, event_b) is True

    def test_compute_relation(self) -> None:
        """Compute independence relation for multiple events."""
        events = [
            TownTraceEvent(
                event_id="e1",
                phase="MORNING",
                operation="greet",
                participants=("alice", "bob"),
                success=True,
            ),
            TownTraceEvent(
                event_id="e2",
                phase="MORNING",
                operation="trade",
                participants=("charlie", "diana"),
                success=True,
            ),
            TownTraceEvent(
                event_id="e3",
                phase="AFTERNOON",
                operation="gossip",
                participants=("bob", "charlie"),  # Overlaps with both e1 and e2
                success=True,
            ),
        ]

        relation = compute_independence_relation(events)

        # e1 and e2 are independent
        assert ("e1", "e2") in relation
        assert ("e2", "e1") in relation

        # e1 and e3 are NOT independent (share bob)
        assert ("e1", "e3") not in relation

        # e2 and e3 are NOT independent (share charlie)
        assert ("e2", "e3") not in relation


# =============================================================================
# TownTrace Tests
# =============================================================================


class TestTownTrace:
    """Tests for TownTrace."""

    def test_append_event(self) -> None:
        """Append events to trace."""
        trace = TownTrace()

        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="greet",
            participants=["alice", "bob"],
            success=True,
        )

        trace_event = trace.append(event)

        assert trace_event.event_id.startswith("town_")
        assert len(trace.events) == 1
        assert trace.get_event(trace_event.event_id) == trace_event

    def test_append_with_repl_command(self) -> None:
        """Append event with REPL command."""
        trace = TownTrace()

        event = TownEvent(
            phase=TownPhase.AFTERNOON,
            operation="gossip",
            participants=["charlie", "diana"],
            success=True,
        )

        trace_event = trace.append(
            event,
            repl_command="world.town.gossip",
            repl_session_id="session_001",
        )

        assert trace_event.repl_command == "world.town.gossip"
        assert trace_event.repl_session_id == "session_001"

    def test_independence_cached(self) -> None:
        """Independence relation is computed lazily and cached."""
        trace = TownTrace()

        # Add events
        trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="greet",
                participants=["alice", "bob"],
                success=True,
            )
        )
        trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="trade",
                participants=["charlie", "diana"],
                success=True,
            )
        )

        # Access independence (triggers computation)
        independence1 = trace.independence
        independence2 = trace.independence

        # Same cached object
        assert independence1 is independence2

    def test_can_commute(self) -> None:
        """Check if events can commute."""
        trace = TownTrace()

        e1 = trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="greet",
                participants=["alice", "bob"],
                success=True,
            )
        )
        e2 = trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="trade",
                participants=["charlie", "diana"],
                success=True,
            )
        )

        assert trace.can_commute(e1.event_id, e2.event_id) is True

    def test_replay_range(self) -> None:
        """Get events for replay range."""
        trace = TownTrace()

        # Add 5 events
        for i in range(5):
            trace.append(
                TownEvent(
                    phase=TownPhase.MORNING,
                    operation="solo",
                    participants=[f"citizen_{i}"],
                    success=True,
                )
            )

        # Get range [1, 4)
        events = trace.replay_range(1, 4)

        assert len(events) == 3
        assert events[0].participants == ("citizen_1",)
        assert events[2].participants == ("citizen_3",)

    def test_find_dependent_chain(self) -> None:
        """Find events dependent on a given event."""
        trace = TownTrace()

        e1 = trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="greet",
                participants=["alice", "bob"],
                success=True,
            )
        )
        e2 = trace.append(
            TownEvent(
                phase=TownPhase.AFTERNOON,
                operation="gossip",
                participants=["bob", "charlie"],  # Shares bob with e1
                success=True,
            )
        )
        e3 = trace.append(
            TownEvent(
                phase=TownPhase.EVENING,
                operation="trade",
                participants=["diana", "eve"],  # Independent
                success=True,
            )
        )

        chain = trace.find_dependent_chain(e1.event_id)

        # Only e2 is dependent on e1 (shares bob)
        assert len(chain) == 1
        assert chain[0].event_id == e2.event_id

    def test_to_dict(self) -> None:
        """Trace serializes correctly."""
        trace = TownTrace()
        trace.append(
            TownEvent(
                phase=TownPhase.MORNING,
                operation="greet",
                participants=["alice", "bob"],
                success=True,
            )
        )

        data = trace.to_dict()

        assert data["type"] == "town_trace"
        assert data["event_count"] == 1
        assert len(data["events"]) == 1


# =============================================================================
# ReplayState Tests
# =============================================================================


class TestReplayState:
    """Tests for ReplayState."""

    def test_default_state(self) -> None:
        """Default replay state has correct values."""
        state = ReplayState()

        assert state.current_tick == 0
        assert state.is_playing is False
        assert state.playback_speed == 1.0

    def test_to_dict(self) -> None:
        """State serializes correctly."""
        state = ReplayState(
            current_tick=10,
            max_tick=100,
            is_playing=True,
        )
        data = state.to_dict()

        assert data["type"] == "replay_state"
        assert data["current_tick"] == 10
        assert data["is_playing"] is True

    def test_immutability(self) -> None:
        """State is immutable."""
        state = ReplayState()

        with pytest.raises(AttributeError):
            state.current_tick = 5  # type: ignore[misc]


# =============================================================================
# TownTrace → ReplayState Integration Tests (Step 2)
# =============================================================================


class TestTownTraceReplayStateIntegration:
    """Tests for TownTrace → ReplayState integration."""

    def test_create_replay_state_empty_trace(self) -> None:
        """Create replay state from empty trace."""
        trace = TownTrace()
        state = trace.create_replay_state()

        assert state.current_tick == 0
        assert state.min_tick == 0
        assert state.max_tick == 0
        assert state.start_time is None
        assert state.end_time is None

    def test_create_replay_state_with_events(self) -> None:
        """Create replay state from trace with events."""
        trace = TownTrace()

        # Add 5 events
        for i in range(5):
            trace.append(
                TownEvent(
                    phase=TownPhase.MORNING,
                    operation="solo",
                    participants=[f"citizen_{i}"],
                    success=True,
                )
            )

        state = trace.create_replay_state()

        assert state.current_tick == 0
        assert state.min_tick == 0
        assert state.max_tick == 5
        assert state.start_time is not None
        assert state.end_time is not None

    def test_create_replay_state_custom_tick(self) -> None:
        """Create replay state with custom initial tick."""
        trace = TownTrace()

        for i in range(10):
            trace.append(
                TownEvent(
                    phase=TownPhase.AFTERNOON,
                    operation="solo",
                    participants=[f"citizen_{i}"],
                    success=True,
                )
            )

        state = trace.create_replay_state(current_tick=5, is_playing=True)

        assert state.current_tick == 5
        assert state.is_playing is True

    def test_events_at_tick(self) -> None:
        """Get events at specific tick."""
        trace = TownTrace()

        for i in range(3):
            trace.append(
                TownEvent(
                    phase=TownPhase.MORNING,
                    operation="solo",
                    participants=[f"citizen_{i}"],
                    success=True,
                )
            )

        events = trace.events_at_tick(1)
        assert len(events) == 1
        assert events[0].participants == ("citizen_1",)

        # Invalid tick returns empty
        assert trace.events_at_tick(-1) == []
        assert trace.events_at_tick(10) == []

    def test_events_for_replay_state(self) -> None:
        """Get events based on replay state."""
        trace = TownTrace()

        for i in range(5):
            trace.append(
                TownEvent(
                    phase=TownPhase.EVENING,
                    operation="greet",
                    participants=[f"alice_{i}", f"bob_{i}"],
                    success=True,
                )
            )

        replay_state = trace.create_replay_state(current_tick=2)
        events = trace.events_for_replay_state(replay_state)

        assert len(events) == 1
        assert events[0].participants == ("alice_2", "bob_2")
