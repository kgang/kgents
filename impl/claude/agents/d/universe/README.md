# Universe: D-gent's Schema-Aware Data Management

> *"Agents don't think about storage. They think about data. The Universe handles the rest."*

## Purpose

Universe is a higher-level abstraction over D-gent's `DgentProtocol` that provides schema awareness for typed objects while maintaining schema-free storage underneath.

**Use Universe when**:
- Working with typed objects (Crystal, Mark, etc.)
- Need automatic serialization/deserialization
- Want backend auto-selection with graceful fallback

**Use DgentRouter when**:
- Working with raw Datum (schema-free bytes)
- Need low-level control
- Building infrastructure

## Quick Start

### Basic Usage

```python
from agents.d import Universe, get_universe
from services.witness.crystal import Crystal

# Get singleton instance (lazy init)
universe = get_universe()

# Register schema for Crystal type
universe.register_type("crystal", Crystal)

# Store a crystal
crystal = Crystal(...)
crystal_id = await universe.store(crystal)

# Retrieve crystal (automatically deserialized)
retrieved = await universe.get(crystal_id)
assert isinstance(retrieved, Crystal)
```

### Explicit Initialization

```python
from agents.d import init_universe

# Initialize with specific backend
universe = await init_universe(backend="postgres", namespace="my-app")

# Now use it
await universe.store(crystal)
```

### Schema Registration

```python
# Option 1: Register by type (for dataclasses with to_dict/from_dict)
universe.register_type("crystal", Crystal)

# Option 2: Register custom schema
from agents.d import DataclassSchema

schema = DataclassSchema(name="my_type", type_cls=MyType)
universe.register_schema(schema)
```

### Querying

```python
from agents.d import Query

# Query by schema
q = Query(schema="crystal", limit=50)
crystals = await universe.query(q)

# Or use convenience method
crystals = await universe.recall(schema="crystal", limit=50)
```

### Backend Selection

Universe auto-selects the best available backend:

1. **Postgres** - If `KGENTS_DATABASE_URL` is set
2. **SQLite** - If filesystem is writable (XDG-compliant)
3. **Memory** - Fallback (ephemeral)

```python
# Explicit backend selection
universe = Universe(namespace="test", preferred_backend="memory")
await universe._ensure_initialized()

# Check which backend was selected
stats = await universe.stats()
print(f"Using backend: {stats.backend}")
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Universe (Schema-Aware Layer)                  │
│  - Schema registry                              │
│  - Serialize/deserialize typed objects          │
│  - Auto backend selection                       │
├─────────────────────────────────────────────────┤
│  DgentProtocol (Schema-Free Layer)              │
│  - put/get/delete/list/causal_chain             │
│  - Datum storage                                │
├─────────────────────────────────────────────────┤
│  Backends (Projection Lattice)                  │
│  - Memory (Tier 0)                              │
│  - SQLite (Tier 2)                              │
│  - Postgres (Tier 3)                            │
└─────────────────────────────────────────────────┘
```

**Key Insight**: Universe stores everything as `Datum` underneath. Schemas only matter at the boundary (store/retrieve).

## API Reference

### Core Operations

```python
class Universe:
    # Schema management
    def register_schema(self, schema: Schema[T]) -> None
    def register_type(self, name: str, type_cls: type[T]) -> None
    def schema_for(self, name: str) -> Schema[Any] | None
    def schema_for_type(self, cls: type) -> Schema[Any] | None

    # Data operations
    async def store(self, obj: T, schema_name: str | None = None) -> str
    async def store_datum(self, datum: Datum) -> str
    async def get(self, id: str) -> Any | None
    async def query(self, q: Query) -> list[Any]
    async def delete(self, id: str) -> bool

    # Convenience
    async def remember(self, value: T, **meta: str) -> T
    async def recall(self, schema: str, **filters: Any) -> list[Any]

    # Stats
    async def stats(self) -> UniverseStats
```

### Schema Protocol

```python
class Schema(Protocol[T]):
    name: str

    def serialize(self, obj: T) -> dict[str, Any]: ...
    def deserialize(self, data: dict[str, Any]) -> T: ...
```

### Query

```python
@dataclass
class Query:
    prefix: str | None = None      # Filter by ID prefix
    after: float | None = None      # Filter by timestamp
    limit: int = 100                # Maximum results
    schema: str | None = None       # Filter by schema type
```

## Examples

### Working with Crystal

```python
from agents.d import get_universe
from services.witness.crystal import Crystal

universe = get_universe()
universe.register_type("crystal", Crystal)

# Store
crystal = Crystal.from_crystallization(
    insight="Completed D-gent Universe implementation",
    significance="Higher-level abstraction for typed data",
    principles=["tasteful", "composable"],
    source_marks=[],
    time_range=(start, end),
)
crystal_id = await universe.store(crystal)

# Retrieve
retrieved = await universe.get(crystal_id)
print(retrieved.insight)

# Query all crystals
crystals = await universe.recall(schema="crystal", limit=100)
```

### Schema-Free Path (Raw Datum)

```python
from agents.d import Datum

# Store raw bytes without schema
datum = Datum.create(content=b"raw data")
datum_id = await universe.store_datum(datum)

# Retrieve - gets Datum back (no deserialization)
retrieved = await universe.get(datum_id)
assert isinstance(retrieved, Datum)
```

### Custom Schema

```python
from agents.d import Schema
from typing import Any

class CustomSchema(Schema[MyType]):
    name = "my_type"

    def serialize(self, obj: MyType) -> dict[str, Any]:
        return {"field": obj.field}

    def deserialize(self, data: dict[str, Any]) -> MyType:
        return MyType(field=data["field"])

universe.register_schema(CustomSchema())
```

## Design Principles

### 1. Schema at the Boundary

Schemas exist only at the Universe interface. Underneath, everything is stored as schema-free `Datum`. This maintains D-gent's core principle while adding convenience for typed objects.

### 2. Graceful Degradation

If you retrieve data and the schema is unknown, you get a `Datum` instead of an error. This enables graceful handling of unregistered types.

### 3. Backend Transparency

Services don't choose backends. Universe auto-selects based on availability. This enables:
- Local development with SQLite
- Production with Postgres
- Testing with Memory

### 4. Lazy Initialization

Universe initializes on first use, not at import time. This avoids startup overhead and enables configuration.

## Teaching

### Gotcha: Universe is NOT a replacement for DgentRouter

Universe is a convenience layer for typed objects. Low-level infrastructure should still use `DgentRouter` and `Datum` directly.

### Gotcha: Schemas are helpers, not enforcement

D-gent remains schema-free at the Datum level. Schemas only matter at the Universe boundary (store/retrieve). You can always access raw Datum if needed.

### Gotcha: Backend selection happens at init

Once initialized, the backend is fixed for that Universe instance. Create a new instance if you need a different backend.

### Gotcha: Singleton behavior

`get_universe()` and `init_universe()` use a global singleton. For tests or isolated contexts, create fresh instances directly:

```python
universe = Universe(namespace="test", preferred_backend="memory")
await universe._ensure_initialized()
```

## Cross-References

- **Spec**: `spec/agents/d-gent.md`
- **Skill**: `docs/skills/unified-storage.md`
- **Skill**: `docs/skills/metaphysical-fullstack.md` (Layer 0)
- **Implementation**: `agents/d/universe/universe.py`
- **Tests**: `agents/d/_tests/test_universe.py`

---

*"The Universe manages all data. Services think about domain logic. That's the division of labor."*
