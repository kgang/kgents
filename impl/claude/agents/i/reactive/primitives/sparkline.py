"""
SparklineWidget: Time-series mini-chart visualization.

A Sparkline shows history as a compact horizontal chart using
vertical bar characters. Perfect for:
- CPU/memory usage over time
- Request latency trends
- Agent activity history
- Temperature/pressure readings

The sparkline composes from glyphs, each representing a data point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from agents.i.reactive.entropy import SPARK_CHARS, entropy_to_distortion
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class SparklineState:
    """
    Immutable sparkline state.

    Values is a tuple (immutable) of floats representing the time series.
    Each value is normalized to 0.0-1.0 range.
    """

    values: tuple[float, ...] = ()  # Time series data (0.0-1.0 each)
    max_length: int = 20  # Maximum history length
    fg: str | None = None  # Foreground color
    bg: str | None = None  # Background color
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Time in milliseconds
    label: str | None = None  # Optional label
    show_bounds: bool = False  # Show min/max values


class SparklineWidget(KgentsWidget[SparklineState]):
    """
    A sparkline visualization for time-series data.

    Shows a compact history chart using vertical bar characters.
    Each position represents a data point, with height indicating value.

    Features:
    - Configurable history length (max_length)
    - Auto-scrolling (oldest values drop off)
    - Entropy-based visual distortion
    - Optional min/max bounds display

    The sparkline characters: ▁▂▃▄▅▆▇█

    Example:
        spark = SparklineWidget(SparklineState(
            values=(0.1, 0.3, 0.5, 0.8, 0.6, 0.4),
            max_length=20,
        ))

        print(spark.project(RenderTarget.CLI))  # "▁▂▄▇▅▃"

        # Add new value
        new_spark = spark.push(0.9)
        print(new_spark.project(RenderTarget.CLI))  # "▁▂▄▇▅▃█"
    """

    state: Signal[SparklineState]

    def __init__(self, initial: SparklineState | None = None) -> None:
        self.state = Signal.of(initial or SparklineState())

    def push(self, value: float) -> SparklineWidget:
        """
        Push a new value, returning new sparkline. Immutable.

        If at max_length, oldest value is dropped.
        """
        current = self.state.value
        clamped = max(0.0, min(1.0, value))

        # Append and trim to max_length
        new_values = (*current.values, clamped)
        if len(new_values) > current.max_length:
            new_values = new_values[-current.max_length :]

        return SparklineWidget(
            SparklineState(
                values=new_values,
                max_length=current.max_length,
                fg=current.fg,
                bg=current.bg,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                label=current.label,
                show_bounds=current.show_bounds,
            )
        )

    def with_values(self, values: tuple[float, ...] | list[float]) -> SparklineWidget:
        """Replace all values. Immutable."""
        current = self.state.value
        normalized = tuple(max(0.0, min(1.0, v)) for v in values)
        trimmed = normalized[-current.max_length :]

        return SparklineWidget(
            SparklineState(
                values=trimmed,
                max_length=current.max_length,
                fg=current.fg,
                bg=current.bg,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                label=current.label,
                show_bounds=current.show_bounds,
            )
        )

    def with_time(self, t: float) -> SparklineWidget:
        """Return new sparkline with updated time. Immutable."""
        current = self.state.value
        return SparklineWidget(
            SparklineState(
                values=current.values,
                max_length=current.max_length,
                fg=current.fg,
                bg=current.bg,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                label=current.label,
                show_bounds=current.show_bounds,
            )
        )

    def with_entropy(self, entropy: float) -> SparklineWidget:
        """Return new sparkline with updated entropy. Immutable."""
        current = self.state.value
        return SparklineWidget(
            SparklineState(
                values=current.values,
                max_length=current.max_length,
                fg=current.fg,
                bg=current.bg,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
                t=current.t,
                label=current.label,
                show_bounds=current.show_bounds,
            )
        )

    def _value_to_spark(self, value: float) -> str:
        """Map a value (0.0-1.0) to a spark character."""
        idx = int(value * (len(SPARK_CHARS) - 1))
        return SPARK_CHARS[min(idx, len(SPARK_CHARS) - 1)]

    def _build_glyphs(self) -> list[GlyphWidget]:
        """Build glyph array for this sparkline."""
        state = self.state.value
        glyphs: list[GlyphWidget] = []

        for i, value in enumerate(state.values):
            char = self._value_to_spark(value)
            glyph_seed = state.seed + i

            glyph_state = GlyphState(
                char=char,
                fg=state.fg,
                bg=state.bg,
                entropy=state.entropy,
                seed=glyph_seed,
                t=state.t,
            )
            glyphs.append(GlyphWidget(glyph_state))

        return glyphs

    def project(self, target: RenderTarget) -> Any:
        """
        Project this sparkline to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (sparkline as ASCII)
            - TUI: Rich Text
            - MARIMO: HTML div with spans
            - JSON: dict with sparkline data
        """
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
        """CLI projection: sparkline as ASCII string."""
        state = self.state.value

        if not state.values:
            return "─" * min(state.max_length, 10)  # Empty placeholder

        glyphs = self._build_glyphs()
        chars = [g.project(RenderTarget.CLI) for g in glyphs]
        result = "".join(chars)

        if state.show_bounds and state.values:
            min_val = min(state.values)
            max_val = max(state.values)
            result = f"[{min_val:.2f}-{max_val:.2f}] {result}"

        if state.label:
            result = f"{state.label}: {result}"

        return result

    def _to_tui(self) -> Any:
        """TUI projection: Rich Text with styling."""
        try:
            from rich.text import Text

            glyphs = self._build_glyphs()
            result = Text()

            for glyph in glyphs:
                glyph_text = glyph.project(RenderTarget.TUI)
                if isinstance(glyph_text, Text):
                    result.append_text(glyph_text)
                else:
                    result.append(str(glyph_text))

            return result
        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML div with glyph spans."""
        state = self.state.value
        glyphs = self._build_glyphs()

        spans = [g.project(RenderTarget.MARIMO) for g in glyphs]

        html = '<div class="kgents-sparkline" style="display: inline-flex; font-family: monospace; align-items: flex-end;">'
        html += "".join(spans)
        html += "</div>"

        if state.label:
            html = f'<div class="kgents-sparkline-container" style="color: #212529;"><span class="kgents-sparkline-label">{state.label}: </span>{html}</div>'

        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full sparkline data."""
        state = self.state.value
        glyphs = self._build_glyphs()

        result: dict[str, Any] = {
            "type": "sparkline",
            "values": list(state.values),
            "max_length": state.max_length,
            "entropy": state.entropy,
            "glyphs": [g.project(RenderTarget.JSON) for g in glyphs],
        }

        if state.values:
            result["min"] = min(state.values)
            result["max"] = max(state.values)
            result["current"] = state.values[-1] if state.values else None

        if state.label:
            result["label"] = state.label
        if state.fg:
            result["fg"] = state.fg
        if state.bg:
            result["bg"] = state.bg
        if state.entropy > 0.1:
            result["distortion"] = entropy_to_distortion(
                state.entropy, state.seed, state.t
            )

        return result
