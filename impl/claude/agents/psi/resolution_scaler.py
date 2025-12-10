"""
Psi-gent ResolutionScaler: The Z-axis of the 4-axis tensor.

Controls abstraction altitude using Model of Hierarchical Complexity (MHC).

High MHC = blur details to find structural isomorphisms.
Low MHC = sharpen to ground abstractions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .types import MHCLevel, Novel, AxisType, ValidationResult, StabilityStatus


# =============================================================================
# Complexity Metrics
# =============================================================================


@dataclass(frozen=True)
class ComplexityMetrics:
    """
    Metrics describing problem complexity.

    Used to determine appropriate MHC level.
    """

    # Structural complexity
    num_entities: int = 1
    num_relationships: int = 0
    nesting_depth: int = 1

    # Semantic complexity
    domain_specificity: float = 0.5  # 0 = generic, 1 = highly specialized
    abstraction_level: float = 0.5  # 0 = concrete, 1 = abstract

    # Entropy
    entropy: float = 0.5

    # Additional metrics expected by tests
    description_length: int = 0  # Length of problem description
    raw_complexity: float = 0.5  # Raw complexity before normalization

    @property
    def overall_complexity(self) -> float:
        """Calculate overall complexity score."""
        structural = min(1.0, (self.num_entities + self.num_relationships) / 20.0)
        nesting = min(1.0, self.nesting_depth / 5.0)
        # Weight abstraction_level heavily as it's the primary indicator of conceptual complexity
        return (
            structural * 0.15
            + nesting * 0.15
            + self.domain_specificity * 0.2
            + self.abstraction_level * 0.5
        )

    @property
    def mhc_level(self) -> MHCLevel:
        """Get the MHC level (alias for suggested_mhc)."""
        return self.suggested_mhc

    @property
    def suggested_mhc(self) -> MHCLevel:
        """Suggest appropriate MHC level based on complexity."""
        complexity = self.overall_complexity

        # Map complexity to MHC levels (lower complexity = lower MHC)
        if complexity < 0.2:
            return MHCLevel.NOMINAL  # Level 4 - simple categories
        elif complexity < 0.4:
            return MHCLevel.SENTENTIAL  # Level 5 - propositions
        elif complexity < 0.6:
            return MHCLevel.CONCRETE  # Level 8 - concrete operations
        elif complexity < 0.8:
            return MHCLevel.FORMAL  # Level 10 - formal systems
        else:
            return MHCLevel.METASYSTEMATIC  # Level 12 - meta-systems


# =============================================================================
# Resolution Scaler
# =============================================================================


@dataclass
class ResolutionScaler:
    """
    The Z-axis controller: manages abstraction altitude.

    Responsibilities:
    1. Analyze problem complexity
    2. Determine appropriate MHC level
    3. Abstract (blur) or concretize (sharpen) problems
    4. Validate resolution matches tractability
    """

    # Configuration
    tractability_threshold: float = 0.7
    min_level: MHCLevel = MHCLevel.CONCRETE
    max_level: MHCLevel = MHCLevel.METASYSTEMATIC

    def measure_complexity(self, problem: Novel) -> ComplexityMetrics:
        """
        Measure the complexity of a novel problem.
        """
        # Count entities (words as proxy)
        words = problem.description.split()
        num_entities = len(set(words)) // 5 + 1

        # Count relationships (connective words as proxy)
        connectives = {"and", "or", "but", "because", "therefore", "if", "then", "when"}
        num_relationships = sum(1 for w in words if w.lower() in connectives)

        # Estimate nesting from context depth
        nesting_depth = self._estimate_nesting(problem.context)

        # Domain specificity from constraints
        domain_specificity = min(1.0, len(problem.constraints) * 0.2)

        # Description length
        description_length = len(problem.description)

        # Raw complexity calculation
        raw_complexity = (
            num_entities / 10 + num_relationships / 5 + nesting_depth / 3
        ) / 3
        raw_complexity = min(1.0, max(0.0, raw_complexity))

        return ComplexityMetrics(
            num_entities=num_entities,
            num_relationships=num_relationships,
            nesting_depth=nesting_depth,
            domain_specificity=domain_specificity,
            abstraction_level=problem.complexity,
            entropy=problem.entropy,
            description_length=description_length,
            raw_complexity=raw_complexity,
        )

    def optimize_resolution(
        self, problem: Novel, target_level: MHCLevel | None = None
    ) -> Novel:
        """
        Optimize problem resolution toward a target MHC level.

        If target_level is provided, adjust problem toward that level.
        Otherwise, determine optimal level automatically.
        """
        metrics = self.measure_complexity(problem)
        current_level = metrics.suggested_mhc

        if target_level is None:
            # Auto-determine target
            complexity = metrics.overall_complexity
            if complexity > self.tractability_threshold:
                target_level = self._abstract_level(current_level)
            elif problem.entropy > 0.7:
                target_level = self._concretize_level(current_level)
            else:
                return problem  # Already optimal

        # Apply abstraction or concretization
        if target_level.value > current_level.value:
            return self._abstract_to_level(problem, target_level)
        elif target_level.value < current_level.value:
            return self._concretize_to_level(problem, target_level)
        else:
            return problem

    def get_optimal_level(self, problem: Novel) -> MHCLevel:
        """
        Determine optimal MHC level for a problem.

        If complexity > tractability threshold: abstract (increase MHC)
        If problem is vague: concretize (decrease MHC)
        """
        metrics = self.measure_complexity(problem)
        complexity = metrics.overall_complexity

        if complexity > self.tractability_threshold:
            return self._abstract_level(metrics.suggested_mhc)
        elif problem.entropy > 0.7:
            return self._concretize_level(metrics.suggested_mhc)
        else:
            return metrics.suggested_mhc

    def abstract(self, problem: Novel, target_level: MHCLevel | None = None) -> Novel:
        """
        Abstract a problem to a higher MHC level.

        Blurs details to find structural isomorphisms.
        """
        current_level = self.measure_complexity(problem).suggested_mhc

        if target_level is None:
            target_level = self._abstract_level(current_level)

        return self._abstract_to_level(problem, target_level)

    def _abstract_to_level(self, problem: Novel, target_level: MHCLevel) -> Novel:
        """Internal: abstract problem to specific level."""
        current_level = self.measure_complexity(problem).suggested_mhc

        if target_level.value <= current_level.value:
            return problem  # Already at or above target

        # Create abstracted description
        abstracted_desc = self._abstract_description(problem.description, target_level)

        # Simplify context
        abstracted_context = self._abstract_context(problem.context, target_level)

        # Generalize constraints
        abstracted_constraints = self._abstract_constraints(
            problem.constraints, target_level
        )

        return Novel(
            problem_id=f"{problem.problem_id}@{target_level.name}",
            timestamp=problem.timestamp,
            description=abstracted_desc,
            domain=problem.domain,
            complexity=problem.complexity,
            entropy=max(0.0, problem.entropy - 0.1),  # Abstraction reduces entropy
            embedding=problem.embedding,
            context=abstracted_context,
            constraints=abstracted_constraints,
        )

    def concretize(self, problem: Novel, target_level: MHCLevel | None = None) -> Novel:
        """
        Concretize a problem to a lower MHC level.

        Sharpens details to ground abstractions.
        """
        current_level = self.measure_complexity(problem).suggested_mhc

        if target_level is None:
            target_level = self._concretize_level(current_level)

        return self._concretize_to_level(problem, target_level)

    def _concretize_to_level(self, problem: Novel, target_level: MHCLevel) -> Novel:
        """Internal: concretize problem to specific level."""
        current_level = self.measure_complexity(problem).suggested_mhc

        if target_level.value >= current_level.value:
            return problem  # Already at or below target

        # Create concretized description
        concretized_desc = self._concretize_description(
            problem.description, target_level
        )

        # Expand context
        concretized_context = self._concretize_context(problem.context, target_level)

        return Novel(
            problem_id=f"{problem.problem_id}@{target_level.name}",
            timestamp=problem.timestamp,
            description=concretized_desc,
            domain=problem.domain,
            complexity=problem.complexity,
            entropy=min(1.0, problem.entropy + 0.1),  # Concretization may add details
            embedding=problem.embedding,
            context=concretized_context,
            constraints=problem.constraints,
        )

    def validate(
        self,
        projection_or_problem: Novel | Any,
        metaphor_tractability: float | None = None,
    ) -> ValidationResult:
        """
        Validate that problem resolution matches metaphor tractability.

        Can accept either a Novel problem or a Projection (which contains source problem and target metaphor).
        Returns a ValidationResult for the Z-axis.
        """
        # Handle Projection or Novel input
        from .types import Projection

        if isinstance(projection_or_problem, Projection):
            problem = projection_or_problem.source
            metaphor_tractability = projection_or_problem.target.tractability
        else:
            problem = projection_or_problem
            if metaphor_tractability is None:
                metaphor_tractability = 0.7  # Default tractability

        metrics = self.measure_complexity(problem)
        complexity = metrics.overall_complexity

        # Check if complexity is within tractable range
        if complexity > metaphor_tractability:
            return ValidationResult(
                axis=AxisType.Z_MHC,
                status=StabilityStatus.UNSTABLE,
                score=metaphor_tractability / complexity if complexity > 0 else 0,
                message=f"Problem complexity ({complexity:.2f}) exceeds metaphor tractability ({metaphor_tractability:.2f})",
                details={"suggested_action": "abstract to higher MHC level"},
            )
        elif complexity < metaphor_tractability * 0.3:
            return ValidationResult(
                axis=AxisType.Z_MHC,
                status=StabilityStatus.FRAGILE,
                score=0.7,
                message="Problem may be over-simplified for this metaphor",
                details={"suggested_action": "consider more specific metaphor"},
            )
        else:
            return ValidationResult(
                axis=AxisType.Z_MHC,
                status=StabilityStatus.STABLE,
                score=1.0 - abs(complexity - metaphor_tractability * 0.7),
                message="Resolution matches metaphor tractability",
            )

    # =========================================================================
    # Private Implementation
    # =========================================================================

    def _estimate_nesting(self, context: dict[str, Any]) -> int:
        """Estimate nesting depth of context."""

        def depth(obj: Any, current: int = 0) -> int:
            if isinstance(obj, dict):
                if not obj:
                    return current
                return max(depth(v, current + 1) for v in obj.values())
            elif isinstance(obj, (list, tuple)):
                if not obj:
                    return current
                return max(depth(v, current + 1) for v in obj)
            else:
                return current

        return depth(context)

    def _abstract_level(self, current: MHCLevel) -> MHCLevel:
        """Get next higher MHC level (capped at max)."""
        next_value = min(current.value + 2, self.max_level.value)
        return MHCLevel(next_value)

    def _concretize_level(self, current: MHCLevel) -> MHCLevel:
        """Get next lower MHC level (floored at min)."""
        prev_value = max(current.value - 2, self.min_level.value)
        return MHCLevel(prev_value)

    def _abstract_description(self, description: str, target_level: MHCLevel) -> str:
        """Abstract a description to target MHC level."""
        # Simple abstraction: remove specific details
        abstracted = description

        # Remove numbers (specific quantities)
        import re

        abstracted = re.sub(r"\b\d+\b", "N", abstracted)

        # Replace specific nouns with category terms
        if target_level.is_formal or target_level.is_paradigmatic:
            abstracted = f"[Abstract: {target_level.name}] {abstracted}"

        return abstracted

    def _abstract_context(
        self, context: dict[str, Any], target_level: MHCLevel
    ) -> dict[str, Any]:
        """Abstract context to target MHC level."""
        if target_level.is_paradigmatic:
            # Keep only top-level keys
            return {k: "..." for k in context}
        elif target_level.is_formal:
            # Flatten nested structures
            return {k: str(v)[:50] for k, v in context.items()}
        else:
            return context

    def _abstract_constraints(
        self, constraints: tuple[str, ...], target_level: MHCLevel
    ) -> tuple[str, ...]:
        """Abstract constraints to target MHC level."""
        if target_level.is_paradigmatic:
            # Generalize constraints
            return tuple(f"general: {c}" for c in constraints[:2])
        else:
            return constraints

    def _concretize_description(self, description: str, target_level: MHCLevel) -> str:
        """Concretize a description to target MHC level."""
        # Simple concretization: add specificity markers
        if target_level.is_concrete:
            return f"[Specific: {target_level.name}] {description}"
        return description

    def _concretize_context(
        self, context: dict[str, Any], target_level: MHCLevel
    ) -> dict[str, Any]:
        """Concretize context to target MHC level."""
        # Add placeholder specifics
        result = dict(context)
        if target_level.is_concrete:
            result["_concretized"] = True
        return result
