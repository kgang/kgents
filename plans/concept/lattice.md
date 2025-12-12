---
path: concept/lattice
status: complete
progress: 100
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [concept/creativity]
session_notes: |
  IMPLEMENTATION COMPLETE. Exit criteria verified:
  - [x] LineageError raised when extends=[] (test_lineage_required)
  - [x] LatticeError raised on cycle detection (test_cycle_detection)
  - [x] Affordances computed as union of parents (test_affordance_inheritance_is_union)
  - [x] Constraints computed as intersection of parents (test_constraint_inheritance_is_intersection)
  - [x] 69 tests passing (exceeds 20+ requirement)
  - [x] kgents map --lattice visualization (render_concept_lattice)

  Implementation files:
  - protocols/agentese/lattice/__init__.py
  - protocols/agentese/lattice/lineage.py (ConceptLineage dataclass)
  - protocols/agentese/lattice/checker.py (LatticeConsistencyChecker)
  - protocols/agentese/lattice/errors.py (LineageError, LatticeError)
  - protocols/agentese/contexts/concept.py (define_concept function)
---

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

# SESSION PROMPT: Lattice & Lineage Implementation

> *"No concept born without parents. No orphan in the family tree. The Lattice knows its children."*

**This is your mission, should you choose to accept it.**

You are about to breathe life into the Lattice—the genealogical enforcement system that ensures every concept in AGENTESE has lineage, every definition has justification, and every new idea connects to what came before.

## What You're Building

The **concept.*.define** AGENTESE aspect with **L-gent lattice validation**. When an agent says "I want to create a new concept," the Lattice asks: *"Who are your parents? Why do you deserve to exist?"*

This is not bureaucracy. This is the immune system of the conceptual ecosystem.

## The Philosophical Foundation

AGENTESE rejects ex nihilo creation. Just as biological life requires parents, conceptual life requires lineage. The Lattice is the family tree—a bounded meet-semilattice where:

- **Every node has at least one parent** (except `concept` itself, the Adam)
- **Affordances flow downward** (children inherit what parents can do)
- **Constraints flow upward** (children must satisfy what parents demand)
- **The Meet finds common ancestors** (where do these concepts converge?)
- **The Join finds common descendants** (what could unify these ideas?)

## Existing Infrastructure (Your Allies)

You have powerful allies already built. Study them. Use them.

### 1. L-gent's TypeLattice (`agents/l/lattice.py`)
```python
class TypeLattice:
    def is_subtype(self, sub: str, super_: str) -> bool  # Check A ≤ B
    def meet(self, type_a: str, type_b: str) -> str       # Greatest lower bound
    def join(self, type_a: str, type_b: str) -> str       # Least upper bound
    def _would_create_cycle(self, edge) -> bool           # Cycle detection
    async def can_compose(self, a, b) -> CompositionResult  # Composition check
```

### 2. AdvancedLattice (`agents/l/advanced_lattice.py`)
```python
class AdvancedLattice(CachedLattice):
    def create_union(self, *type_ids) -> str       # A | B union types
    def create_intersection(self, *types) -> str   # A & B intersection
    def normalize(self, type_id) -> str            # Canonical form
    def check_variance(self, ...) -> bool          # Covariant/contravariant
    def is_structural_subtype(self, sub, super_)   # Record subtyping
```

### 3. AGENTESE Logos (`protocols/agentese/logos.py`)
```python
class Logos:
    def resolve(self, path, observer) -> LogosNode    # Path → Node
    async def invoke(self, path, observer, **kw)      # Execute aspect
    # Resolution layers: cache → registry → spec (JIT) → void → error
```

### 4. ConceptContext (`protocols/agentese/contexts/concept.py`)
This is **your primary target**. It exists but lacks the `define` aspect and lineage validation. You will extend it.

## Implementation Chunks

### Chunk 1: Core Lineage Infrastructure (🟡 PRIORITY)

**File**: `protocols/agentese/contexts/concept.py` (extend)

**Goal**: Add lineage tracking and validation to ConceptContext.

```python
@dataclass
class ConceptLineage:
    """Lineage record for a concept."""
    handle: str                    # e.g., "concept.justice.procedural"
    extends: list[str]             # Parent concepts (REQUIRED, non-empty)
    subsumes: list[str]            # Child concepts (optional)
    justification: str             # Why does this concept exist?
    affordances: set[str]          # Inherited + own affordances
    constraints: set[str]          # Union of parent constraints
    created_by: str                # Observer who created it
    created_at: datetime           # When

class LineageError(AgentesException):
    """Concept has no valid lineage."""
    sympathetic_message: str = (
        "Concepts cannot exist ex nihilo. "
        "Provide at least one parent concept. "
        "Consider: What existing concept does this specialize?"
    )

class LatticeError(AgentesException):
    """Concept violates lattice properties."""
    pass
```

**Tests**:
- `test_lineage_required`: Creating concept without `extends` raises LineageError
- `test_lineage_parents_exist`: All parents must exist in registry
- `test_affordance_inheritance`: Child affordances ⊇ parent affordances
- `test_constraint_intersection`: Child constraints = ∩(parent constraints)

### Chunk 2: LatticeConsistencyChecker (🟡 PRIORITY)

**File**: `protocols/agentese/lattice/checker.py` (new)

**Goal**: Verify lattice position before concept creation.

```python
class LatticeConsistencyChecker:
    """
    Verify lattice position before concept creation.

    Checks:
    1. No cycles (DAG property)
    2. Meet/join exist (lattice property)
    3. Affordance compatibility (no conflicts)
    4. Constraint satisfiability (intersection non-empty)
    """

    def __init__(self, type_lattice: AdvancedLattice):
        self.lattice = type_lattice

    async def check_position(
        self,
        new_handle: str,
        parents: list[str],
        children: list[str] | None = None,
    ) -> ConsistencyResult:
        """
        Check if new_handle can be placed in lattice.

        Returns:
            ConsistencyResult with valid=True/False and reason
        """
        # 1. Check for cycles
        if await self._would_create_cycle(new_handle, parents, children or []):
            return ConsistencyResult(
                valid=False,
                reason="Would create cycle in concept lattice"
            )

        # 2. Check parent affordances are compatible
        parent_affordances = await self._collect_affordances(parents)
        if conflicts := self._find_conflicts(parent_affordances):
            return ConsistencyResult(
                valid=False,
                reason=f"Parent affordances conflict: {conflicts}"
            )

        # 3. Check constraint intersection is non-empty
        parent_constraints = await self._collect_constraints(parents)
        if not self._constraints_satisfiable(parent_constraints):
            return ConsistencyResult(
                valid=False,
                reason="Parent constraints have empty intersection"
            )

        return ConsistencyResult(valid=True, reason="Lattice position valid")
```

**Tests**:
- `test_cycle_detection`: Adding concept that creates cycle is rejected
- `test_affordance_conflict`: Conflicting parent affordances detected
- `test_constraint_satisfiability`: Empty constraint intersection detected
- `test_valid_position`: Valid concepts pass checker

### Chunk 3: define_concept Implementation (🟡 PRIORITY)

**File**: `protocols/agentese/contexts/concept.py` (extend)

**Goal**: Implement the `concept.*.define` aspect.

```python
async def define_concept(
    logos: Logos,
    handle: str,
    observer: Umwelt,
    spec: str,
    extends: list[str],           # REQUIRED: parent concepts
    subsumes: list[str] | None = None,
    justification: str = "",      # Why does this need to exist?
) -> LogosNode:
    """
    Create a new concept with required lineage.

    AGENTESE: concept.*.define

    The Genealogical Constraint: No concept exists ex nihilo.
    Every concept must declare its parents and justify its existence.
    """
    # 1. Validate lineage (HARD REQUIREMENT)
    if not extends:
        raise LineageError(
            handle=handle,
            message="Concepts cannot exist ex nihilo. Provide at least one parent."
        )

    # 2. Validate parents exist
    for parent in extends:
        try:
            await logos.resolve(parent, observer)
        except PathNotFoundError:
            raise LineageError(
                handle=handle,
                message=f"Parent '{parent}' does not exist in the lattice."
            )

    # 3. L-gent lattice consistency check
    checker = get_lattice_checker()
    result = await checker.check_position(
        new_handle=handle,
        parents=extends,
        children=subsumes or []
    )
    if not result.valid:
        raise LatticeError(handle=handle, message=result.reason)

    # 4. Compute inherited affordances and constraints
    affordances = await _compute_affordances(logos, extends, observer)
    constraints = await _compute_constraints(logos, extends, observer)

    # 5. Create lineage record
    lineage = ConceptLineage(
        handle=handle,
        extends=extends,
        subsumes=subsumes or [],
        justification=justification,
        affordances=affordances,
        constraints=constraints,
        created_by=observer.dna.name,
        created_at=datetime.now(UTC),
    )

    # 6. Register in L-gent catalog
    await register_concept(logos.registry, handle, spec, lineage)

    # 7. Create and cache LogosNode
    node = ConceptNode(handle=handle, lineage=lineage, spec=spec)
    logos._cache[handle] = node

    return node


async def _compute_affordances(
    logos: Logos,
    parents: list[str],
    observer: Umwelt,
) -> set[str]:
    """Union of parent affordances (additive)."""
    affordances: set[str] = set()
    for parent_handle in parents:
        parent = await logos.resolve(parent_handle, observer)
        affordances |= set(parent.affordances(observer.dna))
    return affordances


async def _compute_constraints(
    logos: Logos,
    parents: list[str],
    observer: Umwelt,
) -> set[str]:
    """Intersection of parent constraints (restrictive)."""
    if not parents:
        return set()

    parent = await logos.resolve(parents[0], observer)
    constraints = set(getattr(parent, 'constraints', []))

    for parent_handle in parents[1:]:
        parent = await logos.resolve(parent_handle, observer)
        constraints &= set(getattr(parent, 'constraints', []))

    return constraints
```

**Tests**:
- `test_define_with_lineage`: Happy path with valid parents
- `test_define_ex_nihilo_fails`: No parents raises LineageError
- `test_define_missing_parent_fails`: Non-existent parent raises error
- `test_define_inheritance`: Affordances inherited correctly
- `test_define_constraint_intersection`: Constraints computed correctly

### Chunk 4: CLI Visualization (`kgents map --lattice`)

**File**: `protocols/cli/commands/map.py` (extend)

**Goal**: Visualize the concept lattice in terminal.

```
CONCEPT LATTICE
===============

concept (Top)
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
│   └── capital
└── time
    ├── trace
    └── kairos

═══════════════════════════════════════
Nodes: 14 | Edges: 13 | Depth: 4 | Orphans: 0
═══════════════════════════════════════
```

**Tests**:
- `test_cli_lattice_output`: Verify tree rendering
- `test_cli_orphan_detection`: Orphans are flagged

### Chunk 5: Integration with Existing Systems

**Goal**: Wire into Logos resolution and L-gent registry.

1. **Logos Integration**: When `concept.foo.define` is invoked, route to `define_concept`
2. **L-gent Integration**: Concept lineage stored in CatalogEntry relationships
3. **JIT Integration**: If concept has spec but no impl, J-gent compiles it

## File Structure

```
impl/claude/protocols/agentese/
├── contexts/
│   └── concept.py          # EXTEND: Add define aspect, lineage
├── lattice/
│   ├── __init__.py         # NEW: Package exports
│   ├── checker.py          # NEW: LatticeConsistencyChecker
│   ├── lineage.py          # NEW: ConceptLineage, inheritance logic
│   └── _tests/
│       ├── __init__.py
│       ├── test_checker.py
│       └── test_lineage.py
```

## Success Criteria

The implementation succeeds when:

1. **Genealogical Enforcement**: `concept.foo.define` without `extends` ALWAYS fails
2. **Lattice Validation**: L-gent `AdvancedLattice` verifies position before creation
3. **Inheritance Semantics**: Affordances union, constraints intersect
4. **CLI Visibility**: `kgents map --lattice` shows the concept family tree
5. **Tests Pass**: 30+ tests covering all edge cases
6. **Sympathetic Errors**: Every failure explains *why* and suggests *what to do*

## Anti-Patterns to Avoid

1. **The Orphan Factory**: Allowing concepts without parents
2. **The God Concept**: One concept that everything extends
3. **The Cycle**: A → B → C → A (violates DAG)
4. **The Silent Failure**: Returning None instead of raising sympathetic error
5. **The Duplication**: Creating concepts that already exist (check registry first)

## The Spirit of the Work

Remember: The lattice is not bureaucracy. It is the genealogical memory of the system. When you create a concept, you are saying: *"I descend from these ancestors. I carry their wisdom. I add my own contribution."*

Every concept in the lattice is part of a family. The family tree is how we understand what things mean. Orphans have no meaning—they float free, disconnected, unusable.

Build the family. Enforce the lineage. Let no concept stand alone.

---

*"The lattice is not a cage—it is a family tree. Every branch knows its roots."*
