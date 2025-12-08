"""CounterAgent - Identity morphism with invocation counting.

Category Theory: C: A → A (with side effect: count++)
The identity morphism that tracks invocation count.

Type III Observer - Inspection without modification.
"""

from __future__ import annotations
from typing import Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from bootstrap.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")


class CounterAgent(Generic[A]):
    """Identity morphism with invocation counting C.

    Category Theory:
    - Morphism: C: A → A
    - Properties: Identity with counting side effect
    - Purpose: Track agent usage and test invocation patterns

    Algebraic Laws:
    - C(a) = a (identity on data)
    - count(C ∘ C) = 2 (counts accumulate)
    - C is idempotent on data but not on count

    Example:
        >>> counter = CounterAgent(label="API Calls")
        >>> await counter.invoke("request 1")
        >>> await counter.invoke("request 2")
        >>> counter.assert_count(2)
        >>> print(f"API called {counter.count} times")
    """

    def __init__(self, label: str):
        """Initialize CounterAgent.

        Args:
            label: Human-readable label for this counter
        """
        self.name = f"Counter({label})"
        self.label = label
        self.count = 0
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Increment counter and pass through.

        Category Theory: C: A → A (count++)

        Args:
            input_data: Input to pass through

        Returns:
            Input unchanged
        """
        self.count += 1
        return input_data

    def reset(self) -> None:
        """Reset counter to zero.

        Useful for test isolation.
        """
        self.count = 0

    def assert_count(self, expected: int) -> None:
        """Assert exact invocation count.

        Args:
            expected: Expected count

        Raises:
            AssertionError: If count doesn't match expected
        """
        assert (
            self.count == expected
        ), f"Expected {expected} invocations, got {self.count}"

    def __rshift__(self, other: Agent[A, B]) -> ComposedAgent[A, A, B]:
        """Composition operator: self >> other.

        Args:
            other: Agent to compose with

        Returns:
            Composed agent
        """
        from bootstrap.types import ComposedAgent

        return ComposedAgent(self, other)
