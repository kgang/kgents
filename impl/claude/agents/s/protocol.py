"""
StateBackend: The principled protocol for state persistence.

This module defines the minimal interface for state threading in S-gent.

Category-theoretic insight:
    State threading requires exactly two operations:
    - load: Unit → S (introduce state into computation)
    - save: S → Unit (persist state, exit computation)

This is the comonad structure for state:
    - load is the counit (extract)
    - save is the dual (embed)

Laws:
    1. load-save identity: save(await load()) is idempotent
    2. save-load roundtrip: await load() after save(s) returns s
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

S = TypeVar("S")  # State type
S_co = TypeVar("S_co", covariant=True)  # Covariant state for protocol


@runtime_checkable
class StateBackend(Protocol[S_co]):
    """
    Minimal interface for state persistence.

    This is the algebra for state threading. Any type that implements
    load() and save() can be used as a StateBackend.

    Category-theoretic:
        StateBackend[S] is an object in the category of state stores.
        load() and save() are the fundamental morphisms.

    Laws (must hold for all implementations):
        1. load-save identity:
           s = await backend.load()
           await backend.save(s)
           # State unchanged (idempotent)

        2. save-load roundtrip:
           await backend.save(s)
           s2 = await backend.load()
           assert s == s2  # Roundtrip preserves value

    Examples:
        # In-memory backend
        class MemoryBackend(StateBackend[S]):
            def __init__(self, initial: S):
                self._state = initial

            async def load(self) -> S:
                return copy.deepcopy(self._state)

            async def save(self, state: S) -> None:
                self._state = copy.deepcopy(state)

        # Usage
        backend = MemoryBackend({"count": 0})
        state = await backend.load()  # {"count": 0}
        state["count"] += 1
        await backend.save(state)
        assert await backend.load() == {"count": 1}
    """

    async def load(self) -> S_co:
        """
        Load current state.

        Returns:
            The current state value.

        Note:
            Implementations should return a copy to prevent
            accidental mutation of internal state.
        """
        ...

    async def save(self, state: S_co) -> None:
        """
        Persist new state.

        Args:
            state: The new state to persist.

        Note:
            Implementations should store a copy to prevent
            external mutation from affecting stored state.
        """
        ...


# Type alias for state logic functions
StateLogic = Generic[S]
"""Type for pure state logic: (Input, State) → (Output, NewState)"""


__all__ = [
    "StateBackend",
]
