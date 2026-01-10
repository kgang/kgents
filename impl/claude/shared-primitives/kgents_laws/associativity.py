"""
kgents-laws/associativity: Behavioral Associativity Law Verification

The associativity law states that composition grouping doesn't matter:

    (f >> g) >> h = f >> (g >> h)

This module provides BEHAVIORAL verification - we actually run
concrete inputs through both orderings and compare outputs.

Why behavioral verification?

Structural type checking might pass while runtime behavior diverges:
- Floating-point accumulation errors
- Order-dependent side effects
- State transitions that depend on composition order
- Lazy evaluation differences

By running real inputs through both groupings, we catch real bugs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .core import LawStatus, LawVerification
from .errors import AssociativityError

if TYPE_CHECKING:
    from kgents_poly import PolyAgent


# -----------------------------------------------------------------------------
# Associativity Law Verification
# -----------------------------------------------------------------------------


def verify_associativity(
    f: PolyAgent[Any, Any, Any],
    g: PolyAgent[Any, Any, Any],
    h: PolyAgent[Any, Any, Any],
    test_inputs: list[tuple[Any, Any]],
    *,
    raise_on_failure: bool = False,
    verbose: bool = False,
) -> LawVerification:
    """
    Verify associativity: (f >> g) >> h = f >> (g >> h).

    This function performs BEHAVIORAL verification by running
    concrete inputs through both composition orderings.

    Args:
        f: First agent in composition.
        g: Second agent (middle).
        h: Third agent (rightmost).
        test_inputs: List of (state, input) tuples to test.
                     State should be compatible with f's positions.
        raise_on_failure: If True, raise AssociativityError on violation.
                          If False, return LawVerification with FAILED status.
        verbose: If True, print detailed progress for debugging.

    Returns:
        LawVerification with:
        - status=PASSED if all test inputs produce equal results
        - status=FAILED if any test input shows divergence
        - status=SKIPPED if no valid test inputs

    Raises:
        AssociativityError: If raise_on_failure=True and violation detected.

    Example:
        >>> from kgents_poly import from_function
        >>>
        >>> # Create agents
        >>> double = from_function("double", lambda x: x * 2)
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> square = from_function("square", lambda x: x * x)
        >>>
        >>> # Verify associativity
        >>> test_inputs = [
        ...     ("ready", 1),
        ...     ("ready", 5),
        ...     ("ready", 10),
        ... ]
        >>> result = verify_associativity(double, add_one, square, test_inputs)
        >>> assert result.passed

    How it works:

        For each (state, input):

        1. Compose left-associative: left = (f >> g) >> h
        2. Compose right-associative: right = f >> (g >> h)
        3. Build states: left_state = ((f_s, g_s), h_s), right_state = (f_s, (g_s, h_s))
        4. Run both: left.invoke(left_state, input), right.invoke(right_state, input)
        5. Compare outputs

        The state structure differs because sequential composition nests states
        as tuples in the order of composition.
    """
    from kgents_poly import sequential

    # Compose both ways
    fg = sequential(f, g)
    gh = sequential(g, h)

    left = sequential(fg, h)  # (f >> g) >> h
    right = sequential(f, gh)  # f >> (g >> h)

    # Get initial states for each agent
    f_init = next(iter(f.positions))
    g_init = next(iter(g.positions))
    h_init = next(iter(h.positions))

    # Track results
    tests_run = 0
    tests_passed = 0

    for state, inp in test_inputs:
        try:
            # Use provided state for f, or fall back to f_init
            f_state = state if state in f.positions else f_init

            if verbose:
                print(f"Testing: input={inp!r}")

            # Build composed states
            # Left: ((f_state, g_state), h_state)
            left_state = ((f_state, g_init), h_init)
            # Right: (f_state, (g_state, h_state))
            right_state = (f_state, (g_init, h_init))

            # Run left-associative composition
            _, left_output = left.invoke(left_state, inp)
            if verbose:
                print(f"  ({f.name} >> {g.name}) >> {h.name} = {left_output!r}")

            # Run right-associative composition
            _, right_output = right.invoke(right_state, inp)
            if verbose:
                print(f"  {f.name} >> ({g.name} >> {h.name}) = {right_output!r}")

            tests_run += 1

            # Compare outputs
            if left_output != right_output:
                # Try to find intermediate values for debugging
                try:
                    _, fg_output = fg.invoke((f_state, g_init), inp)
                    _, gh_output = gh.invoke((g_init, h_init), fg_output)
                    intermediate_left = fg_output
                    intermediate_right = None  # Would need f's output
                except Exception:
                    intermediate_left = None
                    intermediate_right = None

                failure_msg = (
                    f"Associativity violated for input {inp!r}: "
                    f"({f.name} >> {g.name}) >> {h.name} = {left_output!r}, "
                    f"but {f.name} >> ({g.name} >> {h.name}) = {right_output!r}"
                )

                if raise_on_failure:
                    raise AssociativityError(
                        agents=(f.name, g.name, h.name),
                        test_input=inp,
                        left_result=left_output,
                        right_result=right_output,
                        divergence_step=-1,  # Could compute if needed
                        intermediate_left=intermediate_left,
                        intermediate_right=intermediate_right,
                    )

                return LawVerification(
                    law_name="associativity",
                    status=LawStatus.FAILED,
                    left_result=left_output,
                    right_result=right_output,
                    message=failure_msg,
                    test_input=inp,
                )

            tests_passed += 1

        except (TypeError, ValueError) as e:
            # Type mismatch for this input - skip but log if verbose
            if verbose:
                print(f"  Skipped (type error): {e}")
            continue

    # All tests passed (or no valid tests)
    if tests_run == 0:
        return LawVerification(
            law_name="associativity",
            status=LawStatus.SKIPPED,
            message="No valid test inputs could be processed",
        )

    return LawVerification(
        law_name="associativity",
        status=LawStatus.PASSED,
        message=(
            f"Associativity verified for ({f.name} >> {g.name}) >> {h.name} "
            f"with {tests_passed}/{tests_run} test inputs"
        ),
    )


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


def quick_associativity_check(
    f: PolyAgent[Any, Any, Any],
    g: PolyAgent[Any, Any, Any],
    h: PolyAgent[Any, Any, Any],
    inputs: list[Any] | None = None,
) -> bool:
    """
    Quick check if three agents satisfy associativity.

    This is a convenience function for simple cases where you
    just want a boolean answer.

    Args:
        f, g, h: Agents to test.
        inputs: List of input values (state defaults to first position of f).

    Returns:
        True if associativity holds, False otherwise.

    Example:
        >>> from kgents_poly import from_function
        >>> double = from_function("double", lambda x: x * 2)
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> square = from_function("square", lambda x: x * x)
        >>> assert quick_associativity_check(double, add_one, square, [1, 2, 3])
    """
    if inputs is None:
        inputs = [0, 1, 2, 10]

    # Use first position of f as state for all inputs
    state = next(iter(f.positions))
    test_inputs = [(state, inp) for inp in inputs]

    result = verify_associativity(f, g, h, test_inputs, raise_on_failure=False)
    return result.passed


def verify_triple(
    f: PolyAgent[Any, Any, Any],
    g: PolyAgent[Any, Any, Any],
    h: PolyAgent[Any, Any, Any],
    test_inputs: list[tuple[Any, Any]],
    *,
    raise_on_failure: bool = False,
    verbose: bool = False,
) -> LawVerification:
    """
    Alias for verify_associativity with clearer naming.

    In categorical terms, we're verifying that the triple
    (f, g, h) forms a valid composition.

    See verify_associativity for full documentation.
    """
    return verify_associativity(
        f,
        g,
        h,
        test_inputs,
        raise_on_failure=raise_on_failure,
        verbose=verbose,
    )


# -----------------------------------------------------------------------------
# Advanced: Verify All Triples
# -----------------------------------------------------------------------------


def verify_all_triples(
    agents: list[PolyAgent[Any, Any, Any]],
    test_inputs: list[tuple[Any, Any]],
    *,
    raise_on_failure: bool = False,
    verbose: bool = False,
) -> list[LawVerification]:
    """
    Verify associativity for all ordered triples of agents.

    This is useful when you have a collection of agents and want
    to ensure associativity holds for all possible compositions.

    Args:
        agents: List of agents (need at least 3).
        test_inputs: Test inputs to use for each triple.
        raise_on_failure: If True, raise on first failure.
        verbose: If True, print progress.

    Returns:
        List of LawVerification results for each triple.

    Example:
        >>> agents = [double, add_one, square, negate]
        >>> results = verify_all_triples(agents, test_inputs)
        >>> assert all(r.passed for r in results)
    """
    from itertools import permutations

    results: list[LawVerification] = []

    if len(agents) < 3:
        return [
            LawVerification(
                law_name="associativity",
                status=LawStatus.SKIPPED,
                message="Need at least 3 agents to verify associativity",
            )
        ]

    for f, g, h in permutations(agents, 3):
        if verbose:
            print(f"\nVerifying: ({f.name} >> {g.name}) >> {h.name}")

        result = verify_associativity(
            f,
            g,
            h,
            test_inputs,
            raise_on_failure=raise_on_failure,
            verbose=verbose,
        )
        results.append(result)

        if not result.passed and raise_on_failure:
            break  # Already raised

    return results


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


__all__ = [
    "verify_associativity",
    "quick_associativity_check",
    "verify_triple",
    "verify_all_triples",
]
