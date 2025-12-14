"""
Mixins for DashboardApp decomposition.

This module provides focused mixins that decompose the ~937 LOC
DashboardApp into composable, testable units:

- DashboardNavigationMixin: Navigation actions and screen transitions
- DashboardScreensMixin: Screen factory methods
- DashboardHelpMixin: Help and documentation overlays

Philosophy: Mixins separate concerns by axis of change.
Navigation changes independently of screen creation,
which changes independently of help content.

Usage:
    class DashboardApp(
        App,
        DashboardNavigationMixin,
        DashboardScreensMixin,
        DashboardHelpMixin,
    ):
        def __init__(self, ...):
            super().__init__()
            self._nav_controller = NavigationController(...)
            self._state_manager = StateManager()
            # ... rest of setup
"""

from .help import DashboardHelpMixin
from .navigation import DashboardNavigationMixin
from .screens import DashboardScreensMixin

__all__ = [
    "DashboardNavigationMixin",
    "DashboardScreensMixin",
    "DashboardHelpMixin",
]
