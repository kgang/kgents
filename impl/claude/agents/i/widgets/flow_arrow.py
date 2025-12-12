"""
FlowArrow Widget - Renders connections between agents.

Connection bandwidth is visualized via line thickness:
  High throughput:   ════════  (double line)
  Medium throughput: ────────  (single line)
  Low throughput:    ........  (dotted)
  Lazy/Promise:      : : : :   (sparse dots)
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


class ConnectionType(Enum):
    """Types of connections between agents."""

    HIGH = "HIGH"  # ════ double line
    MEDIUM = "MEDIUM"  # ──── single line
    LOW = "LOW"  # .... dotted
    LAZY = "LAZY"  # : :  sparse (promise, lazy eval)
    NONE = "NONE"  # invisible


class Direction(Enum):
    """Arrow direction."""

    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    DIAGONAL_DOWN = "DIAGONAL_DOWN"
    DIAGONAL_UP = "DIAGONAL_UP"


class Point(NamedTuple):
    """2D point."""

    x: int
    y: int


# Line characters by type and direction
LINE_CHARS = {
    ConnectionType.HIGH: {
        Direction.HORIZONTAL: "═",
        Direction.VERTICAL: "║",
        Direction.DIAGONAL_DOWN: "╲",
        Direction.DIAGONAL_UP: "╱",
    },
    ConnectionType.MEDIUM: {
        Direction.HORIZONTAL: "─",
        Direction.VERTICAL: "│",
        Direction.DIAGONAL_DOWN: "╲",
        Direction.DIAGONAL_UP: "╱",
    },
    ConnectionType.LOW: {
        Direction.HORIZONTAL: "·",
        Direction.VERTICAL: "·",
        Direction.DIAGONAL_DOWN: "·",
        Direction.DIAGONAL_UP: "·",
    },
    ConnectionType.LAZY: {
        Direction.HORIZONTAL: ":",
        Direction.VERTICAL: ":",
        Direction.DIAGONAL_DOWN: ":",
        Direction.DIAGONAL_UP: ":",
    },
}

# Arrow heads
ARROW_HEADS = {
    "right": "►",
    "left": "◄",
    "up": "▲",
    "down": "▼",
}


def throughput_to_connection_type(throughput: float) -> ConnectionType:
    """Map throughput (0.0-1.0) to connection type."""
    if throughput >= 0.7:
        return ConnectionType.HIGH
    elif throughput >= 0.3:
        return ConnectionType.MEDIUM
    elif throughput > 0:
        return ConnectionType.LOW
    else:
        return ConnectionType.LAZY


def generate_horizontal_arrow(
    length: int,
    connection_type: ConnectionType,
    show_arrow: bool = True,
    label: str = "",
) -> str:
    """Generate a horizontal arrow."""
    if length <= 0:
        return ""

    char = LINE_CHARS[connection_type][Direction.HORIZONTAL]

    # Build the line
    if show_arrow and length > 1:
        line = char * (length - 1) + ARROW_HEADS["right"]
    else:
        line = char * length

    # Add label in middle if room
    if label and length > len(label) + 4:
        mid = (length - len(label)) // 2
        line = line[:mid] + label + line[mid + len(label) :]

    return line


def generate_vertical_arrow(
    length: int,
    connection_type: ConnectionType,
    show_arrow: bool = True,
) -> list[str]:
    """Generate a vertical arrow (list of single-char strings)."""
    if length <= 0:
        return []

    char = LINE_CHARS[connection_type][Direction.VERTICAL]

    # Build the line
    if show_arrow and length > 1:
        lines = [char] * (length - 1) + [ARROW_HEADS["down"]]
    else:
        lines = [char] * length

    return lines


class FlowArrow(Widget):
    """
    Render a connection between agents with throughput-based styling.

    The thickness and style of the line indicates bandwidth:
    - High throughput uses double lines (═══)
    - Low throughput uses dots (...)
    - Lazy/promise connections use sparse dots (: :)
    """

    DEFAULT_CSS = """
    FlowArrow {
        width: auto;
        height: 1;
    }

    FlowArrow.high {
        color: #e88a8a;
    }

    FlowArrow.medium {
        color: #d4a574;
    }

    FlowArrow.low {
        color: #8b7ba5;
    }

    FlowArrow.lazy {
        color: #5a5a6a;
    }
    """

    # Reactive properties
    throughput: reactive[float] = reactive(0.5)
    length: reactive[int] = reactive(10)
    direction: reactive[Direction] = reactive(Direction.HORIZONTAL)
    show_arrow_head: reactive[bool] = reactive(True)
    label: reactive[str] = reactive("")

    def __init__(
        self,
        throughput: float = 0.5,
        length: int = 10,
        direction: Direction = Direction.HORIZONTAL,
        show_arrow_head: bool = True,
        label: str = "",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.throughput = throughput
        self.length = length
        self.direction = direction
        self.show_arrow_head = show_arrow_head
        self.label = label
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on throughput."""
        self.remove_class("high", "medium", "low", "lazy")
        conn_type = throughput_to_connection_type(self.throughput)

        class_map = {
            ConnectionType.HIGH: "high",
            ConnectionType.MEDIUM: "medium",
            ConnectionType.LOW: "low",
            ConnectionType.LAZY: "lazy",
        }
        if conn_type in class_map:
            self.add_class(class_map[conn_type])

    def watch_throughput(self, new_value: float) -> None:
        """React to throughput changes."""
        self._update_classes()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the flow arrow."""
        conn_type = throughput_to_connection_type(self.throughput)

        if self.direction == Direction.HORIZONTAL:
            return generate_horizontal_arrow(
                self.length,
                conn_type,
                self.show_arrow_head,
                self.label,
            )
        elif self.direction == Direction.VERTICAL:
            lines = generate_vertical_arrow(
                self.length,
                conn_type,
                self.show_arrow_head,
            )
            return "\n".join(lines)
        else:
            # Diagonal - simplified as horizontal for now
            return generate_horizontal_arrow(
                self.length,
                conn_type,
                self.show_arrow_head,
            )

    def set_throughput(self, throughput: float) -> None:
        """Set throughput level (0.0 to 1.0)."""
        self.throughput = max(0.0, min(1.0, throughput))

    def watch_length(self, new_value: int) -> None:
        """React to length changes."""
        self.refresh()
