"""
HintContainer Widget - Dynamic container that renders agent-emitted hints.

A heterarchical UI primitive: agents define their own representation
by emitting VisualHints, and the HintContainer dynamically renders them.

The container listens to a hint stream and re-renders when new hints arrive.
Hints are organized by position (main, sidebar, overlay, footer) and
sorted by priority.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget

from ..data.hint_registry import get_hint_registry
from ..data.hints import VisualHint

if TYPE_CHECKING:
    from textual.app import ComposeResult


class HintContainer(Widget):
    """
    Dynamic container that renders VisualHints.

    Agents emit hints, and this container dynamically renders them
    based on position and priority. This makes the UI heterarchical:
    the agent decides how to be seen.

    The container has four zones:
    - main: Main content area
    - sidebar: Right sidebar
    - overlay: Modal overlays
    - footer: Footer area

    Within each zone, hints are sorted by priority (higher first).

    Example:
        >>> container = HintContainer()
        >>> # Agent emits hints
        >>> hint1 = VisualHint(type="text", data={"text": "Hello"}, position="main")
        >>> hint2 = VisualHint(type="table", data={...}, position="sidebar")
        >>> container.hints = [hint1, hint2]
        >>> # Container automatically re-renders
    """

    DEFAULT_CSS = """
    HintContainer {
        width: 100%;
        height: 100%;
    }

    HintContainer > Horizontal {
        width: 100%;
        height: 100%;
    }

    HintContainer .main-zone {
        width: 3fr;
        height: 100%;
    }

    HintContainer .sidebar-zone {
        width: 1fr;
        height: 100%;
        border-left: solid $panel;
    }

    HintContainer .overlay-zone {
        layer: overlay;
        align: center middle;
    }

    HintContainer .footer-zone {
        height: auto;
        dock: bottom;
        border-top: solid $panel;
    }
    """

    # Reactive properties
    hints: reactive[list[VisualHint]] = reactive(list, init=False)

    def __init__(
        self,
        hints: list[VisualHint] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize HintContainer.

        Args:
            hints: Initial list of hints (default: empty)
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.hints = hints or []

    def compose(self) -> ComposeResult:
        """
        Compose the container with zones.

        The layout is:
        - Horizontal container with main and sidebar
        - Overlay zone (layered on top)
        - Footer zone (docked to bottom)
        """
        with Horizontal():
            yield Vertical(id="main-zone", classes="main-zone")
            yield Vertical(id="sidebar-zone", classes="sidebar-zone")

        yield Vertical(id="overlay-zone", classes="overlay-zone")
        yield Vertical(id="footer-zone", classes="footer-zone")

    def watch_hints(self, hints: list[VisualHint]) -> None:
        """
        React to hints changes.

        Re-renders all zones when hints change.
        """
        self._render_hints(hints)

    def _render_hints(self, hints: list[VisualHint]) -> None:
        """
        Render hints into their respective zones.

        Hints are sorted by priority within each zone.
        """
        registry = get_hint_registry()

        # Group hints by position
        by_position: dict[str, list[VisualHint]] = {
            "main": [],
            "sidebar": [],
            "overlay": [],
            "footer": [],
        }

        for hint in hints:
            position = hint.position
            if position in by_position:
                by_position[position].append(hint)

        # Render each zone
        for position, zone_hints in by_position.items():
            zone_id = f"{position}-zone"
            zone = self.query_one(f"#{zone_id}", Vertical)

            # Clear existing widgets
            zone.remove_children()

            # Sort by priority (higher first)
            sorted_hints = sorted(
                zone_hints,
                key=lambda h: (-h.priority, h.agent_id),
            )

            # Render and mount widgets
            for hint in sorted_hints:
                widget = registry.render(hint)
                zone.mount(widget)

    def add_hint(self, hint: VisualHint) -> None:
        """
        Add a hint to the container.

        Args:
            hint: The VisualHint to add
        """
        self.hints = [*self.hints, hint]

    def remove_hints_by_agent(self, agent_id: str) -> None:
        """
        Remove all hints from a specific agent.

        Args:
            agent_id: The agent ID to filter
        """
        self.hints = [h for h in self.hints if h.agent_id != agent_id]

    def clear_hints(self) -> None:
        """Clear all hints."""
        self.hints = []

    def get_hints_by_position(self, position: str) -> list[VisualHint]:
        """
        Get all hints for a specific position.

        Args:
            position: The position to filter ("main", "sidebar", etc.)

        Returns:
            List of hints at that position
        """
        return [h for h in self.hints if h.position == position]

    def get_hints_by_agent(self, agent_id: str) -> list[VisualHint]:
        """
        Get all hints from a specific agent.

        Args:
            agent_id: The agent ID to filter

        Returns:
            List of hints from that agent
        """
        return [h for h in self.hints if h.agent_id == agent_id]
