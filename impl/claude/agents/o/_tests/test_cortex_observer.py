"""
Tests for CortexObserver (Instance DB Phase 6).

Tests cortex health observation, metrics collection, and subscriptions.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from agents.o.cortex_observer import (
    CoherencyStatus,
    CortexHealth,
    CortexHealthSnapshot,
    CortexObserver,
    CortexObserverConfig,
    DreamerStatus,
    HippocampusStatus,
    LeftHemisphereStatus,
    RightHemisphereStatus,
    SynapseStatus,
    create_cortex_observer,
    create_mock_cortex_observer,
)


class TestCortexHealth:
    """Tests for health status enums."""

    def test_health_enum_values(self):
        """Test health enum has expected values."""
        assert CortexHealth.HEALTHY.value == "healthy"
        assert CortexHealth.DEGRADED.value == "degraded"
        assert CortexHealth.CRITICAL.value == "critical"
        assert CortexHealth.UNKNOWN.value == "unknown"


class TestLeftHemisphereStatus:
    """Tests for Left Hemisphere status."""

    def test_error_rate_zero_queries(self):
        """Test error rate with zero queries."""
        status = LeftHemisphereStatus(queries_total=0, errors_total=0)
        assert status.error_rate == 0.0

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        status = LeftHemisphereStatus(queries_total=100, errors_total=5)
        assert status.error_rate == 0.05

    def test_health_unavailable(self):
        """Test health when unavailable."""
        status = LeftHemisphereStatus(available=False)
        assert status.health == CortexHealth.CRITICAL

    def test_health_healthy(self):
        """Test health when all good."""
        status = LeftHemisphereStatus(
            available=True,
            latency_ms=50.0,
            queries_total=100,
            errors_total=0,
        )
        assert status.health == CortexHealth.HEALTHY

    def test_health_degraded_latency(self):
        """Test health degrades with high latency."""
        status = LeftHemisphereStatus(
            available=True,
            latency_ms=150.0,
            queries_total=100,
            errors_total=0,
        )
        assert status.health == CortexHealth.DEGRADED

    def test_health_critical_error_rate(self):
        """Test health critical with high error rate."""
        status = LeftHemisphereStatus(
            available=True,
            queries_total=100,
            errors_total=15,  # 15% error rate
        )
        assert status.health == CortexHealth.CRITICAL


class TestCoherencyStatus:
    """Tests for Coherency status."""

    def test_health_healthy(self):
        """Test coherency health when good."""
        status = CoherencyStatus(coherency_rate=0.98, ghost_count=0)
        assert status.health == CortexHealth.HEALTHY

    def test_health_degraded(self):
        """Test coherency health when degraded."""
        status = CoherencyStatus(coherency_rate=0.92, ghost_count=15)
        assert status.health == CortexHealth.DEGRADED

    def test_health_critical(self):
        """Test coherency health when critical."""
        status = CoherencyStatus(coherency_rate=0.85)
        assert status.health == CortexHealth.CRITICAL


class TestSynapseStatus:
    """Tests for Synapse status."""

    def test_health_unavailable(self):
        """Test health when synapse unavailable."""
        status = SynapseStatus(available=False)
        assert status.health == CortexHealth.CRITICAL

    def test_health_healthy(self):
        """Test health when healthy."""
        status = SynapseStatus(available=True, flashbulb_rate=0.1)
        assert status.health == CortexHealth.HEALTHY

    def test_health_degraded_flashbulb(self):
        """Test health degrades with high flashbulb rate."""
        status = SynapseStatus(available=True, flashbulb_rate=0.6)
        assert status.health == CortexHealth.DEGRADED


class TestCortexHealthSnapshot:
    """Tests for CortexHealthSnapshot."""

    def test_to_dict(self):
        """Test snapshot serialization."""
        snapshot = CortexHealthSnapshot(
            timestamp="2024-01-01T00:00:00",
            overall=CortexHealth.HEALTHY,
            left_hemisphere=LeftHemisphereStatus(available=True),
            right_hemisphere=RightHemisphereStatus(available=True),
            coherency=CoherencyStatus(),
            synapse=SynapseStatus(available=True),
            hippocampus=HippocampusStatus(),
            dreamer=DreamerStatus(),
        )

        data = snapshot.to_dict()

        assert data["overall"] == "healthy"
        assert data["left_hemisphere"]["available"] is True
        assert "coherency" in data
        assert "synapse" in data


class TestCortexObserverConfig:
    """Tests for CortexObserverConfig."""

    def test_defaults(self):
        """Test default configuration."""
        config = CortexObserverConfig()
        assert config.history_limit == 1000
        assert config.health_check_interval_ms == 1000

    def test_from_dict(self):
        """Test creating config from dict."""
        config = CortexObserverConfig.from_dict(
            {
                "history_limit": 500,
                "latency_warning_ms": 50.0,
            }
        )
        assert config.history_limit == 500
        assert config.latency_warning_ms == 50.0


class TestCortexObserver:
    """Tests for CortexObserver."""

    def test_create_without_components(self):
        """Test creating observer without components."""
        observer = CortexObserver()
        health = observer.get_health()

        assert health.overall == CortexHealth.CRITICAL
        assert health.left_hemisphere.available is False

    def test_get_health_returns_snapshot(self):
        """Test get_health returns valid snapshot."""
        observer = create_mock_cortex_observer()
        health = observer.get_health()

        assert isinstance(health, CortexHealthSnapshot)
        assert health.timestamp is not None

    def test_history_tracking(self):
        """Test history is tracked."""
        observer = CortexObserver()

        # Generate some health checks
        for _ in range(5):
            observer.get_health()

        history = observer.get_history(limit=10)
        assert len(history) == 5

    def test_history_limit(self):
        """Test history respects limit."""
        config = CortexObserverConfig(history_limit=3)
        observer = CortexObserver(config=config)

        # Generate more than limit
        for _ in range(10):
            observer.get_health()

        history = observer.get_history()
        assert len(history) == 3

    def test_health_change_callback(self):
        """Test health change callbacks."""
        observer = CortexObserver()
        callbacks_called = []

        def on_change(snapshot: CortexHealthSnapshot):
            callbacks_called.append(snapshot)

        unsubscribe = observer.on_health_change(on_change)

        # Force a health check (first won't trigger since no previous)
        observer.get_health()

        # Verify we can unsubscribe
        unsubscribe()
        assert on_change not in observer._callbacks

    def test_render_compact(self):
        """Test compact rendering."""
        observer = create_mock_cortex_observer()
        compact = observer.render_compact()

        assert "[CORTEX]" in compact
        assert "CRITICAL" in compact or "HEALTHY" in compact or "DEGRADED" in compact

    def test_stats(self):
        """Test statistics collection."""
        observer = CortexObserver()
        observer.get_health()

        stats = observer.get_stats()

        assert stats["observations_total"] == 1
        assert "components" in stats


class TestCortexObserverWithMocks:
    """Tests with mock components."""

    def test_observe_bicameral(self):
        """Test observing bicameral memory."""
        mock_bicameral = MagicMock()
        mock_bicameral.stats.return_value = {
            "total_recalls": 100,
            "ghosts_healed": 5,
            "stale_flagged": 2,
            "coherency_checks": 10,
            "has_semantic": True,
        }
        mock_bicameral.ghost_log = []
        mock_bicameral.stale_log = []

        observer = CortexObserver(bicameral=mock_bicameral)
        health = observer.get_health()

        assert health.left_hemisphere.available is True
        assert health.left_hemisphere.queries_total == 100

    def test_observe_synapse(self):
        """Test observing synapse."""
        mock_synapse = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.high_surprise_count = 80
        mock_metrics.low_surprise_count = 20
        mock_metrics.flashbulb_count = 5
        mock_metrics.type_total_surprise = {"test": 0.5}
        mock_metrics.type_counts = {"test": 10}
        mock_synapse.get_metrics.return_value = mock_metrics
        mock_synapse.has_flashbulb_pending.return_value = False
        mock_synapse.batch_queue_size = 10

        observer = CortexObserver(synapse=mock_synapse)
        health = observer.get_health()

        assert health.synapse.available is True
        assert health.synapse.signals_total == 100

    def test_observe_hippocampus(self):
        """Test observing hippocampus."""
        mock_hippocampus = MagicMock()
        mock_hippocampus.get_stats.return_value = {
            "max_size": 1000,
            "flushes_total": 5,
            "last_flush": "2024-01-01T00:00:00",
        }
        mock_hippocampus.size = 500

        observer = CortexObserver(hippocampus=mock_hippocampus)
        health = observer.get_health()

        assert health.hippocampus.available is True
        assert health.hippocampus.memory_count == 500
        assert health.hippocampus.utilization == 0.5


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_cortex_observer(self):
        """Test factory function."""
        observer = create_cortex_observer()
        assert isinstance(observer, CortexObserver)

    def test_create_cortex_observer_with_config(self):
        """Test factory function with config."""
        observer = create_cortex_observer(config_dict={"history_limit": 500})
        assert observer._config.history_limit == 500

    def test_create_mock_cortex_observer(self):
        """Test mock factory function."""
        observer = create_mock_cortex_observer()
        assert isinstance(observer, CortexObserver)
        health = observer.get_health()
        assert isinstance(health, CortexHealthSnapshot)
