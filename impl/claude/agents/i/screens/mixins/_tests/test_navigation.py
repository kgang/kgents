"""
Tests for DashboardNavigationMixin.

Tests cover:
- Screen order configuration
- Navigation action event emission
- Cycle navigation logic
- Zoom in/out delegation
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from agents.i.screens.mixins.navigation import DashboardNavigationMixin
from agents.i.services.events import EventBus, ScreenNavigationEvent


class MockNavController:
    """Mock NavigationController for testing."""

    def __init__(self) -> None:
        self.zoom_in = AsyncMock()
        self.zoom_out = AsyncMock()
        self.go_to_forge = Mock()
        self.go_to_debugger = Mock()


class MockApp(DashboardNavigationMixin):
    """Mock app that uses the navigation mixin."""

    _nav_controller: Any  # Allow MockNavController

    def __init__(self) -> None:
        self._nav_controller = MockNavController()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def event_bus():
    """Provide a fresh EventBus for each test."""
    EventBus.reset()
    bus = EventBus.get()
    yield bus
    EventBus.reset()


@pytest.fixture
def app():
    """Provide a mock app with navigation mixin."""
    return MockApp()


# =============================================================================
# Screen Order Configuration Tests
# =============================================================================


def test_screen_order_has_all_screens():
    """_SCREEN_ORDER should contain all expected screens."""
    expected_screens = {
        "observatory",  # LOD -1
        "dashboard",  # LOD 0
        "cockpit",  # LOD 1
        "flux",  # LOD 1
        "loom",  # LOD 1
        "mri",  # LOD 1
    }

    assert set(DashboardNavigationMixin._SCREEN_ORDER) == expected_screens


def test_screen_order_is_lod_sorted():
    """_SCREEN_ORDER should be roughly sorted by LOD level."""
    order = DashboardNavigationMixin._SCREEN_ORDER

    # First should be observatory (LOD -1)
    assert order[0] == "observatory"

    # Second should be dashboard (LOD 0)
    assert order[1] == "dashboard"

    # Rest should be LOD 1 screens
    lod1_screens = {"cockpit", "flux", "loom", "mri"}
    assert set(order[2:]) == lod1_screens


# =============================================================================
# Direct Navigation Tests
# =============================================================================


def test_action_go_screen_1_emits_observatory_event(app, event_bus):
    """action_go_screen_1 should emit event for observatory."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_1()

    assert len(events) == 1
    assert events[0].target_screen == "observatory"


def test_action_go_screen_2_emits_dashboard_event(app, event_bus):
    """action_go_screen_2 should emit event for dashboard."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_2()

    assert len(events) == 1
    assert events[0].target_screen == "dashboard"


def test_action_go_screen_3_emits_cockpit_event(app, event_bus):
    """action_go_screen_3 should emit event for cockpit."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_3()

    assert len(events) == 1
    assert events[0].target_screen == "cockpit"


def test_action_go_screen_4_emits_flux_event(app, event_bus):
    """action_go_screen_4 should emit event for flux."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_4()

    assert len(events) == 1
    assert events[0].target_screen == "flux"


def test_action_go_screen_5_emits_loom_event(app, event_bus):
    """action_go_screen_5 should emit event for loom."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_5()

    assert len(events) == 1
    assert events[0].target_screen == "loom"


def test_action_go_screen_6_emits_mri_event(app, event_bus):
    """action_go_screen_6 should emit event for mri."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_go_screen_6()

    assert len(events) == 1
    assert events[0].target_screen == "mri"


# =============================================================================
# Zoom Navigation Tests
# =============================================================================


@pytest.mark.asyncio
async def test_action_zoom_in_delegates_to_controller(app):
    """action_zoom_in should delegate to NavigationController."""
    await app.action_zoom_in()

    app._nav_controller.zoom_in.assert_called_once()


@pytest.mark.asyncio
async def test_action_zoom_out_delegates_to_controller(app):
    """action_zoom_out should delegate to NavigationController."""
    await app.action_zoom_out()

    app._nav_controller.zoom_out.assert_called_once()


# =============================================================================
# Cyclic Navigation Tests
# =============================================================================


def test_action_cycle_next_emits_event(app, event_bus):
    """action_cycle_next should emit navigation event."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_cycle_next()

    assert len(events) == 1
    assert isinstance(events[0], ScreenNavigationEvent)
    # Should emit first screen (placeholder implementation)
    assert events[0].target_screen == "observatory"


def test_action_cycle_prev_emits_event(app, event_bus):
    """action_cycle_prev should emit navigation event."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app.action_cycle_prev()

    assert len(events) == 1
    assert isinstance(events[0], ScreenNavigationEvent)
    # Should emit last screen (placeholder implementation)
    assert events[0].target_screen == "mri"


# =============================================================================
# Special Screen Navigation Tests
# =============================================================================


def test_action_open_forge_delegates_to_controller(app):
    """action_open_forge should delegate to NavigationController."""
    app.action_open_forge()

    app._nav_controller.go_to_forge.assert_called_once()


def test_action_open_debugger_delegates_to_controller(app):
    """action_open_debugger should delegate to NavigationController."""
    app.action_open_debugger()

    app._nav_controller.go_to_debugger.assert_called_once()


# =============================================================================
# Internal Helper Tests
# =============================================================================


def test_navigate_to_emits_correct_event(app, event_bus):
    """_navigate_to should emit ScreenNavigationEvent with target_screen."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app._navigate_to("custom_screen")

    assert len(events) == 1
    assert events[0].target_screen == "custom_screen"


def test_navigate_to_multiple_calls_emit_multiple_events(app, event_bus):
    """Multiple _navigate_to calls should emit multiple events."""
    events: list[ScreenNavigationEvent] = []
    event_bus.subscribe(ScreenNavigationEvent, events.append)

    app._navigate_to("screen1")
    app._navigate_to("screen2")
    app._navigate_to("screen3")

    assert len(events) == 3
    assert events[0].target_screen == "screen1"
    assert events[1].target_screen == "screen2"
    assert events[2].target_screen == "screen3"


# =============================================================================
# Event Isolation Tests
# =============================================================================


def test_navigation_events_do_not_interfere_with_other_event_types(app, event_bus):
    """Navigation events should not trigger non-navigation handlers."""
    from agents.i.services.events import AgentFocusedEvent

    nav_events: list[ScreenNavigationEvent] = []
    focus_events: list[ScreenNavigationEvent] = []

    event_bus.subscribe(ScreenNavigationEvent, nav_events.append)
    event_bus.subscribe(AgentFocusedEvent, focus_events.append)

    app.action_go_screen_1()

    assert len(nav_events) == 1
    assert len(focus_events) == 0  # Should not be triggered


# =============================================================================
# Regression Tests
# =============================================================================


def test_all_action_methods_exist():
    """All action_go_screen_* methods should exist."""
    mixin = DashboardNavigationMixin

    assert hasattr(mixin, "action_go_screen_1")
    assert hasattr(mixin, "action_go_screen_2")
    assert hasattr(mixin, "action_go_screen_3")
    assert hasattr(mixin, "action_go_screen_4")
    assert hasattr(mixin, "action_go_screen_5")
    assert hasattr(mixin, "action_go_screen_6")


def test_all_zoom_methods_exist():
    """Zoom action methods should exist."""
    mixin = DashboardNavigationMixin

    assert hasattr(mixin, "action_zoom_in")
    assert hasattr(mixin, "action_zoom_out")


def test_all_special_navigation_methods_exist():
    """Special navigation methods should exist."""
    mixin = DashboardNavigationMixin

    assert hasattr(mixin, "action_open_forge")
    assert hasattr(mixin, "action_open_debugger")
