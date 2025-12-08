"""LatencyAgent - Identity morphism with temporal cost.

Category Theory: L_Δ: (A, t) → (A, t + Δ)
The morphism that adds temporal delay while preserving data.

Type II Saboteur - Chaos Engineering for performance testing.
"""

from __future__ import annotations
from typing import Generic, TypeVar, Optional, TYPE_CHECKING
import asyncio
import random

if TYPE_CHECKING:
    from bootstrap.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")


class LatencyAgent(Generic[A]):
    """Identity morphism with temporal cost L_Δ.

    Category Theory:
    - Morphism: L_Δ: (A, t) → (A, t + Δ)
    - Properties: Identity on data, adds time dimension
    - Purpose: Test performance under latency

    Algebraic Laws:
    - L_0 = id (zero latency is identity)
    - L_a ∘ L_b = L_{a+b} (latency composes additively)
    - data(L_Δ(a)) = a (data unchanged)
    - time(L_Δ(a)) = time(a) + Δ (time increased)

    Example:
        >>> latency = LatencyAgent(delay=0.1, variance=0.02, seed=42)
        >>> start = time.time()
        >>> result = await latency.invoke("test")
        >>> elapsed = time.time() - start
        >>> assert 0.08 <= elapsed <= 0.12  # 0.1 ± 0.02
        >>> assert result == "test"  # Data unchanged
    """

    def __init__(
        self,
        delay: float,
        variance: float = 0.0,
        seed: Optional[int] = None,
    ):
        """Initialize LatencyAgent.

        Args:
            delay: Base delay in seconds
            variance: Random variance (±variance) in seconds
            seed: Random seed for reproducibility
        """
        self.name = f"Latency(Δ={delay}s)"
        self.delay = delay
        self.variance = variance
        self.rng = random.Random(seed)
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Add latency, then return input unchanged.

        Category Theory: L_Δ: (A, t) → (A, t + Δ)

        Args:
            input_data: Input to pass through

        Returns:
            Input unchanged (after delay)
        """
        actual_delay = self.delay

        if self.variance > 0:
            actual_delay += self.rng.uniform(-self.variance, self.variance)

        # Never negative delay
        actual_delay = max(0, actual_delay)

        await asyncio.sleep(actual_delay)
        return input_data

    def __rshift__(self, other: Agent[A, B]) -> ComposedAgent[A, A, B]:
        """Composition operator: self >> other.

        Args:
            other: Agent to compose with

        Returns:
            Composed agent
        """
        from bootstrap.types import ComposedAgent

        return ComposedAgent(self, other)
