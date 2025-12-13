"""
D-gent Polynomial: Memory Operations as State Machine.

The D-gent polynomial models data agents as a state machine:
- IDLE: Ready for operations
- LOADING: Retrieving state from storage
- STORING: Persisting state to storage
- QUERYING: Searching/filtering state
- STREAMING: Processing event stream
- FORGETTING: Controlled state removal

The Insight:
    Memory is not a passive store, but an active state machine.
    Different operations are valid in different states (directions).
    The polynomial structure enables composable memory operations.

Example:
    >>> agent = MemoryPolynomialAgent(initial_state={"count": 0})
    >>> response = await agent.store({"count": 1})
    >>> print(response.status, response.history_length)

See: plans/architecture/polyfunctor.md (Phase 3: D-gent Migration)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet, TypeVar

from agents.poly.primitives import (
    FORGET,
    REMEMBER,
    ForgetState,
    Memory,
    RememberState,
)
from agents.poly.protocol import PolyAgent

S = TypeVar("S")  # State type


# =============================================================================
# Memory State Machine
# =============================================================================


class MemoryPhase(Enum):
    """
    Positions in the D-gent polynomial.

    These model the lifecycle of memory operations:
    - IDLE: Ready for new operations
    - LOADING: Reading state from storage
    - STORING: Writing state to storage
    - QUERYING: Searching state
    - STREAMING: Processing events
    - FORGETTING: Controlled removal
    """

    IDLE = auto()
    LOADING = auto()
    STORING = auto()
    QUERYING = auto()
    STREAMING = auto()
    FORGETTING = auto()


@dataclass(frozen=True)
class LoadCommand:
    """Command to load state."""

    key: str | None = None
    default: Any = None


@dataclass(frozen=True)
class StoreCommand:
    """Command to store state."""

    state: Any
    key: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class QueryCommand:
    """Command to query state."""

    predicate: str | None = None
    path: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class ForgetCommand:
    """Command to forget state."""

    key: str | None = None
    predicate: str | None = None
    all: bool = False


@dataclass
class MemoryResponse:
    """Response from memory operations."""

    phase: MemoryPhase
    success: bool
    state: Any | None = None
    history: list[Any] = field(default_factory=list)
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Direction Functions (Phase-Dependent Valid Inputs)
# =============================================================================


def memory_directions(phase: MemoryPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each memory phase.

    This encodes what operations are valid in each state.
    """
    match phase:
        case MemoryPhase.IDLE:
            return frozenset(
                {LoadCommand, StoreCommand, QueryCommand, ForgetCommand, Any}
            )
        case MemoryPhase.LOADING:
            return frozenset({LoadCommand, type(LoadCommand), Any})
        case MemoryPhase.STORING:
            return frozenset({StoreCommand, type(StoreCommand), Any})
        case MemoryPhase.QUERYING:
            return frozenset({QueryCommand, type(QueryCommand), Any})
        case MemoryPhase.STREAMING:
            return frozenset({Any})  # Streaming accepts any events
        case MemoryPhase.FORGETTING:
            return frozenset({ForgetCommand, type(ForgetCommand), Any})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


class MemoryStore:
    """
    Instance-isolated memory store.

    Solves the global state problem by encapsulating memory per-agent.
    """

    def __init__(self) -> None:
        self.state: dict[str, Any] = {}
        self.history: list[Any] = []

    def clear(self) -> None:
        """Clear all state."""
        self.state.clear()
        self.history.clear()


# Default store for the singleton MEMORY_POLYNOMIAL
_default_store = MemoryStore()


def memory_transition(
    phase: MemoryPhase, input: Any, store: MemoryStore | None = None
) -> tuple[MemoryPhase, Any]:
    """
    Memory state transition function.

    This is the polynomial core:
    transition: Phase × Command → (NewPhase, Response)

    Integrates with REMEMBER and FORGET primitives.

    Args:
        phase: Current memory phase
        input: Command or data input
        store: Optional isolated memory store (uses default if None)
    """
    if store is None:
        store = _default_store

    match phase:
        case MemoryPhase.IDLE:
            # Route to appropriate operation
            if isinstance(input, LoadCommand):
                return MemoryPhase.LOADING, input
            elif isinstance(input, StoreCommand):
                return MemoryPhase.STORING, input
            elif isinstance(input, QueryCommand):
                return MemoryPhase.QUERYING, input
            elif isinstance(input, ForgetCommand):
                return MemoryPhase.FORGETTING, input
            else:
                # Default: treat as store command with the input as state
                return MemoryPhase.STORING, StoreCommand(state=input)

        case MemoryPhase.LOADING:
            lcmd = input if isinstance(input, LoadCommand) else LoadCommand()
            # Use REMEMBER primitive (for tracing)
            _, _ = REMEMBER.invoke(
                RememberState.IDLE, Memory(key=lcmd.key or "_default", content=None)
            )
            state = store.state.get(lcmd.key or "_default", lcmd.default)
            response = MemoryResponse(
                phase=MemoryPhase.LOADING,
                success=True,
                state=state,
                history=list(store.history),
            )
            return MemoryPhase.IDLE, response

        case MemoryPhase.STORING:
            scmd: StoreCommand
            if isinstance(input, StoreCommand):
                scmd = input
            else:
                scmd = StoreCommand(state=input)

            # Use REMEMBER primitive
            _, _ = REMEMBER.invoke(
                RememberState.STORING,
                Memory(key=scmd.key or "_default", content=scmd.state),
            )

            # Store in local state
            key = scmd.key or "_default"
            old_state = store.state.get(key)
            if old_state is not None:
                store.history.append(old_state)
            store.state[key] = scmd.state

            response = MemoryResponse(
                phase=MemoryPhase.STORING,
                success=True,
                state=scmd.state,
                history=list(store.history),
            )
            return MemoryPhase.IDLE, response

        case MemoryPhase.QUERYING:
            qcmd: QueryCommand
            if isinstance(input, QueryCommand):
                qcmd = input
            else:
                qcmd = QueryCommand(predicate=str(input) if input else None)

            # Simple query: return all state or filtered
            state = dict(store.state)
            history = list(store.history)[: qcmd.limit]

            response = MemoryResponse(
                phase=MemoryPhase.QUERYING,
                success=True,
                state=state,
                history=history,
            )
            return MemoryPhase.IDLE, response

        case MemoryPhase.STREAMING:
            # Streaming: append to history and return
            store.history.append(input)
            response = MemoryResponse(
                phase=MemoryPhase.STREAMING,
                success=True,
                state=input,
                history=list(store.history[-10:]),  # Last 10
            )
            return MemoryPhase.STREAMING, response  # Stay in streaming

        case MemoryPhase.FORGETTING:
            fcmd: ForgetCommand
            if isinstance(input, ForgetCommand):
                fcmd = input
            else:
                fcmd = ForgetCommand()

            # Use FORGET primitive
            _, _ = FORGET.invoke(ForgetState.FORGETTING, fcmd.key or "_all")

            # Perform forgetting
            if fcmd.all:
                store.clear()
            elif fcmd.key:
                store.state.pop(fcmd.key, None)

            response = MemoryResponse(
                phase=MemoryPhase.FORGETTING,
                success=True,
                state=None,
                history=list(store.history),
            )
            return MemoryPhase.IDLE, response

        case _:
            response = MemoryResponse(
                phase=phase,
                success=False,
                error=f"Unknown phase: {phase}",
            )
            return MemoryPhase.IDLE, response


# =============================================================================
# The Polynomial Agent
# =============================================================================


MEMORY_POLYNOMIAL: PolyAgent[MemoryPhase, Any, Any] = PolyAgent(
    name="MemoryPolynomial",
    positions=frozenset(MemoryPhase),
    _directions=memory_directions,
    _transition=memory_transition,
)
"""
The D-gent polynomial agent.

This models memory as a polynomial state machine:
- positions: 6 memory phases
- directions: phase-dependent valid commands
- transition: memory operations using REMEMBER/FORGET primitives
"""


# =============================================================================
# Backwards-Compatible Wrapper
# =============================================================================


def create_memory_polynomial(store: MemoryStore) -> PolyAgent[MemoryPhase, Any, Any]:
    """
    Create a memory polynomial with isolated store.

    Args:
        store: The memory store for this polynomial instance

    Returns:
        A PolyAgent bound to the given store
    """

    def bound_transition(phase: MemoryPhase, input: Any) -> tuple[MemoryPhase, Any]:
        return memory_transition(phase, input, store)

    return PolyAgent(
        name="MemoryPolynomial",
        positions=frozenset(MemoryPhase),
        _directions=memory_directions,
        _transition=bound_transition,
    )


class MemoryPolynomialAgent:
    """
    Backwards-compatible D-gent polynomial wrapper.

    Provides async DataAgent-like interface while using PolyAgent internally.
    Each instance has isolated memory state.

    Example:
        >>> agent = MemoryPolynomialAgent()
        >>> await agent.store({"key": "value"})
        >>> response = await agent.load()
        >>> print(response.state)
    """

    def __init__(self, initial_state: Any = None) -> None:
        # Each instance gets its own isolated memory store
        self._store = MemoryStore()
        self._poly = create_memory_polynomial(self._store)
        self._phase = MemoryPhase.IDLE

        # Initialize state if provided
        if initial_state is not None:
            self._store.state["_default"] = initial_state

    @property
    def name(self) -> str:
        return "MemoryPolynomialAgent"

    @property
    def phase(self) -> MemoryPhase:
        """Current memory phase."""
        return self._phase

    def reset(self) -> None:
        """Reset to IDLE phase."""
        self._phase = MemoryPhase.IDLE

    async def load(self, key: str | None = None, default: Any = None) -> MemoryResponse:
        """
        Load state from memory.

        Args:
            key: Optional key for named state
            default: Default value if not found

        Returns:
            MemoryResponse with loaded state
        """
        self._phase = MemoryPhase.IDLE
        cmd = LoadCommand(key=key, default=default)
        self._phase, result = self._poly.transition(self._phase, cmd)
        self._phase, result = self._poly.transition(self._phase, result)

        if isinstance(result, MemoryResponse):
            return result

        return MemoryResponse(
            phase=MemoryPhase.LOADING,
            success=False,
            error="Load failed",
        )

    async def store(
        self,
        state: Any,
        key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryResponse:
        """
        Store state to memory.

        Args:
            state: State to store
            key: Optional key for named state
            metadata: Optional metadata

        Returns:
            MemoryResponse with confirmation
        """
        self._phase = MemoryPhase.IDLE
        cmd = StoreCommand(state=state, key=key, metadata=metadata)
        self._phase, result = self._poly.transition(self._phase, cmd)
        self._phase, result = self._poly.transition(self._phase, result)

        if isinstance(result, MemoryResponse):
            return result

        return MemoryResponse(
            phase=MemoryPhase.STORING,
            success=False,
            error="Store failed",
        )

    async def query(
        self,
        predicate: str | None = None,
        path: str | None = None,
        limit: int = 100,
    ) -> MemoryResponse:
        """
        Query state.

        Args:
            predicate: Optional filter predicate
            path: Optional path to query
            limit: Maximum results

        Returns:
            MemoryResponse with query results
        """
        self._phase = MemoryPhase.IDLE
        cmd = QueryCommand(predicate=predicate, path=path, limit=limit)
        self._phase, result = self._poly.transition(self._phase, cmd)
        self._phase, result = self._poly.transition(self._phase, result)

        if isinstance(result, MemoryResponse):
            return result

        return MemoryResponse(
            phase=MemoryPhase.QUERYING,
            success=False,
            error="Query failed",
        )

    async def forget(
        self,
        key: str | None = None,
        predicate: str | None = None,
        all: bool = False,
    ) -> MemoryResponse:
        """
        Forget state.

        Args:
            key: Key to forget
            predicate: Predicate for selective forgetting
            all: Forget all state

        Returns:
            MemoryResponse with confirmation
        """
        self._phase = MemoryPhase.IDLE
        cmd = ForgetCommand(key=key, predicate=predicate, all=all)
        self._phase, result = self._poly.transition(self._phase, cmd)
        self._phase, result = self._poly.transition(self._phase, result)

        if isinstance(result, MemoryResponse):
            return result

        return MemoryResponse(
            phase=MemoryPhase.FORGETTING,
            success=False,
            error="Forget failed",
        )

    async def stream(self, event: Any) -> MemoryResponse:
        """
        Process a streaming event.

        Args:
            event: Event to process

        Returns:
            MemoryResponse with current stream state
        """
        if self._phase != MemoryPhase.STREAMING:
            self._phase = MemoryPhase.STREAMING

        self._phase, result = self._poly.transition(self._phase, event)

        if isinstance(result, MemoryResponse):
            return result

        return MemoryResponse(
            phase=MemoryPhase.STREAMING,
            success=True,
            state=event,
        )

    async def history(self, limit: int | None = None) -> list[Any]:
        """
        Get state history.

        Args:
            limit: Maximum history entries

        Returns:
            List of historical states
        """
        response = await self.query(limit=limit or 100)
        return response.history


# =============================================================================
# Utility Functions
# =============================================================================


def reset_memory() -> None:
    """Reset default memory store (for testing with MEMORY_POLYNOMIAL singleton)."""
    _default_store.clear()


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # State Machine
    "MemoryPhase",
    # Commands
    "LoadCommand",
    "StoreCommand",
    "QueryCommand",
    "ForgetCommand",
    # Response
    "MemoryResponse",
    # Memory Store
    "MemoryStore",
    # Polynomial Agent
    "MEMORY_POLYNOMIAL",
    "memory_directions",
    "memory_transition",
    "create_memory_polynomial",
    # Wrapper
    "MemoryPolynomialAgent",
    # Utilities
    "reset_memory",
]
