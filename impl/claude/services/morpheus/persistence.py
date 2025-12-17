"""
Morpheus Persistence: Domain semantics for LLM gateway operations.

This is the persistence/service layer in the Metaphysical Fullstack pattern.
It owns:
- WHEN to route (model prefix matching)
- WHY to persist (request logging, metrics)
- HOW to compose (adapter selection, telemetry)

The MorpheusPersistence wraps MorpheusGateway and adds:
- Telemetry integration (spans, metrics)
- Result types with rich metadata
- Observer-dependent provider filtering
- Streaming support with telemetry
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from opentelemetry import trace

from .gateway import MorpheusGateway, RateLimitError
from .observability import (
    MorpheusTelemetry,
    record_completion,
    record_rate_limit,
    record_time_to_first_token,
    ATTR_TOKENS_IN,
    ATTR_TOKENS_OUT,
)
from .types import ChatRequest, ChatResponse, StreamChunk

if TYPE_CHECKING:
    pass


# === Result Types ===


@dataclass(frozen=True)
class CompletionResult:
    """Result of a completion operation with metadata."""

    response: ChatResponse
    provider_name: str
    latency_ms: float
    telemetry_span_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "response": self.response.to_dict(),
            "provider_name": self.provider_name,
            "latency_ms": self.latency_ms,
            "telemetry_span_id": self.telemetry_span_id,
        }


@dataclass(frozen=True)
class ProviderStatus:
    """Status of a single provider."""

    name: str
    prefix: str
    enabled: bool
    available: bool
    public: bool
    request_count: int
    health: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "prefix": self.prefix,
            "enabled": self.enabled,
            "available": self.available,
            "public": self.public,
            "request_count": self.request_count,
            "health": self.health,
        }


@dataclass(frozen=True)
class MorpheusStatus:
    """Overall Morpheus health status."""

    healthy: bool
    providers_healthy: int
    providers_total: int
    total_requests: int
    total_errors: int
    uptime_seconds: float
    providers: list[ProviderStatus] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "providers_healthy": self.providers_healthy,
            "providers_total": self.providers_total,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "uptime_seconds": self.uptime_seconds,
            "providers": [p.to_dict() for p in self.providers],
        }


# === Persistence Layer ===


class MorpheusPersistence:
    """
    Domain semantics for Morpheus Gateway.

    Composes:
    - MorpheusGateway: Routing and provider management
    - Telemetry: Spans and metrics (OTEL integration)

    This is the persistence layer in the Metaphysical Fullstack pattern.
    All transports (HTTP, CLI, AGENTESE) collapse to this interface.
    """

    def __init__(
        self,
        gateway: Optional[MorpheusGateway] = None,
        *,
        telemetry_enabled: bool = True,
    ) -> None:
        """
        Initialize MorpheusPersistence.

        Args:
            gateway: MorpheusGateway instance (creates default if None)
            telemetry_enabled: Whether to record OTEL spans and metrics
        """
        self._gateway = gateway or MorpheusGateway()
        self._start_time = time.monotonic()
        self._telemetry = MorpheusTelemetry() if telemetry_enabled else None

    @property
    def gateway(self) -> MorpheusGateway:
        """Access the underlying gateway."""
        return self._gateway

    async def manifest(self) -> MorpheusStatus:
        """
        Return Morpheus status.

        AGENTESE: world.morpheus.manifest
        """
        health = self._gateway.health_check()

        # Build provider statuses
        provider_statuses = []
        for name, config in self._gateway._providers.items():
            adapter_health = config.adapter.health_check()
            provider_statuses.append(
                ProviderStatus(
                    name=name,
                    prefix=config.prefix,
                    enabled=config.enabled,
                    available=config.adapter.is_available(),
                    public=config.public,
                    request_count=adapter_health.get("total_requests", 0),
                    health=adapter_health,
                )
            )

        return MorpheusStatus(
            healthy=health["status"] == "healthy",
            providers_healthy=health["providers_healthy"],
            providers_total=health["providers_total"],
            total_requests=health["total_requests"],
            total_errors=health["total_errors"],
            uptime_seconds=time.monotonic() - self._start_time,
            providers=provider_statuses,
        )

    async def complete(
        self, request: ChatRequest, archetype: str = "guest"
    ) -> CompletionResult:
        """
        Process a chat completion request with telemetry.

        AGENTESE: world.morpheus.complete

        Args:
            request: OpenAI-compatible chat request
            archetype: Observer archetype for rate limiting

        Returns:
            CompletionResult with response and metadata
        """
        # Find provider for telemetry tagging
        provider = self._gateway._route_model(request.model)
        provider_name = provider.name if provider else "unknown"

        start = time.monotonic()
        span_id: Optional[str] = None
        success = True
        tokens_in = 0
        tokens_out = 0

        try:
            if self._telemetry:
                async with self._telemetry.trace_completion(
                    request, archetype, provider_name
                ) as span:
                    span_id = format(span.get_span_context().span_id, "016x")
                    response = await self._gateway.complete(request, archetype)

                    # Record tokens on span
                    if response.usage:
                        tokens_in = response.usage.prompt_tokens
                        tokens_out = response.usage.completion_tokens
                        span.set_attribute(ATTR_TOKENS_IN, tokens_in)
                        span.set_attribute(ATTR_TOKENS_OUT, tokens_out)
            else:
                response = await self._gateway.complete(request, archetype)
                if response.usage:
                    tokens_in = response.usage.prompt_tokens
                    tokens_out = response.usage.completion_tokens

        except RateLimitError as e:
            success = False
            record_rate_limit(archetype, request.model)
            raise
        except Exception:
            success = False
            raise
        finally:
            latency_ms = (time.monotonic() - start) * 1000
            # Record metrics
            record_completion(
                model=request.model,
                provider=provider_name,
                archetype=archetype,
                duration_s=latency_ms / 1000,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                success=success,
                streaming=False,
            )

        return CompletionResult(
            response=response,
            provider_name=provider_name,
            latency_ms=latency_ms,
            telemetry_span_id=span_id,
        )

    async def stream(
        self, request: ChatRequest, archetype: str = "guest"
    ) -> AsyncIterator[StreamChunk]:
        """
        Process a streaming chat completion request with telemetry.

        AGENTESE: world.morpheus.stream

        Args:
            request: OpenAI-compatible chat request
            archetype: Observer archetype for rate limiting

        Yields:
            StreamChunk objects with delta content
        """
        provider = self._gateway._route_model(request.model)
        provider_name = provider.name if provider else "unknown"

        start = time.monotonic()
        first_token_time: Optional[float] = None
        total_tokens = 0

        try:
            if self._telemetry:
                async with self._telemetry.trace_stream(
                    request, archetype, provider_name
                ) as span:
                    async for chunk in self._gateway.stream(request, archetype):
                        # Record time to first token
                        if first_token_time is None and chunk.choices:
                            delta = chunk.choices[0].delta
                            if delta.content:
                                first_token_time = time.monotonic()
                                ttft = first_token_time - start
                                record_time_to_first_token(
                                    request.model, provider_name, ttft
                                )
                        total_tokens += 1
                        yield chunk
            else:
                async for chunk in self._gateway.stream(request, archetype):
                    if first_token_time is None and chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            first_token_time = time.monotonic()
                    total_tokens += 1
                    yield chunk

        except RateLimitError as e:
            record_rate_limit(archetype, request.model)
            raise
        finally:
            latency_ms = (time.monotonic() - start) * 1000
            # Record metrics (estimate tokens from chunks)
            record_completion(
                model=request.model,
                provider=provider_name,
                archetype=archetype,
                duration_s=latency_ms / 1000,
                tokens_in=0,  # Unknown for streaming
                tokens_out=total_tokens,  # Approximate
                success=True,  # If we got here, it succeeded
                streaming=True,
            )

    async def list_providers(
        self,
        *,
        enabled_only: bool = False,
        public_only: bool = False,
    ) -> list[ProviderStatus]:
        """
        List providers with optional filtering.

        AGENTESE: world.morpheus.providers

        Args:
            enabled_only: Only return enabled providers
            public_only: Only return public providers

        Returns:
            List of ProviderStatus objects
        """
        configs = self._gateway.list_providers(
            enabled_only=enabled_only,
            public_only=public_only,
        )

        return [
            ProviderStatus(
                name=c.name,
                prefix=c.prefix,
                enabled=c.enabled,
                available=c.adapter.is_available(),
                public=c.public,
                request_count=c.adapter.health_check().get("total_requests", 0),
                health=c.adapter.health_check(),
            )
            for c in configs
        ]

    async def route_info(self, model: str) -> dict[str, Any]:
        """
        Get routing info for a model.

        AGENTESE: world.morpheus.route

        Args:
            model: Model name to check routing for

        Returns:
            Dict with routing information
        """
        return self._gateway.route_info(model)

    async def health(self) -> dict[str, Any]:
        """
        Get health check info.

        AGENTESE: world.morpheus.health

        Returns:
            Dict with health status
        """
        return self._gateway.health_check()

    def rate_limit_status(self, archetype: str) -> dict[str, Any]:
        """
        Get rate limit status for an archetype.

        AGENTESE: world.morpheus.rate_limit

        Args:
            archetype: Observer archetype

        Returns:
            Dict with rate limit info
        """
        return self._gateway.rate_limit_status(archetype)


__all__ = [
    "MorpheusPersistence",
    "MorpheusStatus",
    "ProviderStatus",
    "CompletionResult",
]
