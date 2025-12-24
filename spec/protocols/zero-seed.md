# Zero Seed Protocol

> *"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

**Filed**: 2025-12-24
**Status**: Genesis — ready for cultivation
**Principles**: Tasteful, Composable, Generative, Heterarchical

---

## Prerequisites

> *Zero Seed is not standalone. It lives within the kgents ecosystem.*

| Prerequisite | Location | What It Provides |
|--------------|----------|------------------|
| **Constitution** | `spec/principles/CONSTITUTION.md` | The 7+7 principles (7 design + 7 governance) |
| **AGENTESE** | `spec/protocols/agentese.md` | Five contexts, path semantics, observer model |
| **Witness Protocol** | `spec/protocols/witness-primitives.md` | Mark and Crystal structures |
| **K-Block** | `spec/protocols/k-block.md` | Transactional isolation for editing |
| **Typed Hypergraph** | `spec/protocols/typed-hypergraph.md` | Graph model foundations |

**Import Order**: Constitution → AGENTESE → Witness → K-Block → Zero Seed

---

## Purpose

Why does this need to exist?

The Zero Seed provides a **minimal, cultivable bootstrap state** for the kgents system. Rather than requiring users to learn an exhaustive metatheory before participating, they receive a living hypergraph they can modify incrementally.

**The Core Tension Resolved**: Users need structure to act meaningfully, but structure imposed externally feels dead. The Zero Seed resolves this by providing a *minimal generative kernel*—enough structure to grow from, sparse enough to make your own.

**Value Proposition**:
- First-time users see 3-5 axiom nodes, not an empty void
- Every element (axiom, value, goal, spec, action, reflection, representation) is a graph node
- All relational morphisms are user-manipulable via modal editing
- The same K-Block + hyperedge system works at every layer
- No separate "configuration" vs "content"—it's all the same graph

---

## The Core Insight

**Everything is a node. Everything composes.**

The Zero Seed formalizes seven epistemic layers into a single integrated holarchy where:
- **Nodes** are elements at any layer (axioms, values, goals, specs, actions, reflections, representations)
- **Edges** are morphisms between elements (`derives_from`, `justifies`, `implements`, `contradicts`, `crystallizes`)
- **Observers** determine what's visible (telescope focal distance × AGENTESE context)
- **Marks** witness every modification (full trace, no exceptions)
- **Contradictions coexist** until user-initiated resolution (paraconsistent tolerance)

---

## Part I: The Seven Layers Formalization

### 1.1 Layer Taxonomy

> **Note on Exemplars vs Mandates**: The node types below are *exemplars*, not exhaustive requirements. You may define additional node kinds within each layer. The layer membership is the constraint; the kind within a layer is suggestive.

| Layer | Semantic Domain | Node Types (Exemplar) | Edge Types (Primary) |
|-------|-----------------|------------|----------------------|
| **L1: Assumptions** | Axioms, beliefs, lifestyle, entitlements | `Axiom`, `Belief`, `Lifestyle`, `Entitlement` | `grounds`, `assumes` |
| **L2: Values** | Principles, natural affinities | `Principle`, `Value`, `Affinity` | `justifies`, `embodies` |
| **L3: Goals** | Dreams, plans, gestures, attention | `Dream`, `Goal`, `Plan`, `Gesture`, `Attention` | `aspires_to`, `directs` |
| **L4: Specification** | Proofs, evidence, argumentations, policy | `Spec`, `Proof`, `Evidence`, `Argument`, `Policy` | `specifies`, `evidences` |
| **L5: Execution** | Implementation, results, experimental data | `Action`, `Result`, `Experiment`, `Data` | `implements`, `produces` |
| **L6: Reflection** | Synthesis, delta on process, process rewards | `Reflection`, `Synthesis`, `Delta`, `Reward` | `reflects_on`, `synthesizes` |
| **L7: Representation** | Interpretation, analysis, insights, meta-cognition, ethics | `Interpretation`, `Analysis`, `Insight`, `Metacognition`, `EthicalJudgment` | `represents`, `interprets` |

### 1.2 Layer Properties

```python
@dataclass(frozen=True)
class Layer:
    level: int                          # 1-7
    name: str                           # "Assumptions", "Values", etc.
    semantic_domain: str                # Human-readable description
    node_types: tuple[str, ...]         # Valid node kinds at this layer
    primary_edges: tuple[str, ...]      # Primary morphism types
    agentese_context: str               # Mapped AGENTESE context
    requires_proof: bool                # Whether Toulmin proof is required

    @property
    def is_axiom_layer(self) -> bool:
        """Axiom layers (L1, L2) are unproven—taken on faith or somatic sense."""
        return self.level <= 2
```

### 1.3 Inter-Layer Morphisms

Edges between layers follow a **directed acyclic flow** with exceptions:

```
L1 (Assumptions)
   ↓ grounds
L2 (Values)
   ↓ justifies
L3 (Goals)
   ↓ specifies
L4 (Specifications)
   ↓ implements
L5 (Execution)
   ↓ reflects_on
L6 (Reflection)
   ↓ represents
L7 (Representation)
   ↓ ← feedback loops allowed →
   ↺ (L7 can modify L1-L6 via witnessed edits)
```

**Exception: Dialectical Feedback**

Any layer can spawn a `contradicts` edge to any other layer. Contradictions are not errors—they are dialectical invitations. The system tracks them; the user resolves (or tolerates) them.

---

## Part II: AGENTESE Context Mapping

### 2.1 Isomorphic Mapping

The Seven Layers map to Five AGENTESE Contexts via a surjective morphism:

| AGENTESE Context | Layers | Semantic |
|------------------|--------|----------|
| `void.*` | L1 + L2 (Assumptions + Values) | The Accursed Share—irreducible ground, not derived |
| `concept.*` | L3 + L4 (Goals + Specifications) | The Abstract—dreams and their formal specification |
| `world.*` | L5 (Execution) | The External—actions in the world, results produced |
| `self.*` | L6 (Reflection) | The Internal—synthesis, process deltas, introspection |
| `time.*` | L7 (Representation) | The Temporal—traces, forecasts, meta-cognition across time |

### 2.2 Path Structure

```
void.axiom.{axiom_id}          → L1 Axiom node
void.value.{value_id}          → L2 Value node
concept.goal.{goal_id}         → L3 Goal node
concept.spec.{spec_id}         → L4 Specification node
world.action.{action_id}       → L5 Execution node
self.reflection.{reflection_id} → L6 Reflection node
time.insight.{insight_id}      → L7 Representation node
```

### 2.3 Observer-Layer Visibility

Different observers see different layers with different affordances:

```python
LAYER_VISIBILITY: dict[str, dict[int, tuple[str, ...]]] = {
    "philosopher": {
        1: ("contemplate", "question", "ground"),
        2: ("weigh", "compare", "judge"),
        7: ("interpret", "meta-analyze"),
    },
    "engineer": {
        4: ("implement", "refactor", "test"),
        5: ("deploy", "measure", "debug"),
    },
    "poet": {
        1: ("feel", "intuit", "metaphorize"),
        3: ("dream", "aspire", "gesture"),
    },
    "strategist": {
        3: ("plan", "prioritize", "allocate"),
        6: ("synthesize", "adjust", "reward"),
    },
}
```

---

## Part III: Hypergraph Data Model

### 3.1 Node Schema

Every element in the Zero Seed is a `ZeroNode`:

```python
@dataclass(frozen=True)
class ZeroNode:
    """A node in the Zero Seed holarchy."""

    # Identity
    id: NodeId                          # Unique identifier
    path: str                           # AGENTESE path (e.g., "void.axiom.mirror-test")

    # Classification
    layer: int                          # 1-7
    kind: str                           # Node type within layer

    # Content
    content: str                        # Markdown content
    title: str                          # Display name

    # Epistemic State
    proof: Proof | None                 # Toulmin structure (None for L1-L2)
    confidence: float                   # [0, 1] subjective confidence

    # Provenance
    created_at: datetime
    created_by: str                     # Agent who created
    lineage: tuple[NodeId, ...]         # Derivation chain

    # Metadata
    tags: frozenset[str]
    metadata: dict[str, Any]
```

### 3.2 Edge Schema

Morphisms between nodes are `ZeroEdge`:

```python
@dataclass(frozen=True)
class ZeroEdge:
    """A morphism between Zero Seed nodes."""

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
    mark_id: MarkId                     # Witness mark (required)

    # For contradicts edges
    is_resolved: bool = False
    resolution_id: NodeId | None = None
```

### 3.3 Edge Kind Taxonomy

```python
class EdgeKind(Enum):
    # Inter-layer (directed DAG flow)
    GROUNDS = "grounds"                 # L1 → L2: Axiom grounds value
    JUSTIFIES = "justifies"             # L2 → L3: Value justifies goal
    SPECIFIES = "specifies"             # L3 → L4: Goal specifies spec
    IMPLEMENTS = "implements"           # L4 → L5: Spec implements as action
    REFLECTS_ON = "reflects_on"         # L5 → L6: Action reflected upon
    REPRESENTS = "represents"           # L6 → L7: Reflection represented

    # Intra-layer (same layer relationships)
    DERIVES_FROM = "derives_from"       # Node derived from sibling
    EXTENDS = "extends"                 # Node extends sibling
    REFINES = "refines"                 # More specific version

    # Dialectical
    CONTRADICTS = "contradicts"         # Paraconsistent conflict
    SYNTHESIZES = "synthesizes"         # Resolution of contradiction
    SUPERSEDES = "supersedes"           # Replaces older version

    # Crystallization
    CRYSTALLIZES = "crystallizes"       # Compression (Mark → Crystal, etc.)
    SOURCES = "sources"                 # Evidence source
```

### 3.4 Bidirectional Invariant

Every edge has a computed inverse. The graph is always navigable in both directions:

```python
EDGE_INVERSES: dict[EdgeKind, EdgeKind] = {
    EdgeKind.GROUNDS: EdgeKind.GROUNDED_BY,
    EdgeKind.JUSTIFIES: EdgeKind.JUSTIFIED_BY,
    EdgeKind.SPECIFIES: EdgeKind.SPECIFIED_BY,
    EdgeKind.IMPLEMENTS: EdgeKind.IMPLEMENTED_BY,
    EdgeKind.REFLECTS_ON: EdgeKind.REFLECTED_BY,
    EdgeKind.REPRESENTS: EdgeKind.REPRESENTED_BY,
    EdgeKind.CONTRADICTS: EdgeKind.CONTRADICTS,  # Symmetric
    # ... etc
}
```

---

## Part IV: Telescope UI & Navigation

### 4.1 Focal Model

The Zero Seed uses a **continuous telescope** metaphor—no discrete zoom levels. Instead, focal distance determines what's visible and how nodes cluster.

```python
@dataclass
class TelescopeState:
    """Current telescope configuration."""

    focal_distance: float               # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None          # What we're focused on

    # Derived visibility
    @property
    def visible_layers(self) -> set[int]:
        """Which layers are visible at current focal distance."""
        if self.focal_distance < 0.2:
            return {self.focal_node.layer}  # Micro: single layer
        elif self.focal_distance < 0.5:
            return {l for l in range(1, 8) if abs(l - self.focal_node.layer) <= 1}
        else:
            return set(range(1, 8))  # Macro: all layers

    @property
    def node_scale(self) -> float:
        """How large nodes appear (for rendering)."""
        return 1.0 - (self.focal_distance * 0.7)
```

### 4.2 Edge-Density Clustering

Nodes cluster based on **edge density**—nodes with many shared edges appear closer:

```python
def compute_proximity(a: ZeroNode, b: ZeroNode, graph: ZeroGraph) -> float:
    """Compute proximity for telescope layout."""
    shared_edges = graph.edges_between(a.id, b.id)
    a_edges = graph.edges_from(a.id) | graph.edges_to(a.id)
    b_edges = graph.edges_from(b.id) | graph.edges_to(b.id)

    if not a_edges or not b_edges:
        return 0.0

    # Jaccard similarity on edge neighborhoods
    intersection = len(a_edges & b_edges)
    union = len(a_edges | b_edges)

    return intersection / union if union > 0 else 0.0
```

### 4.3 Navigation Keybindings

```
TELESCOPE NAVIGATION (continuous zoom):
  +/-      → Zoom in/out (adjust focal_distance)
  =        → Auto-focus on current node
  0        → Reset to macro view
  Shift+0  → Reset to micro view (current node only)

LAYER NAVIGATION (jump by layer):
  [1-7]    → Jump to layer N (sets focal_point to first visible node)
  Tab      → Cycle to next layer
  Shift+Tab → Cycle to previous layer

EDGE NAVIGATION (graph traversal):
  gh/gl    → Parent/child (inter-layer)
  gj/gk    → Previous/next sibling (intra-layer)
  gd       → Follow derives_from edge
  gc       → Follow contradicts edge (if exists)
  gs       → Follow synthesizes edge (resolution)
```

### 4.4 Viewport Projection

```python
def project_to_viewport(
    nodes: list[ZeroNode],
    state: TelescopeState,
    viewport: Rect,
) -> list[NodeProjection]:
    """Project nodes to 2D viewport based on telescope state."""
    projections = []

    for node in nodes:
        if node.layer not in state.visible_layers:
            continue

        # Compute position based on edge-density clustering
        position = compute_clustered_position(node, nodes, state)

        # Scale based on focal distance
        scale = state.node_scale
        if node.id == state.focal_point:
            scale *= 1.5  # Focused node is larger

        projections.append(NodeProjection(
            node=node,
            position=position,
            scale=scale,
            opacity=compute_opacity(node, state),
        ))

    return projections
```

---

## Part V: Axiom Discovery Process

### 5.1 Three-Stage Discovery

Axioms emerge through a **staged discovery process** rather than fixed enumeration:

```
Stage 1: CONSTITUTION MINING
    Input: spec/principles/CONSTITUTION.md, spec/principles/*.md
    Output: Candidate axioms extracted from documented principles
    Method: LLM-assisted extraction + human curation

Stage 2: DIALOGUE REFINEMENT
    Input: Stage 1 candidates + user interaction
    Output: Personalized axiom set via Mirror Test
    Method: Interactive questioning ("Does this feel true for you?")

Stage 3: LIVING CORPUS VALIDATION
    Input: All witness marks, crystals, decisions from system history
    Output: Behaviorally-validated axiom rankings
    Method: Pattern mining ("What do you actually act on?")
```

### 5.2 Stage 1: Constitution Mining

```python
@dataclass
class ConstitutionMiner:
    """Extract candidate axioms from principles documentation."""

    async def mine(self, paths: list[str]) -> list[CandidateAxiom]:
        candidates = []

        for path in paths:
            content = await read_file(path)

            # Extract principle statements
            principles = extract_principle_statements(content)

            for p in principles:
                candidates.append(CandidateAxiom(
                    text=p.text,
                    source_path=path,
                    source_line=p.line,
                    tier=classify_tier(p),  # SOMATIC, AESTHETIC, etc.
                ))

        return deduplicate_and_rank(candidates)
```

### 5.3 Stage 2: Mirror Test Dialogue

```python
async def mirror_test_dialogue(
    candidates: list[CandidateAxiom],
    observer: Observer,
) -> list[ZeroNode]:
    """Refine candidates via interactive Mirror Test."""

    accepted = []

    for candidate in candidates:
        # Present candidate
        response = await ask_user(
            question=f"Does this feel true for you on your best day?\n\n> {candidate.text}",
            options=["Yes, deeply", "Yes, somewhat", "No", "I need to reframe it"],
        )

        match response:
            case "Yes, deeply":
                accepted.append(create_axiom_node(candidate, confidence=1.0))
            case "Yes, somewhat":
                accepted.append(create_axiom_node(candidate, confidence=0.7))
            case "I need to reframe it":
                reframed = await ask_user("How would you say it?")
                accepted.append(create_axiom_node(
                    CandidateAxiom(text=reframed, source_path="user", tier=EvidenceTier.SOMATIC),
                    confidence=1.0,
                ))
            case "No":
                pass  # Skip

    return accepted
```

### 5.4 Stage 3: Living Corpus Validation

```python
async def living_corpus_validation(
    axioms: list[ZeroNode],
    witness_store: WitnessStore,
) -> list[ZeroNode]:
    """Validate axioms against actual witnessed behavior."""

    all_marks = await witness_store.get_all_marks()
    all_crystals = await witness_store.get_all_crystals()

    for axiom in axioms:
        # Find marks that cite this axiom's principles
        citing_marks = [
            m for m in all_marks
            if any(tag in m.tags for tag in axiom.tags)
        ]

        # Compute behavioral alignment score
        if len(citing_marks) > 0:
            alignment = compute_alignment(axiom, citing_marks)
            axiom = axiom.with_metadata(behavioral_alignment=alignment)

        # Check for behavioral contradictions
        contradictions = find_behavioral_contradictions(axiom, all_marks)
        if contradictions:
            for c in contradictions:
                create_edge(EdgeKind.CONTRADICTS, axiom.id, c.id)

    return rank_by_alignment(axioms)
```

---

## Part VI: Proof & Witnessing System

### 6.1 Proof Scope

```python
def requires_proof(node: ZeroNode) -> bool:
    """Axiom layers (L1, L2) are unproven. All others require Toulmin structure."""
    return node.layer > 2
```

### 6.2 Toulmin Structure for Non-Axiom Nodes

```python
@dataclass(frozen=True)
class Proof:
    """Defeasible reasoning structure for L3+ nodes."""

    data: str                           # Evidence ("3 hours, 45K tokens invested")
    warrant: str                        # Reasoning ("Infrastructure enables velocity")
    claim: str                          # Conclusion ("This refactoring was worthwhile")
    backing: str                        # Support for warrant
    qualifier: str                      # Confidence ("definitely", "probably")
    rebuttals: tuple[str, ...]          # Defeaters ("unless API changes")
    tier: EvidenceTier                  # CATEGORICAL, EMPIRICAL, AESTHETIC, etc.
    principles: tuple[str, ...]         # Referenced principles
```

### 6.3 This Spec's Own Proof

As an L4 node, this Zero Seed specification requires a Toulmin proof. Self-application is not exemption.

```yaml
proof:
  data: |
    - 3 years kgents development
    - ~52K lines across 20+ systems
    - Four independent self-validation analyses (categorical, epistemic, dialectical, generative)
    - 85% regenerable from 7 axioms (20:1 compression ratio)

  warrant: |
    Formalized epistemic layers enable coherent evolution. Structure that can
    describe itself can validate itself. Meta-generativity is the signature
    of bootstrap systems (cf. C compilers, Gödel numbering).

  claim: |
    The Zero Seed Protocol resolves the structure-vs-agency tension by providing
    a minimal generative kernel—enough structure to grow from, sparse enough to
    make your own.

  backing: |
    - Categorical foundations (PolyAgent, Operads, Sheaf coherence)
    - Witness system (full tracing, no exceptions)
    - AGENTESE protocol (path semantics, observer-relative behavior)
    - Constitution's 7+7 principles

  qualifier: probably

  rebuttals:
    - "Unless 7-layer taxonomy proves too complex for working memory"
    - "Unless telescope UI is disorienting rather than clarifying"
    - "Unless bootstrap paradox creates implementation deadlock"
    - "Unless AGENTESE path mapping leaks across contexts"

  tier: CATEGORICAL
  principles: [generative, composable, tasteful, heterarchical]
```

### 6.4 Full Witnessing

**Every edit creates a Mark.** No exceptions, no tiers, no opt-outs.

```python
async def modify_node(
    node: ZeroNode,
    delta: NodeDelta,
    observer: Observer,
    reasoning: str,
) -> tuple[ZeroNode, Mark]:
    """Modify a node with full witnessing."""

    # Create new version
    new_node = apply_delta(node, delta)

    # Create witness mark (REQUIRED)
    mark = Mark(
        id=generate_mark_id(),
        origin="zero-seed",
        stimulus=Stimulus(
            kind="edit",
            source_node=node.id,
            delta=delta,
        ),
        response=Response(
            kind="node_updated",
            target_node=new_node.id,
        ),
        umwelt=observer.to_umwelt_snapshot(),
        links=(MarkLink(source=mark.id, target=node.id, kind="modifies"),),
        timestamp=datetime.now(UTC),
        proof=None if node.layer <= 2 else require_proof(delta),
        tags=frozenset({"zero-seed", f"layer:{node.layer}", f"kind:{node.kind}"}),
    )

    # Persist both
    await store.save_node(new_node)
    await store.save_mark(mark)

    return new_node, mark
```

---

## Part VII: Void/Accursed Share Integration

### 7.1 Void Polymorphism (Sum Type)

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
| `void.entropy.*` | Service | Entropy pool operations (sip, pour) |
| `void.random.*` | Service | Random oracle operations (sample) |
| `void.gratitude.*` | Service | Gratitude ledger operations (receive, express) |

**Why polymorphic?** The Accursed Share (Bataille) contains both *structure* (what we believe) and *operations* (how we interact with the irreducible). Axioms and values ARE the Accursed Share; entropy, randomness, and gratitude are its *interfaces*.

### 7.2 Triple Void Structure

The `void.*` context provides three service facilities:

```python
@dataclass
class VoidContext:
    """The Accursed Share—entropy, randomness, gratitude."""

    # 1. Entropy Pool (Bataille's excess energy)
    entropy_pool: EntropyPool

    # 2. Random Oracle (pure randomness)
    oracle: RandomOracle

    # 3. Gratitude Ledger (reciprocal tracking)
    gratitude: GratitudeLedger
```

### 7.3 Entropy Pool (void.entropy.*)

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
```

### 7.4 Random Oracle (void.random.*)

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
```

### 7.5 Gratitude Ledger (void.gratitude.*)

```python
@dataclass
class GratitudeLedger:
    """Track what you've received from outside (slop) and expressed gratitude for."""

    received: list[GratitudeEntry]
    expressed: list[GratitudeEntry]

    @property
    def balance(self) -> float:
        """Gratitude balance: expressed - received."""
        return sum(e.amount for e in self.expressed) - sum(e.amount for e in self.received)

    def receive(self, source: str, amount: float, description: str) -> None:
        """Record something received from outside."""
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
```

### 7.6 Void as Axiom/Value Ground

Since `void.*` maps to L1 + L2, axioms and values are literally stored in the Accursed Share:

```
void.axiom.mirror-test          → L1 Axiom: "Does K-gent feel like me on my best day?"
void.axiom.tasteful-greater     → L1 Axiom: "Tasteful > feature-complete"
void.value.composability        → L2 Value: "Agents are morphisms in a category"
void.value.joy-inducing         → L2 Value: "Delight in interaction; personality matters"
```

This is philosophically correct: axioms and values are **not derived**—they emerge from the irreducible surplus, the Accursed Share.

---

## Part VIII: Edge Creation (Dual Mode)

### 8.1 Modal EDGE Mode

Deliberate, explicit edge creation:

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

### 8.2 Inline Annotation

Fluid edge creation in prose:

```markdown
This goal [[specifies:concept.spec.witness-protocol]] directly.
We [[contradicts:void.axiom.simplicity]] by adding complexity.
```

Parser extracts edges on save:

```python
EDGE_PATTERN = re.compile(r'\[\[(\w+):([^\]]+)\]\]')

def extract_inline_edges(content: str, source_node: ZeroNode) -> list[ZeroEdge]:
    edges = []
    for match in EDGE_PATTERN.finditer(content):
        kind = EdgeKind(match.group(1))
        target_path = match.group(2)
        edges.append(ZeroEdge(
            source=source_node.id,
            target=resolve_path(target_path).id,
            kind=kind,
        ))
    return edges
```

### 8.3 Edge Deduplication

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
        seen[key] = e  # Overwrite
    return list(seen.values())
```

---

## Part IX: Laws & Anti-patterns

### 9.1 Zero Seed Laws

| Law | Statement | Enforcement |
|-----|-----------|-------------|
| **Node Identity** | Each node has exactly one path | Path uniqueness constraint |
| **Layer Integrity** | Node.layer ∈ {1,2,3,4,5,6,7} | Type constraint |
| **Bidirectional Edges** | ∀ edge e, ∃ inverse(e) | Auto-computed on creation |
| **Full Witnessing** | ∀ modification m, ∃ mark(m) | Enforced in modify_node() |
| **Axiom Unprovenness** | L1-L2 nodes have proof=None | Rejected if proof provided |
| **Proof Requirement** | L3+ nodes must have proof | Rejected if proof missing |
| **AGENTESE Mapping** | Layer maps to exactly one context | Surjective mapping |
| **Contradiction Tolerance** | `contradicts` edges may coexist | No automatic resolution |

### 9.2 Anti-patterns

| Anti-pattern | Description | Resolution |
|--------------|-------------|------------|
| **Orphan Axiom** | Axiom with no `grounds` edges to L2 | Warning, not error (may be pending) |
| **Ungrounded Value** | Value with no `grounded_by` edge from L1 | Warning (values can be self-evident) |
| **Proof on Axiom** | Attempting to add proof to L1-L2 node | Error: axioms are taken on faith |
| **Missing Proof** | L3+ node without Toulmin structure | Error: all non-axioms must be justified |
| **Silent Edit** | Modifying node without witness mark | Impossible (enforced) |
| **Layer Skip** | Edge skipping layers (L1 → L4) | Allowed but flagged for review |
| **Contradiction Loop** | A contradicts B contradicts A | Allowed (paraconsistent) but surfaced |

### 9.3 Contradiction Handling

```python
async def check_contradiction_status(graph: ZeroGraph) -> ContradictionReport:
    """Report all unresolved contradictions."""

    contradictions = []
    for edge in graph.edges_of_kind(EdgeKind.CONTRADICTS):
        if not edge.is_resolved:
            contradictions.append(ContradictionPair(
                node_a=graph.get_node(edge.source),
                node_b=graph.get_node(edge.target),
                edge=edge,
            ))

    return ContradictionReport(
        total=len(contradictions),
        by_layer={l: [c for c in contradictions if c.node_a.layer == l] for l in range(1, 8)},
        oldest=min(contradictions, key=lambda c: c.edge.created_at) if contradictions else None,
    )
```

---

## Part X: Integration Points

### 10.1 AGENTESE Protocol

```python
# Zero Seed nodes are AGENTESE nodes
@node("void.axiom", description="Axiom nodes (L1)")
class AxiomNode(BaseLogosNode):
    ...

@node("concept.spec", description="Specification nodes (L4)")
class SpecNode(BaseLogosNode):
    ...
```

### 10.2 K-Block Integration

```python
# All Zero Seed nodes can be edited via K-Block
async def edit_in_kblock(node: ZeroNode) -> KBlock:
    kblock = await kblock_service.create(node.path)
    # K-Block provides:
    # - Checkpoint/rewind
    # - Multi-view (prose, graph, diff)
    # - Entanglement with related nodes
    return kblock
```

### 10.3 Witness Integration

```python
# Zero Seed IS witness-native
# Every node modification creates a mark
# Every mark references the Zero Seed as origin="zero-seed"
```

### 10.4 Hypergraph Editor

```python
# Zero Seed graph renders in existing Hypergraph Editor
# Telescope navigation is a new mode
# Edge creation uses existing EDGE mode with Zero Seed edge kinds
```

---

## Part XI: Bootstrap Initialization

### 11.1 First Run

```python
async def initialize_zero_seed(user: User) -> ZeroGraph:
    """Initialize Zero Seed for new user."""

    graph = ZeroGraph()

    # Stage 1: Mine constitution for candidate axioms
    miner = ConstitutionMiner()
    candidates = await miner.mine([
        "spec/principles/CONSTITUTION.md",
        "spec/principles/meta.md",
        "spec/principles/operational.md",
    ])

    # Stage 2: Mirror Test dialogue
    axioms = await mirror_test_dialogue(candidates, user.observer)

    # Add axioms to graph
    for axiom in axioms:
        graph.add_node(axiom)

    # Stage 3 happens over time (behavioral validation)
    # Initial graph has axioms only

    # Create welcome node
    welcome = ZeroNode(
        id=generate_node_id(),
        path="concept.goal.cultivate-zero-seed",
        layer=3,
        kind="Goal",
        content="Cultivate your Zero Seed by adding values, goals, and eventually specifications.",
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
        created_by=user.id,
        lineage=tuple(a.id for a in axioms),  # Grounded in axioms
        tags=frozenset({"zero-seed", "bootstrap", "welcome"}),
    )
    graph.add_node(welcome)

    # Create edges from axioms to welcome goal
    for axiom in axioms:
        graph.add_edge(ZeroEdge(
            source=axiom.id,
            target=welcome.id,
            kind=EdgeKind.GROUNDS,
            context="Bootstrap cultivation goal",
            confidence=1.0,
            created_at=datetime.now(UTC),
            mark_id=create_bootstrap_mark().id,
        ))

    return graph
```

### 11.2 Incremental Growth

```markdown
Day 1: User has 3-5 axioms + welcome goal
Day 2: User adds first value (L2)
       Edges: axiom → value (GROUNDS), value → goal (JUSTIFIES)
Day 7: User adds specification (L4)
       Edges: goal → spec (SPECIFIES)
Day 14: User performs first action (L5)
        Edges: spec → action (IMPLEMENTS)
Day 30: User reflects on progress (L6)
        Edges: action → reflection (REFLECTS_ON)
...
```

---

## Part XII: Grounding Chain (Self-Application)

### 12.1 The Spec's Own Grounding

This Zero Seed specification (`concept.spec.zero-seed`) requires grounding nodes per its own laws. A spec without parent nodes violates bidirectional edge requirements.

**Required Nodes**:

```yaml
# L1: Axiom (from Constitution)
- id: "axiom-generative"
  path: "void.axiom.generative-principle"
  layer: 1
  kind: "Axiom"
  title: "The Generative Principle"
  content: |
    Spec is compression; design should generate implementation.
    A well-formed specification captures the essential decisions,
    reducing implementation entropy.
  proof: null  # Axiom
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
  proof: null  # Value

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

**Required Edges**:

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

### 12.2 Bootstrap Witnessing

The grounding chain creates a bootstrap paradox: the spec exists before its grounding nodes. Resolution via **retroactive witnessing**:

```python
async def retroactive_witness_bootstrap(spec_node: ZeroNode) -> list[Mark]:
    """Create marks for bootstrap artifacts after the fact."""
    marks = []

    # Create grounding nodes
    axiom = create_generative_axiom()
    value = create_cultivable_value()
    goal = create_provide_goal()

    # Mark each creation with bootstrap tag
    for node in [axiom, value, goal]:
        mark = Mark(
            id=generate_mark_id(),
            origin="zero-seed",
            stimulus=Stimulus(kind="bootstrap", source="retroactive"),
            response=Response(kind="node_created", target_node=node.id),
            tags=frozenset({"bootstrap:retroactive", "zero-seed", "grounding-chain"}),
            timestamp=datetime.now(UTC),
        )
        marks.append(mark)

    # Create edge marks
    for edge in create_grounding_edges(axiom, value, goal, spec_node):
        mark = Mark(
            id=generate_mark_id(),
            origin="zero-seed",
            stimulus=Stimulus(kind="bootstrap", source="retroactive"),
            response=Response(kind="edge_created", target_edge=edge.id),
            tags=frozenset({"bootstrap:retroactive", "zero-seed", "grounding-chain"}),
            timestamp=datetime.now(UTC),
        )
        marks.append(mark)

    return marks
```

---

## Part XIII: Strange Loop (Meta-Generativity)

### 13.1 The Loop

The Zero Seed Protocol exhibits **Gödelian self-reference**:

```
Zero Seed is an L4 specification
  ↓ that defines
Layers L1-L7
  ↓ which includes
L4 (Specification layer)
  ↓ where Zero Seed resides
```

This is a **strange loop** (Hofstadter): the spec defines the layer system that contains it.

### 13.2 Why This Is a Feature

Like a C compiler written in C, the self-reference is **productive**:

| Bootstrap System | Self-Reference | Resolution |
|------------------|----------------|------------|
| C compiler | Compiles itself | Temporal: first bootstrap with simpler compiler |
| Gödel numbering | Encodes statements about numbers | Logical: distinguish levels |
| Zero Seed | Defines layers that contain it | Both: temporal genesis + logical grounding |

### 13.3 Temporal vs Logical Ordering

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

### 13.4 The Fixed Point Property

Formally, Zero Seed is a **categorical fixed point**:

```
Let F: Spec → Graph be the function that generates a graph from a spec.
Let E: Graph → Spec be the function that extracts the defining spec from a graph.

Zero Seed = E(F(Zero Seed))

The Zero Seed is the unique specification that, when instantiated as a graph
and then re-extracted as a spec, produces itself (up to isomorphism).
```

This is not a bug—it is the **price of self-description** and the **gift of generativity**.

### 13.5 Operational Implication

When implementing Zero Seed:

1. **Don't fight the loop** — Accept that the spec precedes its own grounding
2. **Use retroactive witnessing** — Create marks for bootstrap artifacts after the fact
3. **Verify the fixed point** — `regenerate(Zero Seed) ≅ Zero Seed` (85% achieved)
4. **Document deviations** — The 15% that can't regenerate is empirical reality

> *"The seed does not ask: 'What planted me?'
> The seed asks: 'What will I grow?'"*

---

## Part XIV: DP-Native Integration

> *"The value IS the agent. The trace IS the proof."*

### 14.1 The Agent-DP Isomorphism Applied to Zero Seed

The DP-Native kgents work (`spec/theory/dp-native-kgents.md`) reveals that Zero Seed's seven-layer structure IS a dynamic programming formulation:

```
Zero Seed as MDP:
  S = {ZeroNode instances}                    # State space
  A = {EdgeKind operations}                   # Action space
  T(s, a) = traverse_edge(s, a)               # Transition
  R(s, a, s') = constitution.reward(s, a, s') # Constitutional reward
  γ = focal_distance                          # Discount factor
```

### 14.2 The Bellman Equation for Layer Traversal

Navigating the seven-layer holarchy follows the Bellman equation:

```python
V*(node) = max_edge [
    Constitution.reward(node, edge, target) +
    γ · V*(target)
]

where:
    V*(node) = optimal value of being at this node
    edge ∈ {grounds, justifies, specifies, implements, ...}
    Constitution.reward() = weighted sum of 7 principle scores
    γ = telescope focal_distance (0.0=micro, 1.0=macro)
```

**Key Insight**: The discount factor γ maps directly to telescope focal distance:
- `γ → 0`: Myopic view (single layer, micro focus)
- `γ → 1`: Far-sighted view (all layers, macro perspective)

### 14.3 Toulmin Proof as PolicyTrace

The DP PolicyTrace and Toulmin Proof are isomorphic:

| PolicyTrace | Toulmin Proof | Zero Seed |
|-------------|---------------|-----------|
| `state_before` | `data` | Source node |
| `action` | `warrant` | Edge kind |
| `state_after` | `claim` | Target node |
| `value` | `qualifier` | Confidence |
| `rationale` | `backing` | Context |
| `log` | `rebuttals` | Contradiction edges |

```python
def proof_to_trace(proof: Proof) -> PolicyTrace[NodeId]:
    """Convert Toulmin proof to DP trace."""
    entry = TraceEntry(
        state_before=proof.data,
        action=proof.warrant,
        state_after=proof.claim,
        value=qualifier_to_value(proof.qualifier),
        rationale=proof.backing,
    )
    return PolicyTrace.pure(None).with_entry(entry)

def trace_to_proof(trace: PolicyTrace[NodeId]) -> Proof:
    """Convert DP trace to Toulmin proof."""
    entries = trace.log
    return Proof(
        data=str(entries[0].state_before) if entries else "",
        warrant=" → ".join(e.action for e in entries),
        claim=str(entries[-1].state_after) if entries else "",
        qualifier=value_to_qualifier(trace.total_value()),
        backing="; ".join(e.rationale for e in entries if e.rationale),
        tier=EvidenceTier.CATEGORICAL,
        principles=(),
        rebuttals=(),
    )
```

### 14.4 Constitution as the Seven-Principle Reward

The DP Constitution (`dp/core/constitution.py`) provides the reward function for Zero Seed operations:

```python
class ZeroSeedConstitution(Constitution):
    """Constitutional reward for Zero Seed operations."""

    def __init__(self):
        super().__init__()

        # Principle evaluators for Zero Seed domain
        self.set_evaluator(
            Principle.TASTEFUL,
            lambda s, a, ns: 1.0 if len(ns.content) < 500 else 0.5,
            lambda s, a, ns: "Concise nodes are tasteful"
        )

        self.set_evaluator(
            Principle.COMPOSABLE,
            lambda s, a, ns: 1.0 if a in LAYER_EDGES[s.layer] else 0.3,
            lambda s, a, ns: f"Edge {a} follows layer ordering"
        )

        self.set_evaluator(
            Principle.GENERATIVE,
            lambda s, a, ns: min(1.0, len(s.lineage) / 3),
            lambda s, a, ns: f"Node has {len(s.lineage)} ancestors"
        )

        # ETHICAL principle: axioms (L1-L2) cannot be overwritten
        self.set_evaluator(
            Principle.ETHICAL,
            lambda s, a, ns: 0.0 if a == "supersedes" and s.layer <= 2 else 1.0,
            lambda s, a, ns: "Axioms cannot be superseded without Mirror Test"
        )

# Use in value computation
zero_constitution = ZeroSeedConstitution()
reward = zero_constitution.reward(source_node, edge_kind, target_node)
```

### 14.5 Axiom Discovery as MetaDP

The three-stage axiom discovery process IS MetaDP—iterating on problem formulations:

```python
class AxiomDiscoveryMetaDP(MetaDP[str, str]):
    """
    MetaDP for finding optimal axiom formulations.

    Level 0: Initial formulation (Constitution mining)
    Level 1: Solve Bellman (which axioms satisfy principles?)
    Level 2: Evaluate quality (Mirror Test alignment)
    Level 3: Refine formulation (living corpus validation)
    """

    def __init__(self, constitution_paths: list[str]):
        super().__init__()

        # Stage 1: Constitution Mining as initial formulation
        stage1 = ProblemFormulation(
            name="constitution_mining",
            description="Extract axiom candidates from principles docs",
            state_type=str,
            initial_states=frozenset(constitution_paths),
            goal_states=frozenset(),  # Unknown until discovery
            available_actions=lambda s: frozenset(["extract", "filter", "rank"]),
            transition=lambda s, a: mine_transition(s, a),
            reward=lambda s, a, ns: self.mining_reward(s, a, ns),
        )
        self.add_formulation(stage1)

        # Stage 2: Mirror Test as reformulation
        self.add_reformulator(
            "mirror_test",
            lambda f: self.apply_mirror_test(f)
        )

        # Stage 3: Living Corpus as refinement
        self.add_reformulator(
            "living_corpus",
            lambda f: self.validate_with_corpus(f)
        )

    def mining_reward(self, state: str, action: str, next_state: str) -> float:
        """Reward axiom candidates that compress well."""
        # GENERATIVE principle: compression ratio
        if action == "extract":
            return 0.3  # Extraction is easy, low reward
        elif action == "filter":
            return 0.6  # Filtering requires judgment
        elif action == "rank":
            return 0.9  # Ranking is the goal
        return 0.5
```

### 14.6 OptimalSubstructure as Sheaf Coherence

The DP optimal substructure property IS the sheaf gluing condition for Zero Seed:

```
OptimalSubstructure:
    "Optimal solutions to subproblems compose to optimal solutions"

Sheaf Gluing:
    "Local sections that agree on overlaps glue to a global section"

In Zero Seed:
    Local: Proof for edge A→B, proof for edge B→C
    Overlap: Node B (shared endpoint)
    Global: Proof for path A→B→C
```

```python
class ZeroSeedOptimalSubstructure(OptimalSubstructure[NodeId]):
    """Verify that Zero Seed proofs compose correctly."""

    def verify_path(
        self,
        path: list[ZeroEdge],
    ) -> bool:
        """
        Verify that a path through the hypergraph has optimal substructure.

        Each edge must be locally optimal, and the glued path must be
        globally optimal (i.e., no better path exists).
        """
        if len(path) < 2:
            return True

        # Get subproblem solutions for each edge
        subsolutions = []
        for edge in path:
            key = (edge.source, edge.target)
            solution = self.solutions.get(key)
            if solution is None:
                # Edge not yet verified as optimal
                return False
            subsolutions.append(solution)

        # Glue and verify
        glued = subsolutions[0]
        for sub in subsolutions[1:]:
            glued_result = self.glue(glued, sub)
            if glued_result is None:
                return False  # Gluing failed
            glued = glued_result

        return True
```

### 14.7 Contradiction as Pareto Frontier

Paraconsistent tolerance in Zero Seed maps to multi-objective DP:

```python
def handle_contradiction(
    node_a: ZeroNode,
    node_b: ZeroNode,
    constitution: Constitution,
) -> ContradictionResolution:
    """
    Contradictions are Pareto frontiers, not errors.

    Two nodes contradict iff:
    - Neither dominates the other on all principles
    - They represent incomparable trade-offs
    """
    score_a = constitution.evaluate(None, "exist", node_a)
    score_b = constitution.evaluate(None, "exist", node_b)

    a_dominates = all(
        pa.score >= pb.score
        for pa, pb in zip(score_a.principle_scores, score_b.principle_scores)
    )
    b_dominates = all(
        pb.score >= pa.score
        for pa, pb in zip(score_a.principle_scores, score_b.principle_scores)
    )

    if a_dominates and not b_dominates:
        return ContradictionResolution(winner=node_a, reason="A dominates B")
    elif b_dominates and not a_dominates:
        return ContradictionResolution(winner=node_b, reason="B dominates A")
    else:
        # Pareto-incomparable: both are valid, let them coexist
        return ContradictionResolution(
            winner=None,
            reason="Pareto-incomparable: dialectical invitation",
            synthesis_required=True,
        )
```

### 14.8 ValueAgent for Intelligent Navigation

Telescope navigation becomes value-guided:

```python
@dataclass
class TelescopeValueAgent(ValueAgent[TelescopeState, NavigationAction, NodeId]):
    """
    Value-guided telescope navigation.

    The optimal policy tells you where to look next.
    """

    def __post_init__(self):
        self.states = self._compute_telescope_states()
        self.actions = lambda s: self._available_navigation_actions(s)
        self.transition = lambda s, a: self._navigate(s, a)
        self.output_fn = lambda s, a, ns: ns.focal_point
        self.constitution = ZeroSeedConstitution()

    def _navigation_reward(
        self,
        state: TelescopeState,
        action: NavigationAction,
        next_state: TelescopeState,
    ) -> float:
        """
        Reward navigation that leads to high-value nodes.

        JOY_INDUCING: Finding interesting nodes is delightful
        TASTEFUL: Focused navigation over random wandering
        """
        if next_state.focal_point is None:
            return 0.1  # Lost focus is bad

        target_node = self.graph.get_node(next_state.focal_point)
        if target_node is None:
            return 0.1

        # Higher value for more connected nodes (more edges = more interesting)
        connectivity = len(self.graph.edges_from(target_node.id))

        # Higher value for nodes at user's preferred layer
        layer_alignment = 1.0 - abs(target_node.layer - self.preferred_layer) / 7.0

        return 0.5 * min(1.0, connectivity / 5) + 0.5 * layer_alignment
```

### 14.9 Summary: DP-Native Zero Seed

The DP-Native integration reveals that Zero Seed is not just a hypergraph—it's a **value-optimizing system**:

| Zero Seed Concept | DP-Native Mapping |
|-------------------|-------------------|
| 7 Epistemic Layers | State space partitions |
| Edge traversal | Action selection |
| Proof/Witness | PolicyTrace |
| Constitution (7 principles) | Reward function |
| Telescope focal distance | Discount factor γ |
| Axiom discovery | MetaDP reformulation |
| Contradiction tolerance | Pareto frontier |
| Sheaf coherence | OptimalSubstructure |

**The Core Synthesis**:

```
Zero Seed = MetaDP[
    States = ZeroNode,
    Actions = EdgeKind,
    Reward = Constitution(7 principles),
    Trace = PolicyTrace ≅ Toulmin Proof ≅ Witness Mark
]
```

> *"The proof IS the decision. The trace IS the witness. The value IS the agent."*

---

## Part XV: LLM-Augmented Intelligence

> *"LLM calls are decisions. Decisions require proofs. Proofs are witnessed."*

### 15.1 Design Philosophy: Principled, Not Pervasive

LLM integration follows strict principles:

1. **At Decision Points, Not Everywhere** — LLM calls at critical junctures, not batch over everything
2. **Tiered Cost** — Haiku for cheap validation, Sonnet for important synthesis
3. **Fully Witnessed** — Every LLM call creates a Mark with token counts
4. **User Transparency** — Clear indication before/after each call
5. **Budget Conscious** — Session-level token tracking with soft limits

**Anti-Pattern**: Running LLM over all nodes on startup.
**Pattern**: LLM on-demand at user-initiated decision points.

### 15.2 Model Tiers

| Tier | Model | Use Case | Cost | Token Target |
|------|-------|----------|------|--------------|
| **Scout** | `haiku` | Classification, validation, suggestions | ~$0.25/1M | <500 tokens |
| **Analyst** | `sonnet` | Synthesis, proof evaluation, dialogue | ~$3/1M | <2000 tokens |
| **Oracle** | `opus` | Critical decisions, constitutional judgment | ~$15/1M | On-demand only |

```python
class LLMTier(Enum):
    SCOUT = "haiku"      # Fast, cheap, good for classification
    ANALYST = "sonnet"   # Balanced, for synthesis and dialogue
    ORACLE = "opus"      # Expensive, for critical decisions
```

### 15.3 LLM Call Points in Zero Seed

| Operation | Tier | When | Token Budget | Purpose |
|-----------|------|------|--------------|---------|
| **Axiom Mining** | Scout | Stage 1 discovery | ~300/doc | Extract candidate axioms from constitution |
| **Mirror Test Dialogue** | Analyst | Stage 2 refinement | ~1000/exchange | Facilitate Socratic questioning |
| **Proof Validation** | Scout | On proof creation | ~200/proof | Check Toulmin structure coherence |
| **Edge Suggestion** | Scout | On node creation | ~300/node | Suggest relevant edges |
| **Contradiction Detection** | Analyst | On edge creation | ~500/pair | Detect semantic contradictions |
| **Synthesis Generation** | Analyst | On resolution request | ~1500/synthesis | Create synthesized nodes |
| **Macro Summarization** | Scout | On telescope zoom-out | ~400/cluster | Compress for macro view |

### 15.4 The Witnessed LLM Call

Every LLM call creates a Mark. This provides:
- **Auditability**: What was asked, what was answered
- **Cost tracking**: Token counts per operation
- **Reproducibility**: Same prompt should give similar results
- **Debugging**: When things go wrong, we have traces

```python
@dataclass(frozen=True)
class LLMCallMark:
    """Mark structure for LLM calls."""

    # Standard Mark fields
    origin: str = "zero-seed.llm"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # LLM-specific fields
    tier: LLMTier
    operation: str                      # e.g., "axiom_mining", "proof_validation"
    prompt_summary: str                 # First 200 chars of prompt
    response_summary: str               # First 200 chars of response

    # Token tracking
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float

    # Context
    node_ids: tuple[NodeId, ...]        # Relevant nodes
    user_visible: bool = True           # Was this shown to user?

    def to_mark(self) -> Mark:
        """Convert to standard Mark for witnessing."""
        return Mark(
            origin=self.origin,
            stimulus=Stimulus(
                kind="llm_call",
                content=self.prompt_summary,
                metadata={
                    "tier": self.tier.value,
                    "operation": self.operation,
                    "input_tokens": self.input_tokens,
                },
            ),
            response=Response(
                kind="llm_response",
                content=self.response_summary,
                success=True,
                metadata={
                    "output_tokens": self.output_tokens,
                    "total_tokens": self.total_tokens,
                    "estimated_cost_usd": self.estimated_cost_usd,
                },
            ),
            timestamp=self.timestamp,
            tags=frozenset({
                "zero-seed",
                "llm",
                f"tier:{self.tier.value}",
                f"op:{self.operation}",
            }),
        )
```

### 15.5 Liberal Token Budgets

> *"Generous budgets enable radical UX simplification."*

We embrace liberal token budgets to minimize user friction:

```python
class SessionLength(Enum):
    SHORT = "short"    # Quick edits, single-topic
    STANDARD = "standard"  # Typical work session
    LONG = "long"      # Deep exploration, major refactor

@dataclass
class TokenBudget:
    """Liberal session-level token budget."""

    # Generous limits by session type (combined ingress + egress)
    session_limits: dict[SessionLength, int] = field(default_factory=lambda: {
        SessionLength.SHORT: 200_000,      # 200k tokens (~$0.60 haiku, ~$7 sonnet)
        SessionLength.STANDARD: 500_000,   # 500k tokens
        SessionLength.LONG: 2_000_000,     # 2M tokens for deep work
    })

    session_type: SessionLength = SessionLength.STANDARD
    total_used: int = 0
    call_history: list[LLMCallMark] = field(default_factory=list)

    # Suppressed suggestions (user dismissed)
    suppressed: set[str] = field(default_factory=set)

    @property
    def limit(self) -> int:
        return self.session_limits[self.session_type]

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.total_used)

    @property
    def usage_pct(self) -> float:
        return (self.total_used / self.limit * 100) if self.limit > 0 else 0

    def track(self, call: LLMCallMark) -> None:
        """Track an LLM call."""
        self.total_used += call.total_tokens
        self.call_history.append(call)

    def suppress(self, suggestion_id: str) -> None:
        """User dismisses a suggestion - don't show again this session."""
        self.suppressed.add(suggestion_id)

    def is_suppressed(self, suggestion_id: str) -> bool:
        return suggestion_id in self.suppressed

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Session ({self.session_type.value}): "
            f"{self.total_used:,}/{self.limit:,} tokens ({self.usage_pct:.1f}%)"
        )
```

**Philosophy**: With 200k-2M token budgets, we can afford to:
- Do comprehensive analysis upfront (fewer back-and-forth edits)
- Proactively surface issues (self-awareness)
- Let users ignore suggestions without guilt

### 15.6 Self-Aware Analysis

The system proactively identifies weak spots in the graph, surfacing them for user attention with ability to ignore:

```python
@dataclass
class WeakSpot:
    """A weakness the system has identified."""
    id: str                          # For suppression tracking
    node_id: NodeId | None           # Affected node (if any)
    severity: Literal["info", "warning", "critical"]
    category: str                    # e.g., "proof_coherence", "orphan_node", "axiom_drift"
    title: str                       # Human-readable title
    description: str                 # What's wrong
    suggestion: str                  # How to fix
    auto_fixable: bool               # Can system fix automatically?
    confidence: float                # 0.0-1.0

@dataclass
class SelfAwarenessResult:
    """Result of self-aware analysis."""
    weak_spots: list[WeakSpot]
    tokens_used: int
    analysis_time_ms: int

    def critical(self) -> list[WeakSpot]:
        return [w for w in self.weak_spots if w.severity == "critical"]

    def actionable(self) -> list[WeakSpot]:
        return [w for w in self.weak_spots if w.auto_fixable]

async def analyze_graph_health(
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
    scope: Literal["focused", "comprehensive"] = "focused",
) -> SelfAwarenessResult:
    """
    Proactively analyze graph for issues.

    Uses liberal token budget to do comprehensive analysis.
    Results are surfaced to user with ability to suppress.
    """
    # Collect graph context
    nodes_summary = summarize_nodes(graph.nodes, max_chars=50_000)
    edges_summary = summarize_edges(graph.edges, max_chars=20_000)
    proofs_summary = summarize_proofs(graph.nodes, max_chars=30_000)

    prompt = f"""Analyze this epistemic graph for weaknesses.

NODES (by layer):
{nodes_summary}

EDGES:
{edges_summary}

PROOFS:
{proofs_summary}

Identify issues in these categories:
1. **Orphan Nodes**: Nodes with no incoming edges (except L1 axioms)
2. **Proof Coherence**: Toulmin proofs with weak warrants or missing backing
3. **Layer Violations**: Edges that skip layers inappropriately
4. **Axiom Drift**: L1-L2 nodes that have drifted from Constitution
5. **Dead Ends**: Nodes with no outgoing edges (except L7)
6. **Contradiction Clusters**: Multiple contradicting nodes without synthesis

For each issue, provide:
- severity: "info" | "warning" | "critical"
- category: one of the above
- title: short description
- description: what's wrong
- suggestion: how to fix
- auto_fixable: true if system can fix automatically
- confidence: 0.0-1.0

{"Focus on the most critical 3-5 issues." if scope == "focused" else "Be comprehensive, find all issues."}

Return as JSON array.
"""

    response = await llm.generate(
        system="You are analyzing an epistemic graph for structural and semantic weaknesses.",
        user=prompt,
        temperature=0.2,
        max_tokens=4000 if scope == "focused" else 10000,
    )

    # Track the call
    call_mark = create_llm_call_mark(
        tier=LLMTier.ANALYST,
        operation="self_awareness",
        prompt=prompt,
        response=response,
        node_ids=tuple(n.id for n in graph.nodes[:10]),  # Sample
    )
    budget.track(call_mark)

    # Parse and filter suppressed
    weak_spots = parse_weak_spots(response.text)
    weak_spots = [w for w in weak_spots if not budget.is_suppressed(w.id)]

    return SelfAwarenessResult(
        weak_spots=weak_spots,
        tokens_used=response.tokens_used,
        analysis_time_ms=response.raw_metadata.get("duration_ms", 0),
    )
```

### 15.7 Minimal-Edit UX

The system does more work upfront to minimize user edits:

```python
async def create_node_complete(
    user_content: str,
    layer: int,
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
) -> NodeCreationResult:
    """
    Create a node with ALL supporting structure in one operation.

    Instead of:
      1. User creates node
      2. User adds proof
      3. User adds edges
      4. System validates
      5. User fixes issues

    We do:
      1. User provides content
      2. System creates node + proof + edges + validates
      3. User reviews and accepts (or edits)
    """
    prompt = f"""Create a complete node structure for this content.

USER CONTENT:
{user_content}

TARGET LAYER: L{layer} ({LAYER_NAMES[layer]})

EXISTING GRAPH CONTEXT:
{summarize_relevant_nodes(graph, layer, max_chars=30_000)}

Generate:
1. **Node**: title, cleaned content, path, tags
2. **Proof**: Full Toulmin structure (data, warrant, claim, backing, qualifier, rebuttals)
3. **Edges**: 2-5 edges connecting to existing nodes
   - At least one "parent" edge from lower layer
   - Optional "sibling" edges to same layer
   - Optional "child" edges to higher layer
4. **Validation**: Pre-check for issues

Return complete JSON structure ready for insertion.
"""

    response = await llm.generate(
        system="You are creating complete, well-connected epistemic nodes.",
        user=prompt,
        temperature=0.4,
        max_tokens=3000,
    )

    budget.track(create_llm_call_mark(LLMTier.ANALYST, "node_complete", prompt, response, ()))

    result = parse_node_creation_result(response.text)

    # Auto-validate before returning
    if result.validation_issues:
        # Try to auto-fix
        result = await auto_fix_issues(result, llm, budget)

    return result
```

### 15.8 User Transparency (Streamlined)

With liberal budgets, we simplify the display:

```
┌─────────────────────────────────────────────────────────────────────┐
│  ✨ Creating node with proof and 4 edges...                         │
│  ──────────────────────────────────────────────────────────────────  │
│  Session: 12,450 / 200,000 tokens (6.2%)                            │
└─────────────────────────────────────────────────────────────────────┘
```

After completion, show result with dismiss option:

```
┌─────────────────────────────────────────────────────────────────────┐
│  ✓ Node created: "Principle of Minimal Authority"                   │
│  ──────────────────────────────────────────────────────────────────  │
│  + Proof: Toulmin structure (coherence: 0.91)                       │
│  + Edges: grounds←axiom-001, justifies→goal-003, +2 more            │
│                                                                     │
│  ⚠️ 1 suggestion: Consider adding backing from Constitution §3      │
│     [Apply] [Ignore] [Ignore all like this]                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 15.9 Surfacing Weak Spots

The system surfaces weak spots proactively, with user control:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 Graph Health (analyzed 47 nodes)                                │
│  ──────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ⚠️ WARNING: "goal-005" has weak proof backing                      │
│     Suggestion: Add reference to spec/principles/CONSTITUTION.md    │
│     [Fix automatically] [Edit manually] [Ignore]                    │
│                                                                     │
│  ℹ️ INFO: 3 nodes have no outgoing edges                            │
│     These may be dead ends or awaiting expansion.                   │
│     [Show nodes] [Ignore all orphan warnings]                       │
│                                                                     │
│  Session: 45,200 / 200,000 tokens (22.6%)                           │
└─────────────────────────────────────────────────────────────────────┘
```

User actions:
- **Fix automatically**: System applies the suggested fix
- **Edit manually**: Opens the node for user editing
- **Ignore**: Suppresses this specific suggestion for the session
- **Ignore all like this**: Suppresses this category of suggestions

### 15.10 LLM Operations Implementation

#### 15.10.1 Axiom Mining (Scout)

```python
async def mine_axioms_from_constitution(
    constitution_path: str,
    llm: LLMClient,
    budget: TokenBudget,
) -> list[CandidateAxiom]:
    """
    Stage 1: Extract axiom candidates from constitution.

    Uses Scout tier (haiku) for cost efficiency.
    ~300 tokens per document.
    """
    content = await read_file(constitution_path)

    prompt = f"""Extract the 3-5 most fundamental axioms from this principles document.

For each axiom, provide:
1. The axiom statement (one sentence)
2. The source section
3. Why it's irreducible (can't be derived from something more basic)

Document:
{content[:4000]}  # Truncate to control tokens

Format as JSON:
[{{"statement": "...", "source": "...", "irreducibility": "..."}}]
"""

    # Check budget
    check = budget.check_budget(LLMTier.SCOUT, estimated_tokens=300)
    if not check.allowed:
        raise BudgetExceededError(check.message)

    # Show user we're calling
    display_llm_call_start("Axiom Mining", LLMTier.SCOUT, 300, constitution_path)

    # Call LLM
    response = await llm.generate(
        system="You are extracting fundamental axioms from a principles document.",
        user=prompt,
        temperature=0.3,  # Low temperature for extraction
        max_tokens=500,
    )

    # Create witness mark
    call_mark = LLMCallMark(
        tier=LLMTier.SCOUT,
        operation="axiom_mining",
        prompt_summary=prompt[:200],
        response_summary=response.text[:200],
        input_tokens=response.raw_metadata.get("usage", {}).get("input_tokens", 0),
        output_tokens=response.raw_metadata.get("usage", {}).get("output_tokens", 0),
        total_tokens=response.tokens_used,
        estimated_cost_usd=response.tokens_used * 0.00000025,  # Haiku pricing
        node_ids=(),
    )
    budget.track(call_mark)
    await witness_store.save_mark(call_mark.to_mark())

    # Show user result
    display_llm_call_complete(call_mark)

    # Parse and return
    return parse_axiom_candidates(response.text)
```

#### 15.10.2 Proof Validation (Scout)

```python
async def validate_proof(
    proof: Proof,
    node: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ProofValidation:
    """
    Validate a Toulmin proof structure.

    Uses Scout tier (haiku) - quick structural check.
    ~200 tokens per proof.
    """
    prompt = f"""Evaluate this Toulmin proof structure:

DATA: {proof.data}
WARRANT: {proof.warrant}
CLAIM: {proof.claim}
BACKING: {proof.backing}
QUALIFIER: {proof.qualifier}
REBUTTALS: {proof.rebuttals}

Check:
1. Does the data support the warrant?
2. Does the warrant justify the claim?
3. Is the qualifier appropriate given rebuttals?
4. Is the backing sufficient?

Rate overall coherence 0.0-1.0 and explain briefly.
Format: {{"coherence": 0.X, "issues": ["..."], "suggestion": "..."}}
"""

    check = budget.check_budget(LLMTier.SCOUT, estimated_tokens=200)
    if not check.allowed:
        # Degrade gracefully - skip LLM validation
        return ProofValidation(coherence=0.5, issues=["Budget exceeded, using default"], llm_validated=False)

    display_llm_call_start("Proof Validation", LLMTier.SCOUT, 200, node.title)

    response = await llm.generate(
        system="You are a proof structure validator checking Toulmin argument coherence.",
        user=prompt,
        temperature=0.2,
        max_tokens=300,
    )

    # Track and witness
    call_mark = create_llm_call_mark(LLMTier.SCOUT, "proof_validation", prompt, response, (node.id,))
    budget.track(call_mark)
    await witness_store.save_mark(call_mark.to_mark())

    display_llm_call_complete(call_mark)

    return parse_proof_validation(response.text)
```

#### 15.10.3 Contradiction Detection (Analyst)

```python
async def detect_contradiction(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ContradictionAnalysis:
    """
    Detect if two nodes semantically contradict.

    Uses Analyst tier (sonnet) - needs deeper understanding.
    ~500 tokens per pair.
    """
    prompt = f"""Analyze whether these two statements contradict each other:

STATEMENT A ({node_a.title}):
{node_a.content[:500]}

STATEMENT B ({node_b.title}):
{node_b.content[:500]}

Determine:
1. Do they directly contradict? (mutually exclusive claims)
2. Do they tension? (compatible but pulling different directions)
3. Are they independent? (unrelated domains)
4. Do they complement? (different aspects of same truth)

Provide:
- relationship: "contradiction" | "tension" | "independent" | "complement"
- confidence: 0.0-1.0
- explanation: brief reasoning
- synthesis_hint: if contradiction/tension, how might they be reconciled?

Format as JSON.
"""

    check = budget.check_budget(LLMTier.ANALYST, estimated_tokens=500)
    if not check.allowed:
        return ContradictionAnalysis(
            relationship="unknown",
            confidence=0.0,
            explanation="Budget exceeded",
            llm_analyzed=False,
        )

    display_llm_call_start("Contradiction Detection", LLMTier.ANALYST, 500, f"{node_a.title} vs {node_b.title}")

    response = await llm.generate(
        system="You are analyzing logical relationships between statements.",
        user=prompt,
        temperature=0.3,
        max_tokens=400,
    )

    call_mark = create_llm_call_mark(
        LLMTier.ANALYST,
        "contradiction_detection",
        prompt,
        response,
        (node_a.id, node_b.id),
    )
    budget.track(call_mark)
    await witness_store.save_mark(call_mark.to_mark())

    display_llm_call_complete(call_mark)

    return parse_contradiction_analysis(response.text)
```

#### 15.10.4 Synthesis Generation (Analyst)

```python
async def generate_synthesis(
    thesis: ZeroNode,
    antithesis: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ZeroNode:
    """
    Generate a synthesis node from contradicting nodes.

    Uses Analyst tier (sonnet) - creative synthesis.
    ~1500 tokens.
    """
    prompt = f"""Create a synthesis that resolves the tension between these two positions:

THESIS ({thesis.title}):
{thesis.content}

ANTITHESIS ({antithesis.title}):
{antithesis.content}

The synthesis should:
1. Acknowledge the valid core of each position
2. Identify the underlying assumption that creates the tension
3. Propose a higher-order perspective that encompasses both
4. Be actionable, not just philosophical

Provide:
- title: synthesis title
- content: the synthesis (2-3 paragraphs)
- resolution_type: "sublation" | "scope_limitation" | "context_dependency" | "false_dichotomy"
- preserved_from_thesis: what's kept
- preserved_from_antithesis: what's kept
- transcended: what's left behind

Format as JSON.
"""

    check = budget.check_budget(LLMTier.ANALYST, estimated_tokens=1500)
    if not check.allowed:
        raise BudgetExceededError(f"Synthesis requires ~1500 tokens, only {check.remaining} remaining")

    display_llm_call_start(
        "Synthesis Generation",
        LLMTier.ANALYST,
        1500,
        f"{thesis.title} ⊕ {antithesis.title}",
    )

    response = await llm.generate(
        system="You are a dialectical synthesizer creating higher-order resolutions.",
        user=prompt,
        temperature=0.6,  # Higher temperature for creativity
        max_tokens=1000,
    )

    call_mark = create_llm_call_mark(
        LLMTier.ANALYST,
        "synthesis_generation",
        prompt,
        response,
        (thesis.id, antithesis.id),
    )
    budget.track(call_mark)
    await witness_store.save_mark(call_mark.to_mark())

    display_llm_call_complete(call_mark)

    return parse_synthesis_node(response.text, thesis, antithesis)
```

### 15.11 Integration with DP Value Function

LLM calls can improve the constitutional reward function:

```python
class LLMAugmentedConstitution(Constitution):
    """Constitution with LLM-enhanced principle evaluation."""

    def __init__(self, llm: LLMClient, budget: TokenBudget):
        super().__init__()
        self.llm = llm
        self.budget = budget

        # Cache to avoid repeated LLM calls for same content
        self._evaluation_cache: dict[str, float] = {}

    async def evaluate_tasteful_async(
        self,
        node: ZeroNode,
        use_llm: bool = True,
    ) -> PrincipleScore:
        """
        Evaluate TASTEFUL principle with optional LLM enhancement.

        Falls back to heuristics if LLM budget exhausted.
        """
        # Try cache first
        cache_key = f"tasteful:{node.id}"
        if cache_key in self._evaluation_cache:
            return PrincipleScore(
                principle=Principle.TASTEFUL,
                score=self._evaluation_cache[cache_key],
                evidence="Cached evaluation",
                weight=1.0,
            )

        # Heuristic baseline
        heuristic_score = min(1.0, 500 / max(len(node.content), 1))

        if not use_llm:
            return PrincipleScore(
                principle=Principle.TASTEFUL,
                score=heuristic_score,
                evidence="Heuristic: length-based",
                weight=1.0,
            )

        # LLM enhancement (Scout tier)
        check = self.budget.check_budget(LLMTier.SCOUT, estimated_tokens=150)
        if not check.allowed:
            # Graceful degradation
            return PrincipleScore(
                principle=Principle.TASTEFUL,
                score=heuristic_score,
                evidence="Heuristic (LLM budget exhausted)",
                weight=1.0,
            )

        response = await self.llm.generate(
            system="Rate content tastfulness 0.0-1.0. Tasteful = clear purpose, minimal, justified.",
            user=f"Rate: {node.content[:300]}. Reply with just a number 0.0-1.0.",
            temperature=0.1,
            max_tokens=10,
        )

        try:
            score = float(response.text.strip())
            score = max(0.0, min(1.0, score))
        except ValueError:
            score = heuristic_score

        # Blend heuristic and LLM (LLM weighted higher)
        blended = 0.3 * heuristic_score + 0.7 * score
        self._evaluation_cache[cache_key] = blended

        return PrincipleScore(
            principle=Principle.TASTEFUL,
            score=blended,
            evidence=f"LLM: {score:.2f}, heuristic: {heuristic_score:.2f}",
            weight=1.0,
        )
```

### 15.12 CLI Integration

```bash
# View session status
kg zero-seed status
# Output:
# Session (standard): 45,200 / 500,000 tokens (9.0%)
# Weak spots: 2 warnings, 1 info (1 suppressed)
# Last analysis: 2 minutes ago

# Start long session (2M token budget)
kg zero-seed --session=long

# Analyze graph health (uses liberal budget for comprehensive analysis)
kg zero-seed health
kg zero-seed health --comprehensive  # Deep analysis

# Create node with full structure (minimal edits)
kg zero-seed add "My new insight about composability" --layer=3
# System generates: node + proof + edges, user reviews

# Suppress a category of suggestions
kg zero-seed suppress orphan_warnings

# View suppressed items
kg zero-seed suppressed

# Disable LLM for this session (pure heuristics)
kg zero-seed --no-llm

# Force Oracle tier for critical decision
kg zero-seed synthesize --tier=oracle "node-123" "node-456"
```

### 15.13 Summary: Liberal LLM for Radical UX

| Principle | Implementation |
|-----------|----------------|
| **Liberal Budgets** | 200k short, 500k standard, 2M long sessions |
| **Self-Awareness** | System proactively surfaces weak spots |
| **Minimal Edits** | User provides content, system builds complete structure |
| **Suppressible** | User can ignore suggestions by item or category |
| **Comprehensive Analysis** | Liberal tokens enable thorough graph health checks |
| **Auto-Fixable** | System can apply fixes automatically with user consent |

The LLM is an **empowering partner**, not a gatekeeper. With generous budgets, the system can:
- Analyze comprehensively without nickel-and-diming
- Surface issues proactively (user can ignore)
- Build complete structures from minimal input
- Auto-fix issues with user consent

**Philosophy Shift**: From "cost-conscious, user does work" to "generous budgets, system does work, user reviews."

> *"The system surfaces weakness. The user decides what matters. The proof IS witnessed."*

---

## Appendix A: Example Zero Seed (Minimal)

```yaml
nodes:
  - id: "axiom-001"
    path: "void.axiom.mirror-test"
    layer: 1
    kind: "Axiom"
    title: "The Mirror Test"
    content: "Does K-gent feel like me on my best day?"
    proof: null  # Axioms are unproven
    confidence: 1.0

  - id: "axiom-002"
    path: "void.axiom.tasteful-greater"
    layer: 1
    kind: "Axiom"
    title: "Tasteful > Feature-Complete"
    content: "Curation over accumulation. Quality over quantity."
    proof: null
    confidence: 1.0

  - id: "value-001"
    path: "void.value.composability"
    layer: 2
    kind: "Value"
    title: "Composability"
    content: "Agents are morphisms in a category; composition is primary."
    proof: null  # L2 is also unproven
    confidence: 1.0

  - id: "goal-001"
    path: "concept.goal.cultivate"
    layer: 3
    kind: "Goal"
    title: "Cultivate Zero Seed"
    content: "Grow the seed into a living garden of agency."
    proof:
      data: "Axioms exist. Values exist."
      warrant: "Grounded values enable meaningful goals."
      claim: "This goal will guide cultivation."
      qualifier: "definitely"
      tier: "SOMATIC"

edges:
  - source: "axiom-001"
    target: "value-001"
    kind: "GROUNDS"

  - source: "axiom-002"
    target: "value-001"
    kind: "GROUNDS"

  - source: "value-001"
    target: "goal-001"
    kind: "JUSTIFIES"
```

---

## Appendix B: AGENTESE Path Reference

| Path Pattern | Layer | Description |
|--------------|-------|-------------|
| `void.axiom.*` | L1 | Axiom nodes (irreducible beliefs) |
| `void.value.*` | L2 | Value nodes (principles, affinities) |
| `void.entropy.*` | - | Entropy pool operations |
| `void.random.*` | - | Random oracle |
| `void.gratitude.*` | - | Gratitude ledger |
| `concept.goal.*` | L3 | Goal nodes (dreams, plans) |
| `concept.spec.*` | L4 | Specification nodes |
| `concept.proof.*` | L4 | Proof structures |
| `world.action.*` | L5 | Execution nodes |
| `world.result.*` | L5 | Result/data nodes |
| `self.reflection.*` | L6 | Reflection nodes |
| `self.synthesis.*` | L6 | Synthesis nodes |
| `time.insight.*` | L7 | Insight nodes |
| `time.meta.*` | L7 | Meta-cognition nodes |

---

*"The seed is not the garden. The seed is the capacity for gardening."*

---

**Self-Validation Applied** (2025-12-24):
- ✅ Added Toulmin proof for this spec (Part VI §6.3)
- ✅ Added grounding chain (Part XII)
- ✅ Added prerequisites section
- ✅ Clarified void polymorphism as sum type (Part VII §7.1)
- ✅ Documented strange loop as feature (Part XIII)
- ✅ Marked node types as exemplars vs mandates (Part I)
- ✅ **Integrated DP-Native framework** (Part XIV) — Zero Seed as MetaDP
- ✅ **Added LLM-Augmented Intelligence** (Part XV) — Principled, witnessed, tiered

See: `brainstorming/zero-seed-self-validation/SYNTHESIS.md`

**Next Steps (Implementation)**:
1. Implement `ZeroNode` and `ZeroEdge` data models in `services/zero_seed/`
2. Create `ZeroSeedConstitution` extending `dp/core/constitution.py`
3. Implement `AxiomDiscoveryMetaDP` for three-stage discovery
4. Add `TelescopeValueAgent` for value-guided navigation
5. Bridge PolicyTrace ↔ Toulmin Proof with `dp/witness/bridge.py`
6. Implement `LLMCallMark` and `TokenBudget` for witnessed LLM calls
7. Add LLM operations: axiom mining, proof validation, contradiction detection
8. Implement retroactive witnessing for bootstrap
9. Run Mirror Test with Kent on revised spec

**Related Specs**:
- `spec/protocols/witness-primitives.md` — Mark and Crystal structures
- `spec/protocols/k-block.md` — K-Block isolation
- `spec/protocols/typed-hypergraph.md` — Hypergraph model
- `spec/principles/CONSTITUTION.md` — The 7+7 principles
- `spec/theory/dp-native-kgents.md` — **DP-Agent Isomorphism** ⭐
- `spec/theory/agent-dp.md` — Agent Space as Dynamic Programming
- `impl/claude/services/categorical/dp_bridge.py` — DP bridge implementation
- `impl/claude/dp/core/constitution.py` — Constitution as reward function
- `impl/claude/runtime/cli.py` — **ClaudeCLIRuntime** for LLM calls ⭐
- `impl/claude/agents/k/llm.py` — LLMClient abstraction (haiku/sonnet/opus)
- `brainstorming/zero-seed-self-validation/` — Self-validation analysis
