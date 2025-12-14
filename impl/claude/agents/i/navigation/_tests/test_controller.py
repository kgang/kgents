"""Tests for NavigationController."""

from typing import Callable
from unittest.mock import MagicMock

import pytest

from ..controller import NavigationController
from ..state import StateManager


class MockApp:
    """Mock Textual App for testing."""

    def __init__(self) -> None:
        self.screens_pushed: list[str] = []
        self.screens_popped: int = 0

    def push_screen(self, screen: str) -> None:
        """Mock push_screen."""
        self.screens_pushed.append(screen)

    def pop_screen(self) -> None:
        """Mock pop_screen."""
        self.screens_popped += 1


class TestNavigationController:
    """Test suite for NavigationController."""

    def test_initialization(self) -> None:
        """Test controller initialization."""
        app = MockApp()
        state = StateManager()

        nav = NavigationController(app, state)  # type: ignore

        assert nav.get_current_lod() == 0
        assert nav.get_screen_stack() == []

    def test_register_lod_screen(self) -> None:
        """Test registering LOD screens."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register a screen factory
        called = False

        def factory() -> None:
            nonlocal called
            called = True

        nav.register_lod_screen(1, factory)

        # Navigate to it
        nav.go_to_lod(1)

        assert called

    def test_go_to_lod(self) -> None:
        """Test navigating to a specific LOD."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register factories
        nav.register_lod_screen(-1, lambda: None)
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)

        # Navigate to LOD 1
        nav.go_to_lod(1)

        assert nav.get_current_lod() == 1

    @pytest.mark.asyncio
    async def test_zoom_in(self) -> None:
        """Test zooming in to next lower LOD."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register factories
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)
        nav.register_lod_screen(2, lambda: None)

        # Start at LOD 0
        nav.go_to_lod(0)
        assert nav.get_current_lod() == 0

        # Zoom in to LOD 1
        await nav.zoom_in()
        assert nav.get_current_lod() == 1

        # Zoom in to LOD 2
        await nav.zoom_in()
        assert nav.get_current_lod() == 2

        # Can't zoom in further
        await nav.zoom_in()
        assert nav.get_current_lod() == 2

    @pytest.mark.asyncio
    async def test_zoom_out(self) -> None:
        """Test zooming out to next higher LOD."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register factories
        nav.register_lod_screen(-1, lambda: None)
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)

        # Start at LOD 1
        nav.go_to_lod(1)
        assert nav.get_current_lod() == 1

        # Zoom out to LOD 0
        await nav.zoom_out()
        assert nav.get_current_lod() == 0

        # Zoom out to LOD -1
        await nav.zoom_out()
        assert nav.get_current_lod() == -1

        # Can't zoom out further
        await nav.zoom_out()
        assert nav.get_current_lod() == -1

    @pytest.mark.asyncio
    async def test_zoom_in_saves_focus(self) -> None:
        """Test that zoom_in saves focus to state manager."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register factories
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)

        # Start at LOD 0
        nav.go_to_lod(0)

        # Zoom in with focus
        await nav.zoom_in(focus="agent-123")

        # Check that focus was saved
        # LOD 0 maps to "terrarium" not "dashboard"
        focus = state.get_focus("terrarium")
        assert focus == "agent-123"

    @pytest.mark.asyncio
    async def test_zoom_in_pushes_history(self) -> None:
        """Test that zoom_in pushes to navigation history."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register factories
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)

        # Start at LOD 0
        nav.go_to_lod(0)

        # Zoom in
        await nav.zoom_in(focus="agent-123")

        # Check history
        history = state.get_history()
        assert len(history) == 1
        assert history[0] == ("terrarium", "agent-123")

    def test_register_debugger(self) -> None:
        """Test registering Debugger screen."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        called_with = None

        def factory(turn_id: str | None = None) -> None:
            nonlocal called_with
            called_with = turn_id

        nav.register_debugger(factory)
        nav.go_to_debugger(turn_id="turn-123")

        assert called_with == "turn-123"

    def test_go_to_debugger_adds_to_stack(self) -> None:
        """Test that go_to_debugger adds to screen stack."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        nav.register_debugger(lambda turn_id: None)  # type: ignore[arg-type,return-value]
        nav.go_to_debugger()

        stack = nav.get_screen_stack()
        assert "debugger" in stack

    @pytest.mark.asyncio
    async def test_back_pops_screen(self) -> None:
        """Test that back() pops a screen."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Push some screens
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)

        nav.go_to_lod(0)
        await nav.zoom_in()

        # Go back
        nav.back()

        assert app.screens_popped == 1

    def test_back_pops_from_stack(self) -> None:
        """Test that back() removes from screen stack."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Push Debugger
        nav.register_debugger(lambda turn_id: None)  # type: ignore[arg-type,return-value]
        nav.go_to_debugger()

        assert len(nav.get_screen_stack()) == 1

        # Go back
        nav.back()

        assert len(nav.get_screen_stack()) == 0

    def test_lod_to_screen_name_mapping(self) -> None:
        """Test LOD to screen name mapping."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        assert nav._lod_to_screen_name(-1) == "observatory"
        assert nav._lod_to_screen_name(0) == "terrarium"
        assert nav._lod_to_screen_name(1) == "cockpit"
        assert nav._lod_to_screen_name(2) == "debugger"

    def test_screen_name_to_lod_mapping(self) -> None:
        """Test screen name to LOD mapping."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        assert nav._screen_name_to_lod("observatory") == -1
        assert nav._screen_name_to_lod("terrarium") == 0
        assert nav._screen_name_to_lod("dashboard") == 0
        assert nav._screen_name_to_lod("cockpit") == 1
        assert nav._screen_name_to_lod("debugger") == 2

    @pytest.mark.asyncio
    async def test_zoom_in_without_registered_screen(self) -> None:
        """Test that zoom_in gracefully handles unregistered screens."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Start at LOD 0
        nav.register_lod_screen(0, lambda: None)
        nav.go_to_lod(0)

        # Try to zoom in but don't register LOD 1
        # Should not crash
        await nav.zoom_in()

        # LOD should NOT be incremented because go_to_lod returns early
        # when screen is not registered
        assert nav.get_current_lod() == 0

    def test_debugger_without_registration(self) -> None:
        """Test that go_to_debugger gracefully handles no registration."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Should not crash
        nav.go_to_debugger()

        # Nothing should be added to stack
        assert nav.get_screen_stack() == []

    @pytest.mark.asyncio
    async def test_full_navigation_flow(self) -> None:
        """Test a complete navigation flow through multiple LODs."""
        app = MockApp()
        state = StateManager()
        nav = NavigationController(app, state)  # type: ignore

        # Register all screens
        nav.register_lod_screen(-1, lambda: None)
        nav.register_lod_screen(0, lambda: None)
        nav.register_lod_screen(1, lambda: None)
        nav.register_lod_screen(2, lambda: None)

        # Start at LOD 0
        nav.go_to_lod(0)

        # Zoom in to LOD 1 with focus
        await nav.zoom_in(focus="agent-123")
        assert nav.get_current_lod() == 1

        # Zoom in to LOD 2
        await nav.zoom_in()
        assert nav.get_current_lod() == 2

        # Zoom out to LOD 1
        await nav.zoom_out()
        assert nav.get_current_lod() == 1

        # Zoom out to LOD 0
        await nav.zoom_out()
        assert nav.get_current_lod() == 0

        # Check history was built
        history = state.get_history()
        assert len(history) > 0
