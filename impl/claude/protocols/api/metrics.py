"""
Prometheus metrics endpoint for kgents SaaS API.

Exposes metrics for:
- NATS streaming health and throughput
- OpenMeter billing events and latency
- API request rates and errors
- Circuit breaker state

Usage:
    from protocols.api.metrics import create_metrics_router, update_metrics

    router = create_metrics_router()
    app.include_router(router)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Response

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    Response = None  # type: ignore[misc, assignment]

# Prometheus client (optional)
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

logger = logging.getLogger(__name__)

# --- Metric Definitions ---
# Using a custom registry to avoid conflicts with default metrics

if HAS_PROMETHEUS:
    # Custom registry for kgents metrics
    REGISTRY = CollectorRegistry()

    # NATS Metrics
    nats_circuit_state = Gauge(
        "kgents_nats_circuit_state",
        "Circuit breaker state (0=closed, 1=open, 2=half_open)",
        registry=REGISTRY,
    )

    nats_messages_published = Counter(
        "kgents_nats_messages_published_total",
        "Total messages published to NATS",
        ["subject_type"],
        registry=REGISTRY,
    )

    nats_publish_errors = Counter(
        "kgents_nats_publish_errors_total",
        "Total NATS publish errors",
        registry=REGISTRY,
    )

    nats_fallback_queue_depth = Gauge(
        "kgents_nats_fallback_queue_depth",
        "Depth of fallback queue when NATS unavailable",
        registry=REGISTRY,
    )

    # OpenMeter Metrics
    openmeter_events_buffered = Gauge(
        "kgents_openmeter_events_buffered",
        "Events currently in OpenMeter buffer",
        registry=REGISTRY,
    )

    openmeter_events_sent = Counter(
        "kgents_openmeter_events_sent_total",
        "Total events sent to OpenMeter",
        ["event_type"],
        registry=REGISTRY,
    )

    openmeter_flush_errors = Counter(
        "kgents_openmeter_flush_errors_total",
        "Total OpenMeter flush errors",
        registry=REGISTRY,
    )

    openmeter_flush_latency = Histogram(
        "kgents_openmeter_flush_latency_seconds",
        "Latency of OpenMeter flush operations",
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=REGISTRY,
    )

    # Stripe Webhook Metrics
    stripe_webhooks_received = Counter(
        "kgents_stripe_webhooks_received_total",
        "Total Stripe webhooks received",
        ["event_type"],
        registry=REGISTRY,
    )

    stripe_webhooks_processed = Counter(
        "kgents_stripe_webhooks_processed_total",
        "Total Stripe webhooks successfully processed",
        ["event_type"],
        registry=REGISTRY,
    )

    stripe_webhooks_errors = Counter(
        "kgents_stripe_webhooks_errors_total",
        "Total Stripe webhook processing errors",
        ["error_type"],
        registry=REGISTRY,
    )

    # API Metrics
    api_requests = Counter(
        "kgents_api_requests_total",
        "Total API requests",
        ["method", "endpoint", "status"],
        registry=REGISTRY,
    )

    api_request_latency = Histogram(
        "kgents_api_request_latency_seconds",
        "API request latency",
        ["method", "endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=REGISTRY,
    )

else:
    # Stub classes when prometheus_client not installed
    REGISTRY = None
    nats_circuit_state = None
    nats_messages_published = None
    nats_publish_errors = None
    nats_fallback_queue_depth = None
    openmeter_events_buffered = None
    openmeter_events_sent = None
    openmeter_flush_errors = None
    openmeter_flush_latency = None
    stripe_webhooks_received = None
    stripe_webhooks_processed = None
    stripe_webhooks_errors = None
    api_requests = None
    api_request_latency = None


# --- Metric Update Functions ---


def update_nats_circuit_state(state: str) -> None:
    """
    Update NATS circuit breaker state metric.

    Args:
        state: Circuit state ("closed", "open", "half_open")
    """
    if not HAS_PROMETHEUS or nats_circuit_state is None:
        return

    state_values = {"closed": 0, "open": 1, "half_open": 2}
    nats_circuit_state.set(state_values.get(state, -1))


def record_nats_publish(subject_type: str = "chunk") -> None:
    """Record a NATS publish event."""
    if not HAS_PROMETHEUS or nats_messages_published is None:
        return
    nats_messages_published.labels(subject_type=subject_type).inc()


def record_nats_error() -> None:
    """Record a NATS publish error."""
    if not HAS_PROMETHEUS or nats_publish_errors is None:
        return
    nats_publish_errors.inc()


def update_nats_fallback_depth(depth: int) -> None:
    """Update NATS fallback queue depth."""
    if not HAS_PROMETHEUS or nats_fallback_queue_depth is None:
        return
    nats_fallback_queue_depth.set(depth)


def update_openmeter_buffer_depth(depth: int) -> None:
    """Update OpenMeter buffer depth."""
    if not HAS_PROMETHEUS or openmeter_events_buffered is None:
        return
    openmeter_events_buffered.set(depth)


def record_openmeter_event(event_type: str) -> None:
    """Record an OpenMeter event sent."""
    if not HAS_PROMETHEUS or openmeter_events_sent is None:
        return
    openmeter_events_sent.labels(event_type=event_type).inc()


def record_openmeter_error() -> None:
    """Record an OpenMeter flush error."""
    if not HAS_PROMETHEUS or openmeter_flush_errors is None:
        return
    openmeter_flush_errors.inc()


def observe_openmeter_latency(latency_seconds: float) -> None:
    """Record OpenMeter flush latency."""
    if not HAS_PROMETHEUS or openmeter_flush_latency is None:
        return
    openmeter_flush_latency.observe(latency_seconds)


def record_stripe_webhook(event_type: str, processed: bool = True) -> None:
    """Record a Stripe webhook."""
    if not HAS_PROMETHEUS:
        return

    if stripe_webhooks_received is not None:
        stripe_webhooks_received.labels(event_type=event_type).inc()

    if processed and stripe_webhooks_processed is not None:
        stripe_webhooks_processed.labels(event_type=event_type).inc()


def record_stripe_error(error_type: str = "processing") -> None:
    """Record a Stripe webhook error."""
    if not HAS_PROMETHEUS or stripe_webhooks_errors is None:
        return
    stripe_webhooks_errors.labels(error_type=error_type).inc()


def record_api_request(
    method: str, endpoint: str, status: int, latency_seconds: float
) -> None:
    """Record an API request with latency."""
    if not HAS_PROMETHEUS:
        return

    if api_requests is not None:
        api_requests.labels(method=method, endpoint=endpoint, status=str(status)).inc()

    if api_request_latency is not None:
        api_request_latency.labels(method=method, endpoint=endpoint).observe(
            latency_seconds
        )


# --- Metrics Router ---


def create_metrics_router() -> Optional["APIRouter"]:
    """
    Create metrics router.

    Returns:
        APIRouter if FastAPI and prometheus_client are available, None otherwise
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(tags=["system"])

    @router.get("/metrics")
    async def metrics() -> Response:
        """
        Prometheus metrics endpoint.

        Returns metrics in Prometheus text format.
        """
        if not HAS_PROMETHEUS:
            return Response(
                content="# prometheus_client not installed\n",
                media_type="text/plain",
            )

        # Collect metrics from SaaS infrastructure
        await _collect_saas_metrics()

        # Generate Prometheus output
        output = generate_latest(REGISTRY)
        return Response(content=output, media_type=CONTENT_TYPE_LATEST)

    return router


async def _collect_saas_metrics() -> None:
    """Collect current metrics from SaaS infrastructure."""
    try:
        from protocols.config import get_saas_clients

        clients = get_saas_clients()

        # NATS metrics
        if clients.nats is not None:
            health = await clients.nats.health_check()

            # Circuit breaker state
            circuit_state = health.get("circuit_breaker", {}).get("state", "unknown")
            update_nats_circuit_state(circuit_state)

            # Fallback queue depth
            fallback_depth = health.get("fallback_queues", 0)
            update_nats_fallback_depth(fallback_depth)

        # OpenMeter metrics
        if clients.openmeter is not None:
            metrics = clients.openmeter.get_metrics()

            # Buffer depth
            buffer_depth = metrics.get("events_buffered", 0)
            update_openmeter_buffer_depth(buffer_depth)

    except ImportError:
        pass  # SaaS config not available
    except Exception as e:
        logger.warning(f"Failed to collect SaaS metrics: {e}")


def get_metrics_summary() -> dict[str, Any]:
    """
    Get metrics summary as dictionary.

    Useful for JSON health endpoints.
    """
    if not HAS_PROMETHEUS:
        return {"prometheus_available": False}

    # Collect basic metrics
    return {
        "prometheus_available": True,
        "registry_collectors": len(list(REGISTRY.collect())),
    }
