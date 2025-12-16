"""
Shared Rich Widgets for Agent Town UI.

These are reusable UI components built with Rich.
"""

from __future__ import annotations

from typing import Any

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text


def progress_bar(
    value: float,
    max_value: float = 1.0,
    width: int = 20,
    complete_style: str = "green",
    finished_style: str = "bright_green",
) -> ProgressBar:
    """Create a progress bar."""
    completed = value / max_value if max_value > 0 else 0
    return ProgressBar(
        total=100,
        completed=int(completed * 100),
        width=width,
        complete_style=complete_style,
        finished_style=finished_style,
    )


def metric_bar(
    label: str,
    value: float,
    max_value: float = 1.0,
    width: int = 15,
    style: str = "blue",
) -> Text:
    """Create a labeled metric bar."""
    filled = int((value / max_value) * width) if max_value > 0 else 0
    filled = max(0, min(width, filled))
    bar = "▓" * filled + "░" * (width - filled)
    return Text(f"{label}: [{bar}] {value:.2f}", style=style)


def citizen_badge(
    name: str,
    phase: str,
    archetype: str | None = None,
) -> Text:
    """Create a citizen badge with phase icon."""
    icons = {
        "IDLE": "🧍",
        "SOCIALIZING": "💬",
        "WORKING": "🔨",
        "REFLECTING": "💭",
        "RESTING": "😴",
    }
    icon = icons.get(phase, "❓")

    text = Text()
    text.append(f"{icon} ", style="bold")
    text.append(name, style="cyan bold")
    if archetype:
        text.append(f" ({archetype})", style="dim")

    return text


def region_panel(
    name: str,
    description: str,
    citizens: list[tuple[str, str, str]],  # (name, phase, archetype)
    density: float,
    connections: list[str],
) -> Panel:
    """Create a region panel with citizens."""
    content_parts: list[RenderableType] = []

    # Description
    content_parts.append(Text(description, style="italic dim"))
    content_parts.append(Text())

    # Citizens
    if citizens:
        for name, phase, archetype in citizens:
            content_parts.append(citizen_badge(name, phase, archetype))
    else:
        content_parts.append(Text("(empty)", style="dim"))

    # Footer with connections
    connections_text = Text(f"\nConnections: {', '.join(connections)}", style="dim")
    content_parts.append(connections_text)

    # Density indicator
    density_pct = f"{density:.0%}"
    title = f"[bold white]{name.upper()}[/bold white] ({density_pct} density)"

    return Panel(
        Group(*content_parts),
        title=title,
        border_style="blue" if density > 0 else "dim",
    )


def metrics_table(
    metrics: dict[str, float],
    thresholds: dict[str, tuple[float, str]] | None = None,
) -> Table:
    """Create a metrics table with optional threshold warnings."""
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status", justify="center")

    thresholds = thresholds or {}

    for name, value in metrics.items():
        value_str = f"{value:.4f}" if isinstance(value, float) else str(value)

        # Check threshold
        status = ""
        if name in thresholds:
            thresh, warn_msg = thresholds[name]
            if value > thresh:
                status = f"[red]{warn_msg}[/red]"
            else:
                status = "[green]OK[/green]"

        table.add_row(name, value_str, status)

    return table


def event_row(
    operation: str,
    participants: list[str],
    success: bool,
    message: str,
    tokens: int,
) -> Text:
    """Create an event row."""
    text = Text()

    # Status icon
    icon = "✓" if success else "✗"
    icon_style = "green" if success else "red"
    text.append(f"{icon} ", style=icon_style)

    # Operation
    text.append(f"[{operation.upper()}] ", style="bold yellow")

    # Message
    text.append(message)

    # Tokens
    text.append(f" ({tokens} tokens)", style="dim")

    return text


def eigenvector_table(eigenvectors: dict[str, float]) -> Table:
    """Create a table of eigenvector values."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Trait", style="cyan")
    table.add_column("Bar", justify="left")
    table.add_column("Value", justify="right", style="dim")

    for name, value in eigenvectors.items():
        # Create bar
        width = 10
        filled = int(value * width)
        bar = "▓" * filled + "░" * (width - filled)

        table.add_row(name.capitalize(), bar, f"{value:.2f}")

    return table


def relationship_table(
    relationships: dict[str, float],
    citizen_names: dict[str, str] | None = None,
) -> Table:
    """Create a table of relationships."""
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("Citizen", style="cyan")
    table.add_column("Relationship", justify="right")

    citizen_names = citizen_names or {}

    for cid, weight in sorted(relationships.items(), key=lambda x: -x[1]):
        name = citizen_names.get(cid, cid)
        style = "green" if weight > 0 else "red" if weight < 0 else "dim"
        sign = "+" if weight > 0 else ""
        table.add_row(name, Text(f"{sign}{weight:.2f}", style=style))

    if not relationships:
        table.add_row("(none)", "-")

    return table
