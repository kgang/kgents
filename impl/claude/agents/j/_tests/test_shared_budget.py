"""
Tests for Shared Entropy Budget - J-gent × B-gent integration.

Tests:
- SharedEntropyBudget depth-based calculations
- B-gent backing store integration
- DualEntropyBudget coordination
- Child spawning mechanics
"""

from agents.b.metered_functor import EntropyBudget as BgentEntropyBudget
from agents.j.shared_budget import (
    DualEntropyBudget,
    SharedEntropyBudget,
    compute_depth_from_budget,
    create_depth_based_budget,
    create_dual_budget,
)

# =============================================================================
# SharedEntropyBudget Tests
# =============================================================================


class TestSharedEntropyBudget:
    """Tests for SharedEntropyBudget."""

    def test_depth_zero_has_full_budget(self) -> None:
        """Depth 0 has budget 1.0."""
        budget = create_depth_based_budget(depth=0)
        assert budget.remaining == 1.0
        assert budget.initial == 1.0
        assert budget.depth == 0

    def test_depth_one_has_half_budget(self) -> None:
        """Depth 1 has budget 0.5."""
        budget = create_depth_based_budget(depth=1)
        assert budget.remaining == 0.5
        assert budget.depth == 1

    def test_depth_two_has_third_budget(self) -> None:
        """Depth 2 has budget ~0.333."""
        budget = create_depth_based_budget(depth=2)
        assert abs(budget.remaining - 0.333) < 0.01
        assert budget.depth == 2

    def test_depth_three_has_quarter_budget(self) -> None:
        """Depth 3 has budget 0.25."""
        budget = create_depth_based_budget(depth=3)
        assert budget.remaining == 0.25
        assert budget.depth == 3

    def test_is_exhausted_below_threshold(self) -> None:
        """Budget is exhausted when below threshold."""
        # Default threshold is 0.1
        # depth=10 gives budget 1/11 ≈ 0.09 < 0.1
        budget = create_depth_based_budget(depth=10)
        assert budget.is_exhausted is True

    def test_is_exhausted_above_threshold(self) -> None:
        """Budget is not exhausted when above threshold."""
        budget = create_depth_based_budget(depth=0)
        assert budget.is_exhausted is False

    def test_custom_threshold(self) -> None:
        """Custom threshold is respected."""
        budget = create_depth_based_budget(depth=3, threshold=0.3)
        # 0.25 < 0.3, so exhausted
        assert budget.is_exhausted is True

        budget2 = create_depth_based_budget(depth=3, threshold=0.2)
        # 0.25 > 0.2, so not exhausted
        assert budget2.is_exhausted is False


class TestSharedEntropyBudgetOperations:
    """Tests for SharedEntropyBudget operations."""

    def test_can_afford(self) -> None:
        """can_afford checks against remaining budget."""
        budget = create_depth_based_budget(depth=1)  # 0.5
        assert budget.can_afford(0.3) is True
        assert budget.can_afford(0.5) is True
        assert budget.can_afford(0.6) is False

    def test_consume_returns_new_budget(self) -> None:
        """consume returns a new budget with reduced remaining."""
        budget = create_depth_based_budget(depth=0)  # 1.0
        new_budget = budget.consume(0.3)

        # Original unchanged
        assert budget.remaining == 1.0

        # New budget has reduced remaining
        assert new_budget.remaining == 0.7
        assert new_budget.depth == budget.depth

    def test_spawn_child_increases_depth(self) -> None:
        """spawn_child creates budget at depth+1."""
        parent = create_depth_based_budget(depth=0)
        child = parent.spawn_child()

        assert child.depth == 1
        assert child.remaining == 0.5
        assert child.initial == 0.5

    def test_spawn_chain(self) -> None:
        """Chained spawn produces correct depths and budgets."""
        b0 = create_depth_based_budget(depth=0)
        b1 = b0.spawn_child()
        b2 = b1.spawn_child()
        b3 = b2.spawn_child()

        assert b0.remaining == 1.0
        assert b1.remaining == 0.5
        assert abs(b2.remaining - 0.333) < 0.01
        assert b3.remaining == 0.25

    def test_to_dict(self) -> None:
        """to_dict serializes correctly."""
        budget = create_depth_based_budget(depth=1)
        d = budget.to_dict()

        assert d["depth"] == 1
        assert d["initial"] == 0.5
        assert d["remaining"] == 0.5
        assert d["threshold"] == 0.1
        assert d["is_exhausted"] is False
        assert d["utilization"] == 0.0  # No consumption yet


class TestBackingStore:
    """Tests for B-gent backing store integration."""

    def test_backing_is_bgent_entropy_budget(self) -> None:
        """Backing store is B-gent EntropyBudget."""
        budget = create_depth_based_budget(depth=0)
        assert isinstance(budget.backing, BgentEntropyBudget)

    def test_backing_tracks_consumption(self) -> None:
        """Backing store tracks consumption."""
        budget = create_depth_based_budget(depth=0)
        new_budget = budget.consume(0.3)

        assert new_budget.backing.remaining == 0.7
        assert new_budget.backing.initial == 1.0


# =============================================================================
# compute_depth_from_budget Tests
# =============================================================================


class TestComputeDepthFromBudget:
    """Tests for compute_depth_from_budget."""

    def test_budget_1_is_depth_0(self) -> None:
        """Budget 1.0 = depth 0."""
        assert compute_depth_from_budget(1.0) == 0

    def test_budget_half_is_depth_1(self) -> None:
        """Budget 0.5 = depth 1."""
        assert compute_depth_from_budget(0.5) == 1

    def test_budget_third_is_depth_2(self) -> None:
        """Budget 0.333 ≈ depth 2."""
        assert compute_depth_from_budget(0.333) == 2

    def test_budget_quarter_is_depth_3(self) -> None:
        """Budget 0.25 = depth 3."""
        assert compute_depth_from_budget(0.25) == 3

    def test_budget_zero_is_infinite_depth(self) -> None:
        """Budget 0 = effectively infinite depth."""
        assert compute_depth_from_budget(0.0) == 999

    def test_budget_negative_is_infinite_depth(self) -> None:
        """Negative budget = effectively infinite depth."""
        assert compute_depth_from_budget(-0.1) == 999


# =============================================================================
# DualEntropyBudget Tests
# =============================================================================


class TestDualEntropyBudget:
    """Tests for DualEntropyBudget."""

    def test_create_dual_budget(self) -> None:
        """create_dual_budget creates both budgets."""
        dual = create_dual_budget(
            economic_budget=1.0,
            recursion_depth=0,
        )

        assert dual.economic.remaining == 1.0
        assert dual.recursion.remaining == 1.0
        assert dual.recursion.depth == 0

    def test_can_proceed_both_satisfied(self) -> None:
        """can_proceed returns True when both budgets allow."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)
        assert dual.can_proceed(0.5, 0.5) is True

    def test_can_proceed_economic_insufficient(self) -> None:
        """can_proceed returns False when economic insufficient."""
        dual = create_dual_budget(economic_budget=0.3, recursion_depth=0)
        assert dual.can_proceed(0.5, 0.0) is False

    def test_can_proceed_recursion_exhausted(self) -> None:
        """can_proceed returns False when recursion exhausted."""
        # depth=10 gives budget ~0.09 < threshold 0.1
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=10)
        assert dual.can_proceed(0.0, 0.0) is False

    def test_spend_reduces_both(self) -> None:
        """spend reduces both budgets."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)
        new_dual = dual.spend(0.3, 0.2)

        assert new_dual.economic.remaining == 0.7
        assert new_dual.recursion.remaining == 0.8

    def test_spawn_child_recursion(self) -> None:
        """spawn_child_recursion increases recursion depth."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)
        child = dual.spawn_child_recursion()

        # Economic shared
        assert child.economic is dual.economic

        # Recursion increased
        assert child.recursion.depth == 1
        assert child.recursion.remaining == 0.5


class TestDualBudgetCoordination:
    """Tests for dual budget coordination patterns."""

    def test_recursive_spawn_chain(self) -> None:
        """Recursive spawn chain maintains economic but reduces recursion."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)

        # Spawn chain
        d1 = dual.spawn_child_recursion()
        d2 = d1.spawn_child_recursion()
        d3 = d2.spawn_child_recursion()

        # All share economic
        assert d3.economic.remaining == 1.0

        # Recursion diminishes
        assert d1.recursion.remaining == 0.5
        assert abs(d2.recursion.remaining - 0.333) < 0.01
        assert d3.recursion.remaining == 0.25

    def test_economic_spending_across_spawns(self) -> None:
        """Economic spending accumulates across spawned children."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)

        # Spend then spawn
        dual = dual.spend(0.2, 0.0)
        child = dual.spawn_child_recursion()

        # Child inherits reduced economic
        assert child.economic.remaining == 0.8

    def test_independent_economic_budgets(self) -> None:
        """Spawning with fresh economic budget is possible."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)

        # Create child with separate economic budget
        child_recursion = dual.recursion.spawn_child()
        child = DualEntropyBudget(
            economic=BgentEntropyBudget(initial=0.5, remaining=0.5),
            recursion=child_recursion,
        )

        # Parent unaffected
        assert dual.economic.remaining == 1.0

        # Child has own budget
        assert child.economic.remaining == 0.5
        assert child.recursion.depth == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests with J-gent and B-gent patterns."""

    def test_jgent_style_depth_exhaustion(self) -> None:
        """Test J-gent style depth exhaustion pattern."""
        budget = create_depth_based_budget(depth=0, threshold=0.1)

        # Simulate recursive calls
        depths_exhausted_at = None
        current = budget

        for depth in range(20):
            if current.is_exhausted:
                depths_exhausted_at = depth
                break
            current = current.spawn_child()

        # Should exhaust around depth 9-10 (1/10 = 0.1, 1/11 ≈ 0.09)
        assert depths_exhausted_at is not None
        assert depths_exhausted_at == 10  # 1/11 < 0.1

    def test_bgent_style_consumption(self) -> None:
        """Test B-gent style consumption pattern."""
        budget = create_depth_based_budget(depth=0)

        # Consume like B-gent would
        costs = [0.2, 0.3, 0.1, 0.15]
        current = budget

        for cost in costs:
            if not current.can_afford(cost):
                break
            current = current.consume(cost)

        # Should have consumed 0.75 total
        assert current.remaining == 0.25

    def test_mixed_consumption_and_spawning(self) -> None:
        """Test mixed consumption and spawning pattern."""
        dual = create_dual_budget(economic_budget=1.0, recursion_depth=0)

        # Level 0: consume some economic
        dual = dual.spend(0.2, 0.0)
        assert dual.economic.remaining == 0.8

        # Level 1: spawn and consume
        level1 = dual.spawn_child_recursion()
        level1 = level1.spend(0.3, 0.1)
        assert level1.economic.remaining == 0.5
        assert level1.recursion.remaining == 0.4

        # Level 2: spawn again
        level2 = level1.spawn_child_recursion()
        assert level2.economic.remaining == 0.5  # Shared
        assert abs(level2.recursion.remaining - 0.333) < 0.01  # 1/3

    def test_budget_serialization_roundtrip(self) -> None:
        """Test that budget can be serialized and conceptually restored."""
        original = create_depth_based_budget(depth=2, threshold=0.15)
        original = original.consume(0.1)

        data = original.to_dict()

        # Reconstruct from data
        reconstructed = SharedEntropyBudget(
            depth=data["depth"],
            backing=BgentEntropyBudget(
                initial=data["initial"],
                remaining=data["remaining"],
            ),
            threshold=data["threshold"],
        )

        assert reconstructed.depth == original.depth
        assert reconstructed.remaining == original.remaining
        assert reconstructed.threshold == original.threshold


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_very_deep_recursion(self) -> None:
        """Very deep recursion produces tiny but positive budget."""
        budget = create_depth_based_budget(depth=1000)
        assert budget.remaining > 0
        assert budget.remaining < 0.01
        assert budget.is_exhausted is True

    def test_consume_more_than_available(self) -> None:
        """Consuming more than available clamps to zero (B-gent behavior)."""
        budget = create_depth_based_budget(depth=0)
        new_budget = budget.consume(1.5)

        # Clamps to zero (B-gent EntropyBudget behavior)
        # Caller should have checked can_afford first
        assert new_budget.remaining == 0.0

    def test_zero_threshold(self) -> None:
        """Zero threshold never exhausts."""
        budget = create_depth_based_budget(depth=1000, threshold=0.0)
        assert budget.is_exhausted is False  # remaining > 0 >= 0

    def test_high_threshold(self) -> None:
        """High threshold exhausts even at depth 0."""
        budget = create_depth_based_budget(depth=0, threshold=1.5)
        assert budget.is_exhausted is True  # 1.0 < 1.5
