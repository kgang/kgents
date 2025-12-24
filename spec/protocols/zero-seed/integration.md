# Zero Seed: Integration

> *"The void is not empty. It is the ground from which all grows."*

**Module**: Integration
**Depends on**: [`core.md`](./core.md)

---

## Purpose

This module specifies how Zero Seed integrates with the broader kgents ecosystem: AGENTESE paths, K-Block editing, Void services, and edge creation modes.

---

## Void/Accursed Share Integration

### Void Polymorphism (Sum Type)

The `void.*` context is intentionally polymorphic—a **sum type**:

```
void.* = Nodes ⊕ Services

where:
  Nodes    = void.axiom.* (L1) | void.value.* (L2)
  Services = void.entropy.* | void.random.* | void.gratitude.*
```

| Path Pattern | Type | Semantics |
|--------------|------|-----------|
| `void.axiom.*` | Node (L1) | Graph node representing an axiom |
| `void.value.*` | Node (L2) | Graph node representing a value |
| `void.entropy.*` | Service | Entropy pool operations |
| `void.random.*` | Service | Random oracle operations |
| `void.gratitude.*` | Service | Gratitude ledger operations |

**Why polymorphic?** The Accursed Share (Bataille) contains both *structure* (what we believe) and *operations* (how we interact with the irreducible). Axioms and values ARE the Accursed Share; entropy, randomness, and gratitude are its *interfaces*.

### Entropy Pool

```python
@dataclass
class EntropyPool:
    """Fixed budget of entropy that regenerates over time."""

    initial_budget: float = 100.0
    remaining: float = 100.0
    regeneration_rate: float = 0.1     # Per minute
    last_regeneration: datetime = field(default_factory=lambda: datetime.now(UTC))

    def sip(self, amount: float) -> EntropyDraw:
        """Draw entropy from pool (costs budget)."""
        self._regenerate()
        if amount > self.remaining:
            raise EntropyExhaustedError(f"Requested {amount}, only {self.remaining} available")
        self.remaining -= amount
        return EntropyDraw(amount=amount, seed=generate_seed())

    def pour(self, amount: float, recovery_rate: float = 0.5) -> None:
        """Return unused entropy (partial recovery)."""
        self.remaining = min(self.initial_budget, self.remaining + amount * recovery_rate)

    def _regenerate(self) -> None:
        """Regenerate entropy based on time elapsed."""
        now = datetime.now(UTC)
        elapsed_minutes = (now - self.last_regeneration).total_seconds() / 60
        regenerated = elapsed_minutes * self.regeneration_rate
        self.remaining = min(self.initial_budget, self.remaining + regenerated)
        self.last_regeneration = now
```

### Random Oracle

```python
class RandomOracle:
    """Pure randomness, no budget constraints."""

    def sample_uniform(self) -> float:
        """Uniform [0, 1)."""
        return random.random()

    def sample_choice(self, options: list[T]) -> T:
        """Random choice from options."""
        return random.choice(options)

    def sample_shuffle(self, items: list[T]) -> list[T]:
        """Random permutation."""
        return random.sample(items, len(items))

    def sample_weighted(self, options: list[T], weights: list[float]) -> T:
        """Weighted random choice."""
        return random.choices(options, weights=weights, k=1)[0]
```

### Gratitude Ledger

```python
@dataclass
class GratitudeLedger:
    """Track what you've received and expressed gratitude for."""

    received: list[GratitudeEntry] = field(default_factory=list)
    expressed: list[GratitudeEntry] = field(default_factory=list)

    @property
    def balance(self) -> float:
        """Gratitude balance: expressed - received."""
        return sum(e.amount for e in self.expressed) - sum(e.amount for e in self.received)

    def receive(self, source: str, amount: float, description: str) -> None:
        """Record something received from outside (slop)."""
        self.received.append(GratitudeEntry(
            source=source,
            amount=amount,
            description=description,
            timestamp=datetime.now(UTC),
        ))

    def express(self, target: str, amount: float, description: str) -> None:
        """Express gratitude (returns to the Accursed Share)."""
        self.expressed.append(GratitudeEntry(
            source=target,
            amount=amount,
            description=description,
            timestamp=datetime.now(UTC),
        ))

    def suggest_gratitude(self) -> list[GratitudeSuggestion]:
        """Suggest who to express gratitude toward."""
        # Find received entries without corresponding expression
        unexpressed = []
        for r in self.received:
            if not any(e.source == r.source for e in self.expressed):
                unexpressed.append(r)
        return [GratitudeSuggestion(entry=e) for e in unexpressed]
```

---

## Edge Creation (Dual Mode)

### Modal EDGE Mode

Deliberate, explicit edge creation via modal interface:

```
EDGE MODE (e from NORMAL):
  1. Select edge type:
     g → GROUNDS          j → JUSTIFIES
     s → SPECIFIES        i → IMPLEMENTS
     r → REFLECTS_ON      p → REPRESENTS
     d → DERIVES_FROM     c → CONTRADICTS
     y → SYNTHESIZES      x → SUPERSEDES

  2. Navigate to target node (gh/gl/gj/gk)

  3. Confirm (Enter) or cancel (Esc)

  4. System creates:
     - ZeroEdge with mark_id (witnessed)
     - Inverse edge (auto-computed)
```

### Inline Annotation

Fluid edge creation in prose via wiki-style links:

```markdown
This goal [[specifies:concept.spec.witness-protocol]] directly.
We [[contradicts:void.axiom.simplicity]] by adding complexity.
The design [[derives_from:void.value.composability]].
```

Parser extracts edges on save:

```python
EDGE_PATTERN = re.compile(r'\[\[(\w+):([^\]]+)\]\]')

def extract_inline_edges(content: str, source_node: ZeroNode) -> list[ZeroEdge]:
    """Extract edges from inline annotations."""
    edges = []
    for match in EDGE_PATTERN.finditer(content):
        kind = EdgeKind(match.group(1))
        target_path = match.group(2)
        target_node = resolve_path(target_path)

        if target_node:
            edges.append(ZeroEdge(
                id=generate_edge_id(),
                source=source_node.id,
                target=target_node.id,
                kind=kind,
                context=f"Inline annotation in {source_node.path}",
                confidence=1.0,
                created_at=datetime.now(UTC),
                mark_id=None,  # Will be set on save
            ))

    return edges
```

### Edge Deduplication

Both modes merge to single edge set:

```python
def merge_edges(modal: list[ZeroEdge], inline: list[ZeroEdge]) -> list[ZeroEdge]:
    """Deduplicate edges. Inline wins on conflict (more recent context)."""
    seen = {}

    for e in modal:
        key = (e.source, e.target, e.kind)
        seen[key] = e

    for e in inline:
        key = (e.source, e.target, e.kind)
        seen[key] = e  # Overwrite with inline

    return list(seen.values())
```

---

## AGENTESE Integration

### Node Registration

Zero Seed nodes are AGENTESE nodes:

```python
@node("void.axiom", description="Axiom nodes (L1)")
class AxiomNode(BaseLogosNode):
    """AGENTESE node for L1 axioms."""

    async def invoke(self, request: LogosRequest) -> LogosResponse:
        # Axiom-specific behavior
        ...


@node("void.value", description="Value nodes (L2)")
class ValueNode(BaseLogosNode):
    """AGENTESE node for L2 values."""
    ...


@node("concept.goal", description="Goal nodes (L3)")
class GoalNode(BaseLogosNode):
    """AGENTESE node for L3 goals."""
    ...


@node("concept.spec", description="Specification nodes (L4)")
class SpecNode(BaseLogosNode):
    """AGENTESE node for L4 specifications."""
    ...


@node("world.action", description="Execution nodes (L5)")
class ActionNode(BaseLogosNode):
    """AGENTESE node for L5 actions."""
    ...


@node("self.reflection", description="Reflection nodes (L6)")
class ReflectionNode(BaseLogosNode):
    """AGENTESE node for L6 reflections."""
    ...


@node("time.insight", description="Representation nodes (L7)")
class InsightNode(BaseLogosNode):
    """AGENTESE node for L7 representations."""
    ...
```

### Path Resolution

```python
async def resolve_zero_seed_path(path: str) -> ZeroNode | None:
    """Resolve AGENTESE path to Zero Seed node."""
    # Parse path components
    parts = path.split(".")
    if len(parts) < 2:
        return None

    context = parts[0]
    kind = parts[1]
    node_id = parts[2] if len(parts) > 2 else None

    # Map to layer
    layer = context_to_layer(context)
    if layer is None:
        return None

    # Query graph
    if node_id:
        return await graph.get_node_by_path(path)
    else:
        # Return first node of kind in layer
        return await graph.get_first_node(layer=layer, kind=kind)
```

---

## K-Block Integration

All Zero Seed nodes can be edited via K-Block:

```python
async def edit_in_kblock(node: ZeroNode) -> KBlock:
    """Open node in K-Block editor."""
    kblock = await kblock_service.create(
        path=node.path,
        content=node.content,
        metadata={
            "layer": node.layer,
            "kind": node.kind,
            "proof": node.proof.to_dict() if node.proof else None,
        },
    )

    # K-Block provides:
    # - Checkpoint/rewind
    # - Multi-view (prose, graph, diff)
    # - Entanglement with related nodes
    # - Auto-save with witnessing

    return kblock
```

### K-Block Entanglement

When editing a node, related nodes become entangled:

```python
async def compute_entanglement(node: ZeroNode, graph: ZeroGraph) -> list[ZeroNode]:
    """Compute nodes entangled with current node."""
    entangled = []

    # Direct edges
    for edge in graph.edges_from(node.id):
        entangled.append(graph.get_node(edge.target))
    for edge in graph.edges_to(node.id):
        entangled.append(graph.get_node(edge.source))

    # Same-layer siblings
    siblings = await graph.get_nodes(layer=node.layer)
    for sib in siblings[:5]:  # Limit to 5
        if sib.id != node.id:
            entangled.append(sib)

    return entangled
```

---

## Hypergraph Editor Integration

Zero Seed graph renders in existing Hypergraph Editor:

```python
async def render_zero_seed_in_hypergraph(
    graph: ZeroGraph,
    telescope: TelescopeState,
) -> HypergraphView:
    """Render Zero Seed graph in hypergraph editor."""
    # Get visible nodes
    visible_nodes = [n for n in graph.nodes if n.layer in telescope.visible_layers]

    # Project to viewport
    projections = project_to_viewport(visible_nodes, telescope, viewport)

    # Build hypergraph view
    nodes = [
        HypergraphNode(
            id=p.node.id,
            position=p.position,
            label=p.node.title,
            color=LAYER_COLORS[p.node.layer],
            shape=LAYER_SHAPES[p.node.layer],
            opacity=p.opacity,
            scale=p.scale,
        )
        for p in projections
    ]

    edges = [
        HypergraphEdge(
            id=e.id,
            source=e.source,
            target=e.target,
            label=e.kind.value,
            style=edge_style_for_kind(e.kind),
        )
        for e in graph.edges
        if e.source in [n.id for n in visible_nodes]
        and e.target in [n.id for n in visible_nodes]
    ]

    return HypergraphView(nodes=nodes, edges=edges)
```

---

## Witness Integration

Zero Seed IS witness-native:

```python
# Every node modification creates a mark
# Origin is always "zero-seed"
# Tags include layer and kind

ZERO_SEED_WITNESS_TAGS = frozenset({
    "zero-seed",
    "layer:{layer}",
    "kind:{kind}",
})

async def witness_node_modification(
    node: ZeroNode,
    delta: NodeDelta,
    observer: Observer,
) -> Mark:
    """Witness a node modification."""
    return Mark(
        id=generate_mark_id(),
        origin="zero-seed",
        stimulus=Stimulus(
            kind="edit",
            source_node=node.id,
            delta=delta.to_dict(),
        ),
        response=Response(
            kind="node_updated",
            target_node=node.id,
        ),
        umwelt=observer.to_umwelt_snapshot(),
        timestamp=datetime.now(UTC),
        tags=frozenset({
            "zero-seed",
            f"layer:{node.layer}",
            f"kind:{node.kind}",
        }),
    )
```

---

## Open Questions

1. **Void service persistence**: Should entropy/gratitude state persist across sessions?
2. **Cross-graph edges**: Can edges connect nodes in different Zero Seed graphs?
3. **Federation**: How do shared axioms work across users?

---

*"Integration is not bolting together. It is growing from the same root."*
