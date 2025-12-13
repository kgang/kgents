"""
Categorical Test Partitioning (Operad-based).

Models test composition and execution using the operad framework.
Provides operations for:
- Partitioning tests by tier
- Parallelizing independent tests
- Sequencing dependent tests
- Fail-fast ordering

Philosophy: "Test execution is a morphism in the category
of test suites. The operad provides the composition grammar."

AGENTESE: self.test.partition.lens
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Iterable, Iterator, TypeVar

from testing.optimization import RefinementTracker, TestProfile, TestTier

T = TypeVar("T")


class ExecutionStrategy(Enum):
    """How to execute a test partition."""

    SEQUENTIAL = auto()  # Run in order
    PARALLEL = auto()  # Run concurrently
    FAIL_FAST = auto()  # Stop on first failure


@dataclass
class TestPartition:
    """
    A partition of tests with execution metadata.

    Partitions compose via operad operations:
    - seq: Run one partition after another
    - par: Run partitions in parallel
    - tier: Group by execution cost
    """

    name: str
    tests: list[TestProfile] = field(default_factory=list)
    strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    priority: int = 0  # Higher = run first
    dependencies: set[str] = field(
        default_factory=set
    )  # Names of partitions that must complete first

    @property
    def total_time_ms(self) -> float:
        """Total execution time (sequential estimate)."""
        return sum(t.duration_ms for t in self.tests)

    @property
    def tier_distribution(self) -> dict[TestTier, int]:
        """Count of tests per tier."""
        counts: dict[TestTier, int] = {tier: 0 for tier in TestTier}
        for t in self.tests:
            counts[t.tier] += 1
        return counts

    def __len__(self) -> int:
        return len(self.tests)

    def __iter__(self) -> Iterator[TestProfile]:
        return iter(self.tests)


@dataclass
class PartitionPlan:
    """
    Complete test execution plan.

    The plan is a composition of partitions using operad operations.
    It can be serialized to pytest commands or executed directly.
    """

    partitions: list[TestPartition] = field(default_factory=list)
    parallel_workers: int = 4
    fail_fast: bool = True

    @property
    def total_tests(self) -> int:
        """Total tests across all partitions."""
        return sum(len(p) for p in self.partitions)

    @property
    def estimated_time_ms(self) -> float:
        """
        Estimated execution time.

        Accounts for parallelism within parallel partitions.
        """
        time = 0.0
        for p in self.partitions:
            if p.strategy == ExecutionStrategy.PARALLEL:
                # Parallel execution divides by workers
                time += p.total_time_ms / self.parallel_workers
            else:
                time += p.total_time_ms
        return time

    def to_pytest_args(self) -> list[str]:
        """
        Convert plan to pytest command line arguments.

        Returns arguments for pytest-xdist parallelization.
        """
        args: list[str] = []

        if self.parallel_workers > 1:
            args.extend(["-n", str(self.parallel_workers)])

        if self.fail_fast:
            args.append("-x")

        # Collect all test nodeids
        for partition in self.partitions:
            for test in partition.tests:
                args.append(test.test_id)

        return args


# =============================================================================
# Operad Operations for Test Partitions
# =============================================================================


def partition_by_tier(
    profiles: Iterable[TestProfile],
) -> dict[TestTier, TestPartition]:
    """
    Partition tests by execution tier.

    Operad signature: list[Test] → Map[Tier, Partition]

    This is the fundamental partitioning operation that groups
    tests by their execution cost.
    """
    partitions: dict[TestTier, TestPartition] = {}

    for tier in TestTier:
        partitions[tier] = TestPartition(
            name=f"tier_{tier.value}",
            tests=[],
            strategy=ExecutionStrategy.PARALLEL,
            priority=_tier_priority(tier),
        )

    for profile in profiles:
        partitions[profile.tier].tests.append(profile)

    return partitions


def _tier_priority(tier: TestTier) -> int:
    """Priority for tier (higher = run first)."""
    return {
        TestTier.INSTANT: 100,
        TestTier.FAST: 80,
        TestTier.MEDIUM: 60,
        TestTier.SLOW: 40,
        TestTier.EXPENSIVE: 20,
    }[tier]


def sequence_partitions(*partitions: TestPartition) -> list[TestPartition]:
    """
    Sequence partitions for sequential execution.

    Operad signature: Partition × Partition → list[Partition]

    Orders partitions by priority (high to low).
    """
    return sorted(partitions, key=lambda p: p.priority, reverse=True)


def parallelize_partition(
    partition: TestPartition,
    workers: int = 4,
) -> TestPartition:
    """
    Mark partition for parallel execution.

    Operad signature: Partition → Partition (with parallel strategy)
    """
    return TestPartition(
        name=partition.name,
        tests=partition.tests,
        strategy=ExecutionStrategy.PARALLEL,
        priority=partition.priority,
        dependencies=partition.dependencies,
    )


def merge_partitions(*partitions: TestPartition, name: str = "merged") -> TestPartition:
    """
    Merge multiple partitions into one.

    Operad signature: Partition × Partition × ... → Partition
    """
    tests = []
    deps: set[str] = set()

    for p in partitions:
        tests.extend(p.tests)
        deps |= p.dependencies

    return TestPartition(
        name=name,
        tests=tests,
        strategy=ExecutionStrategy.PARALLEL,
        priority=min(p.priority for p in partitions) if partitions else 0,
        dependencies=deps,
    )


def filter_partition(
    partition: TestPartition,
    predicate: Callable[[TestProfile], bool],
    name: str | None = None,
) -> TestPartition:
    """
    Filter tests in a partition.

    Operad signature: Partition × (Test → Bool) → Partition
    """
    filtered = [t for t in partition.tests if predicate(t)]
    return TestPartition(
        name=name or f"{partition.name}_filtered",
        tests=filtered,
        strategy=partition.strategy,
        priority=partition.priority,
        dependencies=partition.dependencies,
    )


# =============================================================================
# Optimal Ordering (Fail-Fast Strategy)
# =============================================================================


def optimal_order(profiles: Iterable[TestProfile]) -> list[TestProfile]:
    """
    Order tests for optimal fail-fast execution.

    Strategy:
    1. Fast tests first (fail fast on cheap tests)
    2. Within tier, order by historical failure rate (TODO)
    3. Independent tests can run in parallel

    Returns ordered list of test profiles.
    """
    tests = list(profiles)

    # Sort by tier (fastest first), then by duration within tier
    return sorted(
        tests,
        key=lambda t: (_tier_priority(t.tier) * -1, t.duration_ms),
    )


def optimal_plan(
    tracker: RefinementTracker,
    parallel_workers: int = 4,
    exclude_slow: bool = True,
) -> PartitionPlan:
    """
    Generate optimal test execution plan.

    Uses tracker profiles to partition and order tests.

    Args:
        tracker: RefinementTracker with test profiles
        parallel_workers: Number of parallel workers
        exclude_slow: Whether to exclude SLOW and EXPENSIVE tests

    Returns:
        PartitionPlan ready for execution
    """
    profiles = list(tracker.profiles.values())

    # Partition by tier
    tier_partitions = partition_by_tier(profiles)

    # Build plan
    plan = PartitionPlan(
        parallel_workers=parallel_workers,
        fail_fast=True,
    )

    # Add partitions in priority order (fast first)
    for tier in [TestTier.INSTANT, TestTier.FAST, TestTier.MEDIUM]:
        partition = tier_partitions[tier]
        if partition.tests:
            partition = parallelize_partition(partition, parallel_workers)
            plan.partitions.append(partition)

    # Optionally add slow tests
    if not exclude_slow:
        for tier in [TestTier.SLOW, TestTier.EXPENSIVE]:
            partition = tier_partitions[tier]
            if partition.tests:
                # Slow tests run sequentially to avoid resource contention
                partition.strategy = ExecutionStrategy.SEQUENTIAL
                plan.partitions.append(partition)

    return plan


# =============================================================================
# Dependency Detection (Future: Graph-based)
# =============================================================================


@dataclass
class TestDependency:
    """Dependency between tests."""

    source: str  # Test that creates state
    target: str  # Test that requires state
    artifact: str  # What is shared (e.g., "database", "cache")


def detect_dependencies(profiles: Iterable[TestProfile]) -> list[TestDependency]:
    """
    Detect dependencies between tests.

    Uses heuristics:
    - Tests in same module may share fixtures
    - Tests with "integration" in name likely have deps
    - Tests marked with @pytest.mark.depends

    Returns list of detected dependencies.
    """
    # TODO: Implement proper dependency detection
    # For now, assume all tests are independent
    return []


def partition_with_dependencies(
    profiles: Iterable[TestProfile],
    dependencies: list[TestDependency],
) -> list[TestPartition]:
    """
    Partition tests respecting dependencies.

    Creates partitions where:
    - Independent tests can run in parallel
    - Dependent tests are sequenced correctly

    Returns topologically sorted partitions.
    """
    tests = list(profiles)

    if not dependencies:
        # No dependencies - single parallel partition
        return [
            TestPartition(
                name="independent",
                tests=tests,
                strategy=ExecutionStrategy.PARALLEL,
            )
        ]

    # Build dependency graph
    # TODO: Implement proper graph partitioning
    # For now, return single sequential partition
    return [
        TestPartition(
            name="dependent",
            tests=tests,
            strategy=ExecutionStrategy.SEQUENTIAL,
        )
    ]


__all__ = [
    # Types
    "ExecutionStrategy",
    "TestPartition",
    "PartitionPlan",
    "TestDependency",
    # Operad operations
    "partition_by_tier",
    "sequence_partitions",
    "parallelize_partition",
    "merge_partitions",
    "filter_partition",
    # Optimal ordering
    "optimal_order",
    "optimal_plan",
    # Dependencies
    "detect_dependencies",
    "partition_with_dependencies",
]
