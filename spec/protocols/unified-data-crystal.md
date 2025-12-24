# Unified Data Crystal Architecture

> *"The datum is a lie. There is only the crystal."*

## Vision

A single, unified data model where:
1. **Agents work declaratively** - No migration anxiety, just data
2. **D-gent manages everything** - In-memory, SQLite, Postgres transparently
3. **Schemas are versioned** - Like code, not like database migrations
4. **Frozen dataclasses as contracts** - Immutable, typed, composable
5. **NoSQL-like operations** - Flexible querying without ORM ceremony

---

## Core Concepts

### 1. The Datum (Ground Truth)

The atomic unit. Always works. Schema-free.

```python
@dataclass(frozen=True)
class Datum:
    """The irreducible atom of data."""
    id: str                           # UUID
    created_at: datetime              # Immutable timestamp
    data: dict[str, Any]              # Raw payload
    tags: frozenset[str] = frozenset() # Classification

    # Provenance
    author: str = "system"
    source: str | None = None         # Where it came from
    parent_id: str | None = None      # Causal lineage
```

### 2. The Crystal (Typed Datum)

A Datum with a versioned schema contract.

```python
@dataclass(frozen=True)
class CrystalMeta:
    """Crystal metadata - the schema envelope."""
    schema_name: str      # e.g., "witness.mark"
    schema_version: int   # e.g., 3
    created_at: datetime
    crystallized_from: str | None  # Datum ID if upgraded

@dataclass(frozen=True)
class Crystal[T]:
    """A typed, versioned datum."""
    meta: CrystalMeta
    datum: Datum          # The underlying data
    value: T              # The typed, validated value

    @classmethod
    def from_datum(cls, datum: Datum, schema: "Schema[T]") -> "Crystal[T]":
        """Crystallize a datum into a typed crystal."""
        value = schema.parse(datum.data)
        return cls(
            meta=CrystalMeta(
                schema_name=schema.name,
                schema_version=schema.version,
                created_at=datetime.now(UTC),
                crystallized_from=datum.id,
            ),
            datum=datum,
            value=value,
        )
```

### 3. The Schema (Versioned Contract)

Frozen dataclasses define the contract. Versions enable evolution.

```python
@dataclass(frozen=True)
class Schema[T]:
    """A versioned data contract."""
    name: str                         # e.g., "witness.mark"
    version: int                      # Monotonic version number
    contract: type[T]                 # The frozen dataclass type
    migrations: dict[int, Callable]   # version -> upgrade function

    def parse(self, data: dict) -> T:
        """Parse raw data into typed contract."""
        return self.contract(**data)

    def upgrade(self, old_version: int, data: dict) -> dict:
        """Upgrade data from old version to current."""
        for v in range(old_version, self.version):
            if v in self.migrations:
                data = self.migrations[v](data)
        return data
```

### 4. The Universe (D-gent's Domain)

The universal data context. Manages all storage backends.

```python
class Universe:
    """
    D-gent's domain. Manages all data across all backends.

    Agents don't think about storage. They think about data.
    The Universe handles the rest.
    """

    # Backend hierarchy (fallback chain)
    backends: list[Backend]  # [Postgres, SQLite, Memory]

    # Schema registry
    schemas: dict[str, Schema]  # name -> schema

    # Active collections
    collections: dict[str, Collection]

    async def store(self, crystal: Crystal) -> str:
        """Store a crystal. D-gent chooses the backend."""
        ...

    async def query(self, q: Query) -> list[Crystal]:
        """Query crystals. Backend-agnostic."""
        ...

    async def get(self, id: str) -> Crystal | Datum:
        """Get by ID. Returns Crystal if schema known, Datum otherwise."""
        ...
```

---

## Schema Versioning Strategy

### Version Numbers

Each schema has a monotonic version number:

```python
# Version 1: Initial
@dataclass(frozen=True)
class WitnessMarkV1:
    action: str
    reasoning: str
    author: str

# Version 2: Added tags
@dataclass(frozen=True)
class WitnessMarkV2:
    action: str
    reasoning: str
    author: str
    tags: tuple[str, ...] = ()

# Version 3: Added principles
@dataclass(frozen=True)
class WitnessMarkV3:
    action: str
    reasoning: str
    author: str
    tags: tuple[str, ...] = ()
    principles: tuple[str, ...] = ()
```

### Migration Functions

```python
WITNESS_MARK_SCHEMA = Schema(
    name="witness.mark",
    version=3,
    contract=WitnessMarkV3,
    migrations={
        1: lambda d: {**d, "tags": ()},           # v1 -> v2
        2: lambda d: {**d, "principles": ()},     # v2 -> v3
    }
)
```

### Fallback Behavior

```python
async def get(self, id: str) -> Crystal | Datum:
    """
    Get data by ID.

    - If schema known and version matches: return Crystal[T]
    - If schema known but old version: upgrade and return Crystal[T]
    - If schema unknown: return raw Datum (always works)
    """
    datum = await self._fetch_datum(id)

    schema_name = datum.data.get("_schema")
    schema_version = datum.data.get("_version", 1)

    if schema_name and schema_name in self.schemas:
        schema = self.schemas[schema_name]
        if schema_version < schema.version:
            # Lazy upgrade
            data = schema.upgrade(schema_version, datum.data)
            datum = datum.replace(data=data)
        return Crystal.from_datum(datum, schema)

    # Unknown schema - return raw datum (safe fallback)
    return datum
```

---

## Backend Abstraction

### Backend Protocol

```python
class Backend(Protocol):
    """Storage backend interface."""

    name: str
    priority: int  # Lower = preferred

    async def store(self, datum: Datum) -> None: ...
    async def get(self, id: str) -> Datum | None: ...
    async def query(self, q: Query) -> list[Datum]: ...
    async def delete(self, id: str) -> bool: ...

    # Health
    async def is_available(self) -> bool: ...
    async def stats(self) -> BackendStats: ...
```

### Implementations

```python
class MemoryBackend(Backend):
    """In-memory storage. Fast, ephemeral."""
    name = "memory"
    priority = 100

class SQLiteBackend(Backend):
    """SQLite storage. Local, persistent."""
    name = "sqlite"
    priority = 50

class PostgresBackend(Backend):
    """PostgreSQL storage. Production, distributed."""
    name = "postgres"
    priority = 10
```

### Automatic Backend Selection

```python
class Universe:
    async def _select_backend(self) -> Backend:
        """Select best available backend."""
        for backend in sorted(self.backends, key=lambda b: b.priority):
            if await backend.is_available():
                return backend
        raise NoBackendAvailable()
```

---

## Query Language

NoSQL-like queries without ORM ceremony:

```python
@dataclass(frozen=True)
class Query:
    """Declarative query specification."""
    schema: str | None = None         # Filter by schema
    tags: frozenset[str] = frozenset() # Must have all tags
    author: str | None = None         # Filter by author
    since: datetime | None = None     # Created after
    until: datetime | None = None     # Created before
    limit: int = 100
    offset: int = 0

    # Flexible predicates
    where: dict[str, Any] | None = None  # {"field": value}

# Usage
marks = await universe.query(Query(
    schema="witness.mark",
    tags=frozenset(["eureka"]),
    since=datetime(2025, 1, 1),
    limit=50,
))
```

---

## Agent Interface

Agents work declaratively. No SQL, no migrations, no backend concerns.

```python
class DataMixin:
    """Mixin for agents that need data access."""

    @property
    def data(self) -> Universe:
        """Access the data universe."""
        return get_universe()

    async def remember(self, value: T, **meta) -> Crystal[T]:
        """Store a typed value as a crystal."""
        schema = self.data.schema_for(type(value))
        datum = Datum(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            data={**asdict(value), "_schema": schema.name, "_version": schema.version},
            **meta,
        )
        crystal = Crystal.from_datum(datum, schema)
        await self.data.store(crystal)
        return crystal

    async def recall(self, query: Query) -> list[Crystal]:
        """Query stored crystals."""
        return await self.data.query(query)
```

---

## Implementation Plan

### Phase 1: Core Primitives
- [ ] Datum frozen dataclass
- [ ] Crystal[T] generic container
- [ ] Schema with versioning
- [ ] CrystalMeta envelope

### Phase 2: Backend Abstraction
- [ ] Backend protocol
- [ ] MemoryBackend implementation
- [ ] SQLiteBackend implementation
- [ ] PostgresBackend implementation

### Phase 3: Universe
- [ ] Universe class
- [ ] Backend selection
- [ ] Schema registry
- [ ] Query execution

### Phase 4: Agent Integration
- [ ] DataMixin for agents
- [ ] AGENTESE self.data.* paths
- [ ] Migration of existing models

### Phase 5: Schema Migration
- [ ] Convert WitnessMark → witness.mark schema
- [ ] Convert Crystal → brain.crystal schema
- [ ] Convert Trail → trail.* schemas
- [ ] Delete old SQLAlchemy models

---

## File Structure

```
impl/claude/
├── agents/d/
│   ├── crystal/
│   │   ├── __init__.py
│   │   ├── datum.py       # Datum frozen dataclass
│   │   ├── crystal.py     # Crystal[T] container
│   │   ├── schema.py      # Schema versioning
│   │   └── query.py       # Query language
│   ├── universe/
│   │   ├── __init__.py
│   │   ├── universe.py    # Universe class
│   │   ├── backend.py     # Backend protocol
│   │   └── backends/
│   │       ├── memory.py
│   │       ├── sqlite.py
│   │       └── postgres.py
│   └── schemas/
│       ├── __init__.py
│       ├── witness.py     # witness.mark, witness.trust, etc.
│       ├── brain.py       # brain.crystal, brain.setting
│       └── trail.py       # trail.*, trail.step.*
```

---

## The Promise

After this refactor:

1. **No more migration anxiety** - Schemas version like code
2. **Backend-agnostic** - Works with memory, SQLite, or Postgres
3. **Type-safe** - Frozen dataclasses ensure immutability
4. **Fallback-safe** - Unknown schemas degrade to raw Datum
5. **Agent-friendly** - Declarative interface, no ORM ceremony
6. **Composable** - Crystals can reference other crystals

> *"The proof IS the crystal. The schema IS the witness."*

---

*Filed: 2025-12-23*
*Status: Proposed*
