"""
DashboardScreen: Main agent monitoring view.

The dashboard is the primary view for observing agent activity. It composes:
- Grid of AgentCards showing active agents
- Live YieldCard stream showing recent outputs
- DensityField backdrop showing agent heat distribution

This is the "mission control" - where you see everything at once.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.density_field import (
    DensityFieldState,
    DensityFieldWidget,
    Entity,
)
from agents.i.reactive.primitives.yield_card import YieldCardState, YieldCardWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DashboardScreenState:
    """
    Immutable dashboard screen state.

    The dashboard shows:
    - Agent cards for each active agent
    - Recent yields from all agents
    - Heat map backdrop from agent activity
    """

    # Agent cards to display
    agents: tuple[AgentCardState, ...] = ()

    # Recent yields to display
    yields: tuple[YieldCardState, ...] = ()

    # Layout configuration
    width: int = 80
    height: int = 24
    cards_per_row: int = 2
    max_yields_shown: int = 5

    # Time for animation
    t: float = 0.0

    # Visual settings
    entropy: float = 0.0  # Base entropy for visual chaos
    seed: int = 0
    show_density_field: bool = True  # Show background heat map
    density_field_width: int = 40
    density_field_height: int = 10


class DashboardScreen(CompositeWidget[DashboardScreenState]):
    """
    Main agent monitoring dashboard.

    Composes:
    - AgentCardWidget[] (grid of active agents)
    - YieldCardWidget[] (stream of recent outputs)
    - DensityFieldWidget (backdrop showing agent heat)

    Features:
    - Grid layout of agent cards
    - Scrolling yield stream
    - Heat map visualization of agent activity
    - Graceful empty state handling

    Example:
        dashboard = DashboardScreen(DashboardScreenState(
            agents=(
                AgentCardState(agent_id="kgent-1", name="Kent", phase="active"),
                AgentCardState(agent_id="kgent-2", name="Helper", phase="waiting"),
            ),
            yields=(
                YieldCardState(yield_id="y1", content="Processing...", yield_type="action"),
                YieldCardState(yield_id="y2", content="Done!", yield_type="artifact"),
            ),
            show_density_field=True,
        ))

        print(dashboard.project(RenderTarget.CLI))
    """

    state: Signal[DashboardScreenState]

    def __init__(self, initial: DashboardScreenState | None = None) -> None:
        state = initial or DashboardScreenState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Build agent cards
        for i, agent_state in enumerate(state.agents):
            # Propagate time and entropy from screen state
            card_state = AgentCardState(
                agent_id=agent_state.agent_id,
                name=agent_state.name,
                phase=agent_state.phase,
                activity=agent_state.activity,
                capability=agent_state.capability,
                entropy=state.entropy if agent_state.entropy == 0 else agent_state.entropy,
                seed=state.seed + i,
                t=state.t,
                style=agent_state.style,
                breathing=agent_state.breathing,
            )
            self.slots[f"agent_{i}"] = AgentCardWidget(card_state)

        # Build yield cards
        yields_to_show = state.yields[: state.max_yields_shown]
        for i, yield_state in enumerate(yields_to_show):
            yield_card_state = YieldCardState(
                yield_id=yield_state.yield_id,
                source_agent=yield_state.source_agent,
                yield_type=yield_state.yield_type,
                content=yield_state.content,
                importance=yield_state.importance,
                timestamp=yield_state.timestamp,
                entropy=state.entropy if yield_state.entropy == 0 else yield_state.entropy,
                seed=state.seed + len(state.agents) + i,
                t=state.t,
                max_content_length=yield_state.max_content_length,
                use_emoji=yield_state.use_emoji,
            )
            self.slots[f"yield_{i}"] = YieldCardWidget(yield_card_state)

        # Build density field backdrop if enabled
        if state.show_density_field:
            # Create entities from agent positions
            entities: list[Entity] = []
            for i, agent in enumerate(state.agents):
                # Distribute agents across the field
                x = (i % 4) * (state.density_field_width // 4) + state.density_field_width // 8
                y = (i // 4) * (state.density_field_height // 2) + state.density_field_height // 4
                heat = 0.8 if agent.phase == "active" else 0.3
                entities.append(
                    Entity(
                        id=agent.agent_id,
                        x=min(x, state.density_field_width - 1),
                        y=min(y, state.density_field_height - 1),
                        phase=agent.phase,
                        heat=heat,
                    )
                )

            self.slots["density_field"] = DensityFieldWidget(
                DensityFieldState(
                    width=state.density_field_width,
                    height=state.density_field_height,
                    base_entropy=state.entropy * 0.5,  # Lower background entropy
                    entities=tuple(entities),
                    seed=state.seed,
                    t=state.t,
                )
            )

    def with_time(self, t: float) -> DashboardScreen:
        """Return new dashboard with updated time. Immutable."""
        current = self.state.value
        return DashboardScreen(
            DashboardScreenState(
                agents=current.agents,
                yields=current.yields,
                width=current.width,
                height=current.height,
                cards_per_row=current.cards_per_row,
                max_yields_shown=current.max_yields_shown,
                t=t,
                entropy=current.entropy,
                seed=current.seed,
                show_density_field=current.show_density_field,
                density_field_width=current.density_field_width,
                density_field_height=current.density_field_height,
            )
        )

    def with_entropy(self, entropy: float) -> DashboardScreen:
        """Return new dashboard with updated entropy. Immutable."""
        current = self.state.value
        return DashboardScreen(
            DashboardScreenState(
                agents=current.agents,
                yields=current.yields,
                width=current.width,
                height=current.height,
                cards_per_row=current.cards_per_row,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
                show_density_field=current.show_density_field,
                density_field_width=current.density_field_width,
                density_field_height=current.density_field_height,
            )
        )

    def add_agent(self, agent: AgentCardState) -> DashboardScreen:
        """Add an agent to the dashboard. Immutable."""
        current = self.state.value
        # Remove existing agent with same id if present
        filtered = tuple(a for a in current.agents if a.agent_id != agent.agent_id)
        return DashboardScreen(
            DashboardScreenState(
                agents=(*filtered, agent),
                yields=current.yields,
                width=current.width,
                height=current.height,
                cards_per_row=current.cards_per_row,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
                show_density_field=current.show_density_field,
                density_field_width=current.density_field_width,
                density_field_height=current.density_field_height,
            )
        )

    def push_yield(self, yield_card: YieldCardState) -> DashboardScreen:
        """Push a new yield to the stream. Immutable."""
        current = self.state.value
        # Add new yield at front, trim to max
        new_yields = (yield_card, *current.yields)[: current.max_yields_shown * 2]
        return DashboardScreen(
            DashboardScreenState(
                agents=current.agents,
                yields=new_yields,
                width=current.width,
                height=current.height,
                cards_per_row=current.cards_per_row,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
                show_density_field=current.show_density_field,
                density_field_width=current.density_field_width,
                density_field_height=current.density_field_height,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this dashboard to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (multi-line ASCII dashboard)
            - TUI: Rich layout
            - MARIMO: HTML grid
            - JSON: dict with dashboard data
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
        """CLI projection: multi-line ASCII dashboard."""
        state = self.state.value
        lines: list[str] = []

        # Header
        lines.append("=" * state.width)
        lines.append(" KGENTS DASHBOARD ".center(state.width, "="))
        lines.append("=" * state.width)

        # Empty state handling
        if not state.agents and not state.yields:
            lines.append("")
            lines.append("  No agents active. Waiting for activity...".center(state.width))
            lines.append("")
            lines.append("=" * state.width)
            return "\n".join(lines)

        # Agent cards section
        if state.agents:
            lines.append("")
            lines.append(" AGENTS ".center(state.width, "-"))
            lines.append("")

            # Grid layout
            for i in range(0, len(state.agents), state.cards_per_row):
                row_cards = []
                for j in range(state.cards_per_row):
                    if i + j < len(state.agents):
                        card = self.slots[f"agent_{i + j}"]
                        card_lines = card.project(RenderTarget.CLI).split("\n")
                        row_cards.append(card_lines)

                # Merge card lines horizontally
                if row_cards:
                    max_lines = max(len(c) for c in row_cards)
                    card_width = state.width // state.cards_per_row - 2
                    for line_idx in range(max_lines):
                        row_str = ""
                        for card_lines in row_cards:
                            if line_idx < len(card_lines):
                                row_str += card_lines[line_idx].ljust(card_width) + "  "
                            else:
                                row_str += " " * card_width + "  "
                        lines.append(row_str.rstrip())
                    lines.append("")

        # Yields section
        if state.yields:
            lines.append(" RECENT YIELDS ".center(state.width, "-"))
            lines.append("")

            yields_to_show = state.yields[: state.max_yields_shown]
            for i in range(len(yields_to_show)):
                yield_card = self.slots[f"yield_{i}"]
                yield_str = yield_card.project(RenderTarget.CLI)
                lines.append(f"  {yield_str}")

            lines.append("")

        # Density field section
        if state.show_density_field and "density_field" in self.slots:
            lines.append(" ACTIVITY FIELD ".center(state.width, "-"))
            field_str = self.slots["density_field"].project(RenderTarget.CLI)
            for field_line in field_str.split("\n"):
                lines.append(f"  {field_line}")
            lines.append("")

        lines.append("=" * state.width)
        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich layout."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value

            # Build agent cards section
            agent_content = Text()
            if state.agents:
                for i in range(len(state.agents)):
                    card = self.slots[f"agent_{i}"]
                    tui_result = card.project(RenderTarget.TUI)
                    if hasattr(tui_result, "renderable"):
                        # It's a Panel, get its content
                        agent_content.append_text(tui_result.renderable)
                    else:
                        agent_content.append(str(tui_result))
                    agent_content.append("\n")
            else:
                agent_content.append("No agents active", style="dim")

            # Build yields section
            yields_content = Text()
            yields_to_show = state.yields[: state.max_yields_shown]
            if yields_to_show:
                for i in range(len(yields_to_show)):
                    yield_card = self.slots[f"yield_{i}"]
                    tui_result = yield_card.project(RenderTarget.TUI)
                    if isinstance(tui_result, Text):
                        yields_content.append_text(tui_result)
                    else:
                        yields_content.append(str(tui_result))
                    yields_content.append("\n")
            else:
                yields_content.append("No recent yields", style="dim")

            # Return a simple combined view
            combined = Text()
            combined.append("KGENTS DASHBOARD\n", style="bold")
            combined.append_text(agent_content)
            combined.append("\n")
            combined.append_text(yields_content)

            return Panel(combined, title="Dashboard")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML grid."""
        state = self.state.value

        html = '<div class="kgents-dashboard" style="font-family: monospace;">'

        # Header
        html += '<div class="kgents-dashboard-header" style="text-align: center; padding: 8px; border-bottom: 2px solid #444;">'
        html += "<h2>KGENTS DASHBOARD</h2>"
        html += "</div>"

        # Empty state
        if not state.agents and not state.yields:
            html += '<div style="text-align: center; padding: 40px; color: #666;">'
            html += "No agents active. Waiting for activity..."
            html += "</div>"
            html += "</div>"
            return html

        # Two-column layout
        html += '<div class="kgents-dashboard-content" style="display: flex; gap: 16px; padding: 16px;">'

        # Agents column
        html += '<div class="kgents-agents-column" style="flex: 1;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Agents</h3>'
        html += '<div class="kgents-agent-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">'

        for i in range(len(state.agents)):
            card = self.slots[f"agent_{i}"]
            html += str(card.project(RenderTarget.MARIMO))

        html += "</div></div>"

        # Yields column
        html += '<div class="kgents-yields-column" style="flex: 1;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Recent Yields</h3>'
        html += '<div class="kgents-yield-stream">'

        yields_to_show = state.yields[: state.max_yields_shown]
        for i in range(len(yields_to_show)):
            yield_card = self.slots[f"yield_{i}"]
            html += str(yield_card.project(RenderTarget.MARIMO))

        html += "</div></div>"

        html += "</div>"

        # Density field
        if state.show_density_field and "density_field" in self.slots:
            html += '<div class="kgents-density-section" style="padding: 16px; border-top: 1px solid #444;">'
            html += '<h3 style="text-align: center;">Activity Field</h3>'
            html += str(self.slots["density_field"].project(RenderTarget.MARIMO))
            html += "</div>"

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: dashboard data."""
        state = self.state.value

        agent_projections = []
        for i in range(len(state.agents)):
            card = self.slots[f"agent_{i}"]
            agent_projections.append(card.project(RenderTarget.JSON))

        yield_projections = []
        yields_to_show = state.yields[: state.max_yields_shown]
        for i in range(len(yields_to_show)):
            yield_card = self.slots[f"yield_{i}"]
            yield_projections.append(yield_card.project(RenderTarget.JSON))

        result: dict[str, Any] = {
            "type": "dashboard_screen",
            "width": state.width,
            "height": state.height,
            "agent_count": len(state.agents),
            "yield_count": len(state.yields),
            "entropy": state.entropy,
            "t": state.t,
            "agents": agent_projections,
            "yields": yield_projections,
        }

        if state.show_density_field and "density_field" in self.slots:
            result["density_field"] = self.slots["density_field"].project(RenderTarget.JSON)

        return result
