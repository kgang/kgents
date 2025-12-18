"""
Tests for T-gents Phase 6: Multi-Tool Orchestration Patterns

Tests all orchestration patterns:
1. Sequential execution
2. Parallel execution (product functor)
3. Supervisor pattern (comma category)
4. Handoff pattern (natural transformation)
5. Dynamic tool selection

Coverage:
- Sequential chaining
- Parallel execution and merging
- Supervisor task delegation
- Agent handoffs with conditions
- Context-based tool selection
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from agents.poly.types import Err
from agents.u.core import Tool, ToolErrorType, ToolMeta
from agents.u.orchestration import (
    CostBasedSelection,
    DynamicToolSelector,
    EnvironmentBasedSelection,
    HandoffCondition,
    HandoffPattern,
    HandoffRule,
    LatencyBasedSelection,
    ParallelOrchestrator,
    ParallelResult,
    SelectionContext,
    SequentialOrchestrator,
    SupervisorPattern,
    Task,
)

# =============================================================================
# Test Fixtures: Simple Tools
# =============================================================================


@dataclass
class NumberInput:
    value: int


@dataclass
class NumberOutput:
    value: int


class AddOneTool(Tool[NumberInput, NumberOutput]):
    """Tool that adds 1 to input."""

    meta = ToolMeta.minimal(
        name="add_one",
        description="Add 1 to number",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        return NumberOutput(value=input.value + 1)


class MultiplyByTwoTool(Tool[NumberInput, NumberOutput]):
    """Tool that multiplies input by 2."""

    meta = ToolMeta.minimal(
        name="multiply_by_two",
        description="Multiply number by 2",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        return NumberOutput(value=input.value * 2)


class SquareTool(Tool[NumberInput, NumberOutput]):
    """Tool that squares input."""

    meta = ToolMeta.minimal(
        name="square",
        description="Square a number",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        return NumberOutput(value=input.value**2)


class SlowTool(Tool[NumberInput, NumberOutput]):
    """Tool that takes a long time."""

    meta = ToolMeta.minimal(
        name="slow_tool",
        description="Slow operation",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        await asyncio.sleep(0.1)  # Simulate slow operation
        return NumberOutput(value=input.value * 10)


class FailingTool(Tool[NumberInput, NumberOutput]):
    """Tool that always fails."""

    meta = ToolMeta.minimal(
        name="failing_tool",
        description="Always fails",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        raise ValueError("Intentional failure")


class FallbackTool(Tool[NumberInput, NumberOutput]):
    """Fallback tool for failed operations."""

    meta = ToolMeta.minimal(
        name="fallback_tool",
        description="Fallback operation",
        input_schema=NumberInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberInput) -> NumberOutput:
        return NumberOutput(value=0)  # Safe fallback


# =============================================================================
# 1. Sequential Orchestrator Tests
# =============================================================================


@pytest.mark.asyncio
async def test_sequential_basic() -> None:
    """Test basic sequential execution."""
    tools = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    orchestrator: SequentialOrchestrator[Any, Any, Any] = SequentialOrchestrator(tools)

    # (5 + 1) * 2 = 12, 12^2 = 144
    result = await orchestrator.execute(NumberInput(value=5))

    assert result.is_ok()
    assert result.unwrap().value == 144


@pytest.mark.asyncio
async def test_sequential_single_tool() -> None:
    """Test sequential with single tool."""
    orchestrator: SequentialOrchestrator[Any, Any, Any] = SequentialOrchestrator([AddOneTool()])

    result = await orchestrator.execute(NumberInput(value=10))

    assert result.is_ok()
    assert result.unwrap().value == 11


@pytest.mark.asyncio
async def test_sequential_stops_on_error() -> None:
    """Test sequential stops on first error."""
    tools = [AddOneTool(), FailingTool(), SquareTool()]
    orchestrator: SequentialOrchestrator[Any, Any, Any] = SequentialOrchestrator(tools)

    result = await orchestrator.execute(NumberInput(value=5))

    assert result.is_err()
    # Access error details from Err result
    assert isinstance(result, Err)
    assert result.error.tool_name == "failing_tool"
    assert result.error.error_type == ToolErrorType.FATAL


@pytest.mark.asyncio
async def test_sequential_empty_tools() -> None:
    """Test sequential requires at least one tool."""
    with pytest.raises(ValueError, match="at least one tool"):
        SequentialOrchestrator([])


# =============================================================================
# 2. Parallel Orchestrator Tests
# =============================================================================


@pytest.mark.asyncio
async def test_parallel_basic() -> None:
    """Test basic parallel execution."""
    tools = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    orchestrator = ParallelOrchestrator(tools)

    result = await orchestrator.execute(NumberInput(value=5))

    assert result.is_ok()
    parallel_result = result.unwrap()
    assert isinstance(parallel_result, ParallelResult)
    assert len(parallel_result.results) == 3
    assert parallel_result.results[0].value == 6  # 5 + 1
    assert parallel_result.results[1].value == 10  # 5 * 2
    assert parallel_result.results[2].value == 25  # 5^2
    assert parallel_result.all_succeeded


@pytest.mark.asyncio
async def test_parallel_indexing() -> None:
    """Test parallel result can be indexed."""
    tools = [AddOneTool(), MultiplyByTwoTool()]
    orchestrator = ParallelOrchestrator(tools)

    result = await orchestrator.execute(NumberInput(value=3))

    assert result.is_ok()
    parallel_result = result.unwrap()
    assert parallel_result[0].value == 4  # 3 + 1
    assert parallel_result[1].value == 6  # 3 * 2


@pytest.mark.asyncio
async def test_parallel_faster_than_sequential() -> None:
    """Test parallel execution is faster than sequential."""
    tools: list[Tool[NumberInput, Any]] = [SlowTool(), SlowTool(), SlowTool()]

    # Parallel execution
    parallel_orchestrator = ParallelOrchestrator(tools)
    result = await parallel_orchestrator.execute(NumberInput(value=1))
    assert result.is_ok()
    parallel_duration = result.unwrap().duration_ms

    # Should be faster than 3 * 100ms = 300ms
    # (With some overhead, expect ~100-150ms for parallel)
    assert parallel_duration < 250


@pytest.mark.asyncio
async def test_parallel_fails_if_any_fails() -> None:
    """Test parallel fails if any tool fails."""
    tools = [AddOneTool(), FailingTool(), SquareTool()]
    orchestrator = ParallelOrchestrator(tools)

    result = await orchestrator.execute(NumberInput(value=5))

    assert result.is_err()


@pytest.mark.asyncio
async def test_parallel_empty_tools() -> None:
    """Test parallel requires at least one tool."""
    with pytest.raises(ValueError, match="at least one tool"):
        ParallelOrchestrator([])


@pytest.mark.asyncio
async def test_parallel_single_tool() -> None:
    """Test parallel with single tool."""
    orchestrator = ParallelOrchestrator([AddOneTool()])

    result = await orchestrator.execute(NumberInput(value=7))

    assert result.is_ok()
    assert result.unwrap()[0].value == 8


# =============================================================================
# 3. Supervisor Pattern Tests
# =============================================================================


@pytest.mark.asyncio
async def test_supervisor_basic() -> None:
    """Test basic supervisor delegation."""
    workers = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    supervisor = SupervisorPattern(workers)

    task = Task(task_id="task1", input=NumberInput(value=5))
    result = await supervisor.delegate(task)

    assert result.is_ok()
    assert task.assigned_worker == "add_one"  # Round-robin picks first


@pytest.mark.asyncio
async def test_supervisor_round_robin() -> None:
    """Test supervisor round-robin worker selection."""
    workers = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    supervisor = SupervisorPattern(workers)

    # First task → worker 0
    task1 = Task(task_id="task1", input=NumberInput(value=5))
    result1 = await supervisor.delegate(task1)
    assert result1.is_ok()
    assert task1.assigned_worker == "add_one"

    # Second task → worker 1
    task2 = Task(task_id="task2", input=NumberInput(value=5))
    result2 = await supervisor.delegate(task2)
    assert result2.is_ok()
    assert task2.assigned_worker == "multiply_by_two"

    # Third task → worker 2
    task3 = Task(task_id="task3", input=NumberInput(value=5))
    result3 = await supervisor.delegate(task3)
    assert result3.is_ok()
    assert task3.assigned_worker == "square"

    # Fourth task → wraps to worker 0
    task4 = Task(task_id="task4", input=NumberInput(value=5))
    result4 = await supervisor.delegate(task4)
    assert result4.is_ok()
    assert task4.assigned_worker == "add_one"


@pytest.mark.asyncio
async def test_supervisor_custom_selector() -> None:
    """Test supervisor with custom selector."""

    def always_square(task: Task[Any], workers: list[Tool[Any, Any]]) -> Tool[Any, Any]:
        return workers[2]  # Always pick SquareTool

    workers = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    supervisor = SupervisorPattern(workers, selector=always_square)

    task = Task(task_id="task1", input=NumberInput(value=5))
    result = await supervisor.delegate(task)

    assert result.is_ok()
    assert task.assigned_worker == "square"
    assert result.unwrap().value == 25


@pytest.mark.asyncio
async def test_supervisor_worker_stats() -> None:
    """Test supervisor tracks worker statistics."""
    workers = [AddOneTool(), MultiplyByTwoTool()]
    supervisor = SupervisorPattern(workers)

    # Execute several tasks
    for i in range(4):
        task = Task(task_id=f"task{i}", input=NumberInput(value=i))
        await supervisor.delegate(task)

    stats = supervisor.get_worker_stats()

    # Round-robin: 4 tasks → 2 each
    assert stats["add_one"]["tasks_completed"] == 2
    assert stats["multiply_by_two"]["tasks_completed"] == 2


@pytest.mark.asyncio
async def test_supervisor_handles_worker_failure() -> None:
    """Test supervisor handles worker failures."""
    workers = [FailingTool(), AddOneTool()]
    supervisor = SupervisorPattern(workers)

    task = Task(task_id="task1", input=NumberInput(value=5))
    result = await supervisor.delegate(task)

    assert result.is_err()
    assert isinstance(result, Err)
    assert result.recoverable  # Could retry with different worker

    stats = supervisor.get_worker_stats()
    assert stats["failing_tool"]["tasks_failed"] == 1


@pytest.mark.asyncio
async def test_supervisor_empty_workers() -> None:
    """Test supervisor requires at least one worker."""
    with pytest.raises(ValueError, match="at least one worker"):
        SupervisorPattern([])


# =============================================================================
# 4. Handoff Pattern Tests
# =============================================================================


@pytest.mark.asyncio
async def test_handoff_no_handoff_on_success() -> None:
    """Test handoff doesn't trigger on success by default."""
    primary = AddOneTool()
    handoff = HandoffPattern(primary, rules=[])

    result = await handoff.execute(NumberInput(value=5))

    assert result.is_ok()
    assert result.unwrap().value == 6


@pytest.mark.asyncio
async def test_handoff_on_failure() -> None:
    """Test handoff on failure condition."""
    primary = FailingTool()
    fallback = FallbackTool()

    rules = [
        HandoffRule(
            condition=HandoffCondition.FAILURE,
            from_tool="failing_tool",
            to_tool=fallback,
        )
    ]

    handoff = HandoffPattern(primary, rules)
    result = await handoff.execute(NumberInput(value=5))

    assert result.is_ok()
    assert result.unwrap().value == 0  # Fallback returns 0


@pytest.mark.asyncio
async def test_handoff_on_success() -> None:
    """Test handoff on success condition."""
    primary = AddOneTool()
    followup = MultiplyByTwoTool()

    rules = [
        HandoffRule(
            condition=HandoffCondition.SUCCESS,
            from_tool="add_one",
            to_tool=followup,
        )
    ]

    handoff = HandoffPattern(primary, rules)
    result = await handoff.execute(NumberInput(value=5))

    # Success triggers handoff: (5 + 1) → multiply by 2 = 12
    assert result.is_ok()
    assert result.unwrap().value == 12


@pytest.mark.asyncio
async def test_handoff_always() -> None:
    """Test unconditional handoff."""
    primary = AddOneTool()
    always_tool = SquareTool()

    rules = [
        HandoffRule(
            condition=HandoffCondition.ALWAYS,
            from_tool="add_one",
            to_tool=always_tool,
        )
    ]

    handoff = HandoffPattern(primary, rules)
    result = await handoff.execute(NumberInput(value=5))

    # Always handoff: (5 + 1) → square = 36
    assert result.is_ok()
    assert result.unwrap().value == 36


@pytest.mark.asyncio
async def test_handoff_with_transform() -> None:
    """Test handoff with transformation."""
    primary = AddOneTool()
    followup = SquareTool()

    def double_value(output: NumberOutput) -> NumberInput:
        return NumberInput(value=output.value * 2)

    rules = [
        HandoffRule(
            condition=HandoffCondition.SUCCESS,
            from_tool="add_one",
            to_tool=followup,
            transform=double_value,
        )
    ]

    handoff = HandoffPattern(primary, rules)
    result = await handoff.execute(NumberInput(value=5))

    # (5 + 1) → transform (*2) = 12 → square = 144
    assert result.is_ok()
    assert result.unwrap().value == 144


@pytest.mark.asyncio
async def test_handoff_multiple_rules() -> None:
    """Test handoff with multiple rules."""
    primary = FailingTool()
    fallback1 = FallbackTool()

    rules = [
        HandoffRule(
            condition=HandoffCondition.FAILURE,
            from_tool="failing_tool",
            to_tool=fallback1,
        ),
        HandoffRule(
            condition=HandoffCondition.TIMEOUT,
            from_tool="failing_tool",
            to_tool=AddOneTool(),
        ),
    ]

    handoff = HandoffPattern(primary, rules)
    result = await handoff.execute(NumberInput(value=5))

    # Failure handoff triggers
    assert result.is_ok()
    assert result.unwrap().value == 0


# =============================================================================
# 5. Dynamic Tool Selection Tests
# =============================================================================


@pytest.mark.asyncio
async def test_dynamic_cost_based() -> None:
    """Test cost-based tool selection."""
    tools = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    selector = DynamicToolSelector(tools, CostBasedSelection())

    context = SelectionContext(
        input=NumberInput(value=5),
        cost_budget_usd=0.01,
    )

    tool = await selector.select(context)
    assert tool is not None
    assert tool.name in ["add_one", "multiply_by_two", "square"]


@pytest.mark.asyncio
async def test_dynamic_latency_based() -> None:
    """Test latency-based tool selection."""
    tools = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    selector = DynamicToolSelector(tools, LatencyBasedSelection())

    context = SelectionContext(
        input=NumberInput(value=5),
        latency_budget_ms=5000,
    )

    tool = await selector.select(context)
    assert tool is not None


@pytest.mark.asyncio
async def test_dynamic_environment_based() -> None:
    """Test environment-based tool selection."""
    dev_tool = AddOneTool()
    prod_tool = MultiplyByTwoTool()

    tool_map = {
        "dev": dev_tool,
        "production": prod_tool,
    }

    tools = [dev_tool, prod_tool]
    selector = DynamicToolSelector(tools, EnvironmentBasedSelection(tool_map))

    # Dev environment
    dev_context = SelectionContext(
        input=NumberInput(value=5),
        environment="dev",
    )
    tool = await selector.select(dev_context)
    assert tool.name == "add_one"

    # Production environment
    prod_context = SelectionContext(
        input=NumberInput(value=5),
        environment="production",
    )
    tool = await selector.select(prod_context)
    assert tool.name == "multiply_by_two"


@pytest.mark.asyncio
async def test_dynamic_execute() -> None:
    """Test dynamic selector execute method."""
    tools = [AddOneTool(), MultiplyByTwoTool()]
    selector = DynamicToolSelector(tools, CostBasedSelection())

    context = SelectionContext(input=NumberInput(value=5))

    result = await selector.execute(context)

    assert result.is_ok()
    # Default selection (first tool) should give 5 + 1 = 6
    assert result.unwrap().value == 6


@pytest.mark.asyncio
async def test_dynamic_empty_tools() -> None:
    """Test dynamic selector requires at least one tool."""
    with pytest.raises(ValueError, match="at least one tool"):
        DynamicToolSelector([], CostBasedSelection())


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_integration_sequential_then_parallel() -> None:
    """Test combining sequential and parallel patterns."""
    # First: sequential (add 1, then multiply by 2)
    sequential: SequentialOrchestrator[Any, Any, Any] = SequentialOrchestrator(
        [AddOneTool(), MultiplyByTwoTool()]
    )
    seq_result = await sequential.execute(NumberInput(value=5))
    assert seq_result.is_ok()
    intermediate = seq_result.unwrap()  # (5 + 1) * 2 = 12

    # Then: parallel on result
    parallel = ParallelOrchestrator([AddOneTool(), SquareTool()])
    par_result = await parallel.execute(intermediate)
    assert par_result.is_ok()
    final = par_result.unwrap()
    assert final[0].value == 13  # 12 + 1
    assert final[1].value == 144  # 12^2


@pytest.mark.asyncio
async def test_integration_supervisor_with_handoff() -> None:
    """Test supervisor delegates to handoff patterns."""
    # Create handoff pattern (primary with fallback)
    primary = FailingTool()
    fallback = FallbackTool()
    rules = [
        HandoffRule(
            condition=HandoffCondition.FAILURE,
            from_tool="failing_tool",
            to_tool=fallback,
        )
    ]
    HandoffPattern(primary, rules)

    # Create supervisor with regular tools and handoff
    # Note: HandoffPattern is not a Tool, so we use regular tools
    workers = [AddOneTool(), MultiplyByTwoTool()]
    supervisor = SupervisorPattern(workers)

    task = Task(task_id="task1", input=NumberInput(value=5))
    result = await supervisor.delegate(task)

    assert result.is_ok()


@pytest.mark.asyncio
async def test_integration_dynamic_selects_from_parallel() -> None:
    """Test dynamic selector choosing from parallel results."""
    # This is more conceptual - in practice you'd have complex logic
    tools = [AddOneTool(), MultiplyByTwoTool(), SquareTool()]
    selector = DynamicToolSelector(tools, LatencyBasedSelection())

    context = SelectionContext(
        input=NumberInput(value=5),
        latency_budget_ms=1000,
    )

    result = await selector.execute(context)
    assert result.is_ok()
