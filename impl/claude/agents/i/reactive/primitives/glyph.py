"""
GlyphWidget: The atomic visual unit.

Everything composes from Glyphs. A Glyph:
- Has deterministic visual state (no randomness in render)
- Responds to entropy with graceful distortion
- Carries semantic meaning through phase
- Time (t) is passed from parent, not managed internally

This is the bottom of the composition stack.
All primitives (Bar, Grid, Tree) compose FROM glyphs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.composable import ComposableMixin
from agents.i.reactive.entropy import (
    PHASE_GLYPHS,
    distortion_to_css,
    entropy_to_distortion,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from agents.i.reactive.entropy import VisualDistortion

Phase = Literal[
    "idle", "active", "waiting", "error", "yielding", "thinking", "complete"
]
Animation = Literal["none", "pulse", "blink", "breathe", "wiggle"]


@dataclass(frozen=True)
class GlyphState:
    """
    Immutable glyph state.

    All visual properties are deterministic from this state.
    The glyph doesn't manage its own time - t is passed from parent.
    """

    char: str = "·"
    fg: str | None = None
    bg: str | None = None
    phase: Phase | None = None
    entropy: float = 0.0
    seed: int = 0
    t: float = 0.0
    animate: Animation = "none"


class GlyphWidget(ComposableMixin, KgentsWidget[GlyphState]):
    """
    The atomic visual unit.

    Everything renders to glyphs. Glyphs compose into Bars, Bars into Cards,
    Cards into Screens.

    A Glyph:
    - Has deterministic visual state (no randomness in render)
    - Responds to entropy with graceful distortion
    - Carries semantic meaning through phase
    - Time (t) is passed from parent, not managed internally

    Example:
        glyph = GlyphWidget(GlyphState(
            char="◉",
            phase="active",
            entropy=0.3,
            seed=42,
            t=time.time() * 1000,  # milliseconds
        ))

        # Render to different targets
        print(glyph.project(RenderTarget.CLI))  # "◉"
        print(glyph.project(RenderTarget.JSON))  # {"type": "glyph", "char": "◉", ...}
    """

    state: Signal[GlyphState]

    def __init__(self, initial: GlyphState | None = None) -> None:
        self.state = Signal.of(initial or GlyphState())

    @classmethod
    def from_signal(cls, signal: Signal[GlyphState]) -> GlyphWidget:
        """
        Create a GlyphWidget that subscribes to an external Signal.

        The widget's state tracks the external signal, enabling
        reactive composition where state changes propagate automatically.

        Args:
            signal: External Signal[GlyphState] to subscribe to

        Returns:
            GlyphWidget bound to the external signal

        Example:
            state_signal = Signal.of(GlyphState(char="X"))
            glyph = GlyphWidget.from_signal(state_signal)
            state_signal.set(GlyphState(char="Y"))  # glyph updates
        """
        widget = cls.__new__(cls)
        widget.state = signal
        return widget

    def with_time(self, t: float) -> GlyphWidget:
        """
        Return new glyph with updated time. Immutable pattern.

        Time flows downward from parent. This method creates a new
        widget with the updated time for rendering.

        Args:
            t: Time in milliseconds

        Returns:
            New GlyphWidget with updated t
        """
        current = self.state.value
        new_state = GlyphState(
            char=current.char,
            fg=current.fg,
            bg=current.bg,
            phase=current.phase,
            entropy=current.entropy,
            seed=current.seed,
            t=t,
            animate=current.animate,
        )
        return GlyphWidget(new_state)

    def with_entropy(self, entropy: float) -> GlyphWidget:
        """Return new glyph with updated entropy."""
        current = self.state.value
        new_state = GlyphState(
            char=current.char,
            fg=current.fg,
            bg=current.bg,
            phase=current.phase,
            entropy=entropy,
            seed=current.seed,
            t=current.t,
            animate=current.animate,
        )
        return GlyphWidget(new_state)

    def with_phase(self, phase: Phase) -> GlyphWidget:
        """Return new glyph with updated phase."""
        current = self.state.value
        new_state = GlyphState(
            char=current.char,
            fg=current.fg,
            bg=current.bg,
            phase=phase,
            entropy=current.entropy,
            seed=current.seed,
            t=current.t,
            animate=current.animate,
        )
        return GlyphWidget(new_state)

    def _resolve_char(self, state: GlyphState) -> str:
        """Resolve the display character based on state."""
        # If phase is set and char is default, use phase glyph
        if state.phase and state.char == "·":
            return PHASE_GLYPHS.get(state.phase, state.char)
        return state.char

    def _compute_distortion(self, state: GlyphState) -> VisualDistortion | None:
        """Compute visual distortion if entropy exceeds threshold."""
        if state.entropy > 0.1:
            return entropy_to_distortion(state.entropy, state.seed, state.t)
        return None

    def project(self, target: RenderTarget) -> Any:
        """
        Project this glyph to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (just the character)
            - TUI: rich.text.Text with styling
            - MARIMO: HTML span string
            - JSON: dict with full glyph data
        """
        state = self.state.value
        char = self._resolve_char(state)
        distortion = self._compute_distortion(state)

        match target:
            case RenderTarget.CLI:
                return self._to_cli(char)
            case RenderTarget.TUI:
                return self._to_tui(char, state, distortion)
            case RenderTarget.MARIMO:
                return self._to_marimo(char, state, distortion)
            case RenderTarget.JSON:
                return self._to_json(char, state, distortion)

    def _to_cli(self, char: str) -> str:
        """CLI projection: just the character."""
        return char

    def _to_tui(
        self,
        char: str,
        state: GlyphState,
        distortion: VisualDistortion | None,
    ) -> Any:
        """TUI projection: Rich Text with styling."""
        try:
            from rich.text import Text

            # Build style string
            style_parts = []
            if state.fg:
                style_parts.append(state.fg)
            if state.bg:
                style_parts.append(f"on {state.bg}")
            if distortion and distortion.pulse > 1.1:
                style_parts.append("bold")
            elif distortion and distortion.blur > 1.0:
                style_parts.append("dim")

            style = " ".join(style_parts) if style_parts else ""
            return Text(char, style=style)
        except ImportError:
            # Fallback if rich not available
            return char

    def _to_marimo(
        self,
        char: str,
        state: GlyphState,
        distortion: VisualDistortion | None,
    ) -> str:
        """MARIMO projection: HTML span with CSS styling."""
        style_parts = []

        # Use explicit color or default to dark for light theme compatibility
        if state.fg:
            style_parts.append(f"color: {state.fg}")
        else:
            style_parts.append("color: #212529")  # Dark text for light backgrounds
        if state.bg:
            style_parts.append(f"background-color: {state.bg}")

        if distortion:
            css = distortion_to_css(distortion)
            style_parts.append(css)

        # Animation class
        anim_class = f"glyph-{state.animate}" if state.animate != "none" else ""

        style = "; ".join(style_parts)
        class_attr = (
            f' class="kgents-glyph {anim_class}"'
            if anim_class
            else ' class="kgents-glyph"'
        )

        return f'<span{class_attr} style="{style}">{char}</span>'

    def _to_json(
        self,
        char: str,
        state: GlyphState,
        distortion: VisualDistortion | None,
    ) -> dict[str, Any]:
        """JSON projection: full glyph data for API."""
        result: dict[str, Any] = {
            "type": "glyph",
            "char": char,
            "phase": state.phase,
            "entropy": state.entropy,
            "animate": state.animate,
        }

        if state.fg:
            result["fg"] = state.fg
        if state.bg:
            result["bg"] = state.bg
        if distortion:
            result["distortion"] = {
                "blur": distortion.blur,
                "skew": distortion.skew,
                "jitter_x": distortion.jitter_x,
                "jitter_y": distortion.jitter_y,
                "pulse": distortion.pulse,
            }

        return result
