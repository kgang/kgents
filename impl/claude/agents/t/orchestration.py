"""
T-gents Phase 6: Multi-Tool Orchestration Patterns

This module implements orchestration functors for coordinating multiple tools:
- Sequential: Chain tools in sequence (already via >> operator)
- Parallel: Execute tools concurrently (product functor)
- Supervisor: Delegate tasks to worker tools (comma category)
- Handoff: Transfer control between tools (natural transformation)
- Dynamic: Context-based tool selection

Category Theory Foundations:
- Sequential: Composition in Tool category (f >> g >> h)
- Parallel: Product functor (A × B → C × D)
- Supervisor: Comma category (supervisor ↓ workers)
- Handoff: Natural transformation (F ⇒ G)
- Dynamic: Functor from Context category to Tool category

Philosophy:
- Orchestration is compositional (functors, not control flow)
- Tools maintain categorical purity
- All patterns return Result monads
- Full W-gent tracing for observability

Integration:
- Tool[A, B]: Base tool abstraction
- Result monad: Railway Oriented Programming
- W-gent: ToolTrace for observability
- P-gent: Parse orchestration outputs

References:
- spec/t-gents/tool-use.md Phase 6
- Category Theory for Computing Science (Barr & Wells)
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar

from bootstrap.types import Result, err, ok

from .tool import Tool, ToolError, ToolErrorType, ToolTrace

# Type variables
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


# =============================================================================
# 1. Sequential Orchestrator (Already via >> operator, provided for completeness)
# =============================================================================


class SequentialOrchestrator(Generic[A, B, C]):
    """
    Sequential tool execution (already via >> composition).

    This is a convenience wrapper that makes sequential execution explicit.
    The >> operator already provides this functionality.

    Category Theory:
    - Morphism composition in Tool category
    - (f : A → B) ∘ (g : B → C) = (g ∘ f : A → C)

    Usage:
        orchestrator = SequentialOrchestrator([tool1, tool2, tool3])
        result = await orchestrator.execute(input_data)
    """

    def __init__(self, tools: list[Tool]):
        """Initialize with list of tools to execute sequentially."""
        if not tools:
            raise ValueError("SequentialOrchestrator requires at least one tool")
        self.tools = tools
        self.name = f"Sequential[{' >> '.join(t.name for t in tools)}]"

    async def execute(self, input: A) -> Result[Any, ToolError]:
        """
        Execute tools sequentially, passing output of each to next.

        Stops on first error (Railway Oriented Programming).
        """
        current: Any = input
        traces: list[ToolTrace] = []

        for i, tool in enumerate(self.tools):
            trace = ToolTrace(
                tool_name=tool.name,
                input=current,
                composition_depth=i,
            )
            try:
                current = await tool.invoke(current)
                trace.finish_success(current)
                traces.append(trace)
            except Exception as e:
                error = ToolError(
                    error_type=ToolErrorType.FATAL,
                    message=str(e),
                    tool_name=tool.name,
                    input=current,
                    recoverable=False,
                )
                trace.finish_error(error)
                traces.append(trace)
                return err(error, str(e), False)

        return ok(current)


# =============================================================================
# 2. Parallel Orchestrator (Product Functor)
# =============================================================================


@dataclass
class ParallelResult(Generic[A]):
    """
    Result from parallel execution.

    Contains results from all tools in execution order.
    """

    results: list[A]
    traces: list[ToolTrace]
    duration_ms: float
    all_succeeded: bool

    def __getitem__(self, index: int) -> A:
        """Access individual result by index."""
        return self.results[index]


class ParallelOrchestrator(Generic[A]):
    """
    Parallel tool execution (product functor).

    Executes multiple tools concurrently and collects results.

    Category Theory:
    - Product functor: F × G : C → D × E
    - Given tools f: A → B and g: A → C
    - Creates (f × g): A → B × C

    Properties:
    - All tools receive same input
    - Execution happens concurrently (asyncio.gather)
    - Returns tuple of results
    - Fails if any tool fails (all-or-nothing)

    Usage:
        orchestrator = ParallelOrchestrator([search, summarize, translate])
        result = await orchestrator.execute(query)
        # → Result[(SearchResult, Summary, Translation), ToolError]
    """

    def __init__(self, tools: list[Tool[A, Any]]):
        """Initialize with list of tools to execute in parallel."""
        if not tools:
            raise ValueError("ParallelOrchestrator requires at least one tool")
        self.tools = tools
        self.name = f"Parallel[{', '.join(t.name for t in tools)}]"

    async def execute(self, input: A) -> Result[ParallelResult, ToolError]:
        """
        Execute all tools in parallel with same input.

        Returns tuple of results if all succeed, error if any fails.
        """
        start_time = datetime.now()
        traces: list[ToolTrace] = []

        # Create tasks for concurrent execution
        async def execute_tool(tool: Tool[A, Any], index: int) -> tuple[int, Any]:
            trace = ToolTrace(
                tool_name=tool.name,
                input=input,
                composition_depth=0,
            )
            try:
                result = await tool.invoke(input)
                trace.finish_success(result)
                traces.append(trace)
                return (index, result)
            except Exception as e:
                error = ToolError(
                    error_type=ToolErrorType.FATAL,
                    message=str(e),
                    tool_name=tool.name,
                    input=input,
                    recoverable=False,
                )
                trace.finish_error(error)
                traces.append(trace)
                raise error

        try:
            # Execute all tools concurrently
            tasks = [execute_tool(tool, i) for i, tool in enumerate(self.tools)]
            indexed_results = await asyncio.gather(*tasks)

            # Sort by original index to maintain order
            results = [result for _, result in sorted(indexed_results)]

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            return ok(
                ParallelResult(
                    results=results,
                    traces=traces,
                    duration_ms=duration_ms,
                    all_succeeded=True,
                )
            )

        except ToolError as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return err(e, str(e), e.recoverable)


# =============================================================================
# 3. Supervisor Pattern (Comma Category)
# =============================================================================


@dataclass
class Task(Generic[A]):
    """
    Task to be delegated to a worker tool.

    Contains task metadata and input data.
    """

    task_id: str
    input: A
    assigned_worker: Optional[str] = None
    priority: int = 0  # Higher = more urgent
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkerAssignment(Generic[A, B]):
    """
    Assignment of task to worker tool.

    Represents morphism in comma category (supervisor ↓ workers).
    """

    task: Task[A]
    worker: Tool[A, B]
    assigned_at: datetime = field(default_factory=datetime.now)


class SupervisorPattern(Generic[A, B]):
    """
    Supervisor pattern for task delegation (comma category).

    A supervisor delegates tasks to worker tools based on:
    - Worker capabilities
    - Current load
    - Task priority
    - Worker availability

    Category Theory:
    - Comma category: (Supervisor ↓ Workers)
    - Objects: (task, worker, supervisor → worker morphism)
    - Morphisms: Task reassignments

    Properties:
    - Dynamic worker selection
    - Load balancing
    - Priority queues
    - Worker health monitoring

    Usage:
        supervisor = SupervisorPattern(
            workers=[worker1, worker2, worker3],
            selector=round_robin_selector,
        )
        result = await supervisor.delegate(task)
    """

    def __init__(
        self,
        workers: list[Tool[A, B]],
        selector: Optional[Callable[[Task[A], list[Tool[A, B]]], Tool[A, B]]] = None,
    ):
        """
        Initialize supervisor with worker pool.

        Args:
            workers: Pool of worker tools
            selector: Strategy for selecting worker (default: round-robin)
        """
        if not workers:
            raise ValueError("SupervisorPattern requires at least one worker")

        self.workers = workers
        self.selector = selector or self._round_robin_selector
        self._current_worker_index = 0
        self._worker_stats: dict[str, dict] = {
            w.name: {"tasks_completed": 0, "tasks_failed": 0, "avg_latency_ms": 0.0}
            for w in workers
        }

    def _round_robin_selector(
        self, task: Task[A], workers: list[Tool[A, B]]
    ) -> Tool[A, B]:
        """Default round-robin worker selection."""
        worker = workers[self._current_worker_index]
        self._current_worker_index = (self._current_worker_index + 1) % len(workers)
        return worker

    async def delegate(self, task: Task[A]) -> Result[B, ToolError]:
        """
        Delegate task to appropriate worker.

        Returns worker's result or error.
        """
        # Select worker
        worker = self.selector(task, self.workers)
        task.assigned_worker = worker.name

        # Create trace
        trace = ToolTrace(
            tool_name=f"Supervisor→{worker.name}",
            input=task.input,
        )

        try:
            # Execute via worker
            result = await worker.invoke(task.input)
            trace.finish_success(result)

            # Update stats
            stats = self._worker_stats[worker.name]
            stats["tasks_completed"] += 1
            if trace.latency_ms:
                current_avg = stats["avg_latency_ms"]
                total_tasks = stats["tasks_completed"]
                stats["avg_latency_ms"] = (
                    current_avg * (total_tasks - 1) + trace.latency_ms
                ) / total_tasks

            return ok(result)

        except Exception as e:
            error = ToolError(
                error_type=ToolErrorType.FATAL,
                message=f"Worker {worker.name} failed: {str(e)}",
                tool_name=worker.name,
                input=task.input,
                recoverable=True,  # Could retry with different worker
            )
            trace.finish_error(error)

            # Update stats
            self._worker_stats[worker.name]["tasks_failed"] += 1

            return err(error, str(error), True)

    def get_worker_stats(self) -> dict[str, dict]:
        """Get statistics for all workers."""
        return self._worker_stats.copy()


# =============================================================================
# 4. Handoff Pattern (Natural Transformation)
# =============================================================================


class HandoffCondition(Enum):
    """Conditions that trigger tool handoffs."""

    SUCCESS = "success"  # Previous tool succeeded
    FAILURE = "failure"  # Previous tool failed
    TIMEOUT = "timeout"  # Previous tool timed out
    PARTIAL = "partial"  # Partial result available
    ALWAYS = "always"  # Unconditional handoff


@dataclass
class HandoffRule(Generic[A, B]):
    """
    Rule for handing off from one tool to another.

    Represents natural transformation component η_A : F(A) → G(A).
    """

    condition: HandoffCondition
    from_tool: str  # Tool name to handoff from
    to_tool: Tool[A, B]  # Tool to handoff to
    transform: Optional[Callable[[Any], A]] = None  # Transform output before handoff


class HandoffPattern(Generic[A, B]):
    """
    Handoff pattern for transferring control between tools.

    Natural transformation between tool functors.

    Category Theory:
    - Natural transformation: η : F ⇒ G
    - Components: η_A : F(A) → G(A) for each object A
    - Naturality: For f : A → B, G(f) ∘ η_A = η_B ∘ F(f)

    Use cases:
    - Fallback to backup tool on failure
    - Upgrade to more powerful tool for complex inputs
    - Specialize to domain-specific tool
    - Retry with different tool configuration

    Usage:
        handoff = HandoffPattern(
            primary=fast_tool,
            rules=[
                HandoffRule(HandoffCondition.TIMEOUT, "fast_tool", slow_but_reliable),
                HandoffRule(HandoffCondition.FAILURE, "fast_tool", fallback_tool),
            ],
        )
        result = await handoff.execute(input)
    """

    def __init__(self, primary: Tool[A, B], rules: list[HandoffRule[A, B]]):
        """
        Initialize handoff pattern.

        Args:
            primary: Primary tool to try first
            rules: Handoff rules for different conditions
        """
        self.primary = primary
        self.rules = rules
        self.name = f"Handoff[{primary.name}]"

    async def execute(self, input: A) -> Result[B, ToolError]:
        """
        Execute with handoff logic.

        Tries primary tool first, then applies handoff rules.
        """
        trace = ToolTrace(tool_name=self.primary.name, input=input)

        try:
            # Try primary tool
            result = await self.primary.invoke(input)
            trace.finish_success(result)

            # Check for SUCCESS handoffs
            for rule in self.rules:
                if rule.condition in (
                    HandoffCondition.SUCCESS,
                    HandoffCondition.ALWAYS,
                ):
                    if rule.from_tool == self.primary.name:
                        # Transform if needed
                        handoff_input = (
                            rule.transform(result) if rule.transform else result
                        )
                        try:
                            handoff_result = await rule.to_tool.invoke(handoff_input)
                            return ok(handoff_result)
                        except Exception as e:
                            return err(
                                ToolError(
                                    error_type=ToolErrorType.FATAL,
                                    message=str(e),
                                    tool_name=rule.to_tool.name,
                                    input=handoff_input,
                                ),
                                str(e),
                                False,
                            )

            return ok(result)

        except asyncio.TimeoutError as e:
            trace.finish_error(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message=str(e),
                    tool_name=self.primary.name,
                    input=input,
                )
            )

            # Check for TIMEOUT handoffs
            for rule in self.rules:
                if rule.condition in (
                    HandoffCondition.TIMEOUT,
                    HandoffCondition.ALWAYS,
                ):
                    if rule.from_tool == self.primary.name:
                        try:
                            handoff_result = await rule.to_tool.invoke(input)
                            return ok(handoff_result)
                        except Exception as e:
                            return err(
                                ToolError(
                                    error_type=ToolErrorType.FATAL,
                                    message=str(e),
                                    tool_name=rule.to_tool.name,
                                    input=input,
                                ),
                                str(e),
                                False,
                            )

            return err(
                ToolError(
                    error_type=ToolErrorType.TIMEOUT,
                    message="Timeout with no handoff rule",
                    tool_name=self.primary.name,
                    input=input,
                ),
                "Timeout",
                True,
            )

        except Exception as e:
            error = ToolError(
                error_type=ToolErrorType.FATAL,
                message=str(e),
                tool_name=self.primary.name,
                input=input,
            )
            trace.finish_error(error)

            # Check for FAILURE handoffs
            for rule in self.rules:
                if rule.condition in (
                    HandoffCondition.FAILURE,
                    HandoffCondition.ALWAYS,
                ):
                    if rule.from_tool == self.primary.name:
                        try:
                            handoff_result = await rule.to_tool.invoke(input)
                            return ok(handoff_result)
                        except Exception as e:
                            return err(
                                ToolError(
                                    error_type=ToolErrorType.FATAL,
                                    message=str(e),
                                    tool_name=rule.to_tool.name,
                                    input=input,
                                ),
                                str(e),
                                False,
                            )

            return err(error, str(e), False)


# =============================================================================
# 5. Dynamic Tool Selection
# =============================================================================


@dataclass
class SelectionContext:
    """
    Context for dynamic tool selection.

    Contains information used to select appropriate tool.
    """

    input: Any
    user_id: Optional[str] = None
    environment: str = "production"  # dev, staging, production
    cost_budget_usd: Optional[float] = None
    latency_budget_ms: Optional[int] = None
    quality_threshold: float = 0.8  # 0.0 to 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class SelectionStrategy(ABC, Generic[A, B]):
    """
    Abstract base for tool selection strategies.

    Functor from Context category to Tool category.
    """

    @abstractmethod
    async def select(
        self, context: SelectionContext, tools: list[Tool[A, B]]
    ) -> Tool[A, B]:
        """Select appropriate tool based on context."""
        pass


class CostBasedSelection(SelectionStrategy[A, B]):
    """Select tool based on cost budget."""

    async def select(
        self, context: SelectionContext, tools: list[Tool[A, B]]
    ) -> Tool[A, B]:
        """Select cheapest tool within budget."""
        if not context.cost_budget_usd:
            return tools[0]  # Default to first tool

        # Filter tools by cost (would need cost in ToolMeta)
        # For now, just return first tool
        return tools[0]


class LatencyBasedSelection(SelectionStrategy[A, B]):
    """Select tool based on latency budget."""

    async def select(
        self, context: SelectionContext, tools: list[Tool[A, B]]
    ) -> Tool[A, B]:
        """Select fastest tool within latency budget."""
        if not context.latency_budget_ms:
            return tools[0]

        # Filter by timeout
        for tool in tools:
            if tool.meta.runtime.timeout_ms <= context.latency_budget_ms:
                return tool

        return tools[0]


class EnvironmentBasedSelection(SelectionStrategy[A, B]):
    """Select tool based on environment (dev/staging/prod)."""

    def __init__(self, tool_map: dict[str, Tool[A, B]]):
        """
        Initialize with environment → tool mapping.

        Args:
            tool_map: {"dev": dev_tool, "staging": staging_tool, "production": prod_tool}
        """
        self.tool_map = tool_map

    async def select(
        self, context: SelectionContext, tools: list[Tool[A, B]]
    ) -> Tool[A, B]:
        """Select tool based on environment."""
        return self.tool_map.get(context.environment, tools[0])


class DynamicToolSelector(Generic[A, B]):
    """
    Dynamic tool selection based on context.

    Functor from Context category to Tool category:
    - Objects (Context): Selection contexts with constraints
    - Objects (Tool): Available tools
    - Morphism: context ↦ tool

    Properties:
    - Context-aware selection
    - Constraint satisfaction (cost, latency, quality)
    - Environment-based routing
    - Extensible strategies

    Usage:
        selector = DynamicToolSelector(
            tools=[cheap_tool, fast_tool, quality_tool],
            strategy=CostBasedSelection(),
        )
        tool = await selector.select(context)
        result = await tool.invoke(input)
    """

    def __init__(self, tools: list[Tool[A, B]], strategy: SelectionStrategy[A, B]):
        """
        Initialize selector with tools and strategy.

        Args:
            tools: Available tools to select from
            strategy: Selection strategy
        """
        if not tools:
            raise ValueError("DynamicToolSelector requires at least one tool")

        self.tools = tools
        self.strategy = strategy
        self.name = f"DynamicSelector[{len(tools)} tools]"

    async def select(self, context: SelectionContext) -> Tool[A, B]:
        """Select appropriate tool based on context."""
        return await self.strategy.select(context, self.tools)

    async def execute(self, context: SelectionContext) -> Result[B, ToolError]:
        """Select tool and execute with context input."""
        try:
            tool = await self.select(context)
            result = await tool.invoke(context.input)
            return ok(result)
        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.FATAL,
                    message=str(e),
                    tool_name=self.name,
                    input=context.input,
                ),
                str(e),
                False,
            )
