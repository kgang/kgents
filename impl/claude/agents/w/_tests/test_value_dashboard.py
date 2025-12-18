"""
Tests for W-gent Value Dashboard.

Tests:
- Dashboard creation and panel detection
- Snapshot collection
- History management
- Wire protocol integration
- Summary generation
"""

from datetime import datetime

import pytest

from agents.w.value_dashboard import (
    DashboardPanel,
    DashboardState,
    RoCSnapshot,
    TensorSnapshot,
    TokenSnapshot,
    VoISnapshot,
    create_minimal_dashboard,
    create_value_dashboard,
)

# =============================================================================
# Snapshot Tests
# =============================================================================


class TestTokenSnapshot:
    """Tests for TokenSnapshot."""

    def test_creation(self) -> None:
        """TokenSnapshot can be created."""
        now = datetime.now()
        snap = TokenSnapshot(
            timestamp=now,
            gas_available=1000,
            gas_consumed=500,
            bucket_level=0.75,
            bucket_capacity=10000.0,
            sinking_fund=100.0,
            outstanding_futures=3,
        )

        assert snap.gas_available == 1000
        assert snap.gas_consumed == 500
        assert snap.bucket_level == 0.75
        assert snap.outstanding_futures == 3


class TestTensorSnapshot:
    """Tests for TensorSnapshot."""

    def test_creation(self) -> None:
        """TensorSnapshot can be created."""
        now = datetime.now()
        snap = TensorSnapshot(
            timestamp=now,
            physical=100.0,
            semantic=50.0,
            economic=75.0,
            ethical=25.0,
            total_value=250.0,
            anomaly_count=0,
        )

        assert snap.physical == 100.0
        assert snap.semantic == 50.0
        assert snap.total_value == 250.0


class TestVoISnapshot:
    """Tests for VoISnapshot."""

    def test_creation(self) -> None:
        """VoISnapshot can be created."""
        now = datetime.now()
        snap = VoISnapshot(
            timestamp=now,
            observations=100,
            anomalies_detected=5,
            confirmations=80,
            false_positives=15,
            epistemic_capital=85.0,
            signal_to_noise=5.67,
            rovi=1.2,
        )

        assert snap.observations == 100
        assert snap.anomalies_detected == 5
        assert snap.signal_to_noise == 5.67
        assert snap.rovi == 1.2


class TestRoCSnapshot:
    """Tests for RoCSnapshot."""

    def test_creation(self) -> None:
        """RoCSnapshot can be created."""
        now = datetime.now()
        snap = RoCSnapshot(
            timestamp=now,
            total_value_generated=1000.0,
            total_gas_consumed=5000,
            current_roc=0.2,
            trend="improving",
            threshold_status="healthy",
        )

        assert snap.total_value_generated == 1000.0
        assert snap.current_roc == 0.2
        assert snap.trend == "improving"


# =============================================================================
# DashboardState Tests
# =============================================================================


class TestDashboardState:
    """Tests for DashboardState."""

    def test_creation(self) -> None:
        """DashboardState can be created."""
        state = DashboardState(agent_id="test-dashboard")

        assert state.agent_id == "test-dashboard"
        assert len(state.panels_enabled) == 0
        assert len(state.token_history) == 0

    def test_history_limit(self) -> None:
        """DashboardState respects history limit."""
        state = DashboardState(
            agent_id="test-dashboard",
            history_limit=10,
        )

        assert state.history_limit == 10


class TestDashboardPanel:
    """Tests for DashboardPanel enum."""

    def test_all_panels_exist(self) -> None:
        """All expected panels exist."""
        assert DashboardPanel.TOKEN_ECONOMICS.value == "token_economics"
        assert DashboardPanel.VALUE_TENSOR.value == "value_tensor"
        assert DashboardPanel.VOI_METRICS.value == "voi_metrics"
        assert DashboardPanel.ROC_MONITOR.value == "roc_monitor"
        assert DashboardPanel.ANOMALY_ALERTS.value == "anomaly_alerts"
        assert DashboardPanel.SYSTEM_HEALTH.value == "system_health"


# =============================================================================
# ValueDashboard Tests
# =============================================================================


class TestValueDashboard:
    """Tests for ValueDashboard."""

    def test_create_minimal(self) -> None:
        """Minimal dashboard can be created."""
        dashboard = create_minimal_dashboard()

        assert dashboard is not None
        assert dashboard.bank is None
        assert dashboard.value_ledger is None

    def test_create_with_agent_id(self) -> None:
        """Dashboard can be created with custom agent_id."""
        dashboard = create_value_dashboard(agent_id="my-dashboard")

        assert dashboard._state.agent_id == "my-dashboard"

    def test_system_health_always_enabled(self) -> None:
        """System health panel is always enabled."""
        dashboard = create_minimal_dashboard()

        assert DashboardPanel.SYSTEM_HEALTH in dashboard._state.panels_enabled

    def test_panels_detected_from_sources(self) -> None:
        """Panels are detected based on data sources."""

        # Create mock bank
        class MockBank:
            pass

        dashboard = create_value_dashboard(bank=MockBank())

        assert DashboardPanel.TOKEN_ECONOMICS in dashboard._state.panels_enabled


class TestValueDashboardHistory:
    """Tests for history management."""

    def test_append_history_respects_limit(self) -> None:
        """History respects limit."""
        dashboard = create_minimal_dashboard()
        dashboard.history_limit = 5

        # Add 10 snapshots
        for i in range(10):
            snap = TokenSnapshot(
                timestamp=datetime.now(),
                gas_available=i * 100,
                gas_consumed=i * 50,
                bucket_level=0.5,
                bucket_capacity=1000.0,
                sinking_fund=0.0,
                outstanding_futures=0,
            )
            dashboard._append_history(dashboard._state.token_history, snap)

        # Should only have 5
        assert len(dashboard._state.token_history) == 5

        # Should have latest (oldest trimmed)
        assert dashboard._state.token_history[-1].gas_available == 900

    def test_get_token_history(self) -> None:
        """get_token_history returns history."""
        dashboard = create_minimal_dashboard()

        # Add snapshots
        for i in range(5):
            snap = TokenSnapshot(
                timestamp=datetime.now(),
                gas_available=i * 100,
                gas_consumed=0,
                bucket_level=0.5,
                bucket_capacity=1000.0,
                sinking_fund=0.0,
                outstanding_futures=0,
            )
            dashboard._state.token_history.append(snap)

        history = dashboard.get_token_history(limit=3)
        assert len(history) == 3


class TestValueDashboardSummary:
    """Tests for summary generation."""

    def test_get_summary_empty(self) -> None:
        """Summary works with no data."""
        dashboard = create_minimal_dashboard()

        summary = dashboard.get_summary()

        assert "Value Dashboard" in summary
        assert dashboard._state.agent_id in summary

    def test_get_summary_with_token_data(self) -> None:
        """Summary includes token data when available."""
        dashboard = create_minimal_dashboard()

        # Add token snapshot
        snap = TokenSnapshot(
            timestamp=datetime.now(),
            gas_available=1000,
            gas_consumed=500,
            bucket_level=0.75,
            bucket_capacity=10000.0,
            sinking_fund=100.0,
            outstanding_futures=3,
        )
        dashboard._state.token_history.append(snap)

        summary = dashboard.get_summary()

        assert "Token Economics" in summary
        assert "1,000" in summary  # gas_available

    def test_get_summary_with_voi_data(self) -> None:
        """Summary includes VoI data when available."""
        dashboard = create_minimal_dashboard()

        # Add VoI snapshot
        snap = VoISnapshot(
            timestamp=datetime.now(),
            observations=100,
            anomalies_detected=5,
            confirmations=80,
            false_positives=15,
            epistemic_capital=85.0,
            signal_to_noise=5.67,
            rovi=1.2,
        )
        dashboard._state.voi_history.append(snap)

        summary = dashboard.get_summary()

        assert "VoI Metrics" in summary
        assert "100" in summary  # observations


class TestValueDashboardState:
    """Tests for state management."""

    def test_get_current_state(self) -> None:
        """get_current_state returns wire data."""
        dashboard = create_minimal_dashboard()

        state = dashboard.get_current_state()

        assert "panels" in state
        assert "token_economics" in state
        assert "voi_metrics" in state
        assert "anomalies" in state

    def test_to_wire_data_format(self) -> None:
        """_to_wire_data produces correct format."""
        dashboard = create_minimal_dashboard()

        data = dashboard._to_wire_data()

        assert isinstance(data["panels"], list)
        assert isinstance(data["anomalies"], list)
        assert isinstance(data["warnings"], list)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_value_dashboard(self) -> None:
        """create_value_dashboard creates dashboard."""
        dashboard = create_value_dashboard(
            agent_id="factory-test",
            history_limit=50,
        )

        assert dashboard._state.agent_id == "factory-test"
        assert dashboard.history_limit == 50

    def test_create_minimal_dashboard(self) -> None:
        """create_minimal_dashboard creates minimal dashboard."""
        dashboard = create_minimal_dashboard("minimal-test")

        assert dashboard._state.agent_id == "minimal-test"
        assert dashboard.bank is None
        assert dashboard.voi_ledger is None


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_start_stop(self) -> None:
        """Dashboard can start and stop."""
        dashboard = create_minimal_dashboard()

        # Start
        await dashboard.start()
        assert dashboard._running is True

        # Stop
        await dashboard.stop()
        assert dashboard._running is False

    def test_collect_metrics_no_sources(self) -> None:
        """Collecting metrics with no sources produces empty snapshots."""
        dashboard = create_minimal_dashboard()

        # Manually collect (normally done in loop)
        now = datetime.now()
        token_snap = dashboard._collect_token_snapshot(now)

        assert token_snap.gas_available == 0
        assert token_snap.gas_consumed == 0

    def test_multiple_panels_enabled(self) -> None:
        """Multiple panels can be enabled."""

        # Create mock sources
        class MockBank:
            pass

        class MockVoILedger:
            pass

        dashboard = create_value_dashboard(
            bank=MockBank(),
            voi_ledger=MockVoILedger(),
        )

        assert DashboardPanel.TOKEN_ECONOMICS in dashboard._state.panels_enabled
        assert DashboardPanel.VOI_METRICS in dashboard._state.panels_enabled


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_history_limit(self) -> None:
        """History with limit 0 stays empty."""
        dashboard = create_minimal_dashboard()
        dashboard.history_limit = 0

        snap = TokenSnapshot(
            timestamp=datetime.now(),
            gas_available=100,
            gas_consumed=0,
            bucket_level=0.5,
            bucket_capacity=1000.0,
            sinking_fund=0.0,
            outstanding_futures=0,
        )

        dashboard._append_history(dashboard._state.token_history, snap)

        assert len(dashboard._state.token_history) == 0

    def test_large_history(self) -> None:
        """Large history is truncated correctly."""
        dashboard = create_minimal_dashboard()
        dashboard.history_limit = 1000

        # Add 2000 snapshots
        for i in range(2000):
            snap = TokenSnapshot(
                timestamp=datetime.now(),
                gas_available=i,
                gas_consumed=0,
                bucket_level=0.5,
                bucket_capacity=1000.0,
                sinking_fund=0.0,
                outstanding_futures=0,
            )
            dashboard._append_history(dashboard._state.token_history, snap)

        assert len(dashboard._state.token_history) == 1000
        # Should have 1000-1999
        assert dashboard._state.token_history[0].gas_available == 1000

    def test_summary_with_anomalies(self) -> None:
        """Summary shows anomalies."""
        dashboard = create_minimal_dashboard()

        dashboard._state.anomalies = [
            {"type": "value_leak", "severity": "high", "message": "Value leaked"},
            {"type": "budget_overrun", "severity": "medium", "message": "Over budget"},
        ]

        summary = dashboard.get_summary()

        assert "Anomalies" in summary
        assert "value_leak" in summary
