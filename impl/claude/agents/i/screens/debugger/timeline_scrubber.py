"""
TimelineScrubber - Time navigation and forking.

Horizontal timeline at bottom of debugger:
- Major events labeled
- Cursor position indicator
- Rewind/step controls
- Fork from cursor creates new Weave
- Export trace functionality
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from weave import TheWeave


class TimelineScrubber(Widget):
    """
    Timeline scrubber widget for time navigation.

    Features:
    - Horizontal timeline showing events
    - Cursor position
    - Rewind/step navigation
    - Fork from cursor
    - Export trace

    Bindings:
        ◀: Rewind (step backward)
        ▶: Step forward
        f: Fork from cursor
        x: Export trace
    """

    DEFAULT_CSS = """
    TimelineScrubber {
        width: 100%;
        height: 5;
        border: solid #4a4a5c;
        padding: 1 2;
        dock: bottom;
    }

    TimelineScrubber:focus {
        border: solid #e6a352;
    }

    TimelineScrubber.at-fork-point {
        border: solid #ff6b6b;
    }
    """

    # Reactive properties
    cursor_position: reactive[int] = reactive(0)
    at_fork_point: reactive[bool] = reactive(False)

    def __init__(
        self,
        weave: TheWeave,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the TimelineScrubber.

        Args:
            weave: The Weave to navigate
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.weave = weave
        self._event_ids: list[str] = []
        self._major_events: dict[int, str] = {}  # index -> label
        self.can_focus = True

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self._build_timeline()
        # Start at end
        if self._event_ids:
            self.cursor_position = len(self._event_ids) - 1

    def render(self) -> RenderableType:
        """Render the timeline scrubber."""
        if not self._event_ids:
            return Panel(
                Text("No events in timeline", style="dim"),
                title="Timeline",
                border_style="dim",
            )

        # Build timeline visualization
        timeline = Text()

        # Calculate time range
        events = list(self.weave.monoid.events)
        if not events:
            return Panel(timeline, title="Timeline", border_style="blue")

        min_time = min(e.timestamp for e in events)
        max_time = max(e.timestamp for e in events)
        time_range = max_time - min_time if max_time > min_time else 1.0

        # Timeline header
        timeline.append("Timeline: ", style="bold")
        timeline.append(f"{len(self._event_ids)} events\n", style="cyan")

        # Build visual timeline (simple text-based for now)
        # We'll show 50 character positions representing the time range
        width = 50
        positions: list[str] = [" "] * width

        # Mark events
        for i, event_id in enumerate(self._event_ids):
            event = self.weave.monoid.get_event(event_id)
            if event:
                # Calculate position (0 to width-1)
                normalized = (event.timestamp - min_time) / time_range if time_range > 0 else 0.5
                pos = int(normalized * (width - 1))
                pos = max(0, min(width - 1, pos))

                # Mark as event
                if i == self.cursor_position:
                    positions[pos] = "▲"  # Cursor
                else:
                    positions[pos] = "●"

        # Build timeline bar
        timeline.append("  ")
        for i, char in enumerate(positions):
            if char == "▲":
                timeline.append(char, style="red bold")
            elif char == "●":
                timeline.append(char, style="cyan")
            else:
                timeline.append(char, style="dim")
        timeline.append("\n")

        # Add time markers
        timeline.append("  ", style="dim")
        timeline.append("t=0s", style="dim")
        timeline.append(" " * (width - 10), style="dim")
        timeline.append(f"t={time_range:.1f}s", style="dim")
        timeline.append("\n")

        # Current position info
        if 0 <= self.cursor_position < len(self._event_ids):
            current_event_id = self._event_ids[self.cursor_position]
            current_event = self.weave.monoid.get_event(current_event_id)
            if current_event:
                timeline.append("\nCursor: ", style="bold")
                timeline.append(f"{self.cursor_position + 1}/{len(self._event_ids)} ", style="cyan")

                # Event info
                source = getattr(current_event, "source", "unknown")
                turn_type = "EVENT"
                if hasattr(current_event, "turn_type"):
                    turn_type = current_event.turn_type.name

                timeline.append(f"[{turn_type}] ", style="yellow")
                timeline.append(f"from {source}", style="white")

        # Controls hint
        timeline.append("\n\n[◀ rewind]  [▶ step]  [f] fork  [x] export", style="dim")

        # Border style based on state
        border_style = "red" if self.at_fork_point else "blue"

        return Panel(
            timeline,
            title="Timeline",
            border_style=border_style,
            padding=(1, 2),
        )

    def rewind(self) -> bool:
        """
        Rewind one step (◀).

        Returns:
            True if rewound successfully, False if at start
        """
        if self.cursor_position > 0:
            self.cursor_position -= 1
            self.refresh()
            return True
        return False

    def step_forward(self) -> bool:
        """
        Step forward one event (▶).

        Returns:
            True if stepped successfully, False if at end
        """
        if self.cursor_position < len(self._event_ids) - 1:
            self.cursor_position += 1
            self.refresh()
            return True
        return False

    def jump_to_event(self, event_index: int) -> bool:
        """
        Jump to a specific event index.

        Args:
            event_index: Index to jump to

        Returns:
            True if jump succeeded, False if out of bounds
        """
        if 0 <= event_index < len(self._event_ids):
            self.cursor_position = event_index
            self.refresh()
            return True
        return False

    def fork_from_cursor(self) -> TheWeave:
        """
        Create a new Weave forked from cursor position.

        Returns:
            New TheWeave containing history up to cursor
        """
        if not self._event_ids or self.cursor_position < 0:
            # Return empty weave
            from weave import TheWeave

            return TheWeave()

        # Get event at cursor
        current_event_id = self._event_ids[self.cursor_position]

        # Use TurnDAGRenderer's fork_from method
        from ..turn_dag import TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=self.weave)
        new_weave = renderer.fork_from(current_event_id)

        # Mark that we're at a fork point
        self.at_fork_point = True
        self.refresh()

        return new_weave

    def export_trace(self) -> str:
        """
        Export the trace as text.

        Returns:
            String representation of the trace
        """
        lines = []
        lines.append("# Trace Export")
        lines.append(f"# Total events: {len(self._event_ids)}")
        lines.append(f"# Cursor position: {self.cursor_position + 1}")
        lines.append("")

        for i, event_id in enumerate(self._event_ids):
            event = self.weave.monoid.get_event(event_id)
            if event:
                prefix = ">>> " if i == self.cursor_position else "    "
                source = getattr(event, "source", "unknown")
                turn_type = "EVENT"
                if hasattr(event, "turn_type"):
                    turn_type = event.turn_type.name

                content = str(getattr(event, "content", ""))
                if len(content) > 60:
                    content = content[:57] + "..."

                lines.append(f"{prefix}[{i:3d}] {turn_type:8s} {source:15s} {content}")

        return "\n".join(lines)

    def get_cursor_event_id(self) -> str | None:
        """
        Get the event ID at the cursor position.

        Returns:
            Event ID or None if no event at cursor
        """
        if 0 <= self.cursor_position < len(self._event_ids):
            return self._event_ids[self.cursor_position]
        return None

    def _build_timeline(self) -> None:
        """Build the timeline from the weave."""
        self._event_ids = [e.id for e in self.weave.monoid.linearize()]
        self._major_events = {}

        # Identify major events (Knots, first/last events, etc.)
        if self._event_ids:
            self._major_events[0] = "start"
            self._major_events[len(self._event_ids) - 1] = "now"

    def watch_cursor_position(self, old: int, new: int) -> None:
        """React to cursor position changes."""
        # Reset fork point state when moving cursor
        if self.at_fork_point:
            self.at_fork_point = False

    def watch_at_fork_point(self, old: bool, new: bool) -> None:
        """React to fork point state changes."""
        if new:
            self.add_class("at-fork-point")
        else:
            self.remove_class("at-fork-point")


__all__ = ["TimelineScrubber"]
