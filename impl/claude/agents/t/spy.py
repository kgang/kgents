"""
SpyAgent: Identity morphism with observation side effects.

An observer that:
- Passes data through unchanged (identity)
- Records all inputs to history (Writer Monad)
- Enables pipeline inspection and debugging

Simplified implementation using plain Python list for history.
"""

from __future__ import annotations

from typing import Generic, List, TypeVar

from agents.poly.types import Agent

A = TypeVar("A")


class SpyAgent(Agent[A, A], Generic[A]):
    """
    Identity agent with logging side effects.

    Morphism: A → A (with side effect: append to history)

    Category Theoretic Definition: The identity morphism with logging,
    representing the Writer Monad: S: A → (A, [A]).

    Properties:
    - Transparent: Data flows through unchanged
    - Observable: All inputs recorded to in-memory history
    - Composable: Can be inserted anywhere in pipeline
    - Testable: History can be inspected for assertions

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

    def __init__(self, label: str = "Spy", max_history: int = 100):
        """
        Initialize spy agent with in-memory history.

        Args:
            label: Human-readable label for this spy
            max_history: Maximum history entries to keep
        """
        self.label = label
        self._history: List[A] = []
        self._max_history = max_history
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"Spy({self.label})"

    @property
    def history(self) -> List[A]:
        """
        Synchronous access to history.

        Returns:
            List of all captured values
        """
        return self._history

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

        # Record to history
        self._history.append(input)

        # Trim if exceeds max
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        # Return unchanged (identity)
        return input

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return len(self._history)

    async def get_history(self) -> List[A]:
        """
        Get full history (async interface for compatibility).

        Returns:
            List of captured values
        """
        return self._history

    def reset(self) -> None:
        """Clear history for test isolation."""
        self._history.clear()

    def assert_captured(self, expected: A) -> None:
        """
        Assert that expected value was captured.

        Args:
            expected: Value that should be in history

        Raises:
            AssertionError: If expected not in history
        """
        assert expected in self._history, (
            f"Expected {expected} not captured in {self.name}. History: {self._history}"
        )

    def assert_count(self, count: int) -> None:
        """
        Assert exact invocation count.

        Args:
            count: Expected number of invocations

        Raises:
            AssertionError: If count doesn't match
        """
        actual = len(self._history)
        assert actual == count, (
            f"Expected {count} invocations in {self.name}, got {actual}"
        )

    def assert_not_empty(self) -> None:
        """
        Assert that spy captured at least one value.

        Raises:
            AssertionError: If history is empty
        """
        assert len(self._history) > 0, f"{self.name} captured nothing"

    def last(self) -> A:
        """
        Get the last captured value.

        Returns:
            Last value in history

        Raises:
            IndexError: If history is empty
        """
        if not self._history:
            raise IndexError(f"{self.name} has no captured values")
        return self._history[-1]


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
