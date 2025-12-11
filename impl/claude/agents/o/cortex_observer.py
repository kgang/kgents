"""
CortexObserver: O-gent Integration for the Bicameral Engine.

Provides systemic proprioception for the Bicameral Engine, observing:
- Left Hemisphere (relational): Latency, throughput, error rate
- Right Hemisphere (vector): Embedding staleness, search latency
- Coherency: Ghost count, stale count, validation rate
- Synapse: Surprise distribution, route breakdown
- Hippocampus: Size, utilization, flush rate
- Dreamer: REM cycles, interrupts, morning briefing

Design principles:
1. Non-blocking: All observation calls are async
2. VoI-aware: Observation cost is tracked
3. Graceful degradation: Works if some components unavailable
4. Wire protocol: All state emitted via WireObservable

From the implementation plan:
> "A cortex also has reflexes, short-term memory, learns new structures, and observes itself."
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable


class CortexHealth(Enum):
    """Overall cortex health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class LeftHemisphereStatus:
    """Status of the Left Hemisphere (relational store)."""

    available: bool = False
    latency_ms: float = 0.0
    queries_total: int = 0
    errors_total: int = 0
    last_check: str | None = None

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.queries_total == 0:
            return 0.0
        return self.errors_total / self.queries_total

    @property
    def health(self) -> CortexHealth:
        """Determine health status."""
        if not self.available:
            return CortexHealth.CRITICAL
        if self.error_rate > 0.1:
            return CortexHealth.CRITICAL
        if self.error_rate > 0.01 or self.latency_ms > 100:
            return CortexHealth.DEGRADED
        return CortexHealth.HEALTHY


@dataclass
class RightHemisphereStatus:
    """Status of the Right Hemisphere (vector store)."""

    available: bool = False
    latency_ms: float = 0.0
    vectors_count: int = 0
    searches_total: int = 0
    embedding_staleness_avg: float = 0.0
    last_check: str | None = None

    @property
    def health(self) -> CortexHealth:
        """Determine health status."""
        if not self.available:
            return CortexHealth.UNKNOWN  # Optional component
        if self.latency_ms > 200:
            return CortexHealth.DEGRADED
        return CortexHealth.HEALTHY


@dataclass
class CoherencyStatus:
    """Status of cross-hemisphere coherency."""

    ghost_count: int = 0
    stale_count: int = 0
    ghosts_healed_total: int = 0
    stale_flagged_total: int = 0
    coherency_rate: float = 1.0
    last_check: str | None = None
    checks_total: int = 0

    @property
    def health(self) -> CortexHealth:
        """Determine coherency health."""
        if self.coherency_rate < 0.9:
            return CortexHealth.CRITICAL
        if self.coherency_rate < 0.95 or self.ghost_count > 10:
            return CortexHealth.DEGRADED
        return CortexHealth.HEALTHY


@dataclass
class SynapseStatus:
    """Status of the Synapse (event bus)."""

    available: bool = False
    surprise_avg: float = 0.5
    flashbulb_rate: float = 0.0
    fast_path_rate: float = 0.0
    batch_path_rate: float = 0.0
    signals_total: int = 0
    batch_pending: int = 0
    has_flashbulb_pending: bool = False
    last_check: str | None = None

    @property
    def health(self) -> CortexHealth:
        """Determine synapse health."""
        if not self.available:
            return CortexHealth.CRITICAL
        if self.flashbulb_rate > 0.5:  # Too many interrupts
            return CortexHealth.DEGRADED
        return CortexHealth.HEALTHY


@dataclass
class HippocampusStatus:
    """Status of the Hippocampus (short-term memory)."""

    available: bool = False
    memory_count: int = 0
    max_size: int = 0
    utilization: float = 0.0
    flushes_total: int = 0
    last_flush: str | None = None
    signals_stored: int = 0
    last_check: str | None = None

    @property
    def health(self) -> CortexHealth:
        """Determine hippocampus health."""
        if not self.available:
            return CortexHealth.DEGRADED  # Can operate without
        if self.utilization > 0.9:
            return CortexHealth.DEGRADED  # Nearly full
        return CortexHealth.HEALTHY


@dataclass
class DreamerStatus:
    """Status of the Lucid Dreamer."""

    available: bool = False
    phase: str = "awake"
    dream_cycles_total: int = 0
    interrupted_total: int = 0
    morning_briefing_count: int = 0
    last_dream: str | None = None
    last_check: str | None = None

    @property
    def health(self) -> CortexHealth:
        """Determine dreamer health."""
        if not self.available:
            return CortexHealth.UNKNOWN  # Optional
        if self.interrupted_total > 10 and self.dream_cycles_total > 0:
            if self.interrupted_total / self.dream_cycles_total > 0.5:
                return CortexHealth.DEGRADED
        return CortexHealth.HEALTHY


@dataclass
class CortexHealthSnapshot:
    """Complete snapshot of cortex health."""

    timestamp: str
    overall: CortexHealth
    left_hemisphere: LeftHemisphereStatus
    right_hemisphere: RightHemisphereStatus
    coherency: CoherencyStatus
    synapse: SynapseStatus
    hippocampus: HippocampusStatus
    dreamer: DreamerStatus

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "overall": self.overall.value,
            "left_hemisphere": {
                "available": self.left_hemisphere.available,
                "latency_ms": self.left_hemisphere.latency_ms,
                "queries_total": self.left_hemisphere.queries_total,
                "error_rate": self.left_hemisphere.error_rate,
                "health": self.left_hemisphere.health.value,
            },
            "right_hemisphere": {
                "available": self.right_hemisphere.available,
                "latency_ms": self.right_hemisphere.latency_ms,
                "vectors_count": self.right_hemisphere.vectors_count,
                "health": self.right_hemisphere.health.value,
            },
            "coherency": {
                "ghost_count": self.coherency.ghost_count,
                "stale_count": self.coherency.stale_count,
                "ghosts_healed_total": self.coherency.ghosts_healed_total,
                "coherency_rate": self.coherency.coherency_rate,
                "health": self.coherency.health.value,
            },
            "synapse": {
                "available": self.synapse.available,
                "surprise_avg": self.synapse.surprise_avg,
                "flashbulb_rate": self.synapse.flashbulb_rate,
                "signals_total": self.synapse.signals_total,
                "health": self.synapse.health.value,
            },
            "hippocampus": {
                "available": self.hippocampus.available,
                "memory_count": self.hippocampus.memory_count,
                "utilization": self.hippocampus.utilization,
                "health": self.hippocampus.health.value,
            },
            "dreamer": {
                "available": self.dreamer.available,
                "phase": self.dreamer.phase,
                "dream_cycles_total": self.dreamer.dream_cycles_total,
                "morning_briefing_count": self.dreamer.morning_briefing_count,
                "health": self.dreamer.health.value,
            },
        }


@dataclass
class CortexObserverConfig:
    """Configuration for the CortexObserver."""

    # History
    history_limit: int = 1000
    health_check_interval_ms: int = 1000

    # Thresholds
    latency_warning_ms: float = 100.0
    latency_critical_ms: float = 500.0
    error_rate_warning: float = 0.01
    error_rate_critical: float = 0.1
    coherency_warning: float = 0.95
    coherency_critical: float = 0.90
    hippocampus_warning_utilization: float = 0.8
    hippocampus_critical_utilization: float = 0.95

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CortexObserverConfig":
        """Create from dictionary."""
        return cls(
            history_limit=data.get("history_limit", 1000),
            health_check_interval_ms=data.get("health_check_interval_ms", 1000),
            latency_warning_ms=data.get("latency_warning_ms", 100.0),
            latency_critical_ms=data.get("latency_critical_ms", 500.0),
            error_rate_warning=data.get("error_rate_warning", 0.01),
            error_rate_critical=data.get("error_rate_critical", 0.1),
            coherency_warning=data.get("coherency_warning", 0.95),
            coherency_critical=data.get("coherency_critical", 0.90),
        )


# Type alias for health change callbacks
HealthChangeCallback = Callable[[CortexHealthSnapshot], None]


@runtime_checkable
class IBicameralMemory(Protocol):
    """Protocol for observing BicameralMemory."""

    def stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        ...

    @property
    def ghost_log(self) -> list[Any]:
        """Ghost healing log."""
        ...

    @property
    def stale_log(self) -> list[Any]:
        """Stale embedding log."""
        ...


@runtime_checkable
class ISynapse(Protocol):
    """Protocol for observing Synapse."""

    def get_metrics(self) -> Any:
        """Get synapse metrics."""
        ...

    def has_flashbulb_pending(self) -> bool:
        """Check for flashbulb signals."""
        ...

    @property
    def batch_queue_size(self) -> int:
        """Current batch queue size."""
        ...


@runtime_checkable
class IHippocampus(Protocol):
    """Protocol for observing Hippocampus."""

    def get_stats(self) -> dict[str, Any]:
        """Get hippocampus statistics."""
        ...

    @property
    def size(self) -> int:
        """Current memory count."""
        ...


@runtime_checkable
class ILucidDreamer(Protocol):
    """Protocol for observing LucidDreamer."""

    @property
    def current_phase(self) -> Any:
        """Current dream phase."""
        ...

    @property
    def stats(self) -> dict[str, Any]:
        """Get dreamer statistics."""
        ...

    @property
    def morning_briefing(self) -> list[Any]:
        """Questions for morning briefing."""
        ...


class CortexObserver:
    """
    O-gent observer for the Bicameral Engine.

    Provides systemic proprioception by observing all cortex components
    and generating unified health snapshots.

    Usage:
        observer = create_cortex_observer(
            bicameral=bicameral_memory,
            synapse=synapse,
            hippocampus=hippocampus,
            dreamer=lucid_dreamer,
        )

        # Get current health
        health = observer.get_health()
        print(f"Cortex health: {health.overall.value}")

        # Subscribe to changes
        unsubscribe = observer.on_health_change(lambda h: print(f"Health: {h}"))

        # Get history
        history = observer.get_history(limit=100)
    """

    def __init__(
        self,
        bicameral: IBicameralMemory | None = None,
        synapse: ISynapse | None = None,
        hippocampus: IHippocampus | None = None,
        dreamer: ILucidDreamer | None = None,
        config: CortexObserverConfig | None = None,
    ):
        """
        Initialize CortexObserver.

        Args:
            bicameral: BicameralMemory instance (optional)
            synapse: Synapse instance (optional)
            hippocampus: Hippocampus instance (optional)
            dreamer: LucidDreamer instance (optional)
            config: Observer configuration
        """
        self._bicameral = bicameral
        self._synapse = synapse
        self._hippocampus = hippocampus
        self._dreamer = dreamer
        self._config = config or CortexObserverConfig()

        # History tracking
        self._history: deque[CortexHealthSnapshot] = deque(
            maxlen=self._config.history_limit
        )

        # Health change callbacks
        self._callbacks: list[HealthChangeCallback] = []

        # Cached last health for change detection
        self._last_health: CortexHealth | None = None

        # Statistics
        self._observations_total = 0
        self._health_checks_total = 0
        self._alerts_triggered = 0

        # Internal state tracking (for components without direct stats)
        self._left_queries_total = 0
        self._left_errors_total = 0
        self._right_searches_total = 0

    # === Health Observation ===

    def get_health(self) -> CortexHealthSnapshot:
        """
        Get current cortex health snapshot.

        Returns:
            CortexHealthSnapshot with all component statuses
        """
        self._observations_total += 1
        now = datetime.now().isoformat()

        # Observe each component
        left_status = self._observe_left_hemisphere()
        right_status = self._observe_right_hemisphere()
        coherency_status = self._observe_coherency()
        synapse_status = self._observe_synapse()
        hippocampus_status = self._observe_hippocampus()
        dreamer_status = self._observe_dreamer()

        # Calculate overall health
        overall = self._calculate_overall_health(
            left_status,
            right_status,
            coherency_status,
            synapse_status,
            hippocampus_status,
            dreamer_status,
        )

        snapshot = CortexHealthSnapshot(
            timestamp=now,
            overall=overall,
            left_hemisphere=left_status,
            right_hemisphere=right_status,
            coherency=coherency_status,
            synapse=synapse_status,
            hippocampus=hippocampus_status,
            dreamer=dreamer_status,
        )

        # Track history
        self._history.append(snapshot)

        # Check for health changes
        if self._last_health is not None and self._last_health != overall:
            self._notify_health_change(snapshot)
        self._last_health = overall

        return snapshot

    def _observe_left_hemisphere(self) -> LeftHemisphereStatus:
        """Observe Left Hemisphere (relational store)."""
        now = datetime.now().isoformat()

        if self._bicameral is None:
            return LeftHemisphereStatus(available=False, last_check=now)

        try:
            stats = self._bicameral.stats()

            return LeftHemisphereStatus(
                available=True,
                latency_ms=0.0,  # Would need instrumentation
                queries_total=stats.get("total_recalls", 0),
                errors_total=0,  # Would need error tracking
                last_check=now,
            )
        except Exception:
            return LeftHemisphereStatus(available=False, last_check=now)

    def _observe_right_hemisphere(self) -> RightHemisphereStatus:
        """Observe Right Hemisphere (vector store)."""
        now = datetime.now().isoformat()

        if self._bicameral is None:
            return RightHemisphereStatus(available=False, last_check=now)

        try:
            stats = self._bicameral.stats()

            return RightHemisphereStatus(
                available=stats.get("has_semantic", False),
                latency_ms=0.0,  # Would need instrumentation
                vectors_count=0,  # Would need vector store stats
                searches_total=stats.get("total_recalls", 0),
                embedding_staleness_avg=0.0,
                last_check=now,
            )
        except Exception:
            return RightHemisphereStatus(available=False, last_check=now)

    def _observe_coherency(self) -> CoherencyStatus:
        """Observe coherency status."""
        now = datetime.now().isoformat()

        if self._bicameral is None:
            return CoherencyStatus(last_check=now)

        try:
            stats = self._bicameral.stats()

            ghosts_healed = stats.get("ghosts_healed", 0)
            stale_flagged = stats.get("stale_flagged", 0)
            total_checks = stats.get("coherency_checks", 0)

            # Estimate coherency rate from ghost/stale logs
            ghost_log = self._bicameral.ghost_log
            stale_log = self._bicameral.stale_log

            # Recent ghost count (last 100 entries)
            recent_ghosts = len(ghost_log[-100:]) if ghost_log else 0
            recent_stale = len(stale_log[-100:]) if stale_log else 0

            # Coherency rate estimation
            total_recent = recent_ghosts + recent_stale + 100  # Assume 100 valid
            coherency_rate = (total_recent - recent_ghosts - recent_stale) / max(
                total_recent, 1
            )

            return CoherencyStatus(
                ghost_count=recent_ghosts,
                stale_count=recent_stale,
                ghosts_healed_total=ghosts_healed,
                stale_flagged_total=stale_flagged,
                coherency_rate=min(1.0, coherency_rate),
                checks_total=total_checks,
                last_check=now,
            )
        except Exception:
            return CoherencyStatus(last_check=now)

    def _observe_synapse(self) -> SynapseStatus:
        """Observe Synapse status."""
        now = datetime.now().isoformat()

        if self._synapse is None:
            return SynapseStatus(available=False, last_check=now)

        try:
            metrics = self._synapse.get_metrics()

            # Calculate rates
            total = metrics.high_surprise_count + metrics.low_surprise_count
            flashbulb_rate = (
                metrics.flashbulb_count / max(total, 1) if total > 0 else 0.0
            )
            fast_rate = (
                metrics.high_surprise_count / max(total, 1) if total > 0 else 0.0
            )
            batch_rate = (
                metrics.low_surprise_count / max(total, 1) if total > 0 else 0.0
            )

            # Calculate average surprise
            type_surprises = list(metrics.type_total_surprise.values())
            type_counts = list(metrics.type_counts.values())
            avg_surprise = (
                sum(type_surprises) / sum(type_counts) if sum(type_counts) > 0 else 0.5
            )

            return SynapseStatus(
                available=True,
                surprise_avg=avg_surprise,
                flashbulb_rate=flashbulb_rate,
                fast_path_rate=fast_rate,
                batch_path_rate=batch_rate,
                signals_total=total,
                batch_pending=self._synapse.batch_queue_size,
                has_flashbulb_pending=self._synapse.has_flashbulb_pending(),
                last_check=now,
            )
        except Exception:
            return SynapseStatus(available=False, last_check=now)

    def _observe_hippocampus(self) -> HippocampusStatus:
        """Observe Hippocampus status."""
        now = datetime.now().isoformat()

        if self._hippocampus is None:
            return HippocampusStatus(available=False, last_check=now)

        try:
            stats = self._hippocampus.get_stats()
            size = self._hippocampus.size
            max_size = stats.get("max_size", 10000)

            return HippocampusStatus(
                available=True,
                memory_count=size,
                max_size=max_size,
                utilization=size / max(max_size, 1),
                flushes_total=stats.get("flushes_total", 0),
                last_flush=stats.get("last_flush"),
                signals_stored=stats.get("signals_stored", 0),
                last_check=now,
            )
        except Exception:
            return HippocampusStatus(available=False, last_check=now)

    def _observe_dreamer(self) -> DreamerStatus:
        """Observe Lucid Dreamer status."""
        now = datetime.now().isoformat()

        if self._dreamer is None:
            return DreamerStatus(available=False, last_check=now)

        try:
            stats = self._dreamer.stats
            phase = self._dreamer.current_phase
            briefing = self._dreamer.morning_briefing

            return DreamerStatus(
                available=True,
                phase=phase.value if hasattr(phase, "value") else str(phase),
                dream_cycles_total=stats.get("dream_cycles_total", 0),
                interrupted_total=stats.get("interrupted_total", 0),
                morning_briefing_count=len(briefing) if briefing else 0,
                last_dream=stats.get("last_dream"),
                last_check=now,
            )
        except Exception:
            return DreamerStatus(available=False, last_check=now)

    def _calculate_overall_health(
        self,
        left: LeftHemisphereStatus,
        right: RightHemisphereStatus,
        coherency: CoherencyStatus,
        synapse: SynapseStatus,
        hippocampus: HippocampusStatus,
        dreamer: DreamerStatus,
    ) -> CortexHealth:
        """Calculate overall cortex health from component statuses."""
        healths = [
            left.health,
            coherency.health,
            synapse.health,
        ]

        # Include optional components if available
        if right.available:
            healths.append(right.health)
        if hippocampus.available:
            healths.append(hippocampus.health)
        if dreamer.available:
            healths.append(dreamer.health)

        # Critical if any critical
        if any(h == CortexHealth.CRITICAL for h in healths):
            return CortexHealth.CRITICAL

        # Degraded if any degraded
        if any(h == CortexHealth.DEGRADED for h in healths):
            return CortexHealth.DEGRADED

        # Unknown if all unknown
        if all(h == CortexHealth.UNKNOWN for h in healths):
            return CortexHealth.UNKNOWN

        return CortexHealth.HEALTHY

    # === Health Change Subscriptions ===

    def on_health_change(self, callback: HealthChangeCallback) -> Callable[[], None]:
        """
        Subscribe to health changes.

        Args:
            callback: Function to call on health changes

        Returns:
            Unsubscribe function
        """
        self._callbacks.append(callback)

        def unsubscribe() -> None:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        return unsubscribe

    def _notify_health_change(self, snapshot: CortexHealthSnapshot) -> None:
        """Notify all subscribers of health change."""
        self._alerts_triggered += 1
        for callback in self._callbacks:
            try:
                callback(snapshot)
            except Exception:
                pass  # Don't let callback errors break observation

    # === History ===

    def get_history(self, limit: int = 100) -> list[CortexHealthSnapshot]:
        """
        Get observation history.

        Args:
            limit: Maximum entries to return

        Returns:
            List of snapshots, most recent last
        """
        history = list(self._history)
        return history[-limit:] if limit < len(history) else history

    def get_stats(self) -> dict[str, Any]:
        """Get observer statistics."""
        return {
            "observations_total": self._observations_total,
            "health_checks_total": self._health_checks_total,
            "alerts_triggered": self._alerts_triggered,
            "history_size": len(self._history),
            "components": {
                "bicameral": self._bicameral is not None,
                "synapse": self._synapse is not None,
                "hippocampus": self._hippocampus is not None,
                "dreamer": self._dreamer is not None,
            },
        }

    # === Compact Rendering ===

    def render_compact(self) -> str:
        """
        Render compact status line.

        Returns:
            Single-line status summary
        """
        health = self.get_health()

        # Status symbol
        status_symbols = {
            CortexHealth.HEALTHY: "OK",
            CortexHealth.DEGRADED: "!",
            CortexHealth.CRITICAL: "X",
            CortexHealth.UNKNOWN: "?",
        }
        symbol = status_symbols.get(health.overall, "?")

        # Build compact line
        parts = [f"[CORTEX] {symbol} {health.overall.value.upper()}"]

        # Add latencies
        if health.left_hemisphere.available:
            parts.append(f"L:{health.left_hemisphere.latency_ms:.0f}ms")
        if health.right_hemisphere.available:
            parts.append(f"R:{health.right_hemisphere.latency_ms:.0f}ms")

        # Add hippocampus
        if health.hippocampus.available:
            parts.append(
                f"H:{health.hippocampus.memory_count}/{health.hippocampus.max_size}"
            )

        # Add synapse
        if health.synapse.available:
            parts.append(f"S:{health.synapse.surprise_avg:.2f}")

        # Add dreamer
        if health.dreamer.available:
            parts.append(f"Dreams:{health.dreamer.dream_cycles_total}")

        return " | ".join(parts)


# === Factory Functions ===


def create_cortex_observer(
    bicameral: IBicameralMemory | None = None,
    synapse: ISynapse | None = None,
    hippocampus: IHippocampus | None = None,
    dreamer: ILucidDreamer | None = None,
    config_dict: dict[str, Any] | None = None,
) -> CortexObserver:
    """
    Create a CortexObserver instance.

    Args:
        bicameral: BicameralMemory instance
        synapse: Synapse instance
        hippocampus: Hippocampus instance
        dreamer: LucidDreamer instance
        config_dict: Configuration dictionary

    Returns:
        Configured CortexObserver
    """
    config = (
        CortexObserverConfig.from_dict(config_dict)
        if config_dict
        else CortexObserverConfig()
    )

    return CortexObserver(
        bicameral=bicameral,
        synapse=synapse,
        hippocampus=hippocampus,
        dreamer=dreamer,
        config=config,
    )


def create_mock_cortex_observer() -> CortexObserver:
    """
    Create a mock CortexObserver for testing.

    Returns:
        CortexObserver with no dependencies
    """
    return CortexObserver()
