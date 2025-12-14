"""
Reactive Substrate Metrics: OpenTelemetry-compatible metrics for widget operations.

Provides counters and histograms for tracking widget renders, enabling
monitoring and observability of the reactive substrate.

Metrics exposed:
- reactive_renders_total: Counter of total renders by widget_type/target
- reactive_render_duration_seconds: Histogram of render durations
- reactive_errors_total: Counter of render errors

Usage:
    from agents.i.reactive._metrics import record_render, get_metrics_summary

    # Record a render (called by instrumented widgets)
    record_render(
        widget_type="AgentCardWidget",
        target="CLI",
        duration_s=0.001,
        success=True,
    )

    # Get current metrics summary
    summary = get_metrics_summary()
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from opentelemetry import metrics

# === Meter Singleton ===

_meter = metrics.get_meter("kgents.reactive", "1.0.0")

# === Counters ===

_render_counter = _meter.create_counter(
    "reactive_renders_total",
    description="Total number of widget renders",
    unit="1",
)

_error_counter = _meter.create_counter(
    "reactive_errors_total",
    description="Total widget render errors",
    unit="1",
)

# === Histograms ===

_duration_histogram = _meter.create_histogram(
    "reactive_render_duration_seconds",
    description="Duration of widget renders",
    unit="s",
)

# === In-Memory Aggregation (for summary) ===


@dataclass
class MetricsState:
    """Thread-safe in-memory metrics state for summaries."""

    total_renders: int = 0
    total_errors: int = 0
    total_duration_s: float = 0.0
    renders_by_widget: dict[str, int] = field(default_factory=dict)
    renders_by_target: dict[str, int] = field(default_factory=dict)
    errors_by_widget: dict[str, int] = field(default_factory=dict)
    durations_by_widget: dict[str, list[float]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)


_state = MetricsState()


# === Recording Functions ===


def record_render(
    widget_type: str,
    target: str,
    duration_s: float,
    success: bool = True,
) -> None:
    """
    Record metrics for a widget render.

    This function is called by instrumented widgets after each render.
    It updates both OpenTelemetry metrics (for export) and in-memory state
    (for summaries).

    Args:
        widget_type: Widget class name (e.g., "AgentCardWidget")
        target: Render target (CLI, TUI, MARIMO, JSON)
        duration_s: Render duration in seconds
        success: Whether the render succeeded
    """
    labels = {"widget_type": widget_type, "target": target}

    # Record to OTEL metrics
    _render_counter.add(1, labels)
    _duration_histogram.record(duration_s, labels)

    if not success:
        _error_counter.add(1, labels)

    # Update in-memory state
    with _state._lock:
        _state.total_renders += 1
        _state.total_duration_s += duration_s

        _state.renders_by_widget[widget_type] = (
            _state.renders_by_widget.get(widget_type, 0) + 1
        )
        _state.renders_by_target[target] = _state.renders_by_target.get(target, 0) + 1

        # Track durations for P95 calculation (keep last 1000 per widget)
        if widget_type not in _state.durations_by_widget:
            _state.durations_by_widget[widget_type] = []
        durations = _state.durations_by_widget[widget_type]
        durations.append(duration_s)
        if len(durations) > 1000:
            _state.durations_by_widget[widget_type] = durations[-1000:]

        if not success:
            _state.total_errors += 1
            _state.errors_by_widget[widget_type] = (
                _state.errors_by_widget.get(widget_type, 0) + 1
            )


def record_error(widget_type: str, target: str, error_type: str = "unknown") -> None:
    """
    Record an error for a widget render.

    Use this for errors that occur before duration can be measured.

    Args:
        widget_type: Widget class name
        target: Render target
        error_type: Type of error (for additional labeling)
    """
    labels = {"widget_type": widget_type, "target": target, "error_type": error_type}
    _error_counter.add(1, labels)

    with _state._lock:
        _state.total_errors += 1
        _state.errors_by_widget[widget_type] = (
            _state.errors_by_widget.get(widget_type, 0) + 1
        )


# === Summary Functions ===


def get_metrics_summary() -> dict[str, Any]:
    """
    Get a summary of current metrics.

    Returns:
        Dict with aggregated metrics for display
    """
    with _state._lock:
        avg_duration = (
            _state.total_duration_s / _state.total_renders
            if _state.total_renders > 0
            else 0.0
        )

        # Compute P95 durations per widget
        p95_by_widget = {}
        for widget_type, durations in _state.durations_by_widget.items():
            if durations:
                sorted_d = sorted(durations)
                idx = int(len(sorted_d) * 0.95)
                p95_by_widget[widget_type] = sorted_d[min(idx, len(sorted_d) - 1)]

        # Get top widgets by render count
        top_widgets = sorted(
            _state.renders_by_widget.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Get error rate by widget
        error_rates = {}
        for widget_type, count in _state.renders_by_widget.items():
            errors = _state.errors_by_widget.get(widget_type, 0)
            error_rates[widget_type] = errors / count if count > 0 else 0.0

        return {
            "total_renders": _state.total_renders,
            "total_errors": _state.total_errors,
            "error_rate": _state.total_errors / _state.total_renders
            if _state.total_renders > 0
            else 0.0,
            "total_duration_s": _state.total_duration_s,
            "avg_duration_s": avg_duration,
            "renders_by_widget": dict(_state.renders_by_widget),
            "renders_by_target": dict(_state.renders_by_target),
            "errors_by_widget": dict(_state.errors_by_widget),
            "top_widgets": dict(top_widgets),
            "p95_duration_by_widget": p95_by_widget,
            "error_rates_by_widget": error_rates,
        }


def reset_metrics() -> None:
    """
    Reset in-memory metrics state.

    Useful for testing or starting fresh.
    Note: This only resets in-memory state, not OTEL counters.
    """
    with _state._lock:
        _state.total_renders = 0
        _state.total_errors = 0
        _state.total_duration_s = 0.0
        _state.renders_by_widget.clear()
        _state.renders_by_target.clear()
        _state.errors_by_widget.clear()
        _state.durations_by_widget.clear()


# === Utility Functions ===


def get_render_count(widget_type: str | None = None, target: str | None = None) -> int:
    """
    Get render count, optionally filtered by widget type or target.

    Args:
        widget_type: Optional widget type filter
        target: Optional target filter

    Returns:
        Count of renders
    """
    with _state._lock:
        if widget_type is None and target is None:
            return _state.total_renders
        if widget_type is not None:
            return _state.renders_by_widget.get(widget_type, 0)
        if target is not None:
            return _state.renders_by_target.get(target, 0)
        return 0


def get_error_count(widget_type: str | None = None) -> int:
    """
    Get error count, optionally filtered by widget type.

    Args:
        widget_type: Optional widget type filter

    Returns:
        Count of errors
    """
    with _state._lock:
        if widget_type is None:
            return _state.total_errors
        return _state.errors_by_widget.get(widget_type, 0)


def get_p95_duration(widget_type: str) -> float | None:
    """
    Get P95 render duration for a widget type.

    Args:
        widget_type: Widget class name

    Returns:
        P95 duration in seconds, or None if no data
    """
    with _state._lock:
        durations = _state.durations_by_widget.get(widget_type, [])
        if not durations:
            return None
        sorted_d = sorted(durations)
        idx = int(len(sorted_d) * 0.95)
        return sorted_d[min(idx, len(sorted_d) - 1)]


# === Timing Context Manager ===


class RenderTimer:
    """
    Context manager for timing widget renders.

    Usage:
        with RenderTimer("AgentCardWidget", "CLI") as timer:
            result = widget.project(target)
        # Metrics automatically recorded
    """

    def __init__(self, widget_type: str, target: str):
        self.widget_type = widget_type
        self.target = target
        self.start_time: float = 0.0
        self.success = True

    def __enter__(self) -> "RenderTimer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration = time.perf_counter() - self.start_time
        self.success = exc_type is None
        record_render(
            widget_type=self.widget_type,
            target=self.target,
            duration_s=duration,
            success=self.success,
        )


__all__ = [
    "record_render",
    "record_error",
    "get_metrics_summary",
    "reset_metrics",
    "get_render_count",
    "get_error_count",
    "get_p95_duration",
    "RenderTimer",
]
