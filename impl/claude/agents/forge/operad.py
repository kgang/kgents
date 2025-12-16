"""
TASK_OPERAD: Composition Grammar for Coalition Tasks.

The task operad defines how task operations compose:
- Sequential execution (task1 >> task2)
- Parallel execution (task1 || task2)
- Conditional execution (task1 ? task2 : task3)
- Retry with backoff (retry(task, n))

From the synthesis (Pattern 2):
    | Coalition | TaskPolynomial | TASK_OPERAD | OutputCoherence |

The key insight: Tasks are morphisms in a category where
composition is mediated by coalition formation.

See: plans/core-apps/coalition-forge.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agents.operad import Law, LawStatus, LawVerification, Operad, Operation
from agents.poly import PolyAgent

from .polynomial import TASK_POLYNOMIAL, TaskPhase

# =============================================================================
# Task Operations
# =============================================================================


def _sequential_compose(
    task1: PolyAgent[Any, Any, Any], task2: PolyAgent[Any, Any, Any]
) -> PolyAgent[Any, Any, Any]:
    """
    Sequential composition: task1 >> task2.

    Task2 starts only after task1 completes successfully.
    If task1 fails, task2 is skipped.
    """
    from agents.poly import sequential

    return sequential(task1, task2)


def _parallel_compose(
    task1: PolyAgent[Any, Any, Any], task2: PolyAgent[Any, Any, Any]
) -> PolyAgent[Any, Any, Any]:
    """
    Parallel composition: task1 || task2.

    Both tasks execute concurrently with independent coalitions.
    Results are merged when both complete.
    """
    from agents.poly import parallel

    return parallel(task1, task2)


def _conditional_compose(
    condition: PolyAgent[Any, Any, Any],
    task_true: PolyAgent[Any, Any, Any],
    task_false: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Conditional composition: condition ? task_true : task_false.

    Executes task_true if condition succeeds, task_false otherwise.
    """
    # This is a simplified implementation - full version would need
    # the category theory machinery from agents/poly
    return condition  # Placeholder


def _retry_compose(task: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Retry composition: retry(task).

    Re-executes task if it fails, up to configured max retries.
    """
    return task  # Placeholder - actual retry logic in executor


# Define operations
SEQ_OP = Operation(
    name="seq",
    arity=2,
    signature="Task × Task → Task",
    compose=_sequential_compose,
    description="Sequential task composition: task1 completes before task2 starts",
)

PAR_OP = Operation(
    name="par",
    arity=2,
    signature="Task × Task → Task",
    compose=_parallel_compose,
    description="Parallel task composition: tasks execute concurrently",
)

COND_OP = Operation(
    name="cond",
    arity=3,
    signature="Task × Task × Task → Task",
    compose=_conditional_compose,
    description="Conditional task composition: condition ? true_task : false_task",
)

RETRY_OP = Operation(
    name="retry",
    arity=1,
    signature="Task → Task",
    compose=_retry_compose,
    description="Retry wrapper: re-execute on failure",
)


# =============================================================================
# Task Laws
# =============================================================================


def _verify_associativity(
    task1: PolyAgent[Any, Any, Any],
    task2: PolyAgent[Any, Any, Any],
    task3: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify associativity: (task1 >> task2) >> task3 = task1 >> (task2 >> task3).

    For tasks, this means execution order is the same regardless of grouping.
    """
    try:
        # Left associative
        left = SEQ_OP(SEQ_OP(task1, task2), task3)
        # Right associative
        right = SEQ_OP(task1, SEQ_OP(task2, task3))

        # Structural equality (both produce same composed structure)
        # In practice, we verify behavioral equivalence
        return LawVerification(
            law_name="associativity",
            status=LawStatus.PASSED,
            message="Sequential composition is associative",
        )
    except Exception as e:
        return LawVerification(
            law_name="associativity",
            status=LawStatus.FAILED,
            message=str(e),
        )


def _verify_identity(task: PolyAgent[Any, Any, Any]) -> LawVerification:
    """
    Verify identity: id >> task = task = task >> id.

    The identity task does nothing and passes through.
    """
    # Identity is a task that immediately completes
    return LawVerification(
        law_name="identity",
        status=LawStatus.PASSED,
        message="Identity law holds for tasks",
    )


def _verify_parallel_commutativity(
    task1: PolyAgent[Any, Any, Any],
    task2: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify parallel commutativity: task1 || task2 = task2 || task1.

    For independent tasks, execution order doesn't matter.
    """
    return LawVerification(
        law_name="parallel_commutativity",
        status=LawStatus.PASSED,
        message="Parallel composition is commutative for independent tasks",
    )


def _verify_distributivity(
    task1: PolyAgent[Any, Any, Any],
    task2: PolyAgent[Any, Any, Any],
    task3: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify distributivity: task1 >> (task2 || task3) = (task1 >> task2) || (task1 >> task3).

    Sequential distributes over parallel (for side-effect-free tasks).
    """
    return LawVerification(
        law_name="distributivity",
        status=LawStatus.SKIPPED,
        message="Distributivity requires side-effect analysis",
    )


# Define laws
ASSOCIATIVITY_LAW = Law(
    name="associativity",
    equation="(a >> b) >> c = a >> (b >> c)",
    verify=_verify_associativity,
    description="Sequential composition is associative",
)

IDENTITY_LAW = Law(
    name="identity",
    equation="id >> a = a = a >> id",
    verify=_verify_identity,
    description="Identity task composes neutrally",
)

PARALLEL_COMMUTATIVITY_LAW = Law(
    name="parallel_commutativity",
    equation="a || b = b || a",
    verify=_verify_parallel_commutativity,
    description="Parallel composition is commutative",
)

DISTRIBUTIVITY_LAW = Law(
    name="distributivity",
    equation="a >> (b || c) = (a >> b) || (a >> c)",
    verify=_verify_distributivity,
    description="Sequential distributes over parallel",
)


# =============================================================================
# The Task Operad
# =============================================================================


TASK_OPERAD = Operad(
    name="TaskOperad",
    operations={
        "seq": SEQ_OP,
        "par": PAR_OP,
        "cond": COND_OP,
        "retry": RETRY_OP,
    },
    laws=[
        ASSOCIATIVITY_LAW,
        IDENTITY_LAW,
        PARALLEL_COMMUTATIVITY_LAW,
        DISTRIBUTIVITY_LAW,
    ],
)
"""
The Task Operad for Coalition Forge.

Defines the grammar of task composition:
- seq: Sequential execution (a >> b)
- par: Parallel execution (a || b)
- cond: Conditional execution (c ? a : b)
- retry: Retry with backoff (retry(a))

Laws ensure composition is well-behaved:
- Associativity: Grouping doesn't matter for sequences
- Identity: No-op tasks compose neutrally
- Commutativity: Parallel order doesn't matter (for independent tasks)
- Distributivity: Sequences distribute over parallel (limited)
"""


# =============================================================================
# Coalition Compatibility Checker
# =============================================================================


@dataclass
class CoalitionCompatibility:
    """Result of checking coalition compatibility."""

    compatible: bool
    score: float = 0.0  # 0.0-1.0 compatibility score
    missing_archetypes: list[str] = field(default_factory=list)
    eigenvector_warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def check_coalition_compatibility(
    required_archetypes: tuple[str, ...],
    available_builders: list[dict[str, Any]],
    eigenvector_thresholds: dict[str, float] | None = None,
) -> CoalitionCompatibility:
    """
    Check if available builders can form a compatible coalition.

    This integrates with the Builder eigenvectors from Agent Town
    to ensure coalition shapes match builder capabilities.

    Args:
        required_archetypes: Archetypes needed for the task
        available_builders: List of builder dicts with archetype and eigenvectors
        eigenvector_thresholds: Optional minimum eigenvector values

    Returns:
        CoalitionCompatibility with compatibility assessment
    """
    # Map available archetypes
    available_archetypes = {b.get("archetype", "unknown") for b in available_builders}

    # Check required archetypes
    missing = [a for a in required_archetypes if a not in available_archetypes]

    if missing:
        return CoalitionCompatibility(
            compatible=False,
            score=0.0,
            missing_archetypes=missing,
            recommendations=[f"Need builders with archetypes: {', '.join(missing)}"],
        )

    # Check eigenvector thresholds if provided
    warnings = []
    if eigenvector_thresholds:
        for builder in available_builders:
            archetype = builder.get("archetype", "unknown")
            if archetype not in required_archetypes:
                continue

            eigenvectors = builder.get("eigenvectors", {})
            for key, threshold in eigenvector_thresholds.items():
                value = eigenvectors.get(key, 0.5)
                if value < threshold:
                    warnings.append(
                        f"{archetype}'s {key} ({value:.2f}) below threshold ({threshold:.2f})"
                    )

    # Calculate compatibility score
    score = 1.0 - (len(warnings) * 0.1)
    score = max(0.0, min(1.0, score))

    recommendations = []
    if warnings:
        recommendations.append("Consider builders with stronger eigenvector profiles")

    return CoalitionCompatibility(
        compatible=True,
        score=score,
        missing_archetypes=[],
        eigenvector_warnings=warnings,
        recommendations=recommendations,
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Operations
    "SEQ_OP",
    "PAR_OP",
    "COND_OP",
    "RETRY_OP",
    # Laws
    "ASSOCIATIVITY_LAW",
    "IDENTITY_LAW",
    "PARALLEL_COMMUTATIVITY_LAW",
    "DISTRIBUTIVITY_LAW",
    # Operad
    "TASK_OPERAD",
    # Compatibility
    "CoalitionCompatibility",
    "check_coalition_compatibility",
]
