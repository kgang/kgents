"""
DashboardScreen: Real-time system health TUI.

A Textual-based dashboard showing:
- K-gent Soul state (mode, garden patterns, last dream)
- Metabolism (pressure, temperature, fever state)
- Database Triad health (durability, resonance, reflex)
- Recent AGENTESE traces

Layout:
┌─────────────────────────────────────────────────────────────────┐
│ kgents dashboard                                     [q] quit   │
├───────────────────────────────┬─────────────────────────────────┤
│  K-GENT                       │  METABOLISM                     │
│  ├─ Mode: DIALOGUE            │  ├─ Pressure: ████░░░░ 42%      │
│  ├─ Garden: 12 patterns       │  ├─ Temperature: 0.72           │
│  └─ Last dream: 2h ago        │  └─ Fever: No                   │
├───────────────────────────────┼─────────────────────────────────┤
│  FLUX                         │  TRIAD                          │
│  ├─ Events/sec: 2.5           │  ├─ D ████████░░ PG             │
│  ├─ Queue: 7 pending          │  ├─ R ██████░░░░ Qd             │
│  └─ Active agents: 3          │  └─ F █████████░ Rd             │
├─────────────────────────────────────────────────────────────────┤
│  RECENT TRACES                                                  │
│  ├─ self.soul.challenge ("singleton") → REJECT     [23ms]       │
│  ├─ world.cortex.invoke (gpt-4) → success          [1.2s]       │
│  └─ void.entropy.tithe (0.1) → discharged          [1ms]        │
└─────────────────────────────────────────────────────────────────┘

Keybindings:
- q: Quit
- r: Refresh now
- 1-4: Focus panel
- d: Toggle demo mode

Philosophy: "Make the system's metabolism visible."
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..data.garden import GardenSnapshot
    from ..data.state import FluxState

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..data.dashboard_collectors import (
    DashboardMetrics,
    MetricsObservable,
    create_demo_metrics,
)
from ..widgets.sparkline import generate_sparkline

if TYPE_CHECKING:
    pass


# =============================================================================
# Focus Style Constants
# =============================================================================

# Consistent focus styling across all panels
FOCUS_CSS = """
    /* Unfocused state: subtle round border */
    {cls} {{
        width: 1fr;
        height: auto;
        border: round {color};
        padding: 0 1;
        background: #1a1a1a;
    }}

    /* Focused state: thick double border + brighter background */
    {cls}:focus {{
        border: double {focus_color};
        background: #252525;
    }}
"""


# =============================================================================
# Panel Widgets
# =============================================================================


class KgentPanel(Static, can_focus=True):
    """K-gent soul state panel."""

    DEFAULT_CSS = (
        FOCUS_CSS.format(cls="KgentPanel", color="#7d9c7a", focus_color="#90ee90d6")
        + """
    KgentPanel .panel-title {
        color: #7d9c7a;
        text-style: bold;
    }

    KgentPanel .metric-value {
        color: #f5f0e6;
    }

    KgentPanel .metric-label {
        color: #6a6560;
    }

    KgentPanel .offline {
        color: #e88a8a;
    }
    """
    )

    is_focused: reactive[bool] = reactive(False)
    mode: reactive[str] = reactive("--")
    garden_patterns: reactive[int] = reactive(0)
    garden_trees: reactive[int] = reactive(0)
    interactions: reactive[int] = reactive(0)
    last_dream: reactive[str] = reactive("--")
    is_online: reactive[bool] = reactive(True)

    def render(self) -> str:
        if not self.is_online:
            return "K-GENT\n├─ [offline]"

        return (
            f"K-GENT\n"
            f"├─ Mode: {self.mode.upper()}\n"
            f"├─ Garden: {self.garden_patterns} patterns ({self.garden_trees} trees)\n"
            f"├─ Interactions: {self.interactions}\n"
            f"└─ Last dream: {self.last_dream}"
        )

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        self.mode = metrics.kgent.mode
        self.garden_patterns = metrics.kgent.garden_patterns
        self.garden_trees = metrics.kgent.garden_trees
        self.interactions = metrics.kgent.interactions_count
        self.last_dream = metrics.kgent.dream_age_str
        self.is_online = metrics.kgent.is_online


class MetabolismPanel(Static, can_focus=True):
    """Metabolic engine state panel."""

    DEFAULT_CSS = (
        FOCUS_CSS.format(
            cls="MetabolismPanel", color="#e6a352", focus_color="#ffa500d6"
        )
        + """
    MetabolismPanel .panel-title {
        color: #e6a352;
        text-style: bold;
    }

    MetabolismPanel .hot {
        color: #e88a8a;
    }

    MetabolismPanel .warm {
        color: #e6a352;
    }

    MetabolismPanel .cool {
        color: #7d9c7a;
    }
    """
    )

    pressure: reactive[float] = reactive(0.0)
    temperature: reactive[float] = reactive(0.0)
    in_fever: reactive[bool] = reactive(False)
    status: reactive[str] = reactive("COOL")
    is_online: reactive[bool] = reactive(True)

    # Pressure history for sparkline
    _pressure_history: list[float] = []

    def render(self) -> str:
        if not self.is_online:
            return "METABOLISM\n├─ [offline]"

        # Build pressure bar
        bar_width = 10
        filled = int(self.pressure * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        pct = int(self.pressure * 100)

        # Sparkline
        sparkline = generate_sparkline(self._pressure_history, width=10)

        fever_str = "FEVER!" if self.in_fever else "No"

        return (
            f"METABOLISM ({self.status})\n"
            f"├─ Pressure: {bar} {pct}%\n"
            f"├─ History: {sparkline}\n"
            f"├─ Temperature: {self.temperature:.2f}\n"
            f"└─ Fever: {fever_str}"
        )

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        self.pressure = metrics.metabolism.pressure
        self.temperature = metrics.metabolism.temperature
        self.in_fever = metrics.metabolism.in_fever
        self.status = metrics.metabolism.status_text
        self.is_online = metrics.metabolism.is_online

        # Track pressure history
        self._pressure_history.append(self.pressure)
        if len(self._pressure_history) > 30:
            self._pressure_history = self._pressure_history[-30:]


class FluxPanel(Static, can_focus=True):
    """Flux event processing panel."""

    DEFAULT_CSS = (
        FOCUS_CSS.format(cls="FluxPanel", color="#8ac4e8", focus_color="#00bfffd6")
        + """
    FluxPanel .panel-title {
        color: #8ac4e8;
        text-style: bold;
    }

    FluxPanel .flowing {
        color: #7d9c7a;
    }

    FluxPanel .backed-up {
        color: #e88a8a;
    }
    """
    )

    events_per_second: reactive[float] = reactive(0.0)
    queue_depth: reactive[int] = reactive(0)
    active_agents: reactive[int] = reactive(0)
    total_events: reactive[int] = reactive(0)
    status: reactive[str] = reactive("IDLE")
    is_online: reactive[bool] = reactive(True)

    # Throughput history for sparkline
    _throughput_history: list[float] = []

    def render(self) -> str:
        if not self.is_online:
            return "FLUX\n├─ [offline]"

        sparkline = generate_sparkline(self._throughput_history, width=10)

        return (
            f"FLUX ({self.status})\n"
            f"├─ Events/sec: {self.events_per_second:.1f} {sparkline}\n"
            f"├─ Queue: {self.queue_depth} pending\n"
            f"├─ Active agents: {self.active_agents}\n"
            f"└─ Total: {self.total_events:,}"
        )

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        self.events_per_second = metrics.flux.events_per_second
        self.queue_depth = metrics.flux.queue_depth
        self.active_agents = metrics.flux.active_agents
        self.total_events = metrics.flux.total_events_processed
        self.status = metrics.flux.status_text
        self.is_online = metrics.flux.is_online

        # Track throughput history
        self._throughput_history.append(self.events_per_second)
        if len(self._throughput_history) > 30:
            self._throughput_history = self._throughput_history[-30:]


class TriadPanel(Static, can_focus=True):
    """Database triad health panel."""

    DEFAULT_CSS = (
        FOCUS_CSS.format(cls="TriadPanel", color="#b3a89a", focus_color="#daa520d6")
        + """
    TriadPanel .panel-title {
        color: #b3a89a;
        text-style: bold;
    }

    TriadPanel .healthy {
        color: #7d9c7a;
    }

    TriadPanel .degraded {
        color: #e6a352;
    }

    TriadPanel .critical {
        color: #e88a8a;
    }
    """
    )

    durability: reactive[float] = reactive(0.0)
    resonance: reactive[float] = reactive(0.0)
    reflex: reactive[float] = reactive(0.0)
    cdc_lag_ms: reactive[float] = reactive(0.0)
    synapse_active: reactive[bool] = reactive(False)
    status: reactive[str] = reactive("--")
    is_online: reactive[bool] = reactive(True)

    def _render_bar(self, value: float, width: int = 8) -> str:
        """Render a health bar."""
        filled = int(value * width)
        return "█" * filled + "░" * (width - filled)

    def render(self) -> str:
        if not self.is_online:
            return "TRIAD\n├─ [offline]"

        d_bar = self._render_bar(self.durability)
        r_bar = self._render_bar(self.resonance)
        f_bar = self._render_bar(self.reflex)

        synapse = "●" if self.synapse_active else "○"

        # Format CDC lag
        if self.cdc_lag_ms < 1000:
            lag_str = f"{int(self.cdc_lag_ms)}ms"
        else:
            lag_str = f"{self.cdc_lag_ms / 1000:.1f}s"

        return (
            f"TRIAD ({self.status})\n"
            f"├─ D {d_bar} PG\n"
            f"├─ R {r_bar} Qd\n"
            f"├─ F {f_bar} Rd\n"
            f"├─ CDC lag: {lag_str}\n"
            f"└─ Synapse: {synapse}"
        )

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        self.durability = metrics.triad.durability
        self.resonance = metrics.triad.resonance
        self.reflex = metrics.triad.reflex
        self.cdc_lag_ms = metrics.triad.cdc_lag_ms
        self.synapse_active = metrics.triad.synapse_active
        self.status = metrics.triad.status_text
        self.is_online = metrics.triad.is_online


class TracesPanel(Static):
    """Recent AGENTESE traces panel."""

    DEFAULT_CSS = """
    TracesPanel {
        width: 100%;
        height: auto;
        min-height: 5;
        border: round #6a6560;
        padding: 0 1;
        background: #1a1a1a;
    }

    TracesPanel .panel-title {
        color: #f5f0e6;
        text-style: bold;
    }

    TracesPanel .trace-path {
        color: #8ac4e8;
    }

    TracesPanel .trace-result {
        color: #7d9c7a;
    }

    TracesPanel .trace-reject {
        color: #e88a8a;
    }
    """

    traces: reactive[str] = reactive("")

    def render(self) -> str:
        if not self.traces:
            return "RECENT TRACES\n└─ (no traces yet)"

        return f"RECENT TRACES\n{self.traces}"

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        if not metrics.traces:
            self.traces = ""
            return

        lines = []
        for i, trace in enumerate(metrics.traces[:5]):
            prefix = "└─" if i == len(metrics.traces) - 1 else "├─"
            lines.append(f"{prefix} {trace.render(show_timestamp=False)}")

        self.traces = "\n".join(lines)


class TraceAnalysisPanel(Static):
    """Static call graph analysis panel with call trees."""

    DEFAULT_CSS = """
    TraceAnalysisPanel {
        width: 100%;
        height: auto;
        min-height: 6;
        border: round #c9a86c;
        padding: 0 1;
        background: #1a1a1a;
    }

    TraceAnalysisPanel .panel-title {
        color: #c9a86c;
        text-style: bold;
    }

    TraceAnalysisPanel .function-hot {
        color: #e88a8a;
    }

    TraceAnalysisPanel .function-warm {
        color: #e6a352;
    }

    TraceAnalysisPanel .function-cool {
        color: #7d9c7a;
    }

    TraceAnalysisPanel .stat {
        color: #6a6560;
    }
    """

    content: reactive[str] = reactive("")
    is_online: reactive[bool] = reactive(True)

    def render(self) -> str:
        if not self.is_online:
            return "CALL GRAPH\n└─ [offline]"

        if not self.content:
            return "CALL GRAPH\n└─ (analyzing...)"

        return f"CALL GRAPH\n{self.content}"

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        ta = metrics.trace_analysis
        self.is_online = ta.is_online

        if not ta.is_online or ta.files_analyzed == 0:
            self.content = ""
            return

        lines = []

        # Stats line
        lines.append(
            f"├─ {ta.files_analyzed:,} files │ "
            f"{ta.definitions_found:,} defs │ "
            f"{ta.calls_found:,} calls"
        )

        # Hottest functions
        if ta.hottest_functions:
            lines.append("├─ Hot Functions:")
            for i, func in enumerate(ta.hottest_functions[:3]):
                name = func.get("name", "?")
                callers = func.get("callers", 0)
                # Truncate long function names
                if len(name) > 30:
                    name = name[:27] + "..."
                prefix = "│  └─" if i == len(ta.hottest_functions[:3]) - 1 else "│  ├─"
                lines.append(f"{prefix} {name} ({callers})")

        # Call trees (if available)
        if ta.call_trees:
            lines.append("└─ Call Trees:")
            for i, tree in enumerate(ta.call_trees[:2]):
                tree_str = self._render_call_tree(
                    tree, is_last=(i == len(ta.call_trees[:2]) - 1)
                )
                lines.append(tree_str)
        else:
            lines.append("└─ (no call trees)")

        self.content = "\n".join(lines)

    def _render_call_tree(
        self, node: Any, prefix: str = "   ", is_last: bool = True
    ) -> str:
        """Render a CallTreeNode as ASCII."""
        # Handle the CallTreeNode render method if available
        if hasattr(node, "render"):
            tree_lines = node.render().split("\n")
            # Indent for dashboard context
            indented = []
            for line in tree_lines[:5]:  # Limit to 5 lines
                indented.append(f"   {line}")
            return "\n".join(indented)
        return f"   ● {getattr(node, 'name', 'unknown')}"


# =============================================================================
# Dashboard Screen
# =============================================================================


class DashboardScreen(Screen[None]):
    """
    Real-time system health dashboard.

    Shows K-gent, Metabolism, Flux, and Triad metrics with
    live updates and recent AGENTESE traces.
    """

    CSS = """
    DashboardScreen {
        background: #1a1a1a;
    }

    DashboardScreen #panels-grid {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
        height: auto;
    }

    DashboardScreen #bottom-panels {
        padding: 0 1 1 1;
        height: auto;
    }

    DashboardScreen #traces-container {
        width: 1fr;
        height: auto;
        padding-right: 1;
    }

    DashboardScreen #trace-analysis-container {
        width: 1fr;
        height: auto;
    }

    DashboardScreen #status-bar {
        dock: bottom;
        height: 1;
        background: #252525;
        color: #6a6560;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "toggle_demo", "Demo Mode"),
    ]

    demo_mode: reactive[bool] = reactive(False)

    def on_key(self, event: Key) -> None:
        """Handle key presses for panel focus."""
        if event.key == "1":
            if self._kgent_panel:
                self._kgent_panel.focus()
        elif event.key == "2":
            if self._metabolism_panel:
                self._metabolism_panel.focus()
        elif event.key == "3":
            if self._flux_panel:
                self._flux_panel.focus()
        elif event.key == "4":
            if self._triad_panel:
                self._triad_panel.focus()

    def __init__(
        self,
        demo_mode: bool = False,
        refresh_interval: float = 1.0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.demo_mode = demo_mode
        self.refresh_interval = refresh_interval
        self._observable = MetricsObservable()
        self._kgent_panel: KgentPanel | None = None
        self._metabolism_panel: MetabolismPanel | None = None
        self._flux_panel: FluxPanel | None = None
        self._triad_panel: TriadPanel | None = None
        self._traces_panel: TracesPanel | None = None
        self._trace_analysis_panel: TraceAnalysisPanel | None = None
        self._status_bar: Static | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        # Main 2x2 grid of metric panels
        with Grid(id="panels-grid"):
            self._kgent_panel = KgentPanel(id="kgent-panel")
            yield self._kgent_panel

            self._metabolism_panel = MetabolismPanel(id="metabolism-panel")
            yield self._metabolism_panel

            self._flux_panel = FluxPanel(id="flux-panel")
            yield self._flux_panel

            self._triad_panel = TriadPanel(id="triad-panel")
            yield self._triad_panel

        # Bottom panels: Traces (left) and Call Graph (right)
        with Horizontal(id="bottom-panels"):
            with Container(id="traces-container"):
                self._traces_panel = TracesPanel(id="traces-panel")
                yield self._traces_panel

            with Container(id="trace-analysis-container"):
                self._trace_analysis_panel = TraceAnalysisPanel(
                    id="trace-analysis-panel"
                )
                yield self._trace_analysis_panel

        # Status bar
        self._status_bar = Static("Collecting metrics...", id="status-bar")
        yield self._status_bar

        yield Footer()

    async def on_mount(self) -> None:
        """Start metrics collection when screen is mounted."""
        self.title = "kgents dashboard"

        # Subscribe to metrics updates
        self._observable.subscribe(self._on_metrics_update)

        # Start collecting (demo mode uses randomized data)
        await self._observable.start_collecting(
            interval=self.refresh_interval,
            demo_mode=self.demo_mode,
        )

    async def on_unmount(self) -> None:
        """Stop metrics collection when screen is unmounted."""
        await self._observable.stop()

    def _on_metrics_update(self, metrics: DashboardMetrics) -> None:
        """Handle new metrics from observable."""
        # Update all panels
        if self._kgent_panel:
            self._kgent_panel.update_from_metrics(metrics)
        if self._metabolism_panel:
            self._metabolism_panel.update_from_metrics(metrics)
        if self._flux_panel:
            self._flux_panel.update_from_metrics(metrics)
        if self._triad_panel:
            self._triad_panel.update_from_metrics(metrics)
        if self._traces_panel:
            self._traces_panel.update_from_metrics(metrics)
        if self._trace_analysis_panel:
            self._trace_analysis_panel.update_from_metrics(metrics)

        # Update status bar
        if self._status_bar:
            mode_str = "[DEMO]" if self.demo_mode else "[LIVE]"
            offline_str = " (some services offline)" if metrics.any_offline else ""
            ts = metrics.collected_at.strftime("%H:%M:%S")
            self._status_bar.update(f"{mode_str} Last update: {ts}{offline_str}")

    async def action_refresh(self) -> None:
        """Force refresh metrics now."""
        from ..data.dashboard_collectors import collect_metrics, create_random_metrics

        if self.demo_mode:
            metrics = create_random_metrics()
        else:
            metrics = await collect_metrics()

        self._on_metrics_update(metrics)
        self.notify("Refreshed")

    async def action_toggle_demo(self) -> None:
        """Toggle demo mode."""
        self.demo_mode = not self.demo_mode

        # Restart collection with new mode
        await self._observable.stop()
        await self._observable.start_collecting(
            interval=self.refresh_interval,
            demo_mode=self.demo_mode,
        )

        mode = "DEMO" if self.demo_mode else "LIVE"
        self.notify(f"Mode: {mode}")


# =============================================================================
# Dashboard App (Standalone)
# =============================================================================


class DashboardApp(App[None]):
    """
    Standalone dashboard application with unified navigation.

    Can be run directly or embedded in kgents CLI.
    Integrates all screens (Observatory, Cockpit, Forge, Debugger) with
    NavigationController for seamless zoom in/out.
    """

    CSS = """
    Screen {
        background: #1a1a1a;
    }
    """

    TITLE = "kgents dashboard"

    BINDINGS = [
        ("plus", "zoom_in", "Zoom In"),
        ("equal", "zoom_in", "Zoom In"),
        ("minus", "zoom_out", "Zoom Out"),
        ("underscore", "zoom_out", "Zoom Out"),
        ("f", "open_forge", "Forge"),
        ("d", "open_debugger", "Debugger"),
        ("question_mark", "show_help", "Help"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, demo_mode: bool = False, refresh_interval: float = 1.0) -> None:
        super().__init__()
        self.demo_mode = demo_mode
        self.refresh_interval = refresh_interval

        # Initialize navigation system
        from ..navigation import NavigationController, StateManager

        self._state_manager = StateManager()
        self._nav_controller = NavigationController(self, self._state_manager)

        # Track current LOD for screen factories
        self._current_lod = 0

        # Store data for screen creation
        self._flux_state: FluxState | None = None
        self._gardens: list[GardenSnapshot] | None = None

    def on_mount(self) -> None:
        """Push the dashboard screen on mount and register navigation."""
        # Register screen factories with navigation controller
        self._register_screens()

        # Push the initial dashboard screen (LOD 0)
        self.push_screen(
            DashboardScreen(
                demo_mode=self.demo_mode,
                refresh_interval=self.refresh_interval,
            )
        )

    def _register_screens(self) -> None:
        """Register all screens with the navigation controller."""
        # LOD -1: Observatory
        self._nav_controller.register_lod_screen(-1, self._create_observatory)

        # LOD 0: Dashboard/Terrarium
        self._nav_controller.register_lod_screen(0, self._create_dashboard)

        # LOD 1: Cockpit
        self._nav_controller.register_lod_screen(1, self._create_cockpit)

        # LOD 2: Debugger (will be handled specially)
        # Debugger requires weave, so we don't register it here

        # Special screens
        self._nav_controller.register_forge(self._create_forge)
        self._nav_controller.register_debugger(self._create_debugger)

    def _create_observatory(self) -> None:
        """Create and push Observatory screen."""
        from ..data.garden import create_demo_gardens
        from ..data.state import create_demo_flux_state
        from .observatory import ObservatoryScreen

        if self.demo_mode and self._gardens is None:
            self._gardens = create_demo_gardens()
        if self.demo_mode and self._flux_state is None:
            self._flux_state = create_demo_flux_state()

        self.push_screen(
            ObservatoryScreen(
                gardens=self._gardens,
                flux_state=self._flux_state,
                demo_mode=self.demo_mode,
            )
        )

    def _create_dashboard(self) -> None:
        """Create and push Dashboard screen."""
        self.push_screen(
            DashboardScreen(
                demo_mode=self.demo_mode,
                refresh_interval=self.refresh_interval,
            )
        )

    def _create_cockpit(self) -> None:
        """Create and push Cockpit screen."""
        from .cockpit import CockpitScreen

        # Get focused agent from state manager
        focus = self._state_manager.get_focus(
            "observatory"
        ) or self._state_manager.get_focus("terrarium")

        self.push_screen(
            CockpitScreen(
                agent_id=focus or "",
                demo_mode=self.demo_mode,
            )
        )

    def _create_forge(self) -> None:
        """Create and push Forge screen."""
        from .forge.screen import ForgeScreen

        self.push_screen(ForgeScreen())

    def _create_debugger(self, turn_id: str | None = None) -> None:
        """Create and push Debugger screen."""
        from weave import TheWeave

        from .debugger_screen import DebuggerScreen

        # Create a demo weave for now
        # In production, this would come from the focused agent
        weave = TheWeave()

        self.push_screen(
            DebuggerScreen(
                weave=weave,
                agent_id=turn_id,
            )
        )

    # ========================================================================
    # Global Actions (Key Bindings)
    # ========================================================================

    async def action_zoom_in(self) -> None:
        """Zoom in to next lower LOD (+/=)."""
        await self._nav_controller.zoom_in()

    async def action_zoom_out(self) -> None:
        """Zoom out to next higher LOD (-/_)."""
        await self._nav_controller.zoom_out()

    def action_open_forge(self) -> None:
        """Open Forge screen (f)."""
        self._nav_controller.go_to_forge()

    def action_open_debugger(self) -> None:
        """Open Debugger screen (d)."""
        self._nav_controller.go_to_debugger()

    def action_show_help(self) -> None:
        """Show help overlay (?)."""
        help_text = """
DASHBOARD NAVIGATION

Zoom:
  +/=  - Zoom in (more detail)
  -/_  - Zoom out (broader view)

Screens:
  f    - Open Forge (agent composition)
  d    - Open Debugger (turn analysis)

Other:
  ?    - Show this help
  q    - Quit

LOD Levels:
  -1   - Observatory (ecosystem view)
   0   - Dashboard (system health)
   1   - Cockpit (single agent)
   2   - Debugger (forensic analysis)
"""
        self.notify(help_text, timeout=10)


# =============================================================================
# CLI Entry Point
# =============================================================================


def run_dashboard(demo_mode: bool = False, refresh_interval: float = 1.0) -> None:
    """
    Run the dashboard TUI.

    Args:
        demo_mode: Use demo data instead of live metrics
        refresh_interval: Seconds between metric updates
    """
    app = DashboardApp(demo_mode=demo_mode, refresh_interval=refresh_interval)
    app.run()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "DashboardScreen",
    "DashboardApp",
    "KgentPanel",
    "MetabolismPanel",
    "FluxPanel",
    "TriadPanel",
    "TracesPanel",
    "TraceAnalysisPanel",
    "run_dashboard",
]
