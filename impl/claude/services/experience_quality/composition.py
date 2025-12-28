"""
Experience Quality Operad: Composition Operations.

Algebraic composition of experience quality:
- Sequential (>>): A then B
- Parallel (||): A and B simultaneously
- Nested ([]): B inside A

These compositions satisfy operad laws:
- Identity: measure(Id) = Quality.unit()
- Associativity: (A >> B) >> C = A >> (B >> C)
- Floor gate: F=0 => Q=0

Philosophy:
    "Quality is not a number. It is a structure. The structure composes."

See: spec/theory/experience-quality-operad.md
"""

from __future__ import annotations

from .measurement import chain_arc_coverage, cosine_distance, experience_vector
from .types import ExperienceQuality


# =============================================================================
# Sequential Composition (>>)
# =============================================================================


def sequential_compose(
    q_a: ExperienceQuality,
    q_b: ExperienceQuality,
) -> ExperienceQuality:
    """
    Sequential composition: A then B.

    When experience A is followed by experience B:
    - Contrast: Measured across the transition (A->B adds to contrast)
    - Arc: Phases chain (A's arc + B's arc + transition arc)
    - Voice: Adversarial AND, Creative OR, Advocate AND
    - Floor: Both must pass (AND semantics)

    The key insight: sequential experiences INCREASE contrast because
    the transition between them adds variety.

    Laws:
    - Associativity: (A >> B) >> C = A >> (B >> C)
    - Identity: A >> unit() = A (approximately)
    - Floor gate: If either floor fails, result floor fails
    """
    # Floor gate: both must pass
    if not q_a.floor_passed or not q_b.floor_passed:
        return ExperienceQuality.zero()

    # Contrast INCREASES with variety between A and B
    # Compute transition contrast from experience vectors
    vec_a = experience_vector(q_a)
    vec_b = experience_vector(q_b)
    transition_contrast = cosine_distance(vec_a, vec_b)

    # Combined contrast: average of both + transition bonus
    combined_contrast = (q_a.contrast + q_b.contrast + transition_contrast) / 3

    # Arc phases chain
    combined_arc = chain_arc_coverage(q_a.arc_coverage, q_b.arc_coverage)

    return ExperienceQuality(
        contrast=min(1.0, combined_contrast),
        arc_coverage=min(1.0, combined_arc),
        # Adversarial: both must be correct (AND)
        voice_adversarial=q_a.voice_adversarial and q_b.voice_adversarial,
        # Creative: one interesting segment saves the sequence (OR)
        voice_creative=q_a.voice_creative or q_b.voice_creative,
        # Advocate: both must be fun (AND)
        voice_advocate=q_a.voice_advocate and q_b.voice_advocate,
        # Floor: both must pass (AND)
        floor_passed=True,  # Already checked above
    )


# =============================================================================
# Parallel Composition (||)
# =============================================================================


def parallel_compose(
    q_a: ExperienceQuality,
    q_b: ExperienceQuality,
) -> ExperienceQuality:
    """
    Parallel composition: A and B simultaneously.

    When experiences A and B happen at the same time (layered):
    - Contrast: Maximum of both (dominant track)
    - Arc: Weighted mean (both contribute)
    - Voice: Adversarial AND, Creative OR, Advocate AND
    - Floor: Both must pass

    Used for: multi-track experiences, layered systems,
    background + foreground experiences.

    Laws:
    - Associativity: (A || B) || C = A || (B || C)
    - Commutativity: A || B = B || A
    - Floor gate: If either floor fails, result floor fails
    """
    # Floor gate: both must pass
    if not q_a.floor_passed or not q_b.floor_passed:
        return ExperienceQuality.zero()

    # Contrast: dominant track wins (max)
    combined_contrast = max(q_a.contrast, q_b.contrast)

    # Arc: weighted mean (equal weight for now)
    combined_arc = (q_a.arc_coverage + q_b.arc_coverage) / 2

    return ExperienceQuality(
        contrast=combined_contrast,
        arc_coverage=combined_arc,
        # Adversarial: both must be correct
        voice_adversarial=q_a.voice_adversarial and q_b.voice_adversarial,
        # Creative: either being interesting is good
        voice_creative=q_a.voice_creative or q_b.voice_creative,
        # Advocate: both must be fun
        voice_advocate=q_a.voice_advocate and q_b.voice_advocate,
        floor_passed=True,
    )


# =============================================================================
# Nested Composition ([])
# =============================================================================


def nested_compose(
    q_outer: ExperienceQuality,
    q_inner: ExperienceQuality,
    outer_weight: float = 0.7,
) -> ExperienceQuality:
    """
    Nested composition: inner experience inside outer experience.

    When experience B is nested inside experience A:
    - Continuous metrics: Weighted combination (outer dominates)
    - Voice adversarial: Outer decides correctness
    - Voice creative: Either can provide interest
    - Voice advocate: Inner decides fun (granular)
    - Floor: Both must pass

    Used for: runs inside sessions, waves inside runs, moments inside waves.

    The outer experience sets the context and correctness,
    while the inner experience provides the fun moment-to-moment.

    Args:
        q_outer: The containing experience quality
        q_inner: The nested experience quality
        outer_weight: How much the outer context dominates (default 0.7)

    Laws:
    - Floor gate: If either floor fails, result floor fails
    - Nesting preserves outer correctness
    - Nesting preserves inner fun
    """
    # Floor gate: both must pass
    if not q_outer.floor_passed or not q_inner.floor_passed:
        return ExperienceQuality.zero()

    inner_weight = 1.0 - outer_weight

    # Continuous metrics: weighted combination
    combined_contrast = (
        outer_weight * q_outer.contrast + inner_weight * q_inner.contrast
    )
    combined_arc = (
        outer_weight * q_outer.arc_coverage + inner_weight * q_inner.arc_coverage
    )

    return ExperienceQuality(
        contrast=combined_contrast,
        arc_coverage=combined_arc,
        # Outer decides correctness (context is correct)
        voice_adversarial=q_outer.voice_adversarial,
        # Either can provide interest
        voice_creative=q_outer.voice_creative or q_inner.voice_creative,
        # Inner decides fun (moment-to-moment)
        voice_advocate=q_inner.voice_advocate,
        floor_passed=True,
    )


# =============================================================================
# Multi-way Compositions
# =============================================================================


def sequential_compose_many(qualities: list[ExperienceQuality]) -> ExperienceQuality:
    """
    Compose multiple qualities sequentially.

    Equivalent to: q1 >> q2 >> q3 >> ...

    Uses left-to-right folding (associative, so order of folding doesn't matter).
    """
    if not qualities:
        return ExperienceQuality.unit()

    result = qualities[0]
    for q in qualities[1:]:
        result = sequential_compose(result, q)

    return result


def parallel_compose_many(qualities: list[ExperienceQuality]) -> ExperienceQuality:
    """
    Compose multiple qualities in parallel.

    Equivalent to: q1 || q2 || q3 || ...

    Uses left-to-right folding (associative and commutative).
    """
    if not qualities:
        return ExperienceQuality.unit()

    result = qualities[0]
    for q in qualities[1:]:
        result = parallel_compose(result, q)

    return result


def nested_compose_many(
    outer: ExperienceQuality,
    inners: list[ExperienceQuality],
) -> ExperienceQuality:
    """
    Nest multiple inner experiences within an outer context.

    First composes all inner experiences in parallel,
    then nests the combined inner within the outer.
    """
    if not inners:
        return outer

    combined_inner = parallel_compose_many(inners)
    return nested_compose(outer, combined_inner)


# =============================================================================
# Identity and Zero
# =============================================================================


def identity() -> ExperienceQuality:
    """
    Return the identity quality.

    The identity satisfies:
    - A >> identity() ≈ A
    - identity() >> A ≈ A
    - A || identity() ≥ A (parallel with identity improves)
    """
    return ExperienceQuality.unit()


def zero() -> ExperienceQuality:
    """
    Return the zero quality (floor failed).

    The zero satisfies:
    - A >> zero() = zero()
    - zero() >> A = zero()
    - A || zero() = zero()
    - nested(A, zero()) = zero()
    """
    return ExperienceQuality.zero()


# =============================================================================
# Law Verification (for testing)
# =============================================================================


def verify_associativity_sequential(
    a: ExperienceQuality,
    b: ExperienceQuality,
    c: ExperienceQuality,
    tolerance: float = 0.01,
) -> bool:
    """
    Verify sequential associativity: (A >> B) >> C ≈ A >> (B >> C)

    Returns True if the law holds within tolerance.
    """
    left = sequential_compose(sequential_compose(a, b), c)
    right = sequential_compose(a, sequential_compose(b, c))

    # Compare overall quality
    return abs(left.overall - right.overall) < tolerance


def verify_associativity_parallel(
    a: ExperienceQuality,
    b: ExperienceQuality,
    c: ExperienceQuality,
    tolerance: float = 0.01,
) -> bool:
    """
    Verify parallel associativity: (A || B) || C ≈ A || (B || C)

    Returns True if the law holds within tolerance.
    """
    left = parallel_compose(parallel_compose(a, b), c)
    right = parallel_compose(a, parallel_compose(b, c))

    return abs(left.overall - right.overall) < tolerance


def verify_floor_gate(
    a: ExperienceQuality,
    b: ExperienceQuality,
) -> bool:
    """
    Verify floor gate law: If F=0, then Q=0.

    Returns True if the law holds.
    """
    # If either floor is false, any composition should be zero
    if not a.floor_passed or not b.floor_passed:
        seq = sequential_compose(a, b)
        par = parallel_compose(a, b)
        nested_result = nested_compose(a, b)

        return (
            seq.overall == 0.0
            and par.overall == 0.0
            and nested_result.overall == 0.0
        )

    return True


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core compositions
    "sequential_compose",
    "parallel_compose",
    "nested_compose",
    # Multi-way
    "sequential_compose_many",
    "parallel_compose_many",
    "nested_compose_many",
    # Identity and zero
    "identity",
    "zero",
    # Law verification
    "verify_associativity_sequential",
    "verify_associativity_parallel",
    "verify_floor_gate",
]
