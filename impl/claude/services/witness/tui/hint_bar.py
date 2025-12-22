"""
HintBar: Context-aware keybinding hints at the bottom.

Pattern 12 from ZenPortal: Context-Aware Hint Bar
"Bottom status line that changes based on context."

See: docs/skills/zenportal-patterns.md
"""

from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.widget import Widget


class HintBar(Widget):
    """
    Context-aware hint bar showing available actions.

    Displays keybinding hints at the bottom of the screen.
    Can be updated dynamically based on current mode/context.

    Example:
        j/k: navigate  Enter: copy  0-3: filter level  q: quit
    """

    DEFAULT_HINTS = "j/k: navigate  Enter: copy  0-3: filter level  a: all  r: refresh  q: quit"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the hint bar."""
        super().__init__(**kwargs)
        self._hints = self.DEFAULT_HINTS

    def set_hints(self, hints: str) -> None:
        """Update the hints displayed."""
        self._hints = hints
        self.refresh()

    def set_mode(self, mode: str) -> None:
        """
        Set hints based on mode.

        Predefined modes for common contexts.
        """
        mode_hints = {
            "normal": self.DEFAULT_HINTS,
            "filter": "0: SESSION  1: DAY  2: WEEK  3: EPOCH  a: All  Esc: cancel",
            "copy": "Enter: confirm copy  Esc: cancel",
            "search": "Type to search...  Enter: select  Esc: cancel",
        }
        self._hints = mode_hints.get(mode, self.DEFAULT_HINTS)
        self.refresh()

    def render(self) -> Text:
        """Render the hint bar."""
        # Parse hints to add styling to key indicators
        result = Text()
        parts = self._hints.split("  ")

        for i, part in enumerate(parts):
            if i > 0:
                result.append("  ", style="dim")

            if ":" in part:
                key, desc = part.split(":", 1)
                result.append(key, style="bold cyan")
                result.append(":", style="dim")
                result.append(desc, style="dim")
            else:
                result.append(part, style="dim")

        return result


__all__ = [
    "HintBar",
]
