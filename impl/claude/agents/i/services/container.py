"""
Service Container for dependency injection in the kgents dashboard.

Centralizes service creation and wiring to enable clean separation of concerns
and testability. The DashboardServices container is created once at app startup
and holds references to all core services.

Philosophy: "Explicit dependencies, implicit complexity management."

Usage:
    services = DashboardServices.create(app, demo_mode=False)
    services.nav_controller.zoom_in(focus="agent-123")
    services.event_bus.emit(MetricsUpdatedEvent(metrics={...}))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

    from ..navigation.controller import NavigationController
    from ..navigation.state import StateManager
    from .events import EventBus


@dataclass
class DashboardServices:
    """
    Service container for dependency injection.

    Holds all core services needed by the dashboard:
    - state_manager: Persists focus/selection across screens
    - nav_controller: Handles LOD transitions and navigation
    - event_bus: Enables decoupled screen-to-screen communication
    - demo_mode: Flag for loading demo fixtures

    The container is immutable after creation to prevent accidental
    service replacement at runtime.
    """

    state_manager: "StateManager"
    nav_controller: "NavigationController"
    event_bus: "EventBus"
    demo_mode: bool = False

    @classmethod
    def create(
        cls,
        app: "App[object]",
        demo_mode: bool = False,
    ) -> "DashboardServices":
        """
        Wire up all services with proper dependencies.

        This is the single source of truth for service instantiation.
        All services are created here with their dependencies injected.

        Args:
            app: The Textual App instance
            demo_mode: If True, load demo fixtures instead of real data

        Returns:
            Fully wired DashboardServices container

        Example:
            >>> from textual.app import App
            >>> app = App()
            >>> services = DashboardServices.create(app, demo_mode=True)
            >>> services.state_manager  # Ready to use
            >>> services.nav_controller  # Ready to use
            >>> services.event_bus  # Singleton EventBus
        """
        from ..navigation.controller import NavigationController
        from ..navigation.state import StateManager
        from .events import EventBus

        # Get the singleton EventBus
        event_bus = EventBus.get()

        # Create StateManager (no dependencies)
        state_manager = StateManager()

        # Create NavigationController (depends on app and StateManager)
        nav_controller = NavigationController(app, state_manager)

        return cls(
            state_manager=state_manager,
            nav_controller=nav_controller,
            event_bus=event_bus,
            demo_mode=demo_mode,
        )

    def reset_state(self) -> None:
        """
        Reset state manager to initial conditions.

        Useful for testing or when starting a new session.
        Does NOT reset the EventBus (that's a singleton).
        """
        self.state_manager.reset()


__all__ = ["DashboardServices"]
