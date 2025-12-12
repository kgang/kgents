"""
Tests for Resource Budget Context Managers

Tests verify:
1. Context manager lifecycle (issue, use, settle)
2. Automatic settlement on exit (even with exceptions)
3. Recovery rate for unused budget
4. Suballocation patterns
"""

from __future__ import annotations

import pytest
from shared.budget import (
    ResourceBudget,
    issue_budget,
    suballocate,
)
from shared.capital import (
    EventSourcedLedger,
    InsufficientCapitalError,
)

# === Fixtures ===


@pytest.fixture
def ledger() -> EventSourcedLedger:
    """Fresh ledger per test."""
    return EventSourcedLedger()


@pytest.fixture
def funded_ledger() -> EventSourcedLedger:
    """Ledger with funded test agent."""
    ledger = EventSourcedLedger()
    ledger.issue("test-agent", 0.5, "test_setup")
    return ledger


# === Basic Context Manager Tests ===


def test_issue_budget_creates_budget(funded_ledger: EventSourcedLedger) -> None:
    """issue_budget creates a ResourceBudget."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        assert isinstance(budget, ResourceBudget)
        assert budget.agent == "test-agent"
        assert budget.initial == 0.2
        assert budget.remaining == 0.2


def test_issue_budget_debits_upfront(funded_ledger: EventSourcedLedger) -> None:
    """Budget allocation debits capital immediately."""
    initial = funded_ledger.balance("test-agent")

    with issue_budget(funded_ledger, "test-agent", 0.2):
        # During context, capital is debited
        pass

    # After full use, no recovery
    # But we didn't spend anything, so partial recovery
    # initial_capital + issued - debit + (recovery of unused)
    # The debit happens, then recovery of 50% of unused (0.2)
    expected = initial - 0.2 + (0.2 * 0.5)  # 50% recovery
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


def test_budget_spend_reduces_remaining(funded_ledger: EventSourcedLedger) -> None:
    """spend() reduces remaining budget."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        success = budget.spend(0.05)
        assert success
        assert budget.remaining == pytest.approx(0.15)
        assert budget.spent == pytest.approx(0.05)


def test_budget_spend_returns_false_if_insufficient(
    funded_ledger: EventSourcedLedger,
) -> None:
    """spend() returns False if insufficient (no exception)."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        success = budget.spend(0.3)  # More than remaining
        assert not success
        assert budget.remaining == 0.2  # Unchanged


def test_budget_spend_or_raise_raises_if_insufficient(
    funded_ledger: EventSourcedLedger,
) -> None:
    """spend_or_raise() raises InsufficientCapitalError."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        with pytest.raises(InsufficientCapitalError) as exc_info:
            budget.spend_or_raise(0.3, "test_operation")

        assert "Budget exhausted" in str(exc_info.value)


# === Settlement Tests ===


def test_budget_settles_on_exit(funded_ledger: EventSourcedLedger) -> None:
    """Budget is settled on context exit."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        budget.spend(0.1)  # Spend half

    assert budget.is_settled


def test_unused_budget_partially_recovered(funded_ledger: EventSourcedLedger) -> None:
    """Unused budget is partially credited back."""
    initial = funded_ledger.balance("test-agent")

    with issue_budget(funded_ledger, "test-agent", 0.2, recovery_rate=0.5) as budget:
        budget.spend(0.1)  # Spend half, 0.1 unused

    # Recovery: 0.1 * 0.5 = 0.05
    expected = initial - 0.2 + 0.05
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


def test_fully_spent_budget_no_recovery(funded_ledger: EventSourcedLedger) -> None:
    """Fully spent budget has no recovery."""
    initial = funded_ledger.balance("test-agent")

    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        budget.spend(0.2)  # Spend all

    expected = initial - 0.2  # No recovery
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


def test_settlement_is_idempotent(funded_ledger: EventSourcedLedger) -> None:
    """Calling settle() multiple times has no effect."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        pass

    balance_after = funded_ledger.balance("test-agent")

    # Manually call settle again
    budget.settle()
    budget.settle()

    assert funded_ledger.balance("test-agent") == balance_after


def test_settlement_on_exception(funded_ledger: EventSourcedLedger) -> None:
    """Budget is settled even if exception occurs."""
    initial = funded_ledger.balance("test-agent")

    try:
        with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
            budget.spend(0.1)
            raise ValueError("Test exception")
    except ValueError:
        pass

    assert budget.is_settled
    # Recovery should still happen
    expected = initial - 0.2 + (0.1 * 0.5)  # 50% of unused
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


# === Insufficient Capital Tests ===


def test_issue_budget_raises_if_insufficient(ledger: EventSourcedLedger) -> None:
    """issue_budget raises if agent lacks capital."""
    with pytest.raises(InsufficientCapitalError) as exc_info:
        with issue_budget(ledger, "poor-agent", 100.0):
            pass

    assert "poor-agent" in str(exc_info.value)


# === Budget Properties Tests ===


def test_budget_is_exhausted(funded_ledger: EventSourcedLedger) -> None:
    """is_exhausted is True when remaining is zero."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        assert not budget.is_exhausted
        budget.spend(0.2)
        assert budget.is_exhausted


# === Suballocation Tests ===


def test_suballocate_from_parent(funded_ledger: EventSourcedLedger) -> None:
    """suballocate creates a sub-budget from parent."""
    with issue_budget(funded_ledger, "test-agent", 0.3) as main:
        with suballocate(main, 0.1) as sub:
            assert sub.initial == 0.1
            assert sub.remaining == 0.1
            assert main.remaining == pytest.approx(0.2)  # Parent reduced


def test_suballocate_returns_to_parent(funded_ledger: EventSourcedLedger) -> None:
    """Sub-budget unused amount returns to parent, not ledger."""
    with issue_budget(funded_ledger, "test-agent", 0.3) as main:
        with suballocate(main, 0.1) as sub:
            sub.spend(0.05)  # Use half

        # Unused (0.05) returns to parent at 100%
        assert main.remaining == pytest.approx(0.2 + 0.05)


def test_suballocate_raises_if_parent_exhausted(
    funded_ledger: EventSourcedLedger,
) -> None:
    """suballocate raises if parent lacks sufficient budget."""
    with issue_budget(funded_ledger, "test-agent", 0.1) as main:
        with pytest.raises(InsufficientCapitalError):
            with suballocate(main, 0.2):  # More than parent has
                pass


def test_nested_suballocation(funded_ledger: EventSourcedLedger) -> None:
    """Suballocations can be nested."""
    with issue_budget(funded_ledger, "test-agent", 0.5) as main:
        with suballocate(main, 0.3) as level1:
            with suballocate(level1, 0.1) as level2:
                level2.spend(0.05)

            # level2 returns 0.05 to level1
            assert level1.remaining == pytest.approx(0.2 + 0.05)

        # level1 returns (0.25) to main
        assert main.remaining == pytest.approx(0.2 + 0.25)


# === Recovery Rate Tests ===


def test_custom_recovery_rate(funded_ledger: EventSourcedLedger) -> None:
    """Custom recovery rate is respected."""
    initial = funded_ledger.balance("test-agent")

    # 80% recovery rate
    with issue_budget(funded_ledger, "test-agent", 0.2, recovery_rate=0.8) as budget:
        budget.spend(0.1)  # 0.1 unused

    # Recovery: 0.1 * 0.8 = 0.08
    expected = initial - 0.2 + 0.08
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


def test_zero_recovery_rate(funded_ledger: EventSourcedLedger) -> None:
    """Zero recovery rate means no return."""
    initial = funded_ledger.balance("test-agent")

    with issue_budget(funded_ledger, "test-agent", 0.2, recovery_rate=0.0) as budget:
        budget.spend(0.1)

    # No recovery
    expected = initial - 0.2
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


def test_full_recovery_rate(funded_ledger: EventSourcedLedger) -> None:
    """100% recovery rate returns all unused."""
    initial = funded_ledger.balance("test-agent")

    with issue_budget(funded_ledger, "test-agent", 0.2, recovery_rate=1.0) as budget:
        budget.spend(0.1)

    # Full recovery: 0.1 * 1.0 = 0.1
    expected = initial - 0.2 + 0.1
    assert funded_ledger.balance("test-agent") == pytest.approx(expected)


# === Correlation ID Tests ===


def test_budget_has_correlation_id(funded_ledger: EventSourcedLedger) -> None:
    """Budget tracks correlation ID from debit event."""
    with issue_budget(funded_ledger, "test-agent", 0.2) as budget:
        assert budget._correlation_id != ""

        # Find the debit event
        events = funded_ledger.witness("test-agent")
        debit_event = next(e for e in events if e.event_type == "DEBIT")
        assert budget._correlation_id == debit_event.correlation_id
