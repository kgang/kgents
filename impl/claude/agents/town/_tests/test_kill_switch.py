"""
Tests for kill-switch monitoring and alert conditions.

Covers:
- Metric calculation (CAC/LTV, churn, conversion, etc.)
- Threshold monitoring
- Alert generation
- Operational safety checks
"""

import pytest
from agents.town.kill_switch import (
    AlertSeverity,
    KillSwitchMonitor,
    KillSwitchType,
    MetricCalculator,
)

# =============================================================================
# Metric Calculator Tests
# =============================================================================


def test_metric_calculator_cac_ltv_ratio():
    """Test CAC/LTV ratio calculation."""
    calc = MetricCalculator()

    # Conservative scenario: CAC $10, LTV $75 → ratio 0.133 (good)
    metric = calc.calculate_cac_ltv_ratio(total_cac=10.0, total_ltv=75.0)

    assert metric.metric_type == KillSwitchType.CAC_LTV_RATIO
    assert metric.value == pytest.approx(0.133, abs=0.01)


def test_metric_calculator_cac_ltv_ratio_breach():
    """Test CAC/LTV ratio breach (bad economics)."""
    calc = MetricCalculator()

    # Bad: CAC $25, LTV $75 → ratio 0.333 (above 30% threshold)
    metric = calc.calculate_cac_ltv_ratio(total_cac=25.0, total_ltv=75.0)

    assert metric.value > 0.30


def test_metric_calculator_m1_churn():
    """Test month 1 churn rate calculation."""
    calc = MetricCalculator()

    # 20 churned out of 100 new users → 20%
    metric = calc.calculate_m1_churn(churned_users=20, total_new_users=100)

    assert metric.metric_type == KillSwitchType.M1_CHURN
    assert metric.value == 0.20


def test_metric_calculator_conversion_rate():
    """Test conversion rate calculation."""
    calc = MetricCalculator()

    # 8 paid out of 100 total → 8%
    metric = calc.calculate_conversion_rate(paid_users=8, total_users=100)

    assert metric.metric_type == KillSwitchType.CONVERSION_RATE
    assert metric.value == 0.08


def test_metric_calculator_conversion_rate_low():
    """Test low conversion rate (below threshold)."""
    calc = MetricCalculator()

    # 2 paid out of 100 → 2% (below 3% threshold)
    metric = calc.calculate_conversion_rate(paid_users=2, total_users=100)

    assert metric.value < 0.03


def test_metric_calculator_lod_unlock_rate():
    """Test LOD unlock rate calculation."""
    calc = MetricCalculator()

    # 10 users unlocking LOD 3+ out of 100 → 10%
    metric = calc.calculate_lod_unlock_rate(users_unlocking_lod=10, total_users=100)

    assert metric.metric_type == KillSwitchType.LOD_UNLOCK_RATE
    assert metric.value == 0.10


def test_metric_calculator_force_rate():
    """Test force mechanic usage rate."""
    calc = MetricCalculator()

    # 40 sessions with force out of 100 INHABIT sessions → 40%
    metric = calc.calculate_force_rate(
        sessions_with_force=40, total_inhabit_sessions=100
    )

    assert metric.metric_type == KillSwitchType.FORCE_RATE
    assert metric.value == 0.40


def test_metric_calculator_force_rate_high():
    """Test high force rate (ethics concern)."""
    calc = MetricCalculator()

    # 35 out of 100 → 35% (above 30% threshold)
    metric = calc.calculate_force_rate(
        sessions_with_force=35, total_inhabit_sessions=100
    )

    assert metric.value > 0.30


def test_metric_calculator_get_latest_metric():
    """Test retrieving latest metric."""
    calc = MetricCalculator()

    calc.calculate_conversion_rate(5, 100)
    calc.calculate_conversion_rate(8, 100)  # Latest

    latest = calc.get_latest_metric(KillSwitchType.CONVERSION_RATE)

    assert latest is not None
    assert latest.value == 0.08


# =============================================================================
# Kill-Switch Monitor Tests
# =============================================================================


def test_kill_switch_monitor_check_metric_pass():
    """Test metric check passes when within threshold."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Good CAC/LTV ratio: 0.13 (below 0.30)
    metric = calc.calculate_cac_ltv_ratio(10.0, 75.0)

    alert = monitor.check_metric(metric)

    assert alert is None  # No alert


def test_kill_switch_monitor_check_metric_breach():
    """Test metric check generates alert when threshold breached."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Bad CAC/LTV ratio: 0.40 (above 0.30 threshold)
    metric = calc.calculate_cac_ltv_ratio(30.0, 75.0)

    alert = monitor.check_metric(metric)

    assert alert is not None
    assert alert.condition.type == KillSwitchType.CAC_LTV_RATIO
    assert alert.condition.severity == AlertSeverity.KILL_SWITCH
    assert "halt_paid_acquisition" in alert.condition.action


def test_kill_switch_monitor_m1_churn_breach():
    """Test M1 churn breach generates critical alert."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # 30% churn (above 25% threshold)
    metric = calc.calculate_m1_churn(30, 100)

    alert = monitor.check_metric(metric)

    assert alert is not None
    assert alert.condition.type == KillSwitchType.M1_CHURN
    assert alert.condition.severity == AlertSeverity.CRITICAL


def test_kill_switch_monitor_conversion_rate_breach():
    """Test low conversion rate breach."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # 2% conversion (below 3% threshold)
    metric = calc.calculate_conversion_rate(2, 100)

    alert = monitor.check_metric(metric)

    assert alert is not None
    assert alert.condition.type == KillSwitchType.CONVERSION_RATE


def test_kill_switch_monitor_force_rate_breach():
    """Test high force rate breach (ethics concern)."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # 40% force rate (above 30% threshold)
    metric = calc.calculate_force_rate(40, 100)

    alert = monitor.check_metric(metric)

    assert alert is not None
    assert alert.condition.type == KillSwitchType.FORCE_RATE
    assert "ethics_review" in alert.condition.action


def test_kill_switch_monitor_get_active_alerts():
    """Test retrieving active alerts."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Generate multiple alerts
    metric1 = calc.calculate_cac_ltv_ratio(30.0, 75.0)  # Breach
    metric2 = calc.calculate_m1_churn(30, 100)  # Breach

    monitor.check_metric(metric1)
    monitor.check_metric(metric2)

    active = monitor.get_active_alerts()

    assert len(active) == 2


def test_kill_switch_monitor_acknowledge_alert():
    """Test acknowledging alerts."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    metric = calc.calculate_cac_ltv_ratio(30.0, 75.0)
    alert = monitor.check_metric(metric)

    assert alert is not None
    assert not alert.acknowledged

    monitor.acknowledge_alert(alert)

    assert alert.acknowledged

    # Should not appear in active alerts
    active = monitor.get_active_alerts()
    assert len(active) == 0


def test_kill_switch_monitor_is_safe_to_operate():
    """Test operational safety check."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Initially safe
    assert monitor.is_safe_to_operate()

    # Trigger KILL_SWITCH severity alert
    metric = calc.calculate_cac_ltv_ratio(30.0, 75.0)
    monitor.check_metric(metric)

    # Now unsafe
    assert not monitor.is_safe_to_operate()


def test_kill_switch_monitor_safe_after_acknowledge():
    """Test system becomes safe after acknowledging kill-switch."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Trigger kill-switch
    metric = calc.calculate_cac_ltv_ratio(30.0, 75.0)
    alert = monitor.check_metric(metric)

    assert not monitor.is_safe_to_operate()

    # Acknowledge
    assert alert is not None
    monitor.acknowledge_alert(alert)

    # Safe again
    assert monitor.is_safe_to_operate()


def test_kill_switch_monitor_status_report():
    """Test status report generation."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Trigger various alerts
    monitor.check_metric(calc.calculate_cac_ltv_ratio(30.0, 75.0))  # KILL_SWITCH
    monitor.check_metric(calc.calculate_m1_churn(30, 100))  # CRITICAL

    status = monitor.get_status_report()

    assert not status["safe_to_operate"]
    assert status["active_alerts"] == 2
    assert status["kill_switch_alerts"] == 1
    assert status["critical_alerts"] == 1
    assert status["total_alerts"] == 2


def test_kill_switch_monitor_filter_by_severity():
    """Test filtering alerts by severity."""
    monitor = KillSwitchMonitor()
    calc = MetricCalculator()

    # Generate alerts of different severities
    monitor.check_metric(calc.calculate_cac_ltv_ratio(30.0, 75.0))  # KILL_SWITCH
    monitor.check_metric(calc.calculate_lod_unlock_rate(2, 100))  # WARNING

    kill_switch_alerts = monitor.get_active_alerts(AlertSeverity.KILL_SWITCH)
    warning_alerts = monitor.get_active_alerts(AlertSeverity.WARNING)

    assert len(kill_switch_alerts) == 1
    assert len(warning_alerts) == 1


# =============================================================================
# Edge Cases
# =============================================================================


def test_metric_calculator_zero_denominator():
    """Test metric calculation with zero denominator."""
    calc = MetricCalculator()

    # Zero LTV
    metric = calc.calculate_cac_ltv_ratio(10.0, 0.0)

    assert metric.value == 999.0  # Infinite ratio (very bad)


def test_metric_calculator_zero_users():
    """Test metrics with zero users."""
    calc = MetricCalculator()

    metric = calc.calculate_conversion_rate(0, 0)

    assert metric.value == 0.0
