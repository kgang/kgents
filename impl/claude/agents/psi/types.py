"""
Psi-gent v3.0 Types.

Minimal, measurable, meaningful.

Design Philosophy:
1. Observable: Every field can be measured or computed
2. Useful: No fields that exist "for completeness"
3. Composable: Types compose without special cases

TODO: Create metaphor collection + cultivation system
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, ClassVar

# =============================================================================
# Core Input/Output Types
# =============================================================================


@dataclass(frozen=True)
class Problem:
    """A novel problem seeking metaphorical illumination."""

    id: str
    description: str
    domain: str
    constraints: tuple[str, ...] = ()
    context: dict[str, Any] = field(default_factory=dict)
    embedding: tuple[float, ...] | None = None

    @property
    def complexity(self) -> float:
        """Heuristic complexity estimate (0.0 to 1.0)."""
        desc_factor = min(1.0, len(self.description) / 1000)
        constraint_factor = min(1.0, len(self.constraints) / 10)
        return (desc_factor + constraint_factor) / 2

    def with_embedding(self, embedding: tuple[float, ...]) -> Problem:
        """Return a new Problem with the given embedding."""
        return Problem(
            id=self.id,
            description=self.description,
            domain=self.domain,
            constraints=self.constraints,
            context=self.context,
            embedding=embedding,
        )


@dataclass(frozen=True)
class Operation:
    """An executable action within a metaphor framework."""

    name: str
    description: str
    signature: str = "entity -> entity"
    preconditions: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class Example:
    """A concrete instance showing the metaphor in use."""

    situation: str
    application: str
    outcome: str


@dataclass(frozen=True)
class Metaphor:
    """A structured framework for reasoning about problems."""

    id: str
    name: str
    domain: str
    description: str
    operations: tuple[Operation, ...]
    examples: tuple[Example, ...] = ()
    embedding: tuple[float, ...] | None = None

    @property
    def tractability(self) -> float:
        """How powerful is this metaphor for reasoning? (0.0 to 1.0)"""
        return min(1.0, len(self.operations) / 5)

    def with_embedding(self, embedding: tuple[float, ...]) -> Metaphor:
        """Return a new Metaphor with the given embedding."""
        return Metaphor(
            id=self.id,
            name=self.name,
            domain=self.domain,
            description=self.description,
            operations=self.operations,
            examples=self.examples,
            embedding=embedding,
        )


# =============================================================================
# Projection Types
# =============================================================================


@dataclass(frozen=True)
class ConceptMapping:
    """A mapping between a problem concept and a metaphor concept."""

    source: str
    target: str
    confidence: float
    rationale: str = ""


@dataclass(frozen=True)
class Projection:
    """A problem mapped into metaphor terms."""

    problem: Problem
    metaphor: Metaphor
    mappings: tuple[ConceptMapping, ...]
    abstraction: float  # 0.0 (concrete) to 1.0 (abstract)
    gaps: tuple[str, ...] = ()
    confidence: float = 0.5
    mapped_description: str = ""

    @property
    def coverage(self) -> float:
        """What fraction of the problem was mapped? (0.0 to 1.0)"""
        if not self.mappings:
            return 0.0
        total_concepts = len(self.mappings) + len(self.gaps)
        return len(self.mappings) / total_concepts if total_concepts > 0 else 0.0


# =============================================================================
# Challenge Types
# =============================================================================


@dataclass(frozen=True)
class ChallengeResult:
    """Result of stress-testing a projection."""

    survives: bool
    challenges_passed: int
    challenges_total: int
    counterexamples: tuple[str, ...] = ()
    caveats: tuple[str, ...] = ()

    @property
    def robustness(self) -> float:
        """How robust is this projection? (0.0 to 1.0)"""
        if self.challenges_total == 0:
            return 0.5  # No testing = uncertain
        return self.challenges_passed / self.challenges_total


# =============================================================================
# Solution Types
# =============================================================================


@dataclass(frozen=True)
class MetaphorSolution:
    """Solution derived within metaphor space."""

    projection: Projection
    reasoning: str
    operations_applied: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True)
class Distortion:
    """Measures information loss through transformation."""

    structural_loss: float  # Unmapped concepts / total (0.0 to 1.0)
    round_trip_error: float  # How different is Phi^-1(Phi(P)) from P? (0.0 to 1.0)
    prediction_failures: int  # Implications that didn't hold

    # Weights for combining (can be tuned)
    STRUCTURAL_WEIGHT: ClassVar[float] = 0.3
    ROUND_TRIP_WEIGHT: ClassVar[float] = 0.4
    PREDICTION_WEIGHT: ClassVar[float] = 0.3
    PREDICTION_PENALTY: ClassVar[float] = 0.1  # Per failure

    @property
    def total(self) -> float:
        """Weighted distortion score (0.0 to ~1.0)."""
        prediction_score = min(1.0, self.prediction_failures * self.PREDICTION_PENALTY)
        return (
            self.structural_loss * self.STRUCTURAL_WEIGHT
            + self.round_trip_error * self.ROUND_TRIP_WEIGHT
            + prediction_score * self.PREDICTION_WEIGHT
        )

    @property
    def acceptable(self) -> bool:
        """Is distortion low enough to trust the solution?"""
        return self.total < 0.5


@dataclass(frozen=True)
class Solution:
    """Complete solution with translation and quality metrics."""

    problem: Problem
    metaphor_solution: MetaphorSolution
    translated_answer: str
    specific_actions: tuple[str, ...]
    distortion: Distortion
    trace_id: str | None = None

    @property
    def success(self) -> bool:
        """Is this solution good enough?"""
        return self.distortion.acceptable


# =============================================================================
# Search State Types
# =============================================================================


@dataclass
class SearchState:
    """Mutable state for the search loop."""

    problem: Problem
    candidates_tried: list[str] = field(default_factory=list)  # Metaphor IDs
    projections_attempted: list[Projection] = field(default_factory=list)
    best_solution: Solution | None = None
    best_distortion: float = float("inf")
    backtrack_reasons: list[str] = field(default_factory=list)
    iteration: int = 0

    def record_attempt(
        self, metaphor_id: str, projection: Projection | None, result: str
    ) -> None:
        """Record an attempt for learning."""
        self.candidates_tried.append(metaphor_id)
        if projection:
            self.projections_attempted.append(projection)
        self.iteration += 1

    def record_backtrack(self, stage: str, reason: str) -> None:
        """Record a backtrack event."""
        self.backtrack_reasons.append(f"{stage}: {reason}")
        self.iteration += 1

    def update_best(self, solution: Solution) -> None:
        """Update best solution if this one is better."""
        if solution.distortion.total < self.best_distortion:
            self.best_solution = solution
            self.best_distortion = solution.distortion.total


@dataclass(frozen=True)
class EngineConfig:
    """Configuration for the Morphic Engine."""

    max_candidates: int = 5
    max_iterations: int = 10
    min_abstraction: float = 0.0
    max_abstraction: float = 1.0
    abstraction_step: float = 0.2
    distortion_threshold: float = 0.5
    enable_learning: bool = True
    enable_tracing: bool = True


# =============================================================================
# Learning Types
# =============================================================================


class Outcome(Enum):
    """Possible outcomes for learning."""

    SUCCESS = "success"
    PARTIAL = "partial"
    CHALLENGE_FAILED = "challenge_failed"
    PROJECTION_FAILED = "projection_failed"
    SOLVE_FAILED = "solve_failed"
    VERIFY_FAILED = "verify_failed"


@dataclass(frozen=True)
class ProblemFeatures:
    """Features extracted from a problem for learning."""

    domain: str
    domain_cluster: int
    complexity: float
    constraint_count: int
    description_length: int
    has_embedding: bool
    embedding_cluster: int | None = None


@dataclass(frozen=True)
class Feedback:
    """Feedback for the learning system."""

    problem_id: str
    problem_features: ProblemFeatures
    metaphor_id: str
    abstraction: float
    outcome: Outcome
    distortion: float | None = None
    time_to_solve_ms: int = 0


# =============================================================================
# Serialization
# =============================================================================


def to_dict(obj: Any) -> Any:
    """Convert dataclass to dict recursively."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    else:
        return obj


def to_json(obj: Any) -> str:
    """Serialize to JSON."""
    return json.dumps(to_dict(obj), indent=2)


# =============================================================================
# Type Invariants (for testing)
# =============================================================================


def validate_distortion(d: Distortion) -> list[str]:
    """Validate distortion invariants."""
    errors = []
    if not 0.0 <= d.structural_loss <= 1.0:
        errors.append(f"structural_loss out of bounds: {d.structural_loss}")
    if not 0.0 <= d.round_trip_error <= 1.0:
        errors.append(f"round_trip_error out of bounds: {d.round_trip_error}")
    if d.prediction_failures < 0:
        errors.append(f"prediction_failures negative: {d.prediction_failures}")
    return errors


def validate_projection(p: Projection) -> list[str]:
    """Validate projection invariants."""
    errors = []
    if not 0.0 <= p.abstraction <= 1.0:
        errors.append(f"abstraction out of bounds: {p.abstraction}")
    if not 0.0 <= p.confidence <= 1.0:
        errors.append(f"confidence out of bounds: {p.confidence}")
    for mapping in p.mappings:
        if not 0.0 <= mapping.confidence <= 1.0:
            errors.append(f"mapping confidence out of bounds: {mapping.confidence}")
    return errors


def validate_metaphor(m: Metaphor) -> list[str]:
    """Validate metaphor invariants."""
    errors = []
    if not m.operations and m.id != "null_metaphor":
        errors.append("metaphor has no operations")
    if len(m.description) < 10:
        errors.append("description too short")
    for op in m.operations:
        if not op.effects:
            errors.append(f"operation '{op.name}' has no effects")
    return errors
