# D-gent Architecture: Unified Data Persistence

> *"D-gent is plumbing. It moves data between memory and storage. Nothing more."*

**Status**: REWRITE — This spec supersedes all prior D-gent documentation.

---

## Purpose

D-gent provides **projection-agnostic data persistence** for any agent. An agent should be able to store and retrieve data without knowing whether the backend is in-memory, a local file, SQLite, Postgres, or a cloud service.

The key insight: **persistence is a spectrum, not a binary**. Data can be "persisted for 0 seconds" (volatile) or "persisted forever" (durable). D-gent handles this transparently.

---

## The Core Abstraction

```python
@dataclass
class Datum:
    """
    The atomic unit of persisted data.

    Schema-free by default. Just bytes with an identity.
    """
    id: str                    # UUID or content-addressed hash
    content: bytes             # Raw data (schema-free)
    created_at: float          # Unix timestamp
    causal_parent: str | None  # ID of datum that caused this one
    metadata: dict[str, str]   # Optional tags (no schema enforcement)
```

That's it. A `Datum` is bytes with an ID and optional causal link.

---

## The Projection Lattice

Storage backends form a **lattice** ordered by durability:

```
                    ┌─────────┐
                    │  Cloud  │  (S3, GCS, etc.)
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │Postgres │  (kind cluster)
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │Postgres │  (docker container)
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │ SQLite  │  (local file)
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │  JSONL  │  (append-only log)
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │In-Memory│  (volatile)
                    └─────────┘
```

**Graceful Degradation**: If the preferred backend is unavailable, descend the lattice.
**Auto-Upgrade**: Background process promotes data to more durable tiers.

---

## The Protocol

```python
class DgentProtocol(Protocol[T]):
    """
    The minimal interface every D-gent backend implements.

    T is the serialized type (usually bytes or str).
    """

    async def put(self, datum: Datum) -> str:
        """Store datum, return ID."""
        ...

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum by ID."""
        ...

    async def delete(self, id: str) -> bool:
        """Remove datum, return success."""
        ...

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """List data with optional filters."""
        ...

    async def causal_chain(self, id: str) -> list[Datum]:
        """Get causal ancestors of a datum."""
        ...
```

**Five methods**. That's the entire D-gent interface.

---

## Projection Selection

The `DgentRouter` selects which backend to use:

```python
class DgentRouter:
    """
    Routes data operations to the appropriate backend.

    Selection order:
    1. Explicit override (if provided)
    2. Environment detection (KGENTS_DGENT_BACKEND)
    3. Availability probe (try preferred, fallback on failure)
    """

    def __init__(
        self,
        preferred: Backend = Backend.SQLITE,
        fallback_chain: list[Backend] = [Backend.JSONL, Backend.MEMORY],
    ):
        self.preferred = preferred
        self.fallback_chain = fallback_chain
        self._backends: dict[Backend, DgentProtocol] = {}

    async def get_backend(self) -> DgentProtocol:
        """Get the best available backend."""
        # Try preferred first
        if await self._is_available(self.preferred):
            return self._get_or_create(self.preferred)

        # Fall back through chain
        for backend in self.fallback_chain:
            if await self._is_available(backend):
                return self._get_or_create(backend)

        # Last resort: in-memory (always available)
        return self._get_or_create(Backend.MEMORY)
```

---

## Backend Implementations

### 1. MemoryBackend (Tier 0)

```python
class MemoryBackend(DgentProtocol):
    """In-memory storage. Fast but ephemeral."""

    def __init__(self):
        self._store: dict[str, Datum] = {}
```

### 2. JSONLBackend (Tier 1)

```python
class JSONLBackend(DgentProtocol):
    """
    Append-only JSON Lines file.

    Simple, human-readable, survives restarts.
    Path: ~/.kgents/data/{namespace}.jsonl
    """

    def __init__(self, namespace: str):
        self.path = Path.home() / ".kgents" / "data" / f"{namespace}.jsonl"
```

### 3. SQLiteBackend (Tier 2)

```python
class SQLiteBackend(DgentProtocol):
    """
    SQLite database. ACID, queryable, single-file.

    Path: ~/.kgents/data/{namespace}.db

    Schema:
        CREATE TABLE data (
            id TEXT PRIMARY KEY,
            content BLOB NOT NULL,
            created_at REAL NOT NULL,
            causal_parent TEXT,
            metadata TEXT  -- JSON
        );
        CREATE INDEX idx_created ON data(created_at);
        CREATE INDEX idx_parent ON data(causal_parent);
    """
```

### 4. PostgresBackend (Tier 3-4)

```python
class PostgresBackend(DgentProtocol):
    """
    PostgreSQL database. Scalable, concurrent, production-ready.

    Connection: KGENTS_POSTGRES_URL environment variable

    Tier 3: Docker container (localhost:5432)
    Tier 4: Kind cluster (postgres.kgents.svc.cluster.local)
    """

    def __init__(self, connection_url: str):
        self.url = connection_url
```

---

## Auto-Upgrade

Data automatically promotes to more durable tiers:

```python
class AutoUpgrader:
    """
    Background process that promotes data up the lattice.

    Triggers:
    1. Size threshold: When JSONL > 10MB, migrate to SQLite
    2. Age threshold: Data older than 1 hour promotes one tier
    3. Explicit command: `self.data.upgrade`
    4. Environment change: New backend becomes available
    """

    async def run(self, interval: float = 60.0):
        """Run upgrade loop."""
        while True:
            await self._check_and_upgrade()
            await asyncio.sleep(interval)

    async def _check_and_upgrade(self):
        """Check all tiers and promote where appropriate."""
        # JSONL → SQLite if size exceeded
        if await self._jsonl_size() > 10_000_000:  # 10MB
            await self._migrate(Backend.JSONL, Backend.SQLITE)

        # SQLite → Postgres if Postgres available and data > 100MB
        if (
            await self._is_available(Backend.POSTGRES)
            and await self._sqlite_size() > 100_000_000
        ):
            await self._migrate(Backend.SQLITE, Backend.POSTGRES)
```

---

## Causal Linking

Every write can specify a causal parent:

```python
# Store with causality
parent_id = await dgent.put(Datum(
    id=uuid4().hex,
    content=b"initial state",
    created_at=time.time(),
    causal_parent=None,
    metadata={},
))

child_id = await dgent.put(Datum(
    id=uuid4().hex,
    content=b"derived state",
    created_at=time.time(),
    causal_parent=parent_id,  # Links to parent
    metadata={},
))

# Retrieve causal chain
chain = await dgent.causal_chain(child_id)
# Returns: [parent_datum, child_datum]
```

This integrates with **TraceMonoid** for full causal history.

---

## AGENTESE Paths

D-gent exposes these paths under `self.data.*`:

| Path | Description |
|------|-------------|
| `self.data.put[content]` | Store raw bytes, return ID |
| `self.data.get[id]` | Retrieve by ID |
| `self.data.delete[id]` | Remove by ID |
| `self.data.list` | List recent data |
| `self.data.chain[id]` | Get causal chain |
| `self.data.upgrade` | Force promotion to next tier |
| `self.data.backend` | Get current backend info |

---

## Schema: Opt-In Later

D-gent stores raw bytes. Schema is applied **at query time** via lenses:

```python
# Store schema-free
datum_id = await dgent.put(Datum(
    id=uuid4().hex,
    content=json.dumps({"name": "Ada", "age": 36}).encode(),
    created_at=time.time(),
    causal_parent=None,
    metadata={"type": "person"},
))

# Query with schema lens (applied at read time)
@dataclass
class Person:
    name: str
    age: int

person_lens = json_lens(Person)
datum = await dgent.get(datum_id)
person = person_lens.get(datum.content)  # Person(name="Ada", age=36)
```

**Key insight**: Schema is a read-time concern, not a storage concern.

---

## Integration with Reactive Substrate

D-gent emits changes to the reactive Signal network:

```python
class ReactiveDgent:
    """D-gent wrapped with reactive signals."""

    def __init__(self, backend: DgentProtocol):
        self.backend = backend
        self.changes = Signal.of([])  # list[Change]

    async def put(self, datum: Datum) -> str:
        id = await self.backend.put(datum)
        self.changes.update(lambda c: c + [Change("put", id, datum)])
        return id
```

---

## Integration with Synergy Bus

D-gent operations can emit synergy events:

```python
class SynergyDgent:
    """D-gent that emits synergy events for cross-jewel coordination."""

    async def put(self, datum: Datum) -> str:
        id = await self.backend.put(datum)

        # Emit synergy event
        await get_synergy_bus().emit(SynergyEvent(
            event_type=SynergyEventType.DATA_STORED,
            source_jewel=Jewel.DGENT,
            target_jewel=Jewel.ANY,
            payload={"datum_id": id, "metadata": datum.metadata},
        ))

        return id
```

---

## What D-gent Is NOT

- **Not a database** — It's a projection selector over databases
- **Not schema-enforcing** — Schema is opt-in at read time
- **Not a memory manager** — That's M-gent's job
- **Not an ORM** — No object mapping, just bytes
- **Not a cache** — Caching is a projection concern, not D-gent's

---

## See Also

- `spec/m-gents/architecture.md` — Memory management (acts ON D-gent)
- `spec/protocols/data-bus.md` — Reactive data flow
- `spec/protocols/agentese.md` — AGENTESE path integration
