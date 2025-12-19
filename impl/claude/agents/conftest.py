"""
Agent-level pytest configuration.

Philosophy: Agents are morphisms in a category; fixtures support law verification.

This conftest provides:
- Registry population fixtures for xdist-safe parallel execution
- Agent-specific fixtures for cross-agent testing
- Integration test helpers
"""

from __future__ import annotations

from typing import Any

import pytest

# =============================================================================
# Registry Population (xdist-safe)
# =============================================================================
#
# NOTE: The authoritative registry population fixture is in impl/claude/conftest.py:
#   _ensure_global_registries_populated()
#
# That fixture runs at session start for ALL tests, populating both:
# - OperadRegistry (all operads)
# - NodeRegistry (all AGENTESE nodes)
#
# See: agents/operad/_tests/test_xdist_registry_canary.py for verification tests.


# =============================================================================
# Cross-Agent Fixtures
# =============================================================================


class CompositionHelper:
    """Helper class for composition testing."""

    def compose_chain(self, agents: list[Any]) -> Any:
        """Compose a list of agents left-to-right."""
        from functools import reduce

        from agents.poly import compose

        return reduce(compose, agents)

    async def verify_identity(self, agent: Any, test_input: Any) -> bool:
        """Verify identity law for an agent."""
        from agents.poly import ID, compose

        # Id >> agent == agent
        left: Any = await compose(ID, agent).invoke(test_input)  # type: ignore[arg-type]
        # agent >> Id == agent
        right: Any = await compose(agent, ID).invoke(test_input)  # type: ignore[arg-type]
        # Direct
        direct = await agent.invoke(test_input)

        return bool(left == direct == right)

    async def verify_associativity(self, f: Any, g: Any, h: Any, test_input: Any) -> bool:
        """Verify associativity for three agents."""
        from agents.poly import compose

        # (f >> g) >> h
        left = await compose(compose(f, g), h).invoke(test_input)
        # f >> (g >> h)
        right = await compose(f, compose(g, h)).invoke(test_input)

        return bool(left == right)


@pytest.fixture
def agent_registry() -> dict[str, Any]:
    """Registry of available agents for composition testing."""
    from agents.o.bootstrap_witness import IdentityAgent

    return {
        "id": IdentityAgent(),
        # Add more as available
    }


@pytest.fixture
def composition_helper() -> CompositionHelper:
    """Helper for testing agent composition."""
    return CompositionHelper()
