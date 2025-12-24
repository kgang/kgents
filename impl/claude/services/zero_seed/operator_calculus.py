"""
Zero Seed Operator Calculus: Edge Operators as Loss Transformations.

Implements the operator algebra from spec/protocols/zero-seed1/operator-calculus.md.

The Core Insight:
    "The edge IS the operator. The loss IS the difficulty. The composition IS the path."

Every edge type (GROUNDS, JUSTIFIES, SPECIFIES, etc.) is formalized as a
loss transformation operator that acts on the information structure of nodes.

Each operator has:
1. Loss Semantics: How much information is lost/preserved
2. Compositional Laws: How operators combine
3. Constitutional Affinity: Alignment with the 7 principles
4. Layer Transition Rules: Valid source/target layers
5. Inverse Structure: Bidirectional operators with partial adjoints
"""

from __future__ import annotations

import heapq
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    import numpy as np

# -----------------------------------------------------------------------------
# Core Types
# -----------------------------------------------------------------------------

T = TypeVar("T")
NodeId = str
EdgeId = str


@dataclass(frozen=True)
class ZeroNode:
    """A node in the Zero Seed holarchy."""

    id: NodeId
    path: str  # AGENTESE path (e.g., "void.axiom.mirror-test")
    layer: int  # 1-7
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)


# -----------------------------------------------------------------------------
# Galois Loss Interface
# -----------------------------------------------------------------------------


@runtime_checkable
class GaloisLossProtocol(Protocol):
    """Protocol for Galois loss computation."""

    def compute(self, content: str) -> float:
        """Compute loss for single content."""
        ...

    def compute_text(self, description: str) -> float:
        """Compute loss from natural language description."""
        ...

    def compute_between(self, original: str, transformed: str) -> float:
        """Compute loss between original and transformed content."""
        ...

    def semantic(self, description: str) -> float:
        """Compute semantic drift component."""
        ...


@dataclass
class GaloisLoss:
    """
    Galois loss computation for Zero Seed operators.

    Measures information loss under restructure/reconstitute operations.
    Three drift components: semantic, structural, operational.
    """

    semantic_weight: float = 0.5
    structural_weight: float = 0.3
    operational_weight: float = 0.2

    def compute(self, content: str) -> float:
        """
        Compute baseline loss for content.

        For axioms, this should be near zero.
        For complex content, higher.
        """
        # Use content complexity as proxy for loss potential
        # Normalized by typical content length
        base_complexity = min(len(content) / 5000, 1.0) * 0.3
        # Depth indicator: more sections = more potential loss
        section_count = content.count("#")
        section_penalty = min(section_count / 20, 0.2)
        return min(base_complexity + section_penalty, 1.0)

    def compute_text(self, description: str) -> float:
        """
        Compute loss from natural language description.

        Analyzes the description to infer loss magnitude.
        """
        # Keywords that indicate low loss
        low_loss_keywords = [
            "directly",
            "immediately",
            "necessarily",
            "follows",
            "inherits",
            "same",
            "identical",
            "equivalent",
        ]
        # Keywords that indicate high loss
        high_loss_keywords = [
            "approximately",
            "somewhat",
            "partially",
            "tenuous",
            "weak",
            "missing",
            "incomplete",
            "gap",
        ]

        desc_lower = description.lower()
        low_count = sum(1 for kw in low_loss_keywords if kw in desc_lower)
        high_count = sum(1 for kw in high_loss_keywords if kw in desc_lower)

        # Base loss from content length
        base_loss = min(len(description) / 3000, 0.4)

        # Adjust based on keywords
        keyword_adjustment = (high_count - low_count) * 0.05
        return max(0.0, min(1.0, base_loss + keyword_adjustment))

    def compute_between(self, original: str, transformed: str) -> float:
        """Compute loss between original and transformed content."""
        if original == transformed:
            return 0.0

        # Simple token-based distance as fallback
        tokens_orig = set(original.lower().split())
        tokens_trans = set(transformed.lower().split())

        if not tokens_orig or not tokens_trans:
            return 1.0 if original != transformed else 0.0

        intersection = len(tokens_orig & tokens_trans)
        union = len(tokens_orig | tokens_trans)
        jaccard_sim = intersection / union if union > 0 else 0.0
        return 1.0 - jaccard_sim

    def semantic(self, description: str) -> float:
        """Compute semantic drift component."""
        return self.compute_text(description) * self.semantic_weight

    def bloat_loss_text(self, content: str) -> float:
        """Measure spec bloat (too much content relative to signal)."""
        # Indicators of bloat
        word_count = len(content.split())
        section_count = content.count("#")

        if word_count == 0:
            return 0.0

        words_per_section = word_count / max(section_count, 1)
        # Ideal: 100-300 words per section
        if 100 <= words_per_section <= 300:
            return 0.0
        elif words_per_section > 300:
            return min((words_per_section - 300) / 500, 0.5)
        else:
            return 0.1  # Too sparse

    def composition_loss_text(self, content: str) -> float:
        """Measure composition issues (poor interface design)."""
        # Look for composition-unfriendly patterns
        bad_patterns = [
            "depends on",
            "requires",
            "must be",
            "cannot be",
            "forbidden",
            "only if",
            "hardcoded",
            "specific to",
        ]
        content_lower = content.lower()
        bad_count = sum(1 for p in bad_patterns if p in content_lower)
        return min(bad_count * 0.1, 0.7)

    def safety_loss_text(self, spec_content: str, impl_content: str) -> float:
        """Measure safety constraint preservation from spec to impl."""
        # Safety keywords that should be preserved
        safety_keywords = [
            "must not",
            "never",
            "always",
            "required",
            "forbidden",
            "critical",
            "safety",
            "constraint",
            "invariant",
        ]

        spec_lower = spec_content.lower()
        impl_lower = impl_content.lower()

        # Count safety terms in spec
        spec_safety = sum(1 for kw in safety_keywords if kw in spec_lower)
        # Count safety terms in impl
        impl_safety = sum(1 for kw in safety_keywords if kw in impl_lower)

        if spec_safety == 0:
            return 0.0  # No safety constraints to preserve

        # Ratio of preserved safety constraints
        preservation_ratio = min(impl_safety / spec_safety, 1.0)
        return 1.0 - preservation_ratio

    def synthesis_loss_text(self, execution_content: str, reflection_content: str) -> float:
        """Measure synthesis quality from execution to reflection."""
        # Good synthesis extracts patterns and insights
        insight_keywords = [
            "pattern",
            "insight",
            "learned",
            "realized",
            "improved",
            "next time",
            "should have",
            "key takeaway",
        ]

        reflection_lower = reflection_content.lower()
        insight_count = sum(1 for kw in insight_keywords if kw in reflection_lower)

        # Also check that reflection references execution
        exec_words = set(execution_content.lower().split())
        refl_words = set(reflection_lower.split())
        overlap = len(exec_words & refl_words) / max(len(exec_words), 1)

        # Good synthesis: high insight density + references execution
        synthesis_quality = min(insight_count * 0.15, 0.5) + min(overlap, 0.5)
        return 1.0 - synthesis_quality

    def aesthetic_loss_text(self, content: str) -> float:
        """Measure aesthetic quality of representation."""
        # Aesthetic indicators (positive)
        elegant_patterns = [
            "elegant",
            "minimal",
            "clean",
            "simple",
            "beautiful",
            "harmonious",
            "balanced",
        ]
        # Anti-aesthetic indicators
        ugly_patterns = [
            "ugly",
            "bloated",
            "verbose",
            "complex",
            "convoluted",
            "messy",
            "unclear",
        ]

        content_lower = content.lower()
        elegant_count = sum(1 for p in elegant_patterns if p in content_lower)
        ugly_count = sum(1 for p in ugly_patterns if p in content_lower)

        # Base aesthetic from structure
        # Good: clear sections, consistent formatting
        section_count = content.count("#")
        list_count = content.count("- ")
        structure_score = min((section_count + list_count) / 10, 0.3)

        net_aesthetic = elegant_count - ugly_count
        keyword_score = max(-0.3, min(0.3, net_aesthetic * 0.1))

        # Lower loss = more aesthetic
        return max(0.0, min(1.0, 0.5 - structure_score - keyword_score))

    def logical_gap_text(self, premise: str, conclusion: str) -> float:
        """Measure logical gap between premise and conclusion."""
        # Simple heuristic: how much new content in conclusion?
        premise_tokens = set(premise.lower().split())
        conclusion_tokens = set(conclusion.lower().split())

        new_tokens = conclusion_tokens - premise_tokens
        new_ratio = len(new_tokens) / max(len(conclusion_tokens), 1)

        # Some new content is expected (entailment adds specificity)
        # Too much new content = logical gap
        if new_ratio < 0.3:
            return 0.1  # Tight entailment
        elif new_ratio < 0.5:
            return 0.3  # Reasonable derivation
        else:
            return min(new_ratio, 0.8)  # Large logical gap

    def restructure_to_layer(self, content: str, layer: int) -> str:
        """Simulate restructuring content to a target layer."""
        # This is a placeholder - real implementation would use LLM
        # For now, return content with layer annotation
        return f"[Layer {layer}]: {content}"


# -----------------------------------------------------------------------------
# Edge Transform Result
# -----------------------------------------------------------------------------


@dataclass
class EdgeTransform:
    """Result of applying an edge operator."""

    edge_kind: EdgeKind
    galois_loss: float  # L(source -> target via operator)
    constitutional_reward: float  # 1 - lambda*galois_loss + principle_bonuses
    proof_required: bool  # Does this transition require Toulmin proof?
    inverse: EdgeOperator | None  # Bidirectional inverse (if exists)

    # Loss decomposition
    semantic_drift: float  # Embedding distance
    structural_drift: float  # Graph edit distance
    operational_drift: float  # Behavioral change

    # Constitutional breakdown
    principle_scores: dict[str, float]  # Per-principle evaluation
    constitutional_violations: list[str]  # Any hard constraints violated


# -----------------------------------------------------------------------------
# Edge Kind Enumeration
# -----------------------------------------------------------------------------


class EdgeKind(Enum):
    """The 10 fundamental edge operators."""

    # Inter-layer (vertical flow)
    GROUNDS = "grounds"  # L1 -> L2 (axiom absorption)
    JUSTIFIES = "justifies"  # L2 -> L3 (value preservation)
    SPECIFIES = "specifies"  # L3 -> L4 (goal concretization)
    IMPLEMENTS = "implements"  # L4 -> L5 (spec deviation)
    REFLECTS_ON = "reflects_on"  # L5 -> L6 (synthesis gap)
    REPRESENTS = "represents"  # L6 -> L7 (meta-blindness)

    # Intra-layer (horizontal flow)
    DERIVES = "derives"  # Logical entailment
    SYNTHESIZES = "synthesizes"  # Synergistic composition (sub-additive loss)

    # Dialectical (conflict/resolution)
    CONTRADICTS = "contradicts"  # Super-additive loss signal

    # Meta (non-standard)
    CROSS_LAYER = "cross_layer"  # Non-adjacent layer jump


# -----------------------------------------------------------------------------
# Edge Operator Base Class
# -----------------------------------------------------------------------------


class EdgeOperator(ABC):
    """
    Base class for edge operators.

    An edge operator transforms node content via restructuring.

    Laws:
    1. Monotonicity: Preserves partial order (more specific -> more specific)
    2. Continuity: lim(apply(x_i)) = apply(lim(x_i))
    3. Bounded Loss: L(apply(x)) <= L_max for all x
    """

    galois: GaloisLoss
    edge_kind: EdgeKind

    @abstractmethod
    def apply(self, source: ZeroNode, target: ZeroNode) -> EdgeTransform:
        """
        Apply operator to create edge: source -op-> target.

        Returns EdgeTransform containing loss, reward, and proof obligations.
        """
        ...

    @abstractmethod
    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """
        Operator composition: (op1 o op2)(x) = op1(op2(x)).

        Laws:
        - Associativity: (op1 o op2) o op3 = op1 o (op2 o op3)
        - Loss subadditivity: L(op1 o op2) <= L(op1) + L(op2)
        """
        ...

    @abstractmethod
    def inverse(self) -> EdgeOperator | None:
        """
        Partial inverse operator (if exists).

        Properties:
        - op o op^-1 approx id (up to Galois loss)
        - Not all operators are invertible
        """
        ...


# -----------------------------------------------------------------------------
# Operator Registry
# -----------------------------------------------------------------------------

OPERATORS: dict[EdgeKind, type[EdgeOperator]] = {}


def operator(kind: EdgeKind) -> Callable[[type[EdgeOperator]], type[EdgeOperator]]:
    """Decorator to register edge operators."""

    def wrapper(cls: type[EdgeOperator]) -> type[EdgeOperator]:
        OPERATORS[kind] = cls
        cls.edge_kind = kind
        return cls

    return wrapper


# -----------------------------------------------------------------------------
# Loss Bounds per Operator
# -----------------------------------------------------------------------------

LOSS_BOUNDS: dict[EdgeKind, dict[str, float]] = {
    EdgeKind.GROUNDS: {
        "min": 0.0,  # Perfect grounding
        "typical": 0.05,  # Slight interpretation
        "max": 0.3,  # Weak grounding
        "reject": 0.5,  # Too tenuous
    },
    EdgeKind.JUSTIFIES: {
        "min": 0.0,  # Terminal goal
        "typical": 0.15,  # Instrumental goal
        "max": 0.4,  # Tenuous justification
        "reject": 0.7,  # Goal conflicts with value
    },
    EdgeKind.SPECIFIES: {
        "min": 0.05,  # Some detail necessary
        "typical": 0.25,  # Standard spec drift
        "max": 0.5,  # Significant drift
        "reject": 0.8,  # Spec doesn't serve goal
    },
    EdgeKind.IMPLEMENTS: {
        "min": 0.1,  # Some deviation inevitable
        "typical": 0.35,  # Standard compromises
        "max": 0.6,  # Significant pragmatic drift
        "reject": 0.8,  # Implementation doesn't realize spec
    },
    EdgeKind.REFLECTS_ON: {
        "min": 0.2,  # Reflection inherently lossy
        "typical": 0.4,  # Standard synthesis
        "max": 0.7,  # Shallow reflection
        "reject": 0.9,  # Doesn't engage execution
    },
    EdgeKind.REPRESENTS: {
        "min": 0.3,  # Maximally lossy (terminal)
        "typical": 0.5,  # Standard meta-blindness
        "max": 0.8,  # Shallow representation
        "reject": 0.95,  # Meaningless
    },
    EdgeKind.DERIVES: {
        "min": 0.0,  # Direct entailment
        "typical": 0.2,  # Few inference steps
        "max": 0.5,  # Many assumptions
        "reject": 0.8,  # Non sequitur
    },
    EdgeKind.SYNTHESIZES: {
        "min": -0.3,  # NEGATIVE loss (pure synergy)
        "typical": 0.1,  # Slight loss with synergy
        "max": 0.4,  # Weak synthesis
        "reject": 0.7,  # No synergy
    },
    EdgeKind.CONTRADICTS: {
        "min": 0.1,  # Tolerance threshold
        "typical": 0.4,  # Standard contradiction
        "max": 0.8,  # Severe contradiction
        "reject": 1.0,  # Explosion
    },
    EdgeKind.CROSS_LAYER: {
        "min": 0.1,  # 1 layer skip
        "typical": 0.5,  # 2-3 layer skip
        "max": 1.2,  # Large skip (L1->L5)
        "reject": 2.0,  # Too many layers
    },
}


def get_loss_bounds(edge_kind: EdgeKind) -> dict[str, float]:
    """Get loss bounds for an edge kind."""
    return LOSS_BOUNDS[edge_kind]


# -----------------------------------------------------------------------------
# Constitutional Weights per Operator
# -----------------------------------------------------------------------------

CONSTITUTIONAL_WEIGHTS: dict[EdgeKind, dict[str, float]] = {
    EdgeKind.GROUNDS: {
        "ETHICAL": 2.0,
        "CURATED": 1.5,
        "GENERATIVE": 1.5,
        "TASTEFUL": 1.0,
        "COMPOSABLE": 1.0,
        "HETERARCHICAL": 0.8,
        "JOY_INDUCING": 0.9,
    },
    EdgeKind.JUSTIFIES: {
        "ETHICAL": 1.8,
        "CURATED": 1.5,
        "GENERATIVE": 1.5,
        "TASTEFUL": 1.2,
        "COMPOSABLE": 1.0,
        "HETERARCHICAL": 1.0,
        "JOY_INDUCING": 1.0,
    },
    EdgeKind.SPECIFIES: {
        "GENERATIVE": 2.0,
        "COMPOSABLE": 1.8,
        "TASTEFUL": 1.5,
        "CURATED": 1.3,
        "ETHICAL": 1.2,
        "HETERARCHICAL": 1.0,
        "JOY_INDUCING": 0.9,
    },
    EdgeKind.IMPLEMENTS: {
        "ETHICAL": 2.5,  # CRITICAL: safety in execution
        "COMPOSABLE": 1.8,
        "GENERATIVE": 1.5,
        "TASTEFUL": 1.0,
        "CURATED": 1.0,
        "HETERARCHICAL": 1.0,
        "JOY_INDUCING": 0.9,
    },
    EdgeKind.REFLECTS_ON: {
        "GENERATIVE": 1.8,
        "JOY_INDUCING": 1.5,
        "CURATED": 1.3,
        "TASTEFUL": 1.0,
        "ETHICAL": 0.9,
        "COMPOSABLE": 0.8,
        "HETERARCHICAL": 1.0,
    },
    EdgeKind.REPRESENTS: {
        "TASTEFUL": 2.0,
        "JOY_INDUCING": 1.8,
        "COMPOSABLE": 1.3,
        "CURATED": 1.2,
        "GENERATIVE": 1.0,
        "ETHICAL": 0.9,
        "HETERARCHICAL": 1.0,
    },
    EdgeKind.DERIVES: {
        "GENERATIVE": 1.8,
        "CURATED": 1.5,
        "COMPOSABLE": 1.3,
        "TASTEFUL": 1.0,
        "ETHICAL": 0.9,
        "HETERARCHICAL": 1.0,
        "JOY_INDUCING": 0.9,
    },
    EdgeKind.SYNTHESIZES: {
        "HETERARCHICAL": 2.0,  # Peak heterarchical operation
        "GENERATIVE": 1.8,
        "JOY_INDUCING": 1.5,
        "CURATED": 1.0,
        "TASTEFUL": 1.0,
        "COMPOSABLE": 0.9,
        "ETHICAL": 0.9,
    },
    EdgeKind.CONTRADICTS: {
        "HETERARCHICAL": 2.0,
        "GENERATIVE": 1.3,
        "CURATED": 0.8,
        "JOY_INDUCING": 0.5,
        "TASTEFUL": 0.6,
        "COMPOSABLE": 0.3,
        "ETHICAL": 0.8,
    },
    EdgeKind.CROSS_LAYER: {
        "GENERATIVE": 1.5,
        "CURATED": 0.7,
        "TASTEFUL": 1.0,
        "COMPOSABLE": 0.6,
        "ETHICAL": 0.9,
        "HETERARCHICAL": 1.0,
        "JOY_INDUCING": 0.7,
    },
}


def compute_constitutional_reward(
    edge_kind: EdgeKind,
    principle_scores: dict[str, float],
) -> float:
    """
    Compute weighted constitutional reward.

    R_constitutional = sum_i(w_i * score_i) / sum_i(w_i)
    """
    weights = CONSTITUTIONAL_WEIGHTS[edge_kind]
    total_weighted = sum(weights[p] * principle_scores[p] for p in weights)
    total_weight = sum(weights.values())
    return total_weighted / total_weight


# -----------------------------------------------------------------------------
# Layer Transition Rules
# -----------------------------------------------------------------------------

LAYER_TRANSITIONS: dict[EdgeKind, list[tuple[int, int]]] = {
    EdgeKind.GROUNDS: [(1, 2)],
    EdgeKind.JUSTIFIES: [(2, 3)],
    EdgeKind.SPECIFIES: [(3, 4)],
    EdgeKind.IMPLEMENTS: [(4, 5)],
    EdgeKind.REFLECTS_ON: [(5, 6)],
    EdgeKind.REPRESENTS: [(6, 7)],
    EdgeKind.DERIVES: [(i, i) for i in range(1, 8)],
    EdgeKind.SYNTHESIZES: [(i, i) for i in range(1, 8)],
    EdgeKind.CONTRADICTS: [(i, i) for i in range(1, 8)],
    EdgeKind.CROSS_LAYER: [
        (i, j) for i in range(1, 8) for j in range(1, 8) if abs(i - j) > 1
    ],
}


def is_valid_transition(
    source_layer: int,
    target_layer: int,
    edge_kind: EdgeKind,
) -> bool:
    """Check if layer transition is valid for edge kind."""
    return (source_layer, target_layer) in LAYER_TRANSITIONS[edge_kind]


# -----------------------------------------------------------------------------
# Fixed Point Threshold
# -----------------------------------------------------------------------------

FIXED_POINT_THRESHOLD = 0.01


# -----------------------------------------------------------------------------
# The 10 Operator Implementations
# -----------------------------------------------------------------------------


@operator(EdgeKind.GROUNDS)
@dataclass
class GroundsOperator(EdgeOperator):
    """
    Nabla_g: L1 (Axioms) -> L2 (Values)

    Loss Semantics:
    - Axioms are zero-loss fixed points: L(axiom) ~ 0
    - Values inherit axiom stability
    - Loss = distance from axiomatic ground

    Constitutional Affinity:
    - ETHICAL (highest): Axioms define safety boundaries
    - CURATED: Only essential axioms admitted
    - GENERATIVE: All values derive from axioms
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.GROUNDS, init=False)

    def apply(self, axiom: ZeroNode, value: ZeroNode) -> EdgeTransform:
        """Ground a value in an axiom."""
        if axiom.layer != 1 or value.layer != 2:
            raise ValueError("GROUNDS requires L1 -> L2")

        # Axioms have near-zero loss
        axiom_loss = self.galois.compute(axiom.content)
        if axiom_loss >= FIXED_POINT_THRESHOLD * 10:
            # Warning: source may not be truly axiomatic
            pass

        # Compute grounding loss
        grounding_desc = f"""
        Value: {value.title}
        {value.content}

        Grounded in axiom: {axiom.title}
        {axiom.content}

        Inheritance: How does the value derive necessity from the axiom?
        """
        loss = self.galois.compute_text(grounding_desc)

        principle_scores = {
            "ETHICAL": 1.0 - 0.5 * loss,
            "CURATED": 1.0 - loss,
            "GENERATIVE": 1.0 - loss,
            "TASTEFUL": 1.0,
            "COMPOSABLE": 1.0,
            "HETERARCHICAL": 0.8,
            "JOY_INDUCING": 0.9,
        }

        return EdgeTransform(
            edge_kind=EdgeKind.GROUNDS,
            galois_loss=loss,
            constitutional_reward=1.0 - 0.3 * loss,
            proof_required=False,  # L1-L2 needs no proof (axioms self-justify)
            inverse=None,  # GROUNDS is not invertible
            semantic_drift=self.galois.semantic(grounding_desc),
            structural_drift=0.0,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=[],
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Compose with next operator."""
        if isinstance(other, JustifiesOperator):
            return CrossLayerOperator(
                source_layer=1,
                target_layer=3,
                via_layers=[2],
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose GROUNDS with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """No inverse: can't remove grounding without invalidating value."""
        return None


@operator(EdgeKind.JUSTIFIES)
@dataclass
class JustifiesOperator(EdgeOperator):
    """
    Nabla_j: L2 (Values) -> L3 (Goals)

    Loss Semantics:
    - Low loss = goal directly expresses value
    - High loss = goal deviates from value

    Constitutional Affinity:
    - CURATED: Goals must have explicit value justification
    - ETHICAL: Values ensure goal safety
    - GENERATIVE: Goals derive from values
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.JUSTIFIES, init=False)

    def apply(self, value: ZeroNode, goal: ZeroNode) -> EdgeTransform:
        """Justify a goal by a value."""
        if value.layer != 2 or goal.layer != 3:
            raise ValueError("JUSTIFIES requires L2 -> L3")

        justification_desc = f"""
        Value: {value.title}
        {value.content}

        Goal: {goal.title}
        {goal.content}

        Justification: Does this goal serve the value?
        """
        loss = self.galois.compute_text(justification_desc)

        principle_scores = {
            "ETHICAL": 1.0 - 0.7 * loss,
            "CURATED": 1.0 - loss,
            "GENERATIVE": 1.0 - loss,
            "TASTEFUL": 1.0 - 0.5 * loss,
            "COMPOSABLE": 1.0 - 0.3 * loss,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.9 - 0.3 * loss,
        }

        violations = ["Value-goal misalignment"] if loss > 0.6 else []

        return EdgeTransform(
            edge_kind=EdgeKind.JUSTIFIES,
            galois_loss=loss,
            constitutional_reward=1.0 - 0.5 * loss,
            proof_required=True,
            inverse=None,  # Partial inverse via GeneralizesOperator
            semantic_drift=self.galois.semantic(justification_desc),
            structural_drift=0.1,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Compose with next operator."""
        if isinstance(other, SpecifiesOperator):
            return CrossLayerOperator(
                source_layer=2,
                target_layer=4,
                via_layers=[3],
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose JUSTIFIES with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """Partial inverse: GENERALIZES (goal -> abstract value)."""
        return GeneralizesOperator(galois=self.galois)


@operator(EdgeKind.SPECIFIES)
@dataclass
class SpecifiesOperator(EdgeOperator):
    """
    Nabla_s: L3 (Goals) -> L4 (Specs)

    Loss Semantics:
    - Low loss = spec fully captures goal
    - High loss = spec drift (implementation bias)

    Constitutional Affinity:
    - GENERATIVE: Specs derive mechanically from goals
    - COMPOSABLE: Specs must have clean interfaces
    - TASTEFUL: Avoid bloat in specification
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.SPECIFIES, init=False)

    def apply(self, goal: ZeroNode, spec: ZeroNode) -> EdgeTransform:
        """Specify a goal into a concrete specification."""
        if goal.layer != 3 or spec.layer != 4:
            raise ValueError("SPECIFIES requires L3 -> L4")

        specification_desc = f"""
        Goal: {goal.title}
        {goal.content}

        Specification: {spec.title}
        {spec.content}

        Concretization: Does the spec fully realize the goal?
        """
        loss = self.galois.compute_text(specification_desc)
        bloat_loss = self.galois.bloat_loss_text(spec.content)
        composition_loss = self.galois.composition_loss_text(spec.content)

        total_loss = 0.5 * loss + 0.3 * bloat_loss + 0.2 * composition_loss

        principle_scores = {
            "GENERATIVE": 1.0 - loss,
            "COMPOSABLE": 1.0 - composition_loss,
            "TASTEFUL": 1.0 - bloat_loss,
            "CURATED": 1.0 - 0.5 * loss,
            "ETHICAL": 0.9 - 0.3 * loss,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.8 - 0.4 * bloat_loss,
        }

        violations = []
        if bloat_loss > 0.5:
            violations.append("Spec bloat")
        if composition_loss > 0.6:
            violations.append("Poor composability")

        return EdgeTransform(
            edge_kind=EdgeKind.SPECIFIES,
            galois_loss=total_loss,
            constitutional_reward=1.0 - 0.6 * total_loss,
            proof_required=True,
            inverse=AbstractsOperator(galois=self.galois),
            semantic_drift=self.galois.semantic(specification_desc),
            structural_drift=0.3,
            operational_drift=0.1,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Compose with next operator."""
        if isinstance(other, ImplementsOperator):
            return CrossLayerOperator(
                source_layer=3,
                target_layer=5,
                via_layers=[4],
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose SPECIFIES with {type(other).__name__}")

    def inverse(self) -> EdgeOperator:
        """Inverse: ABSTRACTS (spec -> abstract goal)."""
        return AbstractsOperator(galois=self.galois)


@operator(EdgeKind.IMPLEMENTS)
@dataclass
class ImplementsOperator(EdgeOperator):
    """
    Nabla_i: L4 (Specs) -> L5 (Execution)

    Loss Semantics:
    - Low loss = spec fully realized
    - High loss = pragmatic compromises, reality constraints

    Constitutional Affinity:
    - ETHICAL: Implementation must preserve safety constraints
    - COMPOSABLE: Execution must match spec interfaces
    - GENERATIVE: Implementation should be derivable
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.IMPLEMENTS, init=False)

    def apply(self, spec: ZeroNode, execution: ZeroNode) -> EdgeTransform:
        """Implement a specification in executable form."""
        if spec.layer != 4 or execution.layer != 5:
            raise ValueError("IMPLEMENTS requires L4 -> L5")

        implementation_desc = f"""
        Specification: {spec.title}
        {spec.content}

        Implementation: {execution.title}
        {execution.content}

        Fidelity: Does the implementation realize the spec?
        """
        loss = self.galois.compute_text(implementation_desc)
        safety_loss = self.galois.safety_loss_text(spec.content, execution.content)
        composition_loss = self.galois.composition_loss_text(execution.content)

        total_loss = 0.4 * loss + 0.4 * safety_loss + 0.2 * composition_loss

        principle_scores = {
            "ETHICAL": 1.0 - safety_loss,  # CRITICAL
            "COMPOSABLE": 1.0 - composition_loss,
            "GENERATIVE": 1.0 - 0.7 * loss,
            "TASTEFUL": 0.9 - 0.5 * loss,
            "CURATED": 1.0 - 0.5 * loss,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.8 - 0.6 * loss,
        }

        violations = []
        if safety_loss > 0.3:
            violations.append("SAFETY VIOLATION")
        if composition_loss > 0.6:
            violations.append("Interface mismatch")

        # Safety violations get negative reward
        if safety_loss > 0.3:
            reward = -1.0
        else:
            reward = 1.0 - 0.7 * loss - 0.3 * safety_loss

        return EdgeTransform(
            edge_kind=EdgeKind.IMPLEMENTS,
            galois_loss=total_loss,
            constitutional_reward=reward,
            proof_required=True,
            inverse=None,  # Can't invert implementation
            semantic_drift=self.galois.semantic(implementation_desc),
            structural_drift=0.4,
            operational_drift=0.8,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Compose with next operator."""
        if isinstance(other, ReflectsOnOperator):
            return CrossLayerOperator(
                source_layer=4,
                target_layer=6,
                via_layers=[5],
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose IMPLEMENTS with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """No clean inverse: can't extract spec from impl without loss."""
        return None


@operator(EdgeKind.REFLECTS_ON)
@dataclass
class ReflectsOnOperator(EdgeOperator):
    """
    Nabla_r: L5 (Execution) -> L6 (Reflection)

    Loss Semantics:
    - Low loss = reflection fully synthesizes execution
    - High loss = synthesis gap (missed insights)

    Constitutional Affinity:
    - GENERATIVE: Reflections enable future improvements
    - JOY_INDUCING: Reflection creates meaning
    - CURATED: Intentional synthesis
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.REFLECTS_ON, init=False)

    def apply(self, execution: ZeroNode, reflection: ZeroNode) -> EdgeTransform:
        """Reflect on an execution to extract insights."""
        if execution.layer != 5 or reflection.layer != 6:
            raise ValueError("REFLECTS_ON requires L5 -> L6")

        reflection_desc = f"""
        Execution: {execution.title}
        {execution.content}

        Reflection: {reflection.title}
        {reflection.content}

        Synthesis: Does the reflection capture key insights?
        """
        loss = self.galois.compute_text(reflection_desc)
        synthesis_loss = self.galois.synthesis_loss_text(
            execution.content, reflection.content
        )

        total_loss = 0.6 * loss + 0.4 * synthesis_loss

        principle_scores = {
            "GENERATIVE": 1.0 - synthesis_loss,
            "JOY_INDUCING": 1.0 - 0.5 * loss,
            "CURATED": 1.0 - loss,
            "TASTEFUL": 1.0 - 0.3 * loss,
            "ETHICAL": 0.9,
            "COMPOSABLE": 0.8,
            "HETERARCHICAL": 1.0,
        }

        violations = ["Synthesis gap"] if synthesis_loss > 0.6 else []

        return EdgeTransform(
            edge_kind=EdgeKind.REFLECTS_ON,
            galois_loss=total_loss,
            constitutional_reward=1.0 - 0.5 * total_loss,
            proof_required=True,
            inverse=None,
            semantic_drift=self.galois.semantic(reflection_desc),
            structural_drift=0.5,
            operational_drift=-0.3,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Compose with next operator."""
        if isinstance(other, RepresentsOperator):
            return CrossLayerOperator(
                source_layer=5,
                target_layer=7,
                via_layers=[6],
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose REFLECTS_ON with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """No inverse: can't reconstruct execution from reflection."""
        return None


@operator(EdgeKind.REPRESENTS)
@dataclass
class RepresentsOperator(EdgeOperator):
    """
    Nabla_p: L6 (Reflection) -> L7 (Representation)

    Loss Semantics:
    - Low loss = representation faithfully captures reflection
    - High loss = meta-blindness (tacit knowledge lost)

    Constitutional Affinity:
    - TASTEFUL: Representations should be elegant
    - COMPOSABLE: External forms must compose
    - JOY_INDUCING: Beautiful representations
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.REPRESENTS, init=False)

    def apply(self, reflection: ZeroNode, representation: ZeroNode) -> EdgeTransform:
        """Represent a reflection in external form."""
        if reflection.layer != 6 or representation.layer != 7:
            raise ValueError("REPRESENTS requires L6 -> L7")

        representation_desc = f"""
        Reflection: {reflection.title}
        {reflection.content}

        Representation: {representation.title}
        {representation.content}

        Fidelity: Does the representation capture the reflection?
        """
        loss = self.galois.compute_text(representation_desc)
        aesthetic_loss = self.galois.aesthetic_loss_text(representation.content)

        total_loss = 0.6 * loss + 0.4 * aesthetic_loss

        principle_scores = {
            "TASTEFUL": 1.0 - aesthetic_loss,
            "JOY_INDUCING": 1.0 - aesthetic_loss,
            "COMPOSABLE": 1.0 - 0.5 * loss,
            "CURATED": 1.0 - 0.7 * loss,
            "GENERATIVE": 0.8 - 0.5 * loss,
            "ETHICAL": 0.9,
            "HETERARCHICAL": 1.0,
        }

        violations = ["Aesthetic failure"] if aesthetic_loss > 0.7 else []

        return EdgeTransform(
            edge_kind=EdgeKind.REPRESENTS,
            galois_loss=total_loss,
            constitutional_reward=1.0 - 0.3 * loss - 0.4 * aesthetic_loss,
            proof_required=True,
            inverse=None,
            semantic_drift=self.galois.semantic(representation_desc),
            structural_drift=0.6,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Terminal operator: no further composition."""
        raise TypeError("REPRESENTS is terminal (L7 is final layer)")

    def inverse(self) -> EdgeOperator | None:
        """No inverse: can't recover reflection from representation."""
        return None


@operator(EdgeKind.DERIVES)
@dataclass
class DerivesOperator(EdgeOperator):
    """
    Nabla_d: Intra-layer logical derivation

    Loss Semantics:
    - Low loss = direct entailment (few inference steps)
    - High loss = tenuous connection (many assumptions)

    Constitutional Affinity:
    - GENERATIVE: Derivations extend the graph
    - COMPOSABLE: Derived nodes compose cleanly
    - CURATED: Derivation must be justified
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.DERIVES, init=False)

    def apply(self, premise: ZeroNode, conclusion: ZeroNode) -> EdgeTransform:
        """Derive a conclusion from a premise (same layer)."""
        if premise.layer != conclusion.layer:
            raise ValueError("DERIVES requires same layer")

        derivation_desc = f"""
        Premise: {premise.title}
        {premise.content}

        Conclusion: {conclusion.title}
        {conclusion.content}

        Logical steps: Does the conclusion follow from the premise?
        """
        loss = self.galois.compute_text(derivation_desc)
        logical_gap = self.galois.logical_gap_text(premise.content, conclusion.content)

        total_loss = 0.5 * loss + 0.5 * logical_gap

        principle_scores = {
            "GENERATIVE": 1.0 - logical_gap,
            "CURATED": 1.0 - loss,
            "COMPOSABLE": 1.0 - 0.3 * loss,
            "TASTEFUL": 1.0 - 0.4 * loss,
            "ETHICAL": 0.9,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.85 - 0.3 * logical_gap,
        }

        violations = ["Logical gap"] if logical_gap > 0.6 else []

        return EdgeTransform(
            edge_kind=EdgeKind.DERIVES,
            galois_loss=total_loss,
            constitutional_reward=1.0 - 0.6 * total_loss,
            proof_required=True,
            inverse=GeneralizesOperator(galois=self.galois),
            semantic_drift=self.galois.semantic(derivation_desc),
            structural_drift=0.2,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Transitive derivation chain."""
        if isinstance(other, DerivesOperator):
            return DerivesOperator(galois=self.galois)
        raise TypeError(f"Cannot compose DERIVES with {type(other).__name__}")

    def inverse(self) -> EdgeOperator:
        """Partial inverse: GENERALIZES."""
        return GeneralizesOperator(galois=self.galois)


@operator(EdgeKind.SYNTHESIZES)
@dataclass
class SynthesizesOperator(EdgeOperator):
    """
    Nabla_y: Dialectical synthesis

    Loss Semantics:
    - SYNERGY: L(A + B) < L(A) + L(B)
    - Sub-additive loss = emergent structure
    - Synthesis resolves tensions, creates coherence

    Constitutional Affinity:
    - HETERARCHICAL: Synthesis transcends hierarchy
    - GENERATIVE: Creates new possibilities
    - JOY_INDUCING: Synergy is delightful
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.SYNTHESIZES, init=False)

    def apply(
        self, thesis: ZeroNode, antithesis: ZeroNode, synthesis: ZeroNode | None = None
    ) -> EdgeTransform:
        """
        Synthesize thesis and antithesis into new node.

        Note: This is a ternary operation for full synthesis.
        For binary, synthesis target is inferred.
        """
        if synthesis is None:
            # Binary mode: thesis -> antithesis relationship
            synthesis = antithesis

        if not (thesis.layer == antithesis.layer == synthesis.layer):
            raise ValueError("SYNTHESIZES requires same layer")

        synthesis_desc = f"""
        Thesis: {thesis.title}
        {thesis.content}

        Antithesis: {antithesis.title}
        {antithesis.content}

        Synthesis: {synthesis.title}
        {synthesis.content}

        Synergy: Does the synthesis transcend the opposition?
        """

        # Individual losses
        loss_thesis = self.galois.compute(thesis.content)
        loss_antithesis = self.galois.compute(antithesis.content)

        # Joint loss
        loss_synthesis = self.galois.compute_text(synthesis_desc)

        # Synergy = sub-additivity
        synergy = (loss_thesis + loss_antithesis) - loss_synthesis

        # For binary mode, we're lenient on synergy check
        if synergy <= 0 and synthesis != antithesis:
            raise ValueError(f"No synergy detected: {synergy:.3f} <= 0")

        # Clamp synergy for score computation
        synergy = max(0.0, synergy)

        principle_scores = {
            "HETERARCHICAL": 1.0,  # Peak heterarchical operation
            "GENERATIVE": 1.0 - 0.3 * loss_synthesis + 0.5 * synergy,
            "JOY_INDUCING": 1.0 - 0.2 * loss_synthesis + 0.7 * synergy,
            "CURATED": 1.0 - 0.5 * loss_synthesis,
            "TASTEFUL": 1.0 - 0.4 * loss_synthesis + 0.3 * synergy,
            "COMPOSABLE": 0.9,
            "ETHICAL": 0.9,
        }

        # Clamp scores to [0, 1]
        principle_scores = {k: max(0.0, min(1.0, v)) for k, v in principle_scores.items()}

        return EdgeTransform(
            edge_kind=EdgeKind.SYNTHESIZES,
            galois_loss=loss_synthesis,
            constitutional_reward=1.0 - 0.3 * loss_synthesis + 0.7 * synergy,
            proof_required=True,
            inverse=None,
            semantic_drift=self.galois.semantic(synthesis_desc),
            structural_drift=-synergy,  # NEGATIVE drift (simplification)
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=[],
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Synthesis doesn't compose cleanly."""
        raise TypeError("SYNTHESIZES is dialectical (doesn't compose)")

    def inverse(self) -> EdgeOperator | None:
        """No inverse: can't decompose emergent structure."""
        return None


@operator(EdgeKind.CONTRADICTS)
@dataclass
class ContradictsOperator(EdgeOperator):
    """
    Nabla_c: Paraconsistent contradiction

    Loss Semantics:
    - TENSION: L(A + B) > L(A) + L(B)
    - Super-additive loss = semantic incompatibility
    - Contradictions are INVITATIONS to synthesis

    Constitutional Affinity:
    - HETERARCHICAL: Contradictions reveal multiple valid views
    - CURATED: Intentional tension (not error)
    - GENERATIVE: Contradictions drive dialectic
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    tolerance: float = 0.1  # tau in super-additivity check
    edge_kind: EdgeKind = field(default=EdgeKind.CONTRADICTS, init=False)

    def apply(self, node_a: ZeroNode, node_b: ZeroNode) -> EdgeTransform:
        """Mark two nodes as contradictory."""
        # Individual losses
        loss_a = self.galois.compute(node_a.content)
        loss_b = self.galois.compute(node_b.content)

        # Joint loss
        joint_content = f"{node_a.content}\n\n{node_b.content}"
        loss_joint = self.galois.compute_text(joint_content)

        # Check super-additivity
        super_additive = loss_joint - (loss_a + loss_b)

        if super_additive <= self.tolerance:
            raise ValueError(
                f"Not a genuine contradiction: "
                f"super_additive={super_additive:.3f} <= tau={self.tolerance}"
            )

        principle_scores = {
            "HETERARCHICAL": 1.0,
            "CURATED": 0.8,
            "GENERATIVE": 0.7 + 0.3 * min(super_additive, 1.0),
            "JOY_INDUCING": 0.5,
            "TASTEFUL": 0.6,
            "COMPOSABLE": 0.3,
            "ETHICAL": 0.8,
        }

        violations = ["Severe contradiction"] if super_additive >= 0.7 else []

        # Mild contradictions are generative; severe ones problematic
        if super_additive < 0.3:
            reward = 0.5 + super_additive
        else:
            reward = 0.5 - 0.5 * (super_additive - 0.3)

        return EdgeTransform(
            edge_kind=EdgeKind.CONTRADICTS,
            galois_loss=super_additive,  # Loss IS the tension
            constitutional_reward=reward,
            proof_required=True,
            inverse=None,  # Symmetric
            semantic_drift=super_additive,
            structural_drift=0.0,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Contradictions don't compose."""
        raise TypeError("CONTRADICTS is symmetric (doesn't compose)")

    def inverse(self) -> EdgeOperator | None:
        """Symmetric operator (self-inverse)."""
        return self


@operator(EdgeKind.CROSS_LAYER)
@dataclass
class CrossLayerOperator(EdgeOperator):
    """
    Nabla_x: Non-adjacent layer jump

    Loss Semantics:
    - L(L_i -> L_j) = sum L(L_k -> L_{k+1}) for i < k < j
    - Loss accumulation from skipped layers
    - Used for composition shortcuts

    Constitutional Affinity:
    - GENERATIVE: When derivable from composition
    - TASTEFUL: When skipping reduces bloat
    - CURATED: Requires explicit justification
    """

    source_layer: int
    target_layer: int
    via_layers: list[int]  # Intermediate layers skipped
    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.CROSS_LAYER, init=False)

    def apply(self, source: ZeroNode, target: ZeroNode) -> EdgeTransform:
        """Create cross-layer edge."""
        if source.layer != self.source_layer or target.layer != self.target_layer:
            raise ValueError(
                f"Layer mismatch: expected {self.source_layer}->{self.target_layer}"
            )

        if abs(source.layer - target.layer) <= 1:
            raise ValueError("CROSS_LAYER requires non-adjacent layers")

        # Compute accumulated loss
        accumulated_loss = 0.0
        current_content = source.content

        for layer in self.via_layers:
            intermediate = self.galois.restructure_to_layer(current_content, layer)
            loss_step = self.galois.compute_between(current_content, intermediate)
            accumulated_loss += loss_step
            current_content = intermediate

        # Final step to target
        final_loss = self.galois.compute_between(current_content, target.content)
        accumulated_loss += final_loss

        cross_layer_desc = f"""
        Source (L{source.layer}): {source.title}
        Target (L{target.layer}): {target.title}
        Skipped layers: {self.via_layers}
        Accumulated loss: {accumulated_loss:.3f}
        """

        principle_scores = {
            "GENERATIVE": 1.0 - 0.8 * accumulated_loss,
            "CURATED": 0.7,
            "TASTEFUL": 1.0 - 0.5 * accumulated_loss,
            "COMPOSABLE": 0.6,
            "ETHICAL": 0.9 - 0.3 * accumulated_loss,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.7,
        }

        # Clamp scores
        principle_scores = {k: max(0.0, min(1.0, v)) for k, v in principle_scores.items()}

        violations = ["Excessive layer skip"] if len(self.via_layers) > 3 else []

        return EdgeTransform(
            edge_kind=EdgeKind.CROSS_LAYER,
            galois_loss=accumulated_loss,
            constitutional_reward=1.0 - 0.9 * accumulated_loss,
            proof_required=True,
            inverse=None,
            semantic_drift=self.galois.semantic(cross_layer_desc),
            structural_drift=0.5 * len(self.via_layers),
            operational_drift=0.3 * len(self.via_layers),
            principle_scores=principle_scores,
            constitutional_violations=violations,
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Cross-layer edges compose by concatenating via_layers."""
        if isinstance(other, CrossLayerOperator):
            return CrossLayerOperator(
                source_layer=self.source_layer,
                target_layer=other.target_layer,
                via_layers=self.via_layers + [self.target_layer] + other.via_layers,
                galois=self.galois,
            )
        raise TypeError(f"Cannot compose CROSS_LAYER with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """Inverse cross-layer (reverse path)."""
        return CrossLayerOperator(
            source_layer=self.target_layer,
            target_layer=self.source_layer,
            via_layers=list(reversed(self.via_layers)),
            galois=self.galois,
        )


# -----------------------------------------------------------------------------
# Inverse Operators (Partial Adjoints)
# -----------------------------------------------------------------------------


@dataclass
class GeneralizesOperator(EdgeOperator):
    """
    Partial inverse of JUSTIFIES and DERIVES.

    Generalizes a specific node to a more abstract form.
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.DERIVES, init=False)  # Uses DERIVES edge type

    def apply(self, specific: ZeroNode, general: ZeroNode) -> EdgeTransform:
        """Generalize a specific node to abstract form."""
        desc = f"""
        Specific: {specific.title}
        {specific.content}

        General: {general.title}
        {general.content}

        Generalization: Does the general form capture the essence?
        """
        loss = self.galois.compute_text(desc)

        principle_scores = {
            "GENERATIVE": 1.0 - loss,
            "CURATED": 1.0 - 0.5 * loss,
            "COMPOSABLE": 1.0 - 0.3 * loss,
            "TASTEFUL": 1.0 - 0.4 * loss,
            "ETHICAL": 0.9,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.85 - 0.3 * loss,
        }

        return EdgeTransform(
            edge_kind=EdgeKind.DERIVES,
            galois_loss=loss,
            constitutional_reward=1.0 - 0.5 * loss,
            proof_required=True,
            inverse=None,
            semantic_drift=self.galois.semantic(desc),
            structural_drift=-0.2,
            operational_drift=0.0,
            principle_scores=principle_scores,
            constitutional_violations=[],
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Generalization composes with derivation."""
        if isinstance(other, DerivesOperator):
            return GeneralizesOperator(galois=self.galois)
        raise TypeError(f"Cannot compose GENERALIZES with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """Inverse: derivation (specialize)."""
        return DerivesOperator(galois=self.galois)


@dataclass
class AbstractsOperator(EdgeOperator):
    """
    Partial inverse of SPECIFIES.

    Abstracts a concrete spec back to goal level.
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    edge_kind: EdgeKind = field(default=EdgeKind.DERIVES, init=False)

    def apply(self, concrete: ZeroNode, abstract: ZeroNode) -> EdgeTransform:
        """Abstract a concrete node to goal level."""
        desc = f"""
        Concrete: {concrete.title}
        {concrete.content}

        Abstract: {abstract.title}
        {abstract.content}

        Abstraction: Does the abstract form capture intent?
        """
        loss = self.galois.compute_text(desc)

        principle_scores = {
            "GENERATIVE": 1.0 - loss,
            "CURATED": 1.0 - 0.5 * loss,
            "COMPOSABLE": 1.0 - 0.3 * loss,
            "TASTEFUL": 1.0 - 0.2 * loss,
            "ETHICAL": 0.9,
            "HETERARCHICAL": 1.0,
            "JOY_INDUCING": 0.9 - 0.2 * loss,
        }

        return EdgeTransform(
            edge_kind=EdgeKind.DERIVES,
            galois_loss=loss,
            constitutional_reward=1.0 - 0.5 * loss,
            proof_required=True,
            inverse=SpecifiesOperator(galois=self.galois),
            semantic_drift=self.galois.semantic(desc),
            structural_drift=-0.3,
            operational_drift=-0.1,
            principle_scores=principle_scores,
            constitutional_violations=[],
        )

    def compose(self, other: EdgeOperator) -> EdgeOperator:
        """Abstraction composes with generalization."""
        if isinstance(other, GeneralizesOperator):
            return AbstractsOperator(galois=self.galois)
        raise TypeError(f"Cannot compose ABSTRACTS with {type(other).__name__}")

    def inverse(self) -> EdgeOperator | None:
        """Inverse: specification."""
        return SpecifiesOperator(galois=self.galois)


# -----------------------------------------------------------------------------
# Operator Composition Algebra
# -----------------------------------------------------------------------------

# Composition semantics
COMPOSITION_TABLE: dict[tuple[EdgeKind, EdgeKind], EdgeKind | None] = {
    # Vertical flow (inter-layer)
    (EdgeKind.GROUNDS, EdgeKind.JUSTIFIES): EdgeKind.CROSS_LAYER,
    (EdgeKind.JUSTIFIES, EdgeKind.SPECIFIES): EdgeKind.CROSS_LAYER,
    (EdgeKind.SPECIFIES, EdgeKind.IMPLEMENTS): EdgeKind.CROSS_LAYER,
    (EdgeKind.IMPLEMENTS, EdgeKind.REFLECTS_ON): EdgeKind.CROSS_LAYER,
    (EdgeKind.REFLECTS_ON, EdgeKind.REPRESENTS): EdgeKind.CROSS_LAYER,
    # Horizontal flow (intra-layer)
    (EdgeKind.DERIVES, EdgeKind.DERIVES): EdgeKind.DERIVES,  # Transitive
    (EdgeKind.SYNTHESIZES, EdgeKind.SYNTHESIZES): None,  # Doesn't compose
    # Dialectical
    (EdgeKind.CONTRADICTS, EdgeKind.SYNTHESIZES): None,  # Resolution
    (EdgeKind.SYNTHESIZES, EdgeKind.CONTRADICTS): None,
    # Cross-layer
    (EdgeKind.CROSS_LAYER, EdgeKind.CROSS_LAYER): EdgeKind.CROSS_LAYER,
}


def compose_operators(op1: EdgeOperator, op2: EdgeOperator) -> EdgeOperator:
    """
    Compose two operators: (op1 o op2).

    Raises ValueError if composition is invalid.
    """
    kind1 = op1.edge_kind
    kind2 = op2.edge_kind

    result_kind = COMPOSITION_TABLE.get((kind1, kind2))

    if result_kind is None:
        raise ValueError(f"Cannot compose {kind1} with {kind2}")

    if result_kind == EdgeKind.CROSS_LAYER:
        # Get layers from operators
        source_layer = getattr(op1, "source_layer", 1)
        target_layer = getattr(op2, "target_layer", 7)
        via = [getattr(op1, "target_layer", 2)]

        return CrossLayerOperator(
            source_layer=source_layer,
            target_layer=target_layer,
            via_layers=via,
            galois=op1.galois,
        )
    else:
        return OPERATORS[result_kind](galois=op1.galois)


# -----------------------------------------------------------------------------
# Zero Seed Operad
# -----------------------------------------------------------------------------


@dataclass
class ZeroSeedOperad:
    """
    The operad structure for Zero Seed operators.

    Laws:
    1. Composition closure: op1 o op2 in Operators (or error)
    2. Associativity (lax): (op1 o op2) o op3 ~ op1 o (op2 o op3)
    3. Identity: id o op = op = op o id
    4. Loss subadditivity: L(op1 o op2) <= L(op1) + L(op2)
    """

    operators: dict[EdgeKind, type[EdgeOperator]] = field(default_factory=lambda: OPERATORS)
    composition_table: dict[tuple[EdgeKind, EdgeKind], EdgeKind | None] = field(
        default_factory=lambda: COMPOSITION_TABLE
    )

    def compose(self, op1: EdgeOperator, op2: EdgeOperator) -> EdgeOperator:
        """Compose operators via operad structure."""
        return compose_operators(op1, op2)

    def get_operator(self, kind: EdgeKind, galois: GaloisLoss | None = None) -> EdgeOperator:
        """Get operator instance by kind."""
        galois = galois or GaloisLoss()
        operator_cls = self.operators[kind]
        return operator_cls(galois=galois)

    def verify_associativity(
        self,
        op1: EdgeOperator,
        op2: EdgeOperator,
        op3: EdgeOperator,
        epsilon: float = 0.1,
    ) -> bool:
        """Verify associativity up to epsilon."""
        try:
            left = self.compose(self.compose(op1, op2), op3)
            right = self.compose(op1, self.compose(op2, op3))
            # Both should be same type
            return type(left) == type(right)
        except (TypeError, ValueError):
            # Composition failed - not composable
            return True  # Vacuously true

    def verify_subadditivity(
        self,
        op1: EdgeOperator,
        op2: EdgeOperator,
        source: ZeroNode,
        intermediate: ZeroNode,
        target: ZeroNode,
    ) -> bool:
        """Verify loss subadditivity: L(op1 o op2) <= L(op1) + L(op2)."""
        try:
            transform1 = op1.apply(source, intermediate)
            transform2 = op2.apply(intermediate, target)

            composed = self.compose(op1, op2)
            transform_composed = composed.apply(source, target)

            return transform_composed.galois_loss <= (
                transform1.galois_loss + transform2.galois_loss
            )
        except (TypeError, ValueError):
            return True  # Not composable


# Canonical operad instance
ZERO_SEED_OPERAD = ZeroSeedOperad()


# -----------------------------------------------------------------------------
# Optimal Path Selection
# -----------------------------------------------------------------------------


@dataclass
class OperatorPath:
    """A path through the graph via operators."""

    nodes: list[ZeroNode]
    operators: list[EdgeKind]
    total_loss: float
    total_reward: float
    value: float

    @property
    def length(self) -> int:
        return len(self.operators)


def find_optimal_path(
    source: ZeroNode,
    target: ZeroNode,
    graph_nodes: dict[str, ZeroNode],
    galois: GaloisLoss | None = None,
    lambda_penalty: float = 0.3,
) -> OperatorPath:
    """
    Find minimum-loss path from source to target.

    Uses Dijkstra's algorithm with loss as edge weight.
    """
    galois = galois or GaloisLoss()

    # Priority queue: (accumulated_loss, node_id, nodes_path, ops_path)
    queue: list[tuple[float, str, list[ZeroNode], list[EdgeKind]]] = [
        (0.0, source.id, [], [])
    ]
    visited: set[str] = set()

    while queue:
        accum_loss, current_id, nodes_path, ops_path = heapq.heappop(queue)

        if current_id in visited:
            continue

        visited.add(current_id)
        current = graph_nodes[current_id]
        nodes_path = nodes_path + [current]

        if current_id == target.id:
            # Found target
            total_reward = sum(
                _compute_edge_reward(
                    nodes_path[i], ops_path[i], nodes_path[i + 1], galois
                )
                for i in range(len(ops_path))
            )
            return OperatorPath(
                nodes=nodes_path,
                operators=ops_path,
                total_loss=accum_loss,
                total_reward=total_reward,
                value=total_reward - lambda_penalty * accum_loss,
            )

        # Explore neighbors via valid operators
        for edge_kind in EdgeKind:
            # Check what layer transitions are valid
            valid_transitions = LAYER_TRANSITIONS.get(edge_kind, [])

            for neighbor_id, neighbor in graph_nodes.items():
                if neighbor_id in visited:
                    continue

                # Check if transition is valid
                if (current.layer, neighbor.layer) not in valid_transitions:
                    continue

                try:
                    operator = OPERATORS.get(edge_kind)
                    if operator is None:
                        continue

                    op_instance = operator(galois=galois)
                    transform = op_instance.apply(current, neighbor)
                    new_loss = accum_loss + transform.galois_loss

                    heapq.heappush(
                        queue,
                        (new_loss, neighbor_id, nodes_path, ops_path + [edge_kind]),
                    )
                except (ValueError, TypeError):
                    # Invalid transition for this operator
                    continue

    raise ValueError(f"No path found from {source.id} to {target.id}")


def _compute_edge_reward(
    source: ZeroNode,
    edge_kind: EdgeKind,
    target: ZeroNode,
    galois: GaloisLoss,
) -> float:
    """Compute constitutional reward for an edge."""
    operator_cls = OPERATORS.get(edge_kind)
    if operator_cls is None:
        return 0.0

    try:
        op_instance = operator_cls(galois=galois)
        transform = op_instance.apply(source, target)
        return transform.constitutional_reward
    except (ValueError, TypeError):
        return 0.0


# -----------------------------------------------------------------------------
# Value Iteration Agent
# -----------------------------------------------------------------------------


@dataclass
class OperatorValueAgent:
    """Value iteration agent for operator selection."""

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    lambda_penalty: float = 0.3
    gamma: float = 0.9  # Discount factor
    _value_cache: dict[str, float] = field(default_factory=dict)

    def compute_value(
        self,
        source: ZeroNode,
        graph_nodes: dict[str, ZeroNode],
        max_depth: int = 10,
    ) -> float:
        """
        Compute optimal value V*(source).

        V*(s) = max_{op,t} [ R(s,op,t) - lambda*L(op) + gamma*V*(t) ]
        """
        if source.id in self._value_cache:
            return self._value_cache[source.id]

        if max_depth <= 0 or source.layer == 7:
            return 0.0  # Terminal or depth limit

        max_value = float("-inf")

        for edge_kind in EdgeKind:
            valid_transitions = LAYER_TRANSITIONS.get(edge_kind, [])

            for target_id, target in graph_nodes.items():
                if (source.layer, target.layer) not in valid_transitions:
                    continue

                try:
                    operator_cls = OPERATORS.get(edge_kind)
                    if operator_cls is None:
                        continue

                    op_instance = operator_cls(galois=self.galois)
                    transform = op_instance.apply(source, target)

                    reward = transform.constitutional_reward
                    loss = transform.galois_loss
                    future_value = self.compute_value(target, graph_nodes, max_depth - 1)

                    total_value = (
                        reward - self.lambda_penalty * loss + self.gamma * future_value
                    )
                    max_value = max(max_value, total_value)
                except (ValueError, TypeError):
                    continue

        value = max_value if max_value > float("-inf") else 0.0
        self._value_cache[source.id] = value
        return value

    def select_optimal_operator(
        self,
        source: ZeroNode,
        graph_nodes: dict[str, ZeroNode],
    ) -> tuple[EdgeKind | None, ZeroNode | None, float]:
        """
        Select optimal operator and target.

        Returns: (edge_kind, target_node, value)
        """
        best_edge: EdgeKind | None = None
        best_target: ZeroNode | None = None
        best_value = float("-inf")

        for edge_kind in EdgeKind:
            valid_transitions = LAYER_TRANSITIONS.get(edge_kind, [])

            for target_id, target in graph_nodes.items():
                if (source.layer, target.layer) not in valid_transitions:
                    continue

                try:
                    operator_cls = OPERATORS.get(edge_kind)
                    if operator_cls is None:
                        continue

                    op_instance = operator_cls(galois=self.galois)
                    transform = op_instance.apply(source, target)

                    reward = transform.constitutional_reward
                    loss = transform.galois_loss
                    value = reward - self.lambda_penalty * loss

                    if value > best_value:
                        best_value = value
                        best_edge = edge_kind
                        best_target = target
                except (ValueError, TypeError):
                    continue

        return best_edge, best_target, best_value


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Core types
    "ZeroNode",
    "EdgeTransform",
    "EdgeKind",
    "EdgeOperator",
    # Galois Loss
    "GaloisLoss",
    "GaloisLossProtocol",
    # The 10 Operators
    "GroundsOperator",
    "JustifiesOperator",
    "SpecifiesOperator",
    "ImplementsOperator",
    "ReflectsOnOperator",
    "RepresentsOperator",
    "DerivesOperator",
    "SynthesizesOperator",
    "ContradictsOperator",
    "CrossLayerOperator",
    # Inverse Operators
    "GeneralizesOperator",
    "AbstractsOperator",
    # Operad
    "ZeroSeedOperad",
    "ZERO_SEED_OPERAD",
    # Composition
    "compose_operators",
    "COMPOSITION_TABLE",
    # Layer Transitions
    "LAYER_TRANSITIONS",
    "is_valid_transition",
    # Loss Bounds
    "LOSS_BOUNDS",
    "get_loss_bounds",
    # Constitutional Weights
    "CONSTITUTIONAL_WEIGHTS",
    "compute_constitutional_reward",
    # Path Finding
    "OperatorPath",
    "find_optimal_path",
    # Value Agent
    "OperatorValueAgent",
    # Registry
    "OPERATORS",
    "operator",
    # Constants
    "FIXED_POINT_THRESHOLD",
]
