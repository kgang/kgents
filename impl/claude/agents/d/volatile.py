"""
VolatileAgent: In-memory state storage with bounded history.

Fast, ephemeral state management for temporary context and caches.
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar, List
import copy

S = TypeVar("S")


@dataclass
class VolatileAgent(Generic[S]):
    """
    In-memory state storage.

    - Fastest performance (no I/O)
    - State lost on process termination
    - Useful for conversational context, temporary caches, test fixtures

    The VolatileAgent uses `copy.deepcopy` for isolation, ensuring that
    mutations to loaded state don't affect the stored state.

    History is bounded to prevent unbounded memory growth (entropy-aware).
    """

    _state: S
    _history: List[S] = field(default_factory=list)
    _max_history: int = 100

    async def load(self) -> S:
        """
        Load current state.

        Returns a deep copy to ensure isolation from internal state.
        """
        return copy.deepcopy(self._state)

    async def save(self, state: S) -> None:
        """
        Save new state.

        Archives the current state to history before updating.
        Maintains bounded history by dropping oldest entries.
        """
        # Archive current state to history
        self._history.append(copy.deepcopy(self._state))

        # Maintain bounded history (entropy-conscious)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Update to new state
        self._state = copy.deepcopy(state)

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Query state evolution over time.

        Returns history in reverse chronological order (newest first).
        Does NOT include current state.

        Args:
            limit: Maximum number of historical states to return
        """
        hist = self._history[::-1]  # Newest first
        if limit is not None:
            hist = hist[:limit]
        return [copy.deepcopy(s) for s in hist]

    def snapshot(self) -> S:
        """
        Non-async snapshot for testing/debugging.

        Returns current state without going through async load().
        """
        return copy.deepcopy(self._state)
