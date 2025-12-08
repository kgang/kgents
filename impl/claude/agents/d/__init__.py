"""
D-gents: Data Agents for stateful computation.

This package provides the core abstractions for state management in kgents:

- DataAgent[S]: The protocol all D-gents implement
- VolatileAgent[S]: In-memory state (fast, ephemeral)
- Symbiont[I,O,S]: Fuses pure logic with stateful memory

State management philosophy:
- Pure logic should be stateless
- D-gents contain the complexity of memory
- Symbiont makes stateful agents composable via >>

Example:
    >>> from agents.d import VolatileAgent, Symbiont
    >>>
    >>> def counter_logic(inc: int, count: int) -> tuple[int, int]:
    ...     new_count = count + inc
    ...     return new_count, new_count
    ...
    >>> memory = VolatileAgent(_state=0)
    >>> counter = Symbiont(logic=counter_logic, memory=memory)
    >>>
    >>> await counter.invoke(1)  # Returns 1
    >>> await counter.invoke(5)  # Returns 6 (remembers previous state)
"""

from .protocol import DataAgent
from .errors import (
    StateError,
    StateNotFoundError,
    StateCorruptionError,
    StateSerializationError,
    StorageError,
)
from .volatile import VolatileAgent
from .symbiont import Symbiont

__all__ = [
    # Protocol
    "DataAgent",
    # Errors
    "StateError",
    "StateNotFoundError",
    "StateCorruptionError",
    "StateSerializationError",
    "StorageError",
    # Implementations
    "VolatileAgent",
    "Symbiont",
]
