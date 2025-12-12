"""
Resource Budget Context Managers

Pythonic approximation of linear types via context managers.

Design Insight: Python cannot enforce linearity at the type level.
Context managers are Python's native lifecycle mechanism—use them.

Usage:
    with issue_budget(ledger, agent, 100) as budget:
        budget.spend(50)
    # Budget automatically settled on exit

Principle Alignment:
- Joy-Inducing: Pythonic patterns over fighting the type system
- Composable: Budgets compose within nested contexts
- Ethical: Automatic settlement prevents resource leaks
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from .capital import EventSourcedLedger

from .capital import InsufficientCapitalError

# === Resource Budget ===


@dataclass
class ResourceBudget:
    """
    A scoped resource budget.

    Usage:
        with issue_budget(ledger, agent, 100) as budget:
            # Budget is live
            budget.spend(50)
        # Budget automatically settled on exit

    Lifecycle:
    1. Budget issued (capital debited from ledger)
    2. Operations consume from budget
    3. On exit, unused budget partially returned
    """

    agent: str
    initial: float
    remaining: float
    ledger: "EventSourcedLedger"
    recovery_rate: float = 0.5  # 50% of unused budget returned
    _settled: bool = field(default=False, repr=False)
    _correlation_id: str = field(default="", repr=False)

    def spend(self, amount: float) -> bool:
        """
        Spend from budget.

        Returns False if insufficient budget (does not throw).
        This allows callers to handle the failure gracefully.
        """
        if amount > self.remaining:
            return False
        self.remaining -= amount
        return True

    def spend_or_raise(self, amount: float, reason: str = "operation") -> None:
        """
        Spend from budget, raising if insufficient.

        Use when failure should halt the operation.
        """
        if amount > self.remaining:
            raise InsufficientCapitalError(
                f"Budget exhausted for {reason}",
                agent=self.agent,
                required=amount,
                available=self.remaining,
            )
        self.remaining -= amount

    def settle(self) -> float:
        """
        Return unused budget to ledger.

        Returns the amount credited back (after recovery rate applied).
        Called automatically by context manager.
        """
        if self._settled:
            return 0.0

        self._settled = True
        unused = self.remaining

        if unused > 0:
            # Partial recovery—entropy tax for unused allocation
            recovery = unused * self.recovery_rate
            self.ledger.credit(
                self.agent,
                recovery,
                "budget_return",
                correlation_id=self._correlation_id,
                original_unused=unused,
                recovery_rate=self.recovery_rate,
            )
            return recovery
        return 0.0

    @property
    def spent(self) -> float:
        """Amount spent from this budget."""
        return self.initial - self.remaining

    @property
    def is_exhausted(self) -> bool:
        """True if no budget remains."""
        return self.remaining <= 0

    @property
    def is_settled(self) -> bool:
        """True if budget has been settled."""
        return self._settled


# === Context Manager ===


@contextmanager
def issue_budget(
    ledger: "EventSourcedLedger",
    agent: str,
    amount: float,
    *,
    recovery_rate: float = 0.5,
) -> Generator[ResourceBudget, None, None]:
    """
    Issue a scoped resource budget.

    Pythonic approximation of linear types via context manager.
    The budget is automatically settled on exit, even if an exception occurs.

    Args:
        ledger: The capital ledger to debit from
        agent: The agent requesting the budget
        amount: The amount to allocate
        recovery_rate: Fraction of unused budget to return (default 50%)

    Raises:
        InsufficientCapitalError: If agent lacks sufficient capital

    Example:
        with issue_budget(ledger, "b-gent", 0.3) as budget:
            if budget.spend(0.1):
                do_operation()
            else:
                handle_insufficient_budget()
        # Automatically settles, returning unused * recovery_rate
    """
    # Check balance and debit upfront
    current_balance = ledger.balance(agent)
    if current_balance < amount:
        raise InsufficientCapitalError(
            f"{agent} lacks capital for budget allocation",
            agent=agent,
            required=amount,
            available=current_balance,
        )

    # Debit the full amount
    event = ledger.debit(agent, amount, "budget_issue")
    if event is None:
        # Should not happen given the check above, but handle defensively
        raise InsufficientCapitalError(
            f"Failed to debit {amount} from {agent}",
            agent=agent,
            required=amount,
            available=current_balance,
        )

    budget = ResourceBudget(
        agent=agent,
        initial=amount,
        remaining=amount,
        ledger=ledger,
        recovery_rate=recovery_rate,
        _correlation_id=event.correlation_id,
    )

    try:
        yield budget
    finally:
        # Always settle, even on exception
        budget.settle()


# === Nested Budget Context ===


@contextmanager
def suballocate(
    parent: ResourceBudget,
    amount: float,
) -> Generator[ResourceBudget, None, None]:
    """
    Allocate a sub-budget from a parent budget.

    Useful for hierarchical resource management.

    Example:
        with issue_budget(ledger, "agent", 1.0) as main:
            with suballocate(main, 0.3) as sub:
                sub.spend(0.1)
            # sub settles, returning to main (not ledger)
    """
    if not parent.spend(amount):
        raise InsufficientCapitalError(
            "Parent budget exhausted for suballocation",
            agent=parent.agent,
            required=amount,
            available=parent.remaining,
        )

    # Create a pseudo-budget that returns to parent on settle
    class SubBudget(ResourceBudget):
        def settle(self) -> float:
            if self._settled:
                return 0.0
            self._settled = True
            unused = self.remaining
            if unused > 0:
                # Return directly to parent (full recovery within same context)
                parent.remaining += unused
            return unused

    sub = SubBudget(
        agent=parent.agent,
        initial=amount,
        remaining=amount,
        ledger=parent.ledger,
        recovery_rate=1.0,  # Full recovery within context
    )

    try:
        yield sub
    finally:
        sub.settle()
