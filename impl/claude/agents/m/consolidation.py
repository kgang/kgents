"""
ConsolidationAgent: Background Memory Processing.

The Hypnagogic Worker: runs when the system is idle.
Implements the "sleep" phase of memory management.

Operations:
1. COMPRESS: Reduce resolution of cold memories
2. STRENGTHEN: Increase resolution of hot memories
3. INTEGRATE: Merge similar memories (chunking)
4. FORGET: Reduce interference from irrelevant patterns
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Generic, Optional, TypeVar

from .holographic import CompressionLevel, HolographicMemory

T = TypeVar("T")


class ConsolidationMode(Enum):
    """Modes of consolidation."""

    LIGHT = auto()  # Quick pass, minimal changes
    NORMAL = auto()  # Standard consolidation
    DEEP = auto()  # Thorough cleanup, more aggressive compression


@dataclass
class TemperatureProfile:
    """Temperature distribution of memory patterns."""

    hot_count: int
    warm_count: int
    cold_count: int
    frozen_count: int  # Very old, heavily compressed

    hot_ids: list[str] = field(default_factory=list)
    cold_ids: list[str] = field(default_factory=list)
    frozen_ids: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total pattern count."""
        return self.hot_count + self.warm_count + self.cold_count + self.frozen_count

    @property
    def heat_ratio(self) -> float:
        """Ratio of hot to total."""
        return self.hot_count / max(self.total, 1)


@dataclass
class ConsolidationResult:
    """Result of a consolidation pass."""

    mode: ConsolidationMode
    timestamp: datetime
    duration_ms: float

    # Counts
    demoted: int
    promoted: int
    integrated: int
    forgotten: int

    # State before/after
    before_profile: TemperatureProfile
    after_profile: TemperatureProfile

    # Details
    demoted_ids: list[str] = field(default_factory=list)
    promoted_ids: list[str] = field(default_factory=list)
    integrated_clusters: list[list[str]] = field(default_factory=list)

    @property
    def was_productive(self) -> bool:
        """Check if consolidation made meaningful changes."""
        return (self.demoted + self.promoted + self.integrated) > 0


class ConsolidationAgent(Generic[T]):
    """Background memory processing agent.

    The Hypnagogic pattern: system improves while idle.
    Memory consolidation is not just cleanup—it's learning.

    Example:
        memory = HolographicMemory(embedder=my_embedder)
        consolidator = ConsolidationAgent(memory)

        # ... agent activity ...

        # During idle time (e.g., between sessions)
        result = await consolidator.invoke()
        print(f"Consolidated: {result.demoted} demoted, {result.promoted} promoted")
    """

    def __init__(
        self,
        memory: HolographicMemory[T],
        hot_threshold: float = 0.7,
        cold_threshold: float = 0.3,
        frozen_threshold_days: float = 30.0,
        integration_similarity: float = 0.95,
    ):
        """Initialize consolidation agent.

        Args:
            memory: HolographicMemory to consolidate
            hot_threshold: Temperature above which patterns are "hot"
            cold_threshold: Temperature below which patterns are "cold"
            frozen_threshold_days: Days of inactivity before "frozen"
            integration_similarity: Similarity threshold for merging patterns
        """
        self._memory = memory
        self._hot_threshold = hot_threshold
        self._cold_threshold = cold_threshold
        self._frozen_threshold = timedelta(days=frozen_threshold_days)
        self._integration_similarity = integration_similarity

    async def invoke(
        self,
        mode: ConsolidationMode = ConsolidationMode.NORMAL,
    ) -> ConsolidationResult:
        """Run consolidation pass.

        Args:
            mode: Consolidation intensity

        Returns:
            ConsolidationResult with statistics
        """
        start_time = datetime.now()
        before_profile = self._profile_memory()

        result = ConsolidationResult(
            mode=mode,
            timestamp=start_time,
            duration_ms=0,
            demoted=0,
            promoted=0,
            integrated=0,
            forgotten=0,
            before_profile=before_profile,
            after_profile=before_profile,  # Updated at end
        )

        # Demotion pass (cold → colder)
        await self._demote_cold(result, mode)

        # Promotion pass (hot → hotter)
        await self._promote_hot(result, mode)

        # Integration pass (merge similar)
        if mode in (ConsolidationMode.NORMAL, ConsolidationMode.DEEP):
            await self._integrate_similar(result)

        # Deep mode: aggressive forgetting
        if mode == ConsolidationMode.DEEP:
            await self._aggressive_forget(result)

        # Finalize
        end_time = datetime.now()
        result.duration_ms = (end_time - start_time).total_seconds() * 1000
        result.after_profile = self._profile_memory()

        return result

    async def profile(self) -> TemperatureProfile:
        """Get current temperature profile without consolidating."""
        return self._profile_memory()

    async def schedule_consolidation(
        self,
        target_heat_ratio: float = 0.3,
    ) -> Optional[ConsolidationMode]:
        """Determine if and how to consolidate.

        Returns recommended mode based on current state,
        or None if consolidation isn't needed.

        Args:
            target_heat_ratio: Desired ratio of hot patterns

        Returns:
            Recommended mode or None
        """
        profile = self._profile_memory()

        # Too many hot patterns → need cooling
        if profile.heat_ratio > target_heat_ratio + 0.2:
            return ConsolidationMode.LIGHT

        # Too many cold patterns → need cleanup
        cold_ratio = profile.cold_count / max(profile.total, 1)
        if cold_ratio > 0.5:
            return ConsolidationMode.NORMAL

        # Too many frozen patterns → deep clean
        frozen_ratio = profile.frozen_count / max(profile.total, 1)
        if frozen_ratio > 0.3:
            return ConsolidationMode.DEEP

        return None

    def _profile_memory(self) -> TemperatureProfile:
        """Compute temperature profile of memory."""
        hot_count = 0
        warm_count = 0
        cold_count = 0
        frozen_count = 0

        hot_ids = []
        cold_ids = []
        frozen_ids = []

        for pattern in self._memory._patterns.values():
            temp = pattern.temperature

            if temp > self._hot_threshold:
                hot_count += 1
                hot_ids.append(pattern.id)
            elif temp < self._cold_threshold:
                if pattern.time_since_access > self._frozen_threshold:
                    frozen_count += 1
                    frozen_ids.append(pattern.id)
                else:
                    cold_count += 1
                    cold_ids.append(pattern.id)
            else:
                warm_count += 1

        return TemperatureProfile(
            hot_count=hot_count,
            warm_count=warm_count,
            cold_count=cold_count,
            frozen_count=frozen_count,
            hot_ids=hot_ids,
            cold_ids=cold_ids,
            frozen_ids=frozen_ids,
        )

    async def _demote_cold(
        self,
        result: ConsolidationResult,
        mode: ConsolidationMode,
    ) -> None:
        """Demote cold patterns to lower resolution."""
        # Get cold patterns
        cold_patterns = self._memory.identify_cold()

        for pattern in cold_patterns:
            # Determine demotion level based on age and mode
            if pattern.time_since_access > self._frozen_threshold:
                levels = 2 if mode == ConsolidationMode.DEEP else 1
            else:
                levels = 1

            # Skip if already at minimum
            if pattern.compression == CompressionLevel.MINIMAL:
                continue

            await self._memory.demote(pattern.id, levels=levels)
            result.demoted += 1
            result.demoted_ids.append(pattern.id)

    async def _promote_hot(
        self,
        result: ConsolidationResult,
        mode: ConsolidationMode,
    ) -> None:
        """Promote hot patterns to higher resolution."""
        hot_patterns = self._memory.identify_hot()

        for pattern in hot_patterns:
            # Skip if already at maximum
            if pattern.compression == CompressionLevel.FULL:
                continue

            # More aggressive promotion in deep mode
            levels = 2 if mode == ConsolidationMode.DEEP else 1

            await self._memory.promote(pattern.id, levels=levels)
            result.promoted += 1
            result.promoted_ids.append(pattern.id)

    async def _integrate_similar(self, result: ConsolidationResult) -> None:
        """Merge highly similar patterns."""
        patterns = list(self._memory._patterns.values())
        visited = set()

        for i, p1 in enumerate(patterns):
            if p1.id in visited:
                continue

            cluster = [p1.id]
            visited.add(p1.id)

            for p2 in patterns[i + 1 :]:
                if p2.id in visited:
                    continue

                sim = self._memory._cosine_similarity(p1.embedding, p2.embedding)
                if sim >= self._integration_similarity:
                    cluster.append(p2.id)
                    visited.add(p2.id)

            if len(cluster) > 1:
                await self._memory._integrate_cluster(cluster)
                result.integrated += len(cluster) - 1
                result.integrated_clusters.append(cluster)

    async def _aggressive_forget(self, result: ConsolidationResult) -> None:
        """Aggressively compress frozen patterns.

        In deep mode, patterns that haven't been accessed in a long time
        are compressed to minimal resolution.
        """
        profile = result.before_profile

        for pattern_id in profile.frozen_ids:
            if pattern_id not in self._memory._patterns:
                continue

            pattern = self._memory._patterns[pattern_id]

            # Compress to minimal
            pattern.compression = CompressionLevel.MINIMAL

            # Reduce strength
            pattern.strength = max(0.1, pattern.strength * 0.5)

            result.forgotten += 1


class ForgettingCurveAgent(Generic[T]):
    """Agent that models forgetting to guide consolidation.

    Based on Ebbinghaus forgetting curve:
    R = e^(-t/S)

    Where:
    - R = retention (0 to 1)
    - t = time since last recall
    - S = strength (increases with repetition)
    """

    def __init__(
        self,
        memory: HolographicMemory[T],
        review_threshold: float = 0.3,
        compress_threshold: float = 0.9,
    ):
        """Initialize forgetting curve agent.

        Args:
            memory: HolographicMemory to analyze
            review_threshold: Retention below which review is needed
            compress_threshold: Retention above which compression is safe
        """
        self._memory = memory
        self._review_threshold = review_threshold
        self._compress_threshold = compress_threshold

    async def analyze(self) -> dict[str, list[str]]:
        """Analyze memory based on forgetting curves.

        Returns:
            Dictionary with "needs_review", "can_compress", "stable" lists
        """
        needs_review = []
        can_compress = []
        stable = []

        for pattern in self._memory._patterns.values():
            retention = pattern.retention

            if retention < self._review_threshold:
                needs_review.append(pattern.id)
            elif retention > self._compress_threshold:
                can_compress.append(pattern.id)
            else:
                stable.append(pattern.id)

        return {
            "needs_review": needs_review,
            "can_compress": can_compress,
            "stable": stable,
        }

    def optimal_review_interval(self, pattern_id: str) -> Optional[timedelta]:
        """Calculate optimal interval for next review (spaced repetition).

        Based on SuperMemo SM-2 algorithm.

        Args:
            pattern_id: Pattern to calculate interval for

        Returns:
            Optimal review interval, or None if pattern not found
        """
        if pattern_id not in self._memory._patterns:
            return None

        pattern = self._memory._patterns[pattern_id]

        # SM-2 inspired interval
        # Base: 1 day, multiplied by strength
        base_days = 1.0
        multiplier = 2.5 * pattern.strength

        return timedelta(days=base_days * multiplier)
