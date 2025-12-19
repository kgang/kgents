"""
State Backend Adapters: Bridge various storage systems to StateBackend[S].

This module provides adapters that wrap existing storage mechanisms
to conform to the StateBackend protocol.

Adapters:
    - MemoryStateBackend: In-memory state (volatile, fast)
    - DataAgentBackend: Wraps legacy DataAgent[S] protocol
    - DgentStateBackend: Wraps DgentProtocol with serialization

The adapter pattern allows StateFunctor to work with any storage
backend without coupling to specific implementations.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from .protocol import StateBackend

if TYPE_CHECKING:
    from agents.d.datum import Datum
    from agents.d.protocol import DataAgent, DgentProtocol

S = TypeVar("S")


@dataclass
class MemoryStateBackend(Generic[S]):
    """
    In-memory state backend.

    Fast, volatile storage for state. State is lost on process termination.
    Useful for testing, conversational context, and temporary state.

    Uses deep copy for isolation - mutations to loaded state don't
    affect stored state until explicitly saved.

    Example:
        backend = MemoryStateBackend(initial={"count": 0})
        state = await backend.load()  # {"count": 0}
        state["count"] += 1
        await backend.save(state)
        # State persisted in memory
    """

    initial: S
    _state: S = field(init=False)

    def __post_init__(self) -> None:
        """Initialize internal state from initial value."""
        self._state = copy.deepcopy(self.initial)

    async def load(self) -> S:
        """Load current state (returns deep copy)."""
        return copy.deepcopy(self._state)

    async def save(self, state: S) -> None:
        """Save new state (stores deep copy)."""
        self._state = copy.deepcopy(state)

    def snapshot(self) -> S:
        """
        Non-async snapshot for testing/debugging.

        Returns current state without async overhead.
        """
        return copy.deepcopy(self._state)

    def reset(self) -> None:
        """Reset state to initial value."""
        self._state = copy.deepcopy(self.initial)


@dataclass
class DataAgentBackend(Generic[S]):
    """
    Adapter for legacy DataAgent[S] protocol.

    Wraps agents implementing the old DataAgent protocol (load/save/history)
    to conform to StateBackend. Enables migration path for existing code.

    Example:
        # Wrap existing VolatileAgent
        from agents.d import VolatileAgent
        volatile = VolatileAgent(_state={"count": 0})
        backend = DataAgentBackend(agent=volatile)

        # Use with StateFunctor
        state_functor = StateFunctor(backend=backend, ...)
    """

    agent: "DataAgent[S]"

    async def load(self) -> S:
        """Delegate to DataAgent.load()."""
        return await self.agent.load()

    async def save(self, state: S) -> None:
        """Delegate to DataAgent.save()."""
        await self.agent.save(state)


@dataclass
class DgentStateBackend(Generic[S]):
    """
    Adapter for DgentProtocol with serialization.

    Wraps a DgentProtocol backend (put/get/delete/list/causal_chain)
    to provide StateBackend interface. Requires a codec for serialization.

    The state is stored as a single Datum with a fixed key.

    Example:
        from agents.d import MemoryBackend
        dgent = MemoryBackend()
        backend = DgentStateBackend(
            dgent=dgent,
            key="my_state",
            serialize=json.dumps,
            deserialize=json.loads,
            initial={"count": 0},
        )
    """

    dgent: "DgentProtocol"
    key: str
    serialize: Callable[[S], bytes] = field(default_factory=lambda: _json_serialize)
    deserialize: Callable[[bytes], S] = field(default_factory=lambda: _json_deserialize)
    initial: S | None = None

    async def load(self) -> S:
        """Load state from DgentProtocol."""
        from agents.d.datum import Datum

        datum = await self.dgent.get(self.key)
        if datum is None:
            if self.initial is not None:
                return copy.deepcopy(self.initial)
            raise ValueError(f"No state found for key '{self.key}' and no initial provided")
        return self.deserialize(datum.content)

    async def save(self, state: S) -> None:
        """Save state to DgentProtocol."""
        import time

        from agents.d.datum import Datum

        datum = Datum(
            id=self.key,
            content=self.serialize(state),
            created_at=time.time(),
            metadata={"type": "state", "backend": "dgent"},
        )
        await self.dgent.put(datum)


def _json_serialize(obj: Any) -> bytes:
    """Default JSON serializer."""
    return json.dumps(obj).encode("utf-8")


def _json_deserialize(data: bytes) -> Any:
    """Default JSON deserializer."""
    return json.loads(data.decode("utf-8"))


__all__ = [
    "MemoryStateBackend",
    "DataAgentBackend",
    "DgentStateBackend",
]
