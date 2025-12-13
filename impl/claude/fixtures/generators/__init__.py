"""
Fixture Generators: LLM-powered rich data generation.

These generators produce rich, LLM-generated fixture data.
They run once during fixture refresh and the output is cached.

Philosophy: LLM-once is cheap. Pre-compute rich data, hotload forever.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

# Registry of generators for CLI refresh
GENERATORS: dict[str, Callable[[], Awaitable[Any]]] = {}


def register_generator(name: str, generator: Callable[[], Awaitable[Any]]) -> None:
    """Register a generator function for a fixture."""
    GENERATORS[name] = generator


def get_generator(name: str) -> Callable[[], Awaitable[Any]] | None:
    """Get a generator by fixture name."""
    return GENERATORS.get(name)


# Future: Add LLM-powered generators here
# Example:
#
# async def generate_rich_agent_snapshot(archetype: str = "deliberator") -> AgentSnapshot:
#     """Generate rich agent snapshot via K-gent or void.compose.sip."""
#     from protocols.agentese import Logos
#     logos = Logos()
#     result = await logos.invoke("void.compose.sip", {"archetype": archetype})
#     return AgentSnapshot.from_dict(result)
