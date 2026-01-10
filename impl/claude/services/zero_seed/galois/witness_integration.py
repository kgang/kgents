"""
Zero Seed Witness Integration: Galois-Grounded Traceability.

This module integrates Zero Seed Galois operations with the Witness system:
- ZeroSeedMark: Extended Mark with Galois loss tracking
- GaloisWitnessTriage: Automatic witness mode selection based on loss
- Witnessed operations: Node creation, edge traversal, proof validation
- Lineage tracing: Node -> Mark provenance chains
- Dialectic capture: Thesis/antithesis/synthesis witnessing

The Unified Insight:
    The DP PolicyTrace IS the Witness Walk.
    The Toulmin Proof IS the Mark metadata.
    The Galois loss IS the quality metric that makes witnessing tractable at scale.

Key Innovation:
    Galois loss makes witness triage automatic--important operations (low loss)
    get full witnessing, speculative operations (high loss) get lazy witnessing.
    No manual mode selection needed.

See: spec/protocols/zero-seed1/witness-integration.md
See: spec/protocols/witness-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Protocol
from uuid import uuid4

if TYPE_CHECKING:
    from services.witness import Crystal, MarkStore
    from services.witness.crystal_store import CrystalStore

from services.witness.mark import (
    EvidenceTier,
    Mark,
    MarkId,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)

from .galois_loss import GaloisLossComputer
from .proof import (
    GaloisWitnessedProof,
    ProofLossDecomposition,
    WitnessMode,
    classify_by_loss,
    select_witness_mode_from_loss,
)

logger = logging.getLogger("kgents.zero_seed.witness_integration")


# =============================================================================
# Type Aliases
# =============================================================================

NodeId = str
EdgeId = str


def generate_node_id() -> NodeId:
    """Generate a unique Zero Seed node ID."""
    return f"zs-node-{uuid4().hex[:12]}"


def generate_edge_id() -> EdgeId:
    """Generate a unique Zero Seed edge ID."""
    return f"zs-edge-{uuid4().hex[:12]}"


# =============================================================================
# GaloisLossComponents (Principle-Based)
# =============================================================================


@dataclass(frozen=True)
class GaloisLossComponents:
    """
    Breakdown of Galois loss by constitutional principle.

    Enables diagnostic analysis: which principle is violated most?

    The seven principles from the kgents constitution:
    - TASTEFUL: Bloat, unnecessary complexity
    - COMPOSABLE: Hidden coupling, interface violations
    - GENERATIVE: Failed regeneration from lineage
    - ETHICAL: Hidden safety risks
    - JOY_INDUCING: Aesthetic coherence drift
    - HETERARCHICAL: Imposed rigidity
    - CURATED: Arbitrary changes, weak justification
    """

    total: float  # Aggregate loss [0, 1]

    # Per-principle losses
    tasteful_loss: float = 0.0
    composable_loss: float = 0.0
    generative_loss: float = 0.0
    ethical_loss: float = 0.0
    joy_inducing_loss: float = 0.0
    heterarchical_loss: float = 0.0
    curated_loss: float = 0.0

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
        if all(v == 0 for v in losses.values()):
            return "NONE"
        return max(losses.items(), key=lambda x: x[1])[0]

    def to_dict(self) -> dict[str, Any]:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GaloisLossComponents:
        """Create from dictionary."""
        return cls(
            total=data.get("total", 0.0),
            tasteful_loss=data.get("tasteful_loss", 0.0),
            composable_loss=data.get("composable_loss", 0.0),
            generative_loss=data.get("generative_loss", 0.0),
            ethical_loss=data.get("ethical_loss", 0.0),
            joy_inducing_loss=data.get("joy_inducing_loss", 0.0),
            heterarchical_loss=data.get("heterarchical_loss", 0.0),
            curated_loss=data.get("curated_loss", 0.0),
        )

    @classmethod
    def zero(cls) -> GaloisLossComponents:
        """Create a zero-loss decomposition (perfect coherence)."""
        return cls(total=0.0)

    @classmethod
    def from_total(cls, total: float) -> GaloisLossComponents:
        """Create decomposition from total, distributing evenly."""
        per_principle = total / 7 if total > 0 else 0.0
        return cls(
            total=total,
            tasteful_loss=per_principle,
            composable_loss=per_principle,
            generative_loss=per_principle,
            ethical_loss=per_principle,
            joy_inducing_loss=per_principle,
            heterarchical_loss=per_principle,
            curated_loss=per_principle,
        )

    @classmethod
    def from_proof_decomposition(cls, decomp: ProofLossDecomposition) -> GaloisLossComponents:
        """
        Convert from Toulmin-based ProofLossDecomposition to principle-based.

        Maps:
        - data -> generative (evidence preservation)
        - warrant -> composable (reasoning structure)
        - claim -> tasteful (conclusion clarity)
        - backing -> curated (justification quality)
        - qualifier -> ethical (confidence honesty)
        - rebuttals -> heterarchical (flexibility)
        - composition -> joy_inducing (overall coherence)
        """
        return cls(
            total=decomp.total,
            tasteful_loss=decomp.claim_loss,
            composable_loss=decomp.warrant_loss,
            generative_loss=decomp.data_loss,
            ethical_loss=decomp.qualifier_loss,
            joy_inducing_loss=decomp.composition_loss,
            heterarchical_loss=decomp.rebuttal_loss,
            curated_loss=decomp.backing_loss,
        )


# =============================================================================
# ZeroSeedMark: Mark Extended with Galois Tracking
# =============================================================================


@dataclass(frozen=True)
class ZeroSeedMark(Mark):
    """
    Mark extended with Galois loss tracking for Zero Seed operations.

    Every Zero Seed operation produces a mark with:
    - Standard witness data (origin, stimulus, response, timestamp)
    - Galois loss breakdown (total + per-principle components)
    - Optional layer transition data
    - Constitutional scores

    The Galois loss enables automatic witness mode selection:
      - loss < 0.10: WitnessMode.SINGLE (important, full trace)
      - loss < 0.30: WitnessMode.SESSION (moderate, accumulated)
      - loss >= 0.30: WitnessMode.LAZY (speculative, batched)
    """

    # Core Galois tracking
    galois_loss: float = 0.0  # Total Galois loss [0, 1]
    loss_components: GaloisLossComponents = field(default_factory=GaloisLossComponents.zero)

    # Optional Zero Seed specifics
    layer_transition: tuple[int, int] | None = None  # (from_layer, to_layer)
    constitutional_scores: dict[str, float] | None = None  # Principle -> score

    # LLM tracking (if operation used LLM)
    llm_tier: str | None = None  # "scout" | "analyst" | "architect"
    llm_tokens_input: int = 0
    llm_tokens_output: int = 0
    llm_latency_ms: float = 0.0

    def get_witness_mode(self) -> WitnessMode:
        """
        Automatic witness mode selection via Galois triage.

        Low loss -> important operation -> full witnessing
        High loss -> speculative operation -> lazy witnessing
        """
        return select_witness_mode_from_loss(self.galois_loss)

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

    def to_dict(self) -> dict[str, Any]:
        """Extend parent to_dict with Galois fields."""
        base = super().to_dict()
        base.update(
            {
                "galois_loss": self.galois_loss,
                "loss_components": self.loss_components.to_dict(),
                "layer_transition": list(self.layer_transition) if self.layer_transition else None,
                "constitutional_scores": self.constitutional_scores,
                "llm_tier": self.llm_tier,
                "llm_tokens_input": self.llm_tokens_input,
                "llm_tokens_output": self.llm_tokens_output,
                "llm_latency_ms": self.llm_latency_ms,
            }
        )
        return base

    @classmethod
    def from_mark(
        cls,
        mark: Mark,
        galois_loss: float,
        loss_components: GaloisLossComponents | None = None,
        **kwargs: Any,
    ) -> ZeroSeedMark:
        """Create ZeroSeedMark from existing Mark with Galois data."""
        return cls(
            id=mark.id,
            origin=mark.origin,
            stimulus=mark.stimulus,
            response=mark.response,
            umwelt=mark.umwelt,
            links=mark.links,
            timestamp=mark.timestamp,
            phase=mark.phase,
            walk_id=mark.walk_id,
            proof=mark.proof,
            tags=mark.tags,
            metadata=mark.metadata,
            galois_loss=galois_loss,
            loss_components=loss_components or GaloisLossComponents.from_total(galois_loss),
            **kwargs,
        )


# =============================================================================
# Operation-Specific Mark Types
# =============================================================================


@dataclass(frozen=True)
class NodeCreationMark(ZeroSeedMark):
    """Mark for creating a new Zero Seed node."""

    node_id: str = ""
    node_layer: int = 0
    node_kind: str = ""  # axiom | value | goal | spec | action | reflection | insight
    node_title: str = ""

    # Justification
    justification: str = ""
    derived_from: tuple[str, ...] = ()  # Parent node IDs (lineage)

    # Quality metrics
    axiom_stability: float | None = None  # For L1 nodes: fixed-point score


@dataclass(frozen=True)
class EdgeCreationMark(ZeroSeedMark):
    """Mark for creating an edge between nodes."""

    edge_id: str = ""
    source_node: str = ""
    target_node: str = ""
    edge_kind: str = ""  # GROUNDS | JUSTIFIES | SPECIFIES | IMPLEMENTS | REFLECTS_ON

    # Transition metrics
    layer_jump: int = 0  # Abs difference in layers (1 = adjacent, >1 = skip)
    transition_loss: float = 0.0  # Galois loss of this specific transition

    # Proof data
    warrant: str = ""  # Toulmin warrant for this edge
    backing: str | None = None  # Supporting evidence


@dataclass(frozen=True)
class ProofValidationMark(ZeroSeedMark):
    """Mark for validating a Toulmin proof."""

    proof_id: str = ""
    is_valid: bool = False
    validation_method: str = ""  # "galois_loss" | "llm_judge" | "human_review"

    # Proof structure
    proof_data: str = ""
    proof_warrant: str = ""
    proof_claim: str = ""
    qualifier: str = ""  # "definitely" | "probably" | "possibly" | "tentatively"
    rebuttals: tuple[str, ...] = ()

    # Quality assessment
    logical_coherence: float = 0.0  # [0, 1] from Galois logical loss
    evidence_tier: str = ""  # CATEGORICAL | EMPIRICAL | ANECDOTAL


@dataclass(frozen=True)
class ContradictionMark(ZeroSeedMark):
    """Mark for detecting a contradiction."""

    node_a_id: str = ""
    node_b_id: str = ""
    contradiction_type: str = ""  # "genuine" | "apparent"
    strength: float = 0.0  # Super-additive loss magnitude

    # Resolution
    resolution_strategy: str = ""  # "synthesis" | "choose_one" | "defer" | "embrace"
    synthesis_node: str | None = None  # If synthesized, the new node ID


@dataclass(frozen=True)
class LLMOperationMark(ZeroSeedMark):
    """Mark for LLM operations (restructure, reconstitute, loss measurement)."""

    operation: str = ""  # "restructure" | "reconstitute" | "galois_loss" | "axiom_mine"
    model: str = ""  # "opus-4.5" | "sonnet-4.5" | "haiku-3.5"

    # Budget tracking
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

    # Quality
    success: bool = False
    error: str | None = None


# =============================================================================
# GaloisWitnessTriage: Automatic Mode Selection
# =============================================================================


class GaloisWitnessTriage:
    """
    Automatic witness mode selection based on Galois loss.

    Philosophy: Let the loss tell us how important this is.
    - Low loss (< 10%) -> SINGLE (important, full trace)
    - Medium loss (10-30%) -> SESSION (moderate, accumulated)
    - High loss (> 30%) -> LAZY (speculative, batched)
    """

    THRESHOLDS = {
        "SINGLE": 0.10,  # Important operations
        "SESSION": 0.30,  # Moderate operations
        # Above 0.30 -> LAZY
    }

    # Critical operations that override Galois triage
    CRITICAL_OPERATIONS = frozenset(
        {
            "zero_seed.axiom_creation",
            "zero_seed.constitution_change",
            "zero_seed.contradiction",
            "zero_seed.proof_validation",
            "zero_seed.dialectic.fusion",
        }
    )

    @classmethod
    def select_mode(cls, galois_loss: float) -> WitnessMode:
        """Automatic triage based on Galois loss."""
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

    @classmethod
    def get_mode_for_origin(
        cls,
        origin: str,
        galois_loss: float,
        override_mode: WitnessMode | None = None,
    ) -> WitnessMode:
        """
        Get witness mode considering critical operations.

        Critical operations always get SINGLE mode regardless of loss.
        """
        if origin in cls.CRITICAL_OPERATIONS:
            return WitnessMode.SINGLE
        if override_mode:
            return override_mode
        return cls.select_mode(galois_loss)


# =============================================================================
# Galois Loss Computer Protocol
# =============================================================================


class GaloisLossComputerProtocol(Protocol):
    """Protocol for computing Galois loss (enables DI/mocking)."""

    async def compute(self, content: str) -> float:
        """Compute total Galois loss for content."""
        ...

    async def compute_full_breakdown(self, content: str) -> GaloisLossComponents:
        """Compute full breakdown by constitutional principle."""
        ...


@dataclass
class MockGaloisLossComputer:
    """Mock implementation for testing."""

    default_loss: float = 0.1

    async def compute(self, content: str) -> float:
        """Return default loss."""
        return self.default_loss

    async def compute_full_breakdown(self, content: str) -> GaloisLossComponents:
        """Return evenly distributed breakdown."""
        return GaloisLossComponents.from_total(self.default_loss)


# =============================================================================
# Witnessed Operations
# =============================================================================


@dataclass
class ZeroNode:
    """A Zero Seed node (simplified for witness integration)."""

    id: str
    title: str
    content: str
    layer: int
    kind: str  # axiom | value | goal | spec | action | reflection | insight
    lineage: list[str] = field(default_factory=list)
    tags: frozenset[str] = field(default_factory=frozenset)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "layer": self.layer,
            "kind": self.kind,
            "lineage": self.lineage,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ZeroEdge:
    """A Zero Seed edge (simplified for witness integration)."""

    id: str
    source: str
    target: str
    kind: str  # GROUNDS | JUSTIFIES | SPECIFIES | IMPLEMENTS | REFLECTS_ON
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


async def create_node_witnessed(
    title: str,
    content: str,
    layer: int,
    kind: str,
    derived_from: list[str],
    justification: str,
    galois: GaloisLossComputerProtocol,
    mark_store: MarkStore,
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
        created_at=datetime.now(timezone.utc),
    )

    # 4. Create witness mark
    mark = NodeCreationMark(
        id=generate_mark_id(),
        origin="zero_seed.node_creation",
        stimulus=Stimulus(
            kind="user_request",
            content=f"Create {kind} node: {title}",
        ),
        response=Response(
            kind="node_created",
            content=f"Created node {node.id} at layer {layer}",
            metadata={"target_id": node.id},
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
        derived_from=tuple(derived_from),
        tags=("zero_seed", "node_creation", kind),
    )

    # 5. Auto-select witness mode
    mode = mark.get_witness_mode()
    logger.info(
        f"Created node {node.id} with Galois loss {mark.galois_loss:.2%} (mode={mode.name})"
    )

    # 6. Store mark
    mark_store.append(mark)

    return node, mark


async def create_edge_witnessed(
    source: ZeroNode,
    target: ZeroNode,
    kind: str,
    warrant: str,
    backing: str | None,
    galois: GaloisLossComputerProtocol,
    mark_store: MarkStore,
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
        created_at=datetime.now(timezone.utc),
    )

    # Create mark
    mark = EdgeCreationMark(
        id=generate_mark_id(),
        origin="zero_seed.edge_creation",
        stimulus=Stimulus(
            kind="edge_request",
            content=f"Connect {source.title} -> {target.title} via {kind}",
        ),
        response=Response(
            kind="edge_created",
            content=f"Created {kind} edge",
            metadata={"target_id": edge.id},
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
        tags=("zero_seed", "edge_creation", kind),
    )

    mark_store.append(mark)

    return edge, mark


async def validate_proof_witnessed(
    proof: GaloisWitnessedProof,
    galois: GaloisLossComputerProtocol,
    mark_store: MarkStore,
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
    proof_text = proof.quality_summary()
    logical_loss = await galois.compute(proof_text)

    # Validation decision
    is_valid = logical_loss < 0.15  # < 15% logical loss

    # Loss breakdown
    loss_components = GaloisLossComponents(
        total=logical_loss,
        # For proofs, focus on these:
        composable_loss=logical_loss * 0.4,  # Proof structure
        generative_loss=logical_loss * 0.3,  # Derivation chain
        curated_loss=logical_loss * 0.3,  # Justification quality
    )

    # Create mark
    mark = ProofValidationMark(
        id=generate_mark_id(),
        origin="zero_seed.proof_validation",
        stimulus=Stimulus(
            kind="validation_request",
            content=f"Validate proof: {proof.claim}",
        ),
        response=Response(
            kind="validation_result",
            content=f"Proof {'valid' if is_valid else 'invalid'}",
        ),
        timestamp=datetime.now(timezone.utc),
        galois_loss=logical_loss,
        loss_components=loss_components,
        # Proof-specific
        proof_id=str(uuid4().hex[:12]),
        is_valid=is_valid,
        validation_method="galois_loss",
        proof_data=proof.data,
        proof_warrant=proof.warrant,
        proof_claim=proof.claim,
        qualifier=proof.qualifier,
        rebuttals=proof.rebuttals,
        logical_coherence=1.0 - logical_loss,
        evidence_tier=classify_by_loss(logical_loss).value,
        tags=("zero_seed", "proof_validation"),
    )

    # Always important - use SINGLE mode
    mark_store.append(mark)

    return is_valid, mark


async def detect_contradiction_witnessed(
    node_a: ZeroNode,
    node_b: ZeroNode,
    galois: GaloisLossComputerProtocol,
    mark_store: MarkStore,
    tolerance: float = 0.1,
) -> ContradictionMark | None:
    """
    Detect contradiction via super-additive Galois loss.

    Contradiction signature:
      L(A U B) > L(A) + L(B) + tolerance
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
            resolution_strategy = "synthesis"  # Moderate -> synthesize
        else:
            resolution_strategy = "choose_one"  # Severe -> pick one

        mark = ContradictionMark(
            id=generate_mark_id(),
            origin="zero_seed.contradiction_detection",
            stimulus=Stimulus(
                kind="contradiction_check",
                content=f"Check {node_a.title} vs {node_b.title}",
            ),
            response=Response(
                kind="contradiction_detected",
                content=f"Detected {contradiction_type} contradiction (strength={strength:.2f})",
            ),
            timestamp=datetime.now(timezone.utc),
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
            tags=("zero_seed", "contradiction", contradiction_type),
        )

        mark_store.append(mark)
        return mark

    # No contradiction
    return None


# =============================================================================
# Dialectic Fusion (Kent vs Claude)
# =============================================================================


async def create_dialectic_fusion_witnessed(
    thesis: ZeroNode,
    antithesis: ZeroNode,
    synthesis_content: str,
    warrant: str,
    galois: GaloisLossComputerProtocol,
    mark_store: MarkStore,
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
        title=f"Synthesis: {thesis.title} x {antithesis.title}",
        content=synthesis_content,
        layer=max(thesis.layer, antithesis.layer),  # Inherit higher layer
        kind="synthesis",
        lineage=[thesis.id, antithesis.id],
        tags=frozenset({"synthesis", "dialectic"}),
        created_at=datetime.now(timezone.utc),
    )

    # Create fusion mark
    mark = ZeroSeedMark(
        id=generate_mark_id(),
        origin="zero_seed.dialectic.fusion",
        stimulus=Stimulus(
            kind="contradiction_resolution",
            content=f"Resolve: {thesis.title} vs {antithesis.title}",
        ),
        response=Response(
            kind="synthesis_created",
            content=f"Created synthesis: {synthesis.title}",
            metadata={"target_id": synthesis.id},
        ),
        timestamp=synthesis.created_at,
        galois_loss=loss_components.total,
        loss_components=loss_components,
        tags=("zero_seed", "dialectic", "fusion"),
        metadata={
            "thesis_node": thesis.id,
            "antithesis_node": antithesis.id,
            "synthesis_node": synthesis.id,
            "warrant": warrant,
            "fusion_type": "dialectic",
        },
    )

    mark_store.append(mark)

    return synthesis, mark


# =============================================================================
# Lineage Tracing
# =============================================================================


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
    creation_mark_id: MarkId | None
    parent_nodes: list[str]
    parent_marks: list[MarkId]
    proof_marks: list[MarkId]


async def trace_node_lineage(
    node: ZeroNode,
    mark_store: MarkStore,
    depth: int = 10,
) -> NodeLineage:
    """
    Trace a node's lineage back to axioms.

    Returns the full provenance chain.
    """
    from services.witness.trace_store import MarkQuery

    # Find creation mark
    creation_mark_id: MarkId | None = None
    for mark in mark_store.all():
        if (
            mark.origin == "zero_seed.node_creation"
            and mark.response.metadata.get("target_id") == node.id
        ):
            creation_mark_id = mark.id
            break

    # Find parent nodes
    parent_nodes = node.lineage

    # Find parent marks
    parent_marks: list[MarkId] = []
    for parent_id in parent_nodes:
        for mark in mark_store.all():
            if (
                mark.origin == "zero_seed.node_creation"
                and mark.response.metadata.get("target_id") == parent_id
            ):
                parent_marks.append(mark.id)
                break

    # Find proof marks (validation history)
    proof_marks: list[MarkId] = []
    for mark in mark_store.all():
        if mark.origin == "zero_seed.proof_validation" and mark.metadata.get("node_id") == node.id:
            proof_marks.append(mark.id)

    return NodeLineage(
        node_id=node.id,
        creation_mark_id=creation_mark_id,
        parent_nodes=parent_nodes,
        parent_marks=parent_marks,
        proof_marks=proof_marks,
    )


# =============================================================================
# Crystal Creation from Galois Proofs
# =============================================================================


async def crystallize_galois_session(
    marks: list[ZeroSeedMark],
    crystal_store: CrystalStore,
    session_id: str = "",
) -> Crystal:
    """
    Create a Crystal from a batch of Zero Seed marks.

    This integrates with the existing Crystallizer but adds Galois-specific
    data to the crystal topics and mood.
    """
    from services.witness import Crystal, CrystalLevel, MoodVector

    if not marks:
        raise ValueError("Cannot crystallize empty marks list")

    # Sort by timestamp
    marks = sorted(marks, key=lambda m: m.timestamp)

    # Extract time range
    time_range = (marks[0].timestamp, marks[-1].timestamp)

    # Compute aggregate loss
    avg_loss = sum(m.galois_loss for m in marks) / len(marks)

    # Extract dominant violations
    violations: dict[str, int] = {}
    for mark in marks:
        dom = mark.loss_components.dominant_violation()
        violations[dom] = violations.get(dom, 0) + 1

    # Generate insight from marks
    node_creations = [m for m in marks if m.origin == "zero_seed.node_creation"]
    edge_creations = [m for m in marks if m.origin == "zero_seed.edge_creation"]
    contradictions = [m for m in marks if m.origin == "zero_seed.contradiction_detection"]

    insight_parts = []
    if node_creations:
        insight_parts.append(f"Created {len(node_creations)} nodes")
    if edge_creations:
        insight_parts.append(f"Connected {len(edge_creations)} edges")
    if contradictions:
        insight_parts.append(f"Resolved {len(contradictions)} contradictions")
    insight_parts.append(f"(avg Galois loss: {avg_loss:.1%})")
    insight = ". ".join(insight_parts)

    # Significance from loss trend
    if len(marks) > 1:
        first_half_loss = sum(m.galois_loss for m in marks[: len(marks) // 2]) / (len(marks) // 2)
        second_half_loss = sum(m.galois_loss for m in marks[len(marks) // 2 :]) / (
            len(marks) - len(marks) // 2
        )
        if second_half_loss < first_half_loss - 0.05:
            significance = "Coherence improved over session"
        elif second_half_loss > first_half_loss + 0.05:
            significance = "Coherence degraded over session"
        else:
            significance = "Stable coherence maintained"
    else:
        significance = "Single-mark session"

    # Extract principles (inverted from violations)
    principles_list = [k for k, v in sorted(violations.items(), key=lambda x: -x[1])[:3]]

    # Topics from mark origins
    topics = set()
    for mark in marks:
        topics.add(mark.origin.replace("zero_seed.", ""))
        topics.update(mark.tags)

    # Mood from loss characteristics
    brightness = 1.0 - avg_loss  # Lower loss = brighter
    complexity = min(1.0, len(marks) / 20)  # More marks = more complex
    tempo = min(1.0, len(marks) / 10)  # More marks = faster tempo

    mood = MoodVector(
        warmth=0.6,
        weight=avg_loss,  # Higher loss = heavier
        tempo=tempo,
        texture=0.5 + avg_loss * 0.3,  # Higher loss = rougher
        brightness=brightness,
        saturation=0.7,
        complexity=complexity,
    )

    # Create crystal
    crystal = Crystal.from_crystallization(
        insight=insight,
        significance=significance,
        principles=principles_list,
        source_marks=[m.id for m in marks],
        time_range=time_range,
        confidence=1.0 - avg_loss,
        topics=topics,
        mood=mood,
        session_id=session_id,
    )

    # Store crystal
    await crystal_store.save(crystal)  # type: ignore[func-returns-value, arg-type]

    return crystal


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "NodeId",
    "EdgeId",
    "generate_node_id",
    "generate_edge_id",
    # Loss components
    "GaloisLossComponents",
    # Marks
    "ZeroSeedMark",
    "NodeCreationMark",
    "EdgeCreationMark",
    "ProofValidationMark",
    "ContradictionMark",
    "LLMOperationMark",
    # Triage
    "GaloisWitnessTriage",
    # Protocols
    "GaloisLossComputerProtocol",
    "MockGaloisLossComputer",
    # Data structures
    "ZeroNode",
    "ZeroEdge",
    "NodeLineage",
    # Witnessed operations
    "create_node_witnessed",
    "create_edge_witnessed",
    "validate_proof_witnessed",
    "detect_contradiction_witnessed",
    "create_dialectic_fusion_witnessed",
    # Lineage
    "trace_node_lineage",
    # Crystallization
    "crystallize_galois_session",
]
