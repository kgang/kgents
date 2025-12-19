"""
Timeline Widget - Horizontal scrollable timeline with state snapshots.

Shows the evolution of system state over time:
- Events as markers on the timeline
- Hover to see state snapshot
- Click to jump to that moment
- Play/pause controls for replay

The timeline IS time.* made visible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import traitlets

from .base import KgentsWidget

# Path to JS file
_JS_DIR = Path(__file__).parent / "js"


class TimelineWidget(KgentsWidget):
    """
    Horizontal timeline with state snapshots.

    Features:
    - Scrollable event markers
    - Color-coded event types
    - Hover preview of state at that moment
    - Playback controls for replay
    - Zoom in/out for detail levels
    """

    _esm = _JS_DIR / "timeline.js"

    # Events: list of dicts with {tick, type, source, message, level}
    events: Any = traitlets.List([]).tag(sync=True)

    # Playback state
    current_tick = traitlets.Int(0).tag(sync=True)
    playing = traitlets.Bool(False).tag(sync=True)
    playback_speed = traitlets.Float(1.0).tag(sync=True)

    # View state
    zoom = traitlets.Float(1.0).tag(sync=True)  # Pixels per tick multiplier

    # Interaction
    clicked_event = traitlets.Dict({}).tag(sync=True)

    def add_event(
        self,
        tick: int,
        event_type: str,
        source: str,
        message: str,
        level: str = "info",
    ) -> None:
        """Add an event to the timeline."""
        self.events = [
            *self.events,
            {
                "tick": tick,
                "type": event_type,
                "source": source,
                "message": message,
                "level": level,
            },
        ]

    def seek(self, tick: int) -> None:
        """Seek to a specific tick."""
        self.current_tick = tick

    def play(self) -> None:
        """Start playback."""
        self.playing = True

    def pause(self) -> None:
        """Pause playback."""
        self.playing = False

    @classmethod
    def from_field_state(cls, field_state: Any) -> "TimelineWidget":
        """Create from FieldState event log."""
        widget = cls()
        widget.events = field_state.events
        widget.current_tick = field_state.tick
        return widget
