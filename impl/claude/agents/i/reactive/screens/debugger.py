"""
DebuggerScreen: Agent inspection and debugging view.

The debugger provides detailed inspection of a single agent. It composes:
- Selected agent's full card (expanded view)
- Activity history sparkline (with zoom capability)
- Yield timeline (all yields from this agent)
- Entropy slider for visual chaos testing

This is the "microscope" - where you examine agents in detail.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.primitives.yield_card import YieldCardState, YieldCardWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DebuggerScreenState:
    """
    Immutable debugger screen state.

    The debugger shows:
    - Selected agent (full card view)
    - Extended activity history (full sparkline)
    - All yields from this agent
    - Entropy control for visual testing
    """

    # Agent being debugged
    agent: AgentCardState | None = None

    # Extended activity history (more than the card shows)
    activity_history: tuple[float, ...] = ()

    # All yields from this agent
    yields: tuple[YieldCardState, ...] = ()

    # Layout
    width: int = 80
    height: int = 30
    max_activity_points: int = 50
    max_yields_shown: int = 10

    # Time for animation
    t: float = 0.0

    # Visual settings - entropy is controllable in debugger
    entropy: float = 0.0
    seed: int = 0


class DebuggerScreen(CompositeWidget[DebuggerScreenState]):
    """
    Agent inspection/debugging screen.

    Composes:
    - AgentCardWidget (selected agent, expanded view)
    - SparklineWidget (full activity history with zoom)
    - YieldCardWidget[] (all yields from this agent)
    - BarWidget (entropy slider)

    Features:
    - Detailed agent card view
    - Extended activity timeline
    - Complete yield history
    - Entropy slider for testing visual chaos
    - Empty state handling when no agent selected

    Example:
        debugger = DebuggerScreen(DebuggerScreenState(
            agent=AgentCardState(agent_id="kgent-1", name="Kent", phase="active"),
            activity_history=(0.1, 0.3, 0.5, 0.8, 0.6, 0.9, 0.4, 0.7),
            yields=(
                YieldCardState(yield_id="y1", content="Thinking...", yield_type="thought"),
                YieldCardState(yield_id="y2", content="Action!", yield_type="action"),
            ),
            entropy=0.3,
        ))

        print(debugger.project(RenderTarget.CLI))
    """

    state: Signal[DebuggerScreenState]

    def __init__(self, initial: DebuggerScreenState | None = None) -> None:
        state = initial or DebuggerScreenState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Agent card (if selected)
        if state.agent is not None:
            # Create expanded card with screen's entropy
            self.slots["agent_card"] = AgentCardWidget(
                AgentCardState(
                    agent_id=state.agent.agent_id,
                    name=state.agent.name,
                    phase=state.agent.phase,
                    activity=state.agent.activity,
                    capability=state.agent.capability,
                    entropy=state.entropy,  # Use debugger's entropy control
                    seed=state.seed,
                    t=state.t,
                    style="full",
                    breathing=state.agent.breathing,
                )
            )

        # Extended activity sparkline
        activity_values = state.activity_history[: state.max_activity_points]
        self.slots["activity_sparkline"] = SparklineWidget(
            SparklineState(
                values=activity_values,
                max_length=state.max_activity_points,
                entropy=state.entropy,
                seed=state.seed + 1,
                t=state.t,
            )
        )

        # Yield cards
        yields_to_show = state.yields[: state.max_yields_shown]
        for i, yield_state in enumerate(yields_to_show):
            self.slots[f"yield_{i}"] = YieldCardWidget(
                YieldCardState(
                    yield_id=yield_state.yield_id,
                    source_agent=yield_state.source_agent,
                    yield_type=yield_state.yield_type,
                    content=yield_state.content,
                    importance=yield_state.importance,
                    timestamp=yield_state.timestamp,
                    entropy=state.entropy,  # Use debugger's entropy
                    seed=state.seed + 10 + i,
                    t=state.t,
                    max_content_length=yield_state.max_content_length,
                    use_emoji=yield_state.use_emoji,
                )
            )

        # Entropy control slider
        self.slots["entropy_slider"] = BarWidget(
            BarState(
                value=state.entropy,
                width=20,
                style="gradient",
                entropy=0.0,  # Slider itself doesn't have chaos
                seed=state.seed + 100,
                t=state.t,
            )
        )

    def with_agent(self, agent: AgentCardState | None) -> DebuggerScreen:
        """Return new debugger with selected agent. Immutable."""
        current = self.state.value
        return DebuggerScreen(
            DebuggerScreenState(
                agent=agent,
                activity_history=current.activity_history,
                yields=current.yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_activity(self, history: tuple[float, ...] | list[float]) -> DebuggerScreen:
        """Return new debugger with activity history. Immutable."""
        current = self.state.value
        normalized = tuple(max(0.0, min(1.0, v)) for v in history)
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=normalized,
                yields=current.yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def push_activity(self, value: float) -> DebuggerScreen:
        """Push a new activity value. Immutable."""
        current = self.state.value
        clamped = max(0.0, min(1.0, value))
        new_history = (*current.activity_history, clamped)[-current.max_activity_points :]
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=new_history,
                yields=current.yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_yields(self, yields: tuple[YieldCardState, ...]) -> DebuggerScreen:
        """Return new debugger with yields. Immutable."""
        current = self.state.value
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=current.activity_history,
                yields=yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def push_yield(self, yield_card: YieldCardState) -> DebuggerScreen:
        """Push a new yield. Immutable."""
        current = self.state.value
        new_yields = (yield_card, *current.yields)
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=current.activity_history,
                yields=new_yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_time(self, t: float) -> DebuggerScreen:
        """Return new debugger with updated time. Immutable."""
        current = self.state.value
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=current.activity_history,
                yields=current.yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=t,
                entropy=current.entropy,
                seed=current.seed,
            )
        )

    def with_entropy(self, entropy: float) -> DebuggerScreen:
        """Return new debugger with updated entropy. Immutable."""
        current = self.state.value
        return DebuggerScreen(
            DebuggerScreenState(
                agent=current.agent,
                activity_history=current.activity_history,
                yields=current.yields,
                width=current.width,
                height=current.height,
                max_activity_points=current.max_activity_points,
                max_yields_shown=current.max_yields_shown,
                t=current.t,
                entropy=max(0.0, min(1.0, entropy)),
                seed=current.seed,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this debugger to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (multi-line ASCII debugger)
            - TUI: Rich layout
            - MARIMO: HTML layout
            - JSON: dict with debugger data
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
        """CLI projection: multi-line ASCII debugger."""
        state = self.state.value
        lines: list[str] = []

        # Header
        lines.append("=" * state.width)
        lines.append(" AGENT DEBUGGER ".center(state.width, "="))
        lines.append("=" * state.width)

        # Empty state handling
        if state.agent is None:
            lines.append("")
            lines.append("  No agent selected.".center(state.width))
            lines.append("  Select an agent to debug.".center(state.width))
            lines.append("")
            lines.append("=" * state.width)
            return "\n".join(lines)

        # Agent card section
        lines.append("")
        lines.append(" AGENT ".center(state.width, "-"))
        lines.append("")

        agent_card = self.slots["agent_card"].project(RenderTarget.CLI)
        for line in agent_card.split("\n"):
            lines.append(f"    {line}")

        lines.append("")

        # Activity timeline section
        lines.append(" ACTIVITY TIMELINE ".center(state.width, "-"))
        lines.append("")

        sparkline = self.slots["activity_sparkline"].project(RenderTarget.CLI)
        points_count = len(state.activity_history)
        lines.append(f"    {sparkline}  ({points_count} points)")
        lines.append("")

        # Yields section
        if state.yields:
            lines.append(" YIELD HISTORY ".center(state.width, "-"))
            lines.append("")

            yields_to_show = state.yields[: state.max_yields_shown]
            for i in range(len(yields_to_show)):
                yield_card = self.slots[f"yield_{i}"]
                yield_str = yield_card.project(RenderTarget.CLI)
                # Indent each line
                for yield_line in yield_str.split("\n"):
                    lines.append(f"    {yield_line}")
                lines.append("")

            if len(state.yields) > state.max_yields_shown:
                remaining = len(state.yields) - state.max_yields_shown
                lines.append(f"    ... and {remaining} more yields")
                lines.append("")

        # Entropy control section
        lines.append(" ENTROPY CONTROL ".center(state.width, "-"))
        lines.append("")

        entropy_bar = self.slots["entropy_slider"].project(RenderTarget.CLI)
        entropy_pct = int(state.entropy * 100)
        lines.append(f"    Chaos Level: {entropy_bar} {entropy_pct}%")
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
            content.append("AGENT DEBUGGER\n\n", style="bold")

            # Empty state
            if state.agent is None:
                content.append("No agent selected.\n", style="dim")
                content.append("Select an agent to debug.", style="dim")
                return Panel(content, title="Debugger")

            # Agent card
            content.append("Agent:\n", style="underline")
            agent_card = self.slots["agent_card"].project(RenderTarget.TUI)
            if hasattr(agent_card, "renderable"):
                content.append_text(agent_card.renderable)
            else:
                content.append(str(agent_card))
            content.append("\n\n")

            # Activity timeline
            content.append("Activity Timeline:\n", style="underline")
            sparkline = self.slots["activity_sparkline"].project(RenderTarget.TUI)
            if isinstance(sparkline, Text):
                content.append_text(sparkline)
            else:
                content.append(str(sparkline))
            content.append(f"  ({len(state.activity_history)} points)\n\n")

            # Yields
            if state.yields:
                content.append("Yield History:\n", style="underline")
                yields_to_show = state.yields[: state.max_yields_shown]
                for i in range(len(yields_to_show)):
                    yield_card = self.slots[f"yield_{i}"]
                    yield_tui = yield_card.project(RenderTarget.TUI)
                    if isinstance(yield_tui, Text):
                        content.append_text(yield_tui)
                    else:
                        content.append(str(yield_tui))
                    content.append("\n")
                content.append("\n")

            # Entropy control
            content.append("Entropy Control:\n", style="underline")
            entropy_bar = self.slots["entropy_slider"].project(RenderTarget.TUI)
            if isinstance(entropy_bar, Text):
                content.append_text(entropy_bar)
            else:
                content.append(str(entropy_bar))
            content.append(f" {int(state.entropy * 100)}%")

            return Panel(content, title="Debugger")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML layout."""
        state = self.state.value

        html = '<div class="kgents-debugger" style="font-family: monospace; padding: 16px;">'

        # Header
        html += '<div class="kgents-debugger-header" style="text-align: center; padding: 8px; border-bottom: 2px solid #444;">'
        html += "<h2>AGENT DEBUGGER</h2>"
        html += "</div>"

        # Empty state
        if state.agent is None:
            html += '<div style="text-align: center; padding: 40px; color: #666;">'
            html += "No agent selected.<br>Select an agent to debug."
            html += "</div></div>"
            return html

        # Main content
        html += '<div style="padding: 16px;">'

        # Agent section
        html += '<div class="kgents-debugger-agent" style="margin-bottom: 24px;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Agent</h3>'
        html += '<div style="padding: 16px; border: 1px solid #333; border-radius: 4px;">'
        html += str(self.slots["agent_card"].project(RenderTarget.MARIMO))
        html += "</div></div>"

        # Activity timeline section
        html += '<div class="kgents-debugger-activity" style="margin-bottom: 24px;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Activity Timeline</h3>'
        html += '<div style="padding: 16px; border: 1px solid #333; border-radius: 4px;">'
        html += str(self.slots["activity_sparkline"].project(RenderTarget.MARIMO))
        html += f'<span style="margin-left: 8px; color: #666;">({len(state.activity_history)} points)</span>'
        html += "</div></div>"

        # Yields section
        if state.yields:
            html += '<div class="kgents-debugger-yields" style="margin-bottom: 24px;">'
            html += '<h3 style="border-bottom: 1px solid #444;">Yield History</h3>'
            html += '<div style="max-height: 300px; overflow-y: auto;">'

            yields_to_show = state.yields[: state.max_yields_shown]
            for i in range(len(yields_to_show)):
                yield_card = self.slots[f"yield_{i}"]
                html += str(yield_card.project(RenderTarget.MARIMO))

            if len(state.yields) > state.max_yields_shown:
                remaining = len(state.yields) - state.max_yields_shown
                html += f'<div style="text-align: center; padding: 8px; color: #666;">... and {remaining} more yields</div>'

            html += "</div></div>"

        # Entropy control section
        html += '<div class="kgents-debugger-entropy" style="margin-bottom: 24px;">'
        html += '<h3 style="border-bottom: 1px solid #444;">Entropy Control</h3>'
        html += '<div style="padding: 16px; border: 1px solid #333; border-radius: 4px; display: flex; align-items: center; gap: 16px;">'
        html += "<label>Chaos Level:</label>"
        html += str(self.slots["entropy_slider"].project(RenderTarget.MARIMO))
        html += f"<span>{int(state.entropy * 100)}%</span>"
        html += "</div></div>"

        html += "</div></div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: debugger data."""
        state = self.state.value

        result: dict[str, Any] = {
            "type": "debugger_screen",
            "width": state.width,
            "height": state.height,
            "entropy": state.entropy,
            "t": state.t,
            "has_agent": state.agent is not None,
            "activity_point_count": len(state.activity_history),
            "yield_count": len(state.yields),
        }

        if state.agent is not None:
            result["agent_card"] = self.slots["agent_card"].project(RenderTarget.JSON)

        result["activity_sparkline"] = self.slots["activity_sparkline"].project(RenderTarget.JSON)

        yield_projections = []
        yields_to_show = state.yields[: state.max_yields_shown]
        for i in range(len(yields_to_show)):
            yield_card = self.slots[f"yield_{i}"]
            yield_projections.append(yield_card.project(RenderTarget.JSON))

        result["yields"] = yield_projections
        result["entropy_slider"] = self.slots["entropy_slider"].project(RenderTarget.JSON)

        return result
