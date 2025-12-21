# Categorical Foundation

> *The mathematical substrate: polynomial functors, operads, sheaves.*

---

## agents.d.__init__

## __init__

```python
module __init__
```

D-gents: Data Agents for stateful computation.

---

## agents.d.adapters.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `self.data.table.`

D-gent Adapters: Bridge various storage systems to DgentProtocol.

---

## agents.d.adapters.table_adapter

## table_adapter

```python
module table_adapter
```

**AGENTESE:** `self.data.table.`

TableAdapter: Bridge functor APP_STATE -> AGENT_MEMORY.

---

## TableAdapter

```python
class TableAdapter(BaseDgent, Generic[T])
```

Lifts an Alembic-managed table into DgentProtocol.

### Examples
```python
>>> adapter = TableAdapter(
```
```python
>>> model=Crystal,
```
```python
>>> session_factory=get_session_factory(),
```
```python
>>> )
```
```python
>>> datum = await adapter.get(crystal_id)
```

---

## TableStateBackend

```python
class TableStateBackend(Generic[T])
```

StateBackend implementation backed by TableAdapter.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum by upserting into the Alembic table.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve from table, return as Datum.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete from table.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List from table with filters.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal chain via recursive query.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check if record exists (optimized).

---

## count

```python
async def count(self) -> int
```

Count total records (optimized).

---

## table_name

```python
def table_name(self) -> str
```

Get the underlying table name.

---

## as_state_backend

```python
def as_state_backend(self, key: str) -> 'TableStateBackend[T]'
```

Create a StateBackend that uses this table for state storage.

---

## load

```python
async def load(self) -> T
```

Load state from table.

---

## save

```python
async def save(self, state: T) -> None
```

Save state to table.

---

## agents.d.backends.__init__

## __init__

```python
module __init__
```

D-gent Backends: Storage implementations for the projection lattice.

---

## agents.d.backends.jsonl

## jsonl

```python
module jsonl
```

JSONLBackend: Append-only JSON Lines storage for D-gent.

---

## JSONLBackend

```python
class JSONLBackend(BaseDgent)
```

Append-only JSON Lines file backend.

---

## __init__

```python
def __init__(self, namespace: str='default', data_dir: Path | None=None) -> None
```

Initialize JSONL backend.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum by appending to JSONL file.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum from index.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete datum by appending tombstone.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with filters, sorted by created_at descending.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence directly.

---

## count

```python
async def count(self) -> int
```

Count data directly.

---

## compact

```python
async def compact(self) -> int
```

Compact the JSONL file by removing tombstones and duplicates.

---

## clear

```python
def clear(self) -> None
```

Clear all data (for testing).

---

## agents.d.backends.memory

## memory

```python
module memory
```

MemoryBackend: In-memory storage for D-gent.

---

## MemoryBackend

```python
class MemoryBackend(BaseDgent)
```

In-memory storage backend.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum in memory.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum from memory.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Remove datum from memory.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with filters, sorted by created_at descending.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence directly (faster than get).

---

## count

```python
async def count(self) -> int
```

Count data directly (faster than list).

---

## clear

```python
def clear(self) -> None
```

Clear all data (for testing).

---

## agents.d.backends.postgres

## postgres

```python
module postgres
```

PostgresBackend: PostgreSQL database storage for D-gent.

---

## PostgresBackend

```python
class PostgresBackend(BaseDgent)
```

PostgreSQL database backend using asyncpg.

---

## __init__

```python
def __init__(self, url: str, namespace: str='default', min_pool_size: int=2, max_pool_size: int=10) -> None
```

Initialize PostgreSQL backend.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum in PostgreSQL database.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum from PostgreSQL database.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete datum from PostgreSQL database.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with filters, sorted by created_at descending.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum using recursive CTE.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence efficiently.

---

## count

```python
async def count(self) -> int
```

Count data efficiently.

---

## vacuum

```python
async def vacuum(self) -> None
```

Vacuum the database to reclaim space.

---

## close

```python
async def close(self) -> None
```

Close the connection pool.

---

## health_check

```python
async def health_check(self) -> dict[str, Any]
```

Check database health and return stats.

---

## __aenter__

```python
async def __aenter__(self) -> 'PostgresBackend'
```

Async context manager entry.

---

## __aexit__

```python
async def __aexit__(self, *args: Any) -> None
```

Async context manager exit.

---

## agents.d.backends.sqlite

## sqlite

```python
module sqlite
```

SQLiteBackend: SQLite database storage for D-gent.

---

## SQLiteBackend

```python
class SQLiteBackend(BaseDgent)
```

SQLite database backend.

---

## __init__

```python
def __init__(self, namespace: str='default', data_dir: Path | None=None) -> None
```

Initialize SQLite backend.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum in SQLite database.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum from SQLite database.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete datum from SQLite database.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with filters, sorted by created_at descending.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum using recursive CTE.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence efficiently.

---

## count

```python
async def count(self) -> int
```

Count data efficiently.

---

## vacuum

```python
async def vacuum(self) -> int
```

Vacuum the database to reclaim space.

---

## close

```python
def close(self) -> None
```

Close the database connection.

---

## clear

```python
def clear(self) -> None
```

Clear all data and reset (for testing).

---

## __del__

```python
def __del__(self) -> None
```

Cleanup on garbage collection.

---

## agents.d.bus

## bus

```python
module bus
```

DataBus: Reactive data flow for D-gent.

---

## DataEventType

```python
class DataEventType(Enum)
```

Types of data events.

---

## DataEvent

```python
class DataEvent
```

An event representing a data change.

---

## Subscriber

```python
class Subscriber
```

A subscriber to data events.

---

## DataBus

```python
class DataBus
```

Central bus for data events.

---

## BusEnabledDgent

```python
class BusEnabledDgent(BaseDgent)
```

D-gent wrapper that emits events to the Data Bus.

---

## get_data_bus

```python
def get_data_bus() -> DataBus
```

Get the global data bus instance.

---

## reset_data_bus

```python
def reset_data_bus() -> None
```

Reset the global data bus (for testing).

---

## create

```python
def create(cls, event_type: DataEventType, datum_id: str, source: str='dgent', causal_parent: str | None=None, metadata: dict[str, str] | None=None) -> DataEvent
```

Factory for creating events with sensible defaults.

---

## emit

```python
async def emit(self, event: DataEvent) -> None
```

Emit an event to all subscribers.

---

## subscribe

```python
def subscribe(self, event_type: DataEventType, handler: EventHandler) -> Callable[[], None]
```

Subscribe to events of a specific type.

---

## subscribe_all

```python
def subscribe_all(self, handler: EventHandler) -> Callable[[], None]
```

Subscribe to ALL event types.

---

## replay

```python
async def replay(self, handler: EventHandler, since: float | None=None, event_type: DataEventType | None=None) -> int
```

Replay buffered events to a handler.

---

## latest

```python
def latest(self) -> DataEvent | None
```

Get the most recent event.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all subscribers and buffer (for testing).

---

## __init__

```python
def __init__(self, backend: DgentProtocol, bus: DataBus, source: str='dgent') -> None
```

Initialize bus-enabled D-gent.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum and emit PUT event.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum (no event emitted for reads).

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete datum and emit DELETE event if successful.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data (no event emitted for reads).

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal chain (no event emitted for reads).

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence (no event emitted for reads).

---

## count

```python
async def count(self) -> int
```

Count data (no event emitted for reads).

---

## agents.d.datum

## datum

```python
module datum
```

Datum: The atomic unit of persisted data.

---

## Datum

```python
class Datum
```

The atomic unit of persisted data.

---

## create

```python
def create(cls, content: bytes, *, id: str | None=None, causal_parent: str | None=None, metadata: dict[str, str] | None=None, content_addressed: bool=False) -> Datum
```

Factory for creating Datum with sensible defaults.

---

## from_json

```python
def from_json(cls, data: dict[str, Any]) -> Datum
```

Deserialize from JSON-compatible dict.

---

## to_json

```python
def to_json(self) -> dict[str, Any]
```

Serialize to JSON-compatible dict.

---

## to_jsonl_line

```python
def to_jsonl_line(self) -> str
```

Serialize to a single JSONL line (no trailing newline).

---

## from_jsonl_line

```python
def from_jsonl_line(cls, line: str) -> Datum
```

Deserialize from a single JSONL line.

---

## with_metadata

```python
def with_metadata(self, **kwargs: str) -> Datum
```

Return new Datum with additional metadata.

---

## derive

```python
def derive(self, content: bytes, *, id: str | None=None, metadata: dict[str, str] | None=None) -> Datum
```

Create a new Datum that causally derives from this one.

---

## size

```python
def size(self) -> int
```

Size of content in bytes.

---

## agents.d.errors

## errors

```python
module errors
```

Error types for D-gents (Data Agents).

---

## StateError

```python
class StateError(Exception)
```

Base exception for D-gent errors.

---

## StateNotFoundError

```python
class StateNotFoundError(StateError)
```

State does not exist (e.g., first access to persistent store).

---

## StateCorruptionError

```python
class StateCorruptionError(StateError)
```

Stored state is invalid or corrupted.

---

## StateSerializationError

```python
class StateSerializationError(StateError)
```

State cannot be encoded for storage.

---

## StorageError

```python
class StorageError(StateError)
```

Backend storage operation failed.

---

## NoosphereError

```python
class NoosphereError(StateError)
```

Base for Noosphere layer errors.

---

## SemanticError

```python
class SemanticError(NoosphereError)
```

Semantic manifold operation failed.

---

## TemporalError

```python
class TemporalError(NoosphereError)
```

Temporal witness operation failed.

---

## LatticeError

```python
class LatticeError(NoosphereError)
```

Relational lattice operation failed.

---

## VoidNotFoundError

```python
class VoidNotFoundError(SemanticError)
```

No unexplored regions detected.

---

## DriftDetectionError

```python
class DriftDetectionError(TemporalError)
```

Could not analyze drift (insufficient data).

---

## NodeNotFoundError

```python
class NodeNotFoundError(LatticeError)
```

Node does not exist in lattice.

---

## EdgeNotFoundError

```python
class EdgeNotFoundError(LatticeError)
```

Edge does not exist in lattice.

---

## agents.d.legacy

## legacy

```python
module legacy
```

Legacy stubs for deleted D-gent modules.

---

## MemoryConfig

```python
class MemoryConfig
```

DEPRECATED: Old memory configuration.

---

## UnifiedMemory

```python
class UnifiedMemory(Generic[S])
```

DEPRECATED: Old unified memory abstraction.

---

## MemoryLoadResponse

```python
class MemoryLoadResponse
```

DEPRECATED: Old memory load response type.

---

## WitnessReport

```python
class WitnessReport
```

DEPRECATED: Old witness/trace report.

---

## MemoryPolynomialAgent

```python
class MemoryPolynomialAgent
```

DEPRECATED: Old polynomial memory agent.

---

## save

```python
async def save(self, state: S) -> None
```

Save state (stub stores in _current).

---

## load

```python
async def load(self) -> S | None
```

Load state (stub returns _current).

---

## witness

```python
async def witness(self, label: str, state: S) -> None
```

Record state snapshot (stub appends to history).

---

## agents.d.lens

## lens

```python
module lens
```

Lens: Compositional state access.

---

## Lens

```python
class Lens(Generic[S, A])
```

A composable getter/setter for accessing sub-state.

### Examples
```python
>>> name_lens = key_lens("name")
```
```python
>>> state = {"name": "Alice", "age": 30}
```
```python
>>> name_lens.get(state)
```
```python
>>> name_lens.set(state, "Bob")
```

---

## identity_lens

```python
def identity_lens() -> Lens[S, S]
```

Identity lens (focuses on whole state).

---

## key_lens

```python
def key_lens(key: str) -> Lens[dict[str, Any], Any]
```

Lens focusing on a dictionary key.

### Examples
```python
>>> lens = key_lens("user")
```
```python
>>> state = {"user": "Alice", "count": 5}
```
```python
>>> lens.get(state)
```
```python
>>> lens.set(state, "Bob")
```

---

## field_lens

```python
def field_lens(field_name: str) -> Lens[Any, Any]
```

Lens for dataclass field.

### Examples
```python
>>> from dataclasses import dataclass
```
```python
>>> @dataclass
```
```python
>>> lens = field_lens("name")
```
```python
>>> user = User(name="Alice", age=30)
```
```python
>>> lens.get(user)
```

---

## index_lens

```python
def index_lens(i: int) -> Lens[list[Any], Any]
```

Lens focusing on list element at index i.

### Examples
```python
>>> lens = index_lens(0)
```
```python
>>> items = [1, 2, 3]
```
```python
>>> lens.get(items)
```
```python
>>> lens.set(items, 10)
```

---

## attr_lens

```python
def attr_lens(attr_name: str) -> Lens[Any, Any]
```

Lens for object attribute (mutable objects).

### Examples
```python
>>> class Mutable:
```
```python
>>> lens = attr_lens("value")
```
```python
>>> obj = Mutable(42)
```
```python
>>> lens.get(obj)
```

---

## verify_get_put_law

```python
def verify_get_put_law(lens: Lens[S, A], state: S) -> bool
```

Verify GetPut law: set(s, get(s)) = s

---

## verify_put_get_law

```python
def verify_put_get_law(lens: Lens[S, A], state: S, value: A) -> bool
```

Verify PutGet law: get(set(s, a)) = a

---

## verify_put_put_law

```python
def verify_put_put_law(lens: Lens[S, A], state: S, a1: A, a2: A) -> bool
```

Verify PutPut law: set(set(s, a1), a2) = set(s, a2)

---

## verify_lens_laws

```python
def verify_lens_laws(lens: Lens[S, A], state: S, value1: A, value2: A) -> dict[str, bool]
```

Verify all three lens laws.

### Examples
```python
>>> lens = key_lens("name")
```
```python
>>> state = {"name": "Alice", "age": 30}
```
```python
>>> results = verify_lens_laws(lens, state, "Bob", "Carol")
```
```python
>>> results
```

---

## Prism

```python
class Prism(Generic[S, A])
```

A lens that may fail to focus (for optional fields).

### Examples
```python
>>> prism = optional_key_prism("user")
```
```python
>>> state1 = {"user": "Alice"}
```
```python
>>> state2 = {"count": 5}
```
```python
>>> prism.preview(state1)  # Some("Alice")
```
```python
>>> prism.preview(state2)  # None
```

---

## optional_key_prism

```python
def optional_key_prism(key: str) -> Prism[dict[str, Any], Any]
```

Prism focusing on an optional dictionary key.

### Examples
```python
>>> prism = optional_key_prism("user")
```
```python
>>> state = {"count": 5}
```
```python
>>> prism.preview(state)  # None (key doesn't exist)
```
```python
>>> prism.set_if_present(state, "Alice")  # {"count": 5} (unchanged)
```

---

## optional_field_prism

```python
def optional_field_prism(field_name: str) -> Prism[Any, Any]
```

Prism for optional dataclass field (may be None).

### Examples
```python
>>> @dataclass
```
```python
>>> prism = optional_field_prism("email")
```
```python
>>> user = User(name="Alice", email=None)
```
```python
>>> prism.preview(user)  # None
```

---

## optional_index_prism

```python
def optional_index_prism(i: int) -> Prism[list[Any], Any]
```

Prism focusing on list element at index i (if it exists).

### Examples
```python
>>> prism = optional_index_prism(5)
```
```python
>>> items = [1, 2, 3]
```
```python
>>> prism.preview(items)  # None (index out of bounds)
```

---

## Traversal

```python
class Traversal(Generic[S, A])
```

Like a lens, but can target 0..N elements.

### Examples
```python
>>> trav = list_traversal()
```
```python
>>> items = [1, 2, 3]
```
```python
>>> trav.get_all(items)  # [1, 2, 3]
```
```python
>>> trav.modify(items, lambda x: x * 2)  # [2, 4, 6]
```

---

## list_traversal

```python
def list_traversal() -> Traversal[List[A], A]
```

Traversal over all elements of a list.

### Examples
```python
>>> trav = list_traversal()
```
```python
>>> items = [1, 2, 3]
```
```python
>>> trav.get_all(items)  # [1, 2, 3]
```
```python
>>> trav.modify(items, lambda x: x * 2)  # [2, 4, 6]
```

---

## dict_values_traversal

```python
def dict_values_traversal() -> Traversal[dict[str, Any], Any]
```

Traversal over all values in a dictionary.

### Examples
```python
>>> trav = dict_values_traversal()
```
```python
>>> d = {"a": 1, "b": 2}
```
```python
>>> trav.get_all(d)  # [1, 2]
```
```python
>>> trav.modify(d, lambda x: x * 2)  # {"a": 2, "b": 4}
```

---

## dict_keys_traversal

```python
def dict_keys_traversal() -> Traversal[dict[str, Any], Any]
```

Traversal over all keys in a dictionary.

### Examples
```python
>>> trav = dict_keys_traversal()
```
```python
>>> d = {"a": 1, "b": 2}
```
```python
>>> trav.get_all(d)  # ["a", "b"]
```
```python
>>> trav.modify(d, str.upper)  # {"A": 1, "B": 2}
```

---

## dict_items_traversal

```python
def dict_items_traversal() -> Traversal[dict[str, Any], tuple[str, Any]]
```

Traversal over all (key, value) pairs in a dictionary.

### Examples
```python
>>> trav = dict_items_traversal()
```
```python
>>> d = {"a": 1, "b": 2}
```
```python
>>> trav.get_all(d)  # [("a", 1), ("b", 2)]
```

---

## LensValidation

```python
class LensValidation
```

Result of lens law validation.

---

## validate_composed_lens

```python
def validate_composed_lens(lens1: Lens[S, A], lens2: Lens[A, B], state: S, value1: B, value2: B) -> LensValidation
```

Validate that a composition of two lenses satisfies lens laws.

### Examples
```python
>>> user_lens = key_lens("user")
```
```python
>>> name_lens = key_lens("name")
```
```python
>>> state = {"user": {"name": "Alice"}}
```
```python
>>> result = validate_composed_lens(user_lens, name_lens, state, "Bob", "Carol")
```
```python
>>> result.is_valid
```

---

## verify_prism_laws

```python
def verify_prism_laws(prism: Prism[S, A], state_with_value: S, state_without_value: S, value: A) -> dict[str, bool]
```

Verify prism laws.

---

## verify_traversal_laws

```python
def verify_traversal_laws(trav: Traversal[S, A], state: S, value: A) -> dict[str, bool]
```

Verify traversal laws.

---

## compose

```python
def compose(self, other: 'Lens[A, B]') -> 'Lens[S, B]'
```

Compose two lenses to access deeply nested state.

### Examples
```python
>>> user_lens = key_lens("user")
```
```python
>>> name_lens = key_lens("name")
```
```python
>>> full_lens = user_lens >> name_lens
```
```python
>>> state = {"user": {"name": "Alice"}}
```
```python
>>> full_lens.get(state)
```

---

## __rshift__

```python
def __rshift__(self, other: 'Lens[A, B]') -> 'Lens[S, B]'
```

Syntactic sugar: lens1 >> lens2

---

## set_if_present

```python
def set_if_present(self, state: S, value: A) -> S
```

Set the value only if the prism focuses successfully.

---

## compose

```python
def compose(self, other: 'Prism[A, B]') -> 'Prism[S, B]'
```

Compose two prisms: S -?-> A -?-> B.

---

## __rshift__

```python
def __rshift__(self, other: 'Prism[A, B]') -> 'Prism[S, B]'
```

Syntactic sugar: prism1 >> prism2

---

## set_all

```python
def set_all(self, state: S, value: A) -> S
```

Set all focused elements to the same value.

---

## filter

```python
def filter(self, predicate: Callable[[A], bool]) -> 'Traversal[S, A]'
```

Create a filtered traversal that only targets elements matching predicate.

### Examples
```python
>>> trav = list_traversal().filter(lambda x: x > 2)
```
```python
>>> items = [1, 2, 3, 4, 5]
```
```python
>>> trav.get_all(items)  # [3, 4, 5]
```

---

## compose

```python
def compose(self, other: 'Traversal[A, B]') -> 'Traversal[S, B]'
```

Compose two traversals: S ->> A ->> B.

---

## __rshift__

```python
def __rshift__(self, other: 'Traversal[A, B]') -> 'Traversal[S, B]'
```

Syntactic sugar: trav1 >> trav2

---

## agents.d.lens_agent

## lens_agent

```python
module lens_agent
```

LensAgent: D-gent with focused state view.

---

## LensAgent

```python
class LensAgent(Generic[S, A])
```

A D-gent that provides a focused view into parent state.

### Examples
```python
>>> from agents.d import VolatileAgent
```
```python
>>> from agents.d.lens import key_lens
```
```python
>>> >>> # Global state
```
```python
>>> global_dgent = VolatileAgent(_state={"users": {}, "products": {}})
```
```python
>>> >>> # Focused D-gent for users only
```

---

## focused

```python
def focused(parent: DataAgent[S], lens: Lens[S, A]) -> LensAgent[S, A]
```

Create a LensAgent (convenience function).

### Examples
```python
>>> from agents.d import VolatileAgent
```
```python
>>> from agents.d.lens import key_lens
```
```python
>>> dgent = VolatileAgent(_state={"a": 1, "b": 2})
```
```python
>>> focused_dgent = focused(dgent, key_lens("a"))
```
```python
>>> await focused_dgent.load()
```

---

## load

```python
async def load(self) -> A
```

Load parent state, project to sub-state.

---

## save

```python
async def save(self, sub_state: A) -> None
```

Update sub-state within parent state.

---

## history

```python
async def history(self, limit: int | None=None) -> List[A]
```

Project historical states through lens.

---

## __rshift__

```python
def __rshift__(self, other: Lens[A, B]) -> LensAgent[S, B]
```

Compose lenses for deeper focusing: self >> other.

### Examples
```python
>>> from agents.d import VolatileAgent
```
```python
>>> from agents.d.lens import key_lens
```
```python
>>> >>> # Nested state: user → address → zip
```
```python
>>> state = {"user": {"address": {"zip": "12345"}}}
```
```python
>>> dgent = VolatileAgent(_state=state)
```

---

## agents.d.persistent

## persistent

```python
module persistent
```

PersistentAgent: File-backed state with atomic writes.

---

## PersistentAgent

```python
class PersistentAgent(Generic[S])
```

File-backed D-gent with atomic writes and JSONL history.

### Examples
```python
>>> from dataclasses import dataclass
```
```python
>>> @dataclass
```
```python
>>> dgent = PersistentAgent(
```
```python
>>> await dgent.save(UserProfile(name="Alice", age=30))
```
```python
>>> profile = await dgent.load()
```

---

## __init__

```python
def __init__(self, path: Path | str, schema: Type[S], max_history: int=100) -> None
```

Initialize persistent D-gent.

---

## load

```python
async def load(self) -> S
```

Load state from file.

---

## save

```python
async def save(self, state: S) -> None
```

Atomically save state to file + append to history.

---

## history

```python
async def history(self, limit: int | None=None) -> List[S]
```

Load historical states from JSONL file.

---

## enum_serializer

```python
def enum_serializer(obj: Any) -> Any
```

Convert enums to their values for JSON serialization.

---

## agents.d.protocol

## protocol

```python
module protocol
```

D-gent Protocols: Dual interface for data persistence.

### Things to Know

ℹ️ put() overwrites existing datum with same ID This is intentional for graceful degradation updates, not a bug. Use content-addressed IDs (SHA-256) if you need immutability.
  - *Verified in: `test_backends.py::TestPut::test_put_overwrites_existing`*

ℹ️ causal_chain() returns empty list for missing parent, not error If a datum has causal_parent pointing to a deleted datum, you get just the child in the chain. Handle orphaned data gracefully.
  - *Verified in: `test_backends.py::TestCausalChain::test_causal_chain_orphaned_datum`*

ℹ️ list() returns newest first (sorted by created_at descending) This affects pagination. Use `after` param for time-based filtering.
  - *Verified in: `test_backends.py::TestList::test_list_sorted_by_created_at_desc`*

ℹ️ DgentRouter silently falls back to memory backend If preferred backend unavailable (e.g., Postgres URL missing), it uses MEMORY without error. Check selected_backend after put().
  - *Verified in: `test_router.py::TestBackendSelection::test_falls_back_to_memory`*

ℹ️ DataBus subscriber errors don't block other subscribers A failing handler is logged but doesn't prevent event delivery. Check bus.stats["total_errors"] for silent failures.
  - *Verified in: `test_bus.py::TestErrorHandling::test_subscriber_error_does_not_block`*

ℹ️ get() and list() are silent reads - no DataBus events emitted Only put() and delete() emit events. If you need read tracking, instrument at a higher layer (e.g., M-gent reinforcement).
  - *Verified in: `test_bus.py::TestBusEnabledDgent::test_get_does_not_emit`*

---

## DataAgent

```python
class DataAgent(Protocol[S])
```

Typed state management protocol for Symbiont pattern.

---

## DgentProtocol

```python
class DgentProtocol(Protocol)
```

The minimal interface every D-gent backend implements.

---

## BaseDgent

```python
class BaseDgent
```

Base class providing default implementations for optional methods.

---

## load

```python
async def load(self) -> S
```

Retrieve current state.

---

## save

```python
async def save(self, state: S) -> None
```

Persist new state.

---

## history

```python
async def history(self, limit: int | None=None) -> List[S]
```

Query state evolution over time.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum, return ID.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum by ID.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Remove datum, return success.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with optional filters.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check if a datum exists.

---

## count

```python
async def count(self) -> int
```

Count total number of data stored.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Default: check via get().

---

## count

```python
async def count(self) -> int
```

Default: count via list() - may be slow.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum, return ID.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum by ID.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Remove datum, return success.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data with optional filters.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal ancestors of a datum.

---

## agents.d.router

## router

```python
module router
```

DgentRouter: Backend selection with graceful degradation.

---

## Backend

```python
class Backend(Enum)
```

Available backends in the projection lattice.

---

## BackendStatus

```python
class BackendStatus
```

Status of a backend.

---

## DgentRouter

```python
class DgentRouter(BaseDgent)
```

Routes data operations to the best available backend.

---

## create_dgent

```python
def create_dgent(namespace: str='default', preferred: Backend | None=None, data_dir: Path | None=None) -> DgentRouter
```

Create a D-gent router with the given configuration.

---

## put

```python
async def put(self, datum: Datum) -> str
```

Store datum via selected backend.

---

## get

```python
async def get(self, id: str) -> Datum | None
```

Retrieve datum via selected backend.

---

## delete

```python
async def delete(self, id: str) -> bool
```

Delete datum via selected backend.

---

## list

```python
async def list(self, prefix: str | None=None, after: float | None=None, limit: int=100) -> List[Datum]
```

List data via selected backend.

---

## causal_chain

```python
async def causal_chain(self, id: str) -> List[Datum]
```

Get causal chain via selected backend.

---

## exists

```python
async def exists(self, id: str) -> bool
```

Check existence via selected backend.

---

## count

```python
async def count(self) -> int
```

Count data via selected backend.

---

## selected_backend

```python
def selected_backend(self) -> Backend | None
```

Get the currently selected backend (None if not yet selected).

---

## status

```python
async def status(self) -> List[BackendStatus]
```

Get availability status of all backends.

---

## force_backend

```python
async def force_backend(self, backend: Backend) -> None
```

Force use of a specific backend (raises if unavailable).

---

## reset

```python
def reset(self) -> None
```

Reset the router (clears selected backend).

---

## agents.d.state_monad

## state_monad

```python
module state_monad
```

StateMonadFunctor: Legacy stub for deleted module.

---

## StateMonadFunctor

```python
class StateMonadFunctor(Generic[S])
```

DEPRECATED: Old state monad functor.

---

## run

```python
def run(self, f: Any) -> tuple[Any, S]
```

Run a stateful computation.

---

## agents.d.symbiont

## symbiont

```python
module symbiont
```

Symbiont: Fuses stateless logic with stateful memory.

---

## Symbiont

```python
class Symbiont(Agent[In, Out], Generic[In, Out, S])
```

Fuses stateless logic with stateful memory.

### Examples
```python
>>> def chat_logic(msg: str, history: list) -> tuple[str, list]:
```
```python
>>> memory = VolatileAgent(_state=[])
```
```python
>>> chatbot = Symbiont(logic=chat_logic, memory=memory)
```
```python
>>> await chatbot.invoke("Hello")  # Returns "Echo: Hello"
```

---

## name

```python
def name(self) -> str
```

Name for composition chains.

---

## invoke

```python
async def invoke(self, input_data: In) -> Out
```

Execute the stateful computation.

---

## agents.d.upgrader

## upgrader

```python
module upgrader
```

AutoUpgrader: Automatic data promotion through the projection lattice.

---

## UpgradeReason

```python
class UpgradeReason(Enum)
```

Reasons for promoting data to a higher tier.

---

## UpgradePolicy

```python
class UpgradePolicy
```

Policy for when to upgrade data to a more durable tier.

---

## UpgradeStats

```python
class UpgradeStats
```

Statistics about upgrade activity.

---

## DatumStats

```python
class DatumStats
```

Statistics for a single datum (for upgrade decisions).

---

## AutoUpgrader

```python
class AutoUpgrader
```

Background process for automatic data promotion.

---

## migrate_data

```python
async def migrate_data(source: DgentProtocol, target: DgentProtocol, batch_size: int=100, delete_source: bool=False) -> int
```

Migrate all data from source to target.

---

## verify_migration

```python
async def verify_migration(source: DgentProtocol, target: DgentProtocol) -> tuple[bool, list[str]]
```

Verify that all data in source exists in target.

---

## __init__

```python
def __init__(self, source: DgentProtocol, source_tier: Backend, targets: dict[Backend, DgentProtocol], bus: DataBus | None=None, policy: UpgradePolicy | None=None, check_interval: float=30.0, synergy_bus: 'SynergyEventBus | None'=None, emit_synergy: bool=True) -> None
```

Initialize the AutoUpgrader.

---

## on_upgrade

```python
def on_upgrade(self, callback: Callable[[Datum, Backend, Backend], Awaitable[None]]) -> None
```

Register callback for upgrade events.

---

## start

```python
async def start(self) -> None
```

Start the background upgrade process.

---

## stop

```python
async def stop(self) -> None
```

Stop the background upgrade process.

---

## force_upgrade

```python
async def force_upgrade(self, datum_id: str, to_tier: Backend) -> bool
```

Force upgrade a specific datum to a target tier.

---

## mark_important

```python
def mark_important(self, datum_id: str) -> None
```

Mark a datum as important (for Postgres promotion).

---

## stats

```python
def stats(self) -> UpgradeStats
```

Get upgrade statistics.

---

## get_datum_stats

```python
def get_datum_stats(self, datum_id: str) -> DatumStats | None
```

Get tracking stats for a specific datum.

---

## agents.d.volatile

## volatile

```python
module volatile
```

VolatileAgent: In-memory state storage with bounded history.

---

## VolatileAgent

```python
class VolatileAgent(Generic[S])
```

In-memory state storage.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize history deque with correct maxlen.

---

## load

```python
async def load(self) -> S
```

Load current state.

---

## save

```python
async def save(self, state: S) -> None
```

Save new state.

---

## history

```python
async def history(self, limit: int | None=None) -> List[S]
```

Query state evolution over time.

---

## snapshot

```python
def snapshot(self) -> S
```

Non-async snapshot for testing/debugging.

---

## __rshift__

```python
def __rshift__(self, other: 'Lens[S, A]') -> 'LensAgent[S, A]'
```

Compose with a lens to create focused view: dgent >> lens.

### Examples
```python
>>> from agents.d.lens import key_lens
```
```python
>>> >>> # Global state
```
```python
>>> dgent = VolatileAgent(_state={"users": {}, "products": {}})
```
```python
>>> >>> # Focus on users via composition
```
```python
>>> user_dgent = dgent >> key_lens("users")
```

---

## __or__

```python
def __or__(self, transform: 'Callable[[S], S]') -> 'TransformAgent[S]'
```

Compose with a transformation function: dgent | transform.

### Examples
```python
>>> # Normalize state on access
```
```python
>>> dgent = VolatileAgent(_state={"count": 5})
```
```python
>>> normalized = dgent | (lambda s: {**s, "count": max(0, s["count"])})
```
```python
>>> >>> await normalized.save({"count": -10})
```
```python
>>> await normalized.load()
```

---

## agents.flux.__init__

## __init__

```python
module __init__
```

Flux Functor: Lifting agents from Discrete State to Continuous Flow.

### Examples
```python
>>> from agents.flux import Flux, FluxConfig
```
```python
>>> from agents.flux.sources import from_iterable
```
```python
>>> >>> # Lift a discrete agent to flux domain
```
```python
>>> flux_agent = Flux.lift(my_agent)
```
```python
>>> >>> # Process a stream
```

---

## agents.flux.agent

## agent

```python
module agent
```

FluxAgent: Stream-transforming agent wrapper.

### Things to Know

🚨 **Critical:** start() returns AsyncIterator[B], NOT None. You MUST consume the iterator with `async for`. Just calling start() does nothing.
  - *Verified in: `test_agent.py::TestFluxAgentStartReturnsAsyncIterator`*

ℹ️ invoke() behavior changes based on state. DORMANT = direct call, FLOWING = perturbation injected into stream. Same method, different semantics. Check flux.state before assuming behavior.
  - *Verified in: `test_agent.py::TestFluxAgentInvokeOnDormant`*

🚨 **Critical:** Cannot start() a FLOWING flux. You'll get FluxStateError. The flux must be DORMANT or STOPPED first. Use flux.stop() to reset.
  - *Verified in: `test_agent.py::TestFluxAgentStateTransitions::test_cannot_start_while_flowing`*

ℹ️ Entropy exhaustion causes COLLAPSED state, which is TERMINAL. Unlike STOPPED, you cannot restart from COLLAPSED. Call reset() first, which restores entropy_budget and clears counters.
  - *Verified in: `test_agent.py::TestFluxAgentEntropyManagement::test_entropy_collapse`*

ℹ️ Core processing is EVENT-DRIVEN, not timer-driven. No asyncio.sleep() in _process_flux. If you add polling loops, you're fighting the design. Use event sources and let the stream drive execution.
  - *Verified in: `test_agent.py::TestNoAsyncSleepInCore`*

---

## FluxAgent

```python
class FluxAgent(Generic[A, B])
```

An agent lifted into the streaming domain.

### Examples
```python
>>> flux_agent = Flux.lift(my_agent)
```
```python
>>> async for result in flux_agent.start(events):
```
```python
>>> pipeline = flux_a | flux_b
```
```python
>>> async for result in pipeline.start(source):
```

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize runtime state and queues.

---

## name

```python
def name(self) -> str
```

Human-readable name including inner agent.

---

## state

```python
def state(self) -> FluxState
```

Current lifecycle state.

---

## events_processed

```python
def events_processed(self) -> int
```

Number of events processed so far.

---

## entropy_remaining

```python
def entropy_remaining(self) -> float
```

Remaining entropy budget.

---

## id

```python
def id(self) -> str
```

Unique identifier for this flux.

---

## is_running

```python
def is_running(self) -> bool
```

Check if flux is currently processing.

---

## metabolism

```python
def metabolism(self) -> 'FluxMetabolism[A, B] | None'
```

Optional metabolism adapter.

---

## attach_metabolism

```python
def attach_metabolism(self, metabolism: 'FluxMetabolism[A, B]') -> 'FluxAgent[A, B]'
```

Attach a metabolism adapter to this flux.

### Examples
```python
>>> flux = Flux.lift(agent).attach_metabolism(metabolism)
```

---

## detach_metabolism

```python
def detach_metabolism(self) -> 'FluxMetabolism[A, B] | None'
```

Detach the metabolism adapter.

---

## attach_mirror

```python
def attach_mirror(self, mirror: 'HolographicBuffer') -> 'FluxAgent[A, B]'
```

Attach a HolographicBuffer for Terrarium observability.

### Examples
```python
>>> flux = Flux.lift(agent).attach_mirror(buffer)
```

---

## detach_mirror

```python
def detach_mirror(self) -> 'HolographicBuffer | None'
```

Detach the mirror.

---

## mirror

```python
def mirror(self) -> 'HolographicBuffer | None'
```

Optional mirror for Terrarium observability.

---

## attach_purgatory

```python
def attach_purgatory(self, purgatory: 'Purgatory') -> 'FluxAgent[A, B]'
```

Attach a Purgatory for semaphore handling.

### Examples
```python
>>> flux = Flux.lift(agent).attach_purgatory(purgatory)
```

---

## detach_purgatory

```python
def detach_purgatory(self) -> 'Purgatory | None'
```

Detach the purgatory.

---

## purgatory

```python
def purgatory(self) -> 'Purgatory | None'
```

Optional purgatory for semaphore handling.

---

## start

```python
async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]
```

Start the flux and return the output stream.

### Examples
```python
>>> async for result in flux_agent.start(events):
```
```python
>>> pipeline = flux_a | flux_b
```
```python
>>> async for result in pipeline.start(source):
```

---

## invoke

```python
async def invoke(self, input_data: A) -> B
```

Discrete invocation OR perturbation depending on state.

---

## stop

```python
async def stop(self) -> None
```

Stop the flux gracefully.

---

## wait

```python
async def wait(self) -> None
```

Wait for flux to complete (source exhausted or stopped).

---

## reset

```python
def reset(self) -> None
```

Reset flux to DORMANT state.

---

## __or__

```python
def __or__(self, other: 'FluxAgent[B, Any]') -> 'FluxPipeline[A, Any]'
```

Pipe operator: flux_a | flux_b

---

## __rshift__

```python
def __rshift__(self, other: Agent[B, Any]) -> 'FluxAgent[A, Any]'
```

Compose with static agent: Flux(f) >> g

---

## agents.flux.circuit_breaker

## circuit_breaker

```python
module circuit_breaker
```

Circuit Breaker for Synapse target operations.

---

## CircuitState

```python
class CircuitState(Enum)
```

Circuit breaker states.

---

## CircuitOpenError

```python
class CircuitOpenError(Exception)
```

Raised when circuit is open and call is rejected.

---

## CircuitBreakerConfig

```python
class CircuitBreakerConfig
```

Configuration for circuit breaker behavior.

---

## CircuitBreaker

```python
class CircuitBreaker
```

Circuit breaker for protecting Synapse targets.

---

## create_qdrant_breaker

```python
def create_qdrant_breaker(failure_threshold: int=5, recovery_timeout: float=30.0) -> CircuitBreaker
```

Create a circuit breaker for Qdrant operations.

---

## create_embedding_breaker

```python
def create_embedding_breaker(failure_threshold: int=3, recovery_timeout: float=60.0) -> CircuitBreaker
```

Create a circuit breaker for embedding provider.

---

## state

```python
def state(self) -> CircuitState
```

Current circuit state.

---

## is_closed

```python
def is_closed(self) -> bool
```

True if circuit is closed (normal operation).

---

## is_open

```python
def is_open(self) -> bool
```

True if circuit is open (failing fast).

---

## is_half_open

```python
def is_half_open(self) -> bool
```

True if circuit is half-open (testing recovery).

---

## time_in_state

```python
def time_in_state(self) -> float
```

Seconds since last state change.

---

## time_until_retry

```python
def time_until_retry(self) -> float
```

Seconds until circuit will attempt half-open.

---

## call

```python
async def call(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any
```

Execute function through circuit breaker.

---

## call_sync

```python
def call_sync(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T
```

Synchronous version of call.

---

## force_open

```python
def force_open(self) -> None
```

Manually open the circuit (for testing/emergencies).

---

## force_close

```python
def force_close(self) -> None
```

Manually close the circuit (for testing/recovery).

---

## reset

```python
def reset(self) -> None
```

Reset to initial closed state.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get circuit breaker statistics.

---

## agents.flux.config

## config

```python
module config
```

Flux configuration.

---

## FluxConfig

```python
class FluxConfig
```

Configuration for FluxAgent behavior.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate configuration values.

---

## with_entropy

```python
def with_entropy(self, budget: float | None=None, decay: float | None=None, max_events: int | None=None) -> 'FluxConfig'
```

Create a new config with modified entropy settings.

---

## with_backpressure

```python
def with_backpressure(self, buffer_size: int | None=None, drop_policy: str | None=None) -> 'FluxConfig'
```

Create a new config with modified backpressure settings.

---

## with_feedback

```python
def with_feedback(self, fraction: float | None=None, transform: Callable[[Any], Any] | None=None, queue_size: int | None=None) -> 'FluxConfig'
```

Create a new config with modified feedback settings.

---

## infinite

```python
def infinite(cls) -> 'FluxConfig'
```

Create a config with no entropy limit (runs until source exhausts).

---

## bounded

```python
def bounded(cls, max_events: int) -> 'FluxConfig'
```

Create a config that processes exactly max_events events.

---

## ouroboric

```python
def ouroboric(cls, feedback_fraction: float=0.5) -> 'FluxConfig'
```

Create a config with ouroboric feedback enabled.

---

## agents.flux.dlq

## dlq

```python
module dlq
```

Dead Letter Queue for CDC events that fail processing.

---

## DLQReason

```python
class DLQReason(Enum)
```

Reason for event landing in DLQ.

---

## DeadLetterEvent

```python
class DeadLetterEvent
```

Event that failed all retry attempts.

---

## DeadLetterQueue

```python
class DeadLetterQueue
```

Stores events that failed processing.

---

## get_dlq

```python
def get_dlq(max_size: int=1000) -> DeadLetterQueue
```

Get or create the global DLQ instance.

---

## reset_dlq

```python
def reset_dlq() -> None
```

Reset global DLQ (for testing).

---

## from_event

```python
def from_event(cls, event: Any, target: str, error: str, reason: DLQReason, retry_count: int) -> 'DeadLetterEvent'
```

Create from a ChangeEvent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for storage or API.

---

## __init__

```python
def __init__(self, max_size: int=1000, persist_hook: Callable[[DeadLetterEvent], Any] | None=None) -> None
```

Initialize the DLQ.

---

## enqueue

```python
async def enqueue(self, event: DeadLetterEvent) -> None
```

Add failed event to DLQ.

---

## enqueue_sync

```python
def enqueue_sync(self, event: DeadLetterEvent) -> None
```

Synchronous enqueue (skips persist hook).

---

## drain

```python
def drain(self) -> list[DeadLetterEvent]
```

Get all events for reprocessing.

---

## peek

```python
def peek(self, n: int=10) -> list[DeadLetterEvent]
```

Peek at the first n events without removing.

---

## peek_by_table

```python
def peek_by_table(self, table: str) -> list[DeadLetterEvent]
```

Get events for a specific table.

---

## peek_by_reason

```python
def peek_by_reason(self, reason: DLQReason) -> list[DeadLetterEvent]
```

Get events with a specific failure reason.

---

## remove

```python
def remove(self, event: DeadLetterEvent) -> bool
```

Remove a specific event (after manual processing).

---

## clear

```python
def clear(self) -> int
```

Clear all events. Returns count cleared.

---

## size

```python
def size(self) -> int
```

Current queue size.

---

## is_empty

```python
def is_empty(self) -> bool
```

True if queue is empty.

---

## total_enqueued

```python
def total_enqueued(self) -> int
```

Total events ever enqueued.

---

## total_evicted

```python
def total_evicted(self) -> int
```

Total events evicted due to queue full.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get DLQ statistics.

---

## agents.flux.errors

## errors

```python
module errors
```

Flux-specific exceptions.

### Things to Know

ℹ️ All Flux exceptions carry a `context` dict with structured data. Don't just catch and log the message - check context for state info, buffer sizes, stage indices, etc. Useful for debugging pipelines.
  - *Verified in: `Structural - FluxError.__init__ stores context`*

ℹ️ FluxStateError contains current_state and attempted_operation fields. When debugging "cannot X from state Y" errors, these tell you exactly what the flux was doing and what you tried to do.
  - *Verified in: `Structural - FluxStateError stores these fields`*

---

## FluxError

```python
class FluxError(Exception)
```

Base exception for flux operations.

---

## FluxStateError

```python
class FluxStateError(FluxError)
```

Invalid state transition.

---

## FluxEntropyError

```python
class FluxEntropyError(FluxError)
```

Entropy budget exhausted.

---

## FluxBackpressureError

```python
class FluxBackpressureError(FluxError)
```

Backpressure limit exceeded.

---

## FluxPerturbationError

```python
class FluxPerturbationError(FluxError)
```

Perturbation failed.

---

## FluxPipelineError

```python
class FluxPipelineError(FluxError)
```

Pipeline composition or execution failed.

---

## FluxSourceError

```python
class FluxSourceError(FluxError)
```

Source stream error.

---

## agents.flux.functor

## functor

```python
module functor
```

Flux Functor: The lift mechanism.

### Things to Know

ℹ️ Flux.lift() creates a NEW FluxAgent each time. Lifting the same agent twice gives two independent flux instances with separate state. If you need shared state, lift once and reuse the FluxAgent. (Evidence: Structural - lift() calls FluxAgent constructor)

🚨 **Critical:** Flux.unlift() does NOT stop a running flux. It just returns the inner agent. Always call flux.stop() first if the flux is running.
  - *Verified in: `Structural - unlift docstring explicitly warns`*

ℹ️ Functor law verification is complex for FluxFunctor because it operates on streams. Identity law holds per-element, not for the whole stream. Composition law requires collecting stream outputs.
  - *Verified in: `test_integration.py::TestFluxFunctorLaws`*

ℹ️ FluxFunctor.pure() returns a single-element AsyncIterator, not a FluxAgent. Use it for stream-level identity, not agent lifting.
  - *Verified in: `Structural - pure returns async generator`*

---

## Flux

```python
class Flux
```

The Flux Functor: Agent[A, B] → Agent[Flux[A], Flux[B]]

### Examples
```python
>>> flux_agent = Flux.lift(my_agent)
```
```python
>>> async for result in flux_agent.start(source):
```

---

## FluxLifter

```python
class FluxLifter
```

A configured lifter that can lift multiple agents with the same config.

---

## FluxFunctor

```python
class FluxFunctor(UniversalFunctor[FluxAgent[Any, Any]])
```

Universal Functor for Flux (stream processing) context.

### Examples
```python
>>> flux_agent = FluxFunctor.lift(my_agent)
```
```python
>>> async for result in flux_agent.start(source):
```

---

## lift

```python
def lift(agent: Agent[A, B], config: FluxConfig | None=None) -> FluxAgent[A, B]
```

Lift agent to flux domain.

### Examples
```python
>>> from agents.poly import Id
```
```python
>>> flux_id = Flux.lift(Id())
```
```python
>>> # flux_id now maps AsyncIterator[A] → AsyncIterator[A]
```

---

## unlift

```python
def unlift(flux_agent: FluxAgent[A, B]) -> Agent[A, B]
```

Extract inner agent from flux.

---

## is_flux

```python
def is_flux(agent: Any) -> bool
```

Check if agent is a FluxAgent.

---

## lift_with_config

```python
def lift_with_config(entropy_budget: float=1.0, entropy_decay: float=0.01, buffer_size: int=100, drop_policy: str='block', feedback_fraction: float=0.0) -> 'FluxLifter'
```

Create a configured lifter for lifting multiple agents.

### Examples
```python
>>> lifter = Flux.lift_with_config(buffer_size=50)
```
```python
>>> flux_a = lifter(agent_a)
```
```python
>>> flux_b = lifter(agent_b)
```

---

## __call__

```python
def __call__(self, agent: Agent[A, B]) -> FluxAgent[A, B]
```

Lift an agent using this lifter's configuration.

---

## config

```python
def config(self) -> FluxConfig
```

The configuration used by this lifter.

---

## with_config

```python
def with_config(self, **kwargs: Any) -> 'FluxLifter'
```

Create a new lifter with modified configuration.

---

## lift

```python
def lift(agent: Agent[A, B]) -> Any
```

Lift an agent to the streaming domain.

---

## pure

```python
def pure(value: A) -> AsyncIterator[A]
```

Embed a value as a single-element stream.

---

## agents.flux.metabolism

## metabolism

```python
module metabolism
```

FluxMetabolism: Bridge between Flux and Metabolic Engine.

---

## FluxMetabolism

```python
class FluxMetabolism(Generic[A, B])
```

Adapter connecting FluxAgent to MetabolicEngine.

### Examples
```python
>>> from protocols.agentese.metabolism import get_metabolic_engine
```
```python
>>> from agents.flux.metabolism import FluxMetabolism
```
```python
>>> >>> metabolism = FluxMetabolism(engine=get_metabolic_engine())
```
```python
>>> flux_agent = Flux.lift(my_agent)
```
```python
>>> flux_agent.attach_metabolism(metabolism)
```

---

## create_flux_metabolism

```python
def create_flux_metabolism(engine: 'MetabolicEngine | None'=None, input_tokens: int=50, output_tokens: int=100, on_fever: Any | None=None) -> FluxMetabolism[Any, Any]
```

Factory function for FluxMetabolism.

---

## consume

```python
async def consume(self, _event: A) -> 'FeverEvent | None'
```

Called when FluxAgent processes an event.

---

## tithe

```python
def tithe(self, amount: float=0.1) -> dict[str, Any]
```

Voluntarily discharge metabolic pressure.

---

## pressure

```python
def pressure(self) -> float
```

Current metabolic pressure.

---

## in_fever

```python
def in_fever(self) -> bool
```

Whether the system is currently in fever state.

---

## temperature

```python
def temperature(self) -> float
```

Token-based temperature (input/output ratio).

---

## status

```python
def status(self) -> dict[str, Any]
```

Get combined flux-metabolism status.

---

## agents.flux.mirror

## mirror

```python
module mirror
```

HolographicBuffer: The Mirror Protocol implementation.

---

## WebSocketLike

```python
class WebSocketLike(Protocol)
```

Protocol for WebSocket-like objects.

---

## HolographicBuffer

```python
class HolographicBuffer
```

The Mirror.

---

## send_text

```python
async def send_text(self, data: str) -> None
```

Send text data.

---

## accept

```python
async def accept(self) -> None
```

Accept the connection.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize the history deque.

---

## observer_count

```python
def observer_count(self) -> int
```

Number of active observers (mirrors).

---

## history_length

```python
def history_length(self) -> int
```

Current history length.

---

## events_reflected

```python
def events_reflected(self) -> int
```

Total events reflected through this buffer.

---

## pending_broadcast_count

```python
def pending_broadcast_count(self) -> int
```

Number of broadcasts still in flight.

---

## is_shutting_down

```python
def is_shutting_down(self) -> bool
```

True if the buffer is draining for shutdown.

---

## reflect

```python
async def reflect(self, event: dict[str, Any]) -> None
```

Emit an event through the mirror.

---

## attach_mirror

```python
async def attach_mirror(self, websocket: WebSocketLike) -> None
```

Connect a read-only observer (The Reflection).

---

## detach_mirror

```python
def detach_mirror(self, websocket: WebSocketLike) -> bool
```

Remove an observer.

---

## clear_history

```python
def clear_history(self) -> None
```

Clear the history buffer.

---

## get_snapshot

```python
def get_snapshot(self) -> list[dict[str, Any]]
```

Get current history snapshot.

---

## drain

```python
async def drain(self, timeout: float | None=None) -> int
```

Gracefully drain pending broadcasts before shutdown.

---

## shutdown

```python
async def shutdown(self) -> None
```

Full graceful shutdown: drain broadcasts and disconnect mirrors.

---

## agents.flux.perturbation

## perturbation

```python
module perturbation
```

Perturbation handling for FluxAgent.

### Things to Know

ℹ️ Perturbation priority ordering is REVERSED for asyncio.PriorityQueue. Higher priority values come FIRST (e.g., priority=100 before priority=10). This is because PriorityQueue is a min-heap, so we flip comparison.
  - *Verified in: `test_perturbation.py::TestPerturbationOrdering::test_higher_priority_comes_first`*

ℹ️ set_result/set_exception/cancel are IDEMPOTENT. Calling them on an already-done Future is safe (no-op). This prevents race conditions between flux processing and caller cancellation.
  - *Verified in: `test_perturbation.py::TestPerturbationResult::test_set_result_idempotent`*

ℹ️ create_perturbation() uses priority=100 by default, not 0. This means helper-created perturbations are HIGH priority. If you want normal priority, explicitly pass priority=0.
  - *Verified in: `test_perturbation.py::TestCreatePerturbation::test_create_with_data`*

---

## Perturbation

```python
class Perturbation
```

A high-priority event injected via invoke() on a FLOWING flux.

---

## is_perturbation

```python
def is_perturbation(event: Any) -> bool
```

Check if event is a Perturbation wrapper.

---

## unwrap_perturbation

```python
def unwrap_perturbation(event: Any) -> tuple[Any, asyncio.Future[Any] | None]
```

Unwrap event, returning (data, future_or_none).

---

## create_perturbation

```python
def create_perturbation(data: Any, priority: int=100, loop: asyncio.AbstractEventLoop | None=None) -> Perturbation
```

Create a new perturbation with a fresh Future.

---

## await_perturbation

```python
async def await_perturbation(perturbation: Perturbation, timeout: float | None=None) -> Any
```

Await a perturbation result with optional timeout.

---

## __lt__

```python
def __lt__(self, other: 'Perturbation') -> bool
```

For priority queue ordering (higher priority first).

---

## __hash__

```python
def __hash__(self) -> int
```

Hash based on id for use in sets.

---

## __eq__

```python
def __eq__(self, other: object) -> bool
```

Equality based on identity, not values.

---

## set_result

```python
def set_result(self, result: Any) -> None
```

Set the result for the perturbation.

---

## set_exception

```python
def set_exception(self, exc: Exception) -> None
```

Set an exception for the perturbation.

---

## cancel

```python
def cancel(self, msg: str='Perturbation cancelled') -> None
```

Cancel the perturbation.

---

## is_done

```python
def is_done(self) -> bool
```

Check if the perturbation has been processed.

---

## agents.flux.pipeline

## pipeline

```python
module pipeline
```

FluxPipeline: Living Pipelines via | operator.

### Things to Know

🚨 **Critical:** Empty pipelines raise FluxPipelineError immediately in __post_init__. You cannot create FluxPipeline([]). Always have at least one stage.
  - *Verified in: `test_pipeline.py::TestPipelineValidation::test_empty_pipeline_raises`*

ℹ️ Pipeline can only be started ONCE. Re-calling start() on a running pipeline raises FluxPipelineError. Create a new pipeline or stop first. (Evidence: Structural - start() checks self._started flag)

ℹ️ stop() stops stages in REVERSE order (last to first). This allows proper draining of intermediate data. If any stage fails to stop, errors are collected and raised as a combined FluxPipelineError.
  - *Verified in: `test_pipeline.py::TestPipelineStop::test_stop_all_stages`*

ℹ️ Piping a pipeline into another pipeline MERGES them into a single pipeline, not a nested structure. (p1 | p2) has len(p1)+len(p2) stages.
  - *Verified in: `test_pipeline.py::TestPipelineCombination::test_pipeline_or_pipeline`*

---

## FluxPipeline

```python
class FluxPipeline(Generic[A, B])
```

A chain of FluxAgents forming a Living Pipeline.

---

## pipeline

```python
def pipeline(*stages: FluxAgent[Any, Any]) -> FluxPipeline[Any, Any]
```

Create a pipeline from multiple stages.

### Examples
```python
>>> p = pipeline(flux_a, flux_b, flux_c)
```
```python
>>> async for result in p.start(source):
```

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate pipeline has at least one stage.

---

## name

```python
def name(self) -> str
```

Human-readable name showing all stages.

---

## first

```python
def first(self) -> FluxAgent[A, Any]
```

First stage of the pipeline.

---

## last

```python
def last(self) -> FluxAgent[Any, B]
```

Last stage of the pipeline.

---

## is_running

```python
def is_running(self) -> bool
```

Check if any stage is running.

---

## start

```python
async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]
```

Start all stages, chaining their streams.

### Examples
```python
>>> pipeline = flux_a | flux_b | flux_c
```
```python
>>> async for result in pipeline.start(events):
```

---

## stop

```python
async def stop(self) -> None
```

Stop all stages.

---

## wait

```python
async def wait(self) -> None
```

Wait for all stages to complete.

---

## __or__

```python
def __or__(self, other: FluxAgent[Any, Any] | 'FluxPipeline[Any, Any]') -> 'FluxPipeline[A, Any]'
```

Extend pipeline: pipeline | flux_c

---

## __len__

```python
def __len__(self) -> int
```

Number of stages in the pipeline.

---

## __iter__

```python
def __iter__(self) -> Iterator[FluxAgent[Any, Any]]
```

Iterate over stages.

---

## __getitem__

```python
def __getitem__(self, index: int) -> FluxAgent[Any, Any]
```

Get stage by index.

---

## agents.flux.semantic_metrics

## semantic_metrics

```python
module semantic_metrics
```

Semantic Metrics: Purpose-oriented Database Triad health signals.

---

## HealthLevel

```python
class HealthLevel(Enum)
```

Semantic health levels.

---

## PostgresPulse

```python
class PostgresPulse
```

Raw Postgres metrics (vendor pulse).

---

## RedisPulse

```python
class RedisPulse
```

Raw Redis metrics (vendor pulse).

---

## QdrantPulse

```python
class QdrantPulse
```

Raw Qdrant metrics (vendor pulse).

---

## DurabilitySignal

```python
class DurabilitySignal
```

Is the truth safe? (Postgres health)

---

## ReflexSignal

```python
class ReflexSignal
```

How fast can I think? (Redis health)

---

## ResonanceSignal

```python
class ResonanceSignal
```

Can I remember similar things? (Qdrant health)

---

## TriadHealth

```python
class TriadHealth
```

Aggregate health of the Database Triad.

---

## SemanticMetricsCollector

```python
class SemanticMetricsCollector
```

Collects vendor pulses and transforms to semantic signals.

---

## from_postgres_pulse

```python
def from_postgres_pulse(cls, pulse: PostgresPulse) -> 'DurabilitySignal'
```

Natural transformation: PostgresPulse -> DurabilitySignal.

---

## mock

```python
def mock(cls, health: HealthLevel=HealthLevel.HEALTHY) -> 'DurabilitySignal'
```

Create a mock signal for testing.

---

## from_redis_pulse

```python
def from_redis_pulse(cls, pulse: RedisPulse) -> 'ReflexSignal'
```

Natural transformation: RedisPulse -> ReflexSignal.

---

## mock

```python
def mock(cls, health: HealthLevel=HealthLevel.HEALTHY) -> 'ReflexSignal'
```

Create a mock signal for testing.

---

## from_qdrant_pulse

```python
def from_qdrant_pulse(cls, pulse: QdrantPulse, cdc_lag_ms: float=0) -> 'ResonanceSignal'
```

Natural transformation: QdrantPulse -> ResonanceSignal.

---

## from_synapse_lag

```python
def from_synapse_lag(cls, tracker: 'CDCLagTracker', pulse: QdrantPulse) -> 'ResonanceSignal'
```

Natural transformation: (CDCLag, QdrantPulse) -> ResonanceSignal.

---

## mock

```python
def mock(cls, health: HealthLevel=HealthLevel.HEALTHY, coherency: float=0.9) -> 'ResonanceSignal'
```

Create a mock signal for testing.

---

## overall_health

```python
def overall_health(self) -> HealthLevel
```

Aggregate health (worst-of).

---

## is_coherent

```python
def is_coherent(self) -> bool
```

True if the functor stack is coherent.

---

## can_persist

```python
def can_persist(self) -> bool
```

True if we can safely persist state.

---

## can_recall

```python
def can_recall(self) -> bool
```

True if we can reliably recall cached state.

---

## can_associate

```python
def can_associate(self) -> bool
```

True if semantic search is functional.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Serialize to dictionary for API responses.

---

## mock

```python
def mock(cls, health: HealthLevel=HealthLevel.HEALTHY) -> 'TriadHealth'
```

Create a mock triad for testing.

---

## __init__

```python
def __init__(self, cdc_lag_tracker: 'CDCLagTracker | None'=None) -> None
```

Initialize the collector.

---

## update_postgres

```python
def update_postgres(self, pulse: PostgresPulse) -> DurabilitySignal
```

Update Postgres metrics and return semantic signal.

---

## update_redis

```python
def update_redis(self, pulse: RedisPulse) -> ReflexSignal
```

Update Redis metrics and return semantic signal.

---

## update_qdrant

```python
def update_qdrant(self, pulse: QdrantPulse) -> ResonanceSignal
```

Update Qdrant metrics and return semantic signal.

---

## collect

```python
def collect(self) -> TriadHealth | None
```

Collect current triad health.

---

## set_cdc_lag_tracker

```python
def set_cdc_lag_tracker(self, tracker: 'CDCLagTracker') -> None
```

Wire up the CDC lag tracker from Synapse.

---

## agents.flux.semaphore.__init__

## __init__

```python
module __init__
```

Agent Semaphores: The Rodizio Pattern.

### Examples
```python
>>> from agents.flux.semaphore import (
```
```python
>>> >>> # Agent encounters situation needing human input
```
```python
>>> token = SemaphoreToken(
```
```python
>>> return token  # NOT yield!
```
```python
>>> >>> # FluxAgent detects token, ejects to Purgatory
```

---

## agents.flux.semaphore.durable

## durable

```python
module durable
```

DurablePurgatory: Crash-resistant Purgatory with D-gent backing.

### Examples
```python
>>> from agents.d.volatile import VolatileAgent
```
```python
>>> from agents.flux.semaphore.durable import DurablePurgatory
```
```python
>>> >>> # Create with volatile memory (for testing)
```
```python
>>> memory = VolatileAgent(_state={"tokens": {}})
```
```python
>>> purgatory = DurablePurgatory(memory=memory)
```

---

## PurgatoryState

```python
class PurgatoryState(TypedDict)
```

Schema for persisted purgatory state.

---

## DurablePurgatory

```python
class DurablePurgatory(Purgatory)
```

Purgatory with D-gent backing for crash resistance.

### Examples
```python
>>> from agents.d.volatile import VolatileAgent
```
```python
>>> >>> memory = VolatileAgent(_state=DEFAULT_STATE.copy())
```
```python
>>> purgatory = DurablePurgatory(memory=memory)
```
```python
>>> >>> # Save token
```
```python
>>> await purgatory.save(token)
```

---

## create_durable_purgatory

```python
def create_durable_purgatory(memory: DataAgent[PurgatoryState] | None=None, emit_pheromone: PheromoneEmitter | None=None) -> DurablePurgatory
```

Create a DurablePurgatory with optional memory and pheromone emitter.

---

## create_and_recover_purgatory

```python
async def create_and_recover_purgatory(memory: DataAgent[PurgatoryState] | None=None, emit_pheromone: PheromoneEmitter | None=None) -> DurablePurgatory
```

Create a DurablePurgatory and recover state from memory.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Wire memory to base class.

---

## save

```python
async def save(self, token: SemaphoreToken[Any]) -> None
```

Eject an event to Purgatory (with persistence).

---

## resolve

```python
async def resolve(self, token_id: str, human_input: Any) -> ReentryContext[Any] | None
```

Resolve a pending semaphore (with persistence).

---

## cancel

```python
async def cancel(self, token_id: str) -> bool
```

Cancel a pending semaphore (with persistence).

---

## void_expired

```python
async def void_expired(self) -> list[SemaphoreToken[Any]]
```

Void all tokens whose deadlines have passed (with persistence).

---

## recover

```python
async def recover(self) -> list[SemaphoreToken[Any]]
```

Recover pending semaphores after restart.

---

## attach_memory

```python
def attach_memory(self, memory: DataAgent[PurgatoryState]) -> 'DurablePurgatory'
```

Attach a D-gent memory adapter.

---

## agents.flux.semaphore.flux_integration

## flux_integration

```python
module flux_integration
```

Flux Integration for Agent Semaphores.

### Examples
```python
>>> from agents.flux.semaphore import Purgatory, SemaphoreToken
```
```python
>>> from agents.flux.semaphore.flux_integration import (
```
```python
>>> >>> # Wrap FluxAgent with semaphore awareness
```
```python
>>> flux = SemaphoreAwareFlux(inner=my_agent, purgatory=Purgatory())
```
```python
>>> >>> # Or use the factory
```

---

## create_reentry_perturbation

```python
def create_reentry_perturbation(reentry: ReentryContext[Any], loop: asyncio.AbstractEventLoop | None=None) -> Perturbation
```

Create a Perturbation from a ReentryContext.

---

## is_reentry_context

```python
def is_reentry_context(event: Any) -> bool
```

Check if an event is a ReentryContext.

---

## SemaphoreFluxConfig

```python
class SemaphoreFluxConfig
```

Configuration for semaphore-aware flux processing.

---

## process_semaphore_result

```python
async def process_semaphore_result(token: SemaphoreToken[Any], purgatory: Purgatory, original_event: Any) -> None
```

Process a SemaphoreToken result from inner.invoke().

---

## process_reentry_event

```python
async def process_reentry_event(reentry: ReentryContext[Any], agent: 'Agent[Any, Any]') -> Any
```

Process a ReentryContext by calling agent.resume().

---

## inject_reentry

```python
async def inject_reentry(purgatory: Purgatory, flux: 'FluxAgent[Any, Any]', token_id: str, human_input: Any) -> bool
```

Resolve a semaphore and inject ReentryContext into flux.

---

## SemaphoreFluxMixin

```python
class SemaphoreFluxMixin
```

Mixin that adds semaphore awareness to FluxAgent.

### Examples
```python
>>> class SemaphoreAwareFluxAgent(SemaphoreFluxMixin, FluxAgent):
```

---

## create_semaphore_flux

```python
def create_semaphore_flux(agent: 'Agent[A, B]', purgatory: Purgatory | None=None, **flux_config: Any) -> 'FluxAgent[A, B]'
```

Create a FluxAgent with semaphore awareness.

---

## configure_semaphores

```python
def configure_semaphores(self, config: SemaphoreFluxConfig) -> None
```

Configure semaphore handling.

---

## purgatory

```python
def purgatory(self) -> Purgatory
```

Get the Purgatory instance.

---

## agents.flux.semaphore.mixin

## mixin

```python
module mixin
```

SemaphoreMixin: Protocol for agents that can yield semaphores.

---

## SemaphoreCapable

```python
class SemaphoreCapable(Protocol[B])
```

Protocol for agents that can yield semaphores.

### Examples
```python
>>> class ReviewAgent(SemaphoreCapable[Document, Review]):
```

---

## SemaphoreMixin

```python
class SemaphoreMixin(Generic[A, B, S])
```

Mixin providing semaphore utilities for agents.

### Examples
```python
>>> class MyAgent(SemaphoreMixin[Input, Output, MyState]):
```

---

## is_semaphore_token

```python
def is_semaphore_token(result: Any) -> bool
```

Check if a result is a SemaphoreToken.

---

## is_semaphore_capable

```python
def is_semaphore_capable(agent: Any) -> bool
```

Check if an agent implements SemaphoreCapable.

---

## resume

```python
async def resume(self, frozen_state: bytes, human_input: Any) -> B
```

Resume processing after human provides context.

---

## create_semaphore

```python
def create_semaphore(self, reason: Any, state: S, original_event: Any=None, prompt: str='', options: list[str] | None=None, severity: str='info', **kwargs: Any) -> SemaphoreToken[Any]
```

Create a SemaphoreToken with serialized state.

---

## freeze_state

```python
def freeze_state(self, state: S) -> bytes
```

Serialize state for storage in SemaphoreToken.

---

## restore_state

```python
def restore_state(self, frozen_state: bytes) -> S
```

Deserialize state from ReentryContext.

---

## process_reentry

```python
def process_reentry(self, reentry: ReentryContext[Any]) -> tuple[S, Any]
```

Process a ReentryContext into (state, human_input).

---

## agents.flux.semaphore.purgatory

## purgatory

```python
module purgatory
```

Purgatory: The waiting room for ejected events.

---

## Purgatory

```python
class Purgatory
```

The waiting room for ejected events.

### Examples
```python
>>> purgatory = Purgatory()
```
```python
>>> >>> # Agent returns SemaphoreToken, FluxAgent detects and ejects
```
```python
>>> await purgatory.save(token)
```
```python
>>> >>> # Stream continues, human eventually resolves
```
```python
>>> reentry = await purgatory.resolve(token.id, human_input)
```

---

## save

```python
async def save(self, token: SemaphoreToken[Any]) -> None
```

Eject an event to Purgatory.

---

## resolve

```python
async def resolve(self, token_id: str, human_input: Any) -> ReentryContext[Any] | None
```

Resolve a pending semaphore with human-provided context.

### Examples
```python
>>> reentry = await purgatory.resolve("sem-abc12345", "Approve")
```
```python
>>> if reentry:
```

---

## cancel

```python
async def cancel(self, token_id: str) -> bool
```

Cancel a pending semaphore. Event is discarded.

---

## get

```python
def get(self, token_id: str) -> SemaphoreToken[Any] | None
```

Get a token by ID (any state).

---

## list_pending

```python
def list_pending(self) -> list[SemaphoreToken[Any]]
```

List all pending (unresolved) semaphores.

---

## list_all

```python
def list_all(self) -> list[SemaphoreToken[Any]]
```

List all semaphores (any state).

---

## recover

```python
async def recover(self) -> list[SemaphoreToken[Any]]
```

Recover pending semaphores after restart.

---

## clear

```python
def clear(self) -> None
```

Clear all tokens (for testing).

---

## void_expired

```python
async def void_expired(self) -> list[SemaphoreToken[Any]]
```

Void all tokens whose deadlines have passed.

---

## agents.flux.semaphore.reason

## reason

```python
module reason
```

SemaphoreReason: Why the agent yielded to human.

---

## SemaphoreReason

```python
class SemaphoreReason(Enum)
```

Why the agent yielded to human.

---

## agents.flux.semaphore.reentry

## reentry

```python
module reentry
```

ReentryContext: The Green Card.

---

## ReentryContext

```python
class ReentryContext(Generic[R])
```

The Green Card. Injected back into Flux as high-priority Perturbation.

### Examples
```python
>>> reentry = ReentryContext(
```
```python
>>> # Inject as perturbation
```
```python
>>> perturbation = create_perturbation(reentry, priority=200)
```
```python
>>> await flux_agent._perturbation_queue.put(perturbation)
```

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate reentry context.

---

## agents.flux.semaphore.token

## token

```python
module token
```

SemaphoreToken: The Red Card.

---

## SemaphoreToken

```python
class SemaphoreToken(Generic[R])
```

The Red Card. Return this from an agent to flip red.

### Examples
```python
>>> token = SemaphoreToken(
```
```python
>>> return token  # NOT yield!
```

---

## is_pending

```python
def is_pending(self) -> bool
```

Check if token is still awaiting resolution.

---

## is_resolved

```python
def is_resolved(self) -> bool
```

Check if token was resolved (not cancelled).

---

## is_cancelled

```python
def is_cancelled(self) -> bool
```

Check if token was cancelled.

---

## __hash__

```python
def __hash__(self) -> int
```

Hash based on id for use in sets and dict keys.

---

## __eq__

```python
def __eq__(self, other: object) -> bool
```

Equality based on id, not all fields.

---

## is_voided

```python
def is_voided(self) -> bool
```

Check if token was voided (deadline expired).

---

## check_deadline

```python
def check_deadline(self) -> bool
```

Check if deadline has passed and void if so.

---

## to_json

```python
def to_json(self) -> dict[str, Any]
```

Serialize token to JSON-compatible dict.

---

## from_json

```python
def from_json(cls, data: dict[str, Any]) -> 'SemaphoreToken[Any]'
```

Deserialize token from JSON dict.

---

## agents.flux.sources.__init__

## __init__

```python
module __init__
```

Flux Sources: Event-driven stream generators.

---

## agents.flux.sources.base

## base

```python
module base
```

Base protocols and types for flux sources.

### Things to Know

ℹ️ Sources should be EVENT-DRIVEN, not timer-driven. If your __anext__() uses asyncio.sleep() in a loop to poll, you're doing it wrong. Await the actual event (file watcher, message queue, etc.) instead.
  - *Verified in: `Structural - module docstring emphasizes event-driven`*

ℹ️ close() is NOT async. If your source needs async cleanup, do it in __aexit__ (the async context manager exit) instead.
  - *Verified in: `Structural - close signature is sync`*

---

## SourceProtocol

```python
class SourceProtocol(Protocol[T_co])
```

Protocol for objects that can produce async streams.

---

## Source

```python
class Source(AsyncIterator[T])
```

Base class for custom flux sources.

---

## subscribe

```python
def subscribe(self) -> AsyncIterator[T_co]
```

Subscribe to events from this source.

---

## __aiter__

```python
def __aiter__(self) -> AsyncIterator[T]
```

Return self as the async iterator.

---

## __anext__

```python
async def __anext__(self) -> T
```

Get the next event from the source.

---

## close

```python
def close(self) -> None
```

Close the source and release any resources.

---

## __aenter__

```python
async def __aenter__(self) -> 'Source[T]'
```

Context manager entry.

---

## __aexit__

```python
async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object) -> None
```

Context manager exit - closes the source.

---

## agents.flux.sources.events

## events

```python
module events
```

Event-driven sources (NOT timer-driven).

---

## from_events

```python
async def from_events(bus: SourceProtocol[T]) -> AsyncIterator[T]
```

Yield events as they occur from an event bus.

### Examples
```python
>>> async for event in from_events(my_bus):
```

---

## from_stream

```python
async def from_stream(stream: AsyncIterator[T]) -> AsyncIterator[T]
```

Pass-through adapter for any async iterator.

### Examples
```python
>>> async def my_generator():
```
```python
>>> async for item in from_stream(my_generator()):
```

---

## from_iterable

```python
async def from_iterable(items: Iterable[T]) -> AsyncIterator[T]
```

Create an async iterator from a synchronous iterable.

### Examples
```python
>>> async for item in from_iterable([1, 2, 3]):
```

---

## from_queue

```python
async def from_queue(queue: Any) -> AsyncIterator[Any]
```

Yield items from an asyncio.Queue until a sentinel is received.

---

## empty

```python
async def empty() -> AsyncIterator[Any]
```

Create an empty async iterator.

---

## single

```python
async def single(value: T) -> AsyncIterator[T]
```

Create a source that emits a single value then completes.

### Examples
```python
>>> async for item in single(42):
```

---

## repeat

```python
async def repeat(value: T, times: int | None=None) -> AsyncIterator[T]
```

Create a source that emits a value repeatedly.

### Examples
```python
>>> async for item in repeat("hello", 3):
```

---

## range_source

```python
async def range_source(start: int, stop: int, step: int=1) -> AsyncIterator[int]
```

Create a source that emits integers in a range.

### Examples
```python
>>> async for i in range_source(0, 5):
```

---

## agents.flux.sources.merged

## merged

```python
module merged
```

Stream combinators for flux sources.

---

## merged

```python
async def merged(*sources: AsyncIterator[T]) -> AsyncIterator[T]
```

Merge multiple sources into a single stream.

### Examples
```python
>>> async for item in merged(source_a, source_b, source_c):
```

---

## filtered

```python
async def filtered(source: AsyncIterator[T], predicate: Callable[[T], bool] | Callable[[T], Awaitable[bool]]) -> AsyncIterator[T]
```

Filter items from a source based on a predicate.

### Examples
```python
>>> async for n in filtered(numbers(), lambda x: x % 2 == 0):
```

---

## mapped

```python
async def mapped(source: AsyncIterator[T], transform: Callable[[T], U] | Callable[[T], Awaitable[U]]) -> AsyncIterator[U]
```

Transform items from a source.

### Examples
```python
>>> async for s in mapped(numbers(), str):
```

---

## batched

```python
async def batched(source: AsyncIterator[T], size: int, timeout: float | None=None) -> AsyncIterator[list[T]]
```

Group items into batches.

### Examples
```python
>>> async for batch in batched(items(), 10, timeout=1.0):
```

---

## debounced

```python
async def debounced(source: AsyncIterator[T], delay: float) -> AsyncIterator[T]
```

Emit item only after delay with no new items.

### Examples
```python
>>> # Only emit after 0.5s of no new input
```
```python
>>> async for value in debounced(keystrokes(), 0.5):
```

---

## take

```python
async def take(source: AsyncIterator[T], count: int) -> AsyncIterator[T]
```

Take at most count items from source.

### Examples
```python
>>> async for item in take(infinite_source(), 10):
```

---

## skip

```python
async def skip(source: AsyncIterator[T], count: int) -> AsyncIterator[T]
```

Skip the first count items from source.

### Examples
```python
>>> async for item in skip(source(), 5):
```

---

## take_while

```python
async def take_while(source: AsyncIterator[T], predicate: Callable[[T], bool]) -> AsyncIterator[T]
```

Take items while predicate is True.

### Examples
```python
>>> async for n in take_while(numbers(), lambda x: x < 10):
```

---

## skip_while

```python
async def skip_while(source: AsyncIterator[T], predicate: Callable[[T], bool]) -> AsyncIterator[T]
```

Skip items while predicate is True.

### Examples
```python
>>> async for n in skip_while(numbers(), lambda x: x < 5):
```

---

## enumerate_source

```python
async def enumerate_source(source: AsyncIterator[T], start: int=0) -> AsyncIterator[tuple[int, T]]
```

Add index to each item.

### Examples
```python
>>> async for i, item in enumerate_source(items()):
```

---

## get_next

```python
async def get_next(index: int, it: AsyncIterator[T]) -> tuple[int, T]
```

Get next item from iterator, returning (index, item).

---

## agents.flux.sources.outbox

## outbox

```python
module outbox
```

Outbox Source: Polls Postgres outbox table for CDC events.

---

## AsyncDatabaseConnection

```python
class AsyncDatabaseConnection(Protocol)
```

Protocol for async database connections.

---

## AsyncConnectionPool

```python
class AsyncConnectionPool(Protocol)
```

Protocol for async connection pools.

---

## OutboxConfig

```python
class OutboxConfig
```

Configuration for the OutboxSource.

---

## MockConnection

```python
class MockConnection
```

Mock database connection for testing without a real database.

---

## MockConnectionPool

```python
class MockConnectionPool
```

Mock connection pool that returns a MockConnection.

---

## OutboxSource

```python
class OutboxSource(Source[ChangeEvent])
```

Source that polls the Postgres outbox table for CDC events.

### Examples
```python
>>> pool = await asyncpg.create_pool(dsn)
```
```python
>>> source = OutboxSource(pool)
```
```python
>>> async for event in source:
```
```python
>>> mock_conn = MockConnection(pending_events=[...])
```
```python
>>> pool = MockConnectionPool(mock_conn)
```

---

## poll_outbox_events

```python
async def poll_outbox_events(pool: AsyncConnectionPool | MockConnectionPool, config: OutboxConfig | None=None, synapse_callback: Any | None=None) -> AsyncIterator[ChangeEvent]
```

Convenience function to poll outbox and optionally auto-acknowledge.

---

## fetch

```python
async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]
```

Execute query and return all rows.

---

## execute

```python
async def execute(self, query: str, *args: Any) -> None
```

Execute query without returning rows.

---

## acquire

```python
async def acquire(self) -> AsyncDatabaseConnection
```

Acquire a connection from the pool.

---

## release

```python
async def release(self, conn: AsyncDatabaseConnection) -> None
```

Release a connection back to the pool.

---

## fetch

```python
async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]
```

Return pre-configured events.

---

## execute

```python
async def execute(self, query: str, *args: Any) -> None
```

Record the execute call.

---

## acquire

```python
async def acquire(self) -> MockConnection
```

Return the mock connection.

---

## release

```python
async def release(self, conn: AsyncDatabaseConnection | MockConnection) -> None
```

No-op for mock.

---

## __init__

```python
def __init__(self, pool: AsyncConnectionPool | MockConnectionPool, config: OutboxConfig | None=None) -> None
```

Initialize the OutboxSource.

---

## __anext__

```python
async def __anext__(self) -> ChangeEvent
```

Get the next ChangeEvent from the outbox.

---

## acknowledge

```python
async def acknowledge(self, sequence_id: int | None) -> None
```

Mark an event as processed.

---

## acknowledge_batch

```python
async def acknowledge_batch(self, sequence_ids: list[int]) -> None
```

Mark multiple events as processed.

---

## close

```python
def close(self) -> None
```

Stop polling the outbox.

---

## is_stopped

```python
def is_stopped(self) -> bool
```

True if the source has been stopped.

---

## agents.flux.sources.periodic

## periodic

```python
module periodic
```

Periodic source (timer-based).

---

## periodic

```python
async def periodic(interval: float) -> AsyncIterator[float]
```

Emit timestamps at regular intervals.

### Examples
```python
>>> async for ts in periodic(1.0):
```

---

## countdown

```python
async def countdown(count: int, interval: float=1.0) -> AsyncIterator[int]
```

Emit countdown from count to 0.

### Examples
```python
>>> async for n in countdown(5):
```

---

## tick

```python
async def tick(interval: float, count: int | None=None) -> AsyncIterator[int]
```

Emit sequential tick numbers at regular intervals.

### Examples
```python
>>> async for n in tick(0.5, count=3):
```

---

## delayed

```python
async def delayed(value: T, delay: float) -> AsyncIterator[T]
```

Emit a single value after a delay.

### Examples
```python
>>> async for v in delayed("ready", 2.0):
```

---

## timeout_source

```python
async def timeout_source(duration: float) -> AsyncIterator[None]
```

Create a source that emits nothing for a duration, then completes.

### Examples
```python
>>> # Use with merged() for timeout patterns
```
```python
>>> async for item in merged(data_source(), timeout_source(5.0)):
```

---

## agents.flux.state

## state

```python
module state
```

Flux lifecycle states.

### Things to Know

ℹ️ COLLAPSED is TERMINAL - no transitions out. Unlike STOPPED (which allows restart via start()), COLLAPSED requires explicit reset() to return to DORMANT. Entropy exhaustion = permanent death.
  - *Verified in: `can_transition_to returns empty set for COLLAPSED`*

ℹ️ allows_perturbation() is only True for FLOWING state. DORMANT uses direct invoke (not perturbation), PERTURBED rejects (already handling one), and terminal states reject entirely. Check state first.
  - *Verified in: `Structural - allows_perturbation implementation`*

ℹ️ DRAINING is a transient state between source exhaustion and STOPPED. is_processing() returns True for DRAINING because output buffer may still have items. Wait for STOPPED before assuming completion.
  - *Verified in: `Structural - is_processing includes DRAINING`*

---

## FluxState

```python
class FluxState(Enum)
```

Lifecycle states for FluxAgent.

---

## can_start

```python
def can_start(self) -> bool
```

Check if flux can transition to FLOWING from this state.

---

## is_processing

```python
def is_processing(self) -> bool
```

Check if flux is actively processing events.

---

## is_terminal

```python
def is_terminal(self) -> bool
```

Check if flux is in a terminal state.

---

## allows_perturbation

```python
def allows_perturbation(self) -> bool
```

Check if invoke() can be accepted as a perturbation.

---

## can_transition_to

```python
def can_transition_to(self, target: 'FluxState') -> bool
```

Check if transition to target state is valid.

---

## agents.flux.synapse

## synapse

```python
module synapse
```

Synapse: CDC Flux agent that maintains derived views.

---

## ChangeOperation

```python
class ChangeOperation(Enum)
```

Database change operations.

---

## ChangeEvent

```python
class ChangeEvent
```

A change in the Anchor (Postgres).

---

## SyncTarget

```python
class SyncTarget(Enum)
```

Target systems for sync operations.

---

## SyncOperation

```python
class SyncOperation(Enum)
```

Types of sync operations.

---

## SyncResult

```python
class SyncResult
```

Result of syncing to a derived view.

---

## EmbeddingProvider

```python
class EmbeddingProvider(Protocol)
```

Protocol for computing embeddings.

---

## VectorStore

```python
class VectorStore(Protocol)
```

Protocol for vector database operations.

---

## CacheStore

```python
class CacheStore(Protocol)
```

Protocol for cache operations.

---

## RetryConfig

```python
class RetryConfig
```

Configuration for retry behavior with exponential backoff.

---

## SynapseConfig

```python
class SynapseConfig
```

Configuration for the Synapse CDC agent.

---

## SynapseMetrics

```python
class SynapseMetrics
```

Metrics for monitoring the CDC pipeline.

---

## SynapseProcessor

```python
class SynapseProcessor(Agent[ChangeEvent, list[SyncResult]])
```

Inner agent that processes CDC events.

---

## RobustSynapseProcessor

```python
class RobustSynapseProcessor(Agent[ChangeEvent, list[SyncResult]])
```

Enhanced Synapse processor with robustification features.

---

## create_synapse

```python
def create_synapse(config: SynapseConfig | None=None, embedding_provider: EmbeddingProvider | None=None, vector_store: VectorStore | None=None, cache_store: CacheStore | None=None, flux_config: FluxConfig | None=None) -> FluxAgent[ChangeEvent, list[SyncResult]]
```

Create a Synapse FluxAgent.

### Examples
```python
>>> synapse = create_synapse(
```
```python
>>> async for results in synapse.start(outbox_events):
```

---

## create_robust_synapse

```python
def create_robust_synapse(config: SynapseConfig | None=None, embedding_provider: EmbeddingProvider | None=None, vector_store: VectorStore | None=None, cache_store: CacheStore | None=None, flux_config: FluxConfig | None=None, metrics: SynapseMetrics | None=None) -> FluxAgent[ChangeEvent, list[SyncResult]]
```

Create a robust Synapse FluxAgent with retry, circuit breaker, and DLQ.

### Examples
```python
>>> config = SynapseConfig(
```
```python
>>> synapse = create_robust_synapse(
```
```python
>>> async for results in synapse.start(outbox_events):
```
```python
>>> # Check metrics
```
```python
>>> print(synapse._inner.metrics.to_prometheus())
```

---

## OutboxConfig

```python
class OutboxConfig
```

Configuration for polling the outbox table.

---

## poll_outbox

```python
async def poll_outbox(fetch_events: AsyncIterator[list[ChangeEvent]]) -> AsyncIterator[ChangeEvent]
```

Convert batched outbox fetches into individual ChangeEvents.

### Examples
```python
>>> async def fetch_from_db():
```
```python
>>> >>> async for event in poll_outbox(fetch_from_db()):
```

---

## CDCLagTracker

```python
class CDCLagTracker
```

Tracks CDC lag for monitoring.

---

## insert

```python
def insert(cls, table: str, row_id: str, data: dict[str, Any], sequence_id: int | None=None) -> 'ChangeEvent'
```

Create an INSERT event.

---

## update

```python
def update(cls, table: str, row_id: str, data: dict[str, Any], sequence_id: int | None=None) -> 'ChangeEvent'
```

Create an UPDATE event.

---

## delete

```python
def delete(cls, table: str, row_id: str, sequence_id: int | None=None) -> 'ChangeEvent'
```

Create a DELETE event.

---

## success_upsert

```python
def success_upsert(cls, target: SyncTarget, lag_ms: float, sequence: int | None=None) -> 'SyncResult'
```

Create a successful upsert result.

---

## success_delete

```python
def success_delete(cls, target: SyncTarget, lag_ms: float, sequence: int | None=None) -> 'SyncResult'
```

Create a successful delete result.

---

## failed

```python
def failed(cls, target: SyncTarget, operation: SyncOperation, error: str, sequence: int | None=None) -> 'SyncResult'
```

Create a failed sync result.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Compute embedding vector for text.

---

## upsert

```python
async def upsert(self, collection: str, id: str, vector: list[float], payload: dict[str, Any]) -> None
```

Upsert a vector with payload.

---

## delete

```python
async def delete(self, collection: str, id: str) -> None
```

Delete a vector by ID.

---

## invalidate

```python
async def invalidate(self, key: str) -> None
```

Invalidate a cache key.

---

## delay_for_attempt

```python
def delay_for_attempt(self, attempt: int) -> float
```

Calculate delay in seconds for given attempt (0-indexed).

---

## record_success

```python
def record_success(self, lag_ms: float) -> None
```

Record a successful sync.

---

## record_failure

```python
def record_failure(self) -> None
```

Record a failed sync.

---

## record_retry

```python
def record_retry(self) -> None
```

Record a retry attempt.

---

## record_dlq

```python
def record_dlq(self) -> None
```

Record event sent to DLQ.

---

## set_circuit_state

```python
def set_circuit_state(self, state: str) -> None
```

Update circuit breaker state.

---

## to_prometheus

```python
def to_prometheus(self) -> str
```

Export as Prometheus text format.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Export as dictionary for API responses.

---

## __init__

```python
def __init__(self, config: SynapseConfig, embedding_provider: EmbeddingProvider | None=None, vector_store: VectorStore | None=None, cache_store: CacheStore | None=None) -> None
```

Initialize the Synapse processor.

---

## invoke

```python
async def invoke(self, event: ChangeEvent) -> list[SyncResult]
```

Process a single CDC event.

---

## __init__

```python
def __init__(self, config: SynapseConfig, embedding_provider: EmbeddingProvider | None=None, vector_store: VectorStore | None=None, cache_store: CacheStore | None=None, metrics: SynapseMetrics | None=None) -> None
```

Initialize the robust Synapse processor.

---

## metrics

```python
def metrics(self) -> SynapseMetrics
```

Get current metrics.

---

## invoke

```python
async def invoke(self, event: ChangeEvent) -> list[SyncResult]
```

Process a CDC event with retry and circuit breaker.

---

## record

```python
def record(self, lag_ms: float) -> None
```

Record a lag sample.

---

## avg_lag_ms

```python
def avg_lag_ms(self) -> float
```

Average lag in milliseconds.

---

## max_lag_ms

```python
def max_lag_ms(self) -> float
```

Maximum lag in milliseconds.

---

## coherency

```python
def coherency(self) -> float
```

Coherency with truth (0-1).

---

## agents.flux.synapse_runner

## synapse_runner

```python
module synapse_runner
```

Synapse CDC Runner - Kubernetes CronJob/Deployment entrypoint.

---

## RunnerConfig

```python
class RunnerConfig
```

Configuration loaded from environment.

---

## PostgresClient

```python
class PostgresClient
```

PostgreSQL client for outbox polling.

---

## QdrantClient

```python
class QdrantClient
```

Qdrant client for vector operations.

---

## EmbeddingClient

```python
class EmbeddingClient
```

Embedding provider client.

---

## SynapseRunner

```python
class SynapseRunner
```

Main runner that orchestrates CDC processing.

---

## main

```python
def main() -> None
```

Entry point.

---

## from_env

```python
def from_env(cls) -> 'RunnerConfig'
```

Load configuration from environment variables.

---

## connect

```python
async def connect(self) -> None
```

Connect to PostgreSQL.

---

## close

```python
async def close(self) -> None
```

Close connection pool.

---

## fetch_pending_events

```python
async def fetch_pending_events(self, batch_size: int) -> list[dict[str, Any]]
```

Fetch unprocessed outbox events.

---

## mark_processed

```python
async def mark_processed(self, event_ids: list[int]) -> None
```

Mark events as processed.

---

## get_outbox_stats

```python
async def get_outbox_stats(self) -> dict[str, Any]
```

Get outbox statistics for monitoring.

---

## connect

```python
async def connect(self) -> None
```

Connect to Qdrant.

---

## upsert

```python
async def upsert(self, id: str, vector: list[float], payload: dict[str, Any]) -> None
```

Upsert vector to collection.

---

## delete

```python
async def delete(self, id: str) -> None
```

Delete vector from collection.

---

## get_collection_info

```python
async def get_collection_info(self) -> dict[str, Any]
```

Get collection info for monitoring.

---

## connect

```python
async def connect(self) -> None
```

Initialize embedding client.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Compute embedding for text.

---

## connect

```python
async def connect(self) -> None
```

Connect to all services.

---

## close

```python
async def close(self) -> None
```

Close all connections.

---

## process_batch

```python
async def process_batch(self) -> int
```

Process a single batch of events. Returns count processed.

---

## run_once

```python
async def run_once(self) -> None
```

Run a single batch and exit.

---

## run_continuous

```python
async def run_continuous(self) -> None
```

Run continuously, polling for events.

---

## agents.flux.terrarium_events

## terrarium_events

```python
module terrarium_events
```

Terrarium events for Flux agent widget updates.

---

## EventType

```python
class EventType(str, Enum)
```

Types of events that flow through the Mirror.

---

## TerriumEvent

```python
class TerriumEvent
```

Event for I-gent widget updates.

---

## SemaphoreEvent

```python
class SemaphoreEvent
```

Event emitted when a semaphore is ejected to Purgatory.

---

## make_result_event

```python
def make_result_event(agent_id: str, result: Any, state: str | None=None, pressure: float=0.0, flow: float=0.0, temperature: float=0.0) -> TerriumEvent
```

Create a result event.

---

## make_error_event

```python
def make_error_event(agent_id: str, error: str, error_type: str | None=None) -> TerriumEvent
```

Create an error event.

---

## make_metabolism_event

```python
def make_metabolism_event(agent_id: str, pressure: float, flow: float, temperature: float, state: str) -> TerriumEvent
```

Create a metabolism update event.

---

## as_dict

```python
def as_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dict.

---

## as_terrium_event

```python
def as_terrium_event(self) -> TerriumEvent
```

Convert to TerriumEvent for broadcasting.

---

## agents.k.__init__

## __init__

```python
module __init__
```

K-gent: Kent Simulacra - The Digital Soul (Governance Functor)

---

## agents.k.audit

## audit

```python
module audit
```

K-gent Audit Trail: Logging and querying mediation decisions.

---

## AuditEntry

```python
class AuditEntry
```

A single audit trail entry.

---

## AuditTrail

```python
class AuditTrail
```

Audit trail for K-gent mediation decisions.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for JSON serialization.

---

## from_dict

```python
def from_dict(cls, d: dict[str, Any]) -> 'AuditEntry'
```

Create from dictionary.

---

## to_audit_string

```python
def to_audit_string(self) -> str
```

Convert to human-readable audit string.

---

## to_short_string

```python
def to_short_string(self) -> str
```

Short one-line summary.

---

## __init__

```python
def __init__(self, storage_path: Optional[Path]=None, max_entries: int=10000)
```

Initialize audit trail.

---

## log_file

```python
def log_file(self) -> Path
```

Path to the audit log file.

---

## log

```python
def log(self, entry: AuditEntry) -> None
```

Log an audit entry.

---

## recent

```python
def recent(self, limit: int=10) -> list[AuditEntry]
```

Get recent audit entries.

---

## all_entries

```python
def all_entries(self) -> list[AuditEntry]
```

Get all audit entries.

---

## filter_by_action

```python
def filter_by_action(self, action: str) -> list[AuditEntry]
```

Filter entries by action type.

---

## filter_by_date

```python
def filter_by_date(self, start: Optional[datetime]=None, end: Optional[datetime]=None) -> list[AuditEntry]
```

Filter entries by date range.

---

## summary

```python
def summary(self) -> dict[str, Any]
```

Get summary statistics of the audit trail.

---

## format_recent

```python
def format_recent(self, limit: int=10) -> str
```

Format recent entries for display.

---

## format_summary

```python
def format_summary(self) -> str
```

Format summary for display.

---

## clear

```python
def clear(self) -> None
```

Clear the audit trail (for testing).

---

## agents.k.eigenvectors

## eigenvectors

```python
module eigenvectors
```

K-gent Eigenvectors: Personality coordinates in the manifold.

---

## EigenvectorCoordinate

```python
class EigenvectorCoordinate
```

A single eigenvector coordinate.

---

## KentEigenvectors

```python
class KentEigenvectors
```

Kent's six personality eigenvectors.

---

## get_eigenvectors

```python
def get_eigenvectors() -> KentEigenvectors
```

Get Kent's personality eigenvectors.

---

## eigenvector_context

```python
def eigenvector_context() -> str
```

Get eigenvector context for prompts.

---

## get_challenge_style

```python
def get_challenge_style(eigenvectors: KentEigenvectors) -> str
```

Generate challenge style guidance based on eigenvector coordinates.

---

## get_dialectical_prompt

```python
def get_dialectical_prompt(eigenvectors: KentEigenvectors, user_thesis: str) -> str
```

Generate a dialectical challenge prompt based on eigenvectors.

---

## description

```python
def description(self) -> str
```

Human-readable description of this coordinate.

---

## to_prompt_fragment

```python
def to_prompt_fragment(self) -> str
```

Generate prompt fragment for this eigenvector.

---

## all_eigenvectors

```python
def all_eigenvectors(self) -> list[EigenvectorCoordinate]
```

Return all six eigenvectors.

---

## to_dict

```python
def to_dict(self) -> dict[str, float]
```

Export as simple dictionary.

---

## to_full_dict

```python
def to_full_dict(self) -> dict[str, dict[str, Any]]
```

Export full eigenvector data for persistence.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'KentEigenvectors'
```

Restore eigenvectors from persisted data.

---

## modify

```python
def modify(self, name: str, delta: float=0.0, absolute: float | None=None, confidence_delta: float=0.0) -> bool
```

Modify an eigenvector coordinate.

---

## to_context_prompt

```python
def to_context_prompt(self) -> str
```

Generate prompt fragment describing Kent's personality coordinates.

---

## average_confidence

```python
def average_confidence(self) -> float
```

Average confidence across all eigenvectors.

---

## to_system_prompt_section

```python
def to_system_prompt_section(self) -> str
```

Generate the full personality section for K-gent system prompts.

---

## agents.k.events

## events

```python
module events
```

SoulEvent: Event types for K-gent streaming.

---

## SoulEventType

```python
class SoulEventType(str, Enum)
```

Types of events in the K-gent stream.

---

## SoulEvent

```python
class SoulEvent
```

A single event in the K-gent stream.

---

## dialogue_start_event

```python
def dialogue_start_event(mode: str, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DIALOGUE_START event.

---

## dialogue_turn_event

```python
def dialogue_turn_event(message: str, response: Optional[str]=None, mode: Optional[str]=None, is_request: bool=True, correlation_id: Optional[str]=None, soul_state: Optional[dict[str, Any]]=None) -> SoulEvent
```

Create a DIALOGUE_TURN event.

---

## dialogue_end_event

```python
def dialogue_end_event(reason: str='completed', correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DIALOGUE_END event.

---

## mode_change_event

```python
def mode_change_event(from_mode: str, to_mode: str, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a MODE_CHANGE event.

---

## intercept_request_event

```python
def intercept_request_event(token_id: str, prompt: str, severity: str='info', options: Optional[list[str]]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create an INTERCEPT_REQUEST event.

---

## intercept_result_event

```python
def intercept_result_event(token_id: str, handled: bool, recommendation: Optional[str]=None, confidence: float=0.0, reasoning: str='', correlation_id: Optional[str]=None, soul_state: Optional[dict[str, Any]]=None) -> SoulEvent
```

Create an INTERCEPT_RESULT event.

---

## eigenvector_probe_event

```python
def eigenvector_probe_event(eigenvectors: dict[str, Any], correlation_id: Optional[str]=None) -> SoulEvent
```

Create an EIGENVECTOR_PROBE event (introspection).

---

## pulse_event

```python
def pulse_event(interactions_count: int=0, tokens_used_session: int=0, active_mode: str='reflect', is_healthy: bool=True, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a PULSE event (vitality signal).

---

## state_snapshot_event

```python
def state_snapshot_event(state: dict[str, Any], correlation_id: Optional[str]=None) -> SoulEvent
```

Create a STATE_SNAPSHOT event.

---

## error_event

```python
def error_event(error: str, error_type: Optional[str]=None, original_event_type: Optional[str]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create an ERROR event.

---

## ping_event

```python
def ping_event() -> SoulEvent
```

Create a PING event (keep-alive).

---

## thought_event

```python
def thought_event(content: str, depth: int=1, triggered_by: Optional[str]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a THOUGHT event (internal monologue / rumination).

---

## feeling_event

```python
def feeling_event(valence: str, intensity: float=0.5, cause: Optional[str]=None, eigenvector_shift: Optional[dict[str, float]]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a FEELING event (emotional state shift).

---

## observation_event

```python
def observation_event(pattern: str, confidence: float=0.5, domain: str='general', evidence: Optional[list[str]]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create an OBSERVATION event (pattern noticed in environment).

---

## self_challenge_event

```python
def self_challenge_event(thesis: str, antithesis: str, synthesis: Optional[str]=None, eigenvector: Optional[str]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a SELF_CHALLENGE event (self-initiated dialectic).

---

## perturbation_event

```python
def perturbation_event(source: str, intensity: float=0.5, data: Optional[dict[str, Any]]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a PERTURBATION event (environmental stimulus).

---

## gratitude_event

```python
def gratitude_event(for_what: str, to_whom: Optional[str]=None, depth: int=1, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a GRATITUDE event (tithe to entropy).

---

## dream_start_event

```python
def dream_start_event(interactions_count: int, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DREAM_START event.

---

## dream_pattern_event

```python
def dream_pattern_event(pattern: str, occurrences: int, promoted: bool=False, maturity: str='seed', correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DREAM_PATTERN event.

---

## dream_insight_event

```python
def dream_insight_event(eigenvector: str, delta: float, old_confidence: float, new_confidence: float, evidence: Optional[list[str]]=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DREAM_INSIGHT event.

---

## dream_end_event

```python
def dream_end_event(patterns_discovered: int, patterns_promoted: int, patterns_composted: int, eigenvector_changes: int, insights: Optional[list[str]]=None, was_dry_run: bool=False, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DREAM_END event.

---

## from_dialogue_output

```python
def from_dialogue_output(output: 'SoulDialogueOutput', original_message: str, soul_state: Optional['SoulState']=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create a DIALOGUE_TURN event from SoulDialogueOutput.

---

## from_intercept_result

```python
def from_intercept_result(result: 'InterceptResult', token_id: str, soul_state: Optional['SoulState']=None, correlation_id: Optional[str]=None) -> SoulEvent
```

Create an INTERCEPT_RESULT event from InterceptResult.

---

## is_dialogue_event

```python
def is_dialogue_event(event: SoulEvent) -> bool
```

Check if event is a dialogue event.

---

## is_intercept_event

```python
def is_intercept_event(event: SoulEvent) -> bool
```

Check if event is an intercept event.

---

## is_system_event

```python
def is_system_event(event: SoulEvent) -> bool
```

Check if event is a system event (pulse, ping, snapshot).

---

## is_request_event

```python
def is_request_event(event: SoulEvent) -> bool
```

Check if event requires processing (vs. response/status).

---

## is_ambient_event

```python
def is_ambient_event(event: SoulEvent) -> bool
```

Check if event is an ambient event (soul present, not invoked).

---

## is_external_event

```python
def is_external_event(event: SoulEvent) -> bool
```

Check if event originated from external source.

---

## is_dream_event

```python
def is_dream_event(event: SoulEvent) -> bool
```

Check if event is a dream/hypnagogia event.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dict.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'SoulEvent'
```

Create a SoulEvent from a dict.

---

## agents.k.evolution

## evolution

```python
module evolution
```

K-gent Evolution: How the persona changes over time.

---

## ConfidenceLevel

```python
class ConfidenceLevel(Enum)
```

Confidence levels for preferences.

---

## ChangeSource

```python
class ChangeSource(Enum)
```

Source of preference/pattern changes.

---

## EvolutionInput

```python
class EvolutionInput
```

Input for persona evolution.

---

## EvolutionOutput

```python
class EvolutionOutput
```

Output from persona evolution.

---

## EvolutionHandler

```python
class EvolutionHandler(Protocol)
```

Protocol for handlers that process specific evolution triggers.

---

## ConfidenceTracker

```python
class ConfidenceTracker
```

Track confidence for a single preference/pattern.

---

## ExplicitUpdateHandler

```python
class ExplicitUpdateHandler
```

Handler for explicit user updates.

---

## ObservationHandler

```python
class ObservationHandler
```

Handler for observed patterns.

---

## ContradictionHandler

```python
class ContradictionHandler
```

Handler for contradictions between behavior and stated preferences.

---

## ForgetHandler

```python
class ForgetHandler
```

Handler for intentional and natural forgetting.

---

## ConflictData

```python
class ConflictData
```

Data about conflicting preferences.

---

## ConflictDetector

```python
class ConflictDetector
```

Detects conflicts between preferences and patterns.

---

## ReviewHandler

```python
class ReviewHandler
```

Handler for periodic reviews of stale preferences.

---

## TriggerRouter

```python
class TriggerRouter(Agent[EvolutionInput, EvolutionOutput])
```

Routes evolution inputs to appropriate handlers based on trigger type.

---

## EvolutionAgent

```python
class EvolutionAgent(Agent[EvolutionInput, EvolutionOutput])
```

Evolve K-gent's persona over time.

---

## BootstrapMode

```python
class BootstrapMode(Enum)
```

Bootstrap modes for initial persona population.

---

## BootstrapConfig

```python
class BootstrapConfig
```

Configuration for persona bootstrapping.

---

## bootstrap_persona

```python
async def bootstrap_persona(config: BootstrapConfig, existing_state: Optional[PersonaState]=None) -> PersonaState
```

Bootstrap a persona state based on configuration.

---

## evolve_persona

```python
def evolve_persona(state: PersonaState) -> EvolutionAgent
```

Create an evolution agent for the given persona state.

---

## bootstrap_clean_slate

```python
async def bootstrap_clean_slate() -> PersonaState
```

Quick bootstrap with clean slate mode.

---

## bootstrap_hybrid

```python
async def bootstrap_hybrid(existing_state: Optional[PersonaState]=None) -> PersonaState
```

Quick bootstrap with recommended hybrid mode.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle evolution input and return output.

---

## reinforce

```python
def reinforce(self) -> None
```

Increase confidence from new evidence.

---

## decay

```python
def decay(self, months: float) -> None
```

Decrease confidence over time.

---

## contradict

```python
def contradict(self) -> None
```

Decrease confidence from contradictory evidence.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle explicit user updates - immediate, high confidence.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle inferred changes - propose, medium confidence.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle contradictions between behavior and stated preferences.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle forgetting - intentional removal or archival.

---

## detect_conflicts

```python
def detect_conflicts(self) -> list[ConflictData]
```

Detect conflicting preferences based on evidence.

---

## handle

```python
async def handle(self, input: EvolutionInput) -> EvolutionOutput
```

Handle periodic reviews of stale preferences.

---

## invoke

```python
async def invoke(self, input: EvolutionInput) -> EvolutionOutput
```

Route input to appropriate handler based on trigger.

---

## invoke

```python
async def invoke(self, input: EvolutionInput) -> EvolutionOutput
```

Evolve the persona based on input.

---

## agents.k.flux

## flux

```python
module flux
```

KgentFlux: K-gent as a Flux Stream Agent.

### Things to Know

ℹ️ FluxStream is single-use. Once consumed (iterated), _consumed=True and re-iteration raises StopAsyncIteration immediately. Create a new FluxStream for each consumption via factory function. (Evidence: test_soul_streaming_integration.py::TestPipeAssociativity uses create_stream() factory to avoid reuse)

🚨 **Critical:** Metadata events ALWAYS pass through filter(), take(), map() unchanged. Only data events are filtered/transformed. This preserves token counts and completion signals. Don't filter expecting metadata to be blocked.
  - *Verified in: `test_soul_streaming_integration.py::test_pipeline_preserves_metadata`*

---

## FluxEvent

```python
class FluxEvent(Generic[T])
```

A streaming event in a Flux stream.

---

## FluxOperator

```python
class FluxOperator(Protocol[T, U])
```

Protocol for FluxStream transformation operators.

---

## FluxStream

```python
class FluxStream(Generic[T])
```

Composable async stream of FluxEvents with operators.

---

## LLMStreamSource

```python
class LLMStreamSource
```

Wraps an LLMClient's generate_stream() as a Flux source.

---

## KgentFluxState

```python
class KgentFluxState(str, Enum)
```

Lifecycle states for KgentFlux.

---

## KgentFluxConfig

```python
class KgentFluxConfig
```

Configuration for KgentFlux.

---

## KgentFlux

```python
class KgentFlux
```

K-gent as a Flux Stream Agent.

---

## create_kgent_flux

```python
def create_kgent_flux(soul: Optional[KgentSoul]=None, config: Optional[KgentFluxConfig]=None, agent_id: Optional[str]=None) -> KgentFlux
```

Create a KgentFlux instance.

---

## data

```python
def data(cls, value: T) -> 'FluxEvent[T]'
```

Create a data event containing a chunk of content.

---

## metadata

```python
def metadata(cls, meta: StreamingLLMResponse) -> 'FluxEvent[T]'
```

Create a metadata event containing stream completion info.

---

## is_data

```python
def is_data(self) -> bool
```

Check if this is a data event.

---

## is_metadata

```python
def is_metadata(self) -> bool
```

Check if this is a metadata event.

---

## value

```python
def value(self) -> Any
```

Get the event value (data or metadata).

---

## __call__

```python
def __call__(self, source: AsyncIterator[FluxEvent[T]]) -> AsyncIterator[FluxEvent[U]]
```

Apply the operator to a source stream.

---

## __init__

```python
def __init__(self, source: AsyncIterator[FluxEvent[T]]) -> None
```

Initialize FluxStream wrapping an async iterator.

---

## __aiter__

```python
def __aiter__(self) -> AsyncIterator[FluxEvent[T]]
```

Return self as async iterator.

---

## __anext__

```python
async def __anext__(self) -> FluxEvent[T]
```

Get next event from the stream.

---

## map

```python
def map(self, fn: Callable[[FluxEvent[T]], FluxEvent[U]]) -> 'FluxStream[U]'
```

Transform data events, pass metadata through unchanged.

---

## filter

```python
def filter(self, predicate: Callable[[FluxEvent[T]], bool]) -> 'FluxStream[T]'
```

Filter events based on a predicate, metadata always passes through.

---

## take

```python
def take(self, n: int) -> 'FluxStream[T]'
```

Limit stream to first n data events, metadata always passes through.

---

## tap

```python
def tap(self, fn: Callable[[FluxEvent[T]], None]) -> 'FluxStream[T]'
```

Perform side effects without modifying the stream.

---

## chain

```python
def chain(cls, *sources: 'FluxStream[T]') -> 'FluxStream[T]'
```

Concatenate multiple streams sequentially.

---

## merge

```python
def merge(cls, *sources: 'FluxStream[T]') -> 'FluxStream[T]'
```

Interleave multiple streams (first-available wins).

---

## zip

```python
def zip(self, other: 'FluxStream[T]') -> 'FluxStream[tuple[T, T]]'
```

Pair events from two streams.

---

## collect

```python
async def collect(self) -> list[T]
```

Materialize stream to a list of data values.

---

## pipe

```python
def pipe(self, *operators: Callable[['FluxStream[Any]'], 'FluxStream[Any]']) -> 'FluxStream[Any]'
```

Apply a sequence of operators to this stream.

---

## __init__

```python
def __init__(self, client: LLMClient, system: str, user: str, temperature: float=0.7, max_tokens: int=4000, buffer_size: Optional[int]=None) -> None
```

Initialize the LLM stream source.

---

## __aiter__

```python
def __aiter__(self) -> AsyncIterator[FluxEvent[str]]
```

Return self as async iterator.

---

## __anext__

```python
async def __anext__(self) -> FluxEvent[str]
```

Get next event from the stream.

---

## cancel

```python
async def cancel(self) -> None
```

Cancel the stream source.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if the stream has completed.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize runtime state.

---

## name

```python
def name(self) -> str
```

Human-readable name.

---

## state

```python
def state(self) -> KgentFluxState
```

Current lifecycle state.

---

## events_processed

```python
def events_processed(self) -> int
```

Number of events processed.

---

## entropy_remaining

```python
def entropy_remaining(self) -> float
```

Remaining entropy budget.

---

## id

```python
def id(self) -> str
```

Unique identifier.

---

## is_running

```python
def is_running(self) -> bool
```

Check if flux is currently processing.

---

## is_dormant

```python
def is_dormant(self) -> bool
```

Check if flux is in dormant mode.

---

## attach_mirror

```python
def attach_mirror(self, mirror: 'HolographicBuffer') -> 'KgentFlux'
```

Attach a HolographicBuffer for Terrarium observability.

---

## detach_mirror

```python
def detach_mirror(self) -> Optional['HolographicBuffer']
```

Detach the mirror.

---

## mirror

```python
def mirror(self) -> Optional['HolographicBuffer']
```

Optional mirror for Terrarium observability.

---

## start

```python
async def start(self, source: AsyncIterator[SoulEvent]) -> AsyncIterator[SoulEvent]
```

Start the flux and return the output stream.

---

## invoke

```python
async def invoke(self, input_event: SoulEvent) -> SoulEvent
```

Process a SoulEvent.

---

## stop

```python
async def stop(self) -> None
```

Stop the flux gracefully.

---

## wait

```python
async def wait(self) -> None
```

Wait for flux to complete.

---

## reset

```python
def reset(self) -> None
```

Reset flux to DORMANT state.

---

## dialogue

```python
async def dialogue(self, message: str, mode: Optional[DialogueMode]=None) -> SoulEvent
```

Convenience method for dialogue.

---

## on_chunk

```python
def on_chunk(chunk_text: str) -> None
```

Emit streaming chunk event via mirror.

---

## fill_buffer

```python
async def fill_buffer(src: AsyncIterator[FluxEvent[T]], buf: list[FluxEvent[T]]) -> FluxEvent[T] | None
```

Get next data event, yielding metadata.

---

## agents.k.functor

## functor

```python
module functor
```

Soul Functor: The Categorical Imperative.

---

## Soul

```python
class Soul(Generic[A])
```

Soul context wrapper for values.

### Examples
```python
>>> raw_input = "Should I add more features?"
```
```python
>>> soul_input = Soul(raw_input, eigenvectors=KENT_EIGENVECTORS)
```
```python
>>> # Now agents can access the minimalist aesthetic preference
```

---

## SoulAgent

```python
class SoulAgent(Agent[Soul[A], Soul[B]])
```

An agent lifted to operate with soul context.

---

## SoulFunctor

```python
class SoulFunctor(UniversalFunctor[SoulAgent[Any, Any]])
```

Universal Functor for Soul (K-gent persona) context.

### Examples
```python
>>> lifted = SoulFunctor.lift(my_agent)
```
```python
>>> result = await lifted.invoke(Soul(input_value))
```
```python
>>> # result is Soul[B] with preserved persona context
```

---

## soul_lift

```python
def soul_lift(agent: Agent[A, B]) -> SoulAgent[A, B]
```

Lift an agent to the soul domain.

### Examples
```python
>>> lifted = soul_lift(my_agent)
```
```python
>>> result = await lifted.invoke(Soul(input))
```

---

## soul

```python
def soul(value: A) -> Soul[A]
```

Embed a value in soul context.

### Examples
```python
>>> s = soul("What should I prioritize?")
```
```python
>>> s.eigenvectors.aesthetic.value  # 0.15 (minimalist)
```

---

## soul_with

```python
def soul_with(value: A, eigenvectors: KentEigenvectors | None=None, persona: PersonaState | None=None, **metadata: Any) -> Soul[A]
```

Create a soul with explicit context.

---

## unlift

```python
def unlift(soul_agent: SoulAgent[A, B]) -> Agent[A, B]
```

Extract inner agent from soul wrapper.

---

## unwrap

```python
def unwrap(soul_value: Soul[A]) -> A
```

Extract raw value from soul wrapper.

---

## __eq__

```python
def __eq__(self, other: object) -> bool
```

Equality based on value and context.

---

## map

```python
def map(self, f: Any) -> 'Soul[Any]'
```

Apply a function to the wrapped value, preserving context.

---

## with_metadata

```python
def with_metadata(self, key: str, value: Any) -> 'Soul[A]'
```

Add metadata while preserving context.

---

## context_prompt

```python
def context_prompt(self) -> str
```

Generate a context prompt from soul state.

---

## __init__

```python
def __init__(self, inner: Agent[A, B], default_eigenvectors: KentEigenvectors | None=None, default_persona: PersonaState | None=None) -> None
```

Create a soul-lifted agent.

---

## name

```python
def name(self) -> str
```

Name of the lifted agent.

---

## inner

```python
def inner(self) -> Agent[A, B]
```

Access the inner (unlifted) agent.

---

## invoke

```python
async def invoke(self, input: Soul[A]) -> Soul[B]
```

Invoke the inner agent, preserving soul context.

---

## __rshift__

```python
def __rshift__(self, other: 'Agent[Soul[B], C]') -> 'ComposedAgent[Soul[A], Soul[B], C]'
```

Compose with another soul-aware agent.

---

## lift

```python
def lift(agent: Agent[A, B]) -> SoulAgent[A, B]
```

Lift an agent to operate with soul context.

---

## pure

```python
def pure(value: A) -> Soul[A]
```

Embed a value in the soul context.

---

## lift_with_persona

```python
def lift_with_persona(agent: Agent[A, B], eigenvectors: KentEigenvectors | None=None, persona: PersonaState | None=None) -> SoulAgent[A, B]
```

Lift an agent with explicit persona configuration.

---

## agents.k.garden

## garden

```python
module garden
```

PersonaGarden: The soul's memory garden.

---

## EntryType

```python
class EntryType(str, Enum)
```

Types of entries in the persona garden.

---

## GardenLifecycle

```python
class GardenLifecycle(str, Enum)
```

Lifecycle stages for garden entries.

---

## GardenSeason

```python
class GardenSeason(str, Enum)
```

Seasonal rhythms for the garden.

---

## GardenEntry

```python
class GardenEntry
```

An entry in the persona garden.

---

## GardenStats

```python
class GardenStats
```

Statistics about the persona garden.

---

## SeasonConfig

```python
class SeasonConfig
```

Configuration for seasonal behaviors.

---

## PersonaGarden

```python
class PersonaGarden
```

The soul's memory garden.

### Examples
```python
>>> garden = PersonaGarden()
```
```python
>>> >>> # Plant a preference (explicit)
```
```python
>>> await garden.plant(
```
```python
>>> >>> # Get stats
```
```python
>>> stats = await garden.stats()
```

---

## get_garden

```python
def get_garden() -> PersonaGarden
```

Get or create the global PersonaGarden instance.

---

## set_garden

```python
def set_garden(garden: PersonaGarden) -> None
```

Set the global PersonaGarden instance.

---

## age_days

```python
def age_days(self) -> float
```

Age since planting in days.

---

## staleness_days

```python
def staleness_days(self) -> float
```

Days since last nurturing.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'GardenEntry'
```

Deserialize from dictionary.

---

## for_season

```python
def for_season(cls, season: GardenSeason) -> 'SeasonConfig'
```

Get config optimized for a season.

---

## __init__

```python
def __init__(self, storage_path: Optional[Path]=None, auto_save: bool=True, season: Optional[GardenSeason]=None) -> None
```

Initialize persona garden.

---

## season

```python
def season(self) -> GardenSeason
```

Get current garden season.

---

## season

```python
def season(self, value: GardenSeason) -> None
```

Set garden season and update config.

---

## storage_path

```python
def storage_path(self) -> Path
```

Get storage path.

---

## entries

```python
def entries(self) -> dict[str, GardenEntry]
```

Get all entries (copy).

---

## plant

```python
async def plant(self, content: str, entry_type: EntryType, source: str='manual', confidence: float=0.3, tags: Optional[list[str]]=None, eigenvector_affinities: Optional[dict[str, float]]=None) -> GardenEntry
```

Plant a new entry in the garden.

---

## plant_preference

```python
async def plant_preference(self, content: str, confidence: float=0.5, tags: Optional[list[str]]=None) -> GardenEntry
```

Convenience method to plant a preference.

---

## plant_pattern

```python
async def plant_pattern(self, content: str, source: str='hypnagogia', confidence: float=0.3, eigenvector_affinities: Optional[dict[str, float]]=None) -> GardenEntry
```

Convenience method to plant a pattern.

---

## nurture

```python
async def nurture(self, entry_id: str, evidence: str, confidence_boost: float=0.05) -> Optional[GardenEntry]
```

Nurture an entry with evidence.

---

## get

```python
async def get(self, entry_id: str) -> Optional[GardenEntry]
```

Get entry by ID.

---

## list_by_type

```python
async def list_by_type(self, entry_type: EntryType) -> list[GardenEntry]
```

List entries by type.

---

## list_by_lifecycle

```python
async def list_by_lifecycle(self, lifecycle: GardenLifecycle) -> list[GardenEntry]
```

List entries by lifecycle stage.

---

## seeds

```python
async def seeds(self) -> list[GardenEntry]
```

Get all seeds.

---

## saplings

```python
async def saplings(self) -> list[GardenEntry]
```

Get all saplings.

---

## trees

```python
async def trees(self) -> list[GardenEntry]
```

Get all trees (established patterns).

---

## flowers

```python
async def flowers(self) -> list[GardenEntry]
```

Get all flowers (peak insights).

---

## preferences

```python
async def preferences(self) -> list[GardenEntry]
```

Get all preferences.

---

## patterns

```python
async def patterns(self) -> list[GardenEntry]
```

Get all patterns.

---

## compost

```python
async def compost(self, entry_id: str) -> Optional[GardenEntry]
```

Compost an entry (mark as deprecated).

---

## prune_stale

```python
async def prune_stale(self, days_threshold: int=30) -> list[GardenEntry]
```

Compost entries that haven't been nurtured recently.

---

## staleness_decay

```python
async def staleness_decay(self) -> list[tuple[GardenEntry, float]]
```

Apply natural confidence decay to stale entries.

---

## cross_pollinate

```python
async def cross_pollinate(self, other: 'PersonaGarden', similarity_threshold: float=0.8) -> list[GardenEntry]
```

Cross-pollinate patterns from another garden.

---

## auto_plant_from_dialogue

```python
async def auto_plant_from_dialogue(self, message: str, response: str, detected_patterns: Optional[list[str]]=None, eigenvector_affinities: Optional[dict[str, float]]=None) -> list[GardenEntry]
```

Auto-plant patterns detected from dialogue.

---

## sync_from_hypnagogia

```python
async def sync_from_hypnagogia(self, cycle: 'HypnagogicCycle') -> int
```

Sync patterns from HypnagogicCycle.

---

## stats

```python
async def stats(self) -> GardenStats
```

Get garden statistics.

---

## format_summary

```python
def format_summary(self) -> str
```

Format garden summary for display.

---

## format_entry

```python
def format_entry(self, entry: GardenEntry) -> str
```

Format a single entry for display.

---

## agents.k.garden_sql

## garden_sql

```python
module garden_sql
```

**AGENTESE:** `self.soul.garden.durable`

SQLPersonaGarden: PostgreSQL-backed PersonaGarden.

---

## AsyncContextManager

```python
class AsyncContextManager(Protocol[_T_co])
```

Protocol for async context managers.

---

## DatabasePool

```python
class DatabasePool(Protocol)
```

Protocol for asyncpg connection pool.

---

## SQLPersonaGarden

```python
class SQLPersonaGarden
```

PostgreSQL-backed PersonaGarden.

### Examples
```python
>>> garden = await SQLPersonaGarden.connect(database_url)
```
```python
>>> await garden.plant_preference("Concise communication")
```
```python
>>> await garden.close()
```

---

## get_sql_garden

```python
async def get_sql_garden(database_url: Optional[str]=None) -> SQLPersonaGarden
```

Get or create the global SQLPersonaGarden instance.

---

## close_sql_garden

```python
async def close_sql_garden() -> None
```

Close the global SQLPersonaGarden instance.

---

## acquire

```python
def acquire(self) -> AsyncContextManager[Any]
```

Acquire a connection from the pool (returns async context manager).

---

## close

```python
async def close(self) -> None
```

Close the pool.

---

## __init__

```python
def __init__(self, pool: DatabasePool, season: Optional[GardenSeason]=None) -> None
```

Initialize with a database connection pool.

---

## connect

```python
async def connect(cls, database_url: str, min_size: int=1, max_size: int=5, season: Optional[GardenSeason]=None) -> 'SQLPersonaGarden'
```

Create and connect a SQLPersonaGarden.

---

## close

```python
async def close(self) -> None
```

Close the connection pool.

---

## season

```python
def season(self) -> GardenSeason
```

Get current garden season.

---

## season

```python
def season(self, value: GardenSeason) -> None
```

Set garden season and update config.

---

## plant

```python
async def plant(self, content: str, entry_type: EntryType, source: str='manual', confidence: float=0.3, tags: Optional[list[str]]=None, eigenvector_affinities: Optional[dict[str, float]]=None) -> GardenEntry
```

Plant a new entry in the garden.

---

## plant_preference

```python
async def plant_preference(self, content: str, confidence: float=0.5, tags: Optional[list[str]]=None) -> GardenEntry
```

Convenience method to plant a preference.

---

## plant_pattern

```python
async def plant_pattern(self, content: str, source: str='hypnagogia', confidence: float=0.3, eigenvector_affinities: Optional[dict[str, float]]=None) -> GardenEntry
```

Convenience method to plant a pattern.

---

## nurture

```python
async def nurture(self, entry_id: str, evidence: str, confidence_boost: float=0.05) -> Optional[GardenEntry]
```

Nurture an entry with evidence.

---

## get

```python
async def get(self, entry_id: str) -> Optional[GardenEntry]
```

Get entry by ID.

---

## list_by_type

```python
async def list_by_type(self, entry_type: EntryType) -> list[GardenEntry]
```

List entries by type.

---

## list_by_lifecycle

```python
async def list_by_lifecycle(self, lifecycle: GardenLifecycle) -> list[GardenEntry]
```

List entries by lifecycle stage.

---

## seeds

```python
async def seeds(self) -> list[GardenEntry]
```

Get all seeds.

---

## saplings

```python
async def saplings(self) -> list[GardenEntry]
```

Get all saplings.

---

## trees

```python
async def trees(self) -> list[GardenEntry]
```

Get all trees (established patterns).

---

## flowers

```python
async def flowers(self) -> list[GardenEntry]
```

Get all flowers (peak insights).

---

## preferences

```python
async def preferences(self) -> list[GardenEntry]
```

Get all preferences.

---

## patterns

```python
async def patterns(self) -> list[GardenEntry]
```

Get all patterns.

---

## entries

```python
def entries(self) -> dict[str, GardenEntry]
```

Get all entries.

---

## compost

```python
async def compost(self, entry_id: str) -> Optional[GardenEntry]
```

Compost an entry (mark as deprecated).

---

## prune_stale

```python
async def prune_stale(self, days_threshold: int=30) -> list[GardenEntry]
```

Compost entries that haven't been nurtured recently.

---

## staleness_decay

```python
async def staleness_decay(self) -> list[tuple[GardenEntry, float]]
```

Apply natural confidence decay to stale entries.

---

## sync_from_hypnagogia

```python
async def sync_from_hypnagogia(self, cycle: 'HypnagogicCycle') -> int
```

Sync patterns from HypnagogicCycle.

---

## auto_plant_from_dialogue

```python
async def auto_plant_from_dialogue(self, message: str, response: str, detected_patterns: Optional[list[str]]=None, eigenvector_affinities: Optional[dict[str, float]]=None) -> list[GardenEntry]
```

Auto-plant patterns detected from dialogue.

---

## stats

```python
async def stats(self) -> GardenStats
```

Get garden statistics.

---

## format_summary

```python
def format_summary(self) -> str
```

Format garden summary for display.

---

## format_entry

```python
def format_entry(self, entry: GardenEntry) -> str
```

Format a single entry for display.

---

## agents.k.gatekeeper

## gatekeeper

```python
module gatekeeper
```

Semantic Gatekeeper: Validate code against principles.

### Things to Know

🚨 **Critical:** Only ERROR and CRITICAL severities cause result.passed=False. INFO and WARNING violations are informational and DO NOT fail validation. Check by_severity counts if you need warning-level enforcement.
  - *Verified in: `test_gatekeeper.py::TestSeverity::test_pass_fail_threshold`*

ℹ️ LLM failures in semantic analysis are SILENT - they return empty list. The gatekeeper gracefully degrades to heuristic-only validation. Check if self._llm is set AND use_llm=True to confirm LLM is active.
  - *Verified in: `gatekeeper.py::_check_semantic catches all exceptions`*

---

## Principle

```python
class Principle(str, Enum)
```

The seven kgents principles.

---

## Severity

```python
class Severity(str, Enum)
```

Severity of a violation.

---

## Violation

```python
class Violation
```

A potential principle violation.

---

## ValidationResult

```python
class ValidationResult
```

Result of validating against principles.

---

## AnalyzerResult

```python
class AnalyzerResult
```

Result from a specialized analyzer.

---

## TastefullnessAnalyzer

```python
class TastefullnessAnalyzer
```

Analyzer for TASTEFUL principle (110% Domain 2).

---

## ComposabilityAnalyzer

```python
class ComposabilityAnalyzer
```

Analyzer for COMPOSABLE principle (110% Domain 2).

---

## GratitudeAnalyzer

```python
class GratitudeAnalyzer
```

Analyzer for Accursed Share acknowledgment (110% Domain 2).

---

## ValidationHistoryEntry

```python
class ValidationHistoryEntry
```

A historical validation record.

---

## ValidationHistory

```python
class ValidationHistory
```

Tracks validation history for pattern detection (110% Domain 2).

---

## DeepAnalysisResult

```python
class DeepAnalysisResult
```

Result from deep analysis with explanations (110% Domain 2).

---

## SemanticGatekeeper

```python
class SemanticGatekeeper
```

Semantic Gatekeeper: Validate code against kgents principles.

### Examples
```python
>>> gatekeeper = SemanticGatekeeper()
```
```python
>>> result = await gatekeeper.validate_file("src/agent.py")
```
```python
>>> if not result.passed:
```
```python
>>> >>> # Deep analysis with explanations (110%)
```
```python
>>> deep = await gatekeeper.validate_deep("src/agent.py", explain=True)
```

---

## validate_file

```python
async def validate_file(file_path: str, use_llm: bool=False, llm: Optional['LLMClient']=None) -> ValidationResult
```

Validate a file against principles.

---

## validate_content

```python
async def validate_content(content: str, target: str='content', use_llm: bool=False, llm: Optional['LLMClient']=None) -> ValidationResult
```

Validate content against principles.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## format

```python
def format(self) -> str
```

Format for display.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## by_severity

```python
def by_severity(self) -> dict[str, int]
```

Count violations by severity.

---

## by_principle

```python
def by_principle(self) -> dict[str, int]
```

Count violations by principle.

---

## format

```python
def format(self) -> str
```

Format for display.

---

## analyze

```python
async def analyze(self, content: str, target: str) -> AnalyzerResult
```

Analyze content for tastefulness.

---

## analyze

```python
async def analyze(self, content: str, target: str) -> AnalyzerResult
```

Analyze content for composability.

---

## analyze

```python
async def analyze(self, content: str, target: str) -> AnalyzerResult
```

Analyze content for gratitude/acknowledgment.

---

## __init__

```python
def __init__(self, max_entries: int=100) -> None
```

Initialize validation history.

---

## record

```python
def record(self, result: 'ValidationResult') -> None
```

Record a validation result.

---

## recurring_violations

```python
def recurring_violations(self) -> dict[str, int]
```

Find principles that are repeatedly violated.

---

## improvement_trend

```python
def improvement_trend(self) -> float
```

Calculate improvement trend (-1 to 1, positive = improving).

---

## blind_spots

```python
def blind_spots(self) -> list[str]
```

Find principles that have never been violated (potential blind spots).

---

## generate_report

```python
def generate_report(self) -> str
```

Generate a human-readable history report.

---

## format

```python
def format(self) -> str
```

Format with explanations.

---

## __init__

```python
def __init__(self, llm: Optional['LLMClient']=None, use_llm: bool=True, history: Optional[ValidationHistory]=None) -> None
```

Initialize gatekeeper.

---

## history

```python
def history(self) -> ValidationHistory
```

Get validation history.

---

## validate_file

```python
async def validate_file(self, file_path: str) -> ValidationResult
```

Validate a file against principles.

---

## validate_content

```python
async def validate_content(self, content: str, target: str='content', use_analyzers: bool=True) -> ValidationResult
```

Validate content against principles.

---

## validate_deep

```python
async def validate_deep(self, file_path: str, explain: bool=True) -> DeepAnalysisResult
```

Deep validation with explanations (110% Domain 2).

---

## agents.k.hypnagogia

## hypnagogia

```python
module hypnagogia
```

Hypnagogia: The Dream Cycle.

---

## HypnagogicConfig

```python
class HypnagogicConfig
```

Configuration for dream cycles.

---

## DreamSchedule

```python
class DreamSchedule
```

Schedule information for CortexDaemon integration (110% Domain 3).

---

## HypnagogicCalibration

```python
class HypnagogicCalibration
```

Adaptive calibration for dream timing (110% Domain 3).

---

## PatternMaturity

```python
class PatternMaturity(str, Enum)
```

Maturity levels for discovered patterns.

---

## Pattern

```python
class Pattern
```

A pattern discovered during dream processing.

---

## EigenvectorDelta

```python
class EigenvectorDelta
```

Changes to eigenvector confidence from dream processing.

---

## DreamReport

```python
class DreamReport
```

Report from a dream cycle.

---

## Interaction

```python
class Interaction
```

A recorded interaction for dream processing.

---

## DreamPersistence

```python
class DreamPersistence
```

Persist and load dream state (110% Domain 3).

---

## HypnagogicCycle

```python
class HypnagogicCycle
```

The dream cycle - background refinement of patterns.

---

## create_hypnagogic_cycle

```python
def create_hypnagogic_cycle(config: Optional[HypnagogicConfig]=None, llm: Optional['LLMClient']=None) -> HypnagogicCycle
```

Create a HypnagogicCycle instance.

---

## get_hypnagogia

```python
def get_hypnagogia() -> HypnagogicCycle
```

Get or create the global hypnagogia instance.

---

## set_hypnagogia

```python
def set_hypnagogia(cycle: HypnagogicCycle) -> None
```

Set the global hypnagogia instance.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## record_quality

```python
def record_quality(self, pattern_rate: float, promotion_rate: float) -> None
```

Record dream quality metrics.

---

## recalibrate

```python
def recalibrate(self) -> bool
```

Recalibrate dream parameters based on history.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## id

```python
def id(self) -> str
```

Generate stable ID for pattern.

---

## age_days

```python
def age_days(self) -> float
```

Age of pattern in days.

---

## staleness_days

```python
def staleness_days(self) -> float
```

Days since last seen.

---

## promote

```python
def promote(self) -> 'Pattern'
```

Promote pattern to next maturity level.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## delta

```python
def delta(self) -> float
```

The change in confidence.

---

## direction

```python
def direction(self) -> str
```

Human-readable direction.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## summary

```python
def summary(self) -> str
```

Human-readable summary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## to_text

```python
def to_text(self) -> str
```

Convert to text for pattern extraction.

---

## __init__

```python
def __init__(self, storage_path: Optional[Path]=None) -> None
```

Initialize persistence.

---

## patterns_file

```python
def patterns_file(self) -> Path
```

Path to patterns file.

---

## history_file

```python
def history_file(self) -> Path
```

Path to history file.

---

## calibration_file

```python
def calibration_file(self) -> Path
```

Path to calibration file.

---

## save_patterns

```python
def save_patterns(self, patterns: dict[str, 'Pattern']) -> None
```

Save patterns to disk.

---

## load_patterns

```python
def load_patterns(self) -> dict[str, 'Pattern']
```

Load patterns from disk.

---

## save_history

```python
def save_history(self, history: list['DreamReport'], max_entries: int=30) -> None
```

Save dream history to disk.

---

## load_history

```python
def load_history(self) -> list['DreamReport']
```

Load dream history from disk.

---

## save_calibration

```python
def save_calibration(self, calibration: 'HypnagogicCalibration') -> None
```

Save calibration state to disk.

---

## load_calibration

```python
def load_calibration(self) -> 'HypnagogicCalibration'
```

Load calibration state from disk.

---

## __init__

```python
def __init__(self, config: Optional[HypnagogicConfig]=None, llm: Optional['LLMClient']=None, persistence: Optional[DreamPersistence]=None) -> None
```

Initialize hypnagogic cycle.

---

## set_event_callback

```python
def set_event_callback(self, callback: Callable[[str, dict[str, Any]], None]) -> None
```

Set callback for Flux event emission (110% Domain 3).

---

## config

```python
def config(self) -> HypnagogicConfig
```

Get configuration.

---

## patterns

```python
def patterns(self) -> dict[str, Pattern]
```

Get all patterns.

---

## interactions_buffered

```python
def interactions_buffered(self) -> int
```

Number of interactions in buffer.

---

## last_dream

```python
def last_dream(self) -> Optional[DreamReport]
```

Most recent dream report.

---

## schedule

```python
def schedule(self) -> DreamSchedule
```

Get dream schedule (110% Domain 3).

---

## calibration

```python
def calibration(self) -> HypnagogicCalibration
```

Get calibration state (110% Domain 3).

---

## record_interaction

```python
def record_interaction(self, message: str, response: str, mode: str, tokens_used: int=0) -> None
```

Record an interaction for dream processing.

---

## clear_interactions

```python
def clear_interactions(self) -> int
```

Clear interaction buffer, return count cleared.

---

## dream

```python
async def dream(self, soul: 'KgentSoul', dry_run: bool=False) -> DreamReport
```

Execute a dream cycle.

---

## extract_patterns

```python
async def extract_patterns(self, interactions: list[Interaction]) -> list[Pattern]
```

Extract patterns from recent interactions.

---

## update_eigenvectors

```python
async def update_eigenvectors(self, patterns: list[Pattern], soul: 'KgentSoul') -> list[EigenvectorDelta]
```

Adjust eigenvector confidence based on discovered patterns.

---

## status

```python
def status(self) -> dict[str, Any]
```

Get current hypnagogia status.

---

## should_dream

```python
def should_dream(self) -> bool
```

Check if conditions are met for dreaming.

---

## agents.k.llm

## llm

```python
module llm
```

K-gent LLM Client: Abstraction for LLM-backed K-gent operations.

---

## LLMResponse

```python
class LLMResponse
```

Response from LLM generation.

---

## StreamingLLMResponse

```python
class StreamingLLMResponse
```

Final response from streaming LLM generation.

---

## LLMClient

```python
class LLMClient(Protocol)
```

Protocol for LLM clients used by K-gent.

---

## BaseLLMClient

```python
class BaseLLMClient(ABC)
```

Base class for LLM clients.

---

## ClaudeLLMClient

```python
class ClaudeLLMClient(BaseLLMClient)
```

LLM client using ClaudeCLIRuntime.

---

## MockLLMClient

```python
class MockLLMClient(BaseLLMClient)
```

Mock LLM client for testing.

---

## morpheus_available

```python
def morpheus_available() -> bool
```

Check if Morpheus Gateway is available.

---

## create_llm_client

```python
def create_llm_client(timeout: float=120.0, verbose: bool=False, mock: bool=False, mock_responses: Optional[list[str]]=None, prefer_morpheus: bool=True) -> LLMClient
```

Create an LLM client for K-gent.

---

## has_llm_credentials

```python
def has_llm_credentials() -> bool
```

Check if any LLM client is available.

---

## generate

```python
async def generate(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> LLMResponse
```

Generate a response from the LLM.

---

## generate_stream

```python
def generate_stream(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> AsyncIterator[Union[str, StreamingLLMResponse]]
```

Generate a streaming response from the LLM.

---

## generate

```python
async def generate(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> LLMResponse
```

Generate a response from the LLM.

---

## generate_stream

```python
async def generate_stream(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> AsyncIterator[Union[str, StreamingLLMResponse]]
```

Generate a streaming response from the LLM.

---

## __init__

```python
def __init__(self, timeout: float=120.0, verbose: bool=False)
```

Initialize Claude LLM client.

---

## generate

```python
async def generate(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> LLMResponse
```

Generate a response using ClaudeCLIRuntime.

---

## generate_stream

```python
async def generate_stream(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> AsyncIterator[Union[str, StreamingLLMResponse]]
```

Generate a streaming response using ClaudeCLIRuntime.

---

## __init__

```python
def __init__(self, responses: Optional[list[str]]=None, default_response: str='Mock response')
```

Initialize mock client.

---

## generate

```python
async def generate(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> LLMResponse
```

Return mock response.

---

## call_history

```python
def call_history(self) -> list[dict[str, Any]]
```

Get history of calls made to this client.

---

## call_count

```python
def call_count(self) -> int
```

Get number of calls made to this client.

---

## generate_stream

```python
async def generate_stream(self, system: str, user: str, temperature: float=0.7, max_tokens: int=4000) -> AsyncIterator[Union[str, StreamingLLMResponse]]
```

Generate a streaming mock response.

---

## agents.k.memory_allocation

## memory_allocation

```python
module memory_allocation
```

K-gent Memory Allocation: Soul Substrate Integration.

---

## KgentMemoryProfile

```python
class KgentMemoryProfile
```

K-gent's memory configuration.

---

## AllocationStats

```python
class AllocationStats
```

Statistics for K-gent's memory allocation.

---

## KgentAllocationManager

```python
class KgentAllocationManager
```

Manages K-gent's memory allocation in the SharedSubstrate.

---

## KgentPheromoneDepositor

```python
class KgentPheromoneDepositor
```

Deposits pheromones for K-gent's activity.

---

## create_kgent_allocation

```python
async def create_kgent_allocation(substrate: 'SharedSubstrate[Any]', profile: Optional[KgentMemoryProfile]=None) -> KgentAllocationManager
```

Factory function to create and initialize K-gent allocation.

---

## create_kgent_depositor

```python
def create_kgent_depositor(field: 'PheromoneField') -> KgentPheromoneDepositor
```

Factory function to create K-gent pheromone depositor.

---

## total_max_patterns

```python
def total_max_patterns(self) -> int
```

Total pattern capacity across all tiers.

---

## __init__

```python
def __init__(self, substrate: 'SharedSubstrate[Any]', profile: Optional[KgentMemoryProfile]=None, agent_id: str='kgent') -> None
```

Initialize K-gent allocation manager.

---

## is_initialized

```python
def is_initialized(self) -> bool
```

Check if allocations are initialized.

---

## interaction_count

```python
def interaction_count(self) -> int
```

Number of interactions since initialization.

---

## initialize

```python
async def initialize(self) -> None
```

Initialize K-gent's memory allocations.

---

## store_working

```python
async def store_working(self, concept_id: str, content: Any, embedding: list[float]) -> bool
```

Store pattern in working memory.

---

## retrieve_working

```python
async def retrieve_working(self, cue: list[float], threshold: float=0.5, limit: int=10) -> list[Any]
```

Retrieve from working memory by resonance.

---

## store_eigenvector

```python
async def store_eigenvector(self, dimension: str, value: float, embedding: list[float]) -> bool
```

Store eigenvector dimension value.

---

## cache_soul_state

```python
async def cache_soul_state(self, soul_state: 'SoulState', embedding: list[float]) -> bool
```

Cache the full soul state.

---

## store_dialogue

```python
async def store_dialogue(self, turn_id: str, message: str, response: str, mode: str, embedding: list[float]) -> bool
```

Store a dialogue turn.

---

## retrieve_dialogue

```python
async def retrieve_dialogue(self, cue: list[float], threshold: float=0.5, limit: int=10) -> list[Any]
```

Retrieve dialogue history by resonance.

---

## store_dream

```python
async def store_dream(self, pattern_id: str, content: Any, embedding: list[float]) -> bool
```

Store a consolidated dream pattern.

---

## retrieve_dreams

```python
async def retrieve_dreams(self, cue: list[float], threshold: float=0.5, limit: int=10) -> list[Any]
```

Retrieve dream patterns by resonance.

---

## should_promote

```python
def should_promote(self) -> bool
```

Check if dialogue allocation should be promoted to dedicated crystal.

---

## promote_dialogue

```python
async def promote_dialogue(self) -> bool
```

Promote dialogue allocation to dedicated crystal.

---

## compact_dreams

```python
async def compact_dreams(self, ratio: float=0.8) -> int
```

Compact dream patterns during Hypnagogia.

---

## crystallize

```python
async def crystallize(self, tier: str='dialogue') -> dict[str, Any]
```

Trigger crystallization for a specific tier.

---

## stats

```python
def stats(self) -> AllocationStats
```

Get K-gent allocation statistics.

---

## __init__

```python
def __init__(self, field: 'PheromoneField', agent_id: str='kgent') -> None
```

Initialize K-gent pheromone depositor.

---

## deposit_dialogue

```python
async def deposit_dialogue(self, mode: str, intensity: float=1.0) -> None
```

Deposit trace for dialogue activity.

---

## deposit_eigenvector

```python
async def deposit_eigenvector(self, dimension: str, value: float) -> None
```

Deposit trace for eigenvector state.

---

## deposit_pattern

```python
async def deposit_pattern(self, pattern_type: str, pattern_id: str, intensity: float=1.0) -> None
```

Deposit trace for pattern recognition.

---

## deposit_emotional_state

```python
async def deposit_emotional_state(self, state: str, intensity: float=1.0) -> None
```

Deposit trace for emotional state.

---

## agents.k.pattern_store

## pattern_store

```python
module pattern_store
```

**AGENTESE:** `self.soul.patterns.resonance`

PatternStore: Qdrant-backed semantic pattern storage.

---

## EmbeddingProvider

```python
class EmbeddingProvider(Protocol)
```

Protocol for computing embeddings.

---

## VectorClient

```python
class VectorClient(Protocol)
```

Protocol for vector operations.

---

## PatternStoreConfig

```python
class PatternStoreConfig
```

Configuration for the pattern store.

---

## PatternMatch

```python
class PatternMatch
```

A pattern match from semantic search.

---

## SearchResult

```python
class SearchResult
```

Result of a pattern search.

---

## MockEmbedder

```python
class MockEmbedder
```

Mock embedder for testing.

---

## MockVectorClient

```python
class MockVectorClient
```

Mock Qdrant client for testing.

---

## QdrantVectorClient

```python
class QdrantVectorClient
```

Real Qdrant client implementation.

---

## OpenAIEmbedder

```python
class OpenAIEmbedder
```

OpenAI embeddings provider.

---

## PatternStore

```python
class PatternStore
```

Semantic pattern storage backed by Qdrant.

### Examples
```python
>>> store = await PatternStore.create()
```
```python
>>> await store.index_pattern(pattern)
```
```python
>>> similar = await store.find_similar("logical reasoning")
```
```python
>>> for match in similar.matches:
```

---

## get_pattern_store

```python
async def get_pattern_store(config: PatternStoreConfig | None=None) -> PatternStore
```

Get or create the global PatternStore instance.

---

## close_pattern_store

```python
async def close_pattern_store() -> None
```

Close the global PatternStore instance.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Compute embedding vector for text.

---

## upsert

```python
async def upsert(self, collection: str, id: str, vector: list[float], payload: dict[str, Any]) -> None
```

Upsert a vector with payload.

---

## delete

```python
async def delete(self, collection: str, id: str) -> None
```

Delete a vector by ID.

---

## search

```python
async def search(self, collection: str, query_vector: list[float], top_k: int, filter_: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Search for similar vectors.

---

## from_env

```python
def from_env(cls) -> 'PatternStoreConfig'
```

Load configuration from environment.

---

## is_high_confidence

```python
def is_high_confidence(self) -> bool
```

Check if this is a high-confidence match.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Create deterministic mock embedding.

---

## connect

```python
async def connect(self) -> None
```

Connect to Qdrant and ensure collection exists.

---

## connect

```python
async def connect(self) -> None
```

Initialize OpenAI client.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Compute embedding using OpenAI API.

---

## create

```python
async def create(cls, config: PatternStoreConfig | None=None) -> 'PatternStore'
```

Create a PatternStore with appropriate backends.

---

## index_pattern

```python
async def index_pattern(self, pattern: Pattern) -> None
```

Index a pattern for semantic search.

---

## remove_pattern

```python
async def remove_pattern(self, pattern_id: str) -> None
```

Remove a pattern from the index.

---

## find_similar

```python
async def find_similar(self, query: str, top_k: int | None=None, min_score: float | None=None, maturity_filter: PatternMaturity | None=None) -> SearchResult
```

Find patterns semantically similar to the query.

---

## index_all_patterns

```python
async def index_all_patterns(self, patterns: dict[str, Pattern]) -> int
```

Index all patterns from a HypnagogicCycle.

---

## find_related_to_eigenvector

```python
async def find_related_to_eigenvector(self, eigenvector: str, threshold: float=0.3) -> list[PatternMatch]
```

Find patterns with affinity to a specific eigenvector.

---

## indexed_count

```python
def indexed_count(self) -> int
```

Number of indexed patterns.

---

## agents.k.persistent_persona

## persistent_persona

```python
module persistent_persona
```

Persistent K-gent: Persona with durable state storage.

---

## PersistentPersonaAgent

```python
class PersistentPersonaAgent(KgentAgent)
```

K-gent with persistent persona state.

### Examples
```python
>>> persona = PersistentPersonaAgent(
```
```python
>>> # First session
```
```python
>>> response = await persona.invoke(
```
```python
>>> # Later session - remembers preferences
```
```python
>>> persona2 = PersistentPersonaAgent(namespace="kgent_persona")
```

---

## PersistentPersonaQueryAgent

```python
class PersistentPersonaQueryAgent(PersonaQueryAgent)
```

Persona query agent backed by persistent storage.

---

## persistent_kgent

```python
def persistent_kgent(namespace: str='kgent_persona', initial_state: Optional[PersonaState]=None, data_dir: Path | None=None) -> PersistentPersonaAgent
```

Create a persistent K-gent dialogue agent.

---

## persistent_query_persona

```python
def persistent_query_persona(namespace: str='kgent_persona_query', initial_state: Optional[PersonaState]=None, data_dir: Path | None=None) -> PersistentPersonaQueryAgent
```

Create a persistent persona query agent.

---

## __init__

```python
def __init__(self, namespace: str='kgent_persona', initial_state: Optional[PersonaState]=None, auto_save: bool=True, data_dir: Path | None=None, preferred_backend: Backend=Backend.SQLITE)
```

Initialize persistent persona agent.

---

## load_state

```python
async def load_state(self) -> None
```

Load persona state from storage.

---

## save_state

```python
async def save_state(self) -> None
```

Persist current persona state to storage.

---

## invoke

```python
async def invoke(self, input: DialogueInput) -> DialogueOutput
```

Engage in dialogue and optionally persist state changes.

---

## get_evolution_history

```python
async def get_evolution_history(self, limit: int=10) -> list[PersonaState]
```

Get history of persona state changes via causal chain.

---

## update_preference

```python
def update_preference(self, category: str, key: str, value: Any, confidence: float=0.9, source: str='explicit') -> None
```

Update a persona preference with tracking.

---

## __init__

```python
def __init__(self, namespace: str='kgent_persona_query', initial_state: Optional[PersonaState]=None, data_dir: Path | None=None, preferred_backend: Backend=Backend.SQLITE)
```

Initialize persistent query agent.

---

## load_state

```python
async def load_state(self) -> None
```

Load persona state from storage.

---

## save_state

```python
async def save_state(self) -> None
```

Persist current persona state.

---

## agents.k.persona

## persona

```python
module persona
```

K-gent Persona: The interactive persona model.

---

## Maybe

```python
class Maybe(Generic[A])
```

Maybe monad for graceful degradation.

---

## DialogueMode

```python
class DialogueMode(Enum)
```

The four dialogue modes of K-gent.

---

## PersonaSeed

```python
class PersonaSeed
```

The irreducible seed of K-gent.

---

## PersonaState

```python
class PersonaState
```

Full persona state including context and confidence.

---

## PersonaQuery

```python
class PersonaQuery
```

Query to K-gent for preferences/patterns.

---

## PersonaResponse

```python
class PersonaResponse
```

Response to a persona query.

---

## DialogueInput

```python
class DialogueInput
```

Input for K-gent dialogue.

---

## DialogueOutput

```python
class DialogueOutput
```

Output from K-gent dialogue.

---

## PersonaQueryAgent

```python
class PersonaQueryAgent(Agent[PersonaQuery, PersonaResponse])
```

Query K-gent's preferences and patterns.

---

## KgentAgent

```python
class KgentAgent(Agent[DialogueInput, DialogueOutput])
```

The main K-gent dialogue agent.

---

## kgent

```python
def kgent(state: Optional[PersonaState]=None) -> KgentAgent
```

Create a K-gent dialogue agent.

---

## query_persona

```python
def query_persona(state: Optional[PersonaState]=None) -> PersonaQueryAgent
```

Create a persona query agent.

---

## just

```python
def just(value: A) -> 'Maybe[A]'
```

Create a Maybe with a value.

---

## nothing

```python
def nothing(error: str='No value') -> 'Maybe[A]'
```

Create an empty Maybe with error context.

---

## value_or

```python
def value_or(self, default: A) -> A
```

Get value or return default.

---

## map

```python
def map(self, f: Callable[[A], Any]) -> 'Maybe[Any]'
```

Apply function if value exists.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'PersonaSeed'
```

Create from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'PersonaState'
```

Create from dictionary.

---

## invoke

```python
async def invoke(self, query: PersonaQuery) -> PersonaResponse
```

Query preferences and patterns with Maybe wrapper.

---

## invoke_safe

```python
def invoke_safe(self, query: PersonaQuery) -> Maybe[PersonaResponse]
```

Safe query that returns Maybe for composition.

---

## __init__

```python
def __init__(self, state: Optional[PersonaState]=None, llm: Optional['LLMClient']=None, eigenvectors: Optional['KentEigenvectors']=None)
```

Initialize K-gent agent.

---

## has_llm

```python
def has_llm(self) -> bool
```

Check if LLM is configured.

---

## set_llm

```python
def set_llm(self, llm: 'LLMClient') -> None
```

Set the LLM client.

---

## set_eigenvectors

```python
def set_eigenvectors(self, eigenvectors: 'KentEigenvectors') -> None
```

Set the eigenvectors.

---

## invoke

```python
async def invoke(self, input: DialogueInput) -> DialogueOutput
```

Engage in dialogue with K-gent.

---

## invoke_stream

```python
async def invoke_stream(self, input: DialogueInput) -> AsyncIterator[tuple[str, bool, int]]
```

Engage in streaming dialogue with K-gent.

---

## agents.k.polynomial

## polynomial

```python
module polynomial
```

K-gent Polynomial: Eigenvector Contexts as Polynomial Positions.

### Examples
```python
>>> agent = SoulPolynomialAgent()
```
```python
>>> response = await agent.query("Should I add this feature?")
```
```python
>>> print(response.context, response.judgment)
```
```python
>>> agent = SoulPolynomialAgent()
```
```python
>>> response = await agent.query("Should I add this feature?")
```

---

## EigenvectorContext

```python
class EigenvectorContext(Enum)
```

Positions in the K-gent polynomial.

---

## SoulQuery

```python
class SoulQuery
```

Input to the K-gent polynomial.

---

## SoulJudgment

```python
class SoulJudgment
```

Output from a single eigenvector context.

---

## SoulResponse

```python
class SoulResponse
```

Full response from K-gent polynomial.

---

## eigenvector_directions

```python
def eigenvector_directions(state: EigenvectorContext) -> FrozenSet[Any]
```

Valid inputs for each eigenvector state.

---

## eigenvector_transition

```python
def eigenvector_transition(state: EigenvectorContext, input: Any) -> tuple[EigenvectorContext, Any]
```

Eigenvector state transition function.

---

## to_sheaf_context

```python
def to_sheaf_context(ctx: EigenvectorContext) -> Context | None
```

Map EigenvectorContext to SOUL_SHEAF Context.

---

## from_sheaf_context

```python
def from_sheaf_context(ctx: Context) -> EigenvectorContext | None
```

Map SOUL_SHEAF Context to EigenvectorContext.

---

## SoulPolynomialAgent

```python
class SoulPolynomialAgent
```

Backwards-compatible K-gent polynomial wrapper.

### Examples
```python
>>> agent = SoulPolynomialAgent()
```
```python
>>> response = await agent.query("Should I add this feature?")
```
```python
>>> print(response.primary_context.name, response.synthesis)
```

---

## state

```python
def state(self) -> EigenvectorContext
```

Current eigenvector context.

---

## set_context

```python
def set_context(self, ctx: EigenvectorContext) -> None
```

Set the current context.

---

## query

```python
async def query(self, message: str, context: EigenvectorContext | None=None, depth: int=1) -> SoulResponse
```

Query the soul polynomial.

---

## query_all

```python
async def query_all(self, message: str) -> SoulResponse
```

Query all eigenvector contexts and synthesize.

---

## query_sheaf

```python
async def query_sheaf(self, message: str) -> dict[str, Any]
```

Query via SOUL_SHEAF for full emergent response.

---

## agents.k.prompts

## prompts

```python
module prompts
```

K-gent Prompts: System prompts for K-gent's various modes of operation.

---

## agents.k.refinements

## refinements

```python
module refinements
```

K-gent 110% Refinements: Domains 5-7.

---

## SoulPath

```python
class SoulPath(str, Enum)
```

AGENTESE paths for self.soul.* namespace.

---

## SoulPathResult

```python
class SoulPathResult
```

Result from invoking a soul path.

---

## SoulPathResolver

```python
class SoulPathResolver
```

Resolver for AGENTESE self.soul.* paths.

---

## SoulErrorSeverity

```python
class SoulErrorSeverity(str, Enum)
```

Severity levels for soul errors.

---

## SoulError

```python
class SoulError(Exception)
```

Base error class for K-gent soul errors.

---

## DialogueError

```python
class DialogueError(SoulError)
```

Error in dialogue processing.

---

## EigenvectorError

```python
class EigenvectorError(SoulError)
```

Error in eigenvector processing.

---

## GardenError

```python
class GardenError(SoulError)
```

Error in persona garden.

---

## HypnagogiaError

```python
class HypnagogiaError(SoulError)
```

Error in hypnagogia/dream processing.

---

## GracefulDegradation

```python
class GracefulDegradation
```

Graceful degradation handler for K-gent.

---

## FractalNode

```python
class FractalNode
```

A node in the fractal expansion tree.

---

## FractalExpander

```python
class FractalExpander
```

Fractal expansion of ideas.

---

## ConstitutionArticle

```python
class ConstitutionArticle
```

An article in the holographic constitution.

---

## HolographicConstitution

```python
class HolographicConstitution
```

Holographic constitution for K-gent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## __init__

```python
def __init__(self, soul: 'KgentSoul') -> None
```

Initialize resolver.

---

## resolve

```python
async def resolve(self, path: str, observer: str='anonymous', **kwargs: Any) -> SoulPathResult
```

Resolve an AGENTESE path.

---

## __str__

```python
def __str__(self) -> str
```

Format error message.

---

## format_human

```python
def format_human(self) -> str
```

Format error for human consumption.

---

## format_technical

```python
def format_technical(self) -> str
```

Format error for technical logs.

---

## __init__

```python
def __init__(self, message: str, mode: Optional[str]=None) -> None
```

Initialize dialogue error.

---

## __init__

```python
def __init__(self, message: str, eigenvector: str) -> None
```

Initialize eigenvector error.

---

## __init__

```python
def __init__(self, message: str, entry_id: Optional[str]=None) -> None
```

Initialize garden error.

---

## __init__

```python
def __init__(self, message: str, phase: Optional[str]=None) -> None
```

Initialize hypnagogia error.

---

## __init__

```python
def __init__(self) -> None
```

Initialize degradation handler.

---

## record_error

```python
def record_error(self, feature: str, error: Exception) -> None
```

Record an error for a feature.

---

## is_degraded

```python
def is_degraded(self, feature: str) -> bool
```

Check if a feature is degraded.

---

## restore

```python
def restore(self, feature: str) -> bool
```

Attempt to restore a degraded feature.

---

## status

```python
def status(self) -> dict[str, Any]
```

Get degradation status.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## __init__

```python
def __init__(self, max_depth: int=3, branching_factor: int=3) -> None
```

Initialize expander.

---

## expand

```python
async def expand(self, seed: str, soul: Optional['KgentSoul']=None) -> FractalNode
```

Expand a seed idea into a fractal tree.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## __init__

```python
def __init__(self) -> None
```

Initialize constitution.

---

## get_article

```python
def get_article(self, number: int) -> Optional[ConstitutionArticle]
```

Get article by number.

---

## get_by_eigenvector

```python
def get_by_eigenvector(self, eigenvector: str) -> list[ConstitutionArticle]
```

Get articles weighted by an eigenvector.

---

## holographic_lookup

```python
def holographic_lookup(self, query: str, soul: Optional['KgentSoul']=None) -> list[ConstitutionArticle]
```

Holographic lookup - find articles that resonate with query.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize constitution.

---

## agents.k.rumination

## rumination

```python
module rumination
```

Rumination: The Soul's Internal Life.

---

## RuminationConfig

```python
class RuminationConfig
```

Configuration for rumination behavior.

---

## RuminationState

```python
class RuminationState
```

Runtime state for rumination.

---

## generate_thought

```python
def generate_thought(eigenvectors: 'Eigenvectors', recent_pattern: Optional[str]=None) -> tuple[str, int, Optional[str]]
```

Generate a thought based on eigenvector weights.

---

## generate_feeling

```python
def generate_feeling(eigenvectors: 'Eigenvectors', recent_events_count: int) -> tuple[str, float, Optional[str]]
```

Generate a feeling based on soul state.

---

## generate_observation

```python
def generate_observation() -> tuple[str, float, str]
```

Generate an observation.

---

## generate_self_challenge

```python
def generate_self_challenge(eigenvectors: 'Eigenvectors') -> tuple[str, str, Optional[str], str]
```

Generate a self-challenge based on eigenvector tension.

---

## generate_gratitude

```python
def generate_gratitude() -> tuple[str, Optional[str], int]
```

Generate a gratitude expression.

---

## ruminate

```python
async def ruminate(soul: 'KgentSoul', config: Optional[RuminationConfig]=None) -> AsyncIterator[SoulEvent]
```

Generate ambient events from the soul's internal life.

---

## quick_rumination

```python
async def quick_rumination(soul: 'KgentSoul', count: int=5) -> AsyncIterator[SoulEvent]
```

Generate a fixed number of ruminations quickly (for testing).

---

## soul_to_pulse

```python
def soul_to_pulse(soul: 'KgentSoul', phase: str='thinking', recent_content: str='') -> dict[str, Any]
```

Convert KgentSoul state to D-gent Pulse-compatible format.

---

## rumination_to_crystal_task

```python
def rumination_to_crystal_task(events: list['SoulEvent'], description: str='Rumination session') -> dict[str, Any]
```

Convert rumination events to D-gent TaskState format for crystallization.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate and clamp probabilities.

---

## total_probability

```python
def total_probability(self) -> float
```

Sum of all event probabilities.

---

## agents.k.session

## session

```python
module session
```

K-gent Soul Session: Cross-Session Identity.

---

## get_soul_dir

```python
def get_soul_dir() -> Path
```

Get the soul persistence directory.

---

## SoulChange

```python
class SoulChange
```

A proposed or committed change to soul state.

---

## SoulCrystal

```python
class SoulCrystal
```

A checkpoint of soul state.

---

## IntrospectionRecord

```python
class IntrospectionRecord
```

A persisted H-gent introspection output.

---

## DriftReport

```python
class DriftReport
```

Changes between introspections.

---

## SoulHistory

```python
class SoulHistory
```

Who was I? The archaeology of self.

---

## PersistedSoulState

```python
class PersistedSoulState
```

Soul state that persists across sessions.

---

## SoulPersistence

```python
class SoulPersistence
```

Soul persistence layer.

---

## SoulSession

```python
class SoulSession
```

Cross-session soul identity.

---

## load_session

```python
async def load_session(soul_dir: Optional[Path]=None) -> SoulSession
```

Load or create a soul session.

---

## quick_dialogue

```python
async def quick_dialogue(message: str, mode: Optional[DialogueMode]=None) -> str
```

Quick dialogue without managing session.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> SoulChange
```

Deserialize from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> SoulCrystal
```

Deserialize from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> IntrospectionRecord
```

Deserialize from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> DriftReport
```

Deserialize from dictionary.

---

## is_stable

```python
def is_stable(self) -> bool
```

Check if the drift indicates stability.

---

## summary

```python
def summary(self) -> str
```

Generate human-readable drift summary.

---

## add_change

```python
def add_change(self, change: SoulChange) -> None
```

Add a change to history.

---

## add_crystal

```python
def add_crystal(self, crystal: SoulCrystal) -> None
```

Add a crystal to history.

---

## pending_changes

```python
def pending_changes(self) -> list[SoulChange]
```

Get pending (unapproved) changes.

---

## committed_changes

```python
def committed_changes(self) -> list[SoulChange]
```

Get committed changes.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> SoulHistory
```

Deserialize from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> PersistedSoulState
```

Deserialize from dictionary.

---

## __init__

```python
def __init__(self, soul_dir: Optional[Path]=None) -> None
```

Initialize persistence.

---

## exists

```python
def exists(self) -> bool
```

Check if persisted soul state exists.

---

## load_state

```python
def load_state(self) -> Optional[PersistedSoulState]
```

Load persisted soul state.

---

## save_state

```python
def save_state(self, state: PersistedSoulState) -> None
```

Save soul state.

---

## load_history

```python
def load_history(self) -> SoulHistory
```

Load soul history.

---

## save_history

```python
def save_history(self, history: SoulHistory) -> None
```

Save soul history.

---

## save_crystal

```python
def save_crystal(self, crystal: SoulCrystal) -> None
```

Save a soul crystal checkpoint.

---

## load_crystal

```python
def load_crystal(self, crystal_id: str) -> Optional[SoulCrystal]
```

Load a soul crystal by ID.

---

## list_crystals

```python
def list_crystals(self) -> list[str]
```

List all crystal IDs.

---

## load_introspections

```python
def load_introspections(self) -> list[IntrospectionRecord]
```

Load all introspection records.

---

## save_introspections

```python
def save_introspections(self, records: list[IntrospectionRecord]) -> None
```

Save all introspection records.

---

## get_introspections_by_type

```python
def get_introspections_by_type(self, introspection_type: IntrospectionType) -> list[IntrospectionRecord]
```

Get introspections filtered by type, sorted newest first.

---

## get_latest_introspection

```python
def get_latest_introspection(self, introspection_type: IntrospectionType) -> Optional[IntrospectionRecord]
```

Get the most recent introspection of a given type.

---

## __init__

```python
def __init__(self, soul: KgentSoul, persistence: SoulPersistence, history: SoulHistory, persisted_state: Optional[PersistedSoulState]=None, nphase_session: Optional['NPhaseSession']=None) -> None
```

Initialize session.

---

## soul

```python
def soul(self) -> KgentSoul
```

Get the underlying soul.

---

## history

```python
def history(self) -> SoulHistory
```

Get soul history.

---

## is_first_session

```python
def is_first_session(self) -> bool
```

Check if this is the first session.

---

## pending_changes

```python
def pending_changes(self) -> list[SoulChange]
```

Get pending changes.

---

## nphase_session

```python
def nphase_session(self) -> Optional['NPhaseSession']
```

Get the optional N-Phase session for phase tracking.

---

## nphase_session

```python
def nphase_session(self, session: Optional['NPhaseSession']) -> None
```

Set the N-Phase session for phase tracking.

---

## get_nphase_context

```python
def get_nphase_context(self) -> dict[str, Any]
```

Get current N-Phase context for use in dialogue/reflection.

---

## advance_nphase

```python
def advance_nphase(self, target_phase: str, payload: Optional[dict[str, Any]]=None) -> bool
```

Advance N-Phase session to target phase.

---

## load

```python
async def load(cls, soul_dir: Optional[Path]=None, nphase_session: Optional['NPhaseSession']=None) -> SoulSession
```

Load or create a soul session.

---

## dialogue

```python
async def dialogue(self, message: str, mode: Optional[DialogueMode]=None, budget: BudgetTier=BudgetTier.DIALOGUE) -> SoulDialogueOutput
```

Engage in dialogue with K-gent.

---

## propose_change

```python
async def propose_change(self, description: str, aspect: str='behavior', current_value: Any=None, proposed_value: Any=None) -> SoulChange
```

K-gent proposes a change to itself.

---

## commit_change

```python
async def commit_change(self, change_id: str, felt_sense: Optional[str]=None) -> bool
```

User approves and commits a change.

---

## revert_change

```python
async def revert_change(self, change_id: str) -> bool
```

Revert a committed change.

---

## reflect

```python
async def reflect(self, topic: Optional[str]=None) -> SoulDialogueOutput
```

K-gent reflects on its recent changes and growth.

---

## crystallize

```python
async def crystallize(self, name: str, reason: str='') -> SoulCrystal
```

Crystallize current soul state as a checkpoint.

---

## resume_crystal

```python
async def resume_crystal(self, crystal_id: str) -> bool
```

Resume from a crystallized state.

---

## manifest

```python
def manifest(self) -> dict[str, Any]
```

Get current soul state.

---

## who_was_i

```python
def who_was_i(self, limit: int=10) -> list[dict[str, Any]]
```

Get soul history - who was I?

---

## record_introspection

```python
async def record_introspection(self, introspection_type: IntrospectionType, data: IntrospectionData, self_image: str='', tags: list[str] | None=None) -> IntrospectionRecord
```

Record an H-gent introspection for drift tracking.

---

## compute_drift

```python
async def compute_drift(self, introspection_type: IntrospectionType, current_data: IntrospectionData) -> Optional[DriftReport]
```

Compare current introspection to the most recent saved one.

---

## get_introspection_history

```python
async def get_introspection_history(self, introspection_type: IntrospectionType, limit: int=10) -> list[IntrospectionRecord]
```

Get history of introspections for a type.

---

## latest_shadow

```python
def latest_shadow(self) -> Optional[IntrospectionRecord]
```

Get the most recent shadow introspection.

---

## latest_archetype

```python
def latest_archetype(self) -> Optional[IntrospectionRecord]
```

Get the most recent archetype introspection.

---

## latest_mirror

```python
def latest_mirror(self) -> Optional[IntrospectionRecord]
```

Get the most recent mirror introspection.

---

## agents.k.soul

## soul

```python
module soul
```

K-gent Soul: The Middleware of Consciousness.

### Things to Know

🚨 **Critical:** Budget tiers are NOT just token limits - they gate LLM access entirely. DORMANT and WHISPER never call the LLM; they use templates. Set budget=BudgetTier.DIALOGUE to actually invoke the LLM.
  - *Verified in: `test_soul.py::test_soul_dialogue_template - templates bypass LLM`*

ℹ️ Auto-LLM creation spawns subprocesses which are SLOW in tests. Set KGENTS_NO_AUTO_LLM=1 or pass auto_llm=False in test fixtures. The test suite does this via environment variable.
  - *Verified in: `test_soul.py::TestLLMDialogue - uses auto_llm=False`*

ℹ️ Empty/whitespace messages return templates, NOT errors. This is intentional graceful degradation - "What's on your mind?" Do not rely on dialogue() to validate user input.
  - *Verified in: `test_soul.py::test_soul_dialogue_empty_message`*

🚨 **Critical:** intercept_deep() ALWAYS escalates dangerous operations regardless of LLM recommendations. The DANGEROUS_KEYWORDS set is hardcoded and cannot be overridden. This is a safety invariant.
  - *Verified in: `test_soul.py::test_deep_intercept_dangerous_operation`*

ℹ️ Low LLM confidence (< 0.7) forces escalation even if LLM says "approve". This prevents overconfident auto-approval of ambiguous operations.
  - *Verified in: `test_soul.py::test_deep_intercept_low_confidence_escalates`*

ℹ️ Without LLM, intercept_deep() silently falls back to shallow intercept. Check result.was_deep to know which path was taken.
  - *Verified in: `test_soul.py::test_deep_intercept_fallback_without_llm`*

---

## BudgetTier

```python
class BudgetTier(Enum)
```

Token budget tiers for K-gent responses.

---

## BudgetConfig

```python
class BudgetConfig
```

Configuration for K-gent budget tiers.

---

## SoulState

```python
class SoulState
```

Current K-gent soul state.

---

## InterceptResult

```python
class InterceptResult
```

Result from K-gent semaphore interception.

---

## SoulDialogueOutput

```python
class SoulDialogueOutput(DialogueOutput)
```

Extended dialogue output with soul metadata.

---

## KgentSoul

```python
class KgentSoul
```

K-gent Soul: The Middleware of Consciousness.

---

## create_soul

```python
def create_soul(persona_state: Optional[PersonaState]=None, eigenvectors: Optional[KentEigenvectors]=None) -> KgentSoul
```

Create a K-gent Soul instance.

---

## soul

```python
def soul() -> KgentSoul
```

Create a default K-gent Soul instance.

---

## tier_for_tokens

```python
def tier_for_tokens(self, tokens: int) -> BudgetTier
```

Determine tier based on token count.

---

## is_fresh_session

```python
def is_fresh_session(self) -> bool
```

Check if this is a fresh session.

---

## __init__

```python
def __init__(self, persona_state: Optional[PersonaState]=None, eigenvectors: Optional[KentEigenvectors]=None, budget_config: Optional[BudgetConfig]=None, llm: Optional[LLMClient]=None, auto_llm: bool=True) -> None
```

Initialize K-gent Soul.

---

## eigenvectors

```python
def eigenvectors(self) -> KentEigenvectors
```

Get personality eigenvectors.

---

## active_mode

```python
def active_mode(self) -> DialogueMode
```

Get current dialogue mode.

---

## active_mode

```python
def active_mode(self, mode: DialogueMode) -> None
```

Set current dialogue mode.

---

## has_llm

```python
def has_llm(self) -> bool
```

Check if LLM is configured.

---

## audit

```python
def audit(self) -> 'AuditTrail'
```

Get the audit trail, creating if necessary.

---

## set_llm

```python
def set_llm(self, llm: LLMClient) -> None
```

Set the LLM client.

---

## dialogue

```python
async def dialogue(self, message: str, mode: Optional[DialogueMode]=None, budget: BudgetTier=BudgetTier.DIALOGUE, on_chunk: Optional[Callable[[str], None]]=None) -> SoulDialogueOutput
```

Engage in dialogue with K-gent Soul.

---

## dialogue_flux

```python
def dialogue_flux(self, message: str, mode: Optional[DialogueMode]=None, budget: BudgetTier=BudgetTier.DIALOGUE) -> 'FluxStream[str]'
```

Engage in dialogue with K-gent Soul via Flux streaming.

---

## intercept

```python
async def intercept(self, token: Any) -> InterceptResult
```

Intercept a semaphore token for potential auto-resolution.

---

## intercept_deep

```python
async def intercept_deep(self, token: Any) -> InterceptResult
```

Deep intercept using LLM-backed principle reasoning.

---

## manifest

```python
def manifest(self) -> SoulState
```

Get current soul state.

---

## manifest_brief

```python
def manifest_brief(self) -> dict[str, Any]
```

Get brief soul state for display.

---

## get_starter

```python
def get_starter(self, mode: Optional[DialogueMode]=None) -> str
```

Get a random starter prompt for the given mode.

---

## get_all_starters

```python
def get_all_starters(self, mode: Optional[DialogueMode]=None) -> list[str]
```

Get all starter prompts for the given mode.

---

## format_starters

```python
def format_starters(self, mode: Optional[DialogueMode]=None) -> str
```

Format starter prompts for CLI display.

---

## enter_mode

```python
def enter_mode(self, mode: DialogueMode) -> str
```

Enter a dialogue mode and return entry message.

---

## agents.k.soul_cache

## soul_cache

```python
module soul_cache
```

**AGENTESE:** `self.soul.reflex`

SoulCache: Redis-backed soul state caching.

---

## CacheClient

```python
class CacheClient(Protocol)
```

Protocol for Redis-like cache operations.

---

## SoulCacheConfig

```python
class SoulCacheConfig
```

Configuration for the soul cache.

---

## CachedSessionState

```python
class CachedSessionState
```

Session state stored in cache.

---

## CachedEigenvectors

```python
class CachedEigenvectors
```

Eigenvector confidences stored in cache.

---

## CachedActiveMode

```python
class CachedActiveMode
```

Active dialogue mode stored in cache.

---

## MockCacheClient

```python
class MockCacheClient
```

In-memory mock Redis client for testing.

---

## RedisCacheClient

```python
class RedisCacheClient
```

Real Redis client implementation.

---

## SoulCache

```python
class SoulCache
```

Redis-backed soul state cache.

### Examples
```python
>>> cache = await SoulCache.create()
```
```python
>>> await cache.cache_session(session_id, state)
```
```python
>>> state = await cache.get_session(session_id)
```

---

## get_soul_cache

```python
async def get_soul_cache(config: SoulCacheConfig | None=None) -> SoulCache
```

Get or create the global SoulCache instance.

---

## close_soul_cache

```python
async def close_soul_cache() -> None
```

Close the global SoulCache instance.

---

## get

```python
async def get(self, key: str) -> str | None
```

Get value by key.

---

## set

```python
async def set(self, key: str, value: str, ttl: int | None=None) -> None
```

Set key to value with optional TTL in seconds.

---

## delete

```python
async def delete(self, key: str) -> None
```

Delete a key.

---

## exists

```python
async def exists(self, key: str) -> bool
```

Check if key exists.

---

## expire

```python
async def expire(self, key: str, ttl: int) -> None
```

Set expiry on a key.

---

## ttl

```python
async def ttl(self, key: str) -> int
```

Get TTL of a key in seconds (-1 if no TTL, -2 if doesn't exist).

---

## from_env

```python
def from_env(cls) -> 'SoulCacheConfig'
```

Load configuration from environment.

---

## to_json

```python
def to_json(self) -> str
```

Serialize to JSON.

---

## from_json

```python
def from_json(cls, data: str) -> 'CachedSessionState'
```

Deserialize from JSON.

---

## to_json

```python
def to_json(self) -> str
```

Serialize to JSON.

---

## from_json

```python
def from_json(cls, data: str) -> 'CachedEigenvectors'
```

Deserialize from JSON.

---

## to_json

```python
def to_json(self) -> str
```

Serialize to JSON.

---

## from_json

```python
def from_json(cls, data: str) -> 'CachedActiveMode'
```

Deserialize from JSON.

---

## connect

```python
async def connect(self) -> None
```

Connect to Redis.

---

## close

```python
async def close(self) -> None
```

Close Redis connection.

---

## create

```python
async def create(cls, config: SoulCacheConfig | None=None) -> 'SoulCache'
```

Create a SoulCache with appropriate backend.

---

## cache_session

```python
async def cache_session(self, session_id: str, active_mode: str, interactions_count: int, tokens_used: int, created_at: datetime, last_interaction: datetime | None=None) -> None
```

Cache session state.

---

## get_session

```python
async def get_session(self, session_id: str) -> CachedSessionState | None
```

Get cached session state.

---

## invalidate_session

```python
async def invalidate_session(self, session_id: str) -> None
```

Invalidate cached session state.

---

## touch_session

```python
async def touch_session(self, session_id: str) -> None
```

Extend session TTL without updating content.

---

## cache_eigenvectors

```python
async def cache_eigenvectors(self, soul_id: str, aesthetic: float, categorical: float, collaborative: float, ethical: float, joyful: float, tasteful: float) -> None
```

Cache eigenvector confidences.

---

## get_eigenvectors

```python
async def get_eigenvectors(self, soul_id: str) -> CachedEigenvectors | None
```

Get cached eigenvector confidences.

---

## invalidate_eigenvectors

```python
async def invalidate_eigenvectors(self, soul_id: str) -> None
```

Invalidate cached eigenvectors.

---

## cache_mode

```python
async def cache_mode(self, session_id: str, mode: str, reason: str | None=None) -> None
```

Cache active dialogue mode.

---

## get_mode

```python
async def get_mode(self, session_id: str) -> CachedActiveMode | None
```

Get cached active mode.

---

## invalidate_mode

```python
async def invalidate_mode(self, session_id: str) -> None
```

Invalidate cached mode.

---

## invalidate_all_for_soul

```python
async def invalidate_all_for_soul(self, soul_id: str) -> None
```

Invalidate all cached data for a soul.

---

## ping

```python
async def ping(self) -> bool
```

Check if cache is healthy.

---

## agents.k.starters

## starters

```python
module starters
```

K-gent Starters: Mode-specific starter prompts for self-dialogue.

---

## get_starters

```python
def get_starters(mode: 'DialogueMode') -> list[str]
```

Get all starter prompts for a dialogue mode.

---

## random_starter

```python
def random_starter(mode: 'DialogueMode') -> str
```

Get a random starter prompt for a dialogue mode.

---

## all_starters

```python
def all_starters() -> dict[str, list[str]]
```

Get all starters organized by mode name.

---

## format_starters_for_display

```python
def format_starters_for_display(mode: 'DialogueMode') -> str
```

Format starters for CLI display.

---

## format_all_starters_for_display

```python
def format_all_starters_for_display() -> str
```

Format all starters for CLI display.

---

## ModePersonality

```python
class ModePersonality
```

Personality traits for each dialogue mode (110% Domain 4).

---

## get_personality

```python
def get_personality(mode: 'DialogueMode') -> ModePersonality
```

Get personality for a dialogue mode.

---

## DynamicStarterGenerator

```python
class DynamicStarterGenerator
```

Generate contextual starters based on recent activity (110% Domain 4).

---

## RichOutput

```python
class RichOutput
```

Rich output for dialogue responses (110% Domain 4).

---

## get_personality_from_mode_name

```python
def get_personality_from_mode_name(mode_name: str) -> ModePersonality
```

Get personality from mode name string.

---

## format_response

```python
def format_response(self, response: str) -> str
```

Apply personality formatting to a response.

---

## __init__

```python
def __init__(self) -> None
```

Initialize generator.

---

## record_topic

```python
def record_topic(self, topic: str) -> None
```

Record a topic from recent dialogue.

---

## generate

```python
def generate(self, mode: 'DialogueMode', context: Optional[dict[str, Any]]=None) -> str
```

Generate a contextual starter.

---

## format_plain

```python
def format_plain(self) -> str
```

Format as plain text.

---

## format_rich

```python
def format_rich(self) -> str
```

Format with personality and styling.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## agents.k.templates

## templates

```python
module templates
```

K-gent Templates: Zero-token responses for cost-conscious operation.

---

## try_template_response

```python
def try_template_response(input_text: str, mode: Optional['DialogueMode']=None) -> Optional[str]
```

Attempt to respond without LLM call.

---

## get_whisper_response

```python
def get_whisper_response(input_text: str) -> str
```

Generate a WHISPER-level response (~100 tokens).

---

## should_use_template

```python
def should_use_template(input_text: str) -> bool
```

Check if input can be handled by template (no LLM needed).

---

## agents.k.watcher

## watcher

```python
module watcher
```

K-gent File Watcher: Ambient pair programming presence.

---

## FileEvent

```python
class FileEvent(Protocol)
```

Protocol for file system events.

---

## SimpleFileEvent

```python
class SimpleFileEvent
```

Simple implementation of FileEvent for testing/fallback.

---

## HeuristicResult

```python
class HeuristicResult
```

Result from a heuristic check.

---

## Heuristic

```python
class Heuristic(Protocol)
```

Protocol for watch heuristics.

---

## ComplexityHeuristic

```python
class ComplexityHeuristic
```

Detects functions that are getting too complex.

---

## NamingHeuristic

```python
class NamingHeuristic
```

Detects poor variable naming (single letters, unclear names).

---

## PatternHeuristic

```python
class PatternHeuristic
```

Detects common design patterns that might need naming.

---

## TestsHeuristic

```python
class TestsHeuristic
```

Detects code that might need tests.

---

## DocsHeuristic

```python
class DocsHeuristic
```

Detects undocumented public functions and classes.

---

## WatcherConfig

```python
class WatcherConfig
```

Configuration for the K-gent watcher.

---

## WatchNotification

```python
class WatchNotification
```

A notification from the watcher.

---

## KgentWatcher

```python
class KgentWatcher
```

K-gent File Watcher: Ambient pair programming presence.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check if this heuristic applies to the given path.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Run the heuristic check and return result.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check Python files.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Check function lengths in the file.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check Python files.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Check for poor variable naming.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check Python files.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Check for design patterns.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check non-test Python files.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Check for untested code.

---

## matches

```python
def matches(self, path: str, content: str | None=None) -> bool
```

Check Python files.

---

## check

```python
def check(self, path: str, content: str | None=None) -> HeuristicResult
```

Check for missing docstrings.

---

## from_file

```python
def from_file(cls, path: Path) -> 'WatcherConfig'
```

Load config from YAML file.

---

## __init__

```python
def __init__(self, config: WatcherConfig | None=None, project_root: Path | str | None=None) -> None
```

Initialize the watcher.

---

## subscribe

```python
def subscribe(self, callback: Callable[[WatchNotification], None]) -> None
```

Subscribe to notifications.

---

## unsubscribe

```python
def unsubscribe(self, callback: Callable[[WatchNotification], None]) -> None
```

Unsubscribe from notifications.

---

## start

```python
async def start(self) -> None
```

Start watching for file changes.

---

## stop

```python
async def stop(self) -> None
```

Stop watching for file changes.

---

## running

```python
def running(self) -> bool
```

Check if watcher is running.

---

## notifications

```python
def notifications(self) -> list[WatchNotification]
```

Get all notifications.

---

## recent_notifications

```python
def recent_notifications(self, limit: int=10) -> list[WatchNotification]
```

Get recent notifications.

---

## clear_notifications

```python
def clear_notifications(self) -> None
```

Clear notification history.

---

## agents.m.__init__

## __init__

```python
module __init__
```

M-gents: Memory Agents for intelligent recall.

---

## agents.m.associative

## associative

```python
module associative
```

AssociativeMemory: Semantic Similarity Search

---

## HashEmbedder

```python
class HashEmbedder
```

Hash-based pseudo-embedder (fallback when L-gent unavailable).

---

## AssociativeMemory

```python
class AssociativeMemory
```

Memory with semantic similarity search.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Generate hash-based pseudo-embedding.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize default embedder if not provided.

---

## create_with_vgent

```python
async def create_with_vgent(cls, dgent: 'DgentProtocol', vgent: 'VgentProtocol', embedder: Embedder | None=None) -> 'AssociativeMemory'
```

Create AssociativeMemory with V-gent for vector operations.

---

## has_vgent

```python
def has_vgent(self) -> bool
```

Check if V-gent is configured for vector operations.

---

## remember

```python
async def remember(self, content: bytes, embedding: list[float] | None=None, metadata: dict[str, str] | None=None) -> str
```

Store content as a memory.

---

## recall

```python
async def recall(self, cue: str | list[float], limit: int=5, threshold: float=0.5) -> list[RecallResult]
```

Associative recall by semantic similarity.

---

## forget

```python
async def forget(self, memory_id: str) -> bool
```

Begin graceful forgetting (transition to COMPOSTING).

---

## cherish

```python
async def cherish(self, memory_id: str) -> bool
```

Pin memory from forgetting.

---

## consolidate

```python
async def consolidate(self) -> ConsolidationReport
```

Run consolidation cycle ("sleep").

---

## wake

```python
async def wake(self) -> None
```

End consolidation, return DREAMING -> DORMANT.

---

## status

```python
async def status(self) -> MemoryStatus
```

Get current memory system state.

---

## by_lifecycle

```python
async def by_lifecycle(self, lifecycle: Lifecycle) -> list[Memory]
```

Get memories in a specific lifecycle state.

---

## get

```python
async def get(self, memory_id: str) -> Memory | None
```

Get a specific memory by ID.

---

## exists

```python
async def exists(self, memory_id: str) -> bool
```

Check if a memory exists.

---

## count

```python
async def count(self) -> int
```

Count total memories.

---

## decay_all

```python
async def decay_all(self, factor: float=0.99) -> int
```

Apply relevance decay to all non-cherished memories.

---

## degrade_composting

```python
async def degrade_composting(self, factor: float=0.5) -> int
```

Degrade resolution of all COMPOSTING memories.

---

## agents.m.bus_listener

## bus_listener

```python
module bus_listener
```

Bus Listener: Data Bus Integration for M-gent

---

## BusEventHandler

```python
class BusEventHandler
```

Handler for processing Data Bus events.

---

## MgentBusListener

```python
class MgentBusListener
```

Listener that connects M-gent to the Data Bus.

---

## create_bus_listener

```python
def create_bus_listener(mgent: 'AssociativeMemory', bus: 'DataBus', auto_index: bool=True, auto_remove: bool=True, embedder: Callable[[str], Awaitable[list[float]]] | None=None) -> MgentBusListener
```

Create a bus listener for M-gent.

---

## handle_put

```python
async def handle_put(self, event: 'DataEvent', mgent: 'AssociativeMemory') -> None
```

Handle PUT event - new datum stored.

---

## handle_delete

```python
async def handle_delete(self, event: 'DataEvent', mgent: 'AssociativeMemory') -> None
```

Handle DELETE event - datum removed.

---

## handle_upgrade

```python
async def handle_upgrade(self, event: 'DataEvent', mgent: 'AssociativeMemory') -> None
```

Handle UPGRADE event - datum promoted to higher tier.

---

## handle_degrade

```python
async def handle_degrade(self, event: 'DataEvent', mgent: 'AssociativeMemory') -> None
```

Handle DEGRADE event - datum demoted.

---

## start

```python
def start(self) -> None
```

Start listening to Data Bus events.

---

## stop

```python
def stop(self) -> None
```

Stop listening to Data Bus events.

---

## is_running

```python
def is_running(self) -> bool
```

Check if listener is currently active.

---

## replay_and_index

```python
async def replay_and_index(self, since: float | None=None) -> int
```

Replay buffered events and index any missed data.

---

## agents.m.consolidation_engine

## consolidation_engine

```python
module consolidation_engine
```

ConsolidationEngine: Memory Sleep Cycles

---

## ConsolidationConfig

```python
class ConsolidationConfig
```

Configuration for consolidation behavior.

---

## ConsolidationStats

```python
class ConsolidationStats
```

Statistics from a consolidation cycle.

---

## ConsolidationEngine

```python
class ConsolidationEngine
```

Engine for memory consolidation ("sleep" cycles).

---

## create_consolidation_engine

```python
def create_consolidation_engine(mgent: 'AssociativeMemory', aggressive: bool=False) -> ConsolidationEngine
```

Create a consolidation engine with sensible defaults.

---

## add_listener

```python
def add_listener(self, listener: Callable[[LifecycleEvent], Awaitable[None] | None]) -> None
```

Add a listener for lifecycle events during consolidation.

---

## remove_listener

```python
def remove_listener(self, listener: Callable[[LifecycleEvent], Awaitable[None] | None]) -> None
```

Remove a listener.

---

## consolidate

```python
async def consolidate(self) -> ConsolidationReport
```

Run a full consolidation cycle.

---

## agents.m.importers.__init__

## __init__

```python
module __init__
```

M-gent Importers: Convert external knowledge sources to MemoryCrystal engrams.

---

## agents.m.importers.markdown

## markdown

```python
module markdown
```

Markdown Importer: Parse Obsidian/Notion markdown into MemoryCrystal engrams.

---

## FrontmatterData

```python
class FrontmatterData(TypedDict)
```

Typed dictionary for parsed frontmatter.

---

## WikiLink

```python
class WikiLink
```

A parsed wiki link from markdown.

---

## MarkdownEngram

```python
class MarkdownEngram
```

A knowledge unit extracted from markdown, ready for Crystal storage.

---

## ImportProgress

```python
class ImportProgress
```

Track progress during batch import.

---

## extract_frontmatter

```python
def extract_frontmatter(content: str) -> tuple[FrontmatterData, str]
```

Extract YAML frontmatter from markdown content.

### Examples
```python
>>> fm, body = extract_frontmatter('''---
```
```python
>>> fm['title']
```

---

## extract_wikilinks

```python
def extract_wikilinks(content: str) -> list[WikiLink]
```

Extract all wiki links from markdown content.

### Examples
```python
>>> links = extract_wikilinks("See [[Python]] and [[ML|Machine Learning]]")
```
```python
>>> [l.target for l in links]
```

---

## extract_tags

```python
def extract_tags(content: str) -> list[str]
```

Extract all #tags from markdown content.

### Examples
```python
>>> extract_tags("This is #python and #data/science")
```

---

## extract_headings

```python
def extract_headings(content: str) -> list[tuple[int, str]]
```

Extract all headings from markdown content.

### Examples
```python
>>> extract_headings("# Title\n## Subtitle")
```

---

## extract_code_blocks

```python
def extract_code_blocks(content: str) -> list[tuple[str, str]]
```

Extract fenced code blocks from markdown.

### Examples
```python
>>> blocks = extract_code_blocks("```python\nprint('hi')\n```")
```
```python
>>> blocks[0]
```

---

## strip_markdown_formatting

```python
def strip_markdown_formatting(content: str) -> str
```

Remove markdown formatting for plain text extraction.

---

## parse_markdown

```python
def parse_markdown(content: str, source_path: Path | None=None) -> MarkdownEngram
```

Parse markdown content into a MarkdownEngram.

---

## ObsidianVaultParser

```python
class ObsidianVaultParser
```

Parse an Obsidian vault into MarkdownEngrams.

---

## MarkdownImporter

```python
class MarkdownImporter
```

Batch import markdown files into a MemoryCrystal.

---

## create_lgent_embedder

```python
def create_lgent_embedder() -> Callable[[str], list[float]] | None
```

Create an L-gent embedder if available.

---

## create_importer_with_best_embedder

```python
def create_importer_with_best_embedder(crystal: Any, prefer: str='sentence-transformers', batch_size: int=100, on_progress: Callable[[ImportProgress], None] | None=None) -> MarkdownImporter
```

Create a MarkdownImporter with the best available embedder.

---

## generate_concept_id

```python
def generate_concept_id(text: str | None=None, path: Path | None=None) -> str
```

Generate a unique concept ID.

---

## display

```python
def display(self) -> str
```

Text to display for this link.

---

## word_count

```python
def word_count(self) -> int
```

Approximate word count of content.

---

## link_count

```python
def link_count(self) -> int
```

Number of outgoing wiki links.

---

## tag_list

```python
def tag_list(self) -> list[str]
```

All tags, both from frontmatter and inline.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## percent_complete

```python
def percent_complete(self) -> float
```

Percentage of files processed.

---

## is_complete

```python
def is_complete(self) -> bool
```

Whether all files have been processed.

---

## __init__

```python
def __init__(self, vault_path: str | Path, skip_folders: set[str] | None=None, skip_patterns: set[str] | None=None, include_daily_notes: bool=True, include_templates: bool=False) -> None
```

Initialize the vault parser.

---

## discover_files

```python
def discover_files(self) -> list[Path]
```

Discover all markdown files in the vault.

---

## parse_file

```python
def parse_file(self, path: Path) -> MarkdownEngram
```

Parse a single markdown file.

---

## parse_all

```python
def parse_all(self) -> Iterator[MarkdownEngram]
```

Parse all markdown files in the vault.

---

## parse_folder

```python
def parse_folder(self, folder_name: str) -> Iterator[MarkdownEngram]
```

Parse markdown files in a specific folder.

---

## get_link_graph

```python
def get_link_graph(self) -> dict[str, set[str]]
```

Build a graph of links between notes.

---

## get_tag_index

```python
def get_tag_index(self) -> dict[str, set[str]]
```

Build an index of tags to concept_ids.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get vault statistics.

---

## __init__

```python
def __init__(self, crystal: Any, embedder: Callable[[str], list[float]] | None=None, batch_size: int=100, on_progress: Callable[[ImportProgress], None] | None=None) -> None
```

Initialize the importer.

---

## import_vault

```python
def import_vault(self, vault_path: str | Path, **parser_kwargs: Any) -> ImportProgress
```

Import an entire Obsidian vault.

---

## import_files

```python
def import_files(self, file_paths: list[Path]) -> ImportProgress
```

Import a list of specific markdown files.

---

## import_content

```python
def import_content(self, content: str, concept_id: str | None=None, source_path: Path | None=None) -> MarkdownEngram
```

Import a single markdown string.

---

## agents.m.lifecycle

## lifecycle

```python
module lifecycle
```

Lifecycle: Memory State Machine

---

## LifecycleEvent

```python
class LifecycleEvent
```

Event emitted when a memory transitions between lifecycle states.

---

## TimeoutPolicy

```python
class TimeoutPolicy
```

Policy: ACTIVE -> DORMANT after inactivity period.

---

## RelevancePolicy

```python
class RelevancePolicy
```

Policy: Manage relevance decay and demotion.

---

## ResolutionPolicy

```python
class ResolutionPolicy
```

Policy: Graceful degradation in COMPOSTING state.

---

## LifecycleManager

```python
class LifecycleManager
```

Manages memory lifecycle transitions.

---

## is_valid_transition

```python
def is_valid_transition(from_state: Lifecycle, to_state: Lifecycle) -> bool
```

Check if a lifecycle transition is valid.

---

## is_demotion

```python
def is_demotion(self) -> bool
```

Is this a demotion (toward COMPOSTING)?

---

## is_promotion

```python
def is_promotion(self) -> bool
```

Is this a promotion (toward ACTIVE)?

---

## should_deactivate

```python
def should_deactivate(self, memory: Memory, now: float | None=None) -> bool
```

Check if memory should transition to DORMANT.

---

## should_demote

```python
def should_demote(self, memory: Memory) -> bool
```

Check if memory should be demoted to COMPOSTING.

---

## apply_decay

```python
def apply_decay(self, memory: Memory) -> Memory
```

Apply relevance decay to a memory.

---

## should_degrade

```python
def should_degrade(self, memory: Memory) -> bool
```

Check if memory should be degraded.

---

## apply_degradation

```python
def apply_degradation(self, memory: Memory) -> Memory
```

Apply resolution degradation to a memory.

---

## add_listener

```python
def add_listener(self, listener: Callable[[LifecycleEvent], None]) -> None
```

Add a listener for lifecycle events.

---

## remove_listener

```python
def remove_listener(self, listener: Callable[[LifecycleEvent], None]) -> None
```

Remove a listener.

---

## evaluate

```python
def evaluate(self, memory: Memory, now: float | None=None) -> LifecycleEvent | None
```

Evaluate if memory should transition states.

---

## apply

```python
def apply(self, memory: Memory, target_state: Lifecycle) -> Memory
```

Apply a lifecycle transition.

---

## apply_policies

```python
def apply_policies(self, memory: Memory) -> Memory
```

Apply all applicable policies to a memory.

---

## batch_evaluate

```python
def batch_evaluate(self, memories: list[Memory], now: float | None=None) -> list[tuple[Memory, LifecycleEvent | None]]
```

Evaluate multiple memories for transitions.

---

## agents.m.memory

## memory

```python
module memory
```

Memory: The Core M-gent Dataclass

---

## Lifecycle

```python
class Lifecycle(Enum)
```

Memory lifecycle states.

---

## Memory

```python
class Memory
```

A Memory is a Datum enriched with semantic meaning and lifecycle.

---

## simple_embedding

```python
def simple_embedding(text: str, dim: int=64) -> tuple[float, ...]
```

Generate simple hash-based embedding (NO semantic similarity).

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate memory fields.

---

## create

```python
def create(cls, datum_id: str, embedding: list[float] | tuple[float, ...], resolution: float=1.0, lifecycle: Lifecycle=Lifecycle.ACTIVE, relevance: float=1.0, metadata: dict[str, str] | None=None) -> Memory
```

Factory method to create a Memory.

---

## activate

```python
def activate(self) -> Memory
```

Transition to ACTIVE state (recall).

---

## deactivate

```python
def deactivate(self) -> Memory
```

Transition to DORMANT state (timeout).

---

## dream

```python
def dream(self) -> Memory
```

Transition to DREAMING state (consolidation).

---

## wake

```python
def wake(self) -> Memory
```

Transition from DREAMING to DORMANT.

---

## compost

```python
def compost(self) -> Memory
```

Transition to COMPOSTING state (forgetting).

---

## degrade

```python
def degrade(self, factor: float=0.5) -> Memory
```

Reduce resolution by factor (graceful degradation).

---

## reinforce

```python
def reinforce(self, boost: float=0.1) -> Memory
```

Increase relevance (reinforcement learning).

---

## decay

```python
def decay(self, factor: float=0.99) -> Memory
```

Decay relevance over time.

---

## cherish

```python
def cherish(self) -> Memory
```

Pin memory from forgetting (max relevance).

---

## is_cherished

```python
def is_cherished(self) -> bool
```

Check if memory is cherished (pinned from forgetting).

---

## similarity

```python
def similarity(self, other_embedding: tuple[float, ...] | list[float]) -> float
```

Compute cosine similarity with another embedding.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize memory to dict for JSON storage.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Memory
```

Deserialize memory from dict.

---

## agents.m.protocol

## protocol

```python
module protocol
```

MgentProtocol: The M-gent Interface

### Things to Know

ℹ️ forget() returns False for cherished memories - they're protected Call cherish() to pin important memories from the forgetting cycle. This is intentional: cherished memories have relevance=1.0 and can't compost.
  - *Verified in: `test_associative.py::TestForget::test_forget_cherished_returns_false`*

ℹ️ recall() reinforces accessed memories (increases access_count) Every recall is a touch - relevance increases through repeated access. This is the stigmergy pattern: use strengthens memory.
  - *Verified in: `test_associative.py::TestRecall::test_recall_reinforces_memory`*

🚨 **Critical:** ACTIVE -> COMPOSTING is INVALID transition (must go through DORMANT) Lifecycle transitions have strict rules. Memory must be DORMANT before it can be demoted to COMPOSTING during consolidation.
  - *Verified in: `test_lifecycle.py::TestValidTransitions::test_active_to_composting_invalid`*

ℹ️ Consolidation applies relevance decay to non-cherished memories only Cherished memories keep relevance=1.0 through sleep cycles. Use cherish() sparingly - it's a commitment to preserve.
  - *Verified in: `test_consolidation_engine.py::TestConsolidationBasic::test_consolidate_protects_cherished`*

ℹ️ similarity() returns 0.0 for mismatched embedding dimensions If you mix embeddings of different sizes, comparisons silently fail. Ensure all embeddings use consistent dimension (e.g., 64 for HashEmbedder).
  - *Verified in: `test_memory.py::TestSimilarity::test_similarity_mismatched_dimensions`*

ℹ️ Memory.embedding is a tuple, not list (converted on creation) Pass list to create(), get tuple back. This ensures hashability.
  - *Verified in: `test_memory.py::TestMemoryCreation::test_embedding_list_to_tuple`*

---

## ConsolidationReport

```python
class ConsolidationReport
```

Report from a consolidation ("sleep") cycle.

---

## MemoryStatus

```python
class MemoryStatus
```

Current state of the memory system.

---

## RecallResult

```python
class RecallResult
```

Result from a recall operation.

---

## MgentProtocol

```python
class MgentProtocol(Protocol)
```

The interface for intelligent memory management.

---

## ExtendedMgentProtocol

```python
class ExtendedMgentProtocol(MgentProtocol, Protocol)
```

Extended protocol with additional convenience methods.

---

## summary

```python
def summary(self) -> str
```

Human-readable summary.

---

## summary

```python
def summary(self) -> str
```

Human-readable summary.

---

## is_strong_match

```python
def is_strong_match(self) -> bool
```

Is this a strong match (>= 0.8 similarity)?

---

## remember

```python
async def remember(self, content: bytes, embedding: list[float] | None=None, metadata: dict[str, str] | None=None) -> str
```

Store content as a memory.

---

## recall

```python
async def recall(self, cue: str | list[float], limit: int=5, threshold: float=0.5) -> list[RecallResult]
```

Associative recall by semantic similarity.

---

## forget

```python
async def forget(self, memory_id: str) -> bool
```

Begin graceful forgetting (transition to COMPOSTING).

---

## cherish

```python
async def cherish(self, memory_id: str) -> bool
```

Pin memory from forgetting (high relevance, won't compost).

---

## consolidate

```python
async def consolidate(self) -> ConsolidationReport
```

Run consolidation cycle ("sleep").

---

## wake

```python
async def wake(self) -> None
```

End consolidation, return DREAMING -> DORMANT.

---

## status

```python
async def status(self) -> MemoryStatus
```

Get current memory system state.

---

## by_lifecycle

```python
async def by_lifecycle(self, lifecycle: Lifecycle) -> list[Memory]
```

Get memories in a specific lifecycle state.

---

## get

```python
async def get(self, memory_id: str) -> Memory | None
```

Get a specific memory by ID.

---

## exists

```python
async def exists(self, memory_id: str) -> bool
```

Check if a memory exists.

---

## count

```python
async def count(self) -> int
```

Count total memories.

---

## decay_all

```python
async def decay_all(self, factor: float=0.99) -> int
```

Apply relevance decay to all non-cherished memories.

---

## degrade_composting

```python
async def degrade_composting(self, factor: float=0.5) -> int
```

Degrade resolution of all COMPOSTING memories.

---

## agents.m.semantic_routing

## semantic_routing

```python
module semantic_routing
```

Semantic Routing: Legacy stub for deleted module.

---

## LocalityConfig

```python
class LocalityConfig
```

DEPRECATED: Old locality configuration.

---

## PrefixSimilarity

```python
class PrefixSimilarity
```

DEPRECATED: Old prefix similarity calculator.

---

## SemanticRouter

```python
class SemanticRouter(Generic[T])
```

DEPRECATED: Old semantic router.

---

## create_semantic_router

```python
def create_semantic_router() -> SemanticRouter[Any]
```

Create a semantic router (DEPRECATED).

---

## calculate

```python
def calculate(self, a: str, b: str) -> float
```

Calculate prefix-based similarity.

---

## route

```python
def route(self, query: str) -> T | None
```

Route a query to the best matching value.

---

## agents.m.soul_memory

## soul_memory

```python
module soul_memory
```

SoulMemory: K-gent Identity Continuity via M-gent

---

## MemoryCategory

```python
class MemoryCategory(Enum)
```

Categories of K-gent memories.

---

## BeliefMemory

```python
class BeliefMemory
```

A cherished belief in K-gent's soul.

---

## ContextMemory

```python
class ContextMemory
```

Session context in K-gent's soul.

---

## PatternMemory

```python
class PatternMemory
```

A behavioral pattern K-gent has observed.

---

## SoulMemory

```python
class SoulMemory
```

K-gent's use of M-gent for identity continuity.

---

## create_soul_memory

```python
def create_soul_memory(mgent: 'AssociativeMemory') -> SoulMemory
```

Create a SoulMemory instance.

---

## is_principle

```python
def is_principle(self) -> bool
```

Is this a core principle?

---

## is_preference

```python
def is_preference(self) -> bool
```

Is this a preference?

---

## remember_belief

```python
async def remember_belief(self, belief: str, tags: list[str] | None=None) -> BeliefMemory
```

Store a core belief (automatically cherished).

---

## get_beliefs

```python
async def get_beliefs(self) -> list[BeliefMemory]
```

Get all cherished beliefs.

---

## reinforce_belief

```python
async def reinforce_belief(self, memory_id: str) -> bool
```

Reinforce a belief (increase its relevance).

---

## remember_pattern

```python
async def remember_pattern(self, pattern: str, initial_relevance: float=0.7) -> PatternMemory
```

Store a behavioral pattern.

---

## reinforce_pattern

```python
async def reinforce_pattern(self, memory_id: str) -> bool
```

Reinforce a pattern (increase frequency + relevance).

---

## get_active_patterns

```python
async def get_active_patterns(self, limit: int=10) -> list[PatternMemory]
```

Get the most active patterns (highest relevance).

---

## remember_context

```python
async def remember_context(self, context: str, session_id: str, initial_relevance: float=0.8) -> ContextMemory
```

Store session context.

---

## get_session_context

```python
async def get_session_context(self, session_id: str, limit: int=20) -> list[ContextMemory]
```

Get context memories for a specific session.

---

## plant_seed

```python
async def plant_seed(self, idea: str, initial_relevance: float=0.4) -> str
```

Plant a creative seed (experimental idea).

---

## grow_seed

```python
async def grow_seed(self, memory_id: str) -> bool
```

Grow a seed (convert to pattern if reinforced enough).

---

## recall_for_topic

```python
async def recall_for_topic(self, topic: str | list[float], limit: int=10, include_seeds: bool=False) -> list[RecallResult]
```

Recall memories relevant to a topic.

---

## recall_beliefs_for_decision

```python
async def recall_beliefs_for_decision(self, decision: str, limit: int=5) -> list[BeliefMemory]
```

Recall beliefs relevant to a decision.

---

## identity_status

```python
async def identity_status(self) -> dict[str, Any]
```

Get status of K-gent's identity memory.

---

## agents.m.stigmergy

## stigmergy

```python
module stigmergy
```

Stigmergic Memory: Coordination via Pheromone Fields.

---

## Trace

```python
class Trace
```

A pheromone trace in the field.

---

## SenseResult

```python
class SenseResult
```

Result of sensing pheromones from a position.

---

## PheromoneField

```python
class PheromoneField
```

Environmental memory via pheromone traces.

---

## StigmergicAgent

```python
class StigmergicAgent
```

Agent that navigates via pheromone gradients.

---

## ConceptSpace

```python
class ConceptSpace(Protocol)
```

Protocol for providing a vocabulary of concepts.

---

## SimpleConceptSpace

```python
class SimpleConceptSpace
```

Simple concept space with predefined vocabulary.

---

## EnhancedStigmergicAgent

```python
class EnhancedStigmergicAgent(StigmergicAgent)
```

Enhanced stigmergic agent with concept space awareness.

---

## create_ant_colony_optimization

```python
async def create_ant_colony_optimization(field: PheromoneField, concept_space: SimpleConceptSpace, ant_count: int=10, iterations: int=100, evaporation_interval: timedelta=timedelta(hours=1)) -> dict[str, float]
```

Run ant colony optimization on a pheromone field.

---

## age

```python
def age(self) -> timedelta
```

Time since deposit.

---

## age_hours

```python
def age_hours(self) -> float
```

Age in hours.

---

## __init__

```python
def __init__(self, decay_rate: float=0.1, evaporation_threshold: float=0.01) -> None
```

Initialize pheromone field.

---

## decay_rate

```python
def decay_rate(self) -> float
```

Current decay rate per hour.

---

## concepts

```python
def concepts(self) -> set[str]
```

All concepts with active traces.

---

## deposit

```python
async def deposit(self, concept: str, intensity: float, depositor: str='anonymous', metadata: dict[str, Any] | None=None) -> Trace
```

Leave a trace at a concept (void.tithe integration).

---

## sense

```python
async def sense(self, position: str | None=None) -> list[SenseResult]
```

Perceive gradients from current position.

---

## gradient_toward

```python
async def gradient_toward(self, concept: str) -> float
```

Get gradient strength toward a specific concept.

---

## decay

```python
async def decay(self, elapsed: timedelta) -> int
```

Explicitly apply decay for a time period.

---

## reinforce

```python
async def reinforce(self, concept: str, factor: float=1.5) -> int
```

Reinforce all traces at a concept.

---

## clear_concept

```python
async def clear_concept(self, concept: str) -> int
```

Remove all traces at a concept.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get field statistics.

---

## __init__

```python
def __init__(self, field: PheromoneField, exploration_rate: float=0.1, deposit_intensity: float=1.0) -> None
```

Initialize stigmergic agent.

---

## current_position

```python
def current_position(self) -> str | None
```

Current concept position.

---

## path_history

```python
def path_history(self) -> list[str]
```

History of visited concepts.

---

## follow_gradient

```python
async def follow_gradient(self) -> str | None
```

Move toward strongest trace or explore.

---

## move_to

```python
async def move_to(self, concept: str) -> None
```

Explicitly move to a concept.

---

## deposit

```python
async def deposit(self, intensity: float | None=None, metadata: dict[str, Any] | None=None) -> Trace | None
```

Deposit a trace at current position.

---

## sample

```python
async def sample(self) -> str
```

Sample a random concept.

---

## neighbors

```python
async def neighbors(self, concept: str) -> list[str]
```

Get neighboring concepts.

---

## sample

```python
async def sample(self) -> str
```

Sample a random concept from vocabulary.

---

## neighbors

```python
async def neighbors(self, concept: str) -> list[str]
```

Get neighbors of a concept.

---

## __init__

```python
def __init__(self, field: PheromoneField, concept_space: SimpleConceptSpace, exploration_rate: float=0.1, deposit_intensity: float=1.0) -> None
```

Initialize enhanced agent.

---

## follow_neighbors

```python
async def follow_neighbors(self) -> str | None
```

Move to a neighbor of current position.

---

## agents.m.substrate

## substrate

```python
module substrate
```

Substrate: Legacy stub for deleted module.

---

## MemoryQuota

```python
class MemoryQuota
```

DEPRECATED: Old memory quota.

---

## SharedSubstrate

```python
class SharedSubstrate(Generic[T])
```

DEPRECATED: Old shared memory substrate.

---

## create_substrate

```python
def create_substrate(max_bytes: int=1000000) -> SharedSubstrate[Any]
```

Create a shared substrate (DEPRECATED).

---

## CrystalPolicy

```python
class CrystalPolicy
```

DEPRECATED: Old crystal policy.

---

## agents.operad.__init__

## __init__

```python
module __init__
```

Operad: Grammar of Agent Composition.

---

## agents.operad.algebra

## algebra

```python
module algebra
```

CLI Algebra: Operad → CLI Commands.

### Things to Know

ℹ️ CLIAlgebra.to_cli() requires an agent_resolver to map names to agents. The default resolver uses poly.get_primitive(). If your agents aren't registered primitives, provide a custom resolver or you'll get None.
  - *Verified in: `Structural - _default_resolver calls get_primitive`*

ℹ️ Command names are auto-generated from operad name + operation name. The operad name is lowercased and "operad" is stripped, so "SoulOperad" + "introspect" becomes "kg soul introspect". (Evidence: Structural - to_cli() line 133)

---

## CLIHandler

```python
class CLIHandler(Protocol)
```

Protocol for CLI handlers.

---

## CLICommand

```python
class CLICommand
```

A CLI command generated from an operad operation.

---

## CLIAlgebra

```python
class CLIAlgebra
```

Functor: Operad → CLI Commands.

---

## TestAlgebra

```python
class TestAlgebra
```

Functor: Operad Laws → Test Cases.

---

## __call__

```python
async def __call__(self, args: list[str]) -> int
```

Execute the CLI command.

---

## __init__

```python
def __init__(self, operad: Operad, agent_resolver: Callable[[str], PolyAgent[Any, Any, Any] | None] | None=None, prefix: str='kg')
```

Initialize CLI algebra.

---

## to_cli

```python
def to_cli(self, op_name: str) -> CLICommand
```

Convert an operad operation to a CLI command.

---

## generate_all

```python
def generate_all(self) -> dict[str, CLICommand]
```

Generate CLI commands for all operations.

---

## register_all

```python
def register_all(self, registry: dict[str, Callable[[list[str]], int]]) -> None
```

Register all commands with a CLI registry.

---

## help

```python
def help(self) -> str
```

Generate help text for all commands.

---

## generate_law_tests

```python
def generate_law_tests(self) -> str
```

Generate pytest code for all operad laws.

---

## generate_composition_tests

```python
def generate_composition_tests(self, depth: int=2) -> str
```

Generate property tests for random compositions.

---

## handler

```python
def handler(args: list[str]) -> int
```

CLI handler for this operation.

---

## agents.operad.core

## core

```python
module core
```

Operad Core: Grammar of Agent Composition.

### Things to Know

ℹ️ Operations require EXACT arity. An Operation with arity=2 rejects 1 or 3 arguments with ValueError, even if semantically valid.
  - *Verified in: `test_core.py::TestOperation::test_operation_wrong_arity_raises`*

🚨 **Critical:** Operad.compose() raises KeyError for unknown operations, not None. Always check `operad.get(op_name)` first if unsure.
  - *Verified in: `test_core.py::TestOperad::test_operad_compose_unknown_op_raises`*

ℹ️ State composition via seq/par creates NESTED tuple states. Left-assoc seq(seq(a,b),c) gives state ((s_a,s_b),s_c), right-assoc gives (s_a,(s_b,s_c)). Results are equivalent but state shapes differ.
  - *Verified in: `test_core.py::TestCompositionLaws::test_seq_associativity_behavioral`*

ℹ️ OperadRegistry uses class-level state. For parallel test execution (xdist), call OperadRegistry.reset() + re-import in conftest to ensure clean state.
  - *Verified in: `test_xdist_registry_canary.py`*

ℹ️ Law verification is STRUCTURAL, not behavioral. verify_law() checks composition structure but doesn't execute with test inputs by default. For behavioral verification, pass agents AND invoke the result.
  - *Verified in: `test_core.py::TestLawVerification::test_verify_law_by_name`*

---

## LawStatus

```python
class LawStatus(Enum)
```

Status of a law verification.

---

## LawVerification

```python
class LawVerification
```

Result of verifying an operad law.

---

## Operation

```python
class Operation
```

An operation in the operad.

---

## Law

```python
class Law
```

An equation that must hold in the operad.

---

## Operad

```python
class Operad
```

Grammar of agent composition.

---

## create_agent_operad

```python
def create_agent_operad() -> Operad
```

Create the Universal Agent Operad.

---

## OperadRegistry

```python
class OperadRegistry
```

Registry of all operads in kgents.

---

## passed

```python
def passed(self) -> bool
```

True if law was verified (either runtime or structurally).

---

## __call__

```python
def __call__(self, *agents: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]
```

Apply the operation to agents.

---

## get

```python
def get(self, op_name: str) -> Operation | None
```

Get an operation by name.

---

## compose

```python
def compose(self, op_name: str, *agents: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]
```

Apply an operation to compose agents.

---

## verify_law

```python
def verify_law(self, law_name: str, *test_agents: Any) -> LawVerification
```

Verify a specific law.

---

## verify_all_laws

```python
def verify_all_laws(self, *test_agents: Any) -> list[LawVerification]
```

Verify all laws.

---

## enumerate

```python
def enumerate(self, primitives: list[PolyAgent[Any, Any, Any]], depth: int, filter_fn: Callable[[PolyAgent[Any, Any, Any]], bool] | None=None) -> list[PolyAgent[Any, Any, Any]]
```

Generate all valid compositions up to given depth.

---

## register

```python
def register(cls, operad: Operad) -> None
```

Register an operad.

---

## get

```python
def get(cls, name: str) -> Operad | None
```

Get an operad by name.

---

## all_operads

```python
def all_operads(cls) -> dict[str, Operad]
```

Get all registered operads.

---

## verify_all

```python
def verify_all(cls, *test_agents: Any) -> dict[str, list[LawVerification]]
```

Verify all laws across all registered operads.

---

## reset

```python
def reset(cls) -> None
```

Clear all registered operads (for testing).

---

## agents.operad.domains.__init__

## __init__

```python
module __init__
```

Domain-Specific Operads.

---

## agents.operad.domains.evolution

## evolution

```python
module evolution
```

Evolution Operad: Genetic/Evolutionary Composition Grammar.

---

## create_evolution_operad

```python
def create_evolution_operad() -> Operad
```

Create the Evolution Operad (genetic/evolutionary composition grammar).

---

## combine_fn

```python
def combine_fn(pair: tuple[Any, Any]) -> dict[str, Any]
```

Combine two evolution results.

---

## agents.operad.domains.memory

## memory

```python
module memory
```

Memory Operad: D-gent Composition Grammar.

---

## create_memory_operad

```python
def create_memory_operad() -> Operad
```

Create the Memory Operad (D-gent composition grammar).

---

## select_fn

```python
def select_fn(pair: tuple[bool, Any]) -> Any
```

Select based on check result.

---

## agents.operad.domains.narrative

## narrative

```python
module narrative
```

Narrative Operad: N-gent Composition Grammar.

---

## create_narrative_operad

```python
def create_narrative_operad() -> Operad
```

Create the Narrative Operad (N-gent composition grammar).

---

## weave_fn

```python
def weave_fn(pair: tuple[Any, Any]) -> dict[str, Any]
```

Weave two narratives together.

---

## agents.operad.domains.parse

## parse

```python
module parse
```

Parse Operad: P-gent Composition Grammar.

---

## ParseResult

```python
class ParseResult
```

Result of a parsing operation.

---

## ConfidentParse

```python
class ConfidentParse
```

Parsing result with confidence annotation.

---

## create_parse_operad

```python
def create_parse_operad() -> Operad
```

Create the Parse Operad (P-gent composition grammar).

---

## agents.operad.domains.reality

## reality

```python
module reality
```

Reality Operad: J-gent Composition Grammar.

---

## RealityType

```python
class RealityType(Enum)
```

Classification of reality types.

---

## RealityClassification

```python
class RealityClassification
```

A value with its reality classification.

---

## create_reality_operad

```python
def create_reality_operad() -> Operad
```

Create the Reality Operad (J-gent composition grammar).

---

## agents.operad.domains.soul

## soul

```python
module soul
```

Soul Operad: K-gent Composition Grammar.

### Things to Know

ℹ️ Domain operads EXTEND the universal AGENT_OPERAD, not replace it. SOUL_OPERAD includes all 5 universal operations (seq, par, branch, fix, trace) PLUS the soul-specific ones. Check for duplicates.
  - *Verified in: `test_domains.py::TestSoulOperad::test_has_universal_operations`*

ℹ️ dialectic uses parallel() then sequential(sublate). The input goes to BOTH thesis and antithesis agents, then their pair output goes to sublation. Don't assume thesis runs before antithesis.
  - *Verified in: `test_domains.py::TestSoulOperad::test_dialectic_composes_parallel_then_sublate`*

---

## create_soul_operad

```python
def create_soul_operad() -> Operad
```

Create the Soul Operad (K-gent composition grammar).

---

## agents.poly.__init__

## __init__

```python
module __init__
```

Poly: Polynomial Agent Infrastructure.

---

## agents.poly.primitives

## primitives

```python
module primitives
```

Polynomial Primitives: The 17 Atomic Agents.

### Things to Know

ℹ️ All state Enums follow the pattern: initial state, intermediate states, terminal state(s). The directions function uses this to control valid inputs per state.
  - *Verified in: `test_primitives.py::TestPrimitiveProperties::test_all_primitives_have_directions`*

ℹ️ PRIMITIVES is a registry dict, not a list. Use get_primitive("id") to retrieve by name, not PRIMITIVES[0].
  - *Verified in: `test_primitives.py::TestPrimitiveRegistry::test_get_primitive_by_name`*

ℹ️ The primitive module imports from .protocol—if you see circular import errors, check that protocol.py doesn't import primitives.
  - *Verified in: `test_primitives.py::TestPrimitiveRegistry::test_all_17_primitives_registered`*

---

## GroundState

```python
class GroundState(Enum)
```

States for the Ground primitive.

---

## JudgeState

```python
class JudgeState(Enum)
```

States for the Judge primitive.

---

## ContradictState

```python
class ContradictState(Enum)
```

States for the Contradict primitive.

---

## SublateState

```python
class SublateState(Enum)
```

States for the Sublate primitive.

---

## FixState

```python
class FixState(Enum)
```

States for the Fix primitive.

---

## WitnessState

```python
class WitnessState(Enum)
```

States for the Witness primitive.

---

## SipState

```python
class SipState(Enum)
```

States for the Sip primitive.

---

## TitheState

```python
class TitheState(Enum)
```

States for the Tithe primitive.

---

## Claim

```python
class Claim
```

A claim to be judged.

---

## Verdict

```python
class Verdict
```

Result of judgment.

---

## Thesis

```python
class Thesis
```

A position to be contradicted.

---

## Antithesis

```python
class Antithesis
```

The contradiction of a thesis.

---

## Synthesis

```python
class Synthesis
```

The resolution of thesis and antithesis.

---

## Handle

```python
class Handle
```

A handle to an entity for observation.

---

## Umwelt

```python
class Umwelt
```

Observer context for perception.

---

## Manifestation

```python
class Manifestation
```

Result of manifesting a handle.

---

## Trace

```python
class Trace
```

A recorded trace of events.

---

## EntropyRequest

```python
class EntropyRequest
```

Request for entropy from the void.

---

## EntropyGrant

```python
class EntropyGrant
```

Entropy granted from the void.

---

## Offering

```python
class Offering
```

An offering to the void (gratitude tithe).

---

## Spec

```python
class Spec
```

Specification for autopoietic creation.

---

## Definition

```python
class Definition
```

Result of autopoietic definition.

---

## RememberState

```python
class RememberState(Enum)
```

States for the Remember primitive.

---

## ForgetState

```python
class ForgetState(Enum)
```

States for the Forget primitive.

---

## Memory

```python
class Memory
```

A memory to store or recall.

---

## MemoryResult

```python
class MemoryResult
```

Result of a memory operation.

---

## EvolveState

```python
class EvolveState(Enum)
```

States for the Evolve primitive.

---

## NarrateState

```python
class NarrateState(Enum)
```

States for the Narrate primitive.

---

## Organism

```python
class Organism
```

An entity subject to evolution.

---

## Evolution

```python
class Evolution
```

Result of evolutionary step.

---

## Story

```python
class Story
```

A narrative constructed from events.

---

## get_primitive

```python
def get_primitive(name: str) -> PolyAgent[Any, Any, Any] | None
```

Get a primitive by name.

---

## all_primitives

```python
def all_primitives() -> list[PolyAgent[Any, Any, Any]]
```

Get all primitives.

---

## primitive_names

```python
def primitive_names() -> list[str]
```

Get all primitive names.

---

## agents.poly.protocol

## protocol

```python
module protocol
```

Polynomial Agent Protocol: Agents as Dynamical Systems.

---

## PolyAgentProtocol

```python
class PolyAgentProtocol(Protocol[S, A, B])
```

Protocol for polynomial agents.

### Things to Know

ℹ️ This is a typing.Protocol, not ABC. Use isinstance() checks with @runtime_checkable, not inheritance verification.
  - *Verified in: `test_protocol.py::TestPolyAgentConstruction`*

ℹ️ The directions function returns valid inputs for each state. This enables MODE-DEPENDENT behavior—the key polynomial insight. Different states accept different inputs.
  - *Verified in: `test_protocol.py::TestStateDependentBehavior`*

---

## PolyAgent

```python
class PolyAgent(Generic[S, A, B])
```

Immutable polynomial agent.

### Examples
```python
>>> id_agent = PolyAgent(
```
```python
>>> id_agent = PolyAgent(
```
```python
>>> ...     name="Id",
```
```python
>>> ...     positions=frozenset({"ready"}),
```
```python
>>> ...     _directions=lambda s: frozenset({Any}),
```

### Things to Know

ℹ️ PolyAgent[S,A,B] > Agent[A,B] because state enables mode-dependent behavior. A stateless agent is just PolyAgent[str, A, B] with positions={"ready"}.
  - *Verified in: `test_protocol.py::test_stateless_agent_type_alias`*

ℹ️ Use frozenset({Any}) in _directions to accept any input. The _accepts_input helper checks for Any type marker.
  - *Verified in: `test_protocol.py::test_identity_construction`*

ℹ️ invoke() validates state and input BEFORE calling transition. Invalid state/input raises ValueError, not silent failure.
  - *Verified in: `test_protocol.py::test_invoke_invalid_state_raises`*

---

## WiringDiagram

```python
class WiringDiagram(Generic[S, S2, A, B, C])
```

Wiring diagram for polynomial composition.

### Things to Know

ℹ️ compose() creates a new PolyAgent with PRODUCT state space. If left has 3 states and right has 4, composed has 12 states.
  - *Verified in: `test_protocol.py::TestWiringDiagram`*

ℹ️ Output of left feeds into input of right. This is sequential composition. For parallel (same input to both), use parallel().
  - *Verified in: `test_protocol.py::TestSequentialComposition`*

---

## identity

```python
def identity(name: str='Id') -> PolyAgent[str, Any, Any]
```

Create the identity polynomial agent.

---

## constant

```python
def constant(value: B, name: str='Const') -> PolyAgent[str, Any, B]
```

Create a constant polynomial agent.

---

## stateful

```python
def stateful(name: str, states: FrozenSet[S], initial: S, transition_fn: Callable[[S, A], tuple[S, B]], directions_fn: Callable[[S], FrozenSet[A]] | None=None) -> PolyAgent[S, A, B]
```

Create a stateful polynomial agent.

---

## from_function

```python
def from_function(name: str, fn: Callable[[A], B]) -> PolyAgent[str, A, B]
```

Lift a pure function to a polynomial agent.

---

## sequential

```python
def sequential(left: PolyAgent[S, A, B], right: PolyAgent[S2, B, C]) -> PolyAgent[tuple[S, S2], A, C]
```

Sequential composition: left >> right.

---

## parallel

```python
def parallel(left: PolyAgent[S, A, B], right: PolyAgent[S2, A, C]) -> PolyAgent[tuple[S, S2], A, tuple[B, C]]
```

Parallel composition: run both agents on same input.

---

## to_bootstrap_agent

```python
def to_bootstrap_agent(poly: PolyAgent[S, A, B]) -> Any
```

Convert a PolyAgent to a bootstrap Agent-compatible wrapper.

### Examples
```python
>>> poly = from_function("doubler", lambda x: x * 2)
```
```python
>>> agent = to_bootstrap_agent(poly)
```
```python
>>> await agent.invoke(21)  # Returns 42
```

---

## from_bootstrap_agent

```python
def from_bootstrap_agent(agent: Any) -> PolyAgent[str, Any, Any]
```

Convert a bootstrap Agent to a PolyAgent.

### Examples
```python
>>> from agents import agent
```
```python
>>> @agent
```
```python
>>> poly = from_bootstrap_agent(doubler)
```

---

## name

```python
def name(self) -> str
```

Agent name for identification.

---

## positions

```python
def positions(self) -> FrozenSet[S]
```

The set of valid states (positions in polynomial).

---

## directions

```python
def directions(self, state: S) -> FrozenSet[A]
```

Valid inputs for a given state.

---

## transition

```python
def transition(self, state: S, input: A) -> tuple[S, B]
```

State transition function.

---

## directions

```python
def directions(self, state: S) -> FrozenSet[A]
```

Get valid inputs for state.

---

## transition

```python
def transition(self, state: S, input: A) -> tuple[S, B]
```

Execute state transition.

---

## invoke

```python
def invoke(self, state: S, input: A) -> tuple[S, B]
```

Execute one step of the dynamical system.

---

## run

```python
def run(self, initial: S, inputs: list[A]) -> tuple[S, list[B]]
```

Run the system through a sequence of inputs.

---

## composed_positions

```python
def composed_positions(self) -> FrozenSet[tuple[S, S2]]
```

Product of position sets.

---

## compose

```python
def compose(self) -> PolyAgent[tuple[S, S2], A, C]
```

Compose two agents via wiring diagram.

---

## PolyAgentWrapper

```python
class PolyAgentWrapper(BootstrapAgent[A, B])
```

Wrapper that adapts PolyAgent to bootstrap Agent interface.

### Things to Know

ℹ️ State is MUTABLE in the wrapper (via self._state). The underlying PolyAgent is immutable, but the wrapper tracks current state across invocations.
  - *Verified in: `test_protocol.py::test_to_bootstrap_agent_stateful`*

---

## invoke

```python
async def invoke(self, input: A) -> B
```

Execute the polynomial agent.

---

## agents.poly.types

## types

```python
module types
```

Bootstrap Types - Foundation types for all agents.

### Things to Know

ℹ️ Agent is a Protocol, not a base class. Use structural typing. Don't inherit from Agent—implement the invoke() method.
  - *Verified in: `test_protocol.py::test_agent_structural_typing`*

ℹ️ ComposedAgent flattens automatically. (a >> b) >> c = a >> (b >> c). This is associativity. Verify with BootstrapWitness.verify_composition_laws().
  - *Verified in: `test_primitives.py::test_composition_associativity`*

🚨 **Critical:** Result.unwrap() raises RuntimeError on Err. Always check is_ok() first or use unwrap_or(default) for safe extraction.
  - *Verified in: `test_primitives.py::test_result_unwrap_error`*

ℹ️ Type variables A_contra and B_co have variance for Protocol correctness. Using invariant type vars in Protocol causes mypy errors.
  - *Verified in: `test_protocol.py::test_variance_correctness`*

---

## Ok

```python
class Ok(Generic[T])
```

Success result containing value.

---

## Err

```python
class Err(Generic[E])
```

Error result containing error information.

---

## ok

```python
def ok(value: T) -> Ok[T]
```

Create an Ok result.

---

## err

```python
def err(error: E, message: str='', recoverable: bool=True) -> Err[E]
```

Create an Err result.

---

## AgentProtocol

```python
class AgentProtocol(Protocol[A_contra, B_co])
```

Protocol for agent-like objects (structural typing).

---

## Agent

```python
class Agent(ABC, Generic[A, B])
```

Abstract base class for all agents.

---

## ComposedAgent

```python
class ComposedAgent(Agent[A, C], Generic[A, B, C])
```

Sequential composition of two agents: f >> g.

---

## TensionMode

```python
class TensionMode(Enum)
```

Types of tension that can be detected between outputs.

---

## Tension

```python
class Tension
```

A detected contradiction between two outputs.

---

## Synthesis

```python
class Synthesis
```

Resolution of a tension via Hegelian sublation.

---

## HoldTension

```python
class HoldTension
```

Decision to consciously hold a tension rather than resolve it.

---

## VerdictType

```python
class VerdictType(Enum)
```

Possible outcomes of judgment.

---

## PartialVerdict

```python
class PartialVerdict
```

Verdict from a single mini-judge (one principle).

---

## Verdict

```python
class Verdict
```

Complete verdict from Judge.

---

## Principles

```python
class Principles
```

The seven principles that Judge evaluates against.

---

## PersonaSeed

```python
class PersonaSeed
```

The irreducible facts about a persona.

---

## WorldSeed

```python
class WorldSeed
```

The irreducible facts about the world state.

---

## Facts

```python
class Facts
```

Complete grounded facts returned by Ground agent.

---

## FixConfig

```python
class FixConfig(Generic[A])
```

Configuration for fixed-point iteration.

---

## FixResult

```python
class FixResult(Generic[A])
```

Result of fixed-point iteration.

---

## ContradictInput

```python
class ContradictInput
```

Input to Contradict agent.

---

## ContradictResult

```python
class ContradictResult
```

Result from Contradict agent.

---

## SublateInput

```python
class SublateInput
```

Input to Sublate agent.

---

## JudgeInput

```python
class JudgeInput
```

Input to Judge agent.

---

## Void

```python
class Void
```

The void type - Ground's input.

---

## unwrap

```python
def unwrap(self) -> T
```

Extract the value.

---

## unwrap_or

```python
def unwrap_or(self, default: T) -> T
```

Extract value or return default.

---

## map

```python
def map(self, f: Callable[[T], B]) -> 'Result[B, Any]'
```

Apply function to contained value.

---

## unwrap

```python
def unwrap(self) -> Any
```

Raises exception - can't unwrap an error.

---

## unwrap_or

```python
def unwrap_or(self, default: T) -> T
```

Return default value.

---

## map

```python
def map(self, f: Callable[[Any], B]) -> 'Result[B, E]'
```

Map is identity for errors - just propagate the error.

---

## name

```python
def name(self) -> str
```

Human-readable name for this agent.

---

## invoke

```python
async def invoke(self, input: A) -> B
```

Invoke the agent with input and produce output.

---

## __rshift__

```python
def __rshift__(self, other: 'Agent[B, C]') -> 'ComposedAgent[A, B, C]'
```

Composition operator: self >> other.

---

## invoke

```python
async def invoke(self, input: A) -> C
```

Execute f, then g.

---

## first

```python
def first(self) -> Agent[A, B]
```

Access first agent in composition.

---

## second

```python
def second(self) -> Agent[B, C]
```

Access second agent in composition.

---

## accept

```python
def accept(reasons: Optional[list[str]]=None) -> 'Verdict'
```

Factory for ACCEPT verdict.

---

## reject

```python
def reject(reasons: Optional[list[str]]=None) -> 'Verdict'
```

Factory for REJECT verdict.

---

## revise

```python
def revise(revisions: list[str], reasons: Optional[list[str]]=None) -> 'Verdict'
```

Factory for REVISE verdict with suggested changes.

---

## all

```python
def all(cls) -> tuple[str, ...]
```

Return all principle names.

---

## check

```python
def check(principle: str, agent: Agent[Any, Any]) -> PartialVerdict
```

Check if an agent satisfies a principle.

---

## agents.poly.umwelt

## umwelt

```python
module umwelt
```

Umwelt Protocol: Agent-Specific World Projection.

---

## Contract

```python
class Contract(Protocol)
```

F-gent contract for ground constraints.

---

## GroundingError

```python
class GroundingError(Exception)
```

Raised when output violates gravitational constraints.

---

## Umwelt

```python
class Umwelt(Generic[S, D])
```

An agent's projected world.

### Examples
```python
>>> umwelt = Umwelt(
```
```python
>>> await umwelt.get()  # Read state through lens
```
```python
>>> await umwelt.set(new_state)  # Write state through lens
```
```python
>>> umwelt.is_grounded(output)  # Check constraints
```

---

## LightweightUmwelt

```python
class LightweightUmwelt(Generic[S, D])
```

Simplified Umwelt for agents with direct state access.

---

## Projector

```python
class Projector
```

Projects the infinite World into finite agent Umwelts.

### Examples
```python
>>> from agents.d import VolatileAgent
```
```python
>>> root = VolatileAgent({"agents": {}})
```
```python
>>> projector = Projector(root)
```
```python
>>> umwelt = projector.project(
```

---

## HypotheticalProjector

```python
class HypotheticalProjector
```

Creates hypothetical worlds for counter-factual reasoning.

### Examples
```python
>>> real_projector = Projector(persistent_root)
```
```python
>>> hypothetical = HypotheticalProjector.from_snapshot(real_projector)
```
```python
>>> # Spawn agents in hypothetical world
```
```python
>>> umwelt_a = hypothetical.project("b.hypothesis", dna_a)
```
```python
>>> umwelt_b = hypothetical.project("b.hypothesis", dna_b)
```

---

## TemporalLens

```python
class TemporalLens(Generic[S])
```

Lens that projects state at a specific timestamp.

---

## TemporalProjector

```python
class TemporalProjector
```

Projects Umwelts at specific points in time.

### Examples
```python
>>> temporal = TemporalProjector(projector, timestamp=one_hour_ago)
```
```python
>>> historical_umwelt = temporal.project("k", dna)
```
```python
>>> # Agent sees state as it was one hour ago
```

---

## name

```python
def name(self) -> str
```

Human-readable contract name.

---

## check

```python
def check(self, output: Any) -> str | None
```

Check if output satisfies contract.

---

## admits

```python
def admits(self, intent: str) -> bool
```

Check if an intent is admissible under this contract.

---

## get

```python
async def get(self) -> S
```

Read state through lens.

---

## set

```python
async def set(self, value: S) -> None
```

Write state through lens (gravity checked on agent output, not here).

---

## is_grounded

```python
def is_grounded(self, output: Any) -> bool
```

Check if output satisfies all gravitational constraints.

---

## check_grounding

```python
def check_grounding(self, output: Any) -> list[str]
```

Return list of constraint violations for output.

---

## get

```python
async def get(self) -> S
```

Read state directly.

---

## set

```python
async def set(self, value: S) -> None
```

Write state directly.

---

## is_grounded

```python
def is_grounded(self, output: Any) -> bool
```

Check if output satisfies all gravitational constraints.

---

## __init__

```python
def __init__(self, root: DataAgent[Any])
```

Initialize with a root D-gent (the "Real").

---

## project

```python
def project(self, agent_id: str, dna: Any, gravity: list[Contract] | None=None, path: str | None=None) -> Umwelt[Any, Any]
```

Create an Umwelt for an agent.

---

## project_lightweight

```python
def project_lightweight(self, agent_id: str, dna: Any, storage: DataAgent[Any], gravity: list[Contract] | None=None) -> LightweightUmwelt[Any, Any]
```

Create a lightweight Umwelt with direct storage access.

---

## register_gravity

```python
def register_gravity(self, agent_id: str, contracts: list[Contract]) -> None
```

Register default gravity for an agent type.

---

## __init__

```python
def __init__(self, root: DataAgent[Any])
```

Initialize with a volatile (in-memory) root.

---

## from_snapshot

```python
async def from_snapshot(cls, real_projector: Projector, volatile_class: type[DataAgent[Any]] | None=None) -> 'HypotheticalProjector'
```

Create hypothetical projector from snapshot of real world.

---

## project

```python
def project(self, agent_id: str, dna: Any, gravity: list[Contract] | None=None) -> Umwelt[Any, Any]
```

Project an agent into the hypothetical world.

---

## is_hypothetical

```python
def is_hypothetical(self) -> bool
```

Always True for hypothetical projectors.

---

## get

```python
async def get(self) -> S | None
```

Get state as it was at timestamp.

---

## __init__

```python
def __init__(self, base_projector: Projector, timestamp: float)
```

Initialize temporal projector.

---

## project

```python
def project(self, agent_id: str, dna: Any, gravity: list[Contract] | None=None) -> Umwelt[Any, Any]
```

Project agent at historical timestamp.

---

## agents.sheaf.__init__

## __init__

```python
module __init__
```

Sheaf: Emergence Infrastructure.

---

## agents.sheaf.emergence

## emergence

```python
module emergence
```

Emergence: Global Soul from Local Agents.

---

## create_aesthetic_soul

```python
def create_aesthetic_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create aesthetic soul agent.

---

## create_categorical_soul

```python
def create_categorical_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create categorical soul agent.

---

## create_gratitude_soul

```python
def create_gratitude_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create gratitude soul agent.

---

## create_heterarchy_soul

```python
def create_heterarchy_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create heterarchy soul agent.

---

## create_generativity_soul

```python
def create_generativity_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create generativity soul agent.

---

## create_joy_soul

```python
def create_joy_soul() -> PolyAgent[str, Any, dict[str, Any]]
```

Create joy soul agent.

---

## create_emergent_soul

```python
def create_emergent_soul() -> PolyAgent[Any, Any, Any]
```

Create emergent Kent Soul via sheaf gluing.

---

## query_soul

```python
def query_soul(input: Any, context: Context | None=None) -> dict[str, Any]
```

Query the emergent soul.

---

## agents.sheaf.protocol

## protocol

```python
module protocol
```

Sheaf Protocol: Emergence from Local to Global.

### Things to Know

🚨 **Critical:** restrict() raises RestrictionError if no positions valid in subcontext Position filter must match at least one position, or restriction fails. Check your filter predicate before calling restrict().
  - *Verified in: `test_emergence.py::TestSheafRestriction::test_restrict_to_context`*

ℹ️ glue() raises GluingError if locals fail compatibility check Compatible means: agents on overlapping contexts produce equivalent outputs on the overlap. Call compatible() first to diagnose issues.
  - *Verified in: `test_emergence.py::TestSheafGluing::test_glue_local_souls`*

ℹ️ Context is hashable - use as dict key or in sets Context uses frozen capabilities, so it's safe for hash-based containers.
  - *Verified in: `test_emergence.py::TestContext::test_context_hashable`*

ℹ️ eigenvector_overlap() returns None for non-overlapping contexts No shared capabilities = no overlap. This is expected for disjoint contexts. Use this to detect when gluing is unnecessary.
  - *Verified in: `test_emergence.py::TestEigenvectorOverlap::test_no_overlap`*

ℹ️ Glued agent positions are UNION of local positions Position "ready" appearing in multiple locals appears once in glued agent. The first-registered local handles dispatch for shared positions.
  - *Verified in: `test_emergence.py::TestSheafGluing::test_glued_has_union_positions`*

---

## Context

```python
class Context
```

A context in the observation topology.

---

## GluingError

```python
class GluingError(Exception)
```

Raised when local agents cannot be glued.

---

## RestrictionError

```python
class RestrictionError(Exception)
```

Raised when restriction fails.

---

## AgentSheaf

```python
class AgentSheaf(Generic[Ctx])
```

Sheaf structure for emergent agent behavior.

---

## eigenvector_overlap

```python
def eigenvector_overlap(ctx1: Context, ctx2: Context) -> Context | None
```

Compute overlap of eigenvector contexts.

---

## create_soul_sheaf

```python
def create_soul_sheaf() -> AgentSheaf[Context]
```

Create the Soul Sheaf over eigenvector contexts.

---

## __init__

```python
def __init__(self, contexts: set[Ctx], overlap_fn: Callable[[Ctx, Ctx], Ctx | None])
```

Initialize agent sheaf.

---

## restrict

```python
def restrict(self, agent: PolyAgent[Any, Any, Any], subcontext: Ctx, position_filter: Callable[[Any, Ctx], bool] | None=None) -> PolyAgent[Any, Any, Any]
```

Restrict agent behavior to a subcontext.

---

## compatible

```python
def compatible(self, locals: dict[Ctx, PolyAgent[Any, Any, Any]], equivalence: Callable[[Any, Any], bool] | None=None) -> bool
```

Check if local agents agree on overlaps.

---

## glue

```python
def glue(self, locals: dict[Ctx, PolyAgent[Any, Any, Any]]) -> PolyAgent[Any, Any, Any]
```

Glue compatible local agents into global agent.

---

## global_directions

```python
def global_directions(state: Any) -> FrozenSet[Any]
```

Get directions from appropriate local agent.

---

## global_transition

```python
def global_transition(state: Any, input: Any) -> tuple[Any, Any]
```

Dispatch to appropriate local agent.

---

*1776 symbols, 74 teaching moments*

*Generated by Living Docs — 2025-12-21*