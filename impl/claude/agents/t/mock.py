"""
MockAgent: Configurable mock agent for testing.

Returns pre-configured outputs, useful for:
- Testing agent composition without LLM calls
- Validating pipeline behavior
- Fast iteration during development
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from agents.poly.types import Agent

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class MockConfig:
    """Configuration for MockAgent."""

    output: Any = None  # Output to return
    delay_ms: int = 0  # Simulated delay in milliseconds


class MockAgent(Agent[A, B], Generic[A, B]):
    """
    Agent that returns pre-configured mock output.

    Morphism: A → B (where B is pre-configured)

    Category Theoretic Definition: The constant morphism c_b: A → B where
    ∀ a ∈ A: c_b(a) = b for fixed b ∈ B.

    Example:
        # Mock hypothesis generator
        mock_hyp = MockAgent[HypothesisInput, HypothesisOutput](
            MockConfig(output=HypothesisOutput(hypotheses=["Test hypothesis"]))
        )

        result = await mock_hyp.invoke(any_input)
        # Returns: HypothesisOutput(hypotheses=["Test hypothesis"])
    """

    def __init__(self, config: MockConfig):
        """Initialize mock agent with configuration."""
        self.config = config
        self._call_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return "MockAgent"

    async def invoke(self, input: A) -> B:
        """
        Return pre-configured mock output.

        Args:
            input: Input of type A (ignored)

        Returns:
            Pre-configured output of type B
        """
        self._call_count += 1

        if self.config.delay_ms > 0:
            import asyncio

            await asyncio.sleep(self.config.delay_ms / 1000.0)

        return self.config.output  # type: ignore

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return self._call_count

    def reset(self) -> None:
        """Reset call counter."""
        self._call_count = 0


# Singleton for basic mocking
mock_agent = MockAgent[Any, Any](MockConfig(output={"status": "mocked"}))
