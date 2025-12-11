"""
Bootstrap test configuration.

Philosophy: The bootstrap kernel is the irreducible core.
These fixtures verify laws hold.

This conftest provides:
- BootstrapWitness for law verification
- Composition primitives for testing
"""

from typing import Any, Callable

import pytest

# =============================================================================
# Bootstrap Agent Fixtures
# =============================================================================


@pytest.fixture
def id_agent():
    """Identity agent from bootstrap."""
    from bootstrap import ID

    return ID


@pytest.fixture
def compose_fn():
    """Compose function from bootstrap."""
    from bootstrap import compose

    return compose


# =============================================================================
# Test Agent Factory
# =============================================================================


@pytest.fixture
def make_test_agent():
    """Factory for creating test agents with known transforms."""
    from agents.o.bootstrap_witness import TestAgent

    def factory(name: str, transform: Callable[[Any], Any]) -> Any:
        return TestAgent(name=name, transform=transform)

    return factory


@pytest.fixture
def additive_agents(make_test_agent):
    """Set of additive agents for associativity testing."""
    return [
        make_test_agent("add_1", lambda x: x + 1),
        make_test_agent("add_2", lambda x: x + 2),
        make_test_agent("add_3", lambda x: x + 3),
    ]


@pytest.fixture
def multiplicative_agents(make_test_agent):
    """Set of multiplicative agents for associativity testing."""
    return [
        make_test_agent("mul_2", lambda x: x * 2),
        make_test_agent("mul_3", lambda x: x * 3),
        make_test_agent("mul_5", lambda x: x * 5),
    ]


# =============================================================================
# Law Verification Fixtures
# =============================================================================


@pytest.fixture
def law_verifier(id_agent, compose_fn):
    """
    Law verification helper.

    Provides methods to verify category laws with detailed reporting.
    """

    class LawVerifier:
        """Verify category laws for agents."""

        def __init__(self):
            self.id = id_agent
            self.compose = compose_fn

        async def check_left_identity(self, agent: Any, test_input: Any) -> dict:
            """Check Id >> f == f."""
            composed = self.compose(self.id, agent)
            composed_result = await composed.invoke(test_input)
            direct_result = await agent.invoke(test_input)

            return {
                "law": "left_identity",
                "holds": composed_result == direct_result,
                "composed_result": composed_result,
                "direct_result": direct_result,
                "input": test_input,
            }

        async def check_right_identity(self, agent: Any, test_input: Any) -> dict:
            """Check f >> Id == f."""
            composed = self.compose(agent, self.id)
            composed_result = await composed.invoke(test_input)
            direct_result = await agent.invoke(test_input)

            return {
                "law": "right_identity",
                "holds": composed_result == direct_result,
                "composed_result": composed_result,
                "direct_result": direct_result,
                "input": test_input,
            }

        async def check_associativity(
            self, f: Any, g: Any, h: Any, test_input: Any
        ) -> dict:
            """Check (f >> g) >> h == f >> (g >> h)."""
            left = self.compose(self.compose(f, g), h)
            right = self.compose(f, self.compose(g, h))

            left_result = await left.invoke(test_input)
            right_result = await right.invoke(test_input)

            return {
                "law": "associativity",
                "holds": left_result == right_result,
                "left_assoc_result": left_result,
                "right_assoc_result": right_result,
                "input": test_input,
            }

    return LawVerifier()
