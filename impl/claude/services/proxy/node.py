"""
Proxy AGENTESE Node: @node("self.proxy")

Wraps ProxyHandleStore as an AGENTESE node for universal gateway access.

AD-015: Proxy Handles & Transparent Batch Processes

AGENTESE Paths:
- self.proxy.manifest     - Store status: handle counts, reactor state
- self.proxy.list         - List all proxy handles with status
- self.proxy.get          - Get a specific handle by source_type
- self.proxy.invalidate   - Mark a handle as stale (trigger recomputation)
- self.proxy.reactor      - Reactor status (event-driven invalidation)

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "The proof IS the decision. The mark IS the witness. The proxy IS the handle."

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/proxy-handle.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    GetHandleRequest,
    GetHandleResponse,
    HandleListRendering,
    HandleSummary,
    InvalidateRequest,
    InvalidateResponse,
    ListHandlesResponse,
    ProxyManifestRendering,
    ProxyManifestResponse,
    ReactorStatusResponse,
)
from .store import ProxyHandleStore, get_proxy_handle_store
from .types import SourceType

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# ProxyNode
# =============================================================================


@node(
    "self.proxy",
    description="Proxy Handle Crown Jewel - Epistemic hygiene for computed data",
    dependencies=("proxy_handle_store",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(ProxyManifestResponse),
        "list": Response(ListHandlesResponse),
        "reactor": Response(ReactorStatusResponse),
        # Action aspects (Contract with request + response)
        "get": Contract(GetHandleRequest, GetHandleResponse),
        "invalidate": Contract(InvalidateRequest, InvalidateResponse),
    },
    examples=[
        ("manifest", {}, "Get proxy store status"),
        ("list", {}, "List all handles"),
        ("get", {"source_type": "spec_corpus"}, "Get spec corpus handle"),
        ("invalidate", {"source_type": "spec_corpus"}, "Invalidate spec corpus"),
    ],
)
class ProxyNode(BaseLogosNode):
    """
    AGENTESE node for Proxy Handle Crown Jewel.

    Exposes ProxyHandleStore through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    AD-015: Every expensive computation produces a proxy handle—an independent
    artifact with its own identity, lifecycle, and provenance.

    Example:
        # Via AGENTESE
        await logos.invoke("self.proxy.manifest", observer)

        # Via HTTP
        GET /agentese/self/proxy/manifest

        # Via CLI
        kg invoke self.proxy.manifest
    """

    def __init__(
        self,
        proxy_handle_store: ProxyHandleStore | None = None,
    ) -> None:
        """Initialize ProxyNode with store (optional DI)."""
        self._store = proxy_handle_store or get_proxy_handle_store()

    @property
    def handle(self) -> str:
        return "self.proxy"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "list", "get", "invalidate", "reactor")

        # Read-only: architects, guests
        return ("manifest", "list", "get")

    # =========================================================================
    # Perception Aspects
    # =========================================================================

    @aspect(
        AspectCategory.PERCEPTION,
        description="Proxy store status: handle counts, reactor state",
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest proxy store status."""
        stats = self._store.stats()

        # Get reactor stats if available
        try:
            from .reactor import get_proxy_reactor

            reactor = get_proxy_reactor()
            reactor_stats = reactor.stats
        except Exception:
            reactor_stats = {
                "is_wired": False,
                "event_count": 0,
            }

        response = ProxyManifestResponse(
            total_handles=stats.total_handles,
            fresh_count=stats.fresh_count,
            stale_count=stats.stale_count,
            computing_count=stats.computing_count,
            error_count=stats.error_count,
            reactor_wired=reactor_stats.get("is_wired", False),
            reactor_event_count=reactor_stats.get("event_count", 0),
        )

        return ProxyManifestRendering(manifest=response)

    @aspect(
        AspectCategory.PERCEPTION,
        description="List all proxy handles with status",
    )
    async def list_handles(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """List all proxy handles."""
        handles = self._store.all()

        summaries = tuple(
            HandleSummary(
                handle_id=h.handle_id,
                source_type=h.source_type.value,
                human_label=h.human_label,
                status=h.status.value,
                is_fresh=h.is_fresh(),
                created_at=h.created_at.isoformat(),
                expires_at=h.expires_at.isoformat() if h.expires_at else None,
                access_count=h.access_count,
                computation_count=h.computation_count,
            )
            for h in handles
        )

        response = ListHandlesResponse(
            handles=summaries,
            total_count=len(summaries),
        )

        return HandleListRendering(response=response)

    @aspect(
        AspectCategory.PERCEPTION,
        description="Reactor status: event-driven invalidation",
    )
    async def reactor_status(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Get reactor status."""
        try:
            from .reactor import get_proxy_reactor

            reactor = get_proxy_reactor()
            stats = reactor.stats

            response = ReactorStatusResponse(
                is_wired=stats["is_wired"],
                trigger_count=stats["trigger_count"],
                subscription_count=stats["subscription_count"],
                event_count=stats["event_count"],
                invalidation_count=stats["invalidation_count"],
            )
        except Exception as e:
            response = ReactorStatusResponse(
                is_wired=False,
                trigger_count=0,
                subscription_count=0,
                event_count=0,
                invalidation_count=0,
            )

        return BasicRendering(
            summary="Reactor status",
            metadata=response.to_dict(),
        )

    # =========================================================================
    # Action Aspects
    # =========================================================================

    @aspect(
        AspectCategory.MUTATION,
        description="Get a specific handle by source_type",
    )
    async def get_handle(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        source_type: str = "",
        **kwargs: Any,
    ) -> Renderable:
        """Get a specific proxy handle."""
        if not source_type:
            return BasicRendering(
                summary="source_type is required",
                metadata=GetHandleResponse(found=False, error="source_type is required").to_dict(),
            )

        try:
            st = SourceType(source_type)
        except ValueError:
            error_msg = (
                f"Invalid source_type: {source_type}. Valid types: {[s.value for s in SourceType]}"
            )
            return BasicRendering(
                summary=error_msg,
                metadata=GetHandleResponse(found=False, error=error_msg).to_dict(),
            )

        handle = await self._store.get(st)
        if handle is None:
            error_msg = f"No handle for source_type: {source_type}. Use `compute` to create one."
            return BasicRendering(
                summary=error_msg,
                metadata=GetHandleResponse(found=False, error=error_msg).to_dict(),
            )

        handle_summary = HandleSummary(
            handle_id=handle.handle_id,
            source_type=handle.source_type.value,
            human_label=handle.human_label,
            status=handle.status.value,
            is_fresh=handle.is_fresh(),
            created_at=handle.created_at.isoformat(),
            expires_at=handle.expires_at.isoformat() if handle.expires_at else None,
            access_count=handle.access_count,
            computation_count=handle.computation_count,
        )

        return BasicRendering(
            summary=f"Handle '{source_type}': {handle.status.value}",
            metadata=GetHandleResponse(found=True, handle=handle_summary).to_dict(),
        )

    @aspect(
        AspectCategory.MUTATION,
        description="Mark a handle as stale (triggers recomputation on next access)",
    )
    async def invalidate(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        source_type: str = "",
        **kwargs: Any,
    ) -> Renderable:
        """Invalidate a proxy handle."""
        if not source_type:
            return BasicRendering(
                summary="source_type is required",
                metadata=InvalidateResponse(
                    success=False, source_type="", message="source_type is required"
                ).to_dict(),
            )

        try:
            st = SourceType(source_type)
        except ValueError:
            error_msg = (
                f"Invalid source_type: {source_type}. Valid types: {[s.value for s in SourceType]}"
            )
            return BasicRendering(
                summary=error_msg,
                metadata=InvalidateResponse(
                    success=False, source_type=source_type, message=error_msg
                ).to_dict(),
            )

        # Check if handle exists before invalidating
        handle = await self._store.get(st)
        was_fresh = handle.is_fresh() if handle else False

        # Invalidate
        success = await self._store.invalidate(st)

        if success:
            msg = f"Handle '{source_type}' marked as stale. Next access will trigger recomputation."
            return BasicRendering(
                summary=msg,
                metadata=InvalidateResponse(
                    success=True, source_type=source_type, was_fresh=was_fresh, message=msg
                ).to_dict(),
            )
        else:
            msg = f"No handle found for '{source_type}' to invalidate."
            return BasicRendering(
                summary=msg,
                metadata=InvalidateResponse(
                    success=False, source_type=source_type, message=msg
                ).to_dict(),
            )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ["ProxyNode"]
