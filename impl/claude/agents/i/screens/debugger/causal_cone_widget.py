"""
CausalConeWidget - Visualize causal cone for focused agent.

Shows what information was available to an agent at a given turn:
- Context grouped by source (agent, world, self)
- Compression ratio display
- Total event count
- Highlighting when activated
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from weave import CausalCone, TheWeave
    from weave.causal_cone import CausalConeStats


class CausalConeWidget(Widget):
    """
    Widget to visualize an agent's causal cone.

    The causal cone shows what information was available to an
    agent at a specific point in time (their "light cone").

    Features:
    - Groups events by source
    - Shows compression ratio
    - Highlights when active
    - Shows last N events per source
    """

    DEFAULT_CSS = """
    CausalConeWidget {
        width: 100%;
        height: 100%;
        border: solid #4a4a5c;
        padding: 1 2;
    }

    CausalConeWidget:focus {
        border: solid #e6a352;
    }

    CausalConeWidget.highlighted {
        border: solid #ff6b6b;
        background: #2a1a1a;
    }
    """

    # Reactive properties
    agent_id: reactive[str | None] = reactive(None)
    highlighted: reactive[bool] = reactive(False)

    def __init__(
        self,
        weave: TheWeave,
        agent_id: str | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the CausalConeWidget.

        Args:
            weave: The Weave to analyze
            agent_id: Agent to show cone for
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.weave = weave
        self.agent_id = agent_id
        self._cone: CausalCone | None = None
        self._stats: CausalConeStats | None = None
        self.can_focus = True

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        if self.agent_id:
            self._rebuild_cone()

    def render(self) -> RenderableType:
        """Render the causal cone visualization."""
        if not self.agent_id:
            return Panel(
                Text("No agent selected", style="dim"),
                title="Causal Cone",
                border_style="dim",
            )

        if not self._cone or not self._stats:
            self._rebuild_cone()

        # Build the display
        tree = Tree(f"[bold cyan]Causal Cone: {self.agent_id}[/]")

        if not self._stats:
            tree.add("[dim]No context available[/]")
        else:
            # Add stats header
            stats_text = Text()
            stats_text.append(f"Total: {self._stats.cone_size} events\n", style="bold")
            stats_text.append(
                f"Compression: {self._stats.compression_ratio:.0%}\n",
                style="green" if self._stats.compression_ratio > 0.5 else "yellow",
            )

            # Add turn type breakdown
            if self._stats.speech_turns > 0:
                stats_text.append(f"  Speech: {self._stats.speech_turns}\n", style="green")
            if self._stats.action_turns > 0:
                stats_text.append(f"  Action: {self._stats.action_turns}\n", style="blue")
            if self._stats.thought_turns > 0:
                stats_text.append(f"  Thought: {self._stats.thought_turns}\n", style="dim")
            if self._stats.yield_turns > 0:
                stats_text.append(f"  Yield: {self._stats.yield_turns}\n", style="yellow")

            tree.add(stats_text)

            # Group events by source
            if self._cone:
                context = self._cone.project_context(self.agent_id)
                by_source: dict[str, list[Any]] = {}
                for event in context:
                    source = getattr(event, "source", "unknown")
                    by_source.setdefault(source, []).append(event)

                # Add sources
                sources_branch = tree.add(f"[bold]Sources ({len(by_source)})[/]")
                for source, events in sorted(by_source.items()):
                    source_branch = sources_branch.add(
                        f"[yellow]{source}[/] ({len(events)} events)"
                    )

                    # Show last 3 events from this source
                    for event in events[-3:]:
                        content = str(getattr(event, "content", ""))
                        if len(content) > 40:
                            content = content[:37] + "..."

                        # Get turn type color
                        turn_type = "EVENT"
                        color = "white"
                        if hasattr(event, "turn_type"):
                            turn_type = event.turn_type.name
                            color = self._get_turn_color(turn_type)

                        source_branch.add(f"[{color}][{turn_type}][/] {content}")

                    if len(events) > 3:
                        source_branch.add(f"[dim]... and {len(events) - 3} more[/]")

        # Style based on highlight state
        border_style = "red" if self.highlighted else "blue"

        return Panel(
            tree,
            title="Causal Cone",
            border_style=border_style,
            padding=(1, 2),
        )

    def set_agent(self, agent_id: str) -> None:
        """
        Set the agent to show cone for.

        Args:
            agent_id: Agent ID
        """
        self.agent_id = agent_id
        self._rebuild_cone()
        self.refresh()

    def highlight_cone(self) -> None:
        """Highlight the cone (for focusing attention)."""
        self.highlighted = True
        self.refresh()

    def unhighlight_cone(self) -> None:
        """Remove highlight."""
        self.highlighted = False
        self.refresh()

    def get_stats(self) -> CausalConeStats | None:
        """
        Get current cone statistics.

        Returns:
            CausalConeStats if available, None otherwise
        """
        return self._stats

    def _rebuild_cone(self) -> None:
        """Rebuild the causal cone and stats."""
        if not self.agent_id:
            self._cone = None
            self._stats = None
            return

        from weave import CausalCone
        from weave.causal_cone import compute_cone_stats

        self._cone = CausalCone(self.weave)
        self._stats = compute_cone_stats(self._cone, self.agent_id)

    def watch_agent_id(self, old: str | None, new: str | None) -> None:
        """React to agent ID changes."""
        self._rebuild_cone()

    def watch_highlighted(self, old: bool, new: bool) -> None:
        """React to highlight state changes."""
        # Add/remove CSS class for styling
        if new:
            self.add_class("highlighted")
        else:
            self.remove_class("highlighted")

    def _get_turn_color(self, turn_type: str) -> str:
        """Get color for a turn type."""
        colors = {
            "SPEECH": "green",
            "ACTION": "blue",
            "THOUGHT": "dim",
            "YIELD": "yellow",
            "SILENCE": "dim italic",
            "EVENT": "white",
        }
        return colors.get(turn_type, "white")


__all__ = ["CausalConeWidget"]
