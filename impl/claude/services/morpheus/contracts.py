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
    """Response for world.morpheus.manifest."""

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
    """Request for world.morpheus.complete."""

    model: str
    messages: list[dict[str, str]]  # [{role, content}]
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class CompleteResponse:
    """Response for world.morpheus.complete."""

    response: str
    model: str
    provider: str
    latency_ms: float
    tokens: int


# === Stream Aspect ===


@dataclass
class StreamRequest:
    """Request for world.morpheus.stream."""

    model: str
    messages: list[dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class StreamResponse:
    """Response metadata for world.morpheus.stream (actual data is SSE)."""

    type: Literal["stream"] = "stream"
    model: str = ""


# === Providers Aspect (Response only) ===


@dataclass
class ProvidersResponse:
    """Response for world.morpheus.providers."""

    filter: str  # "all", "enabled", "public"
    count: int
    providers: list[dict[str, Any]] = field(default_factory=list)


# === Metrics Aspect (Response only) ===


@dataclass
class MetricsResponse:
    """Response for world.morpheus.metrics."""

    total_requests: int
    total_errors: int
    error_rate: float
    uptime_seconds: float
    providers_healthy: int
    providers_total: int


# === Health Aspect (Response only) ===


@dataclass
class HealthResponse:
    """Response for world.morpheus.health."""

    status: Literal["healthy", "degraded", "unhealthy"]
    providers: list[dict[str, Any]] = field(default_factory=list)


# === Route Aspect ===


@dataclass
class RouteRequest:
    """Request for world.morpheus.route."""

    model: str


@dataclass
class RouteResponse:
    """Response for world.morpheus.route."""

    model: str
    provider: str
    available: bool
    rate_limited: bool = False


# === Rate Limit Aspect (Response only) ===


@dataclass
class RateLimitResponse:
    """Response for world.morpheus.rate_limit."""

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
