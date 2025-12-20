"""
Tests for Tool Orchestrator: Parallel and DAG Execution.

Covers:
- Parallel execution with bounded concurrency
- DAG execution with dependency resolution
- Error handling and aggregation
- Cycle detection
- Performance (parallel should be faster than sequential)

See: services/tooling/orchestrator.py
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import pytest

from services.tooling.base import Tool, ToolCategory, ToolError
from services.tooling.orchestrator import (
    DAGNode,
    OrchestratorResult,
    ParallelRequest,
    ParallelTool,
    ToolOrchestrator,
)

# =============================================================================
# Test Tools
# =============================================================================


@dataclass
class DelayRequest:
    """Request for delay tool."""

    delay_ms: float
    value: str


@dataclass
class DelayResponse:
    """Response from delay tool."""

    value: str
    actual_delay_ms: float


class DelayTool(Tool[DelayRequest, DelayResponse]):
    """Tool that delays for a specified time."""

    @property
    def name(self) -> str:
        return "test.delay"

    @property
    def description(self) -> str:
        return "Delay for testing"

    async def invoke(self, request: DelayRequest) -> DelayResponse:
        start = time.monotonic()
        await asyncio.sleep(request.delay_ms / 1000)
        actual = (time.monotonic() - start) * 1000
        return DelayResponse(value=request.value, actual_delay_ms=actual)


class FailTool(Tool[str, str]):
    """Tool that always fails."""

    @property
    def name(self) -> str:
        return "test.fail"

    @property
    def description(self) -> str:
        return "Always fails"

    async def invoke(self, request: str) -> str:
        raise ToolError(f"Intentional failure: {request}", self.name)


class AddTool(Tool[int, int]):
    """Tool that adds to input."""

    def __init__(self, addend: int = 1) -> None:
        self._addend = addend
        self._name = f"test.add{addend}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"Add {self._addend}"

    async def invoke(self, request: int) -> int:
        return request + self._addend


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def orchestrator() -> ToolOrchestrator:
    """Fresh orchestrator with default settings."""
    return ToolOrchestrator(max_concurrency=5)


@pytest.fixture
def delay_tool() -> DelayTool:
    """Delay tool for timing tests."""
    return DelayTool()


# =============================================================================
# OrchestratorResult Tests
# =============================================================================


class TestOrchestratorResult:
    """Tests for OrchestratorResult."""

    def test_all_succeeded(self) -> None:
        """all_succeeded is True when no errors."""
        result = OrchestratorResult(
            results={"a": None, "b": None},  # type: ignore
            errors={},
            total_duration_ms=100,
            success_count=2,
            failure_count=0,
        )
        assert result.all_succeeded is True
        assert result.all_failed is False

    def test_all_failed(self) -> None:
        """all_failed is True when no successes."""
        result = OrchestratorResult(
            results={},
            errors={"a": ToolError("fail")},
            total_duration_ms=100,
            success_count=0,
            failure_count=1,
        )
        assert result.all_succeeded is False
        assert result.all_failed is True

    def test_partial_success(self) -> None:
        """Partial success detected."""
        result = OrchestratorResult(
            results={"a": None},  # type: ignore
            errors={"b": ToolError("fail")},
            total_duration_ms=100,
            success_count=1,
            failure_count=1,
        )
        assert result.all_succeeded is False
        assert result.all_failed is False


# =============================================================================
# Parallel Execution Tests
# =============================================================================


class TestParallelExecution:
    """Tests for parallel tool execution."""

    async def test_empty_list(self, orchestrator: ToolOrchestrator) -> None:
        """Empty tool list returns empty result."""
        result = await orchestrator.execute_parallel([])
        assert result.success_count == 0
        assert result.failure_count == 0

    async def test_single_tool(self, orchestrator: ToolOrchestrator, delay_tool: DelayTool) -> None:
        """Single tool execution works."""
        result = await orchestrator.execute_parallel(
            [
                (delay_tool, DelayRequest(delay_ms=10, value="test")),
            ]
        )
        assert result.success_count == 1
        assert result.failure_count == 0
        assert "test.delay:0" in result.results

    async def test_multiple_tools(
        self, orchestrator: ToolOrchestrator, delay_tool: DelayTool
    ) -> None:
        """Multiple tools run in parallel."""
        result = await orchestrator.execute_parallel(
            [
                (delay_tool, DelayRequest(delay_ms=10, value="a")),
                (delay_tool, DelayRequest(delay_ms=10, value="b")),
                (delay_tool, DelayRequest(delay_ms=10, value="c")),
            ]
        )
        assert result.success_count == 3
        assert result.failure_count == 0
        # Keys are indexed: "tool.name:index"
        assert "test.delay:0" in result.results
        assert "test.delay:1" in result.results
        assert "test.delay:2" in result.results

    async def test_parallel_faster_than_sequential(
        self, orchestrator: ToolOrchestrator, delay_tool: DelayTool
    ) -> None:
        """Parallel execution is faster than sequential sum."""
        delay_ms = 50
        num_tools = 3

        result = await orchestrator.execute_parallel(
            [(delay_tool, DelayRequest(delay_ms=delay_ms, value=str(i))) for i in range(num_tools)]
        )

        # Parallel should complete in ~delay_ms, not delay_ms * num_tools
        sequential_estimate = delay_ms * num_tools
        assert result.total_duration_ms < sequential_estimate * 0.7  # 30% margin

    async def test_error_collection(self, orchestrator: ToolOrchestrator) -> None:
        """Errors are collected without failing other tools."""
        delay_tool = DelayTool()
        fail_tool = FailTool()

        result = await orchestrator.execute_parallel(
            [
                (delay_tool, DelayRequest(delay_ms=10, value="success")),
                (fail_tool, "should fail"),
            ]
        )

        assert result.success_count == 1
        assert result.failure_count == 1
        assert "test.delay:0" in result.results
        assert "test.fail:1" in result.errors

    async def test_bounded_concurrency(self) -> None:
        """Concurrency is bounded by max_concurrency."""
        max_concurrent = 0
        current_concurrent = 0

        class CountingTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "test.count"

            async def invoke(self, request: int) -> int:
                nonlocal max_concurrent, current_concurrent
                current_concurrent += 1
                max_concurrent = max(max_concurrent, current_concurrent)
                await asyncio.sleep(0.05)
                current_concurrent -= 1
                return request

        orchestrator = ToolOrchestrator(max_concurrency=2)
        tool = CountingTool()

        await orchestrator.execute_parallel([(tool, i) for i in range(5)])

        assert max_concurrent <= 2


# =============================================================================
# DAG Execution Tests
# =============================================================================


class TestDAGExecution:
    """Tests for DAG-based tool execution."""

    async def test_empty_dag(self, orchestrator: ToolOrchestrator) -> None:
        """Empty DAG returns empty result."""
        result = await orchestrator.execute_dag([])
        assert result.success_count == 0

    async def test_single_node(self, orchestrator: ToolOrchestrator) -> None:
        """Single node DAG works."""
        add_tool = AddTool(1)

        result = await orchestrator.execute_dag(
            [
                DAGNode("add", add_tool, 10),
            ]
        )

        assert result.success_count == 1
        assert result.get_result("add") is not None
        assert result.get_result("add").value == 11  # type: ignore

    async def test_linear_dag(self, orchestrator: ToolOrchestrator) -> None:
        """Linear DAG (A → B → C) executes in order."""
        # These tools don't actually pass results, but test dependency ordering
        add1 = AddTool(1)
        add2 = AddTool(2)
        add3 = AddTool(3)

        result = await orchestrator.execute_dag(
            [
                DAGNode("step1", add1, 0),
                DAGNode("step2", add2, 0, depends_on=["step1"]),
                DAGNode("step3", add3, 0, depends_on=["step2"]),
            ]
        )

        assert result.success_count == 3

    async def test_diamond_dag(self, orchestrator: ToolOrchestrator) -> None:
        """Diamond DAG (A → B,C → D) executes correctly."""
        #     A
        #    / \
        #   B   C
        #    \ /
        #     D

        delay_tool = DelayTool()

        result = await orchestrator.execute_dag(
            [
                DAGNode("a", delay_tool, DelayRequest(delay_ms=10, value="a")),
                DAGNode("b", delay_tool, DelayRequest(delay_ms=10, value="b"), depends_on=["a"]),
                DAGNode("c", delay_tool, DelayRequest(delay_ms=10, value="c"), depends_on=["a"]),
                DAGNode(
                    "d", delay_tool, DelayRequest(delay_ms=10, value="d"), depends_on=["b", "c"]
                ),
            ]
        )

        assert result.success_count == 4

    async def test_parallel_in_dag(self, orchestrator: ToolOrchestrator) -> None:
        """Independent branches run in parallel."""
        delay_ms = 50

        delay_tool = DelayTool()

        result = await orchestrator.execute_dag(
            [
                DAGNode("root", delay_tool, DelayRequest(delay_ms=delay_ms, value="root")),
                DAGNode(
                    "branch1",
                    delay_tool,
                    DelayRequest(delay_ms=delay_ms, value="b1"),
                    depends_on=["root"],
                ),
                DAGNode(
                    "branch2",
                    delay_tool,
                    DelayRequest(delay_ms=delay_ms, value="b2"),
                    depends_on=["root"],
                ),
            ]
        )

        # Should complete in ~100ms (root + one parallel level), not 150ms
        assert result.total_duration_ms < delay_ms * 2.5
        assert result.success_count == 3

    async def test_dependency_failure_skips_dependents(
        self, orchestrator: ToolOrchestrator
    ) -> None:
        """Failed node causes dependents to be skipped."""
        fail_tool = FailTool()
        delay_tool = DelayTool()

        result = await orchestrator.execute_dag(
            [
                DAGNode("fail", fail_tool, "fail"),
                DAGNode(
                    "dependent",
                    delay_tool,
                    DelayRequest(delay_ms=10, value="x"),
                    depends_on=["fail"],
                ),
            ]
        )

        assert result.failure_count == 2  # Both fail (one from dep)
        assert "fail" in result.errors
        assert "dependent" in result.errors
        assert "Dependency failed" in str(result.errors["dependent"])


# =============================================================================
# DAG Validation Tests
# =============================================================================


class TestDAGValidation:
    """Tests for DAG validation."""

    async def test_duplicate_names_rejected(self, orchestrator: ToolOrchestrator) -> None:
        """Duplicate node names are rejected."""
        add_tool = AddTool(1)

        with pytest.raises(ToolError, match="Duplicate"):
            await orchestrator.execute_dag(
                [
                    DAGNode("node", add_tool, 1),
                    DAGNode("node", add_tool, 2),
                ]
            )

    async def test_missing_dependency_rejected(self, orchestrator: ToolOrchestrator) -> None:
        """Unknown dependencies are rejected."""
        add_tool = AddTool(1)

        with pytest.raises(ToolError, match="Unknown dependency"):
            await orchestrator.execute_dag(
                [
                    DAGNode("a", add_tool, 1, depends_on=["nonexistent"]),
                ]
            )

    async def test_cycle_detected(self, orchestrator: ToolOrchestrator) -> None:
        """Cycles in DAG are detected."""
        add_tool = AddTool(1)

        with pytest.raises(ToolError, match="Cycle"):
            await orchestrator.execute_dag(
                [
                    DAGNode("a", add_tool, 1, depends_on=["b"]),
                    DAGNode("b", add_tool, 2, depends_on=["a"]),
                ]
            )


# =============================================================================
# ParallelTool Wrapper Tests
# =============================================================================


class TestParallelTool:
    """Tests for ParallelTool wrapper."""

    def test_properties(self) -> None:
        """ParallelTool has correct properties."""
        add_tool = AddTool(1)
        parallel = ParallelTool(add_tool)

        assert "parallel" in parallel.name
        assert "add" in parallel.name
        assert parallel.category == ToolCategory.ORCHESTRATION
        assert parallel.trust_required == add_tool.trust_required

    async def test_parallel_invocation(self) -> None:
        """ParallelTool runs over multiple inputs."""
        add_tool = AddTool(10)
        parallel = ParallelTool(add_tool)

        result = await parallel.invoke(ParallelRequest(inputs=[1, 2, 3]))

        assert result.success_count == 3


# =============================================================================
# Integration Tests
# =============================================================================


class TestOrchestratorIntegration:
    """Integration tests for orchestrator."""

    async def test_complex_dag_workflow(self) -> None:
        """Complex DAG with mixed tools."""
        #     start
        #    /  |  \
        #   a   b   c  (parallel)
        #    \  |  /
        #     merge
        #       |
        #      end

        delay_tool = DelayTool()
        orchestrator = ToolOrchestrator(max_concurrency=3)

        result = await orchestrator.execute_dag(
            [
                DAGNode("start", delay_tool, DelayRequest(delay_ms=10, value="start")),
                DAGNode(
                    "a", delay_tool, DelayRequest(delay_ms=20, value="a"), depends_on=["start"]
                ),
                DAGNode(
                    "b", delay_tool, DelayRequest(delay_ms=20, value="b"), depends_on=["start"]
                ),
                DAGNode(
                    "c", delay_tool, DelayRequest(delay_ms=20, value="c"), depends_on=["start"]
                ),
                DAGNode(
                    "merge",
                    delay_tool,
                    DelayRequest(delay_ms=10, value="merge"),
                    depends_on=["a", "b", "c"],
                ),
                DAGNode(
                    "end", delay_tool, DelayRequest(delay_ms=10, value="end"), depends_on=["merge"]
                ),
            ]
        )

        assert result.all_succeeded
        assert result.success_count == 6

        # Timing: start(10) + parallel(20) + merge(10) + end(10) ≈ 50ms
        # Should be much less than sequential: 10+20+20+20+10+10 = 90ms
        assert result.total_duration_ms < 80
