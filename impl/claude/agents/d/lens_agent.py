"""
LensAgent: D-gent with focused state view.

Wraps a parent D-gent and projects state through a lens,
providing scoped access to sub-state.
"""

from dataclasses import dataclass
from typing import Generic, List, TypeVar

from .lens import Lens
from .protocol import DataAgent

S = TypeVar("S")  # Parent state
A = TypeVar("A")  # Sub-state (focus)
B = TypeVar("B")  # Deeper sub-state


@dataclass
class LensAgent(Generic[S, A]):
    """
    A D-gent that provides a focused view into parent state.

    Reads and writes are projected through the lens:
    - load(): Load parent state, extract sub-state via lens.get
    - save(): Update sub-state within parent via lens.set
    - history(): Project historical states through lens

    This enables:
    - **Least privilege**: Agent sees only needed state
    - **Type safety**: Sub-state type checked
    - **Coordination**: Multiple agents share parent, different lenses
    - **Testability**: Test with isolated sub-state

    Example:
        >>> from agents.d import VolatileAgent
        >>> from agents.d.lens import key_lens
        >>>
        >>> # Global state
        >>> global_dgent = VolatileAgent(_state={"users": {}, "products": {}})
        >>>
        >>> # Focused D-gent for users only
        >>> user_dgent = LensAgent(
        ...     parent=global_dgent,
        ...     lens=key_lens("users")
        ... )
        >>>
        >>> # Agent sees only "users" sub-state
        >>> await user_dgent.save({"alice": {"age": 30}})
        >>> users = await user_dgent.load()
        >>> users
        {'alice': {'age': 30}}
    """

    parent: DataAgent[S]
    lens: Lens[S, A]

    async def load(self) -> A:
        """
        Load parent state, project to sub-state.

        Returns:
            Sub-state extracted via lens.get

        Raises:
            StateNotFoundError: If parent state doesn't exist
            StateCorruptionError: If parent state is corrupt
        """
        full_state = await self.parent.load()
        return self.lens.get(full_state)

    async def save(self, sub_state: A) -> None:
        """
        Update sub-state within parent state.

        Performs:
        1. Load parent state
        2. Apply lens.set(parent, sub_state)
        3. Save updated parent

        Args:
            sub_state: New value for sub-state

        Raises:
            StateNotFoundError: If parent state doesn't exist
            StateSerializationError: If state can't be encoded
            StorageError: If backend write fails
        """
        full_state = await self.parent.load()
        new_full_state = self.lens.set(full_state, sub_state)
        await self.parent.save(new_full_state)

    async def history(self, limit: int | None = None) -> List[A]:
        """
        Project historical states through lens.

        Args:
            limit: Max entries to return

        Returns:
            List of historical sub-states (newest first)
        """
        full_history = await self.parent.history(limit)
        return [self.lens.get(s) for s in full_history]

    def __rshift__(self, other: Lens[A, B]) -> LensAgent[S, B]:
        """
        Compose lenses for deeper focusing: self >> other.

        Enables lens composition to focus on nested state:
        - self: Focus on sub-state A within S
        - other: Focus on deeper sub-state B within A
        - Result: Focus on B within S (composition)

        Type: LensAgent[S, A] >> Lens[A, B] → LensAgent[S, B]

        Example:
            >>> from agents.d import VolatileAgent
            >>> from agents.d.lens import key_lens
            >>>
            >>> # Nested state: user → address → zip
            >>> state = {"user": {"address": {"zip": "12345"}}}
            >>> dgent = VolatileAgent(_state=state)
            >>>
            >>> # Compose lenses
            >>> user_lens = key_lens("user")
            >>> address_lens = key_lens("address")
            >>> zip_lens = key_lens("zip")
            >>>
            >>> # Deep focus via composition
            >>> zip_dgent = (
            ...     LensAgent(dgent, user_lens) >>
            ...     address_lens >>
            ...     zip_lens
            ... )
            >>>
            >>> await zip_dgent.load()  # "12345"
        """
        from .lens import Lens

        # Compose lenses: self.lens >> other
        composed_lens: Lens[S, B] = Lens(
            get=lambda s: other.get(self.lens.get(s)),
            set=lambda s, b: self.lens.set(s, other.set(self.lens.get(s), b)),
        )

        return LensAgent(parent=self.parent, lens=composed_lens)


# === Convenience Functions ===


def focused(parent: DataAgent[S], lens: Lens[S, A]) -> LensAgent[S, A]:
    """
    Create a LensAgent (convenience function).

    Args:
        parent: Parent D-gent with full state
        lens: Lens to focus on sub-state

    Returns:
        LensAgent providing focused view

    Example:
        >>> from agents.d import VolatileAgent
        >>> from agents.d.lens import key_lens
        >>> dgent = VolatileAgent(_state={"a": 1, "b": 2})
        >>> focused_dgent = focused(dgent, key_lens("a"))
        >>> await focused_dgent.load()
        1
    """
    return LensAgent(parent=parent, lens=lens)
