"""
Tests for CockpitScreen - LOD Level 1 (SURFACE).

Tests verify:
- Initialization and demo mode
- Temperature control
- Widget composition
- Navigation actions
- Data updates
"""

from __future__ import annotations

from datetime import datetime

import pytest
from agents.i.data.core_types import Phase
from agents.i.data.state import AgentSnapshot
from agents.i.screens.cockpit import (
    CockpitScreen,
    SemaphoreDisplay,
    ThoughtsStream,
    create_demo_snapshot,
)


class TestCreateDemoSnapshot:
    """Tests for demo snapshot creation."""

    def test_creates_valid_snapshot(self) -> None:
        """Demo snapshot should be valid."""
        snapshot = create_demo_snapshot()
        assert snapshot is not None
        assert snapshot.id != ""
        assert snapshot.name != ""

    def test_has_activity(self) -> None:
        """Demo snapshot should have activity level."""
        snapshot = create_demo_snapshot()
        assert 0.0 <= snapshot.activity <= 1.0

    def test_has_phase(self) -> None:
        """Demo snapshot should have a phase."""
        snapshot = create_demo_snapshot()
        assert isinstance(snapshot.phase, Phase)


class TestSemaphoreDisplay:
    """Tests for SemaphoreDisplay widget."""

    def test_empty_semaphores(self) -> None:
        """Empty list shows no active semaphores."""
        display = SemaphoreDisplay(semaphores=[])
        result = display.render()
        assert "No active semaphores" in result

    def test_active_semaphore(self) -> None:
        """Active semaphore shows bullet."""
        display = SemaphoreDisplay(
            semaphores=[{"name": "test.process", "status": "active"}]
        )
        result = display.render()
        assert "test.process" in result
        assert "●" in result

    def test_waiting_semaphore(self) -> None:
        """Waiting semaphore shows empty circle."""
        display = SemaphoreDisplay(
            semaphores=[{"name": "test.process", "status": "waiting"}]
        )
        result = display.render()
        assert "test.process" in result
        assert "○" in result

    def test_idle_semaphore(self) -> None:
        """Idle semaphore shows dashed circle."""
        display = SemaphoreDisplay(
            semaphores=[{"name": "test.process", "status": "idle"}]
        )
        result = display.render()
        assert "test.process" in result
        assert "◌" in result

    def test_multiple_semaphores(self) -> None:
        """Multiple semaphores rendered on separate lines."""
        display = SemaphoreDisplay(
            semaphores=[
                {"name": "process1", "status": "active"},
                {"name": "process2", "status": "waiting"},
            ]
        )
        result = display.render()
        assert "process1" in result
        assert "process2" in result


class TestThoughtsStream:
    """Tests for ThoughtsStream widget."""

    def test_empty_thoughts(self) -> None:
        """Empty list shows no recent thoughts."""
        stream = ThoughtsStream(thoughts=[])
        result = stream.render()
        assert "No recent thoughts" in result

    def test_single_thought(self) -> None:
        """Single thought is rendered."""
        stream = ThoughtsStream(
            thoughts=[{"time": "12:00:00", "content": "Test thought"}]
        )
        result = stream.render()
        assert "12:00:00" in result
        assert "Test thought" in result

    def test_multiple_thoughts(self) -> None:
        """Multiple thoughts rendered in order."""
        stream = ThoughtsStream(
            thoughts=[
                {"time": "12:00:01", "content": "First"},
                {"time": "12:00:00", "content": "Second"},
            ]
        )
        result = stream.render()
        assert "First" in result
        assert "Second" in result

    def test_limits_to_five(self) -> None:
        """Only shows last 5 thoughts."""
        thoughts = [
            {"time": f"12:00:{i:02d}", "content": f"Thought {i}"} for i in range(10)
        ]
        stream = ThoughtsStream(thoughts=thoughts)
        result = stream.render()
        # Only first 5 should be rendered
        assert result.count("Thought") == 5

    def test_truncates_long_content(self) -> None:
        """Long content is truncated at 50 chars."""
        long_content = "A" * 100
        stream = ThoughtsStream(
            thoughts=[{"time": "12:00:00", "content": long_content}]
        )
        result = stream.render()
        # Should be truncated
        assert len(result.split("\n")[0]) < 100


class TestCockpitScreenInit:
    """Tests for CockpitScreen initialization."""

    def test_default_init(self) -> None:
        """Default initialization creates empty screen."""
        screen = CockpitScreen()
        assert screen.agent_snapshot is None
        assert screen.agent_id == ""
        assert screen.agent_name == ""
        assert screen._demo_mode is False

    def test_demo_mode_creates_snapshot(self) -> None:
        """Demo mode creates demo snapshot."""
        screen = CockpitScreen(demo_mode=True)
        assert screen._demo_mode is True
        assert screen.agent_snapshot is not None
        assert screen._semaphores != []
        assert screen._thoughts != []
        assert screen._activity_history != []

    def test_with_snapshot(self) -> None:
        """Initialization with snapshot uses provided data."""
        snapshot = AgentSnapshot(
            id="test-agent",
            name="Test Agent",
            phase=Phase.ACTIVE,
            activity=0.5,
            summary="Test summary",
            grid_x=0,
            grid_y=0,
            children=[],
            connections={},
        )
        screen = CockpitScreen(agent_snapshot=snapshot)
        assert screen.agent_snapshot == snapshot
        assert screen.agent_id == "test-agent"
        assert screen.agent_name == "Test Agent"

    def test_with_explicit_id_and_name(self) -> None:
        """Explicit ID and name override snapshot values."""
        snapshot = AgentSnapshot(
            id="snapshot-id",
            name="Snapshot Name",
            phase=Phase.ACTIVE,
            activity=0.5,
            summary="Test",
            grid_x=0,
            grid_y=0,
            children=[],
            connections={},
        )
        screen = CockpitScreen(
            agent_snapshot=snapshot,
            agent_id="explicit-id",
            agent_name="Explicit Name",
        )
        assert screen.agent_id == "explicit-id"
        assert screen.agent_name == "Explicit Name"


class TestCockpitScreenTemperature:
    """Tests for temperature control."""

    def test_default_temperature(self) -> None:
        """Default temperature is 0.7."""
        screen = CockpitScreen()
        assert screen.temperature == 0.7

    def test_action_increase_temp(self) -> None:
        """Increase temperature action."""
        screen = CockpitScreen()
        initial = screen.temperature
        screen.action_increase_temp()
        assert screen.temperature == initial + 0.05

    def test_action_decrease_temp(self) -> None:
        """Decrease temperature action."""
        screen = CockpitScreen()
        initial = screen.temperature
        screen.action_decrease_temp()
        assert screen.temperature == initial - 0.05

    def test_temp_clamped_at_max(self) -> None:
        """Temperature clamped at 1.0."""
        screen = CockpitScreen()
        screen.temperature = 0.98
        screen.action_increase_temp()
        assert screen.temperature == 1.0

        screen.action_increase_temp()
        assert screen.temperature == 1.0  # Still clamped

    def test_temp_clamped_at_min(self) -> None:
        """Temperature clamped at 0.0."""
        screen = CockpitScreen()
        screen.temperature = 0.02
        screen.action_decrease_temp()
        assert screen.temperature == 0.0

        screen.action_decrease_temp()
        assert screen.temperature == 0.0  # Still clamped


class TestCockpitScreenUpdates:
    """Tests for data update methods."""

    def test_update_snapshot(self) -> None:
        """update_snapshot updates agent data."""
        screen = CockpitScreen()
        new_snapshot = AgentSnapshot(
            id="new-id",
            name="New Name",
            phase=Phase.VOID,
            activity=0.9,
            summary="Updated",
            grid_x=1,
            grid_y=1,
            children=[],
            connections={},
        )
        screen.update_snapshot(new_snapshot)

        assert screen.agent_snapshot == new_snapshot
        assert screen.agent_id == "new-id"
        assert screen.agent_name == "New Name"

    def test_add_thought(self) -> None:
        """add_thought adds to thoughts stream."""
        screen = CockpitScreen()
        assert len(screen._thoughts) == 0

        screen.add_thought("New thought")
        assert len(screen._thoughts) == 1
        assert screen._thoughts[0]["content"] == "New thought"

    def test_add_thought_limits_to_five(self) -> None:
        """add_thought keeps only last 5."""
        screen = CockpitScreen()
        for i in range(10):
            screen.add_thought(f"Thought {i}")

        assert len(screen._thoughts) == 5
        # Most recent should be first
        assert screen._thoughts[0]["content"] == "Thought 9"

    def test_update_activity_history(self) -> None:
        """update_activity_history adds to history."""
        screen = CockpitScreen()
        initial_len = len(screen._activity_history)

        screen.update_activity_history(0.8)

        assert len(screen._activity_history) == initial_len + 1
        assert screen._activity_history[-1] == 0.8

    def test_activity_history_limits_to_twenty(self) -> None:
        """Activity history keeps only last 20."""
        screen = CockpitScreen()
        for i in range(30):
            screen.update_activity_history(float(i) / 30)

        assert len(screen._activity_history) == 20


class TestCockpitScreenDemoData:
    """Tests for demo mode data generation."""

    def test_demo_semaphores(self) -> None:
        """Demo mode creates semaphores."""
        screen = CockpitScreen(demo_mode=True)
        assert len(screen._semaphores) > 0
        for sem in screen._semaphores:
            assert "name" in sem
            assert "status" in sem

    def test_demo_thoughts(self) -> None:
        """Demo mode creates thoughts."""
        screen = CockpitScreen(demo_mode=True)
        assert len(screen._thoughts) > 0
        for thought in screen._thoughts:
            assert "time" in thought
            assert "content" in thought

    def test_demo_activity_history(self) -> None:
        """Demo mode creates activity history."""
        screen = CockpitScreen(demo_mode=True)
        assert len(screen._activity_history) > 0
        for val in screen._activity_history:
            assert 0.0 <= val <= 1.0


class TestCockpitScreenBindings:
    """Tests for keyboard bindings."""

    def test_has_back_binding(self) -> None:
        """Screen has back binding (Escape)."""
        from textual.binding import Binding

        bindings = {
            b.key: b.action for b in CockpitScreen.BINDINGS if isinstance(b, Binding)
        }
        assert "escape" in bindings
        assert bindings["escape"] == "back"

    def test_has_zoom_bindings(self) -> None:
        """Screen has zoom bindings (+/-)."""
        from textual.binding import Binding

        bindings = {
            b.key: b.action for b in CockpitScreen.BINDINGS if isinstance(b, Binding)
        }
        assert "plus" in bindings
        assert bindings["plus"] == "zoom_in"
        assert "minus" in bindings
        assert bindings["minus"] == "zoom_out"

    def test_has_temp_bindings(self) -> None:
        """Screen has temperature bindings (h/l)."""
        from textual.binding import Binding

        bindings = {
            b.key: b.action for b in CockpitScreen.BINDINGS if isinstance(b, Binding)
        }
        assert "h" in bindings
        assert bindings["h"] == "decrease_temp"
        assert "l" in bindings
        assert bindings["l"] == "increase_temp"

    def test_has_loom_binding(self) -> None:
        """Screen has Loom view binding (t)."""
        from textual.binding import Binding

        bindings = {
            b.key: b.action for b in CockpitScreen.BINDINGS if isinstance(b, Binding)
        }
        assert "t" in bindings
        assert bindings["t"] == "show_loom"


class TestCockpitScreenCss:
    """Tests for CSS styling."""

    def test_has_css(self) -> None:
        """Screen has CSS defined."""
        assert CockpitScreen.CSS is not None
        assert len(CockpitScreen.CSS) > 0

    def test_css_contains_panels(self) -> None:
        """CSS defines panel styles."""
        assert ".panel" in CockpitScreen.CSS

    def test_css_contains_density_panel(self) -> None:
        """CSS defines density panel."""
        assert ".density-panel" in CockpitScreen.CSS

    def test_css_contains_slider_panel(self) -> None:
        """CSS defines slider panel."""
        assert ".slider-panel" in CockpitScreen.CSS
