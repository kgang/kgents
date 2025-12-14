"""
NavigationController - Handle screen transitions with zoom semantics.

The NavigationController orchestrates the Level-of-Detail (LOD) system,
enabling smooth transitions between different views:

LOD -1: Observatory (ecosystem view)
LOD  0: Terrarium (garden view)
LOD  1: Cockpit (single agent)
LOD  2: Debugger (forensic/turn analysis)

Special screens:
- Debugger: Turn analysis (accessible from any LOD)

Philosophy: "Zooming is semantic, not just visual."
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable

from .state import StateManager

if TYPE_CHECKING:
    from textual.app import App


class NavigationController:
    """
    Controls screen transitions with zoom in/out semantics.

    The controller manages:
    - LOD transitions (zoom in/out)
    - Special screen navigation (Debugger)
    - State preservation across transitions
    - Global keybindings

    Usage:
        nav = NavigationController(app, state_manager)
        nav.zoom_in(focus="agent-123")  # Zoom to next lower LOD
        nav.zoom_out()  # Zoom to next higher LOD
        nav.go_to_lod(1)  # Jump directly to Cockpit
    """

    def __init__(
        self,
        app: "App[object]",
        state_manager: StateManager,
        animation_duration_ms: int = 150,
    ) -> None:
        """
        Initialize the NavigationController.

        Args:
            app: Textual application instance
            state_manager: State manager for persistence
            animation_duration_ms: Duration for zoom animations (default 150ms)
        """
        self.app = app
        self.state = state_manager
        self._current_lod = 0  # Start at Terrarium/Dashboard
        self._screen_stack: list[str] = []
        self._animation_duration = animation_duration_ms / 1000.0  # Convert to seconds

        # Screen registry: maps LOD → screen factory
        self._lod_screens: dict[int, Callable[[], None]] = {}

        # Special screen factories
        self._debugger_factory: Callable[[str | None], None] | None = None

        # Animation state
        self._animating = False

    def register_lod_screen(self, lod: int, factory: Callable[[], None]) -> None:
        """
        Register a screen factory for a specific LOD.

        Args:
            lod: LOD level (-1, 0, 1, 2)
            factory: Callable that pushes the screen onto app
        """
        self._lod_screens[lod] = factory

    def register_debugger(self, factory: Callable[[str | None], None]) -> None:
        """
        Register the Debugger screen factory.

        Args:
            factory: Callable that pushes the Debugger screen
        """
        self._debugger_factory = factory

    async def zoom_in(self, focus: str | None = None) -> None:
        """
        Zoom in to the next lower LOD (more detail).

        Args:
            focus: Optional focus identifier (garden ID, agent ID, etc.)

        Example:
            From Observatory (LOD -1) → Terrarium (LOD 0)
            From Terrarium (LOD 0) → Cockpit (LOD 1)
            From Cockpit (LOD 1) → Debugger (LOD 2)
        """
        # Prevent concurrent animations
        if self._animating:
            return

        # Calculate target LOD
        target_lod = self._current_lod + 1

        # Clamp to valid range
        if target_lod > 2:
            # Can't zoom in further than Debugger
            return

        # Save current focus before transitioning
        current_screen = self._lod_to_screen_name(self._current_lod)
        if focus:
            self.state.save_focus(current_screen, focus)

        # Push navigation to history
        self.state.push_history(current_screen, focus)

        # Transition to target LOD with animation
        await self._animate_zoom_in(target_lod)

    async def zoom_out(self) -> None:
        """
        Zoom out to the next higher LOD (broader view).

        Example:
            From Debugger (LOD 2) → Cockpit (LOD 1)
            From Cockpit (LOD 1) → Terrarium (LOD 0)
            From Terrarium (LOD 0) → Observatory (LOD -1)
        """
        # Prevent concurrent animations
        if self._animating:
            return

        # Calculate target LOD
        target_lod = self._current_lod - 1

        # Clamp to valid range
        if target_lod < -1:
            # Can't zoom out further than Observatory
            return

        # Pop from screen stack if present
        if self._screen_stack:
            self._screen_stack.pop()

        # Transition to target LOD with animation
        await self._animate_zoom_out(target_lod)

    def go_to_lod(self, lod: int) -> None:
        """
        Jump directly to a specific LOD.

        Args:
            lod: Target LOD level (-1, 0, 1, 2)
        """
        if lod not in self._lod_screens:
            # Screen not registered yet
            return

        # Update current LOD
        self._current_lod = lod

        # Push screen
        factory = self._lod_screens[lod]
        factory()

        # Update screen stack
        screen_name = self._lod_to_screen_name(lod)
        self._screen_stack.append(screen_name)

    def go_to_debugger(self, turn_id: str | None = None) -> None:
        """
        Navigate to the Debugger screen.

        Args:
            turn_id: Optional turn ID to focus on
        """
        if not self._debugger_factory:
            return

        # Save current screen to state
        current_screen = self._lod_to_screen_name(self._current_lod)
        self.state.push_history(current_screen)

        # Push Debugger screen
        self._debugger_factory(turn_id)
        self._screen_stack.append("debugger")

    def back(self) -> None:
        """
        Go back to the previous screen.

        Uses the navigation history to restore the previous screen.
        """
        # Pop from screen stack
        if self._screen_stack:
            self._screen_stack.pop()

        # Pop from history
        prev = self.state.pop_history()
        if prev:
            screen_name, focus = prev

            # Restore LOD if applicable
            if screen_name in ["observatory", "terrarium", "cockpit", "debugger"]:
                lod = self._screen_name_to_lod(screen_name)
                self._current_lod = lod

            # Pop the current screen
            self.app.pop_screen()

    def get_current_lod(self) -> int:
        """
        Get the current LOD level.

        Returns:
            Current LOD level
        """
        return self._current_lod

    def get_screen_stack(self) -> list[str]:
        """
        Get the current screen stack.

        Returns:
            List of screen names in navigation order
        """
        return self._screen_stack.copy()

    # ========================================================================
    # Internal Helpers
    # ========================================================================

    def _lod_to_screen_name(self, lod: int) -> str:
        """Map LOD to screen name."""
        mapping = {
            -1: "observatory",
            0: "terrarium",  # or "dashboard"
            1: "cockpit",
            2: "debugger",
        }
        return mapping.get(lod, "unknown")

    def _screen_name_to_lod(self, screen: str) -> int:
        """Map screen name to LOD."""
        mapping = {
            "observatory": -1,
            "terrarium": 0,
            "dashboard": 0,
            "cockpit": 1,
            "debugger": 2,
        }
        return mapping.get(screen, 0)

    # ========================================================================
    # Animation Methods
    # ========================================================================

    async def _animate_zoom_in(self, target_lod: int) -> None:
        """
        Animate zoom in transition.

        Creates a smooth transition by:
        1. Fading out current screen
        2. Pushing new screen
        3. Fading in new screen

        Args:
            target_lod: Target LOD to zoom into
        """
        self._animating = True

        try:
            # Brief fade-out delay (simulates zoom preparation)
            await asyncio.sleep(self._animation_duration * 0.3)

            # Push the new screen
            self.go_to_lod(target_lod)

            # Brief fade-in delay (simulates zoom completion)
            await asyncio.sleep(self._animation_duration * 0.7)

        finally:
            self._animating = False

    async def _animate_zoom_out(self, target_lod: int) -> None:
        """
        Animate zoom out transition.

        Creates a smooth transition by:
        1. Fading out current screen
        2. Pushing new screen
        3. Fading in new screen

        Args:
            target_lod: Target LOD to zoom out to
        """
        self._animating = True

        try:
            # Brief fade-out delay
            await asyncio.sleep(self._animation_duration * 0.3)

            # Push the new screen
            self.go_to_lod(target_lod)

            # Brief fade-in delay
            await asyncio.sleep(self._animation_duration * 0.7)

        finally:
            self._animating = False


__all__ = ["NavigationController"]
