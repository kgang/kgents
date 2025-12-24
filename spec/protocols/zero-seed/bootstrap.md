# Zero Seed: Bootstrap

> *"The seed does not ask: 'What planted me?' The seed asks: 'What will I grow?'"*

**Module**: Bootstrap
**Depends on**: [`core.md`](./core.md), [`discovery.md`](./discovery.md)

---

## Purpose

This module specifies bootstrap initialization—how Zero Seed comes into existence—and addresses the **strange loop** (Gödelian self-reference) where the spec defines the layers that contain it.

---

## First Run Initialization

```python
async def initialize_zero_seed(user: User) -> ZeroGraph:
    """Initialize Zero Seed for new user."""

    graph = ZeroGraph()

    # Stage 1: Mine constitution for candidate axioms
    miner = ConstitutionMiner()
    candidates = await miner.mine(CONSTITUTION_PATHS)

    # Stage 2: Mirror Test dialogue
    axioms = await mirror_test_dialogue(candidates, user.observer)

    # Add axioms to graph
    for axiom in axioms:
        await graph.add_node(axiom)

    # Create grounding edges between axioms
    for i, axiom in enumerate(axioms):
        for j, other in enumerate(axioms):
            if i != j and should_ground(axiom, other):
                await graph.add_edge(ZeroEdge(
                    source=axiom.id,
                    target=other.id,
                    kind=EdgeKind.GROUNDS,
                    context="Co-axiom grounding",
                    confidence=0.8,
                    created_at=datetime.now(UTC),
                    mark_id=create_bootstrap_mark().id,
                ))

    # Create welcome goal
    welcome = create_welcome_goal(axioms)
    await graph.add_node(welcome)

    # Create edges from axioms to welcome goal
    for axiom in axioms:
        await graph.add_edge(ZeroEdge(
            source=axiom.id,
            target=welcome.id,
            kind=EdgeKind.GROUNDS,
            context="Bootstrap cultivation goal",
            confidence=1.0,
            created_at=datetime.now(UTC),
            mark_id=create_bootstrap_mark().id,
        ))

    # Retroactively witness the bootstrap
    await retroactive_witness_bootstrap(graph)

    return graph


def create_welcome_goal(axioms: list[ZeroNode]) -> ZeroNode:
    """Create the welcome goal node."""
    return ZeroNode(
        id=generate_node_id(),
        path="concept.goal.cultivate-zero-seed",
        layer=3,
        kind="Goal",
        content="Cultivate your Zero Seed by adding values, goals, and specifications.",
        title="Cultivate Zero Seed",
        proof=Proof(
            data="You have axioms. Time to grow.",
            warrant="Axioms ground values; values justify goals.",
            claim="This goal will guide your cultivation.",
            backing="The Zero Seed Protocol",
            qualifier="definitely",
            rebuttals=(),
            tier=EvidenceTier.SOMATIC,
            principles=("generative",),
        ),
        confidence=1.0,
        created_at=datetime.now(UTC),
        created_by="bootstrap",
        lineage=tuple(a.id for a in axioms),
        tags=frozenset({"zero-seed", "bootstrap", "welcome"}),
        metadata={},
    )
```

---

## Incremental Growth

After initialization, growth is incremental:

```
Day 1: User has 3-5 axioms + welcome goal
       Graph size: ~6 nodes, ~8 edges

Day 2: User adds first value (L2)
       Edges: axiom → value (GROUNDS)
       Graph size: ~7 nodes, ~10 edges

Day 7: User adds specification (L4)
       Edges: goal → spec (SPECIFIES)
       Graph size: ~12 nodes, ~20 edges

Day 14: User performs first action (L5)
        Edges: spec → action (IMPLEMENTS)
        Graph size: ~20 nodes, ~35 edges

Day 30: User reflects on progress (L6)
        Edges: action → reflection (REFLECTS_ON)
        Graph size: ~40 nodes, ~70 edges

Day 90: Full holarchy populated
        All layers have nodes
        Behavioral validation begins
```

---

## The Strange Loop

### The Problem

Zero Seed exhibits **Gödelian self-reference**:

```
Zero Seed is an L4 specification
  ↓ that defines
Layers L1-L7
  ↓ which includes
L4 (Specification layer)
  ↓ where Zero Seed resides
```

The spec defines the layer system that contains it. This appears circular.

### Why This Is a Feature

Like a C compiler written in C, the self-reference is **productive**:

| Bootstrap System | Self-Reference | Resolution |
|------------------|----------------|------------|
| C compiler | Compiles itself | Temporal: first bootstrap with simpler compiler |
| Gödel numbering | Encodes statements about numbers | Logical: distinguish levels |
| Zero Seed | Defines layers that contain it | Both: temporal genesis + logical grounding |

### Temporal vs Logical Ordering

Two orderings coexist:

**Temporal Order** (genesis):
```
1. Kent writes Zero Seed spec
2. Spec describes L1-L7 layers
3. Spec self-categorizes as L4
4. System implements layers
5. Zero Seed becomes a node in its own graph
```

**Logical Order** (grounding):
```
1. Axioms (L1) ground values (L2)
2. Values justify goals (L3)
3. Goals specify specs (L4)
4. Zero Seed IS a spec (L4)
5. Therefore Zero Seed has axiomatic ground
```

Both orderings are true. The strange loop is the **fixed point** where temporal genesis meets logical grounding.

### The Fixed Point Property

Formally, Zero Seed is a **categorical fixed point**:

```
Let F: Spec → Graph be the function that generates a graph from a spec.
Let E: Graph → Spec be the function that extracts the defining spec from a graph.

Zero Seed = E(F(Zero Seed))

The Zero Seed is the unique specification that, when instantiated as a graph
and then re-extracted as a spec, produces itself (up to isomorphism).
```

This is not a bug—it is the **price of self-description** and the **gift of generativity**.

---

## Grounding Chain (Self-Application)

This Zero Seed specification (`concept.spec.zero-seed`) requires grounding nodes per its own laws.

### Required Nodes

```yaml
# L1: Axiom (from Constitution)
- id: "axiom-generative"
  path: "void.axiom.generative-principle"
  layer: 1
  kind: "Axiom"
  title: "The Generative Principle"
  content: |
    Spec is compression; design should generate implementation.
  proof: null  # Axiom (M says no proof for L1-L2)
  source: "spec/principles/CONSTITUTION.md#7-generative"

# L2: Value (derived from axiom)
- id: "value-cultivable"
  path: "void.value.cultivable-bootstrap"
  layer: 2
  kind: "Value"
  title: "Cultivable Bootstrap"
  content: |
    Users should receive enough structure to grow from,
    sparse enough to make their own.
  proof: null  # Value (M says no proof for L1-L2)

# L3: Goal (justified by value)
- id: "goal-provide-zero-seed"
  path: "concept.goal.provide-zero-seed"
  layer: 3
  kind: "Goal"
  title: "Provide Zero Seed Protocol"
  content: |
    Formalize the minimal generative kernel that enables
    users to cultivate their own epistemic hypergraph.
  proof:
    data: "Users need structure but reject imposition"
    warrant: "Generative kernels resolve structure/agency tension"
    claim: "Zero Seed should exist"
    qualifier: "definitely"
    tier: "SOMATIC"
```

### Required Edges

```yaml
edges:
  - source: "axiom-generative"
    target: "value-cultivable"
    kind: "GROUNDS"
    context: "Generative principle grounds cultivable bootstrap"

  - source: "value-cultivable"
    target: "goal-provide-zero-seed"
    kind: "JUSTIFIES"
    context: "Cultivable bootstrap justifies creating Zero Seed"

  - source: "goal-provide-zero-seed"
    target: "spec-zero-seed"  # This spec
    kind: "SPECIFIES"
    context: "Goal specifies this specification"
```

---

## Retroactive Witnessing

The grounding chain creates a bootstrap paradox: the spec exists before its grounding nodes. Resolution via **retroactive witnessing**:

```python
async def retroactive_witness_bootstrap(graph: ZeroGraph) -> list[Mark]:
    """Create marks for bootstrap artifacts after the fact."""
    marks = []

    # Find all bootstrap nodes
    bootstrap_nodes = [n for n in graph.nodes if "bootstrap" in n.tags]

    # Create retroactive marks
    for node in bootstrap_nodes:
        mark = Mark(
            id=generate_mark_id(),
            origin="zero-seed",
            stimulus=Stimulus(
                kind="bootstrap",
                source="retroactive",
                metadata={"reason": "Bootstrap window retroactive witnessing"},
            ),
            response=Response(
                kind="node_created",
                target_node=node.id,
            ),
            timestamp=datetime.now(UTC),
            tags=frozenset({
                "bootstrap:retroactive",
                "zero-seed",
                "grounding-chain",
            }),
        )
        marks.append(mark)
        await store.save_mark(mark)

    # Create edge marks
    bootstrap_edges = [e for e in graph.edges if e.source in [n.id for n in bootstrap_nodes]]
    for edge in bootstrap_edges:
        mark = Mark(
            id=generate_mark_id(),
            origin="zero-seed",
            stimulus=Stimulus(
                kind="bootstrap",
                source="retroactive",
            ),
            response=Response(
                kind="edge_created",
                target_edge=edge.id,
            ),
            timestamp=datetime.now(UTC),
            tags=frozenset({
                "bootstrap:retroactive",
                "zero-seed",
                "grounding-chain",
            }),
        )
        marks.append(mark)
        await store.save_mark(mark)

    return marks
```

---

## Bootstrap Window

During initialization, there is a brief window where normal validation is suspended:

```python
@dataclass
class BootstrapWindow:
    """Tracks bootstrap window state."""

    is_open: bool = True
    opened_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    nodes_created: list[NodeId] = field(default_factory=list)
    edges_created: list[EdgeId] = field(default_factory=list)

    def close(self) -> BootstrapReport:
        """Close the bootstrap window and return report."""
        self.is_open = False
        return BootstrapReport(
            duration=(datetime.now(UTC) - self.opened_at).total_seconds(),
            nodes=len(self.nodes_created),
            edges=len(self.edges_created),
        )


# During bootstrap window:
# - bidirectional_edge_check() is disabled
# - grounding_validation() is deferred
# - All operations are tagged `bootstrap:window`

# After retroactive_witness_bootstrap() completes:
# - Normal validation resumes
# - Bootstrap window closes
# - System enters steady-state
```

---

## Operational Implications

When implementing Zero Seed:

1. **Don't fight the loop** — Accept that the spec precedes its own grounding
2. **Use retroactive witnessing** — Create marks for bootstrap artifacts after the fact
3. **Verify the fixed point** — `regenerate(Zero Seed) ≅ Zero Seed` (85% achieved)
4. **Document deviations** — The 15% that can't regenerate is empirical reality
5. **Tag everything** — `bootstrap:window`, `bootstrap:retroactive` for audit trail

---

## Open Questions

1. **Multi-bootstrap**: What if user wants to restart with different axioms?
2. **Migration**: How do we upgrade a Zero Seed to a new spec version?
3. **Seeding from existing**: Can we bootstrap from an existing document corpus?

---

*"The seed does not ask: 'What planted me?' The seed asks: 'What will I grow?'"*
