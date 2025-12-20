"""
Kill-switch monitoring and alert conditions for Agent Town.

Per unified-v2.md §5: Automated safety thresholds to halt operations
if unit economics or ethics metrics breach acceptable levels.

Kill-switch conditions:
1. CAC > 30% LTV - halt paid acquisition
2. M1 churn > 25% - emergency retention analysis
3. Conversion < 3% - pause monetization
4. LOD unlock rate < 5% - revisit paywall UX
5. Force rate > 30% of sessions - ethics review

This module provides:
- Metric collection and aggregation
- Threshold monitoring
- Alert generation
- Safe operational state checks
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Kill-Switch Conditions
# =============================================================================


class KillSwitchType(str, Enum):
    """Types of kill-switch conditions."""

    CAC_LTV_RATIO = "cac_ltv_ratio"  # Customer Acquisition Cost vs Lifetime Value
    M1_CHURN = "m1_churn"  # Month 1 churn rate
    CONVERSION_RATE = "conversion_rate"  # Free to paid conversion
    LOD_UNLOCK_RATE = "lod_unlock_rate"  # Users unlocking LOD 3+
    FORCE_RATE = "force_rate"  # Sessions using force mechanic


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    KILL_SWITCH = "kill_switch"  # Automated halt


@dataclass
class KillSwitchCondition:
    """Definition of a kill-switch threshold."""

    type: KillSwitchType
    threshold: float
    comparison: str  # "gt" (greater than), "lt" (less than)
    action: str  # Action to take if breached
    severity: AlertSeverity
    enabled: bool = True


# Kill-switch thresholds per unified-v2.md §5
KILL_SWITCH_CONDITIONS = [
    KillSwitchCondition(
        type=KillSwitchType.CAC_LTV_RATIO,
        threshold=0.30,  # CAC > 30% LTV
        comparison="gt",
        action="halt_paid_acquisition",
        severity=AlertSeverity.KILL_SWITCH,
    ),
    KillSwitchCondition(
        type=KillSwitchType.M1_CHURN,
        threshold=0.25,  # >25% churn in month 1
        comparison="gt",
        action="emergency_retention_review",
        severity=AlertSeverity.CRITICAL,
    ),
    KillSwitchCondition(
        type=KillSwitchType.CONVERSION_RATE,
        threshold=0.03,  # <3% conversion
        comparison="lt",
        action="pause_monetization",
        severity=AlertSeverity.CRITICAL,
    ),
    KillSwitchCondition(
        type=KillSwitchType.LOD_UNLOCK_RATE,
        threshold=0.05,  # <5% unlocking LOD
        comparison="lt",
        action="revisit_paywall_ux",
        severity=AlertSeverity.WARNING,
    ),
    KillSwitchCondition(
        type=KillSwitchType.FORCE_RATE,
        threshold=0.30,  # >30% sessions use force
        comparison="gt",
        action="ethics_review",
        severity=AlertSeverity.CRITICAL,
    ),
]


# =============================================================================
# Metrics Tracking
# =============================================================================


@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a point in time."""

    metric_type: KillSwitchType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KillSwitchAlert:
    """Alert generated when threshold is breached."""

    condition: KillSwitchCondition
    metric: MetricSnapshot
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


# =============================================================================
# Metric Calculator
# =============================================================================


class MetricCalculator:
    """
    Calculates business and ethics metrics for kill-switch monitoring.

    In production, this would integrate with analytics backend (e.g., PostHog, Mixpanel).
    For now, provides interface for manual metric input and calculation.
    """

    def __init__(self) -> None:
        """Initialize metric calculator."""
        self._snapshots: list[MetricSnapshot] = []

    def record_metric(
        self,
        metric_type: KillSwitchType,
        value: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a metric snapshot.

        Args:
            metric_type: Type of metric
            value: Metric value
            metadata: Additional context
        """
        snapshot = MetricSnapshot(
            metric_type=metric_type,
            value=value,
            metadata=metadata or {},
        )
        self._snapshots.append(snapshot)
        logger.info(f"Recorded metric {metric_type.value} = {value}")

    def calculate_cac_ltv_ratio(self, total_cac: float, total_ltv: float) -> MetricSnapshot:
        """
        Calculate CAC/LTV ratio.

        Per unified-v2.md §5: Conservative LTV = $75, target CAC < $22.50

        Args:
            total_cac: Total customer acquisition cost
            total_ltv: Total lifetime value

        Returns:
            MetricSnapshot with ratio
        """
        if total_ltv == 0:
            ratio = 999.0  # Infinite ratio (bad)
        else:
            ratio = total_cac / total_ltv

        snapshot = MetricSnapshot(
            metric_type=KillSwitchType.CAC_LTV_RATIO,
            value=ratio,
            metadata={
                "total_cac": total_cac,
                "total_ltv": total_ltv,
            },
        )

        self._snapshots.append(snapshot)
        return snapshot

    def calculate_m1_churn(self, churned_users: int, total_new_users: int) -> MetricSnapshot:
        """
        Calculate month 1 churn rate.

        Args:
            churned_users: Users who churned in first month
            total_new_users: Total users acquired this month

        Returns:
            MetricSnapshot with churn rate
        """
        if total_new_users == 0:
            rate = 0.0
        else:
            rate = churned_users / total_new_users

        snapshot = MetricSnapshot(
            metric_type=KillSwitchType.M1_CHURN,
            value=rate,
            metadata={
                "churned_users": churned_users,
                "total_new_users": total_new_users,
            },
        )

        self._snapshots.append(snapshot)
        return snapshot

    def calculate_conversion_rate(self, paid_users: int, total_users: int) -> MetricSnapshot:
        """
        Calculate free-to-paid conversion rate.

        Args:
            paid_users: Users who converted to paid
            total_users: Total users (free + paid)

        Returns:
            MetricSnapshot with conversion rate
        """
        if total_users == 0:
            rate = 0.0
        else:
            rate = paid_users / total_users

        snapshot = MetricSnapshot(
            metric_type=KillSwitchType.CONVERSION_RATE,
            value=rate,
            metadata={
                "paid_users": paid_users,
                "total_users": total_users,
            },
        )

        self._snapshots.append(snapshot)
        return snapshot

    def calculate_lod_unlock_rate(
        self, users_unlocking_lod: int, total_users: int
    ) -> MetricSnapshot:
        """
        Calculate rate of users unlocking LOD 3+.

        Args:
            users_unlocking_lod: Users who unlocked LOD 3, 4, or 5
            total_users: Total active users

        Returns:
            MetricSnapshot with unlock rate
        """
        if total_users == 0:
            rate = 0.0
        else:
            rate = users_unlocking_lod / total_users

        snapshot = MetricSnapshot(
            metric_type=KillSwitchType.LOD_UNLOCK_RATE,
            value=rate,
            metadata={
                "users_unlocking_lod": users_unlocking_lod,
                "total_users": total_users,
            },
        )

        self._snapshots.append(snapshot)
        return snapshot

    def calculate_force_rate(
        self, sessions_with_force: int, total_inhabit_sessions: int
    ) -> MetricSnapshot:
        """
        Calculate rate of INHABIT sessions using force mechanic.

        Per unified-v2.md §5: Alert if >30% of sessions use force (ethics concern)

        Args:
            sessions_with_force: Sessions where force was used
            total_inhabit_sessions: Total INHABIT sessions

        Returns:
            MetricSnapshot with force rate
        """
        if total_inhabit_sessions == 0:
            rate = 0.0
        else:
            rate = sessions_with_force / total_inhabit_sessions

        snapshot = MetricSnapshot(
            metric_type=KillSwitchType.FORCE_RATE,
            value=rate,
            metadata={
                "sessions_with_force": sessions_with_force,
                "total_inhabit_sessions": total_inhabit_sessions,
            },
        )

        self._snapshots.append(snapshot)
        return snapshot

    def get_latest_metric(self, metric_type: KillSwitchType) -> MetricSnapshot | None:
        """Get most recent snapshot for a metric type."""
        snapshots = [s for s in self._snapshots if s.metric_type == metric_type]
        if not snapshots:
            return None
        return max(snapshots, key=lambda s: s.timestamp)

    def get_metrics_since(
        self, since: datetime, metric_type: KillSwitchType | None = None
    ) -> list[MetricSnapshot]:
        """Get metrics recorded since a timestamp."""
        snapshots = [s for s in self._snapshots if s.timestamp >= since]
        if metric_type:
            snapshots = [s for s in snapshots if s.metric_type == metric_type]
        return snapshots


# =============================================================================
# Kill-Switch Monitor
# =============================================================================


class KillSwitchMonitor:
    """
    Monitors metrics against kill-switch conditions.

    Generates alerts when thresholds are breached.
    """

    def __init__(self, conditions: list[KillSwitchCondition] | None = None) -> None:
        """
        Initialize monitor.

        Args:
            conditions: List of conditions to monitor (defaults to KILL_SWITCH_CONDITIONS)
        """
        self.conditions = conditions or KILL_SWITCH_CONDITIONS
        self.alerts: list[KillSwitchAlert] = []

    def check_metric(self, metric: MetricSnapshot) -> KillSwitchAlert | None:
        """
        Check a metric against all relevant conditions.

        Args:
            metric: Metric snapshot to check

        Returns:
            KillSwitchAlert if threshold breached, None otherwise
        """
        for condition in self.conditions:
            if not condition.enabled:
                continue

            if condition.type != metric.metric_type:
                continue

            # Check threshold
            breached = False
            if condition.comparison == "gt":
                breached = metric.value > condition.threshold
            elif condition.comparison == "lt":
                breached = metric.value < condition.threshold

            if breached:
                alert = KillSwitchAlert(
                    condition=condition,
                    metric=metric,
                    message=self._generate_alert_message(condition, metric),
                )
                self.alerts.append(alert)
                logger.warning(f"KILL-SWITCH ALERT: {alert.message}")
                return alert

        return None

    def _generate_alert_message(
        self, condition: KillSwitchCondition, metric: MetricSnapshot
    ) -> str:
        """Generate human-readable alert message."""
        comparison_text = "above" if condition.comparison == "gt" else "below"
        return (
            f"{condition.type.value} is {comparison_text} threshold: "
            f"{metric.value:.2%} vs {condition.threshold:.2%}. "
            f"Action required: {condition.action}"
        )

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[KillSwitchAlert]:
        """Get unacknowledged alerts, optionally filtered by severity."""
        alerts = [a for a in self.alerts if not a.acknowledged]
        if severity:
            alerts = [a for a in alerts if a.condition.severity == severity]
        return alerts

    def acknowledge_alert(self, alert: KillSwitchAlert) -> None:
        """Mark an alert as acknowledged."""
        alert.acknowledged = True
        logger.info(f"Alert acknowledged: {alert.condition.type.value}")

    def is_safe_to_operate(self) -> bool:
        """
        Check if it's safe to continue operations.

        Returns False if any KILL_SWITCH severity alerts are active.
        """
        kill_switch_alerts = self.get_active_alerts(AlertSeverity.KILL_SWITCH)
        return len(kill_switch_alerts) == 0

    def get_status_report(self) -> dict[str, Any]:
        """Generate status report of all conditions."""
        return {
            "safe_to_operate": self.is_safe_to_operate(),
            "active_alerts": len(self.get_active_alerts()),
            "kill_switch_alerts": len(self.get_active_alerts(AlertSeverity.KILL_SWITCH)),
            "critical_alerts": len(self.get_active_alerts(AlertSeverity.CRITICAL)),
            "warning_alerts": len(self.get_active_alerts(AlertSeverity.WARNING)),
            "total_alerts": len(self.alerts),
            "conditions_monitored": len(self.conditions),
        }


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "AlertSeverity",
    "KillSwitchAlert",
    "KillSwitchCondition",
    "KillSwitchMonitor",
    "KillSwitchType",
    "KILL_SWITCH_CONDITIONS",
    "MetricCalculator",
    "MetricSnapshot",
]
