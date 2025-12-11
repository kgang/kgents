"""
Agent-level pytest configuration.

Philosophy: Agents are morphisms in a category; fixtures support law verification.

This conftest provides:
- Agent-specific fixtures for cross-agent testing
- Integration test helpers
"""

from typing import Any

import pytest

# =============================================================================
# Cross-Agent Fixtures
# =============================================================================


@pytest.fixture
def agent_registry():
    """Registry of available agents for composition testing."""
    from agents.o.bootstrap_witness import IdentityAgent

    return {
        "id": IdentityAgent(),
        # Add more as available
    }


@pytest.fixture
def composition_helper():
    """Helper for testing agent composition."""
    from bootstrap import compose

    class CompositionHelper:
        """Helper class for composition testing."""

        def compose_chain(self, agents: list[Any]) -> Any:
            """Compose a list of agents left-to-right."""
            from functools import reduce

            return reduce(compose, agents)

        async def verify_identity(self, agent: Any, test_input: Any) -> bool:
            """Verify identity law for an agent."""
            from bootstrap import ID, compose

            # Id >> agent == agent
            left = await compose(ID, agent).invoke(test_input)
            # agent >> Id == agent
            right = await compose(agent, ID).invoke(test_input)
            # Direct
            direct = await agent.invoke(test_input)

            return left == direct == right

        async def verify_associativity(
            self, f: Any, g: Any, h: Any, test_input: Any
        ) -> bool:
            """Verify associativity for three agents."""
            from bootstrap import compose

            # (f >> g) >> h
            left = await compose(compose(f, g), h).invoke(test_input)
            # f >> (g >> h)
            right = await compose(f, compose(g, h)).invoke(test_input)

            return left == right

    return CompositionHelper()
