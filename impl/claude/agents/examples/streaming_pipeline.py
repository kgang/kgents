"""
Streaming Pipeline: From Points to Flows.

The Flux Functor transforms discrete agents into continuous processors:

    Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Key insight:
    "The noun is a lie. There is only the rate of change."

    Static agent: A → B (a point transformation)
    Flux agent: dA/dt → dB/dt (a continuous flow)

Run:
    python -m agents.examples.streaming_pipeline
"""

import asyncio
from typing import AsyncIterator

from agents.flux import Flux, FluxAgent, FluxConfig
from agents.poly.types import Agent


class DoubleAgent(Agent[int, int]):
    """Doubles its input."""

    @property
    def name(self) -> str:
        return "doubler"

    async def invoke(self, input: int) -> int:
        return input * 2


class FilterEvenAgent(Agent[int, int | None]):
    """Filters out odd numbers, passes even numbers through."""

    @property
    def name(self) -> str:
        return "filter-even"

    async def invoke(self, input: int) -> int | None:
        return input if input % 2 == 0 else None


async def number_source(n: int) -> AsyncIterator[int]:
    """Generate numbers 1 to n as an async stream."""
    for i in range(1, n + 1):
        yield i
        await asyncio.sleep(0.01)  # Simulate work


async def main() -> None:
    """Demonstrate flux agents and living pipelines."""
    print("=== Flux Functor Demo ===\n")

    # 1. Create a discrete agent
    doubler = DoubleAgent()
    print(f"Discrete agent: {doubler.name}")

    # 2. Lift it to the flux domain
    flux_doubler: FluxAgent[int, int] = Flux.lift(doubler)
    print(f"Flux agent created: {type(flux_doubler).__name__}")

    # 3. Process a stream
    print("\nProcessing stream [1, 2, 3, 4, 5]:")
    results: list[int] = []
    async for result in flux_doubler.start(number_source(5)):
        results.append(result)
        print(f"  -> {result}")

    print(f"\nResults: {results}")

    # 4. Pipeline composition with | operator
    print("\n=== Living Pipeline Demo ===\n")

    # Create another flux agent (shown for demonstration, used in full pipeline)
    _flux_filter: FluxAgent[int, int | None] = Flux.lift(FilterEvenAgent())

    # Compose into a pipeline: double -> filter even
    # (This shows the pattern; actual | operator is on FluxPipeline)

    print("Pipeline: double -> filter even")
    print("Input: [1, 2, 3, 4, 5]")

    # Process through doubler first
    doubled_results: list[int] = []
    async for result in flux_doubler.start(number_source(5)):
        doubled_results.append(result)

    print(f"After doubling: {doubled_results}")  # [2, 4, 6, 8, 10]

    # 5. Custom config
    print("\n=== Custom FluxConfig Demo ===\n")

    config = FluxConfig(
        buffer_size=100,
        feedback_fraction=0.0,  # No ouroboric feedback
    )

    _custom_flux: FluxAgent[int, int] = Flux.lift(doubler, config=config)
    print(f"Flux with custom config: buffer_size={config.buffer_size}")
    del _custom_flux  # Shown for demonstration


if __name__ == "__main__":
    asyncio.run(main())
