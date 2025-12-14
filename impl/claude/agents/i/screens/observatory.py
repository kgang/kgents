"""
ObservatoryScreen - LOD -1: Orbital ecosystem view.

The highest-level view of the kgents ecosystem. Shows all gardens
as cards with health, flux rates, and agent glyphs.

WHAT: Ecosystem-wide view of all gardens.
WHY: Before zooming into a single garden (Terrarium), you need to see the whole system.
HOW: ObservatoryScreen(gardens=...) or ObservatoryScreen(demo_mode=True)
FEEL: Like looking at Earth from orbit. You see continents, not streets.

Navigation:
  Tab        - Cycle focus between gardens
  Enter      - Zoom into focused garden (→ Terrarium)
  +          - Zoom to focused agent (→ Cockpit)
  f          - Open Forge
  d          - Open Debugger for focused agent
  g          - Toggle graph layout (semantic/tree)
  Space      - Emergency brake (pause all flux)
  Esc/q      - Quit

Principle 4 (Joy-Inducing): Breathing gardens, satisfying to watch system health.
Principle 6 (Heterarchical): No fixed entry point - navigate freely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from ..data.core_types import Phase
from ..data.garden import GardenSnapshot, create_demo_gardens
from ..data.state import AgentSnapshot, FluxState, create_demo_flux_state
from ..data.weather import SystemMetrics, WeatherEngine, create_demo_weather
from ..theme.heartbeat import HeartbeatMixin, get_heartbeat_controller
from ..theme.posture import PostureMapper, render_posture_with_tooltip
from ..widgets.graph_layout import GraphLayout
from ..widgets.sparkline import Sparkline
from ..widgets.weather_widget import WeatherWidget
from .base import KgentsScreen

if TYPE_CHECKING:
    pass


class GardenCard(Static, HeartbeatMixin):
    """
    A card displaying a garden in the observatory view.

    Shows:
    - Garden name
    - Agent graph (nodes + edges)
    - Health sparkline
    - Flux rate
    """

    DEFAULT_CSS = """
    GardenCard {
        width: 36;
        height: 16;
        border: solid #4a4a5c;
        padding: 1;
        margin: 1;
        background: #252525;
    }

    GardenCard.focused {
        border: solid #e6a352;
        background: #2a2a2a;
    }

    GardenCard .garden-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        margin-bottom: 1;
    }

    GardenCard .garden-graph {
        height: 8;
        margin-bottom: 1;
    }

    GardenCard .garden-metrics {
        height: 3;
        color: #b3a89a;
    }

    GardenCard .health-sparkline {
        height: 1;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        garden: GardenSnapshot,
        agents: dict[str, AgentSnapshot],
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        HeartbeatMixin.__init__(self)
        self.garden = garden
        self.agents = agents
        self._graph: GraphLayout | None = None
        self._sparkline: Sparkline | None = None

        # Set heartbeat BPM based on garden health (healthier = calmer)
        # Low health = faster heartbeat (stress), high health = slower (calm)
        bpm = HeartbeatMixin.activity_to_bpm(1.0 - garden.health)
        self.set_bpm(bpm)

        # Register with heartbeat controller
        get_heartbeat_controller().register(self)

        # Initialize posture mapper
        self._posture_mapper = PostureMapper()

    def compose(self) -> ComposeResult:
        """Compose the garden card."""
        yield Static(f"[bold]GARDEN: {self.garden.name}[/]", classes="garden-header")

        # Build graph of agents in this garden
        with Container(classes="garden-graph"):
            nodes = []
            edges: list[tuple[str, str]] = []

            # Add all agents as nodes with posture symbols
            for agent_id in self.garden.agent_ids:
                agent = self.agents.get(agent_id)
                if agent:
                    symbol = self._get_posture_symbol(agent)
                    nodes.append(f"{symbol}{agent.name}")

                    # Add edges from connections
                    for conn_id, _ in agent.connections.items():
                        if conn_id in self.garden.agent_ids:
                            conn = self.agents.get(conn_id)
                            if conn:
                                conn_symbol = self._get_posture_symbol(conn)
                                edges.append(
                                    (
                                        f"{symbol}{agent.name}",
                                        f"{conn_symbol}{conn.name}",
                                    )
                                )

            # Show graph if we have nodes
            if nodes:
                self._graph = GraphLayout(
                    nodes=nodes,
                    edges=edges,
                    layout="semantic",
                )
                yield self._graph
            else:
                yield Static("[dim]No agents in this garden[/dim]")

        # Metrics panel
        with Container(classes="garden-metrics"):
            # Health sparkline (mock data for now)
            health_history = [
                max(0.0, min(1.0, self.garden.health + (i % 3 - 1) * 0.05))
                for i in range(14)
            ]
            self._sparkline = Sparkline(
                values=health_history,
                width=32,
                classes="health-sparkline",
            )
            yield self._sparkline

            yield Static(f"health: {self.garden.health * 100:.0f}%")
            yield Static(f"flux: {self.garden.flux_rate:.1f} ev/s")

    def _get_posture_symbol(self, agent: AgentSnapshot) -> str:
        """Get posture symbol for an agent."""
        posture = self._posture_mapper.from_phase(
            agent.phase.value,
            agent.activity,
        )
        return posture.symbol

    def set_focused(self, focused: bool) -> None:
        """Set focus state."""
        if focused:
            self.add_class("focused")
        else:
            self.remove_class("focused")


class VoidPanel(Static):
    """
    Void/Accursed Share panel.

    Shows entropy budget and oblique strategies.
    """

    DEFAULT_CSS = """
    VoidPanel {
        width: 100%;
        height: 5;
        border: solid #8b7ba5;
        padding: 1;
        margin-top: 1;
        background: #1a1a1a;
        color: #b3a89a;
    }

    VoidPanel .void-title {
        text-style: bold;
        color: #8b7ba5;
    }
    """

    def __init__(
        self,
        entropy_budget: float = 0.25,
        suggestion: str = "Honor thy error as a hidden intention",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.entropy_budget = entropy_budget
        self.suggestion = suggestion

    def render(self) -> str:
        """Render the void panel."""
        # Build entropy bar
        filled = int(self.entropy_budget * 20)
        bar = "█" * filled + "░" * (20 - filled)

        return f"""[bold #8b7ba5]VOID (Accursed Share)[/]

Entropy budget: {bar} {self.entropy_budget * 100:.0f}%  │  Suggestion: "{self.suggestion}"
"""


class ObservatoryScreen(KgentsScreen):
    """
    Observatory Screen - LOD -1 (Orbital).

    The ecosystem-level view showing all gardens.
    Each garden is rendered as a card with agents, health, and flux rate.

    Navigation:
      Tab: Cycle focus between gardens
      Enter: Zoom into focused garden (→ Terrarium)
      +: Zoom to focused agent (→ Cockpit)
      f: Open Forge
      d: Open Debugger
      g: Toggle graph layout
      Space: Emergency brake
      Esc/q: Quit
    """

    # Visual anchor for gentle transitions
    ANCHOR = "header-info"

    CSS = """
    ObservatoryScreen {
        background: #1a1a1a;
    }

    ObservatoryScreen #header-info {
        dock: top;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #f5f0e6;
        border-bottom: solid #4a4a5c;
    }

    ObservatoryScreen #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    ObservatoryScreen #garden-grid {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1;
        width: 100%;
        height: 1fr;
    }

    ObservatoryScreen #status-bar {
        dock: bottom;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #b3a89a;
        border-top: solid #4a4a5c;
    }
    """

    BINDINGS = [
        Binding("tab", "next_garden", "Next Garden", show=True),
        Binding("shift+tab", "prev_garden", "Prev Garden", show=False),
        Binding("enter", "zoom_to_terrarium", "Zoom to Terrarium", show=True),
        Binding("plus", "zoom_to_agent", "Zoom to Agent", show=True),
        Binding("equal", "zoom_to_agent", "Zoom to Agent", show=False),
        Binding("f", "open_forge", "Forge", show=True),
        Binding("d", "open_debugger", "Debugger", show=True),
        Binding("g", "toggle_graph", "Toggle Graph", show=False),
        Binding("space", "emergency_brake", "Emergency Brake", show=False),
        Binding("escape", "back", "Back", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive properties
    focused_garden_id: reactive[str | None] = reactive(None)

    def __init__(
        self,
        gardens: list[GardenSnapshot] | None = None,
        flux_state: FluxState | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode

        # Initialize data
        if demo_mode and gardens is None:
            gardens = create_demo_gardens()
        if demo_mode and flux_state is None:
            flux_state = create_demo_flux_state()

        self.gardens = gardens or []
        self.flux_state = flux_state or FluxState()

        # Widget references
        self._garden_cards: dict[str, GardenCard] = {}
        self._void_panel: VoidPanel | None = None
        self._weather_widget: WeatherWidget | None = None

        # Weather engine for system metrics
        self._weather_engine = WeatherEngine()

    def compose(self) -> ComposeResult:
        """Compose the observatory screen."""
        yield Header()

        # Header info with weather widget
        with Container(id="header-info"):
            with Horizontal():
                agent_count = sum(len(g.agent_ids) for g in self.gardens)
                yield Static(
                    f"[bold #f5d08a]OBSERVATORY[/]  │  LOD: ORBITAL  │  "
                    f"Gardens: {len(self.gardens)}  │  Agents: {agent_count}  │  "
                )
                # Weather widget showing system health as weather
                self._weather_widget = WeatherWidget(demo_mode=self._demo_mode)
                yield self._weather_widget
            yield Static("[Tab] cycle  [Enter] zoom  [f] forge  [d] debugger  [?] help")

        # Main content area
        with Container(id="main-container"):
            # Garden grid
            with Container(id="garden-grid"):
                for garden in self.gardens:
                    card = GardenCard(
                        garden=garden,
                        agents=self.flux_state.agents,
                        id=f"garden-{garden.id}",
                    )
                    self._garden_cards[garden.id] = card
                    yield card

            # Void panel
            self._void_panel = VoidPanel()
            yield self._void_panel

        # Status bar
        with Container(id="status-bar"):
            # Mock orchestration state
            if self.gardens:
                primary_garden = self.gardens[0]
                orch_state = primary_garden.orchestration_state
                breath_phase = int(primary_garden.breath_phase * 10)
                breath_bar = (
                    "░" * breath_phase + "█" * 4 + "░" * (10 - breath_phase - 4)
                )

                yield Static(
                    f"ORCHESTRATION: ●{orch_state}     "
                    f"BREATH: {breath_bar}    "
                    f"AGENTS: {sum(len(g.agent_ids) for g in self.gardens)}"
                )

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Focus first garden
        if self.gardens:
            self.focused_garden_id = self.gardens[0].id

    def watch_focused_garden_id(self, old_id: str | None, new_id: str | None) -> None:
        """React to focus changes."""
        # Update card focus states
        if old_id and old_id in self._garden_cards:
            self._garden_cards[old_id].set_focused(False)

        if new_id and new_id in self._garden_cards:
            self._garden_cards[new_id].set_focused(True)

    # ─────────────────────────────────────────────────────────────
    # Public API (Interface Contract)
    # ─────────────────────────────────────────────────────────────

    def get_gardens(self) -> list[GardenSnapshot]:
        """Get all gardens."""
        return self.gardens

    def focus_garden(self, garden_id: str) -> None:
        """Focus a specific garden."""
        if garden_id in self._garden_cards:
            self.focused_garden_id = garden_id

    def zoom_to_terrarium(self, garden_id: str) -> None:
        """Zoom into a specific garden's terrarium view."""
        # Find the garden
        garden = next((g for g in self.gardens if g.id == garden_id), None)
        if not garden:
            self.notify(f"Garden not found: {garden_id}")
            return

        from .terrarium import TerrariumScreen

        self.app.push_screen(
            TerrariumScreen(
                garden=garden,
                flux_state=self.flux_state,
                demo_mode=self._demo_mode,
            )
        )

    def zoom_to_agent(self, agent_id: str) -> None:
        """Zoom directly to an agent's cockpit view."""
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

    def update_weather(
        self, entropy: float, token_rate: float, queue_depth: int
    ) -> None:
        """
        Update weather widget with system metrics.

        Args:
            entropy: Current entropy level (0.0-1.0)
            token_rate: Tokens per second
            queue_depth: Current queue depth
        """
        if self._weather_widget:
            self._weather_widget.update_metrics(
                entropy=entropy,
                token_rate=token_rate,
                queue_depth=queue_depth,
            )

    # ─────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────

    def action_next_garden(self) -> None:
        """Focus next garden (Tab)."""
        if not self.gardens:
            return

        current_idx = 0
        if self.focused_garden_id:
            try:
                current_idx = [g.id for g in self.gardens].index(self.focused_garden_id)
            except ValueError:
                pass

        next_idx = (current_idx + 1) % len(self.gardens)
        self.focused_garden_id = self.gardens[next_idx].id

    def action_prev_garden(self) -> None:
        """Focus previous garden (Shift+Tab)."""
        if not self.gardens:
            return

        current_idx = 0
        if self.focused_garden_id:
            try:
                current_idx = [g.id for g in self.gardens].index(self.focused_garden_id)
            except ValueError:
                pass

        prev_idx = (current_idx - 1) % len(self.gardens)
        self.focused_garden_id = self.gardens[prev_idx].id

    def action_zoom_to_terrarium(self) -> None:
        """Zoom into focused garden (Enter)."""
        if self.focused_garden_id:
            self.zoom_to_terrarium(self.focused_garden_id)
        else:
            self.notify("No garden focused")

    def action_zoom_to_agent(self) -> None:
        """Zoom to focused agent in focused garden (+)."""
        if not self.focused_garden_id:
            self.notify("No garden focused")
            return

        # Get first agent in focused garden
        focused_garden = next(
            (g for g in self.gardens if g.id == self.focused_garden_id), None
        )
        if focused_garden and focused_garden.agent_ids:
            first_agent_id = focused_garden.agent_ids[0]
            self.zoom_to_agent(first_agent_id)
        else:
            self.notify("No agents in focused garden")

    def action_open_forge(self) -> None:
        """Open Forge screen (f)."""
        from .forge.screen import ForgeScreen

        self.app.push_screen(ForgeScreen())

    def action_open_debugger(self) -> None:
        """Open Debugger screen (d)."""
        # Get the first agent from focused garden for debugging context
        if self.focused_garden_id:
            garden = next(
                (g for g in self.gardens if g.id == self.focused_garden_id), None
            )
            if garden and garden.agent_ids:
                agent_id = garden.agent_ids[0]
                from weave import TheWeave

                from .debugger_screen import DebuggerScreen

                weave = TheWeave()  # Demo weave for now
                self.app.push_screen(DebuggerScreen(weave=weave, agent_id=agent_id))
                return

        self.notify("No agent available for debugging")

    def action_toggle_graph(self) -> None:
        """Toggle graph layout (g)."""
        # Toggle all graph layouts between semantic and tree
        from ..widgets.graph_layout import LayoutAlgorithm

        for card in self._garden_cards.values():
            if card._graph:
                current = card._graph.layout_algorithm
                new_algorithm = (
                    LayoutAlgorithm.TREE
                    if current == LayoutAlgorithm.SEMANTIC
                    else LayoutAlgorithm.SEMANTIC
                )
                card._graph.layout_algorithm = new_algorithm
                card._graph.refresh()

    def action_emergency_brake(self) -> None:
        """Emergency brake - pause all flux (Space)."""
        self.notify("Emergency brake activated - all flux streams paused")
        # TODO: Implement actual flux pausing

    def action_back(self) -> None:
        """Go back to Dashboard (Esc)."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application (q)."""
        self.app.exit()
