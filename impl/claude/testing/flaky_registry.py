"""
Registry for flaky test patterns.

Philosophy: Memory is not storage—it is active reconstruction.

Phase 4 of test evolution plan:
- Track test outcomes over time
- Calculate flakiness scores
- Suggest retry strategies
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class FlakyPattern:
    """Record of a flaky test pattern."""

    test_id: str
    failure_count: int = 0
    success_count: int = 0
    last_failure: datetime = field(default_factory=lambda: datetime.min)
    failure_reasons: list[str] = field(default_factory=list)

    @property
    def flakiness_score(self) -> float:
        """
        Calculate flakiness score.

        0.0 = always passes
        1.0 = always fails
        Between = flaky (higher = more flaky)
        """
        total = self.failure_count + self.success_count
        if total == 0:
            return 0.0
        return self.failure_count / total

    @property
    def is_flaky(self) -> bool:
        """Test is considered flaky if it both passes and fails."""
        return self.failure_count > 0 and self.success_count > 0

    @property
    def total_runs(self) -> int:
        """Total number of test runs."""
        return self.failure_count + self.success_count


class FlakyRegistry:
    """
    Registry for tracking flaky test patterns.

    Can be backed by D-gent for persistence, or run in-memory.
    """

    def __init__(self, store: Optional[any] = None):
        """
        Initialize the registry.

        Args:
            store: Optional D-gent store for persistence.
                   If None, uses in-memory dict.
        """
        self.store = store
        self._memory: dict[str, FlakyPattern] = {}

    async def record_outcome(
        self, test_id: str, passed: bool, reason: str = ""
    ) -> FlakyPattern:
        """
        Record a test outcome.

        Args:
            test_id: The test identifier (usually nodeid)
            passed: Whether the test passed
            reason: Optional failure reason

        Returns:
            Updated FlakyPattern for the test
        """
        pattern = await self._get_or_create(test_id)

        if passed:
            pattern.success_count += 1
        else:
            pattern.failure_count += 1
            pattern.last_failure = datetime.now()
            if reason:
                pattern.failure_reasons.append(reason)
                # Keep only last 10 reasons
                pattern.failure_reasons = pattern.failure_reasons[-10:]

        await self._save(test_id, pattern)
        return pattern

    async def get_flaky_tests(self, threshold: float = 0.1) -> list[FlakyPattern]:
        """
        Get tests with flakiness above threshold.

        Args:
            threshold: Minimum flakiness score to include

        Returns:
            List of flaky test patterns
        """
        all_patterns = await self._all_patterns()
        return [p for p in all_patterns if p.flakiness_score > threshold and p.is_flaky]

    async def should_retry(self, test_id: str) -> bool:
        """
        Should this test be retried based on history?

        Tests with moderate flakiness (between 10% and 90%) should be retried.
        Always-fail or always-pass tests should not.
        """
        pattern = await self._get(test_id)
        if not pattern:
            return False
        return 0.1 < pattern.flakiness_score < 0.9

    async def get_pattern(self, test_id: str) -> Optional[FlakyPattern]:
        """Get the pattern for a specific test."""
        return await self._get(test_id)

    async def clear(self) -> None:
        """Clear all recorded patterns."""
        self._memory.clear()
        # If using D-gent store, would clear there too

    # =============================================================================
    # Internal Methods
    # =============================================================================

    async def _get(self, test_id: str) -> Optional[FlakyPattern]:
        """Get pattern from store."""
        if self.store is not None:
            return await self.store.get(test_id)
        return self._memory.get(test_id)

    async def _get_or_create(self, test_id: str) -> FlakyPattern:
        """Get existing pattern or create new one."""
        pattern = await self._get(test_id)
        if pattern is None:
            pattern = FlakyPattern(test_id=test_id)
        return pattern

    async def _save(self, test_id: str, pattern: FlakyPattern) -> None:
        """Save pattern to store."""
        if self.store is not None:
            await self.store.set(test_id, pattern)
        else:
            self._memory[test_id] = pattern

    async def _all_patterns(self) -> list[FlakyPattern]:
        """Get all patterns."""
        if self.store is not None:
            # Would need to implement iteration on D-gent
            return list(self._memory.values())
        return list(self._memory.values())
