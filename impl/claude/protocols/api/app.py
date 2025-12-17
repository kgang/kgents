"""
FastAPI Application for kgents SaaS API Service.

Main application factory that:
- Creates FastAPI app
- Registers routes (Soul, AGENTESE, Sessions)
- Adds middleware (CORS, Tenant Context, Metering)
- Configures health checks
- Provides multi-tenant support
- Mounts AGENTESE Universal Gateway (AD-009)

The Metaphysical Fullstack Pattern:
- The protocol IS the API
- All transports collapse to logos.invoke(path, observer, ...)
- Service nodes are auto-exposed via gateway
"""

from __future__ import annotations

import logging
from typing import Any, Optional

# Graceful FastAPI import
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import RedirectResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None  # type: ignore[misc, assignment]
    CORSMiddleware = None  # type: ignore[misc, assignment]
    RedirectResponse = None  # type: ignore[misc, assignment]

from agents.k.soul import KgentSoul

from .auth import ApiKeyData, TenantContextMiddleware, get_optional_api_key
from .metering import MeteringMiddleware
from .models import HealthResponse
from .soul import create_soul_router

logger = logging.getLogger(__name__)

# SaaS infrastructure (optional)
try:
    from protocols.config import (
        get_saas_clients,
        init_saas_clients,
        shutdown_saas_clients,
    )

    HAS_SAAS_CONFIG = True
except ImportError:
    HAS_SAAS_CONFIG = False
    get_saas_clients = None  # type: ignore[assignment]
    init_saas_clients = None  # type: ignore[assignment]
    shutdown_saas_clients = None  # type: ignore[assignment]


def create_app(
    title: str = "kgents SaaS API",
    version: str = "v1",
    description: str = "Multi-tenant AGENTESE and K-gent Soul API",
    enable_cors: bool = True,
    enable_tenant_middleware: bool = True,
) -> "FastAPI":
    """
    Create and configure FastAPI application.

    Args:
        title: API title
        version: API version
        description: API description
        enable_cors: Whether to enable CORS
        enable_tenant_middleware: Whether to enable tenant context middleware

    Returns:
        Configured FastAPI app

    Raises:
        ImportError: If FastAPI is not installed
    """
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI is not installed. Install with: pip install fastapi uvicorn"
        )

    # Create app
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict this
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add tenant context middleware (sets tenant from API key)
    if enable_tenant_middleware:
        app.add_middleware(TenantContextMiddleware)

    # Add metering middleware
    app.add_middleware(MeteringMiddleware)

    # Register routers
    # Soul endpoints
    soul_router = create_soul_router()
    if soul_router is not None:
        app.include_router(soul_router)

    # AGENTESE endpoints
    from .agentese import create_agentese_router

    agentese_router = create_agentese_router()
    if agentese_router is not None:
        app.include_router(agentese_router)

    # K-gent Sessions endpoints
    from .sessions import create_sessions_router

    sessions_router = create_sessions_router()
    if sessions_router is not None:
        app.include_router(sessions_router)

    # AGENTESE Universal Protocol (AUP) endpoints
    from .aup import create_aup_router

    aup_router = create_aup_router()
    if aup_router is not None:
        app.include_router(aup_router)

    # Webhook endpoints (Stripe → OpenMeter bridge)
    from .webhooks import create_webhooks_router

    webhooks_router = create_webhooks_router()
    if webhooks_router is not None:
        app.include_router(webhooks_router)

    # Prometheus metrics endpoint
    from .metrics import create_metrics_router

    metrics_router = create_metrics_router()
    if metrics_router is not None:
        app.include_router(metrics_router)

    # N-Phase Session endpoints (not yet AGENTESE-ified)
    from .nphase import create_nphase_router

    nphase_router = create_nphase_router()
    if nphase_router is not None:
        app.include_router(nphase_router)

    # Workshop endpoints (not yet AGENTESE-ified)
    from .workshop import create_workshop_router

    workshop_router = create_workshop_router()
    if workshop_router is not None:
        app.include_router(workshop_router)

    # Gallery endpoints (Projection Component Gallery - keep for now)
    from .gallery import create_gallery_router

    gallery_router = create_gallery_router()
    if gallery_router is not None:
        app.include_router(gallery_router)

    # Brain WebSocket (real-time updates - keep for now)
    from .brain_websocket import create_brain_websocket_router

    brain_ws_router = create_brain_websocket_router()
    if brain_ws_router is not None:
        app.include_router(brain_ws_router)

    # Gestalt endpoints (Living Architecture Visualizer - not yet AGENTESE-ified)
    from .gestalt import create_gestalt_router

    gestalt_router = create_gestalt_router()
    if gestalt_router is not None:
        app.include_router(gestalt_router)

    # Infrastructure endpoints (Gestalt Live - not yet AGENTESE-ified)
    from .infrastructure import create_infrastructure_router

    infrastructure_router = create_infrastructure_router()
    if infrastructure_router is not None:
        app.include_router(infrastructure_router)

    # Gardener endpoints (not yet AGENTESE-ified)
    from .gardener import create_gardener_router

    gardener_router = create_gardener_router()
    if gardener_router is not None:
        app.include_router(gardener_router)

    # === AGENTESE Universal Gateway (AD-009) ===
    # The protocol IS the API - auto-exposes all @node registered services
    try:
        from protocols.agentese.container import get_container
        from protocols.agentese.gateway import mount_gateway

        container = get_container()
        gateway = mount_gateway(
            app,
            prefix="/agentese",
            container=container,
            enable_streaming=True,
            enable_websocket=True,
            fallback_to_logos=True,
        )
        logger.info(f"AGENTESE Gateway mounted at /agentese")
    except ImportError as e:
        logger.warning(f"Could not mount AGENTESE Gateway: {e}")

    # === Morpheus Legacy Redirect ===
    # Redirect /v1/chat/completions to AGENTESE path (307 preserves POST method)
    @app.api_route("/v1/chat/completions", methods=["POST", "GET"], tags=["legacy"])
    async def legacy_chat_completions() -> RedirectResponse:
        """
        Legacy OpenAI-compatible endpoint.

        Redirects to AGENTESE protocol: /agentese/world/morpheus/complete
        Uses 307 to preserve POST method and body.

        Deprecated: Use /agentese/world/morpheus/complete directly.
        """
        return RedirectResponse(
            url="/agentese/world/morpheus/complete",
            status_code=307,
            headers={
                "Deprecation": "true",
                "Sunset": "2025-06-01",
                "Link": '</agentese/world/morpheus/complete>; rel="successor-version"',
            },
        )

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health_check(
        api_key: Optional[ApiKeyData] = None,
    ) -> HealthResponse:
        """
        Health check endpoint.

        Returns service status and component health.
        No authentication required.

        Returns:
            Health status
        """
        # Check if soul can be created
        soul_status = "ok"
        llm_status = "unknown"

        try:
            soul = KgentSoul()
            soul_status = "ok"
            llm_status = "ok" if soul.has_llm else "not_configured"
        except Exception as e:
            soul_status = f"error: {str(e)}"

        # Determine overall status
        status = "ok"
        if soul_status != "ok":
            status = "error"
        elif llm_status == "not_configured":
            status = "degraded"

        return HealthResponse(
            status=status,
            version=version,
            has_llm=llm_status == "ok",
            components={
                "soul": soul_status,
                "llm": llm_status,
                "auth": "ok",
                "metering": "ok",
            },
        )

    # SaaS infrastructure health endpoint
    @app.get("/health/saas", tags=["system"])
    async def saas_health_check() -> dict[str, Any]:
        """
        SaaS infrastructure health check.

        Returns status of NATS and OpenMeter clients.
        No authentication required.
        """
        if not HAS_SAAS_CONFIG or get_saas_clients is None:
            return {
                "status": "not_configured",
                "message": "SaaS infrastructure not available",
            }

        clients = get_saas_clients()
        health = await clients.health_check()

        # Determine overall status
        overall_status = "ok"
        if not clients.is_started:
            overall_status = "not_started"
        elif health.get("openmeter", {}).get("status") == "error":
            overall_status = "degraded"
        elif health.get("nats", {}).get("status") == "error":
            overall_status = "degraded"

        return {
            "status": overall_status,
            **health,
        }

    # === Service Provider Lifecycle ===
    @app.on_event("startup")
    async def startup_service_providers() -> None:
        """Initialize service providers on app startup."""
        try:
            from services.providers import setup_providers
            await setup_providers()
            logger.info("Service providers initialized")
        except ImportError as e:
            logger.warning(f"Could not initialize service providers: {e}")
        except Exception as e:
            logger.error(f"Error initializing service providers: {e}")

    # SaaS lifecycle events
    if HAS_SAAS_CONFIG and init_saas_clients is not None:

        @app.on_event("startup")
        async def startup_saas_clients() -> None:
            """Initialize SaaS infrastructure on app startup."""
            await init_saas_clients()

        @app.on_event("shutdown")
        async def shutdown_saas_clients_handler() -> None:
            """Shutdown SaaS infrastructure on app shutdown."""
            if shutdown_saas_clients is not None:
                await shutdown_saas_clients()

    # Root endpoint
    @app.get("/", tags=["system"])
    async def root() -> dict[str, Any]:
        """
        Root endpoint.

        Returns basic API information.
        """
        return {
            "name": title,
            "version": version,
            "description": description,
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                # === AGENTESE Gateway (Primary API) ===
                "gateway": {
                    "discover": "GET /agentese/discover",
                    "manifest": "GET /agentese/{context}/{holon}/manifest",
                    "invoke": "POST /agentese/{context}/{holon}/{aspect}",
                    "affordances": "GET /agentese/{context}/{holon}/affordances",
                    "stream": "GET /agentese/{context}/{holon}/{aspect}/stream (SSE)",
                    "websocket": "WS /agentese/ws/{context}/{holon}",
                },
                # === Crown Jewels (via AGENTESE Gateway) ===
                "brain": {
                    "manifest": "GET /agentese/self/memory/manifest",
                    "capture": "POST /agentese/self/memory/capture",
                    "search": "POST /agentese/self/memory/search",
                    "topology": "GET /agentese/self/memory/topology",
                },
                "town": {
                    "manifest": "GET /agentese/world/town/manifest",
                    "citizen_list": "POST /agentese/world/town/citizen/list",
                    "citizen_get": "POST /agentese/world/town/citizen/get",
                    "converse": "POST /agentese/world/town/converse",
                    "inhabit": "/agentese/world/town/inhabit/*",
                },
                "atelier": {
                    "manifest": "GET /agentese/world/atelier/manifest",
                    "workshop": "/agentese/world/atelier/workshop/*",
                    "artisan": "/agentese/world/atelier/artisan/*",
                    "contribute": "POST /agentese/world/atelier/contribute",
                    "exhibition": "/agentese/world/atelier/exhibition/*",
                    "gallery": "/agentese/world/atelier/gallery/*",
                },
                "park": {
                    "manifest": "GET /agentese/world/park/manifest",
                    "host": "/agentese/world/park/host/*",
                    "episode": "/agentese/world/park/episode/*",
                    "location": "/agentese/world/park/location/*",
                },
                "morpheus": {
                    "manifest": "GET /agentese/world/morpheus/manifest",
                    "complete": "POST /agentese/world/morpheus/complete",
                    "providers": "GET /agentese/world/morpheus/providers",
                    "health": "GET /agentese/world/morpheus/health",
                    "legacy": "POST /v1/chat/completions (307 redirect)",
                },
                # === Non-AGENTESE Endpoints ===
                "soul": {
                    "governance": "/v1/soul/governance",
                    "dialogue": "/v1/soul/dialogue",
                },
                "kgent": {
                    "sessions": "/v1/kgent/sessions",
                    "messages": "/v1/kgent/sessions/{id}/messages",
                },
                "webhooks": {
                    "stripe": "/webhooks/stripe",
                    "stripe_health": "/webhooks/stripe/health",
                },
                "nphase": {
                    "sessions": "GET /v1/nphase/sessions",
                    "create": "POST /v1/nphase/sessions",
                    "advance": "POST /v1/nphase/sessions/{id}/advance",
                },
                "workshop": {
                    "get": "GET /v1/workshop",
                    "stream": "GET /v1/workshop/stream",
                    "status": "GET /v1/workshop/status",
                },
                "gallery": {
                    "all": "GET /api/gallery",
                    "categories": "GET /api/gallery/categories",
                },
                "gestalt": {
                    "manifest": "GET /v1/world/codebase/manifest",
                    "health": "GET /v1/world/codebase/health",
                    "topology": "GET /v1/world/codebase/topology",
                },
                "infrastructure": {
                    "status": "GET /api/infra/status",
                    "topology": "GET /api/infra/topology",
                    "topology_stream": "GET /api/infra/topology/stream (SSE)",
                },
                "websocket": {
                    "brain": "WS /ws/brain",
                    "town": "WS /ws/town/{town_id}",
                },
            },
        }

    return app


# --- CLI Entry Point ---


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """
    Run the Soul API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn is not installed. Install with: pip install uvicorn")

    app = create_app()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    # Run server if executed directly
    run_server(reload=True)
