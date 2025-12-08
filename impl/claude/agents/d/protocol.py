"""
The DataAgent protocol: minimal interface for state management.

All D-gents must implement this protocol to provide uniform access to state.
"""

from typing import TypeVar, Protocol, List
from abc import abstractmethod

S = TypeVar("S")  # State type


class DataAgent(Protocol[S]):
    """
    The core protocol for state management.

    A D-gent abstracts storage mechanisms, providing a uniform
    interface for stateful computation regardless of backend.
    """

    @abstractmethod
    async def load(self) -> S:
        """
        Retrieve current state.

        Returns:
            The current state value of type S

        Raises:
            StateNotFoundError: If state doesn't exist (first access)
            StateCorruptionError: If stored state fails validation
        """
        ...

    @abstractmethod
    async def save(self, state: S) -> None:
        """
        Persist new state.

        Args:
            state: The new state to save

        Raises:
            StateSerializationError: If state cannot be encoded
            StorageError: If backend write fails
        """
        ...

    @abstractmethod
    async def history(self, limit: int | None = None) -> List[S]:
        """
        Query state evolution over time.

        Args:
            limit: Maximum number of historical states to return
                   (None = all history)

        Returns:
            List of states, newest first (excludes current state)

        Note:
            Not all D-gents support history. Implementations may
            return empty list if history is not tracked.
        """
        ...
