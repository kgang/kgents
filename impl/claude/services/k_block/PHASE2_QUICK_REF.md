# Phase 2 Quick Reference

## TL;DR

Zero Seed nodes (L1-L7) are now K-Blocks with derivation tracking.

```python
from services.k_block.zero_seed_storage import get_zero_seed_storage

storage = get_zero_seed_storage()

# Create L1 axiom
_, axiom_id = storage.create_node(
    layer=1, title="Entity", content="Everything is a node."
)

# Create L2 value deriving from axiom
_, value_id = storage.create_node(
    layer=2, title="Composability", content="Agents compose.",
    lineage=[axiom_id]
)

# Trace lineage
lineage = storage.get_lineage(value_id)  # → [axiom_id]
is_grounded = storage.is_grounded(value_id)  # → True
```

## Layer Hierarchy

```
L1 (Axioms)         confidence=1.0   path=void.axiom.*
  ↓
L2 (Values)         confidence=0.95  path=void.value.*
  ↓
L3 (Goals)          confidence=0.90  path=concept.goal.*
  ↓
L4 (Specs)          confidence=0.85  path=concept.spec.*
  ↓
L5 (Actions)        confidence=0.80  path=world.action.*
  ↓
L6 (Reflections)    confidence=0.75  path=self.reflection.*
  ↓
L7 (Documents)      confidence=0.70  path=void.representation.*
```

## API Endpoints

```bash
# Create
POST /api/zero-seed/nodes
{
  "layer": 1,
  "title": "Entity Axiom",
  "content": "Everything is a node.",
  "lineage": [],
  "tags": ["foundational"]
}

# Read
GET /api/zero-seed/nodes/{node_id}

# Update
PUT /api/zero-seed/nodes/{node_id}
{
  "title": "Updated Title",
  "content": "New content",
  "confidence": 0.85
}

# Delete
DELETE /api/zero-seed/nodes/{node_id}
```

## Files

| Path | Purpose |
|------|---------|
| `core/derivation.py` | DerivationDAG for lineage tracking |
| `layers/factories.py` | L1-L7 K-Block factories |
| `zero_seed_storage.py` | CRUD operations + storage |
| `_tests/test_derivation.py` | DAG tests (12) |
| `_tests/test_layer_factories.py` | Factory tests (16) |
| `_tests/test_zero_seed_storage.py` | Storage tests (18) |

## Tests

```bash
# Run all Phase 2 tests
cd impl/claude
uv run pytest services/k_block/_tests/test_derivation.py -v
uv run pytest services/k_block/_tests/test_layer_factories.py -v
uv run pytest services/k_block/_tests/test_zero_seed_storage.py -v

# All k_block tests (241 total)
uv run pytest services/k_block/ -q
```

✅ **All 241 tests passing**
