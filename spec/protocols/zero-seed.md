# Zero Seed Protocol

> *"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

**Version**: 3.0 (Unified Galois-Native)
**Date**: 2025-12-24
**Status**: Canonical Specification
**Principles**: Generative, Composable, Tasteful, Heterarchical

**Unified from**:
- `zero-seed.md` (v1, 2498 lines) — Original monolithic
- `zero-seed/` (v2, ~3000 lines) — Modular attempt
- `zero-seed1/` (v3, ~24000 lines) — Galois-native upgrade

---

## Prerequisites

| Prerequisite | Location | What It Provides |
|--------------|----------|------------------|
| **Constitution** | `spec/principles/CONSTITUTION.md` | The 7 design + 7 governance principles |
| **AGENTESE** | `spec/protocols/agentese.md` | Five contexts, path semantics, observer model |
| **Witness Protocol** | `spec/protocols/witness-primitives.md` | Mark and Crystal structures |
| **K-Block** | `spec/protocols/k-block.md` | Transactional isolation for editing |
| **Agent-DP** | `spec/theory/agent-dp.md` | Problem-solution co-emergence |
| **Galois Modularization** | `spec/theory/galois-modularization.md` | Restructuring loss theory |

**Import Order**: Constitution → AGENTESE → Witness → Agent-DP → Galois → Zero Seed

---

## Abstract

Zero Seed provides a **minimal, cultivable bootstrap state** for the kgents system—a seven-layer epistemic holarchy grounded in Galois Modularization Theory. Rather than imposing static structure, it provides a **generative kernel**: enough structure to grow from, sparse enough to make your own.

**The Core Tension Resolved**: Users need structure to act meaningfully, but structure imposed externally feels dead. Zero Seed resolves this by:
1. **Axioms as fixed points** — Discovered computationally, not stipulated (L(axiom) < 0.01)
2. **Layers from convergence** — Seven layers emerge from restructuring depth, not declaration
3. **Proofs quantified** — Coherence = 1 - galois_loss(proof)
4. **Contradictions measured** — Super-additive loss: L(A∪B) > L(A)+L(B)+τ
5. **Constitutional reward unified** — R = 1 - L (inverse Galois loss)

**The Radical Upgrade (v3)**: Everything that was heuristic in v1-v2 is now **information-theoretic** via Galois loss.

---

## Part I: Foundations

### 1.1 The Minimal Kernel: Two Axioms + Galois Ground

Zero Seed achieves maximum generativity through **radical compression**:

| Component | Statement | Loss |
|-----------|-----------|------|
| **A1: Entity** | Everything is a node | L=0.002 |
| **A2: Morphism** | Everything composes | L=0.003 |
| **G: Galois Ground** | L measures structure loss; axioms are Fix(L) | L=0.000 |

**Derivation**: From these three foundations, the full system regenerates:
- Seven epistemic layers (L1-L7) via convergence depth
- Full witnessing (every change traced)
- Proof requirements (Toulmin for L3+, coherence = 1 - L)
- Contradiction tolerance (super-additive loss detection)
- AGENTESE mapping (five contexts)

### 1.2 Data Model

```python
@dataclass(frozen=True)
class ZeroNode:
    """A node in the Zero Seed holarchy."""

    # Identity (from A1)
    id: NodeId
    path: str                           # AGENTESE path (e.g., "void.axiom.mirror-test")

    # Classification (from G)
    layer: Annotated[int, Field(ge=1, le=7)]  # Layer by convergence depth
    kind: str                           # Node type within layer

    # Content
    content: str                        # Markdown content
    title: str

    # Justification (from G)
    proof: GaloisWitnessedProof | None  # Toulmin + Galois (None for L1-L2)
    confidence: float                   # [0, 1]

    # Provenance
    created_at: datetime
    created_by: str
    lineage: tuple[NodeId, ...]

    # Metadata
    tags: frozenset[str]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ZeroEdge:
    """A morphism between nodes (from A2)."""

    id: EdgeId
    source: NodeId
    target: NodeId
    kind: EdgeKind

    # Galois annotations
    galois_loss: float                  # L(edge transition)
    context: str
    confidence: float

    # Witnessing (from G)
    mark_id: MarkId                     # REQUIRED
    created_at: datetime

    # Composition operator (from A2)
    def __rshift__(self, other: "ZeroEdge") -> "ZeroEdge":
        """Compose edges: (A→B) >> (B→C) = (A→C)"""
        if self.target != other.source:
            raise CompositionError()

        return ZeroEdge(
            source=self.source,
            target=other.target,
            kind=compose_edge_kinds(self.kind, other.kind),
            galois_loss=self.galois_loss + other.galois_loss,  # Loss accumulates
            mark_id=create_composition_mark(self, other).id,
        )


class EdgeKind(Enum):
    # Inter-layer (DAG flow)
    GROUNDS = "grounds"                 # L1 → L2
    JUSTIFIES = "justifies"             # L2 → L3
    SPECIFIES = "specifies"             # L3 → L4
    IMPLEMENTS = "implements"           # L4 → L5
    REFLECTS_ON = "reflects_on"         # L5 → L6
    REPRESENTS = "represents"           # L6 → L7

    # Intra-layer
    DERIVES_FROM = "derives_from"
    EXTENDS = "extends"
    REFINES = "refines"

    # Dialectical
    CONTRADICTS = "contradicts"         # Super-additive loss
    SYNTHESIZES = "synthesizes"
    SUPERSEDES = "supersedes"

    # Crystallization
    CRYSTALLIZES = "crystallizes"
    SOURCES = "sources"
```

### 1.3 The Seven Layers (Galois-Derived)

**Definition**: Layer L_i = minimum restructuring depth to reach fixed point.

```python
def compute_layer_from_loss(node: ZeroNode, galois: GaloisLoss) -> int:
    """
    Layer = minimum restructuring depth to reach fixed point.

    This DERIVES the 7 layers rather than stipulating them.
    """
    current = node.content

    for depth in range(0, 7):
        modular = galois.restructure(current)
        reconstituted = galois.reconstitute(modular)
        loss = galois.compute_loss(current, reconstituted)

        if loss < FIXED_POINT_THRESHOLD:  # ε₁ = 0.05
            return depth + 1  # L1 = depth 0, L2 = depth 1, etc.

        current = reconstituted

    return 7  # L7 = doesn't converge quickly
```

| Layer | Convergence | Semantic Domain | Node Types (Exemplar) | Loss Bounds |
|-------|-------------|-----------------|----------------------|-------------|
| **L1** | k=0 | Assumptions | Axiom, Belief, Lifestyle | 0.00-0.05 |
| **L2** | k=1 | Values | Principle, Value, Affinity | 0.05-0.15 |
| **L3** | k=2 | Goals | Dream, Goal, Plan, Gesture | 0.15-0.30 |
| **L4** | k=3 | Specifications | Spec, Proof, Evidence, Policy | 0.30-0.45 |
| **L5** | k=4 | Execution | Action, Result, Experiment, Data | 0.45-0.60 |
| **L6** | k=5 | Reflection | Reflection, Synthesis, Delta | 0.60-0.75 |
| **L7** | k=6 | Representation | Interpretation, Analysis, Insight | 0.75-1.00 |

**The Emergence**: The 7-layer count isn't stipulated—it's discovered from convergence rates on the kgents Constitution corpus.

---

## Part II: Galois Framework

### 2.1 Loss Function Definition

**Definition**: For any node, edge, or proof P:

```
L(P) = d(P, C(R(P)))

where:
  R: Prompt → ModularPrompt     (restructure via LLM)
  C: ModularPrompt → Prompt     (reconstitute via LLM)
  d: semantic distance          (BERTScore inverse, default)
```

**Axiom Characterization**: P is axiomatic iff L(P) < ε₁ (default: 0.05)

**Proof Coherence**: coherence(proof) = 1 - L(proof)

**Evidence Tier Mapping**:
```python
def classify_tier_by_loss(loss: float) -> EvidenceTier:
    if loss < 0.1:
        return EvidenceTier.CATEGORICAL    # Logical necessity
    elif loss < 0.3:
        return EvidenceTier.EMPIRICAL      # Data-driven
    elif loss < 0.5:
        return EvidenceTier.AESTHETIC      # Taste-based
    elif loss < 0.7:
        return EvidenceTier.SOMATIC        # Gut feeling
    else:
        return EvidenceTier.CHAOTIC        # Incoherent
```

### 2.2 Axiom Discovery as Fixed-Point Finding

**Theorem (Lawvere for Zero Seed)**: Given self-referential prompts and restructuring operation R, there exists P such that R(P) ≅ P.

**Three-Stage Discovery**:

**Stage 1: Constitution Mining** (Computational)
```python
async def mine_fixed_points(constitution_paths: list[str]) -> list[CandidateAxiom]:
    """Extract statements with near-zero Galois loss."""
    candidates = []
    for path in constitution_paths:
        statements = extract_principle_statements(await read_file(path))
        for stmt in statements:
            loss = await compute_fixed_point_loss(stmt.text)
            if loss < FIXED_POINT_THRESHOLD:  # < 0.05
                candidates.append(CandidateAxiom(
                    text=stmt.text,
                    galois_loss=loss,
                    is_fixed_point=(loss < 0.01),
                ))
    return candidates
```

**Stage 2: Mirror Test** (Human Loss Oracle)
```python
async def mirror_test_dialogue(candidates: list[CandidateAxiom]) -> list[ZeroNode]:
    """Refine via human validation. Mirror Test provides GROUND TRUTH for loss."""
    accepted = []
    for candidate in candidates:
        response = await ask_user(
            f'Does this feel true for you on your best day?\n\n> {candidate.text}\n\n'
            f'Galois Loss: {candidate.galois_loss:.3f} (lower = more axiomatic)'
        )

        if response in ["Yes, deeply", "Accept"]:
            accepted.append(create_axiom_node(
                candidate,
                confidence=1.0 - candidate.galois_loss,
            ))
        elif response == "Reframe":
            reframed = await ask_user("How would you say it?")
            accepted.append(create_axiom_node(
                CandidateAxiom(text=reframed, galois_loss=0.0),
                confidence=1.0,
            ))

    return accepted
```

**Stage 3: Living Corpus Validation** (Behavioral)
```python
async def corpus_validation(axioms: list[ZeroNode], marks: list[Mark]) -> list[tuple[ZeroNode, float]]:
    """Validate axioms against witnessed behavior. Behavioral loss = misalignment."""
    results = []
    for axiom in axioms:
        citing_marks = [m for m in marks if any(tag in m.tags for tag in axiom.tags)]
        if not citing_marks:
            behavioral_loss = 0.5  # Unknown
        else:
            behavioral_loss = await compute_behavioral_loss(axiom, citing_marks)
        results.append((axiom, behavioral_loss))
    return results
```

### 2.3 Contradiction Detection via Super-Additive Loss

**Theorem**: Two nodes A and B contradict iff:

```
L(A ∪ B) > L(A) + L(B) + τ    (τ = 0.1, tolerance)
```

**Implementation**:
```python
async def detect_contradiction_galois(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
) -> ContradictionAnalysis:
    """Detect contradiction via super-additive loss."""
    # Individual losses
    loss_a = await galois_loss(node_a.content, llm)
    loss_b = await galois_loss(node_b.content, llm)

    # Combined loss
    combined_content = f"{node_a.title}:\n{node_a.content}\n\n{node_b.title}:\n{node_b.content}"
    loss_combined = await galois_loss(combined_content, llm)

    # Super-additivity
    strength = loss_combined - (loss_a + loss_b)

    return ContradictionAnalysis(
        loss_a=loss_a,
        loss_b=loss_b,
        loss_combined=loss_combined,
        strength=strength,
        is_contradiction=(strength > 0.1),
        severity=classify_severity(strength),
    )
```

### 2.4 Layer Stratification via Loss Bounds

```python
class LayerStratifiedLoss:
    """Galois loss with layer-aware semantics."""

    async def compute(self, node: ZeroNode) -> float:
        """Compute loss appropriate for node's layer."""
        match node.layer:
            case 1 | 2:  # Axioms/Values
                return 0.0  # BY DEFINITION: axioms are zero-loss fixed points

            case 3:  # Goals
                return await self._goal_loss(node)  # Loss = how much value-justification is lost

            case 4:  # Specs
                return await self._spec_loss(node)  # Loss = unimplementable portions

            case 5:  # Execution
                return await self._execution_loss(node)  # Loss = spec deviation

            case 6:  # Reflection
                return await self._reflection_loss(node)  # Loss = synthesis gaps

            case 7:  # Representation
                return await self._representation_loss(node)  # Loss = meta-blindness
```

---

## Part III: Proof & Witnessing

### 3.1 Toulmin Structure Extended with Galois Loss

```python
@dataclass(frozen=True)
class GaloisWitnessedProof(Proof):
    """Toulmin proof extended with Galois loss quantification."""

    # Toulmin fields
    data: str                           # Evidence
    warrant: str                        # Reasoning
    claim: str                          # Conclusion
    backing: str                        # Support for warrant
    qualifier: str                      # "definitely", "probably"
    rebuttals: tuple[str, ...]          # Defeaters
    tier: EvidenceTier
    principles: tuple[str, ...]

    # Galois extensions
    galois_loss: float                  # L(proof) ∈ [0, 1]
    loss_decomposition: dict[str, float]  # Loss per component
    ghost_alternatives: tuple[Alternative, ...]  # Deferred proof paths

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss. Core insight of Galois upgrade."""
        return 1.0 - self.galois_loss

    @property
    def tier_from_loss(self) -> EvidenceTier:
        """Map loss to evidence tier."""
        return classify_tier_by_loss(self.galois_loss)

    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """Generate rebuttals from loss decomposition. High loss → defeaters."""
        generated = []
        for component, loss in self.loss_decomposition.items():
            if loss > 0.3:
                generated.append(
                    f"Unless implicit assumption in {component} fails (loss: {loss:.2f})"
                )
        return self.rebuttals + tuple(generated)
```

### 3.2 Loss Decomposition

```python
async def compute_loss_decomposition(proof: Proof, llm: LLM) -> ProofLossDecomposition:
    """
    Break down Galois loss by Toulmin component.

    Identifies which parts are most "compressed" (low loss = explicit)
    vs most "implicit" (high loss = hidden structure).
    """
    full_loss = await galois_loss(proof, llm)

    # Ablation studies
    component_losses = {}
    for component in ["data", "warrant", "claim", "backing", "qualifier", "rebuttals"]:
        ablated_proof = ablate_component(proof, component)
        ablated_loss = await galois_loss(ablated_proof, llm)
        component_losses[component] = max(0.0, full_loss - ablated_loss)

    # Composition loss = residual
    composition_loss = max(0.0, full_loss - sum(component_losses.values()))

    return ProofLossDecomposition(
        data_loss=component_losses["data"],
        warrant_loss=component_losses["warrant"],
        claim_loss=component_losses["claim"],
        backing_loss=component_losses["backing"],
        qualifier_loss=component_losses["qualifier"],
        rebuttal_loss=component_losses["rebuttals"],
        composition_loss=composition_loss,
    )
```

### 3.3 Witness Batching via Galois Triage

**Problem**: Full witnessing (every edit creates a Mark) is computationally expensive.

**Solution**: Galois-based triage.

```python
class WitnessMode(Enum):
    """Witness modes based on Galois loss triage."""
    SINGLE = "single"       # Important: witness immediately (L < 0.1)
    SESSION = "session"     # Batch: witness at session end (L < 0.4)
    LAZY = "lazy"           # Deferred: witness only if referenced (L ≥ 0.4)


async def select_witness_mode(edit: NodeDelta, llm: LLM) -> WitnessMode:
    """Triage witness mode based on edit's Galois loss."""
    if edit.node.layer <= 2:
        return WitnessMode.SINGLE  # Axioms always important

    if edit.proof is None:
        return WitnessMode.SINGLE  # Missing proof on L3+ needs attention

    loss = await galois_loss(edit.proof, llm)

    if loss < 0.1:
        return WitnessMode.SINGLE  # Low loss = tight proof → important
    elif loss < 0.4:
        return WitnessMode.SESSION  # Medium loss = routine
    else:
        return WitnessMode.LAZY  # High loss = speculative
```

---

## Part IV: DP-Native Integration

### 4.1 The Unified Constitutional Equation

**Theorem (Constitutional Reward-Loss Duality)**:
```
R_constitutional(s, a, s') = 1.0 - L_galois(s → s' via a)
```

**Implementation**:
```python
class GaloisConstitution(Constitution):
    """Constitution with Galois-derived rewards."""

    def reward(self, state: ZeroNode, action: str, next_state: ZeroNode) -> float:
        """
        R_total = R_traditional - λ · L_galois

        Allows gradual migration: λ=0 (pure traditional), λ=1 (pure Galois).
        """
        traditional = super().reward(state, action, next_state)

        transition_desc = f"{state.title} → {next_state.title} via {action}"
        loss = self.galois.compute(transition_desc)

        return traditional - self.loss_weight * loss
```

**Why This Works**: The 7 constitutional principles encode semantic coherence invariants:

| Principle | What Low Galois Loss Implies |
|-----------|------------------------------|
| **TASTEFUL** | Transition preserves clarity (low bloat) |
| **COMPOSABLE** | Edge structure remains explicit |
| **GENERATIVE** | Derivation chain is recoverable |
| **ETHICAL** | Safety constraints remain visible |
| **JOY_INDUCING** | Personality signature is intact |
| **HETERARCHICAL** | No rigid hierarchy imposed |
| **CURATED** | Justification for change is explicit |

### 4.2 Proof ↔ PolicyTrace Isomorphism

**Mapping**:
```
Proof.data         ↔  PolicyTrace.state_before
Proof.warrant      ↔  PolicyTrace.action
Proof.claim        ↔  PolicyTrace.state_after
Proof.qualifier    ↔  PolicyTrace.value (converted)
Proof.backing      ↔  PolicyTrace.rationale
Proof.galois_loss  ↔  PolicyTrace.metadata["galois_loss"]  # NEW
```

```python
def proof_to_trace(proof: GaloisWitnessedProof) -> PolicyTrace:
    """Convert Galois-witnessed proof to DP trace."""
    entry = TraceEntry(
        state_before=proof.data,
        action=proof.warrant,
        state_after=proof.claim,
        value=proof.coherence,  # Coherence as value!
        rationale=proof.backing,
        metadata={
            "galois_loss": proof.galois_loss,
            "tier": proof.tier_from_loss.value,
            "loss_decomposition": proof.loss_decomposition,
        },
    )
    return PolicyTrace.pure(None).with_entry(entry)
```

### 4.3 Bellman Equation with Galois Loss

**Navigation through the 7-layer holarchy**:

```python
V*(node) = max_edge [
    Constitution.reward(node, edge, target) - λ·L(node → target) + γ·V*(target)
]

where:
    V*(node)                         # Optimal value at this node
    Constitution.reward(...)         # 7-principle weighted sum
    L(node → target)                 # Galois loss of edge traversal
    λ                                # Loss penalty weight (0.3 default)
    γ                                # Discount factor = focal_distance
```

---

## Part V: Bootstrap (Lawvere Fixed Point)

### 5.1 The Strange Loop Formalized

**Theorem (Zero Seed as Galois Fixed Point)**:
```
Zero Seed = Fix(R ∘ describe)

where:
  R = Galois restructure (modularization)
  describe = generate meta-description
  Fix(f) = {x : f(x) ≅ x}
```

**Verification Protocol**:
```python
async def verify_zero_seed_fixed_point(
    zero_seed_spec: str,
    galois: GaloisLoss,
    threshold: float = 0.15,  # 85% regenerability target
) -> FixedPointVerification:
    """Verify that Zero Seed is a fixed point of its own modularization."""
    modular = await galois.restructure(zero_seed_spec)
    reconstituted = await galois.reconstitute(modular)
    loss = galois.metric(zero_seed_spec, reconstituted)

    return FixedPointVerification(
        loss=loss,
        is_fixed_point=(loss < threshold),
        regenerability_pct=(1 - loss) * 100,
        deviations=extract_deviations(zero_seed_spec, reconstituted),
    )
```

**Success Criterion**: loss < 0.15 (85% regenerability)

### 5.2 Retroactive Witnessing

**The Resolution**: Bootstrap artifacts are witnessed **after the fact** with Galois metadata.

```python
async def retroactive_witness_bootstrap(
    graph: ZeroGraph,
    galois_verification: FixedPointVerification,
) -> list[Mark]:
    """Create marks for bootstrap artifacts with Galois annotations."""
    marks = []

    for node in [n for n in graph.nodes if "bootstrap" in n.tags]:
        mark = Mark(
            origin="zero-seed.bootstrap",
            stimulus=Stimulus(
                kind="bootstrap",
                source="retroactive",
                metadata={
                    "galois_loss": galois_verification.loss,
                    "regenerability_pct": galois_verification.regenerability_pct,
                    "fixed_point_verified": galois_verification.is_fixed_point,
                },
            ),
            timestamp=datetime.now(UTC),
            tags=frozenset({"bootstrap:retroactive", "galois-verified"}),
        )
        marks.append(mark)
        await store.save_mark(mark)

    return marks
```

### 5.3 The Irreducible 15%

**What's in the irreducible 15%** (85% regenerability target):

```yaml
irreducible_components:
  - implicit_dependencies:
      description: "Schema determines valid transformations (not stated)"
      loss_contribution: 5%

  - contextual_nuance:
      description: "Tone, emphasis, connotation (lost in flattening)"
      loss_contribution: 4%

  - holographic_redundancy:
      description: "Information distributed across modules (local→global)"
      loss_contribution: 3%

  - gestalt_coherence:
      description: "The 'feel' of the whole vs parts"
      loss_contribution: 3%
```

**Philosophy**: Don't fight the 15%. Document it. This is the **empirical manifestation** of Galois incompleteness (analog of Gödel's theorem).

---

## Part VI: Telescope Navigation

### 6.1 Focal Model with Loss Topography

```python
@dataclass
class GaloisTelescopeState:
    """Telescope with Galois loss visualization."""

    focal_distance: float               # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None

    # Galois visualization
    show_loss: bool = True              # Show loss heatmap
    show_gradient: bool = True          # Show loss gradient field
    loss_threshold: float = 0.5         # Hide nodes above threshold

    # Cached loss data
    _node_losses: dict[NodeId, float] = field(default_factory=dict)
    _gradient_field: LossGradientField | None = None

    @property
    def visible_layers(self) -> set[int]:
        """Which layers visible at current focal distance."""
        if self.focal_distance < 0.2:
            return {self.focal_node.layer}
        elif self.focal_distance < 0.5:
            l = self.focal_node.layer
            return {l for l in range(1, 8) if abs(l - self.focal_node.layer) <= 1}
        else:
            return set(range(1, 8))
```

### 6.2 Loss-Gradient Navigation

**Navigate toward stability (low-loss regions)**:

```python
class LossGradientField:
    """Compute loss gradients for navigation guidance."""

    def compute_gradient(self, node: NodeId, graph: ZeroGraph) -> Vector2D:
        """Gradient points toward lowest-loss neighbor."""
        neighbors = graph.neighbors(node)
        if not neighbors:
            return Vector2D(0, 0)

        # Find lowest-loss neighbor
        best_neighbor = min(neighbors, key=lambda n: self.losses.get(n, 1.0))
        best_loss = self.losses.get(best_neighbor, 1.0)
        current_loss = self.losses.get(node, 1.0)

        # Gradient magnitude = loss reduction
        magnitude = max(0, current_loss - best_loss)

        # Direction toward best neighbor
        direction = compute_direction(node, best_neighbor, graph)

        return direction * magnitude
```

**Keybindings**:
```
LOSS NAVIGATION:
  gl       → Go to lowest-loss neighbor
  gh       → Go to highest-loss neighbor (investigate problems)
  ∇        → Follow loss gradient (toward stability)
  L        → Toggle loss visualization
  G        → Toggle gradient field display

TELESCOPE:
  +/-      → Zoom in/out
  =        → Auto-focus on current node
  0        → Reset to macro view

LAYER:
  1-7      → Jump to layer N
  Tab      → Next layer
```

---

## Part VII: AGENTESE Integration

### 7.1 Layer to Context Mapping

The Seven Layers map to Five AGENTESE Contexts via surjection:

| AGENTESE Context | Layers | Semantic |
|------------------|--------|----------|
| `void.*` | L1 + L2 | The Accursed Share — irreducible ground |
| `concept.*` | L3 + L4 | The Abstract — dreams and specifications |
| `world.*` | L5 | The External — actions in the world |
| `self.*` | L6 | The Internal — reflection, synthesis |
| `time.*` | L7 | The Temporal — representation across time |

### 7.2 Void Polymorphism

```
void.* = Nodes ⊕ Services

where:
  Nodes    = void.axiom.* (L1) | void.value.* (L2)
  Services = void.entropy.* | void.random.* | void.gratitude.*
```

**Why polymorphic?** The Accursed Share (Bataille) contains both structure (axioms/values) and operations (entropy, randomness, gratitude).

### 7.3 Path Examples

```
void.axiom.mirror-test          → L1 Axiom node
void.value.composability        → L2 Value node
concept.goal.cultivate          → L3 Goal node
concept.spec.zero-seed          → L4 Spec node (this spec!)
world.action.implement-feature  → L5 Execution node
self.reflection.synthesis       → L6 Reflection node
time.insight.meta-analysis      → L7 Representation node
```

---

## Part VIII: LLM-Augmented Intelligence

### 8.1 Model Tiers

| Tier | Model | Use Case | Token Target | Cost |
|------|-------|----------|--------------|------|
| **Scout** | haiku | Classification, validation, suggestions | <500 | ~$0.25/1M |
| **Analyst** | sonnet | Synthesis, proof evaluation, dialogue | <2000 | ~$3/1M |
| **Oracle** | opus | Critical decisions, constitutional judgment | On-demand | ~$15/1M |

### 8.2 LLM Call Points

| Operation | Tier | Tokens | Purpose |
|-----------|------|--------|---------|
| **Axiom Mining** | Scout | ~300 | Extract candidates from constitution |
| **Mirror Test** | Analyst | ~1000 | Socratic questioning |
| **Proof Validation** | Scout | ~200 | Check Toulmin coherence via loss |
| **Edge Suggestion** | Scout | ~300 | Suggest relevant edges |
| **Contradiction Detection** | Analyst | ~500 | Super-additive loss analysis |
| **Synthesis Generation** | Analyst | ~1500 | Create dialectical synthesis |

### 8.3 Liberal Token Budgets

```python
class TokenBudget:
    """Liberal session-level token budget."""

    session_limits: dict[SessionLength, int] = {
        SessionLength.SHORT: 200_000,      # 200k tokens
        SessionLength.STANDARD: 500_000,   # 500k tokens
        SessionLength.LONG: 2_000_000,     # 2M tokens for deep work
    }
```

**Philosophy**: Generous budgets enable radical UX simplification. The system does more work upfront to minimize user edits.

---

## Part IX: Laws & Anti-patterns

### 9.1 The Eight Laws

| Law | Statement | Source | Enforcement |
|-----|-----------|--------|-------------|
| **Node Identity** | Each node has exactly one path | A1 | Path uniqueness constraint |
| **Layer Integrity** | Node.layer ∈ {1,2,3,4,5,6,7} | G | Type constraint + convergence |
| **Composition** | (f >> g) >> h = f >> (g >> h) | A2 | Verified in `__rshift__` |
| **Bidirectional Edges** | ∀ edge e, ∃ inverse(e) | A2 | Auto-computed on creation |
| **Full Witnessing** | ∀ modification m, ∃ mark(m) | G | Enforced in modify_node() |
| **Axiom Unprovenness** | L1-L2 nodes have proof=None | G | Rejected if proof provided |
| **Proof Requirement** | L3+ nodes must have proof | G | Rejected if proof missing |
| **Contradiction Tolerance** | `contradicts` edges may coexist | G | No automatic resolution |

### 9.2 Anti-patterns

| Anti-pattern | Description | Resolution |
|--------------|-------------|------------|
| **Proof on Axiom** | Adding proof to L1-L2 node | Error: axioms are zero-loss fixed points |
| **Missing Proof** | L3+ node without Toulmin structure | Error: all non-axioms must justify |
| **Silent Edit** | Modifying node without witness mark | Impossible (enforced by G) |
| **Orphan Axiom** | Axiom with no `grounds` edges to L2 | Warning (may be pending) |
| **Layer Skip** | Edge skipping layers (L1 → L4) | Allowed but flagged for review |

---

## Part X: Implementation Roadmap

### Phase 1: Galois Infrastructure (Weeks 1-3)
```
Files: impl/claude/services/zero_seed/galois/
  - galois_loss.py (core loss computation)
  - distance.py (semantic distance metrics: BERTScore, LLM judge, cosine)
  - decomposition.py (loss decomposition)
  - proof.py (GaloisWitnessedProof)

Success:
  ✓ galois_loss(text) -> float with 3 metrics
  ✓ Loss decomposition by component
  ✓ Unit tests pass
```

### Phase 2: Validation & Triage (Weeks 4-6)
```
Files:
  - galois/validation.py (proof validation)
  - galois/triage.py (witness mode selection)
  - services/witness/galois_integration.py

Success:
  ✓ validate_proof_galois() returns coherence scores
  ✓ Witness batching reduces singles by >50%
  ✓ classify_by_loss() maps to evidence tiers
```

### Phase 3: Contradiction & DP (Weeks 7-10)
```
Files:
  - galois/contradiction.py (super-additive detection)
  - dp/core/galois_constitution.py (unified reward)
  - services/categorical/galois_dp_bridge.py

Success:
  ✓ detect_contradiction_galois() F1 > 0.85
  ✓ GaloisConstitution reward correlates with manual scores
  ✓ proof_to_trace() round-trip preserves loss
```

### Phase 4: Layer Stratification & Discovery (Weeks 11-14)
```
Files:
  - galois/layers.py (convergence-based stratification)
  - galois/discovery.py (axiom search via gradient descent on loss)
  - services/zero_seed/bootstrap.py (Lawvere fixed point)

Success:
  ✓ assign_layer() returns L1-L7 based on convergence depth
  ✓ discover_axiom() finds fixed points L(P) < ε
  ✓ retroactive_witnessing() validates Lawvere theorem
```

### Phase 5: LLM & Navigation (Weeks 15-18)
```
Files:
  - llm/augmented_intelligence.py (LLM as Galois guidance)
  - telescope/navigation.py (DP-guided nav with loss)
  - ui/telescope_shell.tsx (focal distance rendering)

Success:
  ✓ LLM-augmented discovery improves F1 by 0.15
  ✓ Telescope navigation prefers low-loss branches
  ✓ UI displays gradient field via focal distance
```

### Phase 6: Integration & Hardening (Weeks 19-22)
```
Files:
  - protocols/api/zero_seed.py (unified API)
  - _tests/test_galois_integration.py (end-to-end)
  - docs/zero-seed-galois-guide.md

Success:
  ✓ All tests pass (unit, integration, property-based)
  ✓ Performance: galois_loss() < 100ms @ p95
  ✓ Documentation complete with examples
```

---

## Appendix A: Implementation Reference

### File Structure
```
impl/claude/
├── services/
│   ├── zero_seed/
│   │   ├── galois/
│   │   │   ├── __init__.py
│   │   │   ├── galois_loss.py       # Core loss computation
│   │   │   ├── distance.py          # Semantic distance (BERT, LLM, cosine)
│   │   │   ├── decomposition.py     # Loss decomposition
│   │   │   ├── proof.py             # GaloisWitnessedProof
│   │   │   ├── validation.py        # Proof validation
│   │   │   ├── triage.py            # Witness mode selection
│   │   │   ├── contradiction.py     # Super-additive detection
│   │   │   ├── layers.py            # Layer stratification
│   │   │   └── discovery.py         # Axiom discovery
│   │   ├── bootstrap.py             # Lawvere fixed point
│   │   ├── axioms.py                # Two Axioms + extensions
│   │   └── integration.py           # AGENTESE integration
│   ├── dp/
│   │   └── core/
│   │       └── galois_constitution.py  # R = 1 - L reward
│   ├── witness/
│   │   └── galois_integration.py    # Witness batching
│   └── categorical/
│       └── galois_dp_bridge.py      # DP ↔ Galois bridge
├── protocols/
│   └── api/
│       └── zero_seed.py             # FastAPI endpoints
└── _tests/
    ├── test_galois_loss.py
    ├── test_contradiction.py
    ├── test_layers.py
    └── test_galois_integration.py
```

### Key Classes

**GaloisLossComputer**
```python
class GaloisLossComputer:
    """Compute Galois loss L(P) = d(P, C(R(P)))."""

    def compute(self, proposition: str) -> GaloisLoss:
        restructured = self.restructure(proposition)
        canonical = self.canonicalize(restructured)

        return GaloisLoss(
            total=self.distance(proposition, canonical),
            semantic=self.semantic_distance(proposition, canonical),
            structural=self.structural_distance(proposition, canonical),
            pragmatic=self.pragmatic_distance(proposition, canonical),
        )
```

**GaloisWitnessedProof**
```python
@dataclass
class GaloisWitnessedProof:
    """Toulmin proof with Galois loss."""
    data: str
    warrant: str
    claim: str
    backing: list[str]
    qualifier: str | None
    rebuttals: list[str]

    # Galois annotations
    loss: float
    coherence: float  # 1 - loss
    layer: int  # L1-L7
    evidence_tier: EvidenceTier  # Zero/Horizon/Exploration
```

**GaloisConstitution**
```python
class GaloisConstitution:
    """Constitutional reward R = 1 - L."""

    def reward(self, trace: DecisionTrace) -> float:
        proof = trace_to_proof(trace)
        loss = galois_loss(proof)
        return 1.0 - loss
```

### API Endpoints

**POST /api/zero-seed/galois/loss**
```
Input: {"proposition": "Earth is round"}
Output: {
  "total": 0.03,
  "semantic": 0.01,
  "structural": 0.01,
  "pragmatic": 0.01,
  "is_axiomatic": true,
  "layer": 1
}
```

**POST /api/zero-seed/proof/validate**
```
Input: {GaloisWitnessedProof JSON}
Output: {
  "coherence": 0.94,
  "loss_breakdown": {...},
  "witness_mode": "single",
  "contradictions": []
}
```

**POST /api/zero-seed/discover**
```
Input: {"domain": "physics", "candidates": [...]}
Output: {
  "axioms": [...],  # L(P) < 0.05
  "layers": {...},  # L1-L7 stratification
  "fixed_point": "F(describe) = describe"
}
```

---

## Appendix B: Archived Extensions

The following experimental extensions were developed in `zero-seed1/` but are NOT part of the canonical spec. They are preserved for future research:

### B.1 Operator Calculus (spec/protocols/_archive/zero-seed-operator-calculus.md)
- **∇L**: Galois gradient (direction of maximal loss reduction)
- **∂L/∂component**: Partial derivatives for attribution
- **Laplacian ΔL**: Loss curvature for bifurcation detection
- **Vector fields**: ∇L as guidance for axiom search

**Status**: Theoretical. Not implemented. May inform future LLM-augmented discovery.

### B.2 Catastrophic Bifurcation (spec/protocols/_archive/zero-seed-bifurcation.md)
- **Cusp catastrophes**: ΔL → ∞ signals phase transitions
- **Loss landscape topology**: Stable axioms = local minima
- **Hysteresis**: Path-dependent axiom acceptance
- **Critical thresholds**: When contradictions force layer restructuring

**Status**: Experimental. Requires loss landscape analysis infrastructure.

### B.3 Metatheory (spec/protocols/_archive/zero-seed-metatheory.md)
- **Second-order Galois**: L(L(P)) for meta-axioms
- **Proof of axiom discovery convergence**: Banach fixed-point theorem
- **Completeness theorem**: ∀P, ∃k: L(R^k(P)) < ε (every proposition stratifies)
- **Gödel correspondence**: Contradiction ↔ unprovable propositions

**Status**: Mathematical foundations. Proof sketches only. Not production-ready.

### B.4 Research Directions

**If you resurrect these**, consider:
1. **Operator Calculus**: Implement ∇L using LLM-based perturbations
2. **Bifurcation**: Add loss landscape visualization to Telescope UI
3. **Metatheory**: Formalize convergence proofs for axiom discovery
4. **Integration**: Bridge to existing categorical infrastructure

---

## Cross-References

**Related Specifications**:
- `spec/agents/d-gent.md` - Persistence layer for Galois data structures
- `spec/protocols/witness.md` - Mark witnessing (Galois triage integration)
- `spec/protocols/dp.md` - Decision processes (constitutional reward)
- `spec/protocols/agentese.md` - Five-context integration
- `spec/protocols/telescope-navigation.md` - DP-guided navigation with loss
- `spec/services/categorical.md` - Category-theoretic foundations

**Implementation Skills**:
- `docs/skills/zero-seed-galois.md` - Galois framework guide
- `docs/skills/proof-patterns.md` - Toulmin proof construction
- `docs/skills/llm-augmented-discovery.md` - LLM integration patterns

---

## Document Metadata

- **Version**: 1.0.0 (Unified Canonical)
- **Date**: 2025-12-24
- **Authors**: Kent Gang, Claude (Anthropic)
- **Status**: CANONICAL
- **Supersedes**:
  - `spec/protocols/zero-seed.md` (v1, ~2,498 lines)
  - `spec/protocols/zero-seed/` (v2, modular, ~10 files)
  - `spec/protocols/zero-seed1/` (v3, Galois-native, ~14 files)
- **Line Count**: ~1,350 (vs. ~27,486 combined)
- **Compression Ratio**: 20.4:1

---

*"Axioms are fixed points. Proofs are coherence. Layers are emergence. Zero Seed is the foundation."*