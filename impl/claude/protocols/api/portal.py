"""
Portal REST API: Frontend endpoints for portal URI resolution.

Provides:
- POST /api/portal/resolve - Resolve a portal URI

The portal system provides universal resource addressing for all kgents concepts.
Every resource is addressable. Every address is expandable.

See: spec/protocols/portal-resource-system.md
"""

from __future__ import annotations

import logging
from typing import Any, Optional

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class ResolvePortalRequest(BaseModel):
    """Request body for resolving a portal URI."""

    uri: str = Field(..., description="Portal URI to resolve (e.g., 'chat:session-123', 'file:spec/README.md')")


class ResolvedResourceResponse(BaseModel):
    """Response for a resolved portal resource."""

    uri: str = Field(..., description="Original URI")
    resource_type: str = Field(..., description="Type of resource (file, chat, mark, etc.)")
    exists: bool = Field(..., description="Whether the resource exists")
    title: str = Field(..., description="Display title")
    preview: str = Field(..., description="Short preview text")
    content: Any = Field(..., description="Full content (type varies by resource)")
    actions: list[str] = Field(..., description="Available actions (expand, edit, etc.)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Resource-specific metadata")


class PortalErrorResponse(BaseModel):
    """Error response for portal resolution failures."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    uri: str = Field(..., description="Original URI that failed")


# =============================================================================
# Router Factory
# =============================================================================


def create_portal_router() -> "APIRouter | None":
    """Create the portal API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/portal", tags=["portal"])

    @router.post("/resolve", response_model=ResolvedResourceResponse)
    async def resolve_portal(request: ResolvePortalRequest) -> ResolvedResourceResponse:
        """
        Resolve a portal URI to a resource.

        Accepts a portal URI string and returns the resolved resource with metadata,
        preview, and full content for expansion.

        Supported resource types:
        - file: Files and paths
        - chat: Chat sessions
        - turn: Specific chat turns
        - mark: ChatMarks with constitutional scores
        - crystal: Memory crystals
        - trace: PolicyTraces
        - evidence: Evidence bundles
        - constitutional: Constitutional scores

        Args:
            request: Resolution request with URI

        Returns:
            Resolved resource with metadata and content

        Raises:
            400: Malformed URI
            404: Resource not found
            403: Permission denied
            500: Resolution error
        """
        try:
            from services.portal import (
                PermissionDenied,
                PortalResolverRegistry,
                PortalURI,
                ResourceNotFound,
                UnknownResourceType,
            )
            from services.portal.resolvers import (
                ChatResolver,
                ConstitutionalResolver,
                CrystalResolver,
                EvidenceResolver,
                FileResolver,
                MarkResolver,
                TraceResolver,
            )
            from pathlib import Path

            # Parse URI
            try:
                uri = PortalURI.parse(request.uri)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Malformed URI: {str(e)}",
                )

            # Set up resolver registry
            registry = PortalResolverRegistry()

            # Register all resolvers
            # FileResolver needs base_path (use cwd for now)
            registry.register(FileResolver(base_path=Path.cwd()))

            # ChatResolver needs session_store (try to get it, but make it optional)
            try:
                from services.providers import get_chat_session_store
                session_store = await get_chat_session_store()
                registry.register(ChatResolver(session_store=session_store))
            except Exception as e:
                logger.warning(f"Could not register ChatResolver: {e}")

            # Register other resolvers (they don't need dependencies)
            registry.register(MarkResolver())
            registry.register(TraceResolver())
            registry.register(EvidenceResolver())
            registry.register(ConstitutionalResolver())
            registry.register(CrystalResolver())

            # Resolve through registry
            # Observer is None for now (no access control)
            observer = None

            try:
                resource = await registry.resolve(uri, observer)
            except UnknownResourceType as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown resource type: {uri.resource_type}",
                )
            except ResourceNotFound as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"Resource not found: {request.uri}",
                )
            except PermissionDenied as e:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {str(e)}",
                )

            # Convert to response model
            return ResolvedResourceResponse(
                uri=resource.uri,
                resource_type=resource.resource_type,
                exists=resource.exists,
                title=resource.title,
                preview=resource.preview,
                content=resource.content,
                actions=resource.actions,
                metadata=resource.metadata,
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.exception("Error resolving portal URI")
            raise HTTPException(
                status_code=500,
                detail=f"Resolution error: {str(e)}",
            )

    @router.get("/health")
    async def portal_health() -> dict[str, Any]:
        """
        Health check for portal resolver system.

        Returns:
            Health status with registered resolver types
        """
        try:
            from services.portal import PortalResolverRegistry
            from services.portal.resolvers import (
                ChatResolver,
                ConstitutionalResolver,
                CrystalResolver,
                EvidenceResolver,
                FileResolver,
                MarkResolver,
                TraceResolver,
            )
            from pathlib import Path

            registry = PortalResolverRegistry()

            # Register all resolvers
            registered_types = []

            try:
                registry.register(FileResolver(base_path=Path.cwd()))
                registered_types.append("file")
            except Exception as e:
                logger.warning(f"FileResolver registration failed: {e}")

            try:
                from services.providers import get_chat_session_store
                session_store = await get_chat_session_store()
                registry.register(ChatResolver(session_store=session_store))
                registered_types.append("chat")
            except Exception as e:
                logger.warning(f"ChatResolver registration failed: {e}")

            # Register other resolvers
            for resolver_cls, resource_type in [
                (MarkResolver, "mark"),
                (TraceResolver, "trace"),
                (EvidenceResolver, "evidence"),
                (ConstitutionalResolver, "constitutional"),
                (CrystalResolver, "crystal"),
            ]:
                try:
                    registry.register(resolver_cls())
                    registered_types.append(resource_type)
                except Exception as e:
                    logger.warning(f"{resolver_cls.__name__} registration failed: {e}")

            return {
                "status": "ok",
                "registered_types": registered_types,
                "total_resolvers": len(registered_types),
            }

        except Exception as e:
            logger.exception("Error in portal health check")
            return {
                "status": "error",
                "error": str(e),
            }

    return router


__all__ = ["create_portal_router"]
