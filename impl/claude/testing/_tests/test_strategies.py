"""
Tests for property-based testing strategies.

Philosophy: Spec is compression; strategies generate from that compression.

This demonstrates Phase 3 of the test evolution plan.
Tests here verify the strategies themselves work correctly.
"""

from __future__ import annotations

from typing import Any

import pytest

# Skip all tests if hypothesis not available
pytest.importorskip("hypothesis")


from hypothesis import given, settings
from testing.strategies import (
    agent_chains,
    invalid_dna,
    simple_agents,
    type_names,
    valid_dna,
)


class TestAgentStrategies:
    """Tests for agent generation strategies."""

    @pytest.mark.property
    @given(agent=simple_agents())  # type: ignore[untyped-decorator]
    @settings(max_examples=20)  # type: ignore[untyped-decorator]
    def test_generated_agent_has_name(self, agent: Any) -> None:
        """Generated agents should have a name attribute."""
        assert hasattr(agent, "name")
        assert agent.name.startswith("Agent_")

    @pytest.mark.property
    @given(agent=simple_agents())  # type: ignore[untyped-decorator]
    @settings(max_examples=20)  # type: ignore[untyped-decorator]
    @pytest.mark.asyncio
    async def test_generated_agent_is_invokable(self, agent: Any) -> None:
        """Generated agents should have invoke method."""
        assert hasattr(agent, "invoke")
        result = await agent.invoke(0)
        assert isinstance(result, int)

    @pytest.mark.property
    @given(agents=agent_chains(min_length=2, max_length=5))  # type: ignore[untyped-decorator]
    @settings(max_examples=10)  # type: ignore[untyped-decorator]
    def test_agent_chains_length(self, agents: Any) -> None:
        """Agent chains should have correct length."""
        assert 2 <= len(agents) <= 5

    @pytest.mark.property
    @given(agents=agent_chains(min_length=2, max_length=5))  # type: ignore[untyped-decorator]
    @settings(max_examples=10)  # type: ignore[untyped-decorator]
    @pytest.mark.asyncio
    async def test_agent_chains_composable(self, agents: Any) -> None:
        """Agent chains should be composable."""
        from functools import reduce

        from bootstrap import compose

        composed = reduce(compose, agents)
        assert hasattr(composed, "invoke")

        result = await composed.invoke(0)
        assert isinstance(result, int)


class TestDNAStrategies:
    """Tests for DNA generation strategies."""

    @pytest.mark.property
    @given(dna=valid_dna())  # type: ignore[untyped-decorator]
    @settings(max_examples=30)  # type: ignore[untyped-decorator]
    def test_valid_dna_passes_constraints(self, dna: Any) -> None:
        """Valid DNA should pass all constraints."""
        assert 0 < dna.exploration_budget <= 0.5

    @pytest.mark.property
    @given(dna=invalid_dna())  # type: ignore[untyped-decorator]
    @settings(max_examples=30)  # type: ignore[untyped-decorator]
    def test_invalid_dna_fails_constraints(self, dna: Any) -> None:
        """Invalid DNA should violate constraints."""
        # Either too low or too high
        assert dna.exploration_budget <= 0 or dna.exploration_budget > 0.5


class TestTypeStrategies:
    """Tests for type name generation strategies."""

    @pytest.mark.property
    @given(type_name=type_names())  # type: ignore[untyped-decorator]
    @settings(max_examples=50)  # type: ignore[untyped-decorator]
    def test_type_names_are_strings(self, type_name: Any) -> None:
        """Generated type names should be strings."""
        assert isinstance(type_name, str)
        assert len(type_name) > 0

    @pytest.mark.property
    @given(type_name=type_names())  # type: ignore[untyped-decorator]
    @settings(max_examples=50)  # type: ignore[untyped-decorator]
    def test_type_names_valid_format(self, type_name: Any) -> None:
        """Generated type names should have valid format."""
        # Either a base type or Generic[Base]
        base_types = ["int", "str", "float", "bool", "None", "Any"]
        generic_pattern = any(
            type_name.startswith(g) and "[" in type_name
            for g in ["List", "Dict", "Optional", "Tuple"]
        )

        assert type_name in base_types or generic_pattern, f"Invalid type: {type_name}"
