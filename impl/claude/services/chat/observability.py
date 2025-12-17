"""
Chat Observability: OpenTelemetry spans and metrics for chat sessions.

Phase 5 of the Chat Protocol implementation (spec/protocols/chat.md Part IX).

Provides:
1. OTEL Spans: chat.session, chat.turn, chat.context_render, chat.llm_call
2. Metrics: Counters, histograms, and gauges for chat operations
3. Integration with existing ChatSession via decorators

Design Principles (from telemetry.py):
1. Observation doesn't mutate - outputs unchanged
2. Observation doesn't block - async, non-blocking
3. Observation doesn't leak - data stays within boundaries
4. Observation enables - self-knowledge enables improvement

Usage:
    from services.chat.observability import (
        ChatTelemetry,
        record_turn,
        record_session_event,
        get_chat_metrics_summary,
    )

    # Use with ChatSession
    telemetry = ChatTelemetry()
    async with telemetry.trace_turn(session, message) as span:
        response = await session.send(message)
        span.set_attribute("chat.response_length", len(response))

    # Record metrics manually
    record_turn(
        node_path="self.soul",
        turn_number=3,
        duration_s=1.2,
        tokens_in=100,
        tokens_out=250,
        success=True,
    )
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Any, AsyncIterator

from opentelemetry import metrics, trace
from opentelemetry.trace import Span, Status, StatusCode, Tracer

if TYPE_CHECKING:
    from .session import ChatSession


# =============================================================================
# Tracer and Meter Singletons
# =============================================================================

_tracer: Tracer | None = None
_meter: metrics.Meter | None = None


def get_chat_tracer() -> Tracer:
    """Get the chat tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.chat", "0.1.0")
    return _tracer


def get_chat_meter() -> metrics.Meter:
    """Get the chat meter, creating if needed."""
    global _meter
    if _meter is None:
        _meter = metrics.get_meter("kgents.chat", "0.1.0")
    return _meter


# =============================================================================
# Span Attribute Constants
# =============================================================================

# Session attributes
ATTR_SESSION_ID = "chat.session_id"
ATTR_NODE_PATH = "chat.node_path"
ATTR_OBSERVER_ID = "chat.observer_id"
ATTR_SESSION_STATE = "chat.session_state"

# Turn attributes
ATTR_TURN_NUMBER = "chat.turn_number"
ATTR_TURN_DURATION_MS = "chat.turn_duration_ms"
ATTR_MESSAGE_LENGTH = "chat.message_length"
ATTR_RESPONSE_LENGTH = "chat.response_length"

# Token attributes
ATTR_TOKENS_IN = "chat.tokens_in"
ATTR_TOKENS_OUT = "chat.tokens_out"
ATTR_TOKENS_TOTAL = "chat.tokens_total"

# Context attributes
ATTR_CONTEXT_SIZE = "chat.context_size"
ATTR_CONTEXT_UTILIZATION = "chat.context_utilization"
ATTR_CONTEXT_STRATEGY = "chat.context_strategy"

# Model attributes
ATTR_MODEL = "chat.model"
ATTR_ESTIMATED_COST = "chat.estimated_cost_usd"

# Entropy attributes
ATTR_ENTROPY_BEFORE = "chat.entropy_before"
ATTR_ENTROPY_AFTER = "chat.entropy_after"


# =============================================================================
# Metrics Instruments
# =============================================================================

_instruments_initialized = False


def _ensure_instruments() -> tuple[Any, ...]:
    """Lazy initialization of metrics instruments."""
    global _instruments_initialized
    meter = get_chat_meter()

    if not _instruments_initialized:
        _instruments_initialized = True

    # Counters
    turns_counter = meter.create_counter(
        "chat_turns_total",
        description="Total number of chat turns",
        unit="1",
    )

    sessions_counter = meter.create_counter(
        "chat_sessions_total",
        description="Total number of chat sessions",
        unit="1",
    )

    tokens_counter = meter.create_counter(
        "chat_tokens_total",
        description="Total tokens consumed in chat sessions",
        unit="1",
    )

    errors_counter = meter.create_counter(
        "chat_errors_total",
        description="Total chat errors",
        unit="1",
    )

    # Histograms
    turn_duration_histogram = meter.create_histogram(
        "chat_turn_duration_seconds",
        description="Duration of chat turns",
        unit="s",
    )

    tokens_per_turn_histogram = meter.create_histogram(
        "chat_tokens_per_turn",
        description="Tokens per chat turn",
        unit="1",
    )

    context_utilization_histogram = meter.create_histogram(
        "chat_context_utilization",
        description="Context window utilization ratio",
        unit="1",
    )

    return (
        turns_counter,
        sessions_counter,
        tokens_counter,
        errors_counter,
        turn_duration_histogram,
        tokens_per_turn_histogram,
        context_utilization_histogram,
    )


# =============================================================================
# In-Memory Metrics State (for summaries)
# =============================================================================


@dataclass
class ChatMetricsState:
    """Thread-safe in-memory metrics state for chat summaries."""

    total_turns: int = 0
    total_sessions: int = 0
    total_errors: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_duration_s: float = 0.0
    total_cost_usd: float = 0.0

    # Breakdowns
    turns_by_node: dict[str, int] = field(default_factory=dict)
    sessions_by_node: dict[str, int] = field(default_factory=dict)
    errors_by_node: dict[str, int] = field(default_factory=dict)
    tokens_by_node: dict[str, tuple[int, int]] = field(default_factory=dict)

    # Active sessions (gauge)
    active_sessions_by_node: dict[str, int] = field(default_factory=dict)

    _lock: Lock = field(default_factory=Lock)


_state = ChatMetricsState()


# =============================================================================
# Recording Functions
# =============================================================================


def record_turn(
    node_path: str,
    turn_number: int,
    duration_s: float,
    tokens_in: int,
    tokens_out: int,
    success: bool,
    context_utilization: float = 0.0,
    estimated_cost_usd: float = 0.0,
    observer_id: str = "anonymous",
) -> None:
    """
    Record metrics for a completed chat turn.

    Args:
        node_path: AGENTESE path (e.g., "self.soul", "world.town.citizen.elara")
        turn_number: Turn number in session
        duration_s: Turn duration in seconds
        tokens_in: Input tokens consumed
        tokens_out: Output tokens generated
        success: Whether the turn succeeded
        context_utilization: Context window utilization (0.0-1.0)
        estimated_cost_usd: Estimated cost for this turn
        observer_id: Observer identifier
    """
    labels = {
        "node_path": node_path,
        "observer_archetype": observer_id.split(":")[0] if ":" in observer_id else "user",
    }

    # Get instruments
    (
        turns_counter,
        _sessions,
        tokens_counter,
        errors_counter,
        turn_duration_histogram,
        tokens_per_turn_histogram,
        context_utilization_histogram,
    ) = _ensure_instruments()

    # Record to OTEL
    turns_counter.add(1, labels)
    turn_duration_histogram.record(duration_s, labels)
    tokens_per_turn_histogram.record(tokens_in + tokens_out, labels)
    context_utilization_histogram.record(context_utilization, labels)

    if tokens_in > 0:
        tokens_counter.add(tokens_in, {**labels, "direction": "in"})
    if tokens_out > 0:
        tokens_counter.add(tokens_out, {**labels, "direction": "out"})

    if not success:
        errors_counter.add(1, labels)

    # Update in-memory state
    with _state._lock:
        _state.total_turns += 1
        _state.total_duration_s += duration_s
        _state.total_tokens_in += tokens_in
        _state.total_tokens_out += tokens_out
        _state.total_cost_usd += estimated_cost_usd

        _state.turns_by_node[node_path] = _state.turns_by_node.get(node_path, 0) + 1

        current_tokens = _state.tokens_by_node.get(node_path, (0, 0))
        _state.tokens_by_node[node_path] = (
            current_tokens[0] + tokens_in,
            current_tokens[1] + tokens_out,
        )

        if not success:
            _state.total_errors += 1
            _state.errors_by_node[node_path] = (
                _state.errors_by_node.get(node_path, 0) + 1
            )


def record_session_event(
    node_path: str,
    event: str,
    observer_id: str = "anonymous",
) -> None:
    """
    Record a session lifecycle event.

    Args:
        node_path: AGENTESE path
        event: Event type ("started", "ended", "collapsed", "reset")
        observer_id: Observer identifier
    """
    labels = {
        "node_path": node_path,
        "outcome": event,
    }

    (
        _turns,
        sessions_counter,
        *_rest,
    ) = _ensure_instruments()

    if event == "started":
        sessions_counter.add(1, labels)

        with _state._lock:
            _state.total_sessions += 1
            _state.sessions_by_node[node_path] = (
                _state.sessions_by_node.get(node_path, 0) + 1
            )
            _state.active_sessions_by_node[node_path] = (
                _state.active_sessions_by_node.get(node_path, 0) + 1
            )

    elif event in ("ended", "collapsed"):
        with _state._lock:
            current = _state.active_sessions_by_node.get(node_path, 0)
            _state.active_sessions_by_node[node_path] = max(0, current - 1)


def record_error(
    node_path: str,
    error_type: str,
    observer_id: str = "anonymous",
) -> None:
    """
    Record a chat error.

    Args:
        node_path: AGENTESE path
        error_type: Type of error
        observer_id: Observer identifier
    """
    labels = {
        "node_path": node_path,
        "error_type": error_type,
    }

    # errors_counter is index 3 in the 7-tuple
    instruments = _ensure_instruments()
    errors_counter = instruments[3]
    errors_counter.add(1, labels)

    with _state._lock:
        _state.total_errors += 1
        _state.errors_by_node[node_path] = (
            _state.errors_by_node.get(node_path, 0) + 1
        )


# =============================================================================
# ChatTelemetry: Tracing Context Managers
# =============================================================================


@dataclass
class ChatTelemetry:
    """
    Telemetry wrapper for ChatSession operations.

    Provides context managers for tracing:
    - Full sessions
    - Individual turns
    - Context rendering
    - LLM calls

    Example:
        telemetry = ChatTelemetry()

        # Trace a session
        async with telemetry.trace_session(session) as span:
            # Multiple turns traced under this session span
            async with telemetry.trace_turn(session, message) as turn_span:
                response = await session.send(message)

        # Or trace just a turn
        async with telemetry.trace_turn(session, message) as span:
            response = await session.send(message)
    """

    span_prefix: str = "chat"

    @asynccontextmanager
    async def trace_session(
        self,
        session: "ChatSession",
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace a full chat session.

        Args:
            session: ChatSession instance
            **extra_attributes: Additional span attributes

        Yields:
            The session span
        """
        tracer = get_chat_tracer()

        observer_id = getattr(session.observer, "id", "unknown")

        attributes = {
            ATTR_SESSION_ID: session.session_id,
            ATTR_NODE_PATH: session.node_path,
            ATTR_OBSERVER_ID: str(observer_id),
            ATTR_SESSION_STATE: session.state.value,
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.session",
            attributes=attributes,
        ) as span:
            start_time = time.perf_counter()
            record_session_event(session.node_path, "started", str(observer_id))

            try:
                yield span
                span.set_status(Status(StatusCode.OK))
                # Update final state
                span.set_attribute(ATTR_SESSION_STATE, session.state.value)
                span.set_attribute("chat.total_turns", session.turn_count)
                span.set_attribute("chat.total_tokens", session.budget.total_tokens)

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                record_error(session.node_path, type(e).__name__, str(observer_id))
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("chat.session_duration_ms", duration_ms)
                record_session_event(session.node_path, "ended", str(observer_id))

    @asynccontextmanager
    async def trace_turn(
        self,
        session: "ChatSession",
        message: str,
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace a single chat turn.

        Args:
            session: ChatSession instance
            message: User message for this turn
            **extra_attributes: Additional span attributes

        Yields:
            The turn span
        """
        tracer = get_chat_tracer()

        observer_id = getattr(session.observer, "id", "unknown")
        turn_number = session.turn_count + 1
        entropy_before = session.entropy

        attributes = {
            ATTR_SESSION_ID: session.session_id,
            ATTR_NODE_PATH: session.node_path,
            ATTR_TURN_NUMBER: turn_number,
            ATTR_MESSAGE_LENGTH: len(message),
            ATTR_ENTROPY_BEFORE: entropy_before,
            ATTR_CONTEXT_SIZE: session._get_context_size(),
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.turn",
            attributes=attributes,
        ) as span:
            start_time = time.perf_counter()

            try:
                yield span
                span.set_status(Status(StatusCode.OK))

                # Capture post-turn metrics
                duration_s = time.perf_counter() - start_time

                # Get the last turn if available
                if session._turns:
                    last_turn = session._turns[-1]
                    tokens_in = last_turn.tokens_in
                    tokens_out = last_turn.tokens_out
                    response_length = len(last_turn.assistant_response.content)
                else:
                    tokens_in = 0
                    tokens_out = 0
                    response_length = 0

                span.set_attribute(ATTR_TOKENS_IN, tokens_in)
                span.set_attribute(ATTR_TOKENS_OUT, tokens_out)
                span.set_attribute(ATTR_TOKENS_TOTAL, tokens_in + tokens_out)
                span.set_attribute(ATTR_RESPONSE_LENGTH, response_length)
                span.set_attribute(ATTR_ENTROPY_AFTER, session.entropy)
                span.set_attribute(
                    ATTR_CONTEXT_UTILIZATION, session.get_context_utilization()
                )
                span.set_attribute(ATTR_TURN_DURATION_MS, duration_s * 1000)

                # Record metrics
                record_turn(
                    node_path=session.node_path,
                    turn_number=turn_number,
                    duration_s=duration_s,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    success=True,
                    context_utilization=session.get_context_utilization(),
                    estimated_cost_usd=session.budget.estimated_cost_usd / max(1, session.turn_count),
                    observer_id=str(observer_id),
                )

            except Exception as e:
                duration_s = time.perf_counter() - start_time
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

                record_turn(
                    node_path=session.node_path,
                    turn_number=turn_number,
                    duration_s=duration_s,
                    tokens_in=0,
                    tokens_out=0,
                    success=False,
                    observer_id=str(observer_id),
                )
                raise

    @asynccontextmanager
    async def trace_context_render(
        self,
        session: "ChatSession",
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace context window rendering.

        Args:
            session: ChatSession instance
            **extra_attributes: Additional span attributes

        Yields:
            The context render span
        """
        tracer = get_chat_tracer()

        attributes = {
            ATTR_SESSION_ID: session.session_id,
            ATTR_CONTEXT_SIZE: session._get_context_size(),
            ATTR_CONTEXT_STRATEGY: session.config.context_strategy.value,
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.context_render",
            attributes=attributes,
        ) as span:
            start_time = time.perf_counter()

            try:
                yield span
                span.set_status(Status(StatusCode.OK))
                span.set_attribute(
                    ATTR_CONTEXT_UTILIZATION, session.get_context_utilization()
                )

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("chat.context_render_duration_ms", duration_ms)

    @asynccontextmanager
    async def trace_llm_call(
        self,
        session: "ChatSession",
        model: str = "unknown",
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace an LLM API call within a turn.

        Args:
            session: ChatSession instance
            model: Model name
            **extra_attributes: Additional span attributes

        Yields:
            The LLM call span
        """
        tracer = get_chat_tracer()

        attributes = {
            ATTR_SESSION_ID: session.session_id,
            ATTR_MODEL: model,
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.llm_call",
            attributes=attributes,
        ) as span:
            start_time = time.perf_counter()

            try:
                yield span
                span.set_status(Status(StatusCode.OK))

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("chat.llm_call_duration_ms", duration_ms)


# =============================================================================
# Utility Functions for Manual Tracing
# =============================================================================


def create_turn_span(
    session_id: str,
    node_path: str,
    turn_number: int,
    **attributes: Any,
) -> Span:
    """
    Create a child span for a chat turn.

    Use this when you need manual control over span lifecycle.

    Args:
        session_id: Session identifier
        node_path: AGENTESE path
        turn_number: Turn number
        **attributes: Additional attributes

    Returns:
        Started span (use as context manager)
    """
    tracer = get_chat_tracer()
    return tracer.start_as_current_span(
        "chat.turn",
        attributes={
            ATTR_SESSION_ID: session_id,
            ATTR_NODE_PATH: node_path,
            ATTR_TURN_NUMBER: turn_number,
            **attributes,
        },
    )  # type: ignore[return-value]


def add_turn_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """
    Add an event to the current turn span.

    Events are timestamped annotations, useful for marking
    significant points within a turn (e.g., "context_compressed",
    "memory_injected", "response_started").

    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes or {})


def set_turn_attribute(key: str, value: Any) -> None:
    """
    Set an attribute on the current span.

    Args:
        key: Attribute key (will be prefixed with "chat." if not already)
        value: Attribute value
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        full_key = key if key.startswith("chat.") else f"chat.{key}"
        span.set_attribute(full_key, value)


# =============================================================================
# Summary Functions
# =============================================================================


def get_chat_metrics_summary() -> dict[str, Any]:
    """
    Get a summary of current chat metrics.

    Returns:
        Dict with aggregated chat metrics for display
    """
    with _state._lock:
        avg_duration = (
            _state.total_duration_s / _state.total_turns
            if _state.total_turns > 0
            else 0.0
        )

        avg_tokens_per_turn = (
            (_state.total_tokens_in + _state.total_tokens_out) / _state.total_turns
            if _state.total_turns > 0
            else 0.0
        )

        # Top nodes by turn count
        top_nodes = sorted(
            _state.turns_by_node.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "total_turns": _state.total_turns,
            "total_sessions": _state.total_sessions,
            "total_errors": _state.total_errors,
            "error_rate": _state.total_errors / _state.total_turns
            if _state.total_turns > 0
            else 0.0,
            "total_tokens_in": _state.total_tokens_in,
            "total_tokens_out": _state.total_tokens_out,
            "total_tokens": _state.total_tokens_in + _state.total_tokens_out,
            "avg_tokens_per_turn": round(avg_tokens_per_turn, 1),
            "total_duration_s": round(_state.total_duration_s, 2),
            "avg_turn_duration_s": round(avg_duration, 3),
            "total_cost_usd": round(_state.total_cost_usd, 6),
            "active_sessions": dict(_state.active_sessions_by_node),
            "top_nodes_by_turns": dict(top_nodes),
            "sessions_by_node": dict(_state.sessions_by_node),
        }


def get_active_session_count(node_path: str | None = None) -> int:
    """
    Get count of active sessions.

    Args:
        node_path: Optional filter by node path

    Returns:
        Count of active sessions
    """
    with _state._lock:
        if node_path is None:
            return sum(_state.active_sessions_by_node.values())
        return _state.active_sessions_by_node.get(node_path, 0)


def reset_chat_metrics() -> None:
    """
    Reset in-memory chat metrics state.

    Useful for testing or starting fresh.
    Note: This only resets in-memory state, not OTEL counters.
    """
    global _state
    with _state._lock:
        _state.total_turns = 0
        _state.total_sessions = 0
        _state.total_errors = 0
        _state.total_tokens_in = 0
        _state.total_tokens_out = 0
        _state.total_duration_s = 0.0
        _state.total_cost_usd = 0.0
        _state.turns_by_node.clear()
        _state.sessions_by_node.clear()
        _state.errors_by_node.clear()
        _state.tokens_by_node.clear()
        _state.active_sessions_by_node.clear()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Telemetry class
    "ChatTelemetry",
    # Recording functions
    "record_turn",
    "record_session_event",
    "record_error",
    # Summary functions
    "get_chat_metrics_summary",
    "get_active_session_count",
    "reset_chat_metrics",
    # Manual tracing
    "create_turn_span",
    "add_turn_event",
    "set_turn_attribute",
    # Tracer/meter access
    "get_chat_tracer",
    "get_chat_meter",
    # Attribute constants
    "ATTR_SESSION_ID",
    "ATTR_NODE_PATH",
    "ATTR_OBSERVER_ID",
    "ATTR_SESSION_STATE",
    "ATTR_TURN_NUMBER",
    "ATTR_TURN_DURATION_MS",
    "ATTR_MESSAGE_LENGTH",
    "ATTR_RESPONSE_LENGTH",
    "ATTR_TOKENS_IN",
    "ATTR_TOKENS_OUT",
    "ATTR_TOKENS_TOTAL",
    "ATTR_CONTEXT_SIZE",
    "ATTR_CONTEXT_UTILIZATION",
    "ATTR_CONTEXT_STRATEGY",
    "ATTR_MODEL",
    "ATTR_ESTIMATED_COST",
    "ATTR_ENTROPY_BEFORE",
    "ATTR_ENTROPY_AFTER",
]
