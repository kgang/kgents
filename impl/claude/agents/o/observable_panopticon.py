"""
O-gent Phase 4: W-gent Integration for Visualization.

This module bridges O-gent's Panopticon with W-gent's wire protocol,
enabling real-time visualization of observability data.

Key Components:
1. **ObservablePanopticon**: Panopticon with WireObservable mixin
2. **WireObserver**: Observer that emits observations via wire protocol
3. **PanopticonDashboard**: Async dashboard that streams to wire

Integration Pattern:
    O-gent observes → emits via wire protocol → W-gent renders

Spec Reference: spec/o-gents/README.md - Integration Points / W-gent
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Optional
from pathlib import Path

# Import O-gent components
from .panopticon import (
    IntegratedPanopticon,
    UnifiedPanopticonStatus,
    PanopticonAlert,
    AlertSeverity,
    create_integrated_panopticon,
)
from .observer import (
    BaseObserver,
    ObservationContext,
    ObservationResult,
    ObservationStatus,
)

# Import W-gent wire protocol
from ..w.protocol import WireObservable


# =============================================================================
# Wire Protocol Emission Modes
# =============================================================================


class EmissionMode(str, Enum):
    """How often to emit wire protocol updates."""

    CONTINUOUS = "continuous"  # Emit on every observation
    BATCHED = "batched"  # Batch observations, emit periodically
    ON_CHANGE = "on_change"  # Only emit when status changes
    ON_ALERT = "on_alert"  # Only emit when alerts occur


# =============================================================================
# Observable Panopticon Status
# =============================================================================


@dataclass
class WireStatusSnapshot:
    """
    Snapshot of Panopticon status for wire protocol emission.

    Optimized for serialization and wire transfer.
    """

    timestamp: datetime
    system_status: str
    uptime_seconds: float

    # Dimension summaries (single values, not full objects)
    telemetry_healthy: bool
    telemetry_latency_p95: float
    telemetry_error_rate: float

    semantic_healthy: bool
    semantic_drift: float
    semantic_knots_intact: float

    economic_healthy: bool
    economic_roc: float
    economic_gdp: float

    bootstrap_intact: bool
    bootstrap_streak: int

    # Alerts
    alert_count: int
    critical_alerts: int
    recent_alert: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for wire protocol."""
        return {
            "timestamp": self.timestamp.isoformat() + "Z",
            "system_status": self.system_status,
            "uptime_seconds": self.uptime_seconds,
            "telemetry": {
                "healthy": self.telemetry_healthy,
                "latency_p95": self.telemetry_latency_p95,
                "error_rate": self.telemetry_error_rate,
            },
            "semantic": {
                "healthy": self.semantic_healthy,
                "drift": self.semantic_drift,
                "knots_intact": self.semantic_knots_intact,
            },
            "economic": {
                "healthy": self.economic_healthy,
                "roc": self.economic_roc,
                "gdp": self.economic_gdp,
            },
            "bootstrap": {
                "intact": self.bootstrap_intact,
                "streak": self.bootstrap_streak,
            },
            "alerts": {
                "count": self.alert_count,
                "critical": self.critical_alerts,
                "recent": self.recent_alert,
            },
        }

    @classmethod
    def from_panopticon_status(
        cls, status: UnifiedPanopticonStatus
    ) -> "WireStatusSnapshot":
        """Create snapshot from full Panopticon status."""
        recent_alert = None
        if status.alerts:
            recent_alert = str(status.alerts[-1])

        return cls(
            timestamp=status.timestamp,
            system_status=status.status.value,
            uptime_seconds=status.uptime_seconds,
            telemetry_healthy=status.telemetry.healthy,
            telemetry_latency_p95=status.telemetry.latency_p95_ms,
            telemetry_error_rate=status.telemetry.error_rate,
            semantic_healthy=status.semantic.healthy,
            semantic_drift=status.semantic.drift_score,
            semantic_knots_intact=status.semantic.knots_intact_pct,
            economic_healthy=status.axiological.healthy,
            economic_roc=status.axiological.net_roc,
            economic_gdp=status.axiological.system_gdp,
            bootstrap_intact=status.bootstrap.kernel_intact,
            bootstrap_streak=status.bootstrap.verification_streak,
            alert_count=len(status.alerts),
            critical_alerts=len(status.critical_alerts),
            recent_alert=recent_alert,
        )


# =============================================================================
# Observable Panopticon
# =============================================================================


class ObservablePanopticon(WireObservable):
    """
    Panopticon with W-gent wire protocol integration.

    Wraps IntegratedPanopticon and emits status updates via wire protocol,
    enabling real-time visualization by W-gent fidelity adapters.

    Usage:
        >>> panopticon = ObservablePanopticon()
        >>> await panopticon.start_streaming()
        >>> # Wire files at .wire/o-gent-panopticon/
        >>> # - state.json: Current status snapshot
        >>> # - stream.log: Alert log
        >>> # - metrics.json: Performance metrics
    """

    def __init__(
        self,
        agent_name: str = "o-gent-panopticon",
        wire_base: Optional[Path] = None,
        panopticon: Optional[IntegratedPanopticon] = None,
        emission_mode: EmissionMode = EmissionMode.BATCHED,
        emission_interval: float = 1.0,
        history_limit: int = 100,
    ):
        """
        Initialize ObservablePanopticon.

        Args:
            agent_name: Wire protocol agent name
            wire_base: Base directory for wire files
            panopticon: Existing IntegratedPanopticon (creates one if None)
            emission_mode: How often to emit updates
            emission_interval: Seconds between batched emissions
            history_limit: Max history snapshots to retain
        """
        super().__init__(agent_name, wire_base)

        self.panopticon = panopticon or create_integrated_panopticon()
        self.emission_mode = emission_mode
        self.emission_interval = emission_interval
        self.history_limit = history_limit

        # History of status snapshots
        self._history: list[WireStatusSnapshot] = []

        # Last emitted status (for on_change mode)
        self._last_status: str | None = None
        self._last_alert_count: int = 0

        # Streaming state
        self._streaming = False
        self._stream_task: Optional[asyncio.Task] = None

        # Callbacks
        self._on_status_change: list[Callable[[WireStatusSnapshot], None]] = []
        self._on_alert: list[Callable[[PanopticonAlert], None]] = []

        # Initialize wire state
        self.update_state(
            phase="dormant",
            current_task="Initializing O-gent Panopticon",
            mode=emission_mode.value,
        )

    # -------------------------------------------------------------------------
    # Status Collection and Emission
    # -------------------------------------------------------------------------

    def collect_snapshot(self) -> WireStatusSnapshot:
        """Collect current status snapshot."""
        status = self.panopticon.get_status()
        snapshot = WireStatusSnapshot.from_panopticon_status(status)

        # Add to history
        self._history.append(snapshot)
        while len(self._history) > self.history_limit:
            self._history.pop(0)

        return snapshot

    def emit_snapshot(self, snapshot: WireStatusSnapshot) -> None:
        """Emit snapshot via wire protocol."""
        # Update wire state - don't spread to_dict() to avoid duplicate keys
        self.update_state(
            phase="observing" if snapshot.system_status == "HOMEOSTATIC" else "alert",
            current_task=f"System: {snapshot.system_status}",
            progress=1.0 if snapshot.bootstrap_intact else 0.5,
            stage="monitoring",
            snapshot=snapshot.to_dict(),
        )

        # Update metrics
        self.update_metrics(
            api_calls=len(self._history),
            custom={
                "alert_count": snapshot.alert_count,
                "critical_alerts": snapshot.critical_alerts,
                "roc": snapshot.economic_roc,
                "drift": snapshot.semantic_drift,
            },
        )

    def emit_alert(self, alert: PanopticonAlert) -> None:
        """Emit alert via wire protocol."""
        level = {
            AlertSeverity.INFO: "INFO",
            AlertSeverity.WARN: "WARN",
            AlertSeverity.ERROR: "ERROR",
            AlertSeverity.CRITICAL: "ERROR",
        }.get(alert.severity, "INFO")

        self.log_event(
            level=level,
            stage=alert.source,
            message=str(alert),
        )

        # Trigger callbacks
        for callback in self._on_alert:
            callback(alert)

    def should_emit(self, snapshot: WireStatusSnapshot) -> bool:
        """Determine if snapshot should be emitted based on mode."""
        if self.emission_mode == EmissionMode.CONTINUOUS:
            return True

        if self.emission_mode == EmissionMode.BATCHED:
            return True  # Batching handled by interval

        if self.emission_mode == EmissionMode.ON_CHANGE:
            if self._last_status != snapshot.system_status:
                self._last_status = snapshot.system_status
                return True
            return False

        if self.emission_mode == EmissionMode.ON_ALERT:
            if snapshot.alert_count > self._last_alert_count:
                self._last_alert_count = snapshot.alert_count
                return True
            return False

        return True

    # -------------------------------------------------------------------------
    # Streaming
    # -------------------------------------------------------------------------

    async def start_streaming(self) -> None:
        """Start streaming status updates to wire protocol."""
        if self._streaming:
            return

        self._streaming = True
        self._stream_task = asyncio.create_task(self._stream_loop())

        self.log_event("INFO", "stream", "Started status streaming")
        self.update_state(phase="waking", current_task="Starting stream")

    async def stop_streaming(self) -> None:
        """Stop streaming status updates."""
        self._streaming = False
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass

        self.log_event("INFO", "stream", "Stopped status streaming")
        self.update_state(phase="waning", current_task="Stream stopped")

    async def _stream_loop(self) -> None:
        """Main streaming loop."""
        while self._streaming:
            try:
                snapshot = self.collect_snapshot()

                if self.should_emit(snapshot):
                    self.emit_snapshot(snapshot)

                    # Trigger status change callbacks
                    for callback in self._on_status_change:
                        callback(snapshot)

                # Check for new alerts
                alerts = self.panopticon.alerts
                if len(alerts) > self._last_alert_count:
                    for alert in alerts[self._last_alert_count :]:
                        self.emit_alert(alert)
                    self._last_alert_count = len(alerts)

                await asyncio.sleep(self.emission_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_event("ERROR", "stream", f"Stream error: {e}")
                await asyncio.sleep(self.emission_interval)

    async def stream_snapshots(
        self,
        interval: float | None = None,
    ) -> AsyncIterator[WireStatusSnapshot]:
        """
        Async generator yielding status snapshots.

        Useful for programmatic consumption without wire files.
        """
        interval = interval or self.emission_interval

        while True:
            snapshot = self.collect_snapshot()
            yield snapshot
            await asyncio.sleep(interval)

    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    def on_status_change(
        self, callback: Callable[[WireStatusSnapshot], None]
    ) -> Callable[[], None]:
        """
        Register callback for status changes.

        Returns unsubscribe function.
        """
        self._on_status_change.append(callback)
        return lambda: self._on_status_change.remove(callback)

    def on_alert(
        self, callback: Callable[[PanopticonAlert], None]
    ) -> Callable[[], None]:
        """
        Register callback for alerts.

        Returns unsubscribe function.
        """
        self._on_alert.append(callback)
        return lambda: self._on_alert.remove(callback)

    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------

    def get_history(self, limit: int = 50) -> list[WireStatusSnapshot]:
        """Get status history."""
        return self._history[-limit:]

    def get_current_snapshot(self) -> WireStatusSnapshot:
        """Get current status snapshot without storing."""
        status = self.panopticon.get_status()
        return WireStatusSnapshot.from_panopticon_status(status)

    def get_summary(self) -> str:
        """Get human-readable summary."""
        snapshot = self.get_current_snapshot()
        return f"""
=== O-gent Panopticon (Wire: {self.agent_name}) ===
System: {snapshot.system_status}
Uptime: {snapshot.uptime_seconds:.0f}s

Telemetry: {"HEALTHY" if snapshot.telemetry_healthy else "DEGRADED"}
  Latency p95: {snapshot.telemetry_latency_p95:.1f}ms
  Error rate: {snapshot.telemetry_error_rate:.2%}

Semantics: {"HEALTHY" if snapshot.semantic_healthy else "DEGRADED"}
  Drift: {snapshot.semantic_drift:.2f}
  Knots: {snapshot.semantic_knots_intact:.1f}% intact

Economics: {"HEALTHY" if snapshot.economic_healthy else "DEGRADED"}
  RoC: {snapshot.economic_roc:.2f}x
  GDP: ${snapshot.economic_gdp:.2f}

Bootstrap: {"VERIFIED" if snapshot.bootstrap_intact else "BROKEN"}
  Streak: {snapshot.bootstrap_streak}

Alerts: {snapshot.alert_count} ({snapshot.critical_alerts} critical)
""".strip()


# =============================================================================
# Wire Observer
# =============================================================================


class WireObserver(BaseObserver):
    """
    Observer that emits observations via wire protocol.

    Bridges the Observer pattern with W-gent's wire protocol,
    allowing any observation to be captured and visualized.
    """

    def __init__(
        self,
        observer_id: str = "wire-observer",
        wire_base: Optional[Path] = None,
        emit_context: bool = True,
        emit_results: bool = True,
        emit_entropy: bool = True,
    ):
        """
        Initialize WireObserver.

        Args:
            observer_id: Observer identifier
            wire_base: Base directory for wire files
            emit_context: Whether to emit observation context
            emit_results: Whether to emit observation results
            emit_entropy: Whether to emit entropy (error) events
        """
        super().__init__(observer_id=observer_id)

        self._wire = WireObservable(observer_id, wire_base)
        self._emit_context = emit_context
        self._emit_results = emit_results
        self._emit_entropy = emit_entropy

        self._observation_count = 0
        self._error_count = 0

    def pre_invoke(self, agent: Any, input_data: Any) -> ObservationContext:
        """Pre-invoke: Log observation start."""
        agent_id = getattr(agent, "id", f"agent_{self._observation_count}")
        agent_name = getattr(agent, "name", str(agent))

        context = ObservationContext(
            agent_id=agent_id,
            agent_name=agent_name,
            input_data=input_data,
            observation_id=f"obs_{self._observation_count}",
            metadata={"input_preview": str(input_data)[:100]},
        )

        if self._emit_context:
            self._wire.log_event(
                level="INFO",
                stage="pre_invoke",
                message=f"Observing {context.agent_name}",
            )
            self._wire.update_state(
                phase="active",
                current_task=f"Observing: {context.agent_name}",
                progress=0.0,
            )

        self._observation_count += 1
        return context

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Post-invoke: Log observation completion."""
        obs_result = ObservationResult(
            context=context,
            status=ObservationStatus.COMPLETED,
            output_data=result,
            duration_ms=duration_ms,
        )

        if self._emit_results:
            self._wire.log_event(
                level="INFO",
                stage="post_invoke",
                message=f"Completed {context.agent_name} in {duration_ms:.1f}ms",
            )
            self._wire.update_state(
                phase="active",
                current_task=f"Completed: {context.agent_name}",
                progress=1.0,
                latency_ms=duration_ms,
            )

        return obs_result

    def record_entropy(self, context: ObservationContext, error: Exception) -> None:
        """Record entropy (error) event."""
        self._error_count += 1

        if self._emit_entropy:
            self._wire.log_event(
                level="ERROR",
                stage="entropy",
                message=f"Error in {context.agent_name}: {type(error).__name__}: {error}",
            )
            self._wire.update_state(
                phase="empty",
                error=f"{type(error).__name__}: {error}",
            )

    @property
    def wire(self) -> WireObservable:
        """Access underlying WireObservable."""
        return self._wire

    def get_stats(self) -> dict[str, int]:
        """Get observation statistics."""
        return {
            "observations": self._observation_count,
            "errors": self._error_count,
        }


# =============================================================================
# Panopticon Dashboard (Real-time TUI-ready)
# =============================================================================


@dataclass
class DashboardConfig:
    """Configuration for Panopticon dashboard."""

    update_interval: float = 1.0
    history_depth: int = 60  # 60 seconds of history at 1s intervals
    show_alerts: bool = True
    show_dimensions: bool = True
    show_bootstrap: bool = True
    compact_mode: bool = False


class PanopticonDashboard:
    """
    Real-time dashboard for Panopticon visualization.

    Designed for integration with TUI renderers (I-gent or terminal).
    Emits structured data via wire protocol.
    """

    def __init__(
        self,
        panopticon: ObservablePanopticon | None = None,
        config: DashboardConfig | None = None,
    ):
        """
        Initialize dashboard.

        Args:
            panopticon: ObservablePanopticon instance
            config: Dashboard configuration
        """
        self.panopticon = panopticon or create_observable_panopticon()
        self.config = config or DashboardConfig()

        # Time series for sparklines
        self._latency_history: list[float] = []
        self._roc_history: list[float] = []
        self._drift_history: list[float] = []

    async def start(self) -> None:
        """Start dashboard."""
        await self.panopticon.start_streaming()

        # Register history collection
        self.panopticon.on_status_change(self._collect_history)

    async def stop(self) -> None:
        """Stop dashboard."""
        await self.panopticon.stop_streaming()

    def _collect_history(self, snapshot: WireStatusSnapshot) -> None:
        """Collect history for sparklines."""
        self._latency_history.append(snapshot.telemetry_latency_p95)
        self._roc_history.append(snapshot.economic_roc)
        self._drift_history.append(snapshot.semantic_drift)

        # Trim to history depth
        max_depth = self.config.history_depth
        self._latency_history = self._latency_history[-max_depth:]
        self._roc_history = self._roc_history[-max_depth:]
        self._drift_history = self._drift_history[-max_depth:]

    def render_compact(self) -> str:
        """Render compact single-line status."""
        snapshot = self.panopticon.get_current_snapshot()

        status_icon = {
            "HOMEOSTATIC": "✓",
            "DEGRADED": "!",
            "CRITICAL": "✗",
            "UNKNOWN": "?",
        }.get(snapshot.system_status, "?")

        return (
            f"[O] {status_icon} {snapshot.system_status} | "
            f"T:{snapshot.telemetry_latency_p95:.0f}ms "
            f"S:{snapshot.semantic_drift:.2f} "
            f"E:{snapshot.economic_roc:.1f}x "
            f"B:{'✓' if snapshot.bootstrap_intact else '✗'} | "
            f"Alerts:{snapshot.alert_count}"
        )

    def render_dimensions(self) -> str:
        """Render dimension status panels."""
        snapshot = self.panopticon.get_current_snapshot()

        return f"""
┌─ [X] TELEMETRY ─────────┐  ┌─ [Y] SEMANTICS ──────────┐
│ Latency: {snapshot.telemetry_latency_p95:>6.0f}ms (p95)  │  │ Drift: {snapshot.semantic_drift:>5.2f}              │
│ Errors:  {snapshot.telemetry_error_rate:>6.2%}        │  │ Knots: {snapshot.semantic_knots_intact:>5.1f}% intact     │
│ Status:  {"HEALTHY" if snapshot.telemetry_healthy else "DEGRADED":>8}        │  │ Status: {"HEALTHY" if snapshot.semantic_healthy else "DEGRADED":>8}        │
└─────────────────────────┘  └──────────────────────────┘

┌─ [Z] ECONOMICS ─────────────────────────────────────────┐
│ RoC: {snapshot.economic_roc:>5.2f}x    GDP: ${snapshot.economic_gdp:>8.2f}    {"HEALTHY" if snapshot.economic_healthy else "DEGRADED":>8}       │
└─────────────────────────────────────────────────────────┘
""".strip()

    def render_sparklines(self) -> str:
        """Render ASCII sparklines for time series."""

        def sparkline(values: list[float], width: int = 20) -> str:
            if not values:
                return "─" * width

            min_v = min(values)
            max_v = max(values)
            range_v = max_v - min_v if max_v != min_v else 1

            chars = "▁▂▃▄▅▆▇█"

            # Sample values to fit width
            step = max(1, len(values) // width)
            sampled = values[::step][:width]

            result = ""
            for v in sampled:
                idx = int((v - min_v) / range_v * (len(chars) - 1))
                result += chars[idx]

            return result.ljust(width, "─")

        return f"""
Latency (p95): [{sparkline(self._latency_history)}]
RoC:           [{sparkline(self._roc_history)}]
Drift:         [{sparkline(self._drift_history)}]
""".strip()

    def get_wire_data(self) -> dict[str, Any]:
        """Get data formatted for wire protocol."""
        snapshot = self.panopticon.get_current_snapshot()

        return {
            "snapshot": snapshot.to_dict(),
            "sparklines": {
                "latency": self._latency_history[-20:],
                "roc": self._roc_history[-20:],
                "drift": self._drift_history[-20:],
            },
            "compact": self.render_compact(),
            "dimensions": self.render_dimensions(),
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_observable_panopticon(
    agent_name: str = "o-gent-panopticon",
    emission_mode: EmissionMode = EmissionMode.BATCHED,
    emission_interval: float = 1.0,
    **panopticon_kwargs: Any,
) -> ObservablePanopticon:
    """
    Create an ObservablePanopticon instance.

    Args:
        agent_name: Wire protocol agent name
        emission_mode: How often to emit updates
        emission_interval: Seconds between emissions
        **panopticon_kwargs: Arguments for IntegratedPanopticon

    Returns:
        Configured ObservablePanopticon
    """
    panopticon = create_integrated_panopticon(**panopticon_kwargs)

    return ObservablePanopticon(
        agent_name=agent_name,
        panopticon=panopticon,
        emission_mode=emission_mode,
        emission_interval=emission_interval,
    )


def create_wire_observer(
    observer_id: str = "wire-observer",
    emit_all: bool = True,
) -> WireObserver:
    """
    Create a WireObserver instance.

    Args:
        observer_id: Observer identifier
        emit_all: Whether to emit all event types

    Returns:
        Configured WireObserver
    """
    return WireObserver(
        observer_id=observer_id,
        emit_context=emit_all,
        emit_results=emit_all,
        emit_entropy=True,  # Always emit errors
    )


def create_panopticon_dashboard(
    panopticon: ObservablePanopticon | None = None,
    compact: bool = False,
    update_interval: float = 1.0,
) -> PanopticonDashboard:
    """
    Create a PanopticonDashboard instance.

    Args:
        panopticon: ObservablePanopticon instance
        compact: Whether to use compact mode
        update_interval: Update interval in seconds

    Returns:
        Configured PanopticonDashboard
    """
    config = DashboardConfig(
        compact_mode=compact,
        update_interval=update_interval,
    )

    return PanopticonDashboard(
        panopticon=panopticon,
        config=config,
    )


async def create_streaming_panopticon(
    agent_name: str = "o-gent-panopticon",
    emission_interval: float = 1.0,
) -> ObservablePanopticon:
    """
    Create and start a streaming ObservablePanopticon.

    Args:
        agent_name: Wire protocol agent name
        emission_interval: Update interval in seconds

    Returns:
        Started ObservablePanopticon
    """
    panopticon = create_observable_panopticon(
        agent_name=agent_name,
        emission_interval=emission_interval,
    )
    await panopticon.start_streaming()
    return panopticon
