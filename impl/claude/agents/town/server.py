"""
Standalone FastAPI server for Agent Town microservice.

Combines all Town endpoints:
- REST API for town CRUD operations
- SSE streaming for live events
- WebSocket for bidirectional communication
- Budget management with Redis backend

Run with:
    uvicorn agents.town.server:app --host 0.0.0.0 --port 8001

Or via Docker:
    docker run -p 8001:8001 kgents/town:latest

See: plans/velvety-mapping-puddle.md Phase 4
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Application Factory
# =============================================================================


def create_town_app() -> Any:
    """
    Create the Town service FastAPI application.

    Returns:
        FastAPI application instance
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        raise RuntimeError("FastAPI not installed. Run: pip install fastapi uvicorn")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Application lifespan handler."""
        logger.info("Town service starting...")

        # Log configuration
        logger.info(f"MORPHEUS_URL: {os.environ.get('MORPHEUS_URL', 'not set')}")
        logger.info(f"REDIS_URL: {os.environ.get('REDIS_URL', 'not set')}")
        logger.info(f"NATS_SERVERS: {os.environ.get('NATS_SERVERS', 'not set')}")

        yield

        logger.info("Town service shutting down...")

    app = FastAPI(
        title="Agent Town Service",
        description="Live Agent Town orchestration with LLM dialogue",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==========================================================================
    # Health Endpoints
    # ==========================================================================

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "town"}

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        """Readiness check - verify dependencies are available."""
        checks: dict[str, Any] = {
            "status": "ready",
            "checks": {},
        }

        # Check Redis
        try:
            from agents.town.budget_store import RedisBudgetStore

            RedisBudgetStore()  # Verify store can be created
            # Simple ping would go here
            checks["checks"]["redis"] = "available"
        except Exception as e:
            checks["checks"]["redis"] = f"unavailable: {e}"

        # Check LLM
        try:
            from agents.k.llm import has_llm_credentials

            if has_llm_credentials():
                checks["checks"]["llm"] = "available"
            else:
                checks["checks"]["llm"] = "no credentials"
        except Exception as e:
            checks["checks"]["llm"] = f"unavailable: {e}"

        return checks

    # ==========================================================================
    # Register Routers
    # ==========================================================================

    # Town REST/SSE endpoints
    try:
        from protocols.api.town import create_town_router

        town_router = create_town_router()
        if town_router:
            app.include_router(town_router)
            logger.info("Registered: Town REST/SSE router")
    except Exception as e:
        logger.warning(f"Failed to register town router: {e}")

    # Town AUP endpoints (init, perturb, step, etc.)
    try:
        from protocols.api.aup import create_aup_router

        aup_router = create_aup_router()
        if aup_router:
            app.include_router(aup_router)
            logger.info("Registered: AUP router (town endpoints)")
    except Exception as e:
        logger.warning(f"Failed to register AUP router: {e}")

    # WebSocket endpoint
    try:
        from protocols.api.town_websocket import create_town_websocket_router

        ws_router = create_town_websocket_router()
        if ws_router:
            app.include_router(ws_router)
            logger.info("Registered: WebSocket router")
    except Exception as e:
        logger.warning(f"Failed to register WebSocket router: {e}")

    # ==========================================================================
    # Budget Status Endpoint
    # ==========================================================================

    @app.get("/budget/{tenant_id}")
    async def get_budget(tenant_id: str, tier: str = "FREE") -> dict[str, Any]:
        """Get budget status for a tenant."""
        try:
            from protocols.api.town_budget import get_budget_enforcer

            enforcer = get_budget_enforcer()
            return await enforcer.get_budget_status(tenant_id, tier)
        except Exception as e:
            return {"error": str(e)}

    # ==========================================================================
    # Metrics Endpoint (Prometheus)
    # ==========================================================================

    @app.get("/metrics")
    async def metrics() -> str:
        """Prometheus metrics endpoint."""
        try:
            from prometheus_client import generate_latest

            result: bytes = generate_latest()
            return result.decode()
        except ImportError:
            # Basic metrics if prometheus_client not installed
            return (
                "# HELP town_service_up Town service is running\n"
                "# TYPE town_service_up gauge\n"
                "town_service_up 1\n"
            )

    return app


# =============================================================================
# Application Instance
# =============================================================================

# Create the app instance for uvicorn
app = create_town_app()


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> None:
    """Run the server directly."""
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8001"))

    logger.info(f"Starting town-service on {host}:{port}")

    uvicorn.run(
        "agents.town.server:app",
        host=host,
        port=port,
        reload=os.environ.get("DEBUG", "").lower() == "true",
        log_level="info",
    )


if __name__ == "__main__":
    main()
