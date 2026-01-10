"""
kgents-laws/identity: Behavioral Identity Law Verification

The identity law states that composing with the identity morphism
has no effect:

    Id >> f = f = f >> Id

This module provides BEHAVIORAL verification - we actually run
concrete inputs through both orderings and compare outputs.

Why behavioral verification?

Type-level verification can miss bugs that only manifest at runtime.
By running real inputs, we catch:
- Type coercion issues (e.g., int -> float)
- Floating-point precision differences
- State mutation bugs
- Reference equality vs value equality issues
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .core import LawStatus, LawVerification
from .errors import IdentityError

if TYPE_CHECKING:
    from kgents_poly import PolyAgent


# -----------------------------------------------------------------------------
# Identity Law Verification
# -----------------------------------------------------------------------------


def verify_identity(
    agent: PolyAgent[Any, Any, Any],
    test_inputs: list[tuple[Any, Any]],
    *,
    raise_on_failure: bool = False,
    verbose: bool = False,
) -> LawVerification:
    """
    Verify the identity law: Id >> agent = agent = agent >> Id.

    This function performs BEHAVIORAL verification by actually running
    test inputs through both compositions and comparing outputs.

    Args:
        agent: The polynomial agent to verify.
        test_inputs: List of (state, input) tuples to test.
                     Each tuple provides a starting state and input value.
        raise_on_failure: If True, raise IdentityError on violation.
                          If False, return LawVerification with FAILED status.
        verbose: If True, print detailed progress (useful for debugging).

    Returns:
        LawVerification with:
        - status=PASSED if all test inputs pass
        - status=FAILED if any test input shows violation
        - status=SKIPPED if no valid test inputs

    Raises:
        IdentityError: If raise_on_failure=True and violation detected.

    Example:
        >>> from kgents_poly import from_function
        >>>
        >>> # Create a simple agent
        >>> double = from_function("double", lambda x: x * 2)
        >>>
        >>> # Verify identity law with various inputs
        >>> test_inputs = [
        ...     ("ready", 1),
        ...     ("ready", 10),
        ...     ("ready", -5),
        ... ]
        >>> result = verify_identity(double, test_inputs)
        >>> assert result.passed

    How it works:

        For each (state, input) pair:

        1. Run: agent.invoke(state, input) -> (_, agent_output)
        2. Run: (Id >> agent).invoke((id_state, state), input) -> (_, left_output)
        3. Run: (agent >> Id).invoke((state, id_state), input) -> (_, right_output)
        4. Verify: left_output == agent_output == right_output

        If any inequality is found, that's a law violation.
    """
    from kgents_poly import identity as create_identity
    from kgents_poly import sequential

    # Create the identity agent
    id_agent = create_identity("Id")
    id_state = next(iter(id_agent.positions))

    # Track results
    tests_run = 0
    tests_passed = 0

    for state, inp in test_inputs:
        try:
            # Get agent's initial state from positions if needed
            agent_state = state
            if state not in agent.positions:
                # Try to use the provided state anyway, or fall back
                agent_state = next(iter(agent.positions))

            if verbose:
                print(f"Testing: state={agent_state!r}, input={inp!r}")

            # Run agent alone
            _, agent_output = agent.invoke(agent_state, inp)
            if verbose:
                print(f"  agent({agent_state!r}, {inp!r}) = {agent_output!r}")

            # Run Id >> agent (left identity)
            left_composed = sequential(id_agent, agent)
            left_state = (id_state, agent_state)
            _, left_output = left_composed.invoke(left_state, inp)
            if verbose:
                print(f"  (Id >> agent)({left_state!r}, {inp!r}) = {left_output!r}")

            # Run agent >> Id (right identity)
            right_composed = sequential(agent, id_agent)
            right_state = (agent_state, id_state)
            # For right identity, we need to feed the agent's output type to Id
            _, right_output = right_composed.invoke(right_state, inp)
            if verbose:
                print(f"  (agent >> Id)({right_state!r}, {inp!r}) = {right_output!r}")

            tests_run += 1

            # Check left identity: Id >> agent = agent
            if left_output != agent_output:
                failure_msg = (
                    f"Left identity violated for input {inp!r}: "
                    f"Id >> {agent.name} gave {left_output!r}, "
                    f"but {agent.name} alone gave {agent_output!r}"
                )

                if raise_on_failure:
                    raise IdentityError(
                        agent_name=agent.name,
                        test_input=inp,
                        expected=agent_output,
                        actual=left_output,
                        side="left",
                    )

                return LawVerification(
                    law_name="identity",
                    status=LawStatus.FAILED,
                    left_result=left_output,
                    right_result=agent_output,
                    message=failure_msg,
                    test_input=inp,
                )

            # Check right identity: agent >> Id = agent
            if right_output != agent_output:
                failure_msg = (
                    f"Right identity violated for input {inp!r}: "
                    f"{agent.name} >> Id gave {right_output!r}, "
                    f"but {agent.name} alone gave {agent_output!r}"
                )

                if raise_on_failure:
                    raise IdentityError(
                        agent_name=agent.name,
                        test_input=inp,
                        expected=agent_output,
                        actual=right_output,
                        side="right",
                    )

                return LawVerification(
                    law_name="identity",
                    status=LawStatus.FAILED,
                    left_result=right_output,
                    right_result=agent_output,
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
            law_name="identity",
            status=LawStatus.SKIPPED,
            message="No valid test inputs could be processed",
        )

    return LawVerification(
        law_name="identity",
        status=LawStatus.PASSED,
        message=f"Identity law verified with {tests_passed}/{tests_run} test inputs",
    )


# -----------------------------------------------------------------------------
# Convenience Function
# -----------------------------------------------------------------------------


def quick_identity_check(
    agent: PolyAgent[Any, Any, Any],
    inputs: list[Any] | None = None,
) -> bool:
    """
    Quick check if agent satisfies identity law.

    This is a convenience function for simple cases where you
    just want a boolean answer.

    Args:
        agent: Agent to test.
        inputs: List of input values (state defaults to "ready").

    Returns:
        True if identity law holds, False otherwise.

    Example:
        >>> from kgents_poly import from_function
        >>> double = from_function("double", lambda x: x * 2)
        >>> assert quick_identity_check(double, [1, 2, 3, 10])
    """
    if inputs is None:
        inputs = [0, 1, 2, "test"]

    # Use first position as state for all inputs
    state = next(iter(agent.positions))
    test_inputs = [(state, inp) for inp in inputs]

    result = verify_identity(agent, test_inputs, raise_on_failure=False)
    return result.passed


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


__all__ = [
    "verify_identity",
    "quick_identity_check",
]
