"""
EventStream Widget - Scrolling log viewer for agent events.

The event stream is a key component of the WIRE overlay,
showing real-time events from the agent's processing.

Events have:
- Timestamp
- Event type (search, filter, synthesize, etc.)
- Message

Supports j/k scrolling, follow mode, and export to markdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import RenderResult


class EventType(Enum):
    """Type of agent event."""

    SEARCH = "search"
    FILTER = "filter"
    SYNTHESIZE = "synthesize"
    REASON = "reason"
    TOOL = "tool"
    ERROR = "error"
    INFO = "info"
    COMPLETE = "complete"


# Color mapping for event types (using EARTH_PALETTE values)
EVENT_COLORS = {
    EventType.SEARCH: "#8ac4e8",  # Sky blue
    EventType.FILTER: "#7d9c7a",  # Sage
    EventType.SYNTHESIZE: "#e6a352",  # Amber
    EventType.REASON: "#f5d08a",  # Pale gold
    EventType.TOOL: "#b3a89a",  # Dusty tan
    EventType.ERROR: "#c97b84",  # Dusty rose
    EventType.INFO: "#6a6560",  # Dim
    EventType.COMPLETE: "#7d9c7a",  # Sage
}


@dataclass
class AgentEvent:
    """An event from an agent's processing stream."""

    timestamp: datetime
    event_type: EventType
    message: str
    agent_id: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def format_timestamp(self) -> str:
        """Format timestamp as HH:MM:SS."""
        return self.timestamp.strftime("%H:%M:%S")

    def format_line(self, width: int = 60) -> str:
        """Format as a single line for display."""
        ts = self.format_timestamp()
        event_tag = f"[{self.event_type.value}]"
        # Truncate message to fit width
        max_msg_len = max(20, width - len(ts) - len(event_tag) - 4)
        msg = self.message[:max_msg_len]
        if len(self.message) > max_msg_len:
            msg = msg[:-3] + "..."
        return f"{ts} {event_tag:14} {msg}"

    def to_markdown(self) -> str:
        """Export as markdown list item."""
        ts = self.format_timestamp()
        return f"- **{ts}** [{self.event_type.value}] {self.message}"


def create_demo_events(agent_id: str = "robin") -> list[AgentEvent]:
    """Create demo events for testing."""
    now = datetime.now()
    base_ts = now.replace(second=0, microsecond=0)

    events = [
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=15),
            event_type=EventType.SEARCH,
            message="Querying PubMed for β-sheet formation...",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=18),
            event_type=EventType.SEARCH,
            message="15 papers found, retrieving abstracts",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=20),
            event_type=EventType.FILTER,
            message="3 high-relevance papers selected",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=25),
            event_type=EventType.SYNTHESIZE,
            message="Drafting conclusion from extracted data...",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=30),
            event_type=EventType.SYNTHESIZE,
            message="Pattern detected: β-sheet stabilization via hydrogen bonds",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=35),
            event_type=EventType.REASON,
            message="Cross-referencing with molecular dynamics simulations",
            agent_id=agent_id,
        ),
        AgentEvent(
            timestamp=base_ts.replace(minute=42, second=40),
            event_type=EventType.COMPLETE,
            message="Hypothesis formulated with 87% confidence",
            agent_id=agent_id,
        ),
    ]
    return events


class EventStream(Widget):
    """
    Scrolling log viewer for agent events.

    Supports:
    - j/k for line-by-line scrolling
    - f to toggle follow mode
    - Automatic scrolling when following
    """

    DEFAULT_CSS = """
    EventStream {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
        padding: 0 1;
        overflow-y: auto;
    }

    EventStream .event-line {
        height: 1;
    }

    EventStream .event-line.current {
        background: #252525;
    }

    EventStream .event-type-search {
        color: #8ac4e8;
    }

    EventStream .event-type-filter {
        color: #7d9c7a;
    }

    EventStream .event-type-synthesize {
        color: #e6a352;
    }

    EventStream .event-type-reason {
        color: #f5d08a;
    }

    EventStream .event-type-error {
        color: #c97b84;
    }
    """

    # Reactive properties
    follow: reactive[bool] = reactive(True)
    _scroll_pos: reactive[int] = reactive(0)
    current_line: reactive[int] = reactive(-1)  # -1 means latest

    def __init__(
        self,
        events: list[AgentEvent] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._events: list[AgentEvent] = events or []

    @property
    def events(self) -> list[AgentEvent]:
        """Get the events list."""
        return self._events

    @events.setter
    def events(self, value: list[AgentEvent]) -> None:
        """Set the events list."""
        self._events = value
        self.refresh()

    def add_event(self, event: AgentEvent) -> None:
        """Add a new event to the stream."""
        self._events.append(event)
        if self.follow:
            # Auto-scroll to bottom
            self.current_line = len(self._events) - 1
            self._scroll_pos = max(0, len(self._events) - self._visible_lines())
        self.refresh()

    def _visible_lines(self) -> int:
        """Calculate number of visible lines based on widget height."""
        return max(1, self.size.height - 2)  # Account for border

    def move_up(self) -> None:
        """Scroll up one line."""
        if self._scroll_pos > 0:
            self._scroll_pos -= 1
            self.follow = False
        self.refresh()

    def move_down(self) -> None:
        """Scroll down one line."""
        max_offset = max(0, len(self._events) - self._visible_lines())
        if self._scroll_pos < max_offset:
            self._scroll_pos += 1
        if self._scroll_pos >= max_offset:
            self.follow = True
        self.refresh()

    def toggle_follow(self) -> None:
        """Toggle follow mode."""
        self.follow = not self.follow
        if self.follow:
            # Jump to bottom
            self._scroll_pos = max(0, len(self._events) - self._visible_lines())
        self.refresh()

    def export_markdown(self) -> str:
        """Export all events to markdown format."""
        lines = [
            "# Agent Event Stream",
            "",
            f"Exported: {datetime.now().isoformat()}",
            "",
        ]
        for event in self._events:
            lines.append(event.to_markdown())
        return "\n".join(lines)

    def render(self) -> "RenderResult":
        """Render the event stream."""
        if not self._events:
            return "(no events)"

        width = max(40, self.size.width - 4)
        visible = self._visible_lines()

        # Get visible slice of events
        start = self._scroll_pos
        end = min(start + visible, len(self._events))
        visible_events = self._events[start:end]

        lines = []
        for i, event in enumerate(visible_events):
            line_idx = start + i
            # Mark current line if at bottom in follow mode
            is_current = self.follow and line_idx == len(self._events) - 1
            prefix = "▶ " if is_current else "  "
            line = prefix + event.format_line(width - 2)
            lines.append(line)

        # Pad if fewer events than visible lines
        while len(lines) < visible:
            lines.append("")

        return "\n".join(lines)


class EventStreamDisplay(Widget):
    """
    Compound widget: event stream with title and status bar.

    Used in the WIRE overlay with keybinding hints.
    """

    DEFAULT_CSS = """
    EventStreamDisplay {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
    }

    EventStreamDisplay .stream-title {
        dock: top;
        height: 1;
        padding: 0 1;
        color: #b3a89a;
        text-style: bold;
        background: #252525;
    }

    EventStreamDisplay .stream-status {
        dock: bottom;
        height: 1;
        padding: 0 1;
        color: #6a6560;
        background: #252525;
    }
    """

    title: reactive[str] = reactive("Event Stream")

    def __init__(
        self,
        events: list[AgentEvent] | None = None,
        title: str = "Event Stream",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._events = events or []
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the event stream display."""
        yield Static(f"─ {self.title} ─", classes="stream-title")
        yield EventStream(events=self._events, id="stream")
        yield Static("", classes="stream-status", id="status")

    def on_mount(self) -> None:
        """Update status on mount."""
        self._update_status()

    def _update_status(self) -> None:
        """Update the status bar."""
        try:
            stream = self.query_one("#stream", EventStream)
            status = self.query_one("#status", Static)
            follow_indicator = "[F]" if stream.follow else "[ ]"
            status.update(f"Events: {len(stream.events)} │ {follow_indicator} follow")
        except Exception:
            pass

    def add_event(self, event: AgentEvent) -> None:
        """Add event to the internal stream."""
        stream = self.query_one("#stream", EventStream)
        stream.add_event(event)
        self._update_status()

    def move_up(self) -> None:
        """Scroll up in the stream."""
        stream = self.query_one("#stream", EventStream)
        stream.move_up()
        self._update_status()

    def move_down(self) -> None:
        """Scroll down in the stream."""
        stream = self.query_one("#stream", EventStream)
        stream.move_down()
        self._update_status()

    def toggle_follow(self) -> None:
        """Toggle follow mode."""
        stream = self.query_one("#stream", EventStream)
        stream.toggle_follow()
        self._update_status()

    def export_markdown(self) -> str:
        """Export stream to markdown."""
        stream = self.query_one("#stream", EventStream)
        return stream.export_markdown()
