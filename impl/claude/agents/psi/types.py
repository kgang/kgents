"""
Psi-gent Core Types: The Morphic Engine primitives.

The Universal Translator of Semantic Topologies.
Functor between the unknown (Novelty) and the known (Archetype).

Philosophy:
    To understand the mountain, become the river that flows around it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

# Type variables for functor generics
Source = TypeVar("Source")
Target = TypeVar("Target")
A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# MHC Levels (Model of Hierarchical Complexity)
# =============================================================================


class MHCLevel(Enum):
    """
    Model of Hierarchical Complexity levels.

    High MHC = blur details to find structural isomorphisms.
    Low MHC = sharpen to ground abstractions.
    """

    # Concrete levels (low abstraction)
    SENSORIMOTOR = 1  # Direct perception
    CIRCULAR = 2  # Simple loops
    SENSORIMOTOR_NOMINAL = 3  # Named actions
    NOMINAL = 4  # Categories

    # Abstract levels (medium abstraction)
    SENTENTIAL = 5  # Propositions
    PREOPERATIONAL = 6  # Simple relations
    PRIMARY = 7  # Single abstractions
    CONCRETE = 8  # Concrete operations

    # Formal levels (high abstraction)
    ABSTRACT = 9  # Abstract operations
    FORMAL = 10  # Formal systems
    SYSTEMATIC = 11  # System of systems
    METASYSTEMATIC = 12  # Meta-systems

    # Paradigmatic levels (very high abstraction)
    PARADIGMATIC = 13  # Paradigm comparison
    CROSS_PARADIGMATIC = 14  # Cross-paradigm synthesis
    META_CROSS_PARADIGMATIC = 15  # Meta-synthesis

    @property
    def is_concrete(self) -> bool:
        return self.value <= 4

    @property
    def is_abstract(self) -> bool:
        return 5 <= self.value <= 8

    @property
    def is_formal(self) -> bool:
        return 9 <= self.value <= 12

    @property
    def is_paradigmatic(self) -> bool:
        return self.value >= 13


# =============================================================================
# Novel Problem Space
# =============================================================================


@dataclass(frozen=True)
class Novel:
    """
    A novel problem in the high-entropy Problem Space.

    This is the input to the Psi-gent: an unstructured, unfamiliar problem
    that needs to be projected into a familiar metaphor space.
    """

    # Identity
    problem_id: str

    # The problem description
    description: str
    domain: str  # "software", "organization", "biology", etc.

    # Complexity metrics (with defaults)
    complexity: float = 0.5  # 0.0 = trivial, 1.0 = maximally complex
    entropy: float = 0.5  # Structural randomness
    timestamp: datetime = field(default_factory=datetime.now)

    # Embedding for similarity search
    embedding: tuple[float, ...] | None = None

    # Context
    context: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()

    def with_embedding(self, embedding: list[float]) -> Novel:
        """Create a new Novel with the given embedding."""
        return Novel(
            problem_id=self.problem_id,
            timestamp=self.timestamp,
            description=self.description,
            domain=self.domain,
            complexity=self.complexity,
            entropy=self.entropy,
            embedding=tuple(embedding),
            context=self.context,
            constraints=self.constraints,
        )


# =============================================================================
# Metaphor Space
# =============================================================================


@dataclass(frozen=True)
class MetaphorOperation:
    """
    An operation available within a metaphor space.

    Example: In MilitaryStrategy, operations might be ["flank", "siege", "retreat"].
    """

    name: str
    description: str
    signature: str = "Any -> Any"  # Type signature like "Position -> Position"
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    postconditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Metaphor:
    """
    A familiar metaphor space for problem solving.

    The Metaphor Space is low-entropy, structured, and tractable.
    Problems are projected here, solved, then reified back.
    """

    # Identity
    metaphor_id: str
    name: str  # "MilitaryStrategy", "Thermodynamics", "BiologicalSystem"
    domain: str  # Category of metaphor

    # Description
    description: str

    # Available operations in this space
    operations: tuple[MetaphorOperation, ...] = ()

    # Embedding for similarity matching
    embedding: tuple[float, ...] | None = None

    # Structural properties
    tractability: float = 0.8  # How easy to reason in this space
    generality: float = 0.5  # How broadly applicable

    # Relationships to other metaphors
    related_metaphors: tuple[str, ...] = ()  # IDs of related metaphors

    # Usage tracking
    usage_count: int = 0
    success_rate: float = 0.5

    def with_embedding(self, embedding: list[float]) -> Metaphor:
        """Create a new Metaphor with the given embedding."""
        return Metaphor(
            metaphor_id=self.metaphor_id,
            name=self.name,
            domain=self.domain,
            description=self.description,
            operations=self.operations,
            embedding=tuple(embedding),
            tractability=self.tractability,
            generality=self.generality,
            related_metaphors=self.related_metaphors,
            usage_count=self.usage_count,
            success_rate=self.success_rate,
        )

    def increment_usage(self, success: bool) -> Metaphor:
        """Create a new Metaphor with updated usage stats."""
        new_count = self.usage_count + 1
        # Exponential moving average for success rate
        alpha = 0.1
        new_rate = self.success_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha
        return Metaphor(
            metaphor_id=self.metaphor_id,
            name=self.name,
            domain=self.domain,
            description=self.description,
            operations=self.operations,
            embedding=self.embedding,
            tractability=self.tractability,
            generality=self.generality,
            related_metaphors=self.related_metaphors,
            usage_count=new_count,
            success_rate=new_rate,
        )


# =============================================================================
# Projection and Distortion
# =============================================================================


@dataclass(frozen=True)
class ConceptMapping:
    """A mapping from source concept to target concept."""

    source_concept: str
    target_concept: str
    confidence: float = 0.5
    notes: str = ""


@dataclass(frozen=True)
class Projection:
    """
    The result of projecting a Novel problem into a Metaphor space.

    This is Φ(P) in the spec: the problem expressed in metaphor terms.
    """

    # Source and target
    source: Novel
    target: Metaphor

    # The projected representation
    projected_description: str
    mapped_concepts: dict[str, str]  # source concept -> metaphor concept
    applicable_operations: tuple[str, ...] = ()  # Which operations apply

    # Quality metrics
    confidence: float = 0.5  # How confident in this projection
    coverage: float = 0.5  # What fraction of problem is captured

    # Distortion tracking
    projection_timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Distortion:
    """
    The semantic distortion from a metaphor transformation.

    Δ = |P_input - Φ⁻¹(Φ(P_input))|

    Lower distortion = better metaphor fit.
    """

    # The metric
    delta: float  # 0.0 = lossless, 1.0 = complete information loss

    # Human-readable details
    details: str = ""

    # Breakdown by aspect
    structural_loss: float = 0.0  # Loss of structural information
    semantic_loss: float = 0.0  # Loss of meaning
    contextual_loss: float = 0.0  # Loss of context

    # What was lost
    lost_concepts: tuple[str, ...] = ()
    lost_constraints: tuple[str, ...] = ()

    # What was distorted
    distorted_mappings: dict[str, str] = field(
        default_factory=dict
    )  # original -> distorted

    @property
    def is_acceptable(self) -> bool:
        """Is this distortion within acceptable bounds?"""
        return self.delta < 0.5

    @property
    def is_excellent(self) -> bool:
        """Is this distortion excellent?"""
        return self.delta < 0.2


# =============================================================================
# Solution Types
# =============================================================================


@dataclass(frozen=True)
class MetaphorSolution:
    """
    A solution found within the metaphor space.

    This is Σ(Φ(P)) - the result of solving in the metaphor space,
    before reification back to the original problem space.
    """

    # Context
    projection: Projection
    operations_applied: tuple[str, ...]  # Which metaphor operations were used

    # The solution (in metaphor terms)
    intermediate_results: tuple[str, ...] = ()  # Results from each operation
    final_state: str = ""  # Final state in metaphor terms
    solution_description: str = ""  # Human-readable description
    solution_data: dict[str, Any] = field(default_factory=dict)

    # Quality
    confidence: float = 0.5
    completeness: float = 0.5  # Does it fully address the problem?


@dataclass(frozen=True)
class ReifiedSolution:
    """
    The final solution, reified back to the original problem space.

    This is Φ⁻¹(Σ(Φ(P))) - the complete transformation.
    """

    # Source (required)
    original_problem: Novel
    metaphor_solution: MetaphorSolution

    # The reified solution (required)
    solution_description: str

    # Quality metrics (required)
    distortion: Distortion

    # Optional fields with defaults
    solution_data: dict[str, Any] = field(default_factory=dict)
    overall_quality: float = 0.5

    # Audit trail
    transformation_chain: tuple[str, ...] = ()  # IDs of transformations applied
    reification_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_successful(self) -> bool:
        """Did the transformation produce an acceptable solution?"""
        return self.distortion.is_acceptable and self.overall_quality > 0.5


# =============================================================================
# 4-Axis Tensor Components
# =============================================================================


class AxisType(Enum):
    """The four axes of the Psi-gent tensor."""

    Z_MHC = "z"  # MHC - Abstraction altitude
    X_JUNGIAN = "x"  # Parallax - Shadow rotation
    Y_LACANIAN = "y"  # Topology - Knot integrity
    T_AXIOLOGICAL = "t"  # Cost - Value exchange rates


# Alias for backward compatibility
AxisType.Z_RESOLUTION = AxisType.Z_MHC


@dataclass(frozen=True)
class AxisPosition:
    """Position along a single axis."""

    axis: AxisType
    value: float  # Normalized 0.0 to 1.0
    label: str = ""


@dataclass(frozen=True)
class TensorPosition:
    """
    Position in the 4-axis Psi-gent tensor.

    Instead of a linear pipeline, Psi-gents operate as a coordinate system.
    """

    z_altitude: float  # Resolution (MHC level normalized)
    x_rotation: float  # Jungian parallax
    y_topology: float  # Lacanian topology
    t_axiological: float  # Axiological cost

    # Legacy aliases
    @property
    def z(self) -> float:
        return self.z_altitude

    @property
    def x(self) -> float:
        return self.x_rotation

    @property
    def y(self) -> float:
        return self.y_topology

    @property
    def t(self) -> float:
        return self.t_axiological

    @property
    def overall(self) -> float:
        """Overall position score (average of all axes)."""
        return (
            self.z_altitude + self.x_rotation + self.y_topology + self.t_axiological
        ) / 4

    @classmethod
    def origin(cls) -> TensorPosition:
        """The origin point (default position)."""
        return cls(z_altitude=0.5, x_rotation=0.5, y_topology=0.5, t_axiological=0.5)

    def distance_to(self, other: TensorPosition) -> float:
        """Euclidean distance to another position."""
        return (
            (self.z_altitude - other.z_altitude) ** 2
            + (self.x_rotation - other.x_rotation) ** 2
            + (self.y_topology - other.y_topology) ** 2
            + (self.t_axiological - other.t_axiological) ** 2
        ) ** 0.5


# =============================================================================
# Stability and Validation
# =============================================================================


class StabilityStatus(Enum):
    """Result of stability/validation checks."""

    STABLE = "stable"
    UNSTABLE = "unstable"
    FRAGILE = "fragile"  # Passes but barely
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ValidationResult:
    """Result from an axis validator."""

    axis: AxisType
    status: StabilityStatus
    score: float  # 0.0 = failed, 1.0 = perfect
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status in (StabilityStatus.STABLE, StabilityStatus.FRAGILE)


@dataclass(frozen=True)
class TensorValidation:
    """Combined validation across all axes."""

    # Full API for PsychopompAgent
    position: TensorPosition | None = None
    z_result: ValidationResult | None = None
    x_result: ValidationResult | None = None
    y_result: ValidationResult | None = None
    t_result: ValidationResult | None = None
    overall_status: StabilityStatus = StabilityStatus.UNKNOWN
    overall_confidence: float = 0.0

    # Legacy API
    results: tuple[ValidationResult, ...] = ()
    overall_score: float = 0.0

    def __post_init__(self):
        # If individual results are set, compute the tuple
        if self.z_result or self.x_result or self.y_result or self.t_result:
            results_list = []
            for r in [self.z_result, self.x_result, self.y_result, self.t_result]:
                if r is not None:
                    results_list.append(r)
            object.__setattr__(self, "results", tuple(results_list))
            object.__setattr__(self, "overall_score", self.overall_confidence)

    @classmethod
    def from_results(cls, results: list[ValidationResult]) -> TensorValidation:
        """Create from individual axis results."""
        if not results:
            return cls(
                results=(), overall_status=StabilityStatus.UNKNOWN, overall_score=0.0
            )

        # Overall score is product (all must pass)
        scores = [r.score for r in results]
        overall = 1.0
        for s in scores:
            overall *= s

        # Overall status is worst status
        statuses = [r.status for r in results]
        if StabilityStatus.UNSTABLE in statuses:
            status = StabilityStatus.UNSTABLE
        elif StabilityStatus.FRAGILE in statuses:
            status = StabilityStatus.FRAGILE
        elif all(s == StabilityStatus.STABLE for s in statuses):
            status = StabilityStatus.STABLE
        else:
            status = StabilityStatus.UNKNOWN

        return cls(results=tuple(results), overall_status=status, overall_score=overall)

    @property
    def passed(self) -> bool:
        return self.overall_status in (StabilityStatus.STABLE, StabilityStatus.FRAGILE)


# =============================================================================
# Anti-Patterns
# =============================================================================


class AntiPattern(Enum):
    """
    Known anti-patterns in metaphor transformation.

    These should be detected and avoided.
    """

    PROCRUSTEAN_BED = "procrustean"  # Force problem into ill-fitting metaphor
    MAP_TERRITORY_CONFUSION = "map_territory"  # Believe metaphor IS reality
    RESOLUTION_MISMATCH = "resolution"  # Level 12 problem with Level 9 tools
    SHADOW_BLINDNESS = "shadow"  # Accept Ego solution ignoring Shadow
    VALUE_BLINDNESS = "value"  # Ignore ethical cost of translation


@dataclass(frozen=True)
class AntiPatternDetection:
    """Result of anti-pattern detection."""

    pattern: AntiPattern
    detected: bool
    confidence: float
    evidence: str = ""
    mitigation: str = ""
