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

Events shown:
    - Recent git activity (files changed, commits)
    - Witness marks from yesterday
    - Focus hygiene results
    - System status messages

The garden is intentionally minimal — a status bar, not a dashboard.

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any

from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

logger = logging.getLogger(__name__)


class GardenEventType(Enum):
    """Categories of garden events for optional filtering."""

    INFO = "info"  # General information
    SUCCESS = "success"  # Completed actions
    WARNING = "warning"  # Attention needed
    SYSTEM = "system"  # System status


class GardenEvent(Message):
    """
    Message bus event for the Garden status bar.

    Post this message from any widget to add an event to the Garden.
    Events bubble up to the app and are handled by DawnCockpit.on_garden_event.

    Usage:
        self.post_message(GardenEvent("Something happened"))
        self.post_message(GardenEvent("Error!", event_type=GardenEventType.WARNING))

    Teaching:
        gotcha: Use bubble=True so events from nested widgets reach DawnCockpit.
                DawnCockpit.on_garden_event handler forwards to GardenView.add_event().
                (Evidence: Textual message passing pattern)

        gotcha: bubble must be a class attribute, not a class argument!
                `class Foo(Message, bubble=True)` does NOT work.
                `class Foo(Message): bubble = True` is correct.
    """

    bubble = True  # Must be class attribute, not class argument

    def __init__(
        self,
        text: str,
        event_type: GardenEventType = GardenEventType.INFO,
    ) -> None:
        self.text = text
        self.event_type = event_type
        super().__init__()


# Maximum events to display
MAX_EVENTS = 3


class GardenView(Widget):
    """
    The garden status bar showing recent events.

    Displays the last few events in a compact format.
    Events auto-expire (not shown) but kept in memory for
    potential history view.

    Teaching:
        gotcha: The garden is a status bar, not a dashboard.
                Keep it to 3-4 lines max. Quarter-screen means
                every line counts.
                (Evidence: spec/protocols/dawn-cockpit.md § Visual Design)
    """

    _reactive_events: reactive[tuple[str, ...]] = reactive(())

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._event_history: deque[tuple[datetime, str]] = deque(maxlen=50)
        self._events: tuple[str, ...] = ()  # Non-reactive for testing

    @property
    def events(self) -> tuple[str, ...]:
        """Get events."""
        return self._events

    @events.setter
    def events(self, value: tuple[str, ...]) -> None:
        """Set events and update reactive."""
        self._events = value
        # Only update reactive if we're in a running app
        try:
            self._reactive_events = value
        except Exception:
            pass  # Not in app context

    def compose(self) -> Any:
        """Compose the garden view."""
        yield Static("GARDEN (what grew overnight)", classes="pane-title")
        yield Static(id="events-container")

    def on_mount(self) -> None:
        """Initialize with default message."""
        self._render_events()

    def add_event(self, event: str) -> None:
        """
        Add an event to the garden.

        Events are timestamped and kept in history.
        Only the most recent MAX_EVENTS are displayed.
        """
        now = datetime.now()
        self._event_history.append((now, event))

        # Update reactive events tuple
        recent = list(self._event_history)[-MAX_EVENTS:]
        self.events = tuple(e[1] for e in recent)

    def watch__reactive_events(self, events: tuple[str, ...]) -> None:
        """Update display when events change."""
        self._render_events()

    def _render_events(self) -> None:
        """Render events to the container."""
        container = self.query_one("#events-container", Static)

        if not self._event_history:
            container.update("[dim]No events yet. The garden awaits.[/dim]")
            return

        lines = []
        recent = list(self._event_history)[-MAX_EVENTS:]

        for timestamp, event in recent:
            time_str = timestamp.strftime("%H:%M")
            lines.append(f"[dim]{time_str}[/dim] • {event}")

        container.update("\n".join(lines))

    def clear(self) -> None:
        """Clear all events."""
        self._event_history.clear()
        self.events = ()


__all__ = [
    "GardenEvent",
    "GardenEventType",
    "GardenView",
]
