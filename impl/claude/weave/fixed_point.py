"""
Fixed-Point Utilities for the Turn Protocol.

Provides Y-combinator style iteration until stability:
- is_stable(): Check if a turn reached fixed point
- iterate_until_stable(): Run agent until output stabilizes
- detect_cycle(): Find limit cycles in turn history

This module operationalizes the fixed-point semantics originally
specified in Y-gent, now part of the Turn Protocol.

Mathematical Foundation:
A fixed point is reached when f(x) = x. For agents:
- Turn is stable when state_hash_pre == state_hash_post
- Iteration continues until stability or resource exhaustion

References:
- Y-combinator: lambda f. (lambda x. f(x x))(lambda x. f(x x))
- Banach fixed-point theorem (contraction mappings)
- spec/protocols/turn.md
- spec/y-gents-archived/MIGRATION.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from .turn import Turn

if TYPE_CHECKING:
    from .weave import TheWeave

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")


def is_stable(turn: Turn[Any]) -> bool:
    """
    Check if a turn represents a fixed point (state didn't change).

    A turn is stable when:
    - state_hash_pre == state_hash_post
    - Both are not "empty" (to avoid false positives)

    Args:
        turn: The turn to check

    Returns:
        True if the turn is stable (fixed point reached)

    Example:
        turn = Turn.create_turn(
            content="done",
            source="agent",
            turn_type=TurnType.SPEECH,
            state_pre={"x": 1},
            state_post={"x": 1},  # Same state = stable
        )
        assert is_stable(turn)
    """
    # Empty states are not considered stable (no meaningful comparison)
    if turn.state_hash_pre == "empty" or turn.state_hash_post == "empty":
        return False

    return turn.state_hash_pre == turn.state_hash_post


def detect_cycle(turns: list[Turn[Any]], window: int = 3) -> bool:
    """
    Detect limit cycles in turn history.

    A limit cycle occurs when state_hash_post repeats within the window.
    This indicates the agent is oscillating between states without
    reaching a true fixed point.

    Args:
        turns: List of turns in order
        window: Number of recent turns to check for cycles

    Returns:
        True if a cycle is detected

    Example:
        # Agent oscillates: A -> B -> A -> B
        turns = [turn_a, turn_b, turn_a, turn_b]
        assert detect_cycle(turns, window=4)
    """
    if len(turns) < window:
        return False

    recent_hashes = [t.state_hash_post for t in turns[-window:]]
    # Cycle exists if not all hashes are unique
    return len(recent_hashes) != len(set(recent_hashes))


def find_cycle_length(turns: list[Turn[Any]], max_length: int = 10) -> int | None:
    """
    Find the length of a detected cycle.

    Args:
        turns: List of turns in order
        max_length: Maximum cycle length to search for

    Returns:
        Cycle length if found, None otherwise

    Example:
        # Period-2 oscillation: A -> B -> A -> B
        turns = [turn_a, turn_b, turn_a, turn_b]
        assert find_cycle_length(turns) == 2
    """
    if len(turns) < 2:
        return None

    # Check for cycles of increasing length
    for period in range(1, min(max_length + 1, len(turns) // 2 + 1)):
        is_cycle = True
        for i in range(period):
            if (
                turns[-(i + 1)].state_hash_post
                != turns[-(i + 1 + period)].state_hash_post
            ):
                is_cycle = False
                break
        if is_cycle:
            return period

    return None


@dataclass
class FixedPointResult(Generic[T]):
    """Result of fixed-point iteration."""

    value: T
    iterations: int
    stable: bool
    cycle_detected: bool
    cycle_length: int | None
    history: list[Turn[Any]]


async def iterate_until_stable(
    invoke_fn: Callable[[A], Any],
    initial: A,
    *,
    max_iterations: int = 10,
    stability_check: Callable[[Turn[Any]], bool] | None = None,
    cycle_window: int = 3,
) -> FixedPointResult[Any]:
    """
    Y-combinator style fixed-point iteration.

    Runs the invoke function until output stabilizes (state stops changing)
    or resource limits are reached.

    This replaces Y-gent's Y.fix() operator with proper Turn Protocol
    integration.

    Args:
        invoke_fn: Function that takes input and returns a Turn
                   (typically an agent's invoke_with_turn method)
        initial: Initial input value
        max_iterations: Maximum iterations before giving up
        stability_check: Custom stability function (default: is_stable)
        cycle_window: Window size for cycle detection

    Returns:
        FixedPointResult with final value and metadata

    Example:
        async def agent_invoke(x):
            result = await agent.invoke(x)
            return Turn.create_turn(
                content=result,
                source=agent.id,
                turn_type=TurnType.THOUGHT,
                state_pre=agent.state,
                state_post=agent.state,  # May have changed
            )

        result = await iterate_until_stable(agent_invoke, initial_input)
        if result.stable:
            print(f"Fixed point reached in {result.iterations} iterations")
    """
    check_stable = stability_check or is_stable
    current = initial
    history: list[Turn[Any]] = []

    for i in range(max_iterations):
        turn = await invoke_fn(current)
        history.append(turn)

        # Check for stability (fixed point)
        if check_stable(turn):
            return FixedPointResult(
                value=turn.content,
                iterations=i + 1,
                stable=True,
                cycle_detected=False,
                cycle_length=None,
                history=history,
            )

        # Check for limit cycle
        if detect_cycle(history, window=cycle_window):
            cycle_len = find_cycle_length(history)
            return FixedPointResult(
                value=turn.content,
                iterations=i + 1,
                stable=False,
                cycle_detected=True,
                cycle_length=cycle_len,
                history=history,
            )

        current = turn.content

    # Max iterations reached without stability
    return FixedPointResult(
        value=history[-1].content if history else initial,
        iterations=max_iterations,
        stable=False,
        cycle_detected=False,
        cycle_length=None,
        history=history,
    )


def collapse_to_ground(history: list[Turn[Any]]) -> Any:
    """
    Collapse a limit cycle to a "ground" value.

    When a cycle is detected, we need to return something meaningful.
    Options:
    1. Return the first state in the cycle (simplest)
    2. Return the state with highest confidence
    3. Return a synthesis of cycle states

    Currently implements option 2 (highest confidence).

    Args:
        history: Turn history containing a cycle

    Returns:
        Best value from the cycle
    """
    if not history:
        return None

    # Find turn with highest confidence
    best_turn = max(history, key=lambda t: t.confidence)
    return best_turn.content


@dataclass
class ConvergenceMetrics:
    """Metrics about convergence behavior."""

    total_iterations: int
    stability_achieved: bool
    cycle_detected: bool
    cycle_length: int | None
    convergence_rate: float  # How quickly state changes decreased
    final_confidence: float


def compute_convergence_metrics(result: FixedPointResult[Any]) -> ConvergenceMetrics:
    """
    Compute metrics about the convergence behavior.

    Useful for debugging and optimization.

    Args:
        result: Result from iterate_until_stable

    Returns:
        ConvergenceMetrics with detailed analysis
    """
    history = result.history

    # Compute convergence rate (how much state change decreased)
    state_changes = []
    for i in range(1, len(history)):
        prev_hash = history[i - 1].state_hash_post
        curr_hash = history[i].state_hash_post
        # 1 if changed, 0 if same
        state_changes.append(0 if prev_hash == curr_hash else 1)

    if len(state_changes) >= 2:
        # Rate of change decrease (higher = converging faster)
        early_changes = sum(state_changes[: len(state_changes) // 2])
        late_changes = sum(state_changes[len(state_changes) // 2 :])
        if early_changes > 0:
            convergence_rate = 1.0 - (late_changes / early_changes)
        else:
            convergence_rate = 1.0 if late_changes == 0 else 0.0
    else:
        convergence_rate = 1.0 if result.stable else 0.0

    final_confidence = history[-1].confidence if history else 0.0

    return ConvergenceMetrics(
        total_iterations=result.iterations,
        stability_achieved=result.stable,
        cycle_detected=result.cycle_detected,
        cycle_length=result.cycle_length,
        convergence_rate=convergence_rate,
        final_confidence=final_confidence,
    )


__all__ = [
    "is_stable",
    "detect_cycle",
    "find_cycle_length",
    "iterate_until_stable",
    "collapse_to_ground",
    "FixedPointResult",
    "ConvergenceMetrics",
    "compute_convergence_metrics",
]
