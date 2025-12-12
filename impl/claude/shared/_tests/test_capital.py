"""
Tests for Event-Sourced Capital Ledger

Tests verify:
1. Event sourcing invariants (balance is projection)
2. OCap pattern (BypassToken is capability)
3. Accursed Share (potlatch burns capital)
4. Immutability (events are frozen)

Property-based tests ensure the spec is correct regardless of implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from shared.capital import (
    BypassToken,
    EventSourcedLedger,
    InsufficientCapitalError,
    LedgerEvent,
)

# === Fixtures ===


@pytest.fixture
def ledger() -> EventSourcedLedger:
    """Fresh ledger per test—no shared state."""
    return EventSourcedLedger()


@pytest.fixture
def funded_ledger() -> EventSourcedLedger:
    """Ledger with test agent funded."""
    ledger = EventSourcedLedger()
    ledger.credit("test-agent", 0.5, "test_setup")
    return ledger


# === Event Immutability Tests ===


def test_events_are_immutable() -> None:
    """Events cannot be modified after creation (frozen=True)."""
    event = LedgerEvent(event_type="CREDIT", agent="a", amount=1.0)

    with pytest.raises((AttributeError, TypeError)):
        event.amount = 2.0  # type: ignore[misc]


def test_event_is_credit() -> None:
    """is_credit correctly identifies credit events."""
    assert LedgerEvent(event_type="CREDIT", agent="a", amount=1.0).is_credit()
    assert LedgerEvent(event_type="ISSUE", agent="a", amount=1.0).is_credit()
    assert not LedgerEvent(event_type="DEBIT", agent="a", amount=1.0).is_credit()
    assert not LedgerEvent(event_type="POTLATCH", agent="a", amount=1.0).is_credit()


def test_event_is_debit() -> None:
    """is_debit correctly identifies debit events."""
    assert LedgerEvent(event_type="DEBIT", agent="a", amount=1.0).is_debit()
    assert LedgerEvent(event_type="BYPASS", agent="a", amount=1.0).is_debit()
    assert LedgerEvent(event_type="DECAY", agent="a", amount=1.0).is_debit()
    assert LedgerEvent(event_type="POTLATCH", agent="a", amount=1.0).is_debit()
    assert not LedgerEvent(event_type="CREDIT", agent="a", amount=1.0).is_debit()


# === Balance Projection Tests ===


def test_balance_starts_at_initial_capital(ledger: EventSourcedLedger) -> None:
    """New agents start with initial_capital."""
    assert ledger.balance("new-agent") == ledger.initial_capital


def test_balance_is_derived_from_events(ledger: EventSourcedLedger) -> None:
    """Balance is computed from event stream, not stored."""
    agent = "test-agent"

    # Credit increases balance
    ledger.credit(agent, 0.2, "test")
    assert ledger.balance(agent) == ledger.initial_capital + 0.2

    # Debit decreases balance
    ledger.debit(agent, 0.1, "test")
    assert ledger.balance(agent) == ledger.initial_capital + 0.2 - 0.1


def test_balance_clamped_to_max(ledger: EventSourcedLedger) -> None:
    """Balance cannot exceed max_capital (prevents oligarchs)."""
    ledger.credit("agent", 100.0, "huge_credit")
    assert ledger.balance("agent") == ledger.max_capital


def test_balance_clamped_to_zero(ledger: EventSourcedLedger) -> None:
    """Balance cannot go negative."""
    # Debit more than balance (will fail at debit, but let's test projection)
    # Manually create a debit event to test clamping
    ledger._events.append(LedgerEvent(event_type="DEBIT", agent="agent", amount=100.0))
    assert ledger.balance("agent") == 0.0


def test_debit_fails_if_insufficient_balance(ledger: EventSourcedLedger) -> None:
    """Debit returns None if agent lacks sufficient capital."""
    result = ledger.debit("agent", 100.0, "too_much")
    assert result is None


def test_debit_succeeds_with_sufficient_balance(
    funded_ledger: EventSourcedLedger,
) -> None:
    """Debit returns event if agent has sufficient capital."""
    result = funded_ledger.debit("test-agent", 0.3, "valid_debit")
    assert result is not None
    assert result.event_type == "DEBIT"
    assert result.amount == 0.3


# === Witness (Event History) Tests ===


def test_witness_returns_event_stream(ledger: EventSourcedLedger) -> None:
    """witness returns the event history."""
    ledger.credit("agent", 0.1, "first")
    ledger.debit("agent", 0.05, "second")

    history = ledger.witness("agent")
    assert len(history) == 2
    assert history[0].event_type == "CREDIT"
    assert history[1].event_type == "DEBIT"


def test_witness_filters_by_agent(ledger: EventSourcedLedger) -> None:
    """witness filters events by agent."""
    ledger.credit("agent-a", 0.1, "a")
    ledger.credit("agent-b", 0.2, "b")

    history_a = ledger.witness("agent-a")
    assert len(history_a) == 1
    assert history_a[0].agent == "agent-a"


def test_witness_limits_results(ledger: EventSourcedLedger) -> None:
    """witness respects limit parameter."""
    for i in range(10):
        ledger.credit("agent", 0.01, f"credit_{i}")

    history = ledger.witness("agent", limit=3)
    assert len(history) == 3


# === Potlatch (Accursed Share) Tests ===


def test_potlatch_burns_capital(funded_ledger: EventSourcedLedger) -> None:
    """Potlatch destroys capital (Accursed Share)."""
    initial = funded_ledger.balance("test-agent")
    event = funded_ledger.potlatch("test-agent", 0.2)

    assert event is not None
    assert event.event_type == "POTLATCH"
    assert funded_ledger.balance("test-agent") == initial - 0.2


def test_potlatch_fails_if_insufficient(ledger: EventSourcedLedger) -> None:
    """Potlatch fails if agent lacks capital to burn."""
    result = ledger.potlatch("poor-agent", 100.0)
    assert result is None


# === Bypass Token (OCap) Tests ===


def test_mint_bypass_returns_token(funded_ledger: EventSourcedLedger) -> None:
    """mint_bypass creates a BypassToken capability."""
    token = funded_ledger.mint_bypass("test-agent", "trust_gate", 0.2)

    assert token is not None
    assert isinstance(token, BypassToken)
    assert token.agent == "test-agent"
    assert token.check_name == "trust_gate"
    assert token.cost == 0.2


def test_bypass_token_is_valid_before_expiration() -> None:
    """Token is valid before expiration."""
    now = datetime.now(UTC)
    token = BypassToken(
        agent="agent",
        check_name="test",
        granted_at=now,
        expires_at=now + timedelta(seconds=60),
        cost=0.1,
        correlation_id="test-id",
    )
    assert token.is_valid()


def test_bypass_token_is_invalid_after_expiration() -> None:
    """Token is invalid after expiration."""
    now = datetime.now(UTC)
    token = BypassToken(
        agent="agent",
        check_name="test",
        granted_at=now - timedelta(seconds=120),
        expires_at=now - timedelta(seconds=60),
        cost=0.1,
        correlation_id="test-id",
    )
    assert not token.is_valid()


def test_mint_bypass_debits_capital(funded_ledger: EventSourcedLedger) -> None:
    """Minting a bypass token debits the agent's capital."""
    initial = funded_ledger.balance("test-agent")
    funded_ledger.mint_bypass("test-agent", "gate", 0.2)

    assert funded_ledger.balance("test-agent") == initial - 0.2


def test_mint_bypass_fails_if_insufficient(ledger: EventSourcedLedger) -> None:
    """Cannot mint bypass if insufficient capital."""
    token = ledger.mint_bypass("poor-agent", "gate", 100.0)
    assert token is None


# === Decay Tests ===


def test_apply_decay_reduces_all_balances(funded_ledger: EventSourcedLedger) -> None:
    """apply_decay reduces balances by decay_rate."""
    funded_ledger.credit("agent-b", 0.3, "setup")

    balance_a = funded_ledger.balance("test-agent")
    balance_b = funded_ledger.balance("agent-b")

    events = funded_ledger.apply_decay()

    # Decay applied to both agents
    assert len(events) == 2
    assert all(e.event_type == "DECAY" for e in events)

    # Balances reduced
    expected_a = balance_a - (balance_a * funded_ledger.decay_rate)
    expected_b = balance_b - (balance_b * funded_ledger.decay_rate)

    assert abs(funded_ledger.balance("test-agent") - expected_a) < 0.001
    assert abs(funded_ledger.balance("agent-b") - expected_b) < 0.001


# === Issue Tests ===


def test_issue_creates_capital(ledger: EventSourcedLedger) -> None:
    """issue creates capital from nothing (system operation)."""
    initial = ledger.balance("new-agent")
    ledger.issue("new-agent", 0.3, "bootstrap")

    assert ledger.balance("new-agent") == initial + 0.3


# === Error Message Tests ===


def test_insufficient_capital_error_is_sympathetic() -> None:
    """Error message includes helpful context."""
    error = InsufficientCapitalError(
        "Test error",
        agent="test-agent",
        required=0.5,
        available=0.2,
    )

    message = str(error)
    assert "test-agent" in message
    assert "0.500" in message or "0.5" in message
    assert "0.200" in message or "0.2" in message
    assert "Try:" in message


# === Property-Based Tests ===


@given(
    st.lists(
        st.tuples(
            st.sampled_from(["CREDIT", "DEBIT"]),
            st.floats(min_value=0.001, max_value=0.5),
        ),
        min_size=0,
        max_size=20,
    )
)
@settings(max_examples=100)
def test_balance_is_projection(events: list[tuple[str, float]]) -> None:
    """
    GENERATIVE PRINCIPLE: Balance equals sum of credits minus sum of debits.

    This property test verifies the spec, not the implementation.
    Any correct implementation will satisfy this invariant.
    """
    ledger = EventSourcedLedger()
    agent = "test-agent"

    # Apply events
    for event_type, amount in events:
        if event_type == "CREDIT":
            ledger.credit(agent, amount, "test")
        else:
            # Only debit if sufficient balance (matching real behavior)
            if ledger.balance(agent) >= amount:
                ledger.debit(agent, amount, "test")

    # Compute expected balance manually
    expected = ledger.initial_capital
    for event in ledger.witness(agent):
        if event.is_credit():
            expected += event.amount
        elif event.is_debit():
            expected -= event.amount

    # Clamp to bounds
    expected = min(max(0, expected), ledger.max_capital)

    assert abs(ledger.balance(agent) - expected) < 0.0001


@given(st.floats(min_value=0.01, max_value=0.3))
@settings(max_examples=50)
def test_potlatch_preserves_invariants(amount: float) -> None:
    """Potlatch maintains ledger invariants."""
    ledger = EventSourcedLedger()
    agent = "test"

    # Give agent capital that won't exceed max when added to initial_capital
    # This ensures no clamping affects our expectations
    issue_amount = amount + 0.1
    ledger.issue(agent, issue_amount, "setup")

    # Balance before potlatch (may be clamped)
    initial = ledger.balance(agent)

    # Potlatch
    event = ledger.potlatch(agent, amount)

    # The actual computation: initial_capital + issued - potlatch, clamped
    expected_raw = ledger.initial_capital + issue_amount - amount
    expected = min(max(0, expected_raw), ledger.max_capital)

    assert event is not None
    assert ledger.balance(agent) == pytest.approx(expected, abs=0.0001)
    assert ledger.balance(agent) >= 0
