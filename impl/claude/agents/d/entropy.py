"""
EntropyConstrainedAgent: D-gent wrapper with entropy budget enforcement.

Enforces state size limits based on J-gent entropy budgets,
ensuring that state growth doesn't violate computational constraints.
"""

import sys
from typing import TypeVar, Generic, List

from .protocol import DataAgent
from .errors import StorageError

S = TypeVar("S")


class EntropyConstrainedAgent(Generic[S]):
    """
    D-gent wrapper that enforces entropy budget constraints.

    Wraps any DataAgent and enforces maximum state size,
    preventing unbounded state growth in recursive/iterative contexts.

    Entropy budget formula (from J-gents):
        budget = initial_budget * (decay_factor ** depth)

    Example:
        >>> from agents.d import VolatileAgent, EntropyConstrainedAgent
        >>>
        >>> # At depth 2 in promise tree, budget is 0.5 * (0.5 ** 2) = 0.125
        >>> dgent = EntropyConstrainedAgent(
        ...     backend=VolatileAgent(initial_state),
        ...     budget=0.125,
        ...     max_size_bytes=125_000  # 12.5% of 1MB base
        ... )
        >>>
        >>> # This will fail if state exceeds budget
        >>> await dgent.save(large_state)  # Raises StorageError if too large
    """

    def __init__(
        self,
        backend: DataAgent[S],
        budget: float,
        max_size_bytes: int,
        enforce_on_save: bool = True,
    ):
        """
        Initialize entropy-constrained D-gent.

        Args:
            backend: Underlying D-gent for actual storage
            budget: Entropy budget (0.0-1.0)
            max_size_bytes: Maximum state size in bytes
            enforce_on_save: Raise error on budget violation (vs warn)
        """
        self.backend = backend
        self.budget = budget
        self.max_size_bytes = max_size_bytes
        self.enforce_on_save = enforce_on_save

    async def load(self) -> S:
        """Load state from backend (no constraint check)."""
        return await self.backend.load()

    async def save(self, state: S) -> None:
        """
        Save state with entropy budget enforcement.

        Args:
            state: State to save

        Raises:
            StorageError: If state exceeds budget and enforce_on_save=True
        """
        # Estimate state size
        size = self._estimate_size(state)

        # Check budget
        if size > self.max_size_bytes:
            msg = (
                f"State size {size} bytes exceeds entropy budget "
                f"{self.budget:.2%} (max {self.max_size_bytes} bytes)"
            )

            if self.enforce_on_save:
                raise StorageError(msg)
            else:
                # Warn but allow
                import logging

                logging.warning(msg)

        # Delegate to backend
        await self.backend.save(state)

    async def history(self, limit: int | None = None) -> List[S]:
        """Get state history from backend."""
        return await self.backend.history(limit)

    def _estimate_size(self, state: S) -> int:
        """
        Estimate state size in bytes.

        Uses sys.getsizeof as rough approximation.
        More accurate sizing could use pickle or json dumps.
        """
        return sys.getsizeof(state)

    @classmethod
    def from_depth(
        cls,
        backend: DataAgent[S],
        depth: int,
        initial_budget: float = 0.5,
        decay_factor: float = 0.5,
        base_size_bytes: int = 1_000_000,
    ) -> "EntropyConstrainedAgent[S]":
        """
        Create entropy-constrained D-gent from J-gent depth.

        Args:
            backend: Underlying D-gent
            depth: Depth in promise tree
            initial_budget: Initial entropy budget
            decay_factor: Budget decay per depth level
            base_size_bytes: Base maximum size (1MB default)

        Returns:
            Configured EntropyConstrainedAgent
        """
        budget = initial_budget * (decay_factor**depth)
        max_size = int(base_size_bytes * budget)

        return cls(
            backend=backend,
            budget=budget,
            max_size_bytes=max_size,
        )


# Convenience function


def entropy_constrained(
    backend: DataAgent[S],
    budget: float,
    max_size_bytes: int,
) -> EntropyConstrainedAgent[S]:
    """
    Create entropy-constrained D-gent wrapper.

    Args:
        backend: Underlying D-gent
        budget: Entropy budget (0.0-1.0)
        max_size_bytes: Maximum state size in bytes

    Returns:
        EntropyConstrainedAgent wrapping backend
    """
    return EntropyConstrainedAgent(
        backend=backend,
        budget=budget,
        max_size_bytes=max_size_bytes,
    )
