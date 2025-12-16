"""
TUI Progress Widget: Progress bars and step indicators.

Supports bar and step variants with animations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from rich.console import RenderableType
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from protocols.projection.schema import WidgetMeta
from protocols.projection.tui.base import TUIWidget


@dataclass(frozen=True)
class ProgressStep:
    """A step in a multi-step progress."""

    label: str
    completed: bool = False
    current: bool = False


@dataclass(frozen=True)
class ProgressState:
    """State for progress widget."""

    value: int = 0  # 0-100
    variant: Literal["bar", "steps"] = "bar"
    label: str | None = None
    steps: tuple[ProgressStep, ...] = field(default_factory=tuple)
    indeterminate: bool = False


class TUIProgressWidget(TUIWidget[ProgressState]):
    """
    TUI progress display widget.

    Renders progress bars or step indicators.
    """

    DEFAULT_CSS = """
    TUIProgressWidget {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def render_content(self) -> RenderableType:
        """Render progress content based on variant."""
        if self.state is None:
            return ProgressBar(total=100, completed=0)

        if self.state.variant == "steps":
            return self._render_steps()
        return self._render_bar()

    def _render_bar(self) -> RenderableType:
        """Render progress bar."""
        value = max(0, min(100, self.state.value if self.state else 0))

        table = Table.grid(padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(width=6, justify="right")

        if self.state and self.state.label:
            table.add_row(Text(self.state.label, style="bold"), Text(f"{value}%"))

        bar = ProgressBar(
            total=100,
            completed=value,
            complete_style="blue",
            finished_style="green",
        )
        table.add_row(bar, "")

        return table

    def _render_steps(self) -> RenderableType:
        """Render step indicator."""
        if not self.state or not self.state.steps:
            return Text("No steps defined")

        table = Table.grid(padding=(0, 2))
        for _ in self.state.steps:
            table.add_column(justify="center")

        # Step circles
        circles = []
        for i, step in enumerate(self.state.steps):
            if step.completed:
                circles.append(Text("✓", style="bold green"))
            elif step.current:
                circles.append(Text(str(i + 1), style="bold blue"))
            else:
                circles.append(Text(str(i + 1), style="dim"))

        table.add_row(*circles)

        # Step labels
        labels = []
        for step in self.state.steps:
            style = "bold" if step.current else ("green" if step.completed else "dim")
            labels.append(Text(step.label, style=style))

        table.add_row(*labels)

        return table

    def render(self) -> RenderableType:
        """Render the widget."""
        return self.render_content()


class TUIProgressBar(Static):
    """
    Simple progress bar for quick rendering.

    Use this when you don't need full TUIWidget features.
    """

    def __init__(self, value: int = 0, label: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._value = max(0, min(100, value))
        self._label = label

    def render(self) -> RenderableType:
        table = Table.grid(padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(width=6, justify="right")

        if self._label:
            table.add_row(Text(self._label, style="bold"), Text(f"{self._value}%"))

        bar = ProgressBar(total=100, completed=self._value)
        table.add_row(bar, "")

        return table

    def update_progress(self, value: int, label: str | None = None) -> None:
        """Update progress value and optionally label."""
        self._value = max(0, min(100, value))
        if label is not None:
            self._label = label
        self.refresh()
