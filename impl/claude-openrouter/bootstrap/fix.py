"""
Fix (μ) - The fixed-point operator.

Type: (A → A) → A
Returns: x where f(x) = x

Takes a self-referential definition and finds what it stabilizes to.

Why irreducible: Self-reference cannot be eliminated from a system that
                 describes itself. The bootstrap agents themselves are
                 defined in terms of what they generate, which includes
                 themselves. This circularity requires Fix.
What it grounds: Recursive agent definitions. Self-describing specifications.

IDIOM: Polling is Fix
> Any iteration pattern is a fixed-point search.

Polling, retry loops, watch patterns, reconciliation—all are instances of Fix:
    Fix(poll_state) = stable_state where poll_state(stable_state) = stable_state

Structure:
- The transform defines "one step" (poll once, retry once, check once)
- The equality check defines "stability" (state unchanged, success achieved)
- Fix iterates until stable or max iterations

Anti-pattern: `while True` loops with inline break conditions.
"""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar, Union

from .types import Agent

A = TypeVar("A")


@dataclass
class FixConfig:
    """Configuration for fixed-point iteration."""
    max_iterations: int = 100
    convergence_threshold: float = 0.0  # For numeric convergence


@dataclass
class FixResult(Generic[A]):
    """Result of fixed-point computation."""
    value: A
    iterations: int
    converged: bool
    history: list[A]  # For debugging/analysis


class Fix(Agent[tuple[Callable[[A], Awaitable[A]], A], FixResult[A]]):
    """
    The fixed-point operator: iterate until stable.

    Usage:
        fix = Fix()

        # Find stable state through polling
        result = await fix.invoke((
            transform_fn,  # A → A, the step function
            initial_state,  # Starting point
        ))

        if result.converged:
            stable = result.value
        else:
            print(f"Did not converge in {result.iterations} iterations")

    Example - Polling pattern:
        async def poll_once(state: DetectionState) -> DetectionState:
            new_state = await check_process()
            return DetectionState(new_state, state.confidence + 0.1)

        result = await fix.invoke((poll_once, DetectionState.initial()))

    Example - Reconciliation:
        async def reconcile(state: ClusterState) -> ClusterState:
            desired = load_desired_state()
            actual = probe_actual_state()
            if desired == actual:
                return state  # Fixed point reached
            return apply_changes(state, desired, actual)

        result = await fix.invoke((reconcile, ClusterState.empty()))
    """

    def __init__(
        self,
        config: Optional[FixConfig] = None,
        equality: Optional[Callable[[A, A], bool]] = None,
    ):
        """
        Initialize Fix with optional configuration.

        config: Iteration limits and convergence settings
        equality: Custom equality check (default: ==)
        """
        self._config = config or FixConfig()
        self._equality = equality or (lambda a, b: a == b)

    @property
    def name(self) -> str:
        return "Fix"

    async def invoke(
        self, input: tuple[Callable[[A], Awaitable[A]], A]
    ) -> FixResult[A]:
        """
        Find the fixed point of transform starting from initial.

        Iterates: x_{n+1} = transform(x_n)
        Until: x_{n+1} == x_n (or max iterations)
        """
        transform, initial = input
        history: list[A] = [initial]

        current = initial
        for i in range(self._config.max_iterations):
            next_value = await transform(current)
            history.append(next_value)

            if self._equality(current, next_value):
                return FixResult(
                    value=next_value,
                    iterations=i + 1,
                    converged=True,
                    history=history,
                )

            current = next_value

        # Did not converge
        return FixResult(
            value=current,
            iterations=self._config.max_iterations,
            converged=False,
            history=history,
        )


# Convenience function for common use case
async def fix(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    equality_check: Optional[Callable[[A, A], bool]] = None,
    max_iterations: int = 100,
) -> FixResult[A]:
    """
    Convenience function for fixed-point iteration.

    Usage:
        result = await fix(
            transform=poll_and_detect,
            initial=DetectionState(RUNNING, confidence=0.0),
            equality_check=lambda a, b: a.state == b.state and b.confidence >= 0.8,
        )
    """
    config = FixConfig(max_iterations=max_iterations)
    fix_agent = Fix(config=config, equality=equality_check)
    return await fix_agent.invoke((transform, initial))


# Specialized Fix variants for common patterns

class RetryFix(Agent[tuple[Callable[[], Awaitable[A]], int], Optional[A]]):
    """
    Retry a fallible operation until success or max attempts.

    This is Fix specialized for operations that may fail.
    """

    @property
    def name(self) -> str:
        return "RetryFix"

    async def invoke(
        self, input: tuple[Callable[[], Awaitable[A]], int]
    ) -> Optional[A]:
        operation, max_attempts = input

        for attempt in range(max_attempts):
            try:
                return await operation()
            except Exception:
                if attempt == max_attempts - 1:
                    return None
                continue

        return None


class ConvergeFix(Agent[tuple[Callable[[float], Awaitable[float]], float], FixResult[float]]):
    """
    Find fixed point with numeric convergence check.

    For when "equality" means "close enough".
    """

    def __init__(self, threshold: float = 1e-6, max_iterations: int = 1000):
        self._threshold = threshold
        self._max_iterations = max_iterations

    @property
    def name(self) -> str:
        return "ConvergeFix"

    async def invoke(
        self, input: tuple[Callable[[float], Awaitable[float]], float]
    ) -> FixResult[float]:
        transform, initial = input
        history: list[float] = [initial]

        current = initial
        for i in range(self._max_iterations):
            next_value = await transform(current)
            history.append(next_value)

            if abs(current - next_value) < self._threshold:
                return FixResult(
                    value=next_value,
                    iterations=i + 1,
                    converged=True,
                    history=history,
                )

            current = next_value

        return FixResult(
            value=current,
            iterations=self._max_iterations,
            converged=False,
            history=history,
        )


# Regeneration is Fix
#
# The bootstrap itself is a fixed-point operation:
#   Regenerate(Spec) ≅ Current Impl
#   Judge(Regenerated, Principles) = accept ∀ components
#   Contradict(Regenerated, Spec) = None
#
# We iterate:
#   impl_0 = generate(spec)
#   impl_1 = fix(impl_0, judge_feedback)
#   impl_n = fix(impl_{n-1}, ...)
# Until:
#   Judge accepts and Contradict finds nothing
