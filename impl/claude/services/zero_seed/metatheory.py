"""
Zero Seed Metatheory: The Unified Foundation.

This module implements the metatheoretic foundation for Zero Seed v2,
unifying three seemingly distinct theories into a single mathematical structure:

1. Galois Modularization - Layer transitions as lossy compression functors
2. Agent-DP - Constitutional reward as dynamic programming value function
3. Seven-Layer Holarchy - Epistemic stratification as Galois convergence depth

The Core Unification:
    - L1 (Axioms) = Zero-loss fixed points: L(P) < epsilon_1
    - L2-L7 = Increasing restructuring depth to convergence
    - Constitutional Reward = 1 - lambda * L(transition) (inverse Galois loss)
    - Strange Loop = Lawvere fixed point (not paradox, necessity)

Philosophy:
    "The loss IS the layer transition cost. The fixed point IS the axiom.
     The Constitution IS the Galois adjunction."

See: spec/protocols/zero-seed1/metatheory.md
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Hashable,
    Protocol,
    Sequence,
    TypeVar,
)

if TYPE_CHECKING:
    from dp.core.constitution import Constitution
    from services.categorical.dp_bridge import PolicyTrace, TraceEntry

logger = logging.getLogger("kgents.zero_seed.metatheory")


# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T")  # Generic content type
S = TypeVar("S", bound=Hashable)  # State type


# =============================================================================
# Constants from Metatheory Spec
# =============================================================================

# Layer thresholds (from Section 2.1)
EPSILON_FIXED_POINT = 0.05  # epsilon_1: Axiom threshold
MAX_LAYERS = 7  # Maximum holarchy depth
CONTRADICTION_TOLERANCE = 0.1  # tau: Super-additive loss threshold
LOSS_PENALTY_LAMBDA = 0.3  # lambda: Loss penalty weight in value function
EXPLOSION_THRESHOLD = 0.9  # Maximum loss before blocking inference

# Miller's 7+/-2 working memory limit (Section 2.2)
MILLER_MIN_LAYERS = 5
MILLER_MAX_LAYERS = 9


# =============================================================================
# Layer System (Section II)
# =============================================================================


class EpistemicLayer(Enum):
    """
    The seven epistemic layers derived from Galois convergence depth.

    From Section 2.1:
    - Layer = minimum restructuring iterations to reach fixed point
    - L1 (depth 0): Axioms - immediate fixed points
    - L7 (depth 6+): Meta-cognition - slow/no convergence
    """

    L1_AXIOMS = 1  # Constitutional axioms, fixed points
    L2_PRINCIPLES = 2  # Principle statements
    L3_GOALS = 3  # Goal statements
    L4_SPECIFICATIONS = 4  # Specification prose (Zero Seed lives here)
    L5_ACTIONS = 5  # Code/actions
    L6_REFLECTIONS = 6  # Reflections
    L7_META = 7  # Meta-cognition, representations

    @property
    def convergence_depth(self) -> int:
        """Expected iterations to reach fixed point."""
        return self.value - 1

    @property
    def description(self) -> str:
        """Human-readable layer description."""
        descriptions = {
            1: "Constitutional axioms (immediate fixed points)",
            2: "Principle statements (1 iteration)",
            3: "Goal statements (2-3 iterations)",
            4: "Specification prose (3-4 iterations)",
            5: "Code and actions (4-5 iterations)",
            6: "Reflections (5+ iterations)",
            7: "Meta-cognition (slow/no convergence)",
        }
        return descriptions.get(self.value, "Unknown layer")


@dataclass(frozen=True)
class LayerAssignment:
    """
    Result of assigning content to an epistemic layer.

    From Algorithm 9.1.1 in the spec.
    """

    layer: EpistemicLayer
    loss: float
    confidence: float
    reasoning: str
    convergence_iterations: int = 0

    @property
    def is_fixed_point(self) -> bool:
        """True if content is a fixed point (axiom candidate)."""
        return self.loss < EPSILON_FIXED_POINT

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage/transmission."""
        return {
            "layer": self.layer.value,
            "layer_name": self.layer.name,
            "loss": self.loss,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "convergence_iterations": self.convergence_iterations,
            "is_fixed_point": self.is_fixed_point,
        }


# =============================================================================
# Galois Loss Protocol (Part I, Section 1.3)
# =============================================================================


class GaloisLossProtocol(Protocol):
    """
    Protocol for Galois loss computation.

    The Galois loss measures information lost during restructuring:
        L(T) = d(T, C(R(T)))

    Where:
        R: Text -> Modular (restructure - upper adjoint)
        C: Modular -> Text (reconstitute - lower adjoint)
        d: Text x Text -> [0,1] (semantic distance metric)
    """

    async def restructure(self, content: str) -> str:
        """
        R: Text -> Modular

        Restructure content into modular form.
        This is the upper adjoint in the Galois connection.
        """
        ...

    async def reconstitute(self, modular: str) -> str:
        """
        C: Modular -> Text

        Reconstitute content from modular form.
        This is the lower adjoint in the Galois connection.
        """
        ...

    async def compute_loss(self, original: str, reconstituted: str) -> float:
        """
        d: Text x Text -> [0,1]

        Compute semantic distance between original and reconstituted.
        """
        ...

    async def compute(self, content: str) -> float:
        """
        L(T) = d(T, C(R(T)))

        Full Galois loss computation.
        """
        ...


@dataclass
class GaloisAdjunction:
    """
    The Galois adjunction R -| C for text modularization.

    This is the mathematical primitive from which layers, proofs, and
    contradictions emerge (Section 1.3).

    Adjunction Laws:
        C(R(T)) >= T (reconstitution is at least as general)
        R(C(M)) <= M (re-restructuring is at most as specific)
    """

    restructure_fn: Callable[[str], str]
    reconstitute_fn: Callable[[str], str]
    distance_fn: Callable[[str, str], float]

    def loss(self, content: str) -> float:
        """
        L(T) = d(T, C(R(T)))

        Compute Galois loss for content.
        """
        modular = self.restructure_fn(content)
        reconstituted = self.reconstitute_fn(modular)
        return self.distance_fn(content, reconstituted)

    def is_fixed_point(self, content: str, epsilon: float = EPSILON_FIXED_POINT) -> bool:
        """
        Check if content is a fixed point of restructuring.

        Definition 3.1.1: R(A) ~= A modulo semantic equivalence.
        """
        return self.loss(content) < epsilon


# =============================================================================
# Layer Computation (Section 2.1, Algorithm 9.1.1)
# =============================================================================


@dataclass
class LayerComputer:
    """
    Computes epistemic layer via Galois convergence depth.

    From Definition 2.1.1:
        Layer = minimum restructuring iterations to reach fixed point.
        Returns: 1-7 (L1 = immediate fixed point, L7 = slow/no convergence)
    """

    galois: GaloisAdjunction
    epsilon: float = EPSILON_FIXED_POINT
    max_iterations: int = MAX_LAYERS

    def compute_layer(self, content: str) -> LayerAssignment:
        """
        Assign content to layer via convergence depth.

        Algorithm 9.1.1 from the spec.
        """
        current = content

        for depth in range(self.max_iterations):
            # Apply restructure-reconstitute cycle
            modular = self.galois.restructure_fn(current)
            reconstituted = self.galois.reconstitute_fn(modular)

            # Measure loss
            loss = self.galois.distance_fn(current, reconstituted)

            # Fixed point reached?
            if loss < self.epsilon:
                layer_num = depth + 1
                layer = EpistemicLayer(min(layer_num, MAX_LAYERS))

                return LayerAssignment(
                    layer=layer,
                    loss=loss,
                    confidence=1.0 - loss,
                    reasoning=f"Converged at depth {depth}",
                    convergence_iterations=depth,
                )

            current = reconstituted  # Iterate

        # Did not converge
        return LayerAssignment(
            layer=EpistemicLayer.L7_META,
            loss=self.galois.loss(content),
            confidence=0.5,
            reasoning=f"Did not converge in {self.max_iterations} iterations",
            convergence_iterations=self.max_iterations,
        )


# =============================================================================
# Axiom Discovery (Part III)
# =============================================================================


@dataclass(frozen=True)
class CandidateAxiom:
    """
    An axiom candidate discovered via fixed-point search.

    From Definition 3.1.1: A node A is an axiom iff R(A) ~= A.
    """

    text: str
    loss: float
    source_path: str
    confidence: float = 1.0
    is_fixed_point: bool = False
    tags: tuple[str, ...] = ()
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_axiom_node(self) -> "ZeroNode":
        """Convert to a ZeroNode for the graph."""
        return ZeroNode(
            id=f"axiom:{hash(self.text)}",
            content=self.text,
            layer=EpistemicLayer.L1_AXIOMS,
            loss=self.loss,
            tags=self.tags,
            source_path=self.source_path,
        )


@dataclass
class AxiomMiner:
    """
    Mine axiom candidates via fixed-point search.

    From Algorithm 9.1.2: Mine candidates by minimizing Galois loss.
    Axioms are statements where L(statement) < threshold.
    """

    galois: GaloisAdjunction
    threshold: float = EPSILON_FIXED_POINT

    def extract_statements(self, content: str) -> list[str]:
        """
        Extract individual statements from content.

        Simple implementation: split on newlines and filter.
        Override for more sophisticated extraction.
        """
        lines = content.strip().split("\n")
        statements = []

        for line in lines:
            line = line.strip()
            # Filter headers, empty lines, code blocks
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("```"):
                continue
            if len(line) < 10:
                continue
            statements.append(line)

        return statements

    def mine(
        self,
        content: str,
        source_path: str = "unknown",
    ) -> list[CandidateAxiom]:
        """
        Mine axiom candidates from content.

        Returns candidates sorted by loss (lowest first).
        """
        statements = self.extract_statements(content)
        candidates: list[CandidateAxiom] = []

        for stmt in statements:
            loss = self.galois.loss(stmt)

            if loss < self.threshold:
                candidates.append(
                    CandidateAxiom(
                        text=stmt,
                        loss=loss,
                        source_path=source_path,
                        confidence=1.0 - loss,
                        is_fixed_point=loss < 0.01,
                    )
                )

        # Sort by loss (lowest first = best axiom candidates)
        return sorted(candidates, key=lambda c: c.loss)


# =============================================================================
# Proof Quality (Part IV)
# =============================================================================


class EvidenceTier(Enum):
    """
    Evidence tier classification based on Galois loss.

    From Section 4.3: Quality thresholds based on loss ranges.
    """

    EXCELLENT = auto()  # Loss [0.0, 0.2) - Proof survives restructuring intact
    GOOD = auto()  # Loss [0.2, 0.4) - Minor structural gaps
    ADEQUATE = auto()  # Loss [0.4, 0.6) - Significant gaps
    WEAK = auto()  # Loss [0.6, 0.8) - Major logical leaps
    INCOHERENT = auto()  # Loss [0.8, 1.0] - Proof doesn't hold

    @classmethod
    def from_loss(cls, loss: float) -> "EvidenceTier":
        """Classify tier based on Galois loss."""
        if loss < 0.2:
            return cls.EXCELLENT
        elif loss < 0.4:
            return cls.GOOD
        elif loss < 0.6:
            return cls.ADEQUATE
        elif loss < 0.8:
            return cls.WEAK
        else:
            return cls.INCOHERENT

    @property
    def coherence(self) -> tuple[float, float]:
        """Return coherence range (low, high)."""
        ranges = {
            EvidenceTier.EXCELLENT: (0.8, 1.0),
            EvidenceTier.GOOD: (0.6, 0.8),
            EvidenceTier.ADEQUATE: (0.4, 0.6),
            EvidenceTier.WEAK: (0.2, 0.4),
            EvidenceTier.INCOHERENT: (0.0, 0.2),
        }
        return ranges[self]

    @property
    def requires_revision(self) -> bool:
        """True if proof should trigger revision prompts."""
        return self in (EvidenceTier.WEAK, EvidenceTier.INCOHERENT)


@dataclass(frozen=True)
class ProofCoherence:
    """
    Proof quality measurement via inverse Galois loss.

    From Definition 4.1.1:
        coherence(proof) = 1 - L(proof_text)
    """

    proof_text: str
    galois_loss: float
    tier: EvidenceTier

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss."""
        return 1.0 - self.galois_loss

    @property
    def is_valid(self) -> bool:
        """True if proof has acceptable coherence."""
        return self.tier not in (EvidenceTier.WEAK, EvidenceTier.INCOHERENT)


@dataclass
class ProofEvaluator:
    """
    Evaluate proof quality via Galois loss.

    High coherence = proof survives restructuring.
    Low coherence = proof loses meaning when modularized.
    """

    galois: GaloisAdjunction

    def evaluate(
        self,
        data: str,
        warrant: str,
        claim: str,
        backing: str = "",
    ) -> ProofCoherence:
        """
        Evaluate Toulmin proof structure.

        Constructs proof text and measures Galois loss.
        """
        proof_text = f"""
Data: {data}
Warrant: {warrant}
Claim: {claim}
Backing: {backing}
"""
        loss = self.galois.loss(proof_text)
        tier = EvidenceTier.from_loss(loss)

        return ProofCoherence(
            proof_text=proof_text.strip(),
            galois_loss=loss,
            tier=tier,
        )


# =============================================================================
# Contradiction Detection (Part V)
# =============================================================================


class ContradictionType(Enum):
    """Type of contradiction detected."""

    GENUINE = auto()  # Real logical conflict
    APPARENT = auto()  # Surface tension, composable
    EXPLOSIVE = auto()  # Loss > explosion threshold


@dataclass(frozen=True)
class ContradictionAnalysis:
    """
    Result of contradiction detection via super-additive loss.

    From Definition 5.1.1:
        Two nodes contradict iff L(A U B) > L(A) + L(B) + tau
    """

    is_contradiction: bool
    strength: float  # Super-additive component
    type: ContradictionType
    reason: str
    resolution_strategy: str = ""

    # Individual losses for analysis
    loss_a: float = 0.0
    loss_b: float = 0.0
    loss_joint: float = 0.0

    @property
    def is_explosive(self) -> bool:
        """True if contradiction is too severe for inference."""
        return self.loss_joint > EXPLOSION_THRESHOLD

    @property
    def can_synthesize(self) -> bool:
        """True if synthesis is possible (moderate contradiction)."""
        return (
            self.is_contradiction
            and 0.1 < self.strength < 0.5
            and self.type == ContradictionType.GENUINE
        )


@dataclass
class ContradictionDetector:
    """
    Detect contradictions via super-additive Galois loss.

    From Section 5.1: Contradictions coexist without explosion
    in paraconsistent logic. We measure contradiction strength
    as super-additive loss.
    """

    galois: GaloisAdjunction
    tolerance: float = CONTRADICTION_TOLERANCE

    def detect(
        self,
        content_a: str,
        content_b: str,
    ) -> ContradictionAnalysis:
        """
        Detect if two contents contradict.

        Super-additivity = L(A U B) - L(A) - L(B)
        If super_additive > tolerance: CONTRADICTION
        """
        # Individual losses
        loss_a = self.galois.loss(content_a)
        loss_b = self.galois.loss(content_b)

        # Joint loss
        joint_content = f"{content_a}\n\n{content_b}"
        loss_joint = self.galois.loss(joint_content)

        # Super-additivity = contradiction strength
        super_additive = loss_joint - (loss_a + loss_b)

        if loss_joint > EXPLOSION_THRESHOLD:
            return ContradictionAnalysis(
                is_contradiction=True,
                strength=super_additive,
                type=ContradictionType.EXPLOSIVE,
                reason="Joint modularization exceeds explosion threshold",
                resolution_strategy="choose_one_or_abandon",
                loss_a=loss_a,
                loss_b=loss_b,
                loss_joint=loss_joint,
            )
        elif super_additive > self.tolerance:
            strategy = "synthesis" if super_additive < 0.5 else "choose_one"
            return ContradictionAnalysis(
                is_contradiction=True,
                strength=super_additive,
                type=ContradictionType.GENUINE,
                reason="Joint modularization loses more than sum of parts",
                resolution_strategy=strategy,
                loss_a=loss_a,
                loss_b=loss_b,
                loss_joint=loss_joint,
            )
        else:
            return ContradictionAnalysis(
                is_contradiction=False,
                strength=max(0.0, super_additive),
                type=ContradictionType.APPARENT,
                reason="Nodes compose efficiently despite surface tension",
                loss_a=loss_a,
                loss_b=loss_b,
                loss_joint=loss_joint,
            )


# =============================================================================
# Three-Valued Paraconsistent Logic (Section 5.3)
# =============================================================================


class ThreeValuedTruth(Enum):
    """
    Three-valued logic with Galois semantics.

    From Section 5.3:
        TRUE = L(proof) < 0.2
        FALSE = L(proof) > 0.8
        UNKNOWN = 0.2 <= L(proof) <= 0.8
    """

    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

    @classmethod
    def from_loss(cls, loss: float) -> "ThreeValuedTruth":
        """Determine truth value from Galois loss."""
        if loss < 0.2:
            return cls.TRUE
        elif loss > 0.8:
            return cls.FALSE
        else:
            return cls.UNKNOWN


# =============================================================================
# Constitutional Reward (Part VI)
# =============================================================================


class ConstitutionalPrinciple(Enum):
    """
    The 7 constitutional principles with Galois loss mappings.

    From Section 6.2: Each principle maps to a specific Galois loss variant.
    """

    TASTEFUL = auto()  # bloat_loss: Unnecessary structure
    COMPOSABLE = auto()  # composition_loss: Hidden dependencies
    GENERATIVE = auto()  # regeneration_loss: Failure to reconstruct
    ETHICAL = auto()  # safety_loss: Hidden risky assumptions
    JOY_INDUCING = auto()  # aesthetic_loss: Deviation from personality
    HETERARCHICAL = auto()  # rigidity_loss: Imposed hierarchy
    CURATED = auto()  # arbitrariness_loss: Unjustified changes

    @property
    def loss_name(self) -> str:
        """Name of the corresponding Galois loss function."""
        mapping = {
            ConstitutionalPrinciple.TASTEFUL: "bloat_loss",
            ConstitutionalPrinciple.COMPOSABLE: "composition_loss",
            ConstitutionalPrinciple.GENERATIVE: "regeneration_loss",
            ConstitutionalPrinciple.ETHICAL: "safety_loss",
            ConstitutionalPrinciple.JOY_INDUCING: "aesthetic_loss",
            ConstitutionalPrinciple.HETERARCHICAL: "rigidity_loss",
            ConstitutionalPrinciple.CURATED: "arbitrariness_loss",
        }
        return mapping[self]

    @property
    def default_weight(self) -> float:
        """Default weight for this principle."""
        # From Section 6.2 defaults
        weights = {
            ConstitutionalPrinciple.ETHICAL: 2.0,  # Safety first
            ConstitutionalPrinciple.COMPOSABLE: 1.5,  # Architectural importance
            ConstitutionalPrinciple.JOY_INDUCING: 1.2,  # Kent's aesthetic priority
        }
        return weights.get(self, 1.0)


@dataclass
class GaloisConstitution:
    """
    The Constitution as Galois Adjunction.

    From Theorem 6.1.1 (Constitutional Reward-Loss Duality):
        R_constitutional(s, a, s') = 1.0 - L_galois(s -> s' via a)

    Deep Theorem 6.3.1: Constitution = Adjunction
        R + L = 1.0 (total information conserved)
    """

    galois: GaloisAdjunction
    principle_weights: dict[ConstitutionalPrinciple, float] = field(
        default_factory=lambda: {p: p.default_weight for p in ConstitutionalPrinciple}
    )

    # Principle-specific loss functions (override for customization)
    principle_losses: dict[ConstitutionalPrinciple, Callable[[str], float]] = field(
        default_factory=dict
    )

    def _get_principle_loss(
        self,
        principle: ConstitutionalPrinciple,
        content: str,
    ) -> float:
        """Get loss for a specific principle."""
        if principle in self.principle_losses:
            return self.principle_losses[principle](content)
        # Default: use general Galois loss
        return self.galois.loss(content)

    def reward(
        self,
        state_content: str,
        action: str,
        next_state_content: str,
    ) -> float:
        """
        Unified constitutional reward via weighted Galois losses.

        R_total = sum_i w_i * (1 - L_i)
        """
        losses: dict[ConstitutionalPrinciple, float] = {}

        for principle in ConstitutionalPrinciple:
            # Compute principle-specific loss on next state
            loss = self._get_principle_loss(principle, next_state_content)
            losses[principle] = loss

        # Weighted sum of inverse losses
        total_weight = sum(self.principle_weights.values())
        weighted_sum = sum(
            self.principle_weights.get(p, 1.0) * (1.0 - loss) for p, loss in losses.items()
        )

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def evaluate_transition(
        self,
        state_content: str,
        action: str,
        next_state_content: str,
    ) -> dict[str, Any]:
        """
        Full evaluation with per-principle breakdown.

        Returns detailed scores for each principle.
        """
        result = {
            "principles": {},
            "total_reward": 0.0,
            "transition_loss": 0.0,
        }

        for principle in ConstitutionalPrinciple:
            loss = self._get_principle_loss(principle, next_state_content)
            reward = 1.0 - loss
            weight = self.principle_weights.get(principle, 1.0)

            result["principles"][principle.name] = {  # type: ignore[index]
                "loss": loss,
                "reward": reward,
                "weight": weight,
                "weighted_reward": reward * weight,
            }

        result["total_reward"] = self.reward(state_content, action, next_state_content)
        result["transition_loss"] = self.galois.loss(
            f"{state_content} -> {next_state_content} via {action}"
        )

        return result


# =============================================================================
# Strange Loop / Lawvere Fixed Point (Part VII)
# =============================================================================


@dataclass(frozen=True)
class FixedPointVerification:
    """
    Result of verifying Zero Seed as a fixed point.

    From Theorem 7.1.1 (Lawvere for Zero Seed):
        R(P) ~= P modulo semantic fidelity
        Success: L(spec, C(R(spec))) < 0.15 (85% regenerability)
    """

    loss: float
    is_fixed_point: bool
    regenerability: float
    interpretation: str

    @classmethod
    def verify(
        cls,
        spec_content: str,
        galois: GaloisAdjunction,
        threshold: float = 0.15,
    ) -> "FixedPointVerification":
        """
        Verify if content is approximately a fixed point.

        From Section 7.3: Zero Seed claims 85% regenerability.
        """
        loss = galois.loss(spec_content)
        is_fixed = loss < threshold
        regenerability = 1.0 - loss

        interpretation = (
            "Verified fixed point"
            if is_fixed
            else f"Not yet fixed point (loss={loss:.2f}, target<{threshold})"
        )

        return cls(
            loss=loss,
            is_fixed_point=is_fixed,
            regenerability=regenerability,
            interpretation=interpretation,
        )


@dataclass
class StrangeLoopVerifier:
    """
    Verify the strange loop (self-reference) property.

    From Section 7.1-7.2: Zero Seed describes itself at L4.
    This is a Lawvere fixed point, not a paradox.

    Two orderings coexist:
    1. Temporal: Kent writes spec -> spec describes layers -> system implements
    2. Logical: A1 + A2 + G -> adjunction -> layers emerge -> L4 = spec layer
    """

    galois: GaloisAdjunction

    def verify_zero_seed(
        self,
        spec_content: str,
        threshold: float = 0.15,
    ) -> FixedPointVerification:
        """
        Verify Zero Seed is approximately a fixed point.

        Expected result: L(Zero Seed) ~= 0.13 (87% regenerability)
        """
        return FixedPointVerification.verify(spec_content, self.galois, threshold)

    def check_self_reference_consistency(
        self,
        spec_content: str,
        layer_computer: LayerComputer,
    ) -> dict[str, Any]:
        """
        Check if spec correctly self-categorizes at L4.

        The spec should:
        1. Assign itself to L4 (Specifications layer)
        2. Have loss consistent with L4 characteristics
        3. Not exhibit paradoxical self-reference
        """
        assignment = layer_computer.compute_layer(spec_content)

        return {
            "computed_layer": assignment.layer.value,
            "expected_layer": EpistemicLayer.L4_SPECIFICATIONS.value,
            "is_consistent": assignment.layer == EpistemicLayer.L4_SPECIFICATIONS,
            "loss": assignment.loss,
            "convergence_iterations": assignment.convergence_iterations,
            "is_paradoxical": False,  # Lawvere fixed point resolves paradox
            "interpretation": (
                "Self-reference is productive (Lawvere fixed point)"
                if assignment.layer == EpistemicLayer.L4_SPECIFICATIONS
                else f"Self-reference anomaly: expected L4, got L{assignment.layer.value}"
            ),
        }


# =============================================================================
# ZeroNode: Core Graph Primitive (Axiom A1)
# =============================================================================


@dataclass(frozen=True)
class ZeroNode:
    """
    A node in the ZeroGraph (Axiom A1: Everything is a Node).

    From Section 1.1:
        forall x in Universe: exists node(x) in ZeroGraph
        The graph is the totality of expressible knowledge.
    """

    id: str
    content: str
    layer: EpistemicLayer
    loss: float
    tags: tuple[str, ...] = ()
    source_path: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_axiom(self) -> bool:
        """True if node is at L1 (axiom layer)."""
        return self.layer == EpistemicLayer.L1_AXIOMS

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss."""
        return 1.0 - self.loss

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage/transmission."""
        return {
            "id": self.id,
            "content": self.content,
            "layer": self.layer.value,
            "layer_name": self.layer.name,
            "loss": self.loss,
            "coherence": self.coherence,
            "tags": list(self.tags),
            "source_path": self.source_path,
            "created_at": self.created_at.isoformat(),
            "is_axiom": self.is_axiom,
        }


# =============================================================================
# Synthesis (Section 5.4)
# =============================================================================


@dataclass(frozen=True)
class SynthesisResult:
    """
    Result of dialectical synthesis.

    From Section 5.4:
        Synthesis succeeds iff L(synthesis) < L(thesis U antithesis)
    """

    success: bool
    synthesis_node: ZeroNode | None
    thesis_loss: float
    antithesis_loss: float
    union_loss: float
    synthesis_loss: float | None
    reason: str

    @property
    def improvement(self) -> float | None:
        """How much loss was reduced by synthesis."""
        if self.synthesis_loss is None:
            return None
        return self.union_loss - self.synthesis_loss


@dataclass
class DialecticalSynthesizer:
    """
    Generate synthesis from thesis/antithesis.

    From Section 5.4: Synthesis succeeds iff it reduces total loss.
    This is the Hegelian dialectic formalized.
    """

    galois: GaloisAdjunction
    synthesis_fn: Callable[[str, str], str] | None = None

    def _default_synthesis(self, thesis: str, antithesis: str) -> str:
        """Default synthesis: simple combination."""
        return f"Synthesis of:\n- {thesis}\n- {antithesis}"

    def synthesize(
        self,
        thesis_node: ZeroNode,
        antithesis_node: ZeroNode,
    ) -> SynthesisResult:
        """
        Attempt to synthesize thesis and antithesis.

        Success criterion:
            L(synthesis) < min(L(thesis U antithesis), L(thesis), L(antithesis))
        """
        thesis_loss = self.galois.loss(thesis_node.content)
        antithesis_loss = self.galois.loss(antithesis_node.content)
        union_loss = self.galois.loss(f"{thesis_node.content}\n{antithesis_node.content}")

        # Generate synthesis
        synthesize = self.synthesis_fn or self._default_synthesis
        synthesis_content = synthesize(thesis_node.content, antithesis_node.content)
        synthesis_loss = self.galois.loss(synthesis_content)

        # Success criterion from Section 5.4
        threshold = min(union_loss, thesis_loss, antithesis_loss)
        success = synthesis_loss < threshold

        if success:
            synthesis_node = ZeroNode(
                id=f"synthesis:{hash(synthesis_content)}",
                content=synthesis_content,
                layer=EpistemicLayer(max(thesis_node.layer.value, antithesis_node.layer.value)),
                loss=synthesis_loss,
                tags=thesis_node.tags + antithesis_node.tags,
            )
            reason = f"Synthesis reduced loss from {threshold:.2f} to {synthesis_loss:.2f}"
        else:
            synthesis_node = None
            reason = (
                f"Synthesis has higher loss ({synthesis_loss:.2f}) than threshold ({threshold:.2f})"
            )

        return SynthesisResult(
            success=success,
            synthesis_node=synthesis_node,
            thesis_loss=thesis_loss,
            antithesis_loss=antithesis_loss,
            union_loss=union_loss,
            synthesis_loss=synthesis_loss,
            reason=reason,
        )


# =============================================================================
# Value Function Integration (Section IX.2)
# =============================================================================


@dataclass
class ZeroSeedValueFunction:
    """
    Value function for Zero Seed navigation with Galois reward.

    From Section 2.3 (Theorem 2.3.1):
        V*(node) = max_edge [
            R_constitutional(node, edge, target)
            - lambda * L(node -> target)
            + gamma * V*(target)
        ]
    """

    galois: GaloisAdjunction
    constitution: GaloisConstitution
    gamma: float = 0.99  # Discount factor (telescope parameter)
    loss_penalty: float = LOSS_PENALTY_LAMBDA

    def q_value(
        self,
        state_content: str,
        action: str,
        next_state_content: str,
        future_value: float = 0.0,
    ) -> float:
        """
        Compute Q(s, a) = R - lambda*L + gamma*V(s')

        This is the Bellman equation for Zero Seed navigation.
        """
        # Constitutional reward
        r_const = self.constitution.reward(state_content, action, next_state_content)

        # Galois loss penalty
        transition = f"{state_content} -> {next_state_content} via {action}"
        loss = self.galois.loss(transition)

        # Combined value
        return r_const - self.loss_penalty * loss + self.gamma * future_value


# =============================================================================
# Disgust Veto (Article IV)
# =============================================================================


@dataclass(frozen=True)
class DisgustVetoResult:
    """
    Result of evaluating proposal with disgust veto.

    From Section 8.2: Somatic disgust bypasses Galois loss entirely.
    Loss = 1.0 by fiat if vetoed.
    """

    galois_loss: float
    is_vetoed: bool
    reason: str = ""

    @property
    def effective_loss(self) -> float:
        """Loss after veto (1.0 if vetoed)."""
        return 1.0 if self.is_vetoed else self.galois_loss


def evaluate_with_disgust_veto(
    proposal_content: str,
    galois: GaloisAdjunction,
    disgust_oracle: Callable[[str], bool],
) -> DisgustVetoResult:
    """
    Evaluate proposal with disgust veto.

    The disgust veto is the ethical floor - irreducible human judgment
    that cannot be argued away (Kant's categorical imperative as loss = 1.0).
    """
    # Check disgust veto FIRST
    is_vetoed = disgust_oracle(proposal_content)

    if is_vetoed:
        return DisgustVetoResult(
            galois_loss=1.0,
            is_vetoed=True,
            reason="Disgust veto invoked - absolute rejection",
        )

    # Compute Galois loss only if not vetoed
    loss = galois.loss(proposal_content)
    return DisgustVetoResult(
        galois_loss=loss,
        is_vetoed=False,
    )


# =============================================================================
# Loss Accumulation Bound (Theorem 2.4.1)
# =============================================================================


def compute_loss_bound(
    path_length: int,
    r_min: float = 0.7,
) -> float:
    """
    Compute the upper bound on total loss through a path.

    From Theorem 2.4.1:
        L_total(L1 -> L7) <= sum_{i=1}^{6} L(Li -> Li+1) <= 6 * (1 - R_min)

    This guarantees that even the deepest paths (L1 -> L7) lose at most
    a bounded amount of semantic fidelity.

    Args:
        path_length: Number of layer transitions (max 6 for L1->L7)
        r_min: Minimum acceptable constitutional reward (default 0.7)

    Returns:
        Upper bound on total loss
    """
    return path_length * (1 - r_min)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Constants
    "EPSILON_FIXED_POINT",
    "MAX_LAYERS",
    "CONTRADICTION_TOLERANCE",
    "LOSS_PENALTY_LAMBDA",
    "EXPLOSION_THRESHOLD",
    # Layer System
    "EpistemicLayer",
    "LayerAssignment",
    "LayerComputer",
    # Galois Foundation
    "GaloisLossProtocol",
    "GaloisAdjunction",
    # Axiom Discovery
    "CandidateAxiom",
    "AxiomMiner",
    # Proof Quality
    "EvidenceTier",
    "ProofCoherence",
    "ProofEvaluator",
    # Contradiction Detection
    "ContradictionType",
    "ContradictionAnalysis",
    "ContradictionDetector",
    # Three-Valued Logic
    "ThreeValuedTruth",
    # Constitutional Reward
    "ConstitutionalPrinciple",
    "GaloisConstitution",
    # Strange Loop
    "FixedPointVerification",
    "StrangeLoopVerifier",
    # Core Types
    "ZeroNode",
    # Synthesis
    "SynthesisResult",
    "DialecticalSynthesizer",
    # Value Function
    "ZeroSeedValueFunction",
    # Disgust Veto
    "DisgustVetoResult",
    "evaluate_with_disgust_veto",
    # Utilities
    "compute_loss_bound",
]
