"""
StateDiffWidget - Compare state between turns.

Shows differences between two turns:
- Turn type transition
- Phase changes (if polynomial agent)
- Confidence delta
- Entropy delta
- Memory changes (future)
- Semaphore changes (future)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from weave import TheWeave
    from weave.turn import Turn


class StateDiffWidget(Widget):
    """
    Widget to show state differences between turns.

    Compares two turns and shows what changed:
    - Turn types
    - Confidence
    - Entropy cost
    - State hashes (for debugging)
    - Phase transitions (if available)
    """

    DEFAULT_CSS = """
    StateDiffWidget {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
        padding: 1 2;
    }

    StateDiffWidget:focus {
        border: solid #e6a352;
    }
    """

    # Reactive properties
    turn_a_id: reactive[str | None] = reactive(None)
    turn_b_id: reactive[str | None] = reactive(None)

    def __init__(
        self,
        weave: TheWeave,
        turn_a_id: str | None = None,
        turn_b_id: str | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the StateDiffWidget.

        Args:
            weave: The Weave to analyze
            turn_a_id: First turn ID (before)
            turn_b_id: Second turn ID (after)
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.weave = weave
        self.turn_a_id = turn_a_id
        self.turn_b_id = turn_b_id
        self.can_focus = True

    def render(self) -> RenderableType:
        """Render the state diff."""
        if not self.turn_a_id or not self.turn_b_id:
            return Panel(
                Text("Select two turns to compare", style="dim"),
                title="State Diff",
                border_style="dim",
            )

        # Get the turns
        turn_a = self._get_turn(self.turn_a_id)
        turn_b = self._get_turn(self.turn_b_id)

        if not turn_a or not turn_b:
            return Panel(
                Text("Turn(s) not found", style="red"),
                title="State Diff",
                border_style="red",
            )

        # Build comparison table
        table = Table(show_header=True, header_style="bold", expand=True)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Before", style="yellow", width=30)
        table.add_column("After", style="green", width=30)
        table.add_column("Delta", style="magenta", width=20)

        # Turn types
        turn_type_a = self._get_turn_type(turn_a)
        turn_type_b = self._get_turn_type(turn_b)
        table.add_row(
            "Turn Type",
            turn_type_a,
            turn_type_b,
            "→" if turn_type_a != turn_type_b else "—",
        )

        # Source
        source_a = getattr(turn_a, "source", "unknown")
        source_b = getattr(turn_b, "source", "unknown")
        table.add_row(
            "Source",
            source_a,
            source_b,
            "→" if source_a != source_b else "—",
        )

        # Confidence (if Turn instances)
        if hasattr(turn_a, "confidence") and hasattr(turn_b, "confidence"):
            conf_a = turn_a.confidence
            conf_b = turn_b.confidence
            delta = conf_b - conf_a
            delta_str = f"{delta:+.0%}" if abs(delta) > 0.01 else "—"
            delta_color = "green" if delta > 0 else "red" if delta < 0 else "dim"
            table.add_row(
                "Confidence",
                f"{conf_a:.0%}",
                f"{conf_b:.0%}",
                f"[{delta_color}]{delta_str}[/]",
            )

        # Entropy cost (if Turn instances)
        if hasattr(turn_a, "entropy_cost") and hasattr(turn_b, "entropy_cost"):
            entropy_a = turn_a.entropy_cost
            entropy_b = turn_b.entropy_cost
            delta = entropy_b - entropy_a
            delta_str = f"{delta:+.3f}" if abs(delta) > 0.001 else "—"
            table.add_row(
                "Entropy Cost",
                f"{entropy_a:.3f}",
                f"{entropy_b:.3f}",
                delta_str,
            )

        # State hashes (if Turn instances)
        if hasattr(turn_a, "state_hash_pre") and hasattr(turn_b, "state_hash_post"):
            hash_a_pre = turn_a.state_hash_pre[:8]
            hash_a_post = turn_a.state_hash_post[:8]
            hash_b_pre = turn_b.state_hash_pre[:8]
            hash_b_post = turn_b.state_hash_post[:8]

            table.add_row(
                "State Hash Pre",
                hash_a_pre,
                hash_b_pre,
                "→" if hash_a_pre != hash_b_pre else "—",
            )
            table.add_row(
                "State Hash Post",
                hash_a_post,
                hash_b_post,
                "→" if hash_a_post != hash_b_post else "—",
            )

        # Timestamp
        time_a = getattr(turn_a, "timestamp", 0.0)
        time_b = getattr(turn_b, "timestamp", 0.0)
        delta_time = time_b - time_a
        table.add_row(
            "Time Delta",
            f"{time_a:.2f}",
            f"{time_b:.2f}",
            f"{delta_time:+.2f}s",
        )

        return Panel(
            table,
            title=f"State Diff: {self.turn_a_id[:8]} → {self.turn_b_id[:8]}",
            border_style="blue",
            padding=(1, 2),
        )

    def set_turns(self, turn_a_id: str, turn_b_id: str) -> None:
        """
        Set the turns to compare.

        Args:
            turn_a_id: First turn ID (before)
            turn_b_id: Second turn ID (after)
        """
        self.turn_a_id = turn_a_id
        self.turn_b_id = turn_b_id
        self.refresh()

    def set_turn_a(self, turn_id: str) -> None:
        """Set the first turn."""
        self.turn_a_id = turn_id
        self.refresh()

    def set_turn_b(self, turn_id: str) -> None:
        """Set the second turn."""
        self.turn_b_id = turn_id
        self.refresh()

    def cycle_turns(self) -> None:
        """Cycle to next turn pair (useful for Tab navigation)."""
        if not self.turn_a_id or not self.turn_b_id:
            return

        # Move to next sequential pair
        all_turns = [e.id for e in self.weave.monoid.events]
        try:
            idx_b = all_turns.index(self.turn_b_id)
            if idx_b + 1 < len(all_turns):
                self.turn_a_id = self.turn_b_id
                self.turn_b_id = all_turns[idx_b + 1]
                self.refresh()
        except (ValueError, IndexError):
            pass

    def _get_turn(self, turn_id: str) -> Any | None:
        """Get a turn by ID."""
        return self.weave.monoid.get_event(turn_id)

    def _get_turn_type(self, turn: Any) -> str:
        """Get turn type as string."""
        if hasattr(turn, "turn_type"):
            return str(turn.turn_type.name)
        return "EVENT"

    def watch_turn_a_id(self, old: str | None, new: str | None) -> None:
        """React to turn A changes."""
        pass  # Refresh happens automatically

    def watch_turn_b_id(self, old: str | None, new: str | None) -> None:
        """React to turn B changes."""
        pass  # Refresh happens automatically


__all__ = ["StateDiffWidget"]
