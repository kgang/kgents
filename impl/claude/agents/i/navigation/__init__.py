"""
Navigation layer for unified dashboard screen management.

This module provides:
- StateManager: Persist focus and selection state across screen transitions
- NavigationController: Handle screen transitions with zoom in/out semantics

Track D of Dashboard Overhaul.
"""

from .controller import NavigationController
from .state import StateManager

__all__ = ["NavigationController", "StateManager"]
