"""
Hippocampus: Short-Term Memory Consolidation for the Bicameral Engine.

The Hippocampus holds the "Day Log" - session context before encoding
to long-term storage. It provides:
- Fast in-memory storage for current session
- Flush to Cortex during Dreaming
- Lethe Epoch creation for forgetting boundaries

Design rationale:
- Jumping from Synapse directly to Long-Term Storage loses session context
- The Hippocampus buffers short-term memories
- During Dreaming, memories are consolidated to long-term storage

From the implementation plan:
> "A cortex doesn't just store; it predicts, forgets, and hallucinates."
> We now add: "A cortex also has reflexes, short-term memory, and learns new structures."

Biological analogy:
- Hippocampus: Temporary storage, needed for forming new long-term memories
- Sleep: Memory consolidation, transfer from hippocampus to neocortex
- Lethe: The river of forgetfulness in Greek mythology
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from .nervous import Signal
from .synapse import Synapse


@dataclass
class LetheEpoch:
    """
    A sealed epoch of memories eligible for forgetting.

    Lethe epochs mark boundaries for memory retention policies.
    Once an epoch is sealed, its memories can be:
    - Retained (consolidated to long-term)
    - Composted (compressed to statistics)
    - Forgotten (deleted with cryptographic proof)

    Named after the river Lethe in Greek mythology - drinking from it
    caused complete forgetfulness.
    """

    epoch_id: str
    created_at: str
    sealed_at: str
    signal_count: int
    signal_types: set[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_hours(self) -> float:
        """Duration of this epoch in hours."""
        created = datetime.fromisoformat(self.created_at)
        sealed = datetime.fromisoformat(self.sealed_at)
        return (sealed - created).total_seconds() / 3600


@dataclass
class FlushResult:
    """Result of flushing Hippocampus to Cortex."""

    signals_transferred: int
    epoch_id: str | None
    flush_time_ms: float
    errors: list[str] = field(default_factory=list)


@dataclass
class HippocampusConfig:
    """Configuration for the Hippocampus."""

    # Storage backend: "memory" or "redis" (future)
    backend: str = "memory"

    # Maximum size before auto-flush (in signals)
    max_size: int = 10000

    # Maximum age before auto-flush (in seconds)
    max_age_seconds: int = 3600  # 1 hour

    # Whether to create Lethe epochs on flush
    create_epochs: bool = True

    # Flush strategy: "on_sleep", "on_size", "on_age", "manual"
    flush_strategy: str = "on_sleep"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HippocampusConfig":
        """Create from configuration dict."""
        return cls(
            backend=data.get("backend", "memory"),
            max_size=data.get("max_size", 10000),
            max_age_seconds=data.get("max_age_seconds", 3600),
            create_epochs=data.get("create_epochs", True),
            flush_strategy=data.get("flush_strategy", "on_sleep"),
        )


@runtime_checkable
class ICortex(Protocol):
    """
    Protocol for the Cortex (Long-Term Storage).

    The Hippocampus flushes to the Cortex during consolidation.
    This protocol allows for dependency injection in tests.
    """

    async def store_signal(self, signal: Signal) -> bool:
        """Store a signal in long-term storage."""
        ...

    async def store_batch(self, signals: list[Signal]) -> int:
        """Store multiple signals. Returns count stored."""
        ...


class NullCortex:
    """Null Cortex for testing - drops all signals."""

    async def store_signal(self, signal: Signal) -> bool:
        return True

    async def store_batch(self, signals: list[Signal]) -> int:
        return len(signals)


class MemoryBackend:
    """
    In-memory storage backend for Hippocampus.

    Fast, ephemeral storage for current session.
    Lost on process termination (by design).
    """

    def __init__(self, max_size: int = 10000):
        self._signals: deque[Signal] = deque(maxlen=max_size)
        self._signal_types: set[str] = set()
        self._created_at: str = datetime.now().isoformat()

    async def append(self, signal: Signal) -> None:
        """Append a signal to short-term memory."""
        self._signals.append(signal)
        self._signal_types.add(signal.signal_type)

    async def drain(self) -> list[Signal]:
        """Drain all signals (destructive read)."""
        signals = list(self._signals)
        self._signals.clear()
        self._signal_types = set()
        self._created_at = datetime.now().isoformat()
        return signals

    async def peek(self, limit: int = 100) -> list[Signal]:
        """Peek at recent signals (non-destructive)."""
        return list(self._signals)[-limit:]

    @property
    def size(self) -> int:
        """Current number of signals."""
        return len(self._signals)

    @property
    def signal_types(self) -> set[str]:
        """Set of signal types in memory."""
        return self._signal_types.copy()

    @property
    def created_at(self) -> str:
        """When this batch started."""
        return self._created_at


class Hippocampus:
    """
    Short-Term Memory Consolidation.

    Holds current session context before encoding to long-term storage.
    Flushes to Cortex during Dreaming, creating Lethe Epochs for
    forgetting boundaries.

    Usage:
        hippocampus = Hippocampus()

        # During active session
        await hippocampus.remember(signal)

        # During Dreaming (sleep)
        result = await hippocampus.flush_to_cortex(cortex)
        # → Creates LetheEpoch, transfers memories to long-term storage
    """

    def __init__(
        self,
        cortex: ICortex | None = None,
        config: HippocampusConfig | None = None,
    ):
        """
        Initialize the Hippocampus.

        Args:
            cortex: Long-term storage target (can be set later)
            config: Configuration options
        """
        self._config = config or HippocampusConfig()
        self._cortex = cortex or NullCortex()

        # Initialize backend
        self._backend = MemoryBackend(max_size=self._config.max_size)

        # Epoch tracking
        self._epochs: list[LetheEpoch] = []
        self._current_epoch_start: str = datetime.now().isoformat()

        # Auto-flush state
        self._flush_lock = asyncio.Lock()
        self._last_flush: datetime = datetime.now()

    @property
    def config(self) -> HippocampusConfig:
        """Get configuration."""
        return self._config

    @property
    def size(self) -> int:
        """Current number of signals in short-term memory."""
        return self._backend.size

    @property
    def signal_types(self) -> set[str]:
        """Signal types currently in memory."""
        return self._backend.signal_types

    @property
    def epochs(self) -> list[LetheEpoch]:
        """List of sealed Lethe epochs."""
        return self._epochs.copy()

    @property
    def last_flush(self) -> datetime:
        """When the last flush occurred."""
        return self._last_flush

    def set_cortex(self, cortex: ICortex) -> None:
        """Set the Cortex for long-term storage."""
        self._cortex = cortex

    async def remember(self, signal: Signal) -> bool:
        """
        Store a signal in short-term memory.

        May trigger auto-flush based on flush_strategy.

        Args:
            signal: The signal to remember

        Returns:
            True if stored, False if error
        """
        await self._backend.append(signal)

        # Check auto-flush conditions
        if self._should_auto_flush():
            await self.flush_to_cortex()

        return True

    async def remember_batch(self, signals: list[Signal]) -> int:
        """
        Store multiple signals efficiently.

        Args:
            signals: List of signals to remember

        Returns:
            Number of signals stored
        """
        for signal in signals:
            await self._backend.append(signal)

        if self._should_auto_flush():
            await self.flush_to_cortex()

        return len(signals)

    def _should_auto_flush(self) -> bool:
        """Check if auto-flush should trigger."""
        strategy = self._config.flush_strategy

        if strategy == "manual":
            return False

        if strategy == "on_size" or strategy == "on_sleep":
            if self._backend.size >= self._config.max_size:
                return True

        if strategy == "on_age":
            age = datetime.now() - self._last_flush
            if age.total_seconds() >= self._config.max_age_seconds:
                return True

        return False

    async def flush_to_cortex(self, cortex: ICortex | None = None) -> FlushResult:
        """
        Transfer short-term memories to long-term storage.

        Called during Dreaming or when auto-flush triggers.
        Creates a Lethe Epoch marking this batch of memories.

        Args:
            cortex: Optional cortex override (uses configured if None)

        Returns:
            FlushResult with transfer statistics
        """
        target = cortex or self._cortex
        start_time = datetime.now()

        async with self._flush_lock:
            # Drain memories
            signals = await self._backend.drain()

            if not signals:
                return FlushResult(
                    signals_transferred=0,
                    epoch_id=None,
                    flush_time_ms=0.0,
                )

            errors = []

            # Transfer to cortex
            try:
                await target.store_batch(signals)
            except Exception as e:
                errors.append(str(e))

            # Create Lethe Epoch
            epoch_id = None
            if self._config.create_epochs:
                epoch = LetheEpoch(
                    epoch_id=str(uuid4()),
                    created_at=self._current_epoch_start,
                    sealed_at=datetime.now().isoformat(),
                    signal_count=len(signals),
                    signal_types={s.signal_type for s in signals},
                )
                self._epochs.append(epoch)
                epoch_id = epoch.epoch_id

            # Reset epoch tracking
            self._current_epoch_start = datetime.now().isoformat()
            self._last_flush = datetime.now()

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            return FlushResult(
                signals_transferred=len(signals),
                epoch_id=epoch_id,
                flush_time_ms=elapsed_ms,
                errors=errors,
            )

    async def peek(self, limit: int = 100) -> list[Signal]:
        """
        Peek at recent signals without removing them.

        Args:
            limit: Max signals to return

        Returns:
            List of recent signals
        """
        return await self._backend.peek(limit)

    async def recall_by_type(self, signal_type: str, limit: int = 100) -> list[Signal]:
        """
        Recall signals of a specific type (non-destructive).

        Args:
            signal_type: Type to filter by
            limit: Max signals to return

        Returns:
            Matching signals
        """
        all_signals = await self._backend.peek(limit * 10)  # Over-fetch then filter
        return [s for s in all_signals if s.signal_type == signal_type][:limit]

    def get_epoch(self, epoch_id: str) -> LetheEpoch | None:
        """Get a specific epoch by ID."""
        for epoch in self._epochs:
            if epoch.epoch_id == epoch_id:
                return epoch
        return None

    def forget_epoch(self, epoch_id: str) -> bool:
        """
        Mark an epoch as forgotten.

        In production, this would trigger cryptographic deletion.
        For now, we just remove from the list.

        Args:
            epoch_id: Epoch to forget

        Returns:
            True if forgotten, False if not found
        """
        for i, epoch in enumerate(self._epochs):
            if epoch.epoch_id == epoch_id:
                self._epochs.pop(i)
                return True
        return False

    def age_seconds(self) -> float:
        """Age of current session in seconds."""
        return (datetime.now() - self._last_flush).total_seconds()

    def stats(self) -> dict[str, Any]:
        """Get hippocampus statistics."""
        return {
            "size": self.size,
            "signal_types": list(self.signal_types),
            "epoch_count": len(self._epochs),
            "age_seconds": self.age_seconds(),
            "last_flush": self._last_flush.isoformat(),
            "config": {
                "backend": self._config.backend,
                "max_size": self._config.max_size,
                "flush_strategy": self._config.flush_strategy,
            },
        }


# Factory function
def create_hippocampus(
    cortex: ICortex | None = None,
    config_dict: dict[str, Any] | None = None,
) -> Hippocampus:
    """
    Create a Hippocampus with optional configuration.

    Args:
        cortex: Long-term storage target
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured Hippocampus
    """
    config = (
        HippocampusConfig.from_dict(config_dict) if config_dict else HippocampusConfig()
    )
    return Hippocampus(cortex=cortex, config=config)


# Integration with Synapse
class SynapseHippocampusIntegration:
    """
    Integration layer connecting Synapse and Hippocampus.

    Signals that pass through Synapse can optionally be remembered
    in the Hippocampus for session context.
    """

    def __init__(self, synapse: Synapse, hippocampus: Hippocampus):
        self._synapse = synapse
        self._hippocampus = hippocampus

        # Register as handler
        synapse.on_fast_path(self._remember_signal)
        synapse.on_batch_path(self._remember_signal)

    async def _remember_signal(self, signal: Signal) -> None:
        """Remember signal in hippocampus."""
        await self._hippocampus.remember(signal)

    @property
    def synapse(self) -> Synapse:
        return self._synapse

    @property
    def hippocampus(self) -> Hippocampus:
        return self._hippocampus
