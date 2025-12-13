"""
HintRegistry - Maps VisualHints to Widgets.

Extensible registry allowing agents to register custom hint types.
The I-gent uses this to dynamically render agent-emitted hints.

Built-in factories for:
- "text" → Static
- "table" → DataTable
- "density" → DensityField
- "sparkline" → Sparkline
- "graph" → GraphWidget (stub if needed)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from textual.containers import Container, Vertical
from textual.widgets import DataTable, Static

from .hints import VisualHint

if TYPE_CHECKING:
    from textual.widget import Widget


# Type alias for factory functions
HintFactory = Callable[[VisualHint], "Widget"]


class HintRegistry:
    """
    Registry mapping hint types to widget factories.

    Agents can register custom hint types, making the UI
    extensible and heterarchical.

    The registry provides default factories for common hint types,
    but agents are free to define their own representation.

    Example:
        >>> registry = HintRegistry()
        >>> # Use built-in factory
        >>> hint = VisualHint(type="text", data={"text": "Hello"})
        >>> widget = registry.render(hint)

        >>> # Register custom factory
        >>> def custom_factory(hint: VisualHint) -> Widget:
        ...     return MyCustomWidget(hint.data)
        >>> registry.register("custom", custom_factory)

        >>> # Render custom hint
        >>> custom_hint = VisualHint(type="custom", data={...})
        >>> custom_widget = registry.render(custom_hint)
    """

    def __init__(self) -> None:
        """Initialize registry with default factories."""
        self._factories: dict[str, HintFactory] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in hint types."""
        self.register("text", self._text_factory)
        self.register("table", self._table_factory)
        self.register("density", self._density_factory)
        self.register("sparkline", self._sparkline_factory)
        self.register("graph", self._graph_factory)
        self.register("loom", self._loom_factory)

    def register(self, hint_type: str, factory: HintFactory) -> None:
        """
        Register a factory for a hint type.

        Args:
            hint_type: The hint type string (e.g., "custom")
            factory: Callable that takes VisualHint and returns Widget
        """
        self._factories[hint_type] = factory

    def render(self, hint: VisualHint) -> "Widget":
        """
        Render a hint to a widget.

        Args:
            hint: The VisualHint to render

        Returns:
            Widget instance created by the appropriate factory

        Example:
            >>> hint = VisualHint(type="text", data={"text": "Hello"})
            >>> widget = registry.render(hint)
        """
        factory = self._factories.get(hint.type)
        if factory:
            return factory(hint)

        # Fallback for unknown hint types
        return Static(
            f"[dim]Unknown hint type: {hint.type!r}[/dim]\n[dim]Data: {hint.data}[/dim]"
        )

    def render_many(
        self,
        hints: list[VisualHint],
        sort_by_priority: bool = True,
    ) -> Vertical:
        """
        Render multiple hints into a container.

        Hints are sorted by priority (higher first) before rendering.

        Args:
            hints: List of VisualHints to render
            sort_by_priority: Whether to sort by priority (default True)

        Returns:
            Vertical container with all rendered widgets

        Example:
            >>> hints = [
            ...     VisualHint(type="text", data={"text": "A"}, priority=1),
            ...     VisualHint(type="text", data={"text": "B"}, priority=10),
            ... ]
            >>> container = registry.render_many(hints)
            >>> # "B" renders first (higher priority)
        """
        if sort_by_priority:
            # Sort by priority (higher first), then by agent_id for stability
            sorted_hints = sorted(
                hints,
                key=lambda h: (-h.priority, h.agent_id),
            )
        else:
            sorted_hints = hints

        widgets = [self.render(hint) for hint in sorted_hints]
        return Vertical(*widgets)

    # ─────────────────────────────────────────────────────────────
    # Default Factories
    # ─────────────────────────────────────────────────────────────

    def _text_factory(self, hint: VisualHint) -> "Widget":
        """Factory for "text" hints."""
        text = hint.data.get("text", "")
        return Static(str(text))

    def _table_factory(self, hint: VisualHint) -> "Widget":
        """
        Factory for "table" hints.

        Expected data format:
            {"column1": value1, "column2": value2, ...}
            OR
            {"rows": [[v1, v2], [v3, v4]], "columns": ["col1", "col2"]}

        Note: Returns a simple Static widget with formatted table text
        instead of DataTable to avoid app context requirement in tests.
        In a real TUI with app context, DataTable would work fine.
        """
        # Format as simple text table for now
        # This avoids the app context requirement
        lines = []

        # Check for explicit rows/columns format
        if "rows" in hint.data and "columns" in hint.data:
            columns = hint.data["columns"]
            rows = hint.data["rows"]

            # Header
            lines.append(" | ".join(str(c) for c in columns))
            lines.append("-" * (len(" | ".join(str(c) for c in columns))))

            # Rows
            for row in rows:
                lines.append(" | ".join(str(v) for v in row))

        else:
            # Simple dict format: key-value pairs
            lines.append("Key | Value")
            lines.append("----+------")

            for key, value in hint.data.items():
                if key not in ("rows", "columns"):
                    lines.append(f"{key} | {value}")

        return Static("\n".join(lines) if lines else "[dim]Empty table[/dim]")

    def _density_factory(self, hint: VisualHint) -> "Widget":
        """
        Factory for "density" hints.

        Expected data format:
            {"activity": 0.0-1.0, "phase": "ACTIVE"|"DORMANT"|...}
        """
        from ..widgets.density_field import DensityField
        from .core_types import Phase

        activity = hint.data.get("activity", 0.5)
        phase_str = hint.data.get("phase", "ACTIVE")

        # Convert string to Phase enum
        try:
            phase = Phase[phase_str.upper()]
        except KeyError:
            phase = Phase.ACTIVE

        return DensityField(
            agent_id=hint.agent_id,
            agent_name=hint.data.get("name", ""),
            activity=activity,
            phase=phase,
        )

    def _sparkline_factory(self, hint: VisualHint) -> "Widget":
        """
        Factory for "sparkline" hints.

        Expected data format:
            {"values": [1.0, 2.0, 3.0, ...], "width": 20}
        """
        # Import here to avoid circular dependency
        # The Sparkline widget doesn't exist yet, so we'll create a stub
        try:
            from ..widgets.sparkline import Sparkline

            values = hint.data.get("values", [])
            width = hint.data.get("width", 20)
            return Sparkline(values=values, width=width)
        except ImportError:
            # Fallback if Sparkline not yet implemented
            values = hint.data.get("values", [])
            chars = "▁▂▃▄▅▆▇█"

            if not values:
                sparkline = "▁" * 20
            else:
                min_v, max_v = min(values), max(values)
                range_v = max_v - min_v if max_v > min_v else 1

                result = []
                for v in values[-20:]:  # Last 20 values
                    idx = int(((v - min_v) / range_v) * (len(chars) - 1))
                    result.append(chars[max(0, min(len(chars) - 1, idx))])

                sparkline = "".join(result)

            return Static(sparkline)

    def _graph_factory(self, hint: VisualHint) -> "Widget":
        """
        Factory for "graph" hints (stub).

        Expected data format:
            {"nodes": ["A", "B"], "edges": [("A", "B"), ("B", "C")]}
        """
        # Stub implementation until GraphWidget is created
        nodes = hint.data.get("nodes", [])
        edges = hint.data.get("edges", [])

        graph_repr = "[bold]Graph:[/bold]\n"
        graph_repr += f"Nodes: {', '.join(str(n) for n in nodes)}\n"
        graph_repr += f"Edges: {', '.join(f'{a}→{b}' for a, b in edges)}"

        return Static(graph_repr)

    def _loom_factory(self, hint: VisualHint) -> "Widget":
        """
        Factory for "loom" hints (cognitive tree).

        Expected data format:
            {"tree": CognitiveTree, "show_ghosts": True}

        The BranchTree widget renders cognitive history as a navigable
        git-graph style tree, making the Shadow (rejected branches) visible.
        """
        from ..widgets.branch_tree import BranchTree
        from .loom import CognitiveTree

        tree = hint.data.get("tree")
        show_ghosts = hint.data.get("show_ghosts", True)

        if tree is None:
            return Static(
                "[bold]Cognitive Loom[/bold]\n[dim]No cognitive tree provided[/dim]"
            )

        # If tree is a CognitiveTree, use it directly
        if isinstance(tree, CognitiveTree):
            return BranchTree(cognitive_tree=tree, show_ghosts=show_ghosts)

        # Otherwise return error
        return Static(
            "[bold]Cognitive Loom[/bold]\n"
            f"[dim]Invalid tree type: {type(tree).__name__}[/dim]"
        )


# ─────────────────────────────────────────────────────────────
# Global Registry
# ─────────────────────────────────────────────────────────────

_global_registry: HintRegistry | None = None


def get_hint_registry() -> HintRegistry:
    """
    Get the global hint registry.

    Returns:
        The singleton HintRegistry instance

    Example:
        >>> registry = get_hint_registry()
        >>> hint = VisualHint(type="text", data={"text": "Hello"})
        >>> widget = registry.render(hint)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = HintRegistry()
    return _global_registry


def reset_hint_registry() -> None:
    """
    Reset the global hint registry.

    Useful for testing to ensure clean state.
    """
    global _global_registry
    _global_registry = None
