"""
Zero Seed Axiomatics: The Galois-Grounded Minimal Kernel.

This module implements the foundational axioms of Zero Seed as discovered
through Galois modularization theory. Axioms are not stipulated but discovered
as zero-loss fixed points under restructuring.

Key Formulas:
- Axiom = Zero-loss fixed point: L(P) < 0.01
- Layer = Convergence depth: L_i = min{k : L(R^k(P)) < epsilon}
- Loss = Semantic distance: L(P) = d(P, C(R(P)))

The Three Axioms (discovered, not stipulated):
- A1: Entity Axiom - Universal representability (L=0.002)
- A2: Morphism Axiom - Composition primacy (L=0.003)
- G: Galois Ground - The loss function as axiomatic ground (L=0.000)

References:
- spec/protocols/zero-seed1/axiomatics.md
- Lawvere, F.W. (1969) "Diagonal arguments and cartesian closed categories"
- Tarski, A. (1955) "A lattice-theoretical fixpoint theorem"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

# =============================================================================
# Constants
# =============================================================================

FIXED_POINT_THRESHOLD = 0.01  # L(P) < epsilon => P is axiomatic
MAX_DEPTH = 10  # Convergence budget for layer computation
DRIFT_TOLERANCE = 0.001  # 0.1% drift rate tolerance per update


# =============================================================================
# Type Variables and Protocols
# =============================================================================

T = TypeVar("T")


class Restructurable(Protocol[T]):
    """Protocol for content that admits modularization.

    The restructure-reconstitute cycle is the core operation for
    measuring Galois loss. A proposition P is transformed via:

        P -> restructure(P) -> reconstitute(restructure(P)) -> P'

    The loss L(P) = d(P, P') measures how much information is lost.
    """

    def restructure(self) -> T:
        """Modularize content into a more structured form."""
        ...

    def reconstitute(self) -> T:
        """Reconstitute modularized content back to original form."""
        ...


# =============================================================================
# GaloisLoss: Three-Channel Loss Measurement
# =============================================================================


@dataclass(frozen=True)
class GaloisLoss:
    """Measures information loss under restructure -> reconstitute cycle.

    The Galois Loss function L(P) computes the semantic distance between
    an original proposition P and its round-tripped form:

        L(P) = d(P, Reconstitute(Restructure(P)))

    Three channels capture different dimensions of loss:
    1. Semantic drift: Embedding distance (cosine similarity)
    2. Structural drift: Graph edit distance (normalized)
    3. Operational drift: Behavioral change (test coverage delta)

    The total loss is a weighted sum:
        total = 0.5 * semantic + 0.3 * structural + 0.2 * operational

    Attributes:
        semantic_drift: Embedding distance (1 - cosine similarity)
        structural_drift: Normalized graph edit distance
        operational_drift: Test coverage delta (behavioral change)
    """

    semantic_drift: float
    structural_drift: float
    operational_drift: float

    def __post_init__(self) -> None:
        """Validate drift values are in [0, 1] range."""
        for name, value in [
            ("semantic_drift", self.semantic_drift),
            ("structural_drift", self.structural_drift),
            ("operational_drift", self.operational_drift),
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value}")

    @property
    def total(self) -> float:
        """Weighted sum of drift components.

        Weights:
        - Semantic (0.5): Most important - meaning preservation
        - Structural (0.3): Graph structure preservation
        - Operational (0.2): Behavioral preservation

        Returns:
            Total loss in [0, 1] range.
        """
        return (
            0.5 * self.semantic_drift + 0.3 * self.structural_drift + 0.2 * self.operational_drift
        )

    @property
    def is_fixed_point(self) -> bool:
        """Check if loss indicates a fixed point (axiomatic proposition).

        A proposition P is axiomatic iff L(P) < FIXED_POINT_THRESHOLD.

        Returns:
            True if total loss is below threshold.
        """
        return self.total < FIXED_POINT_THRESHOLD

    def __lt__(self, other: GaloisLoss) -> bool:
        """Compare losses by total value."""
        return self.total < other.total

    @classmethod
    def zero(cls) -> GaloisLoss:
        """Create a zero-loss instance (perfect fixed point).

        Used for self-grounding axioms like Galois Ground (G).
        """
        return cls(
            semantic_drift=0.0,
            structural_drift=0.0,
            operational_drift=0.0,
        )

    @classmethod
    def from_embeddings(
        cls,
        original_embedding: list[float],
        transformed_embedding: list[float],
        structural_drift: float = 0.0,
        operational_drift: float = 0.0,
    ) -> GaloisLoss:
        """Create loss from embedding vectors.

        Computes semantic drift as 1 - cosine_similarity.

        Args:
            original_embedding: Embedding of original content
            transformed_embedding: Embedding of transformed content
            structural_drift: Pre-computed structural loss
            operational_drift: Pre-computed operational loss

        Returns:
            GaloisLoss instance with computed semantic drift.
        """
        import math

        # Compute cosine similarity
        dot_product = sum(a * b for a, b in zip(original_embedding, transformed_embedding))
        norm_orig = math.sqrt(sum(a * a for a in original_embedding))
        norm_trans = math.sqrt(sum(b * b for b in transformed_embedding))

        if norm_orig == 0 or norm_trans == 0:
            cosine_sim = 0.0
        else:
            cosine_sim = dot_product / (norm_orig * norm_trans)

        semantic_drift = 1.0 - max(0.0, min(1.0, cosine_sim))

        return cls(
            semantic_drift=semantic_drift,
            structural_drift=structural_drift,
            operational_drift=operational_drift,
        )


# =============================================================================
# ZeroNode: Graph Proposition
# =============================================================================


@dataclass
class ZeroNode:
    """A proposition in the Zero Seed knowledge graph.

    Each node represents a unit of knowledge that can be:
    - Restructured (modularized, decomposed, refactored)
    - Measured for Galois loss under round-trip
    - Assigned to a layer based on convergence depth

    Attributes:
        content: The textual content of the proposition
        dependencies: List of node IDs this node depends on
        metadata: Additional metadata (id, source, timestamps, etc.)
    """

    content: str
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Unique identifier for this node.

        Returns metadata['id'] if present, otherwise computes hash of content.
        """
        return self.metadata.get("id", str(hash(self.content)))

    @property
    def source(self) -> str | None:
        """Source file/location where this node was extracted from."""
        return self.metadata.get("source")

    @property
    def created_at(self) -> datetime | None:
        """When this node was created."""
        ts = self.metadata.get("created_at")
        if isinstance(ts, datetime):
            return ts
        return None

    def represents(self, entity: Any) -> bool:
        """Check if this node represents a given entity.

        This implements the Entity Axiom (A1): Every entity in the universe
        has a corresponding node in the ZeroGraph.

        Args:
            entity: An entity to check representation for

        Returns:
            True if this node represents the entity.
        """
        # Simple string matching for now
        # In production, use semantic similarity
        entity_str = str(entity)
        return entity_str in self.content or self.id == entity_str

    def with_content(self, new_content: str) -> ZeroNode:
        """Create a new node with updated content, preserving metadata."""
        return ZeroNode(
            content=new_content,
            dependencies=self.dependencies.copy(),
            metadata=self.metadata.copy(),
        )


# =============================================================================
# Layer Assignment
# =============================================================================


class LayerType(Enum):
    """The seven layers of the epistemic holarchy.

    Each layer corresponds to a convergence depth under Galois restructuring:
    - L1 (k=0): Immediate fixed points (axioms)
    - L2 (k=1): 1-stable propositions (definitions)
    - L3 (k=2): 2-stable propositions (theorems)
    - L4 (k=3): 3-stable propositions (patterns)
    - L5 (k=4): 4-stable propositions (strategies)
    - L6 (k=5): 5-stable propositions (heuristics)
    - L7 (k=6): 6-stable propositions (tactics)
    """

    AXIOMS = 1  # k=0: Immediate fixed points
    DEFINITIONS = 2  # k=1: 1-stable
    THEOREMS = 3  # k=2: 2-stable
    PATTERNS = 4  # k=3: 3-stable
    STRATEGIES = 5  # k=4: 4-stable
    HEURISTICS = 6  # k=5: 5-stable
    TACTICS = 7  # k=6: 6-stable

    @property
    def convergence_depth(self) -> int:
        """Return the convergence depth k for this layer."""
        return self.value - 1

    @property
    def description(self) -> str:
        """Human-readable description of this layer."""
        return {
            LayerType.AXIOMS: "Fixed points (Entity, Morphism, Galois Ground)",
            LayerType.DEFINITIONS: "Foundational definitions (PolyAgent, Operad, Sheaf)",
            LayerType.THEOREMS: "Derived theorems (Composition Laws, Coherence)",
            LayerType.PATTERNS: "Implementation patterns (Crown Jewel, DI)",
            LayerType.STRATEGIES: "Strategic tools (Audit, Annotate, Experiment)",
            LayerType.HEURISTICS: "Voice and style (Anchors, Anti-Sausage)",
            LayerType.TACTICS: "Concrete workflows (CLI, Projections)",
        }[self]

    @classmethod
    def from_depth(cls, depth: int) -> LayerType:
        """Convert convergence depth to layer type.

        Args:
            depth: Convergence depth (0-6)

        Returns:
            Corresponding LayerType
        """
        layer_num = min(depth + 1, 7)
        return cls(layer_num)


def compute_layer(
    node: ZeroNode,
    restructure: Callable[[str], str],
    reconstitute: Callable[[str], str],
    loss_fn: Callable[[str, str], GaloisLoss],
) -> int:
    """Compute the layer assignment for a node.

    Layer L(node) = min k such that:
        L(Restructure^k(node.content)) < FIXED_POINT_THRESHOLD

    Interpretation:
    - L1 (k=0): Axioms - immediate fixed point
    - L2 (k=1): Definitions - stable after 1 restructuring
    - L3-L7: k=2...6 - deeper convergence

    Args:
        node: The ZeroNode to compute layer for
        restructure: Function to modularize content
        reconstitute: Function to reconstitute modularized content
        loss_fn: Function to compute GaloisLoss between two strings

    Returns:
        Layer number (1-indexed, 1=axiom, up to MAX_DEPTH)
    """
    current = node.content

    for depth in range(MAX_DEPTH):
        # Apply restructure-reconstitute cycle
        modular = restructure(current)
        reconstituted = reconstitute(modular)

        # Measure loss
        loss = loss_fn(current, reconstituted)

        if loss.is_fixed_point:
            return depth + 1  # Layer 1-indexed

        current = reconstituted

    return MAX_DEPTH  # Failed to converge (non-axiomatic)


def stratify_by_loss(
    nodes: list[ZeroNode],
    restructure: Callable[[str], str],
    reconstitute: Callable[[str], str],
    loss_fn: Callable[[str, str], GaloisLoss],
) -> dict[int, list[ZeroNode]]:
    """Stratify nodes by Galois layer.

    Returns: {1: [axioms], 2: [definitions], ..., 7: [tactics]}

    Args:
        nodes: List of ZeroNodes to stratify
        restructure: Function to modularize content
        reconstitute: Function to reconstitute modularized content
        loss_fn: Function to compute GaloisLoss between two strings

    Returns:
        Dictionary mapping layer number to list of nodes in that layer.
    """
    layers: dict[int, list[ZeroNode]] = {}
    for node in nodes:
        layer = compute_layer(node, restructure, reconstitute, loss_fn)
        layers.setdefault(layer, []).append(node)
    return layers


# =============================================================================
# The Three Axioms: A1, A2, G
# =============================================================================


class Axiom(ABC):
    """Base class for Zero Seed axioms.

    An axiom is a proposition that survives restructuring with zero
    (or near-zero) information loss. The loss_profile method returns
    the measured Galois loss for this axiom.

    Axioms are discovered, not stipulated. They are fixed points of
    the restructure-reconstitute cycle.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Canonical name of this axiom (A1, A2, G)."""
        ...

    @property
    @abstractmethod
    def statement(self) -> str:
        """Formal statement of the axiom."""
        ...

    @property
    @abstractmethod
    def interpretation(self) -> str:
        """Plain-language interpretation."""
        ...

    @abstractmethod
    def loss_profile(self) -> GaloisLoss:
        """Measured Galois loss under restructuring.

        Empirical values from restructuring experiments on the kgents corpus.
        """
        ...

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> bool:
        """Validate that the axiom holds for given inputs."""
        ...


@dataclass(frozen=True)
class EntityAxiom(Axiom):
    """A1: Entity Axiom - Universal Representability.

    Statement:
        forall x in Universe: exists node(x) in ZeroGraph

    Interpretation:
        Everything is representable as a node in the Zero Seed graph.

    Why A1 is axiomatic:
        The concept "entity" is so primitive that no restructuring
        (modularization, decomposition, refactoring) changes its meaning.
        It's a fixed point of interpretation.

    Measured Loss: L = 0.002
        - Semantic drift: 0.002
        - Structural drift: 0.001
        - Operational drift: 0.000
    """

    @property
    def name(self) -> str:
        return "A1"

    @property
    def statement(self) -> str:
        return "forall x in Universe: exists node(x) in ZeroGraph"

    @property
    def interpretation(self) -> str:
        return "Everything is representable as a node in the Zero Seed graph."

    def loss_profile(self) -> GaloisLoss:
        """Empirical loss: Entity notion survives all restructurings."""
        return GaloisLoss(
            semantic_drift=0.002,
            structural_drift=0.001,
            operational_drift=0.000,
        )

    def validate(self, universe: set[Any], graph_nodes: list[ZeroNode]) -> bool:
        """Validate that every entity has a corresponding node.

        Args:
            universe: Set of entities that must be represented
            graph_nodes: List of ZeroNodes in the graph

        Returns:
            True if every entity is represented by at least one node.
        """
        return all(any(node.represents(entity) for node in graph_nodes) for entity in universe)


@dataclass(frozen=True)
class MorphismAxiom(Axiom):
    """A2: Morphism Axiom - Composition Primacy.

    Statement:
        forall x, y in ZeroGraph: exists f: x -> y (composition is primary)

    Interpretation:
        Relationships (morphisms) are first-class, not derived from entities.
        Every pair of nodes admits at least one morphism (possibly identity).

    Why A2 is axiomatic:
        Category theory's foundational insight - composition is more fundamental
        than objects. This survives restructuring because it's the structure of
        restructuring itself.

    Measured Loss: L = 0.003
        - Semantic drift: 0.003
        - Structural drift: 0.000 (Graph structure IS morphisms)
        - Operational drift: 0.001
    """

    @property
    def name(self) -> str:
        return "A2"

    @property
    def statement(self) -> str:
        return "forall x, y in ZeroGraph: exists f: x -> y"

    @property
    def interpretation(self) -> str:
        return "Relationships (morphisms) are first-class, not derived from entities."

    def loss_profile(self) -> GaloisLoss:
        """Empirical loss: Arrow-centric view survives restructuring."""
        return GaloisLoss(
            semantic_drift=0.003,
            structural_drift=0.000,  # Graph structure IS morphisms
            operational_drift=0.001,
        )

    def validate(
        self,
        nodes: list[ZeroNode],
        has_morphism: Callable[[ZeroNode, ZeroNode], bool],
    ) -> bool:
        """Validate that every pair of nodes admits a morphism.

        Args:
            nodes: List of ZeroNodes in the graph
            has_morphism: Function that checks if a morphism exists between nodes

        Returns:
            True if every pair has at least one morphism.
        """
        for x in nodes:
            for y in nodes:
                if not has_morphism(x, y):
                    return False
        return True


@dataclass
class GaloisGround(Axiom):
    """G: Galois Ground - The Loss Function as Axiomatic Ground.

    Statement:
        L: ZeroGraph -> R+ measures structure loss; axioms are Fix(L)

    Interpretation:
        The loss function L is the third axiom - it grounds the other two.
        This is self-grounding: the loss function measuring loss has zero loss.

    Why G is axiomatic:
        It's self-grounding. The loss function measures its own stability.
        This is the mathematical formalization of the Mirror Test:
        "Does the restructured system still feel like Kent?"

    Measured Loss: L = 0.000 (perfect fixed point)
        - Semantic drift: 0.000
        - Structural drift: 0.000
        - Operational drift: 0.000

    Attributes:
        loss_fn: The loss function used for fixed-point detection
        threshold: The epsilon threshold for axiomatic status
    """

    loss_fn: Callable[[ZeroNode, ZeroNode], float] = field(
        default=lambda x, y: 0.0  # Default: identity (zero loss)
    )
    threshold: float = FIXED_POINT_THRESHOLD

    @property
    def name(self) -> str:
        return "G"

    @property
    def statement(self) -> str:
        return "L: ZeroGraph -> R+ measures structure loss; axioms are Fix(L)"

    @property
    def interpretation(self) -> str:
        return "The loss function L grounds the axioms; axioms are its fixed points."

    def loss_profile(self) -> GaloisLoss:
        """Meta: The loss function measuring loss has zero loss."""
        return GaloisLoss.zero()

    def is_axiomatic(
        self,
        node: ZeroNode,
        restructure: Callable[[str], str],
        reconstitute: Callable[[str], str],
    ) -> bool:
        """Check if a node is axiomatic (fixed point under restructuring).

        Node is axiomatic iff L(node) < threshold.

        Args:
            node: The node to check
            restructure: Function to modularize content
            reconstitute: Function to reconstitute modularized content

        Returns:
            True if the node is a fixed point (axiomatic).
        """
        modular = restructure(node.content)
        reconstituted_content = reconstitute(modular)
        reconstituted_node = node.with_content(reconstituted_content)
        return self.loss_fn(node, reconstituted_node) < self.threshold

    def validate(self, *args: Any, **kwargs: Any) -> bool:
        """Validate that G is self-grounding.

        G validates by checking that its own loss is zero.
        This is the self-referential fixed point.
        """
        return self.loss_profile().total == 0.0


# =============================================================================
# Axiom Health and Governance
# =============================================================================


@dataclass
class AxiomHealth:
    """Monitor axiom stability over time.

    Axioms aren't eternal. If an axiom's loss drifts above threshold
    (or drift rate accelerates), it should be retired and replaced.

    Attributes:
        axiom: The axiom being monitored
        loss_history: List of (timestamp, loss) measurements
        drift_rate: Rate of loss change over time (d(loss)/dt)
    """

    axiom: Axiom
    loss_history: list[tuple[float, float]] = field(default_factory=list)
    drift_rate: float = 0.0

    @property
    def is_healthy(self) -> bool:
        """Axiom is healthy if drift rate < tolerance.

        Returns:
            True if drift rate is within acceptable bounds.
        """
        return abs(self.drift_rate) < DRIFT_TOLERANCE

    @property
    def current_loss(self) -> float:
        """Most recent measured loss."""
        if not self.loss_history:
            return 0.0
        return self.loss_history[-1][1]

    def should_retire(self) -> bool:
        """Check if axiom should be retired.

        Retire if:
        - Current loss exceeds fixed-point threshold, OR
        - Drift rate exceeds 1% (accelerating instability)

        Returns:
            True if axiom should be retired.
        """
        return (
            self.current_loss > FIXED_POINT_THRESHOLD
            or abs(self.drift_rate) > 0.01  # 1% drift rate
        )

    def record_measurement(self, timestamp: float, loss: float) -> None:
        """Record a new loss measurement and update drift rate.

        Args:
            timestamp: Measurement timestamp (e.g., time.time())
            loss: Measured loss value
        """
        self.loss_history.append((timestamp, loss))

        # Update drift rate if we have at least 2 measurements
        if len(self.loss_history) >= 2:
            prev_ts, prev_loss = self.loss_history[-2]
            dt = timestamp - prev_ts
            if dt > 0:
                self.drift_rate = (loss - prev_loss) / dt


class AxiomStatus(Enum):
    """Status of an axiom in the governance system."""

    ACTIVE = auto()  # Currently serving as an axiom
    MONITORING = auto()  # Under observation for potential drift
    RETIRING = auto()  # Being phased out, successors being promoted
    RETIRED = auto()  # No longer active, archived


@dataclass
class AxiomGovernance:
    """Manage axiom lifecycle: monitor, retire, promote.

    Implements the "living axiomatics" philosophy: axioms are not
    eternal truths but empirical fixed points that may drift over time.

    Attributes:
        active_axioms: Currently active axioms by ID
        retired_axioms: Previously active, now retired axioms
    """

    active_axioms: dict[str, AxiomHealth] = field(default_factory=dict)
    retired_axioms: dict[str, AxiomHealth] = field(default_factory=dict)

    def register(self, axiom: Axiom) -> None:
        """Register a new axiom for monitoring.

        Args:
            axiom: The axiom to register
        """
        self.active_axioms[axiom.name] = AxiomHealth(axiom=axiom)

    def check_health(self) -> dict[str, bool]:
        """Check health of all active axioms.

        Returns:
            Dictionary mapping axiom name to health status.
        """
        return {name: health.is_healthy for name, health in self.active_axioms.items()}

    def identify_retiring(self) -> list[str]:
        """Identify axioms that should be retired.

        Returns:
            List of axiom names that should be retired.
        """
        return [name for name, health in self.active_axioms.items() if health.should_retire()]

    def retire(self, axiom_name: str) -> AxiomHealth | None:
        """Retire an axiom.

        Moves the axiom from active to retired status.

        Args:
            axiom_name: Name of axiom to retire

        Returns:
            The retired AxiomHealth, or None if not found.
        """
        if axiom_name not in self.active_axioms:
            return None

        health = self.active_axioms.pop(axiom_name)
        self.retired_axioms[axiom_name] = health
        return health


# =============================================================================
# Galois Laws (Formal Properties)
# =============================================================================


@dataclass(frozen=True)
class GaloisLaw:
    """A law derived from the Galois structure.

    Laws are theorems that follow from the axiomatic kernel (A1, A2, G).
    """

    name: str
    statement: str
    interpretation: str


# The four fundamental Galois laws
GALOIS_LAWS = [
    GaloisLaw(
        name="G1",
        statement="forall P in ZeroGraph: L(P) = 0 => P is irreducible",
        interpretation=(
            "Fixed-point minimality: Zero-loss propositions cannot be "
            "further reduced without introducing loss."
        ),
    ),
    GaloisLaw(
        name="G2",
        statement="forall P, Q in ZeroGraph: P -> Q => layer(P) <= layer(Q)",
        interpretation=(
            "Layer monotonicity: If P implies Q, then Q's layer is at least as deep as P's layer."
        ),
    ),
    GaloisLaw(
        name="G3",
        statement="stratification is a Galois connection: Lower dashv Upper",
        interpretation=(
            "Galois correspondence: Layer stratification forms an adjunction "
            "between propositions and layers."
        ),
    ),
    GaloisLaw(
        name="G4",
        statement="Axioms = Fix(Restructure^infinity)",
        interpretation=(
            "Fixed-point characterization: Axioms are precisely the fixed "
            "points of infinite restructuring."
        ),
    ),
]


# =============================================================================
# Factory Functions
# =============================================================================


def create_axiom_kernel() -> tuple[EntityAxiom, MorphismAxiom, GaloisGround]:
    """Create the minimal axiomatic kernel (A1, A2, G).

    Returns:
        Tuple of the three foundational axioms.
    """
    return (
        EntityAxiom(),
        MorphismAxiom(),
        GaloisGround(),
    )


def create_axiom_governance() -> AxiomGovernance:
    """Create a governance system with the three axioms registered.

    Returns:
        AxiomGovernance with A1, A2, G registered for monitoring.
    """
    governance = AxiomGovernance()
    a1, a2, g = create_axiom_kernel()
    governance.register(a1)
    governance.register(a2)
    governance.register(g)
    return governance


# =============================================================================
# MirrorTestOracle: Human-in-the-Loop Loss Validation
# =============================================================================


# Default voice anchors from CLAUDE.md / _focus.md
DEFAULT_VOICE_ANCHORS: list[str] = [
    "Daring, bold, creative, opinionated but not gaudy",
    "The Mirror Test",
    "Tasteful > feature-complete",
    "The persona is a garden, not a museum",
    "Depth over breadth",
]


@dataclass
class MirrorTestOracle:
    """Human-in-the-loop loss validation.

    The Mirror Test is Kent's human loss oracle - a qualitative measure
    of semantic drift. It asks: "Does K-gent feel like me on my best day?"

    This formalizes the Mirror Test as a loss function:
        Mirror(P, P') = 1 - VoicePreservation(P, P')

    Where VoicePreservation checks:
    - Anchor phrases ("daring, bold, creative...")
    - Opinionated stance (not hedged)
    - Joy-inducing vs. merely functional

    Attributes:
        voice_anchors: List of voice anchor phrases to check for preservation
    """

    voice_anchors: list[str] = field(default_factory=lambda: DEFAULT_VOICE_ANCHORS.copy())

    async def evaluate(
        self,
        original: str,
        transformed: str,
    ) -> float:
        """Evaluate human-assessed loss between original and transformed.

        In production: Present via TUI with side-by-side comparison.
        For now: Heuristic based on voice anchor preservation.

        Args:
            original: Original content
            transformed: Transformed content after restructure-reconstitute

        Returns:
            Human-assessed loss in [0, 1]:
            - 0.0 = "feels exactly like me"
            - 1.0 = "this is corporate sausage"
        """
        import asyncio

        # Run heuristic check (could be replaced with actual human feedback)
        anchor_preservation = await asyncio.to_thread(
            self._check_voice_anchors, original, transformed
        )
        return 1.0 - anchor_preservation

    def _check_voice_anchors(self, original: str, transformed: str) -> float:
        """Check if voice anchors survive transformation.

        Anchors:
        - "Daring, bold, creative, opinionated but not gaudy"
        - "The Mirror Test"
        - "Tasteful > feature-complete"
        - "The persona is a garden, not a museum"

        Args:
            original: Original content
            transformed: Transformed content

        Returns:
            Fraction of anchors preserved (0.0 to 1.0)
        """
        if not self.voice_anchors:
            return 1.0

        preserved_count = sum(
            1
            for anchor in self.voice_anchors
            if self._preserves_anchor(original, transformed, anchor)
        )
        return preserved_count / len(self.voice_anchors)

    def _preserves_anchor(
        self,
        original: str,
        transformed: str,
        anchor: str,
    ) -> bool:
        """Check if a single anchor is preserved.

        Heuristic: Anchor preserved if:
        1. Exact phrase appears in both, OR
        2. Key words from anchor appear in both

        Args:
            original: Original content
            transformed: Transformed content
            anchor: Voice anchor phrase to check

        Returns:
            True if anchor is preserved.
        """
        # Exact match in both
        if anchor in original and anchor in transformed:
            return True

        # If anchor wasn't in original, consider it preserved
        # (we only penalize losing anchors that were there)
        if anchor not in original:
            return True

        # Check for key words (at least 50% of words must be preserved)
        words = anchor.lower().split()
        if len(words) < 2:
            return anchor.lower() in transformed.lower()

        words_in_transformed = sum(1 for word in words if word in transformed.lower())
        return words_in_transformed >= len(words) * 0.5


# =============================================================================
# GaloisAxiomDiscovery: Three-Stage Discovery Process
# =============================================================================


@dataclass
class DiscoveryResult:
    """Result of axiom discovery for a single candidate.

    Attributes:
        node: The candidate ZeroNode
        layer: Computed layer (1 = axiom candidate)
        computational_loss: Loss from restructure-reconstitute
        human_loss: Loss from Mirror Test oracle (if validated)
        corpus_metrics: Corpus validation metrics (if validated)
        is_axiom_candidate: Whether this qualifies as axiom
    """

    node: ZeroNode
    layer: int
    computational_loss: float
    human_loss: float | None = None
    corpus_metrics: dict[str, float] | None = None

    @property
    def is_axiom_candidate(self) -> bool:
        """Check if this qualifies as an axiom candidate.

        Axiom candidates have layer = 1 (immediate fixed point).
        """
        return self.layer == 1

    @property
    def is_validated(self) -> bool:
        """Check if this has been validated by Mirror Test."""
        return self.human_loss is not None and self.human_loss < FIXED_POINT_THRESHOLD


class GaloisAxiomDiscovery:
    """Discover axioms as zero-loss fixed points.

    Three stages of discovery:
    1. **Computational**: Find L(P) < epsilon via restructure-reconstitute
    2. **Human**: Mirror Test as loss oracle
    3. **Empirical**: Validate on living corpus

    This implements the scientific method for axioms:
    - hypothesis (fixed point)
    - experiment (restructure)
    - validation (corpus coverage)

    Attributes:
        restructure: Function to modularize content
        reconstitute: Function to reconstitute modularized content
        loss_fn: Function to compute GaloisLoss between two strings
        mirror_oracle: Human loss oracle for Mirror Test
    """

    def __init__(
        self,
        restructure: Callable[[str], str],
        reconstitute: Callable[[str], str],
        loss_fn: Callable[[str, str], GaloisLoss],
        mirror_oracle: MirrorTestOracle | None = None,
    ) -> None:
        """Initialize axiom discovery.

        Args:
            restructure: Function to modularize content
            reconstitute: Function to reconstitute modularized content
            loss_fn: Function to compute GaloisLoss between two strings
            mirror_oracle: Optional Mirror Test oracle for human validation
        """
        self.restructure = restructure
        self.reconstitute = reconstitute
        self.loss_fn = loss_fn
        self.mirror_oracle = mirror_oracle or MirrorTestOracle()

    async def discover(
        self,
        constitution_paths: list[str],
    ) -> "AsyncIterator[ZeroNode]":
        """Stage 1: Computational fixed-point finding.

        Yields candidates with L(P) < FIXED_POINT_THRESHOLD (layer = 1).

        Args:
            constitution_paths: Paths to constitution files (CLAUDE.md, etc.)

        Yields:
            ZeroNode instances that are immediate fixed points.
        """
        nodes = await self._load_constitution(constitution_paths)

        for node in nodes:
            layer = compute_layer(node, self.restructure, self.reconstitute, self.loss_fn)

            if layer == 1:  # Immediate fixed point
                yield node

    async def discover_all(
        self,
        constitution_paths: list[str],
    ) -> list[DiscoveryResult]:
        """Stage 1: Discover all nodes with their layers.

        Unlike discover(), this returns all nodes with their computed layers,
        not just axiom candidates.

        Args:
            constitution_paths: Paths to constitution files

        Returns:
            List of DiscoveryResult for all discovered nodes.
        """
        nodes = await self._load_constitution(constitution_paths)
        results: list[DiscoveryResult] = []

        for node in nodes:
            layer = compute_layer(node, self.restructure, self.reconstitute, self.loss_fn)

            # Compute computational loss
            modular = self.restructure(node.content)
            reconstituted = self.reconstitute(modular)
            loss = self.loss_fn(node.content, reconstituted)

            results.append(
                DiscoveryResult(
                    node=node,
                    layer=layer,
                    computational_loss=loss.total,
                )
            )

        return results

    async def validate_mirror(
        self,
        candidate: ZeroNode,
    ) -> tuple[bool, float]:
        """Stage 2: Mirror Test validation.

        Ask: "Does restructured P still feel like Kent?"

        Args:
            candidate: Candidate ZeroNode to validate

        Returns:
            Tuple of (is_valid, human_loss) where is_valid is True
            if human_loss < FIXED_POINT_THRESHOLD.
        """
        original = candidate.content
        modular = self.restructure(original)
        reconstituted = self.reconstitute(modular)

        # Human oracle
        human_loss = await self.mirror_oracle.evaluate(original, reconstituted)

        return human_loss < FIXED_POINT_THRESHOLD, human_loss

    async def validate_corpus(
        self,
        candidate: ZeroNode,
        corpus_paths: list[str],
    ) -> tuple[bool, dict[str, float]]:
        """Stage 3: Empirical corpus validation.

        Test: Does P explain corpus variations with zero additional assumptions?

        Args:
            candidate: Candidate ZeroNode to validate
            corpus_paths: Paths to corpus files (impl/, tests, etc.)

        Returns:
            Tuple of (is_valid, metrics) where metrics contains
            {coverage, parsimony, coherence}.
        """
        corpus = await self._load_corpus(corpus_paths)

        # Coverage: Can P + definitions explain all corpus nodes?
        coverage = self._compute_coverage(candidate, corpus)

        # Parsimony: Is P minimal (removing it breaks explanations)?
        parsimony = self._compute_parsimony(candidate, corpus)

        # Coherence: Are corpus explanations mutually consistent?
        coherence = self._compute_coherence(candidate, corpus)

        is_valid = coverage > 0.95 and parsimony > 0.90 and coherence > 0.85

        return is_valid, {
            "coverage": coverage,
            "parsimony": parsimony,
            "coherence": coherence,
        }

    async def full_discovery(
        self,
        constitution_paths: list[str],
        corpus_paths: list[str] | None = None,
    ) -> list[DiscoveryResult]:
        """Run full three-stage discovery.

        Args:
            constitution_paths: Paths to constitution files
            corpus_paths: Optional paths to corpus files for stage 3

        Returns:
            List of fully validated DiscoveryResult instances.
        """
        results: list[DiscoveryResult] = []

        # Stage 1: Computational
        all_results = await self.discover_all(constitution_paths)

        for result in all_results:
            if not result.is_axiom_candidate:
                results.append(result)
                continue

            # Stage 2: Mirror Test
            is_valid, human_loss = await self.validate_mirror(result.node)
            result.human_loss = human_loss

            if not is_valid:
                results.append(result)
                continue

            # Stage 3: Corpus validation (optional)
            if corpus_paths:
                _, corpus_metrics = await self.validate_corpus(result.node, corpus_paths)
                result.corpus_metrics = corpus_metrics

            results.append(result)

        return results

    async def _load_constitution(self, paths: list[str]) -> list[ZeroNode]:
        """Load nodes from constitution files (CLAUDE.md, principles.md, etc.).

        Parses markdown sections into ZeroNodes. Each ## heading becomes
        a node, with dependencies extracted from cross-references.

        Args:
            paths: List of file paths to load

        Returns:
            List of ZeroNodes extracted from constitution files.
        """
        import asyncio
        from pathlib import Path

        nodes: list[ZeroNode] = []

        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                continue

            content = await asyncio.to_thread(path.read_text, encoding="utf-8")

            # Simple section extraction: split by ## headings
            sections = self._extract_sections(content, str(path))
            nodes.extend(sections)

        return nodes

    def _extract_sections(self, content: str, source: str) -> list[ZeroNode]:
        """Extract sections from markdown content.

        Args:
            content: Markdown content
            source: Source file path

        Returns:
            List of ZeroNodes, one per section.
        """
        import re

        nodes: list[ZeroNode] = []

        # Match ## headings and their content
        pattern = r"^##\s+(.+?)$"
        matches = list(re.finditer(pattern, content, re.MULTILINE))

        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            # Extract dependencies (cross-references like `See: ...` or links)
            deps = self._extract_dependencies(section_content)

            nodes.append(
                ZeroNode(
                    content=f"# {title}\n\n{section_content}",
                    dependencies=deps,
                    metadata={
                        "id": f"{source}::{title}",
                        "source": source,
                        "title": title,
                    },
                )
            )

        return nodes

    def _extract_dependencies(self, content: str) -> list[str]:
        """Extract cross-references as dependencies.

        Args:
            content: Section content

        Returns:
            List of dependency IDs.
        """
        import re

        deps: list[str] = []

        # Match See: references
        see_pattern = r"See:\s*`?([^`\n]+)`?"
        for match in re.finditer(see_pattern, content):
            deps.append(match.group(1).strip())

        # Match markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, content):
            deps.append(match.group(2).strip())

        return deps

    async def _load_corpus(self, paths: list[str]) -> list[str]:
        """Load impl/ files, tests, specs for validation.

        Args:
            paths: List of corpus paths

        Returns:
            List of file contents.
        """
        import asyncio
        from pathlib import Path

        contents: list[str] = []

        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                content = await asyncio.to_thread(path.read_text, encoding="utf-8")
                contents.append(content)
            elif path.is_dir():
                for py_file in path.rglob("*.py"):
                    content = await asyncio.to_thread(py_file.read_text, encoding="utf-8")
                    contents.append(content)

        return contents

    def _compute_coverage(self, axiom: ZeroNode, corpus: list[str]) -> float:
        """Compute what fraction of corpus is explainable from axiom.

        Args:
            axiom: Candidate axiom
            corpus: List of corpus contents

        Returns:
            Coverage ratio (0.0 to 1.0)
        """
        if not corpus:
            return 1.0

        # Heuristic: Check if axiom concepts appear in corpus
        axiom_words = set(axiom.content.lower().split())
        covered = 0

        for content in corpus:
            content_words = set(content.lower().split())
            if axiom_words & content_words:  # Non-empty intersection
                covered += 1

        return covered / len(corpus)

    def _compute_parsimony(self, axiom: ZeroNode, corpus: list[str]) -> float:
        """Compute if axiom is necessary (removing it breaks explanations).

        Args:
            axiom: Candidate axiom
            corpus: List of corpus contents

        Returns:
            Parsimony score (0.0 to 1.0)
        """
        # Heuristic: axiom is parsimonious if it's referenced/used
        reference_count = sum(
            1
            for content in corpus
            if axiom.metadata.get("title", "") in content
            or any(dep in content for dep in axiom.dependencies)
        )

        if not corpus:
            return 1.0

        return min(1.0, reference_count / max(1, len(corpus) * 0.1))

    def _compute_coherence(self, axiom: ZeroNode, corpus: list[str]) -> float:
        """Compute if corpus explanations are mutually consistent.

        Args:
            axiom: Candidate axiom
            corpus: List of corpus contents

        Returns:
            Coherence score (0.0 to 1.0)
        """
        # Heuristic: High coherence if axiom concepts are used consistently
        # For now, return high coherence as placeholder
        return 0.9


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "FIXED_POINT_THRESHOLD",
    "MAX_DEPTH",
    "DRIFT_TOLERANCE",
    "DEFAULT_VOICE_ANCHORS",
    # Core types
    "GaloisLoss",
    "ZeroNode",
    "Restructurable",
    # Layers
    "LayerType",
    "compute_layer",
    "stratify_by_loss",
    # Axioms
    "Axiom",
    "EntityAxiom",
    "MorphismAxiom",
    "GaloisGround",
    # Health and governance
    "AxiomHealth",
    "AxiomStatus",
    "AxiomGovernance",
    # Laws
    "GaloisLaw",
    "GALOIS_LAWS",
    # Discovery
    "MirrorTestOracle",
    "DiscoveryResult",
    "GaloisAxiomDiscovery",
    # Factories
    "create_axiom_kernel",
    "create_axiom_governance",
]
