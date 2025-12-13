"""
Integration tests for Semantic Metrics against the Database Triad.

Validates that semantic signals accurately reflect actual infrastructure state.

Test Categories:
1. DurabilitySignal reflects Postgres health
2. ResonanceSignal coherency correlates with CDC lag
3. TriadHealth aggregation under various conditions
4. Collector integration with CDC pipeline
"""

from __future__ import annotations

import pytest

from agents.flux.synapse import CDCLagTracker
from protocols.terrarium.semantic_metrics import (
    DurabilitySignal,
    HealthLevel,
    PostgresPulse,
    QdrantPulse,
    RedisPulse,
    ReflexSignal,
    ResonanceSignal,
    SemanticMetricsCollector,
    TriadHealth,
)

from .conftest import TriadFixture


# ===========================================================================
# DurabilitySignal Integration
# ===========================================================================


class TestDurabilitySignalIntegration:
    """Validate DurabilitySignal reflects Postgres state."""

    def test_durability_accurately_reflects_pool_saturation(self) -> None:
        """DurabilitySignal correctly reports pool saturation."""
        # Simulate saturated pool
        saturated = PostgresPulse(
            pool_active=20,
            pool_max=20,
            pool_waiting=5,
            avg_latency_ms=500.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(saturated)

        assert signal.health == HealthLevel.DEGRADED
        assert signal.write_capacity < 0.1

    def test_durability_reflects_healthy_pool(self) -> None:
        """DurabilitySignal correctly reports healthy pool."""
        healthy = PostgresPulse(
            pool_active=5,
            pool_max=50,
            pool_waiting=0,
            avg_latency_ms=5.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(healthy)

        assert signal.health == HealthLevel.THRIVING
        assert signal.write_capacity > 0.8

    def test_durability_confidence_degrades_with_replication_lag(self) -> None:
        """Replication lag reduces persistence confidence."""
        lagging = PostgresPulse(
            pool_active=5,
            pool_max=50,
            pool_waiting=0,
            avg_latency_ms=10.0,
            replication_lag_bytes=8_000_000,  # 8MB lag
        )

        signal = DurabilitySignal.from_postgres_pulse(lagging)

        # Confidence should be reduced but not zero
        assert signal.persistence_confidence < 0.8
        assert signal.persistence_confidence > 0


# ===========================================================================
# ResonanceSignal Coherency Integration
# ===========================================================================


class TestResonanceCoherencyIntegration:
    """Validate coherency_with_truth matches actual data freshness."""

    @pytest.mark.asyncio
    async def test_coherency_high_when_synced(self, triad: TriadFixture) -> None:
        """coherency_with_truth is high when Qdrant is in sync."""
        # Insert and process immediately
        await triad.postgres.insert("memories", {"content": "Fresh data"})
        await triad.process_pending_events()

        pulse = QdrantPulse(
            vector_count=1,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)

        # Should be high coherency (low lag)
        assert signal.coherency_with_truth > 0.9

    @pytest.mark.asyncio
    async def test_coherency_degrades_with_pending_events(
        self, triad: TriadFixture
    ) -> None:
        """Pending events indicate coherency lag."""
        # Insert but don't process
        await triad.postgres.insert("memories", {"content": "Pending data"})

        # Pending events exist
        pending = triad.count_pending_outbox()
        assert pending > 0

        # Simulate lag in tracker
        triad.lag_tracker.record(3000.0)  # 3 second simulated lag

        pulse = QdrantPulse(
            vector_count=0,  # Nothing in Qdrant yet
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)

        # Coherency should be degraded
        assert signal.coherency_with_truth < 0.5

    def test_coherency_is_zero_at_threshold(self) -> None:
        """5000ms lag = 0 coherency (threshold behavior)."""
        tracker = CDCLagTracker()
        tracker.record(5000.0)

        pulse = QdrantPulse(10000, 20.0, 256.0)
        signal = ResonanceSignal.from_synapse_lag(tracker, pulse)

        assert signal.coherency_with_truth == 0.0
        assert signal.health == HealthLevel.CRITICAL

    def test_coherency_linear_degradation(self) -> None:
        """Coherency degrades linearly with lag."""
        pulse = QdrantPulse(10000, 20.0, 256.0)

        test_cases = [
            (0, 1.0),
            (1000, 0.8),
            (2500, 0.5),
            (4000, 0.2),
            (5000, 0.0),
        ]

        for lag_ms, expected_coherency in test_cases:
            tracker = CDCLagTracker()
            tracker.record(float(lag_ms))
            signal = ResonanceSignal.from_synapse_lag(tracker, pulse)
            assert signal.coherency_with_truth == pytest.approx(
                expected_coherency, abs=0.01
            ), f"Failed for lag={lag_ms}"


# ===========================================================================
# ReflexSignal Integration
# ===========================================================================


class TestReflexSignalIntegration:
    """Validate ReflexSignal reflects Redis state."""

    def test_reflex_reflects_memory_pressure(self) -> None:
        """ReflexSignal accurately reports memory pressure."""
        high_pressure = RedisPulse(
            memory_used_mb=120.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.7,
        )

        signal = ReflexSignal.from_redis_pulse(high_pressure)

        assert signal.memory_pressure > 0.9
        assert signal.thought_speed < 0.2

    def test_reflex_reflects_hit_rate(self) -> None:
        """ReflexSignal accurately reports recall reliability."""
        good_cache = RedisPulse(
            memory_used_mb=64.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.95,
        )

        signal = ReflexSignal.from_redis_pulse(good_cache)

        assert signal.recall_reliability == 0.95


# ===========================================================================
# TriadHealth Integration
# ===========================================================================


class TestTriadHealthIntegration:
    """Validate TriadHealth aggregation."""

    def test_triad_worst_of_semantics(self) -> None:
        """TriadHealth reports worst component status."""
        health = TriadHealth(
            durability=DurabilitySignal.mock(HealthLevel.THRIVING),
            reflex=ReflexSignal.mock(HealthLevel.HEALTHY),
            resonance=ResonanceSignal.mock(HealthLevel.DEGRADED, coherency=0.3),
        )

        assert health.overall_health == HealthLevel.DEGRADED

    def test_triad_is_coherent_threshold(self) -> None:
        """is_coherent uses 0.7 threshold."""
        coherent = TriadHealth(
            durability=DurabilitySignal.mock(),
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(coherency=0.75),
        )
        incoherent = TriadHealth(
            durability=DurabilitySignal.mock(),
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(coherency=0.65),
        )

        assert coherent.is_coherent is True
        assert incoherent.is_coherent is False

    def test_triad_can_persist_threshold(self) -> None:
        """can_persist uses 0.5 threshold."""
        # Create durability with high confidence
        good_pulse = PostgresPulse(5, 50, 0, 10.0)
        good_durability = DurabilitySignal.from_postgres_pulse(good_pulse)

        # Create durability with low confidence
        bad_pulse = PostgresPulse(48, 50, 5, 500.0)
        bad_durability = DurabilitySignal.from_postgres_pulse(bad_pulse)

        can_persist = TriadHealth(
            durability=good_durability,
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(),
        )
        cannot_persist = TriadHealth(
            durability=bad_durability,
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(),
        )

        assert can_persist.can_persist is True
        assert cannot_persist.can_persist is False

    def test_triad_serialization(self) -> None:
        """TriadHealth serializes correctly for API."""
        health = TriadHealth.mock(HealthLevel.HEALTHY)
        d = health.to_dict()

        assert d["overall_health"] == "healthy"
        assert "durability" in d
        assert "reflex" in d
        assert "resonance" in d
        durability = d["durability"]
        assert isinstance(durability, dict) and durability["health"] == "healthy"


# ===========================================================================
# SemanticMetricsCollector Integration
# ===========================================================================


class TestCollectorIntegration:
    """Validate SemanticMetricsCollector integration with CDC."""

    @pytest.mark.asyncio
    async def test_collector_with_cdc_lag_tracker(
        self, triad: TriadFixture
    ) -> None:
        """Collector integrates with CDCLagTracker from Synapse."""
        collector = SemanticMetricsCollector(cdc_lag_tracker=triad.lag_tracker)

        # Process some events
        await triad.postgres.insert("memories", {"content": "test"})
        await triad.process_pending_events()

        # Update all pulses
        collector.update_postgres(PostgresPulse(5, 50, 0, 10.0))
        collector.update_redis(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        collector.update_qdrant(QdrantPulse(1, 20.0, 256.0))

        # Collect triad health
        health = collector.collect()

        assert health is not None
        # Low lag should mean high coherency
        assert health.resonance.coherency_with_truth > 0.9

    def test_collector_set_cdc_lag_tracker(self) -> None:
        """set_cdc_lag_tracker wires tracker after creation."""
        collector = SemanticMetricsCollector()
        tracker = CDCLagTracker()
        tracker.record(2000.0)  # 2 second lag

        collector.set_cdc_lag_tracker(tracker)
        collector.update_postgres(PostgresPulse(5, 50, 0, 10.0))
        collector.update_redis(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        collector.update_qdrant(QdrantPulse(100, 20.0, 256.0))

        health = collector.collect()

        assert health is not None
        # 2000ms lag = 0.6 coherency
        assert health.resonance.coherency_with_truth == pytest.approx(0.6, abs=0.01)

    def test_collector_returns_none_without_all_pulses(self) -> None:
        """collect() returns None if any pulse missing."""
        collector = SemanticMetricsCollector()
        collector.update_postgres(PostgresPulse(5, 50, 0, 10.0))
        # Missing redis and qdrant

        assert collector.collect() is None


# ===========================================================================
# Health Transition Tests
# ===========================================================================


class TestHealthTransitions:
    """Tests for health level transitions in integrated context."""

    def test_resonance_transitions_with_lag(self) -> None:
        """ResonanceSignal health transitions correctly with lag."""
        pulse = QdrantPulse(10000, 20.0, 256.0)

        def health_at_lag(lag_ms: float) -> HealthLevel:
            tracker = CDCLagTracker()
            tracker.record(lag_ms)
            return ResonanceSignal.from_synapse_lag(tracker, pulse).health

        # Verify transitions follow coherency thresholds:
        # >0.9 = THRIVING, >0.7 = HEALTHY, >0.5 = STRAINED, >0.2 = DEGRADED, else CRITICAL
        # coherency = 1 - (lag / 5000)
        # 0ms -> 1.0 -> THRIVING
        # 400ms -> 0.92 -> THRIVING (with low latency)
        # 1000ms -> 0.8 -> HEALTHY
        # 1500ms -> 0.7 -> STRAINED (boundary - 0.7 is not > 0.7)
        # 2000ms -> 0.6 -> STRAINED (>0.5)
        # 2500ms -> 0.5 -> DEGRADED (boundary - 0.5 is not > 0.5)
        # 3500ms -> 0.3 -> DEGRADED (>0.2)
        # 4000ms -> 0.2 -> CRITICAL (boundary - 0.2 is not > 0.2)
        assert health_at_lag(0) == HealthLevel.THRIVING
        assert health_at_lag(400) == HealthLevel.THRIVING
        assert health_at_lag(1000) == HealthLevel.HEALTHY
        assert health_at_lag(1500) == HealthLevel.STRAINED
        assert health_at_lag(2000) == HealthLevel.STRAINED  # 0.6 coherency
        assert health_at_lag(2500) == HealthLevel.DEGRADED  # 0.5 boundary
        assert health_at_lag(3500) == HealthLevel.DEGRADED  # 0.3 coherency
        assert health_at_lag(4000) == HealthLevel.CRITICAL  # 0.2 boundary
        assert health_at_lag(4500) == HealthLevel.CRITICAL

    def test_durability_transitions_with_load(self) -> None:
        """DurabilitySignal health transitions with pool load."""

        def health_at_load(active: int, max_pool: int, waiters: int) -> HealthLevel:
            pulse = PostgresPulse(active, max_pool, waiters, 15.0)
            return DurabilitySignal.from_postgres_pulse(pulse).health

        # Verify transitions
        assert health_at_load(5, 50, 0) == HealthLevel.THRIVING
        assert health_at_load(30, 50, 0) == HealthLevel.HEALTHY
        assert health_at_load(42, 50, 0) == HealthLevel.STRAINED
        assert health_at_load(50, 50, 5) == HealthLevel.DEGRADED


# ===========================================================================
# Stress Scenario Tests
# ===========================================================================


class TestStressScenarios:
    """Tests for stress scenarios and recovery."""

    @pytest.mark.asyncio
    async def test_health_recovery_after_processing_backlog(
        self, triad: TriadFixture
    ) -> None:
        """Health improves after processing pending events."""
        # Simulate backlog with high lag
        for _ in range(10):
            triad.lag_tracker.record(4000.0)

        pulse = QdrantPulse(100, 20.0, 256.0)
        degraded = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)
        # 4000ms lag = 0.2 coherency which is DEGRADED or CRITICAL
        assert degraded.health in [HealthLevel.DEGRADED, HealthLevel.CRITICAL]

        # Process events with low lag
        for _ in range(20):
            triad.lag_tracker.record(50.0)

        recovered = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)

        # Avg lag should improve, health should recover
        assert recovered.health in [HealthLevel.HEALTHY, HealthLevel.THRIVING]
        assert recovered.coherency_with_truth > degraded.coherency_with_truth

    def test_all_critical_yields_critical_triad(self) -> None:
        """All critical components = critical triad."""
        health = TriadHealth(
            durability=DurabilitySignal.mock(HealthLevel.CRITICAL),
            reflex=ReflexSignal.mock(HealthLevel.CRITICAL),
            resonance=ResonanceSignal.mock(HealthLevel.CRITICAL, coherency=0.0),
        )

        assert health.overall_health == HealthLevel.CRITICAL
        assert health.is_coherent is False
        assert health.can_persist is False
        assert health.can_recall is False
        assert health.can_associate is False
