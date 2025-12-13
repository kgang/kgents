"""
Tests for TurnBudgetTracker - Phase 7 of Turn-gents Protocol.

Tests cover:
1. Budget initialization
2. Order budget consumption
3. Surplus budget consumption (sacred)
4. Budget exhaustion
5. Replenishment
6. Statistics and history
7. Policy integration
8. Callbacks
"""

import pytest

from ..economics import (
    BudgetPolicy,
    BudgetStats,
    BudgetType,
    TurnBudgetTracker,
    create_default_tracker,
)


class TestBudgetType:
    """Tests for BudgetType enum."""

    def test_two_budget_types(self) -> None:
        """Should have exactly two budget types."""
        assert BudgetType.ORDER
        assert BudgetType.SURPLUS

    def test_types_are_distinct(self) -> None:
        """Budget types should be distinct."""
        # Explicit value comparison to satisfy mypy
        assert BudgetType.ORDER.value != BudgetType.SURPLUS.value


class TestTurnBudgetTrackerInit:
    """Tests for TurnBudgetTracker initialization."""

    def test_default_surplus_fraction(self) -> None:
        """Default surplus fraction is 10%."""
        tracker = TurnBudgetTracker(order_budget=1.0)
        assert tracker.surplus_fraction == 0.1

    def test_surplus_budget_derived(self) -> None:
        """Surplus budget is derived from order budget."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        assert tracker.surplus_budget == 0.1

    def test_custom_surplus_fraction(self) -> None:
        """Can specify custom surplus fraction."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.2)
        assert tracker.surplus_budget == 0.2

    def test_initial_remaining_equals_total(self) -> None:
        """Initially remaining equals total."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        assert tracker.order_remaining == 1.0
        assert tracker.surplus_remaining == 0.1


class TestOrderBudgetConsumption:
    """Tests for order (production) budget consumption."""

    def test_consume_order(self) -> None:
        """Can consume from order budget."""
        tracker = TurnBudgetTracker(order_budget=1.0)

        result = tracker.consume(0.1)

        assert result is True
        assert tracker.order_remaining == 0.9

    def test_can_consume_checks_order(self) -> None:
        """can_consume checks order budget."""
        tracker = TurnBudgetTracker(order_budget=0.1)

        assert tracker.can_consume(0.1) is True
        assert tracker.can_consume(0.2) is False

    def test_consume_returns_false_when_exhausted(self) -> None:
        """consume returns False when budget exhausted."""
        tracker = TurnBudgetTracker(order_budget=0.1)

        result = tracker.consume(0.2)

        assert result is False

    def test_consume_still_records_when_exhausted(self) -> None:
        """Consumption is recorded even when exceeding budget."""
        tracker = TurnBudgetTracker(order_budget=0.1)

        tracker.consume(0.2)

        assert tracker.order_remaining == 0.0  # Clamped to 0
        assert tracker.total_spent == 0.2  # Still tracked


class TestSurplusBudgetConsumption:
    """Tests for surplus (exploration) budget consumption."""

    def test_consume_surplus(self) -> None:
        """Can consume from surplus budget."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

        result = tracker.consume(0.05, is_oblique=True)

        assert result is True
        assert tracker.surplus_remaining == 0.05

    def test_surplus_is_separate(self) -> None:
        """Surplus consumption doesn't affect order budget."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

        tracker.consume(0.05, is_oblique=True)

        assert tracker.order_remaining == 1.0  # Order unchanged
        assert tracker.surplus_remaining == 0.05

    def test_can_consume_checks_surplus(self) -> None:
        """can_consume checks surplus budget for oblique."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

        assert tracker.can_consume(0.1, is_oblique=True) is True
        assert tracker.can_consume(0.2, is_oblique=True) is False

    def test_surplus_sacred_even_when_order_exhausted(self) -> None:
        """Surplus budget remains available when order exhausted."""
        tracker = TurnBudgetTracker(order_budget=0.1, surplus_fraction=0.5)

        # Exhaust order budget
        tracker.consume(0.15)

        # Surplus should still be available
        assert tracker.order_remaining == 0.0
        assert tracker.surplus_remaining == 0.05  # 0.1 * 0.5
        assert tracker.can_consume(0.05, is_oblique=True) is True


class TestBudgetExhaustion:
    """Tests for budget exhaustion handling."""

    def test_should_yield_when_order_exhausted(self) -> None:
        """should_yield_for_budget True when order exhausted."""
        tracker = TurnBudgetTracker(order_budget=0.1)

        tracker.consume(0.15)

        assert tracker.should_yield_for_budget() is True

    def test_should_not_yield_when_has_budget(self) -> None:
        """should_yield_for_budget False when budget available."""
        tracker = TurnBudgetTracker(order_budget=1.0)

        tracker.consume(0.1)

        assert tracker.should_yield_for_budget() is False


class TestReplenishment:
    """Tests for budget replenishment."""

    def test_replenish_restores_order(self) -> None:
        """Replenish restores order budget."""
        tracker = TurnBudgetTracker(order_budget=1.0)
        tracker.consume(0.5)

        tracker.replenish(0.3)

        assert tracker.order_remaining == 0.8  # 0.5 - 0.3 spent = 0.2 remaining deficit

    def test_replenish_with_surplus(self) -> None:
        """Replenish also restores surplus by default."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        tracker.consume(0.5)
        tracker.consume(0.05, is_oblique=True)

        tracker.replenish(1.0, replenish_surplus=True)

        assert tracker.order_remaining == 1.0
        assert tracker.surplus_remaining == 0.1

    def test_reset_clears_all(self) -> None:
        """Reset clears all spending."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        tracker.consume(0.5)
        tracker.consume(0.05, is_oblique=True)

        tracker.reset()

        assert tracker.order_remaining == 1.0
        assert tracker.surplus_remaining == 0.1
        assert tracker.total_spent == 0.0


class TestBudgetStats:
    """Tests for budget statistics."""

    def test_stats_initial(self) -> None:
        """Initial stats reflect full budget."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

        stats = tracker.stats()

        assert stats.order_total == 1.0
        assert stats.order_remaining == 1.0
        assert stats.order_spent == 0.0
        assert stats.order_utilization == 0.0

    def test_stats_after_consumption(self) -> None:
        """Stats reflect consumption."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        tracker.consume(0.5)
        tracker.consume(0.05, is_oblique=True)

        stats = tracker.stats()

        assert stats.order_spent == 0.5
        assert stats.order_utilization == 0.5
        assert stats.surplus_spent == 0.05
        assert stats.total_spent == 0.55

    def test_exploration_ratio(self) -> None:
        """Exploration ratio calculated correctly."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        tracker.consume(0.9)  # 90% order
        tracker.consume(0.1, is_oblique=True)  # 10% surplus

        stats = tracker.stats()

        assert stats.exploration_ratio == 0.1

    def test_exploration_ratio_zero_spending(self) -> None:
        """Exploration ratio is 0 when nothing spent."""
        tracker = TurnBudgetTracker(order_budget=1.0)

        stats = tracker.stats()

        assert stats.exploration_ratio == 0.0


class TestBudgetHistory:
    """Tests for consumption history."""

    def test_history_empty_initially(self) -> None:
        """History is empty initially."""
        tracker = TurnBudgetTracker(order_budget=1.0)

        assert tracker.history() == []

    def test_history_records_consumption(self) -> None:
        """History records each consumption."""
        tracker = TurnBudgetTracker(order_budget=1.0)

        tracker.consume(0.1, turn_id="turn-1", reason="test")
        tracker.consume(0.2, is_oblique=True, turn_id="turn-2", reason="explore")

        history = tracker.history()
        assert len(history) == 2
        assert history[0].amount == 0.1
        assert history[0].budget_type == BudgetType.ORDER
        assert history[0].turn_id == "turn-1"
        assert history[1].budget_type == BudgetType.SURPLUS

    def test_reset_clears_history(self) -> None:
        """Reset clears consumption history."""
        tracker = TurnBudgetTracker(order_budget=1.0)
        tracker.consume(0.1)

        tracker.reset()

        assert tracker.history() == []


class TestBudgetCallbacks:
    """Tests for exhaustion callbacks."""

    def test_callback_on_order_exhaustion(self) -> None:
        """Callback triggered on order exhaustion."""
        tracker = TurnBudgetTracker(order_budget=0.1)
        callback_data: list[tuple[BudgetType, BudgetStats]] = []

        def on_exhausted(budget_type: BudgetType, stats: BudgetStats) -> None:
            callback_data.append((budget_type, stats))

        tracker.on_exhausted(on_exhausted)
        tracker.consume(0.2)

        assert len(callback_data) == 1
        assert callback_data[0][0] == BudgetType.ORDER

    def test_callback_on_surplus_exhaustion(self) -> None:
        """Callback triggered on surplus exhaustion."""
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)
        callback_data: list[BudgetType] = []

        def on_exhausted(budget_type: BudgetType, stats: BudgetStats) -> None:
            callback_data.append(budget_type)

        tracker.on_exhausted(on_exhausted)
        tracker.consume(0.2, is_oblique=True)

        assert len(callback_data) == 1
        assert callback_data[0] == BudgetType.SURPLUS


class TestBudgetPolicy:
    """Tests for BudgetPolicy."""

    def test_default_yields_on_order_exhaustion(self) -> None:
        """Default policy yields on order exhaustion."""
        policy = BudgetPolicy()

        assert policy.yield_on_order_exhaustion is True
        assert policy.yield_on_surplus_exhaustion is False

    def test_should_yield_order_exhausted(self) -> None:
        """should_yield True when order exhausted."""
        policy = BudgetPolicy(yield_on_order_exhaustion=True)
        stats = BudgetStats(
            order_total=1.0,
            order_remaining=0.0,  # Exhausted
            order_spent=1.0,
            order_utilization=1.0,
            surplus_total=0.1,
            surplus_remaining=0.1,
            surplus_spent=0.0,
            surplus_utilization=0.0,
            total_spent=1.0,
            total_remaining=0.1,
        )

        assert policy.should_yield(stats) is True

    def test_should_encourage_exploration(self) -> None:
        """should_encourage_exploration when ratio low."""
        policy = BudgetPolicy(minimum_exploration_ratio=0.1)
        stats = BudgetStats(
            order_total=1.0,
            order_remaining=0.5,
            order_spent=0.5,
            order_utilization=0.5,
            surplus_total=0.1,
            surplus_remaining=0.1,
            surplus_spent=0.0,  # No exploration yet
            surplus_utilization=0.0,
            total_spent=0.5,
            total_remaining=0.6,
        )

        assert policy.should_encourage_exploration(stats) is True


class TestCreateDefaultTracker:
    """Tests for create_default_tracker convenience function."""

    def test_creates_tracker(self) -> None:
        """Creates a tracker with defaults."""
        tracker = create_default_tracker()

        assert tracker.order_budget == 1.0
        assert tracker.surplus_fraction == 0.1

    def test_custom_values(self) -> None:
        """Can customize tracker values."""
        tracker = create_default_tracker(entropy_budget=2.0, surplus_fraction=0.2)

        assert tracker.order_budget == 2.0
        assert tracker.surplus_budget == 0.4


class TestBudgetStatsProperties:
    """Tests for BudgetStats derived properties."""

    def test_is_order_exhausted(self) -> None:
        """is_order_exhausted when remaining is 0."""
        stats = BudgetStats(
            order_total=1.0,
            order_remaining=0.0,
            order_spent=1.0,
            order_utilization=1.0,
            surplus_total=0.1,
            surplus_remaining=0.1,
            surplus_spent=0.0,
            surplus_utilization=0.0,
            total_spent=1.0,
            total_remaining=0.1,
        )

        assert stats.is_order_exhausted is True
        assert stats.is_surplus_exhausted is False

    def test_is_surplus_exhausted(self) -> None:
        """is_surplus_exhausted when remaining is 0."""
        stats = BudgetStats(
            order_total=1.0,
            order_remaining=1.0,
            order_spent=0.0,
            order_utilization=0.0,
            surplus_total=0.1,
            surplus_remaining=0.0,  # Exhausted
            surplus_spent=0.1,
            surplus_utilization=1.0,
            total_spent=0.1,
            total_remaining=1.0,
        )

        assert stats.is_order_exhausted is False
        assert stats.is_surplus_exhausted is True
