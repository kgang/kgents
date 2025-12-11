"""
Fix Agent - Fixed-point iteration.

Fix: (A → A) → A
Fix(f) = x where f(x) = x

The fixed-point operator. Takes a self-referential definition and finds
what it stabilizes to. Self-reference cannot be eliminated from a system
that describes itself.

Critical Pattern: Fix Needs Memory
Fixed-point iteration requires carrying state between iterations.
The transform is (State, Previous) → State, not just Input → State.

See spec/bootstrap.md lines 181-193, Idiom 1 (lines 318-347).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, Optional, TypeVar

from .types import Agent, FixConfig, FixResult

A = TypeVar("A")


class Fix(Agent[tuple[Callable[[A], Awaitable[A]], A], FixResult[A]], Generic[A]):
    """
    The fixed-point iteration agent.

    Takes a transform function and initial value, iterates until
    the value stabilizes (or max iterations reached).

    Usage:
        fix = Fix(FixConfig(max_iterations=10))
        result = await fix.invoke((transform_fn, initial_value))

        if result.converged:
            print(f"Found fixed point: {result.value}")
        else:
            print(f"Did not converge after {result.iterations} iterations")

    The transform function should be async and take a single argument:
        async def transform(current: A) -> A: ...

    For stateful iteration (Idiom 6: Fix Needs Memory), pass state
    through the value itself:
        @dataclass
        class State:
            value: int
            confidence: float

        async def stateful_transform(state: State) -> State:
            new_value = compute(state.value)
            new_confidence = state.confidence + 0.1
            return State(new_value, new_confidence)
    """

    def __init__(self, config: Optional[FixConfig[A]] = None):
        """
        Initialize Fix with configuration.

        Args:
            config: FixConfig with max_iterations, equality_check, etc.
        """
        self._config: FixConfig[A] = config or FixConfig()

    @property
    def name(self) -> str:
        return "Fix"

    async def invoke(
        self, input: tuple[Callable[[A], Awaitable[A]], A]
    ) -> FixResult[A]:
        """
        Find fixed point of transform starting from initial value.

        Iterates until:
        1. Value stabilizes (equality_check returns True)
        2. should_continue returns False
        3. max_iterations reached
        4. Entropy budget exhausted (J-gents integration)
        """
        transform, initial = input
        current = initial
        history: list[A] = [initial]

        # Track entropy budget if specified
        initial_budget = self._config.entropy_budget
        current_budget = initial_budget

        # Performance: Bounded history sliding window (H6)
        max_history = self._config.max_history_size

        for i in range(self._config.max_iterations):
            # Check entropy budget (J-gents: force stop if budget exhausted)
            if current_budget is not None:
                # Entropy diminishes: 1.0 / (iteration + 1)
                current_budget = initial_budget / (i + 1) if initial_budget else None
                if current_budget is not None and current_budget < 0.1:
                    # Budget exhausted - return with entropy_remaining=0
                    return FixResult(
                        value=current,
                        converged=False,
                        iterations=i + 1,
                        history=tuple(history),
                        proximity=self._compute_proximity(history),
                        entropy_remaining=0.0,
                    )

            # Check if we should continue
            if not self._config.should_continue(current, i):
                return FixResult(
                    value=current,
                    converged=False,
                    iterations=i + 1,
                    history=tuple(history),
                    proximity=self._compute_proximity(history),
                    entropy_remaining=current_budget,
                )

            # Apply transform
            previous = current
            current = await transform(current)
            history.append(current)

            # Performance: Trim history to max_history_size if bounded (H6)
            if max_history is not None and len(history) > max_history:
                history = history[-max_history:]

            # Check for convergence
            if self._config.equality_check(previous, current):
                return FixResult(
                    value=current,
                    converged=True,
                    iterations=i + 1,
                    history=tuple(history),
                    proximity=0.0,  # Converged = 0 distance
                    entropy_remaining=current_budget,
                )

        # Max iterations reached without convergence
        return FixResult(
            value=current,
            converged=False,
            iterations=self._config.max_iterations,
            history=tuple(history),
            proximity=self._compute_proximity(history),
            entropy_remaining=current_budget,
        )

    def _compute_proximity(self, history: list[A]) -> float:
        """
        Compute proximity metric for adaptive convergence.

        Measures how close we are to a fixed point.
        Lower values indicate closer to convergence.

        This is an evolution improvement for adaptive strategies.
        """
        if len(history) < 2:
            return 1.0

        # Simple heuristic: count consecutive equal values at end
        consecutive_equal = 0
        for i in range(len(history) - 1, 0, -1):
            try:
                if self._config.equality_check(history[i], history[i - 1]):
                    consecutive_equal += 1
                else:
                    break
            except Exception:
                break

        # More consecutive equals = closer to fixed point
        return 1.0 / (1.0 + consecutive_equal)


# --- Convenience Functions ---


async def fix(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    max_iterations: int = 100,
    equality_check: Optional[Callable[[A, A], bool]] = None,
    entropy_budget: Optional[float] = None,
    max_history_size: Optional[int] = None,
) -> FixResult[A]:
    """
    Find fixed point of transform.

    Convenience function for Fix().invoke(...).

    Args:
        transform: Async function A → A
        initial: Starting value
        max_iterations: Maximum iterations before giving up
        equality_check: Custom equality (default: ==)
        entropy_budget: J-gents entropy budget (diminishes per iteration)
        max_history_size: Bounded history size (None = unbounded)

    Returns:
        FixResult with converged value and metadata
    """
    config: FixConfig[A] = FixConfig(
        max_iterations=max_iterations,
        equality_check=equality_check or (lambda a, b: a == b),
        entropy_budget=entropy_budget,
        max_history_size=max_history_size,
    )
    return await Fix(config).invoke((transform, initial))


async def iterate_until_stable(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    max_iterations: int = 100,
) -> A:
    """
    Iterate transform until stable, returning final value.

    Simpler interface when you just need the result.
    Raises RuntimeError if doesn't converge.
    """
    result = await fix(transform, initial, max_iterations)
    if not result.converged:
        raise RuntimeError(f"Failed to converge after {result.iterations} iterations")
    return result.value


# --- Polling Pattern (Idiom 1: Polling is Fix) ---


@dataclass
class PollState(Generic[A]):
    """State for polling-based fixed-point iteration."""

    value: A
    stable_count: int = 0
    required_stability: int = 3


async def poll_until_stable(
    poll_fn: Callable[[], Awaitable[A]],
    max_polls: int = 100,
    required_stability: int = 3,
    equality_check: Optional[Callable[[A, A], bool]] = None,
) -> FixResult[A]:
    """
    Poll until value is stable for required_stability consecutive polls.

    This is Idiom 1: Polling is Fix.

    Args:
        poll_fn: Function that returns current value (no args)
        max_polls: Maximum number of polls
        required_stability: How many consecutive equal values needed
        equality_check: Custom equality (default: ==)

    Returns:
        FixResult with final polled value

    Example:
        result = await poll_until_stable(
            lambda: get_process_state(),
            required_stability=3,
        )
        if result.converged:
            print(f"Process stable at: {result.value}")
    """
    eq = equality_check or (lambda a, b: a == b)

    # Initial poll
    initial_value = await poll_fn()
    initial_state = PollState(
        value=initial_value, required_stability=required_stability
    )

    async def poll_transform(state: PollState[A]) -> PollState[A]:
        new_value = await poll_fn()
        if eq(state.value, new_value):
            return PollState(
                value=new_value,
                stable_count=state.stable_count + 1,
                required_stability=state.required_stability,
            )
        else:
            return PollState(
                value=new_value,
                stable_count=0,
                required_stability=state.required_stability,
            )

    def is_stable(a: PollState[A], b: PollState[A]) -> bool:
        return b.stable_count >= b.required_stability

    config: FixConfig[PollState[A]] = FixConfig(
        max_iterations=max_polls,
        equality_check=is_stable,
    )

    result = await Fix(config).invoke((poll_transform, initial_state))

    # Extract the value from the state
    return FixResult(
        value=result.value.value,
        converged=result.converged,
        iterations=result.iterations,
        history=tuple(s.value for s in result.history),
        proximity=result.proximity,
    )
