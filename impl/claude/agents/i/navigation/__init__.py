"""
Navigation layer for unified dashboard screen management.

This module provides:
- StateManager: Persist focus and selection state across screen transitions
- NavigationController: Handle screen transitions with zoom in/out semantics
- ReplayController: Animated playback of Turn DAG for debugging

Track D of Dashboard Overhaul.
"""

from .controller import NavigationController
from .replay import (
    PlaybackState,
    ReplayController,
    ReplayStats,
    Turn,
    TurnHighlightEvent,
    create_demo_turns,
)
from .state import StateManager

__all__ = [
    "NavigationController",
    "StateManager",
    "ReplayController",
    "Turn",
    "TurnHighlightEvent",
    "ReplayStats",
    "PlaybackState",
    "create_demo_turns",
]
