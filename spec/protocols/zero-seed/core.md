# Zero Seed: Core

> *"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

**Filed**: 2025-12-24
**Status**: Genesis v2 — Radical Axiom Reduction
**Principles**: Generative, Composable, Tasteful

---

## The Minimal Kernel: Two Axioms + One Meta-Principle

Zero Seed achieves maximum generativity through **radical compression**. The entire seven-layer epistemic holarchy derives from just two axioms and one meta-principle.

### A1: Entity (Everything is a Node)

```
∀x ∈ Universe: ∃ node(x) ∈ ZeroGraph
```

Every concept, belief, value, goal, specification, action, reflection, and representation is a node. There is no privileged "configuration" vs "content" distinction. The graph is universal.

**Corollaries**:
- The Zero Seed spec itself is a node (`concept.spec.zero-seed`)
- The user's values are nodes (`void.value.*`)
- The user's actions are nodes (`world.action.*`)
- This axiom statement is a node (`void.axiom.entity`)

### A2: Morphism (Everything Composes)

```
∀ node_a, node_b: ∃ potential edge(a, b) ∈ Hom(ZeroGraph)
```

Any two nodes can be connected. Edges are morphisms in a category. Composition is primary.

**Corollaries**:
- Identity morphisms exist: `id: node → node`
- Composition is associative: `(f >> g) >> h = f >> (g >> h)`
- The graph is navigable in any direction (bidirectionality from inverses)

### M: Justification (The Meta-Principle)

```
∀ node n where n.layer > 2: ∃ proof(n) ∈ ToulminStructure
```

**Every node justifies its existence—or admits it cannot.**

This single meta-principle generates:
1. **The Seven Layers**: Nodes that cannot justify (axioms, values) form L1-L2. Nodes that must justify form L3-L7.
2. **Full Witnessing**: Justification requires traces. Every modification creates a Mark.
3. **Proof Structure**: Toulmin proofs (data, warrant, claim, backing, qualifier, rebuttals) are the universal justification form.
4. **Contradiction Tolerance**: Two nodes may both "justify" incompatibly—dialectical invitation, not error.

---

## The Seven Layers (Derived from M)

The meta-principle M partitions nodes by justification depth:

| Layer | Name | Justification | Edge Type (Primary) |
|-------|------|---------------|---------------------|
| **L1** | Assumptions | **NONE** — taken on faith, somatic sense | `grounds` |
| **L2** | Values | **NONE** — principles, affinities | `justifies` |
| **L3** | Goals | Justified by values | `specifies` |
| **L4** | Specifications | Justified by goals | `implements` |
| **L5** | Execution | Justified by specs | `reflects_on` |
| **L6** | Reflection | Justified by actions | `represents` |
| **L7** | Representation | Justified by reflections | (terminal) |

### The Derivation

From M, we observe:
- Some nodes CANNOT justify (irreducible ground) → L1, L2
- Some nodes MUST justify → L3-L7
- Justification forms chains → layer ordering
- Deeper justification = higher layer number

```python
def layer_of(node: ZeroNode) -> int:
    """Layer is determined by justification depth."""
    if node.proof is None:
        # Cannot justify → axiom layer
        if node.kind in AXIOM_KINDS:
            return 1  # Assumptions
        else:
            return 2  # Values
    else:
        # Must justify → compute from proof chain
        return 2 + proof_depth(node.proof)
```

---

## Data Model

### ZeroNode

```python
@dataclass(frozen=True)
class ZeroNode:
    """A node in the Zero Seed holarchy. Derived from A1 (Entity)."""

    # Identity (from A1)
    id: NodeId                          # Unique identifier
    path: str                           # AGENTESE path (e.g., "void.axiom.mirror-test")

    # Classification (derived from M)
    layer: Annotated[int, Field(ge=1, le=7)]  # Layer constraint
    kind: str                           # Node type within layer

    # Content
    content: str                        # Markdown content
    title: str                          # Display name

    # Justification (from M)
    proof: Proof | None                 # Toulmin structure (None for L1-L2)
    confidence: float                   # [0, 1] subjective confidence

    # Provenance
    created_at: datetime
    created_by: str
    lineage: tuple[NodeId, ...]         # Derivation chain

    # Metadata
    tags: frozenset[str]
    metadata: dict[str, Any]

    def requires_proof(self) -> bool:
        """L1-L2 nodes are unproven; L3+ require proof."""
        return self.layer > 2
```

### ZeroEdge

```python
@dataclass(frozen=True)
class ZeroEdge:
    """A morphism between Zero Seed nodes. Derived from A2 (Morphism)."""

    # Identity
    id: EdgeId
    source: NodeId
    target: NodeId

    # Classification
    kind: EdgeKind                      # See taxonomy below

    # Metadata
    context: str                        # Why this edge exists
    confidence: float                   # [0, 1] strength
    created_at: datetime
    mark_id: MarkId                     # Witness mark (REQUIRED by M)

    # For contradiction edges
    is_resolved: bool = False
    resolution_id: NodeId | None = None

    # Composition operator (from A2)
    def __rshift__(self, other: "ZeroEdge") -> "ZeroEdge":
        """
        Compose edges: (A→B) >> (B→C) = (A→C)

        Laws (VERIFIED):
        - Identity: id >> f = f = f >> id
        - Associativity: (f >> g) >> h = f >> (g >> h)
        """
        if self.target != other.source:
            raise CompositionError(f"Cannot compose: {self.target} != {other.source}")

        return ZeroEdge(
            id=generate_edge_id(),
            source=self.source,
            target=other.target,
            kind=compose_edge_kinds(self.kind, other.kind),
            context=f"Composed: {self.context} >> {other.context}",
            confidence=self.confidence * other.confidence,
            created_at=datetime.now(UTC),
            mark_id=create_composition_mark(self, other).id,
        )
```

### Edge Kind Taxonomy

```python
class EdgeKind(Enum):
    # Inter-layer (DAG flow from M's layer ordering)
    GROUNDS = "grounds"                 # L1 → L2
    JUSTIFIES = "justifies"             # L2 → L3
    SPECIFIES = "specifies"             # L3 → L4
    IMPLEMENTS = "implements"           # L4 → L5
    REFLECTS_ON = "reflects_on"         # L5 → L6
    REPRESENTS = "represents"           # L6 → L7

    # Intra-layer (from A2's universality)
    DERIVES_FROM = "derives_from"
    EXTENDS = "extends"
    REFINES = "refines"

    # Dialectical (from M's contradiction tolerance)
    CONTRADICTS = "contradicts"         # Paraconsistent conflict
    SYNTHESIZES = "synthesizes"         # Resolution
    SUPERSEDES = "supersedes"           # Version replacement

    # Crystallization (from witnessing)
    CRYSTALLIZES = "crystallizes"
    SOURCES = "sources"

# Bidirectional inverses (from A2)
EDGE_INVERSES: dict[EdgeKind, EdgeKind] = {
    EdgeKind.GROUNDS: EdgeKind.GROUNDED_BY,
    EdgeKind.JUSTIFIES: EdgeKind.JUSTIFIED_BY,
    # ... (auto-computed for all)
    EdgeKind.CONTRADICTS: EdgeKind.CONTRADICTS,  # Symmetric
}
```

### Proof Structure (from M)

```python
@dataclass(frozen=True)
class Proof:
    """Toulmin proof structure. Required for L3+ nodes by M."""

    data: str                           # Evidence
    warrant: str                        # Reasoning
    claim: str                          # Conclusion
    backing: str                        # Support for warrant
    qualifier: str                      # Confidence ("definitely", "probably")
    rebuttals: tuple[str, ...]          # Defeaters
    tier: EvidenceTier                  # CATEGORICAL, EMPIRICAL, AESTHETIC, SOMATIC
    principles: tuple[str, ...]         # Referenced Constitution principles
```

---

## Laws

From the two axioms and meta-principle, eight laws follow:

| Law | Statement | Source | Enforcement |
|-----|-----------|--------|-------------|
| **Node Identity** | Each node has exactly one path | A1 | Path uniqueness constraint |
| **Layer Integrity** | Node.layer ∈ {1,2,3,4,5,6,7} | M | Type constraint |
| **Composition** | (f >> g) >> h = f >> (g >> h) | A2 | Verified in `__rshift__` |
| **Bidirectional Edges** | ∀ edge e, ∃ inverse(e) | A2 | Auto-computed on creation |
| **Full Witnessing** | ∀ modification m, ∃ mark(m) | M | Enforced in modify_node() |
| **Axiom Unprovenness** | L1-L2 nodes have proof=None | M | Rejected if proof provided |
| **Proof Requirement** | L3+ nodes must have proof | M | Rejected if proof missing |
| **Contradiction Tolerance** | `contradicts` edges may coexist | M | No automatic resolution |

---

## AGENTESE Mapping

The Seven Layers map to Five AGENTESE Contexts via surjection:

| AGENTESE Context | Layers | Semantic |
|------------------|--------|----------|
| `void.*` | L1 + L2 | The Accursed Share — irreducible ground |
| `concept.*` | L3 + L4 | The Abstract — dreams and specifications |
| `world.*` | L5 | The External — actions in the world |
| `self.*` | L6 | The Internal — reflection, synthesis |
| `time.*` | L7 | The Temporal — representation across time |

```python
def layer_to_context(layer: int) -> str:
    """Surjective mapping from layer to AGENTESE context."""
    match layer:
        case 1 | 2: return "void"
        case 3 | 4: return "concept"
        case 5: return "world"
        case 6: return "self"
        case 7: return "time"
```

---

## Anti-Patterns

| Anti-pattern | Description | Resolution |
|--------------|-------------|------------|
| **Proof on Axiom** | Adding proof to L1-L2 node | Error: axioms are taken on faith |
| **Missing Proof** | L3+ node without Toulmin structure | Error: all non-axioms must justify |
| **Silent Edit** | Modifying node without witness mark | Impossible (enforced by M) |
| **Orphan Axiom** | Axiom with no `grounds` edges to L2 | Warning (may be pending) |
| **Layer Skip** | Edge skipping layers (L1 → L4) | Allowed but flagged for review |

---

## This Spec's Own Grounding

As an L4 node, this specification requires grounding per its own laws.

### Grounding Chain

```
A1 (Entity) + A2 (Morphism)
    ↓ generates
M (Justification)
    ↓ derives
void.axiom.generative-principle (L1)
    ↓ grounds
void.value.cultivable-bootstrap (L2)
    ↓ justifies
concept.goal.provide-zero-seed (L3)
    ↓ specifies
concept.spec.zero-seed (L4) ← THIS SPEC
```

### Toulmin Proof

```yaml
proof:
  data: |
    - 3 years kgents development
    - ~52K lines across 20+ systems
    - Four independent self-validation analyses
    - 85% regenerable from 2 axioms + 1 meta-principle

  warrant: |
    Radical axiom reduction achieves maximum generativity.
    2 Axioms + 1 Meta-Principle derives the full seven-layer system.
    Justification-as-meta-principle grounds both layers AND witnessing.

  claim: |
    The Zero Seed Protocol provides a minimal generative kernel —
    enough structure to grow from, sparse enough to make your own.

  qualifier: probably

  rebuttals:
    - "Unless 7-layer taxonomy proves too complex"
    - "Unless radical compression makes the system harder to understand"
    - "Unless justification-as-meta-principle is too abstract for users"

  tier: CATEGORICAL
  principles: [generative, composable, tasteful]
```

---

## Open Questions

These remain for dialectical refinement:

1. **Is justification-as-meta too abstract?** We may need to provide more concrete examples of how M generates the layers.

2. **Should we formalize the composition of edge kinds?** `compose_edge_kinds(GROUNDS, JUSTIFIES) = ?`

3. **How do we handle multi-hop derivations?** If A grounds B and B justifies C, what's the direct A→C relationship?

4. **Layer skip semantics**: When is L1→L4 valid? When is it a smell?

---

## Module Index

This is the core module of Zero Seed. Related modules:

| Module | Purpose |
|--------|---------|
| [`navigation.md`](./navigation.md) | Telescope UI, focal model, keybindings |
| [`discovery.md`](./discovery.md) | Three-stage axiom discovery |
| [`proof.md`](./proof.md) | Witnessing system, batch strategies |
| [`integration.md`](./integration.md) | Void services, edge creation, AGENTESE |
| [`bootstrap.md`](./bootstrap.md) | Initialization, strange loop, retroactive witnessing |
| [`dp.md`](./dp.md) | DP-Native integration, value functions |
| [`llm.md`](./llm.md) | LLM-augmented intelligence |

---

*"Two axioms. One meta-principle. Seven layers. Infinite gardens."*
