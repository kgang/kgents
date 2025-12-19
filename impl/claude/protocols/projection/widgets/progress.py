"""
ProgressWidget: Progress bars and step indicators.

Supports multiple variants:
- BAR: Traditional progress bar
- RING: Circular progress (web only, falls back to bar)
- STEPS: Multi-step progress with labels
- INDETERMINATE: Unknown progress (spinner/pulse)

Example:
    widget = ProgressWidget(ProgressWidgetState(
        value=0.65,
        variant=ProgressVariant.BAR,
        label="Uploading...",
        show_percentage=True
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


class ProgressVariant(Enum):
    """Progress indicator variants."""

    BAR = auto()  # Horizontal bar
    RING = auto()  # Circular (web only)
    STEPS = auto()  # Multi-step with labels
    INDETERMINATE = auto()  # Unknown progress


@dataclass(frozen=True)
class ProgressStep:
    """
    Single step in a multi-step progress.

    Attributes:
        label: Step label
        status: Step status (pending/active/complete/error)
    """

    label: str
    status: Literal["pending", "active", "complete", "error"] = "pending"


@dataclass(frozen=True)
class ProgressWidgetState:
    """
    Immutable progress widget state.

    Attributes:
        value: Progress 0.0-1.0, or -1 for indeterminate
        variant: Visual variant
        label: Optional label text
        show_percentage: Show percentage number
        steps: Steps for STEPS variant
        color: Optional color override
    """

    value: float  # 0.0-1.0, or -1 for indeterminate
    variant: ProgressVariant = ProgressVariant.BAR
    label: str | None = None
    show_percentage: bool = True
    steps: tuple[ProgressStep, ...] = ()
    color: str | None = None

    @property
    def is_indeterminate(self) -> bool:
        """Whether progress is indeterminate."""
        return self.value < 0 or self.variant == ProgressVariant.INDETERMINATE

    @property
    def percentage(self) -> int:
        """Progress as percentage (0-100)."""
        if self.is_indeterminate:
            return 0
        return int(self.value * 100)

    def with_value(self, value: float) -> ProgressWidgetState:
        """Return new state with updated value."""
        return ProgressWidgetState(
            value=value,
            variant=self.variant,
            label=self.label,
            show_percentage=self.show_percentage,
            steps=self.steps,
            color=self.color,
        )


class ProgressWidget(KgentsWidget[ProgressWidgetState]):
    """
    Progress indicator widget.

    Projections:
        - CLI: ASCII bar or step list
        - TUI: Rich Progress or step display
        - MARIMO: HTML progress bar
        - JSON: State dict for API responses
    """

    def __init__(self, state: ProgressWidgetState | None = None) -> None:
        self.state = Signal.of(state or ProgressWidgetState(value=0, variant=ProgressVariant.BAR))

    def project(self, target: RenderTarget) -> Any:
        """Project progress to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: ASCII progress."""
        s = self.state.value

        if s.variant == ProgressVariant.STEPS:
            return self._steps_to_cli()

        # Bar or indeterminate
        width = 20
        label = s.label or ""

        if s.is_indeterminate:
            # Spinning animation represented as [<=>]
            return f"{label} [<=>]"

        filled = int(width * s.value)
        empty = width - filled
        bar = "█" * filled + "░" * empty

        percentage = f" {s.percentage}%" if s.show_percentage else ""
        return f"{label} [{bar}]{percentage}"

    def _steps_to_cli(self) -> str:
        """Render steps variant for CLI."""
        s = self.state.value
        lines = []

        for i, step in enumerate(s.steps, 1):
            status_char = {
                "pending": "○",
                "active": "◉",
                "complete": "●",
                "error": "✗",
            }.get(step.status, "○")

            connector = "───" if i < len(s.steps) else ""
            lines.append(f"{status_char} {step.label} {connector}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Progress bar."""
        try:
            from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
            from rich.text import Text

            s = self.state.value

            if s.variant == ProgressVariant.STEPS:
                # Steps as Rich Text
                lines = []
                for step in s.steps:
                    style = {
                        "pending": "dim",
                        "active": "bold yellow",
                        "complete": "green",
                        "error": "red",
                    }.get(step.status, "")
                    lines.append(Text(f"• {step.label}", style=style))
                return Text("\n").join(lines)

            # Progress bar
            if s.is_indeterminate:
                return Text(f"{s.label or ''} [spinning...]", style="yellow")

            bar = "█" * int(20 * s.value) + "░" * (20 - int(20 * s.value))
            percentage = f" {s.percentage}%" if s.show_percentage else ""
            return Text(f"{s.label or ''} [{bar}]{percentage}")

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML progress."""
        s = self.state.value

        if s.variant == ProgressVariant.STEPS:
            return self._steps_to_marimo()

        label_html = f'<span class="kgents-progress-label">{s.label}</span>' if s.label else ""
        percentage_html = (
            f'<span class="kgents-progress-percentage">{s.percentage}%</span>'
            if s.show_percentage
            else ""
        )

        if s.is_indeterminate:
            return f"""
            <div class="kgents-progress kgents-progress-indeterminate">
                {label_html}
                <progress class="kgents-progress-bar"></progress>
            </div>
            """

        color_style = f"--progress-color: {s.color};" if s.color else ""
        return f"""
        <div class="kgents-progress" style="{color_style}">
            {label_html}
            <progress class="kgents-progress-bar" value="{s.value}" max="1"></progress>
            {percentage_html}
        </div>
        """

    def _steps_to_marimo(self) -> str:
        """Render steps variant for marimo."""
        s = self.state.value
        items = []

        for step in s.steps:
            status_class = f"kgents-step-{step.status}"
            items.append(f'<li class="kgents-step {status_class}">{step.label}</li>')

        return f'<ol class="kgents-progress-steps">{"".join(items)}</ol>'

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "progress",
            "value": s.value,
            "variant": s.variant.name.lower(),
            "label": s.label,
            "showPercentage": s.show_percentage,
            "steps": [{"label": step.label, "status": step.status} for step in s.steps],
            "color": s.color,
            "isIndeterminate": s.is_indeterminate,
            "percentage": s.percentage,
        }


__all__ = ["ProgressWidget", "ProgressWidgetState", "ProgressVariant", "ProgressStep"]
