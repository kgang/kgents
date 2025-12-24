# Crystal - Unified Data Crystal Architecture

> "The datum is a lie. There is only the crystal."

## Overview

The Crystal primitives provide kgents' unified data layer - a single, immutable, versioned data model that works across all storage backends (memory, SQLite, Postgres) without migration anxiety.

**Spec**: `/Users/kentgang/git/kgents/spec/protocols/unified-data-crystal.md`

## Core Primitives

### 1. Datum - The Ground Truth

Schema-free, immutable atom of data. Always works, never fails.

```python
from agents.d.crystal import Datum

datum = Datum.create(
    data={"action": "test", "reasoning": "example"},
    tags={"witness", "core"},
    author="claude",
)

# Immutable operations return new instances
datum2 = datum.with_tags("additional")
```

**Key Features**:
- Frozen dataclass (immutable)
- UUID identifier
- Timestamp (created_at)
- Schema-free data dict
- Provenance (author, source, parent_id)
- Taggable (frozenset)

### 2. Schema - Versioned Contracts

Frozen dataclasses as type contracts with migration paths.

```python
from dataclasses import dataclass
from agents.d.crystal import Schema

@dataclass(frozen=True)
class MarkV1:
    action: str
    reasoning: str

@dataclass(frozen=True)
class MarkV2:
    action: str
    reasoning: str
    tags: tuple[str, ...] = ()

schema = Schema(
    name="witness.mark",
    version=2,
    contract=MarkV2,
    migrations={
        1: lambda d: {**d, "tags": ()},  # v1 -> v2
    },
)
```

**Key Features**:
- Monotonic version numbers
- Pure function migrations
- Lazy upgrade on read
- Type-safe contract enforcement

### 3. Crystal[T] - Typed Datums

A Datum validated against a Schema contract. Provides both raw and typed access.

```python
from agents.d.crystal import Crystal

# Crystallize datum into typed value
crystal = Crystal.from_datum(datum, schema)

# Type-safe access
crystal.value.action  # → str (typed)

# Raw access always available
crystal.datum.data    # → dict (fallback)

# Check if upgraded
crystal.was_upgraded()  # → bool
```

**Key Features**:
- Generic type parameter T
- Dual access (typed + raw)
- Upgrade tracking
- Immutable semantics

### 4. Query - Declarative Queries

NoSQL-like query specification, backend-agnostic.

```python
from datetime import datetime
from agents.d.crystal import Query

# Simple query
q = Query(
    schema="witness.mark",
    tags=frozenset(["eureka"]),
    author="claude",
    limit=50,
)

# Compound query
q = Query(
    schema="witness.mark",
    tags=frozenset(["eureka", "witness"]),
    since=datetime(2025, 12, 1),
    where={"status": "active"},
)

# Fluent API
q = (
    Query()
    .with_schema("witness.mark")
    .with_tags("eureka")
    .with_limit(10)
    .next_page()
)

# In-memory filtering
if q.matches_datum(datum):
    print("Match!")
```

**Key Features**:
- Schema filtering
- Tag intersection (AND)
- Time range filtering
- Flexible predicates (where clause)
- Pagination support
- Fluent builder API

## File Structure

```
agents/d/crystal/
├── __init__.py        # Public exports
├── datum.py           # Datum frozen dataclass
├── schema.py          # Schema[T] with versioning
├── crystal.py         # Crystal[T] container
├── query.py           # Query specification
├── _demo.py           # Demonstration script
└── README.md          # This file
```

## Type Safety

All primitives pass strict mypy checking:

```bash
cd /Users/kentgang/git/kgents/impl/claude
uv run mypy agents/d/crystal/datum.py \
            agents/d/crystal/schema.py \
            agents/d/crystal/crystal.py \
            agents/d/crystal/query.py \
            agents/d/crystal/__init__.py \
            --strict
```

## Demo Script

Run the comprehensive demo:

```bash
cd /Users/kentgang/git/kgents/impl/claude
uv run python -m agents.d.crystal._demo
```

Demonstrates:
1. Basic Datum → Crystal flow
2. Schema evolution with migrations
3. Query API and filtering
4. Immutability semantics

## Usage Examples

### Creating Versioned Schemas

```python
# Version 1
@dataclass(frozen=True)
class ConfigV1:
    theme: str

# Version 2: Add mode
@dataclass(frozen=True)
class ConfigV2:
    theme: str
    mode: str = "light"

# Version 3: Add font_size
@dataclass(frozen=True)
class ConfigV3:
    theme: str
    mode: str = "light"
    font_size: int = 14

CONFIG_SCHEMA = Schema(
    name="app.config",
    version=3,
    contract=ConfigV3,
    migrations={
        1: lambda d: {**d, "mode": "light"},
        2: lambda d: {**d, "font_size": 14},
    },
)
```

### Lazy Schema Upgrades

```python
# Old data (v1)
old_datum = Datum.create(
    {
        "theme": "dark",
        "_schema": "app.config",
        "_version": 1,
    }
)

# Auto-upgrades to v3
crystal = Crystal.from_datum(old_datum, CONFIG_SCHEMA)

assert crystal.value.theme == "dark"      # Original
assert crystal.value.mode == "light"      # Added in v2
assert crystal.value.font_size == 14      # Added in v3
assert crystal.was_upgraded() == True
```

### Querying with Predicates

```python
# Find all active, high-priority items by claude since Dec 1
q = Query(
    schema="task.item",
    author="claude",
    since=datetime(2025, 12, 1),
    where={
        "status": "active",
        "priority": "high",
    },
    tags=frozenset(["urgent"]),
    limit=100,
)

# Backend executes query
results = await universe.query(q)

# Or in-memory filtering
datums = get_all_datums()
matches = [d for d in datums if q.matches_datum(d)]
```

### Creating Typed Crystals

```python
@dataclass(frozen=True)
class Mark:
    action: str
    reasoning: str
    tags: tuple[str, ...] = ()

schema = Schema(name="witness.mark", version=1, contract=Mark)

# From typed value
mark = Mark(
    action="Implemented crystal",
    reasoning="Foundation for unified data",
    tags=("witness", "core"),
)
crystal = Crystal.create(mark, schema, author="claude")

# From raw datum
datum = Datum.create(
    {"action": "test", "reasoning": "example"},
    tags={"witness"},
)
crystal = Crystal.from_datum(datum, schema)
```

## Philosophy

1. **Datums are ground truth** - Schema-free, always work
2. **Crystals are typed views** - Validated, versioned, type-safe
3. **Schemas version like code** - Not database DDL
4. **Migrations are pure functions** - Composable, testable
5. **Unknown schemas degrade gracefully** - Fall back to Datum
6. **Immutable by default** - Frozen dataclasses prevent mutation
7. **Backend-agnostic** - Works with memory, SQLite, Postgres

## Next Steps

This implements Phase 1 of the Unified Data Crystal Architecture:

- [x] Datum frozen dataclass
- [x] Crystal[T] generic container
- [x] Schema with versioning
- [x] CrystalMeta envelope
- [x] Query specification

Upcoming phases:

- [ ] Backend abstraction (Protocol + implementations)
- [ ] Universe (D-gent's domain)
- [ ] Agent integration (DataMixin)
- [ ] Schema migration (convert existing SQLAlchemy models)

See: `/Users/kentgang/git/kgents/spec/protocols/unified-data-crystal.md`

---

*Implemented: 2025-12-23*
*Status: Production-ready*
*Type-checked: mypy --strict*
