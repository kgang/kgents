"""
YieldCardWidget: Agent output/yield display.

A YieldCard represents an agent's output - a thought, action, or artifact.
It composes:
- Type indicator glyph (thought, action, artifact)
- Content preview with entropy-based emphasis
- Timestamp and source agent reference
- Importance bar (entropy-based visual weight)

Yields are the "sentences" agents speak to the world.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.entropy import entropy_to_distortion
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    from protocols.projection.schema import UIHint

YieldType = Literal["thought", "action", "artifact", "error", "yield"]

# Glyph mapping for yield types
YIELD_GLYPHS: dict[YieldType, str] = {
    "thought": "💭",
    "action": "⚡",
    "artifact": "📦",
    "error": "⚠",
    "yield": "◇",
}

# ASCII fallback glyphs
YIELD_GLYPHS_ASCII: dict[YieldType, str] = {
    "thought": "?",
    "action": "!",
    "artifact": "#",
    "error": "X",
    "yield": "*",
}


@dataclass(frozen=True)
class YieldCardState:
    """
    Immutable yield card state.

    All visual properties derive deterministically from this state.
    """

    yield_id: str = "yield"
    source_agent: str = "agent"
    yield_type: YieldType = "yield"
    content: str = ""
    importance: float = 0.5  # 0.0-1.0, visual weight/emphasis
    timestamp: float = 0.0  # When this yield was produced
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Current time for animation
    max_content_length: int = 50  # Truncate content preview
    use_emoji: bool = True  # Use emoji glyphs (False = ASCII)


class YieldCardWidget(CompositeWidget[YieldCardState]):
    """
    Agent output/yield display as a composed card.

    Composes:
    - GlyphWidget (type indicator: thought/action/artifact)
    - BarWidget (importance/emphasis indicator)

    Features:
    - Type-specific glyph (thought, action, artifact, error)
    - Content preview with truncation
    - Importance bar for visual weight
    - Entropy-based distortion on high-importance yields
    - Source agent reference

    Example:
        yield_card = YieldCardWidget(YieldCardState(
            yield_id="yield-001",
            source_agent="kgent-1",
            yield_type="action",
            content="Executing database query...",
            importance=0.8,
            timestamp=1702500000.0,
        ))

        print(yield_card.project(RenderTarget.CLI))
        # ⚡ Executing database query...
        # ████████░░
    """

    state: Signal[YieldCardState]

    def __init__(self, initial: YieldCardState | None = None) -> None:
        state = initial or YieldCardState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Determine glyph character based on type and emoji preference
        glyph_map = YIELD_GLYPHS if state.use_emoji else YIELD_GLYPHS_ASCII
        glyph_char = glyph_map.get(state.yield_type, "·")

        # Type indicator glyph
        # Scale entropy by importance for high-importance yields
        glyph_entropy = state.entropy + (state.importance * 0.2)
        self.slots["type_glyph"] = GlyphWidget(
            GlyphState(
                char=glyph_char,
                entropy=min(1.0, glyph_entropy),
                seed=state.seed,
                t=state.t,
                animate="pulse" if state.importance > 0.8 else "none",
            )
        )

        # Importance bar
        self.slots["importance"] = BarWidget(
            BarState(
                value=state.importance,
                width=10,
                style="solid",
                entropy=state.entropy,
                seed=state.seed + 1,
                t=state.t,
            )
        )

    def with_content(self, content: str) -> YieldCardWidget:
        """Return new card with updated content. Immutable."""
        current = self.state.value
        return YieldCardWidget(
            YieldCardState(
                yield_id=current.yield_id,
                source_agent=current.source_agent,
                yield_type=current.yield_type,
                content=content,
                importance=current.importance,
                timestamp=current.timestamp,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                max_content_length=current.max_content_length,
                use_emoji=current.use_emoji,
            )
        )

    def with_importance(self, importance: float) -> YieldCardWidget:
        """Return new card with updated importance. Immutable."""
        current = self.state.value
        return YieldCardWidget(
            YieldCardState(
                yield_id=current.yield_id,
                source_agent=current.source_agent,
                yield_type=current.yield_type,
                content=current.content,
                importance=max(0.0, min(1.0, importance)),
                timestamp=current.timestamp,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                max_content_length=current.max_content_length,
                use_emoji=current.use_emoji,
            )
        )

    def with_type(self, yield_type: YieldType) -> YieldCardWidget:
        """Return new card with updated yield type. Immutable."""
        current = self.state.value
        return YieldCardWidget(
            YieldCardState(
                yield_id=current.yield_id,
                source_agent=current.source_agent,
                yield_type=yield_type,
                content=current.content,
                importance=current.importance,
                timestamp=current.timestamp,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                max_content_length=current.max_content_length,
                use_emoji=current.use_emoji,
            )
        )

    def with_time(self, t: float) -> YieldCardWidget:
        """Return new card with updated time. Immutable."""
        current = self.state.value
        return YieldCardWidget(
            YieldCardState(
                yield_id=current.yield_id,
                source_agent=current.source_agent,
                yield_type=current.yield_type,
                content=current.content,
                importance=current.importance,
                timestamp=current.timestamp,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                max_content_length=current.max_content_length,
                use_emoji=current.use_emoji,
            )
        )

    def with_entropy(self, entropy: float) -> YieldCardWidget:
        """Return new card with updated entropy. Immutable."""
        current = self.state.value
        return YieldCardWidget(
            YieldCardState(
                yield_id=current.yield_id,
                source_agent=current.source_agent,
                yield_type=current.yield_type,
                content=current.content,
                importance=current.importance,
                timestamp=current.timestamp,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
                t=current.t,
                max_content_length=current.max_content_length,
                use_emoji=current.use_emoji,
            )
        )

    def _truncate_content(self) -> str:
        """Get truncated content preview."""
        state = self.state.value
        content = state.content
        if len(content) > state.max_content_length:
            return content[: state.max_content_length - 3] + "..."
        return content

    def project(self, target: RenderTarget) -> Any:
        """
        Project this yield card to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (multi-line ASCII card)
            - TUI: Rich Text or Panel
            - MARIMO: HTML div with styled children
            - JSON: dict with card data and child projections
        """
        # Rebuild slots to reflect current state
        self._rebuild_slots()

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
        """CLI projection: multi-line ASCII card."""
        state = self.state.value

        # Header: type glyph + content
        glyph = self.slots["type_glyph"].project(RenderTarget.CLI)
        content = self._truncate_content()
        header = f"{glyph} {content}"

        # Only show importance bar for important yields
        if state.importance > 0.3:
            importance = self.slots["importance"].project(RenderTarget.CLI)
            return f"{header}\n{importance}"

        return header

    def _to_tui(self) -> Any:
        """TUI projection: Rich Text with styling."""
        try:
            from rich.text import Text

            state = self.state.value

            # Build content
            result = Text()

            # Type glyph
            glyph = self.slots["type_glyph"].project(RenderTarget.TUI)
            if isinstance(glyph, Text):
                result.append_text(glyph)
            else:
                result.append(str(glyph))

            # Content with style based on importance
            content = self._truncate_content()
            style = "bold" if state.importance > 0.7 else ""
            result.append(f" {content}", style=style)

            # Source reference
            result.append(f" [{state.source_agent}]", style="dim")

            if state.importance > 0.3:
                result.append("\n")
                importance = self.slots["importance"].project(RenderTarget.TUI)
                if isinstance(importance, Text):
                    result.append_text(importance)
                else:
                    result.append(str(importance))

            return result

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML div with styled children."""
        state = self.state.value

        # Get child projections
        glyph_html = str(self.slots["type_glyph"].project(RenderTarget.MARIMO))
        importance_html = str(self.slots["importance"].project(RenderTarget.MARIMO))

        content = self._truncate_content()

        # Card container style - varies by importance
        border_color = "#666" if state.importance < 0.5 else "#f80"
        bg_color = "#1a1a1a" if state.importance < 0.8 else "#2a1a1a"

        card_style = (
            f"font-family: monospace; "
            f"border-left: 3px solid {border_color}; "
            f"padding: 6px 8px; "
            f"margin: 4px 0; "
            f"background: {bg_color};"
        )

        html = (
            f'<div class="kgents-yield-card" data-yield-id="{state.yield_id}" style="{card_style}">'
        )

        # Header line
        html += '<div class="kgents-yield-header" style="display: flex; align-items: center;">'
        html += glyph_html

        # Content with emphasis based on importance
        content_style = "margin-left: 6px;"
        if state.importance > 0.7:
            content_style += " font-weight: bold;"

        html += f'<span class="kgents-yield-content" style="{content_style}">{content}</span>'

        # Source reference
        html += f'<span class="kgents-yield-source" style="margin-left: auto; color: #666; font-size: 0.9em;">[{state.source_agent}]</span>'
        html += "</div>"

        # Importance bar for important yields
        if state.importance > 0.3:
            html += '<div class="kgents-yield-importance" style="margin-top: 4px;">'
            html += importance_html
            html += "</div>"

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full card data."""
        state = self.state.value

        result: dict[str, Any] = {
            "type": "yield_card",
            "yield_id": state.yield_id,
            "source_agent": state.source_agent,
            "yield_type": state.yield_type,
            "content": state.content,
            "content_preview": self._truncate_content(),
            "importance": state.importance,
            "timestamp": state.timestamp,
            "entropy": state.entropy,
            "children": {
                "type_glyph": self.slots["type_glyph"].project(RenderTarget.JSON),
                "importance": self.slots["importance"].project(RenderTarget.JSON),
            },
        }

        if state.entropy > 0.1:
            result["distortion"] = entropy_to_distortion(state.entropy, state.seed, state.t)

        return result

    # =========================================================================
    # Projection Integration
    # =========================================================================

    def ui_hint(self) -> "UIHint":
        """
        Return the UI hint for this widget.

        YieldCards render as "card" type (agent output).
        """
        return "card"

    def widget_type(self) -> str:
        """Override to return 'yield_card' explicitly."""
        return "yield_card"
