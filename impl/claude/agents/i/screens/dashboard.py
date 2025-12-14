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
from ..data.replay_integration import ScenarioReplayProvider
from ..data.weather import WeatherEngine
from ..widgets.replay_controls import ReplayControlsWidget
from ..widgets.sparkline import generate_sparkline
from ..widgets.weather_widget import CompactWeatherWidget, WeatherWidget

# Import mixins for DashboardApp decomposition
from .mixins import (
    DashboardHelpMixin,
    DashboardNavigationMixin,
    DashboardScreensMixin,
)

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

    # Detailed lifecycle counts
    garden_seeds: reactive[int] = reactive(0)
    garden_saplings: reactive[int] = reactive(0)
    garden_flowers: reactive[int] = reactive(0)
    garden_compost: reactive[int] = reactive(0)
    garden_season: reactive[str] = reactive("summer")

    def _render_lifecycle_bar(self) -> str:
        """Render garden lifecycle as visual bar: 🌱🌿🌳🌸🍂"""
        # Icons for each lifecycle stage
        icons = {
            "seed": "🌱",
            "sapling": "🌿",
            "tree": "🌳",
            "flower": "🌸",
            "compost": "🍂",
        }
        parts = []
        for stage, count, icon in [
            ("seed", self.garden_seeds, icons["seed"]),
            ("sapling", self.garden_saplings, icons["sapling"]),
            ("tree", self.garden_trees, icons["tree"]),
            ("flower", self.garden_flowers, icons["flower"]),
            ("compost", self.garden_compost, icons["compost"]),
        ]:
            if count > 0:
                parts.append(f"{icon}{count}")
        return " ".join(parts) if parts else "empty"

    def render(self) -> str:
        if not self.is_online:
            return "K-GENT\n├─ [offline]"

        lifecycle_bar = self._render_lifecycle_bar()
        season_emoji = {
            "spring": "🌱",
            "summer": "☀️",
            "autumn": "🍂",
            "winter": "❄️",
        }.get(self.garden_season, "")

        return (
            f"K-GENT ({self.mode.upper()})\n"
            f"├─ Garden: {self.garden_patterns} patterns {season_emoji}\n"
            f"│  └─ {lifecycle_bar}\n"
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

        # Update lifecycle counts
        self.garden_seeds = metrics.kgent.garden_seeds
        self.garden_saplings = metrics.kgent.garden_saplings
        self.garden_flowers = metrics.kgent.garden_flowers
        self.garden_compost = metrics.kgent.garden_compost
        self.garden_season = metrics.kgent.garden_season


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
    fever_count: reactive[int] = reactive(0)
    last_tithe: reactive[str] = reactive("never")

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

        # Fever indicator with history
        if self.in_fever:
            fever_str = f"🔥 ACTIVE! ({self.fever_count} total)"
        elif self.fever_count > 0:
            fever_str = f"No ({self.fever_count} past)"
        else:
            fever_str = "No"

        return (
            f"METABOLISM ({self.status})\n"
            f"├─ Pressure: {bar} {pct}%\n"
            f"├─ History: {sparkline}\n"
            f"├─ Temperature: {self.temperature:.2f}\n"
            f"├─ Fever: {fever_str}\n"
            f"└─ Last tithe: {self.last_tithe}"
        )

    def update_from_metrics(self, metrics: DashboardMetrics) -> None:
        """Update panel from metrics bundle."""
        self.pressure = metrics.metabolism.pressure
        self.temperature = metrics.metabolism.temperature
        self.in_fever = metrics.metabolism.in_fever
        self.status = metrics.metabolism.status_text
        self.is_online = metrics.metabolism.is_online
        self.fever_count = metrics.metabolism.fever_count
        self.last_tithe = metrics.metabolism.tithe_age_str

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

    DashboardScreen #weather-header {
        dock: top;
        height: 2;
        background: #252525;
        padding: 0 2;
        border-bottom: solid #4a4a5c;
    }

    DashboardScreen #weather-label {
        width: auto;
        color: #f5f0e6;
        padding-right: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "toggle_demo", "Demo Mode"),
        Binding("p", "toggle_replay", "Replay Mode"),
        Binding("space", "play_pause", "Play/Pause", show=False),
        Binding("s", "cycle_speed", "Speed", show=False),
    ]

    demo_mode: reactive[bool] = reactive(False)
    replay_mode: reactive[bool] = reactive(False)

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
        replay_mode: bool = False,
        refresh_interval: float = 1.0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.demo_mode = demo_mode
        self.replay_mode = replay_mode
        self.refresh_interval = refresh_interval
        self._observable = MetricsObservable()
        self._kgent_panel: KgentPanel | None = None
        self._metabolism_panel: MetabolismPanel | None = None
        self._flux_panel: FluxPanel | None = None
        self._triad_panel: TriadPanel | None = None
        self._traces_panel: TracesPanel | None = None
        self._trace_analysis_panel: TraceAnalysisPanel | None = None
        self._status_bar: Static | None = None
        self._weather_widget: WeatherWidget | None = None
        self._weather_engine = WeatherEngine()

        # Replay provider (only created when replay_mode is enabled)
        self._replay_provider: ScenarioReplayProvider | None = None
        self._replay_controls: ReplayControlsWidget | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        # Weather widget in header area
        with Horizontal(id="weather-header"):
            yield Static("[bold]System Weather:[/] ", id="weather-label")
            self._weather_widget = WeatherWidget(demo_mode=self.demo_mode)
            yield self._weather_widget

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

        # Replay controls (shown in replay mode)
        if self.replay_mode:
            self._replay_controls = ReplayControlsWidget(id="replay-controls")
            yield self._replay_controls

        # Status bar
        self._status_bar = Static("Collecting metrics...", id="status-bar")
        yield self._status_bar

        yield Footer()

    async def on_mount(self) -> None:
        """Start metrics collection when screen is mounted."""
        self.title = "kgents dashboard"

        if self.replay_mode:
            # Replay mode: drive dashboard from scenario playback
            self._replay_provider = ScenarioReplayProvider(
                on_metrics_update=self._on_metrics_update,
            )

            # Wire replay controls to provider
            if self._replay_controls:
                self._replay_controls.set_provider(self._replay_provider)

            # Start replay at 2x speed (covers 24 hours in ~12 minutes)
            await self._replay_provider.start_replay(speed=2.0)
        else:
            # Normal mode: periodic metrics collection
            # Subscribe to metrics updates
            self._observable.subscribe(self._on_metrics_update)

            # Start collecting (demo mode uses randomized data)
            await self._observable.start_collecting(
                interval=self.refresh_interval,
                demo_mode=self.demo_mode,
            )

    async def on_unmount(self) -> None:
        """Stop metrics collection when screen is unmounted."""
        if self._replay_provider:
            await self._replay_provider.stop()
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

        # Update weather widget based on system metrics
        if self._weather_widget:
            # Map metabolism metrics to weather
            # pressure (0.0-1.0) → entropy (cloud cover)
            # temperature → token rate (warmth)
            # flux queue depth → pressure (congestion)
            entropy = metrics.metabolism.pressure if metrics.metabolism else 0.3
            token_rate = (
                metrics.metabolism.temperature * 100.0 if metrics.metabolism else 100.0
            )
            queue_depth = metrics.flux.queue_depth if metrics.flux else 5

            self._weather_widget.update_metrics(
                entropy=entropy,
                token_rate=token_rate,
                queue_depth=queue_depth,
            )

            # Update weather engine with pressure trend for forecast
            if self._metabolism_panel and self._metabolism_panel._pressure_history:
                history = self._metabolism_panel._pressure_history
                if len(history) >= 3:
                    # Calculate trend from last 3 readings
                    recent_avg = sum(history[-3:]) / 3
                    older_avg = (
                        sum(history[-6:-3]) / 3 if len(history) >= 6 else recent_avg
                    )
                    self._weather_engine.set_trend(recent_avg - older_avg)

        # Update status bar
        if self._status_bar:
            if self.replay_mode and self._replay_provider:
                state = self._replay_provider.state
                play_str = "▶" if state.state.name == "PLAYING" else "⏸"
                mode_str = f"[REPLAY {play_str} {state.speed}x]"
                ts = f"{state.current_hour:02d}:00"
                progress = f" {state.progress_pct}%"
                self._status_bar.update(
                    f"{mode_str} Simulated: {ts}{progress} | p=toggle s=speed"
                )
            else:
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

    async def action_toggle_replay(self) -> None:
        """Toggle replay mode (animated scenario playback)."""
        self.replay_mode = not self.replay_mode

        if self.replay_mode:
            # Start replay mode
            self._replay_provider = ScenarioReplayProvider(
                on_metrics_update=self._on_metrics_update,
            )
            await self._observable.stop()  # Stop regular collection
            await self._replay_provider.start_replay(speed=2.0)
            self.notify("Replay: ON (space=play/pause, s=speed)")
        else:
            # Stop replay mode
            if self._replay_provider:
                await self._replay_provider.stop()
                self._replay_provider = None
            # Restart regular collection
            await self._observable.start_collecting(
                interval=self.refresh_interval,
                demo_mode=self.demo_mode,
            )
            self.notify("Replay: OFF")

    def action_play_pause(self) -> None:
        """Toggle replay play/pause."""
        if self._replay_provider:
            self._replay_provider.toggle_pause()
            state = (
                "Playing"
                if self._replay_provider.state.state.name == "PLAYING"
                else "Paused"
            )
            self.notify(f"Replay: {state}")

    def action_cycle_speed(self) -> None:
        """Cycle replay speed."""
        if self._replay_provider:
            new_speed = self._replay_provider.cycle_speed()
            self.notify(f"Speed: {new_speed}x")


# =============================================================================
# Dashboard App (Standalone)
# =============================================================================


class DashboardApp(
    App[object],
    DashboardNavigationMixin,
    DashboardScreensMixin,
    DashboardHelpMixin,
):
    """
    Standalone dashboard application with unified navigation.

    Can be run directly or embedded in kgents CLI.
    Integrates all screens (Observatory, Cockpit, Forge, Debugger) with
    NavigationController for seamless zoom in/out.

    Uses mixins for separation of concerns:
    - DashboardNavigationMixin: Keybindings and screen transitions
    - DashboardScreensMixin: Screen factory methods
    - DashboardHelpMixin: Help overlays and documentation
    """

    CSS = """
    Screen {
        background: #1a1a1a;
    }
    """

    TITLE = "kgents dashboard"

    BINDINGS = [
        # Number key navigation (handled by mixin actions)
        ("1", "go_screen_1", "Observatory"),
        ("2", "go_screen_2", "Dashboard"),
        ("3", "go_screen_3", "Cockpit"),
        ("4", "go_screen_4", "Flux"),
        ("5", "go_screen_5", "Loom"),
        ("6", "go_screen_6", "MRI"),
        # Zoom navigation
        ("plus", "zoom_in", "Zoom In"),
        ("equal", "zoom_in", "Zoom In"),
        ("minus", "zoom_out", "Zoom Out"),
        ("underscore", "zoom_out", "Zoom Out"),
        # Tab cycling
        ("tab", "cycle_next", "Next Screen"),
        # Special screens
        ("f", "open_forge", "Forge"),
        ("d", "open_debugger", "Debugger"),
        ("m", "open_memory_map", "Memory Map"),
        # Help
        ("question_mark", "show_help", "Help"),
        # Quit
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        demo_mode: bool = False,
        refresh_interval: float = 1.0,
        replay_mode: bool = False,
    ) -> None:
        super().__init__()
        self.demo_mode = demo_mode
        self.refresh_interval = refresh_interval
        self.replay_mode = replay_mode

        # Initialize services container (EventBus, StateManager, NavigationController)
        from ..services import DashboardServices, EventBus, ScreenNavigationEvent

        self._services = DashboardServices.create(self, demo_mode=demo_mode)
        self._state_manager = self._services.state_manager
        self._nav_controller = self._services.nav_controller
        self._event_bus = self._services.event_bus

        # Track current LOD for screen factories
        self._current_lod = 0

        # Store data for screen creation
        self._flux_state: FluxState | None = None
        self._gardens: list[GardenSnapshot] | None = None

    def on_mount(self) -> None:
        """Push the dashboard screen on mount and register navigation."""
        # Wire EventBus subscriptions for screen navigation
        from ..services import FeverTriggeredEvent, ScreenNavigationEvent

        self._event_bus.subscribe(ScreenNavigationEvent, self._on_screen_navigation)

        # Wire FeverTriggeredEvent for auto-showing fever overlay
        self._event_bus.subscribe(FeverTriggeredEvent, self._on_fever_triggered)

        # Register screen factories with navigation controller
        self._register_screens()

        # Push the initial dashboard screen (LOD 0)
        self.push_screen(
            DashboardScreen(
                demo_mode=self.demo_mode,
                refresh_interval=self.refresh_interval,
                replay_mode=self.replay_mode,
            )
        )

    def _on_screen_navigation(self, event: Any) -> None:
        """Handle screen navigation events from EventBus.

        Uses GentleNavigator to determine appropriate transition style
        based on the source and target screens.
        """
        from typing import Callable

        from .transitions import GentleNavigator

        screen_name = event.target_screen.lower()
        source_screen = getattr(event, "source_screen", None) or ""

        # Map screen names to factory methods
        screen_factories: dict[str, Callable[[], None]] = {
            "observatory": self._create_observatory,
            "dashboard": self._create_dashboard,
            "cockpit": lambda: self._create_cockpit(),
            "flux": self._create_flux,
            "loom": self._create_loom,
            "mri": self._create_mri,
            "forge": self._create_forge,
            "debugger": lambda: self._create_debugger(),
        }

        factory = screen_factories.get(screen_name)
        if factory:
            # Get appropriate transition based on source/target screens
            # Note: transition computed for future animation support
            _navigator = GentleNavigator()
            _ = _navigator.get_transition_for_screens(source_screen, screen_name)

            # Execute the factory to push the screen
            factory()
        else:
            self.notify(f"Unknown screen: {screen_name}")

    def _on_fever_triggered(self, event: Any) -> None:
        """Handle fever events by showing the FeverOverlay.

        The Accursed Share made visible: when entropy exceeds the threshold,
        the FeverOverlay surfaces creative oblique strategies from the void.
        """
        from ..overlays.fever import (
            create_fever_overlay,
            should_show_fever_overlay,
        )

        # Check if entropy exceeds threshold (0.7)
        if should_show_fever_overlay(event.entropy):
            # Create and push the fever overlay
            overlay = create_fever_overlay(
                entropy=event.entropy,
                fever_event=None,  # Could wire to actual FeverEvent if available
            )
            self.push_screen(overlay)

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

    def _create_cockpit(self, agent_id: str | None = None) -> None:
        """Create and push Cockpit screen."""
        from .cockpit import CockpitScreen

        # Get focused agent from state manager if not provided
        if agent_id is None:
            focus = self._state_manager.get_focus(
                "observatory"
            ) or self._state_manager.get_focus("terrarium")
            agent_id = focus or ""

        self.push_screen(
            CockpitScreen(
                agent_id=agent_id,
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
    #
    # Most actions are provided by mixins:
    # - DashboardNavigationMixin: action_go_screen_1 through action_go_screen_6,
    #   action_zoom_in, action_zoom_out, action_open_forge, action_open_debugger,
    #   action_cycle_next, action_cycle_prev
    # - DashboardHelpMixin: action_show_help
    #
    # The actions below are additional or override the mixins.
    # ========================================================================

    def action_open_memory_map(self) -> None:
        """Open Memory Map screen (m)."""
        from .memory_map import MemoryMapScreen

        self.push_screen(
            MemoryMapScreen(
                demo_mode=self.demo_mode,
            )
        )

    def _navigate_to(self, screen_name: str) -> None:
        """Navigate to a screen by name.

        This override ensures that navigation events work properly by
        calling the appropriate factory method directly.

        Args:
            screen_name: The target screen identifier
        """
        from ..services import EventBus, ScreenNavigationEvent

        EventBus.get().emit(ScreenNavigationEvent(target_screen=screen_name))


# =============================================================================
# CLI Entry Point
# =============================================================================


def run_dashboard(
    demo_mode: bool = False,
    replay_mode: bool = False,
    refresh_interval: float = 1.0,
) -> None:
    """
    Run the dashboard TUI.

    Args:
        demo_mode: Use demo data instead of live metrics
        replay_mode: Use animated scenario playback (Day in the Life)
        refresh_interval: Seconds between metric updates

    Modes:
    - LIVE: Collect real metrics from running services
    - DEMO: Random synthetic metrics for showcase
    - REPLAY: Animated 24-hour "Day in the Life" scenario

    Replay controls:
    - p: Toggle replay mode
    - space: Play/Pause
    - s: Cycle speed (0.25x, 0.5x, 1x, 2x, 4x)
    """
    # Pass replay_mode directly to app for proper initialization
    app = DashboardApp(
        demo_mode=demo_mode,
        refresh_interval=refresh_interval,
        replay_mode=replay_mode,
    )
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
