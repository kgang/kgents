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
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

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

logger = logging.getLogger(__name__)


# AD-015: Removed _warm_ledger_cache() (2025-12-23)
# Analysis is a build step, not a runtime step.
# Use `kg spec analyze` to pre-compute, server loads artifacts.
# See spec/principles.md AD-015: Explicit Upload-and-Copy Data Model

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


@asynccontextmanager
async def _create_lifespan(
    enable_saas: bool = True,
) -> AsyncIterator[None]:
    """
    FastAPI lifespan context manager.

    Handles startup and shutdown events without deprecated on_event decorators.
    See: https://fastapi.tiangolo.com/advanced/events/#lifespan

    Args:
        enable_saas: Whether to initialize SaaS infrastructure clients.
    """
    # === STARTUP ===
    # Initialize service providers
    try:
        from services.providers import setup_providers

        await setup_providers()
        logger.info("Service providers initialized")
    except ImportError as e:
        logger.warning(f"Could not initialize service providers: {e}")
    except Exception as e:
        logger.error(f"Error initializing service providers: {e}")

    # AD-015: Spec ledger warming REMOVED (2025-12-23)
    # Analysis is a build step, not a runtime step.
    # Server loads pre-computed artifacts; no startup computation.

    # Initialize SaaS clients if configured
    if enable_saas and HAS_SAAS_CONFIG and init_saas_clients is not None:
        await init_saas_clients()

    yield  # App runs here

    # === SHUTDOWN ===
    # Shutdown SaaS clients
    if enable_saas and HAS_SAAS_CONFIG and shutdown_saas_clients is not None:
        await shutdown_saas_clients()


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
        raise ImportError("FastAPI is not installed. Install with: pip install fastapi uvicorn")

    # Create lifespan context manager
    @asynccontextmanager
    async def lifespan(app: "FastAPI") -> AsyncIterator[None]:
        async with _create_lifespan(enable_saas=HAS_SAAS_CONFIG):
            yield

    # Create app with lifespan (replaces deprecated on_event)
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add CORS middleware
    if enable_cors:
        # CORS_ALLOW_ALL=1 enables permissive mode for local development
        # In production, use CORS_ORIGINS to specify allowed origins
        if os.getenv("CORS_ALLOW_ALL", "").lower() in ("1", "true", "yes"):
            # Local development: allow all origins (no credentials for safety)
            cors_origins = ["*"]
            allow_credentials = False
        else:
            # Production: explicit origins from env, default to localhost
            origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
            cors_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
            allow_credentials = True

        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add tenant context middleware (sets tenant from API key)
    if enable_tenant_middleware:
        app.add_middleware(TenantContextMiddleware)

    # Add metering middleware
    app.add_middleware(MeteringMiddleware)

    # Register routers
    # === Soul endpoints REMOVED (AD-009 Phase 2 Router Consolidation) ===
    # The /v1/soul/* endpoints are superseded by:
    # - POST /agentese/self/soul/dialogue - Dialogue with K-gent
    # - POST /agentese/self/soul/governance - Semantic gatekeeper
    # See: protocols/agentese/contexts/self_soul.py (SoulNode)

    # === AGENTESE Legacy Router REMOVED (AD-009) ===
    # The /v1/agentese/* endpoints are superseded by /agentese/* gateway.
    # All clients should use the gateway at /agentese/{path}/{aspect}.
    # See: protocols/agentese/gateway.py

    # === K-gent Sessions REMOVED (AD-009 Phase 2) ===
    # The /v1/kgent/* endpoints are superseded by:
    # - POST /agentese/self/kgent/create - Create session
    # - POST /agentese/self/kgent/list - List sessions
    # - POST /agentese/self/kgent/message - Send message (SSE)
    # - POST /agentese/self/kgent/history - Get message history
    # See: protocols/agentese/contexts/self_kgent.py (KgentSessionNode)

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

    # === N-Phase Session REMOVED (AD-009 Phase 2) ===
    # The /v1/nphase/* endpoints are superseded by:
    # - POST /agentese/self/session/create - Create session
    # - POST /agentese/self/session/list - List sessions
    # - POST /agentese/self/session/{id}/advance - Advance phase
    # - POST /agentese/self/session/{id}/checkpoint - Create checkpoint
    # - POST /agentese/self/session/{id}/detect - Detect phase signal
    # See: protocols/agentese/contexts/self_nphase.py (NPhaseNode)

    # === Workshop Router REMOVED (AD-009 Phase 3) ===
    # The /v1/workshop/* endpoints are superseded by:
    # - GET /agentese/world/workshop/manifest - Workshop status
    # - POST /agentese/world/workshop/task - Assign task
    # - GET /agentese/world/workshop/stream (SSE) - Event stream
    # - GET /agentese/world/workshop/builders - List builders
    # - POST /agentese/world/workshop/perturb - Inject perturbation
    # - GET /agentese/world/workshop/history - Task history
    # - GET /agentese/world/workshop/metrics - Aggregate metrics
    # See: protocols/agentese/contexts/world_workshop.py (WorkshopNode)

    # === Gallery Router REMOVED (AD-009 Phase 3) ===
    # The /api/gallery/* endpoints are superseded by:
    # - GET /agentese/world/gallery/manifest - All pilots
    # - GET /agentese/world/gallery/categories - Category list
    # - POST /agentese/world/gallery/pilot - Single pilot detail
    # See: protocols/agentese/contexts/world_gallery_api.py (GalleryApiNode)

    # Brain WebSocket (real-time updates - keep for now)
    from .brain_websocket import create_brain_websocket_router

    brain_ws_router = create_brain_websocket_router()
    if brain_ws_router is not None:
        app.include_router(brain_ws_router)

    # Witness REST API (frontend dashboard)
    from .witness import create_witness_router

    witness_router = create_witness_router()
    if witness_router is not None:
        app.include_router(witness_router)
        logger.info("Witness API mounted at /api/witness")

    # Spec Ledger REST API (living spec dashboard)
    from .spec_ledger import create_spec_ledger_router

    spec_ledger_router = create_spec_ledger_router()
    if spec_ledger_router is not None:
        app.include_router(spec_ledger_router)
        logger.info("Spec Ledger API mounted at /api/spec")

    # Gestalt endpoints REMOVED (AD-009 Router Consolidation)
    # The /v1/world/codebase/* endpoints are superseded by:
    # - GET/POST /agentese/world/codebase/{aspect}
    # - GET /agentese/world/codebase/{aspect}/stream (SSE)
    # See: services/gestalt/node.py (GestaltNode)

    # === Infrastructure Router REMOVED (AD-009 Phase 3) ===
    # The /api/infra/* endpoints are superseded by:
    # - GET /agentese/world/gestalt/live/status - Collector status
    # - POST /agentese/world/gestalt/live/connect - Connect to K8s
    # - POST /agentese/world/gestalt/live/disconnect - Disconnect
    # - GET /agentese/world/gestalt/live/topology - Current topology
    # - GET /agentese/world/gestalt/live/topology_stream (SSE) - Topology updates
    # - GET /agentese/world/gestalt/live/events_stream (SSE) - Event stream
    # - GET /agentese/world/gestalt/live/health - Aggregate health
    # - POST /agentese/world/gestalt/live/entity_detail - Entity details
    # See: protocols/agentese/contexts/world_gestalt_live.py (GestaltLiveNode)

    # Gardener endpoints REMOVED (AD-009 Router Consolidation)
    # The /v1/gardener/* endpoints are superseded by:
    # - concept.gardener.*  - Session polynomial (SENSE→ACT→REFLECT)
    # - self.garden.*       - Garden state (seasons, plots, tending)
    # See: protocols/agentese/contexts/gardener.py, contexts/garden.py

    # === AGENTESE Universal Gateway (AD-009) ===
    # The protocol IS the API - auto-exposes all @node registered services
    try:
        from protocols.agentese.container import get_container
        from protocols.agentese.gateway import mount_gateway

        container = get_container()
        mount_gateway(
            app,
            prefix="/agentese",
            container=container,
            enable_streaming=True,
            enable_websocket=True,
            fallback_to_logos=True,
        )
        logger.info("AGENTESE Gateway mounted at /agentese")
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
    # NOTE: Startup/shutdown now handled via lifespan context manager above.
    # This avoids FastAPI's deprecated on_event decorator.
    # See: https://fastapi.tiangolo.com/advanced/events/#lifespan

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
                # === K-gent Soul (via AGENTESE Gateway) ===
                "soul": {
                    "note": "Use AGENTESE gateway instead of /v1/soul/*",
                    "manifest": "GET /agentese/self/soul/manifest",
                    "dialogue": "POST /agentese/self/soul/dialogue",
                    "governance": "POST /agentese/self/soul/governance",
                    "challenge": "POST /agentese/self/soul/challenge",
                    "reflect": "POST /agentese/self/soul/reflect",
                },
                # === K-gent Sessions (via AGENTESE Gateway) ===
                "kgent": {
                    "note": "Use AGENTESE gateway instead of /v1/kgent/*",
                    "create": "POST /agentese/self/kgent/create",
                    "list": "POST /agentese/self/kgent/list",
                    "message": "POST /agentese/self/kgent/message",
                    "history": "POST /agentese/self/kgent/history",
                },
                # === N-Phase Sessions (via AGENTESE Gateway) ===
                "nphase": {
                    "note": "Use AGENTESE gateway instead of /v1/nphase/*",
                    "create": "POST /agentese/self/session/create",
                    "list": "POST /agentese/self/session/list",
                    "advance": "POST /agentese/self/session/advance",
                    "checkpoint": "POST /agentese/self/session/checkpoint",
                    "detect": "POST /agentese/self/session/detect",
                },
                # === Workshop (via AGENTESE Gateway) ===
                "workshop": {
                    "note": "Use AGENTESE gateway instead of /v1/workshop/*",
                    "manifest": "GET /agentese/world/workshop/manifest",
                    "task": "POST /agentese/world/workshop/task",
                    "stream": "GET /agentese/world/workshop/stream/stream (SSE)",
                    "builders": "POST /agentese/world/workshop/builders",
                    "perturb": "POST /agentese/world/workshop/perturb",
                    "history": "POST /agentese/world/workshop/history",
                    "metrics": "POST /agentese/world/workshop/metrics",
                },
                # === Gallery (via AGENTESE Gateway) ===
                "gallery": {
                    "note": "Use AGENTESE gateway instead of /api/gallery/*",
                    "manifest": "GET /agentese/world/gallery/manifest",
                    "categories": "POST /agentese/world/gallery/categories",
                    "pilot": "POST /agentese/world/gallery/pilot",
                },
                # === Gestalt Codebase (via AGENTESE Gateway) ===
                "gestalt": {
                    "note": "Use AGENTESE gateway instead of /v1/world/codebase/*",
                    "manifest": "GET /agentese/world/codebase/manifest",
                    "health": "POST /agentese/world/codebase/health",
                    "topology": "POST /agentese/world/codebase/topology",
                    "stream": "GET /agentese/world/codebase/topology/stream (SSE)",
                },
                # === Gardener (via AGENTESE Gateway) ===
                "gardener": {
                    "note": "Use AGENTESE gateway instead of /v1/gardener/*",
                    "session": "GET /agentese/concept/gardener/manifest",
                    "garden": "GET /agentese/self/garden/manifest",
                    "season": "POST /agentese/self/garden/season",
                    "health": "POST /agentese/self/garden/health",
                },
                # === Infrastructure / Gestalt Live (via AGENTESE Gateway) ===
                "infrastructure": {
                    "note": "Use AGENTESE gateway instead of /api/infra/*",
                    "status": "GET /agentese/world/gestalt/live/status/manifest",
                    "topology": "POST /agentese/world/gestalt/live/topology",
                    "topology_stream": "GET /agentese/world/gestalt/live/topology_stream/stream (SSE)",
                    "events_stream": "GET /agentese/world/gestalt/live/events_stream/stream (SSE)",
                    "health": "POST /agentese/world/gestalt/live/health",
                    "connect": "POST /agentese/world/gestalt/live/connect",
                    "disconnect": "POST /agentese/world/gestalt/live/disconnect",
                },
                # === Non-AGENTESE Endpoints ===
                "witness": {
                    "list": "GET /api/witness/marks",
                    "create": "POST /api/witness/marks",
                    "retract": "PATCH /api/witness/marks/{id}/retract",
                    "stream": "GET /api/witness/stream (SSE)",
                },
                "webhooks": {
                    "stripe": "/webhooks/stripe",
                    "stripe_health": "/webhooks/stripe/health",
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
