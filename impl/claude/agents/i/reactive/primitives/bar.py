"""
BarWidget: Horizontal/vertical bar visualization.

A Bar composes from Glyphs - it's a 1D array of glyphs that represent
progress, capacity, or any scalar value.

Uses:
- Progress bars (loading, completion)
- Capacity meters (memory, CPU)
- Heat indicators (temperature, pressure)
- Health bars (agent vitality)

The bar IS a row/column of glyphs. Composition, not inheritance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.entropy import entropy_to_distortion
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass

Orientation = Literal["horizontal", "vertical"]
BarStyle = Literal["solid", "gradient", "segments", "dots"]

# Bar characters for different styles
BAR_CHARS = {
    "solid": {"empty": "░", "filled": "█", "partial": "▓"},
    "gradient": {"empty": " ", "filled": "█", "chars": "░▒▓█"},
    "segments": {"empty": "○", "filled": "●", "partial": "◐"},
    "dots": {"empty": "·", "filled": "◉", "partial": "○"},
}


@dataclass(frozen=True)
class BarState:
    """
    Immutable bar state.

    All visual properties derive deterministically from this state.
    Time (t) flows from parent for consistent animation.
    """

    value: float = 0.0  # 0.0-1.0, current fill level
    width: int = 10  # Number of glyphs in the bar
    orientation: Orientation = "horizontal"
    style: BarStyle = "solid"
    fg: str | None = None  # Foreground color
    bg: str | None = None  # Background color
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Time in milliseconds
    label: str | None = None  # Optional label


class BarWidget(KgentsWidget[BarState]):
    """
    A bar visualization composed of glyphs.

    The bar is a 1D array of GlyphWidgets. Each glyph's appearance
    depends on whether it's filled, empty, or partial.

    Features:
    - Horizontal or vertical orientation
    - Multiple visual styles (solid, gradient, segments, dots)
    - Entropy-based distortion flows through to child glyphs
    - Time flows down from parent for consistent animation

    Example:
        bar = BarWidget(BarState(
            value=0.75,
            width=20,
            style="gradient",
            entropy=0.3,
        ))

        print(bar.project(RenderTarget.CLI))  # "████████████████░░░░"
    """

    state: Signal[BarState]

    def __init__(self, initial: BarState | None = None) -> None:
        self.state = Signal.of(initial or BarState())

    def with_value(self, value: float) -> BarWidget:
        """Return new bar with updated value. Immutable."""
        current = self.state.value
        return BarWidget(
            BarState(
                value=max(0.0, min(1.0, value)),
                width=current.width,
                orientation=current.orientation,
                style=current.style,
                fg=current.fg,
                bg=current.bg,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                label=current.label,
            )
        )

    def with_time(self, t: float) -> BarWidget:
        """Return new bar with updated time. Immutable."""
        current = self.state.value
        return BarWidget(
            BarState(
                value=current.value,
                width=current.width,
                orientation=current.orientation,
                style=current.style,
                fg=current.fg,
                bg=current.bg,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                label=current.label,
            )
        )

    def with_entropy(self, entropy: float) -> BarWidget:
        """Return new bar with updated entropy. Immutable."""
        current = self.state.value
        return BarWidget(
            BarState(
                value=current.value,
                width=current.width,
                orientation=current.orientation,
                style=current.style,
                fg=current.fg,
                bg=current.bg,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
                t=current.t,
                label=current.label,
            )
        )

    def _build_glyphs(self) -> list[GlyphWidget]:
        """Build the glyph array for this bar."""
        state = self.state.value
        glyphs: list[GlyphWidget] = []
        chars = BAR_CHARS[state.style]

        filled_count = state.value * state.width
        full_filled = int(filled_count)
        partial = filled_count - full_filled

        for i in range(state.width):
            # Determine character based on position
            if i < full_filled:
                char = chars["filled"]
            elif i == full_filled and partial > 0.5:
                char = chars.get("partial", chars["filled"])
            else:
                char = chars["empty"]

            # Create glyph with inherited entropy, slightly varied by position
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
        Project this bar to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (the bar as ASCII art)
            - TUI: Rich Text or list of Text
            - MARIMO: HTML div with spans
            - JSON: dict with bar data and glyph array
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
        """CLI projection: bar as ASCII string."""
        state = self.state.value
        glyphs = self._build_glyphs()
        chars = [g.project(RenderTarget.CLI) for g in glyphs]

        if state.orientation == "vertical":
            return "\n".join(chars)

        result = "".join(chars)
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

        direction = "column" if state.orientation == "vertical" else "row"
        spans = [g.project(RenderTarget.MARIMO) for g in glyphs]

        html = f'<div class="kgents-bar" style="display: flex; flex-direction: {direction}; font-family: monospace;">'
        html += "".join(spans)
        html += "</div>"

        if state.label:
            html = f'<div class="kgents-bar-container"><span class="kgents-bar-label">{state.label}: </span>{html}</div>'

        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full bar data."""
        state = self.state.value
        glyphs = self._build_glyphs()

        result: dict[str, Any] = {
            "type": "bar",
            "value": state.value,
            "width": state.width,
            "orientation": state.orientation,
            "style": state.style,
            "entropy": state.entropy,
            "glyphs": [g.project(RenderTarget.JSON) for g in glyphs],
        }

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
