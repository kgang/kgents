# Zero Seed × Galois Modularization: Integration

> *"The contradiction IS the super-additive signal. The ghost IS the deferred alternative. The edge IS the loss bridge."*

**Module**: Galois Integration
**Depends on**: [`core.md`](./core.md), [`proof.md`](./proof.md), `spec/theory/galois-modularization.md`
**Status**: Radical Upgrade — Quantitative Foundations
**Date**: 2025-12-24

---

## Abstract

This spec integrates Galois Modularization Theory with Zero Seed to provide **quantitative grounding** for:

1. **Contradiction detection** via super-additive loss (not LLM heuristics)
2. **Proof quality** as inverse Galois loss (measurable coherence)
3. **Layer assignment** via loss minimization (not manual stipulation)
4. **Axiom discovery** as fixed-point computation (zero-loss nodes)
5. **Graph health** via loss topography (weak edges = high loss)
6. **Edge strength** annotated with Galois loss (grounding quality)

**The Core Unification**: Zero Seed layers ARE Galois depth strata. Moving down layers = restructuring (abstraction). Moving up layers = reconstitution (concretization). Contradiction = semantic incompatibility measured by super-additive loss.

---

## Part I: The Galois-Zero Seed Isomorphism

### 1.1 Conceptual Mapping

| Zero Seed Concept | Galois Equivalent | Unification |
|-------------------|-------------------|-------------|
| Layer (L1-L7) | Galois depth | Layer = # restructurings to fixed point |
| Axiom (L1) | Zero-loss fixed point | L(axiom) ≈ 0 by definition |
| Proof coherence | Inverse Galois loss | coherence = 1 - L(proof) |
| Contradiction | Super-additive loss | L(a ∪ b) > L(a) + L(b) |
| Edge strength | Grounding via loss | strength = 1 - L(edge) |
| Constitutional reward | Structure preservation | R(s,a,s') = 1 - L(transition) |
| Bootstrap paradox | Lawvere fixed point | Zero Seed = Fix(R ∘ describe) |
| Ghost alternatives | Deferred restructurings | Différance ≅ Galois ghosts |

### 1.2 The Unified Value Function

The DP value function for Zero Seed navigation becomes:

```python
V*(node) = max_edge [
    Σᵢ wᵢ · Principleᵢ(node, edge, target) - λ · L(node → target)
]

where:
    V*(node) = optimal value of being at this node
    Principleᵢ = the 7 constitutional principles
    L(node → target) = Galois loss of the edge
    λ = loss penalty weight (default: 0.3)
```

**Key Insight**: Constitutional principles and Galois loss are **dual objectives**—principles maximize semantic quality, loss minimizes structure degradation.

---

## Part II: Contradiction as Super-Additive Loss

### 2.1 The Quantitative Definition

**Original Problem** (from feedback): Zero Seed detects contradiction via LLM heuristics. This is non-deterministic and expensive.

**Galois Solution**: Contradiction is **super-additive Galois loss**.

```python
def is_contradiction(a: ZeroNode, b: ZeroNode, tolerance: float = 0.05) -> bool:
    """
    Two nodes contradict if combining them loses more than the sum.

    This is a quantitative, measurable definition of semantic incompatibility.
    """
    loss_a = galois_loss(a.content)
    loss_b = galois_loss(b.content)
    loss_combined = galois_loss(f"{a.content}\n\n{b.content}")

    # Super-additivity indicates semantic incompatibility
    return loss_combined > loss_a + loss_b + tolerance
```

### 2.2 Contradiction Strength

The degree of contradiction is the **excess loss**:

```python
def contradiction_strength(a: ZeroNode, b: ZeroNode) -> float:
    """
    Measure how strongly two nodes contradict.

    Returns:
        > 0: Contradiction (super-additive)
        ≈ 0: Independent (additive)
        < 0: Synergistic (sub-additive)
    """
    loss_a = galois_loss(a.content)
    loss_b = galois_loss(b.content)
    loss_combined = galois_loss(f"{a.content}\n\n{b.content}")

    return loss_combined - (loss_a + loss_b)
```

**Interpretation**:
- `strength > 0.2`: Strong contradiction (nodes resist joint modularization)
- `strength ≈ 0`: Independent nodes (losses are additive)
- `strength < -0.1`: Synergistic nodes (combining REDUCES loss)

### 2.3 Synthesis Hint from Ghost Alternatives

When contradiction is detected, the ghost alternatives provide synthesis hints:

```python
@dataclass
class ContradictionAnalysis:
    """Analysis of contradiction via Galois loss."""

    node_a: ZeroNode
    node_b: ZeroNode
    strength: float                    # Super-additive excess
    loss_a: float
    loss_b: float
    loss_combined: float

    # Ghost alternatives from restructuring
    ghost_alternatives: list[Alternative]

    @property
    def synthesis_hint(self) -> Alternative | None:
        """
        The ghost alternative closest to both nodes.

        This is the "middle path" that resolves the contradiction.
        """
        if not self.ghost_alternatives:
            return None

        # Find alternative with minimal combined distance
        def distance_to_both(alt: Alternative) -> float:
            d_a = semantic_distance(alt.content, self.node_a.content)
            d_b = semantic_distance(alt.content, self.node_b.content)
            return d_a + d_b

        return min(self.ghost_alternatives, key=distance_to_both)

    def to_dialectic_fusion(self) -> DialecticFusion | None:
        """
        Convert to Dialectic Fusion structure.

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
            metadata={
                "contradiction_strength": self.strength,
                "galois_loss_a": self.loss_a,
                "galois_loss_b": self.loss_b,
                "galois_loss_combined": self.loss_combined,
            }
        )
```

### 2.4 Implementation

```python
async def detect_contradiction_galois(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ContradictionAnalysis:
    """
    Detect contradiction using Galois loss.

    Uses Analyst tier (sonnet) for restructuring operations.
    ~600 tokens per analysis.
    """
    # Compute individual losses
    loss_a = await galois_loss(node_a.content, llm)
    loss_b = await galois_loss(node_b.content, llm)

    # Compute combined loss
    combined_content = f"{node_a.title}:\n{node_a.content}\n\n{node_b.title}:\n{node_b.content}"

    # Get restructuring with ghost alternatives
    modular = await restructure_with_ghosts(combined_content, llm, n_ghosts=5)
    reconstituted = await reconstitute(modular, llm)
    loss_combined = semantic_distance(combined_content, reconstituted)

    # Compute contradiction strength
    strength = loss_combined - (loss_a + loss_b)

    # Extract ghost alternatives
    ghost_alternatives = [
        Alternative(
            content=await reconstitute(ghost, llm),
            loss=semantic_distance(combined_content, await reconstitute(ghost, llm)),
        )
        for ghost in modular.ghosts
    ]

    # Create witness mark
    call_mark = LLMCallMark(
        tier=LLMTier.ANALYST,
        operation="contradiction_detection_galois",
        prompt_summary=f"Analyze {node_a.title} vs {node_b.title}",
        response_summary=f"Strength: {strength:.3f}",
        input_tokens=estimate_tokens(combined_content),
        output_tokens=500,
        total_tokens=estimate_tokens(combined_content) + 500,
        estimated_cost_usd=0.003,  # Analyst pricing
        node_ids=(node_a.id, node_b.id),
    )
    budget.track(call_mark)

    return ContradictionAnalysis(
        node_a=node_a,
        node_b=node_b,
        strength=strength,
        loss_a=loss_a,
        loss_b=loss_b,
        loss_combined=loss_combined,
        ghost_alternatives=ghost_alternatives,
    )
```

---

## Part III: Proof Quality as Inverse Galois Loss

### 3.1 The Metric

**Original Problem**: Toulmin proofs have qualitative coherence, but no quantitative measure.

**Galois Solution**: `proof_quality(proof) = 1 - galois_loss(proof)`

```python
async def validate_proof_galois(
    proof: Proof,
    node: ZeroNode,
    llm: LLMClient,
    budget: TokenBudget,
) -> ProofValidation:
    """
    Validate Toulmin proof using Galois loss.

    Uses Scout tier (haiku) for fast validation.
    ~250 tokens per proof.
    """
    # Construct proof text
    proof_text = f"""
Data: {proof.data}
Warrant: {proof.warrant}
Claim: {proof.claim}
Backing: {proof.backing}
Qualifier: {proof.qualifier}
Rebuttals: {', '.join(proof.rebuttals)}
"""

    # Compute Galois loss
    loss = await galois_loss(proof_text, llm)
    coherence = 1.0 - loss

    # Classify tier by loss
    if loss < 0.1:
        tier = EvidenceTier.CATEGORICAL  # Near-lossless = deductive
    elif loss < 0.3:
        tier = EvidenceTier.EMPIRICAL  # Moderate loss = empirical
    else:
        tier = EvidenceTier.SOMATIC  # High loss = intuitive

    # Generate issues if loss is high
    issues = []
    if loss > 0.2:
        issues.append("Proof structure doesn't survive modularization")
    if loss > 0.4:
        issues.append("Warrant-claim linkage is weak")
    if loss > 0.6:
        issues.append("Data doesn't support warrant")

    # Track LLM call
    call_mark = LLMCallMark(
        tier=LLMTier.SCOUT,
        operation="proof_validation_galois",
        prompt_summary=proof_text[:100],
        response_summary=f"Coherence: {coherence:.2f}",
        input_tokens=250,
        output_tokens=50,
        total_tokens=300,
        estimated_cost_usd=0.00008,  # Haiku pricing
        node_ids=(node.id,),
    )
    budget.track(call_mark)

    return ProofValidation(
        coherence=coherence,
        tier=tier,
        issues=issues,
        llm_validated=True,
        galois_loss=loss,
    )
```

### 3.2 Loss Decomposition

Break down where loss comes from in the proof:

```python
async def decompose_proof_loss(
    proof: Proof,
    llm: LLMClient,
) -> dict[str, float]:
    """
    Decompose Galois loss by proof component.

    Returns dict mapping component → loss contribution.
    """
    components = {
        "data": proof.data,
        "warrant": proof.warrant,
        "claim": proof.claim,
        "backing": proof.backing,
    }

    # Baseline loss (full proof)
    full_loss = await galois_loss(format_proof(proof), llm)

    # Ablation: remove each component and measure change
    loss_decomposition = {}
    for name, content in components.items():
        # Create proof without this component
        ablated = proof.without(name)
        ablated_loss = await galois_loss(format_proof(ablated), llm)

        # Loss contribution = how much loss INCREASES when removed
        contribution = ablated_loss - full_loss
        loss_decomposition[name] = contribution

    return loss_decomposition
```

### 3.3 Galois-Witnessed Proof

Extend Toulmin proof with Galois annotations:

```python
@dataclass(frozen=True)
class GaloisWitnessedProof(Proof):
    """Toulmin proof with Galois loss annotations."""

    # Standard Toulmin fields (inherited)
    # data: str
    # warrant: str
    # claim: str
    # backing: str
    # qualifier: str
    # rebuttals: tuple[str, ...]
    # tier: EvidenceTier
    # principles: tuple[str, ...]

    # Galois-specific extensions
    galois_loss: float                     # Total loss
    coherence: float                       # 1 - loss
    loss_decomposition: dict[str, float]   # Where loss came from
    ghost_alternatives: tuple[Alternative, ...]  # Deferred proof paths

    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """
        Generate rebuttals from loss sources.

        High-loss components become rebuttals.
        """
        loss_rebuttals = []
        for component, loss_contrib in self.loss_decomposition.items():
            if loss_contrib > 0.1:
                loss_rebuttals.append(
                    f"Unless {component} is strengthened (contributes {loss_contrib:.2f} loss)"
                )

        # Combine with manual rebuttals
        return self.rebuttals + tuple(loss_rebuttals)

    @property
    def is_strong(self) -> bool:
        """Strong proof = low Galois loss."""
        return self.galois_loss < 0.2

    def suggest_improvements(self) -> list[str]:
        """Suggest improvements based on loss decomposition."""
        suggestions = []

        # Sort components by loss (highest first)
        sorted_components = sorted(
            self.loss_decomposition.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for component, loss in sorted_components[:2]:  # Top 2 offenders
            if loss > 0.15:
                suggestions.append(f"Strengthen {component} (current loss: {loss:.2f})")

        # Suggest ghost alternatives if available
        if self.ghost_alternatives:
            best_ghost = min(self.ghost_alternatives, key=lambda g: g.loss)
            if best_ghost.loss < self.galois_loss:
                suggestions.append(
                    f"Consider alternative formulation (would reduce loss to {best_ghost.loss:.2f})"
                )

        return suggestions
```

---

## Part IV: Layer Assignment via Loss Minimization

### 4.1 The Algorithm

**Original Problem**: Layer assignment is manual, requiring user to choose L1-L7.

**Galois Solution**: Layer = depth where loss is minimized.

```python
async def assign_layer_via_galois(
    content: str,
    graph: ZeroGraph,
    llm: LLMClient,
    budget: TokenBudget,
) -> LayerAssignment:
    """
    Assign content to the layer where it has minimal loss.

    Uses Scout tier for fast loss computation across layers.
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
    call_mark = LLMCallMark(
        tier=LLMTier.SCOUT,
        operation="layer_assignment_galois",
        prompt_summary=content[:100],
        response_summary=f"Assigned to L{best_layer} (loss: {best_loss:.2f})",
        input_tokens=1400,
        output_tokens=100,
        total_tokens=1500,
        estimated_cost_usd=0.0004,  # Haiku pricing
        node_ids=(),
    )
    budget.track(call_mark)

    return LayerAssignment(
        layer=best_layer,
        loss=best_loss,
        loss_by_layer=losses,
        confidence=confidence,
        insight=f"Content naturally lives at L{best_layer} ({LAYER_NAMES[best_layer]})",
        rationale=explain_layer_choice(best_layer, losses),
    )
```

### 4.2 Layer-Stratified Loss Semantics

Each layer has its own loss interpretation:

```python
@dataclass
class LayerStratifiedLoss:
    """Galois loss with layer-aware semantics."""

    graph: ZeroGraph
    llm: LLMClient

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
        Loss for goals = how much value-justification is lost.

        Goals should be grounded in values (L2). Loss measures
        how well the goal preserves value semantics.
        """
        # Get justifying values
        justifying_edges = self.graph.edges_to(node.id, kind=EdgeKind.JUSTIFIES)

        if not justifying_edges:
            return 1.0  # Unjustified goal = total loss

        # Compute grounding strength
        grounding_strengths = []
        for edge in justifying_edges:
            value_node = self.graph.get_node(edge.source)
            # Loss = how much semantics is lost in value → goal transition
            combined = f"{value_node.content}\n\nTherefore: {node.content}"
            loss = await galois_loss(combined, self.llm)
            grounding_strengths.append(1.0 - loss)

        # Average grounding strength
        return 1.0 - mean(grounding_strengths)

    async def _spec_loss(self, node: ZeroNode) -> float:
        """
        Loss for specs = how much goal intent is lost.

        Specs should preserve goal intent. Loss measures
        unimplementable or unspecified portions.
        """
        # Get specifying goals
        specifying_edges = self.graph.edges_to(node.id, kind=EdgeKind.SPECIFIES)

        if not specifying_edges:
            return 0.5  # Spec without goal = moderate loss

        # Measure goal → spec preservation
        preservation_scores = []
        for edge in specifying_edges:
            goal_node = self.graph.get_node(edge.source)
            combined = f"Goal: {goal_node.content}\n\nSpec: {node.content}"
            loss = await galois_loss(combined, self.llm)
            preservation_scores.append(1.0 - loss)

        return 1.0 - mean(preservation_scores)

    # Similar for other layers...
```

---

## Part V: Axiom Discovery as Fixed-Point Finding

### 5.1 Zero-Loss Fixed Points

**Original Problem**: Axiom discovery is a three-stage heuristic (mining, Mirror Test, corpus).

**Galois Upgrade**: Axioms ARE zero-loss fixed points under restructuring.

```python
class GaloisAxiomDiscovery:
    """Axiom discovery via Galois fixed-point finding."""

    def __init__(self, llm: LLMClient, budget: TokenBudget):
        self.llm = llm
        self.budget = budget
        self.fixed_point_threshold = 0.05  # L < 0.05 = near-fixed point

    async def discover(
        self,
        constitution_paths: list[str],
    ) -> list[ZeroNode]:
        """
        Three-stage discovery with Galois grounding.

        Stage 1: Find zero-loss fixed points (axioms)
        Stage 2: Mirror Test as human loss oracle
        Stage 3: Living corpus as empirical loss validation
        """
        # Stage 1: Find candidates that are fixed points of restructuring
        candidates = []

        for path in constitution_paths:
            content = await read_file(path)
            statements = extract_principle_statements(content)

            for stmt in statements:
                # Check if statement is a fixed point
                loss = await self._compute_fixed_point_loss(stmt.text)

                if loss < self.fixed_point_threshold:
                    candidates.append(CandidateAxiom(
                        text=stmt.text,
                        source_path=path,
                        source_line=stmt.line,
                        galois_loss=loss,
                        is_fixed_point=loss < 0.01,
                        tier=EvidenceTier.SOMATIC,  # From constitution
                    ))

        # Sort by loss (lowest first = most axiomatic)
        candidates.sort(key=lambda c: c.galois_loss)

        # Stage 2: Mirror Test filters by human loss oracle
        axioms = await self._mirror_test_filter(candidates)

        # Stage 3: Validate against living corpus
        axioms = await self._corpus_validation(axioms)

        return axioms

    async def _compute_fixed_point_loss(self, text: str) -> float:
        """
        Compute loss for a potential axiom.

        Axiom = content that survives restructuring unchanged.
        """
        # Restructure
        modular = await restructure(text, self.llm)

        # Reconstitute
        reconstituted = await reconstitute(modular, self.llm)

        # Measure loss
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
            # Present candidate with loss
            response = await ask_user(
                question=f"""Does this feel true for you on your best day?

> {candidate.text}

Galois Loss: {candidate.galois_loss:.3f} (lower = more axiomatic)
Fixed Point: {'Yes' if candidate.is_fixed_point else 'Near'}

[Accept] [Reframe] [Skip]
""",
            )

            match response:
                case "Accept":
                    accepted.append(create_axiom_node(
                        candidate,
                        confidence=1.0 - candidate.galois_loss,
                    ))

                case "Reframe":
                    reframed = await ask_user("How would you say it?")
                    reframed_loss = await self._compute_fixed_point_loss(reframed)
                    accepted.append(create_axiom_node(
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
```

**Key Insight**: Axioms (L1) have `galois_loss ≈ 0` by definition. They are the irreducible content that cannot be compressed further—the fixed points of restructuring.

---

## Part VI: Graph Health via Loss Topography

### 6.1 Loss-Weighted Edges

Every edge carries a Galois loss annotation:

```python
@dataclass(frozen=True)
class GaloisEdge(ZeroEdge):
    """Zero Seed edge with Galois loss annotation."""

    # Inherited from ZeroEdge:
    # id: EdgeId
    # source: NodeId
    # target: NodeId
    # kind: EdgeKind
    # context: str
    # confidence: float
    # created_at: datetime
    # mark_id: MarkId
    # is_resolved: bool
    # resolution_id: NodeId | None

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
        """
        Weak edges are candidates for reinforcement.

        Default threshold: loss > 0.5 = weak
        """
        return self.galois_loss > threshold

    def should_flag(self) -> bool:
        """Flag edges with very high loss for user attention."""
        return self.galois_loss > 0.7
```

### 6.2 Graph Health Report

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
            issues.append(f"Overall loss ({self.overall_loss:.2f}) is very high")

        if len(self.weak_edges) > 10:
            issues.append(f"{len(self.weak_edges)} weak edges need reinforcement")

        for region in self.unstable_regions:
            if region.aggregate_loss > 0.6:
                issues.append(
                    f"Unstable region with {len(region.nodes)} nodes (loss: {region.aggregate_loss:.2f})"
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
        loss = await compute_edge_loss(edge, graph, galois)

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
    overall_loss = mean([
        await galois.compute(n)
        for n in graph.nodes
        if n.layer > 2  # Exclude axioms/values
    ])

    return GraphHealthReport(
        weak_edges=weak_edges,
        high_loss_nodes=high_loss_nodes,
        unstable_regions=unstable_regions,
        overall_loss=overall_loss,
    )
```

### 6.3 Loss Topography Visualization

Extend the Telescope UI to show loss landscape:

```python
@dataclass
class LossTopographyTelescope(TelescopeState):
    """Telescope that visualizes Galois loss landscape."""

    # Inherited from TelescopeState:
    # focal_distance: float
    # focal_point: NodeId | None

    # Loss visualization
    show_loss: bool = True
    loss_colormap: str = "viridis"  # Low loss = cool (blue), high loss = hot (red)
    show_gradient_field: bool = False

    def project_node(
        self,
        node: ZeroNode,
        galois: LayerStratifiedLoss,
    ) -> NodeProjection:
        """Project node with loss-based coloring."""
        base = super().project_node(node)

        if self.show_loss and node.layer > 2:
            loss = galois.compute_cached(node)  # Use cached to avoid recomputation

            # Color by loss
            base.color = colormap_sample(self.loss_colormap, loss)

            # Glow for very high loss
            if loss > 0.7:
                base.glow = True
                base.glow_intensity = loss

        return base

    def loss_gradient_field(
        self,
        nodes: list[ZeroNode],
        galois: LayerStratifiedLoss,
    ) -> VectorField:
        """
        Compute gradient flow toward low-loss regions.

        Each vector points in the direction of steepest loss decrease.
        """
        vectors = {}

        for node in nodes:
            if node.layer <= 2:
                continue  # No gradient for axioms

            # Compute gradient (approximate via finite differences)
            gradient = compute_loss_gradient(node, galois)

            # Negate to point toward LOW loss
            vectors[node.id] = -gradient

        return VectorField(vectors=vectors)
```

---

## Part VII: Ghost Graph as Contradiction Space

### 7.1 Galois Ghost Graph

For any node, the ghost alternatives form a graph of deferred restructurings:

```python
def ghost_graph(node: ZeroNode, llm: LLMClient, n: int = 10) -> GhostGraph:
    """
    Generate Galois ghost graph for a node.

    Nodes = actual + ghost alternatives
    Edges = weighted by semantic distance (Galois loss)

    This IS the Différance ghost heritage graph.
    """
    # Sample n alternative restructurings
    alternatives = await sample_restructurings(node.content, llm, n=n)

    # All nodes (actual + ghosts)
    nodes = [node] + alternatives

    # Compute pairwise Galois losses
    edges = []
    for a, b in combinations(nodes, 2):
        loss = await galois_loss_between(a, b, llm)
        edges.append(GhostEdge(
            source=a,
            target=b,
            galois_loss=loss,
            is_actual=a == node or b == node,
        ))

    return GhostGraph(
        actual_node=node,
        ghost_nodes=alternatives,
        edges=edges,
    )
```

### 7.2 Contradiction as Ghost Cluster

When two nodes contradict, they appear as **disconnected clusters** in the joint ghost graph:

```python
async def contradiction_via_ghost_graph(
    node_a: ZeroNode,
    node_b: ZeroNode,
    llm: LLMClient,
) -> ContradictionAnalysis:
    """
    Detect contradiction by analyzing ghost graph structure.

    Contradiction ⟺ nodes are in disconnected ghost clusters.
    """
    # Generate joint ghost graph
    ghost_a = await ghost_graph(node_a, llm, n=5)
    ghost_b = await ghost_graph(node_b, llm, n=5)

    # Merge graphs
    joint_graph = merge_ghost_graphs(ghost_a, ghost_b)

    # Find connected components
    components = find_connected_components(joint_graph, threshold=0.4)

    # Check if a and b are in different components
    component_a = find_component(components, node_a)
    component_b = find_component(components, node_b)

    if component_a != component_b:
        # Nodes are in different clusters = contradiction

        # Find bridge ghosts (closest nodes in different clusters)
        bridge_ghosts = find_bridge_nodes(
            component_a,
            component_b,
            joint_graph,
        )

        return ContradictionAnalysis(
            node_a=node_a,
            node_b=node_b,
            strength=compute_cluster_distance(component_a, component_b),
            ghost_alternatives=bridge_ghosts,  # These are synthesis hints
            resolution_type="ghost_bridge",
        )
    else:
        # Same cluster = compatible
        return ContradictionAnalysis(
            node_a=node_a,
            node_b=node_b,
            strength=0.0,
            ghost_alternatives=[],
            resolution_type="compatible",
        )
```

**Key Insight**: The Galois ghost graph IS the Différance ghost heritage. Contradiction is cluster separation. Synthesis is the bridge ghost.

---

## Part VIII: Integration with Existing Systems

### 8.1 AGENTESE Context Mapping (Preserved)

The AGENTESE mapping from the original integration.md is preserved:

| AGENTESE Context | Layers | Loss Semantics |
|------------------|--------|----------------|
| `void.*` | L1 + L2 | Zero loss by definition (axioms/values) |
| `concept.*` | L3 + L4 | Goal-justification + spec-implementability loss |
| `world.*` | L5 | Spec-deviation loss |
| `self.*` | L6 | Synthesis-gap loss |
| `time.*` | L7 | Meta-blindness loss |

### 8.2 Void Services (Unchanged)

Entropy pool, random oracle, and gratitude ledger remain unchanged from `integration.md`.

### 8.3 Edge Creation Modes (Enhanced)

Both modal and inline edge creation now include loss preview:

```markdown
EDGE MODE (e from NORMAL):
  1. Select edge type (g/j/s/i/r/p/d/c/y/x)

  2. Navigate to target node (gh/gl/gj/gk)

  3. **Preview loss** (NEW):
     ┌─────────────────────────────────────────┐
     │ Edge: JUSTIFIES                         │
     │ Source: void.value.composability        │
     │ Target: concept.goal.cultivate          │
     │                                         │
     │ Galois Loss: 0.12 (Low)                 │
     │ Grounding Strength: 0.88                │
     │ Estimated Quality: Strong               │
     └─────────────────────────────────────────┘

  4. Confirm (Enter) or cancel (Esc)
```

Inline annotations extract loss after save:

```python
async def extract_inline_edges_with_loss(
    content: str,
    source_node: ZeroNode,
    graph: ZeroGraph,
    galois: LayerStratifiedLoss,
) -> list[GaloisEdge]:
    """Extract edges from inline annotations with loss computation."""
    edges = []

    for match in EDGE_PATTERN.finditer(content):
        kind = EdgeKind(match.group(1))
        target_path = match.group(2)
        target_node = await resolve_path(target_path)

        if target_node:
            # Compute edge loss
            loss = await compute_edge_loss_direct(
                source_node,
                kind,
                target_node,
                galois,
            )

            edges.append(GaloisEdge(
                id=generate_edge_id(),
                source=source_node.id,
                target=target_node.id,
                kind=kind,
                context=f"Inline annotation in {source_node.path}",
                confidence=1.0 - loss,  # Confidence = grounding strength
                created_at=datetime.now(UTC),
                mark_id=None,  # Will be set on save
                galois_loss=loss,
                loss_direction=infer_loss_direction(source_node.layer, target_node.layer),
                loss_decomposition=None,  # Computed lazily if requested
            ))

    return edges
```

---

## Part IX: CLI Integration

### 9.1 New Commands

```bash
# Analyze contradiction with Galois loss
kg zero-seed contradict <node-a-id> <node-b-id>
# Output:
# Contradiction Strength: 0.34 (moderate)
# Galois Loss: 0.67 (combined) vs 0.15 + 0.18 (separate)
# Super-additive excess: +0.34
# Synthesis hint: <ghost alternative content>

# Validate proof with Galois
kg zero-seed proof-quality <node-id>
# Output:
# Coherence: 0.78 (good)
# Galois Loss: 0.22
# Issues: None
# Suggestions: Strengthen backing (contributes 0.15 loss)

# Assign layer automatically
kg zero-seed assign-layer "Content here..."
# Output:
# Assigned to L3 (Goals)
# Galois Loss: 0.18
# Confidence: 0.82
# Loss by layer: {1: 0.85, 2: 0.62, 3: 0.18, 4: 0.34, ...}

# Discover axioms via fixed points
kg zero-seed discover-axioms spec/principles/CONSTITUTION.md
# Output:
# Found 5 zero-loss fixed points:
#   1. "Tasteful > feature-complete" (loss: 0.01)
#   2. "The Mirror Test" (loss: 0.02)
#   ...

# Graph health via loss topography
kg zero-seed health
# Output:
# Overall Loss: 0.28 (healthy)
# Weak Edges: 3 (threshold: loss > 0.5)
# High-Loss Nodes: 1
# Unstable Regions: 0

# Show ghost graph for node
kg zero-seed ghosts <node-id>
# Generates ghost graph with 10 alternatives
# Shows loss-weighted edges between actual and ghosts
```

### 9.2 Telescope UI Commands

```bash
# Toggle loss visualization
:toggle-loss

# Show gradient field
:show-gradients

# Navigate to lowest-loss node
:goto-min-loss

# Highlight high-loss regions
:highlight-loss 0.6
```

---

## Part X: Performance Considerations

### 10.1 LLM Call Budget

Galois operations are LLM-intensive. Budget management:

| Operation | Tier | Tokens | Cost (USD) | Batching |
|-----------|------|--------|------------|----------|
| Contradiction detection | Analyst | ~600 | ~$0.002 | No (user-initiated) |
| Proof validation | Scout | ~300 | ~$0.0001 | Yes (batch on save) |
| Layer assignment | Scout | ~1400 | ~$0.0004 | No (one-time per node) |
| Axiom discovery | Scout | ~500/candidate | ~$0.0002 | Yes (batch all candidates) |
| Ghost graph generation | Analyst | ~800 | ~$0.003 | No (user-initiated) |
| Edge loss computation | Scout | ~200 | ~$0.00005 | Yes (batch edges) |

**Liberal Budget Philosophy**: With 500k token standard sessions, we can afford:
- ~800 contradiction analyses
- ~1600 proof validations
- ~350 layer assignments

This enables **comprehensive analysis** without nickel-and-diming.

### 10.2 Caching Strategy

```python
@dataclass
class GaloisLossCache:
    """Cache Galois loss computations to avoid redundant LLM calls."""

    # Cache keyed by (content_hash, operation)
    cache: dict[tuple[str, str], float] = field(default_factory=dict)
    ttl: timedelta = timedelta(hours=1)

    def get(self, content: str, operation: str) -> float | None:
        """Get cached loss if available and fresh."""
        key = (hash_content(content), operation)

        if key in self.cache:
            loss, timestamp = self.cache[key]
            if datetime.now(UTC) - timestamp < self.ttl:
                return loss

        return None

    def set(self, content: str, operation: str, loss: float) -> None:
        """Cache loss computation."""
        key = (hash_content(content), operation)
        self.cache[key] = (loss, datetime.now(UTC))

    def invalidate(self, content: str) -> None:
        """Invalidate all cached losses for content."""
        content_hash = hash_content(content)
        keys_to_remove = [
            key for key in self.cache.keys()
            if key[0] == content_hash
        ]
        for key in keys_to_remove:
            del self.cache[key]
```

---

## Part XI: Success Criteria

### 11.1 Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Contradiction Detection Accuracy** | > 85% | Compare Galois super-additivity vs human judgment on 100 node pairs |
| **Proof Quality Correlation** | r > 0.7 | Galois coherence vs human-rated proof quality |
| **Layer Assignment Accuracy** | > 80% | Galois-assigned vs human-assigned layers |
| **Axiom Fixed-Point Ratio** | > 90% | Proportion of constitution axioms with L < 0.05 |
| **Graph Health Predictiveness** | r > 0.6 | Overall loss vs user-reported graph issues |

### 11.2 Qualitative Goals

- [ ] Contradiction detection is **transparent** (users understand why nodes contradict)
- [ ] Proof quality is **actionable** (users know how to improve low-coherence proofs)
- [ ] Layer assignment is **defensible** (users can see loss-by-layer rationale)
- [ ] Axiom discovery is **principled** (fixed-point theory, not heuristics)
- [ ] Graph health is **diagnostic** (identifies specific weak edges/regions)

---

## Part XII: Open Questions

1. **Optimal Loss Threshold**: What loss level distinguishes L1 from L2, L2 from L3, etc.?
2. **Ghost Sampling Strategy**: How many ghosts (n) balances cost vs coverage?
3. **Loss Metric Choice**: Which semantic distance (cosine, BERTScore, LLM-judge) works best?
4. **Caching Invalidation**: When should cached losses be invalidated?
5. **Human-in-Loop**: When should system ask user to override Galois assignments?

---

## Part XIII: Related Specs

- `spec/theory/galois-modularization.md` — Formal Galois theory foundations
- `spec/protocols/zero-seed.md` — Original Zero Seed spec
- `spec/protocols/zero-seed/proof.md` — Toulmin proof structure
- `spec/protocols/zero-seed/dp.md` — DP value function
- `spec/protocols/differance.md` — Ghost alternatives and trace monoid
- `spec/m-gents/phase8-ghost-substrate-galois-link.md` — Galois connections

---

*"The contradiction IS the super-additive signal. The ghost IS the deferred alternative. The edge IS the loss bridge."*

---

**Filed**: 2025-12-24
**Status**: Radical Upgrade — Quantitative Foundations
**Next Actions**:
1. Implement `galois_loss()` with multiple semantic distance metrics
2. Run contradiction detection experiments (Galois vs LLM-heuristic)
3. Validate proof coherence correlation (Galois vs human judgment)
4. Implement layer assignment and measure accuracy
5. Discover axioms from constitution via fixed points
6. Build loss topography telescope UI
