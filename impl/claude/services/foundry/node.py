"""
Foundry AGENTESE Node: @node("self.foundry")

Wraps AgentFoundry as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.foundry.manifest  - Foundry status (cache size, forges, etc.)
- self.foundry.forge     - Forge new ephemeral agent from intent
- self.foundry.inspect   - Inspect agent capabilities
- self.foundry.cache     - Cache operations (list, get, evict)
- self.foundry.promote   - Promote ephemeral to permanent (Phase 5)

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    CacheRequest,
    CacheResponse,
    ForgeRequest,
    ForgeResponse,
    FoundryManifestResponse,
    InspectRequest,
    InspectResponse,
    PromoteRequest,
    PromoteResponse,
)
from .core import AgentFoundry

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class FoundryManifestRendering:
    """Rendering for foundry status manifest."""

    response: FoundryManifestResponse

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class ForgeRendering:
    """Rendering for forge operation result."""

    response: ForgeResponse

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        if not self.response.success:
            return f"Forge failed: {self.response.error}"

        lines = [
            "Forge Result",
            "============",
            f"Cache Key: {self.response.cache_key}",
            f"Target: {self.response.target}",
            f"Reality: {self.response.reality}",
            f"Artifact Type: {self.response.artifact_type}",
        ]

        if self.response.stability_score is not None:
            lines.append(f"Stability: {self.response.stability_score:.1%}")

        if self.response.forced:
            lines.append(f"Forced: {self.response.reason}")

        lines.append("")
        lines.append("Artifact:")
        lines.append("---------")

        artifact = self.response.artifact
        if isinstance(artifact, str):
            # Truncate if too long
            if len(artifact) > 500:
                lines.append(artifact[:500] + "\n... (truncated)")
            else:
                lines.append(artifact)
        elif isinstance(artifact, list):
            lines.append(f"[{len(artifact)} manifests]")
        else:
            lines.append(str(artifact))

        return "\n".join(lines)


@dataclass(frozen=True)
class InspectRendering:
    """Rendering for inspect operation result."""

    response: InspectResponse

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        if not self.response.found:
            return f"Agent not found: {self.response.agent_name}"

        lines = [
            f"Agent: {self.response.agent_name}",
            "=" * (7 + len(self.response.agent_name or "")),
        ]

        if self.response.is_ephemeral:
            lines.append("Type: Ephemeral (JIT)")
        else:
            lines.append("Type: Registered")

        if self.response.aspects:
            lines.append(f"Aspects: {', '.join(self.response.aspects)}")

        if self.response.halo:
            lines.append(f"Capabilities: {len(self.response.halo)}")

        if self.response.cache_metrics:
            metrics = self.response.cache_metrics
            lines.append("")
            lines.append("Cache Metrics:")
            lines.append(f"  Invocations: {metrics.get('invocation_count', 0)}")
            lines.append(f"  Success Rate: {metrics.get('success_rate', 1.0):.1%}")

        return "\n".join(lines)


@dataclass(frozen=True)
class CacheRendering:
    """Rendering for cache operation result."""

    response: CacheResponse

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        if not self.response.success:
            return f"Cache operation failed: {self.response.error}"

        lines = [f"Cache {self.response.action.title()}"]
        lines.append("=" * (6 + len(self.response.action)))

        if self.response.action == "list":
            entries = self.response.entries or []
            lines.append(f"Total: {len(entries)} entries")
            lines.append("")
            for entry in entries[:10]:
                intent = entry.get("intent", "?")[:40]
                target = entry.get("target", "?")
                lines.append(f"  [{entry.get('key', '?')[:8]}] {intent}... -> {target}")
            if len(entries) > 10:
                lines.append(f"  ... and {len(entries) - 10} more")

        elif self.response.action == "get":
            if self.response.entry:
                entry = self.response.entry
                lines.append(f"Key: {entry.get('key')}")
                lines.append(f"Intent: {entry.get('intent')}")
                lines.append(f"Target: {entry.get('target')}")
            else:
                lines.append("Entry not found")

        elif self.response.action in ("evict", "clear", "evict_expired"):
            lines.append(f"Evicted: {self.response.evicted_count} entries")

        return "\n".join(lines)


# =============================================================================
# AGENTESE Node
# =============================================================================


@node(
    "self.foundry",
    description="Agent Foundry - JIT agent synthesis and projection",
    dependencies=("foundry_service",),
    contracts={
        "manifest": Response(FoundryManifestResponse),
        "forge": Contract(ForgeRequest, ForgeResponse),
        "inspect": Contract(InspectRequest, InspectResponse),
        "cache": Contract(CacheRequest, CacheResponse),
        "promote": Contract(PromoteRequest, PromoteResponse),
    },
    examples=[
        ("forge", {"intent": "parse CSV files"}, "Create CSV parser agent"),
        ("forge", {"intent": "validate JSON schema"}, "Create JSON validator"),
        ("inspect", {"agent_name": "my-agent"}, "Inspect agent capabilities"),
        ("cache", {"action": "list"}, "List cached ephemeral agents"),
    ],
)
class FoundryNode(BaseLogosNode):
    """
    AGENTESE node for Agent Foundry Crown Jewel.

    Provides universal access to the Foundry via any transport:
    - CLI: kg foundry forge "parse CSV files"
    - HTTP: POST /agentese/self.foundry:forge
    - WebSocket: {"path": "self.foundry", "aspect": "forge", ...}
    """

    def __init__(self, foundry_service: AgentFoundry) -> None:
        """
        Initialize with injected dependency.

        Args:
            foundry_service: The AgentFoundry instance (injected by container)
        """
        self._foundry = foundry_service

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return "self.foundry"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Developer/Admin: Full access
        Guest: forge and inspect only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("forge", "inspect", "cache", "promote")

        # Guest users can forge and inspect
        return ("forge", "inspect")

    async def manifest(
        self, observer: "Observer | Umwelt[Any, Any]"
    ) -> Renderable:
        """
        Show foundry status to observer.

        Returns cache size, recent forges, hit rate, etc.
        """
        response = self._foundry.manifest()
        return FoundryManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to Foundry methods."""
        match aspect:
            case "forge":
                # Build ForgeRequest from kwargs
                request = ForgeRequest(
                    intent=kwargs.get("intent", ""),
                    context=kwargs.get("context", {}),
                    target_override=kwargs.get("target_override"),
                    entropy_budget=kwargs.get("entropy_budget", 1.0),
                )
                response = await self._foundry.forge(request)
                return ForgeRendering(response=response).to_dict()

            case "inspect":
                request = InspectRequest(
                    agent_name=kwargs.get("agent_name", ""),
                    include_source=kwargs.get("include_source", False),
                )
                response = await self._foundry.inspect(request)
                return InspectRendering(response=response).to_dict()

            case "cache":
                request = CacheRequest(
                    action=kwargs.get("action", "list"),
                    key=kwargs.get("key"),
                )
                response = await self._foundry.handle_cache(request)
                return CacheRendering(response=response).to_dict()

            case "promote":
                request = PromoteRequest(
                    cache_key=kwargs.get("cache_key", ""),
                    agent_name=kwargs.get("agent_name", ""),
                    description=kwargs.get("description"),
                )
                response = await self._foundry.promote(request)
                return response.to_dict()

            case _:
                return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "FoundryNode",
    "FoundryManifestRendering",
    "ForgeRendering",
    "InspectRendering",
    "CacheRendering",
]
