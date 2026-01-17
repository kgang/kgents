# Genesis Experience Skill

> *"Genesis is self-description, not interrogation."*
>
> *"The garden knows itself. The system teaches itself. The user discovers alongside."*

**When to use**: Implementing or extending the first-run experience, understanding the Constitutional Graph flow, building onboarding that illuminates rather than interrogates.

**Spec**: `spec/protocols/genesis-clean-slate.md`
**Plans**: `plans/genesis-overhaul/`

---

## The Core Insight

Traditional onboarding: `User → Questions → Answers → Configure → Empty State`
Genesis: `Pre-Seeded Constitution → Exploration → Discovery → Extension`

| Traditional Onboarding | Genesis |
|------------------------|---------|
| "Tell me about yourself" | "Here's who WE are" |
| Configuration before creation | Discovery before declaration |
| Blank canvas paralysis | Living structure from the start |
| User as data source to be mined | User as explorer and extender |
| Gates before gardens | Gardens from the start |

---

## The Philosophy Shift

```
OLD: Genesis = Interview(user) >> Configure(preferences) >> Start(empty)

NEW: Genesis = Seed(Constitution) >> Manifest(K-Blocks) >> Illuminate(Derivations)
```

This is not cosmetic. This is a paradigm shift from **interrogation** to **illumination**.

### What Genesis Does NOT Do

The Illumination Principle forbids:
- Asking the user to answer questions
- Requiring configuration before proceeding
- Blocking progress until information is provided
- Judging the user's choices

### What Genesis DOES Do

- Shows what exists
- Explains why it exists
- Demonstrates how things connect
- Invites extension when ready

---

## The 6-Phase Exploration Flow

### Phase 1: Orient (0-30 seconds)

**Goal**: User understands they are looking at a foundation, not an empty canvas.

```
+-------------------------------------------------------------------+
|                                                                   |
|         Welcome to kgents                                         |
|                                                                   |
|         The system already knows itself.                          |
|         Your job is to explore---and then extend.                 |
|                                                                   |
+-------------------------------------------------------------------+

     L0: ZERO SEED          The irreducible axioms
     ==============

     o A1: Entity           "There exist things"
     o A2: Morphism         "Things relate"
     o A3: Mirror Test      "We judge by reflection"
     o G: Galois Ground     "Axioms are fixed points"

     Press [Space] to explore   [Tab] to navigate layers
```

**Implementation notes**:
- L0 axioms are the starting point
- Each axiom has a one-line summary
- Visual hierarchy shows: this is the foundation

### Phase 2: Traverse (30 seconds - 2 minutes)

**Goal**: User learns navigation by doing.

- User presses [Space] to expand A1: Entity
- K-Block reveals full content with derivations
- User sees edges leading to L1 (Compose, Ground)
- User presses [Tab] to move to L1

**Key pattern**: First action is **traverse**, not **answer**.

### Phase 3: Understand (2-5 minutes)

**Goal**: User grasps the derivation structure.

- User explores L1 (Minimal Kernel)
- Each primitive shows its derivation from L0
- User begins to see: "Oh, Compose comes from Morphism"

### Phase 4: Connect (5-10 minutes)

**Goal**: Pattern recognition kicks in.

- User explores L2 (Principles)
- Sees how TASTEFUL derives from Judge + Mirror
- Sees how COMPOSABLE derives from Compose + Id
- Insight: "Everything derives from those four axioms"

### Phase 5: Apply (10+ minutes)

**Goal**: User understands self-description.

- User sees L3 (Architecture)
- ASHC, Metaphysical Fullstack, Hypergraph Editor
- User understands: "This is how the system builds itself"

### Phase 6: Extend (when ready)

**Goal**: User creates their first declaration ON the foundation.

```python
await genesis.extend(
    declaration="Build software that feels alive",
    derivations=["genesis:L0:entity", "genesis:L0:mirror"],
)
# Creates a new L1 axiom grounded by the Mirror Test
```

**Key insight**: Extension is invitation, not gate. User declarations are L1 (grounded by Mirror Test only).

---

## Navigation Commands

Navigation follows the hypergraph editor paradigm:

| Command | Action | Edge Type |
|---------|--------|-----------|
| `gh` | Go to parent | Inverse `derives_from` |
| `gl` | Go to child | Forward `derives_from` |
| `gj` | Next sibling | Same parent |
| `gk` | Previous sibling | Same parent |
| `gd` | Go to definition | `implements` edge |
| `gp` | Go to parent spec | `derives_from` edge |

### Navigation Example

```
User at: genesis:L2:tasteful (TASTEFUL principle)

gh  → goes to genesis:L1:judge (Judge primitive)
gl  → lists nodes that derive from TASTEFUL
gj  → goes to genesis:L2:curated (next sibling principle)
gk  → goes to genesis:L2:joy (previous sibling principle)
gp  → same as gh for Constitutional nodes
```

---

## The 22 K-Blocks

### Layer 0: Zero Seed (4 Axioms)

| ID | Title | Purpose |
|----|-------|---------|
| `genesis:L0:entity` | A1: Entity | "There exist things" - objects in a category |
| `genesis:L0:morphism` | A2: Morphism | "Things relate" - arrows between objects |
| `genesis:L0:mirror` | A3: Mirror Test | "We judge by reflection" - Kent's somatic oracle |
| `genesis:L0:galois` | G: Galois Ground | "Axioms are fixed points" - termination guarantee |

**Key property**: L0 axioms have no `derivations_from`. They are GIVEN, not derived.

### Layer 1: Minimal Kernel (7 Primitives)

| ID | Title | Derivations From |
|----|-------|------------------|
| `genesis:L1:compose` | Compose | A2 (Morphism) |
| `genesis:L1:judge` | Judge | A3 (Mirror) |
| `genesis:L1:ground` | Ground | A1 (Entity) |
| `genesis:L1:id` | Identity | Compose + Judge |
| `genesis:L1:contradict` | Contradict | Judge |
| `genesis:L1:sublate` | Sublate | Compose + Judge + Contradict |
| `genesis:L1:fix` | Fix | Compose + Judge |

**Key property**: L1 primitives are near-fixed-points (Galois loss < 0.05).

### Layer 2: Principles (7 Design Principles)

| ID | Title | = Judge Applied To |
|----|-------|-------------------|
| `genesis:L2:tasteful` | TASTEFUL | aesthetics via Mirror |
| `genesis:L2:curated` | CURATED | selection via Ground |
| `genesis:L2:ethical` | ETHICAL | harm via Mirror |
| `genesis:L2:joy` | JOY_INDUCING | affect via Mirror |
| `genesis:L2:composable` | COMPOSABLE | category laws (Compose + Id) |
| `genesis:L2:heterarchical` | HETERARCHICAL | hierarchy (categorical theorem) |
| `genesis:L2:generative` | GENERATIVE | regenerability (Ground + Compose + Fix) |

### Layer 3: Architecture (4 Self-Descriptions)

| ID | Title | Purpose |
|----|-------|---------|
| `genesis:L3:ashc` | ASHC | How the compiler works |
| `genesis:L3:metaphysical` | Metaphysical Fullstack | How agents are structured |
| `genesis:L3:hypergraph` | Hypergraph Editor | How navigation works |
| `genesis:L3:crown-jewels` | Crown Jewels | What domain compositions exist |

---

## Data Model

```python
@dataclass(frozen=True)
class GenesisKBlock:
    """A K-Block in the Genesis Constitutional Graph."""

    id: str                                    # e.g., "genesis:L0:entity"
    path: str                                  # AGENTESE path
    layer: Literal[0, 1, 2, 3]                 # Genesis layer
    title: str
    content: str                               # Markdown
    proof: GaloisWitnessedProof | None         # None for L0
    confidence: float                          # 1 - galois_loss
    color: str                                 # LIVING_EARTH hex
    derivations_from: list[str]                # K-Block IDs
    derivations_to: list[str]                  # K-Block IDs
    tags: frozenset[str]


@dataclass
class ConstitutionalGraph:
    """The seeded graph of Genesis K-Blocks."""

    nodes: dict[str, GenesisKBlock]            # id -> K-Block
    edges: list[tuple[str, str, str]]          # (source, target, edge_type)

    def get_layer(self, layer: int) -> list[GenesisKBlock]: ...
    def get_derivations(self, node_id: str) -> list[GenesisKBlock]: ...
    def get_derived(self, node_id: str) -> list[GenesisKBlock]: ...
```

---

## AGENTESE Integration

Genesis operations are exposed via AGENTESE:

```python
@node("void.genesis", dependencies=("storage", "witness"))
class GenesisNode:
    """Genesis operations via AGENTESE."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> ConstitutionalGraph:
        """Get the Constitutional Graph."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def layer(self, observer: Observer, layer: int) -> list[GenesisKBlock]:
        """Get K-Blocks at a layer."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def extend(
        self,
        observer: Observer,
        declaration: str,
        derivations: list[str],
    ) -> GenesisKBlock:
        """Add user declaration to graph."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def derivation_path(
        self,
        observer: Observer,
        from_id: str,
        to_id: str,
    ) -> list[str]:
        """Find derivation path between two K-Blocks."""
        ...
```

**Usage**:
```
:void.genesis.manifest          # Get the full Constitutional Graph
:void.genesis.layer 0           # Get L0 axioms
:void.genesis.extend "..." [derivations]  # Add user declaration
```

---

## Derivation DAG Invariants

The Constitutional Graph must satisfy these laws:

```python
def verify_derivation_dag():
    # L1: Unique Root
    # Only L0 axioms have layer=0
    roots = [b for b in blocks if b.layer == 0]
    assert len(roots) == 4  # A1, A2, A3, G

    # L2: No Orphan Parents
    # Every derivation_from must reference an existing K-Block
    for block in blocks:
        for parent_id in block.derivations_from:
            assert parent_id in block_ids

    # L3: Layer Monotonicity
    # Parents must be at strictly lower layers
    for block in blocks:
        for parent_id in block.derivations_from:
            parent = get_block(parent_id)
            assert parent.layer < block.layer

    # L4: Acyclicity
    # No cycles in the derivation graph
    assert is_dag(derivation_graph)

    # L5: L0 Has No Parents
    # Axioms derive from nothing
    for block in l0_blocks:
        assert block.derivations_from == []

    # L6: L1+ Has Parents
    # Everything above L0 derives from something
    for block in blocks:
        if block.layer > 0:
            assert len(block.derivations_from) > 0
```

---

## Implementation Checklist

When implementing genesis features:

- [ ] Constitutional Graph is pre-seeded (22 K-Blocks present on fresh instance)
- [ ] User can traverse immediately (no blocking questions)
- [ ] Navigation uses `gh/gl/gj/gk/gd/gp` commands
- [ ] Each K-Block shows its derivations
- [ ] Extension creates K-Blocks that derive from existing ones
- [ ] Derivation DAG invariants are enforced
- [ ] Galois loss bounds are respected per layer

---

## Anti-patterns

| Don't | Instead |
|-------|---------|
| Ask "who are you?" on first run | Show "here's who WE are" |
| Require configuration before use | Allow immediate exploration |
| Start with empty canvas | Start with pre-seeded Constitution |
| Block progress on input | Invite extension when ready |
| Hide the derivation structure | Make derivations visible and navigable |

---

## Voice Anchors Preserved

| Anchor | How Genesis Honors It |
|--------|----------------------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Four axioms, not forty. Self-describing genesis, not interview. No badges, no gamification. |
| *"The Mirror Test"* | A3 explicitly embeds the Mirror Test as irreducible axiom. Kent's somatic response grounds all judgment. |
| *"Tasteful > feature-complete"* | 22 K-Blocks---minimal but complete. Each earns its place through derivation. |
| *"The persona is a garden, not a museum"* | The Constitutional Graph is living, not static. User can extend. The garden grows. |
| *"Depth over breadth"* | Deep category theory grounding. Galois loss as computable trust. Not feature sprawl. |

---

## Connection to Other Skills

| Skill | Connection |
|-------|------------|
| `hypergraph-editor.md` | Navigation commands (gh/gl/gj/gk) |
| `agentese-node-registration.md` | GenesisNode registration |
| `zero-seed-for-agents.md` | L0 axioms and Galois grounding |
| `derivation-edges.md` | Edge types and DAG structure |
| `elastic-ui-patterns.md` | Layer visualization |

---

*Skill created: 2026-01-17*
*Lines: ~350*
*Source: plans/genesis-overhaul/99-summary-walkthrough.md*
