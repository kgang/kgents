"""
U-gent Server: FastAPI application for cluster-native tool execution.

This server exposes U-gent capabilities as HTTP endpoints for Kubernetes deployment.
It integrates:
- K-gent Soul (as library, not RPC) for conscience checks
- Morpheus Gateway for LLM operations
- MCP clients for external tool access

Usage (local development):
    uvicorn agents.u.server:app --reload --port 8080

Usage (in-cluster):
    Deploy via K8s manifest with MORPHEUS_URL environment variable

AGENTESE: world.ugent.server
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# --- Request/Response Models ---


class ExecuteRequest(BaseModel):
    """Request to execute a tool or operation."""

    prompt: str = Field(..., description="The operation to execute")
    tool_name: Optional[str] = Field(None, description="Specific tool to use")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    require_approval: bool = Field(True, description="Require Soul approval")
    severity: float = Field(0.5, ge=0.0, le=1.0, description="Operation severity")


class ExecuteResponse(BaseModel):
    """Response from tool execution."""

    status: str  # "approved", "rejected", "escalated", "executed", "error"
    result: Optional[Any] = None
    annotation: Optional[str] = None  # Soul annotation if escalated
    reasoning: Optional[str] = None  # Soul reasoning
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    token_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    soul_available: bool
    morpheus_available: bool
    timestamp: str


# --- Mock Soul for graceful degradation ---


@dataclass
class MockInterceptResult:
    """Mock intercept result when Soul is unavailable."""

    handled: bool = False
    annotation: Optional[str] = "Soul unavailable. Human review required."
    recommendation: Optional[str] = "escalate"
    confidence: float = 0.0
    matching_principles: list[str] = None  # type: ignore
    reasoning: str = "Soul service not configured."
    was_deep: bool = False

    def __post_init__(self) -> None:
        if self.matching_principles is None:
            self.matching_principles = []


# --- Server State ---


@dataclass
class ServerState:
    """Server state for dependency injection."""

    soul: Any = None  # KgentSoul when available
    llm_client: Any = None  # LLM client when available
    startup_time: datetime = None  # type: ignore

    def __post_init__(self) -> None:
        if self.startup_time is None:
            self.startup_time = datetime.now()

    @property
    def soul_available(self) -> bool:
        """Check if Soul is available."""
        return self.soul is not None

    @property
    def morpheus_available(self) -> bool:
        """Check if Morpheus Gateway is configured."""
        from agents.k.llm import morpheus_available

        return morpheus_available()


# Global state (initialized on startup)
_state: Optional[ServerState] = None


def get_state() -> ServerState:
    """Get server state, initializing if needed."""
    global _state
    if _state is None:
        _state = ServerState()
    return _state


# --- FastAPI Application ---


def create_app() -> Any:
    """
    Create FastAPI application for U-gent server.

    The server provides:
    - POST /execute - Execute an operation with Soul conscience checks
    - GET /health - Health check endpoint
    - GET /tools - List available tools

    Soul Integration:
    - Soul is imported as a library (in-process, no RPC)
    - If Soul requires LLM, it uses Morpheus Gateway via MORPHEUS_URL

    Returns:
        FastAPI application
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
    except ImportError:
        raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Lifespan context manager for startup/shutdown."""
        # Startup
        state = get_state()

        # Try to initialize Soul
        try:
            from agents.k.soul import KgentSoul

            state.soul = KgentSoul(auto_llm=True)
            logger.info(f"Soul initialized (has_llm={state.soul.has_llm})")
        except Exception as e:
            logger.warning(f"Soul initialization failed: {e}")
            state.soul = None

        # Log Morpheus status
        if state.morpheus_available:
            morpheus_url = os.environ.get("MORPHEUS_URL", os.environ.get("LLM_ENDPOINT"))
            logger.info(f"Morpheus Gateway configured: {morpheus_url}")
        else:
            logger.info("Morpheus Gateway not configured (Soul will use templates)")

        yield

        # Shutdown (cleanup if needed)

    app = FastAPI(
        title="U-gent Server",
        description="Cluster-native tool execution with K-gent Soul integration",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.post("/execute", response_model=ExecuteResponse)
    async def execute(request: ExecuteRequest) -> ExecuteResponse:
        """
        Execute an operation with Soul conscience checks.

        Flow:
        1. Create decision token from request
        2. Have Soul intercept (deep if LLM available)
        3. If approved, execute the operation
        4. Return result with audit trail
        """
        import time

        start_time = time.time()
        state = get_state()

        # Create a mock token for Soul intercept
        @dataclass
        class DecisionToken:
            prompt: str
            reason: str
            severity: float
            id: str

        token = DecisionToken(
            prompt=request.prompt,
            reason=f"Tool: {request.tool_name}" if request.tool_name else "Direct execution",
            severity=request.severity,
            id=f"ugent-{int(time.time() * 1000)}",
        )

        # Intercept with Soul if available and approval required
        if request.require_approval:
            if state.soul is not None:
                try:
                    # Use deep intercept if LLM is available
                    if state.soul.has_llm:
                        result = await state.soul.intercept_deep(token)
                    else:
                        result = await state.soul.intercept(token)

                    if not result.handled:
                        # Escalate to human
                        return ExecuteResponse(
                            status="escalated",
                            annotation=result.annotation,
                            reasoning=result.reasoning,
                            confidence=result.confidence,
                            execution_time_ms=(time.time() - start_time) * 1000,
                            token_id=token.id,
                        )

                    # Approved by Soul
                    logger.info(f"Soul approved: {token.id} (confidence={result.confidence:.2f})")

                except Exception as e:
                    logger.error(f"Soul intercept failed: {e}")
                    # Fail safe: escalate on error
                    return ExecuteResponse(
                        status="escalated",
                        annotation=f"Soul error: {str(e)}. Human review required.",
                        reasoning="Error during conscience check",
                        confidence=0.0,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        token_id=token.id,
                    )
            else:
                # No Soul available - escalate
                return ExecuteResponse(
                    status="escalated",
                    annotation="Soul not available. Human review required.",
                    reasoning="Soul service not configured",
                    confidence=0.0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    token_id=token.id,
                )

        # Execute the operation
        # TODO: Integrate with actual tool execution
        # For now, return approved status
        return ExecuteResponse(
            status="approved",
            result={"message": f"Operation approved: {request.prompt[:50]}..."},
            confidence=1.0,
            execution_time_ms=(time.time() - start_time) * 1000,
            token_id=token.id,
        )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Health check endpoint."""
        state = get_state()
        return HealthResponse(
            status="healthy" if state.soul_available else "degraded",
            soul_available=state.soul_available,
            morpheus_available=state.morpheus_available,
            timestamp=datetime.now().isoformat(),
        )

    @app.get("/tools")
    async def list_tools() -> dict[str, Any]:
        """List available tools."""
        # TODO: Integrate with ToolRegistry
        return {
            "tools": [],
            "message": "Tool registry not yet integrated",
        }

    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        state = get_state()
        return {
            "name": "U-gent Server",
            "version": "1.0.0",
            "description": "Cluster-native tool execution with K-gent Soul integration",
            "soul_available": state.soul_available,
            "morpheus_available": state.morpheus_available,
            "endpoints": {
                "execute": "POST /execute",
                "health": "GET /health",
                "tools": "GET /tools",
            },
        }

    return app


# Create app instance for uvicorn
app = create_app()


def main() -> None:
    """Run U-gent server."""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn not installed. Install with: pip install uvicorn")

    port = int(os.environ.get("UGENT_PORT", "8080"))
    host = os.environ.get("UGENT_HOST", "0.0.0.0")

    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting U-gent Server on {host}:{port}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
