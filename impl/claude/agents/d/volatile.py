"""
VolatileAgent: In-memory state storage with bounded history.

Fast, ephemeral state management for temporary context and caches.
"""

import copy
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Generic, List, TypeVar

if TYPE_CHECKING:
    from .lens import Lens
    from .lens_agent import LensAgent
    from .transform_agent import TransformAgent

S = TypeVar("S")
A = TypeVar("A")  # Sub-state (for lens composition)


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
    Uses deque with maxlen for O(1) history management.
    """

    _state: S
    _history: deque = field(default_factory=lambda: deque(maxlen=100))
    _max_history: int = 100

    def __post_init__(self):
        """Initialize history deque with correct maxlen."""
        if not isinstance(self._history, deque):
            # Convert list to deque if passed as list
            self._history = deque(self._history, maxlen=self._max_history)
        elif self._history.maxlen != self._max_history:
            # Update maxlen if different
            self._history = deque(self._history, maxlen=self._max_history)

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
        Maintains bounded history automatically via deque maxlen (O(1)).
        """
        # Archive current state to history
        # deque with maxlen automatically evicts oldest entry when full
        self._history.append(copy.deepcopy(self._state))

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
        # Convert deque to list for slicing, then reverse (newest first)
        hist = list(reversed(self._history))
        if limit is not None:
            hist = hist[:limit]
        return [copy.deepcopy(s) for s in hist]

    def snapshot(self) -> S:
        """
        Non-async snapshot for testing/debugging.

        Returns current state without going through async load().
        """
        return copy.deepcopy(self._state)

    def __rshift__(self, other: "Lens[S, A]") -> "LensAgent[S, A]":
        """
        Compose with a lens to create focused view: dgent >> lens.

        Creates a LensAgent that provides scoped access to sub-state.

        Type: VolatileAgent[S] >> Lens[S, A] → LensAgent[S, A]

        Example:
            >>> from agents.d.lens import key_lens
            >>>
            >>> # Global state
            >>> dgent = VolatileAgent(_state={"users": {}, "products": {}})
            >>>
            >>> # Focus on users via composition
            >>> user_dgent = dgent >> key_lens("users")
            >>>
            >>> # Focused agent sees only "users"
            >>> await user_dgent.save({"alice": {"age": 30}})
            >>> await user_dgent.load()
            {'alice': {'age': 30}}
        """
        from .lens_agent import LensAgent

        return LensAgent(parent=self, lens=other)

    def __or__(self, transform: "Callable[[S], S]") -> "TransformAgent[S]":
        """
        Compose with a transformation function: dgent | transform.

        Creates an agent that applies a transformation on save/load.

        Type: VolatileAgent[S] | (S → S) → TransformAgent[S]

        Example:
            >>> # Normalize state on access
            >>> dgent = VolatileAgent(_state={"count": 5})
            >>> normalized = dgent | (lambda s: {**s, "count": max(0, s["count"])})
            >>>
            >>> await normalized.save({"count": -10})
            >>> await normalized.load()
            {'count': 0}  # Transformed to minimum 0
        """
        from .transform_agent import TransformAgent

        return TransformAgent(parent=self, transform=transform)
