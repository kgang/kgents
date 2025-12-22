"""
Synergy Event Bus: Cross-jewel communication infrastructure.

Foundation 4 of the Enlightened Crown strategy.

The bus provides:
1. Non-blocking event emission (fire and forget)
2. Handler registration by event type
3. Graceful degradation (handler failures don't break source)
4. Observable synergy results for CLI/UI visibility

Usage:
    bus = get_synergy_bus()

    # Emit an event (non-blocking)
    await bus.emit(event)

    # Register a handler
    bus.register(SynergyEventType.ANALYSIS_COMPLETE, my_handler)

    # Subscribe to results (for UI notifications)
    unsubscribe = bus.subscribe_results(on_synergy_result)
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Protocol

from opentelemetry import trace

from .events import Jewel, SynergyEvent, SynergyEventType, SynergyResult

if TYPE_CHECKING:
    pass

# Logger for synergy operations
logger = logging.getLogger("kgents.synergy")

# OTEL tracer
_tracer = trace.get_tracer("kgents.synergy", "0.1.0")

# Span attributes
ATTR_EVENT_TYPE = "synergy.event_type"
ATTR_SOURCE_JEWEL = "synergy.source_jewel"
ATTR_TARGET_JEWEL = "synergy.target_jewel"
ATTR_HANDLER_NAME = "synergy.handler_name"
ATTR_HANDLER_COUNT = "synergy.handler_count"


class SynergyHandler(Protocol):
    """Protocol for synergy event handlers."""

    @property
    def name(self) -> str:
        """Handler name for logging/display."""
        ...

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a synergy event."""
        ...


# Type for result subscribers
ResultSubscriber = Callable[[SynergyEvent, SynergyResult], None]


class SynergyEventBus:
    """
    Central event bus for cross-jewel communication.

    Features:
    - Non-blocking emission (handlers run in background)
    - Multiple handlers per event type
    - Result subscription for UI notifications
    - Graceful degradation on handler failures
    """

    def __init__(self) -> None:
        self._handlers: dict[SynergyEventType, list[SynergyHandler]] = defaultdict(list)
        self._result_subscribers: list[ResultSubscriber] = []
        self._lock = threading.Lock()
        self._pending_tasks: set[asyncio.Task[None]] = set()

    def register(
        self,
        event_type: SynergyEventType,
        handler: SynergyHandler,
    ) -> Callable[[], None]:
        """
        Register a handler for an event type.

        Returns an unsubscribe function.
        """
        with self._lock:
            self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            with self._lock:
                if handler in self._handlers[event_type]:
                    self._handlers[event_type].remove(handler)

        return unsubscribe

    def subscribe_results(self, subscriber: ResultSubscriber) -> Callable[[], None]:
        """
        Subscribe to synergy results for UI notifications.

        The subscriber receives (event, result) for each handled event.
        Returns an unsubscribe function.
        """
        with self._lock:
            self._result_subscribers.append(subscriber)

        def unsubscribe() -> None:
            with self._lock:
                if subscriber in self._result_subscribers:
                    self._result_subscribers.remove(subscriber)

        return unsubscribe

    async def emit(self, event: SynergyEvent) -> None:
        """
        Emit an event to all registered handlers.

        This is fire-and-forget: handlers run in background tasks.
        The source operation is not blocked by handler execution.
        """
        with _tracer.start_as_current_span("synergy.emit") as span:
            span.set_attribute(ATTR_EVENT_TYPE, event.event_type.value)
            span.set_attribute(ATTR_SOURCE_JEWEL, event.source_jewel.value)
            span.set_attribute(ATTR_TARGET_JEWEL, event.target_jewel.value)

            handlers = self._get_handlers(event)
            span.set_attribute(ATTR_HANDLER_COUNT, len(handlers))

            if not handlers:
                logger.debug(f"No handlers for {event.event_type.value}")
                return

            # Create background task for dispatch
            task = asyncio.create_task(self._dispatch(event, handlers))
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)

    async def emit_and_wait(self, event: SynergyEvent) -> list[SynergyResult]:
        """
        Emit an event and wait for all handlers to complete.

        Returns list of results from all handlers.
        Useful for testing or when results are needed immediately.
        """
        handlers = self._get_handlers(event)
        if not handlers:
            return []

        results: list[SynergyResult] = []
        for handler in handlers:
            result = await self._safe_handle(handler, event)
            results.append(result)
            self._notify_subscribers(event, result)

        return results

    def _get_handlers(self, event: SynergyEvent) -> list[SynergyHandler]:
        """Get handlers for an event based on event type and target jewel."""
        with self._lock:
            handlers = list(self._handlers.get(event.event_type, []))
        return handlers

    async def _dispatch(
        self,
        event: SynergyEvent,
        handlers: list[SynergyHandler],
    ) -> None:
        """Dispatch event to all handlers."""
        with _tracer.start_as_current_span("synergy.dispatch"):
            for handler in handlers:
                result = await self._safe_handle(handler, event)
                self._notify_subscribers(event, result)

    async def _safe_handle(
        self,
        handler: SynergyHandler,
        event: SynergyEvent,
    ) -> SynergyResult:
        """Handle an event with error catching."""
        with _tracer.start_as_current_span("synergy.handle") as span:
            span.set_attribute(ATTR_HANDLER_NAME, handler.name)

            try:
                return await handler.handle(event)
            except Exception as e:
                logger.warning(
                    f"Synergy handler {handler.name} failed: {e}",
                    exc_info=True,
                )
                span.record_exception(e)
                return SynergyResult(
                    success=False,
                    handler_name=handler.name,
                    message=f"Handler failed: {e}",
                )

    def _notify_subscribers(
        self,
        event: SynergyEvent,
        result: SynergyResult,
    ) -> None:
        """Notify result subscribers."""
        with self._lock:
            subscribers = list(self._result_subscribers)

        for subscriber in subscribers:
            try:
                subscriber(event, result)
            except Exception as e:
                logger.warning(f"Result subscriber failed: {e}")

    async def drain(self, timeout: float = 5.0) -> None:
        """
        Wait for all pending tasks to complete.

        Useful for testing or graceful shutdown.
        """
        if not self._pending_tasks:
            return

        try:
            await asyncio.wait_for(
                asyncio.gather(*self._pending_tasks, return_exceptions=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout waiting for synergy tasks, {len(self._pending_tasks)} still pending"
            )

    def clear(self) -> None:
        """Clear all handlers and subscribers (for testing)."""
        with self._lock:
            self._handlers.clear()
            self._result_subscribers.clear()


# =============================================================================
# Singleton Instance
# =============================================================================

_bus: SynergyEventBus | None = None
_bus_lock = threading.Lock()


def get_synergy_bus() -> SynergyEventBus:
    """
    Get the global synergy bus instance.

    The bus is lazily initialized on first call.
    """
    global _bus
    if _bus is None:
        with _bus_lock:
            if _bus is None:
                _bus = SynergyEventBus()
                # Register default handlers
                _register_default_handlers(_bus)
    return _bus


def reset_synergy_bus() -> None:
    """Reset the global bus instance (for testing)."""
    global _bus
    with _bus_lock:
        if _bus is not None:
            _bus.clear()
        _bus = None


def _register_default_handlers(bus: SynergyEventBus) -> None:
    """Register the default synergy handlers.

    Note: Most handlers removed 2025-12-21 as part of cleanup.
    - Gestalt, Coalition, Domain, Park handlers: archived
    - Garden handlers: deprecated (see spec/protocols/_archive/gardener-evergreen-heritage.md)
    - Atelier handlers: removed

    Currently only WitnessToBrainHandler remains (8th Crown Jewel).
    New handlers should be added here as the system evolves.
    """
    # Import here to avoid circular imports
    from .handlers import WitnessToBrainHandler

    # ==========================================================================
    # Witness (8th Crown Jewel): Capture thoughts and commits to Brain
    # ==========================================================================
    bus.register(
        SynergyEventType.WITNESS_THOUGHT_CAPTURED,
        WitnessToBrainHandler(),
    )


__all__ = [
    # Main class
    "SynergyEventBus",
    # Protocol
    "SynergyHandler",
    "ResultSubscriber",
    # Singleton
    "get_synergy_bus",
    "reset_synergy_bus",
]
