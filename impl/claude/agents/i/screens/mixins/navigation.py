"""
Navigation actions for DashboardApp - keybindings and screen transitions.

This mixin extracts all navigation-related actions from DashboardApp,
providing a clean separation between navigation logic and screen creation.

Philosophy: Navigation is about transitions, not about what you're transitioning to.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ...navigation.controller import NavigationController


class DashboardNavigationMixin:
    """Navigation actions - keybindings and screen transitions.

    This mixin handles:
    - Direct screen navigation (go_screen_1 through go_screen_6)
    - Zoom in/out actions
    - Special screen navigation (forge, debugger)
    - Help overlay display

    Expects the implementing class to have:
    - self._nav_controller: NavigationController
    """

    _SCREEN_ORDER: ClassVar[list[str]] = [
        "observatory",  # LOD -1
        "dashboard",  # LOD 0
        "cockpit",  # LOD 1
        "flux",  # LOD 1 (alternative)
        "loom",  # LOD 1 (alternative)
        "mri",  # LOD 1 (alternative)
    ]

    # Navigation controller (must be provided by implementing class)
    _nav_controller: NavigationController

    # ========================================================================
    # Zoom Navigation (LOD-based)
    # ========================================================================

    async def action_zoom_in(self) -> None:
        """Zoom in to next lower LOD (+/=).

        Delegates to NavigationController to handle the LOD transition.
        """
        await self._nav_controller.zoom_in()

    async def action_zoom_out(self) -> None:
        """Zoom out to next higher LOD (-/_).

        Delegates to NavigationController to handle the LOD transition.
        """
        await self._nav_controller.zoom_out()

    # ========================================================================
    # Direct Screen Navigation
    # ========================================================================

    def action_go_screen_1(self) -> None:
        """Navigate to Observatory (LOD -1)."""
        self._navigate_to("observatory")

    def action_go_screen_2(self) -> None:
        """Navigate to Dashboard (LOD 0)."""
        self._navigate_to("dashboard")

    def action_go_screen_3(self) -> None:
        """Navigate to Cockpit (LOD 1)."""
        self._navigate_to("cockpit")

    def action_go_screen_4(self) -> None:
        """Navigate to Flux (LOD 1)."""
        self._navigate_to("flux")

    def action_go_screen_5(self) -> None:
        """Navigate to Loom (LOD 1)."""
        self._navigate_to("loom")

    def action_go_screen_6(self) -> None:
        """Navigate to MRI (LOD 1)."""
        self._navigate_to("mri")

    # ========================================================================
    # Cyclic Navigation
    # ========================================================================

    def action_cycle_next(self) -> None:
        """Cycle to next screen in _SCREEN_ORDER.

        Wraps around from last to first.
        """
        # Get current screen name (would need to be tracked in state)
        # For now, just emit event for next in list
        # This is a placeholder - full implementation would track current screen
        from ...services.events import EventBus, ScreenNavigationEvent

        # Emit event for next screen (simple version)
        EventBus.get().emit(ScreenNavigationEvent(target_screen=self._SCREEN_ORDER[0]))

    def action_cycle_prev(self) -> None:
        """Cycle to previous screen in _SCREEN_ORDER.

        Wraps around from first to last.
        """
        # Get current screen name (would need to be tracked in state)
        # For now, just emit event for prev in list
        # This is a placeholder - full implementation would track current screen
        from ...services.events import EventBus, ScreenNavigationEvent

        # Emit event for previous screen (simple version)
        EventBus.get().emit(ScreenNavigationEvent(target_screen=self._SCREEN_ORDER[-1]))

    # ========================================================================
    # Special Screen Navigation
    # ========================================================================

    def action_open_forge(self) -> None:
        """Open Forge screen (f).

        Forge is a special screen (not LOD-based) for agent composition.
        """
        self._nav_controller.go_to_forge()

    def action_open_debugger(self) -> None:
        """Open Debugger screen (d).

        Debugger is a special screen (not LOD-based) for forensic analysis.
        """
        self._nav_controller.go_to_debugger()

    # ========================================================================
    # Internal Navigation Helper
    # ========================================================================

    def _navigate_to(self, screen_name: str) -> None:
        """Navigate to a screen by name, emitting event.

        Args:
            screen_name: The target screen identifier

        Emits:
            ScreenNavigationEvent with target_screen set
        """
        from ...services.events import EventBus, ScreenNavigationEvent

        EventBus.get().emit(ScreenNavigationEvent(target_screen=screen_name))


__all__ = ["DashboardNavigationMixin"]
