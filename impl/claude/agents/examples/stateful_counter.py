"""
Stateful Counter: Memory Without Complexity.

The @Stateful capability adds state management to your agent.
The Projector decides HOW state is stored:
- LocalProjector: In-memory or SQLite
- K8sProjector: StatefulSet + PVC

Key insight:
    State is declared, not implemented. You focus on WHAT state you need,
    the Projector handles WHERE it lives.

Run:
    python -m agents.examples.stateful_counter
"""

import asyncio
from dataclasses import dataclass, field

from agents.a import Capability, Delta, get_halo
from agents.poly.types import Agent


@dataclass
class CounterState:
    """The state schema for our counter."""

    count: int = 0
    history: list[int] = field(default_factory=list)


@Capability.Stateful(schema=CounterState)
class CounterAgent(Agent[int, int]):
    """
    A counter that remembers its state.

    Type: Agent[int, int]
    Input: Amount to add
    Output: New count

    The @Stateful decorator declares that this agent needs state.
    The state schema (CounterState) defines WHAT is stored.

    Note: This example shows the declaration pattern. Full state
    threading happens when compiled through LocalProjector.
    """

    def __init__(self) -> None:
        self._state = CounterState()

    @property
    def name(self) -> str:
        return "counter"

    async def invoke(self, input: int) -> int:
        """Add to counter, return new count."""
        self._state.count += input
        self._state.history.append(self._state.count)
        return self._state.count


class CounterUsingDelta(Delta[int, int]):
    """
    Alternative: Using the Delta archetype.

    Delta = Stateful + Observable (data-focused archetype).
    No decorator needed — capabilities come from inheritance.
    """

    def __init__(self) -> None:
        self._count = 0

    @property
    def name(self) -> str:
        return "delta-counter"

    async def invoke(self, input: int) -> int:
        self._count += input
        return self._count


async def main() -> None:
    """Demonstrate stateful agents."""
    # Using @Stateful decorator
    counter = CounterAgent()

    result1 = await counter.invoke(5)
    result2 = await counter.invoke(3)
    result3 = await counter.invoke(-2)

    print(f"Count: {result1} -> {result2} -> {result3}")
    print(f"History: {counter._state.history}")

    # Inspect the Halo
    halo = get_halo(CounterAgent)
    print(f"\nHalo capabilities: {[type(cap).__name__ for cap in halo]}")

    # Using Delta archetype
    _delta_counter = CounterUsingDelta()  # Unused but shows instantiation pattern
    delta_halo = get_halo(CounterUsingDelta)
    print(f"Delta capabilities: {[type(cap).__name__ for cap in delta_halo]}")


if __name__ == "__main__":
    asyncio.run(main())
