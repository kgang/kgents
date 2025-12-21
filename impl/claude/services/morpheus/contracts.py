"""
Morpheus Contracts: Request/Response types for AGENTESE aspects.

These contracts define the type-safe interface for all Morpheus aspects.
They enable:
- Automatic OpenAPI schema generation
- Frontend TypeScript type generation
- Runtime validation at the gateway
- Teaching Mode hints in the UI

See: docs/skills/agentese-node-registration.md for contract patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

# === Manifest Aspect (Response only) ===


@dataclass
class MorpheusManifestResponse:
    """
    Response for world.morpheus.manifest.

    Teaching:
        gotcha: These contract types are for AGENTESE OpenAPI schema generation.
                They are NOT the same as the internal types in types.py/persistence.py.
                (Evidence: node.py uses MorpheusManifestRendering, not this)
    """

    healthy: bool
    providers_healthy: int
    providers_total: int
    total_requests: int
    total_errors: int
    uptime_seconds: float
    providers: list[dict[str, Any]] = field(default_factory=list)


# === Complete Aspect ===


@dataclass
class CompleteRequest:
    """
    Request for world.morpheus.complete.

    Teaching:
        gotcha: `messages` is a list of dicts, not ChatMessage objects.
                The node converts these to ChatMessage internally.
                (Evidence: node.py::_handle_complete converts dicts)
    """

    model: str
    messages: list[dict[str, str]]  # [{role, content}]
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class CompleteResponse:
    """
    Response for world.morpheus.complete.

    Teaching:
        gotcha: `response` is the extracted text, not the full ChatResponse.
                Use world.morpheus.manifest to see detailed response metadata.
                (Evidence: node.py::_handle_complete extracts response_text)
    """

    response: str
    model: str
    provider: str
    latency_ms: float
    tokens: int


# === Stream Aspect ===


@dataclass
class StreamRequest:
    """
    Request for world.morpheus.stream.

    Teaching:
        gotcha: Same structure as CompleteRequest, but the node sets stream=True
                internally and returns an async generator instead of a response.
                (Evidence: node.py::_handle_stream sets request.stream = True)
    """

    model: str
    messages: list[dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class StreamResponse:
    """
    Response metadata for world.morpheus.stream (actual data is SSE).

    Teaching:
        gotcha: The actual content is delivered via SSE, not in this response.
                This is just metadata confirming the stream started.
                (Evidence: node.py::_handle_stream returns stream generator)
    """

    type: Literal["stream"] = "stream"
    model: str = ""


# === Providers Aspect (Response only) ===


@dataclass
class ProvidersResponse:
    """
    Response for world.morpheus.providers.

    Teaching:
        gotcha: The `filter` field indicates which filter was applied based on
                observer archetype: "all" (admin), "enabled" (dev), "public" (guest).
                (Evidence: test_node.py::TestMorpheusNodeProviders)
    """

    filter: str  # "all", "enabled", "public"
    count: int
    providers: list[dict[str, Any]] = field(default_factory=list)


# === Metrics Aspect (Response only) ===


@dataclass
class MetricsResponse:
    """
    Response for world.morpheus.metrics.

    Teaching:
        gotcha: This aspect requires "developer" or "admin" archetype. Guests
                calling metrics get a Forbidden error.
                (Evidence: test_node.py::TestMorpheusNodeMetrics)
    """

    total_requests: int
    total_errors: int
    error_rate: float
    uptime_seconds: float
    providers_healthy: int
    providers_total: int


# === Health Aspect (Response only) ===


@dataclass
class HealthResponse:
    """
    Response for world.morpheus.health.

    Teaching:
        gotcha: "healthy" means at least one provider is available—not that all are.
                "degraded" = some providers down, "unhealthy" = all providers down.
                (Evidence: test_node.py::TestMorpheusNodeHealth)
    """

    status: Literal["healthy", "degraded", "unhealthy"]
    providers: list[dict[str, Any]] = field(default_factory=list)


# === Route Aspect ===


@dataclass
class RouteRequest:
    """
    Request for world.morpheus.route.

    Teaching:
        gotcha: This is a query aspect, not a mutation. It tells you WHERE a model
                would route without actually making a request.
                (Evidence: test_node.py::TestMorpheusNodeRoute)
    """

    model: str


@dataclass
class RouteResponse:
    """
    Response for world.morpheus.route.

    Teaching:
        gotcha: `available` is false if no provider matches the model prefix.
                Check `available` before making a complete/stream request.
                (Evidence: test_node.py::test_route_for_unknown_model)
    """

    model: str
    provider: str
    available: bool
    rate_limited: bool = False


# === Rate Limit Aspect (Response only) ===


@dataclass
class RateLimitResponse:
    """
    Response for world.morpheus.rate_limit.

    Teaching:
        gotcha: `reset_at` is a timestamp hint, not a guarantee. Sliding window
                limits may clear earlier as old requests age out.
                (Evidence: gateway.py RateLimitState uses 60s sliding window)
    """

    archetype: str
    requests_remaining: int
    reset_at: Optional[str] = None


__all__ = [
    "MorpheusManifestResponse",
    "CompleteRequest",
    "CompleteResponse",
    "StreamRequest",
    "StreamResponse",
    "ProvidersResponse",
    "MetricsResponse",
    "HealthResponse",
    "RouteRequest",
    "RouteResponse",
    "RateLimitResponse",
]
