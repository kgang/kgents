"""
FixtureAgent: Deterministic lookup agent for regression testing.

Returns pre-defined outputs based on input lookup, ensuring:
- Regression testing (known input/output pairs)
- Deterministic behavior
- Fast execution (O(1) lookup)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Optional, TypeVar

from agents.poly.types import Agent

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class FixtureConfig(Generic[A, B]):
    """Configuration for FixtureAgent."""

    fixtures: Dict[A, B]  # Input → Output mapping
    default: Optional[B] = None  # Fallback if input not in fixtures
    strict: bool = True  # Raise error on missing input if True


class FixtureAgent(Agent[A, B], Generic[A, B]):
    """
    Agent that returns outputs via deterministic lookup.

    Morphism: A → B (via fixture table)

    Category Theoretic Definition: A morphism f: A → B defined by a
    lookup table (hash map). For regression testing and deterministic
    behavior validation.

    Example:
        # Regression test fixtures
        fixtures = {
            "Fix auth bug": "Added OAuth validation",
            "Optimize query": "Added database index",
        }
        fixture_agent = FixtureAgent[str, str](
            FixtureConfig(fixtures=fixtures)
        )

        result = await fixture_agent.invoke("Fix auth bug")
        # Returns: "Added OAuth validation"
    """

    def __init__(self, config: FixtureConfig[A, B]):
        """Initialize fixture agent with configuration."""
        self.config = config
        self._lookup_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"FixtureAgent({len(self.config.fixtures)} fixtures)"

    async def invoke(self, input: A) -> B:
        """
        Lookup input in fixture table.

        Args:
            input: Input of type A

        Returns:
            Corresponding output of type B from fixtures

        Raises:
            KeyError: If input not in fixtures and strict=True
        """
        self._lookup_count += 1

        # Try fixture lookup
        if input in self.config.fixtures:
            return self.config.fixtures[input]

        # Try default
        if self.config.default is not None:
            return self.config.default

        # Strict mode - raise error
        if self.config.strict:
            raise KeyError(f"No fixture for input: {input}")

        # This should be unreachable (strict=True and no default)
        raise RuntimeError("FixtureAgent: No default and strict=True")

    @property
    def lookup_count(self) -> int:
        """Number of times invoke was called."""
        return self._lookup_count

    def reset(self) -> None:
        """Reset lookup counter."""
        self._lookup_count = 0


# Helper function for quick fixture creation
def fixture_agent(
    fixtures: Dict[A, B], default: Optional[B] = None, strict: bool = True
) -> FixtureAgent[A, B]:
    """
    Create a FixtureAgent with given fixtures.

    Args:
        fixtures: Input → Output mapping
        default: Optional default value for missing inputs
        strict: Whether to raise error on missing input

    Returns:
        Configured FixtureAgent
    """
    return FixtureAgent(
        FixtureConfig(fixtures=fixtures, default=default, strict=strict)
    )
