"""
Tool Orchestrator: Parallel Execution with Dependency Resolution.

Phase 3 of U-gent Tooling: Orchestration at the workflow level.

The Orchestrator enables:
- Parallel execution of independent tools (execute_parallel)
- Dependency-aware execution via DAG (execute_dag)
- Bounded concurrency (max 5 by default)
- Collect-all failure mode (aggregate errors, don't fail fast)

Key insight: The Orchestrator IS a Tool[A,B].
Just as >> is sequential composition, the Orchestrator is parallel composition.

Category perspective:
    >> : Tool[A,B] × Tool[B,C] → Tool[A,C]     (sequential)
    // : Tool[A,B] × Tool[A,C] → Tool[A,(B,C)] (parallel, same input)
    DAG: {name: Tool} × {name: deps} → Tool[inputs, outputs]

See: plans/ugent-tooling-phase3-handoff.md
See: spec/services/tooling.md §8 (Orchestration)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from .base import Tool, ToolCategory, ToolError, ToolResult

logger = logging.getLogger(__name__)

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


# =============================================================================
# Execution Results
# =============================================================================


@dataclass
class OrchestratorResult:
    """
    Result of an orchestrated execution.

    Contains all individual results plus aggregated metadata.
    """

    results: dict[str, ToolResult[Any]]  # tool_name → result
    errors: dict[str, ToolError]  # tool_name → error (if any)
    total_duration_ms: float
    success_count: int
    failure_count: int

    @property
    def all_succeeded(self) -> bool:
        """Check if all tools succeeded."""
        return self.failure_count == 0

    @property
    def all_failed(self) -> bool:
        """Check if all tools failed."""
        return self.success_count == 0

    def get_result(self, name: str) -> ToolResult[Any] | None:
        """Get result for a specific tool."""
        return self.results.get(name)

    def get_error(self, name: str) -> ToolError | None:
        """Get error for a specific tool."""
        return self.errors.get(name)


# =============================================================================
# DAG Node
# =============================================================================


@dataclass
class DAGNode:
    """
    A node in the execution DAG.

    Represents a tool with its input and dependencies.
    """

    name: str
    tool: Tool[Any, Any]
    request: Any
    depends_on: list[str] = field(default_factory=list)


# =============================================================================
# Tool Orchestrator
# =============================================================================


class ToolOrchestrator:
    """
    Orchestrator for parallel and DAG-based tool execution.

    Provides two execution modes:
    1. execute_parallel: Run independent tools concurrently
    2. execute_dag: Run tools in dependency order

    Bounded concurrency prevents resource exhaustion.
    Collect-all failure mode ensures partial results are captured.

    Example:
        orchestrator = ToolOrchestrator(max_concurrency=5)

        # Parallel execution
        result = await orchestrator.execute_parallel([
            (ReadTool(), ReadRequest(path="a.py")),
            (ReadTool(), ReadRequest(path="b.py")),
            (ReadTool(), ReadRequest(path="c.py")),
        ])

        # DAG execution
        result = await orchestrator.execute_dag([
            DAGNode("read", ReadTool(), ReadRequest(path="file.py")),
            DAGNode("grep", GrepTool(), GrepQuery(pattern="TODO"), depends_on=["read"]),
        ])
    """

    def __init__(
        self,
        max_concurrency: int = 5,
        fail_fast: bool = False,
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            max_concurrency: Maximum concurrent tool executions
            fail_fast: If True, cancel remaining on first error
        """
        self._max_concurrency = max_concurrency
        self._fail_fast = fail_fast
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_parallel(
        self,
        tools: list[tuple[Tool[Any, Any], Any]],
    ) -> OrchestratorResult:
        """
        Execute tools in parallel with bounded concurrency.

        All tools receive independent inputs and run concurrently.
        Results are collected even if some fail.

        Args:
            tools: List of (tool, request) tuples

        Returns:
            OrchestratorResult with all results and errors
            Keys are "{tool.name}:{index}" for uniqueness
        """
        if not tools:
            return OrchestratorResult(
                results={},
                errors={},
                total_duration_ms=0.0,
                success_count=0,
                failure_count=0,
            )

        start_time = datetime.now(UTC)
        results: dict[str, ToolResult[Any]] = {}
        errors: dict[str, ToolError] = {}

        async def run_tool(index: int, tool: Tool[Any, Any], request: Any) -> None:
            """Run a single tool with semaphore."""
            key = f"{tool.name}:{index}"
            async with self._semaphore:
                tool_start = datetime.now(UTC)
                try:
                    result = await tool.invoke(request)
                    duration_ms = (datetime.now(UTC) - tool_start).total_seconds() * 1000
                    results[key] = ToolResult(
                        value=result,
                        duration_ms=duration_ms,
                        tool_name=tool.name,
                    )
                except Exception as e:
                    if isinstance(e, ToolError):
                        errors[key] = e
                    else:
                        errors[key] = ToolError(str(e), tool.name)

        # Create tasks with index for unique keys
        tasks = [asyncio.create_task(run_tool(i, tool, req)) for i, (tool, req) in enumerate(tools)]

        # Wait for all (or until first error if fail_fast)
        if self._fail_fast:
            # Cancel remaining on first error
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for task in pending:
                task.cancel()
            # Gather cancelled to suppress warnings
            await asyncio.gather(*pending, return_exceptions=True)
        else:
            # Wait for all
            await asyncio.gather(*tasks, return_exceptions=True)

        total_duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return OrchestratorResult(
            results=results,
            errors=errors,
            total_duration_ms=total_duration,
            success_count=len(results),
            failure_count=len(errors),
        )

    async def execute_dag(
        self,
        nodes: list[DAGNode],
        pass_results: bool = False,
    ) -> OrchestratorResult:
        """
        Execute tools in dependency order.

        Tools are executed when all their dependencies complete.
        Concurrent execution where dependencies allow.

        Args:
            nodes: List of DAGNodes with dependencies
            pass_results: If True, pass predecessor results as context

        Returns:
            OrchestratorResult with all results and errors
        """
        if not nodes:
            return OrchestratorResult(
                results={},
                errors={},
                total_duration_ms=0.0,
                success_count=0,
                failure_count=0,
            )

        start_time = datetime.now(UTC)
        results: dict[str, ToolResult[Any]] = {}
        errors: dict[str, ToolError] = {}
        completed: set[str] = set()
        failed: set[str] = set()

        # Build node map
        node_map = {node.name: node for node in nodes}

        # Validate DAG (no cycles, valid deps)
        self._validate_dag(nodes)

        async def run_node(node: DAGNode) -> None:
            """Run a single node when dependencies are met."""
            async with self._semaphore:
                tool_start = datetime.now(UTC)
                try:
                    result = await node.tool.invoke(node.request)
                    duration_ms = (datetime.now(UTC) - tool_start).total_seconds() * 1000
                    results[node.name] = ToolResult(
                        value=result,
                        duration_ms=duration_ms,
                        tool_name=node.tool.name,
                    )
                    completed.add(node.name)
                except Exception as e:
                    if isinstance(e, ToolError):
                        errors[node.name] = e
                    else:
                        errors[node.name] = ToolError(str(e), node.tool.name)
                    failed.add(node.name)

        async def process_dag() -> None:
            """Process DAG level by level."""
            remaining = set(node_map.keys())
            in_progress: set[asyncio.Task[None]] = set()

            while remaining or in_progress:
                # Find ready nodes (deps satisfied, not failed deps)
                ready = []
                for name in list(remaining):
                    node = node_map[name]
                    deps_satisfied = all(d in completed for d in node.depends_on)
                    deps_failed = any(d in failed for d in node.depends_on)

                    if deps_failed:
                        # Skip nodes with failed dependencies
                        errors[name] = ToolError(
                            f"Dependency failed for {name}",
                            node.tool.name,
                        )
                        failed.add(name)
                        remaining.discard(name)
                    elif deps_satisfied:
                        ready.append(node)
                        remaining.discard(name)

                # Start ready nodes
                for node in ready:
                    task = asyncio.create_task(run_node(node))
                    in_progress.add(task)

                if not in_progress and remaining:
                    # Deadlock: remaining but no in_progress
                    raise ToolError(
                        f"DAG deadlock: {remaining} still pending but no progress",
                        "orchestrator",
                    )

                # Wait for at least one to complete
                if in_progress:
                    done, in_progress = await asyncio.wait(
                        in_progress, return_when=asyncio.FIRST_COMPLETED
                    )

        await process_dag()

        total_duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return OrchestratorResult(
            results=results,
            errors=errors,
            total_duration_ms=total_duration,
            success_count=len(results),
            failure_count=len(errors),
        )

    def _validate_dag(self, nodes: list[DAGNode]) -> None:
        """
        Validate DAG structure.

        Checks:
        - No duplicate names
        - All dependencies exist
        - No cycles

        Raises:
            ToolError: If DAG is invalid
        """
        names = {node.name for node in nodes}

        # Check duplicates
        if len(names) != len(nodes):
            raise ToolError("Duplicate node names in DAG", "orchestrator")

        # Check dependencies exist
        for node in nodes:
            for dep in node.depends_on:
                if dep not in names:
                    raise ToolError(
                        f"Unknown dependency '{dep}' for node '{node.name}'",
                        "orchestrator",
                    )

        # Check for cycles via DFS
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(name: str) -> bool:
            visited.add(name)
            rec_stack.add(name)

            node = next(n for n in nodes if n.name == name)
            for dep in node.depends_on:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.discard(name)
            return False

        for node in nodes:
            if node.name not in visited:
                if has_cycle(node.name):
                    raise ToolError("Cycle detected in DAG", "orchestrator")


# =============================================================================
# Parallel Tool (Wrapper)
# =============================================================================


@dataclass
class ParallelRequest(Generic[A]):
    """Request for parallel tool execution."""

    inputs: list[A]


@dataclass
class ParallelResponse(Generic[B]):
    """Response from parallel tool execution."""

    results: list[B | None]
    errors: list[str | None]
    success_count: int


class ParallelTool(Tool[ParallelRequest[A], ParallelResponse[B]], Generic[A, B]):
    """
    Wrapper that runs a tool in parallel over multiple inputs.

    This is the // operator reified as a Tool:
        parallel_read = ParallelTool(ReadTool())
        result = await parallel_read.invoke(ParallelRequest([req1, req2, req3]))

    Category note: This is the diagonal followed by parallel composition.
    """

    def __init__(
        self,
        tool: Tool[A, B],
        max_concurrency: int = 5,
    ) -> None:
        self._tool = tool
        self._orchestrator = ToolOrchestrator(max_concurrency=max_concurrency)

    @property
    def name(self) -> str:
        return f"parallel({self._tool.name})"

    @property
    def description(self) -> str:
        return f"Run {self._tool.name} in parallel over multiple inputs"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return self._tool.trust_required

    async def invoke(self, request: ParallelRequest[A]) -> ParallelResponse[B]:
        """
        Run tool in parallel over all inputs.

        Args:
            request: ParallelRequest with list of inputs

        Returns:
            ParallelResponse with results aligned to inputs
        """
        # Create tool instances (or reuse if stateless)
        tools = [(self._tool, inp) for inp in request.inputs]

        orch_result = await self._orchestrator.execute_parallel(tools)

        # Align results with inputs by index
        ordered_results: list[B | None] = []
        ordered_errors: list[str | None] = []

        for i in range(len(request.inputs)):
            key = f"{self._tool.name}:{i}"
            if key in orch_result.results:
                ordered_results.append(orch_result.results[key].value)
                ordered_errors.append(None)
            elif key in orch_result.errors:
                ordered_results.append(None)
                ordered_errors.append(str(orch_result.errors[key]))
            else:
                ordered_results.append(None)
                ordered_errors.append("No result")

        return ParallelResponse(
            results=ordered_results,
            errors=ordered_errors,
            success_count=orch_result.success_count,
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Results
    "OrchestratorResult",
    # DAG
    "DAGNode",
    # Orchestrator
    "ToolOrchestrator",
    # Parallel wrapper
    "ParallelRequest",
    "ParallelResponse",
    "ParallelTool",
]
