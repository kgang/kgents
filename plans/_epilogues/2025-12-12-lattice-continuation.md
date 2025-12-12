# Session Continuation: Lattice Implementation

**Date**: 2025-12-12
**Focus**: `concept/lattice` — Wire to `concept.*.define`
**Priority**: PRIMARY (60% attention per `_focus.md`)

---

## Context

You are implementing the **Lattice & Lineage** system for AGENTESE. This enforces the genealogical constraint: *"No concept exists ex nihilo."*

**Plan**: `plans/concept/lattice.md` (read it first)
**Progress**: 60% (foundation exists, wiring needed)

---

## Your Mission

Implement **Chunk 1-3** from the plan:

1. **ConceptLineage** dataclass in `protocols/agentese/contexts/concept.py`
2. **LatticeConsistencyChecker** in new file `protocols/agentese/lattice/checker.py`
3. **define_concept** function wired to `concept.*.define` aspect

---

## Existing Infrastructure (Use These)

| Module | Key Classes | Purpose |
|--------|-------------|---------|
| `agents/l/lattice.py` | `TypeLattice` | Subtyping, meet, join, cycle detection |
| `agents/l/advanced_lattice.py` | `AdvancedLattice` | Union/intersection types, variance |
| `protocols/agentese/logos.py` | `Logos` | Path resolution, aspect invocation |
| `protocols/agentese/contexts/concept.py` | (target) | Add `define` aspect here |

---

## Key Constraints

1. `extends` parameter is **REQUIRED** (non-empty list)
2. All parents must exist in registry
3. Lattice position must pass `check_position()` (no cycles, compatible affordances)
4. Affordances inherit as **union** (additive)
5. Constraints inherit as **intersection** (restrictive)

---

## Tests to Write

```python
# protocols/agentese/lattice/_tests/test_lineage.py
def test_lineage_required():
    """Creating concept without extends raises LineageError."""

def test_lineage_parents_must_exist():
    """All parents must exist in registry."""

def test_affordance_inheritance_is_union():
    """Child affordances ⊇ parent affordances."""

def test_constraint_inheritance_is_intersection():
    """Child constraints = ∩(parent constraints)."""

def test_cycle_detection():
    """Adding concept that creates cycle is rejected."""

def test_define_happy_path():
    """Valid concept with lineage succeeds."""
```

---

## File Structure to Create

```
impl/claude/protocols/agentese/lattice/
├── __init__.py
├── checker.py          # LatticeConsistencyChecker
├── lineage.py          # ConceptLineage dataclass
└── _tests/
    ├── __init__.py
    └── test_lineage.py
```

---

## Exit Criteria

- [ ] `LineageError` raised when `extends=[]`
- [ ] `LatticeError` raised on cycle detection
- [ ] Affordances computed as union of parents
- [ ] Constraints computed as intersection of parents
- [ ] 20+ tests passing
- [ ] `kgents map --lattice` shows tree (Chunk 4, optional)

---

## Spirit

> *"The lattice is not a cage—it is a family tree. Every branch knows its roots."*

Enforce lineage. Build the family. Let no concept stand alone.

---

*Run `cat plans/concept/lattice.md` for full context.*
