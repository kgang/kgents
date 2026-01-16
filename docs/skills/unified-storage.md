# Skill: Unified Storage (D-gent)

> *"Crystal→K-Block: Crystals ARE K-Blocks with isolation=SEALED; unify storage."*
> *"The file is a lie. There is only the graph."*

**Purpose**: Using D-gent's Universe and DataBus for typed storage with reactive events.

**Prerequisites**: [metaphysical-fullstack.md](metaphysical-fullstack.md)

---

## When to Use This Skill

- Storing typed objects (Crystals, K-Blocks, Marks)
- Querying data with filters and pagination
- Wiring reactive events on data changes
- Integrating storage into Crown Jewels

---

## The D-gent Stack

D-gent provides categorical persistence with law-verified access:

```
┌─────────────────────────────────────────────────────────────────┐
│  Universe                                                        │
│  Typed object storage: get, put, query, delete                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DgentRouter                                                     │
│  Routes operations to appropriate backend by type/config         │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ MemoryBackend │  │ JSONLBackend  │  │ PostgresBackend│
│ (dev/test)    │  │ (local files) │  │ (production)   │
└───────────────┘  └───────────────┘  └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DataBus                                                         │
│  Reactive events on data changes                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Operations

### Getting the Universe

```python
from agents.d import get_universe

# Async initialization
universe = await get_universe()

# Or with explicit config
universe = await get_universe(backend="postgres", connection_string="...")
```

### Storing Objects

```python
from models import Crystal

# Put a typed object
crystal = Crystal(
    id="crystal-123",
    content="The proof IS the decision",
    layer=3,
    tags=["witness", "philosophy"],
)
await universe.put(crystal)
```

### Retrieving Objects

```python
# Get by ID
crystal = await universe.get(Crystal, "crystal-123")
if crystal is None:
    print("Not found")

# Get or raise
from services.derivation import DataNotFoundError
crystal = await universe.get_or_raise(Crystal, "crystal-123")  # Throws if missing
```

### Querying Objects

```python
# Query with filters
crystals = await universe.query(
    Crystal,
    filters={"layer": 3, "tags__contains": "witness"},
    limit=10,
    offset=0,
)

# Query all of a type
all_crystals = await universe.query(Crystal)
```

### Deleting Objects

```python
# Delete by ID
await universe.delete(Crystal, "crystal-123")
```

---

## Reactive Events with DataBus

### Subscribing to Events

```python
from agents.d import get_data_bus

bus = await get_data_bus()

async def on_crystal_created(event):
    crystal_id = event.data["id"]
    print(f"New crystal: {crystal_id}")

bus.subscribe("crystal.created", on_crystal_created)
bus.subscribe("crystal.updated", on_crystal_updated)
bus.subscribe("crystal.deleted", on_crystal_deleted)
```

### Emitting Events

Events are emitted automatically by Universe, but you can also emit manually:

```python
await bus.emit("custom.event", {
    "crystal_id": "crystal-123",
    "action": "enriched",
    "metadata": {"source": "brain"},
})
```

### Event Pattern

Standard event structure:

```python
@dataclass
class DataEvent:
    topic: str          # e.g., "crystal.created"
    data: dict          # Event payload
    timestamp: datetime
    source: str         # Emitting component
```

---

## Backend Configuration

### Development: Memory Backend

Fast, ephemeral—great for tests:

```python
universe = await get_universe(backend="memory")
```

### Local: JSONL Backend

Persistent local files:

```python
universe = await get_universe(
    backend="jsonl",
    path="~/.local/share/kgents/data/",
)
```

### Production: PostgreSQL

Scalable, queryable:

```python
universe = await get_universe(
    backend="postgres",
    connection_string="postgresql+asyncpg://...",
)
```

**Environment Variable**: Set `KGENTS_DATABASE_URL` for automatic Postgres.

---

## Storage Patterns

### Pattern: Dual-Track Storage

Store semantic content + queryable metadata separately:

```python
class BrainPersistence:
    """Dual-track: D-gent for content, table for metadata."""

    async def capture(self, content: str, tags: list[str]) -> Crystal:
        # 1. Store content in D-gent (for semantic search)
        datum = await self.universe.put(Datum(content=content))

        # 2. Store metadata in table (for fast queries)
        crystal = Crystal(
            id=f"crystal-{uuid4()}",
            datum_id=datum.id,
            tags=tags,
            created_at=datetime.utcnow(),
        )
        await self.universe.put(crystal)

        return crystal
```

### Pattern: Layer Assignment on Ingest

Always assign layer when storing:

```python
from services.zero_seed import classify_content_layer

async def store_crystal(content: str) -> Crystal:
    # Compute Galois loss
    loss = await galois.compute(content)

    # Classify into layer based on loss
    layer = classify_content_layer(loss)

    # Store with layer
    crystal = Crystal(
        id=f"crystal-{uuid4()}",
        content=content,
        layer=layer,
        galois_loss=loss,
    )
    await universe.put(crystal)
    return crystal
```

### Pattern: Edge Dual Storage

Normalized + JSONB for query performance:

```python
@dataclass(frozen=True)
class KBlockEdge:
    """Edge with both normalized and JSONB storage."""
    id: str
    source_id: str
    target_id: str
    edge_type: str
    metadata: dict  # JSONB for flexible queries

class EdgeSyncService:
    """Maintains consistency between normalized and JSONB."""

    async def create_edge(self, edge: KBlockEdge):
        # Store normalized
        await self.normalized_store.put(edge)

        # Update JSONB index
        await self.jsonb_index.upsert(
            source_id=edge.source_id,
            edges=[edge.model_dump()],
        )
```

---

## Integration with Crown Jewels

### Service Structure

```
services/brain/
├── persistence.py    # Universe + DataBus integration
├── contracts.py      # Typed models (Crystal, etc.)
└── node.py           # AGENTESE exposure
```

### Example: Brain Persistence

```python
# services/brain/persistence.py

class BrainPersistence:
    def __init__(self, universe: Universe, bus: DataBus):
        self.universe = universe
        self.bus = bus

        # Subscribe to events
        bus.subscribe("crystal.created", self._on_crystal_created)

    async def store_crystal(self, crystal: Crystal) -> str:
        await self.universe.put(crystal)
        return crystal.id

    async def get_crystal(self, crystal_id: str) -> Crystal | None:
        return await self.universe.get(Crystal, crystal_id)

    async def search_crystals(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Crystal]:
        # Use semantic search via D-gent
        return await self.universe.semantic_search(
            Crystal,
            query=query,
            limit=limit,
        )

    async def _on_crystal_created(self, event):
        # React to new crystals (e.g., update indices)
        pass
```

---

## Typed Models

### Frozen Dataclasses

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Crystal:
    """Immutable crystal—safe across async boundaries."""
    id: str
    content: str
    layer: int
    galois_loss: float
    tags: tuple[str, ...]  # Use tuple for immutable lists
    created_at: datetime
```

### Pydantic Models

```python
from pydantic import BaseModel

class CrystalModel(BaseModel):
    """Pydantic for validation and serialization."""
    id: str
    content: str
    layer: int
    galois_loss: float
    tags: list[str]
    created_at: datetime

    class Config:
        frozen = True
```

---

## Testing Storage

### Using Memory Backend

```python
import pytest
from agents.d import get_universe

@pytest.fixture
async def test_universe():
    """Isolated in-memory universe for testing."""
    universe = await get_universe(backend="memory")
    yield universe
    # Memory backend auto-clears

async def test_crystal_roundtrip(test_universe):
    crystal = Crystal(id="test-1", content="test", layer=3, ...)
    await test_universe.put(crystal)

    retrieved = await test_universe.get(Crystal, "test-1")
    assert retrieved == crystal
```

### PID-Based Isolation

For parallel tests:

```python
import os

@pytest.fixture(scope="session")
async def isolated_universe():
    pid = os.getpid()
    universe = await get_universe(
        backend="jsonl",
        path=f"/tmp/kgents-test-{pid}/",
    )
    yield universe
    # Cleanup
    shutil.rmtree(f"/tmp/kgents-test-{pid}/")
```

---

## Common Gotchas

### Gotcha: Explicit Edge Creation

Crystals don't auto-link. You must create edges explicitly:

```python
# ✗ BAD: Crystals are isolated
await universe.put(func_crystal)
await universe.put(spec_crystal)

# ✓ GOOD: Link them explicitly
from services.derivation import DerivationService
await derivation.link_derivation(
    source_id=func_crystal.id,
    target_id=spec_crystal.id,
    edge_kind="IMPLEMENTS",
)
```

### Gotcha: Layer Monotonicity

Parent layer must be < child layer in derivations:

```python
# ✓ VALID: L5 → L4 → L2 → L1 (decreasing)
# ✗ INVALID: L3 → L5 (increasing)
```

### Gotcha: Event Handler Isolation

Event handlers run in their own async context:

```python
async def on_crystal_created(event):
    # Don't assume caller's context is available
    # Fetch fresh from universe
    crystal = await universe.get(Crystal, event.data["id"])
```

---

## Quick Reference

```python
# Get universe
universe = await get_universe()

# CRUD operations
await universe.put(obj)
obj = await universe.get(Model, id)
objects = await universe.query(Model, filters={...})
await universe.delete(Model, id)

# Event bus
bus = await get_data_bus()
bus.subscribe("topic", handler)
await bus.emit("topic", data)

# Backends
universe = await get_universe(backend="memory")   # Dev
universe = await get_universe(backend="jsonl")    # Local
universe = await get_universe(backend="postgres") # Prod
```

---

## Related Skills

- [metaphysical-fullstack.md](metaphysical-fullstack.md) — Architecture context
- [data-bus-integration.md](data-bus-integration.md) — Detailed event wiring
- [crown-jewel-patterns.md](crown-jewel-patterns.md) — Service patterns
- [test-patterns.md](test-patterns.md) — Testing storage

---

*"One truth, one store: All Crown Jewels share Universe for typed data."*
