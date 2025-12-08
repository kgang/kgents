"""
C-gents: Parallel Composition - Fan-out and fan-in patterns.

Enables concurrent execution of agents with results combined.

Pattern:
        ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
"""

import asyncio
from typing import TypeVar, Callable, Sequence, Any, Optional
from dataclasses import dataclass

from bootstrap.types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass
class ParallelConfig:
    """
    Configuration for parallel execution with resource limits.

    Prevents DoS attacks from unbounded concurrent execution.
    """
    max_concurrent: int = 10  # Max parallel tasks
    timeout_per_agent: Optional[float] = None  # Per-agent timeout in seconds
    total_timeout: Optional[float] = None  # Total execution timeout

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_concurrent < 1:
            raise ValueError(f"max_concurrent must be >= 1, got {self.max_concurrent}")
        if self.timeout_per_agent is not None and self.timeout_per_agent <= 0:
            raise ValueError(f"timeout_per_agent must be > 0, got {self.timeout_per_agent}")
        if self.total_timeout is not None and self.total_timeout <= 0:
            raise ValueError(f"total_timeout must be > 0, got {self.total_timeout}")


@dataclass
class ParallelResult:
    """Result container for parallel execution with partial failure support."""
    successes: list[tuple[int, Any]]  # (index, result) pairs
    failures: list[tuple[int, Exception]]  # (index, error) pairs
    
    def has_failures(self) -> bool:
        return len(self.failures) > 0
    
    def all_results_or_raise(self) -> list[Any]:
        """Get all results in order, or raise first exception."""
        if self.failures:
            raise self.failures[0][1]
        return [result for _, result in sorted(self.successes)]


class ParallelAgent(Agent[A, list[B]]):
    """
    Run multiple agents in parallel on the same input.

    All agents receive the same input.
    Returns list of all outputs (order preserved).
    Raises exception if any agent fails.

    Security: Enforces resource limits via ParallelConfig to prevent DoS.
    """

    def __init__(
        self,
        agents: Sequence[Agent[A, B]],
        allow_partial: bool = False,
        config: Optional[ParallelConfig] = None,
    ):
        self._agents = list(agents)
        self._allow_partial = allow_partial
        self._config = config or ParallelConfig()
        names = ", ".join(a.name for a in self._agents)
        self._name = f"Parallel({names})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> list[B]:
        """
        Run all agents concurrently with resource limits.

        Uses semaphore to limit concurrent executions and prevent resource exhaustion.
        """
        # Create semaphore for concurrency limit
        semaphore = asyncio.Semaphore(self._config.max_concurrent)

        async def _run_with_limit(agent: Agent[A, B]) -> B:
            """Execute single agent with semaphore and timeout."""
            async with semaphore:
                if self._config.timeout_per_agent:
                    return await asyncio.wait_for(
                        agent.invoke(input),
                        timeout=self._config.timeout_per_agent
                    )
                else:
                    return await agent.invoke(input)

        tasks = [_run_with_limit(agent) for agent in self._agents]

        if self._config.total_timeout:
            # Apply total timeout to all tasks
            if self._allow_partial:
                result = await asyncio.wait_for(
                    self._invoke_with_partial_limited(input, semaphore),
                    timeout=self._config.total_timeout
                )
                return result.all_results_or_raise()
            else:
                return await asyncio.wait_for(
                    asyncio.gather(*tasks),
                    timeout=self._config.total_timeout
                )
        else:
            if self._allow_partial:
                result = await self._invoke_with_partial_limited(input, semaphore)
                return result.all_results_or_raise()
            else:
                return await asyncio.gather(*tasks)
    
    async def _invoke_with_partial(self, input: A) -> ParallelResult:
        """Run with partial failure tracking (legacy, no resource limits)."""
        tasks = [agent.invoke(input) for agent in self._agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successes = []
        failures = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append((idx, result))
            else:
                successes.append((idx, result))

        return ParallelResult(successes=successes, failures=failures)

    async def _invoke_with_partial_limited(self, input: A, semaphore: asyncio.Semaphore) -> ParallelResult:
        """Run with partial failure tracking AND resource limits."""
        async def _run_with_limit(agent: Agent[A, B]) -> B:
            """Execute single agent with semaphore and timeout."""
            async with semaphore:
                if self._config.timeout_per_agent:
                    return await asyncio.wait_for(
                        agent.invoke(input),
                        timeout=self._config.timeout_per_agent
                    )
                else:
                    return await agent.invoke(input)

        tasks = [_run_with_limit(agent) for agent in self._agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successes = []
        failures = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append((idx, result))
            else:
                successes.append((idx, result))

        return ParallelResult(successes=successes, failures=failures)


class FanOutAgent(Agent[A, tuple]):
    """
    Fan-out: send input to multiple agents, return tuple of results.

    Similar to Parallel but returns tuple for heterogeneous types.
    """

    def __init__(self, *agents: Agent[A, Any]):
        self._agents = agents
        names = ", ".join(a.name for a in self._agents)
        self._name = f"FanOut({names})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> tuple:
        """Run all agents concurrently, return tuple of results."""
        tasks = [agent.invoke(input) for agent in self._agents]
        results = await asyncio.gather(*tasks)
        return tuple(results)


class CombineAgent(Agent[A, C]):
    """
    Run agents in parallel, then combine their outputs.

    Pattern: input → [parallel agents] → combiner → output
    """

    def __init__(
        self,
        agents: Sequence[Agent[A, B]],
        combiner: Callable[[list[B]], C],
    ):
        self._parallel = ParallelAgent(agents)
        self._combiner = combiner
        self._name = f"Combine({self._parallel.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> C:
        """Run parallel agents, then combine results."""
        results = await self._parallel.invoke(input)
        return self._combiner(results)


class RaceAgent(Agent[A, B]):
    """
    Run multiple agents in parallel, return first completed result.

    Useful for redundancy or timeout patterns.
    Properly cancels pending tasks to avoid resource leaks.
    """

    def __init__(self, agents: Sequence[Agent[A, B]]):
        self._agents = list(agents)
        names = ", ".join(a.name for a in self._agents)
        self._name = f"Race({names})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        """Return first completed result, cancel others."""
        tasks = [asyncio.create_task(agent.invoke(input)) for agent in self._agents]
        
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Wait for cancellation to complete
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            
            # Return first completed result (may raise if it failed)
            return done.pop().result()
        except Exception:
            # If error occurs, ensure all tasks are cancelled
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise


# --- Convenience functions ---

def parallel(
    *agents: Agent[A, B],
    config: Optional[ParallelConfig] = None
) -> ParallelAgent[A, B]:
    """
    Create a parallel agent from multiple agents.

    Args:
        *agents: Agents to run in parallel
        config: Optional resource limits configuration

    Example:
        # With default limits (max 10 concurrent)
        result = await parallel(agent1, agent2, agent3).invoke(input)

        # Custom limits
        config = ParallelConfig(max_concurrent=5, timeout_per_agent=30.0)
        result = await parallel(agent1, agent2, config=config).invoke(input)
    """
    return ParallelAgent(agents, config=config)


def fan_out(*agents: Agent[A, Any]) -> FanOutAgent[A]:
    """Fan out input to multiple agents, return tuple of results."""
    return FanOutAgent(*agents)


def combine(
    agents: Sequence[Agent[A, B]],
    combiner: Callable[[list[B]], C],
) -> CombineAgent[A, C]:
    """Run agents in parallel, combine with custom function."""
    return CombineAgent(agents, combiner)


def race(*agents: Agent[A, B]) -> RaceAgent[A, B]:
    """Race multiple agents, return first result."""
    return RaceAgent(agents)
