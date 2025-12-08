"""
PredicateAgent: Gate morphism for runtime validation.

A validator that:
- Passes data through if predicate holds
- Raises error if predicate fails
- Enables runtime type checking and invariant validation
"""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

from bootstrap.types import Agent

A = TypeVar("A")


class PredicateAgent(Agent[A, A], Generic[A]):
    """
    Gate agent that validates inputs via predicate.

    Morphism: A → A ∪ {⊥} (where ⊥ is error)

    Category Theoretic Definition: P: A → A ∪ {⊥} where output succeeds
    iff P(a) = True. Acts as a runtime type guard and validation gate.

    Properties:
    - Identity when predicate holds
    - Fails loudly when predicate fails
    - Composable validation in pipelines
    - No silent failures

    Example:
        # Runtime type validation
        def is_valid_hypothesis(h: HypothesisOutput) -> bool:
            return len(h.hypotheses) > 0

        validator = PredicateAgent(
            is_valid_hypothesis,
            name="NonEmptyHypotheses"
        )

        # Will raise if hypotheses list is empty
        pipeline = GenerateHypotheses() >> validator >> RunExperiments()
    """

    def __init__(
        self,
        predicate: Callable[[A], bool],
        name: str = "Predicate",
        error_message: str = ""
    ):
        """
        Initialize predicate agent.

        Args:
            predicate: Function that returns True if input is valid
            name: Human-readable name for this predicate
            error_message: Custom error message (optional)
        """
        self.predicate = predicate
        self.predicate_name = name
        self.error_message = error_message
        self._fail_count = 0
        self._pass_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"Gate({self.predicate_name})"

    async def invoke(self, input: A) -> A:
        """
        Pass through if predicate holds, else raise.

        Args:
            input: Input of type A

        Returns:
            Same input if predicate holds

        Raises:
            ValueError: If predicate fails
        """
        # Evaluate predicate
        try:
            holds = self.predicate(input)
        except Exception as e:
            self._fail_count += 1
            raise ValueError(
                f"Predicate '{self.predicate_name}' raised exception: {e}"
            ) from e

        # Check result
        if not holds:
            self._fail_count += 1
            if self.error_message:
                raise ValueError(self.error_message)
            raise ValueError(
                f"Predicate '{self.predicate_name}' failed for input: {input}"
            )

        # Predicate passed
        self._pass_count += 1
        return input

    @property
    def fail_count(self) -> int:
        """Number of times predicate failed."""
        return self._fail_count

    @property
    def pass_count(self) -> int:
        """Number of times predicate passed."""
        return self._pass_count

    @property
    def total_count(self) -> int:
        """Total number of invocations."""
        return self._fail_count + self._pass_count

    def reset(self) -> None:
        """Reset counters."""
        self._fail_count = 0
        self._pass_count = 0


# Helper function for quick predicate creation
def predicate_agent(
    predicate: Callable[[A], bool],
    name: str = "Predicate",
    error_message: str = ""
) -> PredicateAgent[A]:
    """
    Create a PredicateAgent with given predicate.

    Args:
        predicate: Function that returns True if input is valid
        name: Human-readable name
        error_message: Custom error message

    Returns:
        Configured PredicateAgent
    """
    return PredicateAgent(predicate=predicate, name=name, error_message=error_message)


# Common predicates for convenience

def not_none(x: A | None) -> bool:
    """Predicate: value is not None."""
    return x is not None


def not_empty(x: str | list | dict) -> bool:
    """Predicate: value is not empty."""
    return len(x) > 0


def is_positive(x: int | float) -> bool:
    """Predicate: number is positive."""
    return x > 0


def is_non_negative(x: int | float) -> bool:
    """Predicate: number is non-negative."""
    return x >= 0
