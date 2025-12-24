# Zero Seed Witness Integration: Galois-Grounded Traceability

> *"Every node creation is witnessed. Every edge traversal is marked. Every loss measurement is traced. The proof IS the walk."*

**Version**: 1.0
**Status**: Draft — Integration Specification
**Date**: 2025-12-24
**Principles**: Composable, Ethical, Generative, Tasteful
**Prerequisites**: `witness-primitives.md`, `galois-modularization.md`, `agent-dp.md`, `zero-seed/index.md`, `zero-seed/dp.md`

---

## Abstract

The Witness Protocol provides the audit and traceability foundation for Zero Seed operations. This specification defines how every Zero Seed operation—from axiom discovery to edge creation to proof validation—produces Witness marks with Galois loss annotations.

**The Unified Insight**: The DP PolicyTrace IS the Witness Walk. The Toulmin Proof IS the Mark metadata. The Galois loss IS the quality metric that makes witnessing tractable at scale.

This integration:
1. Extends `Mark` with `GaloisLossComponents` for Zero Seed operations
2. Maps Zero Seed navigation to `Walk` creation and advancement
3. Defines `WitnessMode` selection via Galois triage (low-loss → SINGLE, high-loss → LAZY)
4. Integrates LLM calls for Galois operations with witness budgets
5. Traces decision dialectics through Fusion marks
6. Establishes lineage chains from nodes to creation marks

**Key Innovation**: Galois loss makes witness triage automatic—important operations (low loss) get full witnessing, speculative operations (high loss) get lazy witnessing. No manual mode selection needed.

---

## Part I: Mark Extensions for Zero Seed

### 1.1 The ZeroSeedMark

```python
from dataclasses import dataclass
from typing import Optional
from claude.services.witness.mark import Mark, Stimulus, Response
from claude.services.categorical.galois_loss import GaloisLossComponents

@dataclass
class ZeroSeedMark(Mark):
    """
    Mark extended with Galois loss tracking for Zero Seed operations.

    Every Zero Seed operation produces a mark with:
    - Standard witness data (origin, stimulus, response, timestamp)
    - Galois loss breakdown (total + per-principle components)
    - Optional layer transition data
    - Constitutional scores

    The Galois loss enables automatic witness mode selection:
      - loss < 0.10 → WitnessMode.SINGLE (important, full trace)
      - loss < 0.30 → WitnessMode.SESSION (moderate, accumulated)
      - loss ≥ 0.30 → WitnessMode.LAZY (speculative, batched)
    """

    # Core Galois tracking
    galois_loss: float  # Total Galois loss [0, 1]
    loss_components: GaloisLossComponents  # Breakdown by principle

    # Optional Zero Seed specifics
    layer_transition: Optional[tuple[int, int]] = None  # (from_layer, to_layer)
    constitutional_scores: Optional[dict[str, float]] = None  # Principle → score

    # LLM tracking (if operation used LLM)
    llm_tier: Optional[str] = None  # "scout" | "analyst" | "architect"
    llm_tokens_input: int = 0
    llm_tokens_output: int = 0
    llm_latency_ms: float = 0.0

    def witness_mode(self) -> str:
        """
        Automatic witness mode selection via Galois triage.

        Low loss → important operation → full witnessing
        High loss → speculative operation → lazy witnessing
        """
        if self.galois_loss < 0.10:
            return "SINGLE"  # Important: low loss = high structure preservation
        elif self.galois_loss < 0.30:
            return "SESSION"  # Moderate: some loss but acceptable
        else:
            return "LAZY"  # Speculative: high loss = uncertain operation

    def is_important(self) -> bool:
        """Check if this operation merits immediate witnessing."""
        return self.galois_loss < 0.10

    def quality_grade(self) -> str:
        """Human-readable quality assessment."""
        if self.galois_loss < 0.05:
            return "A+ (Excellent)"
        elif self.galois_loss < 0.10:
            return "A (Very Good)"
        elif self.galois_loss < 0.20:
            return "B (Good)"
        elif self.galois_loss < 0.30:
            return "C (Acceptable)"
        else:
            return "D (Speculative)"

@dataclass
class GaloisLossComponents:
    """
    Breakdown of Galois loss by constitutional principle.

    Enables diagnostic analysis: which principle is violated most?
    """

    total: float  # Aggregate loss [0, 1]

    # Per-principle losses
    tasteful_loss: float = 0.0      # Bloat, unnecessary complexity
    composable_loss: float = 0.0    # Hidden coupling, interface violations
    generative_loss: float = 0.0    # Failed regeneration from lineage
    ethical_loss: float = 0.0       # Hidden safety risks
    joy_inducing_loss: float = 0.0  # Aesthetic coherence drift
    heterarchical_loss: float = 0.0 # Imposed rigidity
    curated_loss: float = 0.0       # Arbitrary changes, weak justification

    def dominant_violation(self) -> str:
        """Identify which principle has highest loss."""
        losses = {
            "TASTEFUL": self.tasteful_loss,
            "COMPOSABLE": self.composable_loss,
            "GENERATIVE": self.generative_loss,
            "ETHICAL": self.ethical_loss,
            "JOY_INDUCING": self.joy_inducing_loss,
            "HETERARCHICAL": self.heterarchical_loss,
            "CURATED": self.curated_loss,
        }
        return max(losses.items(), key=lambda x: x[1])[0]

    def to_dict(self) -> dict:
        """Serialize for storage/transmission."""
        return {
            "total": self.total,
            "tasteful_loss": self.tasteful_loss,
            "composable_loss": self.composable_loss,
            "generative_loss": self.generative_loss,
            "ethical_loss": self.ethical_loss,
            "joy_inducing_loss": self.joy_inducing_loss,
            "heterarchical_loss": self.heterarchical_loss,
            "curated_loss": self.curated_loss,
            "dominant_violation": self.dominant_violation(),
        }
```

### 1.2 Operation-Specific Mark Types

```python
@dataclass
class NodeCreationMark(ZeroSeedMark):
    """Mark for creating a new Zero Seed node."""

    node_id: str
    node_layer: int
    node_kind: str  # axiom | value | goal | spec | action | reflection | insight
    node_title: str

    # Justification
    justification: str  # Why this node?
    derived_from: list[str]  # Parent node IDs (lineage)

    # Quality metrics
    axiom_stability: Optional[float] = None  # For L1 nodes: fixed-point score

@dataclass
class EdgeCreationMark(ZeroSeedMark):
    """Mark for creating an edge between nodes."""

    edge_id: str
    source_node: str
    target_node: str
    edge_kind: str  # GROUNDS | JUSTIFIES | SPECIFIES | IMPLEMENTS | REFLECTS_ON | REPRESENTS

    # Transition metrics
    layer_jump: int  # Abs difference in layers (1 = adjacent, >1 = skip)
    transition_loss: float  # Galois loss of this specific transition

    # Proof data
    warrant: str  # Toulmin warrant for this edge
    backing: Optional[str] = None  # Supporting evidence

@dataclass
class ProofValidationMark(ZeroSeedMark):
    """Mark for validating a Toulmin proof."""

    proof_id: str
    is_valid: bool
    validation_method: str  # "galois_loss" | "llm_judge" | "human_review"

    # Proof structure
    data: str
    warrant: str
    claim: str
    qualifier: str  # "definitely" | "probably" | "possibly" | "tentatively"
    rebuttals: tuple[str, ...]

    # Quality assessment
    logical_coherence: float  # [0, 1] from Galois logical loss
    evidence_tier: str  # CATEGORICAL | EMPIRICAL | ANECDOTAL

@dataclass
class ContradictionMark(ZeroSeedMark):
    """Mark for detecting a contradiction."""

    node_a_id: str
    node_b_id: str
    contradiction_type: str  # "genuine" | "apparent"
    strength: float  # Super-additive loss magnitude

    # Resolution
    resolution_strategy: str  # "synthesis" | "choose_one" | "defer" | "embrace"
    synthesis_node: Optional[str] = None  # If synthesized, the new node ID

@dataclass
class LLMOperationMark(ZeroSeedMark):
    """Mark for LLM operations (restructure, reconstitute, loss measurement)."""

    operation: str  # "restructure" | "reconstitute" | "galois_loss" | "axiom_mine"
    model: str  # "opus-4.5" | "sonnet-4.5" | "haiku-3.5"

    # Budget tracking
    tokens_input: int
    tokens_output: int
    cost_usd: float
    latency_ms: float

    # Quality
    success: bool
    error: Optional[str] = None
```

---

## Part II: Galois-Witnessed Operations

### 2.1 Node Creation with Witnessing

```python
from claude.services.witness import WitnessStore, WitnessMode
from claude.services.categorical.galois_loss import GaloisLoss

async def create_node_witnessed(
    title: str,
    content: str,
    layer: int,
    kind: str,
    derived_from: list[str],
    justification: str,
    galois: GaloisLoss,
    witness_store: WitnessStore,
) -> tuple[ZeroNode, NodeCreationMark]:
    """
    Create a Zero Seed node with full Galois-grounded witnessing.

    Steps:
      1. Compute Galois loss for this node's content
      2. Compute constitutional scores (via loss breakdown)
      3. Create the node
      4. Create witness mark with all metadata
      5. Auto-select witness mode based on loss
      6. Store mark

    Returns: (created_node, witness_mark)
    """

    # 1. Compute Galois loss
    loss_components = await galois.compute_full_breakdown(content)

    # 2. Constitutional scores (inverse of losses)
    constitutional_scores = {
        "TASTEFUL": 1.0 - loss_components.tasteful_loss,
        "COMPOSABLE": 1.0 - loss_components.composable_loss,
        "GENERATIVE": 1.0 - loss_components.generative_loss,
        "ETHICAL": 1.0 - loss_components.ethical_loss,
        "JOY_INDUCING": 1.0 - loss_components.joy_inducing_loss,
        "HETERARCHICAL": 1.0 - loss_components.heterarchical_loss,
        "CURATED": 1.0 - loss_components.curated_loss,
    }

    # 3. Create node
    node = ZeroNode(
        id=generate_node_id(),
        title=title,
        content=content,
        layer=layer,
        kind=kind,
        lineage=derived_from,
        tags=frozenset({f"layer_{layer}", kind}),
        created_at=datetime.now(UTC),
    )

    # 4. Create witness mark
    mark = NodeCreationMark(
        origin="zero_seed.node_creation",
        stimulus=Stimulus(
            kind="user_request",
            content=f"Create {kind} node: {title}",
        ),
        response=Response(
            kind="node_created",
            content=f"Created node {node.id} at layer {layer}",
            target_id=node.id,
        ),
        timestamp=node.created_at,
        galois_loss=loss_components.total,
        loss_components=loss_components,
        layer_transition=None,  # No transition for new node
        constitutional_scores=constitutional_scores,
        # Node-specific
        node_id=node.id,
        node_layer=layer,
        node_kind=kind,
        node_title=title,
        justification=justification,
        derived_from=derived_from,
        tags=frozenset({"zero_seed", "node_creation", kind}),
    )

    # 5. Auto-select witness mode
    mode = mark.witness_mode()

    # 6. Store mark
    await witness_store.save_mark(mark, mode=WitnessMode[mode])

    return node, mark

# Usage example
node, mark = await create_node_witnessed(
    title="Build DP-native Zero Seed UI",
    content="Create a React UI that visualizes value functions...",
    layer=3,  # Goal layer
    kind="goal",
    derived_from=["axiom_generative_id"],
    justification="Visualization enables developer understanding",
    galois=galois_loss_service,
    witness_store=witness_store,
)

print(f"Created node {node.id}")
print(f"Galois loss: {mark.galois_loss:.2%}")
print(f"Quality: {mark.quality_grade()}")
print(f"Witness mode: {mark.witness_mode()}")
# Output:
# Created node goal_dp_ui_id
# Galois loss: 8.50%
# Quality: A (Very Good)
# Witness mode: SINGLE
```

### 2.2 Edge Creation with Transition Loss

```python
async def create_edge_witnessed(
    source: ZeroNode,
    target: ZeroNode,
    kind: str,
    warrant: str,
    backing: Optional[str],
    galois: GaloisLoss,
    witness_store: WitnessStore,
) -> tuple[ZeroEdge, EdgeCreationMark]:
    """
    Create an edge with Galois transition loss measurement.

    Transition loss = semantic distance when traversing this edge.
    """

    # Describe the transition
    transition_desc = f"""
    From: Layer {source.layer} ({source.kind}) "{source.title}"
    To: Layer {target.layer} ({target.kind}) "{target.title}"
    Via: {kind}

    Warrant: {warrant}
    """

    # Compute transition loss
    transition_loss = await galois.compute(transition_desc)
    loss_components = await galois.compute_full_breakdown(transition_desc)

    # Create edge
    edge = ZeroEdge(
        id=generate_edge_id(),
        source=source.id,
        target=target.id,
        kind=kind,
        created_at=datetime.now(UTC),
    )

    # Create mark
    mark = EdgeCreationMark(
        origin="zero_seed.edge_creation",
        stimulus=Stimulus(
            kind="edge_request",
            content=f"Connect {source.title} → {target.title} via {kind}",
        ),
        response=Response(
            kind="edge_created",
            content=f"Created {kind} edge",
            target_id=edge.id,
        ),
        timestamp=edge.created_at,
        galois_loss=loss_components.total,
        loss_components=loss_components,
        layer_transition=(source.layer, target.layer),
        # Edge-specific
        edge_id=edge.id,
        source_node=source.id,
        target_node=target.id,
        edge_kind=kind,
        layer_jump=abs(target.layer - source.layer),
        transition_loss=transition_loss,
        warrant=warrant,
        backing=backing,
        tags=frozenset({"zero_seed", "edge_creation", kind}),
    )

    await witness_store.save_mark(mark, mode=WitnessMode[mark.witness_mode()])

    return edge, mark
```

### 2.3 Proof Validation with Galois Coherence

```python
async def validate_proof_witnessed(
    proof: Proof,
    galois: GaloisLoss,
    witness_store: WitnessStore,
) -> tuple[bool, ProofValidationMark]:
    """
    Validate a Toulmin proof using Galois logical loss.

    A valid proof has:
    - Low logical loss (< 15%)
    - Acyclic dependency graph
    - All warrants justified

    Returns: (is_valid, witness_mark)
    """

    # Compute logical coherence
    proof_text = proof.render_as_prose()
    logical_loss = await galois.galois_loss(
        proof_text,
        proof_text,  # Self-check: can it reproduce itself?
        axis=LossAxis.LOGICAL,
    )

    # Validation decision
    is_valid = logical_loss < 0.15  # < 15% logical loss

    # Loss breakdown
    loss_components = GaloisLossComponents(
        total=logical_loss,
        # For proofs, focus on these:
        composable_loss=logical_loss * 0.4,  # Proof structure
        generative_loss=logical_loss * 0.3,  # Derivation chain
        curated_loss=logical_loss * 0.3,     # Justification quality
    )

    # Create mark
    mark = ProofValidationMark(
        origin="zero_seed.proof_validation",
        stimulus=Stimulus(
            kind="validation_request",
            content=f"Validate proof: {proof.claim}",
        ),
        response=Response(
            kind="validation_result",
            content=f"Proof {'valid' if is_valid else 'invalid'}",
        ),
        timestamp=datetime.now(UTC),
        galois_loss=logical_loss,
        loss_components=loss_components,
        # Proof-specific
        proof_id=proof.id,
        is_valid=is_valid,
        validation_method="galois_loss",
        data=proof.data,
        warrant=proof.warrant,
        claim=proof.claim,
        qualifier=proof.qualifier,
        rebuttals=proof.rebuttals,
        logical_coherence=1.0 - logical_loss,
        evidence_tier=proof.tier.value,
        tags=frozenset({"zero_seed", "proof_validation"}),
    )

    await witness_store.save_mark(mark, mode=WitnessMode.SINGLE)  # Always important

    return is_valid, mark
```

### 2.4 Contradiction Detection with Super-Additive Loss

```python
async def detect_contradiction_witnessed(
    node_a: ZeroNode,
    node_b: ZeroNode,
    galois: GaloisLoss,
    witness_store: WitnessStore,
    tolerance: float = 0.1,
) -> Optional[ContradictionMark]:
    """
    Detect contradiction via super-additive Galois loss.

    Contradiction signature:
      L(A ∪ B) > L(A) + L(B) + tolerance
    """

    # Individual losses
    loss_a = await galois.compute(node_a.content)
    loss_b = await galois.compute(node_b.content)

    # Combined loss
    combined = f"{node_a.content}\n\n{node_b.content}"
    loss_combined = await galois.compute(combined)

    # Check super-additivity
    super_additive = loss_combined - (loss_a + loss_b)

    if super_additive > tolerance:
        # Genuine contradiction detected
        contradiction_type = "genuine"
        strength = super_additive

        # Suggest resolution strategy
        if strength < 0.5:
            resolution_strategy = "synthesis"  # Moderate → synthesize
        else:
            resolution_strategy = "choose_one"  # Severe → pick one

        mark = ContradictionMark(
            origin="zero_seed.contradiction_detection",
            stimulus=Stimulus(
                kind="contradiction_check",
                content=f"Check {node_a.title} vs {node_b.title}",
            ),
            response=Response(
                kind="contradiction_detected",
                content=f"Detected {contradiction_type} contradiction (strength={strength:.2f})",
            ),
            timestamp=datetime.now(UTC),
            galois_loss=loss_combined,
            loss_components=GaloisLossComponents(
                total=loss_combined,
                composable_loss=super_additive,  # Contradiction = composition failure
            ),
            node_a_id=node_a.id,
            node_b_id=node_b.id,
            contradiction_type=contradiction_type,
            strength=strength,
            resolution_strategy=resolution_strategy,
            tags=frozenset({"zero_seed", "contradiction", contradiction_type}),
        )

        await witness_store.save_mark(mark, mode=WitnessMode.SINGLE)
        return mark

    else:
        # No contradiction (or only apparent)
        return None
```

---

## Part III: LLM Call Witnessing

### 3.1 Token Budget Tracking

```python
from claude.services.categorical.galois_loss import LLMGaloisRestructurer

class WitnessedGaloisRestructurer(LLMGaloisRestructurer):
    """
    Galois restructurer that witnesses all LLM calls.

    Every restructure/reconstitute operation produces a mark with:
    - Token counts
    - Cost in USD
    - Latency
    - Success/failure status
    """

    def __init__(
        self,
        llm_client,
        witness_store: WitnessStore,
        token_budget: TokenBudget,
    ):
        super().__init__(llm_client)
        self.witness_store = witness_store
        self.token_budget = token_budget

    async def restructure(
        self,
        content: str,
        context: Context,
    ) -> ModularContent:
        """Restructure with full witnessing."""

        start = time.time()
        success = False
        error = None

        try:
            # Call parent restructure
            result = await super().restructure(content, context)

            # Estimate tokens (actual counts would come from API response)
            tokens_input = len(content.split()) * 1.3  # Rough estimate
            tokens_output = len(str(result).split()) * 1.3

            # Check budget
            if not self.token_budget.can_afford(tokens_input, tokens_output):
                raise TokenBudgetExceeded("Session token budget exceeded")

            # Charge budget
            self.token_budget.charge(tokens_input, tokens_output)

            success = True
            return result

        except Exception as e:
            error = str(e)
            raise

        finally:
            latency_ms = (time.time() - start) * 1000

            # Create witness mark
            mark = LLMOperationMark(
                origin="zero_seed.llm.restructure",
                stimulus=Stimulus(
                    kind="llm_call",
                    content=f"Restructure {len(content)} chars",
                ),
                response=Response(
                    kind="llm_response",
                    content=f"{'Success' if success else 'Failed'}: {error or 'OK'}",
                ),
                timestamp=datetime.now(UTC),
                galois_loss=0.0,  # N/A for LLM operations
                loss_components=GaloisLossComponents(total=0.0),
                operation="restructure",
                model=self.llm_client.model_name,
                tokens_input=int(tokens_input),
                tokens_output=int(tokens_output),
                cost_usd=self.token_budget.session_cost_usd(),
                latency_ms=latency_ms,
                success=success,
                error=error,
                tags=frozenset({"zero_seed", "llm", "restructure"}),
            )

            # Witness in SESSION mode (accumulate, not immediate)
            await self.witness_store.save_mark(mark, mode=WitnessMode.SESSION)
```

### 3.2 Tier Selection Recording

```python
@dataclass
class LLMTierSelection:
    """
    Record which LLM tier was selected for an operation.

    Tiers:
      - Scout (Haiku): Fast, cheap, high loss tolerance (30%)
      - Analyst (Sonnet): Balanced, medium loss tolerance (15%)
      - Architect (Opus): Slow, expensive, low loss tolerance (5%)
    """

    operation: str
    selected_tier: str  # "scout" | "analyst" | "architect"
    max_loss_tolerance: float
    reason: str

async def select_llm_tier_witnessed(
    operation: str,
    max_loss: float,
    witness_store: WitnessStore,
) -> tuple[str, LLMTierSelection]:
    """
    Select LLM tier with witnessing.

    Returns: (model_name, tier_selection_record)
    """

    # Tier selection logic
    if max_loss < 0.05:
        tier = "architect"
        model = "claude-opus-4-5-20251101"
        reason = "Low loss tolerance requires opus-level fidelity"
    elif max_loss < 0.15:
        tier = "analyst"
        model = "claude-sonnet-4-5-20250929"
        reason = "Moderate loss tolerance, sonnet sufficient"
    else:
        tier = "scout"
        model = "claude-3-5-haiku-20241022"
        reason = "High loss tolerance, haiku sufficient"

    # Create tier selection record
    selection = LLMTierSelection(
        operation=operation,
        selected_tier=tier,
        max_loss_tolerance=max_loss,
        reason=reason,
    )

    # Witness the selection
    mark = ZeroSeedMark(
        origin="zero_seed.llm.tier_selection",
        stimulus=Stimulus(
            kind="tier_selection",
            content=f"Select tier for {operation} (max_loss={max_loss})",
        ),
        response=Response(
            kind="tier_selected",
            content=f"Selected {tier} ({model}): {reason}",
        ),
        timestamp=datetime.now(UTC),
        galois_loss=max_loss,  # Use tolerance as proxy
        loss_components=GaloisLossComponents(total=max_loss),
        llm_tier=tier,
        tags=frozenset({"zero_seed", "llm", "tier_selection"}),
    )

    await witness_store.save_mark(mark, mode=WitnessMode.LAZY)

    return model, selection
```

---

## Part IV: Decision Dialectics

### 4.1 Dialectic Fusion with Witnessing

```python
@dataclass
class DialecticFusion:
    """
    A dialectical resolution captured as a Witness mark.

    When Kent and Claude have different views, the synthesis is witnessed.
    """

    thesis_node: str  # Kent's view
    antithesis_node: str  # Claude's view
    synthesis_node: str  # Resolution
    synthesis_warrant: str  # Why this synthesis?

async def create_dialectic_fusion_witnessed(
    thesis: ZeroNode,
    antithesis: ZeroNode,
    synthesis_content: str,
    warrant: str,
    galois: GaloisLoss,
    witness_store: WitnessStore,
) -> tuple[ZeroNode, ZeroSeedMark]:
    """
    Create a synthesis node from thesis/antithesis with full dialectic trace.

    This is the Zero Seed analog of the Witness `kg decide` command.
    """

    # Compute Galois loss of synthesis
    loss_components = await galois.compute_full_breakdown(synthesis_content)

    # Create synthesis node
    synthesis = ZeroNode(
        id=generate_node_id(),
        title=f"Synthesis: {thesis.title} × {antithesis.title}",
        content=synthesis_content,
        layer=max(thesis.layer, antithesis.layer),  # Inherit higher layer
        kind="synthesis",
        lineage=[thesis.id, antithesis.id],
        tags=frozenset({"synthesis", "dialectic"}),
        created_at=datetime.now(UTC),
    )

    # Create fusion mark
    mark = ZeroSeedMark(
        origin="zero_seed.dialectic.fusion",
        stimulus=Stimulus(
            kind="contradiction_resolution",
            content=f"Resolve: {thesis.title} vs {antithesis.title}",
        ),
        response=Response(
            kind="synthesis_created",
            content=f"Created synthesis: {synthesis.title}",
            target_id=synthesis.id,
        ),
        timestamp=synthesis.created_at,
        galois_loss=loss_components.total,
        loss_components=loss_components,
        tags=frozenset({"zero_seed", "dialectic", "fusion"}),
        metadata={
            "thesis_node": thesis.id,
            "antithesis_node": antithesis.id,
            "synthesis_node": synthesis.id,
            "warrant": warrant,
            "fusion_type": "dialectic",
        },
    )

    await witness_store.save_mark(mark, mode=WitnessMode.SINGLE)

    return synthesis, mark

# Usage example (from CLI)
@click.command()
@click.option("--thesis", required=True, help="Kent's view node ID")
@click.option("--antithesis", required=True, help="Claude's view node ID")
@click.option("--synthesis", required=True, help="Resolution text")
@click.option("--warrant", required=True, help="Why this synthesis?")
async def decide(thesis: str, antithesis: str, synthesis: str, warrant: str):
    """
    Zero Seed dialectic decision command.

    Example:
      kg zero-seed decide \\
        --thesis axiom_langchain \\
        --antithesis axiom_kgents \\
        --synthesis "Build minimal kernel, validate, then decide" \\
        --warrant "Avoids both risks: years without validation AND abandoning ideas untested"
    """
    thesis_node = await get_node(thesis)
    antithesis_node = await get_node(antithesis)

    synthesis_node, mark = await create_dialectic_fusion_witnessed(
        thesis=thesis_node,
        antithesis=antithesis_node,
        synthesis_content=synthesis,
        warrant=warrant,
        galois=get_galois_service(),
        witness_store=get_witness_store(),
    )

    click.secho(f"✓ Created synthesis: {synthesis_node.id}", fg="green")
    click.echo(f"  Galois loss: {mark.galois_loss:.2%}")
    click.echo(f"  Quality: {mark.quality_grade()}")
    click.echo(f"  Witnessed: {mark.witness_mode()}")
```

### 4.2 Connection to Emerging Constitution Articles

```python
async def link_to_constitution_article(
    synthesis_node: ZeroNode,
    article_path: str,
    witness_store: WitnessStore,
) -> ZeroSeedMark:
    """
    Link a synthesis to an Emerging Constitution article.

    The Emerging Constitution captures generalizations from dialectic resolutions.
    """

    mark = ZeroSeedMark(
        origin="zero_seed.constitution.link",
        stimulus=Stimulus(
            kind="constitution_link",
            content=f"Link {synthesis_node.title} to {article_path}",
        ),
        response=Response(
            kind="link_created",
            content=f"Linked to constitution article",
        ),
        timestamp=datetime.now(UTC),
        galois_loss=0.0,  # Linking is zero-loss
        loss_components=GaloisLossComponents(total=0.0),
        tags=frozenset({"zero_seed", "constitution", "link"}),
        metadata={
            "synthesis_node": synthesis_node.id,
            "article_path": article_path,
        },
    )

    await witness_store.save_mark(mark, mode=WitnessMode.LAZY)
    return mark
```

---

## Part V: Trace Lineage

### 5.1 Node → Mark Lineage

```python
@dataclass
class NodeLineage:
    """
    Lineage chain from node back to creation mark.

    Every node has:
    - Creation mark (when it was created)
    - Parent nodes (what it derived from)
    - Parent marks (why parents were created)
    - Proof marks (validation history)
    """

    node_id: str
    creation_mark_id: str
    parent_nodes: list[str]
    parent_marks: list[str]
    proof_marks: list[str]

async def trace_node_lineage(
    node: ZeroNode,
    witness_store: WitnessStore,
    depth: int = 10,
) -> NodeLineage:
    """
    Trace a node's lineage back to axioms.

    Returns the full provenance chain.
    """

    # Find creation mark
    creation_marks = await witness_store.query_marks(
        filters={"response.target_id": node.id, "origin": "zero_seed.node_creation"}
    )
    creation_mark_id = creation_marks[0].id if creation_marks else None

    # Find parent nodes
    parent_nodes = node.lineage

    # Find parent marks
    parent_marks = []
    for parent_id in parent_nodes:
        parent_creation_marks = await witness_store.query_marks(
            filters={"response.target_id": parent_id}
        )
        if parent_creation_marks:
            parent_marks.append(parent_creation_marks[0].id)

    # Find proof marks (validation history)
    proof_marks = await witness_store.query_marks(
        filters={"metadata.node_id": node.id, "origin": "zero_seed.proof_validation"}
    )
    proof_mark_ids = [m.id for m in proof_marks]

    return NodeLineage(
        node_id=node.id,
        creation_mark_id=creation_mark_id,
        parent_nodes=parent_nodes,
        parent_marks=parent_marks,
        proof_marks=proof_mark_ids,
    )

# CLI command
@click.command()
@click.argument("node_id")
async def lineage(node_id: str):
    """
    Show full lineage for a Zero Seed node.

    Example:
      kg zero-seed lineage goal_dp_ui_id
    """
    node = await get_node(node_id)
    lineage = await trace_node_lineage(node, get_witness_store())

    click.echo(f"Lineage for {node.title}:")
    click.echo(f"  Created: {lineage.creation_mark_id}")
    click.echo(f"  Parents: {', '.join(lineage.parent_nodes)}")
    click.echo(f"  Parent marks: {', '.join(lineage.parent_marks)}")
    click.echo(f"  Validation marks: {', '.join(lineage.proof_marks)}")
```

### 5.2 Edge → Justification Marks

```python
async def get_edge_justification(
    edge: ZeroEdge,
    witness_store: WitnessStore,
) -> EdgeCreationMark:
    """
    Retrieve the creation mark (justification) for an edge.

    Every edge must have a justification mark explaining why it exists.
    """

    marks = await witness_store.query_marks(
        filters={"response.target_id": edge.id, "origin": "zero_seed.edge_creation"}
    )

    if not marks:
        raise ValueError(f"Edge {edge.id} has no justification mark (violated witnessing contract)")

    return marks[0]  # Should be exactly one
```

### 5.3 Proof → Validation Marks

```python
async def get_proof_validation_history(
    proof: Proof,
    witness_store: WitnessStore,
) -> list[ProofValidationMark]:
    """
    Get all validation attempts for a proof.

    A proof may be validated multiple times:
    - Initial validation (LLM-based)
    - Mirror Test review (human)
    - Retroactive validation after axiom changes
    """

    marks = await witness_store.query_marks(
        filters={"metadata.proof_id": proof.id, "origin": "zero_seed.proof_validation"}
    )

    return sorted(marks, key=lambda m: m.timestamp)
```

---

## Part VI: Mode Selection via Galois Triage

### 6.1 Automatic Mode Selection

```python
class GaloisWitnessTriage:
    """
    Automatic witness mode selection based on Galois loss.

    Philosophy: Let the loss tell us how important this is.
    - Low loss (< 10%) → SINGLE (important, full trace)
    - Medium loss (10-30%) → SESSION (moderate, accumulated)
    - High loss (> 30%) → LAZY (speculative, batched)
    """

    THRESHOLDS = {
        "SINGLE": 0.10,   # Important operations
        "SESSION": 0.30,  # Moderate operations
        # Above 0.30 → LAZY
    }

    @classmethod
    def select_mode(cls, galois_loss: float) -> WitnessMode:
        """Automatic triage."""
        if galois_loss < cls.THRESHOLDS["SINGLE"]:
            return WitnessMode.SINGLE
        elif galois_loss < cls.THRESHOLDS["SESSION"]:
            return WitnessMode.SESSION
        else:
            return WitnessMode.LAZY

    @classmethod
    def should_witness_immediately(cls, galois_loss: float) -> bool:
        """Check if this operation needs immediate witnessing."""
        return galois_loss < cls.THRESHOLDS["SINGLE"]
```

### 6.2 Override for Critical Operations

```python
# Some operations are ALWAYS important regardless of loss
CRITICAL_OPERATIONS = {
    "zero_seed.axiom_creation",      # Always SINGLE
    "zero_seed.constitution_change", # Always SINGLE
    "zero_seed.contradiction",       # Always SINGLE
    "zero_seed.proof_validation",    # Always SINGLE
}

async def save_mark_with_triage(
    mark: ZeroSeedMark,
    witness_store: WitnessStore,
    override_mode: Optional[WitnessMode] = None,
) -> str:
    """
    Save mark with automatic triage unless overridden.

    Critical operations override Galois triage.
    """

    # Check if this is a critical operation
    if mark.origin in CRITICAL_OPERATIONS:
        mode = WitnessMode.SINGLE
    elif override_mode:
        mode = override_mode
    else:
        # Auto-triage based on Galois loss
        mode = GaloisWitnessTriage.select_mode(mark.galois_loss)

    return await witness_store.save_mark(mark, mode=mode)
```

---

## Part VII: Implementation Architecture

### 7.1 Service Module Structure

```
impl/claude/services/zero_seed_witness/
├── __init__.py                  # Exports
├── marks.py                     # ZeroSeedMark, NodeCreationMark, etc.
├── witnessed_operations.py      # create_node_witnessed, etc.
├── galois_triage.py             # GaloisWitnessTriage
├── lineage.py                   # trace_node_lineage, etc.
├── llm_witnessing.py            # WitnessedGaloisRestructurer
├── dialectic.py                 # create_dialectic_fusion_witnessed
└── _tests/
    ├── test_marks.py
    ├── test_triage.py
    ├── test_lineage.py
    └── test_llm_witnessing.py
```

### 7.2 AGENTESE Integration

```python
# services/zero_seed_witness/__init__.py

from claude.protocols.agentese.node import node, NodeAspect

@node(
    "time.zero_seed.create_node",
    aspects=[NodeAspect.STATEFUL, NodeAspect.WITNESSED],
    dependencies=("galois_loss", "witness_store"),
)
class CreateNodeNode:
    """AGENTESE node: create Zero Seed node with witnessing."""

    def __init__(self, galois_loss, witness_store):
        self.galois = galois_loss
        self.witness_store = witness_store

    async def invoke(
        self,
        observer,
        title: str,
        content: str,
        layer: int,
        kind: str,
        derived_from: list[str],
        justification: str,
    ):
        node, mark = await create_node_witnessed(
            title=title,
            content=content,
            layer=layer,
            kind=kind,
            derived_from=derived_from,
            justification=justification,
            galois=self.galois,
            witness_store=self.witness_store,
        )

        yield {
            "node": node.to_dict(),
            "mark": mark.to_dict(),
            "galois_loss": mark.galois_loss,
            "quality": mark.quality_grade(),
            "witness_mode": mark.witness_mode(),
        }
```

### 7.3 CLI Commands

```python
# protocols/cli/handlers/zero_seed_witness.py

@click.group()
def zero_seed():
    """Zero Seed operations with Galois-grounded witnessing."""
    pass

@zero_seed.command()
@click.option("--title", required=True)
@click.option("--content", required=True)
@click.option("--layer", type=int, required=True)
@click.option("--kind", required=True)
@click.option("--derived-from", multiple=True)
@click.option("--justification", required=True)
async def create_node(title, content, layer, kind, derived_from, justification):
    """Create a Zero Seed node with full witnessing."""

    node, mark = await create_node_witnessed(
        title=title,
        content=content,
        layer=layer,
        kind=kind,
        derived_from=list(derived_from),
        justification=justification,
        galois=get_galois_service(),
        witness_store=get_witness_store(),
    )

    click.secho(f"✓ Created node: {node.id}", fg="green")
    click.echo(f"  Title: {node.title}")
    click.echo(f"  Layer: {node.layer}")
    click.echo(f"  Galois loss: {mark.galois_loss:.2%}")
    click.echo(f"  Quality: {mark.quality_grade()}")
    click.echo(f"  Witness mode: {mark.witness_mode()}")

@zero_seed.command()
@click.argument("node_id")
async def lineage(node_id):
    """Show full lineage for a node."""

    node = await get_node(node_id)
    lineage = await trace_node_lineage(node, get_witness_store())

    click.echo(f"Lineage for {node.title}:")
    click.echo(f"  Created: {lineage.creation_mark_id}")
    click.echo(f"  Parents: {', '.join(lineage.parent_nodes)}")
    click.echo(f"  Validation marks: {len(lineage.proof_marks)}")

@zero_seed.command()
@click.option("--today", is_flag=True, help="Show today's marks only")
@click.option("--operation", help="Filter by operation type")
@click.option("--min-loss", type=float, help="Minimum Galois loss")
@click.option("--max-loss", type=float, help="Maximum Galois loss")
async def marks(today, operation, min_loss, max_loss):
    """Query Zero Seed witness marks."""

    filters = {"origin": "zero_seed.*"}  # Regex match

    if today:
        filters["timestamp"] = {"$gte": datetime.now(UTC).replace(hour=0, minute=0)}
    if operation:
        filters["origin"] = f"zero_seed.{operation}"

    marks = await get_witness_store().query_marks(filters=filters)

    # Filter by loss if specified
    if min_loss is not None:
        marks = [m for m in marks if m.galois_loss >= min_loss]
    if max_loss is not None:
        marks = [m for m in marks if m.galois_loss <= max_loss]

    click.echo(f"Found {len(marks)} marks")
    for mark in marks[:20]:  # Show first 20
        click.echo(f"  [{mark.timestamp.strftime('%H:%M')}] {mark.origin}")
        click.echo(f"    Loss: {mark.galois_loss:.2%} ({mark.quality_grade()})")
        click.echo(f"    {mark.response.content}")
```

---

## Part VIII: Testing Strategy

### 8.1 Property-Based Tests

```python
from hypothesis import given, strategies as st

@given(
    st.text(min_size=50),
    st.integers(min_value=1, max_value=7),
)
async def test_create_node_always_produces_mark(content, layer):
    """Property: Every node creation produces exactly one mark."""

    node, mark = await create_node_witnessed(
        title="Test node",
        content=content,
        layer=layer,
        kind="test",
        derived_from=[],
        justification="Test",
        galois=get_test_galois(),
        witness_store=get_test_witness_store(),
    )

    # Verify mark exists
    assert mark is not None
    assert mark.node_id == node.id

    # Verify mark has Galois data
    assert 0.0 <= mark.galois_loss <= 1.0
    assert mark.loss_components.total == mark.galois_loss

@given(st.floats(min_value=0.0, max_value=1.0))
def test_galois_triage_is_monotonic(loss):
    """Property: Higher loss → lazier witnessing."""

    mode1 = GaloisWitnessTriage.select_mode(loss)
    mode2 = GaloisWitnessTriage.select_mode(loss + 0.1)

    # mode2 should be at least as lazy as mode1
    mode_order = ["SINGLE", "SESSION", "LAZY"]
    assert mode_order.index(mode2.name) >= mode_order.index(mode1.name)
```

### 8.2 Integration Tests

```python
async def test_node_lineage_chain():
    """Test: Create axiom → value → goal chain, verify lineage."""

    # Create axiom
    axiom, axiom_mark = await create_node_witnessed(
        title="Entity axiom",
        content="Everything is a node",
        layer=1,
        kind="axiom",
        derived_from=[],
        justification="Fundamental assumption",
        galois=get_test_galois(),
        witness_store=get_test_witness_store(),
    )

    # Create value from axiom
    value, value_mark = await create_node_witnessed(
        title="Tasteful value",
        content="Tasteful > feature-complete",
        layer=2,
        kind="value",
        derived_from=[axiom.id],
        justification="Grounded in entity axiom",
        galois=get_test_galois(),
        witness_store=get_test_witness_store(),
    )

    # Trace lineage
    lineage = await trace_node_lineage(value, get_test_witness_store())

    # Verify lineage chain
    assert axiom.id in lineage.parent_nodes
    assert axiom_mark.id in lineage.parent_marks
    assert lineage.creation_mark_id == value_mark.id

async def test_contradiction_detection_witnessing():
    """Test: Contradiction detection produces mark."""

    node_a = ZeroNode(
        id="test_a",
        title="All is mutable",
        content="Everything can change",
        layer=1,
        kind="axiom",
    )

    node_b = ZeroNode(
        id="test_b",
        title="Marks are immutable",
        content="Marks are frozen after creation",
        layer=1,
        kind="axiom",
    )

    mark = await detect_contradiction_witnessed(
        node_a=node_a,
        node_b=node_b,
        galois=get_test_galois(),
        witness_store=get_test_witness_store(),
    )

    # Should detect contradiction
    assert mark is not None
    assert mark.contradiction_type == "genuine"
    assert mark.strength > 0.1
```

---

## Part IX: Migration Path

### 9.1 Phase 1: Core Witnessing (Weeks 1-2)

**Deliverables**:
```
- impl/claude/services/zero_seed_witness/marks.py
- impl/claude/services/zero_seed_witness/witnessed_operations.py
- impl/claude/services/zero_seed_witness/galois_triage.py
- _tests for all above
```

**Success Criteria**:
- [ ] `ZeroSeedMark` class implemented with all fields
- [ ] `create_node_witnessed()` works, produces marks
- [ ] `GaloisWitnessTriage` selects modes correctly
- [ ] Tests pass with 90%+ coverage

### 9.2 Phase 2: LLM Integration (Weeks 3-4)

**Deliverables**:
```
- impl/claude/services/zero_seed_witness/llm_witnessing.py
- WitnessedGaloisRestructurer class
- Token budget tracking integrated
```

**Success Criteria**:
- [ ] All LLM calls produce `LLMOperationMark`
- [ ] Token budgets tracked per session
- [ ] Tier selection witnessed
- [ ] Budget exceeded → graceful failure

### 9.3 Phase 3: Lineage & Dialectics (Weeks 5-6)

**Deliverables**:
```
- impl/claude/services/zero_seed_witness/lineage.py
- impl/claude/services/zero_seed_witness/dialectic.py
- CLI commands: kg zero-seed lineage, kg zero-seed decide
```

**Success Criteria**:
- [ ] `trace_node_lineage()` returns full chain
- [ ] `create_dialectic_fusion_witnessed()` works
- [ ] CLI commands functional
- [ ] Integration with Emerging Constitution

### 9.4 Phase 4: UI Integration (Weeks 7-8)

**Deliverables**:
```
- impl/claude/web/src/components/zero-seed/WitnessViewer.tsx
- impl/claude/web/src/components/zero-seed/LineageGraph.tsx
- impl/claude/web/src/components/zero-seed/GaloisLossIndicator.tsx
```

**Success Criteria**:
- [ ] Witness marks visible in Zero Seed UI
- [ ] Lineage graph renders
- [ ] Galois loss color-coded (green/yellow/red)
- [ ] Click mark → view details

---

## Part X: Open Questions

### 10.1 Witness Mode Thresholds

**Question**: Are the Galois loss thresholds (0.10, 0.30) optimal?

**Approach**:
- Run experiments on real Zero Seed sessions
- Measure correlation: loss vs human-judged importance
- Adjust thresholds to maximize precision/recall

**Hypothesis**: 0.10 is conservative; 0.15 may be sufficient for SINGLE mode.

### 10.2 Retroactive Witnessing

**Question**: If witnessing fails (e.g., crash), can we reconstruct marks from logs?

**Approach**:
- Design witness recovery protocol
- Store minimal data in fallback log
- Reconstruct marks from log + Galois computation

**Challenge**: Galois loss requires LLM calls → expensive to retroactively compute.

### 10.3 Multi-User Witnessing

**Question**: How do we handle multiple users editing the same Zero Seed graph?

**Approach**:
- Each user has their own Galois oracle (personalized loss)
- Marks include `umwelt_id` (observer identity)
- Aggregate via voting or weighted average

**Trade-off**: Per-user vs shared witness store?

### 10.4 Witness Compression

**Question**: As marks accumulate, storage grows. How do we compress?

**Approach**:
- Crystallize marks into lessons (periodic summary)
- Galois-compress witness walks (lossy but semantics-preserving)
- Retain only high-importance marks beyond N days

**Success Criterion**: 10:1 compression ratio with < 5% information loss

---

## Part XI: Summary and Next Steps

### 11.1 What This Achieves

This specification unifies Zero Seed operations with the Witness Protocol via Galois modularization theory:

1. **Every operation witnessed**: Node creation, edge traversal, proof validation, LLM calls all produce marks
2. **Automatic mode selection**: Galois loss enables triage (low loss → SINGLE, high loss → LAZY)
3. **Full lineage tracing**: Every node traces back to creation marks and parent marks
4. **LLM call accountability**: Token budgets, tier selection, costs all witnessed
5. **Dialectic capture**: Thesis/antithesis/synthesis recorded as fusion marks
6. **Constitutional grounding**: Principle scores computed from loss components

### 11.2 Implementation Priorities

| Priority | Task | Weeks |
|----------|------|-------|
| **HIGH** | Implement `ZeroSeedMark` and witnessed operations | 1-2 |
| **HIGH** | Galois triage for automatic mode selection | 1-2 |
| **MEDIUM** | LLM witnessing with budget tracking | 3-4 |
| **MEDIUM** | Lineage tracing and CLI commands | 5-6 |
| **LOW** | UI integration (witness viewer, lineage graph) | 7-8 |

### 11.3 Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| **Mark coverage** | 100% of Zero Seed operations produce marks |
| **Triage accuracy** | 85%+ agreement with manual importance ratings |
| **Lineage completeness** | 100% of nodes trace back to creation marks |
| **Token budget enforcement** | 100% of sessions respect budget limits |
| **Mirror Test approval** | Kent confirms "feels traceable, not burdensome" |

---

## Cross-References

- `spec/protocols/witness-primitives.md` — Mark, Walk, Playbook, Grant, Scope primitives
- `spec/theory/galois-modularization.md` — Galois loss theory, R ⊣ C adjunction
- `spec/theory/agent-dp.md` — DP foundations, PolicyTrace, ValueAgent
- `spec/protocols/zero-seed1/index.md` — Zero Seed unified specification
- `spec/protocols/zero-seed1/dp.md` — Constitutional reward as inverse Galois loss
- `spec/protocols/zero-seed1/llm.md` — LLM as Galois adjunction
- `impl/claude/services/witness/` — Witness service implementation
- `impl/claude/services/categorical/galois_loss.py` — Galois loss computation

---

*"Every node creation is witnessed. Every edge traversal is marked. Every loss measurement is traced. The proof IS the walk."*

---

**Filed**: 2025-12-24
**Status**: Draft — Ready for Review
**Next Actions**:
1. Review with Kent (Mirror Test)
2. Implement Phase 1 (core witnessing)
3. Validate Galois triage thresholds on real sessions
4. Integrate with existing Zero Seed DP implementation
5. Add UI components for witness visualization
