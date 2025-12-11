"""FlakyAgent - Probabilistic failure wrapper.

Category Theory: F_p: A → B ∪ {⊥}
The morphism that fails with probability p, otherwise delegates to wrapped agent.

Type II Saboteur - Chaos Engineering for reliability testing.
"""

import random
from typing import Generic, Optional, Protocol, TypeVar

In = TypeVar("In")
Out = TypeVar("Out")


I_contra = TypeVar("I_contra", contravariant=True)
O_co = TypeVar("O_co", covariant=True)


class Agent(Protocol[I_contra, O_co]):
    """Protocol for agents that can be wrapped."""

    name: str

    async def invoke(self, input_data: I_contra) -> O_co:
        """Process input and return output."""
        ...


class FlakyAgent(Generic[In, Out]):
    """Probabilistic chaos wrapper F_p.

    Category Theory:
    - Morphism: F_p: A → B ∪ {⊥}
    - Properties: Probabilistic lifting of wrapped morphism
    - Purpose: Test retry logic and error handling

    Algebraic Laws:
    - F_0 = wrapped (no failures)
    - F_1 = ⊥ (always fails)
    - P(F_p succeeds) = 1 - p
    - F_p ∘ F_q has failure probability p + q - pq

    Example:
        >>> agent = SomeAgent()
        >>> flaky = FlakyAgent(agent, probability=0.3, seed=42)
        >>> # Fails ~30% of the time
        >>> try:
        >>>     result = await flaky.invoke(input_data)
        >>> except RuntimeError:
        >>>     # Handle flaky failure
        >>>     pass
    """

    def __init__(
        self,
        wrapped: Agent[In, Out],
        probability: float = 0.1,
        seed: Optional[int] = None,
    ):
        """Initialize FlakyAgent.

        Args:
            wrapped: Agent to wrap
            probability: Failure probability (0.0-1.0)
            seed: Random seed for reproducibility
        """
        self.name = f"Flaky({wrapped.name}, p={probability})"
        self.wrapped = wrapped
        self.probability = probability
        self.rng = random.Random(seed)
        self.__is_test__ = True

    async def invoke(self, input_data: In) -> Out:
        """Randomly fail or delegate to wrapped agent.

        Category Theory: F_p: A → B ∪ {⊥}

        Args:
            input_data: Input to process

        Returns:
            Output from wrapped agent (if not failed)

        Raises:
            RuntimeError: With probability p
        """
        if self.rng.random() < self.probability:
            raise RuntimeError(f"Flaky failure (p={self.probability})")

        return await self.wrapped.invoke(input_data)
