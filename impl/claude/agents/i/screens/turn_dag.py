"""
TurnDAGRenderer - Visualize Turn DAG in the TUI.

Phase 6 of the Turn-gents Protocol: Debugger Integration.

This module provides visualization of:
1. Turn history as a DAG (not list)
2. Causal cone highlighting for selected agent
3. Thought collapse toggle
4. Knot visualization as merge points
5. Rewind/Fork capability for debugging

The key insight: "Context is a Light Cone, not a Window."
Visualizing as a DAG makes causal structure explicit.

References:
- Turn-gents Plan: Phase 6 (Debugger Integration)
- Terrarium architecture for TUI integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from weave import CausalCone, TheWeave
    from weave.turn import Turn, TurnType

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich.tree import Tree


@dataclass
class TurnDAGConfig:
    """Configuration for TurnDAG rendering."""

    # Display options
    show_thoughts: bool = False  # Collapsed by default
    show_timestamps: bool = False
    show_confidence: bool = True
    show_entropy: bool = False
    max_content_length: int = 50

    # Highlighting
    highlight_cone: bool = True  # Highlight agent's causal cone
    highlight_yields: bool = True  # Highlight YIELD turns

    # Fork/rewind
    show_fork_points: bool = True


@dataclass
class TurnNode:
    """A node in the Turn DAG."""

    turn_id: str
    source: str
    turn_type: str
    content_preview: str
    confidence: float
    entropy_cost: float
    timestamp: float
    is_yield: bool
    is_approved: bool
    dependencies: set[str]
    in_cone: bool = False  # Whether in selected agent's cone


@dataclass
class TurnDAGRenderer:
    """
    Render turn history as DAG, not list.

    This is the main visualization component for Turn-gents debugging.
    It renders the Weave as a DAG with causal structure visible.

    Example:
        renderer = TurnDAGRenderer(weave, config=TurnDAGConfig())

        # Render for Rich console
        panel = renderer.render()
        console.print(panel)

        # Render with agent cone highlighted
        panel = renderer.render(agent_id="my-agent")
    """

    weave: TheWeave
    config: TurnDAGConfig = field(default_factory=TurnDAGConfig)

    # Cache
    _nodes: list[TurnNode] = field(default_factory=list, init=False)
    _cone_ids: set[str] = field(default_factory=set, init=False)

    def render(self, agent_id: str | None = None) -> Panel:
        """
        Render the Turn DAG as a Rich Panel.

        Args:
            agent_id: Optional agent to highlight causal cone for

        Returns:
            Rich Panel containing the DAG visualization
        """
        # Build node list
        self._build_nodes(agent_id)

        # Create tree structure
        tree = self._build_tree()

        # Wrap in panel
        title = "Turn DAG"
        if agent_id:
            title += f" (cone: {agent_id})"

        return Panel(
            tree,
            title=title,
            border_style="blue",
            padding=(1, 2),
        )

    def render_cone(self, cone: CausalCone, agent_id: str) -> Tree:
        """
        Render an agent's causal cone as a tree.

        Args:
            cone: CausalCone instance
            agent_id: Agent to render cone for

        Returns:
            Rich Tree showing the causal history
        """
        context = cone.project_context(agent_id)

        tree = Tree(f"[bold cyan]Causal Cone: {agent_id}[/]")

        # Group by source
        by_source: dict[str, list[Any]] = {}
        for event in context:
            source = getattr(event, "source", "unknown")
            by_source.setdefault(source, []).append(event)

        for source, events in by_source.items():
            branch = tree.add(f"[yellow]{source}[/] ({len(events)} events)")
            for event in events[-3:]:  # Last 3 per source
                self._add_event_to_tree(branch, event)

            if len(events) > 3:
                branch.add(f"[dim]... and {len(events) - 3} more[/dim]")

        return tree

    def render_stats(self) -> Text:
        """
        Render statistics about the Turn DAG.

        Returns:
            Rich Text with statistics
        """
        stats = Text()

        total_turns = len(self.weave)
        if total_turns == 0:
            stats.append("No turns recorded yet.", style="dim")
            return stats

        # Count by type
        type_counts = self._count_by_type()

        stats.append(f"Total Turns: {total_turns}\n", style="bold")

        for turn_type, count in type_counts.items():
            color = self._type_color(turn_type)
            stats.append(f"  {turn_type}: ", style="dim")
            stats.append(f"{count}\n", style=color)

        # Thought collapse indicator
        if not self.config.show_thoughts:
            thought_count = type_counts.get("THOUGHT", 0)
            if thought_count > 0:
                stats.append(
                    f"\n[{thought_count} thoughts collapsed]", style="dim italic"
                )

        return stats

    def get_turn_info(self, turn_id: str) -> dict[str, Any] | None:
        """
        Get detailed information about a turn.

        Args:
            turn_id: The turn ID to look up

        Returns:
            Dictionary with turn details, or None if not found
        """
        for event in self.weave.monoid.events:
            if event.id == turn_id:
                return {
                    "id": event.id,
                    "source": getattr(event, "source", "unknown"),
                    "content": getattr(event, "content", None),
                    "turn_type": getattr(event, "turn_type", None),
                    "confidence": getattr(event, "confidence", 1.0),
                    "entropy_cost": getattr(event, "entropy_cost", 0.0),
                    "timestamp": getattr(event, "timestamp", 0.0),
                    "dependencies": self.weave.braid().get_dependencies(turn_id),
                }
        return None

    def fork_from(self, turn_id: str, new_weave_name: str | None = None) -> TheWeave:
        """
        Create a new Weave forked from a specific turn.

        This enables "what if" debugging scenarios.

        Args:
            turn_id: The turn ID to fork from
            new_weave_name: Optional name for the new weave

        Returns:
            New TheWeave containing history up to and including turn_id
        """
        from weave import TheWeave

        # Get all events up to and including this turn
        braid = self.weave.braid()
        ancestors = braid.get_all_dependencies(turn_id)
        ancestors.add(turn_id)

        # Create new weave
        new_weave = TheWeave()

        # Copy events in order
        ordered = self.weave.monoid.linearize_subset(ancestors)
        for event in ordered:
            deps = braid.get_dependencies(event.id) & ancestors
            new_weave.monoid.append_mut(event, deps if deps else None)

        return new_weave

    def _build_nodes(self, agent_id: str | None) -> None:
        """Build the node list from the weave."""
        self._nodes.clear()
        self._cone_ids.clear()

        # Compute cone if agent specified
        if agent_id and self.config.highlight_cone:
            from weave import CausalCone

            cone = CausalCone(self.weave)
            context = cone.project_context(agent_id)
            self._cone_ids = {e.id for e in context}

        # Convert events to nodes
        for event in self.weave.monoid.events:
            node = self._event_to_node(event)

            # Apply thought collapse
            if node.turn_type == "THOUGHT" and not self.config.show_thoughts:
                continue

            node.in_cone = event.id in self._cone_ids
            self._nodes.append(node)

    def _event_to_node(self, event: Any) -> TurnNode:
        """Convert an event to a TurnNode."""
        # Get turn type
        turn_type = "EVENT"
        if hasattr(event, "turn_type"):
            turn_type = event.turn_type.name

        # Get content preview
        content = str(getattr(event, "content", ""))
        if len(content) > self.config.max_content_length:
            content = content[: self.config.max_content_length - 3] + "..."

        # Check yield status
        is_yield = turn_type == "YIELD"
        is_approved = False
        if is_yield and hasattr(event, "is_approved"):
            is_approved = event.is_approved()

        return TurnNode(
            turn_id=event.id,
            source=getattr(event, "source", "unknown"),
            turn_type=turn_type,
            content_preview=content,
            confidence=getattr(event, "confidence", 1.0),
            entropy_cost=getattr(event, "entropy_cost", 0.0),
            timestamp=getattr(event, "timestamp", 0.0),
            is_yield=is_yield,
            is_approved=is_approved,
            dependencies=self.weave.braid().get_dependencies(event.id),
        )

    def _build_tree(self) -> Tree:
        """Build a Rich Tree from the nodes."""
        tree = Tree("[bold]Turns[/]")

        if not self._nodes:
            tree.add("[dim]No turns to display[/]")
            return tree

        # Group by source
        by_source: dict[str, list[TurnNode]] = {}
        for node in self._nodes:
            by_source.setdefault(node.source, []).append(node)

        for source, nodes in by_source.items():
            # Count collapsed thoughts
            thought_count = sum(
                1
                for e in self.weave.monoid.events
                if getattr(e, "source", "") == source
                and hasattr(e, "turn_type")
                and e.turn_type.name == "THOUGHT"
            )

            branch_label = f"[yellow]{source}[/] ({len(nodes)} visible)"
            if not self.config.show_thoughts and thought_count > 0:
                branch_label += f" [dim][{thought_count} thoughts collapsed][/]"

            branch = tree.add(branch_label)

            for node in nodes[-5:]:  # Show last 5 per source
                self._add_node_to_tree(branch, node)

            if len(nodes) > 5:
                branch.add(f"[dim]... and {len(nodes) - 5} earlier turns[/]")

        return tree

    def _add_node_to_tree(self, parent: Tree, node: TurnNode) -> None:
        """Add a turn node to the tree."""
        # Build label
        color = self._type_color(node.turn_type)
        label = Text()

        # Type badge
        label.append(f"[{node.turn_type}] ", style=color)

        # Cone indicator
        if node.in_cone:
            label.append("● ", style="cyan")

        # Content preview
        label.append(node.content_preview, style="white")

        # Confidence (if enabled)
        if self.config.show_confidence and node.confidence < 1.0:
            conf_color = (
                "green"
                if node.confidence > 0.7
                else "yellow"
                if node.confidence > 0.3
                else "red"
            )
            label.append(f" ({node.confidence:.0%})", style=conf_color)

        # Yield status
        if node.is_yield:
            if node.is_approved:
                label.append(" ✓", style="green")
            else:
                label.append(" ⏳", style="yellow")

        parent.add(label)

    def _add_event_to_tree(self, parent: Tree, event: Any) -> None:
        """Add an event to the tree (for cone rendering)."""
        # Get turn type
        turn_type = "EVENT"
        if hasattr(event, "turn_type"):
            turn_type = event.turn_type.name

        # Get content preview
        content = str(getattr(event, "content", ""))
        if len(content) > self.config.max_content_length:
            content = content[: self.config.max_content_length - 3] + "..."

        color = self._type_color(turn_type)
        label = f"[{color}][{turn_type}][/] {content}"
        parent.add(label)

    def _type_color(self, turn_type: str) -> str:
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

    def _count_by_type(self) -> dict[str, int]:
        """Count events by turn type."""
        counts: dict[str, int] = {}
        for event in self.weave.monoid.events:
            if hasattr(event, "turn_type"):
                turn_type = event.turn_type.name
            else:
                turn_type = "EVENT"
            counts[turn_type] = counts.get(turn_type, 0) + 1
        return counts


def render_turn_dag(
    weave: TheWeave,
    agent_id: str | None = None,
    show_thoughts: bool = False,
) -> Panel:
    """
    Convenience function to render a Turn DAG.

    Args:
        weave: The Weave to visualize
        agent_id: Optional agent to highlight cone for
        show_thoughts: Whether to show THOUGHT turns

    Returns:
        Rich Panel with the DAG visualization
    """
    config = TurnDAGConfig(show_thoughts=show_thoughts)
    renderer = TurnDAGRenderer(weave=weave, config=config)
    return renderer.render(agent_id=agent_id)


__all__ = [
    "TurnDAGRenderer",
    "TurnDAGConfig",
    "TurnNode",
    "render_turn_dag",
]
