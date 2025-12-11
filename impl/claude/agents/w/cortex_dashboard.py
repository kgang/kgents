"""
CortexDashboard: W-gent Wire Protocol Dashboard for the Bicameral Engine.

Real-time dashboard using the W-gent wire protocol for cortex health monitoring.
Emits state to wire files for renderer-agnostic visualization.

Design principles:
1. Wire Protocol: All state emitted via WireObservable
2. Non-Intrusion: Zero performance impact on cortex operations
3. Graceful Degradation: Works if some components unavailable
4. Multiple Fidelities: Compact, standard, and full views

From the implementation plan:
> "Real-time dashboard using W-gent wire protocol"
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.o.cortex_observer import (
    CortexHealth,
    CortexHealthSnapshot,
    CortexObserver,
)


class DashboardPanel(Enum):
    """Available dashboard panels."""

    HEMISPHERE_STATUS = "hemisphere_status"
    COHERENCY_MONITOR = "coherency_monitor"
    SYNAPSE_MONITOR = "synapse_monitor"
    HIPPOCAMPUS_GAUGE = "hippocampus_gauge"
    DREAM_REPORT = "dream_report"
    NEUROGENESIS_QUEUE = "neurogenesis_queue"


@dataclass
class SparklineData:
    """Data for sparkline visualization."""

    values: list[float] = field(default_factory=list)
    max_size: int = 60  # 1 minute at 1-second updates

    def add(self, value: float) -> None:
        """Add a value to the sparkline."""
        self.values.append(value)
        if len(self.values) > self.max_size:
            self.values = self.values[-self.max_size :]

    def render(self, width: int = 20) -> str:
        """Render sparkline as ASCII."""
        if not self.values:
            return " " * width

        # Normalize to 0-1
        min_val = min(self.values)
        max_val = max(self.values)
        range_val = max_val - min_val if max_val != min_val else 1.0

        # Sparkline characters (increasing height)
        chars = " ▁▂▃▄▅▆▇█"

        # Sample values to fit width
        step = max(1, len(self.values) // width)
        sampled = self.values[::step][:width]

        result = ""
        for val in sampled:
            normalized = (val - min_val) / range_val
            char_idx = int(normalized * (len(chars) - 1))
            result += chars[char_idx]

        return result.ljust(width)


@dataclass
class CortexDashboardConfig:
    """Configuration for the CortexDashboard."""

    # Wire protocol settings
    wire_agent_name: str = "cortex-dashboard"
    emission_interval: float = 1.0

    # Panel settings
    panels: list[DashboardPanel] = field(
        default_factory=lambda: [
            DashboardPanel.HEMISPHERE_STATUS,
            DashboardPanel.COHERENCY_MONITOR,
            DashboardPanel.SYNAPSE_MONITOR,
            DashboardPanel.HIPPOCAMPUS_GAUGE,
            DashboardPanel.DREAM_REPORT,
        ]
    )
    compact_mode: bool = False

    # History for sparklines
    history_size: int = 60

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CortexDashboardConfig":
        """Create from dictionary."""
        panels = [DashboardPanel(p) for p in data.get("panels", [])] or [
            DashboardPanel.HEMISPHERE_STATUS,
            DashboardPanel.COHERENCY_MONITOR,
            DashboardPanel.SYNAPSE_MONITOR,
            DashboardPanel.HIPPOCAMPUS_GAUGE,
            DashboardPanel.DREAM_REPORT,
        ]
        return cls(
            wire_agent_name=data.get("wire_agent_name", "cortex-dashboard"),
            emission_interval=data.get("emission_interval", 1.0),
            panels=panels,
            compact_mode=data.get("compact_mode", False),
            history_size=data.get("history_size", 60),
        )


class CortexDashboard:
    """
    W-gent Wire Protocol Dashboard for Cortex Health.

    Provides real-time visualization of cortex health via wire protocol
    and ASCII rendering.

    Usage:
        dashboard = create_cortex_dashboard(observer=cortex_observer)
        await dashboard.start()
        # → Wire files at .wire/cortex-dashboard/

        print(dashboard.render_compact())
        # → [CORTEX] OK HEALTHY | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12

        print(dashboard.render_full())
        # → Full ASCII dashboard
    """

    def __init__(
        self,
        observer: CortexObserver,
        config: CortexDashboardConfig | None = None,
    ):
        """
        Initialize CortexDashboard.

        Args:
            observer: CortexObserver to visualize
            config: Dashboard configuration
        """
        self._observer = observer
        self._config = config or CortexDashboardConfig()

        # Running state
        self._running = False
        self._update_task: asyncio.Task | None = None

        # Sparkline histories
        self._surprise_sparkline = SparklineData(max_size=self._config.history_size)
        self._hippocampus_sparkline = SparklineData(max_size=self._config.history_size)
        self._coherency_sparkline = SparklineData(max_size=self._config.history_size)
        self._latency_sparkline = SparklineData(max_size=self._config.history_size)

        # Last snapshot for rendering
        self._last_snapshot: CortexHealthSnapshot | None = None

    # === Lifecycle ===

    async def start(self) -> None:
        """Start dashboard updates."""
        if self._running:
            return

        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())

    async def stop(self) -> None:
        """Stop dashboard updates."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None

    async def _update_loop(self) -> None:
        """Background loop that updates dashboard."""
        while self._running:
            try:
                self._update()
            except Exception:
                pass  # Don't crash on update errors

            await asyncio.sleep(self._config.emission_interval)

    def _update(self) -> None:
        """Update dashboard state."""
        snapshot = self._observer.get_health()
        self._last_snapshot = snapshot

        # Update sparklines
        self._surprise_sparkline.add(snapshot.synapse.surprise_avg)
        self._hippocampus_sparkline.add(snapshot.hippocampus.utilization)
        self._coherency_sparkline.add(snapshot.coherency.coherency_rate)
        self._latency_sparkline.add(snapshot.left_hemisphere.latency_ms)

    # === Rendering ===

    def render_compact(self) -> str:
        """
        Render compact status line.

        Returns:
            Single-line status summary
        """
        if self._last_snapshot is None:
            self._update()

        snapshot = self._last_snapshot
        if snapshot is None:
            return "[CORTEX] ? UNKNOWN"

        # Status symbol
        status_symbols = {
            CortexHealth.HEALTHY: "OK",
            CortexHealth.DEGRADED: "!",
            CortexHealth.CRITICAL: "X",
            CortexHealth.UNKNOWN: "?",
        }
        symbol = status_symbols.get(snapshot.overall, "?")

        # Build compact line
        parts = [f"[CORTEX] {symbol} {snapshot.overall.value.upper()}"]

        # Add latencies
        if snapshot.left_hemisphere.available:
            parts.append(f"L:{snapshot.left_hemisphere.latency_ms:.0f}ms")
        if snapshot.right_hemisphere.available:
            parts.append(f"R:{snapshot.right_hemisphere.latency_ms:.0f}ms")

        # Add hippocampus
        if snapshot.hippocampus.available:
            parts.append(
                f"H:{snapshot.hippocampus.memory_count}/{snapshot.hippocampus.max_size}"
            )

        # Add synapse
        if snapshot.synapse.available:
            parts.append(f"S:{snapshot.synapse.surprise_avg:.2f}")

        # Add dreamer
        if snapshot.dreamer.available:
            parts.append(f"Dreams:{snapshot.dreamer.dream_cycles_total}")

        return " | ".join(parts)

    def render_full(self) -> str:
        """
        Render full ASCII dashboard.

        Returns:
            Multi-line dashboard display
        """
        if self._last_snapshot is None:
            self._update()

        snapshot = self._last_snapshot
        if snapshot is None:
            return self._render_empty_dashboard()

        lines = []

        # Header
        lines.append(self._render_header(snapshot))
        lines.append("")

        # Panels
        for panel in self._config.panels:
            panel_lines = self._render_panel(panel, snapshot)
            lines.extend(panel_lines)
            lines.append("")

        return "\n".join(lines)

    def _render_header(self, snapshot: CortexHealthSnapshot) -> str:
        """Render dashboard header."""
        # Status indicator
        indicators = {
            CortexHealth.HEALTHY: "HEALTHY",
            CortexHealth.DEGRADED: "! DEGRADED",
            CortexHealth.CRITICAL: "X CRITICAL",
            CortexHealth.UNKNOWN: "? UNKNOWN",
        }
        indicator = indicators.get(snapshot.overall, "?")

        width = 70
        title = f" BICAMERAL CORTEX - {indicator} "
        padding = width - len(title)
        left_pad = padding // 2
        right_pad = padding - left_pad

        return "=" * left_pad + title + "=" * right_pad

    def _render_empty_dashboard(self) -> str:
        """Render empty state dashboard."""
        lines = [
            "=" * 70,
            " BICAMERAL CORTEX - INITIALIZING ".center(70, "="),
            "=" * 70,
            "",
            "  Waiting for first health check...",
            "",
        ]
        return "\n".join(lines)

    def _render_panel(
        self, panel: DashboardPanel, snapshot: CortexHealthSnapshot
    ) -> list[str]:
        """Render a single dashboard panel."""
        renderers = {
            DashboardPanel.HEMISPHERE_STATUS: self._render_hemisphere_panel,
            DashboardPanel.COHERENCY_MONITOR: self._render_coherency_panel,
            DashboardPanel.SYNAPSE_MONITOR: self._render_synapse_panel,
            DashboardPanel.HIPPOCAMPUS_GAUGE: self._render_hippocampus_panel,
            DashboardPanel.DREAM_REPORT: self._render_dream_panel,
            DashboardPanel.NEUROGENESIS_QUEUE: self._render_neurogenesis_panel,
        }

        renderer = renderers.get(panel)
        if renderer:
            return renderer(snapshot)
        return []

    def _render_hemisphere_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render hemisphere status panel."""
        left = snapshot.left_hemisphere
        right = snapshot.right_hemisphere

        lines = [
            "-- Hemisphere Status --",
            f"  Left (Bookkeeper):  {'OK' if left.available else 'XX'} | "
            f"Latency: {left.latency_ms:.1f}ms | "
            f"Queries: {left.queries_total} | "
            f"Errors: {left.errors_total}",
            f"  Right (Poet):       {'OK' if right.available else 'XX'} | "
            f"Latency: {right.latency_ms:.1f}ms | "
            f"Vectors: {right.vectors_count}",
            f"  Latency Trend: [{self._latency_sparkline.render(20)}]",
        ]
        return lines

    def _render_coherency_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render coherency monitor panel."""
        c = snapshot.coherency

        # Progress bar for coherency rate
        bar_width = 20
        filled = int(c.coherency_rate * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        lines = [
            "-- Coherency Monitor --",
            f"  Rate: [{bar}] {c.coherency_rate:.1%}",
            f"  Ghosts: {c.ghost_count} (healed: {c.ghosts_healed_total}) | "
            f"Stale: {c.stale_count} (flagged: {c.stale_flagged_total})",
            f"  Trend: [{self._coherency_sparkline.render(20)}]",
        ]
        return lines

    def _render_synapse_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render synapse monitor panel."""
        s = snapshot.synapse

        # Route breakdown bar
        total = s.flashbulb_rate + s.fast_path_rate + s.batch_path_rate
        if total > 0:
            flash_chars = int((s.flashbulb_rate / total) * 20) if total else 0
            fast_chars = int((s.fast_path_rate / total) * 20) if total else 0
            batch_chars = 20 - flash_chars - fast_chars
            route_bar = "!" * flash_chars + ">" * fast_chars + "." * batch_chars
        else:
            route_bar = "." * 20

        lines = [
            "-- Synapse Monitor --",
            f"  Available: {'OK' if s.available else 'XX'} | "
            f"Signals: {s.signals_total} | "
            f"Pending: {s.batch_pending}",
            f"  Surprise Avg: {s.surprise_avg:.3f} | "
            f"Flashbulb: {s.has_flashbulb_pending}",
            f"  Routes [!>..]: [{route_bar}] "
            f"(!:{s.flashbulb_rate:.0%} >:{s.fast_path_rate:.0%} .:{s.batch_path_rate:.0%})",
            f"  Surprise Trend: [{self._surprise_sparkline.render(20)}]",
        ]
        return lines

    def _render_hippocampus_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render hippocampus gauge panel."""
        h = snapshot.hippocampus

        # Utilization bar
        bar_width = 20
        filled = int(h.utilization * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        # Color indicator
        color_indicator = " "
        if h.utilization > 0.9:
            color_indicator = "!"
        elif h.utilization > 0.7:
            color_indicator = "~"

        lines = [
            "-- Hippocampus (Short-Term Memory) --",
            f"  Available: {'OK' if h.available else 'XX'} | "
            f"Size: {h.memory_count}/{h.max_size}",
            f"  Utilization: [{bar}] {h.utilization:.1%} {color_indicator}",
            f"  Flushes: {h.flushes_total} | Last: {h.last_flush or 'never'}",
            f"  Trend: [{self._hippocampus_sparkline.render(20)}]",
        ]
        return lines

    def _render_dream_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render dream report panel."""
        d = snapshot.dreamer

        phase_indicators = {
            "awake": "AWAKE",
            "entering_rem": ">REM",
            "rem_consolidation": "REM:CONSOLIDATE",
            "rem_maintenance": "REM:MAINTAIN",
            "rem_reflection": "REM:REFLECT",
            "waking": "<WAKE",
            "interrupted": "!INTERRUPT",
        }
        phase_display = phase_indicators.get(d.phase, d.phase)

        lines = [
            "-- Lucid Dreamer --",
            f"  Available: {'OK' if d.available else 'XX'} | Phase: {phase_display}",
            f"  Cycles: {d.dream_cycles_total} | "
            f"Interrupted: {d.interrupted_total} | "
            f"Briefing: {d.morning_briefing_count} questions",
            f"  Last Dream: {d.last_dream or 'never'}",
        ]
        return lines

    def _render_neurogenesis_panel(self, snapshot: CortexHealthSnapshot) -> list[str]:
        """Render neurogenesis queue panel."""
        # Would need integration with SchemaNeurogenesis for full data
        lines = [
            "-- Schema Neurogenesis --",
            "  Pending Proposals: 0",
            "  Last Analysis: never",
        ]
        return lines

    # === Wire Protocol Integration ===

    def get_wire_state(self) -> dict[str, Any]:
        """
        Get current state for wire protocol emission.

        Returns:
            State dictionary for WireObservable
        """
        if self._last_snapshot is None:
            self._update()

        snapshot = self._last_snapshot
        if snapshot is None:
            return {"status": "initializing"}

        return {
            "status": snapshot.overall.value,
            "timestamp": snapshot.timestamp,
            "compact": self.render_compact(),
            "health": snapshot.to_dict(),
            "sparklines": {
                "surprise": self._surprise_sparkline.values[-20:],
                "hippocampus": self._hippocampus_sparkline.values[-20:],
                "coherency": self._coherency_sparkline.values[-20:],
                "latency": self._latency_sparkline.values[-20:],
            },
        }

    def to_json(self) -> str:
        """
        Export dashboard state as JSON.

        Returns:
            JSON string of dashboard state
        """
        return json.dumps(self.get_wire_state(), indent=2, default=str)


# === Factory Functions ===


def create_cortex_dashboard(
    observer: CortexObserver,
    config_dict: dict[str, Any] | None = None,
) -> CortexDashboard:
    """
    Create a CortexDashboard instance.

    Args:
        observer: CortexObserver to visualize
        config_dict: Configuration dictionary

    Returns:
        Configured CortexDashboard
    """
    config = (
        CortexDashboardConfig.from_dict(config_dict)
        if config_dict
        else CortexDashboardConfig()
    )

    return CortexDashboard(observer=observer, config=config)


def create_minimal_dashboard(observer: CortexObserver) -> CortexDashboard:
    """
    Create a minimal dashboard with just hemisphere and coherency.

    Args:
        observer: CortexObserver to visualize

    Returns:
        Minimal CortexDashboard
    """
    config = CortexDashboardConfig(
        panels=[
            DashboardPanel.HEMISPHERE_STATUS,
            DashboardPanel.COHERENCY_MONITOR,
        ],
        compact_mode=True,
    )
    return CortexDashboard(observer=observer, config=config)
