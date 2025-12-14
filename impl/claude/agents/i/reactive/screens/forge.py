"""
ForgeScreen: Agent creation and editing view.

The forge is where agents are born and modified. It composes:
- Agent configuration preview (AgentCard showing the agent being built)
- Capability bar editor (Bar showing capabilities)
- Phase glyph selector

This is the "workshop" - where agents take shape before deployment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget, Phase
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    pass

ForgeMode = Literal["create", "edit", "preview"]


@dataclass(frozen=True)
class ForgeScreenState:
    """
    Immutable forge screen state.

    The forge shows:
    - Current agent being created/edited
    - Capability editor
    - Phase selector
    - Preview of the resulting agent
    """

    # Agent being forged
    agent_id: str = ""
    name: str = "New Agent"
    phase: Phase = "idle"
    capability: float = 1.0

    # Mode
    mode: ForgeMode = "create"

    # Layout
    width: int = 60
    height: int = 24

    # Time for animation
    t: float = 0.0

    # Visual settings
    entropy: float = 0.0
    seed: int = 0


# Available phases for selection
AVAILABLE_PHASES: tuple[Phase, ...] = (
    "idle",
    "active",
    "waiting",
    "complete",
    "error",
    "yielding",
    "thinking",
)


class ForgeScreen(CompositeWidget[ForgeScreenState]):
    """
    Agent creation/editing screen.

    Composes:
    - AgentCardWidget (preview of agent being created)
    - BarWidget (capability editor)
    - GlyphWidget[] (phase selector glyphs)

    Features:
    - Live preview of agent configuration
    - Interactive capability slider (conceptually)
    - Phase selection with visual feedback
    - Create/Edit/Preview modes

    Example:
        forge = ForgeScreen(ForgeScreenState(
            agent_id="kgent-new",
            name="Assistant",
            phase="idle",
            capability=0.8,
            mode="create",
        ))

        print(forge.project(RenderTarget.CLI))
    """

    state: Signal[ForgeScreenState]

    def __init__(self, initial: ForgeScreenState | None = None) -> None:
        state = initial or ForgeScreenState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Preview card showing the agent being forged
        self.slots["preview_card"] = AgentCardWidget(
            AgentCardState(
                agent_id=state.agent_id or "preview",
                name=state.name,
                phase=state.phase,
                capability=state.capability,
                entropy=state.entropy,
                seed=state.seed,
                t=state.t,
                style="full",
                breathing=True,
            )
        )

        # Capability bar editor
        self.slots["capability_bar"] = BarWidget(
            BarState(
                value=state.capability,
                width=20,
                style="solid",
                entropy=state.entropy,
                seed=state.seed + 1,
                t=state.t,
            )
        )

        # Phase selector glyphs
        for i, phase in enumerate(AVAILABLE_PHASES):
            # Highlight the selected phase with higher entropy
            is_selected = phase == state.phase
            glyph_entropy = 0.4 if is_selected else 0.1

            self.slots[f"phase_{phase}"] = GlyphWidget(
                GlyphState(
                    phase=phase,
                    entropy=glyph_entropy + state.entropy,
                    seed=state.seed + 10 + i,
                    t=state.t,
                    animate="pulse" if is_selected else "none",
                )
            )

    def with_name(self, name: str) -> ForgeScreen:
        """Return new forge with updated name. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=name,
                phase=current.phase,
                capability=current.capability,
                mode=current.mode,
                width=current.width,
                height=current.height,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_phase(self, phase: Phase) -> ForgeScreen:
        """Return new forge with updated phase. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=current.name,
                phase=phase,
                capability=current.capability,
                mode=current.mode,
                width=current.width,
                height=current.height,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_capability(self, capability: float) -> ForgeScreen:
        """Return new forge with updated capability. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                capability=max(0.0, min(1.0, capability)),
                mode=current.mode,
                width=current.width,
                height=current.height,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_time(self, t: float) -> ForgeScreen:
        """Return new forge with updated time. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                capability=current.capability,
                mode=current.mode,
                width=current.width,
                height=current.height,
                t=t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_entropy(self, entropy: float) -> ForgeScreen:
        """Return new forge with updated entropy. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                capability=current.capability,
                mode=current.mode,
                width=current.width,
                height=current.height,
                t=current.t,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
            )
        )

    def with_mode(self, mode: ForgeMode) -> ForgeScreen:
        """Return new forge with updated mode. Immutable."""
        current = self.state.value
        return ForgeScreen(
            ForgeScreenState(
                agent_id=current.agent_id,
                name=current.name,
                phase=current.phase,
                capability=current.capability,
                mode=mode,
                width=current.width,
                height=current.height,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def get_agent_state(self) -> AgentCardState:
        """Get the current agent configuration as an AgentCardState."""
        state = self.state.value
        return AgentCardState(
            agent_id=state.agent_id or f"agent-{state.seed}",
            name=state.name,
            phase=state.phase,
            capability=state.capability,
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this forge to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (multi-line ASCII forge)
            - TUI: Rich layout
            - MARIMO: HTML form layout
            - JSON: dict with forge data
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
        """CLI projection: multi-line ASCII forge."""
        state = self.state.value
        lines: list[str] = []

        # Header with mode
        mode_label = {
            "create": "CREATE NEW AGENT",
            "edit": "EDIT AGENT",
            "preview": "AGENT PREVIEW",
        }[state.mode]

        lines.append("=" * state.width)
        lines.append(f" FORGE: {mode_label} ".center(state.width, "="))
        lines.append("=" * state.width)
        lines.append("")

        # Configuration section
        lines.append(" CONFIGURATION ".center(state.width, "-"))
        lines.append("")
        lines.append(f"  Name: {state.name}")
        lines.append(f"  ID:   {state.agent_id or '(auto-generated)'}")
        lines.append("")

        # Phase selector
        lines.append("  Phase:")
        phase_line = "    "
        for phase in AVAILABLE_PHASES:
            glyph = self.slots[f"phase_{phase}"]
            glyph_str = glyph.project(RenderTarget.CLI)
            marker = "[*]" if phase == state.phase else "[ ]"
            phase_line += f"{glyph_str}{marker} "

        lines.append(phase_line)
        lines.append("")

        # Capability editor
        lines.append("  Capability:")
        capability_bar = self.slots["capability_bar"].project(RenderTarget.CLI)
        lines.append(f"    {capability_bar} {int(state.capability * 100)}%")
        lines.append("")

        # Preview section
        lines.append(" PREVIEW ".center(state.width, "-"))
        lines.append("")

        preview = self.slots["preview_card"].project(RenderTarget.CLI)
        for line in preview.split("\n"):
            lines.append(f"    {line}")

        lines.append("")
        lines.append("=" * state.width)

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich layout."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value

            content = Text()

            # Mode header
            mode_label = {
                "create": "CREATE NEW AGENT",
                "edit": "EDIT AGENT",
                "preview": "AGENT PREVIEW",
            }[state.mode]
            content.append(f"{mode_label}\n\n", style="bold")

            # Configuration
            content.append("Configuration\n", style="underline")
            content.append(f"Name: {state.name}\n")
            content.append(f"ID: {state.agent_id or '(auto-generated)'}\n\n")

            # Phase selector
            content.append("Phase: ")
            for phase in AVAILABLE_PHASES:
                glyph = self.slots[f"phase_{phase}"]
                glyph_tui = glyph.project(RenderTarget.TUI)
                if isinstance(glyph_tui, Text):
                    content.append_text(glyph_tui)
                else:
                    content.append(str(glyph_tui))

                if phase == state.phase:
                    content.append("*", style="bold yellow")
                content.append(" ")

            content.append("\n\n")

            # Capability
            content.append("Capability: ")
            cap_bar = self.slots["capability_bar"].project(RenderTarget.TUI)
            if isinstance(cap_bar, Text):
                content.append_text(cap_bar)
            else:
                content.append(str(cap_bar))
            content.append(f" {int(state.capability * 100)}%\n\n")

            # Preview
            content.append("Preview:\n", style="underline")
            preview = self.slots["preview_card"].project(RenderTarget.TUI)
            if hasattr(preview, "renderable"):
                content.append_text(preview.renderable)
            else:
                content.append(str(preview))

            return Panel(content, title="Agent Forge")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML form layout."""
        state = self.state.value

        mode_label = {
            "create": "CREATE NEW AGENT",
            "edit": "EDIT AGENT",
            "preview": "AGENT PREVIEW",
        }[state.mode]

        html = (
            '<div class="kgents-forge" style="font-family: monospace; padding: 16px;">'
        )

        # Header
        html += '<div class="kgents-forge-header" style="text-align: center; padding: 8px; border-bottom: 2px solid #444;">'
        html += f"<h2>FORGE: {mode_label}</h2>"
        html += "</div>"

        # Two-column layout
        html += '<div style="display: flex; gap: 24px; padding: 16px;">'

        # Configuration column
        html += '<div class="kgents-forge-config" style="flex: 1;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Configuration</h3>'

        html += '<div style="margin: 16px 0;">'
        html += f"<label>Name:</label> <strong>{state.name}</strong><br>"
        html += (
            f"<label>ID:</label> <code>{state.agent_id or '(auto-generated)'}</code>"
        )
        html += "</div>"

        # Phase selector
        html += '<div style="margin: 16px 0;">'
        html += "<label>Phase:</label><br>"
        html += '<div style="display: flex; gap: 8px; margin-top: 8px;">'

        for phase in AVAILABLE_PHASES:
            glyph = self.slots[f"phase_{phase}"]
            glyph_html = str(glyph.project(RenderTarget.MARIMO))
            is_selected = phase == state.phase
            border = "2px solid #f80" if is_selected else "1px solid #444"
            bg = "#2a1a1a" if is_selected else "transparent"

            html += f'<div style="padding: 4px 8px; border: {border}; border-radius: 4px; background: {bg}; cursor: pointer;">'
            html += glyph_html
            html += f'<span style="font-size: 0.8em; margin-left: 4px;">{phase}</span>'
            html += "</div>"

        html += "</div></div>"

        # Capability bar
        html += '<div style="margin: 16px 0;">'
        html += f"<label>Capability: {int(state.capability * 100)}%</label><br>"
        capability_html = str(self.slots["capability_bar"].project(RenderTarget.MARIMO))
        html += f'<div style="margin-top: 8px;">{capability_html}</div>'
        html += "</div>"

        html += "</div>"

        # Preview column
        html += '<div class="kgents-forge-preview" style="flex: 1;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Preview</h3>'
        html += '<div style="padding: 16px; border: 1px solid #333; border-radius: 4px; margin-top: 16px;">'
        html += str(self.slots["preview_card"].project(RenderTarget.MARIMO))
        html += "</div></div>"

        html += "</div></div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: forge data."""
        state = self.state.value

        phase_glyphs = {}
        for phase in AVAILABLE_PHASES:
            phase_glyphs[phase] = self.slots[f"phase_{phase}"].project(
                RenderTarget.JSON
            )

        return {
            "type": "forge_screen",
            "mode": state.mode,
            "width": state.width,
            "height": state.height,
            "entropy": state.entropy,
            "t": state.t,
            "configuration": {
                "agent_id": state.agent_id,
                "name": state.name,
                "phase": state.phase,
                "capability": state.capability,
            },
            "available_phases": list(AVAILABLE_PHASES),
            "phase_glyphs": phase_glyphs,
            "preview_card": self.slots["preview_card"].project(RenderTarget.JSON),
            "capability_bar": self.slots["capability_bar"].project(RenderTarget.JSON),
        }
