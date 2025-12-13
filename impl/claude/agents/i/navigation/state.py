"""
StateManager - Persist focus and selection state across screen transitions.

The StateManager ensures that when you navigate between screens (e.g., zooming
from Observatory to Cockpit and back), the system remembers which garden,
agent, or turn you were focused on.

Philosophy: "The system has working memory, not just reactive responses."
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class StateManager:
    """
    Manages persistent state across screen transitions.

    Tracks:
    - Screen focus (which item is selected in each screen)
    - Selection state (which items are selected for batch operations)
    - Navigation history (breadcrumb trail)

    Usage:
        state_mgr = StateManager()
        state_mgr.save_focus("observatory", "garden-123")
        focus = state_mgr.get_focus("observatory")  # → "garden-123"
    """

    def __init__(self) -> None:
        """Initialize the StateManager."""
        self._focus: dict[str, str] = {}
        self._selection: dict[str, list[str]] = {}
        self._history: list[tuple[str, str | None]] = []

    def save_focus(self, screen: str, focus: str) -> None:
        """
        Save the current focus for a screen.

        Args:
            screen: Screen name (e.g., "observatory", "cockpit")
            focus: Focus identifier (e.g., garden ID, agent ID, turn ID)
        """
        self._focus[screen] = focus

    def get_focus(self, screen: str) -> str | None:
        """
        Get the saved focus for a screen.

        Args:
            screen: Screen name

        Returns:
            Focus identifier or None if not set
        """
        return self._focus.get(screen)

    def clear_focus(self, screen: str) -> None:
        """
        Clear the focus for a screen.

        Args:
            screen: Screen name
        """
        self._focus.pop(screen, None)

    def save_selection(self, screen: str, items: list[str]) -> None:
        """
        Save the current selection for a screen.

        Args:
            screen: Screen name
            items: List of selected item identifiers
        """
        self._selection[screen] = items.copy()

    def get_selection(self, screen: str) -> list[str]:
        """
        Get the saved selection for a screen.

        Args:
            screen: Screen name

        Returns:
            List of selected item identifiers (empty if none)
        """
        return self._selection.get(screen, []).copy()

    def clear_selection(self, screen: str) -> None:
        """
        Clear the selection for a screen.

        Args:
            screen: Screen name
        """
        self._selection.pop(screen, None)

    def push_history(self, screen: str, focus: str | None = None) -> None:
        """
        Push a navigation to the history stack.

        Args:
            screen: Screen name
            focus: Optional focus identifier
        """
        self._history.append((screen, focus))

    def pop_history(self) -> tuple[str, str | None] | None:
        """
        Pop the last navigation from the history stack.

        Returns:
            Tuple of (screen, focus) or None if empty
        """
        if self._history:
            return self._history.pop()
        return None

    def get_history(self) -> list[tuple[str, str | None]]:
        """
        Get the full navigation history.

        Returns:
            List of (screen, focus) tuples
        """
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear the navigation history."""
        self._history.clear()

    def reset(self) -> None:
        """Reset all state to initial conditions."""
        self._focus.clear()
        self._selection.clear()
        self._history.clear()


__all__ = ["StateManager"]
