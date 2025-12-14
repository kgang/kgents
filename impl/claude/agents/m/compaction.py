"""
Compaction: Purposeful Forgetting as Accursed Share.

The fourth pillar: Graceful Degradation via Compression.

Compaction is not deletion—it's resolution reduction. The holographic
property ensures all memories remain at lower fidelity, rather than
some memories being lost entirely.

Key Concepts:
- Compactor: Applies compression policies to crystals
- AutoCompactionDaemon: Background process that triggers compaction
- CompactionPolicy: Rules for when and how to compact
- CompactionEvent: Record of a compaction operation

The categorical insight: compaction is an endofunctor on MemoryCrystal
that preserves structure while reducing dimension.

    compact: Crystal[T] → Crystal[T]

Where dim(compact(c)) ≤ dim(c) and concepts(compact(c)) = concepts(c).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from .crystal import MemoryCrystal
    from .inference import InferenceGuidedCrystal
    from .substrate import Allocation, SharedSubstrate

T = TypeVar("T")


# =============================================================================
# Compaction Policy
# =============================================================================


@dataclass
class CompactionPolicy:
    """
    Rules for when and how to compact memory.

    The policy balances:
    - Memory pressure (quota usage)
    - Resolution preservation (don't compress too much)
    - Frequency (don't compact too often)

    Categorical insight: The policy is a predicate that decides
    when the compaction functor should be applied.
    """

    # Pressure thresholds
    pressure_threshold: float = 0.8  # Compact when usage > 80%
    critical_threshold: float = 0.95  # Emergency compact when > 95%

    # Compression ratios
    normal_ratio: float = 0.8  # 20% resolution loss per compaction
    aggressive_ratio: float = 0.5  # 50% for critical pressure

    # Frequency limits
    min_interval: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    max_compactions_per_hour: int = 4

    # Resolution floor (never compress below this)
    min_resolution: float = 0.1

    def should_compact(
        self,
        current_pressure: float,
        last_compaction: datetime | None,
        compactions_last_hour: int,
    ) -> tuple[bool, float, str]:
        """
        Evaluate whether to compact.

        Args:
            current_pressure: Current memory pressure (0 to 1)
            last_compaction: When last compaction occurred
            compactions_last_hour: Number of compactions in last hour

        Returns:
            (should_compact, ratio, reason)
        """
        # Check rate limit
        if compactions_last_hour >= self.max_compactions_per_hour:
            return (False, 1.0, "Rate limit reached")

        # Check interval
        if last_compaction:
            elapsed = datetime.now() - last_compaction
            if elapsed < self.min_interval:
                # Exception: critical pressure overrides interval
                if current_pressure >= self.critical_threshold:
                    return (True, self.aggressive_ratio, "Critical pressure override")
                return (False, 1.0, f"Too soon (wait {self.min_interval - elapsed})")

        # Check pressure
        if current_pressure >= self.critical_threshold:
            return (
                True,
                self.aggressive_ratio,
                f"Critical pressure: {current_pressure:.0%}",
            )

        if current_pressure >= self.pressure_threshold:
            return (True, self.normal_ratio, f"High pressure: {current_pressure:.0%}")

        return (False, 1.0, f"Pressure OK: {current_pressure:.0%}")


# =============================================================================
# Compaction Event
# =============================================================================


@dataclass
class CompactionEvent:
    """
    Record of a compaction operation.

    Provides audit trail for memory management.
    """

    timestamp: datetime
    target_id: str  # Agent or crystal identifier
    reason: str
    ratio: float  # Compression ratio applied
    patterns_before: int
    patterns_after: int
    resolution_before: float
    resolution_after: float
    duration_ms: float

    @property
    def patterns_preserved(self) -> bool:
        """True if all patterns were preserved."""
        return self.patterns_after == self.patterns_before

    @property
    def resolution_loss(self) -> float:
        """Resolution lost in this compaction."""
        return self.resolution_before - self.resolution_after


# =============================================================================
# Compactor
# =============================================================================


class Compactor(Generic[T]):
    """
    Applies compression to crystals based on policy.

    The Compactor is the executor of the compaction functor.
    It takes a crystal and policy, evaluates whether compaction
    is needed, and applies it if so.

    Key Properties:
    - Structure-preserving: All concepts are kept
    - Resolution-reducing: Information becomes fuzzier
    - Idempotent (up to resolution): Multiple compactions reach floor

    Example:
        compactor = Compactor(policy)

        # Compact if needed
        event = await compactor.compact(crystal, "agent_id", pressure=0.85)
        if event:
            print(f"Compacted with ratio {event.ratio}")
    """

    def __init__(self, policy: CompactionPolicy | None = None) -> None:
        """
        Initialize compactor.

        Args:
            policy: Compaction policy (default if not provided)
        """
        self._policy = policy or CompactionPolicy()
        self._events: list[CompactionEvent] = []
        self._last_compaction: dict[str, datetime] = {}

    @property
    def policy(self) -> CompactionPolicy:
        """Current compaction policy."""
        return self._policy

    @property
    def events(self) -> list[CompactionEvent]:
        """Compaction history."""
        return self._events.copy()

    def compactions_last_hour(self, target_id: str) -> int:
        """Count compactions for target in last hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        return sum(
            1 for e in self._events if e.target_id == target_id and e.timestamp > cutoff
        )

    async def compact(
        self,
        crystal: "MemoryCrystal[T]",
        target_id: str,
        pressure: float,
        force: bool = False,
    ) -> CompactionEvent | None:
        """
        Compact a crystal if policy permits.

        Args:
            crystal: The crystal to compact
            target_id: Identifier for tracking
            pressure: Current memory pressure
            force: Override policy checks

        Returns:
            CompactionEvent if compacted, None otherwise
        """
        import time

        # Check policy
        if not force:
            should, ratio, reason = self._policy.should_compact(
                current_pressure=pressure,
                last_compaction=self._last_compaction.get(target_id),
                compactions_last_hour=self.compactions_last_hour(target_id),
            )

            if not should:
                return None
        else:
            ratio = self._policy.normal_ratio
            reason = "Forced compaction"

        # Record pre-compaction state
        patterns_before = len(crystal.concepts)
        resolution_before = crystal.stats().get("avg_resolution", 1.0)

        # Perform compaction
        start = time.time()
        compressed = crystal.compress(ratio)
        duration_ms = (time.time() - start) * 1000

        # Record post-compaction state
        patterns_after = len(compressed.concepts)
        resolution_after = compressed.stats().get("avg_resolution", 1.0)

        # Create event
        event = CompactionEvent(
            timestamp=datetime.now(),
            target_id=target_id,
            reason=reason,
            ratio=ratio,
            patterns_before=patterns_before,
            patterns_after=patterns_after,
            resolution_before=resolution_before,
            resolution_after=resolution_after,
            duration_ms=duration_ms,
        )

        self._events.append(event)
        self._last_compaction[target_id] = datetime.now()

        return event

    async def compact_allocation(
        self,
        allocation: "Allocation[T]",
        force: bool = False,
    ) -> CompactionEvent | None:
        """
        Compact an allocation's crystal.

        Args:
            allocation: The allocation to compact
            force: Override policy checks

        Returns:
            CompactionEvent if compacted, None otherwise
        """
        pressure = allocation.usage_ratio()
        return await self.compact(
            crystal=allocation._crystal,
            target_id=str(allocation.agent_id),
            pressure=pressure,
            force=force,
        )

    async def compact_guided(
        self,
        guided: "InferenceGuidedCrystal[T]",
        target_id: str,
        pressure: float,
    ) -> CompactionEvent | None:
        """
        Compact using inference guidance.

        This first consolidates (promotes/demotes) based on free energy,
        then applies compression. More valuable memories retain more
        resolution.

        Args:
            guided: Inference-guided crystal
            target_id: Identifier for tracking
            pressure: Current memory pressure

        Returns:
            CompactionEvent if compacted, None otherwise
        """
        import time

        # Check policy
        should, ratio, reason = self._policy.should_compact(
            current_pressure=pressure,
            last_compaction=self._last_compaction.get(target_id),
            compactions_last_hour=self.compactions_last_hour(target_id),
        )

        if not should:
            return None

        # Record pre-compaction state
        patterns_before = len(guided.crystal.concepts)
        resolution_before = guided.crystal.stats().get("avg_resolution", 1.0)

        # Perform inference-guided compaction
        start = time.time()

        # First, consolidate based on value
        await guided.consolidate()

        # Then compress
        compressed = await guided.smart_compress(ratio)
        duration_ms = (time.time() - start) * 1000

        # Record post-compaction state
        patterns_after = len(compressed.concepts)
        resolution_after = compressed.stats().get("avg_resolution", 1.0)

        # Create event
        event = CompactionEvent(
            timestamp=datetime.now(),
            target_id=target_id,
            reason=f"Inference-guided: {reason}",
            ratio=ratio,
            patterns_before=patterns_before,
            patterns_after=patterns_after,
            resolution_before=resolution_before,
            resolution_after=resolution_after,
            duration_ms=duration_ms,
        )

        self._events.append(event)
        self._last_compaction[target_id] = datetime.now()

        return event

    def stats(self) -> dict[str, Any]:
        """Get compactor statistics."""
        if not self._events:
            return {
                "total_compactions": 0,
                "avg_ratio": 0.0,
                "avg_duration_ms": 0.0,
                "patterns_preserved": True,
            }

        return {
            "total_compactions": len(self._events),
            "avg_ratio": sum(e.ratio for e in self._events) / len(self._events),
            "avg_duration_ms": sum(e.duration_ms for e in self._events)
            / len(self._events),
            "patterns_preserved": all(e.patterns_preserved for e in self._events),
            "total_resolution_loss": sum(e.resolution_loss for e in self._events),
            "targets": list(self._last_compaction.keys()),
        }


# =============================================================================
# Auto-Compaction Daemon
# =============================================================================


class AutoCompactionDaemon:
    """
    Background daemon that triggers compaction automatically.

    Runs on a schedule, checking allocations for memory pressure
    and compacting as needed.

    The daemon embodies the "graceful forgetting" principle:
    instead of hard failures when memory fills, it proactively
    reduces resolution to make room.

    Example:
        substrate = SharedSubstrate()
        daemon = AutoCompactionDaemon(substrate)

        # Start daemon
        await daemon.start()

        # ... later ...
        await daemon.stop()
    """

    def __init__(
        self,
        substrate: "SharedSubstrate[Any]",
        compactor: Compactor[Any] | None = None,
        check_interval: timedelta | None = None,
    ) -> None:
        """
        Initialize auto-compaction daemon.

        Args:
            substrate: The shared substrate to monitor
            compactor: Compactor to use (creates default if not provided)
            check_interval: How often to check (default 5 minutes)
        """
        self._substrate = substrate
        self._compactor = compactor or Compactor()
        self._check_interval = check_interval or timedelta(minutes=5)
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._check_count = 0
        self._compaction_count = 0

    @property
    def running(self) -> bool:
        """Whether daemon is currently running."""
        return self._running

    @property
    def compactor(self) -> Compactor[Any]:
        """The compactor being used."""
        return self._compactor

    async def start(self) -> None:
        """Start the daemon."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the daemon."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        """Main daemon loop."""
        while self._running:
            try:
                await self._check_all_allocations()
                await asyncio.sleep(self._check_interval.total_seconds())
            except asyncio.CancelledError:
                break
            except Exception:
                # Log but don't crash daemon
                await asyncio.sleep(self._check_interval.total_seconds())

    async def _check_all_allocations(self) -> list[CompactionEvent]:
        """Check all allocations for compaction."""
        self._check_count += 1
        events: list[CompactionEvent] = []

        for agent_id, allocation in self._substrate.allocations.items():
            event = await self._compactor.compact_allocation(allocation)
            if event:
                events.append(event)
                self._compaction_count += 1

        return events

    async def check_once(self) -> list[CompactionEvent]:
        """
        Run a single check cycle.

        Useful for testing or manual triggers.

        Returns:
            List of compaction events from this check
        """
        return await self._check_all_allocations()

    def stats(self) -> dict[str, Any]:
        """Get daemon statistics."""
        return {
            "running": self._running,
            "check_count": self._check_count,
            "compaction_count": self._compaction_count,
            "check_interval_seconds": self._check_interval.total_seconds(),
            "allocation_count": len(self._substrate.allocations),
            "compactor_stats": self._compactor.stats(),
        }


# =============================================================================
# Compaction Strategies
# =============================================================================


@dataclass
class StrategyResult:
    """Result of applying a compaction strategy."""

    strategy_name: str
    events: list[CompactionEvent]
    total_resolution_loss: float
    patterns_affected: int


async def apply_uniform_strategy(
    substrate: "SharedSubstrate[T]",
    compactor: Compactor[T],
    ratio: float = 0.8,
) -> StrategyResult:
    """
    Apply uniform compaction to all allocations.

    All allocations get the same compression ratio.

    Args:
        substrate: The substrate to compact
        compactor: The compactor to use
        ratio: Compression ratio

    Returns:
        StrategyResult with compaction details
    """
    events: list[CompactionEvent] = []
    total_loss = 0.0
    patterns = 0

    for agent_id, allocation in substrate.allocations.items():
        event = await compactor.compact(
            crystal=allocation._crystal,
            target_id=str(agent_id),
            pressure=1.0,  # Force check
            force=True,  # Override policy
        )
        if event:
            events.append(event)
            total_loss += event.resolution_loss
            patterns += event.patterns_before

    return StrategyResult(
        strategy_name="uniform",
        events=events,
        total_resolution_loss=total_loss,
        patterns_affected=patterns,
    )


async def apply_pressure_based_strategy(
    substrate: "SharedSubstrate[T]",
    compactor: Compactor[T],
) -> StrategyResult:
    """
    Apply compaction based on individual allocation pressure.

    High-pressure allocations get more aggressive compression.

    Args:
        substrate: The substrate to compact
        compactor: The compactor to use

    Returns:
        StrategyResult with compaction details
    """
    events: list[CompactionEvent] = []
    total_loss = 0.0
    patterns = 0

    for agent_id, allocation in substrate.allocations.items():
        pressure = allocation.usage_ratio()
        event = await compactor.compact(
            crystal=allocation._crystal,
            target_id=str(agent_id),
            pressure=pressure,
        )
        if event:
            events.append(event)
            total_loss += event.resolution_loss
            patterns += event.patterns_before

    return StrategyResult(
        strategy_name="pressure_based",
        events=events,
        total_resolution_loss=total_loss,
        patterns_affected=patterns,
    )


# =============================================================================
# Factory Functions
# =============================================================================


def create_compactor(
    pressure_threshold: float = 0.8,
    critical_threshold: float = 0.95,
    normal_ratio: float = 0.8,
    min_resolution: float = 0.1,
) -> Compactor[Any]:
    """
    Factory function to create a Compactor.

    Args:
        pressure_threshold: When to start compacting
        critical_threshold: Emergency compaction threshold
        normal_ratio: Normal compression ratio
        min_resolution: Floor for resolution

    Returns:
        Configured Compactor
    """
    policy = CompactionPolicy(
        pressure_threshold=pressure_threshold,
        critical_threshold=critical_threshold,
        normal_ratio=normal_ratio,
        min_resolution=min_resolution,
    )
    return Compactor(policy)


def create_daemon(
    substrate: "SharedSubstrate[Any]",
    check_interval_minutes: int = 5,
) -> AutoCompactionDaemon:
    """
    Factory function to create an AutoCompactionDaemon.

    Args:
        substrate: The substrate to monitor
        check_interval_minutes: Check frequency

    Returns:
        Configured AutoCompactionDaemon
    """
    return AutoCompactionDaemon(
        substrate=substrate,
        check_interval=timedelta(minutes=check_interval_minutes),
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "CompactionPolicy",
    "CompactionEvent",
    # Compactor
    "Compactor",
    # Daemon
    "AutoCompactionDaemon",
    # Strategies
    "StrategyResult",
    "apply_uniform_strategy",
    "apply_pressure_based_strategy",
    # Factory functions
    "create_compactor",
    "create_daemon",
]
