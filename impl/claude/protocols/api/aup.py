"""
AGENTESE Universal Protocol (AUP) HTTP Router.

FastAPI router for the AUP endpoints:
- GET  /api/v1/{context}/{holon}/manifest - Manifest entity to observer's view
- POST /api/v1/{context}/{holon}/{aspect} - Invoke aspect on entity
- GET  /api/v1/{context}/{holon}/affordances - List available affordances
- POST /api/v1/compose - Execute composition pipeline
- GET  /api/v1/{context}/{holon}/{aspect}/stream - SSE streaming

Design Principles (from spec/principles.md):
1. No View from Nowhere - Observer context REQUIRED (via headers)
2. Minimal Output - Lean response envelope
3. Sympathetic Errors - Errors include suggestion and available
4. Category Laws - compose() verifies identity/associativity
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter, Request

    from .auth import ApiKeyData

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Body, Depends, HTTPException, Request
    from fastapi.responses import StreamingResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    Body = None  # type: ignore[assignment]
    Depends = None  # type: ignore[assignment]
    StreamingResponse = None  # type: ignore[assignment, misc]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str | dict[str, Any]) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(str(detail))


logger = logging.getLogger(__name__)

# Valid AGENTESE contexts
VALID_CONTEXTS = frozenset({"world", "self", "concept", "void", "time"})


# =============================================================================
# Header Extraction
# =============================================================================


def get_observer_from_headers(request: "Request") -> Any:
    """
    Extract ObserverContext from HTTP headers.

    Headers:
    - X-Observer-Archetype: Observer archetype (default: "viewer")
    - X-Observer-Id: Observer ID (default: "anonymous")
    - X-Observer-Capabilities: Comma-separated capabilities (default: "")

    Args:
        request: FastAPI Request object

    Returns:
        ObserverContext from headers
    """
    from .serializers import ObserverContext

    archetype = request.headers.get("X-Observer-Archetype", "viewer")
    observer_id = request.headers.get("X-Observer-Id", "anonymous")
    capabilities_str = request.headers.get("X-Observer-Capabilities", "")

    # Parse capabilities (comma-separated, filter empty)
    capabilities = [c.strip() for c in capabilities_str.split(",") if c.strip()]

    return ObserverContext(
        archetype=archetype,
        id=observer_id,
        capabilities=capabilities,
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_aup_router() -> "APIRouter | None":
    """
    Create AGENTESE Universal Protocol router.

    Returns:
        FastAPI router with AUP endpoints, or None if FastAPI unavailable

    Endpoints:
        GET  /api/v1/{context}/{holon}/manifest - Manifest entity
        GET  /api/v1/{context}/{holon}/affordances - List affordances
        POST /api/v1/{context}/{holon}/{aspect} - Invoke aspect
        POST /api/v1/compose - Execute composition pipeline
        GET  /api/v1/{context}/{holon}/{aspect}/stream - SSE streaming
    """
    if not HAS_FASTAPI:
        return None

    from .auth import get_api_key, has_scope
    from .bridge import AgenteseBridgeProtocol, get_http_status
    from .bridge_impl import BridgeError, create_logos_bridge
    from .serializers import (
        AffordancesResponse,
        AgenteseRequest,
        AgenteseResponse,
        CompositionRequest,
        CompositionResponse,
        ErrorResponse,
        ObserverContext,
    )

    # Ensure Pydantic model forward references are resolved for FastAPI Body()
    CompositionRequest.model_rebuild()

    # Store local imports in module globals for FastAPI annotation resolution
    # This is needed because `from __future__ import annotations` stringifies all annotations
    globals().update(
        {
            "CompositionRequest": CompositionRequest,
            "CompositionResponse": CompositionResponse,
            "AgenteseRequest": AgenteseRequest,
            "AgenteseResponse": AgenteseResponse,
            "AffordancesResponse": AffordancesResponse,
            "ErrorResponse": ErrorResponse,
            "ObserverContext": ObserverContext,
        }
    )

    router = APIRouter(prefix="/api/v1", tags=["agentese-universal-protocol"])

    # Shared bridge instance (created lazily)
    _bridge: AgenteseBridgeProtocol | None = None

    def get_bridge() -> AgenteseBridgeProtocol:
        """Get or create the shared bridge instance."""
        nonlocal _bridge
        if _bridge is None:
            _bridge = create_logos_bridge()
        return _bridge

    # =========================================================================
    # Town Perturbation Endpoints (MUST come before generic routes)
    # Micro-Experience Factory - plans/micro-experience-factory.md
    # =========================================================================

    # Town flux instances by town_id (simple in-memory store for MVP)
    _town_fluxes: dict[str, Any] = {}
    # Cooldown tracking: town_id -> last_perturb_timestamp
    _perturb_cooldowns: dict[str, float] = {}
    PERTURB_COOLDOWN_SECONDS = 1.0  # Minimum time between perturbations

    @router.post(
        "/town/{town_id}/init",
        tags=["town"],
        responses={
            200: {"description": "Town initialized"},
        },
    )
    async def init_town(
        town_id: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """
        Initialize a new TownFlux for simulation.

        Args:
            town_id: The town ID to create
            request: HTTP request with optional body
            api_key: Validated API key

        Body (optional):
            {
                "num_citizens": 5,
                "seed": 42,
                "enable_dialogue": true  # Enable real LLM dialogue
            }
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        try:
            body = await request.json()
        except Exception:
            body = {}

        num_citizens = body.get("num_citizens", 5)
        seed = body.get("seed")
        enable_dialogue = body.get("enable_dialogue", False)

        from agents.town.environment import (
            create_mpp_environment,
            create_phase2_environment,
        )
        from agents.town.flux import TownFlux

        if num_citizens <= 3:
            env = create_mpp_environment()
        else:
            env = create_phase2_environment()

        # Wire up dialogue engine if enabled
        dialogue_engine = None
        dialogue_info: dict[str, Any] = {"enabled": False}

        if enable_dialogue:
            try:
                from agents.k.llm import create_llm_client, has_llm_credentials
                from agents.town.dialogue_engine import (
                    CitizenDialogueEngine,
                    DialogueBudgetConfig,
                )

                if has_llm_credentials():
                    llm_client = create_llm_client(prefer_morpheus=True)
                    config = DialogueBudgetConfig()
                    dialogue_engine = CitizenDialogueEngine(llm_client, config)

                    # Register citizens with tiers based on API key tier
                    # Evolving citizens get full LLM access, leaders get sampled, standard get templates
                    citizen_list = list(env.citizens.values())
                    num_evolving = max(1, len(citizen_list) // 5)  # ~20% evolving
                    num_leaders = max(1, len(citizen_list) // 4)  # ~25% leaders

                    for i, citizen in enumerate(citizen_list):
                        if i < num_evolving:
                            tier = "evolving"
                        elif i < num_evolving + num_leaders:
                            tier = "leader"
                        else:
                            tier = "standard"
                        dialogue_engine.register_citizen(citizen.id, tier)

                    dialogue_info = {
                        "enabled": True,
                        "llm_available": True,
                        "tiers": {
                            "evolving": num_evolving,
                            "leader": num_leaders,
                            "standard": len(citizen_list) - num_evolving - num_leaders,
                        },
                    }
                else:
                    dialogue_info = {
                        "enabled": False,
                        "llm_available": False,
                        "reason": "No LLM credentials available (MORPHEUS_URL or Claude CLI)",
                    }
            except ImportError as e:
                dialogue_info = {
                    "enabled": False,
                    "llm_available": False,
                    "reason": f"Import error: {e}",
                }

        flux = TownFlux(env, seed=seed, dialogue_engine=dialogue_engine)
        _town_fluxes[town_id] = flux

        return {
            "town_id": town_id,
            "status": "initialized",
            "citizens": [c.name for c in flux.citizens],
            "num_citizens": len(flux.citizens),
            "dialogue": dialogue_info,
        }

    @router.get(
        "/town/{town_id}/status",
        tags=["town"],
        responses={
            200: {"description": "Town status"},
            404: {"model": ErrorResponse, "description": "Town not found"},
        },
    )
    async def get_town_status(
        town_id: str,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """Get current status of a TownFlux."""
        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        flux = _town_fluxes.get(town_id)
        if flux is None:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Town '{town_id}' not found", "code": "NOT_FOUND"},
            )

        status: dict[str, Any] = flux.get_status()
        status["town_id"] = town_id
        return status

    @router.post(
        "/town/{town_id}/perturb",
        tags=["town"],
        responses={
            200: {"description": "Perturbation result"},
            400: {"model": ErrorResponse, "description": "Invalid operation"},
            429: {"model": ErrorResponse, "description": "Cooldown active"},
        },
    )
    async def perturb_town(
        town_id: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """
        Inject a perturbation event into a TownFlux.

        Body: {"operation": "greet"|"gossip"|"trade"|"solo", "participants": [...]}
        """
        import time

        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        now = time.time()
        last_perturb = _perturb_cooldowns.get(town_id, 0)
        if now - last_perturb < PERTURB_COOLDOWN_SECONDS:
            remaining = PERTURB_COOLDOWN_SECONDS - (now - last_perturb)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Cooldown active",
                    "code": "COOLDOWN",
                    "remaining_ms": int(remaining * 1000),
                },
            )

        try:
            body = await request.json()
        except Exception:
            body = {}

        operation = body.get("operation", "greet")
        participants = body.get("participants")

        valid_ops = {"greet", "gossip", "trade", "solo"}
        if operation not in valid_ops:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid operation: '{operation}'",
                    "code": "INVALID_OPERATION",
                    "available": list(valid_ops),
                },
            )

        flux = _town_fluxes.get(town_id)
        if flux is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Town '{town_id}' not found",
                    "code": "NOT_FOUND",
                    "suggestion": "Initialize town first via /api/v1/town/{town_id}/init",
                },
            )

        event = await flux.perturb_async(operation, participants)
        if event is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Could not execute perturbation",
                    "code": "EXECUTION_FAILED",
                },
            )

        _perturb_cooldowns[town_id] = now
        result: dict[str, Any] = event.to_dict()
        return result

    @router.post(
        "/town/{town_id}/step",
        tags=["town"],
        responses={
            200: {"description": "Step result"},
            404: {"model": ErrorResponse, "description": "Town not found"},
        },
    )
    async def step_town(
        town_id: str,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """Execute one step of the town simulation."""
        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        flux = _town_fluxes.get(town_id)
        if flux is None:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Town '{town_id}' not found", "code": "NOT_FOUND"},
            )

        events = []
        async for event in flux.step():
            events.append(event.to_dict())

        status = flux.get_status()
        status["town_id"] = town_id

        return {"events": events, "event_count": len(events), "status": status}

    @router.get(
        "/town/{town_id}/events",
        tags=["town"],
        responses={
            200: {"content": {"text/event-stream": {}}},
            404: {"model": ErrorResponse, "description": "Town not found"},
        },
    )
    async def stream_town_events(
        town_id: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> StreamingResponse:
        """Stream town events via SSE for real-time visualization."""
        import asyncio
        import json

        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        flux = _town_fluxes.get(town_id)
        if flux is None:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Town '{town_id}' not found", "code": "NOT_FOUND"},
            )

        async def event_generator() -> Any:
            from agents.town.isometric import IsometricWidget

            def build_isometric_payload() -> dict[str, Any]:
                """Build isometric payload with citizen data from flux."""
                widget_json = widget.to_json()
                # Inject citizens from flux (frontend expects this shape)
                widget_json["citizens"] = [
                    {
                        "id": c.id,
                        "name": c.name,
                        "archetype": c.archetype,
                        "region": c.region,
                        "phase": c.phase.name
                        if hasattr(c.phase, "name")
                        else str(c.phase),
                        "position": {"x": hash(c.id) % 10, "y": hash(c.name) % 10},
                        "energy": getattr(c, "energy", 1.0),
                        "mood": getattr(c, "mood", 0.5),
                    }
                    for c in flux.citizens
                ]
                widget_json["phase"] = flux.current_phase.name
                widget_json["day"] = flux.day
                return widget_json

            widget = IsometricWidget()
            status = flux.get_status()
            status["town_id"] = town_id
            yield f"event: town.status\ndata: {json.dumps(status)}\n\n"
            yield f"event: town.isometric\ndata: {json.dumps(build_isometric_payload())}\n\n"

            tick = 0
            while True:
                try:
                    async for event in flux.step():
                        yield f"event: town.event\ndata: {json.dumps(event.to_dict())}\n\n"
                        widget.update_from_event(event)
                        yield f"event: town.isometric\ndata: {json.dumps(build_isometric_payload())}\n\n"
                        tick += 1
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    yield f"event: error\ndata: {json.dumps({'error': str(e), 'tick': tick})}\n\n"
                    await asyncio.sleep(1.0)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # =========================================================================
    # Manifest Endpoint
    # =========================================================================

    @router.get(
        "/{context}/{holon}/manifest",
        response_model=AgenteseResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid path syntax"},
            403: {"model": ErrorResponse, "description": "Affordance denied"},
            404: {"model": ErrorResponse, "description": "Path not found"},
        },
    )
    async def manifest(
        context: str,
        holon: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> AgenteseResponse:
        """
        Manifest an entity to observer's perception.

        Collapse the entity to the observer's view.
        Different observers receive different renderings (Polymorphic Principle).

        Args:
            context: AGENTESE context (world, self, concept, void, time)
            holon: Entity/holon name
            request: HTTP request (for headers)
            api_key: Validated API key

        Returns:
            AgenteseResponse with observer-specific result

        Example:
            GET /api/v1/world/field/manifest
            X-Observer-Archetype: architect

            Returns the field's blueprint view for architects.
        """
        # Check scope
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        # Validate context
        if context not in VALID_CONTEXTS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid context: '{context}'",
                    "code": "SYNTAX_ERROR",
                    "available": list(VALID_CONTEXTS),
                    "suggestion": "Valid contexts: world, self, concept, void, time",
                },
            )

        # Get observer from headers
        observer = get_observer_from_headers(request)
        handle = f"{context}.{holon}.manifest"

        try:
            bridge = get_bridge()
            return await bridge.invoke(handle, observer)

        except BridgeError as e:
            raise HTTPException(
                status_code=get_http_status(e.error.code),
                detail=e.error.model_dump(),
            )

    # =========================================================================
    # Affordances Endpoint
    # =========================================================================

    @router.get(
        "/{context}/{holon}/affordances",
        response_model=AffordancesResponse,
        responses={
            404: {"model": ErrorResponse, "description": "Path not found"},
        },
    )
    async def list_affordances(
        context: str,
        holon: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> AffordancesResponse:
        """
        List available affordances for a path.

        Returns affordances filtered by observer archetype.

        Args:
            context: AGENTESE context
            holon: Entity/holon name
            request: HTTP request (for headers)
            api_key: Validated API key

        Returns:
            AffordancesResponse with available affordances

        Example:
            GET /api/v1/world/house/affordances
            X-Observer-Archetype: architect

            Returns ["manifest", "witness", "define", "spawn", ...] for architects.
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        if context not in VALID_CONTEXTS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid context: '{context}'",
                    "code": "SYNTAX_ERROR",
                    "available": list(VALID_CONTEXTS),
                },
            )

        observer = get_observer_from_headers(request)
        path = f"{context}.{holon}"

        bridge = get_bridge()
        affordances = await bridge.affordances(path, observer)

        return AffordancesResponse(
            path=path,
            affordances=affordances,
            observer_archetype=observer.archetype,
            handle=path,
        )

    # =========================================================================
    # Invoke Endpoint
    # =========================================================================

    @router.post(
        "/{context}/{holon}/{aspect}",
        response_model=AgenteseResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid syntax"},
            401: {"model": ErrorResponse, "description": "Observer required"},
            403: {"model": ErrorResponse, "description": "Affordance denied"},
            404: {"model": ErrorResponse, "description": "Path not found"},
            422: {"model": ErrorResponse, "description": "Law violation"},
        },
    )
    async def invoke(
        context: str,
        holon: str,
        aspect: str,
        request: Request,
        body: AgenteseRequest | None = None,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> AgenteseResponse:
        """
        Invoke an aspect on an entity.

        Execute an affordance. Observer must have permission.
        Returns aspect-specific result.

        Args:
            context: AGENTESE context
            holon: Entity/holon name
            aspect: Aspect to invoke
            request: HTTP request (for headers)
            body: Optional request body with kwargs
            api_key: Validated API key

        Returns:
            AgenteseResponse with invocation result

        Example:
            POST /api/v1/concept/justice/refine
            X-Observer-Archetype: philosopher
            Content-Type: application/json

            {"kwargs": {"challenge": "What about edge cases?"}}

            Returns dialectic result.
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        if context not in VALID_CONTEXTS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid context: '{context}'",
                    "code": "SYNTAX_ERROR",
                    "available": list(VALID_CONTEXTS),
                },
            )

        # Get observer - prefer body, fallback to headers
        if body and body.observer:
            observer = body.observer
        else:
            observer = get_observer_from_headers(request)

        # Build handle
        handle = f"{context}.{holon}.{aspect}"

        # Get kwargs from body
        kwargs = body.kwargs if body else {}

        try:
            bridge = get_bridge()
            return await bridge.invoke(handle, observer, kwargs)

        except BridgeError as e:
            raise HTTPException(
                status_code=get_http_status(e.error.code),
                detail=e.error.model_dump(),
            )

    # =========================================================================
    # Compose Endpoint
    # =========================================================================

    @router.post(
        "/compose",
        response_model=CompositionResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid syntax"},
            422: {"model": ErrorResponse, "description": "Composition error"},
        },
    )
    async def compose(
        body: CompositionRequest,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> CompositionResponse:
        """
        Execute a composition pipeline.

        Chain multiple AGENTESE paths into a pipeline.
        Preserves category laws (identity, associativity).

        Args:
            request: HTTP request (for headers)
            body: Composition request with paths
            api_key: Validated API key

        Returns:
            CompositionResponse with final result and trace

        Example:
            POST /api/v1/compose
            {
                "paths": [
                    "world.document.manifest",
                    "concept.summary.refine",
                    "self.memory.engram"
                ],
                "initial_input": null,
                "emit_law_check": true
            }

            Returns final result with pipeline trace and laws verified.
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        # Validate all paths have valid contexts
        for path in body.paths:
            parts = path.split(".")
            if len(parts) < 3:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": f"Path '{path}' must include aspect",
                        "code": "SYNTAX_ERROR",
                        "suggestion": "Format: context.holon.aspect",
                    },
                )
            context = parts[0]
            if context not in VALID_CONTEXTS:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": f"Invalid context '{context}' in path '{path}'",
                        "code": "SYNTAX_ERROR",
                        "available": list(VALID_CONTEXTS),
                    },
                )

        # Get observer
        if body.observer:
            observer = body.observer
        else:
            observer = get_observer_from_headers(request)

        try:
            bridge = get_bridge()
            return await bridge.compose(
                paths=body.paths,
                observer=observer,
                initial_input=body.initial_input,
                emit_law_check=body.emit_law_check,
            )

        except BridgeError as e:
            raise HTTPException(
                status_code=get_http_status(e.error.code),
                detail=e.error.model_dump(),
            )

    # =========================================================================
    # SSE Stream Endpoint
    # =========================================================================

    @router.get(
        "/{context}/{holon}/{aspect}/stream",
        responses={
            200: {"content": {"text/event-stream": {}}},
            400: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
        },
    )
    async def stream_invoke(
        context: str,
        holon: str,
        aspect: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> StreamingResponse:
        """
        Stream an AGENTESE invocation via SSE.

        For long-running operations like:
        - self.soul.challenge (LLM token streaming)
        - concept.*.dialectic (dialectic phases)

        Args:
            context: AGENTESE context
            holon: Entity/holon name
            aspect: Aspect to invoke
            request: HTTP request (for headers and query params)
            api_key: Validated API key

        Returns:
            StreamingResponse with SSE events

        Example:
            GET /api/v1/self/soul/challenge/stream?challenge=What+is+justice%3F
            Accept: text/event-stream
            X-Observer-Archetype: philosopher

            event: chunk
            data: {"type": "response", "content": "Justice is", "partial": true}

            event: done
            data: {"result": "...", "span_id": "..."}
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        if context not in VALID_CONTEXTS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid context: '{context}'",
                    "code": "SYNTAX_ERROR",
                    "available": list(VALID_CONTEXTS),
                },
            )

        observer = get_observer_from_headers(request)
        handle = f"{context}.{holon}.{aspect}"

        # Get kwargs from query params
        kwargs: dict[str, Any] = {}
        for key, value in request.query_params.items():
            if key not in ("api_key",):  # Exclude auth params
                kwargs[key] = value

        bridge = get_bridge()

        async def event_generator() -> Any:
            """Generate SSE events from bridge stream."""
            async for event in bridge.stream(handle, observer, kwargs):
                yield event.serialize()

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # =========================================================================
    # Law Verification Endpoint
    # =========================================================================

    @router.post(
        "/verify-laws",
        responses={
            200: {"description": "Law verification result"},
        },
    )
    async def verify_laws(
        body: CompositionRequest,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """
        Verify category laws for a composition.

        Checks identity and associativity laws.

        Args:
            request: HTTP request
            body: Composition request with paths
            api_key: Validated API key

        Returns:
            LawVerificationResult as dict
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        if body.observer:
            observer = body.observer
        else:
            observer = get_observer_from_headers(request)

        bridge = get_bridge()
        result = await bridge.verify_laws(body.paths, observer)

        return result.model_dump()

    # =========================================================================
    # Resolve Endpoint
    # =========================================================================

    @router.get(
        "/{context}/{holon}/resolve",
        responses={
            200: {"description": "Path resolution result"},
            400: {"model": ErrorResponse},
        },
    )
    async def resolve_path(
        context: str,
        holon: str,
        request: Request,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> dict[str, Any]:
        """
        Resolve an AGENTESE path without invoking.

        Returns metadata about the path.

        Args:
            context: AGENTESE context
            holon: Entity/holon name
            request: HTTP request
            api_key: Validated API key

        Returns:
            Path resolution metadata
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        if context not in VALID_CONTEXTS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid context: '{context}'",
                    "code": "SYNTAX_ERROR",
                    "available": list(VALID_CONTEXTS),
                },
            )

        observer = get_observer_from_headers(request)
        path = f"{context}.{holon}"

        bridge = get_bridge()
        return await bridge.resolve(path, observer)

    # Town endpoints moved to top of router (before generic routes) - see line 154

    return router
