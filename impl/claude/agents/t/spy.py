"""
SpyAgent: Identity morphism with observation side effects.

An observer that:
- Passes data through unchanged (identity)
- Records all inputs to history (Writer Monad)
- Enables pipeline inspection and debugging

Now uses VolatileAgent (D-gent) for history storage,
demonstrating T-gent + D-gent integration.
"""

from __future__ import annotations

from typing import Generic, List, TypeVar

from bootstrap.types import Agent
from agents.d import VolatileAgent

A = TypeVar("A")


class SpyAgent(Agent[A, A], Generic[A]):
    """
    Identity agent with logging side effects.

    Morphism: A → A (with side effect: append to history)

    Category Theoretic Definition: The identity morphism with logging,
    representing the Writer Monad: S: A → (A, [A]).

    Properties:
    - Transparent: Data flows through unchanged
    - Observable: All inputs recorded to history via VolatileAgent
    - Composable: Can be inserted anywhere in pipeline
    - Testable: History can be inspected for assertions

    Now uses VolatileAgent internally for history storage,
    demonstrating D-gent integration with T-gents.

    Example:
        # Spy on intermediate pipeline data
        spy = SpyAgent[HypothesisOutput](label="Hypotheses")
        pipeline = GenerateHypotheses() >> spy >> RunExperiments()

        await pipeline.invoke(input_data)

        # Inspect what was passed
        history = await spy.get_history()
        print(history)  # [HypothesisOutput(...)]
        spy.assert_count(1)
    """

    def __init__(self, label: str = "Spy"):
        """
        Initialize spy agent with D-gent-backed history.

        Args:
            label: Human-readable label for this spy
        """
        self.label = label
        self._memory = VolatileAgent[List[A]](_state=[], _max_history=100)
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"Spy({self.label})"

    @property
    def history(self) -> List[A]:
        """
        Synchronous access to history (backward compatible).

        Note: This returns the current state synchronously.
        For full D-gent functionality, use get_history() async method.
        """
        # Access internal state directly for backward compatibility
        return self._memory._state

    async def invoke(self, input: A) -> A:
        """
        Record input and pass through unchanged.

        Args:
            input: Input of type A

        Returns:
            Same input (identity)
        """
        # Log the capture
        print(f"[{self.name}] Capturing: {input}")

        # Record to D-gent history
        current = await self._memory.load()
        current.append(input)
        await self._memory.save(current)

        # Return unchanged (identity)
        return input

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return len(self.history)

    async def get_history(self) -> List[A]:
        """
        Get full history via D-gent interface.

        Returns:
            List of captured values
        """
        return await self._memory.load()

    async def get_history_snapshots(self, limit: int = 10) -> List[List[A]]:
        """
        Get historical snapshots of spy state.

        Args:
            limit: Maximum number of snapshots

        Returns:
            List of historical states (newest first)
        """
        return await self._memory.history(limit=limit)

    def reset(self) -> None:
        """Clear history for test isolation."""
        self._memory._state.clear()

    def assert_captured(self, expected: A) -> None:
        """
        Assert that expected value was captured.

        Args:
            expected: Value that should be in history

        Raises:
            AssertionError: If expected not in history
        """
        assert expected in self.history, (
            f"Expected {expected} not captured in {self.name}. History: {self.history}"
        )

    def assert_count(self, count: int) -> None:
        """
        Assert exact invocation count.

        Args:
            count: Expected number of invocations

        Raises:
            AssertionError: If count doesn't match
        """
        actual = len(self.history)
        assert actual == count, (
            f"Expected {count} invocations in {self.name}, got {actual}"
        )

    def assert_not_empty(self) -> None:
        """
        Assert that spy captured at least one value.

        Raises:
            AssertionError: If history is empty
        """
        assert len(self.history) > 0, f"{self.name} captured nothing"

    def last(self) -> A:
        """
        Get the last captured value.

        Returns:
            Last value in history

        Raises:
            IndexError: If history is empty
        """
        if not self.history:
            raise IndexError(f"{self.name} has no captured values")
        return self.history[-1]


# Helper function for quick spy creation
def spy_agent(label: str = "Spy") -> SpyAgent[A]:
    """
    Create a SpyAgent with given label.

    Args:
        label: Human-readable label

    Returns:
        Configured SpyAgent
    """
    return SpyAgent(label=label)
