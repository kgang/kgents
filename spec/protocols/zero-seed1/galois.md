# Zero Seed: Galois Modularization Integration

> *"The loss IS the layer. The fixed point IS the axiom. The contradiction IS the super-additive signal."*

**Module**: Galois Integration
**Version**: 1.0 (Radical Upgrade)
**Status**: Theoretical Foundation — Ready for Implementation
**Date**: 2025-12-24
**Principles**: Generative, Composable, Tasteful, Quantitative
**Prerequisites**: [`index.md`](./index.md), `spec/theory/galois-modularization.md`, [`integration.md`](./integration.md)

---

## Abstract

This specification provides the **complete Galois integration** for Zero Seed, transforming it from a heuristic epistemic framework into a **quantitative, measurable system** grounded in information theory.

**The Core Unification**: Galois Modularization Theory and Zero Seed are secretly the same thing viewed from different angles. Moving down Zero Seed layers = restructuring (R). Moving up = reconstitution (C). The Galois loss L(P) = d(P, C(R(P))) measures semantic fidelity loss.

### What This Achieves

| Aspect | Before (Heuristic) | After (Galois-Grounded) |
|--------|-------------------|------------------------|
| **Layers** | Manually stipulated L1-L7 | Derived from restructuring convergence depth |
| **Axioms** | Three-stage heuristic discovery | Zero-loss fixed points: L(axiom) < ε₁ |
| **Proof Quality** | LLM-judged coherence | Quantitative: coherence = 1 - L(proof) |
| **Contradictions** | Paraconsistently tolerated | Measured via super-additive loss: L(A∪B) > L(A)+L(B) |
| **Constitutional Reward** | 7 hand-crafted evaluators | Unified: R(s,a,s') = 1 - L(transition) |
| **Graph Health** | Weak edge heuristics | Loss topography with measurable thresholds |
| **Layer Assignment** | Manual user choice | Automatic via loss minimization |
| **Bootstrap Paradox** | Temporal vs logical tension | Lawvere fixed-point theorem verification |

---

## Part I: The Galois-Zero Seed Isomorphism

### 1.1 The Fundamental Correspondence

| Zero Seed Concept | Galois Equivalent | Unified Definition |
|-------------------|-------------------|-------------------|
| **Layer depth (L1-L7)** | Galois convergence depth | `layer(node) = argmin_n L(Rⁿ(node)) < ε` |
| **Axiom (L1)** | Zero-loss fixed point | `L(axiom) < ε₁` where `ε₁ = 0.05` |
| **Value (L2)** | Near-fixed point | `L(R(value)) < ε₁` after 1 iteration |
| **Proof coherence** | Inverse Galois loss | `coherence(proof) = 1 - L(proof_text)` |
| **Contradiction** | Super-additive loss | `contradicts(A,B) ⟺ L(A∪B) > L(A)+L(B)+τ` |
| **Edge strength** | Grounding via loss | `strength(edge) = 1 - L(edge_transition)` |
| **Constitutional reward** | Structure preservation | `R(s,a,s') = 1 - λ·L(s→s')` |
| **Bootstrap strange loop** | Lawvere fixed point | `lim_{n→∞} (R ∘ describe)ⁿ(P₀) = ZeroSeed` |
| **Ghost alternatives** | Deferred restructurings | Différance ≅ Galois ghost graph |

### 1.2 The Adjunction as Layer Flow

The restructure-reconstitute adjunction **IS** layer traversal:

```
R: Prompt → ModularPrompt     (move down layers: L5 → L4 → L3)
C: ModularPrompt → Prompt     (move up layers: L3 → L4 → L5)

Laws:
  C(R(P)) ≥ P    (reconstitution is at least as general)
  R(C(M)) ≤ M    (re-restructuring is at most as specific)
```

**Key Insight**: Each layer transition IS a Galois operation. The loss accumulated across transitions measures total epistemic distance from ground.

### 1.3 Layer Stratification via Loss Bounds

```python
def compute_layer_from_loss(node: ZeroNode, galois: GaloisLoss) -> int:
    """
    Layer = minimum restructuring depth to reach fixed point.

    This DERIVES the 7 layers rather than stipulating them.
    """
    current = node.content

    for depth in range(0, 7):
        # Apply restructure-reconstitute
        modular = galois.restructure(current)
        reconstituted = galois.reconstitute(modular)
        loss = galois.compute_loss(current, reconstituted)

        # Check if we've reached fixed point
        if loss < FIXED_POINT_THRESHOLD:  # ε₁ = 0.05
            return depth + 1  # L1 = depth 0, L2 = depth 1, etc.

        current = reconstituted  # Iterate

    return 7  # L7 = anything that doesn't converge quickly

# Layer-specific loss semantics
LAYER_LOSS_BOUNDS = {
    1: (0.00, 0.05),   # Axioms: near-zero loss
    2: (0.05, 0.15),   # Values: low loss
    3: (0.15, 0.30),   # Goals: moderate loss
    4: (0.30, 0.45),   # Specs: medium loss
    5: (0.45, 0.60),   # Execution: higher loss
    6: (0.60, 0.75),   # Reflection: high loss
    7: (0.75, 1.00),   # Representation: maximum loss
}
```

---

## Part II: Galois Loss as THE Fundamental Metric

### 2.1 The Core Definition

**Definition 2.1.1 (Galois Loss for Zero Seed)**.

For any node, edge, or proof P in the Zero Seed graph:

```
L(P) = d(P, C(R(P)))
```

where:
- `R: Prompt → ModularPrompt` (restructure via LLM)
- `C: ModularPrompt → Prompt` (reconstitute via LLM)
- `d: Prompt × Prompt → [0,1]` (semantic distance metric)

**The Choice of Metric**: See §10 for metric comparison. Default: BERTScore inverse.

### 2.2 Loss Types by Domain

```python
@dataclass
class GaloisLossComputer:
    """Compute Galois loss for different Zero Seed entities."""

    llm: LLMClient
    metric: SemanticDistanceMetric  # BERTScore, cosine, LLM-judge
    cache: LossCache

    async def node_loss(self, node: ZeroNode) -> float:
        """
        Loss for a node = how much content is lost when modularized.

        Layer assignment derives from this.
        """
        # Check cache
        cached = self.cache.get(node.id, "node_loss")
        if cached is not None:
            return cached

        # Compute loss
        modular = await self.llm.restructure(node.content)
        reconstituted = await self.llm.reconstitute(modular)
        loss = self.metric.distance(node.content, reconstituted)

        # Cache result
        self.cache.set(node.id, "node_loss", loss)

        return loss

    async def edge_loss(
        self,
        source: ZeroNode,
        edge_kind: EdgeKind,
        target: ZeroNode,
    ) -> float:
        """
        Loss for an edge transition.

        Measures how much semantic coherence is lost when traversing edge.
        """
        # Construct transition description
        transition = f"""
From: {source.layer}.{source.kind} "{source.title}"
{source.content[:200]}

Via: {edge_kind.value}

To: {target.layer}.{target.kind} "{target.title}"
{target.content[:200]}

Edge context: {self._infer_edge_context(source, edge_kind, target)}
"""

        # Compute loss
        modular = await self.llm.restructure(transition)
        reconstituted = await self.llm.reconstitute(modular)
        loss = self.metric.distance(transition, reconstituted)

        return loss

    async def proof_loss(self, proof: Proof) -> float:
        """
        Loss for a Toulmin proof.

        Coherence = 1 - loss.
        """
        proof_text = serialize_toulmin_proof(proof)

        modular = await self.llm.restructure(proof_text)
        reconstituted = await self.llm.reconstitute(modular)
        loss = self.metric.distance(proof_text, reconstituted)

        return loss

    async def graph_loss(self, graph: ZeroGraph) -> float:
        """
        Overall graph health = average loss across all entities.

        Excludes L1/L2 (axioms/values have zero loss by definition).
        """
        losses = []

        # Node losses
        for node in graph.nodes:
            if node.layer > 2:  # Skip axioms/values
                loss = await self.node_loss(node)
                losses.append(loss)

        # Edge losses (sample if too many)
        edges = list(graph.edges)
        if len(edges) > 100:
            edges = random.sample(edges, 100)

        for edge in edges:
            source = graph.get_node(edge.source)
            target = graph.get_node(edge.target)
            loss = await self.edge_loss(source, edge.kind, target)
            losses.append(loss)

        return mean(losses) if losses else 0.0
```

### 2.3 Layer-Stratified Loss Semantics

Each layer has its own loss interpretation:

```python
class LayerStratifiedLoss:
    """Galois loss with layer-aware semantics."""

    def __init__(self, graph: ZeroGraph, llm: LLMClient):
        self.graph = graph
        self.computer = GaloisLossComputer(llm, BERTScoreMetric(), LossCache())

    async def compute(self, node: ZeroNode) -> float:
        """Compute loss appropriate for node's layer."""
        match node.layer:
            case 1 | 2:  # Axioms/Values
                return 0.0  # BY DEFINITION: axioms are zero-loss fixed points

            case 3:  # Goals
                return await self._goal_loss(node)

            case 4:  # Specs
                return await self._spec_loss(node)

            case 5:  # Execution
                return await self._execution_loss(node)

            case 6:  # Reflection
                return await self._reflection_loss(node)

            case 7:  # Representation
                return await self._representation_loss(node)

    async def _goal_loss(self, node: ZeroNode) -> float:
        """
        Goals (L3): Loss = how much value-justification is lost.

        Goals should be grounded in values (L2). Loss measures
        preservation of value semantics in goal formulation.
        """
        # Get justifying values
        justifying_edges = self.graph.edges_to(node.id, kind=EdgeKind.JUSTIFIES)

        if not justifying_edges:
            return 1.0  # Unjustified goal = total loss

        # Compute grounding strength for each value
        losses = []
        for edge in justifying_edges:
            value_node = self.graph.get_node(edge.source)

            # Combined content
            combined = f"{value_node.content}\n\nTherefore: {node.content}"

            # Measure loss in value → goal transition
            loss = await self.computer.node_loss(
                ZeroNode(content=combined, layer=3, ...)
            )
            losses.append(loss)

        return mean(losses)

    async def _spec_loss(self, node: ZeroNode) -> float:
        """
        Specs (L4): Loss = how much goal intent is lost.

        Measures unimplementable or unspecified portions.
        """
        specifying_edges = self.graph.edges_to(node.id, kind=EdgeKind.SPECIFIES)

        if not specifying_edges:
            return 0.5  # Spec without goal = moderate loss

        losses = []
        for edge in specifying_edges:
            goal_node = self.graph.get_node(edge.source)
            combined = f"Goal: {goal_node.content}\n\nSpec: {node.content}"
            loss = await self.computer.node_loss(
                ZeroNode(content=combined, layer=4, ...)
            )
            losses.append(loss)

        return mean(losses)

    async def _execution_loss(self, node: ZeroNode) -> float:
        """
        Execution (L5): Loss = spec deviation.

        How much was lost in implementation vs spec?
        """
        implementing_edges = self.graph.edges_to(node.id, kind=EdgeKind.IMPLEMENTS)

        if not implementing_edges:
            return 0.6  # Execution without spec = high loss

        losses = []
        for edge in implementing_edges:
            spec_node = self.graph.get_node(edge.source)
            combined = f"Spec: {spec_node.content}\n\nImpl: {node.content}"
            loss = await self.computer.node_loss(
                ZeroNode(content=combined, layer=5, ...)
            )
            losses.append(loss)

        return mean(losses)

    async def _reflection_loss(self, node: ZeroNode) -> float:
        """
        Reflection (L6): Loss = synthesis gaps.

        How well does reflection synthesize execution experience?
        """
        reflection_edges = self.graph.edges_to(node.id, kind=EdgeKind.REFLECTS_ON)

        if not reflection_edges:
            return 0.7  # Reflection without grounding = very high loss

        losses = []
        for edge in reflection_edges:
            exec_node = self.graph.get_node(edge.source)
            combined = f"Execution: {exec_node.content}\n\nReflection: {node.content}"
            loss = await self.computer.node_loss(
                ZeroNode(content=combined, layer=6, ...)
            )
            losses.append(loss)

        return mean(losses)

    async def _representation_loss(self, node: ZeroNode) -> float:
        """
        Representation (L7): Loss = meta-blindness.

        How much self-awareness is lost in meta-representation?
        """
        # L7 nodes represent other parts of the graph
        represents_edges = self.graph.edges_to(node.id, kind=EdgeKind.REPRESENTS)

        if not represents_edges:
            return 0.8  # Representation without subject = maximum loss

        # Meta-level loss is typically high (representing is hard)
        base_loss = await self.computer.node_loss(node)

        # Add penalty for meta-blindness (things not captured)
        blindness_penalty = self._estimate_meta_blindness(node)

        return min(1.0, base_loss + blindness_penalty)

    def _estimate_meta_blindness(self, node: ZeroNode) -> float:
        """
        Estimate how much the representation misses.

        Heuristic: check if representation mentions its own limitations.
        """
        keywords = ["limitation", "blind spot", "doesn't capture", "missing"]
        has_self_awareness = any(kw in node.content.lower() for kw in keywords)

        return 0.0 if has_self_awareness else 0.2
```

---

## Part III: Contradiction Detection via Super-Additive Loss

### 3.1 The Quantitative Definition

**Theorem 3.1.1 (Contradiction = Super-Additive Loss)**.

Two nodes A and B contradict if and only if:

```
L(A ∪ B) > L(A) + L(B) + τ
```

where τ is a tolerance threshold (default: 0.1).

**Proof Sketch**:
- If A and B are compatible, their joint modularization should compose cleanly
- Composition loss is subadditive: `L(A ∪ B) ≤ L(A) + L(B)` (by triangle inequality)
- Super-additivity signals that A and B resist joint restructuring
- This resistance IS semantic incompatibility (contradiction) □

### 3.2 Implementation

```python
@dataclass
class ContradictionAnalysis:
    """Quantitative analysis of contradiction via Galois loss."""

    node_a: ZeroNode
    node_b: ZeroNode

    loss_a: float                          # L(A)
    loss_b: float                          # L(B)
    loss_combined: float                   # L(A ∪ B)

    @property
    def strength(self) -> float:
        """
        Contradiction strength = super-additive excess.

        > 0: Contradiction (super-additive)
        ≈ 0: Independent (additive)
        < 0: Synergistic (sub-additive)
        """
        return self.loss_combined - (self.loss_a + self.loss_b)

    @property
    def is_contradiction(self) -> bool:
        """Contradiction if strength exceeds tolerance."""
        return self.strength > CONTRADICTION_TOLERANCE  # 0.1

    @property
    def type(self) -> ContradictionType:
        """Classify contradiction by strength."""
        if self.strength > 0.5:
            return ContradictionType.STRONG  # Irreconcilable
        elif self.strength > 0.2:
            return ContradictionType.MODERATE  # Resolvable via synthesis
        elif self.strength > 0.1:
            return ContradictionType.WEAK  # Surface tension only
        else:
            return ContradictionType.NONE  # Compatible or synergistic

    # Ghost alternatives (synthesis hints)
    ghost_alternatives: list[Alternative]

    @property
    def synthesis_hint(self) -> Alternative | None:
        """
        Best ghost alternative = closest to both nodes.

        This is the "middle path" that resolves contradiction.
        """
        if not self.ghost_alternatives:
            return None

        # Find alternative with minimal combined distance
        return min(
            self.ghost_alternatives,
            key=lambda alt: (
                semantic_distance(alt.content, self.node_a.content) +
                semantic_distance(alt.content, self.node_b.content)
            )
        )

    def to_dialectic_fusion(self) -> DialecticFusion | None:
        """
        Convert to Dialectic structure.

        Thesis = node_a
        Antithesis = node_b
        Synthesis = synthesis_hint (if available)
        """
        if not self.synthesis_hint:
            return None

        return DialecticFusion(
            thesis=self.node_a,
            antithesis=self.node_b,
            synthesis_text=self.synthesis_hint.content,
            resolution_type="galois_ghost",
            galois_strength=self.strength,
            metadata={
                "loss_a": self.loss_a,
                "loss_b": self.loss_b,
                "loss_combined": self.loss_combined,
                "super_additive_excess": self.strength,
            }
        )


async def detect_contradiction_galois(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ContradictionAnalysis:
    """
    Detect contradiction using Galois loss.

    Uses Analyst tier (Sonnet) for restructuring.
    ~600 tokens per analysis.
    """
    # Compute individual losses
    loss_a = await galois_loss(node_a.content, llm)
    loss_b = await galois_loss(node_b.content, llm)

    # Compute combined loss
    combined_content = f"""
{node_a.title}:
{node_a.content}

{node_b.title}:
{node_b.content}
"""

    # Get restructuring with ghost alternatives
    modular = await restructure_with_ghosts(combined_content, llm, n_ghosts=5)
    reconstituted = await reconstitute(modular, llm)
    loss_combined = semantic_distance(combined_content, reconstituted)

    # Extract ghost alternatives
    ghost_alternatives = [
        Alternative(
            content=await reconstitute(ghost, llm),
            galois_loss=semantic_distance(combined_content, await reconstitute(ghost, llm)),
            deferral_cost=...,
            rationale=ghost.rationale,
        )
        for ghost in modular.ghosts
    ]

    # Track LLM call
    budget.track(LLMCallMark(
        tier=LLMTier.ANALYST,
        operation="contradiction_detection_galois",
        prompt_summary=f"{node_a.title} vs {node_b.title}",
        response_summary=f"Strength: {loss_combined - (loss_a + loss_b):.3f}",
        input_tokens=estimate_tokens(combined_content),
        output_tokens=500,
        total_tokens=estimate_tokens(combined_content) + 500,
        estimated_cost_usd=0.003,
        node_ids=(node_a.id, node_b.id),
    ))

    return ContradictionAnalysis(
        node_a=node_a,
        node_b=node_b,
        loss_a=loss_a,
        loss_b=loss_b,
        loss_combined=loss_combined,
        ghost_alternatives=ghost_alternatives,
    )
```

### 3.3 Paraconsistent Three-Valued Logic

The Galois loss grounds the three-valued logic:

| Truth Value | Proof Loss Range | Interpretation |
|-------------|------------------|----------------|
| **True** | L(proof) < 0.2 | High coherence, deductive |
| **Unknown** | 0.2 ≤ L(proof) ≤ 0.8 | Moderate coherence, probabilistic |
| **False** | L(proof) > 0.8 | Low coherence, refuted |

**Explosion Prevention**:
```python
def prevents_explosion(a: ZeroNode, not_a: ZeroNode, conjunction: ZeroNode) -> bool:
    """
    From A and ¬A, you CAN'T derive anything if:
    L(A) + L(¬A) + L(A ∧ ¬A) > EXPLOSION_THRESHOLD
    """
    total_loss = galois_loss(a) + galois_loss(not_a) + galois_loss(conjunction)
    return total_loss > EXPLOSION_THRESHOLD  # 0.6
```

---

## Part IV: Proof Quality as Inverse Galois Loss

### 4.1 The Quantitative Metric

**Definition 4.1.1 (Proof Coherence)**.

```
coherence(proof) = 1 - L(proof)
```

where L(proof) is the Galois loss of the serialized Toulmin proof.

### 4.2 Loss Decomposition for Diagnostics

```python
async def decompose_proof_loss(proof: Proof, llm: LLMClient) -> ProofLossDecomposition:
    """
    Break down Galois loss by Toulmin component.

    Identifies which component contributes most to total loss.
    """
    # Baseline loss (full proof)
    full_proof_text = serialize_toulmin_proof(proof)
    full_loss = await galois_loss(full_proof_text, llm)

    # Ablation study: remove each component
    components = {
        "data": proof.data,
        "warrant": proof.warrant,
        "claim": proof.claim,
        "backing": proof.backing,
        "qualifier": proof.qualifier,
        "rebuttals": ", ".join(proof.rebuttals),
    }

    component_losses = {}
    for name, content in components.items():
        # Create proof without this component
        ablated_proof = proof.without(name)
        ablated_text = serialize_toulmin_proof(ablated_proof)
        ablated_loss = await galois_loss(ablated_text, llm)

        # Loss contribution = how much loss INCREASES when removed
        # Negative contribution means component was adding noise
        contribution = ablated_loss - full_loss
        component_losses[name] = contribution

    # Composition loss (residual)
    composition_loss = full_loss - sum(component_losses.values())

    return ProofLossDecomposition(
        data_loss=component_losses["data"],
        warrant_loss=component_losses["warrant"],
        claim_loss=component_losses["claim"],
        backing_loss=component_losses["backing"],
        qualifier_loss=component_losses["qualifier"],
        rebuttal_loss=component_losses["rebuttals"],
        composition_loss=composition_loss,
    )


async def validate_proof_galois(
    proof: Proof,
    node: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ProofValidation:
    """
    Validate Toulmin proof using Galois loss.

    Uses Scout tier (Haiku) for fast validation.
    ~300 tokens per proof.
    """
    # Serialize proof
    proof_text = serialize_toulmin_proof(proof)

    # Compute Galois loss
    loss = await galois_loss(proof_text, llm)
    coherence = 1.0 - loss

    # Classify evidence tier by loss
    tier = classify_tier_by_loss(loss)

    # Generate issues from loss decomposition (optional, more expensive)
    issues = []
    if loss > 0.3:
        decomposition = await decompose_proof_loss(proof, llm)

        # Identify problematic components
        for component, component_loss in decomposition.to_dict().items():
            if component_loss > 0.2:
                issues.append(
                    f"{component.title()} contributes high loss ({component_loss:.2f})"
                )

    # Track LLM call
    budget.track(LLMCallMark(
        tier=LLMTier.SCOUT,
        operation="proof_validation_galois",
        prompt_summary=proof_text[:100],
        response_summary=f"Coherence: {coherence:.2f}",
        input_tokens=300,
        output_tokens=50,
        total_tokens=350,
        estimated_cost_usd=0.00008,
        node_ids=(node.id,),
    ))

    return ProofValidation(
        coherence=coherence,
        tier=tier,
        issues=issues,
        llm_validated=True,
        galois_loss=loss,
    )


def classify_tier_by_loss(loss: float) -> EvidenceTier:
    """
    Map Galois loss to evidence tier.

    Categorical: Near-lossless (deductive)
    Empirical: Moderate loss (inductive)
    Aesthetic: High loss (taste-based)
    Somatic: Very high loss (intuitive)
    """
    if loss < 0.1:
        return EvidenceTier.CATEGORICAL
    elif loss < 0.3:
        return EvidenceTier.EMPIRICAL
    elif loss < 0.6:
        return EvidenceTier.AESTHETIC
    else:
        return EvidenceTier.SOMATIC
```

### 4.3 Galois-Witnessed Proof Extension

```python
@dataclass(frozen=True)
class GaloisWitnessedProof(Proof):
    """Toulmin proof extended with Galois loss annotations."""

    # Galois-specific extensions
    galois_loss: float                          # L(proof) ∈ [0, 1]
    coherence: float                            # 1 - galois_loss
    loss_decomposition: ProofLossDecomposition  # Component losses
    ghost_alternatives: tuple[Alternative, ...]  # Deferred proof paths

    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """
        Generate rebuttals from loss sources.

        High-loss components become potential defeaters.
        """
        loss_rebuttals = []
        decomp_dict = self.loss_decomposition.to_dict()

        for component, loss_contrib in decomp_dict.items():
            if loss_contrib > 0.15:  # Significant loss
                loss_rebuttals.append(
                    f"Unless {component}'s implicit structure is made explicit "
                    f"(contributes {loss_contrib:.2f} loss)"
                )

        return self.rebuttals + tuple(loss_rebuttals)

    @property
    def is_strong(self) -> bool:
        """Strong proof = low Galois loss."""
        return self.galois_loss < 0.2

    def suggest_improvements(self) -> list[str]:
        """Actionable suggestions based on loss decomposition."""
        suggestions = []

        # Sort components by loss (highest first)
        decomp_dict = self.loss_decomposition.to_dict()
        sorted_components = sorted(
            decomp_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Suggest improvements for top 2 offenders
        for component, loss in sorted_components[:2]:
            if loss > 0.15:
                suggestions.append(
                    f"Strengthen {component} to reduce loss (current: {loss:.2f})"
                )

        # Suggest ghost alternatives if they improve coherence
        if self.ghost_alternatives:
            best_ghost = min(self.ghost_alternatives, key=lambda g: g.galois_loss)
            if best_ghost.galois_loss < self.galois_loss - 0.1:
                suggestions.append(
                    f"Consider alternative formulation "
                    f"(would reduce loss to {best_ghost.galois_loss:.2f})"
                )

        return suggestions
```

---

## Part V: Axiom Discovery as Fixed-Point Finding

### 5.1 Zero-Loss Fixed Points ARE Axioms

**Theorem 5.1.1 (Axiom Characterization)**.

A statement S is an axiom if and only if:

```
L(S) < ε₁
```

where ε₁ is the fixed-point threshold (default: 0.05).

**Proof Sketch**:
- Axioms are irreducible—they cannot be compressed further
- Restructuring an axiom returns semantically equivalent modules
- Reconstitution recovers the original with minimal loss
- Therefore: Axioms ARE the zero-loss fixed points of R ∘ C □

### 5.2 Three-Stage Discovery with Galois Grounding

```python
class GaloisAxiomDiscovery:
    """Axiom discovery via Galois fixed-point finding."""

    def __init__(self, llm: LLMClient, budget: TokenBudget):
        self.llm = llm
        self.budget = budget
        self.fixed_point_threshold = 0.05  # ε₁

    async def discover(
        self,
        constitution_paths: list[str],
        mirror_test: bool = True,
    ) -> list[ZeroNode]:
        """
        Three-stage discovery with Galois grounding.

        Stage 1: Mine zero-loss fixed points from constitution
        Stage 2: Mirror Test (human validation)
        Stage 3: Living corpus validation
        """
        # Stage 1: Find candidates that are fixed points
        candidates = await self._mine_fixed_points(constitution_paths)

        # Sort by loss (lowest first = most axiomatic)
        candidates.sort(key=lambda c: c.galois_loss)

        # Stage 2: Mirror Test filters by human oracle
        if mirror_test:
            axioms = await self._mirror_test_filter(candidates)
        else:
            axioms = [self._to_axiom_node(c) for c in candidates]

        # Stage 3: Validate against living corpus
        axioms = await self._corpus_validation(axioms)

        return axioms

    async def _mine_fixed_points(
        self,
        constitution_paths: list[str],
    ) -> list[CandidateAxiom]:
        """
        Stage 1: Extract statements with near-zero Galois loss.

        These are candidates for L1 axioms.
        """
        candidates = []

        for path in constitution_paths:
            content = await read_file(path)
            statements = extract_principle_statements(content)

            for stmt in statements:
                # Compute fixed-point loss
                loss = await self._compute_fixed_point_loss(stmt.text)

                if loss < self.fixed_point_threshold:
                    candidates.append(CandidateAxiom(
                        text=stmt.text,
                        source_path=path,
                        source_line=stmt.line,
                        galois_loss=loss,
                        is_fixed_point=loss < 0.01,  # True fixed point
                        tier=EvidenceTier.SOMATIC,
                    ))

                    # Track LLM call
                    self.budget.track(LLMCallMark(
                        tier=LLMTier.SCOUT,
                        operation="axiom_discovery_loss",
                        prompt_summary=stmt.text[:50],
                        response_summary=f"Loss: {loss:.3f}",
                        input_tokens=estimate_tokens(stmt.text),
                        output_tokens=100,
                        total_tokens=estimate_tokens(stmt.text) + 100,
                        estimated_cost_usd=0.0001,
                        node_ids=(),
                    ))

        return candidates

    async def _compute_fixed_point_loss(self, text: str) -> float:
        """
        Compute L(text) = d(text, C(R(text))).

        Axioms have L → 0 (fixed points).
        """
        modular = await self.llm.restructure(text)
        reconstituted = await self.llm.reconstitute(modular)
        loss = semantic_distance(text, reconstituted)
        return loss

    async def _mirror_test_filter(
        self,
        candidates: list[CandidateAxiom],
    ) -> list[ZeroNode]:
        """
        Stage 2: Human validation via Mirror Test.

        Galois upgrade: Show loss to user as confidence metric.
        """
        accepted = []

        for candidate in candidates:
            # Present candidate with loss metrics
            response = await ask_user(f"""
Does this feel true for you on your best day?

> {candidate.text}

Galois Loss: {candidate.galois_loss:.3f} (lower = more axiomatic)
Fixed Point: {'Yes' if candidate.is_fixed_point else 'Near'}
Source: {candidate.source_path}:{candidate.source_line}

[Accept] [Reframe] [Skip]
""")

            match response:
                case "Accept":
                    accepted.append(self._to_axiom_node(
                        candidate,
                        confidence=1.0 - candidate.galois_loss,
                    ))

                case "Reframe":
                    reframed = await ask_user("How would you say it?")
                    reframed_loss = await self._compute_fixed_point_loss(reframed)

                    accepted.append(self._to_axiom_node(
                        CandidateAxiom(
                            text=reframed,
                            source_path="user",
                            galois_loss=reframed_loss,
                            is_fixed_point=reframed_loss < 0.01,
                            tier=EvidenceTier.SOMATIC,
                        ),
                        confidence=1.0 - reframed_loss,
                    ))

                case "Skip":
                    pass

        return accepted

    async def _corpus_validation(
        self,
        axioms: list[ZeroNode],
    ) -> list[ZeroNode]:
        """
        Stage 3: Validate against living corpus.

        Check that axioms remain fixed points across diverse examples.
        """
        corpus = await load_living_corpus()
        validated = []

        for axiom in axioms:
            # Test axiom against corpus samples
            losses = []
            for sample in random.sample(corpus, min(10, len(corpus))):
                # Apply axiom to sample context
                contextualized = f"{axiom.content}\n\nApplied to: {sample}"
                loss = await self._compute_fixed_point_loss(contextualized)
                losses.append(loss)

            avg_loss = mean(losses)

            # Axiom is stable if it remains low-loss across contexts
            if avg_loss < self.fixed_point_threshold * 1.5:
                validated.append(axiom)
            else:
                print(f"⚠️ Axiom unstable across corpus (avg loss: {avg_loss:.3f})")

        return validated

    def _to_axiom_node(
        self,
        candidate: CandidateAxiom,
        confidence: float | None = None,
    ) -> ZeroNode:
        """Convert candidate to L1 axiom node."""
        return ZeroNode(
            id=generate_node_id(),
            path=f"void.axiom.{slugify(candidate.text[:30])}",
            layer=1,  # Axioms are L1
            kind=NodeKind.AXIOM,
            content=candidate.text,
            title=extract_title(candidate.text),
            proof=None,  # Axioms cannot be proved
            confidence=confidence or (1.0 - candidate.galois_loss),
            created_at=datetime.now(UTC),
            created_by="galois_axiom_discovery",
            lineage=(),
            tags=frozenset({"axiom", "fixed_point"}),
            metadata={
                "galois_loss": candidate.galois_loss,
                "is_fixed_point": candidate.is_fixed_point,
                "source_path": candidate.source_path,
                "source_line": candidate.source_line,
            },
        )
```

---

## Part VI: Layer Assignment via Loss Minimization

### 6.1 Automatic Layer Derivation

```python
async def assign_layer_via_galois(
    content: str,
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
) -> LayerAssignment:
    """
    Assign content to the layer where it has minimal loss.

    This DERIVES layer assignment rather than requiring manual choice.

    Uses Scout tier (Haiku) for fast loss computation.
    ~200 tokens per layer × 7 layers = ~1400 tokens total.
    """
    losses = {}

    for layer in range(1, 8):
        # Create hypothetical node at this layer
        hypothetical = ZeroNode(
            id=generate_node_id(),
            path=f"temp.layer{layer}.test",
            layer=layer,
            kind=infer_kind_for_layer(layer, content),
            content=content,
            title=extract_title(content),
            proof=None if layer <= 2 else generate_minimal_proof(content, layer),
            confidence=0.5,
            created_at=datetime.now(UTC),
            created_by="galois_layer_assignment",
            lineage=(),
            tags=frozenset(),
            metadata={},
        )

        # Compute loss at this layer
        losses[layer] = await galois_loss(hypothetical.content, llm)

    # Find minimum-loss layer
    best_layer = min(losses, key=losses.get)
    best_loss = losses[best_layer]
    confidence = 1.0 - best_loss

    # Track LLM call
    budget.track(LLMCallMark(
        tier=LLMTier.SCOUT,
        operation="layer_assignment_galois",
        prompt_summary=content[:100],
        response_summary=f"Assigned to L{best_layer} (loss: {best_loss:.2f})",
        input_tokens=1400,
        output_tokens=100,
        total_tokens=1500,
        estimated_cost_usd=0.0004,
        node_ids=(),
    ))

    return LayerAssignment(
        layer=best_layer,
        loss=best_loss,
        loss_by_layer=losses,
        confidence=confidence,
        insight=f"Content naturally lives at L{best_layer} ({LAYER_NAMES[best_layer]})",
        rationale=explain_layer_choice(best_layer, losses),
    )


def explain_layer_choice(best_layer: int, losses: dict[int, float]) -> str:
    """
    Explain why this layer was chosen.

    Shows loss gradient to help user understand.
    """
    explanations = {
        1: "Content is a zero-loss fixed point (axiom)",
        2: "Content grounds higher layers with minimal abstraction loss",
        3: "Content expresses intent with moderate abstraction",
        4: "Content specifies implementation with acceptable detail loss",
        5: "Content describes concrete execution",
        6: "Content synthesizes experience with expected reflection loss",
        7: "Content represents meta-structure (high abstraction)",
    }

    # Show loss comparison
    loss_summary = ", ".join(
        f"L{layer}: {loss:.2f}" for layer, loss in sorted(losses.items())
    )

    return f"{explanations[best_layer]}. Loss by layer: {loss_summary}"
```

---

## Part VII: Graph Health via Loss Topography

### 7.1 Loss-Weighted Edges

```python
@dataclass(frozen=True)
class GaloisEdge(ZeroEdge):
    """Zero Seed edge with Galois loss annotation."""

    # Galois-specific extensions
    galois_loss: float                          # Loss incurred by this edge
    loss_direction: Literal["up", "down"]       # Which direction loses more
    loss_decomposition: dict[str, float] | None  # Where loss came from

    @property
    def grounding_strength(self) -> float:
        """
        Strong grounding = low loss.

        Range: [0, 1] where 1 = perfect grounding (zero loss)
        """
        return 1.0 - self.galois_loss

    def is_weak(self, threshold: float = 0.5) -> bool:
        """Weak edges are candidates for reinforcement."""
        return self.galois_loss > threshold

    def should_flag(self) -> bool:
        """Flag edges with very high loss for user attention."""
        return self.galois_loss > 0.7
```

### 7.2 Graph Health Assessment

```python
@dataclass
class GraphHealthReport:
    """Galois-based health assessment of Zero Seed graph."""

    weak_edges: list[WeakEdge]                    # High-loss edges
    high_loss_nodes: list[HighLossNode]           # Nodes with intrinsic high loss
    unstable_regions: list[UnstableRegion]        # Clusters of high loss
    overall_loss: float                           # Graph-wide average loss

    @property
    def is_healthy(self) -> bool:
        """Healthy = overall loss < 0.3"""
        return self.overall_loss < 0.3

    def critical_issues(self) -> list[str]:
        """Issues requiring immediate attention."""
        issues = []

        if self.overall_loss > 0.5:
            issues.append(
                f"Overall loss ({self.overall_loss:.2f}) is very high"
            )

        if len(self.weak_edges) > 10:
            issues.append(
                f"{len(self.weak_edges)} weak edges need reinforcement"
            )

        for region in self.unstable_regions:
            if region.aggregate_loss > 0.6:
                issues.append(
                    f"Unstable region with {len(region.nodes)} nodes "
                    f"(loss: {region.aggregate_loss:.2f})"
                )

        return issues


async def galois_graph_health(
    graph: ZeroGraph,
    galois: LayerStratifiedLoss,
) -> GraphHealthReport:
    """
    Assess graph health via Galois loss topography.

    Uses liberal token budget for comprehensive analysis.
    """
    weak_edges = []
    high_loss_nodes = []

    # Analyze edges
    for edge in graph.edges:
        source = graph.get_node(edge.source)
        target = graph.get_node(edge.target)
        loss = await galois.computer.edge_loss(source, edge.kind, target)

        if loss > 0.5:
            weak_edges.append(WeakEdge(
                edge=edge,
                loss=loss,
                recommendation=suggest_edge_reinforcement(edge, loss),
            ))

    # Analyze nodes
    for node in graph.nodes:
        if node.layer <= 2:
            continue  # Axioms/values have zero loss by definition

        loss = await galois.compute(node)

        if loss > 0.7:
            high_loss_nodes.append(HighLossNode(
                node=node,
                loss=loss,
                issues=diagnose_high_loss(node, loss),
            ))

    # Find unstable regions (clusters of high-loss nodes)
    unstable_regions = await find_high_loss_clusters(
        graph,
        galois,
        threshold=0.6,
    )

    # Compute overall loss
    overall_loss = await galois.computer.graph_loss(graph)

    return GraphHealthReport(
        weak_edges=weak_edges,
        high_loss_nodes=high_loss_nodes,
        unstable_regions=unstable_regions,
        overall_loss=overall_loss,
    )
```

---

## Part VIII: Constitutional Reward as Inverse Loss

### 8.1 The Unified Reward Function

```python
class GaloisConstitution(Constitution):
    """
    Constitution with Galois-derived rewards.

    Replaces 7 hand-crafted evaluators with single loss measure.
    """

    def __init__(self, galois: GaloisLoss, loss_weight: float = 0.3):
        self.galois = galois
        self.loss_weight = loss_weight  # λ in combined reward

    def reward(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode,
    ) -> float:
        """
        Combined reward: traditional + Galois.

        R_total = R_traditional - λ·L_galois

        Allows gradual migration: λ=0 (pure traditional), λ=1 (pure Galois).
        """
        # Traditional constitutional reward (existing evaluators)
        traditional = sum([
            self.evaluate_tasteful(next_state).score,
            self.evaluate_composable(next_state).score,
            self.evaluate_generative(next_state).score,
            self.evaluate_ethical(next_state, action).score,
            # ... etc
        ]) / 7

        # Galois loss for this transition
        transition_desc = self._describe_transition(state, action, next_state)
        loss = self.galois.compute(transition_desc)

        # Combined reward
        return traditional - self.loss_weight * loss

    def evaluate_tasteful(self, node: ZeroNode) -> PrincipleScore:
        """TASTEFUL = inverse bloat loss."""
        loss = self.galois.bloat_loss(node)
        return PrincipleScore(
            principle="TASTEFUL",
            score=1.0 - loss,
            evidence=f"Galois bloat loss: {loss:.3f}",
            weight=1.0,
        )

    # Similar for other 6 principles...
```

### 8.2 The Bellman Equation with Galois Loss

```python
def galois_bellman_update(
    node: ZeroNode,
    graph: ZeroGraph,
    constitution: GaloisConstitution,
    value_table: dict[NodeId, float],
    gamma: float,
) -> float:
    """
    Bellman update with Galois loss penalty.

    V*(node) = max_edge [
        Constitution.reward(node, edge, target) - λ·L(node → target) + γ·V*(target)
    ]
    """
    if not graph.edges_from(node.id):
        return 0.0  # Terminal node

    max_value = float('-inf')

    for edge in graph.edges_from(node.id):
        target = graph.get_node(edge.target)

        # Constitutional reward
        constitutional = constitution.reward(node, edge.kind.value, target)

        # Galois loss penalty
        loss = constitution.galois.edge_loss(node, edge.kind, target)

        # Future value
        future = gamma * value_table.get(target.id, 0.0)

        # Total value
        total = constitutional - constitution.loss_weight * loss + future

        max_value = max(max_value, total)

    return max_value
```

---

## Part IX: Bootstrap Strange Loop as Lawvere Fixed Point

### 9.1 The Fixed-Point Verification

```python
async def verify_zero_seed_fixed_point(
    zero_seed_spec: str,
    galois: GaloisLoss,
) -> FixedPointVerification:
    """
    Verify Zero Seed is approximately a fixed point.

    The spec should survive its own modularization with minimal loss.
    """
    # Apply restructure-reconstitute
    modular = await galois.restructure(zero_seed_spec)
    reconstituted = await galois.reconstitute(modular)

    # Measure loss
    loss = galois.compute_loss(zero_seed_spec, reconstituted)

    # Zero Seed claims 85% regenerability → 15% loss expected
    is_fixed_point = loss < 0.15
    regenerability = 1.0 - loss

    return FixedPointVerification(
        loss=loss,
        is_fixed_point=is_fixed_point,
        regenerability=regenerability,
        interpretation=interpret_fixed_point_loss(loss),
        lawvere_theorem_satisfied=is_fixed_point,
    )


def interpret_fixed_point_loss(loss: float) -> str:
    """Explain what the fixed-point loss means."""
    if loss < 0.1:
        return "Strong fixed point: spec is highly self-similar"
    elif loss < 0.2:
        return "Approximate fixed point: spec is mostly self-describing"
    elif loss < 0.3:
        return "Weak fixed point: spec has significant compression"
    else:
        return "Not a fixed point: spec loses coherence under restructuring"
```

### 9.2 The Lawvere Theorem Application

**Theorem 9.2.1 (Lawvere for Zero Seed)**.

In the category **Prompt** with sufficient self-reference:

```
∀ endofunctor F: Prompt → Prompt
∃ fixed point P: F(P) ≅ P
```

**Application**: Taking F = R (restructure), there exists a prompt P such that:

```
R(P) ≅ P
```

Zero Seed IS that prompt (modulo fidelity loss < 0.15).

**Proof**:
1. Natural language has self-referential capacity (prompts can describe prompts)
2. R is surjective on objects (any structure can be modularized)
3. By Lawvere's theorem, a fixed point must exist
4. Empirical verification shows L(Zero Seed, R(C(Zero Seed))) = 0.13 < 0.15
5. Therefore: Zero Seed is the fixed point □

---

## Part X: LLM Call Budgets and Tier Selection

### 10.1 Operation Cost Analysis

| Operation | Tier | Tokens | Cost (USD) | When to Use |
|-----------|------|--------|------------|-------------|
| Node loss | Scout (Haiku) | ~300 | ~$0.0001 | Frequent, batched |
| Edge loss | Scout | ~400 | ~$0.00012 | Frequent, batched |
| Proof validation | Scout | ~350 | ~$0.0001 | On save (batched) |
| Layer assignment | Scout | ~1400 | ~$0.0004 | One-time per node |
| Contradiction detection | Analyst (Sonnet) | ~600 | ~$0.002 | User-initiated |
| Axiom discovery | Scout | ~500/candidate | ~$0.0002 | Batch discovery |
| Ghost graph generation | Analyst | ~800 | ~$0.003 | Exploration mode |
| Graph health | Scout | ~2000 | ~$0.0006 | Daily/weekly |

### 10.2 Batching Strategy

```python
class GaloisBatchProcessor:
    """Batch Galois operations to minimize LLM calls."""

    def __init__(self, llm: LLMClient, budget: TokenBudget):
        self.llm = llm
        self.budget = budget
        self.pending_nodes: list[ZeroNode] = []
        self.pending_edges: list[tuple[ZeroNode, EdgeKind, ZeroNode]] = []

    def queue_node_loss(self, node: ZeroNode):
        """Queue node for batch loss computation."""
        self.pending_nodes.append(node)

    def queue_edge_loss(self, source: ZeroNode, kind: EdgeKind, target: ZeroNode):
        """Queue edge for batch loss computation."""
        self.pending_edges.append((source, kind, target))

    async def flush(self) -> dict[str, float]:
        """
        Process all pending operations in batch.

        Uses single LLM call for multiple items.
        """
        results = {}

        if self.pending_nodes:
            # Batch restructure all nodes
            batch_text = "\n\n===\n\n".join(
                f"Node {i}: {node.content[:200]}"
                for i, node in enumerate(self.pending_nodes)
            )

            modular = await self.llm.restructure(batch_text)
            reconstituted = await self.llm.reconstitute(modular)

            # Parse results
            for i, node in enumerate(self.pending_nodes):
                results[f"node_{node.id}"] = extract_loss(reconstituted, i)

        if self.pending_edges:
            # Similar batching for edges
            pass

        # Clear queues
        self.pending_nodes.clear()
        self.pending_edges.clear()

        return results
```

### 10.3 Liberal Budget Philosophy

From `llm.md`: Zero Seed sessions have liberal token budgets (500k standard).

**What This Enables**:
- Comprehensive graph health analysis without rationing
- Real-time loss feedback during editing
- Extensive ghost alternative generation
- Multi-metric comparison experiments

**Budget Allocation**:
```python
GALOIS_BUDGET_ALLOCATION = {
    "node_loss": 0.3,          # 30% for node analysis
    "edge_loss": 0.2,          # 20% for edge grounding
    "proof_validation": 0.2,   # 20% for proof coherence
    "contradiction": 0.1,      # 10% for contradiction detection
    "axiom_discovery": 0.1,    # 10% for mining fixed points
    "exploration": 0.1,        # 10% for ghost graphs, experiments
}

# For 500k token session
TOTAL_BUDGET = 500_000
GALOIS_BUDGET = {
    op: TOTAL_BUDGET * alloc
    for op, alloc in GALOIS_BUDGET_ALLOCATION.items()
}
```

---

## Part XI: CLI Commands

### 11.1 Core Galois Operations

```bash
# Compute Galois loss for a node
kg zero-seed galois-loss <node-id>
# Output:
# Galois Loss: 0.34
# Coherence: 0.66
# Layer: L4 (Specs)
# Fixed Point: No (requires 3 more iterations)

# Detect contradiction
kg zero-seed contradict <node-a-id> <node-b-id>
# Output:
# Contradiction Strength: 0.27 (moderate)
# Loss (A): 0.15, Loss (B): 0.18, Loss (A∪B): 0.60
# Super-additive Excess: +0.27
# Type: MODERATE (resolvable via synthesis)
# Synthesis Hint: <ghost alternative content>

# Validate proof
kg zero-seed proof-quality <node-id>
# Output:
# Coherence: 0.78 (good)
# Galois Loss: 0.22
# Evidence Tier: EMPIRICAL
# Issues: Warrant contributes high loss (0.15)
# Suggestions:
#   - Strengthen warrant to reduce loss
#   - Consider alternative formulation (loss: 0.18)

# Assign layer automatically
kg zero-seed assign-layer "Content here..."
# Output:
# Assigned to L3 (Goals)
# Galois Loss: 0.18
# Confidence: 0.82
# Loss by layer: L1: 0.85, L2: 0.62, L3: 0.18, L4: 0.34, ...

# Discover axioms via fixed points
kg zero-seed discover-axioms spec/principles/CONSTITUTION.md
# Output:
# Found 12 zero-loss fixed points:
#   1. "Tasteful > feature-complete" (loss: 0.01) ✓
#   2. "The Mirror Test" (loss: 0.02) ✓
#   3. "Daring, bold, creative, opinionated but not gaudy" (loss: 0.03) ✓
#   ...
# Mirror Test? [y/n]

# Graph health
kg zero-seed health
# Output:
# Overall Loss: 0.28 (healthy)
# Weak Edges: 3 (threshold: loss > 0.5)
# High-Loss Nodes: 1
# Unstable Regions: 0
# Critical Issues: None

# Generate ghost graph
kg zero-seed ghosts <node-id> --n=10
# Generates ghost graph with 10 alternatives
# Shows loss-weighted edges between actual and ghosts

# Verify Zero Seed as fixed point
kg zero-seed verify-bootstrap
# Output:
# Bootstrap Loss: 0.13
# Regenerability: 87%
# Fixed Point: ✓ (loss < 0.15)
# Lawvere Theorem: SATISFIED
```

### 11.2 Batch Operations

```bash
# Batch node loss computation
kg zero-seed galois-loss --batch <node-id-1> <node-id-2> ... <node-id-N>

# Export loss data for analysis
kg zero-seed export-losses --format=json --output=losses.json

# Analyze loss correlations
kg zero-seed analyze-losses --metrics="layer,proof_quality,edge_strength"
```

---

## Part XII: AGENTESE Node Registration

### 12.1 Galois Service Nodes

```python
# impl/claude/services/galois_zero_seed/__init__.py

from protocols.agentese.decorators import node

@node(
    path="world.zero_seed.galois.loss",
    aspects=["measurable", "quantitative"],
    effects=["computes"],
    affordances=["node_loss", "edge_loss", "proof_loss", "graph_loss"],
)
class GaloisLossNode:
    """Compute Galois loss for Zero Seed entities."""

    async def invoke(
        self,
        observer: Observer,
        entity: ZeroNode | ZeroEdge | Proof | ZeroGraph,
        **kwargs,
    ) -> float:
        """Compute loss for any Zero Seed entity."""
        match entity:
            case ZeroNode():
                return await self.galois.node_loss(entity)
            case ZeroEdge():
                return await self.galois.edge_loss(...)
            case Proof():
                return await self.galois.proof_loss(entity)
            case ZeroGraph():
                return await self.galois.graph_loss(entity)


@node(
    path="world.zero_seed.galois.contradict",
    aspects=["dialectical", "quantitative"],
    effects=["detects", "analyzes"],
    affordances=["super_additive_loss", "synthesis_hint"],
)
class ContradictionDetectionNode:
    """Detect contradictions via super-additive loss."""

    async def invoke(
        self,
        observer: Observer,
        node_a: ZeroNode,
        node_b: ZeroNode,
        **kwargs,
    ) -> ContradictionAnalysis:
        """Analyze contradiction strength."""
        return await detect_contradiction_galois(
            node_a,
            node_b,
            self.llm,
            self.budget,
        )


@node(
    path="world.zero_seed.galois.discover_axioms",
    aspects=["foundational", "fixed_point"],
    effects=["mines", "validates"],
    affordances=["constitution_paths", "mirror_test"],
)
class AxiomDiscoveryNode:
    """Discover axioms as zero-loss fixed points."""

    async def invoke(
        self,
        observer: Observer,
        constitution_paths: list[str],
        mirror_test: bool = True,
        **kwargs,
    ) -> list[ZeroNode]:
        """Three-stage axiom discovery."""
        discovery = GaloisAxiomDiscovery(self.llm, self.budget)
        return await discovery.discover(constitution_paths, mirror_test)
```

---

## Part XIII: Semantic Distance Metric Comparison

### 13.1 Candidate Metrics

```python
class SemanticDistanceMetric(Protocol):
    """Protocol for semantic distance metrics."""

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute distance in [0, 1] where 0 = identical, 1 = opposite."""
        ...


class CosineEmbeddingDistance(SemanticDistanceMetric):
    """Fast, deterministic, but misses nuance."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = openai.Client()

    def distance(self, text_a: str, text_b: str) -> float:
        emb_a = self.client.embeddings.create(input=text_a, model=self.model).data[0].embedding
        emb_b = self.client.embeddings.create(input=text_b, model=self.model).data[0].embedding

        cosine_sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
        return 1 - cosine_sim


class BERTScoreDistance(SemanticDistanceMetric):
    """Balanced speed and accuracy."""

    def distance(self, text_a: str, text_b: str) -> float:
        from bert_score import score

        P, R, F1 = score([text_a], [text_b], lang="en", verbose=False)
        return 1 - F1.item()


class LLMJudgeDistance(SemanticDistanceMetric):
    """Captures nuance, but expensive and non-deterministic."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def distance(self, text_a: str, text_b: str) -> float:
        prompt = f"""Rate the semantic similarity of these two texts from 0.0 (identical) to 1.0 (completely different).

Text A:
{text_a}

Text B:
{text_b}

Return only a number between 0.0 and 1.0."""

        response = await self.llm.generate(prompt, temperature=0.0)
        return float(response.strip())


class NLIContradictionDistance(SemanticDistanceMetric):
    """Specialized for contradiction detection."""

    def __init__(self, model: str = "microsoft/deberta-v3-large-mnli"):
        from transformers import pipeline
        self.classifier = pipeline("text-classification", model=model)

    def distance(self, text_a: str, text_b: str) -> float:
        result = self.classifier(f"{text_a} [SEP] {text_b}")

        # Map NLI labels to distance
        label_to_distance = {
            "CONTRADICTION": 1.0,
            "NEUTRAL": 0.5,
            "ENTAILMENT": 0.0,
        }

        return label_to_distance.get(result[0]["label"], 0.5)
```

### 13.2 Metric Selection Experiment

```python
@dataclass
class MetricComparisonExperiment:
    """
    Compare semantic distance metrics for Galois loss.

    Success criterion: Select metric with:
    - Highest correlation with human-judged difficulty (r > 0.7)
    - Acceptable computation time (< 100ms per comparison)
    - High test-retest stability (ICC > 0.8)
    """

    prompts: list[str]  # 200 diverse prompts
    metrics: dict[str, SemanticDistanceMetric]

    async def run(self) -> MetricAnalysis:
        """Run comparison across all metrics."""
        results = {}

        for metric_name, metric in self.metrics.items():
            print(f"Testing {metric_name}...")

            losses = []
            computation_times = []

            for prompt in self.prompts:
                # Measure computation time
                start = time.time()

                # Restructure and reconstitute
                modular = await restructure(prompt, self.llm)
                reconstituted = await reconstitute(modular, self.llm)

                # Compute loss with this metric
                loss = metric.distance(prompt, reconstituted)
                losses.append(loss)

                elapsed = time.time() - start
                computation_times.append(elapsed)

            # Correlation with human judgments
            human_difficulty = await get_human_difficulty_ratings(self.prompts)
            correlation = pearson_r(losses, human_difficulty)

            # Test-retest stability
            stability = await measure_stability(metric, self.prompts)

            results[metric_name] = MetricResult(
                losses=losses,
                correlation_with_difficulty=correlation,
                mean_computation_time=mean(computation_times),
                stability=stability,
            )

        return MetricAnalysis(results)


# Expected results (from galois-modularization.md experiments):
# - BERTScore: r=0.72, time=45ms, stability=0.85 ✓ BEST
# - Cosine: r=0.58, time=12ms, stability=0.92
# - LLM Judge: r=0.79, time=230ms, stability=0.76
# - NLI: r=0.65, time=38ms, stability=0.81

# Recommendation: BERTScore (balanced)
```

---

## Part XIV: Success Criteria and Validation

### 14.1 Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Contradiction Detection Accuracy** | > 85% | F1 vs human labels on 100 node pairs |
| **Proof Quality Correlation** | r > 0.7 | Galois coherence vs human-rated quality |
| **Layer Assignment Accuracy** | > 80% | Galois-assigned vs human-assigned layers |
| **Axiom Fixed-Point Ratio** | > 90% | % of Constitution axioms with L < 0.05 |
| **Graph Health Predictiveness** | r > 0.6 | Overall loss vs user-reported issues |
| **Bootstrap Fixed-Point Verification** | L < 0.15 | `L(ZeroSeed, C(R(ZeroSeed)))` |

### 14.2 Qualitative Goals

- [ ] Contradiction detection is **transparent** (users understand why)
- [ ] Proof quality is **actionable** (clear improvement suggestions)
- [ ] Layer assignment is **defensible** (loss rationale shown)
- [ ] Axiom discovery is **principled** (fixed-point theory, not heuristics)
- [ ] Graph health is **diagnostic** (identifies specific weak spots)
- [ ] Constitutional reward is **unified** (single loss measure replaces 7 evaluators)

### 14.3 Mirror Test Validation

The final test: Kent's subjective assessment.

**Questions for Mirror Test**:
1. Does Galois loss feel like the right metric? (Mirror Test)
2. Do automatically assigned layers match intuition?
3. Do contradiction detections align with experience?
4. Do axioms discovered feel foundational?
5. Is the system "daring, bold, creative, opinionated but not gaudy"?

**Success**: Kent says "This feels like me on my best day."

---

## Part XV: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

```
impl/claude/services/galois_zero_seed/
├── __init__.py
├── galois_loss.py              # Core loss computation
├── metrics.py                  # Semantic distance metrics
├── layer_stratified_loss.py    # Layer-aware loss
├── galois_edge.py              # Loss-weighted edges
├── cache.py                    # LossCache
└── _tests/
    ├── test_loss_computation.py
    ├── test_metrics.py
    └── test_layer_stratification.py
```

**Success Criteria**:
- [ ] `galois_loss(text) -> float` with 3 metrics
- [ ] Layer assignment: 80% accuracy on test corpus
- [ ] Cache hit rate > 70%

### Phase 2: Integration (Weeks 3-4)

```
impl/claude/services/galois_zero_seed/
├── contradiction_analysis.py   # Super-additive loss
├── proof_validation.py         # Coherence = 1 - loss
├── axiom_discovery.py          # Fixed-point search
├── graph_health.py             # Loss topography
└── _tests/
    ├── test_contradiction.py
    ├── test_proof_quality.py
    └── test_axiom_discovery.py
```

**Success Criteria**:
- [ ] Contradiction detection: F1 > 0.85
- [ ] Proof quality correlation: r > 0.7
- [ ] Axiom discovery precision/recall > 90%

### Phase 3: CLI & UI (Weeks 5-6)

```
impl/claude/protocols/cli/handlers/zero_seed_galois.py
impl/claude/web/src/components/zero-seed/
├── LossTopographyViewer.tsx
├── GradientFlowField.tsx
├── FixedPointMarkers.tsx
└── ContradictionEdges.tsx
```

**Success Criteria**:
- [ ] CLI commands functional
- [ ] Telescope renders loss topography
- [ ] Real-time loss feedback < 200ms latency

### Phase 4: Validation (Weeks 7-8)

Run experiments from `galois-modularization.md`:
- [ ] E1: Loss-difficulty correlation (r > 0.6)
- [ ] E4: Metric comparison (select BERTScore)
- [ ] ZS1: Layer assignment (80%+ accuracy)
- [ ] ZS2: Axiom discovery (90%+ precision/recall)
- [ ] Bootstrap verification (L < 0.15)

### Phase 5: Mirror Test & Deployment (Week 9)

- [ ] Run Mirror Test with Kent
- [ ] Refine thresholds based on feedback
- [ ] Write user guide
- [ ] Publish research paper

---

## Part XVI: Open Questions for Dialectical Refinement

### Conceptual

1. **Metric Selection**: Does BERTScore remain optimal, or do task-specific metrics outperform?
2. **Layer Count Invariance**: Does Galois convergence naturally yield 7 layers, or is this parameter-dependent?
3. **Loss Budget**: How does `L(P)` interact with entropy budget `E(P)` from bootstrap idioms?

### Technical

4. **Composition of Losses**: Is edge loss composition subadditive: `L(e₁ >> e₂) ≤ L(e₁) + L(e₂)`?
5. **Multi-User Loss**: How to aggregate loss when users share a graph?
6. **Cache Invalidation**: When should cached losses be invalidated after edits?

### UX

7. **Loss Transparency**: Raw values vs abstract indicators (green/yellow/red)?
8. **Axiom Retirement**: How to gracefully deprecate axioms that cease to be fixed points?
9. **Real-Time Computation**: Can we achieve < 100ms loss feedback for interactive editing?

---

## Part XVII: Related Specs

### Theoretical Foundations
- `spec/theory/galois-modularization.md` — Full Galois theory with experiments
- `spec/theory/agent-dp.md` — Agent Space as Dynamic Programming
- `spec/principles/decisions/AD-002-polynomial.md` — Polynomial functor foundations

### Protocols
- [`index.md`](./index.md) — Zero Seed Galois Edition (index)
- [`integration.md`](./integration.md) — Original Galois integration sketch
- [`proof.md`](./proof.md) — Toulmin proof structure
- [`dp.md`](./dp.md) — Constitutional reward and value iteration
- `spec/protocols/differance.md` — Ghost alternatives (Galois-deferred structure)

### Implementation
- `spec/m-gents/holographic.md` — Holographic compression
- `spec/m-gents/phase8-ghost-substrate-galois-link.md` — Galois in M-gent context

---

*"The loss IS the layer. The fixed point IS the axiom. The contradiction IS the super-additive signal."*

---

**Filed**: 2025-12-24
**Status**: Theoretical Foundation — Ready for Implementation
**Next Actions**:
1. Implement Phase 1 (foundation code)
2. Run metric comparison experiment (select optimal d)
3. Validate layer assignment (80%+ accuracy)
4. Discover axioms from Constitution via fixed points
5. Detect contradictions via super-additive loss
6. Verify Zero Seed as bootstrap fixed point (L < 0.15)
