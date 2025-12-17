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
from datetime import datetime, timedelta
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
class SemaphoreState:
    """
    Semaphore state for TUI display.

    Phase 5: Purgatory integration - show pending semaphores awaiting resolution.
    """

    token_id: str
    prompt: str
    severity: str  # info, warning, critical
    reason: str  # SemaphoreReason value
    options: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: datetime | None = None

    @property
    def time_remaining(self) -> timedelta | None:
        """Calculate time remaining until deadline."""
        if self.deadline is None:
            return None
        remaining = self.deadline - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    @property
    def is_urgent(self) -> bool:
        """Check if this semaphore needs immediate attention."""
        if self.severity == "critical":
            return True
        if self.time_remaining is not None:
            return self.time_remaining.total_seconds() < 300  # < 5 minutes
        return False


@dataclass
class TerrariumState:
    """Complete terrarium state for rendering."""

    health: str = "unknown"
    agents: list[AgentState] = field(default_factory=list)
    pheromones: list[PheromoneLevel] = field(default_factory=list)
    thoughts: list[Thought] = field(default_factory=list)
    budget: TokenBudget | None = None
    semaphores: list[SemaphoreState] = field(default_factory=list)  # Phase 5
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

        title = f" TERRARIUM {health_indicator} "
        time_str = f" {timestamp} UTC "
        content_width = self.width - 2  # Exclude box corners

        # Build header with title left, time right
        padding = content_width - len(title) - len(time_str)
        _header_content = f"{title}{'─' * padding}{time_str}"

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
        semaphores_task = asyncio.create_task(self._fetch_semaphores())

        state.agents = await agents_task
        state.pheromones = await pheromones_task
        state.semaphores = await semaphores_task
        state.thoughts = self._thought_buffer[-20:]
        state.budget = await self._fetch_budget()
        state.last_update = datetime.now()

        # Determine health (include semaphore urgency)
        if not state.agents:
            state.health = "unhealthy"
        elif any(s.is_urgent for s in state.semaphores):
            state.health = "degraded"  # Urgent semaphores need attention
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

    async def _fetch_semaphores(self) -> list[SemaphoreState]:
        """
        Fetch pending semaphores from purgatory.

        Phase 5: Multiple data sources possible:
        - Option A: REST call to terrarium gateway /api/purgatory/list
        - Option B: gRPC call to cortex daemon
        - Option C: kubectl get semaphores CRD (future)

        Currently implements Option A (REST).
        """
        try:
            # Try REST endpoint first (terrarium gateway)
            import httpx

            async with httpx.AsyncClient(timeout=2.0) as client:
                # Try localhost first (development)
                for host in ["localhost:8080", "terrarium.kgents-agents.svc:8080"]:
                    try:
                        response = await client.get(f"http://{host}/api/purgatory/list")
                        if response.status_code == 200:
                            data = response.json()
                            return self._parse_semaphores(data)
                    except Exception:
                        continue

            return []

        except ImportError:
            # httpx not available, try kubectl
            return await self._fetch_semaphores_kubectl()
        except Exception:
            return []

    async def _fetch_semaphores_kubectl(self) -> list[SemaphoreState]:
        """Fetch semaphores via kubectl (future CRD)."""
        # Future: When semaphores become K8s CRDs
        # kubectl get semaphores.kgents.io -n kgents-agents -o json
        return []

    def _parse_semaphores(self, data: dict[str, Any]) -> list[SemaphoreState]:
        """Parse semaphore data from REST response."""
        semaphores = []

        for item in data.get("pending", []):
            deadline = None
            if item.get("deadline"):
                try:
                    deadline = datetime.fromisoformat(item["deadline"])
                except (ValueError, TypeError):
                    pass

            created_at = datetime.now()
            if item.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(item["created_at"])
                except (ValueError, TypeError):
                    pass

            semaphores.append(
                SemaphoreState(
                    token_id=item.get("id", "unknown"),
                    prompt=item.get("prompt", "No prompt"),
                    severity=item.get("severity", "info"),
                    reason=item.get("reason", "unknown"),
                    options=item.get("options", []),
                    created_at=created_at,
                    deadline=deadline,
                )
            )

        # Sort by urgency (critical first, then by deadline)
        semaphores.sort(
            key=lambda s: (
                0 if s.severity == "critical" else 1,
                s.deadline or datetime.max,
            )
        )

        return semaphores

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
    from textual.containers import Container, Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import DataTable, Footer, Header, ProgressBar, Static

    # Import metrics components
    from .data.terrarium_source import AgentMetrics, TerrariumWebSocketSource
    from .widgets.density_field import DensityField
    from .widgets.metrics_panel import MetricsPanel

    class LiveMetricsPanel(Static):
        """
        Panel showing live pressure/flow/temperature metrics.

        Terrarium Phase 3: This panel displays real-time agent metabolism
        sourced from the Terrarium WebSocket feed.
        """

        def __init__(
            self,
            websocket_url: str = "ws://localhost:8080",
            name: str | None = None,
            id: str | None = None,  # noqa: A002
            classes: str | None = None,
        ) -> None:
            super().__init__(name=name, id=id, classes=classes)
            self.websocket_url = websocket_url
            self._metrics_panels: dict[str, MetricsPanel] = {}
            self._ws_source: TerrariumWebSocketSource | None = None
            self._ws_task: asyncio.Task[None] | None = None

        def compose(self) -> ComposeResult:
            yield Static("Connecting to Terrarium...", id="metrics-status")

        async def start_metrics_stream(self, agent_ids: list[str]) -> None:
            """
            Start streaming metrics for the given agents.

            Args:
                agent_ids: List of agent IDs to observe
            """
            if self._ws_task and not self._ws_task.done():
                self._ws_task.cancel()

            self._ws_source = TerrariumWebSocketSource(
                base_url=self.websocket_url,
                on_connected=self._on_connected,
                on_disconnected=self._on_disconnected,
                on_error=self._on_error,
            )

            # Start observing agents
            self._ws_task = asyncio.create_task(self._observe_agents(agent_ids))

        async def _observe_agents(self, agent_ids: list[str]) -> None:
            """Observe multiple agents and update panels."""
            if not self._ws_source:
                return

            from .data.terrarium_source import observe_multiple

            try:
                async for metrics in observe_multiple(self._ws_source, agent_ids):
                    self._update_panel(metrics)
            except asyncio.CancelledError:
                pass

        def _update_panel(self, metrics: AgentMetrics) -> None:
            """Update the display with new metrics."""
            # Build display lines
            lines = []

            # Header
            state_icon = {"flowing": "●", "dormant": "○", "stopped": "◌"}.get(
                metrics.state, "?"
            )
            health_icon = {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}.get(
                metrics.health, "⚪"
            )
            lines.append(f" {state_icon} {metrics.agent_id} {health_icon}")
            lines.append("")

            # Pressure bar
            pressure_bar = _progress_bar(metrics.pressure / 100, 20)
            lines.append(f" Pressure  {pressure_bar} {metrics.pressure:5.1f}")

            # Flow (auto-scale)
            flow_bar = _progress_bar(min(1.0, metrics.flow / 50), 20)
            lines.append(f" Flow      {flow_bar} {metrics.flow:5.1f}/s")

            # Temperature bar
            temp_bar = _progress_bar(metrics.temperature, 20)
            temp_pct = metrics.temperature * 100
            temp_icon = "🔥" if metrics.temperature > 0.8 else "🌡️"
            lines.append(f" Temp {temp_icon}   {temp_bar} {temp_pct:5.1f}%")

            # Update the static content
            self.query_one("#metrics-status", Static).update("\n".join(lines))

        def _on_connected(self, agent_id: str) -> None:
            """Handle WebSocket connection."""
            self.query_one("#metrics-status", Static).update(f"Connected to {agent_id}")

        def _on_disconnected(self, agent_id: str) -> None:
            """Handle WebSocket disconnection."""
            self.query_one("#metrics-status", Static).update(
                f"Disconnected from {agent_id}"
            )

        def _on_error(self, agent_id: str, error: Exception) -> None:
            """Handle WebSocket error."""
            self.query_one("#metrics-status", Static).update(
                f"Error for {agent_id}: {error}"
            )

        async def stop(self) -> None:
            """Stop the metrics stream."""
            if self._ws_task:
                self._ws_task.cancel()
            if self._ws_source:
                await self._ws_source.disconnect_all()

    class AgentDensityPanel(Static):
        """
        Panel showing agents as DensityField clusters.

        Terrarium Phase 3: Agents are rendered as density fields where
        temperature maps to activity level.
        """

        def __init__(
            self,
            name: str | None = None,
            id: str | None = None,  # noqa: A002
            classes: str | None = None,
        ) -> None:
            super().__init__(name=name, id=id, classes=classes)
            self._density_fields: dict[str, DensityField] = {}

        def compose(self) -> ComposeResult:
            yield Static("No agents", id="density-placeholder")

        def update_agent_metrics(self, metrics: AgentMetrics) -> None:
            """
            Update density field for an agent based on metrics.

            Args:
                metrics: AgentMetrics from WebSocket
            """
            agent_id = metrics.agent_id

            if agent_id not in self._density_fields:
                # Create new density field
                field = DensityField(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    activity=metrics.temperature,
                    id=f"density-{agent_id}",
                )
                self._density_fields[agent_id] = field

                # Remove placeholder and mount
                placeholder = self.query_one("#density-placeholder", Static)
                placeholder.remove()
                self.mount(field)
            else:
                # Update existing
                field = self._density_fields[agent_id]
                field.activity = metrics.temperature
                field.agent_name = metrics.state

    class AgentPanel(Static):
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

    class PheromoneHeatmap(Static):
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

    class ThoughtStream(Static):
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

    class TokenEconomy(Static):
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

    class PurgatoryPanel(Static):
        """
        Panel showing pending semaphores awaiting resolution.

        Phase 5: The Rodizio Pattern made visible - tokens in Purgatory
        are displayed here for human attention.
        """

        def compose(self) -> ComposeResult:
            yield Static("No pending semaphores")

        def update_semaphores(self, semaphores: list[SemaphoreState]) -> None:
            """Update the semaphore display."""
            if not semaphores:
                self.update("No pending semaphores")
                return

            lines = []
            for sem in semaphores[:5]:  # Show top 5
                # Severity icon
                icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(
                    sem.severity, "⚪"
                )

                # Time info
                time_str = sem.created_at.strftime("%H:%M:%S")
                deadline_str = ""
                if sem.time_remaining is not None:
                    mins = int(sem.time_remaining.total_seconds() // 60)
                    if mins < 5:
                        deadline_str = f" ⏰ {mins}m"
                    else:
                        deadline_str = f" ⏱ {mins}m"

                # Urgency indicator
                urgent = "❗" if sem.is_urgent else ""

                # Build display
                lines.append(f"{icon} [{time_str}]{deadline_str} {urgent}")
                lines.append(f"   {sem.prompt[:50]}")
                lines.append(f"   Options: {', '.join(sem.options[:3])}")
                lines.append("")

            self.update("\n".join(lines).strip())

    class TerrariumTextualApp(App[None]):
        """The Glass Box - Textual-based TUI for K-Terrarium."""

        CSS = """
        Screen {
            layout: grid;
            grid-size: 2 5;
            grid-columns: 1fr 1fr;
            grid-rows: auto auto auto 1fr auto;
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

        #metrics {
            column-span: 2;
            border: solid magenta;
            padding: 1;
            height: auto;
            min-height: 8;
        }

        #purgatory {
            column-span: 2;
            border: solid red;
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
            ("s", "semaphores", "Semaphores"),
            ("m", "metrics", "Focus Metrics"),
        ]

        def __init__(
            self,
            data_source: TerrariumDataSource | None = None,
            websocket_url: str = "ws://localhost:8080",
        ) -> None:
            super().__init__()
            self.data_source = data_source or TerrariumDataSource()
            self.websocket_url = websocket_url
            self._metrics_panel: LiveMetricsPanel | None = None

        def compose(self) -> ComposeResult:
            yield Header()
            yield AgentPanel(id="agents")
            yield PheromoneHeatmap(id="heatmap")
            yield LiveMetricsPanel(websocket_url=self.websocket_url, id="metrics")
            yield PurgatoryPanel(id="purgatory")
            yield ThoughtStream(id="thoughts")
            yield TokenEconomy(id="economy")
            yield Footer()

        async def on_mount(self) -> None:
            """Start refresh timer on mount."""
            self.set_interval(2.0, self.refresh_state)
            await self.refresh_state()

            # Start metrics stream after first refresh (to get agent IDs)
            self._metrics_panel = self.query_one("#metrics", LiveMetricsPanel)

        async def refresh_state(self) -> None:
            """Refresh all panels with current state."""
            state = await self.data_source.fetch_state()

            self.query_one("#agents", AgentPanel).update_agents(state.agents)
            self.query_one("#heatmap", PheromoneHeatmap).update_pheromones(
                state.pheromones
            )
            self.query_one("#purgatory", PurgatoryPanel).update_semaphores(
                state.semaphores
            )
            self.query_one("#thoughts", ThoughtStream).update_thoughts(state.thoughts)
            self.query_one("#economy", TokenEconomy).update_budget(state.budget)

            # Start metrics stream for discovered agents
            if self._metrics_panel and state.agents:
                agent_ids = [a.name for a in state.agents]
                await self._metrics_panel.start_metrics_stream(agent_ids)

        def action_refresh(self) -> None:
            """Manual refresh action."""
            asyncio.create_task(self.refresh_state())

        def action_detail(self) -> None:
            """Toggle detail mode."""
            pass  # TODO: Implement detail toggle

        def action_tether(self) -> None:
            """Open tether dialog."""
            pass  # TODO: Implement tether dialog

        def action_semaphores(self) -> None:
            """Focus on semaphores panel."""
            self.query_one("#purgatory").focus()

        def action_metrics(self) -> None:
            """Focus on metrics panel."""
            self.query_one("#metrics").focus()

        async def on_unmount(self) -> None:
            """Clean up on unmount."""
            if self._metrics_panel:
                await self._metrics_panel.stop()

    TEXTUAL_AVAILABLE = True

except ImportError:
    TEXTUAL_AVAILABLE = False
    TerrariumTextualApp = None  # type: ignore


def create_terrarium_app(
    use_textual: bool = True,
    refresh_interval: float = 2.0,
    websocket_url: str = "ws://localhost:8080",
) -> TerrariumApp | Any:
    """
    Factory function to create the appropriate TUI.

    Args:
        use_textual: Prefer Textual if available
        refresh_interval: Refresh interval in seconds
        websocket_url: WebSocket URL for live metrics

    Returns:
        TerrariumApp (simple) or TerrariumTextualApp (rich)
    """
    data_source = TerrariumDataSource()

    if use_textual and TEXTUAL_AVAILABLE:
        return TerrariumTextualApp(
            data_source=data_source,
            websocket_url=websocket_url,
        )

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
