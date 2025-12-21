# Dual-Track Architecture

> *"Memory is not monolithic. Agent cognition and application state serve different masters."*

---

## Purpose

Support both **agent-native memory** (crystals, associations, serendipity) AND **normative relational data** (users, sessions, schemas with migrations) within a unified persistence philosophy.

---

## The Core Insight

Two tracks serve different needs:

| Track | Purpose | Schema | Migration | Access Pattern |
|-------|---------|--------|-----------|----------------|
| **Agent Memory** | Cognition, association, serendipity | Schema-free (Datum) | None (append-only) | Lenses, semantic search |
| **Application State** | Consistent app data | Typed (Alembic) | Versioned | SQL, ORM queries |

**The key realization**: Don't force D-gent to support migrations. Each track excels at what it's designed for, with a bridge functor for unified access.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMBRANE (Unified Persistence)                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              D-GENT TRACK (Agent Memory)                   │ │
│  │  - Datum abstraction (bytes + causality)                   │ │
│  │  - Projection lattice (Memory → JSONL → SQLite → Postgres) │ │
│  │  - Lens algebra (focused access)                           │ │
│  │  - Semantic/temporal/relational modes                      │ │
│  │  - AGENTESE: self.data.*                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           ALEMBIC TRACK (Application State)                │ │
│  │  - Typed models (SQLAlchemy or raw SQL)                    │ │
│  │  - Migration versioning (forward-only in prod)             │ │
│  │  - Foreign keys, indices, constraints                      │ │
│  │  - Query builder (SQL or ORM)                              │ │
│  │  - AGENTESE: self.data.table.*                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               BRIDGE (TableAdapter)                        │ │
│  │  - Lifts Alembic tables → DgentProtocol                    │ │
│  │  - Enables lens composition on typed data                  │ │
│  │  - Bidirectional: table ↔ Datum                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Formal Definition

### The Agent Memory Category

Objects: `Datum[namespace]` — typed by namespace, not content schema
Morphisms: `Lens[S, A]` — focusing operations that compose

```python
AGENT_MEMORY = Category(
    objects={"crystals", "associations", "traces", "garden_entries"},
    morphisms=LensAlgebra,
    identity=identity_lens,
    composition=lambda f, g: f >> g  # Lens composition
)
```

### The Application State Category

Objects: `Table[T]` — SQLAlchemy models or raw tables
Morphisms: `Migration` — schema transformations

```python
APP_STATE = Category(
    objects={User, Session, Crystal, CitizenMemory, GardenEntry},
    morphisms=AlembicMigration,
    identity=no_op_migration,
    composition=sequential_migration
)
```

### The Bridge Functor

```python
Bridge: APP_STATE → AGENT_MEMORY
Bridge(Table[T]) = DgentProtocol where content = serialize(T)
```

This functor is **lossy** (schema → bytes loses type info) but enables agent access to application state through familiar patterns.

---

## TableAdapter: The Bridge Functor

```python
class TableAdapter(DgentProtocol, Generic[T]):
    """
    Lifts an Alembic-managed table into DgentProtocol.

    Enables agent access to application state via the same
    patterns used for agent memory (lenses, causal chains).

    Category-theoretic: This is a functor APP_STATE → AGENT_MEMORY.
    """

    def __init__(
        self,
        model: Type[T],
        session_factory: Callable[[], AsyncSession],
        id_field: str = "id",
        serialize: Callable[[T], bytes] = default_serialize,
        deserialize: Callable[[bytes], T] = default_deserialize,
    ):
        self.model = model
        self.session_factory = session_factory
        self.id_field = id_field
        self.serialize = serialize
        self.deserialize = deserialize

    async def put(self, datum: Datum) -> str:
        """Store datum by upserting into the Alembic table."""
        instance = self.deserialize(datum.content)
        async with self.session_factory() as session:
            # Upsert pattern
            existing = await session.get(self.model, datum.id)
            if existing:
                for key, value in instance.__dict__.items():
                    if not key.startswith("_"):
                        setattr(existing, key, value)
            else:
                session.add(instance)
            await session.commit()
        return datum.id

    async def get(self, id: str) -> Datum | None:
        """Retrieve from table, return as Datum."""
        async with self.session_factory() as session:
            instance = await session.get(self.model, id)
            if instance is None:
                return None
            return Datum(
                id=getattr(instance, self.id_field),
                content=self.serialize(instance),
                created_at=getattr(instance, "created_at", time.time()),
                causal_parent=getattr(instance, "causal_parent", None),
                metadata={"source": "alembic", "table": self.model.__tablename__},
            )
```

---

## Laws

### Agent Memory Laws (Preserved)
1. **Append-only**: `put` is idempotent (same content → same result)
2. **Causality**: Every `Datum` knows its `causal_parent`
3. **Lens composition**: `(f >> g) >> h = f >> (g >> h)`

### Application State Laws (New)
1. **Migration idempotence**: Applying migration twice = applying once
2. **Forward-only in production**: Downgrades only for development
3. **Schema evolution**: New columns nullable or with defaults

### Bridge Laws (New)
1. **Round-trip**: `TableAdapter.get(TableAdapter.put(datum).id) ≅ datum`
2. **Source tagging**: `Datum.metadata["source"] == "alembic"` for bridged data
3. **Isolation**: Agent memory changes don't affect Alembic tables (unless explicit)

---

## AGENTESE Paths

| Path | Track | Description |
|------|-------|-------------|
| `self.data.put[content]` | Agent Memory | Store raw bytes |
| `self.data.get[id]` | Agent Memory | Retrieve by ID |
| `self.data.table.{name}.get[id]` | App State | Get typed row |
| `self.data.table.{name}.put[instance]` | App State | Upsert typed row |
| `self.data.table.{name}.list` | App State | Query table |

---

## Crown Jewel Examples

### Brain: Hybrid Crystal Storage

```python
# Alembic table for queryable metadata
class Crystal(Base):
    __tablename__ = "brain_crystals"
    id: Mapped[str] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(index=True)
    summary: Mapped[str]
    tags: Mapped[list[str]] = mapped_column(JSON)
    access_count: Mapped[int] = mapped_column(default=0)
    datum_id: Mapped[str | None]  # Link to D-gent for semantic content

# Usage: semantic content in D-gent, queryable metadata in Alembic
await dgent.put(datum)  # Semantic content
session.add(crystal)     # Queryable metadata
```

### Town: Citizen Memory with Causality

```python
# Alembic table tracks conversation metadata
class CitizenConversation(Base):
    __tablename__ = "citizen_conversations"
    citizen_name: Mapped[str] = mapped_column(index=True)
    turn_count: Mapped[int]
    datum_chain_head: Mapped[str | None]  # Head of D-gent causal chain
```

---

## State Threading (State Functor Integration)

The dual-track architecture provides the **persistence substrate**.
The State Functor provides the **state threading**.

Composition: `StateFunctor >> D-gent`

```python
# StateFunctor backed by TableAdapter
state_functor = StateFunctor.from_table_adapter(
    adapter=TableAdapter(Crystal, session_factory),
    initial_state=Crystal(id="default", tags=[]),
)

# Result: state threading + typed persistence (dual-track D-gent)
```

See `c-gents/functor-catalog.md` §14 for State Functor specification.

---

## Anti-patterns

- **Schema in Datum content**: Don't reinvent Alembic inside D-gent
- **ORM for agent memory**: Don't force typed models on associative cognition
- **Mixing tracks without bridge**: Don't access Alembic tables directly from agents
- **Eager migration**: Don't migrate everything to Alembic; only app state needs it

---

## See Also

- [architecture.md](architecture.md) — D-gent core architecture
- [protocols.md](protocols.md) — DgentProtocol interface
- [symbiont.md](symbiont.md) — The Symbiont composition pattern
- [../c-gents/functor-catalog.md](../c-gents/functor-catalog.md) — Functor catalog (§14: State Functor)

---

*"Agent cognition needs serendipity. Application state needs consistency. The dual-track architecture gives each what it needs."*
