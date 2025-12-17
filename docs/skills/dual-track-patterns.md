# Dual-Track Persistence Patterns

> *"Agent cognition needs serendipity. Application state needs consistency."*

## Overview

The dual-track architecture separates persistence into two complementary tracks:

| Track | Purpose | Schema | Migration | Access Pattern |
|-------|---------|--------|-----------|----------------|
| **Agent Memory** (D-gent) | Cognition, association, serendipity | Schema-free (Datum) | None (append-only) | Lenses, semantic search |
| **Application State** (Alembic) | Consistent app data | Typed (SQLAlchemy) | Versioned | SQL, ORM queries |

## Key Files

```
impl/claude/
├── agents/d/adapters/table_adapter.py   # Bridge functor
├── agents/s/state_functor.py            # State threading
├── services/bootstrap.py                # DI for all 7 Crown Jewels
├── models/*.py                          # SQLAlchemy models
└── system/migrations/versions/          # Alembic migrations
```

---

## Pattern 1: TableAdapter (Bridge Functor)

TableAdapter lifts Alembic tables into DgentProtocol, enabling agent access to typed data.

```python
from agents.d import TableAdapter
from models.brain import Crystal

# Create adapter
adapter = TableAdapter(
    model=Crystal,
    session_factory=session_factory,
)

# Use like DgentProtocol
datum = await adapter.get("crystal-123")
await adapter.put(datum)
chain = await adapter.causal_chain("crystal-123")
```

**Key insight**: The functor is lossy (typed → bytes) but preserves provenance via `metadata["source"] = "alembic"`.

---

## Pattern 2: StateFunctor (State Threading)

StateFunctor lifts agents into stateful computation with automatic load/save.

```python
from agents.s import StateFunctor, MemoryStateBackend

# Create backend with initial state
backend = MemoryStateBackend(initial={"count": 0})

# Define logic function: (input, state) -> (output, new_state)
def counter(msg: str, state: dict) -> tuple[str, dict]:
    new_count = state["count"] + 1
    return f"Count: {new_count}", {"count": new_count}

# Lift to stateful agent
agent = StateFunctor.lift_logic(counter, backend=backend)

# State threads automatically
await agent.invoke("tick")  # "Count: 1"
await agent.invoke("tick")  # "Count: 2"
```

---

## Pattern 3: Bootstrap DI

All 7 Crown Jewels wire through centralized dependency injection.

```python
from services.bootstrap import bootstrap_services, get_service

# At app startup
await bootstrap_services()

# In handlers
brain = await get_service("brain_persistence")
result = await brain.capture("Hello world")

# For testing
from services.bootstrap import inject_service, reset_services
reset_services()
inject_service("brain_persistence", mock_brain)
```

**Available services**:
- `brain_persistence`
- `town_persistence`
- `gardener_persistence`
- `gestalt_persistence`
- `atelier_persistence`
- `coalition_persistence`
- `park_persistence`

---

## Pattern 4: Hybrid Storage (Brain Example)

Store queryable metadata in Alembic, semantic content in D-gent.

```python
async def capture_crystal(content: str, tags: list[str]):
    # 1. Store semantic content in D-gent (for associations)
    datum = Datum(
        id=uuid4().hex,
        content=content.encode(),
        metadata={"type": "crystal", "tags": tags},
    )
    await dgent.put(datum)

    # 2. Store queryable metadata in Alembic table
    crystal = Crystal(
        id=uuid4().hex,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        summary=content[:200],
        tags=tags,
        datum_id=datum.id,  # Link to D-gent
    )
    session.add(crystal)
    await session.commit()
```

---

## Pattern 5: AGENTESE Table Access

Access tables via AGENTESE paths.

```python
# Via Logos
await logos.invoke("self.data.table.crystal.get", umwelt, id="123")
await logos.invoke("self.data.table.crystal.list", umwelt, limit=10)

# The resolver maps:
# self.data.*        -> D-gent (agent memory)
# self.data.table.*  -> TableAdapter (application state)
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Instead |
|--------------|--------------|---------|
| Schema in Datum content | Reinventing Alembic inside D-gent | Use TableAdapter for typed data |
| ORM for agent memory | Forcing types on associative cognition | Use Datum for flexible content |
| Direct table access from agents | Bypasses bridge, loses provenance | Use TableAdapter |
| Eager migration | Not all data needs schema | Only app state needs migrations |

---

## Laws

### Agent Memory Laws
1. **Append-only**: `put` is idempotent
2. **Causality**: Every `Datum` knows its `causal_parent`
3. **Lens composition**: `(f >> g) >> h = f >> (g >> h)`

### Application State Laws
1. **Migration idempotence**: Apply twice = apply once
2. **Forward-only in production**: Downgrades only for dev
3. **Schema evolution**: New columns nullable or with defaults

### Bridge Laws
1. **Round-trip**: `adapter.get(adapter.put(datum).id) ≅ datum`
2. **Source tagging**: `datum.metadata["source"] == "alembic"`
3. **Isolation**: Agent memory changes don't affect tables (unless explicit)

---

## Related

- `spec/d-gents/README.md` — D-gent philosophy
- `spec/s-gents/state-functor.md` — StateFunctor spec
- `plans/d-gent-dual-track-architecture.md` — Full plan
- `docs/skills/building-agent.md` — Agent patterns

---

*"The same categorical structure underlies everything."*
