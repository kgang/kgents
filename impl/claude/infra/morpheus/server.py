"""
Morpheus Gateway Server: FastAPI application serving OpenAI-compatible API.

This is the main entry point for the Morpheus Gateway. It provides:
- POST /v1/chat/completions - OpenAI-compatible chat endpoint
- GET /health - Health check endpoint
- GET /metrics - Prometheus metrics (optional)

Routes requests to appropriate backend based on model prefix:
    claude-*     → Claude CLI Adapter
    claude-api-* → Anthropic API (direct)
    gpt-*        → OpenAI API
    openrouter/* → OpenRouter

AGENTESE: world.morpheus.gateway.server
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from .adapter import AdapterConfig, ClaudeCLIAdapter, MockAdapter
from .types import ChatRequest, ChatResponse, MorpheusError

logger = logging.getLogger(__name__)


class Adapter(Protocol):
    """Protocol for LLM adapters."""

    async def complete(self, request: ChatRequest) -> ChatResponse: ...

    def is_available(self) -> bool: ...

    def health_check(self) -> dict[str, Any]: ...


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: str
    prefix: str  # Model prefix for routing (e.g., "claude-")
    adapter: Adapter
    enabled: bool = True


@dataclass
class GatewayConfig:
    """Configuration for the Morpheus Gateway."""

    port: int = 8080
    metrics_port: int = 9090
    enable_metrics: bool = True
    rate_limit_rpm: int = 60  # Requests per minute
    rate_limit_burst: int = 10


class MorpheusGateway:
    """
    Morpheus Gateway: Routes OpenAI-compatible requests to LLM backends.

    Usage:
        gateway = MorpheusGateway()
        gateway.register_provider("claude-cli", ClaudeCLIAdapter())
        response = await gateway.chat_completion(request)
    """

    def __init__(self, config: Optional[GatewayConfig] = None) -> None:
        self._config = config or GatewayConfig()
        self._providers: dict[str, ProviderConfig] = {}
        self._request_count = 0
        self._error_count = 0

    def register_provider(
        self,
        name: str,
        adapter: Adapter,
        prefix: str,
        enabled: bool = True,
    ) -> None:
        """Register an LLM provider."""
        self._providers[name] = ProviderConfig(
            name=name,
            prefix=prefix,
            adapter=adapter,
            enabled=enabled,
        )
        logger.info(f"Registered provider: {name} (prefix={prefix})")

    def _route_model(self, model: str) -> Optional[ProviderConfig]:
        """Find provider for model based on prefix."""
        for provider in self._providers.values():
            if provider.enabled and model.startswith(provider.prefix):
                return provider
        return None

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat completion request.

        Routes to appropriate provider based on model prefix.
        """
        self._request_count += 1

        provider = self._route_model(request.model)
        if provider is None:
            self._error_count += 1
            raise ValueError(
                f"No provider found for model: {request.model}. "
                f"Available prefixes: {[p.prefix for p in self._providers.values() if p.enabled]}"
            )

        logger.debug(f"Routing {request.model} to provider {provider.name}")

        try:
            response = await provider.adapter.complete(request)
            return response
        except Exception as e:
            self._error_count += 1
            logger.error(f"Provider {provider.name} error: {e}")
            raise

    def health_check(self) -> dict[str, Any]:
        """Return comprehensive health status."""
        provider_health = {
            name: config.adapter.health_check()
            for name, config in self._providers.items()
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
        }


def create_app(
    gateway: Optional[MorpheusGateway] = None,
    mock: bool = False,
) -> Any:
    """
    Create FastAPI application for Morpheus Gateway.

    Args:
        gateway: Pre-configured gateway (creates default if None)
        mock: If True, use MockAdapter for testing

    Returns:
        FastAPI application
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
    except ImportError:
        raise ImportError(
            "FastAPI not installed. Install with: pip install fastapi uvicorn"
        )

    app = FastAPI(
        title="Morpheus Gateway",
        description="OpenAI-compatible LLM router for kgents",
        version="1.0.0",
    )

    # Initialize gateway
    if gateway is None:
        gateway = MorpheusGateway()

        # Register Claude CLI adapter by default
        if mock:
            adapter: Adapter = MockAdapter()
        else:
            adapter = ClaudeCLIAdapter()

        gateway.register_provider(
            name="claude-cli",
            adapter=adapter,
            prefix="claude-",  # Route claude-* models to CLI
        )

    @app.post("/v1/chat/completions")
    async def chat_completions(body: dict[str, Any]) -> JSONResponse:
        """OpenAI-compatible chat completion endpoint."""
        try:
            request = ChatRequest.from_dict(body)
            response = await gateway.chat_completion(request)
            return JSONResponse(content=response.to_dict())
        except ValueError as e:
            error = MorpheusError(
                message=str(e),
                type="invalid_request_error",
            )
            return JSONResponse(content=error.to_dict(), status_code=400)
        except Exception as e:
            logger.exception("Chat completion failed")
            error = MorpheusError(
                message=f"Internal error: {str(e)}",
                type="server_error",
            )
            return JSONResponse(content=error.to_dict(), status_code=500)

    @app.get("/health")
    async def health() -> JSONResponse:
        """Health check endpoint."""
        health_data = gateway.health_check()
        status_code = 200 if health_data["status"] == "healthy" else 503
        return JSONResponse(content=health_data, status_code=status_code)

    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        return {
            "name": "Morpheus Gateway",
            "version": "1.0.0",
            "description": "OpenAI-compatible LLM router for kgents",
            "endpoints": {
                "chat": "POST /v1/chat/completions",
                "health": "GET /health",
            },
        }

    return app


def main() -> None:
    """Run Morpheus Gateway server."""
    import os

    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn not installed. Install with: pip install uvicorn")

    port = int(os.environ.get("MORPHEUS_PORT", "8080"))
    host = os.environ.get("MORPHEUS_HOST", "0.0.0.0")

    logger.info(f"Starting Morpheus Gateway on {host}:{port}")

    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
