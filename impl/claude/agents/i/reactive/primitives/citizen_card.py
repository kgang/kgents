"""
CitizenWidget: Town citizen visualization card.

Wave 4 Component
================

CitizenWidget extends AgentCardWidget semantics for Agent Town citizens.
It maps CitizenPhase to visual glyphs and animations, and extracts
state from Citizen entities.

Phase Mapping:
    IDLE       -> ○ (hollow circle, no animation)
    SOCIALIZING -> ◉ (filled bullseye, breathe)
    WORKING    -> ● (filled circle, breathe)
    REFLECTING -> ◐ (half moon, pulse)
    RESTING    -> ◯ (empty ring, no animation)

Quick Start:
    from agents.i.reactive.primitives.citizen_card import CitizenWidget, CitizenState
    from agents.town.citizen import Citizen
    from agents.town.polynomial import CitizenPhase

    # Create from state
    state = CitizenState(
        citizen_id="alice",
        name="Alice",
        archetype="builder",
        phase=CitizenPhase.WORKING,
    )
    widget = CitizenWidget(state)
    print(widget.project(RenderTarget.CLI))

    # Or from a Citizen entity
    citizen = Citizen(name="Alice", archetype="builder", region="plaza")
    widget = CitizenWidget(CitizenState.from_citizen(citizen))

See Also:
    - agent_card.py: Base AgentCardWidget
    - composable.py: HStack/VStack for grid composition
    - docs/skills/agent-town-visualization.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.i.reactive.composable import ComposableMixin
from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.glyph import Phase
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget
from agents.town.polynomial import CitizenPhase
from protocols.nphase.operad import NPhase

if TYPE_CHECKING:
    from agents.town.citizen import Citizen, Eigenvectors

# =============================================================================
# Phase to Glyph Mapping
# =============================================================================

# Map CitizenPhase to (phase_str for AgentCardWidget, animation)
# Note: Using Phase | str since "resting" isn't in base Phase literal
PHASE_TO_GLYPH: dict[CitizenPhase, tuple[str, str]] = {
    CitizenPhase.IDLE: ("idle", "none"),
    CitizenPhase.SOCIALIZING: ("active", "breathe"),
    CitizenPhase.WORKING: ("active", "breathe"),
    CitizenPhase.REFLECTING: ("thinking", "pulse"),
    CitizenPhase.RESTING: ("idle", "none"),  # Map to idle (visually similar)
}

# Visual glyphs for CLI rendering
PHASE_GLYPHS: dict[CitizenPhase, str] = {
    CitizenPhase.IDLE: "○",
    CitizenPhase.SOCIALIZING: "◉",
    CitizenPhase.WORKING: "●",
    CitizenPhase.REFLECTING: "◐",
    CitizenPhase.RESTING: "◯",
}

# NPhase to short label
NPHASE_LABELS: dict[NPhase, str] = {
    NPhase.SENSE: "S",
    NPhase.ACT: "A",
    NPhase.REFLECT: "R",
}


# =============================================================================
# CitizenState
# =============================================================================


@dataclass(frozen=True)
class CitizenState:
    """
    Immutable state for a Town citizen widget.

    All visual properties derive deterministically from this state.
    Use `from_citizen()` to extract state from a Citizen entity.
    """

    citizen_id: str = ""
    name: str = "Citizen"
    archetype: str = "unknown"
    phase: CitizenPhase = CitizenPhase.IDLE
    nphase: NPhase = NPhase.SENSE
    activity: tuple[float, ...] = ()  # Recent activity samples (0.0-1.0)
    capability: float = 1.0  # 0.0-1.0, derived from accursed_surplus
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    region: str = ""
    mood: str = "calm"
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Time in milliseconds
    # Eigenvector summary (optional)
    warmth: float = 0.5
    curiosity: float = 0.5
    trust: float = 0.5

    def to_agent_card_state(self) -> AgentCardState:
        """
        Convert to AgentCardState for rendering.

        Maps CitizenPhase to the phase string expected by AgentCardWidget.
        """
        from typing import cast

        phase_str, animation = PHASE_TO_GLYPH.get(self.phase, ("idle", "none"))
        # Cast to Phase type for AgentCardState
        phase_str = cast(Phase, phase_str)
        return AgentCardState(
            agent_id=self.citizen_id,
            name=self.name,
            phase=phase_str,
            activity=self.activity,
            capability=self.capability,
            entropy=self.entropy,
            seed=self.seed,
            t=self.t,
            breathing=animation == "breathe",
        )

    @classmethod
    def from_citizen(
        cls,
        citizen: Citizen,
        activity_samples: tuple[float, ...] = (),
        t: float = 0.0,
    ) -> CitizenState:
        """
        Extract state from a Citizen entity.

        Args:
            citizen: The Citizen entity
            activity_samples: Recent activity samples (from TownFlux trace)
            t: Current time for animation

        Returns:
            Frozen CitizenState with all fields populated
        """
        # Capability: inverse of accursed surplus (capped at 10)
        capability = max(0.0, 1.0 - citizen.accursed_surplus / 10.0)

        # Entropy: direct from accursed surplus (capped)
        entropy = min(1.0, citizen.accursed_surplus / 10.0)

        return cls(
            citizen_id=citizen.id,
            name=citizen.name,
            archetype=citizen.archetype,
            phase=citizen._phase,
            nphase=citizen.nphase_state.current_phase,
            activity=activity_samples,
            capability=capability,
            entropy=entropy,
            region=citizen.region,
            mood=citizen._infer_mood(),
            warmth=citizen.eigenvectors.warmth,
            curiosity=citizen.eigenvectors.curiosity,
            trust=citizen.eigenvectors.trust,
        )


# =============================================================================
# CitizenWidget
# =============================================================================


class CitizenWidget(ComposableMixin, CompositeWidget[CitizenState]):
    """
    Widget for visualizing a Town citizen.

    Wraps AgentCardWidget with citizen-specific semantics:
    - Phase glyph mapping (CitizenPhase -> visual)
    - N-Phase indicator
    - Mood display
    - Eigenvector summary (optional)

    Supports composition via >> and // operators.

    Example:
        # Single citizen
        widget = CitizenWidget(CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.WORKING,
        ))
        print(widget.project(RenderTarget.CLI))

        # Grid composition
        row = widget1 >> widget2 >> widget3
        grid = row1 // row2 // row3
    """

    state: Signal[CitizenState]

    def __init__(self, initial: CitizenState | None = None) -> None:
        state = initial or CitizenState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value
        agent_card_state = state.to_agent_card_state()
        self.slots["agent_card"] = AgentCardWidget(agent_card_state)

    def with_state(self, new_state: CitizenState) -> CitizenWidget:
        """Return new widget with updated state. Immutable."""
        return CitizenWidget(new_state)

    def with_activity(self, activity: tuple[float, ...]) -> CitizenWidget:
        """Return new widget with updated activity. Immutable."""
        current = self.state.value
        return CitizenWidget(
            CitizenState(
                citizen_id=current.citizen_id,
                name=current.name,
                archetype=current.archetype,
                phase=current.phase,
                nphase=current.nphase,
                activity=activity,
                capability=current.capability,
                entropy=current.entropy,
                region=current.region,
                mood=current.mood,
                seed=current.seed,
                t=current.t,
                warmth=current.warmth,
                curiosity=current.curiosity,
                trust=current.trust,
            )
        )

    def with_time(self, t: float) -> CitizenWidget:
        """Return new widget with updated time. Immutable."""
        current = self.state.value
        return CitizenWidget(
            CitizenState(
                citizen_id=current.citizen_id,
                name=current.name,
                archetype=current.archetype,
                phase=current.phase,
                nphase=current.nphase,
                activity=current.activity,
                capability=current.capability,
                entropy=current.entropy,
                region=current.region,
                mood=current.mood,
                seed=current.seed,
                t=t,
                warmth=current.warmth,
                curiosity=current.curiosity,
                trust=current.trust,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this citizen widget to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (ASCII card with phase glyph)
            - TUI: Rich Panel
            - MARIMO: HTML div
            - JSON: dict with citizen data
        """
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
        """CLI projection: ASCII card with citizen-specific glyphs."""
        state = self.state.value

        # Phase glyph
        glyph = PHASE_GLYPHS.get(state.phase, "?")

        # N-Phase indicator
        nphase_label = NPHASE_LABELS.get(state.nphase, "?")

        # Header: glyph + name + nphase
        header = f"{glyph} {state.name} [{nphase_label}]"

        # Activity sparkline (from AgentCardWidget)
        activity_line = ""
        if state.activity:
            blocks = " ▁▂▃▄▅▆▇█"
            activity_chars = []
            for v in state.activity[-10:]:  # Last 10
                idx = int(v * 8)
                idx = max(0, min(8, idx))
                activity_chars.append(blocks[idx])
            activity_line = "".join(activity_chars)

        # Capability bar
        cap_width = 10
        filled = int(state.capability * cap_width)
        cap_bar = "█" * filled + "░" * (cap_width - filled)

        # Archetype label
        archetype_short = state.archetype[:8].capitalize()

        return f"{header}\n{archetype_short}\n{activity_line}\ncap: {cap_bar}"

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value
            glyph = PHASE_GLYPHS.get(state.phase, "?")
            nphase_label = NPHASE_LABELS.get(state.nphase, "?")

            content = Text()
            content.append(f"{glyph} ", style="bold")
            content.append(f"{state.name} ", style="bright_white")
            content.append(f"[{nphase_label}]", style="dim")
            content.append(f"\n{state.archetype}", style="cyan")

            if state.activity:
                content.append("\n")
                blocks = " ▁▂▃▄▅▆▇█"
                for v in state.activity[-10:]:
                    idx = max(0, min(8, int(v * 8)))
                    content.append(blocks[idx], style="green")

            content.append(f"\ncap: {state.capability:.0%}", style="yellow")

            return Panel(
                content,
                title=state.citizen_id,
                subtitle=state.mood,
                border_style="dim",
            )
        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML div."""
        state = self.state.value
        glyph = PHASE_GLYPHS.get(state.phase, "?")
        nphase_label = NPHASE_LABELS.get(state.nphase, "?")

        # Animation style
        _, animation = PHASE_TO_GLYPH.get(state.phase, ("idle", "none"))
        anim_style = ""
        if animation == "breathe":
            anim_style = "animation: breathe 2s ease-in-out infinite;"
        elif animation == "pulse":
            anim_style = "animation: pulse 1s ease-in-out infinite;"

        # Activity sparkline
        activity_html = ""
        if state.activity:
            blocks = " ▁▂▃▄▅▆▇█"
            chars = []
            for v in state.activity[-10:]:
                idx = max(0, min(8, int(v * 8)))
                chars.append(blocks[idx])
            activity_html = f'<div class="activity" style="color: #28a745; font-family: monospace;">{"".join(chars)}</div>'

        # Capability bar
        cap_pct = int(state.capability * 100)

        html = f"""
        <div class="kgents-citizen-card" data-citizen-id="{state.citizen_id}" style="
            font-family: monospace;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 8px;
            background: #ffffff;
            color: #212529;
            min-width: 120px;
            {anim_style}
        ">
            <div class="header" style="margin-bottom: 4px;">
                <span style="font-size: 1.2em;">{glyph}</span>
                <span style="font-weight: bold; margin-left: 4px;">{state.name}</span>
                <span style="color: #6c757d; margin-left: 4px;">[{nphase_label}]</span>
            </div>
            <div class="archetype" style="color: #17a2b8; font-size: 0.875em;">{state.archetype}</div>
            {activity_html}
            <div class="capability" style="margin-top: 4px;">
                <div style="background: #e9ecef; border-radius: 2px; height: 8px; width: 100%;">
                    <div style="background: #ffc107; height: 100%; width: {cap_pct}%; border-radius: 2px;"></div>
                </div>
            </div>
            <div class="mood" style="font-size: 0.75em; color: #6c757d; margin-top: 4px;">{state.mood}</div>
        </div>
        """
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full citizen data."""
        state = self.state.value
        return {
            "type": "citizen_card",
            "citizen_id": state.citizen_id,
            "name": state.name,
            "archetype": state.archetype,
            "phase": state.phase.name,
            "nphase": state.nphase.name,
            "activity": list(state.activity),
            "capability": state.capability,
            "entropy": state.entropy,
            "region": state.region,
            "mood": state.mood,
            "eigenvectors": {
                "warmth": state.warmth,
                "curiosity": state.curiosity,
                "trust": state.trust,
            },
        }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PHASE_TO_GLYPH",
    "PHASE_GLYPHS",
    "NPHASE_LABELS",
    "CitizenState",
    "CitizenWidget",
]
