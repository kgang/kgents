"""
Agent Town Action Metrics & Instrumentation (Track B).

Every billable action emits ActionMetric for:
- Unit economics validation
- Revenue tracking
- SLO enforcement
- Ethics monitoring

Patterns reused from:
- K-gent: LLMResponse token tracking
- D-gent: Storage metrics
- N-Phase: Phase transition tracking

See: plans/agent-town/unified-v2.md §4
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

# Graceful OpenTelemetry import
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace import Status, StatusCode

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False
    trace = None  # type: ignore[assignment]
    TracerProvider = None  # type: ignore[assignment, misc]


# =============================================================================
# Action Types & Models
# =============================================================================


class ActionType(Enum):
    """Billable action types in Agent Town."""

    LOD0 = "lod0"  # Free tier
    LOD1 = "lod1"  # Free tier
    LOD2 = "lod2"  # Free tier
    LOD3 = "lod3"  # Haiku - 10 credits
    LOD4 = "lod4"  # Sonnet - 100 credits
    LOD5 = "lod5"  # Opus - 400 credits
    BRANCH = "branch"  # State branching - 150 credits
    INHABIT = "inhabit"  # INHABIT session - 100 credits/10min
    FORCE = "force"  # Force resistance override - 50 credits
    DIALOGUE = "dialogue"  # Citizen dialogue - varies by model


class ModelName(Enum):
    """LLM models used for actions."""

    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"
    TEMPLATE = "template"  # No LLM, template fallback
    CACHED = "cached"  # No LLM, cache hit


# =============================================================================
# Credit Costs (from unified-v2.md §1)
# =============================================================================

# Per-action credit costs (aligned with unit economics)
ACTION_CREDITS: dict[ActionType, int] = {
    ActionType.LOD0: 0,
    ActionType.LOD1: 0,
    ActionType.LOD2: 0,
    ActionType.LOD3: 10,
    ActionType.LOD4: 100,
    ActionType.LOD5: 400,
    ActionType.BRANCH: 150,
    ActionType.INHABIT: 100,  # Per 10 minutes
    ActionType.FORCE: 50,
    ActionType.DIALOGUE: 0,  # Varies, computed from tokens
}

# Model costs (per 1M tokens, from unified-v2.md §1)
MODEL_COSTS_PER_1M: dict[ModelName, tuple[float, float]] = {
    ModelName.HAIKU: (0.25, 1.25),  # (input, output)
    ModelName.SONNET: (3.00, 15.00),
    ModelName.OPUS: (15.00, 75.00),
    ModelName.TEMPLATE: (0.0, 0.0),
    ModelName.CACHED: (0.0, 0.0),
}


# =============================================================================
# ActionMetric
# =============================================================================


@dataclass
class ActionMetric:
    """
    Every billable action emits this metric.

    Fields capture:
    - action_type: LOD level, INHABIT, BRANCH, FORCE, etc.
    - user_id/town_id/citizen_id: Context
    - tokens_in/tokens_out: For unit economics
    - model: haiku/sonnet/opus/template
    - latency_ms: For SLO tracking
    - credits_charged: Revenue tracking
    - timestamp: When action occurred

    Provides:
    - to_otel_span(): Export as OpenTelemetry span attributes
    - to_dict(): Export as JSON for storage/dashboard
    """

    action_type: str  # lod3, lod4, lod5, branch, inhabit, force, dialogue
    user_id: str
    town_id: str
    citizen_id: str | None
    tokens_in: int
    tokens_out: int
    model: str  # haiku, sonnet, opus, template, cached
    latency_ms: int
    credits_charged: int
    timestamp: datetime = field(default_factory=datetime.now)

    # Additional context
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total tokens (input + output)."""
        return self.tokens_in + self.tokens_out

    @property
    def estimated_cost_usd(self) -> float:
        """
        Estimate raw cost in USD based on model pricing.

        Returns 0.0 for template/cached (no LLM call).
        """
        try:
            model_enum = ModelName(self.model)
            if model_enum in (ModelName.TEMPLATE, ModelName.CACHED):
                return 0.0

            input_cost, output_cost = MODEL_COSTS_PER_1M[model_enum]
            return (self.tokens_in * input_cost / 1_000_000) + (
                self.tokens_out * output_cost / 1_000_000
            )
        except (ValueError, KeyError):
            return 0.0

    @property
    def revenue_usd(self) -> float:
        """
        Estimate revenue in USD based on credits charged.

        Assumes credit price range from unified-v2.md §1:
        - Starter: $0.010/credit
        - Explorer: $0.008/credit
        - Adventurer: $0.006/credit

        Conservative estimate: $0.006/credit (lowest tier)
        """
        return self.credits_charged * 0.006

    @property
    def gross_margin(self) -> float:
        """
        Gross margin for this action.

        margin = (revenue - cost) / revenue
        Returns 0.0 if no revenue.
        """
        if self.revenue_usd == 0.0:
            return 0.0
        return (self.revenue_usd - self.estimated_cost_usd) / self.revenue_usd

    def to_otel_span(self) -> dict[str, Any]:
        """Export as OpenTelemetry span attributes."""
        return {
            "action.type": self.action_type,
            "action.model": self.model,
            "action.tokens.in": self.tokens_in,
            "action.tokens.out": self.tokens_out,
            "action.tokens.total": self.total_tokens,
            "action.latency_ms": self.latency_ms,
            "action.credits": self.credits_charged,
            "action.cost_usd": round(self.estimated_cost_usd, 6),
            "action.revenue_usd": round(self.revenue_usd, 6),
            "action.margin": round(self.gross_margin, 4),
            "user.id": self.user_id,
            "town.id": self.town_id,
            "citizen.id": self.citizen_id or "",
        }

    def to_dict(self) -> dict[str, Any]:
        """Export as JSON for storage/dashboard."""
        return {
            "action_type": self.action_type,
            "user_id": self.user_id,
            "town_id": self.town_id,
            "citizen_id": self.citizen_id,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "total_tokens": self.total_tokens,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "credits_charged": self.credits_charged,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            "revenue_usd": round(self.revenue_usd, 6),
            "gross_margin": round(self.gross_margin, 4),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# Metrics Store (In-Memory, for now)
# =============================================================================


class MetricsStore:
    """
    In-memory store for ActionMetrics.

    In production, this would be backed by TimescaleDB or ClickHouse.
    For MVP, we use in-memory with query capabilities.
    """

    def __init__(self) -> None:
        self._metrics: list[ActionMetric] = []
        # Indexes for fast queries
        self._by_user: dict[str, list[ActionMetric]] = defaultdict(list)
        self._by_town: dict[str, list[ActionMetric]] = defaultdict(list)
        self._by_action_type: dict[str, list[ActionMetric]] = defaultdict(list)

    def emit(self, metric: ActionMetric) -> None:
        """Store a metric and update indexes."""
        self._metrics.append(metric)
        self._by_user[metric.user_id].append(metric)
        self._by_town[metric.town_id].append(metric)
        self._by_action_type[metric.action_type].append(metric)

        logger.debug(
            f"Metric emitted: {metric.action_type} "
            f"(tokens={metric.total_tokens}, "
            f"credits={metric.credits_charged}, "
            f"latency={metric.latency_ms}ms)"
        )

    def query(
        self,
        *,
        user_id: str | None = None,
        town_id: str | None = None,
        action_type: str | None = None,
        since: datetime | None = None,
        limit: int = 1000,
    ) -> list[ActionMetric]:
        """Query metrics with filters."""
        candidates = self._metrics

        if user_id:
            candidates = self._by_user.get(user_id, [])
        elif town_id:
            candidates = self._by_town.get(town_id, [])
        elif action_type:
            candidates = self._by_action_type.get(action_type, [])

        # Filter by timestamp
        if since:
            candidates = [m for m in candidates if m.timestamp >= since]

        # Limit
        return candidates[-limit:]

    def aggregate(
        self,
        *,
        user_id: str | None = None,
        town_id: str | None = None,
        action_type: str | None = None,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate metrics for dashboard queries.

        Example:
            "What was the average LOD3 latency today?"
            aggregate(action_type="lod3", since=datetime.today())
        """
        metrics = self.query(
            user_id=user_id,
            town_id=town_id,
            action_type=action_type,
            since=since,
            limit=100_000,
        )

        if not metrics:
            return {
                "count": 0,
                "total_tokens": 0,
                "total_credits": 0,
                "total_cost_usd": 0.0,
                "total_revenue_usd": 0.0,
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "avg_margin": 0.0,
            }

        # Compute aggregates
        total_tokens = sum(m.total_tokens for m in metrics)
        total_credits = sum(m.credits_charged for m in metrics)
        total_cost = sum(m.estimated_cost_usd for m in metrics)
        total_revenue = sum(m.revenue_usd for m in metrics)

        latencies = sorted(m.latency_ms for m in metrics)
        p50_idx = len(latencies) // 2
        p95_idx = int(len(latencies) * 0.95)

        avg_margin = (total_revenue - total_cost) / total_revenue if total_revenue > 0 else 0.0

        return {
            "count": len(metrics),
            "total_tokens": total_tokens,
            "total_credits": total_credits,
            "total_cost_usd": round(total_cost, 6),
            "total_revenue_usd": round(total_revenue, 6),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "p50_latency_ms": latencies[p50_idx] if latencies else 0,
            "p95_latency_ms": latencies[p95_idx] if latencies else 0,
            "avg_margin": round(avg_margin, 4),
            "by_model": self._aggregate_by_model(metrics),
        }

    def _aggregate_by_model(self, metrics: list[ActionMetric]) -> dict[str, Any]:
        """Aggregate metrics by model."""
        by_model: dict[str, list[ActionMetric]] = defaultdict(list)
        for m in metrics:
            by_model[m.model].append(m)

        return {
            model: {
                "count": len(model_metrics),
                "total_tokens": sum(m.total_tokens for m in model_metrics),
                "avg_latency_ms": round(
                    sum(m.latency_ms for m in model_metrics) / len(model_metrics), 2
                ),
            }
            for model, model_metrics in by_model.items()
        }

    def clear(self) -> None:
        """Clear all metrics (for testing)."""
        self._metrics.clear()
        self._by_user.clear()
        self._by_town.clear()
        self._by_action_type.clear()


# Global metrics store
_metrics_store = MetricsStore()


def get_metrics_store() -> MetricsStore:
    """Get the global metrics store."""
    return _metrics_store


# =============================================================================
# OTEL Integration
# =============================================================================


def setup_otel_tracing(
    service_name: str = "agent-town",
    export_to_console: bool = True,
) -> None:
    """
    Set up OpenTelemetry tracing.

    In production, this would export to a collector (Jaeger, Zipkin, etc.).
    For MVP, we export to console for local debugging.

    Args:
        service_name: Service name for traces
        export_to_console: Whether to export to console (for local dev)
    """
    if not HAS_OTEL:
        logger.warning("OpenTelemetry not installed, tracing disabled")
        return

    provider = TracerProvider()

    if export_to_console:
        # Export to console for local debugging
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    logger.info(f"OpenTelemetry tracing enabled for service: {service_name}")


def get_tracer(name: str = "agent-town") -> Any:
    """Get an OpenTelemetry tracer."""
    if not HAS_OTEL or trace is None:
        return None
    return trace.get_tracer(name)


# =============================================================================
# @instrument_action Decorator
# =============================================================================

P = ParamSpec("P")
T = TypeVar("T")


def instrument_action(
    action_type: str,
    *,
    model: str = "haiku",
    user_id: str = "anonymous",
    town_id: str = "unknown",
    citizen_id: str | None = None,
    credits_charged: int = 0,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to instrument billable actions.

    Captures:
    - Execution time (latency_ms)
    - Tokens used (from result if available)
    - Model used
    - Credits charged

    Example:
        @instrument_action("lod3", model="haiku", credits_charged=10)
        async def query_citizen_memory(citizen_id: str) -> dict:
            # ... implementation
            return {"memories": [...], "tokens_used": 50}

    The decorator expects the wrapped function to return a dict-like object
    with optional "tokens_in" and "tokens_out" fields.
    """

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.monotonic()

            # Create OTEL span if available
            tracer = get_tracer()
            span = None
            if tracer:
                span = tracer.start_span(f"action.{action_type}")

            try:
                result = await fn(*args, **kwargs)  # type: ignore[misc]
                latency_ms = int((time.monotonic() - start) * 1000)

                # Extract tokens from result if available
                tokens_in = 0
                tokens_out = 0
                if isinstance(result, dict):
                    tokens_in = result.get("tokens_in", 0)
                    tokens_out = result.get("tokens_out", 0)
                elif hasattr(result, "tokens_in") and hasattr(result, "tokens_out"):
                    tokens_in = getattr(result, "tokens_in", 0)
                    tokens_out = getattr(result, "tokens_out", 0)
                elif hasattr(result, "tokens_used"):
                    tokens_out = getattr(result, "tokens_used", 0)

                # Emit metric
                metric = ActionMetric(
                    action_type=action_type,
                    user_id=user_id,
                    town_id=town_id,
                    citizen_id=citizen_id,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=model,
                    latency_ms=latency_ms,
                    credits_charged=credits_charged,
                )
                _metrics_store.emit(metric)

                # Add OTEL span attributes
                if span:
                    for key, value in metric.to_otel_span().items():
                        span.set_attribute(key, value)
                    span.set_status(Status(StatusCode.OK))

                return result  # type: ignore[no-any-return]

            except Exception as e:
                latency_ms = int((time.monotonic() - start) * 1000)

                # Emit error metric
                metric = ActionMetric(
                    action_type=action_type,
                    user_id=user_id,
                    town_id=town_id,
                    citizen_id=citizen_id,
                    tokens_in=0,
                    tokens_out=0,
                    model=model,
                    latency_ms=latency_ms,
                    credits_charged=0,  # Don't charge for errors
                    metadata={"error": str(e)},
                )
                _metrics_store.emit(metric)

                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))

                raise

            finally:
                if span:
                    span.end()

        @wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.monotonic()

            # Create OTEL span if available
            tracer = get_tracer()
            span = None
            if tracer:
                span = tracer.start_span(f"action.{action_type}")

            try:
                result = fn(*args, **kwargs)
                latency_ms = int((time.monotonic() - start) * 1000)

                # Extract tokens from result if available
                tokens_in = 0
                tokens_out = 0
                if isinstance(result, dict):
                    tokens_in = result.get("tokens_in", 0)
                    tokens_out = result.get("tokens_out", 0)
                elif hasattr(result, "tokens_in") and hasattr(result, "tokens_out"):
                    tokens_in = getattr(result, "tokens_in", 0)
                    tokens_out = getattr(result, "tokens_out", 0)
                elif hasattr(result, "tokens_used"):
                    tokens_out = getattr(result, "tokens_used", 0)

                # Emit metric
                metric = ActionMetric(
                    action_type=action_type,
                    user_id=user_id,
                    town_id=town_id,
                    citizen_id=citizen_id,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=model,
                    latency_ms=latency_ms,
                    credits_charged=credits_charged,
                )
                _metrics_store.emit(metric)

                # Add OTEL span attributes
                if span:
                    for key, value in metric.to_otel_span().items():
                        span.set_attribute(key, value)
                    span.set_status(Status(StatusCode.OK))

                return result

            except Exception as e:
                latency_ms = int((time.monotonic() - start) * 1000)

                # Emit error metric
                metric = ActionMetric(
                    action_type=action_type,
                    user_id=user_id,
                    town_id=town_id,
                    citizen_id=citizen_id,
                    tokens_in=0,
                    tokens_out=0,
                    model=model,
                    latency_ms=latency_ms,
                    credits_charged=0,  # Don't charge for errors
                    metadata={"error": str(e)},
                )
                _metrics_store.emit(metric)

                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))

                raise

            finally:
                if span:
                    span.end()

        # Return async wrapper if fn is async, otherwise sync wrapper
        import inspect

        if inspect.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore[return-value]
        else:
            return sync_wrapper

    return decorator


# =============================================================================
# Manual Metric Emission
# =============================================================================


def emit_action_metric(
    action_type: str,
    *,
    user_id: str = "anonymous",
    town_id: str = "unknown",
    citizen_id: str | None = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    model: str = "haiku",
    latency_ms: int = 0,
    credits_charged: int = 0,
    metadata: dict[str, Any] | None = None,
) -> ActionMetric:
    """
    Manually emit an action metric.

    Use this when you can't use the @instrument_action decorator
    (e.g., in non-function contexts or when you need fine-grained control).

    Returns the emitted metric for inspection.
    """
    metric = ActionMetric(
        action_type=action_type,
        user_id=user_id,
        town_id=town_id,
        citizen_id=citizen_id,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        model=model,
        latency_ms=latency_ms,
        credits_charged=credits_charged,
        metadata=metadata or {},
    )
    _metrics_store.emit(metric)
    return metric


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Enums
    "ActionType",
    "ModelName",
    # Data structures
    "ActionMetric",
    "MetricsStore",
    # Global store
    "get_metrics_store",
    # OTEL
    "setup_otel_tracing",
    "get_tracer",
    # Decorator
    "instrument_action",
    # Manual emission
    "emit_action_metric",
    # Constants
    "ACTION_CREDITS",
    "MODEL_COSTS_PER_1M",
]
