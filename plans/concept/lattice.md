# Lattice & Lineage: concept.*.define Implementation

> *"No concept exists ex nihilo. The Lattice enforces genealogy."*

**AGENTESE Context**: `concept.*.define`
**Status**: Theoretical Foundation, Implementation Planned
**Principles**: Generative, Composable

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Required lineage** | `extends` must be non-empty. No orphan concepts. |
| **L-gent consistency** | Lattice position verified before creation |
| **Affordance inheritance** | Union of parents (additive) |
| **Constraint inheritance** | Intersection of parents (restrictive) |
| **Justification required** | Why does this concept need to exist? |

---

## The Genealogical Constraint

Traditional systems allow arbitrary concept creation. AGENTESE requires **lineage**:

```python
# This FAILS:
await logos.invoke("concept.new_thing.define", spec="...")
# → LineageError: Concepts cannot exist ex nihilo.

# This WORKS:
await logos.invoke(
    "concept.new_thing.define",
    spec="...",
    extends=["concept.existing_thing"],  # Required!
    justification="Specializes X for Y use case"
)
```

---

## Lattice Structure

```
                    ┌─────────────┐
                    │   concept   │  (Top)
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐    ┌─────▼────┐    ┌────▼────┐
      │  world  │    │   self   │    │  void   │
      └────┬────┘    └────┬─────┘    └────┬────┘
           │              │               │
    ┌──────┴──────┐       │         ┌─────┴─────┐
    │             │       │         │           │
┌───▼───┐   ┌─────▼──┐  ┌─▼──┐   ┌──▼───┐  ┌───▼────┐
│cluster│   │project │  │cli │   │entropy│  │capital │
└───────┘   └────────┘  └────┘   └───────┘  └────────┘
```

Every node has parents (except `concept` itself). The lattice enables:
- **Meet**: Find common ancestor
- **Join**: Find common descendant
- **Subtyping**: Child affordances ⊇ parent affordances

---

## define_concept (📋 PLANNED)

```python
async def define_concept(
    logos: Logos,
    handle: str,
    observer: Umwelt,
    spec: str,
    extends: list[str],      # REQUIRED: parent concepts
    subsumes: list[str] | None = None,
    justification: str = ""  # Why does this need to exist?
) -> LogosNode:
    """
    Create a new concept with required lineage.

    AGENTESE: concept.*.define
    """
    if not extends:
        raise LineageError(
            "Concepts cannot exist ex nihilo. "
            "Provide at least one parent. "
            "Consider: What existing concept does this specialize?"
        )

    # Validate parents exist
    for parent in extends:
        try:
            await logos.resolve(parent)
        except PathNotFoundError:
            raise LineageError(f"Parent '{parent}' does not exist.")

    # L-gent lattice consistency
    consistency = await l_gent.check_lattice_position(
        new_handle=handle,
        parents=extends,
        children=subsumes or []
    )

    if not consistency.valid:
        raise LatticeError(f"Violates lattice: {consistency.reason}")

    # Proceed with creation
    ...
```

**Location**: `protocols/agentese/lattice/define.py`

---

## Inheritance Semantics

| Property | Inheritance | Example |
|----------|-------------|---------|
| **Affordances** | Union (additive) | Child can do everything parents can |
| **Constraints** | Intersection (restrictive) | Child must satisfy all parent constraints |
| **Defaults** | Override | Child can override parent defaults |

```python
# world.cluster extends world
# world.cluster.manifest inherits world.manifest affordance
# world.cluster adds cluster-specific affordances

# self.cli extends self
# self.cli.invoke inherits self.invoke
# self.cli adds ghost affordance
```

---

## L-gent Consistency Check

```python
class LatticeConsistencyChecker:
    """
    Verify lattice position before concept creation.

    Checks:
    1. No cycles (DAG property)
    2. Meet/join exist (lattice property)
    3. Affordance compatibility
    """

    async def check_lattice_position(
        self,
        new_handle: str,
        parents: list[str],
        children: list[str],
    ) -> ConsistencyResult:
        # Check for cycles
        if self._would_create_cycle(new_handle, parents, children):
            return ConsistencyResult(
                valid=False,
                reason="Would create cycle in lattice"
            )

        # Check affordance compatibility
        parent_affordances = await self._get_affordances(parents)
        if not self._affordances_compatible(parent_affordances):
            return ConsistencyResult(
                valid=False,
                reason="Parent affordances conflict"
            )

        return ConsistencyResult(valid=True)
```

---

## CLI Visualization (📋 PLANNED)

```bash
kgents map --lattice
```

Output:
```
LATTICE VIEW
============

concept
├── world
│   ├── cluster
│   │   ├── agents
│   │   └── workflow
│   └── project
├── self
│   ├── cli
│   ├── stream
│   └── memory
├── void
│   ├── entropy
│   ├── capital
│   └── pheromone
├── time
│   ├── trace
│   └── kairos
└── concept
    └── (this lattice)

Edges: 23 | Depth: 4 | Orphans: 0
```

---

## AGENTESE Path Registry

| Path | Operation | Description |
|------|-----------|-------------|
| `concept.*.define` | Create | New concept with lineage |
| `concept.*.manifest` | View | Concept definition |
| `concept.*.extends` | Query | Get parent concepts |
| `concept.*.subsumes` | Query | Get child concepts |
| `concept.*.affordances` | Query | Get all affordances |

---

## Error Types

```python
class LineageError(Exception):
    """Concept has no valid lineage."""
    pass

class LatticeError(Exception):
    """Concept violates lattice properties."""
    pass

class OrphanError(LineageError):
    """Concept has no parents (orphan)."""
    pass
```

---

## Cross-References

- **Plans**: `self/stream.md` (Comonadic structure)
- **Impl**: `protocols/agentese/lattice/` (planned), `agents/l/` (L-gent)
- **Spec**: `spec/protocols/agentese.md` (Five Contexts)

---

*"The lattice is not a cage—it is a family tree."*
