"""
Morpheus AGENTESE Node: @node("world.morpheus")

Wraps MorpheusPersistence as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.morpheus.manifest   - Gateway health status
- world.morpheus.complete   - Chat completion (non-streaming)
- world.morpheus.stream     - Chat completion (streaming)
- world.morpheus.providers  - List available providers
- world.morpheus.metrics    - Request/error counts
- world.morpheus.health     - Provider health checks
- world.morpheus.route      - Model routing info

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Observer-Dependent Behavior:
- admin: See all providers, metrics, configure
- developer: See enabled providers, metrics
- guest: Basic completion only, public providers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    CompleteRequest,
    CompleteResponse,
    HealthResponse,
    MetricsResponse,
    MorpheusManifestResponse,
    ProvidersResponse,
    RateLimitResponse,
    RouteRequest,
    RouteResponse,
    StreamRequest,
    StreamResponse,
)
from .persistence import MorpheusPersistence, MorpheusStatus
from .types import ChatRequest

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Rendering Types ===


@dataclass(frozen=True)
class MorpheusManifestRendering:
    """Rendering for Morpheus status manifest."""

    status: MorpheusStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "morpheus_manifest",
            **self.status.to_dict(),
        }

    def to_text(self) -> str:
        lines = [
            "Morpheus Gateway",
            "================",
            f"Status: {'healthy' if self.status.healthy else 'degraded'}",
            f"Providers: {self.status.providers_healthy}/{self.status.providers_total}",
            f"Requests: {self.status.total_requests}",
            f"Errors: {self.status.total_errors}",
            f"Uptime: {self.status.uptime_seconds:.1f}s",
        ]
        if self.status.providers:
            lines.append("\nProviders:")
            for p in self.status.providers:
                status = "enabled" if p.enabled else "disabled"
                avail = "available" if p.available else "unavailable"
                lines.append(f"  {p.name}: {p.prefix}* ({status}, {avail})")
        return "\n".join(lines)


@dataclass(frozen=True)
class CompletionRendering:
    """Rendering for completion result."""

    response_text: str
    model: str
    provider: str
    latency_ms: float
    tokens: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "completion_result",
            "response": self.response_text,
            "model": self.model,
            "provider": self.provider,
            "latency_ms": self.latency_ms,
            "tokens": self.tokens,
        }

    def to_text(self) -> str:
        return self.response_text


@dataclass(frozen=True)
class ProvidersRendering:
    """Rendering for providers list."""

    providers: list[dict[str, Any]]
    filter_applied: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "providers_list",
            "filter": self.filter_applied,
            "count": len(self.providers),
            "providers": self.providers,
        }

    def to_text(self) -> str:
        if not self.providers:
            return "No providers available"
        lines = [f"Providers ({self.filter_applied}):"]
        for p in self.providers:
            lines.append(f"  {p['name']}: {p['prefix']}*")
        return "\n".join(lines)


# === MorpheusNode ===


@node(
    "world.morpheus",
    description="LLM Gateway - universal completion interface",
    dependencies=("morpheus_persistence",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(MorpheusManifestResponse),
        "providers": Response(ProvidersResponse),
        "metrics": Response(MetricsResponse),
        "health": Response(HealthResponse),
        "rate_limit": Response(RateLimitResponse),
        # Mutation aspects (Contract with request + response)
        "complete": Contract(CompleteRequest, CompleteResponse),
        "stream": Contract(StreamRequest, StreamResponse),
        "route": Contract(RouteRequest, RouteResponse),
    },
)
class MorpheusNode(BaseLogosNode):
    """
    AGENTESE node for Morpheus Gateway.

    Exposes MorpheusPersistence through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/morpheus/complete
        {"model": "claude-sonnet-4-20250514", "messages": [...]}

        # Via Logos directly
        await logos.invoke("world.morpheus.complete", observer, model="...", messages=[...])

        # Via CLI
        kg morpheus complete --model claude-sonnet-4-20250514 --message "Hello"
    """

    def __init__(self, morpheus_persistence: MorpheusPersistence) -> None:
        """
        Initialize MorpheusNode.

        Args:
            morpheus_persistence: The persistence layer (injected by container)
        """
        self._persistence = morpheus_persistence

    @property
    def handle(self) -> str:
        return "world.morpheus"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer-dependent:
        - admin/system: Full access including metrics and all providers
        - developer: Standard access with metrics
        - guest: Basic completion only, public providers
        """
        # Base operations available to all
        base = ("complete", "stream", "health")

        if archetype in ("admin", "system"):
            # Full access including configure
            return base + ("providers", "metrics", "route", "configure")
        elif archetype in ("developer",):
            # Standard dev access
            return base + ("providers", "metrics", "route")
        else:
            # Guest: basic completion only
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest Morpheus status to observer.

        AGENTESE: world.morpheus.manifest
        """
        if self._persistence is None:
            return BasicRendering(
                summary="Morpheus not initialized",
                content="No persistence layer configured",
                metadata={"error": "no_persistence"},
            )

        status = await self._persistence.manifest()
        return MorpheusManifestRendering(status=status)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to persistence methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._persistence is None:
            return {"error": "Morpheus persistence not configured"}

        # Get observer archetype for filtering and rate limiting
        archetype = self._get_archetype(observer)

        if aspect == "complete":
            return await self._handle_complete(kwargs, archetype)

        elif aspect == "stream":
            return await self._handle_stream(kwargs, archetype)

        elif aspect == "providers":
            return await self._handle_providers(archetype, kwargs)

        elif aspect == "metrics":
            return await self._handle_metrics(archetype)

        elif aspect == "health":
            return await self._persistence.health()

        elif aspect == "route":
            model = kwargs.get("model", "")
            if not model:
                return {"error": "model parameter required"}
            return await self._persistence.route_info(model)

        elif aspect == "rate_limit":
            return self._persistence.rate_limit_status(archetype)

        elif aspect == "configure":
            # Admin only - check archetype
            if archetype not in ("admin", "system"):
                return {"error": "Forbidden: admin access required"}
            return {"error": "configure not yet implemented"}

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_complete(self, kwargs: dict[str, Any], archetype: str) -> dict[str, Any]:
        """Handle completion request with rate limiting."""
        # Build ChatRequest from kwargs
        model = kwargs.get("model")
        messages = kwargs.get("messages", [])

        if not model:
            return {"error": "model parameter required"}
        if not messages:
            return {"error": "messages parameter required"}

        # Convert messages to ChatMessage format
        from .types import ChatMessage

        chat_messages = []
        for m in messages:
            if isinstance(m, dict):
                chat_messages.append(
                    ChatMessage(
                        role=m.get("role", "user"),
                        content=m.get("content", ""),
                        name=m.get("name"),
                    )
                )
            else:
                chat_messages.append(m)

        request = ChatRequest(
            model=model,
            messages=chat_messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )

        try:
            result = await self._persistence.complete(request, archetype)
        except Exception as e:
            return {"error": str(e)}

        # Get response text
        response_text = ""
        if result.response.choices:
            response_text = result.response.choices[0].message.content

        total_tokens = 0
        if result.response.usage:
            total_tokens = result.response.usage.total_tokens

        return CompletionRendering(
            response_text=response_text,
            model=model,
            provider=result.provider_name,
            latency_ms=result.latency_ms,
            tokens=total_tokens,
        ).to_dict()

    async def _handle_stream(self, kwargs: dict[str, Any], archetype: str) -> dict[str, Any]:
        """
        Handle streaming request.

        Returns an async generator wrapper for streaming chunks.
        """
        from .types import ChatMessage

        model = kwargs.get("model")
        messages = kwargs.get("messages", [])

        if not model:
            return {"error": "model parameter required"}
        if not messages:
            return {"error": "messages parameter required"}

        chat_messages = []
        for m in messages:
            if isinstance(m, dict):
                chat_messages.append(
                    ChatMessage(
                        role=m.get("role", "user"),
                        content=m.get("content", ""),
                        name=m.get("name"),
                    )
                )
            else:
                chat_messages.append(m)

        request = ChatRequest(
            model=model,
            messages=chat_messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )

        # Return a streaming wrapper
        # The caller is responsible for iterating over the stream
        async def stream_generator():
            async for chunk in self._persistence.stream(request, archetype):
                yield chunk

        return {
            "type": "stream",
            "model": model,
            "stream": stream_generator(),
        }

    async def _handle_providers(self, archetype: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle providers list with observer-dependent filtering."""
        # Filter based on observer archetype
        if archetype in ("admin", "system"):
            # Admin sees all providers
            providers = await self._persistence.list_providers()
            filter_applied = "all"
        elif archetype in ("developer",):
            # Developer sees enabled providers
            providers = await self._persistence.list_providers(enabled_only=True)
            filter_applied = "enabled"
        else:
            # Guest sees public providers only
            providers = await self._persistence.list_providers(enabled_only=True, public_only=True)
            filter_applied = "public"

        return ProvidersRendering(
            providers=[p.to_dict() for p in providers],
            filter_applied=filter_applied,
        ).to_dict()

    async def _handle_metrics(self, archetype: str) -> dict[str, Any]:
        """Handle metrics request (admin/developer only)."""
        if archetype not in ("admin", "system", "developer"):
            return {"error": "Forbidden: requires developer or admin access"}

        status = await self._persistence.manifest()
        return {
            "type": "morpheus_metrics",
            "total_requests": status.total_requests,
            "total_errors": status.total_errors,
            "error_rate": (
                status.total_errors / status.total_requests if status.total_requests > 0 else 0
            ),
            "uptime_seconds": status.uptime_seconds,
            "providers_healthy": status.providers_healthy,
            "providers_total": status.providers_total,
        }

    def _get_archetype(self, observer: "Observer | Umwelt[Any, Any]") -> str:
        """Extract archetype from observer."""
        if hasattr(observer, "archetype"):
            return observer.archetype
        if hasattr(observer, "agent") and hasattr(observer.agent, "archetype"):
            return observer.agent.archetype
        return "guest"


__all__ = [
    "MorpheusNode",
    "MorpheusManifestRendering",
    "CompletionRendering",
    "ProvidersRendering",
]
