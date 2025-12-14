"""
H-gent Cards: Reactive visualizations for introspection output.

Cards for visualizing output from H-gent introspection agents:
- ShadowCard: Display shadow inventory with balance bar (Jung)
- DialecticCard: Display thesis/antithesis/synthesis or tension (Hegel)

These cards make introspection results immediately visual:
- Shadow content appears as a list with integration difficulty
- Balance shows persona vs shadow integration (bar)
- Dialectic steps show thesis -> antithesis -> synthesis
- Productive tension is highlighted when synthesis is premature
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass

Difficulty = Literal["low", "medium", "high"]
CardStyle = Literal["compact", "full", "minimal"]


# === Shadow Card ===


@dataclass(frozen=True)
class ShadowItem:
    """A single shadow content item."""

    content: str
    exclusion_reason: str
    difficulty: Difficulty = "medium"


@dataclass(frozen=True)
class ShadowCardState:
    """
    Immutable shadow card state.

    Displays shadow analysis results from JungAgent.
    """

    title: str = "Shadow Analysis"
    shadow_inventory: tuple[ShadowItem, ...] = ()
    balance: float = 0.5  # 0.0 = all persona, 1.0 = fully integrated
    entropy: float = 0.0  # Visual chaos level
    seed: int = 0
    t: float = 0.0
    style: CardStyle = "full"
    max_items: int = 5  # Max shadow items to display


class ShadowCardWidget(CompositeWidget[ShadowCardState]):
    """
    Shadow inventory visualization card.

    Composes:
    - Header: Title glyph + "Shadow Analysis"
    - Body: List of shadow content items with difficulty indicators
    - Footer: Balance bar (persona <-> integrated)

    Features:
    - Shows shadow content with color-coded difficulty
    - Balance bar shows integration progress
    - Entropy affects visual distortion

    Example:
        card = ShadowCardWidget(ShadowCardState(
            shadow_inventory=(
                ShadowItem("capacity for harm", "helpful identity", "high"),
                ShadowItem("tendency to guess", "accuracy identity", "medium"),
            ),
            balance=0.3,
        ))

        print(card.project(RenderTarget.CLI))
        # [SHADOW] Shadow Analysis
        # * capacity for harm (high)
        #   -> helpful identity
        # * tendency to guess (medium)
        #   -> accuracy identity
        # Balance: [###.......] 0.30
    """

    state: Signal[ShadowCardState]

    def __init__(self, initial: ShadowCardState | None = None) -> None:
        state = initial or ShadowCardState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Header glyph
        self.slots["header_glyph"] = GlyphWidget(
            GlyphState(
                char="◐",  # Half-filled circle for shadow
                entropy=state.entropy,
                seed=state.seed,
                t=state.t,
            )
        )

        # Balance bar
        self.slots["balance_bar"] = BarWidget(
            BarState(
                value=state.balance,
                width=10,
                style="solid",
                entropy=state.entropy,
                seed=state.seed + 1,
                t=state.t,
                label="Balance",
            )
        )

    def with_balance(self, balance: float) -> ShadowCardWidget:
        """Return new card with updated balance. Immutable."""
        current = self.state.value
        return ShadowCardWidget(
            ShadowCardState(
                title=current.title,
                shadow_inventory=current.shadow_inventory,
                balance=max(0.0, min(1.0, balance)),
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                style=current.style,
                max_items=current.max_items,
            )
        )

    def with_time(self, t: float) -> ShadowCardWidget:
        """Return new card with updated time. Immutable."""
        current = self.state.value
        return ShadowCardWidget(
            ShadowCardState(
                title=current.title,
                shadow_inventory=current.shadow_inventory,
                balance=current.balance,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                style=current.style,
                max_items=current.max_items,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project this shadow card to a rendering target."""
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

    def _difficulty_indicator(self, difficulty: Difficulty) -> str:
        """Get visual indicator for difficulty level."""
        indicators = {
            "low": "●",
            "medium": "◐",
            "high": "○",
        }
        return indicators.get(difficulty, "●")

    def _to_cli(self) -> str:
        """CLI projection: multi-line shadow card."""
        state = self.state.value

        # Header
        glyph = self.slots["header_glyph"].project(RenderTarget.CLI)
        lines = [f"{glyph} {state.title}", ""]

        if state.style == "minimal":
            return lines[0]

        # Shadow inventory
        if state.shadow_inventory:
            for item in state.shadow_inventory[: state.max_items]:
                indicator = self._difficulty_indicator(item.difficulty)
                lines.append(f"  {indicator} {item.content} ({item.difficulty})")
                if state.style == "full":
                    lines.append(f"    -> {item.exclusion_reason}")

            if len(state.shadow_inventory) > state.max_items:
                remaining = len(state.shadow_inventory) - state.max_items
                lines.append(f"  ... and {remaining} more")
            lines.append("")
        else:
            lines.append("  No shadow content detected.")
            lines.append("")

        # Balance bar
        balance_bar = self.slots["balance_bar"].project(RenderTarget.CLI)
        lines.append(f"{balance_bar} {state.balance:.2f}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel with styled content."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value
            content = Text()

            # Header
            glyph = self.slots["header_glyph"].project(RenderTarget.TUI)
            if isinstance(glyph, Text):
                content.append_text(glyph)
            else:
                content.append(str(glyph))
            content.append(f" {state.title}\n\n")

            # Shadow inventory
            for item in state.shadow_inventory[: state.max_items]:
                indicator = self._difficulty_indicator(item.difficulty)
                color = {"low": "green", "medium": "yellow", "high": "red"}.get(
                    item.difficulty, "white"
                )
                content.append(f"  {indicator} ", style=color)
                content.append(f"{item.content}\n")
                if state.style == "full":
                    content.append(f"    -> {item.exclusion_reason}\n", style="dim")

            if not state.shadow_inventory:
                content.append("  No shadow content detected.\n", style="dim")

            content.append("\n")

            # Balance bar
            balance_bar = self.slots["balance_bar"].project(RenderTarget.TUI)
            if isinstance(balance_bar, Text):
                content.append_text(balance_bar)
            else:
                content.append(str(balance_bar))
            content.append(f" {state.balance:.2f}")

            return Panel(content, title="[SHADOW]", border_style="magenta")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML card."""
        state = self.state.value

        html = '<div class="kgents-shadow-card" style="font-family: monospace; border: 1px solid #8b5cf6; border-radius: 4px; padding: 8px; background: #1a1a1a;">'

        # Header
        glyph_html = self.slots["header_glyph"].project(RenderTarget.MARIMO)
        html += f'<div style="margin-bottom: 8px; font-weight: bold; color: #8b5cf6;">{glyph_html} {state.title}</div>'

        # Shadow inventory
        html += '<div style="margin-bottom: 8px;">'
        for item in state.shadow_inventory[: state.max_items]:
            color = {"low": "#22c55e", "medium": "#eab308", "high": "#ef4444"}.get(
                item.difficulty, "#fff"
            )
            indicator = self._difficulty_indicator(item.difficulty)
            html += f'<div style="color: {color};">{indicator} {item.content} ({item.difficulty})</div>'
            if state.style == "full":
                html += f'<div style="color: #666; margin-left: 16px;">-> {item.exclusion_reason}</div>'

        if not state.shadow_inventory:
            html += '<div style="color: #666;">No shadow content detected.</div>'
        html += "</div>"

        # Balance bar
        balance_html = self.slots["balance_bar"].project(RenderTarget.MARIMO)
        html += f"<div>{balance_html} {state.balance:.2f}</div>"

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full card data."""
        state = self.state.value
        return {
            "type": "shadow_card",
            "title": state.title,
            "shadow_inventory": [
                {
                    "content": item.content,
                    "exclusion_reason": item.exclusion_reason,
                    "difficulty": item.difficulty,
                }
                for item in state.shadow_inventory
            ],
            "balance": state.balance,
            "entropy": state.entropy,
            "style": state.style,
            "children": {
                "header_glyph": self.slots["header_glyph"].project(RenderTarget.JSON),
                "balance_bar": self.slots["balance_bar"].project(RenderTarget.JSON),
            },
        }


# === Dialectic Card ===


@dataclass(frozen=True)
class DialecticCardState:
    """
    Immutable dialectic card state.

    Displays dialectic synthesis results from HegelAgent.
    """

    thesis: str = ""
    antithesis: str | None = None
    synthesis: str | None = None
    productive_tension: bool = False
    sublation_notes: str = ""
    entropy: float = 0.0
    seed: int = 0
    t: float = 0.0
    style: CardStyle = "full"


class DialecticCardWidget(CompositeWidget[DialecticCardState]):
    """
    Dialectic synthesis visualization card.

    Shows:
    - Thesis: the starting position
    - Antithesis: the opposing position (surfaced or provided)
    - Synthesis: the unified insight (if achieved)
    - OR: Productive tension indication (if synthesis is premature)

    Features:
    - Visual arrows showing dialectic flow
    - Color coding: thesis (blue), antithesis (red), synthesis (green)
    - Tension held indicator when synthesis would be premature

    Example:
        card = DialecticCardWidget(DialecticCardState(
            thesis="move fast",
            antithesis="be thorough",
            synthesis="iterative refinement",
            sublation_notes="Speed when exploring, thorough when shipping",
        ))

        print(card.project(RenderTarget.CLI))
        # [DIALECTIC] Synthesis
        # ┌ Thesis: move fast
        # ├ Antithesis: be thorough
        # └ Synthesis: iterative refinement
        # Speed when exploring, thorough when shipping
    """

    state: Signal[DialecticCardState]

    def __init__(self, initial: DialecticCardState | None = None) -> None:
        state = initial or DialecticCardState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Header glyph - different for tension vs synthesis
        char = "⚡" if state.productive_tension else "⚛"
        self.slots["header_glyph"] = GlyphWidget(
            GlyphState(
                char=char,
                entropy=state.entropy,
                seed=state.seed,
                t=state.t,
            )
        )

    def with_time(self, t: float) -> DialecticCardWidget:
        """Return new card with updated time. Immutable."""
        current = self.state.value
        return DialecticCardWidget(
            DialecticCardState(
                thesis=current.thesis,
                antithesis=current.antithesis,
                synthesis=current.synthesis,
                productive_tension=current.productive_tension,
                sublation_notes=current.sublation_notes,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                style=current.style,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project this dialectic card to a rendering target."""
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
        """CLI projection: multi-line dialectic card."""
        state = self.state.value

        glyph = self.slots["header_glyph"].project(RenderTarget.CLI)
        title = "Tension Held" if state.productive_tension else "Synthesis"
        lines = [f"{glyph} {title}", ""]

        if state.style == "minimal":
            return lines[0]

        # Thesis
        lines.append(f"┌ Thesis: {state.thesis}")

        # Antithesis
        if state.antithesis:
            lines.append(f"├ Antithesis: {state.antithesis}")

        # Synthesis or tension
        if state.productive_tension:
            lines.append("└ [Tension held - no synthesis forced]")
        elif state.synthesis:
            lines.append(f"└ Synthesis: {state.synthesis}")

        # Sublation notes
        if state.sublation_notes and state.style == "full":
            lines.append("")
            lines.append(f"  {state.sublation_notes}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel with styled content."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value
            content = Text()

            # Header
            glyph = self.slots["header_glyph"].project(RenderTarget.TUI)
            if isinstance(glyph, Text):
                content.append_text(glyph)
            else:
                content.append(str(glyph))

            title = "Tension Held" if state.productive_tension else "Synthesis"
            content.append(f" {title}\n\n")

            # Thesis (blue)
            content.append("┌ Thesis: ", style="bold")
            content.append(f"{state.thesis}\n", style="cyan")

            # Antithesis (red)
            if state.antithesis:
                content.append("├ Antithesis: ", style="bold")
                content.append(f"{state.antithesis}\n", style="red")

            # Synthesis or tension
            if state.productive_tension:
                content.append("└ ", style="bold")
                content.append("[Tension held - no synthesis forced]\n", style="yellow")
            elif state.synthesis:
                content.append("└ Synthesis: ", style="bold")
                content.append(f"{state.synthesis}\n", style="green")

            # Sublation notes
            if state.sublation_notes and state.style == "full":
                content.append(f"\n  {state.sublation_notes}", style="dim")

            border_color = "yellow" if state.productive_tension else "green"
            return Panel(content, title="[DIALECTIC]", border_style=border_color)

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML card."""
        state = self.state.value

        border_color = "#eab308" if state.productive_tension else "#22c55e"
        html = f'<div class="kgents-dialectic-card" style="font-family: monospace; border: 1px solid {border_color}; border-radius: 4px; padding: 8px; background: #1a1a1a;">'

        # Header
        glyph_html = self.slots["header_glyph"].project(RenderTarget.MARIMO)
        title = "Tension Held" if state.productive_tension else "Synthesis"
        html += f'<div style="margin-bottom: 8px; font-weight: bold; color: {border_color};">{glyph_html} {title}</div>'

        # Thesis
        html += f'<div style="color: #06b6d4;">┌ Thesis: {state.thesis}</div>'

        # Antithesis
        if state.antithesis:
            html += (
                f'<div style="color: #ef4444;">├ Antithesis: {state.antithesis}</div>'
            )

        # Synthesis or tension
        if state.productive_tension:
            html += '<div style="color: #eab308;">└ [Tension held - no synthesis forced]</div>'
        elif state.synthesis:
            html += f'<div style="color: #22c55e;">└ Synthesis: {state.synthesis}</div>'

        # Sublation notes
        if state.sublation_notes and state.style == "full":
            html += f'<div style="color: #666; margin-top: 8px;">  {state.sublation_notes}</div>'

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full card data."""
        state = self.state.value
        return {
            "type": "dialectic_card",
            "thesis": state.thesis,
            "antithesis": state.antithesis,
            "synthesis": state.synthesis,
            "productive_tension": state.productive_tension,
            "sublation_notes": state.sublation_notes,
            "entropy": state.entropy,
            "style": state.style,
            "children": {
                "header_glyph": self.slots["header_glyph"].project(RenderTarget.JSON),
            },
        }
