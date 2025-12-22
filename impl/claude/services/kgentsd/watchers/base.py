"""
BaseWatcher: Common Infrastructure for Event-Driven Watchers.

All Witness watchers share:
- State lifecycle (STOPPED → STARTING → RUNNING → STOPPING → ERROR)
- Handler pattern (add/remove handlers, emit events)
- Async iterator interface (async for event in watcher.watch())
- Statistics tracking

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

This base class ensures consistent behavior across all watcher types.

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, AsyncIterator, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)


# =============================================================================
# Watcher State (Shared Lifecycle)
# =============================================================================


class WatcherState(Enum):
    """State of any watcher."""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    ERROR = auto()


@dataclass
class WatcherStats:
    """Statistics for watchers (shared across all types)."""

    events_emitted: int = 0
    last_event_time: datetime | None = None
    errors_count: int = 0
    started_at: datetime | None = None

    def record_event(self) -> None:
        """Record an event emission."""
        self.events_emitted += 1
        self.last_event_time = datetime.now()

    def record_error(self) -> None:
        """Record an error."""
        self.errors_count += 1


# =============================================================================
# Event Protocol
# =============================================================================

E = TypeVar("E")  # Event type


# =============================================================================
# BaseWatcher (Abstract)
# =============================================================================


class BaseWatcher(ABC, Generic[E]):
    """
    Abstract base class for all Witness watchers.

    Provides:
    - State lifecycle management
    - Handler pattern for event notification
    - Async iterator interface
    - Statistics tracking
    - Graceful shutdown

    Subclasses must implement:
    - _watch_loop(): The main watching logic
    - _cleanup(): Resource cleanup on stop

    Usage Pattern:
        >>> class MyWatcher(BaseWatcher[MyEvent]):
        ...     async def _watch_loop(self) -> None:
        ...         while not self._stop_event.is_set():
        ...             event = await self._detect_event()
        ...             if event:
        ...                 self._emit(event)
        ...
        ...     async def _cleanup(self) -> None:
        ...         pass  # Release resources

    Crown Jewel Pattern: Container-Owns-Workflow
    The watcher owns its watch loop lifecycle.
    """

    def __init__(self) -> None:
        self.state = WatcherState.STOPPED
        self.stats = WatcherStats()
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._handlers: list[Callable[[E], None]] = []

    # -------------------------------------------------------------------------
    # Handler Pattern
    # -------------------------------------------------------------------------

    def add_handler(self, handler: Callable[[E], None]) -> None:
        """Add an event handler."""
        self._handlers.append(handler)

    def remove_handler(self, handler: Callable[[E], None]) -> None:
        """Remove an event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def _emit(self, event: E) -> None:
        """Emit an event to all handlers."""
        self.stats.record_event()
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"{self.__class__.__name__} handler error: {e}")
                self.stats.record_error()

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def start(self) -> None:
        """Start the watcher."""
        if self.state == WatcherState.RUNNING:
            return

        self.state = WatcherState.STARTING
        self._stop_event.clear()

        # Subclass-specific initialization
        await self._on_start()

        self.stats.started_at = datetime.now()
        self.state = WatcherState.RUNNING

        # Start the watch loop
        self._task = asyncio.create_task(self._run_watch_loop())

        logger.info(f"{self.__class__.__name__} started")

    async def stop(self) -> None:
        """Stop the watcher gracefully."""
        if self.state != WatcherState.RUNNING:
            return

        self.state = WatcherState.STOPPING
        self._stop_event.set()

        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

        # Subclass cleanup
        await self._cleanup()

        self.state = WatcherState.STOPPED
        logger.info(f"{self.__class__.__name__} stopped")

    async def _run_watch_loop(self) -> None:
        """Wrapper around watch loop with error handling."""
        try:
            await self._watch_loop()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"{self.__class__.__name__} watch loop error: {e}")
            self.stats.record_error()
            self.state = WatcherState.ERROR

    # -------------------------------------------------------------------------
    # Async Iterator Interface
    # -------------------------------------------------------------------------

    async def watch(self) -> AsyncIterator[E]:
        """
        Async iterator interface for event consumption.

        Usage:
            async for event in watcher.watch():
                process(event)

        Automatically starts the watcher if not running.
        """
        queue: asyncio.Queue[E] = asyncio.Queue()

        def enqueue(event: E) -> None:
            queue.put_nowait(event)

        self.add_handler(enqueue)

        try:
            if self.state != WatcherState.RUNNING:
                await self.start()

            while self.state == WatcherState.RUNNING:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield event
                except asyncio.TimeoutError:
                    continue  # Check state and continue

        finally:
            self.remove_handler(enqueue)
            await self.stop()

    # -------------------------------------------------------------------------
    # Abstract Methods (Subclass Must Implement)
    # -------------------------------------------------------------------------

    async def _on_start(self) -> None:
        """Called during start(), before watch loop begins.

        Override to initialize resources (e.g., connections, initial state).
        Default implementation does nothing.
        """
        pass

    @abstractmethod
    async def _watch_loop(self) -> None:
        """
        Main watching logic.

        Must check self._stop_event.is_set() periodically.
        Emit events using self._emit(event).
        """
        ...

    async def _cleanup(self) -> None:
        """Called during stop(), after watch loop ends.

        Override to release resources.
        Default implementation does nothing.
        """
        pass


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BaseWatcher",
    "WatcherState",
    "WatcherStats",
]
