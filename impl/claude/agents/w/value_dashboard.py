"""
Value Dashboard - Real-time visualization of B-gent economic metrics.

The Value Dashboard integrates W-gent's wire protocol with B-gent's value
accounting to provide live visualization of:

1. **Token Economics**
   - Gas consumption over time
   - Token bucket levels
   - Central Bank balance sheet

2. **Value Tensor**
   - Multi-dimensional value breakdown (Physical, Semantic, Economic, Ethical)
   - Exchange rates between dimensions
   - Conservation law violations (anomalies)

3. **VoI (Value of Information)**
   - Observation cost vs. information gained
   - Epistemic capital accumulation
   - Signal-to-noise ratio

4. **Return on Compute (RoC)**
   - Value generated per token spent
   - Historical RoC trends
   - Threshold alerts

Wire Protocol Integration:
    The dashboard uses WireObservable to emit state updates that can be
    rendered by any fidelity adapter (Teletype, Documentarian, LiveWire).

Example:
    >>> from agents.w import ValueDashboard
    >>> from agents.b import CentralBank, VoILedger
    >>>
    >>> # Create dashboard observing B-gent systems
    >>> dashboard = ValueDashboard(
    ...     bank=CentralBank(),
    ...     voi_ledger=VoILedger(),
    ... )
    >>>
    >>> # Start serving dashboard
    >>> await dashboard.serve(port=8001)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Import W-gent wire protocol
from .protocol import WireObservable, WireState

# Import B-gent value accounting (optional - graceful degradation)
try:
    from agents.b.metered_functor import CentralBank, DualBudget, EntropyBudget, Gas
    from agents.b.value_ledger import BalanceSheet, RoCMonitor, ValueLedger
    from agents.b.value_tensor import (
        Anomaly,
        AntiDelusionChecker,
        TensorAlgebra,
        ValueTensor,
    )
    from agents.b.voi_economics import AdaptiveObserver, EpistemicCapital, VoILedger

    HAS_BGENT = True
except ImportError:
    HAS_BGENT = False


class DashboardPanel(Enum):
    """Available dashboard panels."""

    TOKEN_ECONOMICS = "token_economics"
    VALUE_TENSOR = "value_tensor"
    VOI_METRICS = "voi_metrics"
    ROC_MONITOR = "roc_monitor"
    ANOMALY_ALERTS = "anomaly_alerts"
    SYSTEM_HEALTH = "system_health"


@dataclass
class TokenSnapshot:
    """Point-in-time snapshot of token economics."""

    timestamp: datetime
    gas_available: int
    gas_consumed: int
    bucket_level: float
    bucket_capacity: float
    sinking_fund: float
    outstanding_futures: int


@dataclass
class TensorSnapshot:
    """Point-in-time snapshot of value tensor state."""

    timestamp: datetime
    physical: float
    semantic: float
    economic: float
    ethical: float
    total_value: float
    anomaly_count: int


@dataclass
class VoISnapshot:
    """Point-in-time snapshot of VoI metrics."""

    timestamp: datetime
    observations: int
    anomalies_detected: int
    confirmations: int
    false_positives: int
    epistemic_capital: float
    signal_to_noise: float
    rovi: float  # Return on Value of Information


@dataclass
class RoCSnapshot:
    """Point-in-time snapshot of Return on Compute."""

    timestamp: datetime
    total_value_generated: float
    total_gas_consumed: int
    current_roc: float
    trend: str  # "improving", "stable", "degrading"
    threshold_status: str  # "healthy", "warning", "critical"


@dataclass
class DashboardState:
    """Complete dashboard state for wire protocol emission."""

    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    panels_enabled: set[DashboardPanel] = field(default_factory=set)

    # Time series data (circular buffers)
    token_history: list[TokenSnapshot] = field(default_factory=list)
    tensor_history: list[TensorSnapshot] = field(default_factory=list)
    voi_history: list[VoISnapshot] = field(default_factory=list)
    roc_history: list[RoCSnapshot] = field(default_factory=list)

    # Current alerts
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Configuration
    history_limit: int = 100


class ValueDashboard(WireObservable):
    """
    Real-time dashboard for B-gent value economics visualization.

    Implements WireObservable to emit state through the wire protocol,
    allowing any W-gent fidelity adapter to render the data.
    """

    def __init__(
        self,
        agent_id: str = "value-dashboard",
        bank: Optional[Any] = None,
        value_ledger: Optional[Any] = None,
        voi_ledger: Optional[Any] = None,
        roc_monitor: Optional[Any] = None,
        anti_delusion: Optional[Any] = None,
        history_limit: int = 100,
        update_interval: float = 1.0,
    ):
        """
        Initialize Value Dashboard.

        Args:
            agent_id: Unique identifier for this dashboard
            bank: B-gent CentralBank instance
            value_ledger: B-gent ValueLedger instance
            voi_ledger: B-gent VoILedger instance
            roc_monitor: B-gent RoCMonitor instance
            anti_delusion: B-gent AntiDelusionChecker instance
            history_limit: Max history entries per metric
            update_interval: Seconds between updates
        """
        super().__init__(agent_id)

        self.bank = bank
        self.value_ledger = value_ledger
        self.voi_ledger = voi_ledger
        self.roc_monitor = roc_monitor
        self.anti_delusion = anti_delusion
        self.history_limit = history_limit
        self.update_interval = update_interval

        self._state = DashboardState(
            agent_id=agent_id,
            history_limit=history_limit,
        )

        # Enable panels based on available data sources
        self._detect_panels()

        self._running = False
        self._update_task: Optional[asyncio.Task] = None

    def _detect_panels(self) -> None:
        """Detect which panels to enable based on data sources."""
        if self.bank is not None:
            self._state.panels_enabled.add(DashboardPanel.TOKEN_ECONOMICS)

        if self.value_ledger is not None:
            self._state.panels_enabled.add(DashboardPanel.VALUE_TENSOR)

        if self.voi_ledger is not None:
            self._state.panels_enabled.add(DashboardPanel.VOI_METRICS)

        if self.roc_monitor is not None:
            self._state.panels_enabled.add(DashboardPanel.ROC_MONITOR)

        if self.anti_delusion is not None:
            self._state.panels_enabled.add(DashboardPanel.ANOMALY_ALERTS)

        # System health always available
        self._state.panels_enabled.add(DashboardPanel.SYSTEM_HEALTH)

    async def start(self) -> None:
        """Start the dashboard update loop."""
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        self.log_event("INFO", "start", "Value Dashboard started")

    async def stop(self) -> None:
        """Stop the dashboard update loop."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        self.log_event("INFO", "stop", "Value Dashboard stopped")

    async def _update_loop(self) -> None:
        """Main update loop - collects metrics and emits state."""
        while self._running:
            try:
                await self._collect_metrics()
                await self._emit_state()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_event("ERROR", "update", f"Update failed: {e}")
                await asyncio.sleep(self.update_interval)

    async def _collect_metrics(self) -> None:
        """Collect current metrics from all data sources."""
        now = datetime.now()

        # Token Economics
        if DashboardPanel.TOKEN_ECONOMICS in self._state.panels_enabled:
            snapshot = self._collect_token_snapshot(now)
            self._append_history(self._state.token_history, snapshot)

        # Value Tensor
        if DashboardPanel.VALUE_TENSOR in self._state.panels_enabled:
            snapshot = self._collect_tensor_snapshot(now)
            self._append_history(self._state.tensor_history, snapshot)

        # VoI Metrics
        if DashboardPanel.VOI_METRICS in self._state.panels_enabled:
            snapshot = self._collect_voi_snapshot(now)
            self._append_history(self._state.voi_history, snapshot)

        # RoC Monitor
        if DashboardPanel.ROC_MONITOR in self._state.panels_enabled:
            snapshot = self._collect_roc_snapshot(now)
            self._append_history(self._state.roc_history, snapshot)

        # Anomalies
        if DashboardPanel.ANOMALY_ALERTS in self._state.panels_enabled:
            self._collect_anomalies()

    def _collect_token_snapshot(self, now: datetime) -> TokenSnapshot:
        """Collect token economics snapshot."""
        if not HAS_BGENT or self.bank is None:
            return TokenSnapshot(
                timestamp=now,
                gas_available=0,
                gas_consumed=0,
                bucket_level=0.0,
                bucket_capacity=0.0,
                sinking_fund=0.0,
                outstanding_futures=0,
            )

        # Extract from CentralBank
        bank = self.bank
        return TokenSnapshot(
            timestamp=now,
            gas_available=getattr(bank, "gas_available", 0),
            gas_consumed=getattr(bank, "total_consumed", 0),
            bucket_level=getattr(bank, "bucket_level", 0.0),
            bucket_capacity=getattr(bank, "bucket_capacity", 1.0),
            sinking_fund=getattr(bank, "sinking_fund_balance", 0.0),
            outstanding_futures=len(getattr(bank, "pending_futures", [])),
        )

    def _collect_tensor_snapshot(self, now: datetime) -> TensorSnapshot:
        """Collect value tensor snapshot."""
        if not HAS_BGENT or self.value_ledger is None:
            return TensorSnapshot(
                timestamp=now,
                physical=0.0,
                semantic=0.0,
                economic=0.0,
                ethical=0.0,
                total_value=0.0,
                anomaly_count=0,
            )

        # Extract from ValueLedger
        ledger = self.value_ledger
        balance = getattr(ledger, "current_balance", None)

        if balance and hasattr(balance, "tensor"):
            tensor = balance.tensor
            return TensorSnapshot(
                timestamp=now,
                physical=getattr(tensor, "physical", 0.0),
                semantic=getattr(tensor, "semantic", 0.0),
                economic=getattr(tensor, "economic", 0.0),
                ethical=getattr(tensor, "ethical", 0.0),
                total_value=getattr(tensor, "total_magnitude", 0.0),
                anomaly_count=len(self._state.anomalies),
            )

        return TensorSnapshot(
            timestamp=now,
            physical=0.0,
            semantic=0.0,
            economic=0.0,
            ethical=0.0,
            total_value=0.0,
            anomaly_count=0,
        )

    def _collect_voi_snapshot(self, now: datetime) -> VoISnapshot:
        """Collect VoI metrics snapshot."""
        if not HAS_BGENT or self.voi_ledger is None:
            return VoISnapshot(
                timestamp=now,
                observations=0,
                anomalies_detected=0,
                confirmations=0,
                false_positives=0,
                epistemic_capital=0.0,
                signal_to_noise=0.0,
                rovi=0.0,
            )

        # Extract from VoILedger
        ledger = self.voi_ledger
        capital = getattr(ledger, "epistemic_capital", None)

        if capital and isinstance(capital, dict):
            return VoISnapshot(
                timestamp=now,
                observations=capital.get("observations", 0),
                anomalies_detected=capital.get("anomalies_detected", 0),
                confirmations=capital.get("confirmations", 0),
                false_positives=capital.get("false_positives", 0),
                epistemic_capital=capital.get("net_epistemic_value", 0.0),
                signal_to_noise=capital.get("signal_to_noise_ratio", 0.0),
                rovi=capital.get("rovi", 0.0),
            )

        return VoISnapshot(
            timestamp=now,
            observations=0,
            anomalies_detected=0,
            confirmations=0,
            false_positives=0,
            epistemic_capital=0.0,
            signal_to_noise=0.0,
            rovi=0.0,
        )

    def _collect_roc_snapshot(self, now: datetime) -> RoCSnapshot:
        """Collect Return on Compute snapshot."""
        if not HAS_BGENT or self.roc_monitor is None:
            return RoCSnapshot(
                timestamp=now,
                total_value_generated=0.0,
                total_gas_consumed=0,
                current_roc=0.0,
                trend="stable",
                threshold_status="healthy",
            )

        # Extract from RoCMonitor
        monitor = self.roc_monitor
        assessment = getattr(monitor, "current_assessment", None)

        if assessment:
            return RoCSnapshot(
                timestamp=now,
                total_value_generated=getattr(assessment, "total_value", 0.0),
                total_gas_consumed=getattr(assessment, "total_gas", 0),
                current_roc=getattr(assessment, "current_roc", 0.0),
                trend=getattr(assessment, "trend", "stable"),
                threshold_status=getattr(assessment, "status", "healthy"),
            )

        return RoCSnapshot(
            timestamp=now,
            total_value_generated=0.0,
            total_gas_consumed=0,
            current_roc=0.0,
            trend="stable",
            threshold_status="healthy",
        )

    def _collect_anomalies(self) -> None:
        """Collect anomalies from anti-delusion checker."""
        if not HAS_BGENT or self.anti_delusion is None:
            return

        checker = self.anti_delusion
        anomalies = getattr(checker, "recent_anomalies", [])

        self._state.anomalies = [
            {
                "type": getattr(a, "anomaly_type", "unknown"),
                "severity": getattr(a, "severity", "low"),
                "message": getattr(a, "message", ""),
                "timestamp": getattr(a, "timestamp", datetime.now()).isoformat(),
            }
            for a in anomalies[-10:]  # Last 10 anomalies
        ]

    def _append_history(self, history: list[Any], snapshot: Any) -> None:
        """Append to history with circular buffer semantics."""
        history.append(snapshot)
        while len(history) > self.history_limit:
            history.pop(0)

    async def _emit_state(self) -> None:
        """Emit current state through wire protocol."""
        self._state.timestamp = datetime.now()

        # Convert to WireState format
        WireState(
            agent_id=self._state.agent_id,
            phase="observing",
            data=self._to_wire_data(),
            timestamp=self._state.timestamp,
        )

        # Use WireObservable's update_state
        self.update_state(
            phase="observing",
            panels=[p.value for p in self._state.panels_enabled],
            token_current=self._state.token_history[-1].__dict__
            if self._state.token_history
            else {},
            tensor_current=self._state.tensor_history[-1].__dict__
            if self._state.tensor_history
            else {},
            voi_current=self._state.voi_history[-1].__dict__
            if self._state.voi_history
            else {},
            roc_current=self._state.roc_history[-1].__dict__
            if self._state.roc_history
            else {},
            anomaly_count=len(self._state.anomalies),
            warning_count=len(self._state.warnings),
        )

    def _to_wire_data(self) -> dict[str, Any]:
        """Convert dashboard state to wire protocol data format."""
        return {
            "panels": [p.value for p in self._state.panels_enabled],
            "token_economics": {
                "current": self._state.token_history[-1].__dict__
                if self._state.token_history
                else None,
                "history_length": len(self._state.token_history),
            },
            "value_tensor": {
                "current": self._state.tensor_history[-1].__dict__
                if self._state.tensor_history
                else None,
                "history_length": len(self._state.tensor_history),
            },
            "voi_metrics": {
                "current": self._state.voi_history[-1].__dict__
                if self._state.voi_history
                else None,
                "history_length": len(self._state.voi_history),
            },
            "roc_monitor": {
                "current": self._state.roc_history[-1].__dict__
                if self._state.roc_history
                else None,
                "history_length": len(self._state.roc_history),
            },
            "anomalies": self._state.anomalies,
            "warnings": self._state.warnings,
        }

    # --- Query Methods ---

    def get_token_history(self, limit: int = 50) -> list[TokenSnapshot]:
        """Get token economics history."""
        return self._state.token_history[-limit:]

    def get_tensor_history(self, limit: int = 50) -> list[TensorSnapshot]:
        """Get value tensor history."""
        return self._state.tensor_history[-limit:]

    def get_voi_history(self, limit: int = 50) -> list[VoISnapshot]:
        """Get VoI metrics history."""
        return self._state.voi_history[-limit:]

    def get_roc_history(self, limit: int = 50) -> list[RoCSnapshot]:
        """Get RoC monitor history."""
        return self._state.roc_history[-limit:]

    def get_current_state(self) -> dict[str, Any]:
        """Get complete current dashboard state."""
        return self._to_wire_data()

    def get_summary(self) -> str:
        """Get human-readable summary of current state."""
        lines = [
            f"=== Value Dashboard: {self._state.agent_id} ===",
            f"Timestamp: {self._state.timestamp.isoformat()}",
            f"Active Panels: {', '.join(p.value for p in self._state.panels_enabled)}",
            "",
        ]

        if self._state.token_history:
            t = self._state.token_history[-1]
            lines.extend(
                [
                    "Token Economics:",
                    f"  Gas: {t.gas_available:,} available, {t.gas_consumed:,} consumed",
                    f"  Bucket: {t.bucket_level:.1%} of {t.bucket_capacity:,}",
                    "",
                ]
            )

        if self._state.tensor_history:
            v = self._state.tensor_history[-1]
            lines.extend(
                [
                    "Value Tensor:",
                    f"  Physical: {v.physical:.2f}",
                    f"  Semantic: {v.semantic:.2f}",
                    f"  Economic: {v.economic:.2f}",
                    f"  Ethical:  {v.ethical:.2f}",
                    f"  Total:    {v.total_value:.2f}",
                    "",
                ]
            )

        if self._state.voi_history:
            i = self._state.voi_history[-1]
            lines.extend(
                [
                    "VoI Metrics:",
                    f"  Observations: {i.observations}",
                    f"  Anomalies: {i.anomalies_detected}",
                    f"  Signal/Noise: {i.signal_to_noise:.2f}",
                    f"  RoVI: {i.rovi:.3f}",
                    "",
                ]
            )

        if self._state.roc_history:
            r = self._state.roc_history[-1]
            lines.extend(
                [
                    "Return on Compute:",
                    f"  Value Generated: {r.total_value_generated:.2f}",
                    f"  Gas Consumed: {r.total_gas_consumed:,}",
                    f"  Current RoC: {r.current_roc:.4f}",
                    f"  Trend: {r.trend}",
                    f"  Status: {r.threshold_status}",
                    "",
                ]
            )

        if self._state.anomalies:
            lines.extend(
                [
                    f"Anomalies ({len(self._state.anomalies)}):",
                ]
            )
            for a in self._state.anomalies[:5]:
                lines.append(f"  [{a['severity']}] {a['type']}: {a['message']}")

        return "\n".join(lines)


# --- Factory Functions ---


def create_value_dashboard(
    agent_id: str = "value-dashboard",
    **kwargs: Any,
) -> ValueDashboard:
    """
    Create a Value Dashboard instance.

    Args:
        agent_id: Unique identifier for this dashboard
        **kwargs: Data sources (bank, value_ledger, voi_ledger, etc.)

    Returns:
        Configured ValueDashboard
    """
    return ValueDashboard(agent_id=agent_id, **kwargs)


def create_minimal_dashboard(agent_id: str = "minimal-dashboard") -> ValueDashboard:
    """
    Create a minimal dashboard without any data sources.

    Useful for testing or manual metric injection.
    """
    return ValueDashboard(agent_id=agent_id)
