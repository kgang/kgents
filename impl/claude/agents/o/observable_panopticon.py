"""
O-gent Phase 4: Witness Integration for Observability.

This module bridges O-gent's Panopticon with the Witness protocol,
enabling structured observability via Witness marks.

Key Components:
1. **ObservablePanopticon**: Panopticon that emits Witness marks
2. **WitnessObserver**: Observer that emits observations via Witness protocol
3. **PanopticonDashboard**: Async dashboard that streams to Witness

Integration Pattern:
    O-gent observes → emits Witness marks → queryable via MarkStore

Spec Reference: spec/o-gents/README.md - Integration Points / Witness
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Optional

if TYPE_CHECKING:
    from services.witness import Mark, MarkStore

from .observer import (
    BaseObserver,
    EntropyEvent,
    ObservationContext,
    ObservationResult,
    ObservationStatus,
)

# Import O-gent components
from .panopticon import (
    AlertSeverity,
    IntegratedPanopticon,
    PanopticonAlert,
    UnifiedPanopticonStatus,
    create_integrated_panopticon,
)

# =============================================================================
# Witness Mark Emission Modes
# =============================================================================


class EmissionMode(str, Enum):
    """How often to emit Witness marks."""

    CONTINUOUS = "continuous"  # Emit on every observation
    BATCHED = "batched"  # Batch observations, emit periodically
    ON_CHANGE = "on_change"  # Only emit when status changes
    ON_ALERT = "on_alert"  # Only emit when alerts occur


# =============================================================================
# Observable Panopticon Status
# =============================================================================


@dataclass
class WitnessStatusSnapshot:
    """
    Snapshot of Panopticon status for Witness mark emission.

    Optimized for serialization and storage as Witness mark metadata.
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
        """Convert to dict for Witness mark metadata."""
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
    def from_panopticon_status(cls, status: UnifiedPanopticonStatus) -> "WitnessStatusSnapshot":
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


class ObservablePanopticon:
    """
    Panopticon with Witness protocol integration.

    Wraps IntegratedPanopticon and emits status updates via Witness marks,
    enabling structured observability and traceability.

    Usage:
        >>> panopticon = ObservablePanopticon()
        >>> await panopticon.start_streaming()
        >>> # Witness marks emitted to MarkStore
        >>> # Query via: get_mark_store().query(origins=("o-gent-panopticon",))
    """

    def __init__(
        self,
        agent_name: str = "o-gent-panopticon",
        panopticon: Optional[IntegratedPanopticon] = None,
        emission_mode: EmissionMode = EmissionMode.BATCHED,
        emission_interval: float = 1.0,
        history_limit: int = 100,
    ):
        """
        Initialize ObservablePanopticon.

        Args:
            agent_name: Agent identifier for Witness marks
            panopticon: Existing IntegratedPanopticon (creates one if None)
            emission_mode: How often to emit updates
            emission_interval: Seconds between batched emissions
            history_limit: Max history snapshots to retain
        """
        self.agent_name = agent_name
        self.panopticon = panopticon or create_integrated_panopticon()
        self.emission_mode = emission_mode
        self.emission_interval = emission_interval
        self.history_limit = history_limit

        # History of status snapshots
        self._history: list[WitnessStatusSnapshot] = []

        # Last emitted status (for on_change mode)
        self._last_status: str | None = None
        self._last_alert_count: int = 0

        # Streaming state
        self._streaming = False
        self._stream_task: Optional[asyncio.Task[None]] = None

        # Callbacks
        self._on_status_change: list[Callable[[WitnessStatusSnapshot], None]] = []
        self._on_alert: list[Callable[[PanopticonAlert], None]] = []

    # -------------------------------------------------------------------------
    # Status Collection and Emission
    # -------------------------------------------------------------------------

    def collect_snapshot(self) -> WitnessStatusSnapshot:
        """Collect current status snapshot."""
        status = self.panopticon.get_status()
        snapshot = WitnessStatusSnapshot.from_panopticon_status(status)

        # Add to history
        self._history.append(snapshot)
        while len(self._history) > self.history_limit:
            self._history.pop(0)

        return snapshot

    def emit_snapshot(self, snapshot: WitnessStatusSnapshot) -> None:
        """Emit snapshot via Witness mark."""
        from services.witness import Mark, Stimulus, Response, UmweltSnapshot, get_mark_store

        # Create Witness mark for this observation
        mark = Mark(
            origin=self.agent_name,
            stimulus=Stimulus(
                kind="observation",
                content=f"Panopticon status check: {snapshot.system_status}",
                source="o-gent",
            ),
            response=Response(
                kind="observation",
                content=f"System: {snapshot.system_status}, Alerts: {snapshot.alert_count}",
                success=snapshot.system_status in ("HOMEOSTATIC", "DEGRADED"),
                metadata=snapshot.to_dict(),
            ),
            umwelt=UmweltSnapshot.system(),
            tags=("panopticon", "observability", "o-gent"),
            metadata={
                "emission_mode": self.emission_mode.value,
                "alert_count": snapshot.alert_count,
                "critical_alerts": snapshot.critical_alerts,
            },
        )

        # Store mark
        store = get_mark_store()
        store.append(mark)

    def emit_alert(self, alert: PanopticonAlert) -> None:
        """Emit alert via Witness mark."""
        from services.witness import Mark, Stimulus, Response, UmweltSnapshot, get_mark_store

        # Create Witness mark for this alert
        mark = Mark(
            origin=self.agent_name,
            stimulus=Stimulus(
                kind="alert",
                content=f"Alert from {alert.source}",
                source="o-gent",
                metadata={"severity": alert.severity.value},
            ),
            response=Response(
                kind="alert",
                content=str(alert),
                success=False,
                metadata={
                    "severity": alert.severity.value,
                    "source": alert.source,
                },
            ),
            umwelt=UmweltSnapshot.system(),
            tags=("panopticon", "alert", alert.severity.value),
        )

        # Store mark
        store = get_mark_store()
        store.append(mark)

        # Trigger callbacks
        for callback in self._on_alert:
            callback(alert)

    def should_emit(self, snapshot: WitnessStatusSnapshot) -> bool:
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
        """Start streaming status updates to Witness marks."""
        if self._streaming:
            return

        self._streaming = True
        self._stream_task = asyncio.create_task(self._stream_loop())

    async def stop_streaming(self) -> None:
        """Stop streaming status updates."""
        self._streaming = False
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass

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
            except Exception:
                # Silently continue on error
                await asyncio.sleep(self.emission_interval)

    async def stream_snapshots(
        self,
        interval: float | None = None,
    ) -> AsyncIterator[WitnessStatusSnapshot]:
        """
        Async generator yielding status snapshots.

        Useful for programmatic consumption.
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
        self, callback: Callable[[WitnessStatusSnapshot], None]
    ) -> Callable[[], None]:
        """
        Register callback for status changes.

        Returns unsubscribe function.
        """
        self._on_status_change.append(callback)
        return lambda: self._on_status_change.remove(callback)

    def on_alert(self, callback: Callable[[PanopticonAlert], None]) -> Callable[[], None]:
        """
        Register callback for alerts.

        Returns unsubscribe function.
        """
        self._on_alert.append(callback)
        return lambda: self._on_alert.remove(callback)

    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------

    def get_history(self, limit: int = 50) -> list[WitnessStatusSnapshot]:
        """Get status history."""
        return self._history[-limit:]

    def get_current_snapshot(self) -> WitnessStatusSnapshot:
        """Get current status snapshot without storing."""
        status = self.panopticon.get_status()
        return WitnessStatusSnapshot.from_panopticon_status(status)

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
# Witness Observer
# =============================================================================


class WitnessObserver(BaseObserver):
    """
    Observer that emits observations via Witness protocol.

    Bridges the Observer pattern with Witness marks,
    allowing any observation to be captured and traced.
    """

    def __init__(
        self,
        observer_id: str = "witness-observer",
        emit_context: bool = True,
        emit_results: bool = True,
        emit_entropy: bool = True,
    ):
        """
        Initialize WitnessObserver.

        Args:
            observer_id: Observer identifier
            emit_context: Whether to emit observation context
            emit_results: Whether to emit observation results
            emit_entropy: Whether to emit entropy (error) events
        """
        super().__init__(observer_id=observer_id)

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
            from services.witness import Mark, Stimulus, Response, UmweltSnapshot, get_mark_store

            mark = Mark(
                origin=self.observer_id,
                stimulus=Stimulus(
                    kind="observation",
                    content=f"Observing {context.agent_name}",
                    source="o-gent",
                ),
                response=Response(
                    kind="context",
                    content=f"Pre-invoke: {context.agent_name}",
                    metadata={"agent_id": agent_id, "observation_id": context.observation_id},
                ),
                umwelt=UmweltSnapshot.system(),
                tags=("observation", "pre-invoke"),
            )
            get_mark_store().append(mark)

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
            from services.witness import Mark, Stimulus, Response, UmweltSnapshot, get_mark_store

            mark = Mark(
                origin=self.observer_id,
                stimulus=Stimulus(
                    kind="observation",
                    content=f"Completed {context.agent_name}",
                    source="o-gent",
                ),
                response=Response(
                    kind="result",
                    content=f"Completed in {duration_ms:.1f}ms",
                    success=True,
                    metadata={"duration_ms": duration_ms, "observation_id": context.observation_id},
                ),
                umwelt=UmweltSnapshot.system(),
                tags=("observation", "post-invoke"),
            )
            get_mark_store().append(mark)

        return obs_result

    def record_entropy(self, context: ObservationContext, error: Exception) -> EntropyEvent:
        """Record entropy (error) event."""
        self._error_count += 1

        entropy_event = EntropyEvent(
            source_agent=context.agent_name,
            event_type="exception",
            severity="error",
            description=f"{type(error).__name__}: {error}",
            data={"error_type": type(error).__name__},
        )

        if self._emit_entropy:
            from services.witness import Mark, Stimulus, Response, UmweltSnapshot, get_mark_store

            mark = Mark(
                origin=self.observer_id,
                stimulus=Stimulus(
                    kind="error",
                    content=f"Error in {context.agent_name}",
                    source="o-gent",
                ),
                response=Response(
                    kind="error",
                    content=f"{type(error).__name__}: {error}",
                    success=False,
                    metadata={"error_type": type(error).__name__},
                ),
                umwelt=UmweltSnapshot.system(),
                tags=("observation", "entropy", "error"),
            )
            get_mark_store().append(mark)

        return entropy_event

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


def create_witness_observer(
    observer_id: str = "witness-observer",
    emit_all: bool = True,
) -> WitnessObserver:
    """
    Create a WitnessObserver instance.

    Args:
        observer_id: Observer identifier
        emit_all: Whether to emit all event types

    Returns:
        Configured WitnessObserver
    """
    return WitnessObserver(
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
