"""
O-gent Phase 3: Panopticon Integration

The Panopticon is the unified observation dashboard that aggregates all three
dimensions of O-gent observability plus BootstrapWitness integrity verification.

Spec Reference: spec/o-gents/README.md - "The Panopticon Dashboard"

The Panopticon provides:
1. **Dimension X (Telemetry)**: Latency, error rates, throughput
2. **Dimension Y (Semantics)**: Drift, hallucinations, Borromean knot integrity
3. **Dimension Z (Axiology)**: RoC, GDP, economic health
4. **Bootstrap**: Identity laws, composition laws, kernel integrity
5. **VoI**: Observation economics, RoVI, budget utilization

Key Features:
- Unified status aggregation across all observers
- Real-time streaming via async generators
- Alert aggregation and prioritization
- ASCII dashboard rendering (spec-compliant)
- Integration with BootstrapWitness for kernel verification
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable

from .axiological import AxiologicalObserver, RoCMonitor
from .bootstrap_witness import (
    BootstrapObserver,
    BootstrapVerificationResult,
)
from .observer import (
    BaseObserver,
    ObservationContext,
    ObservationResult,
    ObserverLevel,
)
from .semantic import BorromeanObserver, DriftDetector, SemanticObserver
from .telemetry import TelemetryObserver, TopologyMapper

# VoI integration (optional)
try:
    from .voi_observer import (
        ObservationDepth,
        VoIAwareObserver,
        VoIObservationConfig,
    )

    HAS_VOI = True
except ImportError:
    HAS_VOI = False


# =============================================================================
# System Status Enum
# =============================================================================


class SystemStatus(str, Enum):
    """Overall system health status."""

    HOMEOSTATIC = "HOMEOSTATIC"  # All systems nominal
    DEGRADED = "DEGRADED"  # Some issues, but operational
    CRITICAL = "CRITICAL"  # Serious issues requiring attention
    UNKNOWN = "UNKNOWN"  # Cannot determine status


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# Alert Types
# =============================================================================


@dataclass(frozen=True)
class PanopticonAlert:
    """An alert raised by the Panopticon."""

    severity: AlertSeverity
    source: str  # e.g., "telemetry", "semantic", "axiological", "bootstrap"
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.source}: {self.message}"


# =============================================================================
# Dimension Status Types
# =============================================================================


@dataclass
class TelemetryStatus:
    """Status of Dimension X: Telemetry."""

    ops_per_second: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0
    active_agents: int = 0
    total_invocations: int = 0
    composition_count: int = 0

    @property
    def healthy(self) -> bool:
        """Is telemetry healthy?"""
        return self.error_rate < 0.05 and self.latency_p95_ms < 1000


@dataclass
class SemanticStatus:
    """Status of Dimension Y: Semantics."""

    drift_score: float = 0.0
    drift_severity: str = "NONE"
    knots_checked: int = 0
    knots_intact_pct: float = 100.0
    hallucinations_caught: int = 0
    hallucination_rate: float = 0.0

    @property
    def healthy(self) -> bool:
        """Is semantic health good?"""
        return self.drift_score < 0.3 and self.knots_intact_pct >= 95.0


@dataclass
class AxiologicalStatus:
    """Status of Dimension Z: Axiology (Economics)."""

    system_gdp: float = 0.0
    total_gas_burned: float = 0.0
    net_roc: float = 0.0
    agent_count: int = 0
    top_performer: str | None = None
    top_performer_roc: float = 0.0
    worst_performer: str | None = None
    worst_performer_roc: float = 0.0
    anomaly_count: int = 0

    @property
    def healthy(self) -> bool:
        """Is economic health good?"""
        return self.net_roc >= 1.0 and self.anomaly_count == 0


@dataclass
class BootstrapStatus:
    """Status of Bootstrap integrity."""

    all_agents_exist: bool = True
    identity_laws_hold: bool = True
    composition_laws_hold: bool = True
    kernel_intact: bool = True
    last_verified: datetime | None = None
    verification_streak: int = 0
    agents_importable: int = 2  # Id, Compose are always available
    agents_total: int = 7

    @property
    def healthy(self) -> bool:
        """Is bootstrap kernel healthy?"""
        return self.kernel_intact


@dataclass
class VoIStatus:
    """Status of VoI observation economics."""

    total_observations: int = 0
    skipped_observations: int = 0
    total_gas_consumed: float = 0.0
    total_voi_generated: float = 0.0
    rovi: float = 0.0  # Return on VoI
    observation_fraction: float = 0.0
    budget_utilization: dict[str, float] = field(default_factory=dict)

    @property
    def healthy(self) -> bool:
        """Is VoI economics healthy?"""
        return self.rovi >= 1.0 and self.observation_fraction < 0.10


# =============================================================================
# Unified Panopticon Status
# =============================================================================


@dataclass
class UnifiedPanopticonStatus:
    """
    Complete status of the Panopticon.

    Aggregates all three dimensions + bootstrap + VoI.
    """

    # Overall
    status: SystemStatus = SystemStatus.HOMEOSTATIC
    uptime_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    # Dimensions
    telemetry: TelemetryStatus = field(default_factory=TelemetryStatus)
    semantic: SemanticStatus = field(default_factory=SemanticStatus)
    axiological: AxiologicalStatus = field(default_factory=AxiologicalStatus)
    bootstrap: BootstrapStatus = field(default_factory=BootstrapStatus)
    voi: VoIStatus = field(default_factory=VoIStatus)

    # Alerts
    alerts: list[PanopticonAlert] = field(default_factory=list)
    alert_count_by_severity: dict[str, int] = field(default_factory=dict)

    @property
    def all_dimensions_healthy(self) -> bool:
        """Are all dimensions reporting healthy?"""
        return (
            self.telemetry.healthy
            and self.semantic.healthy
            and self.axiological.healthy
            and self.bootstrap.healthy
        )

    @property
    def critical_alerts(self) -> list[PanopticonAlert]:
        """Get critical alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]


# =============================================================================
# Integrated Panopticon
# =============================================================================


class IntegratedPanopticon(BaseObserver):
    """
    The integrated Panopticon dashboard.

    Aggregates all O-gent observers into a unified view:
    - Dimension X: TelemetryObserver, TopologyMapper
    - Dimension Y: SemanticObserver, DriftDetector, BorromeanObserver
    - Dimension Z: AxiologicalObserver, RoCMonitor
    - Bootstrap: BootstrapWitness, BootstrapObserver
    - VoI: VoIAwareObserver

    Hierarchy Level: SYSTEM (Level 2)
    """

    def __init__(
        self,
        observer_id: str = "panopticon",
        # Dimension X
        telemetry: TelemetryObserver | None = None,
        topology: TopologyMapper | None = None,
        # Dimension Y
        semantic: SemanticObserver | None = None,
        drift_detector: DriftDetector | None = None,
        borromean: BorromeanObserver | None = None,
        # Dimension Z
        axiological: AxiologicalObserver | None = None,
        roc_monitor: RoCMonitor | None = None,
        # Bootstrap
        bootstrap_observer: BootstrapObserver | None = None,
        # VoI
        voi_observer: Any | None = None,  # VoIAwareObserver if available
        # Config
        alert_callback: Callable[[PanopticonAlert], None] | None = None,
        max_alerts: int = 100,
        bootstrap_check_interval_s: float = 60.0,
    ):
        super().__init__(observer_id=observer_id)
        self._level = ObserverLevel.SYSTEM

        # Dimension X: Telemetry
        self.telemetry = telemetry or TelemetryObserver()
        self.topology = topology or TopologyMapper()

        # Dimension Y: Semantics
        self.semantic = semantic
        self.drift_detector = drift_detector
        self.borromean = borromean

        # Dimension Z: Axiology
        self.axiological = axiological
        self.roc_monitor = roc_monitor

        # Bootstrap
        self.bootstrap_observer = bootstrap_observer or BootstrapObserver()

        # VoI
        self.voi_observer = voi_observer

        # Alerts
        self._alerts: list[PanopticonAlert] = []
        self._alert_callback = alert_callback
        self._max_alerts = max_alerts

        # Timing
        self._start_time = datetime.now()
        self._last_bootstrap_check: datetime | None = None
        self._bootstrap_check_interval = bootstrap_check_interval_s
        self._last_bootstrap_result: BootstrapVerificationResult | None = None

        # Streaming
        self._streaming = False
        self._stream_interval_s = 1.0

    # -------------------------------------------------------------------------
    # Alert Management
    # -------------------------------------------------------------------------

    def add_alert(
        self,
        severity: AlertSeverity,
        source: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> PanopticonAlert:
        """Add an alert to the Panopticon."""
        alert = PanopticonAlert(
            severity=severity,
            source=source,
            message=message,
            details=details or {},
        )

        self._alerts.append(alert)

        # Trim to max alerts
        if len(self._alerts) > self._max_alerts:
            self._alerts = self._alerts[-self._max_alerts :]

        # Callback
        if self._alert_callback:
            self._alert_callback(alert)

        return alert

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self._alerts.clear()

    @property
    def alerts(self) -> list[PanopticonAlert]:
        """Get all alerts."""
        return list(self._alerts)

    def get_alerts_by_severity(self, severity: AlertSeverity) -> list[PanopticonAlert]:
        """Get alerts filtered by severity."""
        return [a for a in self._alerts if a.severity == severity]

    # -------------------------------------------------------------------------
    # Status Collection
    # -------------------------------------------------------------------------

    def _collect_telemetry_status(self) -> TelemetryStatus:
        """Collect Dimension X status."""
        status = TelemetryStatus()

        # Get metrics from telemetry observer
        metrics = self.telemetry.metrics

        # Aggregate latency histogram
        latency_hist = metrics.get_histogram("agent.latency_ms")
        if latency_hist:
            status.latency_p50_ms = latency_hist.percentile(0.50)
            status.latency_p95_ms = latency_hist.percentile(0.95)
            status.latency_p99_ms = latency_hist.percentile(0.99)
            status.total_invocations = latency_hist.count

        # Error rate
        total_success = metrics.get_counter("agent.invocations")
        total_errors = metrics.get_counter("agent.errors")
        if total_success + total_errors > 0:
            status.error_rate = total_errors / (total_success + total_errors)

        # Topology
        graph = self.topology.get_topology()
        status.active_agents = len(graph.nodes)
        status.composition_count = sum(e.count for e in graph.edges)

        return status

    def _collect_semantic_status(self) -> SemanticStatus:
        """Collect Dimension Y status."""
        status = SemanticStatus()

        if self.semantic:
            if hasattr(self.semantic, "drift_detector"):
                status.drift_score = self.semantic.drift_detector.get_average_drift(
                    "system"
                )
            if status.drift_score < 0.1:
                status.drift_severity = "NONE"
            elif status.drift_score < 0.3:
                status.drift_severity = "LOW"
            elif status.drift_score < 0.5:
                status.drift_severity = "MEDIUM"
            elif status.drift_score < 0.7:
                status.drift_severity = "HIGH"
            else:
                status.drift_severity = "CRITICAL"

        if self.borromean:
            # Get from borromean observer history if available
            history = getattr(self.borromean, "_history", [])
            status.knots_checked = len(history)
            if history:
                intact = sum(1 for h in history if h.knot_intact)
                status.knots_intact_pct = (
                    (intact / len(history)) * 100 if history else 100.0
                )

        return status

    def _collect_axiological_status(self) -> AxiologicalStatus:
        """Collect Dimension Z status."""
        status = AxiologicalStatus()

        if self.axiological:
            health = self.axiological.get_health_report()
            status.system_gdp = health.system_gdp
            status.total_gas_burned = health.total_gas_burned
            status.net_roc = health.system_roc
            status.agent_count = len(health.agent_rankings)
            status.anomaly_count = len(health.anomalies)

            if health.agent_rankings:
                top = health.agent_rankings[0]
                status.top_performer = top.agent_id
                status.top_performer_roc = top.roc

                worst = min(health.agent_rankings, key=lambda r: r.roc)
                status.worst_performer = worst.agent_id
                status.worst_performer_roc = worst.roc

        return status

    def _collect_bootstrap_status(self) -> BootstrapStatus:
        """Collect Bootstrap status."""
        status = BootstrapStatus()

        last = self.bootstrap_observer.last_verification
        if last:
            self._last_bootstrap_result = last
            status.all_agents_exist = last.all_agents_exist
            status.identity_laws_hold = last.identity_laws_hold
            status.composition_laws_hold = last.composition_laws_hold
            status.kernel_intact = last.kernel_intact
            status.last_verified = last.verified_at
            status.verification_streak = self.bootstrap_observer.integrity_streak

            if last.agent_results:
                status.agents_importable = sum(
                    1 for r in last.agent_results if r.importable
                )
                status.agents_total = len(last.agent_results)

        return status

    def _collect_voi_status(self) -> VoIStatus:
        """Collect VoI status."""
        status = VoIStatus()

        if self.voi_observer and HAS_VOI:
            stats = self.voi_observer.get_stats()
            status.total_observations = stats.get("total_observations", 0)
            status.skipped_observations = stats.get("skipped_observations", 0)
            status.total_gas_consumed = stats.get("total_gas_consumed", 0.0)
            status.total_voi_generated = stats.get("total_voi_generated", 0.0)
            status.rovi = stats.get("rovi", 0.0)
            status.budget_utilization = stats.get("budget_utilization", {})

        return status

    def _determine_system_status(
        self,
        telemetry: TelemetryStatus,
        semantic: SemanticStatus,
        axiological: AxiologicalStatus,
        bootstrap: BootstrapStatus,
    ) -> SystemStatus:
        """Determine overall system status."""
        # Critical conditions
        if not bootstrap.kernel_intact:
            return SystemStatus.CRITICAL
        if telemetry.error_rate > 0.10:
            return SystemStatus.CRITICAL
        if axiological.net_roc < 0.5:
            return SystemStatus.CRITICAL
        if semantic.drift_severity == "CRITICAL":
            return SystemStatus.CRITICAL

        # Degraded conditions
        if telemetry.error_rate > 0.05:
            return SystemStatus.DEGRADED
        if axiological.net_roc < 1.0:
            return SystemStatus.DEGRADED
        if semantic.drift_severity in ["HIGH", "MEDIUM"]:
            return SystemStatus.DEGRADED
        if axiological.anomaly_count > 0:
            return SystemStatus.DEGRADED
        if semantic.knots_intact_pct < 95.0:
            return SystemStatus.DEGRADED

        return SystemStatus.HOMEOSTATIC

    def get_status(self) -> UnifiedPanopticonStatus:
        """Get complete Panopticon status."""
        uptime = (datetime.now() - self._start_time).total_seconds()

        telemetry = self._collect_telemetry_status()
        semantic = self._collect_semantic_status()
        axiological = self._collect_axiological_status()
        bootstrap = self._collect_bootstrap_status()
        voi = self._collect_voi_status()

        system_status = self._determine_system_status(
            telemetry, semantic, axiological, bootstrap
        )

        # Count alerts by severity
        alert_counts = {}
        for sev in AlertSeverity:
            count = len([a for a in self._alerts if a.severity == sev])
            if count > 0:
                alert_counts[sev.value] = count

        return UnifiedPanopticonStatus(
            status=system_status,
            uptime_seconds=uptime,
            telemetry=telemetry,
            semantic=semantic,
            axiological=axiological,
            bootstrap=bootstrap,
            voi=voi,
            alerts=list(self._alerts),
            alert_count_by_severity=alert_counts,
        )

    # -------------------------------------------------------------------------
    # Bootstrap Verification Integration
    # -------------------------------------------------------------------------

    async def verify_bootstrap(self) -> BootstrapVerificationResult:
        """Run bootstrap verification and update status."""
        result = await self.bootstrap_observer.verify_and_record()
        self._last_bootstrap_check = datetime.now()
        self._last_bootstrap_result = result

        # Generate alerts if verification failed
        if not result.kernel_intact:
            if not result.identity_laws_hold:
                self.add_alert(
                    AlertSeverity.CRITICAL,
                    "bootstrap",
                    "Identity laws BROKEN - Category laws violated",
                    {
                        "evidence": result.identity_result.evidence
                        if result.identity_result
                        else ""
                    },
                )
            if not result.composition_laws_hold:
                self.add_alert(
                    AlertSeverity.CRITICAL,
                    "bootstrap",
                    "Composition laws BROKEN - Associativity violated",
                    {
                        "evidence": result.composition_result.evidence
                        if result.composition_result
                        else ""
                    },
                )
            if not result.all_agents_exist:
                missing = [r.agent.value for r in result.agent_results if not r.exists]
                self.add_alert(
                    AlertSeverity.ERROR,
                    "bootstrap",
                    f"Bootstrap agents missing: {missing}",
                )

        return result

    async def maybe_verify_bootstrap(self) -> BootstrapVerificationResult | None:
        """Verify bootstrap if interval has elapsed."""
        if self._last_bootstrap_check is None:
            return await self.verify_bootstrap()

        elapsed = (datetime.now() - self._last_bootstrap_check).total_seconds()
        if elapsed >= self._bootstrap_check_interval:
            return await self.verify_bootstrap()

        return self._last_bootstrap_result

    # -------------------------------------------------------------------------
    # Real-time Streaming
    # -------------------------------------------------------------------------

    async def stream_status(
        self,
        interval_s: float = 1.0,
        include_bootstrap: bool = True,
    ) -> AsyncIterator[UnifiedPanopticonStatus]:
        """
        Stream Panopticon status updates.

        Yields status snapshots at the specified interval.
        """
        self._streaming = True
        self._stream_interval_s = interval_s

        try:
            while self._streaming:
                # Maybe run bootstrap verification
                if include_bootstrap:
                    await self.maybe_verify_bootstrap()

                yield self.get_status()
                await asyncio.sleep(interval_s)
        finally:
            self._streaming = False

    def stop_streaming(self) -> None:
        """Stop streaming status updates."""
        self._streaming = False

    # -------------------------------------------------------------------------
    # Dashboard Rendering
    # -------------------------------------------------------------------------

    def render_dashboard(self) -> str:
        """
        Render ASCII dashboard.

        Matches the spec from o-gents/README.md.
        """
        status = self.get_status()
        return render_unified_dashboard(status)

    def render_compact_dashboard(self) -> str:
        """Render a compact single-line status."""
        status = self.get_status()
        return render_compact_status(status)


# =============================================================================
# Dashboard Rendering Functions
# =============================================================================


def render_unified_dashboard(status: UnifiedPanopticonStatus) -> str:
    """
    Render the full Panopticon dashboard.

    Format matches spec from o-gents/README.md.
    """
    s = status
    t = s.telemetry
    y = s.semantic
    z = s.axiological
    b = s.bootstrap

    lines = [
        "┌─ [O] SYSTEM PROPRIOCEPTION ──────────────────────────────────────────┐",
        "│                                                                      │",
        f"│  STATUS: {s.status.value.ljust(20)} TIME: T+{int(s.uptime_seconds)}s{' ' * 20}│",
        "│                                                                      │",
        "│  ┌─ [X] TELEMETRY ──────────┐  ┌─ [Y] SEMANTICS ───────────────┐     │",
        f"│  │ OPS: {t.ops_per_second:.0f}/sec              │  │ DRIFT: {y.drift_score:.2f} ({y.drift_severity.ljust(8)})     │     │",
        f"│  │ LATENCY: {t.latency_p95_ms:.0f}ms (p95)     │  │ KNOTS: {y.knots_intact_pct:.1f}% Intact           │     │",
        f"│  │ ERR: {t.error_rate:.2%}               │  │ HALLUCINATIONS: {y.hallucinations_caught}             │     │",
        "│  └──────────────────────────┘  └───────────────────────────────┘     │",
        "│                                                                      │",
        "│  ┌─ [Z] AXIOLOGY (ECONOMICS) ──────────────────────────────────┐     │",
        f"│  │ SYSTEM GDP: ${z.system_gdp:.2f} (Impact Generated)                       │     │",
        f"│  │ BURN RATE:  ${z.total_gas_burned:.2f} (Tokens Consumed)                       │     │",
        f"│  │ NET ROC:    {z.net_roc:.1f}x {'(Healthy)' if z.net_roc >= 1.0 else '(WARNING)'}                                    │     │",
    ]

    if z.top_performer:
        lines.append(
            f"│  │ TOP PERFORMER: [{z.top_performer}] (RoC: {z.top_performer_roc:.1f}x)              │     │"
        )
    if z.worst_performer and z.worst_performer_roc < 0.5:
        lines.append(
            f"│  │ CASH BURNER:   [{z.worst_performer}] -> [UNDER AUDIT]          │     │"
        )

    lines.extend(
        [
            "│  └─────────────────────────────────────────────────────────────┘     │",
            "│                                                                      │",
            "│  ┌─ BOOTSTRAP ─────────────────────────────────────────────────┐     │",
        ]
    )

    # Bootstrap status
    kernel_status = "VERIFIED" if b.kernel_intact else "BROKEN"
    id_status = "HOLD" if b.identity_laws_hold else "BROKEN"
    comp_status = "HOLD" if b.composition_laws_hold else "BROKEN"

    lines.extend(
        [
            f"│  │ Kernel Integrity:  {kernel_status.ljust(40)}│     │",
            f"│  │ Identity Laws:     {id_status.ljust(40)}│     │",
            f"│  │ Composition Laws:  {comp_status.ljust(40)}│     │",
            f"│  │ Agents: {b.agents_importable}/{b.agents_total} importable, Streak: {b.verification_streak}                       │     │",
            "│  └─────────────────────────────────────────────────────────────┘     │",
        ]
    )

    # Alerts section
    if s.alerts:
        lines.append(
            "│                                                                      │"
        )
        lines.append(
            "│  ┌─ ALERTS ────────────────────────────────────────────────────┐     │"
        )
        for alert in s.alerts[-5:]:
            sev = alert.severity.value[:4]
            msg = str(alert)[:56]
            lines.append(f"│  │ [{sev}] {msg.ljust(56)}│     │")
        lines.append(
            "│  └─────────────────────────────────────────────────────────────┘     │"
        )

    lines.extend(
        [
            "│                                                                      │",
            "└──────────────────────────────────────────────────────────────────────┘",
        ]
    )

    return "\n".join(lines)


def render_compact_status(status: UnifiedPanopticonStatus) -> str:
    """Render a compact single-line status."""
    s = status
    z = s.axiological

    bootstrap_icon = "✓" if s.bootstrap.kernel_intact else "✗"
    semantic_icon = "✓" if s.semantic.healthy else "!"
    economic_icon = "✓" if z.net_roc >= 1.0 else "!"

    return (
        f"[O] {s.status.value} | "
        f"T:{s.telemetry.latency_p95_ms:.0f}ms "
        f"S:{s.semantic.drift_score:.2f}{semantic_icon} "
        f"E:{z.net_roc:.1f}x{economic_icon} "
        f"B:{bootstrap_icon} | "
        f"Alerts:{len(s.alerts)}"
    )


def render_dimensions_summary(status: UnifiedPanopticonStatus) -> str:
    """Render a summary of all dimensions."""
    lines = [
        "DIMENSION SUMMARY",
        "─" * 40,
        f"  [X] Telemetry:  {'HEALTHY' if status.telemetry.healthy else 'DEGRADED'}",
        f"      - Latency p95: {status.telemetry.latency_p95_ms:.1f}ms",
        f"      - Error rate: {status.telemetry.error_rate:.2%}",
        "",
        f"  [Y] Semantics:  {'HEALTHY' if status.semantic.healthy else 'DEGRADED'}",
        f"      - Drift: {status.semantic.drift_score:.2f} ({status.semantic.drift_severity})",
        f"      - Knots intact: {status.semantic.knots_intact_pct:.1f}%",
        "",
        f"  [Z] Axiology:   {'HEALTHY' if status.axiological.healthy else 'DEGRADED'}",
        f"      - RoC: {status.axiological.net_roc:.2f}x",
        f"      - GDP: ${status.axiological.system_gdp:.2f}",
        "",
        f"  [B] Bootstrap:  {'VERIFIED' if status.bootstrap.kernel_intact else 'BROKEN'}",
        f"      - Identity: {'HOLD' if status.bootstrap.identity_laws_hold else 'BROKEN'}",
        f"      - Composition: {'HOLD' if status.bootstrap.composition_laws_hold else 'BROKEN'}",
    ]
    return "\n".join(lines)


# =============================================================================
# Factory Functions
# =============================================================================


def create_integrated_panopticon(
    observer_id: str = "panopticon",
    with_telemetry: bool = True,
    with_semantic: bool = True,
    with_axiological: bool = True,
    with_bootstrap: bool = True,
    with_voi: bool = True,
    bootstrap_check_interval_s: float = 60.0,
) -> IntegratedPanopticon:
    """
    Create an integrated Panopticon with specified observers.

    Args:
        observer_id: Unique identifier for the Panopticon
        with_telemetry: Include telemetry observer
        with_semantic: Include semantic observer
        with_axiological: Include axiological observer
        with_bootstrap: Include bootstrap observer
        with_voi: Include VoI observer
        bootstrap_check_interval_s: Interval for bootstrap verification

    Returns:
        Configured IntegratedPanopticon instance
    """
    kwargs: dict[str, Any] = {
        "observer_id": observer_id,
        "bootstrap_check_interval_s": bootstrap_check_interval_s,
    }

    if with_telemetry:
        kwargs["telemetry"] = TelemetryObserver(observer_id=f"{observer_id}_telemetry")
        kwargs["topology"] = TopologyMapper()

    if with_semantic:
        kwargs["semantic"] = SemanticObserver(observer_id=f"{observer_id}_semantic")

    if with_axiological:
        kwargs["axiological"] = AxiologicalObserver(
            observer_id=f"{observer_id}_axiological"
        )

    if with_bootstrap:
        kwargs["bootstrap_observer"] = BootstrapObserver()

    if with_voi and HAS_VOI:
        kwargs["voi_observer"] = VoIAwareObserver(observer_id=f"{observer_id}_voi")

    return IntegratedPanopticon(**kwargs)


def create_minimal_panopticon(
    observer_id: str = "minimal_panopticon",
) -> IntegratedPanopticon:
    """Create a minimal Panopticon with only bootstrap verification."""
    return IntegratedPanopticon(
        observer_id=observer_id,
        telemetry=TelemetryObserver(),
        bootstrap_observer=BootstrapObserver(),
    )


async def create_verified_panopticon(
    observer_id: str = "verified_panopticon",
) -> tuple[IntegratedPanopticon, BootstrapVerificationResult]:
    """
    Create a Panopticon and run initial bootstrap verification.

    Returns:
        (panopticon, initial_verification_result)
    """
    panopticon = create_integrated_panopticon(observer_id=observer_id)
    result = await panopticon.verify_bootstrap()
    return panopticon, result


# =============================================================================
# Integration Helpers
# =============================================================================


class PanopticonObserver(BaseObserver):
    """
    Observer wrapper that feeds data to the Panopticon.

    Use this to observe agents and have their telemetry automatically
    aggregated into the Panopticon dashboard.
    """

    def __init__(
        self,
        panopticon: IntegratedPanopticon,
        observer_id: str = "panopticon_observer",
    ):
        super().__init__(observer_id=observer_id)
        self.panopticon = panopticon

    def pre_invoke(self, agent: Any, input_data: Any) -> ObservationContext:
        """Pre-invoke hook - delegates to Panopticon's telemetry."""
        return self.panopticon.telemetry.pre_invoke(agent, input_data)

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Post-invoke hook - records to Panopticon."""
        # Record telemetry
        obs_result = await self.panopticon.telemetry.post_invoke(
            context, result, duration_ms
        )

        # Record topology
        self.panopticon.topology.observe_invocation(context.agent_name)

        # Check for issues and add alerts
        if duration_ms > 1000:  # Slow invocation
            self.panopticon.add_alert(
                AlertSeverity.WARN,
                "telemetry",
                f"Slow invocation: {context.agent_name} took {duration_ms:.0f}ms",
            )

        return obs_result

    def record_entropy(self, context: ObservationContext, error: Exception) -> None:
        """Record entropy (error) to Panopticon."""
        self.panopticon.telemetry.record_entropy(context, error)
        self.panopticon.add_alert(
            AlertSeverity.ERROR,
            "telemetry",
            f"Error in {context.agent_name}: {type(error).__name__}",
            {"error": str(error)},
        )


def create_panopticon_observer(
    panopticon: IntegratedPanopticon | None = None,
    observer_id: str = "panopticon_observer",
) -> PanopticonObserver:
    """Create a PanopticonObserver that feeds into a Panopticon."""
    if panopticon is None:
        panopticon = create_integrated_panopticon()
    return PanopticonObserver(panopticon=panopticon, observer_id=observer_id)
