"""
MetricsPanel Widget - Live agent metabolism metrics display.

Shows pressure/flow/temperature for running agents, sourced from
Terrarium WebSocket feed. This is the bridge from Flux metrics
to I-gent visualization.

The Three Dimensions:
    Pressure (0-100): Queue backlog - how backed up is the agent?
    Flow (events/sec): Throughput - how fast is work moving?
    Temperature (0-1): Metabolic heat - how hard is it working?

Usage:
    >>> panel = MetricsPanel(agent_id="flux-abc")
    >>> panel.update_metrics(AgentMetrics(...))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult

# Block characters for gauge rendering
GAUGE_CHARS = " ▏▎▍▌▋▊▉█"


def _gauge_bar(value: float, max_value: float, width: int = 20) -> str:
    """
    Render a horizontal gauge bar.

    Args:
        value: Current value
        max_value: Maximum value (for normalization)
        width: Bar width in characters

    Returns:
        Gauge bar string
    """
    if max_value <= 0:
        return " " * width

    ratio = min(1.0, value / max_value)
    filled = ratio * width

    # Full blocks
    full_blocks = int(filled)

    # Partial block
    remainder = filled - full_blocks
    partial_idx = int(remainder * (len(GAUGE_CHARS) - 1))
    partial = GAUGE_CHARS[partial_idx] if partial_idx > 0 else ""

    # Empty space
    empty = width - full_blocks - (1 if partial else 0)

    return "█" * full_blocks + partial + " " * empty


def _sparkline(values: list[float], width: int = 15) -> str:
    """
    Render a mini sparkline chart.

    Args:
        values: Historical values
        width: Chart width

    Returns:
        Sparkline string
    """
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


@dataclass
class MetricState:
    """Internal state for a single metric."""

    current: float = 0.0
    history: list[float] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.history is None:
            self.history = []

    def update(self, value: float, max_history: int = 30) -> None:
        """Update with new value, maintaining history."""
        self.current = value
        self.history.append(value)
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]


class MetricsPanel(Widget):
    """
    Display live pressure/flow/temperature metrics for an agent.

    This widget connects the Terrarium WebSocket feed to the TUI,
    showing real-time agent metabolism in an at-a-glance format.
    """

    DEFAULT_CSS = """
    MetricsPanel {
        width: 100%;
        height: auto;
        min-height: 8;
        padding: 1;
        border: solid $primary;
    }

    MetricsPanel > .metric-label {
        color: $text-muted;
    }

    MetricsPanel.healthy {
        border: solid $success;
    }

    MetricsPanel.degraded {
        border: solid $warning;
    }

    MetricsPanel.critical {
        border: solid $error;
    }

    MetricsPanel.fever {
        background: $error 20%;
    }
    """

    # Reactive properties
    agent_id: reactive[str] = reactive("")
    agent_name: reactive[str] = reactive("")
    pressure: reactive[float] = reactive(0.0)  # 0-100
    flow: reactive[float] = reactive(0.0)  # events/sec
    temperature: reactive[float] = reactive(0.0)  # 0-1
    state: reactive[str] = reactive("unknown")

    def __init__(
        self,
        agent_id: str = "",
        agent_name: str = "",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.agent_id = agent_id
        self.agent_name = agent_name or agent_id

        # Internal state for history tracking
        self._pressure_state = MetricState()
        self._flow_state = MetricState()
        self._temperature_state = MetricState()

    def update_metrics(
        self,
        pressure: float,
        flow: float,
        temperature: float,
        state: str = "flowing",
    ) -> None:
        """
        Update all metrics at once.

        Called when new AgentMetrics arrive from WebSocket.

        Args:
            pressure: Queue backlog (0-100)
            flow: Throughput (events/sec)
            temperature: Metabolic heat (0-1)
            state: Agent state string
        """
        # Update reactive properties
        self.pressure = pressure
        self.flow = flow
        self.temperature = temperature
        self.state = state

        # Update history
        self._pressure_state.update(pressure)
        self._flow_state.update(flow)
        self._temperature_state.update(temperature)

        # Update CSS classes based on health
        self._update_health_class()

    def _update_health_class(self) -> None:
        """Update CSS class based on metrics."""
        self.remove_class("healthy", "degraded", "critical", "fever")

        # Fever check
        if self.temperature > 0.8:
            self.add_class("fever")

        # Health based on pressure
        if self.pressure > 80:
            self.add_class("critical")
        elif self.pressure >= 50:
            self.add_class("degraded")
        else:
            self.add_class("healthy")

    def watch_pressure(self, value: float) -> None:
        """React to pressure changes."""
        self._update_health_class()
        self.refresh()

    def watch_flow(self, value: float) -> None:
        """React to flow changes."""
        self.refresh()

    def watch_temperature(self, value: float) -> None:
        """React to temperature changes."""
        self._update_health_class()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the metrics panel."""
        width = max(40, self.size.width - 4)  # Account for padding/border

        lines = []

        # Header with agent name and state
        state_icon = {
            "flowing": "●",
            "dormant": "○",
            "stopped": "◌",
        }.get(self.state, "?")

        header = f" {state_icon} {self.agent_name} [{self.state}]"
        lines.append(header)
        lines.append("")

        # Pressure gauge (0-100)
        pressure_bar = _gauge_bar(self.pressure, 100, width - 25)
        pressure_spark = _sparkline(self._pressure_state.history, 10)
        pressure_indicator = "🔴" if self.pressure > 80 else "🟡" if self.pressure >= 50 else "🟢"
        lines.append(
            f" Pressure  {pressure_indicator} {pressure_bar} {self.pressure:5.1f} {pressure_spark}"
        )

        # Flow gauge (auto-scale based on history)
        max_flow = max(self._flow_state.history or [10], default=10)
        max_flow = max(10, max_flow * 1.2)  # Add 20% headroom
        flow_bar = _gauge_bar(self.flow, max_flow, width - 25)
        flow_spark = _sparkline(self._flow_state.history, 10)
        lines.append(f" Flow      ⚡ {flow_bar} {self.flow:5.1f} {flow_spark}")

        # Temperature gauge (0-1)
        temp_bar = _gauge_bar(self.temperature, 1.0, width - 25)
        temp_spark = _sparkline(self._temperature_state.history, 10)
        temp_indicator = "🔥" if self.temperature > 0.8 else "🌡️"
        temp_pct = self.temperature * 100
        lines.append(f" Temp      {temp_indicator} {temp_bar} {temp_pct:5.1f}% {temp_spark}")

        return "\n".join(lines)


class MultiMetricsPanel(Widget):
    """
    Display metrics for multiple agents in a grid layout.

    Shows a compact view of all observed agents with their
    pressure/flow/temperature at a glance.
    """

    DEFAULT_CSS = """
    MultiMetricsPanel {
        width: 100%;
        height: auto;
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
        padding: 1;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._agent_panels: dict[str, MetricsPanel] = {}

    def add_agent(self, agent_id: str, agent_name: str = "") -> MetricsPanel:
        """
        Add or get a metrics panel for an agent.

        Args:
            agent_id: Agent identifier
            agent_name: Display name

        Returns:
            The MetricsPanel for this agent
        """
        if agent_id not in self._agent_panels:
            panel = MetricsPanel(
                agent_id=agent_id,
                agent_name=agent_name or agent_id,
                id=f"metrics-{agent_id}",
            )
            self._agent_panels[agent_id] = panel

            # Only mount if we're in a running app
            if self.is_mounted:
                self.mount(panel)

        return self._agent_panels[agent_id]

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent's metrics panel.

        Args:
            agent_id: Agent to remove

        Returns:
            True if removed, False if not found
        """
        panel = self._agent_panels.pop(agent_id, None)
        if panel:
            if panel.is_mounted:
                panel.remove()
            return True
        return False

    def update_agent_metrics(
        self,
        agent_id: str,
        pressure: float,
        flow: float,
        temperature: float,
        state: str = "flowing",
    ) -> None:
        """
        Update metrics for a specific agent.

        Creates the panel if it doesn't exist.

        Args:
            agent_id: Agent identifier
            pressure: Queue backlog (0-100)
            flow: Throughput (events/sec)
            temperature: Metabolic heat (0-1)
            state: Agent state string
        """
        panel = self.add_agent(agent_id)
        panel.update_metrics(pressure, flow, temperature, state)

    @property
    def agent_ids(self) -> list[str]:
        """List of currently displayed agent IDs."""
        return list(self._agent_panels.keys())
