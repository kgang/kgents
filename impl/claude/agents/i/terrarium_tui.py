"""
Terrarium TUI - The Glass Box Visualization.

See inside the agent ecosystem: live agents, pheromone heatmap, thought stream,
and token economy - all in a beautiful terminal interface.

The Problem:
    Text tables are for static data. Agents are **flow**.

The Solution: Rich TUI using Textual
    `kgents observe` opens the Terrarium View

Principle alignment:
    - Transparent Infrastructure: The cockpit shows everything
    - Joy-Inducing: Beautiful visualization of agent activity
    - The verb-first ontology made visible

Usage:
    kgents observe              # Opens the Terrarium View
    kgents observe --compact    # Minimal mode
    kgents observe --focus L    # Focus on specific agent
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable


class Resolution(Enum):
    """Display resolution modes."""

    COMPACT = auto()
    NORMAL = auto()
    DETAILED = auto()


@dataclass
class AgentState:
    """State of a single agent."""

    name: str
    genus: str
    status: str
    cpu_percent: float = 0.0
    memory_mb: int = 0
    replicas_ready: int = 0
    replicas_desired: int = 0
    last_activity: str = ""


@dataclass
class PheromoneLevel:
    """Aggregate pheromone level by type."""

    ptype: str
    intensity: float
    count: int
    top_source: str = ""


@dataclass
class Thought:
    """A thought from the thought stream."""

    content: str
    source: str
    timestamp: datetime
    confidence: float
    category: str  # observation, inference, dream, warning


@dataclass
class TokenBudget:
    """Token economy state."""

    used: int
    limit: int
    burn_rate: float  # tokens per minute
    top_consumer: str
    history: list[int] = field(default_factory=list)  # Last N burn rates


@dataclass
class TerrariumState:
    """Complete terrarium state for rendering."""

    health: str = "unknown"
    agents: list[AgentState] = field(default_factory=list)
    pheromones: list[PheromoneLevel] = field(default_factory=list)
    thoughts: list[Thought] = field(default_factory=list)
    budget: TokenBudget | None = None
    last_update: datetime = field(default_factory=datetime.now)


# ASCII art for heatmap visualization
INTENSITY_CHARS = [" ", "░", "▒", "▓", "█"]

# Pheromone type colors (ANSI codes)
PHEROMONE_COLORS = {
    "WARNING": "\033[91m",  # Red
    "METAPHOR": "\033[95m",  # Magenta
    "MEMORY": "\033[94m",  # Blue
    "NARRATIVE": "\033[96m",  # Cyan
    "OPPORTUNITY": "\033[92m",  # Green
    "SCARCITY": "\033[93m",  # Yellow
    "CAPABILITY": "\033[97m",  # White
    "DREAM": "\033[35m",  # Purple
    "STATE": "\033[37m",  # Gray
}
RESET = "\033[0m"


def _intensity_char(intensity: float) -> str:
    """Convert intensity (0-1) to ASCII character."""
    idx = int(intensity * (len(INTENSITY_CHARS) - 1))
    idx = max(0, min(idx, len(INTENSITY_CHARS) - 1))
    return INTENSITY_CHARS[idx]


def _progress_bar(value: float, width: int = 10) -> str:
    """Render a progress bar."""
    filled = int(value * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def _sparkline(
    values: list[int] | list[float] | list[int | float], width: int = 20
) -> str:
    """Render a sparkline from values."""
    if not values:
        return "▁" * width

    # Normalize to last `width` values
    values = values[-width:]

    if not values:
        return "▁" * width

    min_v = min(values)
    max_v = max(values)
    range_v = max_v - min_v if max_v > min_v else 1

    chars = "▁▂▃▄▅▆▇█"
    result = []

    for v in values:
        idx = int(((v - min_v) / range_v) * (len(chars) - 1))
        idx = max(0, min(idx, len(chars) - 1))
        result.append(chars[idx])

    # Pad to width
    while len(result) < width:
        result.insert(0, "▁")

    return "".join(result)


class TerrariumRenderer:
    """
    Renders the Terrarium state to terminal.

    Non-Textual fallback for environments without curses/Textual.
    Uses ANSI escape codes for colors and positioning.
    """

    def __init__(self, width: int = 80) -> None:
        self.width = width

    def render(
        self, state: TerrariumState, resolution: Resolution = Resolution.NORMAL
    ) -> str:
        """Render the full terrarium view."""
        lines = []

        # Header
        lines.append(self._header(state))
        lines.append(self._separator())

        # Main panels
        if resolution == Resolution.COMPACT:
            lines.extend(self._compact_view(state))
        else:
            lines.extend(self._full_view(state, resolution == Resolution.DETAILED))

        # Footer
        lines.append(self._separator())
        lines.append(self._footer())

        return "\n".join(lines)

    def _header(self, state: TerrariumState) -> str:
        """Render header bar."""
        health_color = {
            "healthy": "\033[92m",
            "degraded": "\033[93m",
            "unhealthy": "\033[91m",
        }.get(state.health, "\033[37m")

        timestamp = state.last_update.strftime("%H:%M:%S")
        health_indicator = f"{health_color}●{RESET}"

        title = f" TERRARIUM {health_indicator}"
        time_str = f"{timestamp} UTC "

        padding = self.width - len(" TERRARIUM ● ") - len(time_str)
        return f"┌{'─' * (self.width - 2)}┐"

    def _separator(self) -> str:
        """Render separator line."""
        return f"├{'─' * (self.width - 2)}┤"

    def _footer(self) -> str:
        """Render footer with controls."""
        controls = " [q]uit  [r]efresh  [d]etail  [t]ether  [p]heromones "
        padding = self.width - len(controls) - 2
        return f"└{controls}{'─' * padding}┘"

    def _compact_view(self, state: TerrariumState) -> list[str]:
        """Render compact single-line-per-agent view."""
        lines = []

        # Quick status line
        agent_count = len(state.agents)
        ph_count = sum(p.count for p in state.pheromones)
        thought_count = len(state.thoughts)

        lines.append(
            f"│ Agents: {agent_count} │ Pheromones: {ph_count} │ "
            f"Thoughts: {thought_count} │"
        )
        lines.append(self._separator())

        # Agent list
        for agent in state.agents:
            bar = _progress_bar(agent.cpu_percent / 100, 5)
            status_icon = "●" if agent.status == "running" else "○"
            lines.append(f"│ {status_icon} {agent.genus:<3} {bar} {agent.status:<10} │")

        return lines

    def _full_view(self, state: TerrariumState, detailed: bool) -> list[str]:
        """Render full multi-panel view."""
        lines = []

        # Title line
        timestamp = state.last_update.strftime("%H:%M:%S")
        health_indicator = "●" if state.health == "healthy" else "○"
        title_line = (
            f"│ TERRARIUM {health_indicator}".ljust(self.width - 15)
            + f"{timestamp} UTC │"
        )
        lines.append(title_line)
        lines.append(self._separator())

        # Agents panel
        lines.append("│")
        lines.append("│  ┌─ AGENTS ──────────────────────────────┐")

        for agent in state.agents[:7]:  # Limit to 7 agents
            pct = int(agent.cpu_percent)
            bar = _progress_bar(pct / 100, 10)
            status = agent.status.capitalize()[:12]
            lines.append(f"│  │ {agent.genus:<6} {bar} {pct:3d}%  {status:<12} │")

        lines.append("│  └─────────────────────────────────────────┘")
        lines.append("│")

        # Pheromone heatmap (simplified)
        lines.append("│  ┌─ PHEROMONE LEVELS ───────────────────┐")

        for ph in state.pheromones[:5]:
            color = PHEROMONE_COLORS.get(ph.ptype, "")
            bar = _progress_bar(ph.intensity, 15)
            lines.append(
                f"│  │ {color}{ph.ptype:<12}{RESET} {bar} {ph.intensity:.1f} │"
            )

        lines.append("│  └─────────────────────────────────────────┘")
        lines.append("│")

        # Thought stream
        lines.append("│  ┌─ THOUGHT STREAM ───────────────────────────────────┐")

        for thought in state.thoughts[-5:]:  # Last 5 thoughts
            time_str = thought.timestamp.strftime("%H:%M:%S")
            source = thought.source[:8]
            content = thought.content[:40]
            prefix = "⚠" if thought.category == "warning" else " "
            lines.append(f"│  │ {time_str} [{source:<8}] {prefix}{content:<40} │")

        lines.append("│  └─────────────────────────────────────────────────────┘")
        lines.append("│")

        # Token economy
        if state.budget:
            lines.append("│  ┌─ TOKEN ECONOMY ───────────────────────────────────┐")

            usage_pct = (
                state.budget.used / state.budget.limit if state.budget.limit > 0 else 0
            )
            bar = _progress_bar(usage_pct, 30)
            sparkline = _sparkline(state.budget.history, 30)

            lines.append(
                f"│  │ Budget: {state.budget.used:,} / {state.budget.limit:,} tokens{' ' * 20}│"
            )
            lines.append(f"│  │ {bar} ({usage_pct * 100:.0f}%){' ' * 25}│")
            lines.append(
                f"│  │ Burn Rate: {sparkline} ({state.budget.burn_rate:.0f} tok/min){' ' * 5}│"
            )
            lines.append(f"│  │ Top Consumer: {state.budget.top_consumer:<38}│")
            lines.append("│  └─────────────────────────────────────────────────────┘")

        return lines


class TerrariumDataSource:
    """
    Data source for Terrarium state.

    Fetches state from K-Terrarium cluster via kubectl.
    In production, this would use gRPC to Cortex daemon.
    """

    def __init__(self, namespace: str = "kgents-agents") -> None:
        self.namespace = namespace
        self._thought_buffer: list[Thought] = []
        self._burn_history: list[int] = []

    async def fetch_state(self) -> TerrariumState:
        """Fetch current terrarium state."""
        state = TerrariumState()

        # Fetch in parallel
        agents_task = asyncio.create_task(self._fetch_agents())
        pheromones_task = asyncio.create_task(self._fetch_pheromones())

        state.agents = await agents_task
        state.pheromones = await pheromones_task
        state.thoughts = self._thought_buffer[-20:]
        state.budget = await self._fetch_budget()
        state.last_update = datetime.now()

        # Determine health
        if not state.agents:
            state.health = "unhealthy"
        elif all(a.status == "running" for a in state.agents):
            state.health = "healthy"
        else:
            state.health = "degraded"

        return state

    async def _fetch_agents(self) -> list[AgentState]:
        """Fetch agent states from K8s."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "get",
                "deployments",
                "-n",
                self.namespace,
                "-l",
                "app.kubernetes.io/part-of=kgents",
                "-o",
                "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await proc.communicate()

            if proc.returncode != 0:
                return []

            data = json.loads(stdout.decode())
            agents = []

            for item in data.get("items", []):
                metadata = item.get("metadata", {})
                labels = metadata.get("labels", {})
                status = item.get("status", {})

                name = metadata.get("name", "unknown")
                genus = labels.get("kgents.io/genus", name[0].upper())

                ready = status.get("readyReplicas", 0)
                desired = status.get("replicas", 1)

                agent_status = "running" if ready >= desired else "starting"

                agents.append(
                    AgentState(
                        name=name,
                        genus=genus,
                        status=agent_status,
                        cpu_percent=50.0,  # TODO: fetch from metrics-server
                        memory_mb=128,
                        replicas_ready=ready,
                        replicas_desired=desired,
                    )
                )

            return agents

        except Exception:
            return []

    async def _fetch_pheromones(self) -> list[PheromoneLevel]:
        """Fetch pheromone levels from K8s CRDs."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "get",
                "pheromones.kgents.io",
                "-n",
                self.namespace,
                "-o",
                "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await proc.communicate()

            if proc.returncode != 0:
                return []

            data = json.loads(stdout.decode())

            # Aggregate by type
            by_type: dict[str, list[float]] = {}
            sources: dict[str, str] = {}

            for item in data.get("items", []):
                spec = item.get("spec", {})
                ptype = spec.get("type", "UNKNOWN")
                intensity = spec.get("intensity", 0.0)
                source = spec.get("source", "unknown")

                if ptype not in by_type:
                    by_type[ptype] = []
                    sources[ptype] = source
                by_type[ptype].append(intensity)

            levels = []
            for ptype, intensities in by_type.items():
                avg_intensity = (
                    sum(intensities) / len(intensities) if intensities else 0
                )
                levels.append(
                    PheromoneLevel(
                        ptype=ptype,
                        intensity=avg_intensity,
                        count=len(intensities),
                        top_source=sources.get(ptype, ""),
                    )
                )

            # Sort by intensity descending
            levels.sort(key=lambda x: x.intensity, reverse=True)
            return levels

        except Exception:
            return []

    async def _fetch_budget(self) -> TokenBudget:
        """Fetch token budget (mock for now)."""
        # TODO: This should query the B-gent token ledger
        used = 847234 + int(time.time()) % 1000
        limit = 1000000
        burn_rate = 12.0 + (int(time.time()) % 5)

        self._burn_history.append(int(burn_rate))
        self._burn_history = self._burn_history[-30:]  # Keep last 30

        return TokenBudget(
            used=used,
            limit=limit,
            burn_rate=burn_rate,
            top_consumer="L-gent (embedding generation)",
            history=self._burn_history,
        )

    def add_thought(self, thought: Thought) -> None:
        """Add a thought to the buffer."""
        self._thought_buffer.append(thought)
        self._thought_buffer = self._thought_buffer[-50:]  # Keep last 50


class TerrariumApp:
    """
    The Terrarium TUI application.

    Non-Textual implementation using simple terminal rendering.
    For full Textual implementation, see TerrariumTextualApp below.
    """

    def __init__(
        self,
        data_source: TerrariumDataSource | None = None,
        refresh_interval: float = 2.0,
        resolution: Resolution = Resolution.NORMAL,
    ) -> None:
        self.data_source = data_source or TerrariumDataSource()
        self.renderer = TerrariumRenderer()
        self.refresh_interval = refresh_interval
        self.resolution = resolution
        self._running = False

    async def run(self) -> None:
        """Run the TUI main loop."""
        self._running = True

        # Clear screen and hide cursor
        print("\033[2J\033[H\033[?25l", end="", flush=True)

        try:
            while self._running:
                # Fetch state
                state = await self.data_source.fetch_state()

                # Render
                output = self.renderer.render(state, self.resolution)

                # Clear and draw
                print("\033[H", end="")  # Move cursor home
                print(output, flush=True)

                # Wait for next refresh
                await asyncio.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            pass
        finally:
            # Show cursor and clear
            print("\033[?25h", end="", flush=True)
            self._running = False

    def stop(self) -> None:
        """Stop the TUI."""
        self._running = False


# Textual-based implementation (if textual is available)
try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
    from textual.containers import Horizontal, Vertical, Container
    from textual.reactive import reactive

    class AgentPanel(Static):  # type: ignore[misc]
        """Panel showing agent states."""

        def compose(self) -> ComposeResult:
            yield Static("Loading agents...")

        def update_agents(self, agents: list[AgentState]) -> None:
            """Update the agent display."""
            lines = []
            for agent in agents:
                bar = _progress_bar(agent.cpu_percent / 100, 10)
                status_icon = "●" if agent.status == "running" else "○"
                lines.append(
                    f"{status_icon} {agent.genus:<6} {bar} {agent.cpu_percent:3.0f}%  {agent.status}"
                )
            self.update("\n".join(lines) or "No agents running")

    class PheromoneHeatmap(Static):  # type: ignore[misc]
        """Pheromone heatmap visualization."""

        def compose(self) -> ComposeResult:
            yield Static("Loading pheromones...")

        def update_pheromones(self, pheromones: list[PheromoneLevel]) -> None:
            """Update the pheromone display."""
            lines = []
            for ph in pheromones[:8]:
                bar = _progress_bar(ph.intensity, 15)
                lines.append(f"{ph.ptype:<12} {bar} {ph.intensity:.2f}")
            self.update("\n".join(lines) or "No pheromones")

    class ThoughtStream(Static):  # type: ignore[misc]
        """Thought stream panel."""

        def compose(self) -> ComposeResult:
            yield Static("Waiting for thoughts...")

        def update_thoughts(self, thoughts: list[Thought]) -> None:
            """Update the thought stream."""
            lines = []
            for t in thoughts[-10:]:
                time_str = t.timestamp.strftime("%H:%M:%S")
                prefix = "⚠ " if t.category == "warning" else ""
                lines.append(f"{time_str} [{t.source:<8}] {prefix}{t.content[:50]}")
            self.update("\n".join(lines) or "Quiet mind...")

    class TokenEconomy(Static):  # type: ignore[misc]
        """Token economy panel."""

        def compose(self) -> ComposeResult:
            yield Static("Loading budget...")

        def update_budget(self, budget: TokenBudget | None) -> None:
            """Update the token budget display."""
            if not budget:
                self.update("No budget data")
                return

            pct = budget.used / budget.limit * 100 if budget.limit > 0 else 0
            sparkline = _sparkline(budget.history, 30)

            lines = [
                f"Budget: {budget.used:,} / {budget.limit:,} tokens ({pct:.0f}%)",
                f"Burn Rate: {sparkline} ({budget.burn_rate:.0f} tok/min)",
                f"Top Consumer: {budget.top_consumer}",
            ]
            self.update("\n".join(lines))

    class TerrariumTextualApp(App):  # type: ignore[misc]
        """The Glass Box - Textual-based TUI for K-Terrarium."""

        CSS = """
        Screen {
            layout: grid;
            grid-size: 2 3;
            grid-columns: 1fr 1fr;
            grid-rows: auto 1fr auto;
        }

        #agents {
            row-span: 1;
            border: solid green;
            padding: 1;
        }

        #heatmap {
            row-span: 1;
            border: solid blue;
            padding: 1;
        }

        #thoughts {
            column-span: 2;
            border: solid cyan;
            padding: 1;
        }

        #economy {
            column-span: 2;
            border: solid yellow;
            padding: 1;
        }
        """

        BINDINGS = [
            ("q", "quit", "Quit"),
            ("r", "refresh", "Refresh"),
            ("d", "detail", "Toggle Detail"),
            ("t", "tether", "Tether"),
        ]

        def __init__(self, data_source: TerrariumDataSource | None = None) -> None:
            super().__init__()
            self.data_source = data_source or TerrariumDataSource()

        def compose(self) -> ComposeResult:
            yield Header()
            yield AgentPanel(id="agents")
            yield PheromoneHeatmap(id="heatmap")
            yield ThoughtStream(id="thoughts")
            yield TokenEconomy(id="economy")
            yield Footer()

        async def on_mount(self) -> None:
            """Start refresh timer on mount."""
            self.set_interval(2.0, self.refresh_state)
            await self.refresh_state()

        async def refresh_state(self) -> None:
            """Refresh all panels with current state."""
            state = await self.data_source.fetch_state()

            self.query_one("#agents", AgentPanel).update_agents(state.agents)
            self.query_one("#heatmap", PheromoneHeatmap).update_pheromones(
                state.pheromones
            )
            self.query_one("#thoughts", ThoughtStream).update_thoughts(state.thoughts)
            self.query_one("#economy", TokenEconomy).update_budget(state.budget)

        def action_refresh(self) -> None:
            """Manual refresh action."""
            asyncio.create_task(self.refresh_state())

        def action_detail(self) -> None:
            """Toggle detail mode."""
            pass  # TODO: Implement detail toggle

        def action_tether(self) -> None:
            """Open tether dialog."""
            pass  # TODO: Implement tether dialog

    TEXTUAL_AVAILABLE = True

except ImportError:
    TEXTUAL_AVAILABLE = False
    TerrariumTextualApp = None  # type: ignore


def create_terrarium_app(
    use_textual: bool = True,
    refresh_interval: float = 2.0,
) -> TerrariumApp | Any:
    """
    Factory function to create the appropriate TUI.

    Args:
        use_textual: Prefer Textual if available
        refresh_interval: Refresh interval in seconds

    Returns:
        TerrariumApp (simple) or TerrariumTextualApp (rich)
    """
    data_source = TerrariumDataSource()

    if use_textual and TEXTUAL_AVAILABLE:
        return TerrariumTextualApp(data_source=data_source)

    return TerrariumApp(
        data_source=data_source,
        refresh_interval=refresh_interval,
    )


async def run_terrarium(
    use_textual: bool = True,
    compact: bool = False,
    focus: str | None = None,
) -> None:
    """
    Run the Terrarium TUI.

    Args:
        use_textual: Use Textual if available
        compact: Compact display mode
        focus: Focus on specific agent
    """
    app = create_terrarium_app(use_textual=use_textual)

    if hasattr(app, "run_async"):
        # Textual app
        await app.run_async()
    else:
        # Simple app
        if compact:
            app.resolution = Resolution.COMPACT
        await app.run()
