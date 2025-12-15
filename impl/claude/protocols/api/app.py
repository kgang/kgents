"""
FastAPI Application for kgents SaaS API Service.

Main application factory that:
- Creates FastAPI app
- Registers routes (Soul, AGENTESE, Sessions)
- Adds middleware (CORS, Tenant Context, Metering)
- Configures health checks
- Provides multi-tenant support
"""

from __future__ import annotations

from typing import Any, Optional

# Graceful FastAPI import
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None  # type: ignore[misc, assignment]
    CORSMiddleware = None  # type: ignore[misc, assignment]

from agents.k.soul import KgentSoul

from .auth import ApiKeyData, TenantContextMiddleware, get_optional_api_key
from .metering import MeteringMiddleware
from .models import HealthResponse
from .soul import create_soul_router

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
                "soul": {
                    "governance": "/v1/soul/governance",
                    "dialogue": "/v1/soul/dialogue",
                },
                "agentese": {
                    "invoke": "/v1/agentese/invoke",
                    "resolve": "/v1/agentese/resolve",
                    "affordances": "/v1/agentese/affordances",
                },
                "kgent": {
                    "sessions": "/v1/kgent/sessions",
                    "messages": "/v1/kgent/sessions/{id}/messages",
                },
                "webhooks": {
                    "stripe": "/webhooks/stripe",
                    "stripe_health": "/webhooks/stripe/health",
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
