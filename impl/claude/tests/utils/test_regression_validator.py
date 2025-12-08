"""Tests for E-gents regression validator integration with T-gents."""

import pytest

from runtime.base import Agent
from agents.e.regression_validator import (
    EvolutionValidator,
    validate_evolution,
    check_regression,
    type_preserved,
    not_none,
    output_not_empty,
)


# --- Test Agents ---


class AddOne(Agent[int, int]):
    """Simple agent that adds 1."""

    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input: int) -> int:
        return input + 1


class AddOneEvolved(Agent[int, int]):
    """Evolved version - same behavior."""

    @property
    def name(self) -> str:
        return "AddOneEvolved"

    async def invoke(self, input: int) -> int:
        # Different implementation, same result
        result = input
        result += 1
        return result


class AddOneBroken(Agent[int, int]):
    """Broken evolved version - different behavior."""

    @property
    def name(self) -> str:
        return "AddOneBroken"

    async def invoke(self, input: int) -> int:
        return input + 2  # Bug!


class StringUpper(Agent[str, str]):
    """Agent that uppercases strings."""

    @property
    def name(self) -> str:
        return "StringUpper"

    async def invoke(self, input: str) -> str:
        return input.upper()


class StringUpperEvolved(Agent[str, str]):
    """Evolved version - returns None sometimes."""

    @property
    def name(self) -> str:
        return "StringUpperEvolved"

    async def invoke(self, input: str) -> str:
        if not input:
            return None  # Bug: should return ""
        return input.upper()


# --- Test EvolutionValidator ---


@pytest.mark.asyncio
async def test_validator_passes_same_behavior():
    """Validator should pass when evolved matches original."""
    validator = EvolutionValidator(
        original_agent=AddOne(),
        evolved_agent=AddOneEvolved(),
    )

    result = await validator.validate(test_inputs=[1, 2, 3, 4, 5])

    assert result.passed is True
    assert not result.has_regressions
    assert "all 5 inputs match" in result.summary


@pytest.mark.asyncio
async def test_validator_detects_regression():
    """Validator should detect behavioral differences."""
    validator = EvolutionValidator(
        original_agent=AddOne(),
        evolved_agent=AddOneBroken(),
    )

    result = await validator.validate(test_inputs=[1, 2, 3])

    assert result.passed is False
    assert result.has_regressions
    assert "inputs differ" in result.summary


@pytest.mark.asyncio
async def test_validator_with_properties():
    """Validator should check property invariants."""
    validator = EvolutionValidator(
        original_agent=AddOne(),
        evolved_agent=AddOneEvolved(),
    )

    result = await validator.validate(
        test_inputs=[1, 2, 3],
        properties=[
            ("is_int", type_preserved(int)),
            ("not_none", not_none()),
        ]
    )

    assert result.passed is True
    assert len(result.property_results) == 2
    assert all(p.passed for p in result.property_results)


@pytest.mark.asyncio
async def test_validator_detects_property_violation():
    """Validator should detect property violations."""
    validator = EvolutionValidator(
        original_agent=StringUpper(),
        evolved_agent=StringUpperEvolved(),
    )

    result = await validator.validate(
        test_inputs=["hello", ""],  # Empty string triggers bug
        properties=[
            ("not_none", not_none()),
        ]
    )

    assert result.passed is False
    assert "not_none" in result.failed_properties


@pytest.mark.asyncio
async def test_validator_custom_equality():
    """Validator should use custom equality function."""
    # Create agents that return different types but semantically equal
    class ReturnsInt(Agent[int, int]):
        @property
        def name(self) -> str:
            return "ReturnsInt"

        async def invoke(self, input: int) -> int:
            return input * 2

    class ReturnsFloat(Agent[int, float]):
        @property
        def name(self) -> str:
            return "ReturnsFloat"

        async def invoke(self, input: int) -> float:
            return float(input * 2)

    validator = EvolutionValidator(
        original_agent=ReturnsInt(),
        evolved_agent=ReturnsFloat(),
        equality_fn=lambda a, b: float(a) == float(b),
    )

    result = await validator.validate(test_inputs=[1, 2, 3])
    assert result.passed is True


# --- Test Quick Functions ---


@pytest.mark.asyncio
async def test_validate_evolution_quick():
    """Quick validation function should work."""
    result = await validate_evolution(
        original=AddOne(),
        evolved=AddOneEvolved(),
        test_inputs=[1, 2, 3],
    )

    assert result.passed is True


@pytest.mark.asyncio
async def test_check_regression_single_input():
    """Single input regression check should work."""
    # Same behavior
    assert await check_regression(AddOne(), AddOneEvolved(), 5) is True

    # Different behavior
    assert await check_regression(AddOne(), AddOneBroken(), 5) is False


# --- Test Property Helpers ---


@pytest.mark.asyncio
async def test_type_preserved_property():
    """Type preserved property should check output type."""
    prop = type_preserved(int)

    assert prop(1, 2) is True
    assert prop(1, "string") is False


@pytest.mark.asyncio
async def test_not_none_property():
    """Not none property should check for None."""
    prop = not_none()

    assert prop(1, 2) is True
    assert prop(1, None) is False


@pytest.mark.asyncio
async def test_output_not_empty_property():
    """Output not empty property should check for empty."""
    prop = output_not_empty()

    assert prop("hello", "world") is True
    assert prop("hello", "") is False
    assert prop([1], []) is False


# --- Test RegressionResult Properties ---


@pytest.mark.asyncio
async def test_regression_result_properties():
    """RegressionResult should compute properties correctly."""
    validator = EvolutionValidator(
        original_agent=AddOne(),
        evolved_agent=AddOneBroken(),
    )

    result = await validator.validate(
        test_inputs=[1, 2],
        properties=[
            ("is_int", type_preserved(int)),
        ]
    )

    assert result.has_regressions is True
    assert result.failed_properties == []  # Property passed, regression didn't


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
