"""
TurnDAGWidget - Interactive Turn DAG with navigation.

Wraps the existing TurnDAGRenderer with interactive features:
- j/k navigation through turns
- t toggles thought visibility
- g toggles ghost branches
- Enter to focus/navigate to turn
- Highlighting of selected turn
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import RenderableType
from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from weave import TheWeave
    from weave.turn import Turn

    from ..turn_dag import TurnDAGConfig, TurnDAGRenderer


@dataclass
class TurnSelection:
    """Represents a selected turn in the DAG."""

    turn_id: str
    source: str
    turn_type: str
    content: str


class TurnDAGWidget(Widget):
    """
    Interactive Turn DAG widget with keyboard navigation.

    Wraps TurnDAGRenderer to add:
    - j/k navigation through turns
    - t toggle thought visibility
    - g toggle ghost visibility (not yet in TurnDAGRenderer, future)
    - Focus highlighting
    - Agent focus filtering

    Bindings:
        j/k: Navigate down/up through turns
        t: Toggle thought visibility
        g: Toggle ghost branches (future)
        Enter: Navigate to selected turn
    """

    DEFAULT_CSS = """
    TurnDAGWidget {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
        padding: 1 2;
    }

    TurnDAGWidget:focus {
        border: solid #e6a352;
    }

    TurnDAGWidget .dag-title {
        color: #f5f0e6;
        text-style: bold;
    }
    """

    # Reactive properties
    selected_turn_id: reactive[str | None] = reactive(None)
    show_thoughts: reactive[bool] = reactive(False)
    show_ghosts: reactive[bool] = reactive(False)
    agent_focus: reactive[str | None] = reactive(None)

    def __init__(
        self,
        renderer: TurnDAGRenderer,
        agent_id: str | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the TurnDAGWidget.

        Args:
            renderer: The TurnDAGRenderer to wrap
            agent_id: Optional agent to focus on
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        # Initialize instance variables BEFORE super().__init__
        self._turn_list: list[str] = []  # Ordered list of turn IDs
        self._current_index = 0

        super().__init__(name=name, id=id, classes=classes)
        self.renderer = renderer
        self.agent_focus = agent_id
        self.can_focus = True

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self._build_turn_list()
        if self._turn_list:
            self.selected_turn_id = self._turn_list[0]

    def render(self) -> RenderableType:
        """Render the Turn DAG."""
        # Update renderer config based on widget state
        self.renderer.config.show_thoughts = self.show_thoughts
        # Note: show_ghosts not yet in TurnDAGRenderer, future enhancement

        # Render using the existing renderer
        panel = self.renderer.render(agent_id=self.agent_focus)

        # Add selection indicator if we have a selected turn
        if self.selected_turn_id:
            # Future: could modify panel title to show selection
            pass

        return panel

    def set_agent_focus(self, agent_id: str) -> None:
        """
        Set which agent to focus on.

        Args:
            agent_id: Agent ID to focus on
        """
        self.agent_focus = agent_id
        self._build_turn_list()
        self.refresh()

    def toggle_thoughts(self) -> None:
        """Toggle thought visibility."""
        self.show_thoughts = not self.show_thoughts
        self.refresh()

    def toggle_ghosts(self) -> None:
        """Toggle ghost branch visibility."""
        self.show_ghosts = not self.show_ghosts
        # Note: Ghost rendering not yet implemented in TurnDAGRenderer
        self.refresh()

    def navigate_next(self) -> bool:
        """
        Navigate to next turn (j key).

        Returns:
            True if navigation succeeded, False if at end
        """
        if not self._turn_list:
            return False

        if self._current_index < len(self._turn_list) - 1:
            self._current_index += 1
            self.selected_turn_id = self._turn_list[self._current_index]
            self.refresh()
            return True
        return False

    def navigate_prev(self) -> bool:
        """
        Navigate to previous turn (k key).

        Returns:
            True if navigation succeeded, False if at start
        """
        if not self._turn_list:
            return False

        if self._current_index > 0:
            self._current_index -= 1
            self.selected_turn_id = self._turn_list[self._current_index]
            self.refresh()
            return True
        return False

    def get_selected_turn(self) -> TurnSelection | None:
        """
        Get the currently selected turn.

        Returns:
            TurnSelection if a turn is selected, None otherwise
        """
        if not self.selected_turn_id:
            return None

        # Get turn info from renderer
        info = self.renderer.get_turn_info(self.selected_turn_id)
        if not info:
            return None

        return TurnSelection(
            turn_id=info["id"],
            source=info["source"],
            turn_type=str(info.get("turn_type", "EVENT")),
            content=str(info.get("content", "")),
        )

    def _build_turn_list(self) -> None:
        """Build ordered list of turn IDs for navigation."""
        self._turn_list = []

        # Get all events from weave
        for event in self.renderer.weave.monoid.events:
            # Filter by agent if focus is set
            if self.agent_focus and getattr(event, "source", None) != self.agent_focus:
                continue

            # Filter thoughts if not showing
            if not self.show_thoughts:
                if hasattr(event, "turn_type"):
                    from weave.turn import TurnType

                    if event.turn_type == TurnType.THOUGHT:
                        continue

            self._turn_list.append(event.id)

        # Reset index if out of bounds
        if self._current_index >= len(self._turn_list):
            self._current_index = max(0, len(self._turn_list) - 1)

    def watch_show_thoughts(self, old: bool, new: bool) -> None:
        """React to thought visibility changes."""
        self._build_turn_list()

    def watch_agent_focus(self, old: str | None, new: str | None) -> None:
        """React to agent focus changes."""
        self._build_turn_list()

    def get_turn_count(self) -> int:
        """Get the number of visible turns."""
        return len(self._turn_list)

    def get_current_index(self) -> int:
        """Get the current selection index."""
        return self._current_index


__all__ = ["TurnDAGWidget", "TurnSelection"]
