"""
Tests for categorical test partitioning.

Verifies:
1. TestPartition data structure
2. Operad operations (partition_by_tier, sequence, merge, filter)
3. Optimal ordering for fail-fast execution
4. Pytest argument generation
"""

from __future__ import annotations

import pytest
from testing.optimization import RefinementTracker, TestProfile, TestTier
from testing.optimization.partition import (
    ExecutionStrategy,
    PartitionPlan,
    TestPartition,
    filter_partition,
    merge_partitions,
    optimal_order,
    optimal_plan,
    parallelize_partition,
    partition_by_tier,
    sequence_partitions,
)


class TestTestPartition:
    """Tests for TestPartition data structure."""

    def test_total_time(self) -> None:
        """Computes total execution time."""
        partition = TestPartition(
            name="test",
            tests=[
                TestProfile.from_duration("test_1", 0.1),
                TestProfile.from_duration("test_2", 0.2),
                TestProfile.from_duration("test_3", 0.3),
            ],
        )

        # 100 + 200 + 300 = 600ms
        assert abs(partition.total_time_ms - 600) < 1

    def test_tier_distribution(self) -> None:
        """Counts tests per tier."""
        partition = TestPartition(
            name="test",
            tests=[
                TestProfile.from_duration("test_instant", 0.05),  # INSTANT
                TestProfile.from_duration("test_fast_1", 0.3),  # FAST
                TestProfile.from_duration("test_fast_2", 0.5),  # FAST
            ],
        )

        dist = partition.tier_distribution

        assert dist[TestTier.INSTANT] == 1
        assert dist[TestTier.FAST] == 2

    def test_len_and_iter(self) -> None:
        """Supports len and iteration."""
        tests = [
            TestProfile.from_duration("test_1", 0.1),
            TestProfile.from_duration("test_2", 0.2),
        ]
        partition = TestPartition(name="test", tests=tests)

        assert len(partition) == 2
        assert list(partition) == tests


class TestPartitionByTier:
    """Tests for partition_by_tier operation."""

    def test_partitions_all_tiers(self) -> None:
        """Creates partitions for all tiers."""
        profiles = [
            TestProfile.from_duration("test_instant", 0.05),
            TestProfile.from_duration("test_fast", 0.3),
            TestProfile.from_duration("test_slow", 10.0),
        ]

        partitions = partition_by_tier(profiles)

        assert len(partitions) == len(TestTier)
        assert len(partitions[TestTier.INSTANT]) == 1
        assert len(partitions[TestTier.FAST]) == 1
        assert len(partitions[TestTier.SLOW]) == 1

    def test_empty_tiers(self) -> None:
        """Creates empty partitions for unused tiers."""
        profiles = [TestProfile.from_duration("test_fast", 0.3)]

        partitions = partition_by_tier(profiles)

        assert len(partitions[TestTier.FAST]) == 1
        assert len(partitions[TestTier.INSTANT]) == 0
        assert len(partitions[TestTier.EXPENSIVE]) == 0

    def test_partition_priority(self) -> None:
        """Faster tiers have higher priority."""
        profiles = [
            TestProfile.from_duration("test_instant", 0.05),
            TestProfile.from_duration("test_slow", 10.0),
        ]

        partitions = partition_by_tier(profiles)

        assert (
            partitions[TestTier.INSTANT].priority > partitions[TestTier.SLOW].priority
        )


class TestSequencePartitions:
    """Tests for sequence_partitions operation."""

    def test_orders_by_priority(self) -> None:
        """Sequences partitions high to low priority."""
        low = TestPartition(name="low", priority=10)
        mid = TestPartition(name="mid", priority=50)
        high = TestPartition(name="high", priority=100)

        sequenced = sequence_partitions(low, mid, high)

        assert [p.name for p in sequenced] == ["high", "mid", "low"]


class TestParallelizePartition:
    """Tests for parallelize_partition operation."""

    def test_sets_parallel_strategy(self) -> None:
        """Marks partition for parallel execution."""
        partition = TestPartition(
            name="test",
            tests=[TestProfile.from_duration("t", 0.1)],
            strategy=ExecutionStrategy.SEQUENTIAL,
        )

        parallel = parallelize_partition(partition)

        assert parallel.strategy == ExecutionStrategy.PARALLEL

    def test_preserves_tests(self) -> None:
        """Preserves tests and metadata."""
        tests = [TestProfile.from_duration("t", 0.1)]
        partition = TestPartition(name="test", tests=tests, priority=50)

        parallel = parallelize_partition(partition)

        assert parallel.tests == tests
        assert parallel.priority == 50


class TestMergePartitions:
    """Tests for merge_partitions operation."""

    def test_combines_tests(self) -> None:
        """Merges tests from all partitions."""
        p1 = TestPartition(
            name="p1",
            tests=[TestProfile.from_duration("t1", 0.1)],
        )
        p2 = TestPartition(
            name="p2",
            tests=[TestProfile.from_duration("t2", 0.2)],
        )

        merged = merge_partitions(p1, p2, name="merged")

        assert len(merged) == 2

    def test_merges_dependencies(self) -> None:
        """Combines dependencies from all partitions."""
        p1 = TestPartition(name="p1", dependencies={"dep1"})
        p2 = TestPartition(name="p2", dependencies={"dep2"})

        merged = merge_partitions(p1, p2)

        assert merged.dependencies == {"dep1", "dep2"}

    def test_takes_min_priority(self) -> None:
        """Uses minimum priority of merged partitions."""
        p1 = TestPartition(name="p1", priority=100)
        p2 = TestPartition(name="p2", priority=50)

        merged = merge_partitions(p1, p2)

        assert merged.priority == 50


class TestFilterPartition:
    """Tests for filter_partition operation."""

    def test_filters_tests(self) -> None:
        """Filters tests by predicate."""
        partition = TestPartition(
            name="test",
            tests=[
                TestProfile.from_duration("test_instant", 0.05),
                TestProfile.from_duration("test_slow", 10.0),
            ],
        )

        filtered = filter_partition(
            partition,
            lambda t: t.tier != TestTier.SLOW,
        )

        assert len(filtered) == 1
        assert filtered.tests[0].tier == TestTier.INSTANT

    def test_preserves_metadata(self) -> None:
        """Preserves partition metadata."""
        partition = TestPartition(
            name="test",
            tests=[TestProfile.from_duration("t", 0.1)],
            strategy=ExecutionStrategy.PARALLEL,
            priority=50,
        )

        filtered = filter_partition(partition, lambda t: True)

        assert filtered.strategy == ExecutionStrategy.PARALLEL
        assert filtered.priority == 50


class TestOptimalOrder:
    """Tests for optimal test ordering."""

    def test_fast_tests_first(self) -> None:
        """Orders fast tests before slow tests."""
        profiles = [
            TestProfile.from_duration("test_slow", 10.0),
            TestProfile.from_duration("test_instant", 0.05),
            TestProfile.from_duration("test_fast", 0.3),
        ]

        ordered = optimal_order(profiles)

        # Should be instant, fast, slow
        assert ordered[0].tier == TestTier.INSTANT
        assert ordered[1].tier == TestTier.FAST
        assert ordered[2].tier == TestTier.SLOW

    def test_within_tier_by_duration(self) -> None:
        """Within tier, orders by duration."""
        profiles = [
            TestProfile.from_duration("test_fast_long", 0.8),
            TestProfile.from_duration("test_fast_short", 0.2),
        ]

        ordered = optimal_order(profiles)

        # Shorter first
        assert ordered[0].duration_ms < ordered[1].duration_ms


class TestPartitionPlan:
    """Tests for PartitionPlan."""

    def test_total_tests(self) -> None:
        """Counts total tests across partitions."""
        plan = PartitionPlan(
            partitions=[
                TestPartition(
                    name="p1",
                    tests=[
                        TestProfile.from_duration("t1", 0.1),
                        TestProfile.from_duration("t2", 0.1),
                    ],
                ),
                TestPartition(
                    name="p2",
                    tests=[TestProfile.from_duration("t3", 0.1)],
                ),
            ]
        )

        assert plan.total_tests == 3

    def test_estimated_time_sequential(self) -> None:
        """Estimates time for sequential execution."""
        plan = PartitionPlan(
            partitions=[
                TestPartition(
                    name="p1",
                    tests=[TestProfile.from_duration("t1", 0.1)],  # 100ms
                    strategy=ExecutionStrategy.SEQUENTIAL,
                ),
            ],
            parallel_workers=1,
        )

        assert abs(plan.estimated_time_ms - 100) < 1

    def test_estimated_time_parallel(self) -> None:
        """Estimates time for parallel execution."""
        plan = PartitionPlan(
            partitions=[
                TestPartition(
                    name="p1",
                    tests=[
                        TestProfile.from_duration("t1", 0.1),
                        TestProfile.from_duration("t2", 0.1),
                        TestProfile.from_duration("t3", 0.1),
                        TestProfile.from_duration("t4", 0.1),
                    ],  # 400ms total
                    strategy=ExecutionStrategy.PARALLEL,
                ),
            ],
            parallel_workers=4,
        )

        # 400ms / 4 workers = 100ms
        assert abs(plan.estimated_time_ms - 100) < 1

    def test_to_pytest_args(self) -> None:
        """Generates valid pytest arguments."""
        plan = PartitionPlan(
            partitions=[
                TestPartition(
                    name="p1",
                    tests=[
                        TestProfile.from_duration("test_foo", 0.1),
                        TestProfile.from_duration("test_bar", 0.1),
                    ],
                ),
            ],
            parallel_workers=4,
            fail_fast=True,
        )

        args = plan.to_pytest_args()

        assert "-n" in args
        assert "4" in args
        assert "-x" in args
        assert "test_foo" in args
        assert "test_bar" in args


class TestOptimalPlan:
    """Tests for optimal_plan generation."""

    def test_creates_plan_from_tracker(self) -> None:
        """Creates plan from RefinementTracker profiles."""
        tracker = RefinementTracker()
        tracker.record_profile("test_instant", 0.05)
        tracker.record_profile("test_fast", 0.3)

        plan = optimal_plan(tracker)

        assert plan.total_tests == 2
        assert len(plan.partitions) > 0

    def test_excludes_slow_by_default(self) -> None:
        """Excludes SLOW and EXPENSIVE tests by default."""
        tracker = RefinementTracker()
        tracker.record_profile("test_fast", 0.3)
        tracker.record_profile("test_slow", 10.0)
        tracker.record_profile("test_expensive", 45.0)

        plan = optimal_plan(tracker, exclude_slow=True)

        # Only fast test should be included
        all_tests = [t for p in plan.partitions for t in p.tests]
        test_ids = [t.test_id for t in all_tests]

        assert "test_fast" in test_ids
        assert "test_slow" not in test_ids
        assert "test_expensive" not in test_ids

    def test_includes_slow_when_requested(self) -> None:
        """Includes slow tests when exclude_slow=False."""
        tracker = RefinementTracker()
        tracker.record_profile("test_fast", 0.3)
        tracker.record_profile("test_slow", 10.0)

        plan = optimal_plan(tracker, exclude_slow=False)

        all_tests = [t for p in plan.partitions for t in p.tests]
        test_ids = [t.test_id for t in all_tests]

        assert "test_fast" in test_ids
        assert "test_slow" in test_ids

    def test_respects_worker_count(self) -> None:
        """Sets specified worker count."""
        tracker = RefinementTracker()
        tracker.record_profile("test_fast", 0.3)

        plan = optimal_plan(tracker, parallel_workers=8)

        assert plan.parallel_workers == 8
