# D-gent Protocols

The interface specifications for Data Agents.

---

## The DataAgent Protocol

The minimal interface that all D-gents must implement:

```python
from typing import TypeVar, Protocol, Generic, List
from abc import abstractmethod

S = TypeVar("S")  # State type

class DataAgent(Protocol[S]):
    """
    The core protocol for state management.

    A D-gent abstracts storage mechanisms, providing a uniform
    interface for stateful computation regardless of backend.
    """

    @abstractmethod
    async def load(self) -> S:
        """
        Retrieve current state.

        Returns:
            The current state value of type S

        Raises:
            StateNotFoundError: If state doesn't exist (first access)
            StateCorruptionError: If stored state fails validation
        """
        ...

    @abstractmethod
    async def save(self, state: S) -> None:
        """
        Persist new state.

        Args:
            state: The new state to save

        Raises:
            StateSerializationError: If state cannot be encoded
            StorageError: If backend write fails
        """
        ...

    @abstractmethod
    async def history(self, limit: int | None = None) -> List[S]:
        """
        Query state evolution over time.

        Args:
            limit: Maximum number of historical states to return
                   (None = all history)

        Returns:
            List of states, newest first

        Note:
            Not all D-gents support history. Implementations may
            return empty list if history is not tracked.
        """
        ...
```

---

## Extended Protocol: Transactional

For D-gents that support atomic operations:

```python
class TransactionalDataAgent(DataAgent[S], Protocol):
    """
    Extends DataAgent with transaction support.

    Useful for multi-step state updates that must be atomic.
    """

    @abstractmethod
    async def begin_transaction(self) -> TransactionContext:
        """Start a new transaction."""
        ...

    @abstractmethod
    async def commit(self, tx: TransactionContext) -> None:
        """Commit transaction changes."""
        ...

    @abstractmethod
    async def rollback(self, tx: TransactionContext) -> None:
        """Abort transaction, revert changes."""
        ...
```

**Example**:
```python
async with dgent.begin_transaction() as tx:
    state = await dgent.load()
    state.value += 1
    await dgent.save(state)
    # Automatically commits on exit, rolls back on exception
```

---

## Extended Protocol: Queryable

For D-gents that support structured queries (e.g., databases):

```python
from typing import Callable, Any

class QueryableDataAgent(DataAgent[S], Protocol):
    """
    Extends DataAgent with query capabilities.

    Useful for D-gents backed by databases or index structures.
    """

    @abstractmethod
    async def query(self, predicate: Callable[[S], bool]) -> List[S]:
        """
        Filter state history by predicate.

        Args:
            predicate: Function that returns True for desired states

        Returns:
            All historical states matching predicate
        """
        ...

    @abstractmethod
    async def aggregate(self, operation: str, field: str) -> Any:
        """
        Compute aggregate over state history.

        Args:
            operation: "sum", "avg", "min", "max", "count"
            field: Dotted path to field (e.g., "user.age")

        Returns:
            Aggregated value
        """
        ...
```

---

## Extended Protocol: Observable

For D-gents that support reactive updates:

```python
from typing import Callable, Awaitable

StateObserver = Callable[[S, S], Awaitable[None]]  # (old_state, new_state)

class ObservableDataAgent(DataAgent[S], Protocol):
    """
    Extends DataAgent with observer pattern.

    Allows other agents to react to state changes.
    """

    @abstractmethod
    def subscribe(self, observer: StateObserver) -> str:
        """
        Register observer for state changes.

        Args:
            observer: Async function called when state changes

        Returns:
            Subscription ID for later unsubscribe
        """
        ...

    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None:
        """Remove observer."""
        ...
```

**Example**:
```python
# Log all state changes
async def logger(old: S, new: S):
    print(f"State changed: {old} → {new}")

dgent.subscribe(logger)
await dgent.save(new_state)  # Triggers logger
```

---

## Reference Implementations

### VolatileAgent: In-Memory State

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, List
import copy

S = TypeVar("S")

@dataclass
class VolatileAgent(Generic[S]):
    """
    In-memory state storage.

    - Fastest performance (no I/O)
    - State lost on process termination
    - Useful for conversational context, temporary caches
    """

    _state: S
    _history: List[S] = field(default_factory=list)
    _max_history: int = 100

    async def load(self) -> S:
        return copy.deepcopy(self._state)

    async def save(self, state: S) -> None:
        # Archive current state to history
        self._history.append(copy.deepcopy(self._state))
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Update to new state
        self._state = copy.deepcopy(state)

    async def history(self, limit: int | None = None) -> List[S]:
        hist = self._history[::-1]  # Newest first
        if limit is not None:
            hist = hist[:limit]
        return [copy.deepcopy(s) for s in hist]

    def snapshot(self) -> S:
        """Non-async snapshot for testing."""
        return copy.deepcopy(self._state)
```

**Usage**:
```python
dgent = VolatileAgent[dict](initial={"count": 0})

state = await dgent.load()
state["count"] += 1
await dgent.save(state)

# Query history
past_states = await dgent.history(limit=10)
```

---

### PersistentAgent: File-Backed State

```python
import json
from pathlib import Path
from typing import Generic, TypeVar, Type, List
from dataclasses import dataclass, asdict, is_dataclass

S = TypeVar("S")

@dataclass
class PersistentAgent(Generic[S]):
    """
    File-backed state storage with JSON serialization.

    - Survives process restarts
    - Simple file I/O (suitable for small-medium state)
    - Supports dataclasses and JSON-serializable types
    """

    path: Path
    schema: Type[S]
    _history_path: Path | None = None

    def __post_init__(self):
        self.path = Path(self.path)
        if self._history_path is None:
            self._history_path = self.path.parent / f"{self.path.stem}_history.jsonl"

    async def load(self) -> S:
        if not self.path.exists():
            raise StateNotFoundError(f"State file not found: {self.path}")

        with open(self.path, 'r') as f:
            data = json.load(f)

        # Deserialize based on schema
        if is_dataclass(self.schema):
            return self.schema(**data)
        else:
            return data  # Assume JSON-native type

    async def save(self, state: S) -> None:
        # Archive current state to history (if it exists)
        if self.path.exists():
            with open(self.path, 'r') as f:
                old_state = f.read()
            with open(self._history_path, 'a') as f:
                f.write(old_state.strip() + '\n')

        # Serialize state
        if is_dataclass(state):
            data = asdict(state)
        else:
            data = state

        # Write atomically (temp file + rename)
        temp_path = self.path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        temp_path.rename(self.path)

    async def history(self, limit: int | None = None) -> List[S]:
        if not self._history_path.exists():
            return []

        with open(self._history_path, 'r') as f:
            lines = f.readlines()

        # Parse JSONL history (newest first)
        states = []
        for line in reversed(lines):
            if limit is not None and len(states) >= limit:
                break
            data = json.loads(line)
            if is_dataclass(self.schema):
                states.append(self.schema(**data))
            else:
                states.append(data)

        return states
```

**Usage**:
```python
from dataclasses import dataclass

@dataclass
class UserProfile:
    name: str
    preferences: dict

dgent = PersistentAgent[UserProfile](
    path=Path("user_profile.json"),
    schema=UserProfile
)

# First save
profile = UserProfile(name="Alice", preferences={"theme": "dark"})
await dgent.save(profile)

# Later (even after restart)
loaded = await dgent.load()
assert loaded.name == "Alice"
```

---

## Error Handling

All D-gents should raise these standard exceptions:

```python
class StateError(Exception):
    """Base exception for D-gent errors."""
    pass

class StateNotFoundError(StateError):
    """State does not exist (e.g., first access to persistent store)."""
    pass

class StateCorruptionError(StateError):
    """Stored state is invalid or corrupted."""
    pass

class StateSerializationError(StateError):
    """State cannot be encoded for storage."""
    pass

class StorageError(StateError):
    """Backend storage operation failed."""
    pass
```

**Handling Strategy**:
```python
try:
    state = await dgent.load()
except StateNotFoundError:
    # Initialize with default
    state = default_state()
    await dgent.save(state)
except StateCorruptionError:
    # Log and fallback to safe state
    logger.error("State corrupted, resetting")
    state = safe_fallback_state()
    await dgent.save(state)
```

---

## Testing D-gent Implementations

All D-gent implementations should pass these tests:

### Test 1: Isomorphism (Round-Trip)

```python
async def test_round_trip(dgent: DataAgent[S], sample_state: S):
    """State survives save/load cycle without corruption."""
    await dgent.save(sample_state)
    loaded = await dgent.load()
    assert loaded == sample_state
```

### Test 2: Isolation

```python
async def test_isolation(dgent: DataAgent[dict]):
    """Loaded state is independent copy, not reference."""
    await dgent.save({"value": 1})

    state1 = await dgent.load()
    state1["value"] = 2

    state2 = await dgent.load()
    assert state2["value"] == 1  # Not affected by mutation
```

### Test 3: History Ordering

```python
async def test_history_ordering(dgent: DataAgent[int]):
    """History returns states newest-first."""
    await dgent.save(1)
    await dgent.save(2)
    await dgent.save(3)

    history = await dgent.history(limit=3)
    assert history == [2, 1]  # Current state (3) not in history
```

### Test 4: Concurrent Access (if applicable)

```python
async def test_concurrent_safety(dgent: DataAgent[int]):
    """Concurrent saves don't corrupt state."""
    async def increment():
        state = await dgent.load()
        await dgent.save(state + 1)

    await dgent.save(0)
    await asyncio.gather(*[increment() for _ in range(10)])

    final = await dgent.load()
    # May be < 10 due to race conditions (unless transactional)
    assert 0 < final <= 10
```

---

## Composition Patterns

### Pattern 1: Layering D-gents

```python
# Cache layer over persistent storage
cached = CachedAgent(
    cache=VolatileAgent[S](initial=default),
    backend=PersistentAgent[S](path="state.json", schema=S)
)

# Reads from cache, writes to both
await cached.save(state)  # Updates cache + writes through to file
loaded = await cached.load()  # Fast (from cache)
```

### Pattern 2: Migration Wrapper

```python
# Handle schema evolution
versioned = VersionedAgent(
    backend=dgent,
    migrations={
        1: migrate_v0_to_v1,
        2: migrate_v1_to_v2,
    },
    current_version=2
)

# Automatically migrates old state on load
state = await versioned.load()  # Migrates if needed
```

---

## See Also

- [README.md](README.md) - D-gents overview
- [symbiont.md](symbiont.md) - Using D-gents with logic agents
- [lenses.md](lenses.md) - Compositional state access
- [../t-gents/](../t-gents/) - Testing stateful systems
