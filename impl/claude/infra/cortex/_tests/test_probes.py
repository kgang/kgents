"""
Tests for cognitive probes.

These tests use mock runtimes to verify probe behavior
without actual LLM calls.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from infra.cortex.probes import (
    CognitiveProbe,
    PathProbe,
    ProbeResult,
    ProbeStatus,
    ReasoningProbe,
    full_probe_suite,
    probe_runtime,
)


# =============================================================================
# Mock Runtimes
# =============================================================================


class MockRuntime:
    """Mock LLM runtime for testing."""

    def __init__(
        self,
        response: str = "HEALTHY",
        delay: float = 0.0,
        raise_error: Exception | None = None,
    ):
        self._response = response
        self._delay = delay
        self._raise_error = raise_error

    async def raw_completion(
        self,
        context: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Mock completion."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        if self._raise_error is not None:
            raise self._raise_error

        return self._response, {"model": "mock", "usage": {"total_tokens": 10}}


class SlowRuntime(MockRuntime):
    """Mock runtime that simulates slow responses."""

    def __init__(self, response: str = "HEALTHY", delay: float = 6.0):
        super().__init__(response=response, delay=delay)


class ErrorRuntime(MockRuntime):
    """Mock runtime that always raises an error."""

    def __init__(self, error: Exception | None = None):
        super().__init__(raise_error=error or RuntimeError("Runtime error"))


class TimeoutRuntime:
    """Mock runtime that times out."""

    async def raw_completion(
        self,
        context: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Never returns - simulates timeout."""
        await asyncio.sleep(100)  # Will be cancelled by timeout
        return "never", {}


# =============================================================================
# CognitiveProbe Tests
# =============================================================================


class TestCognitiveProbe:
    """Tests for CognitiveProbe."""

    @pytest.mark.asyncio
    async def test_healthy_response(self) -> None:
        """Test probe with healthy LLM response."""
        runtime = MockRuntime(response="HEALTHY")
        probe = CognitiveProbe()

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.HEALTHY
        assert result.healthy is True
        assert result.latency_ms > 0
        assert "HEALTHY" in result.details.get("response", "")

    @pytest.mark.asyncio
    async def test_healthy_case_insensitive(self) -> None:
        """Test probe accepts various healthy responses."""
        for response in ["HEALTHY", "healthy", "Healthy", "I am healthy."]:
            runtime = MockRuntime(response=response)
            probe = CognitiveProbe()
            result = await probe.check(runtime)
            assert result.healthy is True, f"Failed for response: {response}"

    @pytest.mark.asyncio
    async def test_degraded_on_wrong_response(self) -> None:
        """Test probe marks degraded on unexpected response."""
        runtime = MockRuntime(response="Something else entirely")
        probe = CognitiveProbe()

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.DEGRADED
        assert result.healthy is True  # Degraded is still "healthy enough"
        assert "Unexpected" in result.message

    @pytest.mark.asyncio
    async def test_degraded_on_high_latency(self) -> None:
        """Test probe marks degraded on high latency."""
        runtime = SlowRuntime(response="HEALTHY", delay=6.0)
        probe = CognitiveProbe(degraded_threshold_ms=5000.0)

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.DEGRADED
        assert result.healthy is True
        assert "latency" in result.message.lower()

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test probe handles timeout."""
        runtime = TimeoutRuntime()
        probe = CognitiveProbe(timeout=0.1)

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.TIMEOUT
        assert result.healthy is False

    @pytest.mark.asyncio
    async def test_error_handling(self) -> None:
        """Test probe handles runtime errors."""
        runtime = ErrorRuntime(RuntimeError("Connection failed"))
        probe = CognitiveProbe()

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.ERROR
        assert result.healthy is False
        assert "Connection failed" in result.message


# =============================================================================
# ReasoningProbe Tests
# =============================================================================


class TestReasoningProbe:
    """Tests for ReasoningProbe."""

    @pytest.mark.asyncio
    async def test_correct_arithmetic(self) -> None:
        """Test probe with correct arithmetic response."""
        runtime = MockRuntime(response="12")
        probe = ReasoningProbe()

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.HEALTHY
        assert result.healthy is True
        assert "12" in result.details.get("response", "")

    @pytest.mark.asyncio
    async def test_correct_in_context(self) -> None:
        """Test probe accepts 12 in various formats."""
        for response in ["12", "The answer is 12.", "12.0", "Twelve (12)"]:
            runtime = MockRuntime(response=response)
            probe = ReasoningProbe()
            result = await probe.check(runtime)
            assert result.healthy is True, f"Failed for response: {response}"

    @pytest.mark.asyncio
    async def test_incorrect_arithmetic(self) -> None:
        """Test probe marks degraded on wrong answer."""
        runtime = MockRuntime(response="13")
        probe = ReasoningProbe()

        result = await probe.check(runtime)

        assert result.status == ProbeStatus.DEGRADED
        assert "Incorrect" in result.message


# =============================================================================
# PathProbe Tests
# =============================================================================


class TestPathProbe:
    """Tests for PathProbe."""

    @pytest.mark.asyncio
    async def test_successful_path_resolution(self) -> None:
        """Test probe with successful path invocation."""
        # Create mock cortex servicer
        @dataclass
        class MockInvokeResult:
            result: Any = None
            result_json: str = '{"test": "value"}'
            duration_ms: float = 10.0

        mock_servicer = MagicMock()
        mock_servicer.Invoke = AsyncMock(return_value=MockInvokeResult())

        probe = PathProbe(path="concept.define")
        result = await probe.check(mock_servicer)

        assert result.status == ProbeStatus.HEALTHY
        assert result.healthy is True

    @pytest.mark.asyncio
    async def test_path_error(self) -> None:
        """Test probe handles path errors."""
        @dataclass
        class MockInvokeResult:
            result: Any = None
            result_json: str = '{"error": "Unknown path"}'
            duration_ms: float = 10.0

        mock_servicer = MagicMock()
        mock_servicer.Invoke = AsyncMock(return_value=MockInvokeResult())

        probe = PathProbe(path="unknown.path")
        result = await probe.check(mock_servicer)

        assert result.status == ProbeStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_empty_result(self) -> None:
        """Test probe handles empty results."""
        @dataclass
        class MockInvokeResult:
            result: Any = None
            result_json: str = ""
            duration_ms: float = 10.0

        mock_servicer = MagicMock()
        mock_servicer.Invoke = AsyncMock(return_value=MockInvokeResult())

        probe = PathProbe()
        result = await probe.check(mock_servicer)

        assert result.status == ProbeStatus.UNHEALTHY


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_probe_runtime_healthy(self) -> None:
        """Test probe_runtime returns True for healthy runtime."""
        runtime = MockRuntime(response="HEALTHY")
        result = await probe_runtime(runtime)
        assert result is True

    @pytest.mark.asyncio
    async def test_probe_runtime_unhealthy(self) -> None:
        """Test probe_runtime returns False for unhealthy runtime."""
        runtime = ErrorRuntime()
        result = await probe_runtime(runtime)
        assert result is False

    @pytest.mark.asyncio
    async def test_probe_runtime_with_reasoning(self) -> None:
        """Test probe_runtime with reasoning probe - degraded counts as healthy."""
        # Runtime that responds HEALTHY for cognitive but wrong for arithmetic
        # Note: DEGRADED status still counts as "healthy" in the probe system
        # because it indicates the LLM is responsive, just not ideal
        class MixedRuntime:
            call_count = 0

            async def raw_completion(
                self, context: Any
            ) -> tuple[str, dict[str, Any]]:
                self.call_count += 1
                if self.call_count == 1:
                    return "HEALTHY", {}
                return "99", {}  # Wrong answer - will be DEGRADED but still "healthy"

        runtime = MixedRuntime()
        result = await probe_runtime(runtime, include_reasoning=True)
        # Degraded is still healthy (LLM is responsive, just imprecise)
        assert result is True

    @pytest.mark.asyncio
    async def test_probe_runtime_with_reasoning_error(self) -> None:
        """Test probe_runtime fails when reasoning probe errors."""
        # Runtime that responds HEALTHY for cognitive but errors for arithmetic
        class ErrorOnSecondRuntime:
            call_count = 0

            async def raw_completion(
                self, context: Any
            ) -> tuple[str, dict[str, Any]]:
                self.call_count += 1
                if self.call_count == 1:
                    return "HEALTHY", {}
                raise RuntimeError("Connection lost")

        runtime = ErrorOnSecondRuntime()
        result = await probe_runtime(runtime, include_reasoning=True)
        assert result is False

    @pytest.mark.asyncio
    async def test_full_probe_suite(self) -> None:
        """Test full probe suite runs all probes."""
        runtime = MockRuntime(response="HEALTHY 12")  # Works for both

        results = await full_probe_suite(runtime)

        assert "cognitive" in results
        assert "reasoning" in results
        assert results["cognitive"].healthy is True


# =============================================================================
# ProbeResult Tests
# =============================================================================


class TestProbeResult:
    """Tests for ProbeResult dataclass."""

    def test_healthy_statuses(self) -> None:
        """Test healthy property for various statuses."""
        healthy_result = ProbeResult(
            status=ProbeStatus.HEALTHY, latency_ms=100.0
        )
        degraded_result = ProbeResult(
            status=ProbeStatus.DEGRADED, latency_ms=100.0
        )
        unhealthy_result = ProbeResult(
            status=ProbeStatus.UNHEALTHY, latency_ms=100.0
        )
        timeout_result = ProbeResult(
            status=ProbeStatus.TIMEOUT, latency_ms=100.0
        )
        error_result = ProbeResult(status=ProbeStatus.ERROR, latency_ms=100.0)

        assert healthy_result.healthy is True
        assert degraded_result.healthy is True
        assert unhealthy_result.healthy is False
        assert timeout_result.healthy is False
        assert error_result.healthy is False

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        result = ProbeResult(
            status=ProbeStatus.HEALTHY,
            latency_ms=123.45,
            message="Test message",
            details={"key": "value"},
        )

        data = result.to_dict()

        assert data["status"] == "healthy"
        assert data["healthy"] is True
        assert data["latency_ms"] == 123.45
        assert data["message"] == "Test message"
        assert data["details"] == {"key": "value"}
        assert "timestamp" in data
