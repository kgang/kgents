"""
Differance Integration Helpers for Crown Jewels.

Provides easy integration of trace recording into Brain, Gardener, and other Crown Jewels.
This is the Phase 5: FRUITING integration layer.

Usage Pattern (Pattern 6: Async-Safe Event Emission):

    from agents.differance.integration import (
        record_trace,
        record_trace_sync,
        get_trace_context,
        DifferanceIntegration,
    )

    # In async code (preferred):
    await record_trace(
        operation="capture",
        inputs=(content[:50],),
        output=crystal_id,
        context="Capturing memory to brain",
        alternatives=[
            Alternative("categorize_first", ("auto-tag",), "Could auto-categorize"),
        ],
    )

    # In sync code (uses create_task pattern):
    record_trace_sync(
        operation="record_gesture",
        inputs=(gesture.verb.name, gesture.target),
        output=f"gesture_{gesture.id}",
        context=gesture.reasoning or "Tending garden",
    )

See: spec/protocols/differance.md
See: plans/differance-cultivation.md (Phase 5)
"""

from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

if TYPE_CHECKING:
    from .store import DifferanceStore
    from .trace import Alternative, TraceMonoid, WiringTrace

logger = logging.getLogger(__name__)

# =============================================================================
# Context Variables for Trace Context
# =============================================================================

# Current trace ID (for parent linking)
_current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)

# Global differance store (set at app startup)
_differance_store: ContextVar["DifferanceStore | None"] = ContextVar(
    "differance_store", default=None
)

# Global trace monoid (for in-memory operation)
_trace_monoid: ContextVar["TraceMonoid | None"] = ContextVar("trace_monoid", default=None)

# Mutable trace buffer for sync recording
# (TraceMonoid is frozen, so we use a list for sync accumulation)
# NOTE: Module-level buffer is deprecated; use ContextVar-based buffer for test isolation
_trace_buffer: list["WiringTrace"] = []

# ContextVar-based buffer for test isolation (Phase 6A)
_isolated_trace_buffer: ContextVar[list["WiringTrace"] | None] = ContextVar(
    "isolated_trace_buffer", default=None
)


def _get_active_buffer() -> list["WiringTrace"]:
    """
    Get the active trace buffer.

    Returns isolated buffer if set (for testing), otherwise global buffer.
    This enables pytest-xdist parallel test isolation.
    """
    isolated = _isolated_trace_buffer.get()
    if isolated is not None:
        return isolated
    return _trace_buffer


def create_isolated_buffer() -> list["WiringTrace"]:
    """
    Create and set an isolated buffer for the current context.

    Use in pytest fixtures for test isolation:

        @pytest.fixture(autouse=True)
        def differance_buffer():
            buffer = create_isolated_buffer()
            yield buffer
            reset_isolated_buffer()
    """
    buffer: list["WiringTrace"] = []
    _isolated_trace_buffer.set(buffer)
    return buffer


def reset_isolated_buffer() -> None:
    """Reset the isolated buffer to None, reverting to global buffer."""
    _isolated_trace_buffer.set(None)


# Correlation ID for request-level tracing (Phase 6A)
_current_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Get the current correlation ID from context."""
    return _current_correlation_id.get()


def set_correlation_id(correlation_id: str | None) -> None:
    """Set the correlation ID in context."""
    _current_correlation_id.set(correlation_id)


def get_current_trace_id() -> str | None:
    """Get the current trace ID from context."""
    return _current_trace_id.get()


def set_current_trace_id(trace_id: str | None) -> None:
    """Set the current trace ID in context."""
    _current_trace_id.set(trace_id)


def get_differance_store() -> "DifferanceStore | None":
    """Get the global differance store."""
    return _differance_store.get()


def set_differance_store(store: "DifferanceStore | None") -> None:
    """Set the global differance store."""
    _differance_store.set(store)


def get_trace_monoid() -> "TraceMonoid | None":
    """Get the global trace monoid."""
    return _trace_monoid.get()


def set_trace_monoid(monoid: "TraceMonoid | None") -> None:
    """Set the global trace monoid."""
    _trace_monoid.set(monoid)


def get_trace_buffer() -> list["WiringTrace"]:
    """Get the mutable trace buffer (for sync recording)."""
    return _get_active_buffer()


def clear_trace_buffer() -> list["WiringTrace"]:
    """Clear and return the trace buffer contents."""
    global _trace_buffer
    buffer = _get_active_buffer()
    traces = buffer.copy()
    buffer.clear()
    return traces


def _append_to_monoid_buffer(trace: "WiringTrace") -> None:
    """Append trace to the active buffer."""
    _get_active_buffer().append(trace)


# =============================================================================
# Trace Context Manager
# =============================================================================


@dataclass
class TraceContext:
    """
    Context manager for trace scoping.

    Automatically sets parent_trace_id for nested traces.

    Example:
        async with TraceContext("processing_request") as ctx:
            # All traces within this block will have ctx.trace_id as parent
            await record_trace(...)
    """

    operation: str
    trace_id: str = field(default_factory=lambda: f"trace_{uuid4().hex[:8]}")
    _previous_id: str | None = field(default=None, init=False)

    async def __aenter__(self) -> "TraceContext":
        self._previous_id = get_current_trace_id()
        set_current_trace_id(self.trace_id)
        return self

    async def __aexit__(self, *args: Any) -> None:
        set_current_trace_id(self._previous_id)


def get_trace_context(operation: str) -> TraceContext:
    """Create a trace context for scoping nested traces."""
    return TraceContext(operation=operation)


# =============================================================================
# Record Trace Functions
# =============================================================================


async def record_trace(
    operation: str,
    inputs: tuple[Any, ...],
    output: Any,
    context: str = "",
    alternatives: list["Alternative"] | None = None,
    parent_trace_id: str | None = None,
) -> str | None:
    """
    Record a trace asynchronously.

    This is the primary integration point for async code.

    Args:
        operation: The operation name (e.g., "capture", "record_gesture")
        inputs: Tuple of input values
        output: The output value
        context: Human-readable context string
        alternatives: List of Alternative objects (roads not taken)
        parent_trace_id: Override parent (defaults to current context)

    Returns:
        The trace ID if recorded, None if no store available
    """
    from .trace import Alternative, WiringTrace

    store = get_differance_store()
    monoid = get_trace_monoid()

    if store is None and monoid is None:
        logger.debug("No differance store/monoid configured, skipping trace")
        return None

    # Generate trace ID
    trace_id = f"trace_{uuid4().hex[:8]}"

    # Resolve parent
    parent = parent_trace_id or get_current_trace_id()

    # Create trace
    trace = WiringTrace(
        trace_id=trace_id,
        operation=operation,
        inputs=inputs,
        output=output,
        context=context,
        alternatives=tuple(alternatives or []),
        timestamp=datetime.now(timezone.utc),
        parent_trace_id=parent,
    )

    # Record to store (async)
    if store:
        try:
            await store.append(trace)
            logger.debug(f"Recorded trace {trace_id} to store")
        except Exception as e:
            logger.warning(f"Failed to record trace to store: {e}")

    # Record to monoid (sync)
    # Note: TraceMonoid.traces is immutable tuple, so we compose instead of mutating
    if monoid:
        try:
            # Create a new monoid with this trace and compose
            new_monoid = TraceMonoid(traces=(trace,))
            # Note: Caller should handle composition if they need accumulated result
            logger.debug(f"Recorded trace {trace_id} (monoid composition available via compose)")
        except Exception as e:
            logger.warning(f"Failed to record trace to monoid: {e}")

    return trace_id


def record_trace_sync(
    operation: str,
    inputs: tuple[Any, ...],
    output: Any,
    context: str = "",
    alternatives: list["Alternative"] | None = None,
    parent_trace_id: str | None = None,
    force_buffer: bool = True,
) -> str | None:
    """
    Record a trace from sync code.

    Uses Pattern 6 (Async-Safe Event Emission) to bridge sync → async.

    Args:
        operation: The operation name
        inputs: Tuple of input values
        output: The output value
        context: Human-readable context string
        alternatives: List of Alternative objects
        parent_trace_id: Override parent (defaults to current context)
        force_buffer: If True (default), always record to buffer even without store/monoid

    Returns:
        The trace ID if scheduled, None if disabled
    """
    from .trace import Alternative, WiringTrace

    store = get_differance_store()
    monoid = get_trace_monoid()

    # Generate trace ID - always generate
    trace_id = f"trace_{uuid4().hex[:8]}"

    # Skip if no store, no monoid, and not forcing buffer
    if store is None and monoid is None and not force_buffer:
        logger.debug("No differance store/monoid configured, skipping trace")
        return None

    # Resolve parent
    parent = parent_trace_id or get_current_trace_id()

    # Create trace
    trace = WiringTrace(
        trace_id=trace_id,
        operation=operation,
        inputs=inputs,
        output=output,
        context=context,
        alternatives=tuple(alternatives or []),
        timestamp=datetime.now(timezone.utc),
        parent_trace_id=parent,
    )

    # Always record to buffer (for in-memory access)
    try:
        _append_to_monoid_buffer(trace)
        logger.debug(f"Recorded trace {trace_id} to buffer")
    except Exception as e:
        logger.warning(f"Failed to record trace to buffer: {e}")

    # Record to store (async - scheduled)
    if store:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_async_append(store, trace, trace_id))
            logger.debug(f"Scheduled trace {trace_id} for async recording")
        except RuntimeError:
            # No running event loop - skip async recording
            logger.debug(f"No event loop for async trace recording: {trace_id}")

    return trace_id


async def _async_append(store: "DifferanceStore", trace: "WiringTrace", trace_id: str) -> None:
    """Helper to append trace asynchronously."""
    try:
        await store.append(trace)
        logger.debug(f"Async recorded trace {trace_id}")
    except Exception as e:
        logger.warning(f"Failed async trace recording: {e}")


# =============================================================================
# Integration Class (for Crown Jewel Services)
# =============================================================================


@dataclass
class DifferanceIntegration:
    """
    Integration helper for Crown Jewel services.

    Provides a clean API for services that want to record traces.

    Example:
        class BrainPersistence:
            def __init__(self):
                self._differance = DifferanceIntegration("brain")

            async def capture(self, content: str, ...) -> CaptureResult:
                result = await self._do_capture(content, ...)

                await self._differance.record(
                    operation="capture",
                    inputs=(content[:50],),
                    output=result.crystal_id,
                    context=f"Captured {source_type} to brain",
                    alternatives=[
                        self._differance.alternative(
                            "categorize_first", ("auto-tag",), "Could auto-categorize"
                        )
                    ] if should_suggest_categorize else None,
                )

                return result
    """

    jewel_name: str
    """Name of the Crown Jewel (for trace context)."""

    _enabled: bool = True
    """Whether tracing is enabled."""

    def enable(self) -> None:
        """Enable trace recording."""
        self._enabled = True

    def disable(self) -> None:
        """Disable trace recording."""
        self._enabled = False

    async def record(
        self,
        operation: str,
        inputs: tuple[Any, ...],
        output: Any,
        context: str = "",
        alternatives: list["Alternative"] | None = None,
    ) -> str | None:
        """
        Record a trace asynchronously.

        Args:
            operation: The operation name
            inputs: Tuple of input values
            output: The output value
            context: Human-readable context string
            alternatives: List of Alternative objects

        Returns:
            The trace ID if recorded, None if disabled or no store
        """
        if not self._enabled:
            return None

        full_context = f"[{self.jewel_name}] {context}" if context else f"[{self.jewel_name}]"
        return await record_trace(
            operation=operation,
            inputs=inputs,
            output=output,
            context=full_context,
            alternatives=alternatives,
        )

    def record_sync(
        self,
        operation: str,
        inputs: tuple[Any, ...],
        output: Any,
        context: str = "",
        alternatives: list["Alternative"] | None = None,
    ) -> str | None:
        """
        Record a trace from sync code.

        Uses Pattern 6 (Async-Safe Event Emission).
        """
        if not self._enabled:
            return None

        full_context = f"[{self.jewel_name}] {context}" if context else f"[{self.jewel_name}]"
        return record_trace_sync(
            operation=operation,
            inputs=inputs,
            output=output,
            context=full_context,
            alternatives=alternatives,
        )

    def alternative(
        self,
        operation: str,
        inputs: tuple[Any, ...],
        reason: str,
    ) -> "Alternative":
        """
        Create an Alternative for recording.

        Convenience method that imports Alternative internally.
        """
        from .trace import Alternative

        return Alternative(operation=operation, inputs=inputs, reason_rejected=reason)

    def context(self, operation: str) -> TraceContext:
        """
        Create a trace context for nested traces.

        Example:
            async with self._differance.context("process_batch") as ctx:
                for item in items:
                    await self._differance.record(...)
        """
        return get_trace_context(f"{self.jewel_name}.{operation}")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Context functions
    "get_current_trace_id",
    "set_current_trace_id",
    "get_differance_store",
    "set_differance_store",
    "get_trace_monoid",
    "set_trace_monoid",
    # Correlation ID (Phase 6A)
    "get_correlation_id",
    "set_correlation_id",
    # Trace buffer
    "get_trace_buffer",
    "clear_trace_buffer",
    # Buffer isolation (Phase 6A - for testing)
    "create_isolated_buffer",
    "reset_isolated_buffer",
    # Trace context
    "TraceContext",
    "get_trace_context",
    # Record functions
    "record_trace",
    "record_trace_sync",
    # Integration class
    "DifferanceIntegration",
]
