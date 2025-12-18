"""
Tests for the K-gent Polynomial Agent.

Tests verify:
1. EigenvectorContext state machine
2. Direction validation at each context
3. Single context queries
4. Full synthesis across all contexts
5. Integration with SOUL_SHEAF
"""

from typing import Any

import pytest

from agents.k.polynomial import (
    EIGENVECTOR_JUDGMENTS,
    EIGENVECTOR_QUESTIONS,
    EIGENVECTOR_VALUES,
    SOUL_POLYNOMIAL,
    EigenvectorContext,
    SoulJudgment,
    SoulPolynomialAgent,
    SoulQuery,
    SoulResponse,
    eigenvector_directions,
    eigenvector_transition,
    from_sheaf_context,
    to_sheaf_context,
)

# =============================================================================
# State Tests
# =============================================================================


class TestEigenvectorContext:
    """Test the EigenvectorContext enum."""

    def test_all_contexts_defined(self) -> None:
        """All seven eigenvector contexts are defined."""
        assert EigenvectorContext.AESTHETIC
        assert EigenvectorContext.CATEGORICAL
        assert EigenvectorContext.GRATITUDE
        assert EigenvectorContext.HETERARCHY
        assert EigenvectorContext.GENERATIVITY
        assert EigenvectorContext.JOY
        assert EigenvectorContext.SYNTHESIZING

    def test_contexts_are_unique(self) -> None:
        """Each context has a unique value."""
        contexts = list(EigenvectorContext)
        values = [c.value for c in contexts]
        assert len(values) == len(set(values))

    def test_six_core_contexts_plus_synthesizing(self) -> None:
        """There are 6 core eigenvector contexts plus SYNTHESIZING."""
        assert len(EigenvectorContext) == 7


# =============================================================================
# Eigenvector Values Tests
# =============================================================================


class TestEigenvectorValues:
    """Test the eigenvector coordinate values."""

    def test_all_values_defined(self) -> None:
        """All core eigenvectors have values."""
        for ctx in EigenvectorContext:
            if ctx != EigenvectorContext.SYNTHESIZING:
                assert ctx in EIGENVECTOR_VALUES

    def test_values_in_range(self) -> None:
        """All values are between 0 and 1."""
        for value in EIGENVECTOR_VALUES.values():
            assert 0.0 <= value <= 1.0

    def test_aesthetic_is_minimalist(self) -> None:
        """Aesthetic value reflects minimalist tendency."""
        assert EIGENVECTOR_VALUES[EigenvectorContext.AESTHETIC] < 0.3

    def test_categorical_is_abstract(self) -> None:
        """Categorical value reflects abstract thinking."""
        assert EIGENVECTOR_VALUES[EigenvectorContext.CATEGORICAL] > 0.8

    def test_all_questions_defined(self) -> None:
        """All contexts have questions."""
        for ctx in EigenvectorContext:
            assert ctx in EIGENVECTOR_QUESTIONS

    def test_all_judgments_defined(self) -> None:
        """All contexts have judgments."""
        for ctx in EigenvectorContext:
            assert ctx in EIGENVECTOR_JUDGMENTS


# =============================================================================
# Direction Tests
# =============================================================================


class TestEigenvectorDirections:
    """Test context-dependent direction validation."""

    def test_all_contexts_accept_soul_query(self) -> None:
        """All contexts accept SoulQuery."""
        for ctx in EigenvectorContext:
            dirs = eigenvector_directions(ctx)
            assert SoulQuery in dirs or type(SoulQuery) in dirs or Any in dirs

    def test_synthesizing_accepts_lists(self) -> None:
        """SYNTHESIZING context accepts lists for partial results."""
        dirs = eigenvector_directions(EigenvectorContext.SYNTHESIZING)
        assert list in dirs or tuple in dirs


# =============================================================================
# Transition Tests
# =============================================================================


class TestEigenvectorTransition:
    """Test the eigenvector state transition function."""

    def test_single_context_returns_response(self) -> None:
        """Single context query returns SoulResponse."""
        query = SoulQuery(message="Should I add this?", depth=1)
        new_state, output = eigenvector_transition(EigenvectorContext.AESTHETIC, query)

        assert isinstance(output, SoulResponse)
        assert len(output.judgments) == 1
        assert output.judgments[0].context == EigenvectorContext.AESTHETIC

    def test_multi_depth_continues_traversal(self) -> None:
        """Depth > 1 continues to next context."""
        query = SoulQuery(message="Test", depth=2)
        new_state, output = eigenvector_transition(EigenvectorContext.AESTHETIC, query)

        # Should transition to next context with partial results
        assert new_state == EigenvectorContext.CATEGORICAL
        assert isinstance(output, tuple)

    def test_synthesizing_produces_full_response(self) -> None:
        """SYNTHESIZING produces response with all judgments."""
        query = SoulQuery(message="What should I do?", depth=6)
        new_state, output = eigenvector_transition(EigenvectorContext.SYNTHESIZING, query)

        assert isinstance(output, SoulResponse)
        assert len(output.judgments) == 6  # All core contexts
        assert output.synthesis is not None

    def test_string_input_wraps_in_query(self) -> None:
        """String input is wrapped in SoulQuery."""
        new_state, output = eigenvector_transition(EigenvectorContext.JOY, "Is this fun?")

        assert isinstance(output, SoulResponse)
        assert output.query.message == "Is this fun?"


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestSoulPolynomial:
    """Test the SOUL_POLYNOMIAL agent."""

    def test_has_all_positions(self) -> None:
        """Agent has all seven contexts as positions."""
        assert len(SOUL_POLYNOMIAL.positions) == 7
        for ctx in EigenvectorContext:
            assert ctx in SOUL_POLYNOMIAL.positions

    def test_invoke_single_context(self) -> None:
        """invoke() works for single context."""
        query = SoulQuery(message="test")
        _, output = SOUL_POLYNOMIAL.invoke(EigenvectorContext.GRATITUDE, query)

        assert isinstance(output, SoulResponse)


# =============================================================================
# Wrapper Tests
# =============================================================================


class TestSoulPolynomialAgentWrapper:
    """Test the backwards-compatible SoulPolynomialAgent wrapper."""

    def test_initial_state_is_aesthetic(self) -> None:
        """Agent starts in AESTHETIC context."""
        agent = SoulPolynomialAgent()
        assert agent.state == EigenvectorContext.AESTHETIC

    def test_set_context(self) -> None:
        """set_context() changes current context."""
        agent = SoulPolynomialAgent()
        agent.set_context(EigenvectorContext.JOY)
        assert agent.state == EigenvectorContext.JOY

    @pytest.mark.asyncio
    async def test_query_returns_response(self) -> None:
        """query() returns SoulResponse."""
        agent = SoulPolynomialAgent()
        response = await agent.query("Should I simplify this code?")

        assert isinstance(response, SoulResponse)
        assert len(response.judgments) >= 1

    @pytest.mark.asyncio
    async def test_query_with_context(self) -> None:
        """query() respects context parameter."""
        agent = SoulPolynomialAgent()
        response = await agent.query(
            "Is this peer-to-peer?",
            context=EigenvectorContext.HETERARCHY,
        )

        assert response.primary_context == EigenvectorContext.HETERARCHY

    @pytest.mark.asyncio
    async def test_query_all_returns_synthesis(self) -> None:
        """query_all() returns response with synthesis."""
        agent = SoulPolynomialAgent()
        response = await agent.query_all("What does the whole soul say?")

        assert isinstance(response, SoulResponse)
        assert len(response.judgments) == 6  # All core contexts
        assert response.synthesis is not None


# =============================================================================
# Context Mapping Tests
# =============================================================================


class TestContextMapping:
    """Test mapping between EigenvectorContext and SOUL_SHEAF Context."""

    def test_to_sheaf_maps_core_contexts(self) -> None:
        """Core contexts map to sheaf contexts."""
        for ctx in [
            EigenvectorContext.AESTHETIC,
            EigenvectorContext.CATEGORICAL,
            EigenvectorContext.GRATITUDE,
            EigenvectorContext.HETERARCHY,
            EigenvectorContext.GENERATIVITY,
            EigenvectorContext.JOY,
        ]:
            sheaf_ctx = to_sheaf_context(ctx)
            assert sheaf_ctx is not None

    def test_synthesizing_has_no_sheaf_mapping(self) -> None:
        """SYNTHESIZING doesn't map to sheaf (it glues them)."""
        sheaf_ctx = to_sheaf_context(EigenvectorContext.SYNTHESIZING)
        assert sheaf_ctx is None

    def test_from_sheaf_roundtrip(self) -> None:
        """Mapping is consistent (roundtrip for core contexts)."""
        for ctx in [
            EigenvectorContext.AESTHETIC,
            EigenvectorContext.CATEGORICAL,
            EigenvectorContext.GRATITUDE,
            EigenvectorContext.HETERARCHY,
            EigenvectorContext.GENERATIVITY,
            EigenvectorContext.JOY,
        ]:
            sheaf_ctx = to_sheaf_context(ctx)
            assert sheaf_ctx is not None
            back = from_sheaf_context(sheaf_ctx)
            assert back == ctx


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_message(self) -> None:
        """Empty message is handled gracefully."""
        agent = SoulPolynomialAgent()
        response = await agent.query("")

        assert isinstance(response, SoulResponse)

    @pytest.mark.asyncio
    async def test_long_message_truncated_in_summary(self) -> None:
        """Long messages are truncated in judgment summary."""
        agent = SoulPolynomialAgent()
        long_msg = "x" * 200
        response = await agent.query(long_msg)

        # Summary should be truncated
        assert len(response.judgments[0].input_summary) <= 100

    @pytest.mark.asyncio
    async def test_multiple_queries(self) -> None:
        """Agent can handle multiple queries."""
        agent = SoulPolynomialAgent()

        r1 = await agent.query("First question")
        r2 = await agent.query("Second question")

        assert r1.query.message == "First question"
        assert r2.query.message == "Second question"
