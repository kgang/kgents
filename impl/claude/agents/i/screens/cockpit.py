"""
CockpitScreen - The operational view (LOD Level 1: SURFACE).

The middle zoom level. More than a card, less than an MRI.
This is where you operate the agent - adjust parameters, see metrics,
monitor active processes.

WHAT: Operational dashboard for a single agent.
WHY: Between glancing (ORBIT) and debugging (INTERNAL), you need to operate.
     This is where you adjust temperature, see semaphores, watch the flow.
HOW: CockpitScreen(agent_snapshot=snapshot) or CockpitScreen(demo_mode=True)
FEEL: Like sitting in a control room. Dials, gauges, switches. You're the pilot.

Principle 6 (Heterarchical): The cockpit respects agent autonomy - you guide, not command.
Principle 4 (Joy-Inducing): Satisfying to adjust a slider and see the agent respond.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..data.core_types import Phase
from ..data.state import AgentSnapshot, create_demo_flux_state
from ..widgets.density_field import DensityField
from ..widgets.entropy import entropy_to_params
from ..widgets.graph_layout import GraphLayout
from ..widgets.slider import Slider
from ..widgets.sparkline import Sparkline

if TYPE_CHECKING:
    pass


def create_demo_snapshot() -> AgentSnapshot:
    """Create a demo agent snapshot for testing."""
    state = create_demo_flux_state()
    # Return the first agent, or create a minimal one
    if state.agents:
        return list(state.agents.values())[0]
    return AgentSnapshot(
        id="demo-agent",
        name="Demo Agent",
        phase=Phase.ACTIVE,
        activity=0.65,
        summary="A demonstration agent for the cockpit view.",
        grid_x=0,
        grid_y=0,
        children=[],
        connections={"L-gent": 0.8, "D-gent": 0.5, "N-gent": 0.3},
    )


class SemaphoreDisplay(Static):
    """Display active semaphores (running processes, locks)."""

    DEFAULT_CSS = """
    SemaphoreDisplay {
        width: 100%;
        height: auto;
        padding: 1;
    }

    SemaphoreDisplay .semaphore-active {
        color: #e6a352;
    }

    SemaphoreDisplay .semaphore-waiting {
        color: #8b7ba5;
    }

    SemaphoreDisplay .semaphore-idle {
        color: #6a6560;
    }
    """

    def __init__(
        self,
        semaphores: list[dict[str, str]] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.semaphores = semaphores or []

    def render(self) -> str:
        """Render semaphore list."""
        if not self.semaphores:
            return "[dim]No active semaphores[/dim]"

        lines = []
        for sem in self.semaphores:
            status = sem.get("status", "idle")
            name = sem.get("name", "unknown")
            if status == "active":
                lines.append(f"[#e6a352]● {name}[/]")
            elif status == "waiting":
                lines.append(f"[#8b7ba5]○ {name}[/]")
            else:
                lines.append(f"[#6a6560]◌ {name}[/]")

        return "\n".join(lines)


class ThoughtsStream(Static):
    """Display recent thoughts/actions stream."""

    DEFAULT_CSS = """
    ThoughtsStream {
        width: 100%;
        height: auto;
        padding: 1;
        color: #b3a89a;
    }

    ThoughtsStream .thought-new {
        color: #f5d08a;
    }

    ThoughtsStream .thought-old {
        color: #6a6560;
    }
    """

    def __init__(
        self,
        thoughts: list[dict[str, str]] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.thoughts = thoughts or []

    def render(self) -> str:
        """Render thoughts stream."""
        if not self.thoughts:
            return "[dim]No recent thoughts[/dim]"

        lines = []
        for i, thought in enumerate(self.thoughts[:5]):  # Show last 5
            timestamp = thought.get("time", "")
            content = thought.get("content", "")[:50]
            if i == 0:
                lines.append(f"[#f5d08a]{timestamp} {content}[/]")
            else:
                lines.append(f"[#6a6560]{timestamp} {content}[/]")

        return "\n".join(lines)


class CockpitScreen(Screen[None]):
    """
    Cockpit View - LOD Level 1 (Surface).

    The operational dashboard showing:
    - Larger DensityField with entropy visualization
    - MetricsPanel (pressure/flow/temp from Terrarium)
    - Active semaphores display
    - Recent thoughts stream
    - Mini connection graph
    - Temperature slider for direct manipulation

    Navigation:
      +: Zoom to MRI (LOD 2)
      -: Zoom to Flux (LOD 0)
      h/l: Adjust temperature
      t: Show Loom view
      Esc: Back to Flux
    """

    CSS = """
    CockpitScreen {
        background: #1a1a1a;
    }

    CockpitScreen #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    CockpitScreen #header-info {
        dock: top;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #f5f0e6;
        border-bottom: solid #4a4a5c;
    }

    CockpitScreen #left-panel {
        width: 50%;
        height: 100%;
        padding: 0 1;
    }

    CockpitScreen #right-panel {
        width: 50%;
        height: 100%;
        padding: 0 1;
    }

    CockpitScreen .panel {
        border: solid #4a4a5c;
        padding: 1;
        margin-bottom: 1;
        background: #252525;
    }

    CockpitScreen .panel-title {
        text-style: bold;
        color: #e6a352;
        margin-bottom: 1;
    }

    CockpitScreen .density-panel {
        height: 12;
    }

    CockpitScreen .metrics-panel {
        height: 8;
    }

    CockpitScreen .semaphore-panel {
        height: 8;
    }

    CockpitScreen .thoughts-panel {
        height: 10;
    }

    CockpitScreen .graph-panel {
        height: 12;
    }

    CockpitScreen .slider-panel {
        height: 4;
    }

    CockpitScreen .agent-name {
        text-style: bold;
        color: #f5d08a;
    }

    CockpitScreen .phase-indicator {
        color: #b3a89a;
    }

    CockpitScreen .activity-sparkline {
        height: 1;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("plus", "zoom_in", "Zoom to MRI", show=True),
        Binding("equal", "zoom_in", "Zoom to MRI", show=False),
        Binding("minus", "zoom_out", "Zoom to Flux", show=True),
        Binding("underscore", "zoom_out", "Zoom to Flux", show=False),
        Binding("t", "show_loom", "Loom View", show=True),
        Binding("h", "decrease_temp", "Temp -", show=False),
        Binding("l", "increase_temp", "Temp +", show=False),
        Binding("left", "decrease_temp", "Temp -", show=False),
        Binding("right", "increase_temp", "Temp +", show=False),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive properties
    temperature: reactive[float] = reactive(0.7)

    def __init__(
        self,
        agent_snapshot: AgentSnapshot | None = None,
        agent_id: str = "",
        agent_name: str = "",
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode

        if demo_mode and agent_snapshot is None:
            agent_snapshot = create_demo_snapshot()

        self.agent_snapshot = agent_snapshot
        self.agent_id = agent_id or (agent_snapshot.id if agent_snapshot else "")
        self.agent_name = agent_name or (agent_snapshot.name if agent_snapshot else "")

        # Demo data for semaphores and thoughts
        self._semaphores = self._create_demo_semaphores() if demo_mode else []
        self._thoughts = self._create_demo_thoughts() if demo_mode else []
        self._activity_history = (
            self._create_demo_activity_history() if demo_mode else []
        )

        # Widget references
        self._density_field: DensityField | None = None
        self._temp_slider: Slider | None = None
        self._sparkline: Sparkline | None = None
        self._graph: GraphLayout | None = None

    def _create_demo_semaphores(self) -> list[dict[str, str]]:
        """Create demo semaphores."""
        return [
            {"name": "world.pubmed.search", "status": "active"},
            {"name": "concept.summary.refine", "status": "waiting"},
            {"name": "self.memory.query", "status": "idle"},
        ]

    def _create_demo_thoughts(self) -> list[dict[str, str]]:
        """Create demo thoughts stream."""
        now = datetime.now()
        return [
            {
                "time": (now - timedelta(seconds=5)).strftime("%H:%M:%S"),
                "content": "Analyzing protein structure data...",
            },
            {
                "time": (now - timedelta(seconds=30)).strftime("%H:%M:%S"),
                "content": "Retrieved 47 PubMed results",
            },
            {
                "time": (now - timedelta(minutes=1)).strftime("%H:%M:%S"),
                "content": "Initiated semantic search",
            },
            {
                "time": (now - timedelta(minutes=2)).strftime("%H:%M:%S"),
                "content": "User requested analysis",
            },
            {
                "time": (now - timedelta(minutes=5)).strftime("%H:%M:%S"),
                "content": "Session started",
            },
        ]

    def _create_demo_activity_history(self) -> list[float]:
        """Create demo activity history for sparkline."""
        return [
            0.3,
            0.4,
            0.5,
            0.6,
            0.65,
            0.7,
            0.65,
            0.8,
            0.7,
            0.65,
            0.6,
            0.7,
            0.75,
            0.65,
        ]

    def compose(self) -> ComposeResult:
        """Compose the cockpit screen."""
        yield Header()

        # Header info
        with Container(id="header-info"):
            phase_str = (
                self.agent_snapshot.phase.value if self.agent_snapshot else "UNKNOWN"
            )
            yield Static(
                f"[bold #f5d08a]COCKPIT: {self.agent_name or self.agent_id or 'Unknown'}[/]  │  "
                f"[#b3a89a]Phase: {phase_str}[/]"
            )
            yield Static("LOD: SURFACE  │  +: MRI  -: Flux  t: Loom  Esc: Back")

        # Main content area - two columns
        with Container(id="main-container"):
            with Horizontal():
                # Left panel
                with Vertical(id="left-panel"):
                    # Density field (larger)
                    with Container(classes="panel density-panel"):
                        yield Static("[Density Field]", classes="panel-title")
                        if self.agent_snapshot:
                            self._density_field = DensityField(
                                agent_id=self.agent_snapshot.id,
                                agent_name=self.agent_snapshot.name,
                                activity=self.agent_snapshot.activity,
                                phase=self.agent_snapshot.phase,
                                entropy=self.temperature
                                * 0.5,  # Derive entropy from temp
                            )
                            yield self._density_field

                            # Activity sparkline
                            self._sparkline = Sparkline(
                                values=self._activity_history,
                                width=30,
                                classes="activity-sparkline",
                            )
                            yield self._sparkline
                        else:
                            yield Static("[dim]No agent data[/dim]")

                    # Metrics panel
                    with Container(classes="panel metrics-panel"):
                        yield Static("[Metrics]", classes="panel-title")
                        if self.agent_snapshot:
                            # Mock metrics from activity - simple display
                            pressure = self.agent_snapshot.activity * 0.8
                            flow = self.agent_snapshot.activity * 1.2
                            yield Static(f"Pressure: {pressure:.2f}")
                            yield Static(f"Flow:     {flow:.2f}")
                            yield Static(f"Temp:     {self.temperature:.2f}")
                        else:
                            yield Static("[dim]No metrics available[/dim]")

                    # Temperature slider
                    with Container(classes="panel slider-panel"):
                        yield Static("[Temperature Control]", classes="panel-title")
                        self._temp_slider = Slider(
                            value=self.temperature,
                            min_val=0.0,
                            max_val=1.0,
                            step=0.05,
                            label="Temp",
                            show_value=True,
                            on_change=self._on_temperature_change,
                        )
                        yield self._temp_slider

                # Right panel
                with Vertical(id="right-panel"):
                    # Semaphores
                    with Container(classes="panel semaphore-panel"):
                        yield Static("[Active Semaphores]", classes="panel-title")
                        yield SemaphoreDisplay(semaphores=self._semaphores)

                    # Thoughts stream
                    with Container(classes="panel thoughts-panel"):
                        yield Static("[Recent Thoughts]", classes="panel-title")
                        yield ThoughtsStream(thoughts=self._thoughts)

                    # Mini connection graph
                    with Container(classes="panel graph-panel"):
                        yield Static("[Connections]", classes="panel-title")
                        if self.agent_snapshot and self.agent_snapshot.connections:
                            # Build nodes from agent + connections
                            agent_name = (
                                self.agent_snapshot.name or self.agent_snapshot.id
                            )
                            nodes = [agent_name]
                            edges: list[tuple[str, str]] = []
                            # connections is dict[str, float] - take first 5 by key
                            conn_items = list(self.agent_snapshot.connections.items())[
                                :5
                            ]
                            for conn_name, _ in conn_items:
                                nodes.append(conn_name)
                                edges.append((agent_name, conn_name))

                            self._graph = GraphLayout(
                                nodes=nodes,
                                edges=edges,
                                layout="semantic",
                            )
                            yield self._graph
                        else:
                            yield Static("[dim]No connection data[/dim]")

        yield Footer()

    def _on_temperature_change(self, new_temp: float) -> None:
        """Handle temperature slider changes."""
        self.temperature = new_temp

        # Update density field entropy based on temperature
        if self._density_field:
            self._density_field.entropy = new_temp * 0.5

    def watch_temperature(self, new_temp: float) -> None:
        """React to temperature changes."""
        # Update slider if needed
        if self._temp_slider and abs(self._temp_slider.value - new_temp) > 0.001:
            self._temp_slider.value = new_temp

        # Update density field
        if self._density_field:
            self._density_field.entropy = new_temp * 0.5

    # ─────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────

    def action_back(self) -> None:
        """Return to previous screen (Escape)."""
        self.dismiss()

    def action_zoom_in(self) -> None:
        """Zoom to MRI view (+ key)."""
        if not self.agent_snapshot:
            self.notify("No agent selected")
            return

        from .mri import MRIScreen

        self.app.push_screen(
            MRIScreen(
                agent_snapshot=self.agent_snapshot,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
            )
        )

    def action_zoom_out(self) -> None:
        """Zoom out to Flux view (- key)."""
        self.dismiss()

    def action_show_loom(self) -> None:
        """Show Loom view (t key)."""
        from .loom import LoomScreen

        self.app.push_screen(
            LoomScreen(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                demo_mode=self._demo_mode,
            )
        )

    def action_decrease_temp(self) -> None:
        """Decrease temperature (h/left key)."""
        self.temperature = max(0.0, self.temperature - 0.05)

    def action_increase_temp(self) -> None:
        """Increase temperature (l/right key)."""
        self.temperature = min(1.0, self.temperature + 0.05)

    def action_refresh(self) -> None:
        """Refresh cockpit data (r key)."""
        self.notify("Refreshing cockpit data...")
        # In a real implementation, this would fetch new data from the agent

    def action_quit(self) -> None:
        """Quit the application (q key)."""
        self.app.exit()

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def update_snapshot(self, snapshot: AgentSnapshot) -> None:
        """Update the displayed agent snapshot."""
        self.agent_snapshot = snapshot
        self.agent_id = snapshot.id
        self.agent_name = snapshot.name

        # Update widgets
        if self._density_field:
            self._density_field.activity = snapshot.activity
            self._density_field.phase = snapshot.phase

    def add_thought(self, content: str) -> None:
        """Add a new thought to the stream."""
        now = datetime.now().strftime("%H:%M:%S")
        self._thoughts.insert(0, {"time": now, "content": content})
        self._thoughts = self._thoughts[:5]  # Keep last 5
        self.refresh()

    def update_activity_history(self, new_value: float) -> None:
        """Add a new value to activity history."""
        self._activity_history.append(new_value)
        self._activity_history = self._activity_history[-20:]  # Keep last 20
        if self._sparkline:
            self._sparkline.values = self._activity_history
