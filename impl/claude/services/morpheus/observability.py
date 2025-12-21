"""
Morpheus Observability: OpenTelemetry spans and metrics for LLM gateway.

Provides:
1. OTEL Spans: morpheus.complete, morpheus.stream
2. Metrics: Counters, histograms for LLM operations
3. Context managers for tracing

Design Principles (from services/chat/observability.py):
1. Observation doesn't mutate - outputs unchanged
2. Observation doesn't block - async, non-blocking
3. Observation doesn't leak - data stays within boundaries
4. Observation enables - self-knowledge enables improvement

Usage:
    from services.morpheus.observability import (
        MorpheusTelemetry,
        record_completion,
        get_morpheus_metrics_summary,
    )

    # Use with gateway
    telemetry = MorpheusTelemetry()
    async with telemetry.trace_completion(request, archetype) as span:
        response = await gateway.complete(request)
        span.set_attribute("morpheus.tokens_out", response.usage.completion_tokens)
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
    from .types import ChatRequest, ChatResponse


# =============================================================================
# Tracer and Meter Singletons
# =============================================================================

_tracer: Tracer | None = None
_meter: metrics.Meter | None = None


def get_morpheus_tracer() -> Tracer:
    """Get the morpheus tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.morpheus", "0.1.0")
    return _tracer


def get_morpheus_meter() -> metrics.Meter:
    """Get the morpheus meter, creating if needed."""
    global _meter
    if _meter is None:
        _meter = metrics.get_meter("kgents.morpheus", "0.1.0")
    return _meter


# =============================================================================
# Span Attribute Constants
# =============================================================================

# Request attributes
ATTR_REQUEST_ID = "morpheus.request_id"
ATTR_MODEL = "morpheus.model"
ATTR_PROVIDER = "morpheus.provider"
ATTR_ARCHETYPE = "morpheus.observer_archetype"
ATTR_STREAMING = "morpheus.streaming"

# Token attributes
ATTR_TOKENS_IN = "morpheus.tokens_in"
ATTR_TOKENS_OUT = "morpheus.tokens_out"
ATTR_TOKENS_TOTAL = "morpheus.tokens_total"

# Timing attributes
ATTR_DURATION_MS = "morpheus.duration_ms"
ATTR_TIME_TO_FIRST_TOKEN_MS = "morpheus.time_to_first_token_ms"

# Cost attributes
ATTR_ESTIMATED_COST = "morpheus.estimated_cost_usd"

# Rate limit attributes
ATTR_RATE_LIMIT_REMAINING = "morpheus.rate_limit_remaining"


# =============================================================================
# Metrics Instruments
# =============================================================================

_instruments_initialized = False


def _ensure_instruments() -> tuple[Any, ...]:
    """Lazy initialization of metrics instruments."""
    global _instruments_initialized
    meter = get_morpheus_meter()

    if not _instruments_initialized:
        _instruments_initialized = True

    # Counters
    requests_counter = meter.create_counter(
        "morpheus_requests_total",
        description="Total number of LLM requests",
        unit="1",
    )

    tokens_counter = meter.create_counter(
        "morpheus_tokens_total",
        description="Total tokens consumed",
        unit="1",
    )

    errors_counter = meter.create_counter(
        "morpheus_errors_total",
        description="Total LLM request errors",
        unit="1",
    )

    rate_limit_counter = meter.create_counter(
        "morpheus_rate_limits_total",
        description="Total rate limit hits",
        unit="1",
    )

    # Histograms
    duration_histogram = meter.create_histogram(
        "morpheus_request_duration_seconds",
        description="Duration of LLM requests",
        unit="s",
    )

    tokens_per_request_histogram = meter.create_histogram(
        "morpheus_tokens_per_request",
        description="Tokens per request",
        unit="1",
    )

    time_to_first_token_histogram = meter.create_histogram(
        "morpheus_time_to_first_token_seconds",
        description="Time to first token for streaming requests",
        unit="s",
    )

    return (
        requests_counter,
        tokens_counter,
        errors_counter,
        rate_limit_counter,
        duration_histogram,
        tokens_per_request_histogram,
        time_to_first_token_histogram,
    )


# =============================================================================
# In-Memory Metrics State
# =============================================================================


@dataclass
class MorpheusMetricsState:
    """
    Thread-safe in-memory metrics state for summaries.

    Teaching:
        gotcha: This is SEPARATE from OTEL counters. reset_morpheus_metrics()
                clears this state but OTEL counters keep incrementing.
                (Evidence: test_observability.py - if exists)

        gotcha: The _lock is per-instance but the global _state is a singleton.
                All record_* functions share this lock—contention possible at scale.
                (Evidence: persistence.py record_completion calls)
    """

    total_requests: int = 0
    total_streaming: int = 0
    total_errors: int = 0
    total_rate_limits: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_duration_s: float = 0.0
    total_cost_usd: float = 0.0

    # By model
    requests_by_model: dict[str, int] = field(default_factory=dict)
    tokens_by_model: dict[str, tuple[int, int]] = field(default_factory=dict)

    # By archetype
    requests_by_archetype: dict[str, int] = field(default_factory=dict)

    # By provider
    requests_by_provider: dict[str, int] = field(default_factory=dict)

    _lock: Lock = field(default_factory=Lock)


_state = MorpheusMetricsState()


# =============================================================================
# Recording Functions
# =============================================================================


def record_completion(
    model: str,
    provider: str,
    archetype: str,
    duration_s: float,
    tokens_in: int,
    tokens_out: int,
    success: bool,
    streaming: bool = False,
    estimated_cost_usd: float = 0.0,
) -> None:
    """
    Record metrics for a completed LLM request.

    Args:
        model: Model name (e.g., "claude-sonnet-4-20250514")
        provider: Provider name (e.g., "claude-cli")
        archetype: Observer archetype
        duration_s: Request duration in seconds
        tokens_in: Input tokens consumed
        tokens_out: Output tokens generated
        success: Whether the request succeeded
        streaming: Whether this was a streaming request
        estimated_cost_usd: Estimated cost for this request
    """
    labels = {
        "model": model,
        "provider": provider,
        "archetype": archetype,
        "streaming": str(streaming),
    }

    (
        requests_counter,
        tokens_counter,
        errors_counter,
        _rate_limit,
        duration_histogram,
        tokens_per_request_histogram,
        _ttft,
    ) = _ensure_instruments()

    # Record to OTEL
    requests_counter.add(1, labels)
    duration_histogram.record(duration_s, labels)
    tokens_per_request_histogram.record(tokens_in + tokens_out, labels)

    if tokens_in > 0:
        tokens_counter.add(tokens_in, {**labels, "direction": "in"})
    if tokens_out > 0:
        tokens_counter.add(tokens_out, {**labels, "direction": "out"})

    if not success:
        errors_counter.add(1, labels)

    # Update in-memory state
    with _state._lock:
        _state.total_requests += 1
        if streaming:
            _state.total_streaming += 1
        _state.total_duration_s += duration_s
        _state.total_tokens_in += tokens_in
        _state.total_tokens_out += tokens_out
        _state.total_cost_usd += estimated_cost_usd

        _state.requests_by_model[model] = _state.requests_by_model.get(model, 0) + 1
        _state.requests_by_archetype[archetype] = _state.requests_by_archetype.get(archetype, 0) + 1
        _state.requests_by_provider[provider] = _state.requests_by_provider.get(provider, 0) + 1

        current_tokens = _state.tokens_by_model.get(model, (0, 0))
        _state.tokens_by_model[model] = (
            current_tokens[0] + tokens_in,
            current_tokens[1] + tokens_out,
        )

        if not success:
            _state.total_errors += 1


def record_rate_limit(archetype: str, model: str = "unknown") -> None:
    """Record a rate limit hit."""
    labels = {"archetype": archetype, "model": model}

    instruments = _ensure_instruments()
    rate_limit_counter = instruments[3]
    rate_limit_counter.add(1, labels)

    with _state._lock:
        _state.total_rate_limits += 1


def record_time_to_first_token(
    model: str,
    provider: str,
    ttft_s: float,
) -> None:
    """Record time to first token for streaming requests."""
    labels = {"model": model, "provider": provider}

    instruments = _ensure_instruments()
    ttft_histogram = instruments[6]
    ttft_histogram.record(ttft_s, labels)


# =============================================================================
# MorpheusTelemetry: Tracing Context Managers
# =============================================================================


@dataclass
class MorpheusTelemetry:
    """
    Telemetry wrapper for Morpheus gateway operations.

    Provides context managers for tracing:
    - Completion requests
    - Streaming requests

    Teaching:
        gotcha: The context managers are async but use sync tracer.start_as_current_span.
                This is intentional—OTEL spans are sync, only our I/O is async.
                (Evidence: persistence.py::complete uses trace_completion)

        gotcha: Duration is recorded in the finally block, so it includes error
                handling time. For precise LLM latency, check provider metrics.
                (Evidence: test_observability.py::test_tracing - if exists)
    """

    span_prefix: str = "morpheus"

    @asynccontextmanager
    async def trace_completion(
        self,
        request: "ChatRequest",
        archetype: str,
        provider: str = "unknown",
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace a completion request.

        Args:
            request: Chat completion request
            archetype: Observer archetype
            provider: Provider name
            **extra_attributes: Additional span attributes

        Yields:
            The request span
        """
        tracer = get_morpheus_tracer()

        attributes = {
            ATTR_MODEL: request.model,
            ATTR_ARCHETYPE: archetype,
            ATTR_PROVIDER: provider,
            ATTR_STREAMING: False,
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.complete",
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
                duration_s = time.perf_counter() - start_time
                span.set_attribute(ATTR_DURATION_MS, duration_s * 1000)

    @asynccontextmanager
    async def trace_stream(
        self,
        request: "ChatRequest",
        archetype: str,
        provider: str = "unknown",
        **extra_attributes: Any,
    ) -> AsyncIterator[Span]:
        """
        Trace a streaming request.

        Args:
            request: Chat completion request
            archetype: Observer archetype
            provider: Provider name
            **extra_attributes: Additional span attributes

        Yields:
            The request span
        """
        tracer = get_morpheus_tracer()

        attributes = {
            ATTR_MODEL: request.model,
            ATTR_ARCHETYPE: archetype,
            ATTR_PROVIDER: provider,
            ATTR_STREAMING: True,
            **extra_attributes,
        }

        with tracer.start_as_current_span(
            f"{self.span_prefix}.stream",
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
                duration_s = time.perf_counter() - start_time
                span.set_attribute(ATTR_DURATION_MS, duration_s * 1000)


# =============================================================================
# Summary Functions
# =============================================================================


def get_morpheus_metrics_summary() -> dict[str, Any]:
    """
    Get a summary of current Morpheus metrics.

    Returns:
        Dict with aggregated metrics for display
    """
    with _state._lock:
        avg_duration = (
            _state.total_duration_s / _state.total_requests if _state.total_requests > 0 else 0.0
        )

        avg_tokens_per_request = (
            (_state.total_tokens_in + _state.total_tokens_out) / _state.total_requests
            if _state.total_requests > 0
            else 0.0
        )

        # Top models by request count
        top_models = sorted(
            _state.requests_by_model.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "total_requests": _state.total_requests,
            "total_streaming": _state.total_streaming,
            "total_errors": _state.total_errors,
            "total_rate_limits": _state.total_rate_limits,
            "error_rate": _state.total_errors / _state.total_requests
            if _state.total_requests > 0
            else 0.0,
            "total_tokens_in": _state.total_tokens_in,
            "total_tokens_out": _state.total_tokens_out,
            "total_tokens": _state.total_tokens_in + _state.total_tokens_out,
            "avg_tokens_per_request": round(avg_tokens_per_request, 1),
            "total_duration_s": round(_state.total_duration_s, 2),
            "avg_request_duration_s": round(avg_duration, 3),
            "total_cost_usd": round(_state.total_cost_usd, 6),
            "top_models": dict(top_models),
            "requests_by_archetype": dict(_state.requests_by_archetype),
            "requests_by_provider": dict(_state.requests_by_provider),
        }


def reset_morpheus_metrics() -> None:
    """
    Reset in-memory metrics state.

    Useful for testing or starting fresh.
    Note: This only resets in-memory state, not OTEL counters.
    """
    global _state
    with _state._lock:
        _state.total_requests = 0
        _state.total_streaming = 0
        _state.total_errors = 0
        _state.total_rate_limits = 0
        _state.total_tokens_in = 0
        _state.total_tokens_out = 0
        _state.total_duration_s = 0.0
        _state.total_cost_usd = 0.0
        _state.requests_by_model.clear()
        _state.tokens_by_model.clear()
        _state.requests_by_archetype.clear()
        _state.requests_by_provider.clear()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Telemetry class
    "MorpheusTelemetry",
    # Recording functions
    "record_completion",
    "record_rate_limit",
    "record_time_to_first_token",
    # Summary functions
    "get_morpheus_metrics_summary",
    "reset_morpheus_metrics",
    # Tracer/meter access
    "get_morpheus_tracer",
    "get_morpheus_meter",
    # Attribute constants
    "ATTR_REQUEST_ID",
    "ATTR_MODEL",
    "ATTR_PROVIDER",
    "ATTR_ARCHETYPE",
    "ATTR_STREAMING",
    "ATTR_TOKENS_IN",
    "ATTR_TOKENS_OUT",
    "ATTR_TOKENS_TOTAL",
    "ATTR_DURATION_MS",
    "ATTR_TIME_TO_FIRST_TOKEN_MS",
    "ATTR_ESTIMATED_COST",
    "ATTR_RATE_LIMIT_REMAINING",
]
