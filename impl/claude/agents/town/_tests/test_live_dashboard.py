"""
Tests for LiveDashboard unified visualization.

Verifies:
- Dashboard composition from widgets
- State management across widgets
- Playback control
- Selection propagation
- Layout management
- Rendering outputs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

import pytest

if TYPE_CHECKING:
    from agents.town.flux import TownEvent

from agents.town.live_dashboard import (
    DashboardLayout,
    DashboardState,
    DialogueMessage,
    LiveDashboard,
    create_live_dashboard,
)


@dataclass
class MockPhase:
    """Mock TownPhase."""

    name: str


@dataclass
class MockTownEvent:
    """Mock TownEvent for testing."""

    phase: MockPhase
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.name,
            "operation": self.operation,
            "participants": self.participants,
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else "",
            "tokens_used": self.tokens_used,
            "drama_contribution": self.drama_contribution,
            "metadata": self.metadata,
        }


def create_mock_event(
    phase_name: str = "MORNING",
    operation: str = "greet",
    participants: list[str] | None = None,
    message: str = "",
) -> "TownEvent":
    """Create a mock event cast to TownEvent for type checking."""
    return cast(
        "TownEvent",
        MockTownEvent(
            phase=MockPhase(name=phase_name),
            operation=operation,
            participants=participants or ["alice", "bob"],
            message=message,
        ),
    )


class TestDialogueMessage:
    """Tests for DialogueMessage dataclass."""

    def test_to_dict(self) -> None:
        """Message serializes to dictionary."""
        msg = DialogueMessage(
            speaker_id="alice",
            speaker_name="Alice",
            message="Hello there!",
            timestamp=datetime(2025, 12, 14, 10, 0, 0),
            archetype="explorer",
            is_monologue=False,
        )
        d = msg.to_dict()

        assert d["speaker_id"] == "alice"
        assert d["speaker_name"] == "Alice"
        assert d["message"] == "Hello there!"
        assert d["archetype"] == "explorer"
        assert d["is_monologue"] is False


class TestDashboardState:
    """Tests for DashboardState dataclass."""

    def test_default_values(self) -> None:
        """Default state has sensible values."""
        state = DashboardState()

        assert state.layout == DashboardLayout.FULL
        assert state.is_playing is False
        assert state.playback_speed == 1.0
        assert state.selected_citizen_id is None
        assert len(state.dialogue_messages) == 0

    def test_panel_visibility_defaults(self) -> None:
        """All panels visible by default."""
        state = DashboardState()

        assert state.panel_visible["isometric"] is True
        assert state.panel_visible["scatter"] is True
        assert state.panel_visible["timeline"] is True
        assert state.panel_visible["dialogue"] is True

    def test_to_dict(self) -> None:
        """State serializes to dictionary."""
        state = DashboardState(
            current_tick=42,
            is_playing=True,
            playback_speed=2.0,
        )
        d = state.to_dict()

        assert d["type"] == "dashboard_state"
        assert d["current_tick"] == 42
        assert d["is_playing"] is True
        assert d["playback_speed"] == 2.0


class TestLiveDashboardBasic:
    """Basic LiveDashboard functionality."""

    def test_create_empty_dashboard(self) -> None:
        """Can create dashboard without flux."""
        dashboard = LiveDashboard()

        assert dashboard.current_tick == 0
        assert dashboard.is_playing is False
        assert dashboard.isometric is None
        assert dashboard.scatter is None
        assert dashboard.timeline is None

    def test_create_with_factory(self) -> None:
        """create_live_dashboard() creates dashboard."""
        dashboard = create_live_dashboard()

        assert isinstance(dashboard, LiveDashboard)

    def test_state_property(self) -> None:
        """state property returns DashboardState."""
        dashboard = LiveDashboard()

        assert isinstance(dashboard.state, DashboardState)


class TestLiveDashboardPlayback:
    """Playback control."""

    def test_play_pause(self) -> None:
        """play/pause control playback state."""
        dashboard = LiveDashboard()

        assert not dashboard.is_playing

        dashboard.play()
        assert dashboard.is_playing

        dashboard.pause()
        assert not dashboard.is_playing

    def test_toggle_play(self) -> None:
        """toggle_play() toggles state."""
        dashboard = LiveDashboard()

        assert dashboard.toggle_play() is True
        assert dashboard.is_playing

        assert dashboard.toggle_play() is False
        assert not dashboard.is_playing

    def test_set_speed(self) -> None:
        """set_speed() updates playback rate."""
        dashboard = LiveDashboard()

        dashboard.set_speed(2.0)
        assert dashboard.playback_speed == 2.0

        # Clamped to range
        dashboard.set_speed(10.0)
        assert dashboard.playback_speed == 4.0

        dashboard.set_speed(0.1)
        assert dashboard.playback_speed == 0.25


class TestLiveDashboardSelection:
    """Selection management."""

    def test_select_citizen(self) -> None:
        """select_citizen() updates state."""
        dashboard = LiveDashboard()

        dashboard.select_citizen("alice")
        assert dashboard.state.selected_citizen_id == "alice"

        dashboard.select_citizen(None)
        assert dashboard.state.selected_citizen_id is None

    def test_hover_citizen(self) -> None:
        """hover_citizen() updates state."""
        dashboard = LiveDashboard()

        dashboard.hover_citizen("bob")
        assert dashboard.state.hovered_citizen_id == "bob"


class TestLiveDashboardLayout:
    """Layout management."""

    def test_set_layout_full(self) -> None:
        """FULL layout shows all panels."""
        dashboard = LiveDashboard()
        dashboard.set_layout(DashboardLayout.FULL)

        assert dashboard.state.panel_visible["isometric"] is True
        assert dashboard.state.panel_visible["scatter"] is True
        assert dashboard.state.panel_visible["timeline"] is True
        assert dashboard.state.panel_visible["dialogue"] is True

    def test_set_layout_minimal(self) -> None:
        """MINIMAL layout shows only isometric."""
        dashboard = LiveDashboard()
        dashboard.set_layout(DashboardLayout.MINIMAL)

        assert dashboard.state.panel_visible["isometric"] is True
        assert dashboard.state.panel_visible["scatter"] is False
        assert dashboard.state.panel_visible["timeline"] is False
        assert dashboard.state.panel_visible["dialogue"] is False

    def test_set_layout_compact(self) -> None:
        """COMPACT layout shows isometric + timeline."""
        dashboard = LiveDashboard()
        dashboard.set_layout(DashboardLayout.COMPACT)

        assert dashboard.state.panel_visible["isometric"] is True
        assert dashboard.state.panel_visible["timeline"] is True
        assert dashboard.state.panel_visible["scatter"] is False

    def test_set_layout_analysis(self) -> None:
        """ANALYSIS layout shows scatter + timeline."""
        dashboard = LiveDashboard()
        dashboard.set_layout(DashboardLayout.ANALYSIS)

        assert dashboard.state.panel_visible["scatter"] is True
        assert dashboard.state.panel_visible["timeline"] is True
        assert dashboard.state.panel_visible["isometric"] is False

    def test_toggle_panel(self) -> None:
        """toggle_panel() toggles visibility."""
        dashboard = LiveDashboard()

        assert dashboard.state.panel_visible["scatter"] is True
        result = dashboard.toggle_panel("scatter")
        assert result is False
        assert dashboard.state.panel_visible["scatter"] is False

        result = dashboard.toggle_panel("scatter")
        assert result is True
        assert dashboard.state.panel_visible["scatter"] is True

    def test_toggle_invalid_panel(self) -> None:
        """toggle_panel() returns False for invalid panel."""
        dashboard = LiveDashboard()
        result = dashboard.toggle_panel("nonexistent")
        assert result is False


class TestLiveDashboardCallbacks:
    """Callback registration."""

    def test_on_state_change(self) -> None:
        """State change callbacks fire on mutations."""
        dashboard = LiveDashboard()
        received_values: list[bool] = []

        dashboard.on_state_change(lambda s: received_values.append(s.is_playing))

        dashboard.play()
        dashboard.pause()

        assert len(received_values) == 2
        assert received_values[0] is True
        assert received_values[1] is False

    def test_unsubscribe_callback(self) -> None:
        """Callbacks can be unsubscribed."""
        dashboard = LiveDashboard()
        received = []

        unsub = dashboard.on_state_change(lambda s: received.append(s))
        dashboard.play()

        unsub()
        dashboard.pause()

        assert len(received) == 1


class TestLiveDashboardRendering:
    """Rendering outputs."""

    def test_render_cli(self) -> None:
        """render_cli() produces string output."""
        dashboard = LiveDashboard()
        dashboard._state.current_phase = "MORNING"

        output = dashboard.render_cli(width=60)

        assert "AGENT TOWN" in output
        assert "MORNING" in output
        assert "⏸" in output  # Paused indicator
        assert "Events:" in output

    def test_render_cli_playing(self) -> None:
        """render_cli() shows play indicator."""
        dashboard = LiveDashboard()
        dashboard.play()

        output = dashboard.render_cli()

        assert "▶" in output

    def test_render_json(self) -> None:
        """render_json() produces dict output."""
        dashboard = LiveDashboard()

        output = dashboard.render_json()

        assert "dashboard" in output
        assert output["dashboard"]["type"] == "dashboard_state"

    def test_render_marimo(self) -> None:
        """render_marimo() produces component dict."""
        dashboard = LiveDashboard()

        output = dashboard.render_marimo()

        assert "state" in output


class TestLiveDashboardDialogue:
    """Dialogue stream management."""

    @pytest.mark.asyncio
    async def test_add_dialogue_message(self) -> None:
        """_add_dialogue_message() adds to stream."""
        dashboard = LiveDashboard()

        event = MockTownEvent(
            phase=MockPhase("MORNING"),
            operation="dialogue",
            participants=["alice"],
            message="Hello everyone!",
            metadata={"archetype": "explorer"},
        )

        dashboard._add_dialogue_message(event)  # type: ignore[arg-type]

        assert len(dashboard.state.dialogue_messages) == 1
        msg = dashboard.state.dialogue_messages[0]
        assert msg.speaker_id == "alice"
        assert msg.message == "Hello everyone!"

    @pytest.mark.asyncio
    async def test_dialogue_max_messages(self) -> None:
        """Old messages are pruned when exceeding max."""
        dashboard = LiveDashboard()
        dashboard._state.max_dialogue_messages = 3

        for i in range(5):
            event = MockTownEvent(
                phase=MockPhase("MORNING"),
                operation="dialogue",
                participants=[f"citizen_{i}"],
                message=f"Message {i}",
            )
            dashboard._add_dialogue_message(event)  # type: ignore[arg-type]

        assert len(dashboard.state.dialogue_messages) == 3
        # Should have messages 2, 3, 4 (oldest pruned)
        assert dashboard.state.dialogue_messages[0].speaker_id == "citizen_2"


class TestLiveDashboardEventHandling:
    """Event handling."""

    @pytest.mark.asyncio
    async def test_handle_event_updates_state(self) -> None:
        """_handle_event() updates dashboard state."""
        from agents.town.trace_bridge import TownTrace

        trace = TownTrace()
        dashboard = LiveDashboard(trace=trace)

        event = MockTownEvent(
            phase=MockPhase("AFTERNOON"),
            operation="trade",
            participants=["alice", "bob"],
            tokens_used=100,
        )

        await dashboard._handle_event(event)  # type: ignore[arg-type]

        assert dashboard.state.total_events == 1
        assert dashboard.state.total_tokens == 100
        assert dashboard.state.current_phase == "AFTERNOON"

    @pytest.mark.asyncio
    async def test_handle_event_fires_callbacks(self) -> None:
        """_handle_event() fires registered callbacks."""
        from agents.town.trace_bridge import TownTrace

        trace = TownTrace()
        dashboard = LiveDashboard(trace=trace)
        received_events = []

        dashboard.on_event(lambda e: received_events.append(e))

        event = MockTownEvent(
            phase=MockPhase("MORNING"),
            operation="greet",
            participants=["alice"],
        )

        await dashboard._handle_event(event)  # type: ignore[arg-type]

        assert len(received_events) == 1


class TestLiveDashboardLifecycle:
    """Lifecycle management."""

    def test_close(self) -> None:
        """close() cleans up resources."""
        dashboard = LiveDashboard()
        dashboard.close()
        # Should not raise


class TestLiveDashboardNavigation:
    """Navigation controls."""

    def test_step_forward_without_timeline(self) -> None:
        """step_forward() works without timeline."""
        dashboard = LiveDashboard()
        dashboard._state.current_tick = 5

        result = dashboard.step_forward()
        assert result == 5  # No change without timeline

    def test_step_backward_without_timeline(self) -> None:
        """step_backward() works without timeline."""
        dashboard = LiveDashboard()
        dashboard._state.current_tick = 5

        result = dashboard.step_backward()
        assert result == 5  # No change without timeline

    def test_step_with_timeline(self) -> None:
        """step_forward/backward work with timeline."""
        from agents.town.timeline_widget import TimelineWidget
        from agents.town.trace_bridge import TownTrace

        trace = TownTrace()
        # Add some events
        for i in range(10):
            event = MockTownEvent(
                phase=MockPhase("MORNING"),
                operation="test",
                participants=["alice"],
            )
            trace.append(event)  # type: ignore[arg-type]

        timeline = TimelineWidget(trace=trace)
        dashboard = LiveDashboard(timeline=timeline)

        result = dashboard.step_forward()
        assert result == 1

        result = dashboard.step_forward()
        assert result == 2

        result = dashboard.step_backward()
        assert result == 1
