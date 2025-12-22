"""
Dawn Cockpit Garden View: Bottom status bar.

The garden view shows what "grew overnight" — recent events
and status messages from the Dawn cockpit.

Layout:
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  GARDEN (what grew overnight)                                               │
    │  • 3 files changed → Portal Phase 5 completion                              │
    │  • Witness: 5 marks from yesterday                                          │
    └─────────────────────────────────────────────────────────────────────────────┘

The garden is intentionally minimal — a status bar, not a dashboard.

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any

from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

# Maximum events to display
MAX_EVENTS = 3


class GardenEvent(Message):
    """Message for garden status updates (message bus pattern)."""

    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()


class GardenView(Widget):
    """
    Simple status bar showing recent events.

    No reactive magic - just add_event() and immediate render.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._event_history: deque[tuple[datetime, str]] = deque(maxlen=50)

    def compose(self) -> Any:
        """Compose the garden view."""
        yield Static("🌱 GARDEN", id="garden-title", classes="pane-title")
        yield Static(id="garden-content")

    def on_mount(self) -> None:
        """Show initial state."""
        self._update_display()

    def add_event(self, text: str) -> None:
        """Add event and render immediately."""
        self._event_history.append((datetime.now(), text))
        self._update_display()

    def clear(self) -> None:
        """Clear all events."""
        self._event_history.clear()
        self._update_display()

    def _update_display(self) -> None:
        """Render events to display."""
        try:
            content = self.query_one("#garden-content", Static)
        except Exception:
            return

        if not self._event_history:
            content.update("[dim]No events yet.[/dim]")
            return

        lines = []
        for ts, text in list(self._event_history)[-MAX_EVENTS:]:
            lines.append(f"[dim]{ts.strftime('%H:%M')}[/dim] • {text}")

        content.update("\n".join(lines))

    @property
    def events(self) -> tuple[str, ...]:
        """Get displayed event texts (limited to MAX_EVENTS)."""
        return tuple(text for _, text in list(self._event_history)[-MAX_EVENTS:])


__all__ = ["GardenEvent", "GardenView"]
