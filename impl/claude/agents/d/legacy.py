"""
Legacy stubs for deleted D-gent modules.

DEPRECATED: These are placeholder types for backward compatibility.

The data architecture rewrite removed many complex abstractions.
These stubs allow old code to import without errors, but the
implementations are minimal/no-op.

For new code, use:
- DgentProtocol + backends (MemoryBackend, SQLiteBackend, etc.)
- DataBus for reactive updates
- Memory (M-gent) for semantic memory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

S = TypeVar("S")


@dataclass
class MemoryConfig:
    """
    DEPRECATED: Old memory configuration.

    The new architecture doesn't require explicit configuration.
    Use DgentRouter for automatic backend selection.
    """

    max_size: int = 1000
    ttl_seconds: float | None = None
    compression: bool = False
    # Legacy flags (no-op in stub)
    enable_temporal: bool = False
    enable_semantic: bool = False

    @classmethod
    def default(cls) -> MemoryConfig:
        return cls()


@dataclass
class UnifiedMemory(Generic[S]):
    """
    DEPRECATED: Old unified memory abstraction.

    Replaced by:
    - D-gent (DgentProtocol) for raw storage
    - M-gent (MgentProtocol) for semantic memory
    - DataBus for reactive updates
    """

    _backend: Any = None  # Optional backend (ignored in stub)
    config: MemoryConfig = field(default_factory=MemoryConfig.default)
    _store: dict[str, Any] = field(default_factory=dict, repr=False)
    _history: list[tuple[str, Any]] = field(default_factory=list, repr=False)

    def get(self, key: str) -> Any | None:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()

    # Legacy async methods (minimal stub for backward compatibility)
    async def save(self, state: S) -> None:
        """Save state (stub stores in _current)."""
        self._store["_current"] = state

    async def load(self) -> S | None:
        """Load state (stub returns _current)."""
        return self._store.get("_current")

    async def witness(self, label: str, state: S) -> None:
        """Record state snapshot (stub appends to history)."""
        self._history.append((label, state))


@dataclass
class MemoryLoadResponse:
    """
    DEPRECATED: Old memory load response type.

    The new architecture returns Datum or Memory directly.
    """

    success: bool
    data: Any | None = None
    error: str | None = None

    @classmethod
    def ok(cls, data: Any) -> MemoryLoadResponse:
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> MemoryLoadResponse:
        return cls(success=False, error=error)


@dataclass
class WitnessReport:
    """
    DEPRECATED: Old witness/trace report.

    The new architecture uses TraceMonoid for causal tracing
    and DataBus events for observation.
    """

    events: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""

    def add_event(self, event: dict[str, Any]) -> None:
        self.events.append(event)


@dataclass
class MemoryPolynomialAgent:
    """
    DEPRECATED: Old polynomial memory agent.

    Replaced by:
    - PolyAgent[S, A, B] for state machines
    - M-gent for memory lifecycle
    - DataBus for mode transitions
    """

    state: str = "idle"
    _transitions: dict[str, list[str]] = field(default_factory=dict, repr=False)

    def can_transition(self, to_state: str) -> bool:
        allowed = self._transitions.get(self.state, [])
        return to_state in allowed

    def transition(self, to_state: str) -> bool:
        if self.can_transition(to_state):
            self.state = to_state
            return True
        return False
