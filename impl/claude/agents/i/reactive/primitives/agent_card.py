"""
AgentCardWidget: Full agent representation card.

A card is a "paragraph" in our visual language. It composes:
- Header: Glyph (phase indicator) + name
- Body: Sparkline (activity history)
- Footer: Bar (capability/health indicator)

The AgentCard makes agents feel alive. It's the primary unit
for representing an agent's identity and current state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.entropy import entropy_to_distortion
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget, Phase
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    pass

CardStyle = Literal["compact", "full", "minimal"]


@dataclass(frozen=True)
class AgentCardState:
    """
    Immutable agent card state.

    All visual properties derive deterministically from this state.
    Time (t) flows from parent for consistent animation.
    """

    agent_id: str = "agent"
    name: str = "Agent"
    phase: Phase = "idle"
    activity: tuple[float, ...] = ()  # Activity history (0.0-1.0)
    capability: float = 1.0  # Capability/health level (0.0-1.0)
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Time in milliseconds
    style: CardStyle = "full"  # Card display style
    breathing: bool = True  # Enable breathing animation based on activity


class AgentCardWidget(CompositeWidget[AgentCardState]):
    """
    Full agent representation as a composed card.

    Composes:
    - GlyphWidget (header: phase indicator)
    - SparklineWidget (body: activity history)
    - BarWidget (footer: capability/health)

    Features:
    - Agent identity (id, name, phase glyph)
    - Activity visualization (sparkline of recent actions)
    - Capability bar (what the agent can do / health)
    - Entropy-based distortion flows to all children
    - Optional "breathing" effect based on activity level

    Example:
        card = AgentCardWidget(AgentCardState(
            agent_id="kgent-1",
            name="Kent's Assistant",
            phase="active",
            activity=(0.2, 0.4, 0.8, 0.6, 0.9),
            capability=0.85,
            entropy=0.2,
        ))

        print(card.project(RenderTarget.CLI))
        # ◉ Kent's Assistant
        # ▂▃▆▅▇
        # ████████░░

    """

    state: Signal[AgentCardState]

    def __init__(self, initial: AgentCardState | None = None) -> None:
        state = initial or AgentCardState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Header: Phase glyph
        self.slots["phase_glyph"] = GlyphWidget(
            GlyphState(
                phase=state.phase,
                entropy=state.entropy,
                seed=state.seed,
                t=state.t,
                animate="breathe"
                if state.breathing and state.phase == "active"
                else "none",
            )
        )

        # Body: Activity sparkline
        self.slots["activity"] = SparklineWidget(
            SparklineState(
                values=state.activity,
                max_length=20,
                entropy=state.entropy,
                seed=state.seed + 1,
                t=state.t,
            )
        )

        # Footer: Capability bar
        self.slots["capability"] = BarWidget(
            BarState(
                value=state.capability,
                width=10,
                style="solid",
                entropy=state.entropy,
                seed=state.seed + 2,
                t=state.t,
            )
        )

    def with_phase(self, phase: Phase) -> AgentCardWidget:
        """Return new card with updated phase. Immutable."""
        current = self.state.value
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=phase,
                activity=current.activity,
                capability=current.capability,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def with_activity(
        self, activity: tuple[float, ...] | list[float]
    ) -> AgentCardWidget:
        """Return new card with updated activity history. Immutable."""
        current = self.state.value
        normalized = tuple(max(0.0, min(1.0, v)) for v in activity)
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                activity=normalized,
                capability=current.capability,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def push_activity(self, value: float) -> AgentCardWidget:
        """Push a new activity value, returning new card. Immutable."""
        current = self.state.value
        clamped = max(0.0, min(1.0, value))
        new_activity = (*current.activity, clamped)[-20:]  # Keep last 20
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                activity=new_activity,
                capability=current.capability,
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def with_capability(self, capability: float) -> AgentCardWidget:
        """Return new card with updated capability. Immutable."""
        current = self.state.value
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                activity=current.activity,
                capability=max(0.0, min(1.0, capability)),
                entropy=current.entropy,
                seed=current.seed,
                t=current.t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def with_time(self, t: float) -> AgentCardWidget:
        """Return new card with updated time. Immutable."""
        current = self.state.value
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                activity=current.activity,
                capability=current.capability,
                entropy=current.entropy,
                seed=current.seed,
                t=t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def with_entropy(self, entropy: float) -> AgentCardWidget:
        """Return new card with updated entropy. Immutable."""
        current = self.state.value
        return AgentCardWidget(
            AgentCardState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                activity=current.activity,
                capability=current.capability,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
                t=current.t,
                style=current.style,
                breathing=current.breathing,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this agent card to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (multi-line ASCII card)
            - TUI: Rich Panel or Text
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

        # Header: glyph + name
        glyph = self.slots["phase_glyph"].project(RenderTarget.CLI)
        header = f"{glyph} {state.name}"

        if state.style == "minimal":
            return header

        # Body: activity sparkline
        activity = self.slots["activity"].project(RenderTarget.CLI)

        if state.style == "compact":
            return f"{header} {activity}"

        # Full style: multi-line
        capability = self.slots["capability"].project(RenderTarget.CLI)
        return f"{header}\n{activity}\n{capability}"

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel with styled children."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value

            # Build content
            content = Text()

            # Header line: glyph + name
            glyph = self.slots["phase_glyph"].project(RenderTarget.TUI)
            if isinstance(glyph, Text):
                content.append_text(glyph)
            else:
                content.append(str(glyph))
            content.append(f" {state.name}\n")

            if state.style != "minimal":
                # Activity sparkline
                activity = self.slots["activity"].project(RenderTarget.TUI)
                if isinstance(activity, Text):
                    content.append_text(activity)
                else:
                    content.append(str(activity))

                if state.style == "full":
                    content.append("\n")
                    # Capability bar
                    capability = self.slots["capability"].project(RenderTarget.TUI)
                    if isinstance(capability, Text):
                        content.append_text(capability)
                    else:
                        content.append(str(capability))

            return Panel(content, title=state.agent_id, border_style="dim")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML div with styled children."""
        state = self.state.value

        # Get child projections
        glyph_html = str(self.slots["phase_glyph"].project(RenderTarget.MARIMO))
        activity_html = str(self.slots["activity"].project(RenderTarget.MARIMO))
        capability_html = str(self.slots["capability"].project(RenderTarget.MARIMO))

        # Card container style
        card_style = (
            "font-family: monospace; "
            "border: 1px solid #444; "
            "border-radius: 4px; "
            "padding: 8px; "
            "background: #1a1a1a;"
        )

        # Apply breathing animation if active
        if state.breathing and state.phase == "active":
            card_style += " animation: breathe 2s ease-in-out infinite;"

        html = f'<div class="kgents-agent-card" data-agent-id="{state.agent_id}" style="{card_style}">'

        # Header
        html += '<div class="kgents-card-header" style="margin-bottom: 4px;">'
        html += glyph_html
        html += (
            f'<span style="margin-left: 4px; font-weight: bold;">{state.name}</span>'
        )
        html += "</div>"

        if state.style != "minimal":
            # Activity sparkline
            html += '<div class="kgents-card-body" style="margin-bottom: 4px;">'
            html += activity_html
            html += "</div>"

            if state.style == "full":
                # Capability bar
                html += '<div class="kgents-card-footer">'
                html += capability_html
                html += "</div>"

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full card data."""
        state = self.state.value

        result: dict[str, Any] = {
            "type": "agent_card",
            "agent_id": state.agent_id,
            "name": state.name,
            "phase": state.phase,
            "capability": state.capability,
            "entropy": state.entropy,
            "style": state.style,
            "breathing": state.breathing,
            "children": {
                "phase_glyph": self.slots["phase_glyph"].project(RenderTarget.JSON),
                "activity": self.slots["activity"].project(RenderTarget.JSON),
                "capability": self.slots["capability"].project(RenderTarget.JSON),
            },
        }

        if state.entropy > 0.1:
            result["distortion"] = entropy_to_distortion(
                state.entropy, state.seed, state.t
            )

        return result
