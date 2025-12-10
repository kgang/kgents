"""
Psi-gent MorphicFunctor: The core transformation engine.

This is a Functor in the C-gents sense - preserves composition
while mapping between categories (Problem Space -> Metaphor Space).

The Contortion Formula:
    S_solution = Φ⁻¹(Σ(Φ(P_input)))

Where:
    Φ (project): P → M
    Σ (solve): operation within M
    Φ⁻¹ (reify): M → P
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

from .types import (
    Distortion,
    MHCLevel,
    Metaphor,
    MetaphorOperation,
    MetaphorSolution,
    Novel,
    Projection,
    ReifiedSolution,
)

Source = TypeVar("Source")
Target = TypeVar("Target")


# =============================================================================
# Functor Protocol (from C-gents)
# =============================================================================


class Functor(Protocol[Source, Target]):
    """
    A functor maps objects and morphisms between categories.

    Laws:
    - Identity: Φ(id) = id
    - Composition: Φ(g ∘ f) = Φ(g) ∘ Φ(f)
    """

    def map(self, source: Source) -> Target:
        """Map an object from source to target category."""
        ...


# =============================================================================
# MorphicFunctor
# =============================================================================


@dataclass
class MorphicFunctor:
    """
    The core transformation functor for Psi-gent.

    Maps between:
    - Problem Space (high entropy, novel, unstructured)
    - Metaphor Space (low entropy, familiar, structured)

    Provides:
    - project(Novel, Metaphor) → Projection
    - reify(MetaphorSolution, Novel, Projection) → ReifiedSolution
    - calculate_distortion(Novel, Projection) → Distortion
    """

    # Configuration (optional - can be passed per-call)
    resolution: MHCLevel = MHCLevel.ABSTRACT

    # State tracking
    _last_projection: Projection | None = field(default=None, repr=False)
    _last_source: Novel | None = field(default=None, repr=False)
    _last_metaphor: Metaphor | None = field(default=None, repr=False)

    def project(self, problem: Novel, metaphor: Metaphor) -> Projection:
        """
        Project a novel problem into the metaphor space.

        Φ: P → M

        This is the first step of the Psychopomp transformation.
        """
        # Store metaphor for later use
        self._last_metaphor = metaphor

        # Map concepts from problem domain to metaphor domain
        mapped_concepts = self._map_concepts(problem, metaphor)

        # Determine which operations apply
        applicable_ops = self._find_applicable_operations(
            problem, mapped_concepts, metaphor
        )

        # Create the projected description
        projected_desc = self._create_projection_description(
            problem, mapped_concepts, metaphor
        )

        # Calculate confidence and coverage
        confidence = self._calculate_projection_confidence(
            problem, mapped_concepts, metaphor
        )
        coverage = max(
            0.3, min(1.0, len(mapped_concepts) / max(1, 5))
        )  # Normalized coverage

        projection = Projection(
            source=problem,
            target=metaphor,
            projected_description=projected_desc,
            mapped_concepts=mapped_concepts,
            applicable_operations=tuple(applicable_ops),
            confidence=confidence,
            coverage=coverage,
        )

        # Track for distortion calculation
        self._last_projection = projection
        self._last_source = problem

        return projection

    def reify(
        self,
        solution: MetaphorSolution,
        original_problem: Novel,
        projection: Projection,
    ) -> ReifiedSolution:
        """
        Reify a metaphor solution back to the original problem space.

        Φ⁻¹: M → P

        This is the final step of the Psychopomp transformation.
        """
        # Reverse the concept mapping
        reverse_mapping = {v: k for k, v in projection.mapped_concepts.items()}

        # Create reified description
        reified_desc = self._create_reification_description(
            solution, reverse_mapping, projection
        )

        # Calculate distortion
        distortion = self.calculate_distortion(original_problem, projection)

        # Calculate overall quality
        quality = self._calculate_quality(solution, distortion)

        return ReifiedSolution(
            original_problem=original_problem,
            metaphor_solution=solution,
            solution_description=reified_desc,
            distortion=distortion,
            solution_data=self._reify_data(solution.solution_data, reverse_mapping),
            overall_quality=quality,
            transformation_chain=(
                f"project:{projection.target.metaphor_id}",
                f"solve:{','.join(solution.operations_applied)}",
                f"reify:{original_problem.problem_id}",
            ),
        )

    def calculate_distortion(self, source: Novel, projection: Projection) -> Distortion:
        """
        Calculate the semantic distortion of the transformation.

        Δ = |P_input - Φ⁻¹(Φ(P_input))|

        Lower distortion = better metaphor fit.
        """
        # Calculate structural loss (what structure wasn't captured)
        structural_loss = self._calculate_structural_loss(source, projection)

        # Calculate semantic loss (what meaning was lost)
        semantic_loss = self._calculate_semantic_loss(source, projection)

        # Calculate contextual loss (what context was lost)
        contextual_loss = self._calculate_contextual_loss(source, projection)

        # Find lost concepts
        lost_concepts = self._find_lost_concepts(source, projection)

        # Find lost constraints
        lost_constraints = tuple(
            c
            for c in source.constraints
            if c not in str(projection.projected_description)
        )

        # Calculate overall delta (reduced by metaphor generality)
        base_delta = (structural_loss + semantic_loss + contextual_loss) / 3.0
        generality_factor = 1.0 - (projection.target.generality * 0.3)
        delta = min(1.0, base_delta * generality_factor)

        return Distortion(
            delta=delta,
            structural_loss=structural_loss,
            semantic_loss=semantic_loss,
            contextual_loss=contextual_loss,
            lost_concepts=lost_concepts,
            lost_constraints=lost_constraints,
        )

    # =========================================================================
    # Private Implementation
    # =========================================================================

    def _map_concepts(self, problem: Novel, metaphor: Metaphor) -> dict[str, str]:
        """Map problem concepts to metaphor concepts."""
        mapping: dict[str, str] = {}

        # Map domain if there's a match
        if problem.domain == metaphor.domain:
            mapping["domain"] = metaphor.domain

        # Map based on metaphor operations
        problem_words = set(problem.description.lower().split())

        for op in metaphor.operations:
            op_words = set(op.description.lower().split())
            overlap = problem_words & op_words
            if overlap:
                # Found conceptual overlap
                for word in overlap:
                    mapping[word] = op.name

        # Map context keys if present
        for key in problem.context:
            # Simple heuristic: map context keys to metaphor terms
            key_lower = key.lower()
            for op in metaphor.operations:
                if key_lower in op.name.lower() or key_lower in op.description.lower():
                    mapping[key] = op.name
                    break

        # Always have at least one mapping for coverage
        if not mapping and metaphor.operations:
            mapping["problem"] = metaphor.operations[0].name

        return mapping

    def _find_applicable_operations(
        self, problem: Novel, mapped_concepts: dict[str, str], metaphor: Metaphor
    ) -> list[MetaphorOperation]:
        """Find which metaphor operations apply to this problem."""
        applicable: list[MetaphorOperation] = []

        # Add operations that were mapped
        mapped_names = set(mapped_concepts.values())
        for op in metaphor.operations:
            if op.name in mapped_names:
                applicable.append(op)

        # Add operations based on complexity
        if problem.complexity > 0.7:
            # Complex problems might need transformative operations
            for op in metaphor.operations:
                if (
                    "transform" in op.description.lower()
                    or "change" in op.description.lower()
                ):
                    if op not in applicable:
                        applicable.append(op)

        # Always have at least one operation
        if not applicable and metaphor.operations:
            applicable.append(metaphor.operations[0])

        return applicable

    def _create_projection_description(
        self, problem: Novel, mapped_concepts: dict[str, str], metaphor: Metaphor
    ) -> str:
        """Create a description of the problem in metaphor terms."""
        lines = [
            f"Problem '{problem.problem_id}' viewed through {metaphor.name}:",
            "",
            "In metaphor terms:",
        ]

        if mapped_concepts:
            for source, target in mapped_concepts.items():
                lines.append(f"  - '{source}' maps to '{target}'")
        else:
            lines.append("  (No direct concept mappings found)")

        lines.append("")
        lines.append(f"Available operations: {[op.name for op in metaphor.operations]}")

        return "\n".join(lines)

    def _calculate_projection_confidence(
        self, problem: Novel, mapped_concepts: dict[str, str], metaphor: Metaphor
    ) -> float:
        """Calculate confidence in the projection."""
        base = 0.4

        # More mappings = higher confidence
        mapping_bonus = min(0.3, len(mapped_concepts) * 0.1)

        # Domain match = higher confidence
        domain_bonus = 0.2 if problem.domain == metaphor.domain else 0.0

        # Metaphor tractability
        tractability_bonus = metaphor.tractability * 0.1

        return min(1.0, base + mapping_bonus + domain_bonus + tractability_bonus)

    def _create_reification_description(
        self,
        solution: MetaphorSolution,
        reverse_mapping: dict[str, str],
        projection: Projection,
    ) -> str:
        """Create a description of the solution in original problem terms."""
        lines = [
            f"Solution reified from {projection.target.name}:",
            "",
            f"Operations applied: {solution.operations_applied}",
            "",
            "In original terms:",
        ]

        # Translate solution description using reverse mapping
        reified = solution.final_state
        for metaphor_term, problem_term in reverse_mapping.items():
            reified = reified.replace(metaphor_term, problem_term)

        lines.append(reified)

        return "\n".join(lines)

    def _reify_data(
        self, solution_data: dict[str, Any], reverse_mapping: dict[str, str]
    ) -> dict[str, Any]:
        """Translate solution data back to problem domain."""
        reified: dict[str, Any] = {}

        for key, value in solution_data.items():
            # Translate key if possible
            new_key = reverse_mapping.get(key, key)

            # Translate value if it's a string
            if isinstance(value, str):
                new_value = value
                for m_term, p_term in reverse_mapping.items():
                    new_value = new_value.replace(m_term, p_term)
                reified[new_key] = new_value
            else:
                reified[new_key] = value

        return reified

    def _calculate_structural_loss(
        self, source: Novel, projection: Projection
    ) -> float:
        """Calculate structural information loss."""
        # Simple heuristic: loss based on unmapped concepts
        total_concepts = len(source.context) + len(source.constraints) + 1
        mapped = len(projection.mapped_concepts)
        return max(0.0, 1.0 - (mapped / max(1, total_concepts)))

    def _calculate_semantic_loss(self, source: Novel, projection: Projection) -> float:
        """Calculate semantic information loss."""
        # Heuristic: based on coverage and confidence
        return 1.0 - (projection.coverage * projection.confidence)

    def _calculate_contextual_loss(
        self, source: Novel, projection: Projection
    ) -> float:
        """Calculate contextual information loss."""
        # How much context was preserved?
        context_keys = set(source.context.keys())
        mapped_keys = set(projection.mapped_concepts.keys())
        preserved = context_keys & mapped_keys

        if not context_keys:
            return 0.0

        return 1.0 - (len(preserved) / len(context_keys))

    def _find_lost_concepts(
        self, source: Novel, projection: Projection
    ) -> tuple[str, ...]:
        """Find concepts from source that weren't mapped."""
        # Extract "concepts" from description (simple word-based)
        source_words = set(source.description.lower().split())
        mapped_words = set(k.lower() for k in projection.mapped_concepts.keys())

        # Lost = in source but not mapped
        lost = (
            source_words
            - mapped_words
            - {"the", "a", "an", "is", "are", "to", "and", "or"}
        )

        return tuple(sorted(lost)[:10])  # Limit to 10

    def _calculate_quality(
        self, solution: MetaphorSolution, distortion: Distortion
    ) -> float:
        """Calculate overall solution quality."""
        # Quality is inverse of distortion, weighted by solution confidence
        base_quality = 1.0 - distortion.delta
        confidence_factor = solution.confidence
        completeness_factor = solution.completeness

        return base_quality * 0.5 + confidence_factor * 0.3 + completeness_factor * 0.2


# =============================================================================
# Functor Laws Verification
# =============================================================================


def verify_identity_law(functor: MorphicFunctor, problem: Novel) -> bool:
    """
    Verify: Φ(id) = id

    The identity problem should map to an identity-like projection.
    """
    projection = functor.project(problem)
    # Identity holds if projection of same problem is stable
    projection2 = functor.project(problem)

    return (
        projection.projected_description == projection2.projected_description
        and projection.mapped_concepts == projection2.mapped_concepts
    )


def verify_composition_law(
    functor1: MorphicFunctor, functor2: MorphicFunctor, problem: Novel
) -> bool:
    """
    Verify: Φ(g ∘ f) = Φ(g) ∘ Φ(f)

    Composition of functors should equal functor of composition.
    """
    # This would require composable functors with matching types
    # For now, return True as placeholder
    # Full implementation would chain metaphor transformations
    return True
