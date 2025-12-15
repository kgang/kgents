"""
AGENTESE API Endpoints.

Exposes AGENTESE Logos resolver via REST API:
- POST /v1/agentese/invoke - Invoke an AGENTESE path
- GET /v1/agentese/resolve - Resolve path to node info
- GET /v1/agentese/affordances - List available affordances

Records usage to OpenMeter for billing when configured.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

# SaaS infrastructure (optional)
try:
    from protocols.config import get_saas_clients

    HAS_SAAS_CONFIG = True
except ImportError:
    HAS_SAAS_CONFIG = False
    get_saas_clients = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException, Request
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    BaseModel = object  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Request/Response Models ---


class InvokeRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request for invoking an AGENTESE path."""

    path: str = Field(
        ...,
        description="AGENTESE path to invoke (e.g., 'world.house.manifest')",
        examples=["self.soul.challenge", "world.document.manifest"],
    )
    observer: dict[str, Any] = Field(
        default_factory=lambda: {
            "name": "api_user",
            "archetype": "developer",
            "capabilities": [],
        },
        description="Observer Umwelt configuration",
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional arguments for the aspect",
        examples=[{"input": "test idea"}],
    )


class InvokeResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response from AGENTESE invocation."""

    path: str = Field(..., description="The path that was invoked")
    result: Any = Field(..., description="The result of the invocation")
    tokens_used: int = Field(
        default=0,
        ge=0,
        description="Number of tokens used (if LLM was involved)",
    )
    cached: bool = Field(
        default=False,
        description="Whether the result was from cache",
    )


class ResolveResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response from path resolution."""

    path: str = Field(..., description="The resolved path")
    handle: str = Field(..., description="The handle for this node")
    context: str = Field(..., description="The AGENTESE context (world, self, etc.)")
    affordances: list[str] = Field(
        default_factory=list,
        description="Available affordances for this node",
    )


class AffordancesResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response listing available affordances."""

    path: str = Field(..., description="The path being queried")
    affordances: list[str] = Field(..., description="Available affordances")
    observer_archetype: str = Field(..., description="Observer archetype used")


class ErrorResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Error response for AGENTESE operations."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    path: str = Field(default="", description="Path that caused the error")
    suggestion: str = Field(default="", description="Suggested fix")


# --- Router Factory ---


def create_agentese_router() -> "APIRouter":
    """
    Create AGENTESE API router.

    Returns:
        FastAPI router with AGENTESE endpoints

    Raises:
        ImportError: If FastAPI is not installed
    """
    if not HAS_FASTAPI:
        # Return a stub for when FastAPI is not available
        # This allows the module to be imported without FastAPI
        return None  # type: ignore[return-value]

    from dataclasses import dataclass, field
    from typing import Any as TAny

    from protocols.agentese.exceptions import (
        AffordanceError,
        ObserverRequiredError,
        PathNotFoundError,
        PathSyntaxError,
    )
    from protocols.agentese.logos import create_logos
    from protocols.tenancy.context import get_current_tenant

    from .auth import get_api_key, has_scope

    router = APIRouter(prefix="/v1/agentese", tags=["agentese"])

    # Shared Logos instance
    _logos = create_logos()

    @dataclass
    class _MockDNA:
        """Mock DNA for API Umwelt."""

        name: str = "api_user"
        archetype: str = "developer"
        capabilities: tuple[str, ...] = ()

    @dataclass
    class _MockUmwelt:
        """Minimal Umwelt for API invocations."""

        dna: _MockDNA = field(default_factory=_MockDNA)
        gravity: tuple[TAny, ...] = ()

    def _make_umwelt(observer_config: dict[str, Any]) -> _MockUmwelt:
        """Create a mock Umwelt from observer configuration."""
        dna = _MockDNA(
            name=observer_config.get("name", "api_user"),
            archetype=observer_config.get("archetype", "developer"),
            capabilities=tuple(observer_config.get("capabilities", [])),
        )
        return _MockUmwelt(dna=dna)

    @router.post(
        "/invoke",
        response_model=InvokeResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid path syntax"},
            403: {"model": ErrorResponse, "description": "Affordance not available"},
            404: {"model": ErrorResponse, "description": "Path not found"},
        },
    )
    async def invoke_path(
        request: InvokeRequest,
        api_key: "ApiKeyData" = Depends(get_api_key),
        http_request: Request = None,  # type: ignore
    ) -> InvokeResponse:
        """
        Invoke an AGENTESE path.

        The path must include an aspect (e.g., 'world.house.manifest').
        Observer configuration determines available affordances.

        Example:
            POST /v1/agentese/invoke
            {
                "path": "self.soul.challenge",
                "observer": {"name": "kent", "archetype": "developer"},
                "kwargs": {"input": "test idea"}
            }

        Returns:
            Invocation result with metadata
        """
        # Check scope
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope for AGENTESE invoke",
            )

        # Create observer Umwelt
        umwelt = _make_umwelt(request.observer)

        try:
            # Invoke the path
            # Cast to Any since _MockUmwelt satisfies Umwelt protocol at runtime
            from typing import cast

            result = await _logos.invoke(
                request.path,
                cast(Any, umwelt),
                **request.kwargs,
            )

            # Record usage if tenant context is set
            tenant = get_current_tenant()
            if tenant and http_request:
                from protocols.tenancy.models import UsageEventType
                from protocols.tenancy.service import TenantService

                service = TenantService()
                await service.record_usage(
                    tenant_id=tenant.id,
                    event_type=UsageEventType.AGENTESE_INVOKE,
                    source="api",
                    agentese_path=request.path,
                )

                # Record to OpenMeter for billing (async, non-blocking)
                if HAS_SAAS_CONFIG and get_saas_clients is not None:
                    asyncio.create_task(
                        _record_agentese_to_openmeter(
                            tenant_id=str(tenant.id),
                            path=request.path,
                        )
                    )

            # Handle result serialization
            serialized_result = result
            if hasattr(result, "to_dict"):
                serialized_result = result.to_dict()
            elif hasattr(result, "__dict__"):
                serialized_result = result.__dict__

            return InvokeResponse(
                path=request.path,
                result=serialized_result,
                tokens_used=0,  # Will be populated by LLM-backed paths
                cached=_logos.is_resolved(request.path),
            )

        except PathSyntaxError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid path: {e}",
            )
        except PathNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Path not found: {e}",
            )
        except AffordanceError as e:
            raise HTTPException(
                status_code=403,
                detail=f"Affordance not available: {e}. Available: {e.available}",
            )
        except ObserverRequiredError:
            raise HTTPException(
                status_code=400,
                detail="Observer required for this operation",
            )

    @router.get(
        "/resolve",
        response_model=ResolveResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid path syntax"},
            404: {"model": ErrorResponse, "description": "Path not found"},
        },
    )
    async def resolve_path(
        path: str,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> ResolveResponse:
        """
        Resolve an AGENTESE path to node info.

        Returns the handle and context for a path without invoking.

        Example:
            GET /v1/agentese/resolve?path=world.house

        Returns:
            Path resolution info
        """
        # Check scope
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        try:
            # Resolve path
            node = _logos.resolve(path)

            # Extract parts
            parts = path.split(".")
            context = parts[0] if parts else ""
            handle = getattr(node, "handle", path)

            # Get affordances
            from protocols.agentese.node import AgentMeta

            meta = AgentMeta(name="api_user", archetype="developer")
            affordances = node.affordances(meta) if hasattr(node, "affordances") else []

            return ResolveResponse(
                path=path,
                handle=handle,
                context=context,
                affordances=affordances,
            )

        except PathSyntaxError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except PathNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.get(
        "/affordances",
        response_model=AffordancesResponse,
        responses={
            404: {"model": ErrorResponse, "description": "Path not found"},
        },
    )
    async def list_affordances(
        path: str,
        archetype: str = "developer",
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> AffordancesResponse:
        """
        List available affordances for a path.

        Returns affordances based on the specified observer archetype.

        Example:
            GET /v1/agentese/affordances?path=world.house&archetype=architect

        Returns:
            List of available affordances
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        try:
            node = _logos.resolve(path)

            from protocols.agentese.node import AgentMeta

            meta = AgentMeta(name="api_user", archetype=archetype)
            affordances = node.affordances(meta) if hasattr(node, "affordances") else []

            return AffordancesResponse(
                path=path,
                affordances=affordances,
                observer_archetype=archetype,
            )

        except (PathSyntaxError, PathNotFoundError) as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router


async def _record_agentese_to_openmeter(
    tenant_id: str,
    path: str,
    tokens_used: int = 0,
) -> None:
    """
    Record AGENTESE invocation to OpenMeter for billing.

    Non-blocking helper that logs errors but doesn't raise.
    """
    try:
        clients = get_saas_clients()
        if clients.openmeter is not None:
            # Extract aspect from path (e.g., "self.soul.challenge" -> "challenge")
            aspect = path.split(".")[-1] if "." in path else path
            await clients.openmeter.record_agentese_invoke(
                tenant_id=tenant_id,
                path=path,
                aspect=aspect,
                tokens_used=tokens_used,
            )
    except Exception as e:
        logger.warning(f"Failed to record AGENTESE to OpenMeter: {e}")
