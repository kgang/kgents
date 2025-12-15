"""
Tests for TimelineWidget time-travel debugging.

Verifies:
- Navigation (seek, step forward/backward)
- Event retrieval with dependency highlighting
- Widget snapshot capture/restore
- Checkpoint integration
- State management
- Rendering outputs
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest
from agents.town.timeline_widget import (
    TimelineEvent,
    TimelineState,
    TimelineWidget,
    WidgetSnapshotManager,
    create_timeline_from_events,
    create_timeline_widget,
)
from agents.town.trace_bridge import TownTrace, TownTraceEvent


@dataclass
class MockSignal:
    """Mock Signal for testing snapshots."""

    _value: int = 0
    _generation: int = 0

    def snapshot(self) -> "MockSnapshot":
        return MockSnapshot(
            value=self._value,
            timestamp=0.0,
            generation=self._generation,
        )

    def set(self, value: int) -> None:
        self._value = value
        self._generation += 1

    @property
    def value(self) -> int:
        return self._value


@dataclass(frozen=True)
class MockSnapshot:
    """Mock Snapshot for testing."""

    value: int
    timestamp: float
    generation: int


@dataclass
class MockTownEvent:
    """Mock TownEvent for testing."""

    phase: "MockPhase"
    operation: str
    participants: list[str]
    success: bool = True
    message: str = ""
    timestamp: datetime | None = None
    tokens_used: int = 0
    drama_contribution: float = 0.0
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MockPhase:
    """Mock TownPhase."""

    name: str


@pytest.fixture
def trace_with_events() -> TownTrace:
    """Create a TownTrace with test events."""
    trace = TownTrace()

    # Add events with different participants for independence testing
    events = [
        MockTownEvent(MockPhase("MORNING"), "greet", ["alice", "bob"]),
        MockTownEvent(MockPhase("MORNING"), "gossip", ["alice", "charlie"]),
        MockTownEvent(MockPhase("AFTERNOON"), "trade", ["bob", "diana"]),
        MockTownEvent(MockPhase("AFTERNOON"), "solo", ["eve"]),
        MockTownEvent(MockPhase("EVENING"), "debate", ["alice", "diana"]),
    ]

    for event in events:
        trace.append(event)  # type: ignore[arg-type]

    return trace


class TestTimelineState:
    """Tests for TimelineState dataclass."""

    def test_default_values(self) -> None:
        """Default state has sensible values."""
        state = TimelineState()
        assert state.current_tick == 0
        assert state.max_tick == 0
        assert not state.is_playing
        assert state.playback_speed == 1.0
        assert state.selected_event_id is None

    def test_to_dict(self) -> None:
        """State serializes to dictionary."""
        state = TimelineState(
            current_tick=10,
            max_tick=100,
            is_playing=True,
            playback_speed=2.0,
        )
        d = state.to_dict()

        assert d["current_tick"] == 10
        assert d["max_tick"] == 100
        assert d["is_playing"] is True
        assert d["playback_speed"] == 2.0


class TestTimelineEvent:
    """Tests for TimelineEvent dataclass."""

    def test_to_dict(self) -> None:
        """Event serializes to dictionary."""
        event = TimelineEvent(
            tick=5,
            event_id="town_000005",
            phase="MORNING",
            operation="greet",
            participants=("alice", "bob"),
            timestamp=datetime(2025, 12, 14, 10, 0, 0),
            success=True,
            message="Alice greets Bob",
            is_dependent=True,
            is_independent=False,
            is_checkpoint=True,
        )
        d = event.to_dict()

        assert d["tick"] == 5
        assert d["event_id"] == "town_000005"
        assert d["phase"] == "MORNING"
        assert d["is_dependent"] is True
        assert d["is_checkpoint"] is True


class TestWidgetSnapshotManager:
    """Tests for WidgetSnapshotManager."""

    def test_register_signal(self) -> None:
        """Can register signals."""
        manager = WidgetSnapshotManager()
        signal = MockSignal()

        manager.register("zoom", signal)  # type: ignore[arg-type]
        assert manager.tick_count == 0

    def test_capture_snapshot(self) -> None:
        """capture() records signal state."""
        manager = WidgetSnapshotManager()
        signal = MockSignal()
        signal.set(42)

        manager.register("zoom", signal)  # type: ignore[arg-type]
        snapshots = manager.capture(tick=10)

        assert "zoom" in snapshots
        assert snapshots["zoom"]["value"] == 42
        assert manager.tick_count == 1

    def test_restore_snapshot(self) -> None:
        """restore() reverts signal to captured state."""
        manager = WidgetSnapshotManager()
        signal = MockSignal()
        signal.set(42)

        manager.register("zoom", signal)  # type: ignore[arg-type]
        manager.capture(tick=10)

        # Change value
        signal.set(999)
        assert signal.value == 999

        # Restore
        result = manager.restore(tick=10)
        assert result is True
        assert signal.value == 42

    def test_restore_nonexistent_tick(self) -> None:
        """restore() returns False for missing tick."""
        manager = WidgetSnapshotManager()
        result = manager.restore(tick=999)
        assert result is False

    def test_get_nearest_tick(self) -> None:
        """get_nearest_tick() finds closest snapshot."""
        manager = WidgetSnapshotManager()
        signal = MockSignal()
        manager.register("x", signal)  # type: ignore[arg-type]

        manager.capture(10)
        manager.capture(20)
        manager.capture(30)

        assert manager.get_nearest_tick(10) == 10
        assert manager.get_nearest_tick(15) == 10
        assert manager.get_nearest_tick(17) == 20
        assert manager.get_nearest_tick(25) == 20
        assert manager.get_nearest_tick(50) == 30

    def test_prune_before(self) -> None:
        """prune_before() removes old snapshots."""
        manager = WidgetSnapshotManager()
        signal = MockSignal()
        manager.register("x", signal)  # type: ignore[arg-type]

        manager.capture(10)
        manager.capture(20)
        manager.capture(30)

        pruned = manager.prune_before(25)
        assert pruned == 2
        assert manager.tick_count == 1


class TestTimelineWidgetBasic:
    """Basic TimelineWidget functionality."""

    def test_create_empty_widget(self) -> None:
        """Can create widget without trace."""
        widget = TimelineWidget()
        assert widget.current_tick == 0
        assert widget.max_tick == 0

    def test_create_with_trace(self, trace_with_events: TownTrace) -> None:
        """Widget syncs with trace on creation."""
        widget = TimelineWidget(trace=trace_with_events)

        assert widget.max_tick == 5
        assert widget.state.start_time is not None
        assert widget.state.end_time is not None

    def test_progress_property(self, trace_with_events: TownTrace) -> None:
        """progress reflects position in timeline."""
        widget = TimelineWidget(trace=trace_with_events)

        assert widget.progress == 0.0

        # Manually set tick for testing
        widget._state.current_tick = 2
        assert widget.progress == pytest.approx(0.4)

        widget._state.current_tick = 5
        assert widget.progress == pytest.approx(1.0)


class TestTimelineWidgetNavigation:
    """Navigation functionality."""

    @pytest.mark.asyncio
    async def test_seek(self, trace_with_events: TownTrace) -> None:
        """seek() moves to target tick."""
        widget = TimelineWidget(trace=trace_with_events)

        result = await widget.seek(3)

        assert result is True
        assert widget.current_tick == 3

    @pytest.mark.asyncio
    async def test_seek_bounds(self, trace_with_events: TownTrace) -> None:
        """seek() respects bounds."""
        widget = TimelineWidget(trace=trace_with_events)

        # Out of bounds
        result = await widget.seek(-1)
        assert result is False

        result = await widget.seek(100)
        assert result is False

    @pytest.mark.asyncio
    async def test_seek_fires_callback(self, trace_with_events: TownTrace) -> None:
        """seek() calls registered callbacks."""
        widget = TimelineWidget(trace=trace_with_events)
        received_ticks = []

        widget.on_seek(lambda t: received_ticks.append(t))

        await widget.seek(2)
        await widget.seek(4)

        assert received_ticks == [2, 4]

    def test_step_forward(self, trace_with_events: TownTrace) -> None:
        """step_forward() advances position."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 0

        new_tick = widget.step_forward()
        assert new_tick == 1

        widget._state.current_tick = 1
        new_tick = widget.step_forward(count=3)
        assert new_tick == 4

    def test_step_backward(self, trace_with_events: TownTrace) -> None:
        """step_backward() reverses position."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 4

        new_tick = widget.step_backward()
        assert new_tick == 3

        widget._state.current_tick = 3
        new_tick = widget.step_backward(count=2)
        assert new_tick == 1

    def test_step_respects_bounds(self, trace_with_events: TownTrace) -> None:
        """step operations respect bounds."""
        widget = TimelineWidget(trace=trace_with_events)

        # Can't go below 0
        widget._state.current_tick = 0
        new_tick = widget.step_backward()
        assert new_tick == 0

        # Can't go above max
        widget._state.current_tick = 5
        new_tick = widget.step_forward()
        assert new_tick == 5

    def test_go_to_start_end(self, trace_with_events: TownTrace) -> None:
        """go_to_start/end jump to boundaries."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 2

        assert widget.go_to_start() == 0
        assert widget.go_to_end() == 5


class TestTimelineWidgetSelection:
    """Selection and highlighting."""

    def test_select_event(self, trace_with_events: TownTrace) -> None:
        """select_event() updates state."""
        widget = TimelineWidget(trace=trace_with_events)

        widget.select_event("town_000001")
        assert widget.state.selected_event_id == "town_000001"

        widget.select_event(None)
        assert widget.state.selected_event_id is None

    def test_hover_event(self, trace_with_events: TownTrace) -> None:
        """hover_event() updates state."""
        widget = TimelineWidget(trace=trace_with_events)

        widget.hover_event("town_000002")
        assert widget.state.hovered_event_id == "town_000002"


class TestTimelineWidgetPlayback:
    """Playback control."""

    def test_play_pause(self, trace_with_events: TownTrace) -> None:
        """play/pause control playback state."""
        widget = TimelineWidget(trace=trace_with_events)

        assert not widget.is_playing

        widget.play()
        assert widget.is_playing

        widget.pause()
        assert not widget.is_playing

    def test_toggle_play(self, trace_with_events: TownTrace) -> None:
        """toggle_play() toggles state."""
        widget = TimelineWidget(trace=trace_with_events)

        assert widget.toggle_play() is True
        assert widget.is_playing

        assert widget.toggle_play() is False
        assert not widget.is_playing

    def test_set_speed(self, trace_with_events: TownTrace) -> None:
        """set_speed() updates playback rate."""
        widget = TimelineWidget(trace=trace_with_events)

        widget.set_speed(2.0)
        assert widget.playback_speed == 2.0

        # Clamped to range
        widget.set_speed(10.0)
        assert widget.playback_speed == 4.0

        widget.set_speed(0.1)
        assert widget.playback_speed == 0.25


class TestTimelineWidgetEvents:
    """Event retrieval."""

    def test_get_events_in_range(self, trace_with_events: TownTrace) -> None:
        """get_events_in_range() returns events."""
        widget = TimelineWidget(trace=trace_with_events)

        events = widget.get_events_in_range(0, 3)

        assert len(events) == 3
        assert events[0].tick == 0
        assert events[0].operation == "greet"
        assert events[1].operation == "gossip"
        assert events[2].operation == "trade"

    def test_get_events_with_selection(self, trace_with_events: TownTrace) -> None:
        """Events include dependency metadata when selected."""
        widget = TimelineWidget(trace=trace_with_events)

        # Select first event (alice, bob greet)
        widget.select_event("town_000001")

        events = widget.get_events_in_range(0, 5)

        # Event 0: alice, bob - selected (neither dependent nor independent)
        assert events[0].event_id == "town_000001"

        # Event 1: alice, charlie - DEPENDENT (alice in both)
        assert events[1].is_dependent is True

        # Event 2: bob, diana - DEPENDENT (bob in both)
        assert events[2].is_dependent is True

        # Event 3: eve alone - INDEPENDENT (no overlap)
        assert events[3].is_independent is True
        assert events[3].is_dependent is False

    def test_get_current_event(self, trace_with_events: TownTrace) -> None:
        """get_current_event() returns event at position."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 2

        event = widget.get_current_event()

        assert event is not None
        assert event.tick == 2
        assert event.operation == "trade"

    def test_get_visible_events(self, trace_with_events: TownTrace) -> None:
        """get_visible_events() returns window around position."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 2

        events = widget.get_visible_events(window_size=3)

        assert len(events) <= 3


class TestTimelineWidgetDisplay:
    """Display option toggles."""

    def test_toggle_dependent_chain(self, trace_with_events: TownTrace) -> None:
        """toggle_dependent_chain() toggles display."""
        widget = TimelineWidget(trace=trace_with_events)

        assert widget.state.show_dependent_chain is True

        result = widget.toggle_dependent_chain()
        assert result is False
        assert widget.state.show_dependent_chain is False

        result = widget.toggle_dependent_chain()
        assert result is True

    def test_toggle_independent_highlight(self, trace_with_events: TownTrace) -> None:
        """toggle_independent_highlight() toggles display."""
        widget = TimelineWidget(trace=trace_with_events)

        assert widget.state.highlight_independent is True

        result = widget.toggle_independent_highlight()
        assert result is False

    def test_toggle_phase_markers(self, trace_with_events: TownTrace) -> None:
        """toggle_phase_markers() toggles display."""
        widget = TimelineWidget(trace=trace_with_events)

        result = widget.toggle_phase_markers()
        assert result is False
        assert widget.state.show_phase_markers is False


class TestTimelineWidgetCallbacks:
    """Callback registration."""

    def test_on_state_change(self, trace_with_events: TownTrace) -> None:
        """State change callbacks fire on mutations."""
        widget = TimelineWidget(trace=trace_with_events)
        # Capture values at callback time since state object is mutable
        received_values: list[tuple[bool, float]] = []

        widget.on_state_change(
            lambda s: received_values.append((s.is_playing, s.playback_speed))
        )

        widget.play()
        widget.pause()
        widget.set_speed(2.0)

        assert len(received_values) == 3
        assert received_values[0] == (True, 1.0)  # play()
        assert received_values[1] == (False, 1.0)  # pause()
        assert received_values[2] == (False, 2.0)  # set_speed(2.0)

    def test_unsubscribe_callback(self, trace_with_events: TownTrace) -> None:
        """Callbacks can be unsubscribed."""
        widget = TimelineWidget(trace=trace_with_events)
        received = []

        unsub = widget.on_state_change(lambda s: received.append(s))
        widget.play()

        unsub()
        widget.pause()

        # Only first callback received
        assert len(received) == 1


class TestTimelineWidgetRendering:
    """Rendering outputs."""

    def test_render_cli(self, trace_with_events: TownTrace) -> None:
        """render_cli() produces string output."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 2

        output = widget.render_cli(width=50)

        assert "[0002]" in output
        assert "trade" in output
        assert "●" in output  # Scrubber position
        assert "⏸" in output  # Paused indicator

    def test_render_cli_playing(self, trace_with_events: TownTrace) -> None:
        """render_cli() shows play indicator."""
        widget = TimelineWidget(trace=trace_with_events)
        widget.play()

        output = widget.render_cli()

        assert "▶" in output

    def test_render_json(self, trace_with_events: TownTrace) -> None:
        """render_json() produces dict output."""
        widget = TimelineWidget(trace=trace_with_events)
        widget._state.current_tick = 1

        output = widget.render_json()

        assert "state" in output
        assert "current_event" in output
        assert "progress" in output
        assert output["progress"] == pytest.approx(0.2)


class TestTimelineWidgetCheckpoints:
    """Checkpoint integration."""

    def test_checkpoint_ticks_sync(self) -> None:
        """Widget syncs checkpoint ticks from log."""

        # Create mock log with checkpoints
        class MockLog:
            def list_checkpoints(self):
                return ["cp_000010", "cp_000020", "cp_000030"]

        widget = TimelineWidget(log=MockLog())  # type: ignore[arg-type]

        assert 10 in widget._checkpoint_ticks
        assert 20 in widget._checkpoint_ticks
        assert 30 in widget._checkpoint_ticks
        assert widget.state.checkpoint_count == 3

    def test_go_to_checkpoint(self) -> None:
        """go_to_checkpoint() jumps to checkpoint tick."""

        class MockLog:
            def list_checkpoints(self):
                return ["cp_000010", "cp_000020"]

        trace = TownTrace()
        for i in range(25):
            event = MockTownEvent(MockPhase("MORNING"), "test", ["alice"])
            trace.append(event)  # type: ignore[arg-type]

        widget = TimelineWidget(trace=trace, log=MockLog())  # type: ignore[arg-type]

        tick = widget.go_to_checkpoint("cp_000010")
        assert tick == 10

        tick = widget.go_to_checkpoint("cp_000020")
        assert tick == 20

        tick = widget.go_to_checkpoint("cp_999999")
        assert tick is None

    def test_render_cli_with_checkpoints(self) -> None:
        """render_cli() shows checkpoint markers."""

        class MockLog:
            def list_checkpoints(self):
                return ["cp_000002"]

        trace = TownTrace()
        for i in range(5):
            event = MockTownEvent(MockPhase("MORNING"), "test", ["alice"])
            trace.append(event)  # type: ignore[arg-type]

        widget = TimelineWidget(trace=trace, log=MockLog())  # type: ignore[arg-type]
        output = widget.render_cli(width=60)

        assert "◆" in output  # Checkpoint marker


class TestFactoryFunctions:
    """Factory function tests."""

    def test_create_timeline_widget(self, trace_with_events: TownTrace) -> None:
        """create_timeline_widget() creates configured widget."""
        widget = create_timeline_widget(trace=trace_with_events)

        assert widget.trace is trace_with_events
        assert widget.max_tick == 5

    def test_create_timeline_from_events(self) -> None:
        """create_timeline_from_events() creates from event list."""
        events = [
            MockTownEvent(MockPhase("MORNING"), "greet", ["alice", "bob"]),
            MockTownEvent(MockPhase("MORNING"), "trade", ["alice", "charlie"]),
        ]

        widget = create_timeline_from_events(events)  # type: ignore[arg-type]

        assert widget.max_tick == 2
        assert widget.trace is not None
