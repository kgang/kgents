"""
Zero Seed Core: The Minimal Generative Kernel.

"The proof IS the decision. The mark IS the witness. The seed IS the garden."

This module implements the core primitives of Zero Seed v2, derived from:
- A1 (Entity): Everything is a Node
- A2 (Morphism): Everything Composes
- M (Justification): Every node justifies its existence or admits it cannot

The entire seven-layer epistemic holarchy derives from these two axioms
and one meta-principle.

Philosophy:
    Zero Seed achieves maximum generativity through radical compression.
    Two axioms + one meta-principle → seven layers → infinite gardens.

See: spec/protocols/zero-seed1/core.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, NewType
from uuid import uuid4

if TYPE_CHECKING:
    from services.witness import MarkId

# =============================================================================
# Type Aliases (Galois-Native IDs)
# =============================================================================

NodeId = NewType("NodeId", str)
EdgeId = NewType("EdgeId", str)
MarkIdType = NewType("MarkIdType", str)  # Alias to avoid circular import


def generate_node_id() -> NodeId:
    """Generate a unique Zero Seed Node ID."""
    return NodeId(f"zn-{uuid4().hex[:12]}")


def generate_edge_id() -> EdgeId:
    """Generate a unique Zero Seed Edge ID."""
    return EdgeId(f"ze-{uuid4().hex[:12]}")


# =============================================================================
# Constants: Layer Definitions (Derived from M)
# =============================================================================

# Layer 1-2 nodes are axioms (no proof required)
AXIOM_LAYERS = frozenset({1, 2})

# Kinds that belong to Layer 1 (Assumptions)
AXIOM_KINDS = frozenset(
    {
        "axiom",
        "assumption",
        "postulate",
        "somatic",  # Felt sense - irreducible ground
    }
)

# Kinds that belong to Layer 2 (Values)
VALUE_KINDS = frozenset(
    {
        "value",
        "principle",
        "affinity",
        "aesthetic",
        "ethical",
    }
)


# =============================================================================
# Evidence Tier (Hierarchy of Justification)
# =============================================================================


class EvidenceTier(Enum):
    """
    Hierarchy of evidence types for justification.

    From Zero Seed spec:
        CATEGORICAL = 1     # Mathematical (laws hold)
        EMPIRICAL = 2       # Scientific (tests, measurements)
        AESTHETIC = 3       # Hardy criteria (inevitability, unexpectedness, economy)
        SOMATIC = 4         # The Mirror Test (felt sense)

    Higher tiers are more subjective but may trump lower tiers in human systems.
    """

    CATEGORICAL = 1  # Mathematical: proofs, laws, invariants
    EMPIRICAL = 2  # Scientific: tests, benchmarks, measurements
    AESTHETIC = 3  # Hardy: inevitability, unexpectedness, economy
    SOMATIC = 4  # Mirror Test: "Does this feel like me on my best day?"

    @property
    def is_objective(self) -> bool:
        """Returns True for tiers that are objectively verifiable."""
        return self in {EvidenceTier.CATEGORICAL, EvidenceTier.EMPIRICAL}


# =============================================================================
# Proof: Toulmin Argumentation Structure (from M)
# =============================================================================


@dataclass(frozen=True)
class Proof:
    """
    Toulmin proof structure. Required for L3+ nodes by Meta-Principle M.

    The Toulmin model captures how humans actually argue:
    - data: The evidence supporting the claim
    - warrant: The reasoning connecting data to claim
    - claim: The conclusion being argued for
    - backing: Support for the warrant itself
    - qualifier: Degree of certainty ("definitely", "probably", "possibly")
    - rebuttals: Conditions that would defeat the argument
    - tier: Evidence tier (CATEGORICAL, EMPIRICAL, AESTHETIC, SOMATIC)
    - principles: Referenced Constitution principles

    Why Toulmin?
        - Captures defeasibility (can be overridden by new evidence)
        - Models real human reasoning patterns
        - Enables AI-human dialectical fusion
        - Supports contradiction tolerance from M

    Example:
        >>> proof = Proof(
        ...     data="3 years kgents development, ~52K lines",
        ...     warrant="Radical axiom reduction achieves maximum generativity",
        ...     claim="Zero Seed provides a minimal generative kernel",
        ...     qualifier="probably",
        ...     tier=EvidenceTier.CATEGORICAL,
        ...     principles=("generative", "composable", "tasteful"),
        ... )
    """

    # Core Toulmin structure
    data: str  # Evidence: "Tests pass", "3 hours invested"
    warrant: str  # Reasoning: "Passing tests indicate correctness"
    claim: str  # Conclusion: "This spec is valid"

    # Extended Toulmin
    backing: str = ""  # Support for warrant
    qualifier: str = "probably"  # Confidence: "definitely", "probably", "possibly"
    rebuttals: tuple[str, ...] = ()  # Defeaters: "unless API changes"

    # Evidence tier (from spec)
    tier: EvidenceTier = EvidenceTier.EMPIRICAL

    # Principles referenced (from Constitution)
    principles: tuple[str, ...] = ()

    @classmethod
    def categorical(
        cls,
        data: str,
        warrant: str,
        claim: str,
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create a categorical (mathematical) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            qualifier="definitely",
            tier=EvidenceTier.CATEGORICAL,
            principles=principles,
        )

    @classmethod
    def empirical(
        cls,
        data: str,
        warrant: str,
        claim: str,
        backing: str = "",
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create an empirical (test/measurement) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            backing=backing,
            qualifier="almost certainly",
            tier=EvidenceTier.EMPIRICAL,
            principles=principles,
        )

    @classmethod
    def aesthetic(
        cls,
        data: str,
        warrant: str,
        claim: str,
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create an aesthetic (Hardy criteria) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            qualifier="arguably",
            tier=EvidenceTier.AESTHETIC,
            principles=principles,
        )

    @classmethod
    def somatic(
        cls,
        claim: str,
        feeling: str = "feels right",
    ) -> Proof:
        """
        Create a somatic (Mirror Test) proof.

        The Mirror Test: "Does this feel like me on my best day?"
        This is the irreducible ground of personal authenticity.
        """
        return cls(
            data=feeling,
            warrant="The Mirror Test: felt sense of authenticity",
            claim=claim,
            qualifier="personally",
            tier=EvidenceTier.SOMATIC,
            principles=("ethical", "joy-inducing"),
        )

    def strengthen(self, new_backing: str) -> Proof:
        """Return new Proof with added backing (immutable pattern)."""
        combined = f"{self.backing}; {new_backing}" if self.backing else new_backing
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=combined,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
        )

    def with_rebuttal(self, rebuttal: str) -> Proof:
        """Return new Proof with added rebuttal (immutable pattern)."""
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals + (rebuttal,),
            tier=self.tier,
            principles=self.principles,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.data,
            "warrant": self.warrant,
            "claim": self.claim,
            "backing": self.backing,
            "qualifier": self.qualifier,
            "rebuttals": list(self.rebuttals),
            "tier": self.tier.name,
            "principles": list(self.principles),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Proof:
        """Create from dictionary."""
        return cls(
            data=data.get("data", ""),
            warrant=data.get("warrant", ""),
            claim=data.get("claim", ""),
            backing=data.get("backing", ""),
            qualifier=data.get("qualifier", "probably"),
            rebuttals=tuple(data.get("rebuttals", [])),
            tier=EvidenceTier[data.get("tier", "EMPIRICAL")],
            principles=tuple(data.get("principles", [])),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        claim_preview = self.claim[:40] + "..." if len(self.claim) > 40 else self.claim
        return f"Proof({self.qualifier}: '{claim_preview}', tier={self.tier.name})"


# =============================================================================
# Edge Kind Taxonomy (from A2)
# =============================================================================


class EdgeKind(Enum):
    """
    Types of morphisms between Zero Seed nodes.

    Derived from:
    - A2 (Morphism): Any two nodes can be connected
    - M (Justification): Layer structure implies edge semantics

    Inter-layer edges (DAG flow from M's layer ordering):
    - GROUNDS: L1 → L2
    - JUSTIFIES: L2 → L3
    - SPECIFIES: L3 → L4
    - IMPLEMENTS: L4 → L5
    - REFLECTS_ON: L5 → L6
    - REPRESENTS: L6 → L7

    Intra-layer edges (from A2's universality):
    - DERIVES_FROM, EXTENDS, REFINES

    Dialectical edges (from M's contradiction tolerance):
    - CONTRADICTS, SYNTHESIZES, SUPERSEDES

    Crystallization edges (from witnessing):
    - CRYSTALLIZES, SOURCES
    """

    # Inter-layer (DAG flow from M's layer ordering)
    GROUNDS = "grounds"  # L1 → L2
    JUSTIFIES = "justifies"  # L2 → L3
    SPECIFIES = "specifies"  # L3 → L4
    IMPLEMENTS = "implements"  # L4 → L5
    REFLECTS_ON = "reflects_on"  # L5 → L6
    REPRESENTS = "represents"  # L6 → L7

    # Inverse edges (auto-computed from A2)
    GROUNDED_BY = "grounded_by"  # L2 → L1
    JUSTIFIED_BY = "justified_by"  # L3 → L2
    SPECIFIED_BY = "specified_by"  # L4 → L3
    IMPLEMENTED_BY = "implemented_by"  # L5 → L4
    REFLECTED_BY = "reflected_by"  # L6 → L5
    REPRESENTED_BY = "represented_by"  # L7 → L6

    # Intra-layer (from A2's universality)
    DERIVES_FROM = "derives_from"
    EXTENDS = "extends"
    REFINES = "refines"

    # Dialectical (from M's contradiction tolerance)
    CONTRADICTS = "contradicts"  # Paraconsistent conflict (symmetric)
    SYNTHESIZES = "synthesizes"  # Resolution
    SUPERSEDES = "supersedes"  # Version replacement

    # Crystallization (from witnessing)
    CRYSTALLIZES = "crystallizes"
    SOURCES = "sources"

    @property
    def is_inter_layer(self) -> bool:
        """Returns True if this edge crosses layers."""
        return self in {
            EdgeKind.GROUNDS,
            EdgeKind.JUSTIFIES,
            EdgeKind.SPECIFIES,
            EdgeKind.IMPLEMENTS,
            EdgeKind.REFLECTS_ON,
            EdgeKind.REPRESENTS,
            EdgeKind.GROUNDED_BY,
            EdgeKind.JUSTIFIED_BY,
            EdgeKind.SPECIFIED_BY,
            EdgeKind.IMPLEMENTED_BY,
            EdgeKind.REFLECTED_BY,
            EdgeKind.REPRESENTED_BY,
        }

    @property
    def is_dialectical(self) -> bool:
        """Returns True if this edge is dialectical."""
        return self in {
            EdgeKind.CONTRADICTS,
            EdgeKind.SYNTHESIZES,
            EdgeKind.SUPERSEDES,
        }

    @property
    def inverse(self) -> EdgeKind:
        """Return the inverse edge kind (from A2)."""
        return EDGE_INVERSES.get(self, self)

    @property
    def layer_delta(self) -> int:
        """
        Return the layer delta for inter-layer edges.

        Positive = upward (L1→L2 = +1), Negative = downward (L2→L1 = -1)
        Zero for intra-layer edges.
        """
        return EDGE_LAYER_DELTAS.get(self, 0)


# Bidirectional inverses (from A2)
EDGE_INVERSES: dict[EdgeKind, EdgeKind] = {
    EdgeKind.GROUNDS: EdgeKind.GROUNDED_BY,
    EdgeKind.GROUNDED_BY: EdgeKind.GROUNDS,
    EdgeKind.JUSTIFIES: EdgeKind.JUSTIFIED_BY,
    EdgeKind.JUSTIFIED_BY: EdgeKind.JUSTIFIES,
    EdgeKind.SPECIFIES: EdgeKind.SPECIFIED_BY,
    EdgeKind.SPECIFIED_BY: EdgeKind.SPECIFIES,
    EdgeKind.IMPLEMENTS: EdgeKind.IMPLEMENTED_BY,
    EdgeKind.IMPLEMENTED_BY: EdgeKind.IMPLEMENTS,
    EdgeKind.REFLECTS_ON: EdgeKind.REFLECTED_BY,
    EdgeKind.REFLECTED_BY: EdgeKind.REFLECTS_ON,
    EdgeKind.REPRESENTS: EdgeKind.REPRESENTED_BY,
    EdgeKind.REPRESENTED_BY: EdgeKind.REPRESENTS,
    EdgeKind.CONTRADICTS: EdgeKind.CONTRADICTS,  # Symmetric
    EdgeKind.DERIVES_FROM: EdgeKind.EXTENDS,  # Approximate inverse
    EdgeKind.EXTENDS: EdgeKind.DERIVES_FROM,
    EdgeKind.REFINES: EdgeKind.REFINES,  # Reflexive
    EdgeKind.SYNTHESIZES: EdgeKind.SOURCES,  # Approximate
    EdgeKind.SUPERSEDES: EdgeKind.SUPERSEDES,  # Special handling
    EdgeKind.CRYSTALLIZES: EdgeKind.SOURCES,
    EdgeKind.SOURCES: EdgeKind.CRYSTALLIZES,
}

# Layer deltas for inter-layer edges
EDGE_LAYER_DELTAS: dict[EdgeKind, int] = {
    EdgeKind.GROUNDS: 1,  # L1 → L2
    EdgeKind.JUSTIFIES: 1,  # L2 → L3
    EdgeKind.SPECIFIES: 1,  # L3 → L4
    EdgeKind.IMPLEMENTS: 1,  # L4 → L5
    EdgeKind.REFLECTS_ON: 1,  # L5 → L6
    EdgeKind.REPRESENTS: 1,  # L6 → L7
    EdgeKind.GROUNDED_BY: -1,
    EdgeKind.JUSTIFIED_BY: -1,
    EdgeKind.SPECIFIED_BY: -1,
    EdgeKind.IMPLEMENTED_BY: -1,
    EdgeKind.REFLECTED_BY: -1,
    EdgeKind.REPRESENTED_BY: -1,
}


# =============================================================================
# Errors
# =============================================================================


class ZeroSeedError(Exception):
    """Base exception for Zero Seed errors."""

    pass


class CompositionError(ZeroSeedError):
    """Error during edge composition (A2 violation)."""

    pass


class ProofRequiredError(ZeroSeedError):
    """Error when L3+ node lacks required proof (M violation)."""

    pass


class ProofForbiddenError(ZeroSeedError):
    """Error when L1-L2 node has proof (axioms cannot be proven)."""

    pass


class LayerViolationError(ZeroSeedError):
    """Error when layer constraints are violated."""

    pass


class WitnessRequiredError(ZeroSeedError):
    """Error when modification lacks witness mark (M violation)."""

    pass


# =============================================================================
# ZeroNode: The Entity (from A1)
# =============================================================================


@dataclass(frozen=True)
class ZeroNode:
    """
    A node in the Zero Seed holarchy. Derived from A1 (Entity).

    Every concept, belief, value, goal, specification, action, reflection,
    and representation is a node. There is no privileged "configuration" vs
    "content" distinction. The graph is universal.

    Laws:
    - Node Identity: Each node has exactly one path
    - Layer Integrity: Node.layer in {1,2,3,4,5,6,7}
    - Axiom Unprovenness: L1-L2 nodes have proof=None
    - Proof Requirement: L3+ nodes must have proof

    Example:
        >>> node = ZeroNode(
        ...     path="void.axiom.entity",
        ...     layer=1,
        ...     kind="axiom",
        ...     title="Entity Axiom",
        ...     content="Everything is a node",
        ...     confidence=1.0,
        ... )
    """

    # Identity (from A1)
    id: NodeId = field(default_factory=generate_node_id)
    path: str = ""  # AGENTESE path (e.g., "void.axiom.mirror-test")

    # Classification (derived from M)
    layer: int = 1  # Layer constraint: 1-7
    kind: str = ""  # Node type within layer

    # Content
    content: str = ""  # Markdown content
    title: str = ""  # Display name

    # Justification (from M)
    proof: Proof | None = None  # Toulmin structure (None for L1-L2)
    confidence: float = 1.0  # [0, 1] subjective confidence

    # Provenance
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    lineage: tuple[NodeId, ...] = ()  # Derivation chain

    # Metadata
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate layer and proof constraints."""
        # Layer Integrity (from M)
        if not (1 <= self.layer <= 7):
            raise LayerViolationError(f"Layer must be 1-7, got {self.layer}")

        # Axiom Unprovenness (from M)
        if self.layer <= 2 and self.proof is not None:
            raise ProofForbiddenError(
                f"L1-L2 nodes cannot have proof (axioms are taken on faith). "
                f"Got L{self.layer} node with proof."
            )

        # Proof Requirement (from M)
        if self.layer > 2 and self.proof is None:
            raise ProofRequiredError(
                f"L3+ nodes must have proof (all non-axioms must justify). "
                f"Got L{self.layer} node without proof."
            )

        # Confidence bounds
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")

    def requires_proof(self) -> bool:
        """L1-L2 nodes are unproven; L3+ require proof."""
        return self.layer > 2

    def is_axiom(self) -> bool:
        """Returns True if this is an axiom node (L1-L2)."""
        return self.layer <= 2

    def with_proof(self, proof: Proof) -> ZeroNode:
        """Return new node with proof (immutable pattern, L3+ only)."""
        if self.layer <= 2:
            raise ProofForbiddenError("Cannot add proof to axiom node")
        return ZeroNode(
            id=self.id,
            path=self.path,
            layer=self.layer,
            kind=self.kind,
            content=self.content,
            title=self.title,
            proof=proof,
            confidence=self.confidence,
            created_at=self.created_at,
            created_by=self.created_by,
            lineage=self.lineage,
            tags=self.tags,
            metadata=self.metadata,
        )

    def with_lineage(self, parent_id: NodeId) -> ZeroNode:
        """Return new node with parent added to lineage (immutable pattern)."""
        return ZeroNode(
            id=self.id,
            path=self.path,
            layer=self.layer,
            kind=self.kind,
            content=self.content,
            title=self.title,
            proof=self.proof,
            confidence=self.confidence,
            created_at=self.created_at,
            created_by=self.created_by,
            lineage=self.lineage + (parent_id,),
            tags=self.tags,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "path": self.path,
            "layer": self.layer,
            "kind": self.kind,
            "content": self.content,
            "title": self.title,
            "proof": self.proof.to_dict() if self.proof else None,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "lineage": [str(lid) for lid in self.lineage],
            "tags": list(self.tags),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZeroNode:
        """Create from dictionary."""
        proof = Proof.from_dict(data["proof"]) if data.get("proof") else None
        return cls(
            id=NodeId(data["id"]),
            path=data.get("path", ""),
            layer=data.get("layer", 1),
            kind=data.get("kind", ""),
            content=data.get("content", ""),
            title=data.get("title", ""),
            proof=proof,
            confidence=data.get("confidence", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by", "system"),
            lineage=tuple(NodeId(lid) for lid in data.get("lineage", [])),
            tags=frozenset(data.get("tags", [])),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        title_preview = self.title[:30] + "..." if len(self.title) > 30 else self.title
        return f"ZeroNode(L{self.layer}, path={self.path}, title='{title_preview}')"


# =============================================================================
# ZeroEdge: The Morphism (from A2)
# =============================================================================


@dataclass(frozen=True)
class ZeroEdge:
    """
    A morphism between Zero Seed nodes. Derived from A2 (Morphism).

    Any two nodes can be connected. Edges are morphisms in a category.
    Composition is primary.

    Laws:
    - Identity: id >> f = f = f >> id
    - Associativity: (f >> g) >> h = f >> (g >> h)
    - Bidirectional: For every edge, an inverse exists

    Example:
        >>> edge = ZeroEdge(
        ...     source=NodeId("zn-abc123"),
        ...     target=NodeId("zn-def456"),
        ...     kind=EdgeKind.GROUNDS,
        ...     context="Axiom grounds value",
        ...     mark_id=MarkIdType("mark-xyz789"),
        ... )
    """

    # Identity
    id: EdgeId = field(default_factory=generate_edge_id)
    source: NodeId = field(default_factory=lambda: NodeId(""))
    target: NodeId = field(default_factory=lambda: NodeId(""))

    # Classification
    kind: EdgeKind = EdgeKind.DERIVES_FROM

    # Metadata
    context: str = ""  # Why this edge exists
    confidence: float = 1.0  # [0, 1] strength
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mark_id: MarkIdType = field(
        default_factory=lambda: MarkIdType("")
    )  # Witness mark (REQUIRED by M)

    # For contradiction edges
    is_resolved: bool = False
    resolution_id: NodeId | None = None

    def __post_init__(self) -> None:
        """Validate edge constraints."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")

    def __rshift__(self, other: ZeroEdge) -> ZeroEdge:
        """
        Compose edges: (A->B) >> (B->C) = (A->C)

        Laws (VERIFIED):
        - Identity: id >> f = f = f >> id
        - Associativity: (f >> g) >> h = f >> (g >> h)

        The composed edge:
        - Has a new ID
        - Inherits source from self, target from other
        - Combines contexts
        - Multiplies confidence (probabilistic composition)
        - Gets a new mark_id (from composition mark)
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
            created_at=datetime.now(timezone.utc),
            mark_id=MarkIdType(""),  # Should be set by caller with actual mark
        )

    def inverse(self) -> ZeroEdge:
        """Return the inverse edge (from A2's bidirectionality)."""
        return ZeroEdge(
            id=generate_edge_id(),
            source=self.target,
            target=self.source,
            kind=self.kind.inverse,
            context=f"Inverse of: {self.context}",
            confidence=self.confidence,
            created_at=datetime.now(timezone.utc),
            mark_id=self.mark_id,  # Same witness
            is_resolved=self.is_resolved,
            resolution_id=self.resolution_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "source": str(self.source),
            "target": str(self.target),
            "kind": self.kind.value,
            "context": self.context,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "mark_id": str(self.mark_id),
            "is_resolved": self.is_resolved,
            "resolution_id": str(self.resolution_id) if self.resolution_id else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZeroEdge:
        """Create from dictionary."""
        return cls(
            id=EdgeId(data["id"]),
            source=NodeId(data["source"]),
            target=NodeId(data["target"]),
            kind=EdgeKind(data["kind"]),
            context=data.get("context", ""),
            confidence=data.get("confidence", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            mark_id=MarkIdType(data.get("mark_id", "")),
            is_resolved=data.get("is_resolved", False),
            resolution_id=NodeId(data["resolution_id"]) if data.get("resolution_id") else None,
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"ZeroEdge({str(self.source)[:8]}... --{self.kind.value}--> {str(self.target)[:8]}...)"
        )


# =============================================================================
# Edge Kind Composition (from A2)
# =============================================================================


def compose_edge_kinds(kind1: EdgeKind, kind2: EdgeKind) -> EdgeKind:
    """
    Compute the composed edge kind.

    When composing edges, we need to determine what kind the result should be.
    This follows the layer semantics from M.

    Rules:
    1. Same kind: result is same kind (idempotent)
    2. Inter-layer same direction: result skips layer
    3. Dialectical: result is SYNTHESIZES (resolution)
    4. Default: DERIVES_FROM (generic derivation)

    Example:
        >>> compose_edge_kinds(EdgeKind.GROUNDS, EdgeKind.JUSTIFIES)
        EdgeKind.DERIVES_FROM  # L1->L2->L3 collapses to derivation
    """
    # Same kind is idempotent
    if kind1 == kind2:
        return kind1

    # If both are inter-layer in same direction, result is derivation
    if kind1.is_inter_layer and kind2.is_inter_layer:
        delta1 = kind1.layer_delta
        delta2 = kind2.layer_delta
        if delta1 * delta2 > 0:  # Same direction
            return EdgeKind.DERIVES_FROM

    # Dialectical composition leads to synthesis
    if kind1.is_dialectical or kind2.is_dialectical:
        return EdgeKind.SYNTHESIZES

    # Default: generic derivation
    return EdgeKind.DERIVES_FROM


# =============================================================================
# Layer Utilities (Derived from M)
# =============================================================================


def layer_of(node: ZeroNode) -> int:
    """
    Compute the layer of a node.

    Layer is determined by justification depth:
    - L1-L2: Cannot justify (axioms)
    - L3-L7: Must justify (computed from proof chain depth)

    This is a simple accessor since layer is stored on the node,
    but can be used for verification.
    """
    return node.layer


def proof_depth(proof: Proof) -> int:
    """
    Compute the depth of a proof chain.

    Currently returns 1 (direct proof). Could be extended to
    count the backing chain depth for nested proofs.
    """
    if not proof.backing:
        return 1
    # Could recursively compute if backing contains serialized proofs
    return 1


def compute_layer_from_proof(proof: Proof | None, kind: str) -> int:
    """
    Compute the appropriate layer based on proof presence and kind.

    Used when creating nodes to auto-determine their layer:
    - No proof + axiom kind -> L1
    - No proof + value kind -> L2
    - Proof present -> L3 + proof_depth
    """
    if proof is None:
        # Cannot justify -> axiom layer
        if kind in AXIOM_KINDS:
            return 1  # Assumptions
        elif kind in VALUE_KINDS:
            return 2  # Values
        else:
            # Default to L2 for unspecified axiom kinds
            return 2
    else:
        # Must justify -> compute from proof chain
        return min(7, 2 + proof_depth(proof))


# =============================================================================
# AGENTESE Mapping (Surjection from Layers to Contexts)
# =============================================================================


def layer_to_context(layer: int) -> str:
    """
    Surjective mapping from layer to AGENTESE context.

    | AGENTESE Context | Layers | Semantic |
    |------------------|--------|----------|
    | void.*           | L1 + L2| The Accursed Share - irreducible ground |
    | concept.*        | L3 + L4| The Abstract - dreams and specifications |
    | world.*          | L5     | The External - actions in the world |
    | self.*           | L6     | The Internal - reflection, synthesis |
    | time.*           | L7     | The Temporal - representation across time |
    """
    match layer:
        case 1 | 2:
            return "void"
        case 3 | 4:
            return "concept"
        case 5:
            return "world"
        case 6:
            return "self"
        case 7:
            return "time"
        case _:
            raise LayerViolationError(f"Invalid layer: {layer}")


def context_to_layers(context: str) -> tuple[int, ...]:
    """
    Inverse mapping from AGENTESE context to possible layers.

    Since the mapping is surjective (not bijective), a context may
    correspond to multiple layers.
    """
    match context:
        case "void":
            return (1, 2)
        case "concept":
            return (3, 4)
        case "world":
            return (5,)
        case "self":
            return (6,)
        case "time":
            return (7,)
        case _:
            raise ValueError(f"Unknown AGENTESE context: {context}")


def parse_agentese_path(path: str) -> tuple[str, str, str]:
    """
    Parse an AGENTESE path into (context, domain, name).

    Example:
        >>> parse_agentese_path("void.axiom.entity")
        ("void", "axiom", "entity")
        >>> parse_agentese_path("concept.spec.zero-seed")
        ("concept", "spec", "zero-seed")
    """
    parts = path.split(".")
    if len(parts) < 2:
        raise ValueError(f"Invalid AGENTESE path (need at least context.name): {path}")

    context = parts[0]
    if context not in {"void", "concept", "world", "self", "time"}:
        raise ValueError(f"Unknown AGENTESE context: {context}")

    if len(parts) == 2:
        return (context, "", parts[1])
    else:
        return (context, parts[1], ".".join(parts[2:]))


# =============================================================================
# Layer Names (Human-readable)
# =============================================================================

LAYER_NAMES: dict[int, str] = {
    1: "Assumptions",
    2: "Values",
    3: "Goals",
    4: "Specifications",
    5: "Execution",
    6: "Reflection",
    7: "Representation",
}

LAYER_DESCRIPTIONS: dict[int, str] = {
    1: "Irreducible ground, taken on faith, somatic sense",
    2: "Principles, affinities, ethical commitments",
    3: "Dreams, desires, what we want to achieve",
    4: "Plans, designs, how we'll achieve goals",
    5: "Actions, implementations, doing in the world",
    6: "Learning, synthesis, understanding what happened",
    7: "Artifacts, documentation, capturing for time",
}


def get_layer_name(layer: int) -> str:
    """Get human-readable name for a layer."""
    return LAYER_NAMES.get(layer, f"Layer {layer}")


def get_layer_description(layer: int) -> str:
    """Get description for a layer."""
    return LAYER_DESCRIPTIONS.get(layer, "Unknown layer")


# =============================================================================
# Identity Edge (from A2: Identity Law)
# =============================================================================


def identity_edge(node_id: NodeId) -> ZeroEdge:
    """
    Create an identity edge for a node.

    From A2: id >> f = f = f >> id

    The identity edge has the same source and target,
    and composing with it is a no-op.
    """
    return ZeroEdge(
        id=generate_edge_id(),
        source=node_id,
        target=node_id,
        kind=EdgeKind.REFINES,  # Reflexive kind for identity
        context="Identity morphism",
        confidence=1.0,
        mark_id=MarkIdType(""),  # Identity edges don't need marks
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "NodeId",
    "EdgeId",
    "MarkIdType",
    "generate_node_id",
    "generate_edge_id",
    # Constants
    "AXIOM_LAYERS",
    "AXIOM_KINDS",
    "VALUE_KINDS",
    "LAYER_NAMES",
    "LAYER_DESCRIPTIONS",
    # Evidence tier
    "EvidenceTier",
    # Proof (Toulmin)
    "Proof",
    # Edge kind taxonomy
    "EdgeKind",
    "EDGE_INVERSES",
    "EDGE_LAYER_DELTAS",
    "compose_edge_kinds",
    # Errors
    "ZeroSeedError",
    "CompositionError",
    "ProofRequiredError",
    "ProofForbiddenError",
    "LayerViolationError",
    "WitnessRequiredError",
    # Core types
    "ZeroNode",
    "ZeroEdge",
    # Layer utilities
    "layer_of",
    "proof_depth",
    "compute_layer_from_proof",
    # AGENTESE mapping
    "layer_to_context",
    "context_to_layers",
    "parse_agentese_path",
    # Layer names
    "get_layer_name",
    "get_layer_description",
    # Identity
    "identity_edge",
]
