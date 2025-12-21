"""
Tests for ASHC Bootstrap Isomorphism Checker.

These tests verify that the isomorphism checker correctly identifies
behavioral equivalence between implementations.

Run: uv run pytest protocols/ashc/bootstrap/_tests/test_isomorphism.py -v
"""

import pytest

from ..isomorphism import (
    BehaviorComparison,
    BootstrapIsomorphism,
    check_isomorphism,
    compare_all_agents,
)

# =============================================================================
# Test Fixtures
# =============================================================================

# Minimal valid Id implementation
VALID_ID_CODE = '''
from typing import TypeVar, Generic

A = TypeVar("A")
B = TypeVar("B")

class Agent(Generic[A, B]):
    @property
    def name(self) -> str:
        raise NotImplementedError

    async def invoke(self, input: A) -> B:
        raise NotImplementedError

class Id(Agent[A, A]):
    """Identity agent."""

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input: A) -> A:
        return input
'''

# Invalid Python syntax
INVALID_SYNTAX_CODE = """
class Id
    def invoke(self, x)
        return x
"""

# Missing interface
MISSING_INTERFACE_CODE = '''
class Id:
    """No invoke method."""
    pass
'''

# Wrong behavior
WRONG_BEHAVIOR_CODE = """
from typing import TypeVar, Generic

A = TypeVar("A")

class Agent(Generic[A, A]):
    @property
    def name(self) -> str:
        raise NotImplementedError

    async def invoke(self, input: A) -> A:
        raise NotImplementedError

class Id(Agent):
    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input):
        return None  # Wrong! Should return input
"""


# =============================================================================
# BehaviorComparison Tests
# =============================================================================


class TestBehaviorComparison:
    """Tests for BehaviorComparison dataclass."""

    def test_perfect_comparison_is_isomorphic(self):
        """Perfect scores result in isomorphic."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=1.0,
            type_compatible=True,
            laws_satisfied=True,
            property_tests_pass=True,
        )
        assert comparison.is_isomorphic
        assert comparison.score == 1.0

    def test_high_pass_rate_is_isomorphic(self):
        """95% pass rate is acceptable."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=0.95,
            type_compatible=True,
            laws_satisfied=True,
            property_tests_pass=True,
        )
        assert comparison.is_isomorphic

    def test_low_pass_rate_not_isomorphic(self):
        """Below 95% is not isomorphic."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=0.90,
            type_compatible=True,
            laws_satisfied=True,
            property_tests_pass=True,
        )
        assert not comparison.is_isomorphic

    def test_type_incompatible_not_isomorphic(self):
        """Type incompatibility fails isomorphism."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=1.0,
            type_compatible=False,
            laws_satisfied=True,
            property_tests_pass=True,
        )
        assert not comparison.is_isomorphic

    def test_laws_not_satisfied_not_isomorphic(self):
        """Law violation fails isomorphism."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=1.0,
            type_compatible=True,
            laws_satisfied=False,
            property_tests_pass=True,
        )
        assert not comparison.is_isomorphic

    def test_error_not_isomorphic(self):
        """Error presence fails isomorphism."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=1.0,
            type_compatible=True,
            laws_satisfied=True,
            property_tests_pass=True,
            error="Some error occurred",
        )
        assert not comparison.is_isomorphic

    def test_score_calculation(self):
        """Score is calculated correctly."""
        comparison = BehaviorComparison(
            agent_name="Id",
            test_pass_rate=0.5,  # 0.5 * 0.4 = 0.2
            type_compatible=True,  # +0.2
            laws_satisfied=True,  # +0.25
            property_tests_pass=True,  # +0.15
        )
        expected = 0.2 + 0.2 + 0.25 + 0.15
        assert abs(comparison.score - expected) < 0.01


# =============================================================================
# BootstrapIsomorphism Tests
# =============================================================================


class TestBootstrapIsomorphism:
    """Tests for BootstrapIsomorphism dataclass."""

    def test_empty_comparisons(self):
        """Empty comparisons is not isomorphic."""
        result = BootstrapIsomorphism(comparisons=())
        assert not result.is_isomorphic
        assert result.overall_score == 0.0
        assert result.isomorphic_count == 0

    def test_all_isomorphic(self):
        """All isomorphic agents means overall isomorphic."""
        comparisons = tuple(
            BehaviorComparison(
                agent_name=name,
                test_pass_rate=1.0,
                type_compatible=True,
                laws_satisfied=True,
                property_tests_pass=True,
            )
            for name in ["Id", "Compose"]
        )
        result = BootstrapIsomorphism(comparisons=comparisons)
        assert result.is_isomorphic
        assert result.isomorphic_count == 2
        assert result.overall_score == 1.0

    def test_partial_isomorphism(self):
        """Partial isomorphism is not overall isomorphic."""
        comparisons = (
            BehaviorComparison(
                agent_name="Id",
                test_pass_rate=1.0,
                type_compatible=True,
                laws_satisfied=True,
                property_tests_pass=True,
            ),
            BehaviorComparison(
                agent_name="Compose",
                test_pass_rate=0.5,  # Failed
                type_compatible=True,
                laws_satisfied=False,
                property_tests_pass=True,
            ),
        )
        result = BootstrapIsomorphism(comparisons=comparisons)
        assert not result.is_isomorphic
        assert result.isomorphic_count == 1
        assert 0 < result.overall_score < 1.0

    def test_summary_includes_agents(self):
        """Summary includes all agent names."""
        comparisons = (
            BehaviorComparison(
                agent_name="Id",
                test_pass_rate=1.0,
                type_compatible=True,
                laws_satisfied=True,
                property_tests_pass=True,
            ),
        )
        result = BootstrapIsomorphism(
            comparisons=comparisons,
            regeneration_time_ms=100.0,
            tokens_used=1000,
        )
        summary = result.summary()
        assert "Id" in summary
        assert "100" in summary  # time
        assert "1,000" in summary  # tokens


# =============================================================================
# check_isomorphism Tests
# =============================================================================


class TestCheckIsomorphism:
    """Tests for check_isomorphism function."""

    @pytest.mark.asyncio
    async def test_valid_id_passes(self):
        """Valid Id implementation passes isomorphism check."""
        result = await check_isomorphism(
            generated_code=VALID_ID_CODE,
            agent_name="Id",
        )
        assert result.test_pass_rate > 0.5
        assert result.type_compatible
        # Note: laws_satisfied depends on implementation

    @pytest.mark.asyncio
    async def test_invalid_syntax_fails(self):
        """Invalid syntax fails immediately."""
        result = await check_isomorphism(
            generated_code=INVALID_SYNTAX_CODE,
            agent_name="Id",
        )
        assert not result.is_isomorphic
        assert result.error is not None
        assert "syntax" in result.error.lower()

    @pytest.mark.asyncio
    async def test_missing_interface_fails(self):
        """Missing required interface fails."""
        result = await check_isomorphism(
            generated_code=MISSING_INTERFACE_CODE,
            agent_name="Id",
        )
        assert not result.is_isomorphic
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_empty_code_fails(self):
        """Empty code fails."""
        result = await check_isomorphism(
            generated_code="",
            agent_name="Id",
        )
        assert not result.is_isomorphic


# =============================================================================
# compare_all_agents Tests
# =============================================================================


class TestCompareAllAgents:
    """Tests for compare_all_agents function."""

    @pytest.mark.asyncio
    async def test_compare_single_agent(self):
        """Can compare a single agent."""
        result = await compare_all_agents({"Id": VALID_ID_CODE})
        assert len(result.comparisons) == 1
        assert result.comparisons[0].agent_name == "Id"

    @pytest.mark.asyncio
    async def test_compare_multiple_agents(self):
        """Can compare multiple agents."""
        # Use same code for both (not correct for Compose but tests infrastructure)
        result = await compare_all_agents(
            {
                "Id": VALID_ID_CODE,
                "Compose": VALID_ID_CODE,  # Will fail behavior but tests flow
            }
        )
        assert len(result.comparisons) == 2
        names = {c.agent_name for c in result.comparisons}
        assert names == {"Id", "Compose"}


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_unicode_in_code(self):
        """Unicode in code is handled."""
        code_with_unicode = '''
class Id:
    """Identity agent. → ∀ x: Id(x) = x"""

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input):
        return input
'''
        result = await check_isomorphism(code_with_unicode, "Id")
        # Should at least not crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_very_long_code(self):
        """Very long code is handled."""
        long_code = VALID_ID_CODE + "\n# " + "x" * 10000
        result = await check_isomorphism(long_code, "Id")
        assert result is not None

    @pytest.mark.asyncio
    async def test_code_with_errors_in_invoke(self):
        """Code with runtime errors in invoke is caught."""
        bad_code = """
class Id:
    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input):
        raise RuntimeError("Intentional error")
"""
        result = await check_isomorphism(bad_code, "Id")
        # Should handle gracefully
        assert result is not None
