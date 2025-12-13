"""
TurnBudgetTracker - Economics Integration for Turn-gents.

Phase 7 of the Turn-gents Protocol: Operationalize the Accursed Share.

This module implements the two-budget system:
1. Order Budget: Production-critical turns (metered, bounded)
2. Surplus Budget: Exploration/oblique turns (sacred, 10% default)

The key insight from Bataille's Accursed Share:
"The surplus is not waste to be minimized, but sacred expenditure."

Exploration is first-class. The surplus budget is explicitly reserved
and cannot be reclaimed for production work.

Example:
    tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

    # Production turn
    if tracker.can_consume(0.05, is_oblique=False):
        tracker.consume(0.05, is_oblique=False)

    # Exploration turn (uses surplus budget)
    if tracker.can_consume(0.02, is_oblique=True):
        tracker.consume(0.02, is_oblique=True)

    # Budget exhausted triggers YIELD
    if not tracker.can_consume(0.5, is_oblique=False):
        # Request more budget or yield
        ...

References:
- Bataille, G. "The Accursed Share" (1949)
- Turn-gents Plan: Phase 7 (Economics Integration)
- principles.md: Joy-Inducing, Accursed Share
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class BudgetType(Enum):
    """Type of budget being consumed."""

    ORDER = auto()  # Production-critical
    SURPLUS = auto()  # Exploration (sacred)


@dataclass
class BudgetConsumption:
    """Record of a budget consumption event."""

    amount: float
    budget_type: BudgetType
    turn_id: str | None
    reason: str
    timestamp: float


@dataclass
class BudgetStats:
    """Statistics about budget usage."""

    order_total: float
    order_remaining: float
    order_spent: float
    order_utilization: float

    surplus_total: float
    surplus_remaining: float
    surplus_spent: float
    surplus_utilization: float

    total_spent: float
    total_remaining: float

    @property
    def is_order_exhausted(self) -> bool:
        """Check if order budget is exhausted."""
        return self.order_remaining <= 0.0

    @property
    def is_surplus_exhausted(self) -> bool:
        """Check if surplus budget is exhausted."""
        return self.surplus_remaining <= 0.0

    @property
    def exploration_ratio(self) -> float:
        """Ratio of surplus to total spending."""
        if self.total_spent == 0:
            return 0.0
        return self.surplus_spent / self.total_spent


@dataclass
class TurnBudgetTracker:
    """
    Tracks entropy budgets for Turn-gents economics.

    Implements the two-budget system from the Accursed Share:
    - Order Budget: For production-critical, goal-directed turns
    - Surplus Budget: For exploration, serendipity, oblique turns

    The surplus budget is "sacred" - it cannot be reclaimed for
    production work, even if order budget is exhausted.

    Example:
        tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

        # Order budget: 1.0
        # Surplus budget: 0.1 (10% of order)

        tracker.consume(0.05)  # From order budget
        tracker.consume(0.02, is_oblique=True)  # From surplus budget

    Args:
        order_budget: Initial order (production) budget
        surplus_fraction: Fraction of order budget for surplus (default: 0.1)
    """

    order_budget: float
    surplus_fraction: float = 0.1

    # Runtime state
    _order_spent: float = field(default=0.0, init=False)
    _surplus_spent: float = field(default=0.0, init=False)
    _history: list[BudgetConsumption] = field(default_factory=list, init=False)
    _callbacks: list[Any] = field(default_factory=list, init=False)

    @property
    def surplus_budget(self) -> float:
        """Total surplus budget (derived from order_budget * surplus_fraction)."""
        return self.order_budget * self.surplus_fraction

    @property
    def order_remaining(self) -> float:
        """Remaining order budget."""
        return max(0.0, self.order_budget - self._order_spent)

    @property
    def surplus_remaining(self) -> float:
        """Remaining surplus budget."""
        return max(0.0, self.surplus_budget - self._surplus_spent)

    @property
    def total_remaining(self) -> float:
        """Total remaining budget (order + surplus)."""
        return self.order_remaining + self.surplus_remaining

    @property
    def total_spent(self) -> float:
        """Total spent (order + surplus)."""
        return self._order_spent + self._surplus_spent

    def can_consume(self, cost: float, *, is_oblique: bool = False) -> bool:
        """
        Check if budget can cover a cost.

        Args:
            cost: The cost to check
            is_oblique: If True, check surplus budget; otherwise order

        Returns:
            True if budget is available
        """
        if is_oblique:
            return self.surplus_remaining >= cost
        else:
            return self.order_remaining >= cost

    def consume(
        self,
        cost: float,
        *,
        is_oblique: bool = False,
        turn_id: str | None = None,
        reason: str = "",
    ) -> bool:
        """
        Consume from appropriate budget.

        Args:
            cost: The cost to consume
            is_oblique: If True, consume from surplus; otherwise order
            turn_id: Optional turn ID for tracking
            reason: Optional reason for consumption

        Returns:
            True if consumption succeeded, False if exhausted

        Note:
            Even if False is returned, the consumption is still recorded
            (as a deficit). The return value indicates whether the budget
            was sufficient.
        """
        import time

        budget_type = BudgetType.SURPLUS if is_oblique else BudgetType.ORDER

        # Record consumption
        consumption = BudgetConsumption(
            amount=cost,
            budget_type=budget_type,
            turn_id=turn_id,
            reason=reason,
            timestamp=time.time(),
        )
        self._history.append(consumption)

        # Apply consumption
        if is_oblique:
            had_budget = self._surplus_spent + cost <= self.surplus_budget
            self._surplus_spent += cost
        else:
            had_budget = self._order_spent + cost <= self.order_budget
            self._order_spent += cost

        # Trigger callbacks if budget exhausted
        if not had_budget:
            for callback in self._callbacks:
                try:
                    callback(budget_type, self.stats())
                except Exception:
                    pass

        return had_budget

    def replenish(self, amount: float, *, replenish_surplus: bool = True) -> None:
        """
        Replenish budgets.

        Args:
            amount: Amount to add to order budget
            replenish_surplus: If True, also replenish surplus proportionally

        Note:
            This resets spending, not increases the total budget.
            It's like getting a new budget allocation, not a bigger budget.
        """
        # Reset spending toward the budgets
        if amount > self._order_spent:
            self._order_spent = 0.0
        else:
            self._order_spent -= amount

        if replenish_surplus:
            surplus_replenish = amount * self.surplus_fraction
            if surplus_replenish > self._surplus_spent:
                self._surplus_spent = 0.0
            else:
                self._surplus_spent -= surplus_replenish

    def reset(self) -> None:
        """Reset all budgets to initial state."""
        self._order_spent = 0.0
        self._surplus_spent = 0.0
        self._history.clear()

    def stats(self) -> BudgetStats:
        """
        Get current budget statistics.

        Returns:
            BudgetStats with current state
        """
        order_util = (
            self._order_spent / self.order_budget if self.order_budget > 0 else 0
        )
        surplus_util = (
            self._surplus_spent / self.surplus_budget if self.surplus_budget > 0 else 0
        )

        return BudgetStats(
            order_total=self.order_budget,
            order_remaining=self.order_remaining,
            order_spent=self._order_spent,
            order_utilization=min(1.0, order_util),
            surplus_total=self.surplus_budget,
            surplus_remaining=self.surplus_remaining,
            surplus_spent=self._surplus_spent,
            surplus_utilization=min(1.0, surplus_util),
            total_spent=self.total_spent,
            total_remaining=self.total_remaining,
        )

    def history(self) -> list[BudgetConsumption]:
        """Get consumption history."""
        return list(self._history)

    def on_exhausted(self, callback: Any) -> None:
        """
        Register callback for budget exhaustion events.

        The callback receives (BudgetType, BudgetStats).

        Args:
            callback: Function to call when a budget is exhausted
        """
        self._callbacks.append(callback)

    def should_yield_for_budget(self) -> bool:
        """
        Check if agent should YIELD due to budget exhaustion.

        Returns:
            True if order budget is exhausted and agent should yield
        """
        return self.order_remaining <= 0.0


@dataclass
class BudgetPolicy:
    """
    Policy for budget management.

    Defines rules for automatic budget decisions.
    """

    # When to auto-yield
    yield_on_order_exhaustion: bool = True
    yield_on_surplus_exhaustion: bool = False  # Surplus exhaustion is okay

    # Exploration requirements
    minimum_exploration_ratio: float = 0.05  # At least 5% exploration

    # Replenishment
    auto_replenish: bool = False
    replenish_amount: float = 0.0
    replenish_interval: float = 0.0  # In seconds

    def should_yield(self, stats: BudgetStats) -> bool:
        """
        Determine if agent should yield based on budget stats.

        Args:
            stats: Current budget statistics

        Returns:
            True if agent should yield for budget reasons
        """
        if self.yield_on_order_exhaustion and stats.is_order_exhausted:
            return True
        if self.yield_on_surplus_exhaustion and stats.is_surplus_exhausted:
            return True
        return False

    def should_encourage_exploration(self, stats: BudgetStats) -> bool:
        """
        Determine if agent should be encouraged to explore.

        Args:
            stats: Current budget statistics

        Returns:
            True if exploration ratio is below minimum
        """
        return stats.exploration_ratio < self.minimum_exploration_ratio


def create_default_tracker(
    entropy_budget: float = 1.0, surplus_fraction: float = 0.1
) -> TurnBudgetTracker:
    """
    Create a budget tracker with default settings.

    Args:
        entropy_budget: Initial order budget (default: 1.0)
        surplus_fraction: Fraction for surplus (default: 0.1)

    Returns:
        Configured TurnBudgetTracker
    """
    return TurnBudgetTracker(
        order_budget=entropy_budget,
        surplus_fraction=surplus_fraction,
    )


__all__ = [
    "TurnBudgetTracker",
    "BudgetType",
    "BudgetConsumption",
    "BudgetStats",
    "BudgetPolicy",
    "create_default_tracker",
]
