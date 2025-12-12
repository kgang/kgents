"""
Tests for Store Comonad (context_comonad.py).

Tests the comonad laws and ledger persistence functionality.
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from agents.d.context_comonad import (
    LedgerStoreAdapter,
    StoreComonad,
    StoreSnapshot,
    create_ledger_store,
)

# === Test Fixtures ===


@pytest.fixture
def simple_fold() -> Any:
    """A simple fold function for testing (sum of values)."""

    def fold(state: int, event: int) -> int:
        return state + event

    return fold


@pytest.fixture
def simple_store(simple_fold: Any) -> StoreComonad[int, int]:
    """Create a simple store for testing."""
    return StoreComonad(fold=simple_fold, initial=0)


@pytest.fixture
def ledger_store() -> StoreComonad[dict[str, Any], dict[str, float]]:
    """Create a ledger store for testing."""
    return create_ledger_store()


# === Comonad Law Tests ===


class TestComonadLaws:
    """
    Tests that verify the comonad laws hold.

    Comonad Laws:
    1. Left identity: extract . duplicate ≡ id
    2. Right identity: fmap extract . duplicate ≡ id
    3. Associativity: duplicate . duplicate ≡ fmap duplicate . duplicate
    """

    def test_extract_returns_current_state(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """Extract returns the current state."""
        assert simple_store.extract() == 0  # Initial state

        simple_store.append(5)
        assert simple_store.extract() == 5

        simple_store.append(3)
        assert simple_store.extract() == 8

    def test_extract_at_position(self, simple_store: StoreComonad[int, int]) -> None:
        """Extract returns state at current position during extend."""
        simple_store.append(1)
        simple_store.append(2)
        simple_store.append(3)

        # Extract at each position
        states = simple_store.extend(lambda s: s.extract())

        # Should be: [0, 1, 3, 6] (initial, after 1, after 1+2, after 1+2+3)
        assert states == [0, 1, 3, 6]

    def test_duplicate_creates_snapshots(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """Duplicate creates snapshots at each position."""
        simple_store.append(1)
        simple_store.append(2)

        snapshots = simple_store.duplicate()

        assert len(snapshots) == 3  # initial + 2 events
        assert snapshots[0].state == 0
        assert snapshots[0].position == 0
        assert snapshots[1].state == 1
        assert snapshots[1].position == 1
        assert snapshots[2].state == 3
        assert snapshots[2].position == 2

    def test_left_identity_extract_duplicate(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """
        Left identity: extract . duplicate ≡ id

        Extracting from the last snapshot of duplicate should give current state.
        """
        simple_store.append(5)
        simple_store.append(3)

        current_state = simple_store.extract()
        snapshots = simple_store.duplicate()
        last_snapshot_state = snapshots[-1].state

        assert last_snapshot_state == current_state

    def test_extend_applies_function_everywhere(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """Extend applies the function at each historical position."""
        simple_store.append(10)
        simple_store.append(20)
        simple_store.append(30)

        # Double the state at each position
        doubled = simple_store.extend(lambda s: s.extract() * 2)

        # States are: 0, 10, 30, 60
        # Doubled: 0, 20, 60, 120
        assert doubled == [0, 20, 60, 120]


# === Event Operations Tests ===


class TestEventOperations:
    """Tests for appending events and replaying history."""

    def test_append_adds_event(self, simple_store: StoreComonad[int, int]) -> None:
        """Append adds event to history."""
        assert simple_store.length == 0

        simple_store.append(5)
        assert simple_store.length == 1
        assert simple_store.extract() == 5

    def test_append_records_timestamp(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """Append records timestamp with event."""
        now = datetime.now(UTC)
        simple_store.append(5)

        events = simple_store.witness()
        assert len(events) == 1
        event, ts = events[0]
        assert event == 5
        assert (ts - now).total_seconds() < 1  # Within 1 second

    def test_replay_to_position(self, simple_store: StoreComonad[int, int]) -> None:
        """Replay reconstructs state at position."""
        simple_store.append(1)
        simple_store.append(2)
        simple_store.append(3)

        assert simple_store.replay_to(0) == 0  # Initial
        assert simple_store.replay_to(1) == 1  # After first event
        assert simple_store.replay_to(2) == 3  # After second
        assert simple_store.replay_to(3) == 6  # After third

    def test_replay_to_time(self, simple_store: StoreComonad[int, int]) -> None:
        """Replay to timestamp reconstructs state."""
        t1 = datetime.now(UTC)
        simple_store.append(10, timestamp=t1)

        t2 = t1 + timedelta(seconds=10)
        simple_store.append(20, timestamp=t2)

        t3 = t1 + timedelta(seconds=20)
        simple_store.append(30, timestamp=t3)

        # Replay to just after t1
        state = simple_store.replay_to_time(t1 + timedelta(seconds=5))
        assert state == 10

        # Replay to just after t2
        state = simple_store.replay_to_time(t2 + timedelta(seconds=5))
        assert state == 30

    def test_witness_returns_recent_events(
        self, simple_store: StoreComonad[int, int]
    ) -> None:
        """Witness returns recent events with timestamps."""
        for i in range(10):
            simple_store.append(i)

        events = simple_store.witness(limit=5)
        assert len(events) == 5

        # Should be last 5 events: 5, 6, 7, 8, 9
        values = [e[0] for e in events]
        assert values == [5, 6, 7, 8, 9]

    def test_max_events_enforced(self) -> None:
        """Events beyond max_events are trimmed."""

        def fold(state: int, event: int) -> int:
            return state + event

        store: StoreComonad[int, int] = StoreComonad(fold=fold, initial=0, max_events=5)

        for i in range(10):
            store.append(1)

        assert store.length == 5


# === Persistence Tests ===


class TestPersistence:
    """Tests for JSONL persistence."""

    def test_persist_to_disk(self, simple_fold: Any) -> None:
        """Events are persisted to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            store: StoreComonad[int, int] = StoreComonad(
                fold=simple_fold, initial=0, persistence_path=path
            )

            store.append(5)
            store.append(3)

            # Verify file was created
            assert path.exists()

            # Verify contents
            with open(path) as f:
                lines = f.readlines()
            assert len(lines) == 2

    def test_load_from_disk(self, simple_fold: Any) -> None:
        """Events are loaded from disk on creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"

            # Create and populate store
            store1: StoreComonad[int, int] = StoreComonad(
                fold=simple_fold, initial=0, persistence_path=path
            )
            store1.append(5)
            store1.append(3)

            # Create new store with same path
            store2: StoreComonad[int, int] = StoreComonad(
                fold=simple_fold, initial=0, persistence_path=path
            )

            # Should have loaded events
            assert store2.length == 2
            assert store2.extract() == 8


# === Ledger Store Tests ===


class TestLedgerStore:
    """Tests for the capital ledger store."""

    def test_credit_increases_balance(
        self, ledger_store: StoreComonad[dict[str, Any], dict[str, float]]
    ) -> None:
        """Credit event increases agent balance."""
        ledger_store.append(
            {
                "event_type": "CREDIT",
                "agent": "test-agent",
                "amount": 0.1,
            }
        )

        balances = ledger_store.extract()
        # Initial is 0.5, plus 0.1 = 0.6
        assert balances["test-agent"] == 0.6

    def test_debit_decreases_balance(
        self, ledger_store: StoreComonad[dict[str, Any], dict[str, float]]
    ) -> None:
        """Debit event decreases agent balance."""
        # First credit to create agent
        ledger_store.append(
            {
                "event_type": "CREDIT",
                "agent": "test-agent",
                "amount": 0.0,  # Just to initialize at 0.5
            }
        )
        ledger_store.append(
            {
                "event_type": "DEBIT",
                "agent": "test-agent",
                "amount": 0.1,
            }
        )

        balances = ledger_store.extract()
        assert balances["test-agent"] == 0.4

    def test_balance_capped_at_max(
        self, ledger_store: StoreComonad[dict[str, Any], dict[str, float]]
    ) -> None:
        """Balance cannot exceed 1.0."""
        ledger_store.append(
            {
                "event_type": "CREDIT",
                "agent": "test-agent",
                "amount": 10.0,  # Way more than max
            }
        )

        balances = ledger_store.extract()
        assert balances["test-agent"] == 1.0

    def test_balance_capped_at_zero(
        self, ledger_store: StoreComonad[dict[str, Any], dict[str, float]]
    ) -> None:
        """Balance cannot go below 0.0."""
        ledger_store.append(
            {
                "event_type": "DEBIT",
                "agent": "test-agent",
                "amount": 10.0,  # Way more than balance
            }
        )

        balances = ledger_store.extract()
        assert balances["test-agent"] == 0.0


# === LedgerStoreAdapter Tests ===


class TestLedgerStoreAdapter:
    """Tests for the adapter that wraps Store with EventSourcedLedger API."""

    def test_credit_and_balance(self) -> None:
        """Credit updates balance correctly."""
        adapter = LedgerStoreAdapter()
        adapter.credit("agent-a", 0.1, "test")

        assert adapter.balance("agent-a") == 0.6  # 0.5 + 0.1

    def test_debit_success(self) -> None:
        """Debit succeeds with sufficient balance."""
        adapter = LedgerStoreAdapter()
        result = adapter.debit("agent-a", 0.1, "test")

        assert result is True
        assert adapter.balance("agent-a") == 0.4

    def test_debit_failure(self) -> None:
        """Debit fails with insufficient balance."""
        adapter = LedgerStoreAdapter()
        result = adapter.debit("agent-a", 10.0, "test")

        assert result is False
        assert adapter.balance("agent-a") == 0.5  # Unchanged

    def test_potlatch_success(self) -> None:
        """Potlatch succeeds with sufficient balance."""
        adapter = LedgerStoreAdapter()
        result = adapter.potlatch("agent-a", 0.1)

        assert result is True
        assert adapter.balance("agent-a") == 0.4

    def test_agents_returns_all(self) -> None:
        """Agents returns all agents with balances."""
        adapter = LedgerStoreAdapter()
        adapter.credit("agent-a", 0.1, "test")
        adapter.credit("agent-b", 0.1, "test")

        agents = adapter.agents()
        assert agents == {"agent-a", "agent-b"}

    def test_balance_history(self) -> None:
        """Balance history returns balance at each position."""
        adapter = LedgerStoreAdapter()
        adapter.credit("agent-a", 0.1, "test")
        adapter.credit("agent-a", 0.1, "test")
        adapter.debit("agent-a", 0.05, "test")

        history = adapter.balance_history("agent-a")

        # initial=0.5, +0.1=0.6, +0.1=0.7, -0.05=0.65
        assert history == pytest.approx([0.5, 0.6, 0.7, 0.65])

    def test_snapshots_returns_all(self) -> None:
        """Snapshots returns all historical states."""
        adapter = LedgerStoreAdapter()
        adapter.credit("agent-a", 0.1, "test")
        adapter.credit("agent-b", 0.2, "test")

        snapshots = adapter.snapshots()

        assert len(snapshots) == 3  # initial + 2 events
        assert snapshots[0].state == {}  # Initial (no agents yet)
        assert snapshots[1].state["agent-a"] == 0.6
        assert snapshots[2].state["agent-b"] == 0.7

    def test_persistence(self) -> None:
        """Adapter persists to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ledger.jsonl"

            # Create adapter and add events
            adapter1 = LedgerStoreAdapter(persistence_path=path)
            adapter1.credit("agent-a", 0.1, "test")
            adapter1.credit("agent-b", 0.2, "test")

            # Create new adapter with same path
            adapter2 = LedgerStoreAdapter(persistence_path=path)

            assert adapter2.balance("agent-a") == 0.6
            assert adapter2.balance("agent-b") == 0.7

    def test_replay_to_position(self) -> None:
        """Replay to position reconstructs state."""
        adapter = LedgerStoreAdapter()
        adapter.credit("agent-a", 0.1, "test")
        adapter.credit("agent-a", 0.1, "test")
        adapter.debit("agent-a", 0.05, "test")

        # Position 0 = initial (empty dict, agent not yet seen)
        state0 = adapter.replay_to(0)
        assert "agent-a" not in state0

        # Position 1 = after first credit
        state1 = adapter.replay_to(1)
        assert state1["agent-a"] == 0.6

        # Position 2 = after second credit
        state2 = adapter.replay_to(2)
        assert state2["agent-a"] == 0.7
