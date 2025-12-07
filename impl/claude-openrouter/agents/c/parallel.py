"""
C-gents: Parallel Composition - Fan-out and fan-in patterns.

Enables concurrent execution of agents with results combined.

Pattern:
        ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
"""

import asyncio
from typing import TypeVar, Callable, Sequence, Any

from bootstrap.types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class ParallelAgent(Agent[A, list[B]]):
    """
    Run multiple agents in parallel on the same input.

    All agents receive the same input.
    Returns list of all outputs (order preserved).
    """

    def __init__(self, agents: Sequence[Agent[A, B]]):
        self._agents = list(agents)
        names = ", ".join(a.name for a in self._agents)
        self._name = f"Parallel({names})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> list[B]:
        """Run all agents concurrently, collect results."""
        tasks = [agent.invoke(input) for agent in self._agents]
        return await asyncio.gather(*tasks)


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
    """

    def __init__(self, agents: Sequence[Agent[A, B]]):
        self._agents = list(agents)
        names = ", ".join(a.name for a in self._agents)
        self._name = f"Race({names})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        """Return first completed result."""
        tasks = [asyncio.create_task(agent.invoke(input)) for agent in self._agents]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel pending tasks
        for task in pending:
            task.cancel()

        # Return first completed result
        return done.pop().result()


# --- Convenience functions ---

def parallel(*agents: Agent[A, B]) -> ParallelAgent[A, B]:
    """Create a parallel agent from multiple agents."""
    return ParallelAgent(agents)


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
