"""
Gardener API Endpoints.

Exposes The Gardener (Crown Jewel) capabilities via REST API:
- GET /v1/gardener/session - Get active session
- POST /v1/gardener/session - Create new session
- POST /v1/gardener/session/advance - Advance to next phase
- GET /v1/gardener/session/polynomial - Get polynomial visualization
- GET /v1/gardener/sessions - List recent sessions

Wave 1: Hero Path Polish
See: plans/core-apps/the-gardener.md
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

from .models import (
    GardenerCreateRequest,
    GardenerIntentRequest,
    GardenerPhase,
    GardenerSessionListResponse,
    GardenerSessionResponse,
    PolynomialEdge,
    PolynomialHistoryEntry,
    PolynomialPosition,
    PolynomialVisualization,
    PolynomialVisualizationResponse,
)

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    Depends = None  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


from .auth import get_optional_api_key

# =============================================================================
# Global Gardener Context (thread-safe initialization)
# =============================================================================

_gardener_ctx: Any = None
_gardener_ctx_lock = threading.Lock()


def _get_gardener_context() -> Any:
    """Get or create the shared Gardener context (thread-safe)."""
    global _gardener_ctx

    if _gardener_ctx is None:
        with _gardener_ctx_lock:
            if _gardener_ctx is None:
                from agents.gardener.handlers import GardenerContext
                from agents.gardener.persistence import create_session_store

                store = create_session_store()
                _gardener_ctx = GardenerContext(store=store)

    return _gardener_ctx


# =============================================================================
# Helper: Convert session to polynomial visualization
# =============================================================================


def _session_to_polynomial(session_data: dict[str, Any]) -> PolynomialVisualization:
    """Convert a GardenerSession dict to PolynomialVisualization."""
    phase = session_data.get("phase", "SENSE")

    position_config = {
        "SENSE": {
            "label": "Sense",
            "emoji": "👁️",
            "description": "Gather context from forest, codebase, memory",
        },
        "ACT": {
            "label": "Act",
            "emoji": "⚡",
            "description": "Execute intent: write code, create docs",
        },
        "REFLECT": {
            "label": "Reflect",
            "emoji": "💭",
            "description": "Consolidate learnings, update meta.md",
        },
    }

    positions = []
    for phase_id in ["SENSE", "ACT", "REFLECT"]:
        config = position_config[phase_id]
        positions.append(
            PolynomialPosition(
                id=phase_id,
                label=config["label"],
                description=config["description"],
                emoji=config["emoji"],
                is_current=(phase == phase_id),
                is_terminal=False,  # Gardener phases cycle
                color="#84CC16" if phase == phase_id else None,
            )
        )

    edges = [
        PolynomialEdge(
            source="SENSE",
            target="ACT",
            label="advance",
            is_valid=(phase == "SENSE"),
        ),
        PolynomialEdge(
            source="ACT",
            target="REFLECT",
            label="advance",
            is_valid=(phase == "ACT"),
        ),
        PolynomialEdge(
            source="REFLECT",
            target="SENSE",
            label="cycle",
            is_valid=(phase == "REFLECT"),
        ),
        PolynomialEdge(
            source="ACT",
            target="SENSE",
            label="rollback",
            is_valid=(phase == "ACT"),
        ),
    ]

    valid_directions = {
        "SENSE": ["ACT"],
        "ACT": ["REFLECT", "SENSE"],
        "REFLECT": ["SENSE"],
    }.get(phase, [])

    return PolynomialVisualization(
        id=session_data.get("session_id", "unknown"),
        name=session_data.get("name", "Gardener Session"),
        positions=positions,
        edges=edges,
        current=phase,
        valid_directions=valid_directions,
        history=[],  # Could add history from session_data if available
        metadata={
            "sense_count": session_data.get("sense_count", 0),
            "act_count": session_data.get("act_count", 0),
            "reflect_count": session_data.get("reflect_count", 0),
        },
    )


def _session_dict_to_response(data: dict[str, Any]) -> GardenerSessionResponse:
    """Convert session dict to response model."""
    intent = data.get("intent")
    intent_model = None
    if intent:
        intent_model = GardenerIntentRequest(
            description=intent.get("description", ""),
            priority=intent.get("priority", "normal"),
        )

    return GardenerSessionResponse(
        session_id=data.get("session_id", data.get("id", "unknown")),
        name=data.get("name", "Unnamed Session"),
        phase=GardenerPhase(data.get("phase", "SENSE")),
        plan_path=data.get("plan_path"),
        intent=intent_model,
        artifacts_count=data.get("artifacts_count", 0),
        learnings_count=data.get("learnings_count", 0),
        sense_count=data.get("sense_count", 0),
        act_count=data.get("act_count", 0),
        reflect_count=data.get("reflect_count", 0),
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_gardener_router() -> "APIRouter | None":
    """
    Create Gardener API router.

    Returns:
        FastAPI router with gardener endpoints, or None if FastAPI not available
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/v1/gardener", tags=["gardener"])

    @router.get("/session", response_model=GardenerSessionResponse)
    async def get_active_session(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenerSessionResponse:
        """
        Get the currently active gardener session.

        Returns:
            Active session state, or 404 if no active session
        """
        try:
            ctx = _get_gardener_context()
            await ctx.init()

            if not ctx.active_session:
                raise HTTPException(status_code=404, detail="No active session")

            return _session_dict_to_response(ctx.active_session.state.to_dict())
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to get active session")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/session", response_model=GardenerSessionResponse)
    async def create_session(
        request: GardenerCreateRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenerSessionResponse:
        """
        Create a new gardener session.

        Args:
            request: Session creation parameters

        Returns:
            Created session state
        """
        try:
            from protocols.agentese.node import Observer

            ctx = _get_gardener_context()
            await ctx.init()

            from agents.gardener.handlers import handle_session_create

            observer = Observer.guest().to_dict() if hasattr(Observer, "guest") else {}

            kwargs: dict[str, Any] = {}
            if request.name:
                kwargs["name"] = request.name
            if request.plan_path:
                kwargs["plan_path"] = request.plan_path
            if request.intent:
                kwargs["intent"] = {
                    "description": request.intent.description,
                    "priority": request.intent.priority,
                }

            result = await handle_session_create(ctx, observer, **kwargs)

            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=result.get("message", "Creation failed"))

            session_data = result.get("session", {})
            return _session_dict_to_response(session_data)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to create session")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/session/advance", response_model=GardenerSessionResponse)
    async def advance_session(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenerSessionResponse:
        """
        Advance the active session to the next phase.

        Returns:
            Updated session state after advancing
        """
        try:
            from protocols.agentese.node import Observer

            ctx = _get_gardener_context()
            await ctx.init()

            if not ctx.active_session:
                raise HTTPException(status_code=404, detail="No active session")

            from agents.gardener.handlers import handle_session_advance

            observer = Observer.guest().to_dict() if hasattr(Observer, "guest") else {}

            result = await handle_session_advance(ctx, observer)

            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=result.get("message", "Advance failed"))

            return _session_dict_to_response(ctx.active_session.state.to_dict())
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to advance session")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/session/polynomial", response_model=PolynomialVisualizationResponse)
    async def get_session_polynomial(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> PolynomialVisualizationResponse:
        """
        Get polynomial visualization for the active session.

        Foundation 3: Visible Polynomial State

        Returns:
            Polynomial visualization data for rendering state machine
        """
        try:
            ctx = _get_gardener_context()
            await ctx.init()

            if not ctx.active_session:
                raise HTTPException(status_code=404, detail="No active session")

            session_data = ctx.active_session.state.to_dict()
            visualization = _session_to_polynomial(session_data)

            return PolynomialVisualizationResponse(
                visualization=visualization,
                agentese_path=f"concept.gardener.session[{ctx.active_session.session_id}].manifest",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to get polynomial")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/sessions", response_model=GardenerSessionListResponse)
    async def list_sessions(
        limit: int = 10,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenerSessionListResponse:
        """
        List recent gardener sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of recent sessions
        """
        try:
            ctx = _get_gardener_context()
            await ctx.init()

            recent = await ctx.store.list_recent(limit=limit)

            sessions = []
            for stored in recent:
                data = {
                    "session_id": stored.id,
                    "name": stored.name,
                    "phase": stored.phase,
                    "plan_path": stored.plan_path,
                    **stored.state,
                }
                sessions.append(_session_dict_to_response(data))

            active_id = ctx.active_session.session_id if ctx.active_session else None

            return GardenerSessionListResponse(
                sessions=sessions,
                active_session_id=active_id,
            )
        except Exception as e:
            logger.exception("Failed to list sessions")
            raise HTTPException(status_code=500, detail=str(e))

    return router
