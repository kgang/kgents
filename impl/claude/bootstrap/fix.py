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
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar, Union, get_args, get_origin

from .types import Agent

A = TypeVar("A")


class TypeValidationError(TypeError):
    """Raised when runtime type validation fails."""
    pass


@dataclass
class FixConfig:
    """Configuration for fixed-point iteration."""
    max_iterations: int = 100
    convergence_threshold: float = 0.0  # For numeric convergence
    validate_types: bool = True  # Runtime type checking


@dataclass
class FixResult(Generic[A]):
    """Result of fixed-point computation."""
    value: A
    iterations: int
    converged: bool
    history: list[A]  # For debugging/analysis
    proximity_history: list[float]  # Distance from fixed point over time

    def __post_init__(self) -> None:
        """Validate result invariants."""
        if self.iterations < 0:
            raise TypeValidationError(f"iterations must be non-negative, got {self.iterations}")
        if not isinstance(self.converged, bool):
            raise TypeValidationError(f"converged must be bool, got {type(self.converged)}")
        if not isinstance(self.history, list):
            raise TypeValidationError(f"history must be list, got {type(self.history)}")
        if not isinstance(self.proximity_history, list):
            raise TypeValidationError(f"proximity_history must be list, got {type(self.proximity_history)}")

    @property
    def is_converging(self) -> bool:
        """Check if proximity is decreasing (approaching fixed point)."""
        if len(self.proximity_history) < 2:
            return True
        return self.proximity_history[-1] < self.proximity_history[-2]

    @property
    def convergence_rate(self) -> Optional[float]:
        """Estimate convergence rate from proximity history."""
        if len(self.proximity_history) < 2:
            return None
        if self.proximity_history[0] == 0:
            return None
        return self.proximity_history[-1] / self.proximity_history[0]


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

    Example - Adaptive strategy with proximity:
        def distance(a: State, b: State) -> float:
            return abs(a.value - b.value)

        fix = Fix(proximity=distance)
        result = await fix.invoke((transform, initial))
        
        if not result.converged:
            if result.is_converging:
                # Still making progress, could extend iterations
                pass
            else:
                # Diverging or oscillating, abort early
                pass
    """

    def __init__(
        self,
        config: Optional[FixConfig] = None,
        equality: Optional[Callable[[A, A], bool]] = None,
        proximity: Optional[Callable[[A, A], float]] = None,
    ):
        """
        Initialize Fix with optional configuration.

        config: Iteration limits and convergence settings
        equality: Custom equality check (default: ==)
        proximity: Distance metric A × A → ℝ (default: 0.0 if equal else 1.0)
        """
        self._config = config or FixConfig()
        self._equality = equality or (lambda a, b: a == b)
        self._proximity = proximity or (lambda a, b: 0.0 if self._equality(a, b) else 1.0)

    @property
    def name(self) -> str:
        return "Fix"

    def _validate_input(self, input: tuple[Callable[[A], Awaitable[A]], A]) -> None:
        """Validate input tuple structure at runtime."""
        if not self._config.validate_types:
            return

        if not isinstance(input, tuple):
            raise TypeValidationError(f"Fix input must be tuple, got {type(input)}")
        
        if len(input) != 2:
            raise TypeValidationError(f"Fix input must be 2-tuple (transform, initial), got length {len(input)}")
        
        transform, initial = input
        if not callable(transform):
            raise TypeValidationError(f"transform must be callable, got {type(transform)}")

    async def invoke(
        self, input: tuple[Callable[[A], Awaitable[A]], A]
    ) -> FixResult[A]:
        """
        Find the fixed point of transform starting from initial.

        Iterates: x_{n+1} = transform(x_n)
        Until: x_{n+1} == x_n (or max iterations)
        """
        self._validate_input(input)
        
        transform, initial = input
        history: list[A] = [initial]
        proximity_history: list[float] = []

        current = initial
        for i in range(self._config.max_iterations):
            next_value = await transform(current)
            history.append(next_value)

            distance = self._proximity(current, next_value)
            proximity_history.append(distance)

            if self._equality(current, next_value):
                return FixResult(
                    value=next_value,
                    iterations=i + 1,
                    converged=True,
                    history=history,
                    proximity_history=proximity_history,
                )

            current = next_value

        # Did not converge
        return FixResult(
            value=current,
            iterations=self._config.max_iterations,
            converged=False,
            history=history,
            proximity_history=proximity_history,
        )


# Convenience function for common use case
async def fix(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    equality_check: Optional[Callable[[A, A], bool]] = None,
    proximity_metric: Optional[Callable[[A, A], float]] = None,
    max_iterations: int = 100,
    validate_types: bool = True,
) -> FixResult[A]:
    """
    Convenience function for fixed-point iteration.

    Usage:
        result = await fix(
            transform=poll_and_detect,
            initial=DetectionState(RUNNING, confidence=0.0),
            equality_check=lambda a, b: a.state == b.state and b.confidence >= 0.8,
            proximity_metric=lambda a, b: abs(a.confidence - b.confidence),
        )
    """
    config = FixConfig(max_iterations=max_iterations, validate_types=validate_types)
    fix_agent = Fix(config=config, equality=equality_check, proximity=proximity_metric)
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

    def _validate_input(self, input: tuple[Callable[[], Awaitable[A]], int]) -> None:
        """Validate retry input at runtime."""
        if not isinstance(input, tuple) or len(input) != 2:
            raise TypeValidationError(f"RetryFix input must be 2-tuple, got {type(input)}")
        
        operation, max_attempts = input
        if not callable(operation):
            raise TypeValidationError(f"operation must be callable, got {type(operation)}")
        if not isinstance(max_attempts, int) or max_attempts < 1:
            raise TypeValidationError(f"max_attempts must be positive int, got {max_attempts}")

    async def invoke(
        self, input: tuple[Callable[[], Awaitable[A]], int]
    ) -> Optional[A]:
        self._validate_input(input)
        
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
        if threshold <= 0:
            raise TypeValidationError(f"threshold must be positive, got {threshold}")
        if max_iterations < 1:
            raise TypeValidationError(f"max_iterations must be positive, got {max_iterations}")
        
        self._threshold = threshold
        self._max_iterations = max_iterations

    @property
    def name(self) -> str:
        return "ConvergeFix"

    def _validate_input(self, input: tuple[Callable[[float], Awaitable[float]], float]) -> None:
        """Validate numeric convergence input."""
        if not isinstance(input, tuple) or len(input) != 2:
            raise TypeValidationError(f"ConvergeFix input must be 2-tuple, got {type(input)}")
        
        transform, initial = input
        if not callable(transform):
            raise TypeValidationError(f"transform must be callable, got {type(transform)}")
        if not isinstance(initial, (int, float)):
            raise TypeValidationError(f"initial must be numeric, got {type(initial)}")

    async def invoke(
        self, input: tuple[Callable[[float], Awaitable[float]], float]
    ) -> FixResult[float]:
        self._validate_input(input)
        
        transform, initial = input
        history: list[float] = [initial]
        proximity_history: list[float] = []

        current = initial
        for i in range(self._max_iterations):
            next_value = await transform(current)
            history.append(next_value)

            distance = abs(current - next_value)
            proximity_history.append(distance)

            if distance < self._threshold:
                return FixResult(
                    value=next_value,
                    iterations=i + 1,
                    converged=True,
                    history=history,
                    proximity_history=proximity_history,
                )

            current = next_value

        return FixResult(
            value=current,
            iterations=self._max_iterations,
            converged=False,
            history=history,
            proximity_history=proximity_history,
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