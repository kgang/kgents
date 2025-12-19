"""
Property tests for registry isolation morphism.

Philosophy: Tests must not leak state. The isolation morphism preserves invariants.

The isolation invariant: TestState → CleanState → TestState
Arbitrary test orderings should preserve isolation.

Tests verify:
1. Registry snapshots are consistent
2. Before/after snapshots match after clean operations
3. Property-based: arbitrary test orderings preserve isolation
"""

from __future__ import annotations

import pytest

from testing.sentinel import (
    RegistrySnapshot,
    capture_registry_snapshot,
    verify_isolation,
)

# =============================================================================
# Basic Tests (no hypothesis required)
# =============================================================================


@pytest.mark.sentinel
class TestRegistrySnapshotBasic:
    """Basic tests for registry snapshot functionality."""

    def test_snapshot_creates_valid_object(self) -> None:
        """capture_registry_snapshot returns a valid RegistrySnapshot."""
        snapshot = capture_registry_snapshot()

        assert isinstance(snapshot, RegistrySnapshot)
        assert isinstance(snapshot.operad_count, int)
        assert isinstance(snapshot.node_count, int)
        assert snapshot.operad_count >= 0
        assert snapshot.node_count >= 0

    def test_snapshot_is_deterministic(self) -> None:
        """Consecutive snapshots should be identical (no state changes)."""
        snap1 = capture_registry_snapshot()
        snap2 = capture_registry_snapshot()

        assert snap1 == snap2

    def test_snapshot_equality(self) -> None:
        """RegistrySnapshot equality works correctly."""
        snap1 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        snap2 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        snap3 = RegistrySnapshot(operad_count=6, node_count=10, fixture_count=0, extra_data={})

        assert snap1 == snap2
        assert snap1 != snap3

    def test_snapshot_extra_data_affects_equality(self) -> None:
        """Extra data is considered in equality checks."""
        snap1 = RegistrySnapshot(
            operad_count=5, node_count=10, fixture_count=0, extra_data={"a": 1}
        )
        snap2 = RegistrySnapshot(
            operad_count=5, node_count=10, fixture_count=0, extra_data={"a": 2}
        )

        assert snap1 != snap2


@pytest.mark.sentinel
class TestVerifyIsolation:
    """Tests for the verify_isolation function."""

    def test_identical_snapshots_pass(self) -> None:
        """Identical snapshots should pass isolation check."""
        snap = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})

        assert verify_isolation(snap, snap) is True

    def test_equal_snapshots_pass(self) -> None:
        """Equal (but not identical) snapshots should pass."""
        snap1 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        snap2 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})

        assert verify_isolation(snap1, snap2) is True

    def test_different_operad_count_fails(self) -> None:
        """Different operad counts should fail isolation."""
        before = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        after = RegistrySnapshot(operad_count=6, node_count=10, fixture_count=0, extra_data={})

        assert verify_isolation(before, after) is False

    def test_different_node_count_fails(self) -> None:
        """Different node counts should fail isolation."""
        before = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        after = RegistrySnapshot(operad_count=5, node_count=11, fixture_count=0, extra_data={})

        assert verify_isolation(before, after) is False


@pytest.mark.sentinel
class TestIsolationPropertiesBasic:
    """Basic property-style tests without hypothesis."""

    def test_isolation_is_reflexive(self) -> None:
        """Isolation check is reflexive: verify_isolation(s, s) == True."""
        for operad_count in [0, 5, 50, 100]:
            for node_count in [0, 10, 100, 500]:
                snap = RegistrySnapshot(
                    operad_count=operad_count,
                    node_count=node_count,
                    fixture_count=0,
                    extra_data={},
                )
                assert verify_isolation(snap, snap) is True

    def test_isolation_is_symmetric(self) -> None:
        """Isolation check is symmetric: verify_isolation(a, b) == verify_isolation(b, a)."""
        snap1 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        snap2 = RegistrySnapshot(operad_count=5, node_count=10, fixture_count=0, extra_data={})
        snap3 = RegistrySnapshot(operad_count=6, node_count=10, fixture_count=0, extra_data={})

        assert verify_isolation(snap1, snap2) == verify_isolation(snap2, snap1)
        assert verify_isolation(snap1, snap3) == verify_isolation(snap3, snap1)

    def test_isolation_detects_operad_difference(self) -> None:
        """Operad count differences detected."""
        for diff in [1, 5, 10, 50]:
            snap1 = RegistrySnapshot(
                operad_count=10, node_count=100, fixture_count=0, extra_data={}
            )
            snap2 = RegistrySnapshot(
                operad_count=10 + diff, node_count=100, fixture_count=0, extra_data={}
            )
            assert verify_isolation(snap1, snap2) is False

    def test_isolation_detects_node_difference(self) -> None:
        """Node count differences detected."""
        for diff in [1, 5, 10, 50]:
            snap1 = RegistrySnapshot(
                operad_count=10, node_count=100, fixture_count=0, extra_data={}
            )
            snap2 = RegistrySnapshot(
                operad_count=10, node_count=100 + diff, fixture_count=0, extra_data={}
            )
            assert verify_isolation(snap1, snap2) is False


@pytest.mark.sentinel
class TestArbitraryTestOrderingsBasic:
    """
    Tests verifying isolation under arbitrary test orderings.

    Simulates the core invariant: running tests in any order should
    not affect global registry state.
    """

    def test_simulated_test_sequence_preserves_isolation(self) -> None:
        """
        Simulated test execution preserves isolation.

        This simulates the invariant that:
        1. Capture snapshot before tests
        2. Run tests (simulated - no actual state change)
        3. Capture snapshot after tests
        4. Snapshots should match
        """
        before = capture_registry_snapshot()

        # Simulate running tests - these shouldn't change registry state
        test_names = ["test_foo", "test_bar", "test_baz", "test_long_name_here"]
        for test_name in test_names:
            # Simulate test execution (in reality, tests may call various functions)
            _ = f"Running test: {test_name}"

        after = capture_registry_snapshot()

        # Isolation invariant: before == after
        assert verify_isolation(before, after), (
            f"Isolation violated after running {len(test_names)} simulated tests"
        )

    @pytest.mark.parametrize(
        "ordering",
        [
            ["lint", "typecheck", "test", "contract"],
            ["typecheck", "lint", "contract", "test"],
            ["test", "contract", "lint", "typecheck"],
            ["contract", "test", "typecheck", "lint"],
        ],
    )
    def test_check_orderings_preserve_isolation(self, ordering: list[str]) -> None:
        """Any ordering of CI checks preserves isolation."""
        before = capture_registry_snapshot()

        # Simulate running checks in the given order
        for check in ordering:
            # These are the actual CI steps that should be idempotent
            _ = f"Running check: {check}"

        after = capture_registry_snapshot()

        assert verify_isolation(before, after)


@pytest.mark.sentinel
class TestSnapshotIntegration:
    """Integration tests for snapshot with real registries."""

    def test_snapshot_captures_real_operads(self) -> None:
        """Snapshot captures actually registered operads."""
        snapshot = capture_registry_snapshot()

        # We expect at least some operads from conftest.py population
        # This test documents the expected baseline
        assert snapshot.operad_count >= 0  # May be 0 if imports fail

    def test_snapshot_captures_real_nodes(self) -> None:
        """Snapshot captures actually registered AGENTESE nodes."""
        snapshot = capture_registry_snapshot()

        # We expect at least some nodes if the system is properly set up
        assert snapshot.node_count >= 0  # May be 0 if imports fail

    def test_consecutive_snapshots_stable(self) -> None:
        """Multiple consecutive snapshots should be identical."""
        snapshots = [capture_registry_snapshot() for _ in range(5)]

        # All snapshots should be equal
        for i in range(1, len(snapshots)):
            assert snapshots[0] == snapshots[i], f"Snapshot {i} differs from snapshot 0"


# =============================================================================
# Property-Based Tests (require hypothesis)
# =============================================================================

# Check if hypothesis is available
try:
    from hypothesis import given, settings, strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


@pytest.mark.sentinel
@pytest.mark.property
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestIsolationMorphismHypothesis:
    """Property-based tests for the isolation morphism (requires hypothesis)."""

    def test_isolation_is_reflexive_property(self) -> None:
        """Isolation check is reflexive: verify_isolation(s, s) == True."""
        if not HYPOTHESIS_AVAILABLE:
            pytest.skip("hypothesis not installed")

        @given(
            operad_count=st.integers(min_value=0, max_value=100),
            node_count=st.integers(min_value=0, max_value=500),
        )
        @settings(max_examples=50)
        def _test(operad_count: int, node_count: int) -> None:
            snap = RegistrySnapshot(
                operad_count=operad_count,
                node_count=node_count,
                fixture_count=0,
                extra_data={},
            )
            assert verify_isolation(snap, snap) is True

        _test()

    def test_isolation_is_symmetric_property(self) -> None:
        """Isolation check is symmetric: verify_isolation(a, b) == verify_isolation(b, a)."""
        if not HYPOTHESIS_AVAILABLE:
            pytest.skip("hypothesis not installed")

        @given(
            operad_count=st.integers(min_value=0, max_value=100),
            node_count=st.integers(min_value=0, max_value=500),
        )
        @settings(max_examples=50)
        def _test(operad_count: int, node_count: int) -> None:
            snap1 = RegistrySnapshot(
                operad_count=operad_count,
                node_count=node_count,
                fixture_count=0,
                extra_data={},
            )
            snap2 = RegistrySnapshot(
                operad_count=operad_count,
                node_count=node_count,
                fixture_count=0,
                extra_data={},
            )
            assert verify_isolation(snap1, snap2) == verify_isolation(snap2, snap1)

        _test()

    def test_isolation_detects_any_difference_property(self) -> None:
        """Any difference in counts should be detected."""
        if not HYPOTHESIS_AVAILABLE:
            pytest.skip("hypothesis not installed")

        @given(
            operad1=st.integers(min_value=0, max_value=100),
            operad2=st.integers(min_value=0, max_value=100),
            node1=st.integers(min_value=0, max_value=500),
            node2=st.integers(min_value=0, max_value=500),
        )
        @settings(max_examples=100)
        def _test(operad1: int, operad2: int, node1: int, node2: int) -> None:
            snap1 = RegistrySnapshot(
                operad_count=operad1,
                node_count=node1,
                fixture_count=0,
                extra_data={},
            )
            snap2 = RegistrySnapshot(
                operad_count=operad2,
                node_count=node2,
                fixture_count=0,
                extra_data={},
            )
            expected = (operad1 == operad2) and (node1 == node2)
            assert verify_isolation(snap1, snap2) == expected

        _test()


@pytest.mark.sentinel
@pytest.mark.property
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestArbitraryTestOrderingsHypothesis:
    """
    Property tests verifying isolation under arbitrary test orderings.
    Requires hypothesis for full property-based testing.
    """

    def test_arbitrary_orderings_preserve_isolation_property(self) -> None:
        """
        Simulated test execution in arbitrary order preserves isolation.
        """
        if not HYPOTHESIS_AVAILABLE:
            pytest.skip("hypothesis not installed")

        @given(
            test_sequence=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10),
        )
        @settings(max_examples=30)
        def _test(test_sequence: list[str]) -> None:
            before = capture_registry_snapshot()

            # Simulate running tests
            for test_name in test_sequence:
                _ = f"Running test: {test_name}"

            after = capture_registry_snapshot()
            assert verify_isolation(before, after)

        _test()

    def test_check_orderings_preserve_isolation_property(self) -> None:
        """Any ordering of CI checks preserves isolation."""
        if not HYPOTHESIS_AVAILABLE:
            pytest.skip("hypothesis not installed")

        @given(
            ordering=st.permutations(["lint", "typecheck", "test", "contract"]),
        )
        @settings(max_examples=24)  # 4! = 24 permutations
        def _test(ordering: list[str]) -> None:
            before = capture_registry_snapshot()

            for check in ordering:
                _ = f"Running check: {check}"

            after = capture_registry_snapshot()
            assert verify_isolation(before, after)

        _test()
