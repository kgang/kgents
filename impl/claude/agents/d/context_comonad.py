"""
Store Comonad: D-gent persistence for event-sourced state.

A comonad provides:
- extract: W a → a (get the focus)
- extend: (W a → b) → W a → W b (apply transformation at all positions)
- duplicate: W a → W (W a) (create nested structure)

For event-sourced systems like the Capital Ledger:
- Store E S ≅ (S, [E]) where S is state, E is events
- extract returns the current state
- extend applies a function to each historical position
- duplicate creates a "zipper" over the event history

AGENTESE: The comonad laws ensure compositional access to state.

Category Theory:
- Left identity: extract . duplicate = id
- Right identity: fmap extract . duplicate = id
- Associativity: duplicate . duplicate = fmap duplicate . duplicate
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

S = TypeVar("S")  # State type (e.g., dict[str, float] for balances)
E = TypeVar("E")  # Event type (e.g., LedgerEvent)
B = TypeVar("B")  # Result type for extend


@dataclass
class StoreSnapshot(Generic[E, S]):
    """
    A snapshot of the store at a particular position in the event history.

    This is what gets produced when we duplicate() the store -
    each position in history becomes accessible.
    """

    state: S  # State at this position
    position: int  # Index in event history (0 = initial, n = after n events)
    timestamp: datetime | None  # When this state existed


@dataclass
class StoreComonad(Generic[E, S]):
    """
    Store Comonad for event-sourced state management.

    Wraps an append-only event log and provides:
    - extract(): Get current state
    - extend(f): Apply f to each historical position
    - duplicate(): Create nested store (zipper-like access)

    Persistence is automatic via JSONL append-only file.

    Example:
        # Create store with fold function
        store = StoreComonad(
            fold=apply_ledger_event,
            initial={},
            persistence_path=Path("~/.kgents/ledger.jsonl")
        )

        # Append events
        store.append(event)

        # Extract current state
        balances = store.extract()

        # Time-travel with extend
        def balance_at_position(s: StoreComonad) -> float:
            return s.extract().get("agent-a", 0.0)
        history = store.extend(balance_at_position)

        # Duplicate for nested access
        nested = store.duplicate()
    """

    fold: Callable[[S, E], S]  # Event application function
    initial: S  # Initial state
    persistence_path: Path | None = None
    max_events: int = 10000

    _events: list[E] = field(default_factory=list)
    _timestamps: list[datetime] = field(default_factory=list)
    _current_state: S = field(init=False)
    _position: int = 0  # Current position in history (used for extend/duplicate)

    def __post_init__(self) -> None:
        """Initialize state, optionally loading from persistence."""
        self._current_state = self.initial
        if self.persistence_path:
            self._load_from_disk()

    # === Comonad Operations ===

    def extract(self) -> S:
        """
        W a → a

        Extract the current state (the "focus" of the comonad).
        This is the most recent state after applying all events.
        """
        if self._position == 0:
            return self.initial

        # Replay events up to current position
        state = self.initial
        for event in self._events[: self._position]:
            state = self.fold(state, event)
        return state

    def extend(self, f: Callable[["StoreComonad[E, S]"], B]) -> list[B]:
        """
        (W a → b) → W a → W b

        Apply a function to each historical position.

        This is the key comonad operation: we can access the full
        context at each position in history, not just the values.

        Example: Track balance evolution
            def balance_at_position(store: StoreComonad) -> float:
                return store.extract().get("agent-a", 0.0)
            history = store.extend(balance_at_position)
            # Returns [0.5, 0.6, 0.55, ...] for each position
        """
        results: list[B] = []

        # Save current position
        original_position = self._position

        # Apply f at each position (including position 0 = initial)
        for pos in range(len(self._events) + 1):
            self._position = pos
            results.append(f(self))

        # Restore position
        self._position = original_position

        return results

    def duplicate(self) -> list[StoreSnapshot[E, S]]:
        """
        W a → W (W a)

        Create a nested structure showing the store at each position.

        This is useful for "zooming in" on any point in history.
        Returns snapshots that can be inspected individually.
        """
        snapshots: list[StoreSnapshot[E, S]] = []

        # Position 0: initial state
        snapshots.append(
            StoreSnapshot(
                state=self.initial,
                position=0,
                timestamp=self._timestamps[0] if self._timestamps else None,
            )
        )

        # Each subsequent position
        state = self.initial
        for i, event in enumerate(self._events):
            state = self.fold(state, event)
            snapshots.append(
                StoreSnapshot(
                    state=state,
                    position=i + 1,
                    timestamp=self._timestamps[i]
                    if i < len(self._timestamps)
                    else None,
                )
            )

        return snapshots

    # === Event Operations ===

    def append(self, event: E, timestamp: datetime | None = None) -> S:
        """
        Append an event to the store.

        Returns the new state after applying the event.
        """
        ts = timestamp or datetime.now(UTC)
        self._events.append(event)
        self._timestamps.append(ts)
        self._current_state = self.fold(self._current_state, event)
        self._position = len(self._events)

        # Enforce max_events
        if len(self._events) > self.max_events:
            trim = len(self._events) - self.max_events
            self._events = self._events[trim:]
            self._timestamps = self._timestamps[trim:]
            # Note: We don't adjust position because we're trimming old events

        # Persist
        if self.persistence_path:
            self._append_to_disk(event, ts)

        return self._current_state

    def witness(self, limit: int = 100) -> list[tuple[E, datetime]]:
        """
        Return recent events with timestamps (N-gent witness pattern).

        AGENTESE: void.capital.witness
        """
        events = list(zip(self._events, self._timestamps))
        return events[-limit:]

    def replay_to(self, position: int) -> S:
        """
        Reconstruct state at a specific position in history.

        Position 0 = initial state
        Position n = state after n events
        """
        if position <= 0:
            return self.initial

        state = self.initial
        for event in self._events[: min(position, len(self._events))]:
            state = self.fold(state, event)
        return state

    def replay_to_time(self, target: datetime) -> S:
        """
        Reconstruct state at a specific timestamp.
        """
        state = self.initial
        for event, ts in zip(self._events, self._timestamps):
            if ts > target:
                break
            state = self.fold(state, event)
        return state

    # === Properties ===

    @property
    def events(self) -> list[E]:
        """Read-only access to events."""
        return list(self._events)

    @property
    def position(self) -> int:
        """Current position in history."""
        return self._position

    @property
    def length(self) -> int:
        """Number of events in history."""
        return len(self._events)

    # === Persistence ===

    def _load_from_disk(self) -> None:
        """Load events from JSONL persistence file."""
        if not self.persistence_path or not self.persistence_path.exists():
            return

        try:
            with open(self.persistence_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    event = self._deserialize_event(data["event"])
                    ts = datetime.fromisoformat(data["timestamp"])
                    self._events.append(event)
                    self._timestamps.append(ts)
                    self._current_state = self.fold(self._current_state, event)

            self._position = len(self._events)
        except (json.JSONDecodeError, KeyError, OSError):
            # If load fails, start fresh
            pass

    def _append_to_disk(self, event: E, timestamp: datetime) -> None:
        """Append event to JSONL file (atomic append)."""
        if not self.persistence_path:
            return

        try:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_path, "a") as f:
                data = {
                    "event": self._serialize_event(event),
                    "timestamp": timestamp.isoformat(),
                }
                f.write(json.dumps(data) + "\n")
        except OSError:
            pass  # Silent failure for persistence

    def _serialize_event(self, event: E) -> dict[str, Any]:
        """Serialize event to JSON-compatible dict."""
        if isinstance(event, dict):
            return {"_type": "dict", "data": event}
        if hasattr(event, "__dict__"):
            result: dict[str, Any] = {"_type": "object"}
            for k, v in event.__dict__.items():
                if isinstance(v, datetime):
                    result[k] = v.isoformat()
                else:
                    result[k] = v
            return result
        # Primitive types
        return {"_type": "primitive", "value": event}

    def _deserialize_event(self, data: dict[str, Any]) -> E:
        """
        Deserialize event from JSON dict.

        Handles primitives, dicts, and objects.
        """
        event_type = data.get("_type", "dict")
        result: Any

        if event_type == "primitive":
            result = data["value"]
        elif event_type == "dict":
            result = data.get("data", data)
        else:
            # Object - return as dict (subclasses can reconstruct)
            result = dict(data)
            result.pop("_type", None)

        return result  # type: ignore[no-any-return]


# === Capital Ledger Store ===


def _ledger_fold(balances: dict[str, float], event: dict[str, Any]) -> dict[str, float]:
    """
    Fold function for capital ledger events.

    This applies LedgerEvent-style events to balance state.
    """
    agent = event.get("agent", "")
    amount = event.get("amount", 0.0)
    event_type = event.get("event_type", "")

    new_balances = dict(balances)

    if agent not in new_balances:
        new_balances[agent] = 0.5  # Initial capital

    if event_type in ("ISSUE", "CREDIT"):
        new_balances[agent] = min(1.0, new_balances[agent] + amount)
    elif event_type in ("DEBIT", "BYPASS", "DECAY", "POTLATCH"):
        new_balances[agent] = max(0.0, new_balances[agent] - amount)

    return new_balances


def create_ledger_store(
    persistence_path: Path | None = None,
) -> StoreComonad[dict[str, Any], dict[str, float]]:
    """
    Create a Store Comonad for the capital ledger.

    This provides event-sourced persistence with comonadic operations.

    Example:
        store = create_ledger_store(Path("~/.kgents/ledger.jsonl").expanduser())

        # Append events
        store.append({
            "event_type": "CREDIT",
            "agent": "b-gent",
            "amount": 0.1,
        })

        # Get current balances
        balances = store.extract()

        # Track agent balance over time
        def agent_balance(s: StoreComonad) -> float:
            return s.extract().get("b-gent", 0.0)
        history = store.extend(agent_balance)
    """
    return StoreComonad(
        fold=_ledger_fold,
        initial={},
        persistence_path=persistence_path,
    )


# === Integration with EventSourcedLedger ===


class LedgerStoreAdapter:
    """
    Adapter that wraps EventSourcedLedger with Store Comonad persistence.

    This allows using the existing EventSourcedLedger API while
    gaining comonadic operations and JSONL persistence.
    """

    def __init__(
        self,
        persistence_path: Path | None = None,
        initial_capital: float = 0.5,
        max_capital: float = 1.0,
    ) -> None:
        self.initial_capital = initial_capital
        self.max_capital = max_capital

        # Create the underlying store
        self._store = StoreComonad[dict[str, Any], dict[str, float]](
            fold=self._make_fold(),
            initial={},
            persistence_path=persistence_path,
        )

    def _make_fold(
        self,
    ) -> Callable[[dict[str, float], dict[str, Any]], dict[str, float]]:
        """Create fold function with our config."""
        initial = self.initial_capital
        max_cap = self.max_capital

        def fold(balances: dict[str, float], event: dict[str, Any]) -> dict[str, float]:
            agent = event.get("agent", "")
            amount = event.get("amount", 0.0)
            event_type = event.get("event_type", "")

            new_balances = dict(balances)

            if agent not in new_balances:
                new_balances[agent] = initial

            if event_type in ("ISSUE", "CREDIT"):
                new_balances[agent] = min(max_cap, new_balances[agent] + amount)
            elif event_type in ("DEBIT", "BYPASS", "DECAY", "POTLATCH"):
                new_balances[agent] = max(0.0, new_balances[agent] - amount)

            return new_balances

        return fold

    def balance(self, agent: str) -> float:
        """Get agent's current balance."""
        balances = self._store.extract()
        return balances.get(agent, self.initial_capital)

    def credit(self, agent: str, amount: float, reason: str) -> None:
        """Credit agent with amount."""
        self._store.append(
            {
                "event_type": "CREDIT",
                "agent": agent,
                "amount": amount,
                "metadata": {"reason": reason},
            }
        )

    def debit(self, agent: str, amount: float, reason: str) -> bool:
        """Debit agent if sufficient balance. Returns success."""
        if self.balance(agent) < amount:
            return False
        self._store.append(
            {
                "event_type": "DEBIT",
                "agent": agent,
                "amount": amount,
                "metadata": {"reason": reason},
            }
        )
        return True

    def potlatch(self, agent: str, amount: float) -> bool:
        """Ritual discharge. Returns success."""
        if self.balance(agent) < amount:
            return False
        self._store.append(
            {
                "event_type": "POTLATCH",
                "agent": agent,
                "amount": amount,
                "metadata": {"ritual": "accursed_share"},
            }
        )
        return True

    def witness(self, limit: int = 100) -> list[tuple[dict[str, Any], datetime]]:
        """Return recent events with timestamps."""
        return self._store.witness(limit)

    def agents(self) -> set[str]:
        """All agents with balances."""
        return set(self._store.extract().keys())

    # === Comonad Operations ===

    def balance_history(self, agent: str) -> list[float]:
        """
        Get agent's balance at each point in history.

        Uses extend() to apply balance extraction at each position.
        """

        def get_balance(store: StoreComonad[dict[str, Any], dict[str, float]]) -> float:
            return store.extract().get(agent, self.initial_capital)

        return self._store.extend(get_balance)

    def snapshots(self) -> list[StoreSnapshot[dict[str, Any], dict[str, float]]]:
        """
        Get all historical snapshots via duplicate().

        Returns snapshots that can be inspected individually.
        """
        return self._store.duplicate()

    def replay_to(self, position: int) -> dict[str, float]:
        """Reconstruct balances at a specific position."""
        return self._store.replay_to(position)
