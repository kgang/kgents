"""
Tests for Semantic Metrics: Purpose-oriented Database Triad health signals.

Test Categories:
1. Health level semantics
2. DurabilitySignal natural transformation
3. ReflexSignal natural transformation
4. ResonanceSignal natural transformation (CDC lag integration)
5. TriadHealth aggregation
6. Natural transformation laws
7. SemanticMetricsCollector
8. Edge cases and boundaries
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


# ===========================================================================
# Health Level Tests
# ===========================================================================


class TestHealthLevel:
    """Tests for HealthLevel enum semantics."""

    def test_health_levels_ordered_by_severity(self) -> None:
        """Health levels have implicit severity ordering."""
        # The ordering from best to worst
        levels = [
            HealthLevel.THRIVING,
            HealthLevel.HEALTHY,
            HealthLevel.STRAINED,
            HealthLevel.DEGRADED,
            HealthLevel.CRITICAL,
        ]

        # All levels exist
        assert len(HealthLevel) == 5
        for level in levels:
            assert level in HealthLevel

    def test_health_level_values_are_readable(self) -> None:
        """Health level values are human-readable strings."""
        assert HealthLevel.THRIVING.value == "thriving"
        assert HealthLevel.CRITICAL.value == "critical"


# ===========================================================================
# Vendor Pulse Tests
# ===========================================================================


class TestVendorPulses:
    """Tests for vendor pulse dataclasses."""

    def test_postgres_pulse_creation(self) -> None:
        """PostgresPulse holds vendor metrics."""
        pulse = PostgresPulse(
            pool_active=5,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=15.0,
        )

        assert pulse.pool_active == 5
        assert pulse.pool_max == 20

    def test_postgres_pulse_is_frozen(self) -> None:
        """PostgresPulse is immutable."""
        pulse = PostgresPulse(5, 20, 0, 15.0)

        with pytest.raises(AttributeError):
            pulse.pool_active = 10  # type: ignore

    def test_redis_pulse_creation(self) -> None:
        """RedisPulse holds vendor metrics."""
        pulse = RedisPulse(
            memory_used_mb=50.0,
            memory_max_mb=128.0,
            commands_per_second=1000.0,
            hit_rate=0.95,
        )

        assert pulse.memory_used_mb == 50.0
        assert pulse.hit_rate == 0.95

    def test_qdrant_pulse_creation(self) -> None:
        """QdrantPulse holds vendor metrics."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=25.0,
            memory_mb=256.0,
        )

        assert pulse.vector_count == 10000
        assert pulse.avg_search_latency_ms == 25.0


# ===========================================================================
# DurabilitySignal Tests
# ===========================================================================


class TestDurabilitySignal:
    """Tests for DurabilitySignal (Is the truth safe?)"""

    def test_durability_from_healthy_postgres(self) -> None:
        """Healthy Postgres yields THRIVING durability."""
        pulse = PostgresPulse(
            pool_active=2,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=10.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        assert signal.health == HealthLevel.THRIVING
        assert signal.persistence_confidence > 0.8
        assert signal.write_capacity > 0.8

    def test_durability_from_busy_postgres(self) -> None:
        """Busy but functional Postgres yields HEALTHY."""
        pulse = PostgresPulse(
            pool_active=15,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=50.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        assert signal.health == HealthLevel.HEALTHY
        assert signal.write_capacity > 0.1

    def test_durability_from_strained_postgres(self) -> None:
        """Strained Postgres yields at least STRAINED durability."""
        pulse = PostgresPulse(
            pool_active=16,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=150.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        # At 80% utilization with moderate latency, should be strained
        assert signal.health in [HealthLevel.STRAINED, HealthLevel.DEGRADED]

    def test_durability_from_saturated_postgres(self) -> None:
        """Saturated Postgres with waiters yields DEGRADED."""
        pulse = PostgresPulse(
            pool_active=20,
            pool_max=20,
            pool_waiting=5,
            avg_latency_ms=500.0,
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        assert signal.health == HealthLevel.DEGRADED

    def test_durability_with_replication_lag(self) -> None:
        """Replication lag reduces persistence confidence."""
        pulse = PostgresPulse(
            pool_active=2,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=10.0,
            replication_lag_bytes=5_000_000,  # 5MB lag
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        # Confidence should be reduced
        assert signal.persistence_confidence < 0.9

    def test_durability_with_unflushed_wal(self) -> None:
        """Unflushed WAL reduces truth integrity."""
        pulse = PostgresPulse(
            pool_active=2,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=10.0,
            wal_bytes_unflushed=2_000_000,  # 2MB unflushed
        )

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        assert signal.truth_integrity < 1.0

    def test_durability_mock(self) -> None:
        """Mock creates valid signal."""
        signal = DurabilitySignal.mock(HealthLevel.HEALTHY)

        assert signal.health == HealthLevel.HEALTHY
        assert signal.timestamp is not None

    def test_durability_is_frozen(self) -> None:
        """DurabilitySignal is immutable."""
        signal = DurabilitySignal.mock()

        with pytest.raises(AttributeError):
            signal.health = HealthLevel.CRITICAL  # type: ignore


# ===========================================================================
# ReflexSignal Tests
# ===========================================================================


class TestReflexSignal:
    """Tests for ReflexSignal (How fast can I think?)"""

    def test_reflex_from_healthy_redis(self) -> None:
        """Healthy Redis yields THRIVING reflex."""
        pulse = RedisPulse(
            memory_used_mb=30.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.95,
        )

        signal = ReflexSignal.from_redis_pulse(pulse)

        assert signal.health == HealthLevel.THRIVING
        assert signal.recall_reliability > 0.9
        assert signal.thought_speed > 0.7

    def test_reflex_from_busy_redis(self) -> None:
        """Busy but functional Redis yields HEALTHY."""
        pulse = RedisPulse(
            memory_used_mb=100.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.8,
        )

        signal = ReflexSignal.from_redis_pulse(pulse)

        assert signal.health in [HealthLevel.HEALTHY, HealthLevel.STRAINED]

    def test_reflex_with_evictions(self) -> None:
        """Evictions reduce thought speed."""
        pulse = RedisPulse(
            memory_used_mb=128.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.4,  # Low hit rate due to evictions
            evictions_per_second=100.0,
        )

        signal = ReflexSignal.from_redis_pulse(pulse)

        # High evictions + low hit rate = degraded health
        assert signal.health == HealthLevel.DEGRADED
        assert signal.thought_speed < 0.5

    def test_reflex_low_hit_rate(self) -> None:
        """Low hit rate yields STRAINED."""
        pulse = RedisPulse(
            memory_used_mb=50.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.55,
        )

        signal = ReflexSignal.from_redis_pulse(pulse)

        assert signal.health == HealthLevel.STRAINED
        assert signal.recall_reliability == 0.55

    def test_reflex_memory_pressure(self) -> None:
        """Memory pressure is correctly calculated."""
        pulse = RedisPulse(
            memory_used_mb=64.0,
            memory_max_mb=128.0,
            commands_per_second=1000.0,
            hit_rate=0.8,
        )

        signal = ReflexSignal.from_redis_pulse(pulse)

        assert signal.memory_pressure == 0.5

    def test_reflex_mock(self) -> None:
        """Mock creates valid signal."""
        signal = ReflexSignal.mock(HealthLevel.HEALTHY)

        assert signal.health == HealthLevel.HEALTHY
        assert signal.timestamp is not None


# ===========================================================================
# ResonanceSignal Tests
# ===========================================================================


class TestResonanceSignal:
    """Tests for ResonanceSignal (Can I remember similar things?)"""

    def test_resonance_from_healthy_qdrant(self) -> None:
        """Healthy Qdrant with zero lag yields THRIVING."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=0)

        assert signal.health == HealthLevel.THRIVING
        assert signal.coherency_with_truth == 1.0
        assert signal.search_responsiveness > 0.9

    def test_resonance_cdc_lag_degrades_coherency(self) -> None:
        """CDC lag degrades coherency with truth."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        # 2500ms lag = 50% coherency
        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=2500)

        assert signal.coherency_with_truth == 0.5

    def test_resonance_cdc_threshold(self) -> None:
        """5000ms CDC lag = 0 coherency."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=5000)

        assert signal.coherency_with_truth == 0.0
        assert signal.health == HealthLevel.CRITICAL

    def test_resonance_beyond_threshold(self) -> None:
        """CDC lag beyond threshold floors at 0."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=10000)

        assert signal.coherency_with_truth == 0.0

    def test_resonance_slow_search(self) -> None:
        """Slow search reduces responsiveness."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=400.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=0)

        assert signal.search_responsiveness < 0.3

    def test_resonance_from_synapse_lag_tracker(self) -> None:
        """from_synapse_lag integrates CDCLagTracker."""
        tracker = CDCLagTracker()
        tracker.record(1000.0)  # 1 second lag

        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=30.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_synapse_lag(tracker, pulse)

        # 1000ms / 5000ms = 0.2 off, so 0.8 coherency
        assert signal.coherency_with_truth == 0.8

    def test_resonance_collection_status_affects_capacity(self) -> None:
        """Non-green collection status reduces capacity."""
        pulse = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=30.0,
            memory_mb=256.0,
            collection_status="yellow",
        )

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=0)

        assert signal.associative_capacity == 0.5

    def test_resonance_mock(self) -> None:
        """Mock creates valid signal with custom coherency."""
        signal = ResonanceSignal.mock(HealthLevel.HEALTHY, coherency=0.7)

        assert signal.health == HealthLevel.HEALTHY
        assert signal.coherency_with_truth == 0.7


# ===========================================================================
# TriadHealth Tests
# ===========================================================================


class TestTriadHealth:
    """Tests for TriadHealth aggregation."""

    def test_triad_overall_health_worst_of(self) -> None:
        """Overall health is worst of components."""
        health = TriadHealth(
            durability=DurabilitySignal.mock(HealthLevel.THRIVING),
            reflex=ReflexSignal.mock(HealthLevel.HEALTHY),
            resonance=ResonanceSignal.mock(HealthLevel.DEGRADED),
        )

        assert health.overall_health == HealthLevel.DEGRADED

    def test_triad_all_thriving(self) -> None:
        """All THRIVING yields THRIVING overall."""
        health = TriadHealth(
            durability=DurabilitySignal.mock(HealthLevel.THRIVING),
            reflex=ReflexSignal.mock(HealthLevel.THRIVING),
            resonance=ResonanceSignal.mock(HealthLevel.THRIVING),
        )

        assert health.overall_health == HealthLevel.THRIVING

    def test_triad_one_critical_is_critical(self) -> None:
        """One CRITICAL component makes triad CRITICAL."""
        health = TriadHealth(
            durability=DurabilitySignal.mock(HealthLevel.THRIVING),
            reflex=ReflexSignal.mock(HealthLevel.CRITICAL),
            resonance=ResonanceSignal.mock(HealthLevel.THRIVING),
        )

        assert health.overall_health == HealthLevel.CRITICAL

    def test_triad_is_coherent(self) -> None:
        """is_coherent checks resonance coherency."""
        coherent = TriadHealth(
            durability=DurabilitySignal.mock(),
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(coherency=0.9),
        )
        incoherent = TriadHealth(
            durability=DurabilitySignal.mock(),
            reflex=ReflexSignal.mock(),
            resonance=ResonanceSignal.mock(coherency=0.5),
        )

        assert coherent.is_coherent is True
        assert incoherent.is_coherent is False

    def test_triad_can_persist(self) -> None:
        """can_persist checks durability confidence."""
        health = TriadHealth.mock(HealthLevel.HEALTHY)

        assert health.can_persist is True

    def test_triad_can_recall(self) -> None:
        """can_recall checks reflex reliability."""
        health = TriadHealth.mock(HealthLevel.HEALTHY)

        assert health.can_recall is True

    def test_triad_can_associate(self) -> None:
        """can_associate checks resonance capabilities."""
        health = TriadHealth.mock(HealthLevel.HEALTHY)

        assert health.can_associate is True

    def test_triad_to_dict(self) -> None:
        """to_dict serializes for API."""
        health = TriadHealth.mock(HealthLevel.HEALTHY)

        d = health.to_dict()

        assert "overall_health" in d
        assert "durability" in d
        assert "reflex" in d
        assert "resonance" in d
        assert d["overall_health"] == "healthy"

    def test_triad_mock(self) -> None:
        """Mock creates valid triad."""
        health = TriadHealth.mock(HealthLevel.STRAINED)

        assert health.overall_health == HealthLevel.STRAINED


# ===========================================================================
# Natural Transformation Law Tests
# ===========================================================================


class TestNaturalTransformationLaws:
    """
    Tests verifying the semantic metrics satisfy natural transformation laws.

    For a natural transformation eta: F => G, the naturality square must commute:

        F(A) ---eta_A---> G(A)
         |                 |
       F(f)              G(f)
         |                 |
         v                 v
        F(B) ---eta_B---> G(B)

    In our case:
    - F = VendorMetrics (PostgresPulse, RedisPulse, QdrantPulse)
    - G = SemanticSignals (DurabilitySignal, ReflexSignal, ResonanceSignal)
    - eta = from_*_pulse transformations
    - f = vendor upgrades/changes

    The law says: upgrading then transforming = transforming then upgrading
    """

    def test_postgres_transformation_preserves_ordering(self) -> None:
        """
        Transformation preserves relative health ordering.

        If pulse_A is "better" than pulse_B, then
        signal_A should be at least as healthy as signal_B.
        """
        # Pulse A is clearly better
        pulse_a = PostgresPulse(
            pool_active=2,
            pool_max=20,
            pool_waiting=0,
            avg_latency_ms=5.0,
        )
        # Pulse B is worse
        pulse_b = PostgresPulse(
            pool_active=18,
            pool_max=20,
            pool_waiting=2,
            avg_latency_ms=200.0,
        )

        signal_a = DurabilitySignal.from_postgres_pulse(pulse_a)
        signal_b = DurabilitySignal.from_postgres_pulse(pulse_b)

        # Health ordering should be preserved
        health_order = [
            HealthLevel.CRITICAL,
            HealthLevel.DEGRADED,
            HealthLevel.STRAINED,
            HealthLevel.HEALTHY,
            HealthLevel.THRIVING,
        ]
        assert health_order.index(signal_a.health) >= health_order.index(signal_b.health)

    def test_redis_transformation_preserves_ordering(self) -> None:
        """
        Redis transformation preserves relative health ordering.
        """
        pulse_a = RedisPulse(
            memory_used_mb=20.0,
            memory_max_mb=128.0,
            commands_per_second=5000.0,
            hit_rate=0.99,
        )
        pulse_b = RedisPulse(
            memory_used_mb=128.0,
            memory_max_mb=128.0,
            commands_per_second=100.0,
            hit_rate=0.3,
            evictions_per_second=500.0,
        )

        signal_a = ReflexSignal.from_redis_pulse(pulse_a)
        signal_b = ReflexSignal.from_redis_pulse(pulse_b)

        health_order = [
            HealthLevel.CRITICAL,
            HealthLevel.DEGRADED,
            HealthLevel.STRAINED,
            HealthLevel.HEALTHY,
            HealthLevel.THRIVING,
        ]
        assert health_order.index(signal_a.health) >= health_order.index(signal_b.health)

    def test_qdrant_transformation_preserves_ordering(self) -> None:
        """
        Qdrant transformation preserves relative health ordering.
        """
        pulse_a = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=10.0,
            memory_mb=256.0,
        )
        pulse_b = QdrantPulse(
            vector_count=10000,
            avg_search_latency_ms=400.0,
            memory_mb=256.0,
        )

        signal_a = ResonanceSignal.from_qdrant_pulse(pulse_a, cdc_lag_ms=0)
        signal_b = ResonanceSignal.from_qdrant_pulse(pulse_b, cdc_lag_ms=4000)

        health_order = [
            HealthLevel.CRITICAL,
            HealthLevel.DEGRADED,
            HealthLevel.STRAINED,
            HealthLevel.HEALTHY,
            HealthLevel.THRIVING,
        ]
        assert health_order.index(signal_a.health) >= health_order.index(signal_b.health)

    def test_coherency_is_monotonic_in_lag(self) -> None:
        """
        coherency_with_truth is monotonically decreasing in CDC lag.

        This is a key property: more lag = less coherency.
        """
        pulse = QdrantPulse(10000, 20.0, 256.0)

        coherencies = []
        for lag in [0, 1000, 2000, 3000, 4000, 5000]:
            signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=lag)
            coherencies.append(signal.coherency_with_truth)

        # Each coherency should be <= the previous
        for i in range(1, len(coherencies)):
            assert coherencies[i] <= coherencies[i - 1]


# ===========================================================================
# SemanticMetricsCollector Tests
# ===========================================================================


class TestSemanticMetricsCollector:
    """Tests for SemanticMetricsCollector."""

    def test_collector_creation(self) -> None:
        """Collector can be created."""
        collector = SemanticMetricsCollector()

        assert collector is not None

    def test_collector_update_postgres(self) -> None:
        """update_postgres returns signal."""
        collector = SemanticMetricsCollector()
        pulse = PostgresPulse(2, 20, 0, 10.0)

        signal = collector.update_postgres(pulse)

        assert isinstance(signal, DurabilitySignal)

    def test_collector_update_redis(self) -> None:
        """update_redis returns signal."""
        collector = SemanticMetricsCollector()
        pulse = RedisPulse(50.0, 128.0, 5000.0, 0.95)

        signal = collector.update_redis(pulse)

        assert isinstance(signal, ReflexSignal)

    def test_collector_update_qdrant(self) -> None:
        """update_qdrant returns signal."""
        collector = SemanticMetricsCollector()
        pulse = QdrantPulse(10000, 30.0, 256.0)

        signal = collector.update_qdrant(pulse)

        assert isinstance(signal, ResonanceSignal)

    def test_collector_collect_returns_none_without_all_pulses(self) -> None:
        """collect() returns None if any pulse is missing."""
        collector = SemanticMetricsCollector()
        collector.update_postgres(PostgresPulse(2, 20, 0, 10.0))

        result = collector.collect()

        assert result is None

    def test_collector_collect_returns_triad_with_all_pulses(self) -> None:
        """collect() returns TriadHealth when all pulses are present."""
        collector = SemanticMetricsCollector()
        collector.update_postgres(PostgresPulse(2, 20, 0, 10.0))
        collector.update_redis(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        collector.update_qdrant(QdrantPulse(10000, 30.0, 256.0))

        result = collector.collect()

        assert isinstance(result, TriadHealth)
        assert result.overall_health in HealthLevel

    def test_collector_with_cdc_lag_tracker(self) -> None:
        """Collector uses CDCLagTracker for resonance coherency."""
        tracker = CDCLagTracker()
        tracker.record(2500.0)  # 50% coherency

        collector = SemanticMetricsCollector(cdc_lag_tracker=tracker)
        collector.update_postgres(PostgresPulse(2, 20, 0, 10.0))
        collector.update_redis(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        collector.update_qdrant(QdrantPulse(10000, 30.0, 256.0))

        result = collector.collect()

        assert result is not None
        assert result.resonance.coherency_with_truth == 0.5

    def test_collector_set_cdc_lag_tracker(self) -> None:
        """set_cdc_lag_tracker wires up tracker after creation."""
        collector = SemanticMetricsCollector()
        tracker = CDCLagTracker()
        tracker.record(1000.0)

        collector.set_cdc_lag_tracker(tracker)
        collector.update_postgres(PostgresPulse(2, 20, 0, 10.0))
        collector.update_redis(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        collector.update_qdrant(QdrantPulse(10000, 30.0, 256.0))

        result = collector.collect()

        assert result is not None
        assert result.resonance.coherency_with_truth == 0.8


# ===========================================================================
# Edge Cases and Boundaries
# ===========================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_postgres_zero_pool_max(self) -> None:
        """Handles zero pool_max gracefully."""
        pulse = PostgresPulse(0, 0, 0, 10.0)

        signal = DurabilitySignal.from_postgres_pulse(pulse)

        # Should not crash, should indicate problems
        assert signal is not None

    def test_redis_zero_memory_max(self) -> None:
        """Handles zero memory_max gracefully."""
        pulse = RedisPulse(0.0, 0.0, 1000.0, 0.5)

        signal = ReflexSignal.from_redis_pulse(pulse)

        assert signal is not None

    def test_coherency_clamps_to_zero(self) -> None:
        """Coherency never goes negative."""
        pulse = QdrantPulse(10000, 30.0, 256.0)

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=999999)

        assert signal.coherency_with_truth == 0.0
        assert signal.coherency_with_truth >= 0.0

    def test_coherency_clamps_to_one(self) -> None:
        """Coherency never exceeds 1 (clamped)."""
        pulse = QdrantPulse(10000, 30.0, 256.0)

        signal = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=-1000)

        # Negative lag would give >1, but should clamp to 1.0
        assert signal.coherency_with_truth == 1.0

    def test_search_responsiveness_clamps(self) -> None:
        """Search responsiveness stays in 0-1."""
        slow_pulse = QdrantPulse(10000, 1000.0, 256.0)
        fast_pulse = QdrantPulse(10000, 0.0, 256.0)

        slow_signal = ResonanceSignal.from_qdrant_pulse(slow_pulse, 0)
        fast_signal = ResonanceSignal.from_qdrant_pulse(fast_pulse, 0)

        assert 0.0 <= slow_signal.search_responsiveness <= 1.0
        assert 0.0 <= fast_signal.search_responsiveness <= 1.0

    def test_all_signals_have_timestamps(self) -> None:
        """All signals include timestamps."""
        d = DurabilitySignal.from_postgres_pulse(PostgresPulse(2, 20, 0, 10.0))
        r = ReflexSignal.from_redis_pulse(RedisPulse(50.0, 128.0, 5000.0, 0.95))
        q = ResonanceSignal.from_qdrant_pulse(QdrantPulse(10000, 30.0, 256.0), 0)

        assert d.timestamp is not None
        assert r.timestamp is not None
        assert q.timestamp is not None


# ===========================================================================
# Health Transition Tests
# ===========================================================================


class TestHealthTransitions:
    """Tests for health level transitions."""

    def test_durability_thriving_boundary(self) -> None:
        """THRIVING requires > 50% available and < 20ms latency."""
        # Just over threshold
        thriving = PostgresPulse(9, 20, 0, 19.0)
        # Just under threshold (latency)
        not_thriving = PostgresPulse(9, 20, 0, 21.0)

        assert DurabilitySignal.from_postgres_pulse(thriving).health == HealthLevel.THRIVING
        assert (
            DurabilitySignal.from_postgres_pulse(not_thriving).health != HealthLevel.THRIVING
        )

    def test_resonance_health_depends_on_coherency(self) -> None:
        """Resonance health degrades with coherency."""
        pulse = QdrantPulse(10000, 30.0, 256.0)

        thriving = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=0)  # 100% coherency
        healthy = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=1000)  # 80% coherency
        strained = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=2000)  # 60% coherency
        degraded = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=3500)  # 30% coherency
        critical = ResonanceSignal.from_qdrant_pulse(pulse, cdc_lag_ms=4500)  # 10% coherency

        assert thriving.health == HealthLevel.THRIVING
        assert healthy.health == HealthLevel.HEALTHY
        assert strained.health == HealthLevel.STRAINED
        assert degraded.health == HealthLevel.DEGRADED
        assert critical.health == HealthLevel.CRITICAL
