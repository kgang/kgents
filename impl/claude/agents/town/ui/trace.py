"""
THE TRACE: OpenTelemetry Span Visualization.

Debugging is part of the phenomenon.
The trace reveals the machinery without dispelling the mystery.

Features:
- Span tree visualization
- Token accounting per span
- Duration metrics
- Error highlighting

Integration with protocols/agentese/metrics.py patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


@dataclass
class Span:
    """
    A trace span representing an operation.

    Simplified version of OpenTelemetry spans for Agent Town.
    """

    name: str
    duration_ms: float
    success: bool = True
    tokens_in: int = 0
    tokens_out: int = 0
    attributes: dict[str, Any] = field(default_factory=dict)
    children: list["Span"] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None

    @property
    def total_tokens(self) -> int:
        """Total tokens for this span and children."""
        return (
            self.tokens_in
            + self.tokens_out
            + sum(c.total_tokens for c in self.children)
        )

    @property
    def total_duration_ms(self) -> float:
        """Total duration including children."""
        return self.duration_ms + sum(c.total_duration_ms for c in self.children)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "attributes": dict(self.attributes),
            "children": [c.to_dict() for c in self.children],
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


@dataclass
class TraceView:
    """
    OpenTelemetry span visualization for Agent Town.

    Renders spans as a tree with metrics.
    """

    console: Console | None = None

    def __post_init__(self) -> None:
        if self.console is None:
            self.console = Console()

    def render(self, span: Span) -> Panel:
        """Render a span tree."""
        tree = self._build_tree(span)

        # Summary
        summary = self._render_summary(span)

        return Panel(
            Group(tree, Text(), summary),
            title=f"[bold yellow]TRACE: {span.name}[/bold yellow]",
            border_style="yellow",
        )

    def _build_tree(self, span: Span, tree: Tree | None = None) -> Tree:
        """Build a Rich tree from spans."""
        # Format this span
        status_icon = "✓" if span.success else "✗"
        status_style = "green" if span.success else "red"

        label = Text()
        label.append(f"{status_icon} ", style=status_style)
        label.append(span.name, style="bold")
        label.append(f" ({span.duration_ms:.0f}ms", style="dim")
        if span.tokens_in or span.tokens_out:
            label.append(f", {span.tokens_in}→{span.tokens_out} tok", style="cyan")
        label.append(")", style="dim")

        if span.error:
            label.append(f" ERROR: {span.error}", style="red")

        if tree is None:
            tree = Tree(label)
        else:
            tree = tree.add(label)

        # Add children
        for child in span.children:
            self._build_tree(child, tree)

        return tree

    def _render_summary(self, span: Span) -> RenderableType:
        """Render summary metrics."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total Duration", f"{span.total_duration_ms:.0f}ms")
        table.add_row("Total Tokens", f"{span.total_tokens}")
        table.add_row("Spans", f"{self._count_spans(span)}")

        if span.error:
            table.add_row("Status", Text("ERROR", style="red bold"))
        elif span.success:
            table.add_row("Status", Text("SUCCESS", style="green bold"))
        else:
            table.add_row("Status", Text("PARTIAL", style="yellow bold"))

        return table

    def _count_spans(self, span: Span) -> int:
        """Count total spans in tree."""
        return 1 + sum(self._count_spans(c) for c in span.children)

    def render_span_panel(self, span: Span) -> Panel:
        """Render a single span as a panel."""
        status_icon = "✓" if span.success else "✗"
        status_style = "green" if span.success else "red"

        content = Text()
        content.append(f"{status_icon} ", style=status_style)
        content.append(f"[bold]{span.name}[/bold]\n")
        content.append(f"duration: {span.duration_ms:.0f}ms\n", style="dim")
        content.append(f"tokens: {span.tokens_in}→{span.tokens_out}\n", style="cyan")

        if span.attributes:
            content.append("\nAttributes:\n", style="bold")
            for k, v in span.attributes.items():
                content.append(f"  {k}: {v}\n", style="dim")

        if span.error:
            content.append(f"\nError: {span.error}", style="red")

        return Panel(content, border_style=status_style)

    def print(self, span: Span) -> None:
        """Print the trace view to console."""
        if self.console is None:
            self.console = Console()
        self.console.print(self.render(span))


def render_trace(span: Span) -> str:
    """Render trace view as string (for testing)."""
    console = Console(force_terminal=True, width=70)
    view = TraceView(console=console)

    with console.capture() as capture:
        view.print(span)

    return capture.get()


# =============================================================================
# Span Builder (for creating traces from events)
# =============================================================================


class SpanBuilder:
    """
    Builder for creating spans from town events.

    Usage:
        builder = SpanBuilder("citizen.greet")
        builder.set_attributes({"citizen_a": "Alice", "citizen_b": "Bob"})
        builder.set_tokens(100, 50)
        span = builder.finish()
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.start_time = datetime.now()
        self.attributes: dict[str, Any] = {}
        self.tokens_in = 0
        self.tokens_out = 0
        self.children: list[Span] = []
        self.error: str | None = None

    def set_attributes(self, attrs: dict[str, Any]) -> "SpanBuilder":
        """Set span attributes."""
        self.attributes.update(attrs)
        return self

    def set_tokens(self, tokens_in: int, tokens_out: int = 0) -> "SpanBuilder":
        """Set token counts."""
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        return self

    def add_child(self, span: Span) -> "SpanBuilder":
        """Add a child span."""
        self.children.append(span)
        return self

    def set_error(self, error: str) -> "SpanBuilder":
        """Mark span as error."""
        self.error = error
        return self

    def finish(self) -> Span:
        """Finish the span and return it."""
        end_time = datetime.now()
        duration_ms = (end_time - self.start_time).total_seconds() * 1000

        return Span(
            name=self.name,
            duration_ms=duration_ms,
            success=self.error is None,
            tokens_in=self.tokens_in,
            tokens_out=self.tokens_out,
            attributes=self.attributes,
            children=self.children,
            timestamp=self.start_time,
            error=self.error,
        )


__all__ = ["Span", "TraceView", "render_trace", "SpanBuilder"]
