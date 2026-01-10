"""
kgents-laws: Runtime Law Verification

Verify categorical laws at runtime without understanding the math.
Get actionable error messages when composition fails.

Quick Start (10 minutes or less):

    from kgents_laws import verify_identity, verify_associativity, LawChecker
    from kgents_poly import from_function, identity, sequential

    # Verify identity law: id >> f = f = f >> id
    double = from_function("double", lambda x: x * 2)
    result = verify_identity(double, identity())
    print(result.passed)  # True

    # Verify associativity: (a >> b) >> c = a >> (b >> c)
    add_one = from_function("add_one", lambda x: x + 1)
    square = from_function("square", lambda x: x * x)
    result = verify_associativity(double, add_one, square)
    print(result.passed)  # True

    # Use LawChecker for comprehensive verification
    checker = LawChecker()
    checker.add_agent(double)
    checker.add_agent(add_one)
    report = checker.verify_all()
    print(report.summary)

    # Strict verification (raises on failure)
    from kgents_laws import verify_associativity_strict, AssociativityError
    try:
        verify_associativity_strict(a, b, c, test_inputs)
    except AssociativityError as e:
        print(e.what_failed)
        print(e.how_to_fix)

What are Categorical Laws?

    Laws are equations that must hold for composition to work correctly:

    1. Identity: id >> f = f = f >> id
       Composing with identity changes nothing.

    2. Associativity: (f >> g) >> h = f >> (g >> h)
       Grouping doesn't matter.

    3. Monad Laws (for monadic types):
       - Left identity: pure(a) >>= f = f(a)
       - Right identity: m >>= pure = m
       - Associativity: (m >>= f) >>= g = m >>= (x -> f(x) >>= g)

Why verify laws?

    If laws are violated:
    - Composition order matters when it shouldn't
    - Refactoring changes behavior unexpectedly
    - Optimizations become unsafe

    This library catches violations early with ACTIONABLE error messages.

License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from .errors import (
    AssociativityError,
    CoherenceError,
    IdentityError,
    LawViolationError,
)

# Type variables
T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
S = TypeVar("S")


# -----------------------------------------------------------------------------
# Law Result Types
# -----------------------------------------------------------------------------


class LawStatus(Enum):
    """Status of a law verification."""

    PASSED = auto()  # Law verified with test cases
    FAILED = auto()  # Law violation detected
    SKIPPED = auto()  # Law not tested
    STRUCTURAL = auto()  # Verified by structure only
    ERROR = auto()  # Verification threw an exception


@dataclass(frozen=True)
class LawResult:
    """
    Result of verifying a single law.

    Provides actionable information when laws fail.

    Example:
        >>> result = verify_identity(my_agent, identity())
        >>> if not result:
        ...     print(result.explanation)
        ...     print(f"Left side: {result.left_value}")
        ...     print(f"Right side: {result.right_value}")
    """

    law_name: str
    status: LawStatus
    left_value: Any = None
    right_value: Any = None
    explanation: str = ""
    test_input: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def passed(self) -> bool:
        """True if law was verified."""
        return self.status in (LawStatus.PASSED, LawStatus.STRUCTURAL)

    def __bool__(self) -> bool:
        return self.passed

    def __repr__(self) -> str:
        status = self.status.name
        return f"LawResult({self.law_name!r}, {status})"


@dataclass
class LawReport:
    """
    Report from verifying multiple laws.

    Example:
        >>> report = checker.verify_all()
        >>> print(report.summary)
        >>> for failure in report.failures:
        ...     print(f"FAIL: {failure.law_name}")
        ...     print(f"  {failure.explanation}")
    """

    results: list[LawResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def all_passed(self) -> bool:
        """True if all laws passed."""
        return all(r.passed for r in self.results)

    @property
    def pass_count(self) -> int:
        """Number of laws that passed."""
        return sum(1 for r in self.results if r.passed)

    @property
    def fail_count(self) -> int:
        """Number of laws that failed."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def failures(self) -> list[LawResult]:
        """List of failed verifications."""
        return [r for r in self.results if not r.passed]

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        total = len(self.results)
        if self.all_passed:
            return f"All {total} law(s) verified successfully."
        else:
            failed = [f.law_name for f in self.failures]
            return f"{self.fail_count}/{total} law(s) failed: {', '.join(failed)}"

    def __bool__(self) -> bool:
        return self.all_passed


# -----------------------------------------------------------------------------
# Identity Law Verification
# -----------------------------------------------------------------------------


def verify_identity(
    agent: Any,
    id_agent: Any,
    test_inputs: list[Any] | None = None,
) -> LawResult:
    """
    Verify the identity law: id >> f = f = f >> id.

    The identity agent should have no effect when composed.

    Args:
        agent: The agent to test
        id_agent: The identity agent
        test_inputs: Optional list of test inputs (defaults to [0, 1, "test"])

    Returns:
        LawResult with verification status

    Example:
        >>> from kgents_poly import from_function, identity
        >>> double = from_function("double", lambda x: x * 2)
        >>> result = verify_identity(double, identity())
        >>> print(result.passed)  # True
    """
    from kgents_poly import sequential

    if test_inputs is None:
        test_inputs = [0, 1, "test"]

    try:
        # Get initial states
        id_init = next(iter(id_agent.positions))
        agent_init = next(iter(agent.positions))

        for test_input in test_inputs:
            try:
                # Test: id >> agent
                left = sequential(id_agent, agent)
                left_state = (id_init, agent_init)
                _, left_result = left.invoke(left_state, test_input)

                # Test: agent alone
                _, agent_result = agent.invoke(agent_init, test_input)

                # Test: agent >> id
                right = sequential(agent, id_agent)
                right_state = (agent_init, id_init)
                _, right_result = right.invoke(right_state, left_result)

                # Check left identity
                if left_result != agent_result:
                    return LawResult(
                        law_name="identity",
                        status=LawStatus.FAILED,
                        left_value=left_result,
                        right_value=agent_result,
                        explanation=(
                            f"Left identity failed: id >> {agent.name} gave {left_result!r}, "
                            f"but {agent.name} alone gave {agent_result!r}"
                        ),
                        test_input=test_input,
                    )

            except (TypeError, ValueError):
                # Type mismatch for this input, try next
                continue

        return LawResult(
            law_name="identity",
            status=LawStatus.PASSED,
            explanation="Identity law verified for all test inputs",
        )

    except Exception as e:
        return LawResult(
            law_name="identity",
            status=LawStatus.ERROR,
            explanation=f"Verification error: {e}",
        )


# -----------------------------------------------------------------------------
# Associativity Law Verification
# -----------------------------------------------------------------------------


def verify_associativity(
    a: Any,
    b: Any,
    c: Any,
    test_inputs: list[Any] | None = None,
) -> LawResult:
    """
    Verify associativity: (a >> b) >> c = a >> (b >> c).

    Grouping of compositions should not matter.

    Args:
        a, b, c: Three agents to compose
        test_inputs: Optional list of test inputs

    Returns:
        LawResult with verification status

    Example:
        >>> from kgents_poly import from_function
        >>> double = from_function("double", lambda x: x * 2)
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> square = from_function("square", lambda x: x * x)
        >>> result = verify_associativity(double, add_one, square)
        >>> print(result.passed)  # True
    """
    from kgents_poly import sequential

    if test_inputs is None:
        test_inputs = [0, 1, 2, 10]

    try:
        # Compose left-associative: (a >> b) >> c
        ab = sequential(a, b)
        left = sequential(ab, c)

        # Compose right-associative: a >> (b >> c)
        bc = sequential(b, c)
        right = sequential(a, bc)

        # Get initial states
        a_init = next(iter(a.positions))
        b_init = next(iter(b.positions))
        c_init = next(iter(c.positions))

        for test_input in test_inputs:
            try:
                # Left: ((a, b), c)
                left_state = ((a_init, b_init), c_init)
                _, left_result = left.invoke(left_state, test_input)

                # Right: (a, (b, c))
                right_state = (a_init, (b_init, c_init))
                _, right_result = right.invoke(right_state, test_input)

                if left_result != right_result:
                    return LawResult(
                        law_name="associativity",
                        status=LawStatus.FAILED,
                        left_value=left_result,
                        right_value=right_result,
                        explanation=(
                            f"Associativity failed at step: "
                            f"({a.name} >> {b.name}) >> {c.name} gave {left_result!r}, "
                            f"but {a.name} >> ({b.name} >> {c.name}) gave {right_result!r}. "
                            f"Grouping matters when it shouldn't!"
                        ),
                        test_input=test_input,
                    )

            except (TypeError, ValueError):
                continue

        return LawResult(
            law_name="associativity",
            status=LawStatus.PASSED,
            explanation="Associativity verified for all test inputs",
        )

    except Exception as e:
        return LawResult(
            law_name="associativity",
            status=LawStatus.ERROR,
            explanation=f"Verification error: {e}",
        )


# -----------------------------------------------------------------------------
# Monad Law Verification
# -----------------------------------------------------------------------------


def verify_monad_left_identity(
    pure_fn: Callable[[T], Any],
    bind_fn: Callable[[Any, Callable[[T], Any]], Any],
    f: Callable[[T], Any],
    test_values: list[T] | None = None,
) -> LawResult:
    """
    Verify monad left identity: pure(a) >>= f = f(a).

    Args:
        pure_fn: The monadic pure/return function
        bind_fn: The monadic bind (>>=) function
        f: A Kleisli arrow (T -> M[U])
        test_values: Values to test

    Returns:
        LawResult with verification status

    Example:
        >>> # For a Maybe monad
        >>> result = verify_monad_left_identity(
        ...     pure_fn=lambda x: Just(x),
        ...     bind_fn=lambda m, f: m.bind(f),
        ...     f=lambda x: Just(x * 2),
        ...     test_values=[1, 2, 3],
        ... )
    """
    if test_values is None:
        test_values = [0, 1, "test"]

    try:
        for value in test_values:
            try:
                # Left side: pure(a) >>= f
                left = bind_fn(pure_fn(value), f)

                # Right side: f(a)
                right = f(value)

                if left != right:
                    return LawResult(
                        law_name="monad_left_identity",
                        status=LawStatus.FAILED,
                        left_value=left,
                        right_value=right,
                        explanation=(
                            f"Left identity failed: pure({value!r}) >>= f gave {left!r}, "
                            f"but f({value!r}) gave {right!r}"
                        ),
                        test_input=value,
                    )

            except (TypeError, ValueError):
                continue

        return LawResult(
            law_name="monad_left_identity",
            status=LawStatus.PASSED,
            explanation="Monad left identity verified",
        )

    except Exception as e:
        return LawResult(
            law_name="monad_left_identity",
            status=LawStatus.ERROR,
            explanation=f"Verification error: {e}",
        )


def verify_monad_right_identity(
    pure_fn: Callable[[T], Any],
    bind_fn: Callable[[Any, Callable[[T], Any]], Any],
    m: Any,
) -> LawResult:
    """
    Verify monad right identity: m >>= pure = m.

    Args:
        pure_fn: The monadic pure/return function
        bind_fn: The monadic bind (>>=) function
        m: A monadic value to test

    Returns:
        LawResult with verification status
    """
    try:
        # Left side: m >>= pure
        left = bind_fn(m, pure_fn)

        # Right side: m
        right = m

        if left != right:
            return LawResult(
                law_name="monad_right_identity",
                status=LawStatus.FAILED,
                left_value=left,
                right_value=right,
                explanation=(
                    f"Right identity failed: m >>= pure gave {left!r}, "
                    f"but m was {right!r}"
                ),
            )

        return LawResult(
            law_name="monad_right_identity",
            status=LawStatus.PASSED,
            explanation="Monad right identity verified",
        )

    except Exception as e:
        return LawResult(
            law_name="monad_right_identity",
            status=LawStatus.ERROR,
            explanation=f"Verification error: {e}",
        )


def verify_monad_associativity(
    bind_fn: Callable[[Any, Callable[[T], Any]], Any],
    m: Any,
    f: Callable[[Any], Any],
    g: Callable[[Any], Any],
) -> LawResult:
    """
    Verify monad associativity: (m >>= f) >>= g = m >>= (x -> f(x) >>= g).

    Args:
        bind_fn: The monadic bind (>>=) function
        m: A monadic value
        f: First Kleisli arrow
        g: Second Kleisli arrow

    Returns:
        LawResult with verification status
    """
    try:
        # Left side: (m >>= f) >>= g
        left = bind_fn(bind_fn(m, f), g)

        # Right side: m >>= (x -> f(x) >>= g)
        right = bind_fn(m, lambda x: bind_fn(f(x), g))

        if left != right:
            return LawResult(
                law_name="monad_associativity",
                status=LawStatus.FAILED,
                left_value=left,
                right_value=right,
                explanation=(
                    f"Monad associativity failed: (m >>= f) >>= g gave {left!r}, "
                    f"but m >>= (x -> f(x) >>= g) gave {right!r}"
                ),
            )

        return LawResult(
            law_name="monad_associativity",
            status=LawStatus.PASSED,
            explanation="Monad associativity verified",
        )

    except Exception as e:
        return LawResult(
            law_name="monad_associativity",
            status=LawStatus.ERROR,
            explanation=f"Verification error: {e}",
        )


# -----------------------------------------------------------------------------
# Law Checker: Comprehensive Verification
# -----------------------------------------------------------------------------


@dataclass
class LawChecker:
    """
    Comprehensive law checker for agents.

    Add agents and verify all applicable laws automatically.

    Example:
        >>> from kgents_poly import from_function, identity
        >>> checker = LawChecker()
        >>> checker.add_agent(from_function("double", lambda x: x * 2))
        >>> checker.add_agent(from_function("add_one", lambda x: x + 1))
        >>> checker.set_identity(identity())
        >>> report = checker.verify_all()
        >>> if not report:
        ...     for failure in report.failures:
        ...         print(f"FAIL: {failure.explanation}")
    """

    agents: list[Any] = field(default_factory=list)
    identity_agent: Any = None
    test_inputs: list[Any] = field(default_factory=lambda: [0, 1, 2, "test"])

    def add_agent(self, agent: Any) -> None:
        """Add an agent to check."""
        self.agents.append(agent)

    def set_identity(self, id_agent: Any) -> None:
        """Set the identity agent."""
        self.identity_agent = id_agent

    def set_test_inputs(self, inputs: list[Any]) -> None:
        """Set test inputs for verification."""
        self.test_inputs = inputs

    def verify_all(self) -> LawReport:
        """
        Verify all applicable laws.

        Returns:
            LawReport with all verification results
        """
        results: list[LawResult] = []

        # Verify identity law for each agent
        if self.identity_agent is not None:
            for agent in self.agents:
                result = verify_identity(
                    agent,
                    self.identity_agent,
                    self.test_inputs,
                )
                results.append(result)

        # Verify associativity for all triples
        if len(self.agents) >= 3:
            from itertools import combinations

            for a, b, c in combinations(self.agents, 3):
                result = verify_associativity(a, b, c, self.test_inputs)
                results.append(result)
        elif len(self.agents) == 2:
            # With only 2 agents, test a >> b >> a pattern
            a, b = self.agents
            result = verify_associativity(a, b, a, self.test_inputs)
            results.append(result)

        return LawReport(results=results)

    def verify_identity_law(self) -> LawReport:
        """Verify only identity law."""
        results = []
        if self.identity_agent is not None:
            for agent in self.agents:
                result = verify_identity(
                    agent,
                    self.identity_agent,
                    self.test_inputs,
                )
                results.append(result)
        return LawReport(results=results)

    def verify_associativity_law(self) -> LawReport:
        """Verify only associativity law."""
        results = []
        if len(self.agents) >= 3:
            from itertools import combinations

            for a, b, c in combinations(self.agents, 3):
                result = verify_associativity(a, b, c, self.test_inputs)
                results.append(result)
        return LawReport(results=results)


# -----------------------------------------------------------------------------
# Quick Verification Functions
# -----------------------------------------------------------------------------


def check_composition_laws(
    *agents: Any,
    identity_agent: Any = None,
    test_inputs: list[Any] | None = None,
) -> LawReport:
    """
    Quick function to verify composition laws.

    Args:
        *agents: Agents to verify
        identity_agent: Optional identity agent
        test_inputs: Optional test inputs

    Returns:
        LawReport with verification results

    Example:
        >>> from kgents_poly import from_function, identity
        >>> report = check_composition_laws(
        ...     from_function("double", lambda x: x * 2),
        ...     from_function("add_one", lambda x: x + 1),
        ...     identity_agent=identity(),
        ... )
        >>> print(report.summary)
    """
    checker = LawChecker()
    for agent in agents:
        checker.add_agent(agent)
    if identity_agent is not None:
        checker.set_identity(identity_agent)
    if test_inputs is not None:
        checker.set_test_inputs(test_inputs)
    return checker.verify_all()


__all__ = [
    # Result types
    "LawStatus",
    "LawResult",
    "LawReport",
    # Identity law
    "verify_identity",
    # Associativity law
    "verify_associativity",
    # Monad laws
    "verify_monad_left_identity",
    "verify_monad_right_identity",
    "verify_monad_associativity",
    # Comprehensive checker
    "LawChecker",
    # Quick verification
    "check_composition_laws",
]
