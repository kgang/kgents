"""
T-gents: Law Validator - Categorical property verification.

This module provides agents that validate categorical laws:
- Associativity: (f >> g) >> h ≡ f >> (g >> h)
- Identity: f >> id ≡ f ≡ id >> f
- Functor laws: F(id) = id, F(g . f) = F(g) . F(f)
- Monad laws: Left identity, right identity, associativity

Cross-pollination T2.6: Validates agent pipeline categorical laws.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Protocol, TypeVar

logger = logging.getLogger(__name__)

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
A_contra = TypeVar("A_contra", contravariant=True)
B_co = TypeVar("B_co", covariant=True)


# --- Law Validation Results ---


@dataclass
class LawViolation:
    """Evidence of a categorical law violation."""

    law_name: str
    description: str
    left_result: Any
    right_result: Any
    evidence: str

    def __str__(self) -> str:
        return (
            f"❌ {self.law_name} violation: {self.description}\n"
            f"   Left side: {self.left_result}\n"
            f"   Right side: {self.right_result}\n"
            f"   Evidence: {self.evidence}"
        )


@dataclass
class LawValidationReport:
    """Results of categorical law validation."""

    laws_checked: list[str]
    violations: list[LawViolation]
    passed: bool

    @property
    def total_laws(self) -> int:
        return len(self.laws_checked)

    @property
    def violations_count(self) -> int:
        return len(self.violations)

    @property
    def passed_count(self) -> int:
        return self.total_laws - self.violations_count

    def __str__(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        summary = f"{status} ({self.passed_count}/{self.total_laws} laws verified)\n"

        if self.violations:
            summary += "\nViolations:\n"
            for v in self.violations:
                summary += f"  {v}\n"

        return summary


# --- Agent Protocol (for law checking) ---


class AgentLike(Protocol[A_contra, B_co]):
    """Protocol for composable agents."""

    async def run(self, input_data: A_contra) -> B_co:
        """Execute the agent."""
        ...


# --- Associativity Law ---


async def check_associativity(
    f: AgentLike[A, B],
    g: AgentLike[B, C],
    h: AgentLike[C, Any],
    test_input: A,
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify associativity: (f >> g) >> h ≡ f >> (g >> h)

    Args:
        f, g, h: Three composable agents
        test_input: Input to test with
        equality_fn: Custom equality checker (default: ==)

    Returns:
        LawViolation if law violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Left side: (f >> g) >> h
        fg_result = await g.run(await f.run(test_input))
        left_result = await h.run(fg_result)

        # Right side: f >> (g >> h)
        f_result = await f.run(test_input)
        gh_result = await h.run(await g.run(f_result))
        right_result = gh_result

        if not equality_fn(left_result, right_result):
            return LawViolation(
                law_name="Associativity",
                description="(f >> g) >> h ≠ f >> (g >> h)",
                left_result=left_result,
                right_result=right_result,
                evidence=f"Input: {test_input}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Associativity",
            description="Exception during associativity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


# --- Identity Law ---


async def check_left_identity(
    agent: AgentLike[A, B],
    test_input: A,
    equality_fn: Callable[[B, B], bool] | None = None,
) -> LawViolation | None:
    """
    Verify left identity: agent(input) should not be affected by prepending identity.

    Args:
        agent: Agent to test
        test_input: Input to test with
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Direct application
        direct_result = await agent.run(test_input)

        # With identity prepended (identity just returns input)
        identity_result = test_input  # id(test_input) = test_input
        composed_result = await agent.run(identity_result)

        if not equality_fn(direct_result, composed_result):
            return LawViolation(
                law_name="Left Identity",
                description="id >> agent ≠ agent",
                left_result=direct_result,
                right_result=composed_result,
                evidence=f"Input: {test_input}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Left Identity",
            description="Exception during left identity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


async def check_right_identity(
    agent: AgentLike[A, B],
    test_input: A,
    equality_fn: Callable[[B, B], bool] | None = None,
) -> LawViolation | None:
    """
    Verify right identity: agent(input) should equal (agent >> id)(input).

    Args:
        agent: Agent to test
        test_input: Input to test with
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Direct application
        direct_result = await agent.run(test_input)

        # With identity appended (identity returns its input unchanged)
        composed_result = direct_result  # id(agent(input)) = agent(input)

        if not equality_fn(direct_result, composed_result):
            return LawViolation(
                law_name="Right Identity",
                description="agent >> id ≠ agent",
                left_result=direct_result,
                right_result=composed_result,
                evidence=f"Input: {test_input}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Right Identity",
            description="Exception during right identity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


# --- Functor Laws ---


async def check_functor_identity(
    functor_map: Callable[[Callable[[A], A]], Callable[[Any], Any]],
    test_value: Any,
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify functor identity law: F(id) = id.

    Args:
        functor_map: The functor's map operation
        test_value: Value to test with
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # F(id)(value) should equal value
        def identity(x: A) -> A:
            return x

        mapped = functor_map(identity)
        result = mapped(test_value)

        if not equality_fn(result, test_value):
            return LawViolation(
                law_name="Functor Identity",
                description="F(id) ≠ id",
                left_result=result,
                right_result=test_value,
                evidence=f"Input: {test_value}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Functor Identity",
            description="Exception during functor identity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


async def check_functor_composition(
    functor_map: Callable[[Callable[..., Any]], Callable[..., Any]],
    f: Callable[[A], B],
    g: Callable[[B], C],
    test_value: Any,
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify functor composition law: F(g . f) = F(g) . F(f).

    Args:
        functor_map: The functor's map operation
        f: First function
        g: Second function
        test_value: Value to test with
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Left side: F(g . f)(value)
        def composed_fn(x: A) -> C:
            return g(f(x))

        left_result = functor_map(composed_fn)(test_value)

        # Right side: F(g)(F(f)(value))
        f_mapped = functor_map(f)(test_value)
        right_result = functor_map(g)(f_mapped)

        if not equality_fn(left_result, right_result):
            return LawViolation(
                law_name="Functor Composition",
                description="F(g . f) ≠ F(g) . F(f)",
                left_result=left_result,
                right_result=right_result,
                evidence=f"Input: {test_value}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Functor Composition",
            description="Exception during functor composition check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


# --- Monad Laws ---


async def check_monad_left_identity(
    unit: Callable[[A], Any],  # A -> M[A]
    bind: Callable[[Any, Callable[..., Any]], Any],  # M[A] -> (A -> M[B]) -> M[B]
    f: Callable[[A], Any],  # A -> M[B]
    test_value: A,
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify monad left identity: unit(a).bind(f) ≡ f(a).

    Args:
        unit: The monad's unit/return operation
        bind: The monad's bind operation
        f: Function to bind
        test_value: Value to test with
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Left side: unit(a).bind(f)
        left_result = bind(unit(test_value), f)

        # Right side: f(a)
        right_result = f(test_value)

        if not equality_fn(left_result, right_result):
            return LawViolation(
                law_name="Monad Left Identity",
                description="unit(a).bind(f) ≠ f(a)",
                left_result=left_result,
                right_result=right_result,
                evidence=f"Input: {test_value}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Monad Left Identity",
            description="Exception during monad left identity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


async def check_monad_right_identity(
    unit: Callable[[A], Any],
    bind: Callable[[Any, Callable[..., Any]], Any],
    m: Any,  # M[A]
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify monad right identity: m.bind(unit) ≡ m.

    Args:
        unit: The monad's unit/return operation
        bind: The monad's bind operation
        m: Monadic value to test
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Left side: m.bind(unit)
        left_result = bind(m, unit)

        # Right side: m
        right_result = m

        if not equality_fn(left_result, right_result):
            return LawViolation(
                law_name="Monad Right Identity",
                description="m.bind(unit) ≠ m",
                left_result=left_result,
                right_result=right_result,
                evidence=f"Input: {m}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Monad Right Identity",
            description="Exception during monad right identity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


async def check_monad_associativity(
    bind: Callable[[Any, Callable[..., Any]], Any],
    m: Any,  # M[A]
    f: Callable[[Any], Any],  # A -> M[B]
    g: Callable[[Any], Any],  # B -> M[C]
    equality_fn: Callable[[Any, Any], bool] | None = None,
) -> LawViolation | None:
    """
    Verify monad associativity: m.bind(f).bind(g) ≡ m.bind(λa. f(a).bind(g)).

    Args:
        bind: The monad's bind operation
        m: Monadic value to test
        f: First function to bind
        g: Second function to bind
        equality_fn: Custom equality checker

    Returns:
        LawViolation if violated, None otherwise
    """
    equality_fn = equality_fn or (lambda x, y: x == y)

    try:
        # Left side: m.bind(f).bind(g)
        left_intermediate = bind(m, f)
        left_result = bind(left_intermediate, g)

        # Right side: m.bind(λa. f(a).bind(g))
        def composed_fn(a: Any) -> Any:
            return bind(f(a), g)

        right_result = bind(m, composed_fn)

        if not equality_fn(left_result, right_result):
            return LawViolation(
                law_name="Monad Associativity",
                description="m.bind(f).bind(g) ≠ m.bind(λa. f(a).bind(g))",
                left_result=left_result,
                right_result=right_result,
                evidence=f"Input: {m}",
            )

        return None

    except Exception as e:
        return LawViolation(
            law_name="Monad Associativity",
            description="Exception during monad associativity check",
            left_result=None,
            right_result=None,
            evidence=f"Error: {e}",
        )


# --- High-level Law Validator ---


class LawValidator:
    """
    T-gent for validating categorical laws on agents and pipelines.

    Can be used to validate any agent pipeline for categorical law compliance.
    """

    def __init__(self) -> None:
        self.violations: list[LawViolation] = []
        self.laws_checked: list[str] = []

    async def validate_pipeline_associativity(
        self,
        f: AgentLike[A, B],
        g: AgentLike[B, C],
        h: AgentLike[C, Any],
        test_input: A,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Validate associativity for a 3-stage pipeline.

        Returns:
            True if law holds, False otherwise
        """
        self.laws_checked.append("Associativity")
        violation = await check_associativity(f, g, h, test_input, equality_fn)
        if violation:
            self.violations.append(violation)
            return False
        return True

    async def validate_identity_laws(
        self,
        agent: AgentLike[A, B],
        test_input: A,
        equality_fn: Callable[[B, B], bool] | None = None,
    ) -> bool:
        """
        Validate left and right identity laws.

        Returns:
            True if both laws hold, False otherwise
        """
        self.laws_checked.extend(["Left Identity", "Right Identity"])

        left_violation = await check_left_identity(agent, test_input, equality_fn)
        if left_violation:
            self.violations.append(left_violation)

        right_violation = await check_right_identity(agent, test_input, equality_fn)
        if right_violation:
            self.violations.append(right_violation)

        return not (left_violation or right_violation)

    def get_report(self) -> LawValidationReport:
        """Generate validation report."""
        return LawValidationReport(
            laws_checked=self.laws_checked,
            violations=self.violations,
            passed=len(self.violations) == 0,
        )

    def reset(self) -> None:
        """Reset validator state."""
        self.violations = []
        self.laws_checked = []


# --- Generic Pipeline Law Validator ---


async def validate_evolution_pipeline_laws(
    ground_stage: AgentLike[Any, Any],
    hypothesis_stage: AgentLike[Any, Any],
    experiment_stage: AgentLike[Any, Any],
    test_input: Any,
) -> LawValidationReport:
    """
    Validate categorical laws for a 3-stage pipeline.

    Validates that stage_1 >> stage_2 >> stage_3 satisfies
    associativity and identity laws.

    Args:
        ground_stage: The first stage agent
        hypothesis_stage: The second stage agent
        experiment_stage: The third stage agent
        test_input: Test input for the pipeline

    Returns:
        LawValidationReport with results
    """
    validator = LawValidator()

    logger.info("🔍 Validating pipeline categorical laws...")

    # Check associativity: (Ground >> Hypothesis) >> Experiment ≡ Ground >> (Hypothesis >> Experiment)
    await validator.validate_pipeline_associativity(
        ground_stage,
        hypothesis_stage,
        experiment_stage,
        test_input,
    )

    # Check identity laws for each stage
    await validator.validate_identity_laws(ground_stage, test_input)

    report = validator.get_report()
    logger.info(
        f"Law validation complete: {report.passed_count}/{report.total_laws} passed"
    )

    return report
