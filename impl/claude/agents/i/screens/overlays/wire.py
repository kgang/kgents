"""
WIRE Overlay - Deep-dive into agent event streams.

The WIRE overlay shows:
- Processing waveform (logical/creative/waiting)
- Scrolling event stream with timestamps
- Real-time event updates

Trigger: Press 'w' key while focused on an agent

Navigation:
- j/k: Scroll event stream
- f: Toggle follow mode
- e: Export to markdown
- Escape: Close overlay
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Static

from ...widgets.event_stream import (
    AgentEvent,
    EventStreamDisplay,
    EventType,
    create_demo_events,
)
from ...widgets.waveform import OperationType, WaveformDisplay

if TYPE_CHECKING:
    pass


class WireOverlay(ModalScreen[None]):
    """
    WIRE overlay for event stream visualization.

    Shows the internal processing of an agent in real-time.
    """

    CSS = """
    WireOverlay {
        align: center middle;
    }

    WireOverlay #wire-container {
        width: 80%;
        height: 80%;
        max-width: 100;
        border: solid #4a4a5c;
        background: #1a1a1a;
    }

    WireOverlay #wire-header {
        dock: top;
        height: 1;
        background: #252525;
        color: #f5f0e6;
        text-style: bold;
        padding: 0 2;
    }

    WireOverlay #wire-help {
        dock: bottom;
        height: 1;
        background: #252525;
        color: #6a6560;
        padding: 0 2;
    }

    WireOverlay #wire-content {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    WireOverlay #waveform-section {
        height: 6;
        margin-bottom: 1;
    }

    WireOverlay #stream-section {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Back", show=True),
        Binding("j", "scroll_down", "Down", show=True),
        Binding("k", "scroll_up", "Up", show=True),
        Binding("f", "toggle_follow", "Follow", show=True),
        Binding("e", "export", "Export", show=True),
    ]

    def __init__(
        self,
        agent_id: str = "",
        agent_name: str = "",
        events: list[AgentEvent] | None = None,
        operation_type: OperationType = OperationType.WAITING,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._agent_id = agent_id
        self._agent_name = agent_name or agent_id
        self._events = events
        self._operation_type = operation_type

    def compose(self) -> ComposeResult:
        """Compose the WIRE overlay."""
        # Use demo events if none provided
        events = self._events if self._events is not None else create_demo_events(self._agent_id)

        with Container(id="wire-container"):
            yield Static(f"─ WIRE: {self._agent_name} ─", id="wire-header")
            with Vertical(id="wire-content"):
                with Container(id="waveform-section"):
                    yield WaveformDisplay(
                        operation_type=self._operation_type,
                        title="Processing Waveform",
                        id="waveform-display",
                    )
                with Container(id="stream-section"):
                    yield EventStreamDisplay(
                        events=events,
                        title="Event Stream",
                        id="event-display",
                    )
            yield Static(
                "[j/k] scroll │ [f] follow │ [e] export │ [esc] back",
                id="wire-help",
            )

    async def on_mount(self) -> None:
        """Start waveform animation on mount."""
        try:
            waveform = self.query_one("#waveform-display", WaveformDisplay)
            await waveform.start_animation(interval_ms=100)
        except Exception:
            pass

    async def action_dismiss(self, result: None = None) -> None:
        """Dismiss the overlay."""
        self.dismiss()

    def action_scroll_down(self) -> None:
        """Scroll event stream down."""
        try:
            display = self.query_one("#event-display", EventStreamDisplay)
            display.move_down()
        except Exception:
            pass

    def action_scroll_up(self) -> None:
        """Scroll event stream up."""
        try:
            display = self.query_one("#event-display", EventStreamDisplay)
            display.move_up()
        except Exception:
            pass

    def action_toggle_follow(self) -> None:
        """Toggle follow mode on event stream."""
        try:
            display = self.query_one("#event-display", EventStreamDisplay)
            display.toggle_follow()
        except Exception:
            pass

    def action_export(self) -> None:
        """Export event stream to markdown."""
        try:
            display = self.query_one("#event-display", EventStreamDisplay)
            markdown = display.export_markdown()
            # For now, just show a notification
            # In a full implementation, this would save to file
            self.notify(f"Exported {len(markdown)} characters to markdown")
        except Exception:
            self.notify("Export failed", severity="error")

    def set_operation_type(self, operation_type: OperationType) -> None:
        """Set the waveform operation type."""
        self._operation_type = operation_type
        try:
            waveform = self.query_one("#waveform-display", WaveformDisplay)
            waveform.set_operation(operation_type)
        except Exception:
            pass

    def add_event(self, event: AgentEvent) -> None:
        """Add a new event to the stream."""
        try:
            display = self.query_one("#event-display", EventStreamDisplay)
            display.add_event(event)
        except Exception:
            pass

    def update_operation_from_event(self, event: AgentEvent) -> None:
        """Update waveform operation type based on event type."""
        type_map = {
            EventType.SEARCH: OperationType.LOGICAL,
            EventType.FILTER: OperationType.LOGICAL,
            EventType.SYNTHESIZE: OperationType.CREATIVE,
            EventType.REASON: OperationType.LOGICAL,
            EventType.TOOL: OperationType.LOGICAL,
            EventType.ERROR: OperationType.ERROR,
            EventType.INFO: OperationType.WAITING,
            EventType.COMPLETE: OperationType.WAITING,
        }
        operation = type_map.get(event.event_type, OperationType.WAITING)
        self.set_operation_type(operation)
