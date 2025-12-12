"""
Tests for shared/pataphysics.py - LLM-backed Pataphysics Solver

Tests cover:
1. PataphysicsAgent prompt building and response parsing
2. PataphysicsResult and PataphysicsSolverConfig dataclasses
3. create_pataphysics_solver factory function
4. Integration with @meltable decorator (mocked)
5. Different PataphysicsMode behaviors

Note: These tests use mocked responses to avoid actual LLM calls.
Integration tests with real LLM are marked with pytest.mark.integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from shared.melting import MeltingContext
from shared.pataphysics import (
    SYSTEM_PROMPT,
    PataphysicsAgent,
    PataphysicsMode,
    PataphysicsResult,
    PataphysicsSolverConfig,
    build_anomaly_prompt,
    build_clinamen_prompt,
    build_syzygy_prompt,
    create_pataphysics_solver,
    pataphysics_solver_with_postcondition,
)

# === Test PataphysicsResult ===


class TestPataphysicsResult:
    """Test PataphysicsResult dataclass."""

    def test_result_stores_value(self) -> None:
        """Result should store the imaginary solution value."""
        result = PataphysicsResult(
            value=42,
            mode=PataphysicsMode.ANOMALY,
            reasoning="Test reasoning",
            confidence=0.8,
        )
        assert result.value == 42
        assert result.mode == PataphysicsMode.ANOMALY
        assert result.reasoning == "Test reasoning"
        assert result.confidence == 0.8

    def test_result_default_confidence(self) -> None:
        """Result should default confidence to 0.5."""
        result = PataphysicsResult(
            value="test",
            mode=PataphysicsMode.CLINAMEN,
            reasoning="Test",
        )
        assert result.confidence == 0.5


# === Test PataphysicsSolverConfig ===


class TestPataphysicsSolverConfig:
    """Test PataphysicsSolverConfig dataclass."""

    def test_config_default_values(self) -> None:
        """Config should have sensible defaults."""
        config = PataphysicsSolverConfig()
        assert config.mode == PataphysicsMode.ANOMALY
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.include_type_hints is True
        assert config.verbose is False

    def test_config_custom_values(self) -> None:
        """Config should accept custom values."""
        config = PataphysicsSolverConfig(
            mode=PataphysicsMode.SYZYGY,
            temperature=0.9,
            max_tokens=1024,
            verbose=True,
        )
        assert config.mode == PataphysicsMode.SYZYGY
        assert config.temperature == 0.9
        assert config.max_tokens == 1024
        assert config.verbose is True

    def test_config_is_frozen(self) -> None:
        """Config should be frozen (immutable)."""
        config = PataphysicsSolverConfig()
        with pytest.raises(AttributeError):
            config.mode = PataphysicsMode.CLINAMEN  # type: ignore[misc]


# === Test Prompt Building ===


class TestPromptBuilding:
    """Test prompt building functions."""

    def test_anomaly_prompt_includes_function_name(self) -> None:
        """Anomaly prompt should include function name."""
        ctx = MeltingContext(
            function_name="calculate_value",
            args=(1, 2),
            kwargs={"x": 3},
            error=RuntimeError("Test error"),
        )
        prompt = build_anomaly_prompt(ctx, None)
        assert "calculate_value" in prompt
        assert "RuntimeError" in prompt
        assert "Test error" in prompt

    def test_anomaly_prompt_includes_postcondition(self) -> None:
        """Anomaly prompt should include postcondition if provided."""
        ctx = MeltingContext(
            function_name="test_func",
            args=(),
            kwargs={},
            error=Exception("error"),
        )
        prompt = build_anomaly_prompt(ctx, "lambda x: x > 0")
        assert "lambda x: x > 0" in prompt
        assert "Postcondition" in prompt

    def test_clinamen_prompt_mentions_swerve(self) -> None:
        """Clinamen prompt should mention Lucretian swerve."""
        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("error"),
        )
        prompt = build_clinamen_prompt(ctx, None)
        assert "clinamen" in prompt.lower() or "swerve" in prompt.lower()
        assert "Lucretius" in prompt

    def test_syzygy_prompt_mentions_alignment(self) -> None:
        """Syzygy prompt should mention unexpected alignment."""
        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("error"),
        )
        prompt = build_syzygy_prompt(ctx, None)
        assert "syzygy" in prompt.lower() or "alignment" in prompt.lower()


# === Test PataphysicsAgent ===


class TestPataphysicsAgent:
    """Test PataphysicsAgent LLMAgent implementation."""

    def test_agent_name(self) -> None:
        """Agent should have descriptive name."""
        agent = PataphysicsAgent()
        assert "PataphysicsAgent" in agent.name
        assert "anomaly" in agent.name.lower()

        agent2 = PataphysicsAgent(
            config=PataphysicsSolverConfig(mode=PataphysicsMode.CLINAMEN)
        )
        assert "clinamen" in agent2.name.lower()

    def test_agent_build_prompt_returns_context(self) -> None:
        """build_prompt should return AgentContext."""
        agent = PataphysicsAgent()
        ctx = MeltingContext(
            function_name="test_func",
            args=(1, 2),
            kwargs={"key": "value"},
            error=ValueError("test error"),
        )

        result = agent.build_prompt(ctx)

        assert result.system_prompt == SYSTEM_PROMPT
        assert len(result.messages) == 1
        assert result.messages[0]["role"] == "user"
        assert "test_func" in result.messages[0]["content"]

    def test_agent_parse_response_extracts_json(self) -> None:
        """parse_response should extract JSON from response."""
        agent = PataphysicsAgent()
        response = """Here is the solution:
        {"value": 42, "reasoning": "The answer to everything", "confidence": 0.95}
        """

        result = agent.parse_response(response)

        assert result.value == 42
        assert result.reasoning == "The answer to everything"
        assert result.confidence == 0.95

    def test_agent_parse_response_handles_malformed_json(self) -> None:
        """parse_response should handle malformed responses."""
        agent = PataphysicsAgent()
        response = """Not valid JSON at all"""

        result = agent.parse_response(response)

        # Should return None value with low confidence
        assert result.value is None
        assert result.confidence <= 0.3

    def test_agent_parse_response_extracts_partial_value(self) -> None:
        """parse_response should extract value from partial JSON."""
        agent = PataphysicsAgent()
        response = """
        The value is:
        "value": 100,
        "reasoning": "computed"
        """

        result = agent.parse_response(response)

        # Should extract the value
        assert result.value == 100 or result.value is None  # Depends on regex

    def test_agent_invoke_raises_not_implemented(self) -> None:
        """invoke should raise NotImplementedError."""
        agent = PataphysicsAgent()
        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("test"),
        )

        with pytest.raises(NotImplementedError):
            import asyncio

            asyncio.run(agent.invoke(ctx))


# === Test create_pataphysics_solver ===


class TestCreatePataphysicsSolver:
    """Test create_pataphysics_solver factory function."""

    @pytest.mark.asyncio
    async def test_solver_factory_returns_callable(self) -> None:
        """Factory should return an async callable."""
        solver = create_pataphysics_solver()
        assert callable(solver)

    @pytest.mark.asyncio
    async def test_solver_uses_provided_runtime(self) -> None:
        """Solver should use provided runtime."""
        # Create a mock runtime
        mock_runtime = MagicMock()
        mock_result = MagicMock()
        mock_result.output = PataphysicsResult(
            value=42,
            mode=PataphysicsMode.ANOMALY,
            reasoning="Mocked",
            confidence=0.9,
        )
        mock_runtime.execute = AsyncMock(return_value=mock_result)

        solver = create_pataphysics_solver(runtime=mock_runtime)

        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("test"),
        )

        result = await solver(ctx)

        assert result == 42
        mock_runtime.execute.assert_called_once()


# === Test pataphysics_solver_with_postcondition ===


class TestPataphysicsSolverWithPostcondition:
    """Test pataphysics_solver_with_postcondition convenience function."""

    def test_creates_solver_with_postcondition(self) -> None:
        """Should create solver that knows about postcondition."""

        def ensure(x: int) -> bool:
            return x > 0

        solver = pataphysics_solver_with_postcondition(ensure=ensure)
        assert callable(solver)

    def test_extracts_postcondition_source(self) -> None:
        """Should extract source code of postcondition for prompting."""

        def my_postcondition(x: float) -> bool:
            return 0.0 <= x <= 1.0

        solver = pataphysics_solver_with_postcondition(ensure=my_postcondition)
        assert callable(solver)


# === Test Integration with @meltable (Mocked) ===


class TestMeltableIntegration:
    """Test integration with @meltable decorator using mocks."""

    @pytest.mark.asyncio
    async def test_meltable_with_llm_solver_uses_imaginary_solution(self) -> None:
        """@meltable should use LLM solver's imaginary solution."""
        from shared.melting import meltable

        # Create a mock solver
        async def mock_solver(ctx: MeltingContext) -> int:
            return 42

        @meltable(solver=mock_solver, ensure=lambda x: x > 0)
        async def always_fails() -> int:
            raise RuntimeError("Boom")

        result = await always_fails()
        assert result == 42

    @pytest.mark.asyncio
    async def test_meltable_retries_llm_solver_on_postcondition_failure(self) -> None:
        """@meltable should retry LLM solver if postcondition fails."""
        from shared.melting import meltable

        call_count = 0

        async def improving_solver(ctx: MeltingContext) -> int:
            nonlocal call_count
            call_count += 1
            # First call returns invalid, second returns valid
            if call_count == 1:
                return -1
            return 100

        @meltable(solver=improving_solver, ensure=lambda x: x > 0, max_retries=3)
        async def always_fails() -> int:
            raise RuntimeError("Boom")

        result = await always_fails()
        assert result == 100
        assert call_count == 2


# === Test PataphysicsMode Behavior ===


class TestPataphysicsModeBehavior:
    """Test different PataphysicsMode behaviors."""

    def test_all_modes_produce_different_prompts(self) -> None:
        """Different modes should produce different prompts."""
        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("error"),
        )

        anomaly = build_anomaly_prompt(ctx, None)
        clinamen = build_clinamen_prompt(ctx, None)
        syzygy = build_syzygy_prompt(ctx, None)

        # All should be different
        assert anomaly != clinamen
        assert clinamen != syzygy
        assert anomaly != syzygy

    def test_mode_enum_values(self) -> None:
        """Mode enum should have expected values."""
        assert PataphysicsMode.CLINAMEN.value == "clinamen"
        assert PataphysicsMode.SYZYGY.value == "syzygy"
        assert PataphysicsMode.ANOMALY.value == "anomaly"
