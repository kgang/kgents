"""
TerrariumScreen - LOD 0: Surface view of a single garden.

The Terrarium is the middle ground between the orbital Observatory (LOD -1)
and the operational Cockpit (LOD 1). It shows agents as living organisms
in a shared environment with pheromone trails and stigmergic dynamics.

WHAT: Multi-agent field view with pheromone dynamics.
WHY: Before focusing on a single agent (Cockpit), see how they interact.
HOW: TerrariumScreen(garden=...) or TerrariumScreen(demo_mode=True)
FEEL: Like watching an ant colony. You see patterns of collaboration.

Navigation:
  Tab        - Cycle focus between agents
  Enter/+    - Zoom into focused agent (→ Cockpit)
  -/Esc      - Zoom out to Observatory
  f          - Open Forge
  d          - Open Debugger for focused agent
  1-4        - Switch sub-views (FIELD/TRACES/FLUX/TURNS)
  Space      - Emergency brake (pause all flux)
  ?          - Help

Principle 4 (Joy-Inducing): Pheromone trails, satisfying to watch flow.
Principle 6 (Heterarchical): Navigate freely between agents.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..data.core_types import Phase
from ..data.garden import GardenSnapshot, create_demo_gardens
from ..data.state import AgentSnapshot, FluxState, create_demo_flux_state
from ..widgets.density_field import DensityField
from ..widgets.sparkline import Sparkline

if TYPE_CHECKING:
    pass


# =============================================================================
# Agent Card Widget (for Terrarium)
# =============================================================================


class TerrariumAgentCard(Static, can_focus=True):
    """
    An agent card for the Terrarium view.

    Shows agent as a living organism with:
    - Density field visualization
    - Phase indicator
    - Activity sparkline
    - Connection count
    """

    DEFAULT_CSS = """
    TerrariumAgentCard {
        width: 28;
        height: 10;
        border: solid #4a4a5c;
        padding: 1;
        margin: 1;
        background: #252525;
    }

    TerrariumAgentCard:focus {
        border: double #e6a352;
        background: #2a2a2a;
    }

    TerrariumAgentCard .agent-name {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
    }

    TerrariumAgentCard .agent-phase {
        height: 1;
        color: #b3a89a;
    }

    TerrariumAgentCard .density-area {
        height: 4;
    }

    TerrariumAgentCard .agent-metrics {
        height: 2;
        color: #6a6560;
    }
    """

    # Reactive properties for heartbeat animation
    _pulse_phase: reactive[float] = reactive(0.0)
    _pulse_bpm: reactive[int] = reactive(60)

    def __init__(
        self,
        agent: AgentSnapshot,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.agent = agent
        self._density_field: DensityField | None = None
        self._sparkline: Sparkline | None = None
        self._activity_history: list[float] = self._init_activity_history()

    def _init_activity_history(self) -> list[float]:
        """Initialize activity history with some variance."""
        base = self.agent.activity
        return [max(0.0, min(1.0, base + (i % 5 - 2) * 0.05)) for i in range(12)]

    def _phase_to_symbol(self, phase: Phase) -> str:
        """Convert phase to symbol."""
        symbols = {
            Phase.DORMANT: "○",
            Phase.WAKING: "◐",
            Phase.ACTIVE: "●",
            Phase.WANING: "◑",
            Phase.VOID: "◌",
        }
        return symbols.get(phase, "○")

    def compose(self) -> ComposeResult:
        """Compose the agent card."""
        symbol = self._phase_to_symbol(self.agent.phase)
        yield Static(f"{symbol} {self.agent.name}", classes="agent-name")
        yield Static(f"[{self.agent.phase.value}]", classes="agent-phase")

        with Container(classes="density-area"):
            self._density_field = DensityField(
                agent_id=self.agent.id,
                agent_name=self.agent.name,
                activity=self.agent.activity,
                phase=self.agent.phase,
            )
            yield self._density_field

        with Container(classes="agent-metrics"):
            self._sparkline = Sparkline(
                values=self._activity_history,
                width=24,
            )
            yield self._sparkline

            conn_count = len(self.agent.connections)
            yield Static(f"↔ {conn_count} connections")

    def update_agent(self, agent: AgentSnapshot) -> None:
        """Update the displayed agent."""
        self.agent = agent
        if self._density_field:
            self._density_field.activity = agent.activity
            self._density_field.phase = agent.phase

        # Update activity history
        self._activity_history.append(agent.activity)
        self._activity_history = self._activity_history[-12:]
        if self._sparkline:
            self._sparkline.values = self._activity_history

    def get_pulse_opacity(self) -> float:
        """Get current pulse opacity for heartbeat effect."""
        return 0.7 + 0.3 * math.sin(self._pulse_phase)

    def set_bpm(self, bpm: int) -> None:
        """Set heartbeat BPM based on agent activity."""
        self._pulse_bpm = max(30, min(180, bpm))


# =============================================================================
# Sub-view Widgets
# =============================================================================


class TracesSubview(Static):
    """Recent AGENTESE traces sub-view."""

    DEFAULT_CSS = """
    TracesSubview {
        width: 100%;
        height: 100%;
        padding: 1;
        color: #b3a89a;
    }
    """

    def __init__(
        self,
        traces: list[dict[str, str]] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.traces = traces or self._create_demo_traces()

    def _create_demo_traces(self) -> list[dict[str, str]]:
        """Create demo trace data."""
        now = datetime.now()
        return [
            {
                "path": "self.soul.challenge",
                "args": '"singleton"',
                "result": "ACCEPT",
                "duration": "12ms",
                "time": (now - timedelta(seconds=5)).strftime("%H:%M:%S"),
            },
            {
                "path": "world.cortex.invoke",
                "args": "claude-3",
                "result": "success",
                "duration": "1.2s",
                "time": (now - timedelta(seconds=15)).strftime("%H:%M:%S"),
            },
            {
                "path": "void.entropy.tithe",
                "args": "0.05",
                "result": "discharged",
                "duration": "<1ms",
                "time": (now - timedelta(seconds=30)).strftime("%H:%M:%S"),
            },
            {
                "path": "self.memory.store",
                "args": '"analysis"',
                "result": "stored",
                "duration": "3ms",
                "time": (now - timedelta(seconds=45)).strftime("%H:%M:%S"),
            },
        ]

    def render(self) -> str:
        """Render traces sub-view."""
        lines = ["[bold]Recent AGENTESE Invocations[/]", ""]

        for i, trace in enumerate(self.traces[:8]):
            prefix = "└─" if i == len(self.traces[:8]) - 1 else "├─"
            path = trace.get("path", "?")
            args = trace.get("args", "")
            result = trace.get("result", "?")
            duration = trace.get("duration", "?")

            # Color result based on type
            if result in ("ACCEPT", "success", "stored", "discharged"):
                result_color = "#7d9c7a"  # green
            elif result in ("REJECT", "error"):
                result_color = "#e88a8a"  # red
            else:
                result_color = "#b3a89a"  # neutral

            lines.append(
                f"{prefix} [{result_color}]{path}[/] ({args}) → {result}  [{duration}]"
            )

        return "\n".join(lines)


class FluxSubview(Static):
    """Event stream and throughput sub-view."""

    DEFAULT_CSS = """
    FluxSubview {
        width: 100%;
        height: 100%;
        padding: 1;
        color: #b3a89a;
    }
    """

    def __init__(
        self,
        events_per_second: float = 2.3,
        queue_depth: int = 7,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.events_per_second = events_per_second
        self.queue_depth = queue_depth
        self._throughput_history = [
            1.8,
            2.1,
            2.5,
            2.3,
            2.7,
            2.2,
            2.4,
            2.3,
            2.6,
            2.5,
            2.3,
            2.4,
        ]

    def render(self) -> str:
        """Render flux sub-view."""
        # Build throughput sparkline
        spark_chars = " ▁▂▃▄▅▆▇█"
        max_val = max(self._throughput_history) if self._throughput_history else 1
        sparkline = ""
        for v in self._throughput_history[-20:]:
            idx = int((v / max_val) * 8)
            sparkline += spark_chars[min(idx, 8)]

        return f"""[bold]Event Flux[/]

├─ Events/sec: {self.events_per_second:.1f}
├─ Throughput: {sparkline}
├─ Queue depth: {self.queue_depth}
└─ Status: [#7d9c7a]FLOWING[/]
"""


class TurnsSubview(Static):
    """Turn counts by type sub-view."""

    DEFAULT_CSS = """
    TurnsSubview {
        width: 100%;
        height: 100%;
        padding: 1;
        color: #b3a89a;
    }
    """

    def __init__(
        self,
        turn_counts: dict[str, int] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.turn_counts = turn_counts or {
            "SPEECH": 47,
            "ACTION": 23,
            "THOUGHT": 89,
            "YIELD": 3,
            "SILENCE": 12,
        }

    def render(self) -> str:
        """Render turns sub-view."""
        lines = ["[bold]Turn Summary[/]", ""]

        type_colors = {
            "SPEECH": "#7d9c7a",  # green
            "ACTION": "#8ac4e8",  # blue
            "THOUGHT": "#6a6560",  # dim
            "YIELD": "#f5d08a",  # yellow
            "SILENCE": "#6a6560",  # dim
        }

        total = sum(self.turn_counts.values())

        for turn_type, count in sorted(
            self.turn_counts.items(), key=lambda x: x[1], reverse=True
        ):
            color = type_colors.get(turn_type, "#b3a89a")
            pct = (count / total * 100) if total > 0 else 0
            bar_width = int(pct / 5)
            bar = "█" * bar_width + "░" * (20 - bar_width)
            lines.append(f"├─ [{color}]{turn_type:8}[/] {bar} {count:4} ({pct:.0f}%)")

        lines.append(f"└─ Total: {total}")
        return "\n".join(lines)


# =============================================================================
# Terrarium Screen
# =============================================================================


class TerrariumScreen(Screen[None]):
    """
    Terrarium Screen - LOD 0 (Surface).

    The garden-level view showing multiple agents as living organisms.
    Features pheromone trails, stigmergic dynamics, and sub-views.

    Navigation:
      Tab: Cycle focus between agents
      Enter/+: Zoom into focused agent (→ Cockpit)
      -/Esc: Zoom out to Observatory
      f: Open Forge
      d: Open Debugger
      1-4: Switch sub-views
      Space: Emergency brake
      ?: Help
    """

    CSS = """
    TerrariumScreen {
        background: #1a1a1a;
    }

    TerrariumScreen #header-info {
        dock: top;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #f5f0e6;
        border-bottom: solid #4a4a5c;
    }

    TerrariumScreen #main-container {
        width: 100%;
        height: 100%;
    }

    TerrariumScreen #field-area {
        width: 100%;
        height: 2fr;
        padding: 1;
    }

    TerrariumScreen #agent-grid {
        layout: grid;
        grid-size: 4 2;
        grid-gutter: 1;
        width: 100%;
        height: 100%;
    }

    TerrariumScreen #metrics-bar {
        dock: bottom;
        height: 2;
        background: #252525;
        padding: 0 2;
        color: #b3a89a;
    }

    TerrariumScreen #subview-area {
        width: 100%;
        height: 1fr;
        border: solid #4a4a5c;
        padding: 1;
    }

    TerrariumScreen #subview-tabs {
        height: 1;
        background: #2a2a2a;
        padding: 0 1;
    }

    TerrariumScreen .tab-active {
        color: #e6a352;
        text-style: bold;
    }

    TerrariumScreen .tab-inactive {
        color: #6a6560;
    }
    """

    BINDINGS = [
        Binding("tab", "next_agent", "Next Agent", show=True),
        Binding("shift+tab", "prev_agent", "Prev Agent", show=False),
        Binding("enter", "zoom_to_cockpit", "Zoom to Cockpit", show=True),
        Binding("plus", "zoom_to_cockpit", "Zoom to Cockpit", show=False),
        Binding("equal", "zoom_to_cockpit", "Zoom to Cockpit", show=False),
        Binding("minus", "zoom_to_observatory", "Zoom Out", show=True),
        Binding("underscore", "zoom_to_observatory", "Zoom Out", show=False),
        Binding("f", "open_forge", "Forge", show=True),
        Binding("d", "open_debugger", "Debugger", show=True),
        Binding("1", "subview_field", "Field", show=False),
        Binding("2", "subview_traces", "Traces", show=False),
        Binding("3", "subview_flux", "Flux", show=False),
        Binding("4", "subview_turns", "Turns", show=False),
        Binding("space", "emergency_brake", "Emergency Brake", show=False),
        Binding("escape", "zoom_to_observatory", "Back", show=True),
        Binding("question_mark", "show_help", "Help", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive properties
    focused_agent_id: reactive[str | None] = reactive(None)
    current_subview: reactive[str] = reactive("field")

    def __init__(
        self,
        garden: GardenSnapshot | None = None,
        flux_state: FluxState | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode

        # Initialize data
        if demo_mode:
            gardens = create_demo_gardens()
            garden = gardens[0] if gardens else None
            flux_state = create_demo_flux_state()

        self.garden = garden
        self.flux_state = flux_state or FluxState()

        # Widget references
        self._agent_cards: dict[str, TerrariumAgentCard] = {}
        self._subview_widgets: dict[str, Static] = {}
        self._subview_container: Container | None = None

    def compose(self) -> ComposeResult:
        """Compose the terrarium screen."""
        yield Header()

        # Header info
        with Container(id="header-info"):
            garden_name = self.garden.name if self.garden else "Unknown"
            agent_count = len(self.garden.agent_ids) if self.garden else 0
            entropy = 0.45  # Demo value

            yield Static(
                f"[bold #f5d08a]TERRARIUM: {garden_name}[/]  │  "
                f"LOD: SURFACE  │  Agents: {agent_count}  │  "
                f"Entropy: {entropy * 100:.0f}%"
            )
            yield Static(
                "[Tab] cycle  [Enter/+] cockpit  [-] observatory  "
                "[1-4] subview  [?] help"
            )

        # Main content area
        with Container(id="main-container"):
            # Agent field area
            with Container(id="field-area"):
                with Container(id="agent-grid"):
                    if self.garden and self.garden.agent_ids:
                        for agent_id in self.garden.agent_ids[:8]:  # Max 8 agents
                            agent = self.flux_state.agents.get(agent_id)
                            if agent:
                                card = TerrariumAgentCard(
                                    agent=agent, id=f"agent-{agent_id}"
                                )
                                self._agent_cards[agent_id] = card
                                yield card
                    else:
                        yield Static(
                            "[dim]No agents in this garden[/dim]",
                            id="empty-garden",
                        )

            # Sub-view area
            with Container(id="subview-area"):
                # Sub-view tabs
                yield Static(
                    "[1][bold #e6a352]FIELD[/]  [2]TRACES  [3]FLUX  [4]TURNS",
                    id="subview-tabs",
                )

                # Sub-view content container
                self._subview_container = Container(id="subview-content")
                with self._subview_container:
                    yield Static(
                        "[dim]Agent spatial layout with pheromone gradients[/dim]",
                        id="field-subview",
                    )

        # Metrics bar
        with Container(id="metrics-bar"):
            phase = "FLUX"
            turn_rate = 3.2
            yield Static(
                f"PHASE: ●{phase}    FOCUS: [{self.focused_agent_id or 'None'}]    "
                f"TURN RATE: {turn_rate}/s"
            )

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Focus first agent
        if self._agent_cards:
            first_id = list(self._agent_cards.keys())[0]
            self.focused_agent_id = first_id
            if first_id in self._agent_cards:
                self._agent_cards[first_id].focus()

    def watch_focused_agent_id(self, old_id: str | None, new_id: str | None) -> None:
        """React to focus changes."""
        # Visual feedback could be added here
        pass

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def get_agents(self) -> list[AgentSnapshot]:
        """Get all agents in the terrarium."""
        if not self.garden:
            return []
        return [
            self.flux_state.agents[aid]
            for aid in self.garden.agent_ids
            if aid in self.flux_state.agents
        ]

    def focus_agent(self, agent_id: str) -> None:
        """Focus a specific agent."""
        if agent_id in self._agent_cards:
            self.focused_agent_id = agent_id
            self._agent_cards[agent_id].focus()

    def zoom_to_cockpit(self, agent_id: str) -> None:
        """Zoom into an agent's cockpit view."""
        agent = self.flux_state.agents.get(agent_id)
        if agent:
            from .cockpit import CockpitScreen

            self.app.push_screen(
                CockpitScreen(
                    agent_snapshot=agent,
                    agent_id=agent_id,
                    agent_name=agent.name,
                    demo_mode=self._demo_mode,
                )
            )
        else:
            self.notify(f"Agent not found: {agent_id}")

    # ─────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────

    def action_next_agent(self) -> None:
        """Focus next agent (Tab)."""
        if not self._agent_cards:
            return

        agent_ids = list(self._agent_cards.keys())
        current_idx = 0
        if self.focused_agent_id and self.focused_agent_id in agent_ids:
            current_idx = agent_ids.index(self.focused_agent_id)

        next_idx = (current_idx + 1) % len(agent_ids)
        self.focus_agent(agent_ids[next_idx])

    def action_prev_agent(self) -> None:
        """Focus previous agent (Shift+Tab)."""
        if not self._agent_cards:
            return

        agent_ids = list(self._agent_cards.keys())
        current_idx = 0
        if self.focused_agent_id and self.focused_agent_id in agent_ids:
            current_idx = agent_ids.index(self.focused_agent_id)

        prev_idx = (current_idx - 1) % len(agent_ids)
        self.focus_agent(agent_ids[prev_idx])

    def action_zoom_to_cockpit(self) -> None:
        """Zoom into focused agent (Enter/+)."""
        if self.focused_agent_id:
            self.zoom_to_cockpit(self.focused_agent_id)
        else:
            self.notify("No agent focused")

    def action_zoom_to_observatory(self) -> None:
        """Zoom out to Observatory (-/Esc)."""
        self.app.pop_screen()

    def action_open_forge(self) -> None:
        """Open Forge screen (f)."""
        from .forge.screen import ForgeScreen

        self.app.push_screen(ForgeScreen())

    def action_open_debugger(self) -> None:
        """Open Debugger screen (d)."""
        if self.focused_agent_id:
            from weave import TheWeave

            from .debugger_screen import DebuggerScreen

            weave = TheWeave()  # Demo weave
            self.app.push_screen(
                DebuggerScreen(
                    weave=weave,
                    agent_id=self.focused_agent_id,
                )
            )
        else:
            self.notify("No agent focused for debugging")

    def action_subview_field(self) -> None:
        """Switch to FIELD sub-view (1)."""
        self.current_subview = "field"
        self._update_subview()

    def action_subview_traces(self) -> None:
        """Switch to TRACES sub-view (2)."""
        self.current_subview = "traces"
        self._update_subview()

    def action_subview_flux(self) -> None:
        """Switch to FLUX sub-view (3)."""
        self.current_subview = "flux"
        self._update_subview()

    def action_subview_turns(self) -> None:
        """Switch to TURNS sub-view (4)."""
        self.current_subview = "turns"
        self._update_subview()

    def action_emergency_brake(self) -> None:
        """Emergency brake - pause all flux (Space)."""
        self.notify("Emergency brake activated - all flux streams paused")

    def action_show_help(self) -> None:
        """Show help (?)."""
        help_text = """
TERRARIUM - The Garden View (LOD 0)

Navigation:
  Tab        - Cycle between agents
  Enter/+    - Zoom into agent (→ Cockpit)
  -/Esc      - Zoom out (→ Observatory)
  h/j/k/l    - Navigate agent grid

Sub-views:
  1          - FIELD (spatial layout)
  2          - TRACES (AGENTESE paths)
  3          - FLUX (event throughput)
  4          - TURNS (turn counts)

Special:
  f          - Open Forge
  d          - Open Debugger
  Space      - Emergency brake
  q          - Quit
"""
        self.notify(help_text, timeout=10)

    def action_quit(self) -> None:
        """Quit the application (q)."""
        self.app.exit()

    def _update_subview(self) -> None:
        """Update the sub-view content based on current selection."""
        if not self._subview_container:
            return

        # Update tab indicator
        tabs_widget = self.query_one("#subview-tabs", Static)
        tab_styles = {
            "field": "[bold #e6a352]",
            "traces": "[bold #e6a352]",
            "flux": "[bold #e6a352]",
            "turns": "[bold #e6a352]",
        }

        tabs_text = []
        for i, name in enumerate(["FIELD", "TRACES", "FLUX", "TURNS"], 1):
            if name.lower() == self.current_subview:
                tabs_text.append(f"[{i}]{tab_styles[name.lower()]}{name}[/]")
            else:
                tabs_text.append(f"[{i}]{name}")

        tabs_widget.update("  ".join(tabs_text))


__all__ = ["TerrariumScreen", "TerrariumAgentCard"]
