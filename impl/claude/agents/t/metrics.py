"""MetricsAgent - Identity morphism with performance profiling.

Category Theory: M: A → A (with side effect: record timing)
The identity morphism that tracks performance metrics.

Type III Observer - Inspection with timing data.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from bootstrap.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent."""

    invocation_count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0

    @property
    def avg_time(self) -> float:
        """Average time per invocation.

        Returns:
            Average time in seconds (0.0 if no invocations)
        """
        return (
            self.total_time / self.invocation_count
            if self.invocation_count > 0
            else 0.0
        )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"PerformanceMetrics(count={self.invocation_count}, "
            f"avg={self.avg_time:.4f}s, "
            f"min={self.min_time:.4f}s, "
            f"max={self.max_time:.4f}s)"
        )


class MetricsAgent(Generic[A]):
    """Identity morphism with performance metrics M.

    Category Theory:
    - Morphism: M: A → A
    - Properties: Identity with timing side effects
    - Purpose: Profile agent performance and identify bottlenecks

    Algebraic Laws:
    - M(a) = a (identity on data)
    - time(M(a)) ≈ time(id(a)) (negligible overhead)
    - metrics are monotonic (always increase)

    Example:
        >>> metrics = MetricsAgent(label="LLM Calls")
        >>> for i in range(10):
        >>>     await metrics.invoke(request)
        >>> print(f"Avg latency: {metrics.metrics.avg_time:.3f}s")
        >>> print(f"Max latency: {metrics.metrics.max_time:.3f}s")
    """

    def __init__(self, label: str):
        """Initialize MetricsAgent.

        Args:
            label: Human-readable label for this profiler
        """
        self.name = f"Metrics({label})"
        self.label = label
        self.metrics = PerformanceMetrics()
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Record timing and pass through.

        Category Theory: M: A → A (with timing)

        Args:
            input_data: Input to pass through

        Returns:
            Input unchanged
        """
        start = time.time()
        result = input_data  # Identity morphism
        elapsed = time.time() - start

        self.metrics.invocation_count += 1
        self.metrics.total_time += elapsed
        self.metrics.min_time = min(self.metrics.min_time, elapsed)
        self.metrics.max_time = max(self.metrics.max_time, elapsed)

        return result

    def reset(self) -> None:
        """Reset metrics to initial state.

        Useful for test isolation.
        """
        self.metrics = PerformanceMetrics()

    def print_summary(self) -> None:
        """Print performance summary to console."""
        print(f"\n[{self.name}] Performance Summary:")
        print(f"  Invocations: {self.metrics.invocation_count}")
        print(f"  Total time:  {self.metrics.total_time:.4f}s")
        print(f"  Avg time:    {self.metrics.avg_time:.4f}s")
        print(f"  Min time:    {self.metrics.min_time:.4f}s")
        print(f"  Max time:    {self.metrics.max_time:.4f}s")

    def __rshift__(self, other: Agent[A, B]) -> ComposedAgent[A, A, B]:
        """Composition operator: self >> other.

        Args:
            other: Agent to compose with

        Returns:
            Composed agent
        """
        from bootstrap.types import ComposedAgent

        return ComposedAgent(self, other)
