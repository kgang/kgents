"""
Semantic Metrics: Purpose-oriented Database Triad health signals.

These are natural transformations from vendor metrics to semantic signals.
The observer sees "Is the truth safe?" not "Postgres pool utilization."

The Transformation:
    eta: VendorMetrics => SemanticMetrics

    eta(PostgresPulse) = DurabilitySignal   ("Is the truth safe?")
    eta(RedisPulse)    = ReflexSignal       ("How fast can I think?")
    eta(QdrantPulse)   = ResonanceSignal    ("Can I remember similar things?")

Categorical Property:
    These are natural transformations because they commute with
    vendor upgrades: upgrading then measuring = measuring then transforming.

The key insight is that ResonanceSignal.coherency_with_truth derives
from CDCLagTracker, making the Functor Stack's health observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.flux.synapse import CDCLagTracker


# ─────────────────────────────────────────────────────────────
# Health Levels (Semantic, not Vendor)
# ─────────────────────────────────────────────────────────────


class HealthLevel(Enum):
    """
    Semantic health levels.

    These describe the PURPOSE health, not the implementation health.
    An observer asks "Can I do X?" not "What is the pool size?"
    """

    THRIVING = "thriving"  # Everything excellent
    HEALTHY = "healthy"  # Normal operation
    STRAINED = "strained"  # Approaching limits
    DEGRADED = "degraded"  # Reduced capability
    CRITICAL = "critical"  # Intervention needed


# ─────────────────────────────────────────────────────────────
# Vendor Pulse Types (Input to Natural Transformation)
# ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PostgresPulse:
    """
    Raw Postgres metrics (vendor pulse).

    These are implementation-specific metrics that get transformed
    into semantic signals via the natural transformation.
    """

    pool_active: int
    pool_max: int
    pool_waiting: int
    avg_latency_ms: float
    replication_lag_bytes: int = 0
    wal_bytes_unflushed: int = 0


@dataclass(frozen=True)
class RedisPulse:
    """
    Raw Redis metrics (vendor pulse).

    Implementation-specific metrics from Redis.
    """

    memory_used_mb: float
    memory_max_mb: float
    commands_per_second: float
    hit_rate: float
    evictions_per_second: float = 0.0
    connected_clients: int = 1


@dataclass(frozen=True)
class QdrantPulse:
    """
    Raw Qdrant metrics (vendor pulse).

    Implementation-specific metrics from Qdrant.
    """

    vector_count: int
    avg_search_latency_ms: float
    memory_mb: float
    collection_status: str = "green"


# ─────────────────────────────────────────────────────────────
# Semantic Signals (Output of Natural Transformation)
# ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DurabilitySignal:
    """
    Is the truth safe? (Postgres health)

    The observer asks:
    - "Can I persist state with confidence?"
    - "Will my writes survive?"
    - "Is the source of truth intact?"

    NOT "What is the connection pool utilization?"
    """

    health: HealthLevel
    persistence_confidence: float  # 0-1: Can I persist safely?
    truth_integrity: float  # 0-1: Is the data consistent?
    write_capacity: float  # 0-1: Can I write more?
    timestamp: str | None = None

    @classmethod
    def from_postgres_pulse(cls, pulse: PostgresPulse) -> "DurabilitySignal":
        """
        Natural transformation: PostgresPulse -> DurabilitySignal.

        This is eta_Postgres in the categorical sense.
        """
        # Compute semantic metrics from vendor metrics
        pool_available = (
            1 - (pulse.pool_active / pulse.pool_max) if pulse.pool_max > 0 else 0
        )

        # Write capacity is available pool + no waiters
        write_capacity = pool_available if pulse.pool_waiting == 0 else pool_available * 0.5

        # Persistence confidence derived from replication status
        # If replication lag is high, confidence drops
        if pulse.replication_lag_bytes > 0:
            # 10MB lag = 50% confidence drop
            replication_factor = max(0, 1 - (pulse.replication_lag_bytes / 10_000_000))
            persistence_confidence = pool_available * replication_factor
        else:
            persistence_confidence = pool_available

        # Truth integrity: derived from WAL flush status
        # Unflushed WAL bytes indicate risk
        if pulse.wal_bytes_unflushed > 1_000_000:  # 1MB threshold
            truth_integrity = 0.8
        else:
            truth_integrity = 1.0

        # Determine health level
        if pool_available > 0.5 and pulse.avg_latency_ms < 20:
            health = HealthLevel.THRIVING
        elif pool_available > 0.2 and pulse.avg_latency_ms < 100:
            health = HealthLevel.HEALTHY
        elif pool_available > 0.1:
            health = HealthLevel.STRAINED
        elif pulse.pool_waiting > 0:
            health = HealthLevel.DEGRADED
        else:
            health = HealthLevel.CRITICAL

        return cls(
            health=health,
            persistence_confidence=max(0.0, min(1.0, persistence_confidence)),
            truth_integrity=truth_integrity,
            write_capacity=max(0.0, min(1.0, write_capacity)),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def mock(cls, health: HealthLevel = HealthLevel.HEALTHY) -> "DurabilitySignal":
        """Create a mock signal for testing."""
        return cls(
            health=health,
            persistence_confidence=0.9 if health != HealthLevel.CRITICAL else 0.1,
            truth_integrity=1.0 if health != HealthLevel.CRITICAL else 0.5,
            write_capacity=0.8 if health != HealthLevel.CRITICAL else 0.1,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(frozen=True)
class ReflexSignal:
    """
    How fast can I think? (Redis health)

    The observer asks:
    - "Can I access cached state quickly?"
    - "Is my working memory responsive?"
    - "Can I recall recent thoughts?"

    NOT "What is the Redis memory utilization?"
    """

    health: HealthLevel
    thought_speed: float  # 0-1: How fast can I recall?
    memory_pressure: float  # 0-1: How full is working memory?
    recall_reliability: float  # 0-1: Hit rate (can I find what I cached?)
    timestamp: str | None = None

    @classmethod
    def from_redis_pulse(cls, pulse: RedisPulse) -> "ReflexSignal":
        """
        Natural transformation: RedisPulse -> ReflexSignal.

        This is eta_Redis in the categorical sense.
        """
        # Memory pressure: how close to limit
        memory_pressure = (
            pulse.memory_used_mb / pulse.memory_max_mb
            if pulse.memory_max_mb > 0
            else 0.0
        )

        # Thought speed: inverse of memory pressure (more room = faster)
        thought_speed = 1 - memory_pressure

        # If evictions are happening, thought speed drops
        if pulse.evictions_per_second > 0:
            thought_speed *= 0.7

        # Recall reliability is directly the hit rate
        recall_reliability = pulse.hit_rate

        # Determine health level
        if recall_reliability > 0.9 and memory_pressure < 0.7:
            health = HealthLevel.THRIVING
        elif recall_reliability > 0.7 and memory_pressure < 0.9:
            health = HealthLevel.HEALTHY
        elif recall_reliability > 0.5:
            health = HealthLevel.STRAINED
        elif pulse.evictions_per_second > 10:
            health = HealthLevel.DEGRADED
        else:
            health = HealthLevel.HEALTHY if memory_pressure < 0.9 else HealthLevel.DEGRADED

        return cls(
            health=health,
            thought_speed=max(0.0, min(1.0, thought_speed)),
            memory_pressure=max(0.0, min(1.0, memory_pressure)),
            recall_reliability=max(0.0, min(1.0, recall_reliability)),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def mock(cls, health: HealthLevel = HealthLevel.HEALTHY) -> "ReflexSignal":
        """Create a mock signal for testing."""
        return cls(
            health=health,
            thought_speed=0.9 if health != HealthLevel.CRITICAL else 0.2,
            memory_pressure=0.3 if health != HealthLevel.CRITICAL else 0.95,
            recall_reliability=0.85 if health != HealthLevel.CRITICAL else 0.3,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(frozen=True)
class ResonanceSignal:
    """
    Can I remember similar things? (Qdrant health)

    The observer asks:
    - "Can semantic search find relevant memories?"
    - "Is the derived view coherent with truth?"
    - "Can I associate ideas?"

    NOT "What is the Qdrant vector count?"

    The KEY metric here is coherency_with_truth, which derives from
    the CDC lag. This is the categorical invariant that tells us
    if the Synapse functor is behaving correctly.
    """

    health: HealthLevel
    associative_capacity: float  # 0-1: How many associations can I make?
    search_responsiveness: float  # 0-1: How fast can I search?
    coherency_with_truth: float  # 0-1: Is Qdrant in sync with Postgres?
    timestamp: str | None = None

    @classmethod
    def from_qdrant_pulse(
        cls,
        pulse: QdrantPulse,
        cdc_lag_ms: float = 0,
    ) -> "ResonanceSignal":
        """
        Natural transformation: QdrantPulse -> ResonanceSignal.

        This is eta_Qdrant in the categorical sense.

        Args:
            pulse: Raw Qdrant metrics
            cdc_lag_ms: CDC lag from Synapse (THE KEY METRIC)
        """
        # Coherency degrades as CDC lag increases
        # 0ms = perfect, 5000ms = zero coherency
        threshold_ms = 5000.0
        coherency = max(0.0, min(1.0, 1.0 - (cdc_lag_ms / threshold_ms)))

        # Search responsiveness: inverse of latency
        # 0ms = 1.0, 500ms = 0.0
        search_responsiveness = max(0.0, 1.0 - (pulse.avg_search_latency_ms / 500))

        # Associative capacity: simple presence check
        # In production, would check against collection limits
        associative_capacity = 1.0 if pulse.collection_status == "green" else 0.5

        # Determine health level (coherency is the key factor)
        if coherency > 0.9 and pulse.avg_search_latency_ms < 50:
            health = HealthLevel.THRIVING
        elif coherency > 0.7 and pulse.avg_search_latency_ms < 200:
            health = HealthLevel.HEALTHY
        elif coherency > 0.5:
            health = HealthLevel.STRAINED
        elif coherency > 0.2:
            health = HealthLevel.DEGRADED
        else:
            health = HealthLevel.CRITICAL

        return cls(
            health=health,
            associative_capacity=associative_capacity,
            search_responsiveness=search_responsiveness,
            coherency_with_truth=coherency,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def from_synapse_lag(
        cls,
        tracker: "CDCLagTracker",
        pulse: QdrantPulse,
    ) -> "ResonanceSignal":
        """
        Natural transformation: (CDCLag, QdrantPulse) -> ResonanceSignal.

        This is the key integration point where the Synapse's
        CDCLagTracker feeds into semantic metrics.

        Args:
            tracker: CDCLagTracker from Synapse
            pulse: Raw Qdrant metrics
        """
        return cls.from_qdrant_pulse(pulse, cdc_lag_ms=tracker.avg_lag_ms)

    @classmethod
    def mock(
        cls,
        health: HealthLevel = HealthLevel.HEALTHY,
        coherency: float = 0.9,
    ) -> "ResonanceSignal":
        """Create a mock signal for testing."""
        return cls(
            health=health,
            associative_capacity=1.0 if health != HealthLevel.CRITICAL else 0.3,
            search_responsiveness=0.9 if health != HealthLevel.CRITICAL else 0.2,
            coherency_with_truth=coherency,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# ─────────────────────────────────────────────────────────────
# Aggregate Health (The Triad as One)
# ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TriadHealth:
    """
    Aggregate health of the Database Triad.

    The observer sees one signal: "Is my state infrastructure working?"

    The Triad is healthy when:
    1. Durability is high (truth is safe)
    2. Reflex is responsive (cache is fast)
    3. Resonance is coherent (derived view matches truth)

    The worst-of semantics ensure we don't hide problems.
    """

    durability: DurabilitySignal
    reflex: ReflexSignal
    resonance: ResonanceSignal

    @property
    def overall_health(self) -> HealthLevel:
        """
        Aggregate health (worst-of).

        If any component is critical, the triad is critical.
        """
        levels = [
            self.durability.health,
            self.reflex.health,
            self.resonance.health,
        ]
        priority = [
            HealthLevel.CRITICAL,
            HealthLevel.DEGRADED,
            HealthLevel.STRAINED,
            HealthLevel.HEALTHY,
            HealthLevel.THRIVING,
        ]
        for level in priority:
            if level in levels:
                return level
        return HealthLevel.HEALTHY

    @property
    def is_coherent(self) -> bool:
        """
        True if the functor stack is coherent.

        This is the key categorical invariant: is the derived view
        (Qdrant) faithfully representing the source of truth (Postgres)?
        """
        return self.resonance.coherency_with_truth > 0.7

    @property
    def can_persist(self) -> bool:
        """True if we can safely persist state."""
        return self.durability.persistence_confidence > 0.5

    @property
    def can_recall(self) -> bool:
        """True if we can reliably recall cached state."""
        return self.reflex.recall_reliability > 0.5

    @property
    def can_associate(self) -> bool:
        """True if semantic search is functional."""
        return (
            self.resonance.search_responsiveness > 0.3
            and self.resonance.coherency_with_truth > 0.5
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary for API responses."""
        return {
            "overall_health": self.overall_health.value,
            "is_coherent": self.is_coherent,
            "durability": {
                "health": self.durability.health.value,
                "persistence_confidence": self.durability.persistence_confidence,
                "truth_integrity": self.durability.truth_integrity,
                "write_capacity": self.durability.write_capacity,
            },
            "reflex": {
                "health": self.reflex.health.value,
                "thought_speed": self.reflex.thought_speed,
                "memory_pressure": self.reflex.memory_pressure,
                "recall_reliability": self.reflex.recall_reliability,
            },
            "resonance": {
                "health": self.resonance.health.value,
                "associative_capacity": self.resonance.associative_capacity,
                "search_responsiveness": self.resonance.search_responsiveness,
                "coherency_with_truth": self.resonance.coherency_with_truth,
            },
        }

    @classmethod
    def mock(cls, health: HealthLevel = HealthLevel.HEALTHY) -> "TriadHealth":
        """Create a mock triad for testing."""
        return cls(
            durability=DurabilitySignal.mock(health),
            reflex=ReflexSignal.mock(health),
            resonance=ResonanceSignal.mock(health),
        )


# ─────────────────────────────────────────────────────────────
# Collector (Assembles Signals from Pulses)
# ─────────────────────────────────────────────────────────────


class SemanticMetricsCollector:
    """
    Collects vendor pulses and transforms to semantic signals.

    This is the runtime component that:
    1. Polls vendor metrics (or receives them via push)
    2. Applies natural transformations
    3. Produces TriadHealth for observers

    In production, this would connect to real Prometheus/metrics endpoints.
    For now, it accepts pulses directly.
    """

    def __init__(self, cdc_lag_tracker: "CDCLagTracker | None" = None) -> None:
        """
        Initialize the collector.

        Args:
            cdc_lag_tracker: Optional CDCLagTracker from Synapse.
                           If provided, coherency_with_truth will be computed.
        """
        self._cdc_lag_tracker = cdc_lag_tracker
        self._last_postgres_pulse: PostgresPulse | None = None
        self._last_redis_pulse: RedisPulse | None = None
        self._last_qdrant_pulse: QdrantPulse | None = None

    def update_postgres(self, pulse: PostgresPulse) -> DurabilitySignal:
        """Update Postgres metrics and return semantic signal."""
        self._last_postgres_pulse = pulse
        return DurabilitySignal.from_postgres_pulse(pulse)

    def update_redis(self, pulse: RedisPulse) -> ReflexSignal:
        """Update Redis metrics and return semantic signal."""
        self._last_redis_pulse = pulse
        return ReflexSignal.from_redis_pulse(pulse)

    def update_qdrant(self, pulse: QdrantPulse) -> ResonanceSignal:
        """Update Qdrant metrics and return semantic signal."""
        self._last_qdrant_pulse = pulse

        # Use CDC lag tracker if available
        if self._cdc_lag_tracker is not None:
            return ResonanceSignal.from_synapse_lag(self._cdc_lag_tracker, pulse)
        else:
            return ResonanceSignal.from_qdrant_pulse(pulse)

    def collect(self) -> TriadHealth | None:
        """
        Collect current triad health.

        Returns None if any pulse is missing.
        """
        if self._last_postgres_pulse is None:
            return None
        if self._last_redis_pulse is None:
            return None
        if self._last_qdrant_pulse is None:
            return None

        return TriadHealth(
            durability=DurabilitySignal.from_postgres_pulse(self._last_postgres_pulse),
            reflex=ReflexSignal.from_redis_pulse(self._last_redis_pulse),
            resonance=self.update_qdrant(self._last_qdrant_pulse),
        )

    def set_cdc_lag_tracker(self, tracker: "CDCLagTracker") -> None:
        """Wire up the CDC lag tracker from Synapse."""
        self._cdc_lag_tracker = tracker
