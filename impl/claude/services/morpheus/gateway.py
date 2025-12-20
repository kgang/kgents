"""
Morpheus Gateway: Routes requests to LLM backends.

This is the core routing logic without any HTTP/FastAPI coupling.
The gateway manages providers and routes requests based on model prefix.

AGENTESE: world.morpheus
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

if TYPE_CHECKING:
    from .adapters.base import Adapter
    from .types import ChatRequest, ChatResponse, StreamChunk

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: str
    prefix: str  # Model prefix for routing (e.g., "claude-")
    adapter: "Adapter"
    enabled: bool = True
    public: bool = True  # Visible to non-admin observers


@dataclass
class GatewayConfig:
    """Configuration for the Morpheus Gateway."""

    rate_limit_rpm: int = 60  # Default requests per minute
    rate_limit_burst: int = 10
    rate_limit_by_archetype: dict[str, int] = field(
        default_factory=lambda: {
            "admin": 1000,
            "system": 1000,
            "developer": 100,
            "guest": 20,
        }
    )


@dataclass
class RateLimitState:
    """Thread-safe rate limit tracking using sliding window."""

    _windows: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock)

    def check_and_record(self, archetype: str, limit: int) -> tuple[bool, int]:
        """
        Check rate limit and record request if allowed.

        Returns:
            Tuple of (allowed, remaining)
        """
        now = time.time()
        window_start = now - 60.0  # 1-minute sliding window

        with self._lock:
            # Clean old entries
            self._windows[archetype] = [t for t in self._windows[archetype] if t > window_start]

            current_count = len(self._windows[archetype])
            if current_count >= limit:
                return False, 0

            self._windows[archetype].append(now)
            return True, limit - current_count - 1

    def get_usage(self, archetype: str) -> int:
        """Get current request count in the window."""
        now = time.time()
        window_start = now - 60.0

        with self._lock:
            self._windows[archetype] = [t for t in self._windows[archetype] if t > window_start]
            return len(self._windows[archetype])


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, archetype: str, limit: int, retry_after: float = 60.0):
        self.archetype = archetype
        self.limit = limit
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for '{archetype}': {limit} requests/minute")


class MorpheusGateway:
    """
    Morpheus Gateway: Routes OpenAI-compatible requests to LLM backends.

    Pure routing logic with no HTTP coupling. Can be used by:
    - AGENTESE node (world.morpheus)
    - Direct Python calls
    - Any transport layer

    Usage:
        gateway = MorpheusGateway()
        gateway.register_provider("claude-cli", ClaudeCLIAdapter(), prefix="claude-")
        response = await gateway.complete(request)
    """

    def __init__(self, config: Optional[GatewayConfig] = None) -> None:
        self._config = config or GatewayConfig()
        self._providers: dict[str, ProviderConfig] = {}
        self._request_count = 0
        self._error_count = 0
        self._rate_limit = RateLimitState()

    def register_provider(
        self,
        name: str,
        adapter: "Adapter",
        prefix: str,
        enabled: bool = True,
        public: bool = True,
    ) -> None:
        """
        Register an LLM provider.

        Args:
            name: Unique provider name
            adapter: Adapter instance implementing the Adapter protocol
            prefix: Model prefix for routing (e.g., "claude-")
            enabled: Whether this provider is active
            public: Whether visible to non-admin observers
        """
        self._providers[name] = ProviderConfig(
            name=name,
            prefix=prefix,
            adapter=adapter,
            enabled=enabled,
            public=public,
        )
        logger.info(f"Registered provider: {name} (prefix={prefix})")

    def unregister_provider(self, name: str) -> bool:
        """Remove a provider. Returns True if removed."""
        if name in self._providers:
            del self._providers[name]
            logger.info(f"Unregistered provider: {name}")
            return True
        return False

    def _route_model(self, model: str) -> Optional[ProviderConfig]:
        """Find provider for model based on prefix."""
        for provider in self._providers.values():
            if provider.enabled and model.startswith(provider.prefix):
                return provider
        return None

    def _get_rate_limit(self, archetype: str) -> int:
        """Get rate limit for an archetype."""
        return self._config.rate_limit_by_archetype.get(archetype, self._config.rate_limit_rpm)

    def _check_rate_limit(self, archetype: str) -> None:
        """Check rate limit, raising RateLimitError if exceeded."""
        limit = self._get_rate_limit(archetype)
        allowed, _remaining = self._rate_limit.check_and_record(archetype, limit)
        if not allowed:
            raise RateLimitError(archetype, limit)

    async def complete(self, request: "ChatRequest", archetype: str = "guest") -> "ChatResponse":
        """
        Process a chat completion request.

        Routes to appropriate provider based on model prefix.

        Args:
            request: OpenAI-compatible chat request
            archetype: Observer archetype for rate limiting

        Returns:
            OpenAI-compatible chat response

        Raises:
            ValueError: If no provider matches the model
            RateLimitError: If rate limit exceeded
        """
        self._request_count += 1

        # Check rate limit
        self._check_rate_limit(archetype)

        provider = self._route_model(request.model)
        if provider is None:
            self._error_count += 1
            available = [p.prefix for p in self._providers.values() if p.enabled]
            raise ValueError(
                f"No provider found for model: {request.model}. Available prefixes: {available}"
            )

        logger.debug(f"Routing {request.model} to provider {provider.name}")

        try:
            response = await provider.adapter.complete(request)
            return response
        except Exception as e:
            self._error_count += 1
            logger.error(f"Provider {provider.name} error: {e}")
            raise

    async def stream(
        self, request: "ChatRequest", archetype: str = "guest"
    ) -> AsyncIterator["StreamChunk"]:
        """
        Process a streaming chat completion request.

        Routes to appropriate provider and streams response chunks.

        Args:
            request: OpenAI-compatible chat request
            archetype: Observer archetype for rate limiting

        Yields:
            StreamChunk objects with delta content
        """
        from .types import StreamChunk

        self._request_count += 1
        chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Check rate limit
        try:
            self._check_rate_limit(archetype)
        except RateLimitError as e:
            self._error_count += 1
            yield StreamChunk.from_text(str(e), chunk_id, request.model)
            yield StreamChunk.final(chunk_id, request.model)
            return

        provider = self._route_model(request.model)
        if provider is None:
            self._error_count += 1
            yield StreamChunk.from_text(
                f"No provider found for model: {request.model}",
                chunk_id,
                request.model,
            )
            yield StreamChunk.final(chunk_id, request.model)
            return

        # Check if provider supports streaming
        if not hasattr(provider.adapter, "supports_streaming"):
            supports = False
        else:
            supports = provider.adapter.supports_streaming()

        if not supports:
            self._error_count += 1
            yield StreamChunk.from_text(
                f"Provider {provider.name} does not support streaming",
                chunk_id,
                request.model,
            )
            yield StreamChunk.final(chunk_id, request.model)
            return

        logger.debug(f"Streaming {request.model} via provider {provider.name}")

        try:
            async for chunk in provider.adapter.stream(request):
                yield chunk
        except Exception as e:
            self._error_count += 1
            logger.error(f"Provider {provider.name} streaming error: {e}")
            yield StreamChunk.from_text(f"Error: {e}", chunk_id, request.model)
            yield StreamChunk.final(chunk_id, request.model)

    def list_providers(
        self,
        *,
        enabled_only: bool = False,
        public_only: bool = False,
    ) -> list[ProviderConfig]:
        """
        List providers with optional filtering.

        Args:
            enabled_only: Only return enabled providers
            public_only: Only return public providers (for non-admin observers)

        Returns:
            List of provider configs
        """
        providers = list(self._providers.values())

        if enabled_only:
            providers = [p for p in providers if p.enabled]
        if public_only:
            providers = [p for p in providers if p.public]

        return providers

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get a specific provider by name."""
        return self._providers.get(name)

    def route_info(self, model: str) -> dict[str, Any]:
        """
        Get routing info for a model (for debugging/introspection).

        Returns:
            Dict with routing information
        """
        provider = self._route_model(model)
        if provider is None:
            return {
                "model": model,
                "routed": False,
                "available_prefixes": [p.prefix for p in self._providers.values() if p.enabled],
            }
        return {
            "model": model,
            "routed": True,
            "provider": provider.name,
            "prefix": provider.prefix,
        }

    def rate_limit_status(self, archetype: str) -> dict[str, Any]:
        """Get rate limit status for an archetype."""
        limit = self._get_rate_limit(archetype)
        usage = self._rate_limit.get_usage(archetype)
        return {
            "archetype": archetype,
            "limit_rpm": limit,
            "current_usage": usage,
            "remaining": max(0, limit - usage),
        }

    def health_check(self) -> dict[str, Any]:
        """Return comprehensive health status."""
        provider_health = {
            name: config.adapter.health_check() for name, config in self._providers.items()
        }

        healthy_providers = sum(
            1
            for config in self._providers.values()
            if config.enabled and config.adapter.is_available()
        )

        return {
            "status": "healthy" if healthy_providers > 0 else "degraded",
            "providers": provider_health,
            "providers_healthy": healthy_providers,
            "providers_total": len(self._providers),
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "rate_limits": dict(self._config.rate_limit_by_archetype),
        }

    @property
    def request_count(self) -> int:
        """Total requests processed."""
        return self._request_count

    @property
    def error_count(self) -> int:
        """Total errors encountered."""
        return self._error_count


__all__ = [
    "MorpheusGateway",
    "GatewayConfig",
    "ProviderConfig",
    "RateLimitError",
    "RateLimitState",
]
