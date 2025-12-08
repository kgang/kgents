"""
Regression Validator: Validates evolved code preserves behavior.

Integrates T-gents RegressionOracle and PropertyAgent to ensure evolved
code maintains the same behavior as the original on known inputs, and
satisfies key invariants on random inputs.

Part of SYNERGY_REFACTOR_PLAN Phase 4A: E-gents → T-gents integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional, TypeVar

from runtime.base import Agent
from agents.t.oracle import RegressionOracle, DiffResult

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass(frozen=True)
class RegressionInput(Generic[A]):
    """Input for regression validation."""
    test_inputs: tuple[A, ...]
    equality_fn: Optional[Callable[[Any, Any], bool]] = None


@dataclass(frozen=True)
class PropertyResult:
    """Result of a single property test."""
    property_name: str
    passed: bool
    failing_input: Optional[Any] = None
    error_message: str = ""


@dataclass(frozen=True)
class RegressionResult(Generic[B]):
    """Result of regression validation."""
    passed: bool
    regression_results: tuple[DiffResult[B], ...]
    property_results: tuple[PropertyResult, ...]
    summary: str

    @property
    def has_regressions(self) -> bool:
        """Check if any regression was detected."""
        return any(not r.all_agree for r in self.regression_results)

    @property
    def failed_properties(self) -> list[str]:
        """Get names of failed property tests."""
        return [p.property_name for p in self.property_results if not p.passed]


class EvolutionValidator(Generic[A, B]):
    """
    Validate evolved code preserves behavior and invariants.

    Combines regression testing (compare outputs on known inputs) with
    property testing (verify invariants on random inputs).

    Usage:
        validator = EvolutionValidator(
            original_agent=OldImplementation(),
            evolved_agent=NewImplementation(),
        )

        result = await validator.validate(
            test_inputs=[input1, input2, input3],
            properties=[
                ("type_preserved", lambda i, o: isinstance(o, str)),
                ("no_exceptions", lambda i, o: o is not None),
            ]
        )

        if not result.passed:
            print(f"Validation failed: {result.summary}")
    """

    def __init__(
        self,
        original_agent: Agent[A, B],
        evolved_agent: Agent[A, B],
        equality_fn: Optional[Callable[[B, B], bool]] = None,
    ):
        """
        Initialize the validator.

        Args:
            original_agent: The reference implementation
            evolved_agent: The evolved implementation to test
            equality_fn: Function to compare outputs (default: ==)
        """
        self.original = original_agent
        self.evolved = evolved_agent
        self.equality_fn = equality_fn or (lambda a, b: a == b)

        # Create regression oracle
        self.regression_oracle = RegressionOracle(
            reference=original_agent,
            system_under_test=evolved_agent,
            equality_fn=self.equality_fn,
        )

    async def validate(
        self,
        test_inputs: List[A],
        properties: Optional[List[tuple[str, Callable[[A, B], bool]]]] = None,
    ) -> RegressionResult[B]:
        """
        Run full validation suite.

        Args:
            test_inputs: Known inputs to test for regression
            properties: Optional list of (name, predicate) pairs for property testing

        Returns:
            RegressionResult with all test results
        """
        regression_results: List[DiffResult[B]] = []
        property_results: List[PropertyResult] = []

        # 1. Regression tests: evolved should match original on known inputs
        for test_input in test_inputs:
            result = await self.regression_oracle.invoke((test_input, []))
            regression_results.append(result)

        # 2. Property tests: verify invariants hold
        if properties:
            for prop_name, prop_fn in properties:
                prop_result = await self._test_property(
                    prop_name, prop_fn, test_inputs
                )
                property_results.append(prop_result)

        # Determine overall pass/fail
        regressions_passed = all(r.all_agree for r in regression_results)
        properties_passed = all(p.passed for p in property_results)
        passed = regressions_passed and properties_passed

        # Generate summary
        summary_parts = []
        if not regressions_passed:
            failed_count = sum(1 for r in regression_results if not r.all_agree)
            summary_parts.append(
                f"Regression: {failed_count}/{len(regression_results)} inputs differ"
            )
        else:
            summary_parts.append(
                f"Regression: all {len(regression_results)} inputs match"
            )

        if properties:
            failed_props = [p.property_name for p in property_results if not p.passed]
            if failed_props:
                summary_parts.append(f"Properties failed: {', '.join(failed_props)}")
            else:
                summary_parts.append(
                    f"Properties: all {len(properties)} passed"
                )

        return RegressionResult(
            passed=passed,
            regression_results=tuple(regression_results),
            property_results=tuple(property_results),
            summary="; ".join(summary_parts),
        )

    async def _test_property(
        self,
        name: str,
        prop_fn: Callable[[A, B], bool],
        inputs: List[A],
    ) -> PropertyResult:
        """Test a property on all inputs."""
        for test_input in inputs:
            try:
                output = await self.evolved.invoke(test_input)
                if not prop_fn(test_input, output):
                    return PropertyResult(
                        property_name=name,
                        passed=False,
                        failing_input=test_input,
                        error_message=f"Property '{name}' failed on input",
                    )
            except Exception as e:
                return PropertyResult(
                    property_name=name,
                    passed=False,
                    failing_input=test_input,
                    error_message=f"Exception during property test: {e}",
                )

        return PropertyResult(property_name=name, passed=True)


# --- Standard Properties ---


def type_preserved(expected_type: type) -> Callable[[Any, Any], bool]:
    """Property: output should be of expected type."""
    return lambda _input, output: isinstance(output, expected_type)


def not_none() -> Callable[[Any, Any], bool]:
    """Property: output should not be None."""
    return lambda _input, output: output is not None


def no_exception() -> Callable[[Any, Any], bool]:
    """
    Property: invocation should not raise exception.

    Note: This is implicitly checked by the validator,
    but can be used for documentation.
    """
    return lambda _input, output: True


def output_length_preserved() -> Callable[[Any, Any], bool]:
    """Property: output length should match input length."""
    return lambda input_, output: len(output) == len(input_)


def output_not_empty() -> Callable[[Any, Any], bool]:
    """Property: output should not be empty."""
    return lambda _input, output: bool(output)


# --- Quick Validation Functions ---


async def validate_evolution(
    original: Agent[A, B],
    evolved: Agent[A, B],
    test_inputs: List[A],
    equality_fn: Optional[Callable[[B, B], bool]] = None,
) -> RegressionResult[B]:
    """
    Quick validation of an evolved agent.

    Args:
        original: Reference implementation
        evolved: Evolved implementation
        test_inputs: Inputs to test
        equality_fn: Optional custom equality function

    Returns:
        RegressionResult
    """
    validator = EvolutionValidator(original, evolved, equality_fn)
    return await validator.validate(test_inputs)


async def check_regression(
    original: Agent[A, B],
    evolved: Agent[A, B],
    test_input: A,
    equality_fn: Optional[Callable[[B, B], bool]] = None,
) -> bool:
    """
    Quick check if evolved agent matches original on a single input.

    Args:
        original: Reference implementation
        evolved: Evolved implementation
        test_input: Single input to test
        equality_fn: Optional custom equality function

    Returns:
        True if outputs match, False otherwise
    """
    oracle = RegressionOracle(original, evolved, equality_fn)
    result = await oracle.invoke((test_input, []))
    return result.all_agree
