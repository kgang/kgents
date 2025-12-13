"""
AGENTESE Metrics: Prometheus-compatible metrics for AGENTESE operations.

Provides counters and histograms for tracking AGENTESE invocations,
enabling monitoring and alerting through Prometheus/Grafana.

Metrics exposed:
- agentese_invocations_total: Counter of total invocations by path/context
- agentese_tokens_total: Counter of tokens consumed (in/out)
- agentese_errors_total: Counter of invocation errors
- agentese_invoke_duration_seconds: Histogram of invocation durations

Usage:
    from protocols.agentese.metrics import record_invocation, get_metrics_summary

    # Record an invocation (called by TelemetryMiddleware)
    record_invocation(
        path="self.soul.challenge",
        context="self",
        duration_s=0.125,
        success=True,
        tokens_in=100,
        tokens_out=50,
    )

    # Get current metrics summary
    summary = get_metrics_summary()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from opentelemetry import metrics

# === Meter Singleton ===

_meter = metrics.get_meter("kgents.agentese", "0.1.0")

# === Counters ===

_invoke_counter = _meter.create_counter(
    "agentese_invocations_total",
    description="Total number of AGENTESE invocations",
    unit="1",
)

_token_counter = _meter.create_counter(
    "agentese_tokens_total",
    description="Total tokens consumed by AGENTESE invocations",
    unit="1",
)

_error_counter = _meter.create_counter(
    "agentese_errors_total",
    description="Total AGENTESE invocation errors",
    unit="1",
)

# === Histograms ===

_duration_histogram = _meter.create_histogram(
    "agentese_invoke_duration_seconds",
    description="Duration of AGENTESE invocations",
    unit="s",
)

# === In-Memory Aggregation (for summary) ===


@dataclass
class MetricsState:
    """Thread-safe in-memory metrics state for summaries."""

    total_invocations: int = 0
    total_errors: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_duration_s: float = 0.0
    invocations_by_context: dict[str, int] = field(default_factory=dict)
    invocations_by_path: dict[str, int] = field(default_factory=dict)
    errors_by_path: dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)


_state = MetricsState()


# === Recording Functions ===


def record_invocation(
    path: str,
    context: str,
    duration_s: float,
    success: bool,
    tokens_in: int = 0,
    tokens_out: int = 0,
) -> None:
    """
    Record metrics for an AGENTESE invocation.

    This function is called by TelemetryMiddleware after each invocation.
    It updates both OpenTelemetry metrics (for export) and in-memory state
    (for summaries).

    Args:
        path: Full AGENTESE path (e.g., "self.soul.challenge")
        context: Context (self, world, concept, void, time)
        duration_s: Invocation duration in seconds
        success: Whether the invocation succeeded
        tokens_in: Input tokens consumed (for LLM operations)
        tokens_out: Output tokens generated (for LLM operations)
    """
    labels = {"path": path, "context": context}

    # Record to OTEL metrics
    _invoke_counter.add(1, labels)
    _duration_histogram.record(duration_s, labels)

    if tokens_in > 0:
        _token_counter.add(tokens_in, {**labels, "direction": "in"})
    if tokens_out > 0:
        _token_counter.add(tokens_out, {**labels, "direction": "out"})

    if not success:
        _error_counter.add(1, labels)

    # Update in-memory state
    with _state._lock:
        _state.total_invocations += 1
        _state.total_duration_s += duration_s
        _state.total_tokens_in += tokens_in
        _state.total_tokens_out += tokens_out

        _state.invocations_by_context[context] = (
            _state.invocations_by_context.get(context, 0) + 1
        )
        _state.invocations_by_path[path] = _state.invocations_by_path.get(path, 0) + 1

        if not success:
            _state.total_errors += 1
            _state.errors_by_path[path] = _state.errors_by_path.get(path, 0) + 1


def record_error(path: str, context: str, error_type: str = "unknown") -> None:
    """
    Record an error for an AGENTESE invocation.

    Use this for errors that occur before duration can be measured.

    Args:
        path: Full AGENTESE path
        context: Context
        error_type: Type of error (for additional labeling)
    """
    labels = {"path": path, "context": context, "error_type": error_type}
    _error_counter.add(1, labels)

    with _state._lock:
        _state.total_errors += 1
        _state.errors_by_path[path] = _state.errors_by_path.get(path, 0) + 1


# === Summary Functions ===


def get_metrics_summary() -> dict[str, Any]:
    """
    Get a summary of current metrics.

    Returns:
        Dict with aggregated metrics for display
    """
    with _state._lock:
        avg_duration = (
            _state.total_duration_s / _state.total_invocations
            if _state.total_invocations > 0
            else 0.0
        )

        # Get top paths by invocation count
        top_paths = sorted(
            _state.invocations_by_path.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Get error rate by path
        error_rates = {}
        for path, count in _state.invocations_by_path.items():
            errors = _state.errors_by_path.get(path, 0)
            error_rates[path] = errors / count if count > 0 else 0.0

        return {
            "total_invocations": _state.total_invocations,
            "total_errors": _state.total_errors,
            "error_rate": _state.total_errors / _state.total_invocations
            if _state.total_invocations > 0
            else 0.0,
            "total_tokens_in": _state.total_tokens_in,
            "total_tokens_out": _state.total_tokens_out,
            "total_duration_s": _state.total_duration_s,
            "avg_duration_s": avg_duration,
            "invocations_by_context": dict(_state.invocations_by_context),
            "top_paths": dict(top_paths),
            "error_rates_by_path": error_rates,
        }


def reset_metrics() -> None:
    """
    Reset in-memory metrics state.

    Useful for testing or starting fresh.
    Note: This only resets in-memory state, not OTEL counters.
    """
    global _state
    with _state._lock:
        _state.total_invocations = 0
        _state.total_errors = 0
        _state.total_tokens_in = 0
        _state.total_tokens_out = 0
        _state.total_duration_s = 0.0
        _state.invocations_by_context.clear()
        _state.invocations_by_path.clear()
        _state.errors_by_path.clear()


# === Utility Functions ===


def get_invocation_count(path: str | None = None) -> int:
    """
    Get invocation count, optionally filtered by path.

    Args:
        path: Optional path filter

    Returns:
        Count of invocations
    """
    with _state._lock:
        if path is None:
            return _state.total_invocations
        return _state.invocations_by_path.get(path, 0)


def get_error_count(path: str | None = None) -> int:
    """
    Get error count, optionally filtered by path.

    Args:
        path: Optional path filter

    Returns:
        Count of errors
    """
    with _state._lock:
        if path is None:
            return _state.total_errors
        return _state.errors_by_path.get(path, 0)


def get_token_totals() -> tuple[int, int]:
    """
    Get total token counts.

    Returns:
        Tuple of (tokens_in, tokens_out)
    """
    with _state._lock:
        return _state.total_tokens_in, _state.total_tokens_out
