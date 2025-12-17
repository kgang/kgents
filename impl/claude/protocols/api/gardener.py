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
    GardenComputedResponse,
    GardenMetricsResponse,
    GardenSeason,
    GardenStateResponse,
    GestureResponse,
    PlotResponse,
    # Phase 2 Crown Jewels: Plot CRUD
    PlotCreateRequest,
    PlotListResponse,
    PlotUpdateRequest,
    PolynomialEdge,
    PolynomialHistoryEntry,
    PolynomialPosition,
    PolynomialVisualization,
    PolynomialVisualizationResponse,
    SeasonTransitionRequest,
    TendingVerb,
    TendRequest,
    TendResponse,
    # Phase 8: Auto-Inducer models
    TendResponseWithSuggestion,
    TransitionAcceptRequest,
    TransitionActionResponse,
    TransitionDismissRequest,
    TransitionSignalsResponse,
    TransitionSuggestionResponse,
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

    # =========================================================================
    # Garden State Endpoints (Phase 7: Web Visualization)
    # =========================================================================

    @router.get("/garden", response_model=GardenStateResponse)
    async def get_garden(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenStateResponse:
        """
        Get current garden state.

        Returns the full garden state including:
        - Season and plasticity
        - All plots with progress
        - Recent gestures
        - Health metrics
        """
        try:
            garden = await _get_or_create_garden()
            return _garden_to_response(garden)
        except Exception as e:
            logger.exception("Failed to get garden state")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/garden/tend", response_model=TendResponseWithSuggestion)
    async def apply_tend(
        request: TendRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> TendResponseWithSuggestion:
        """
        Apply a tending gesture to the garden.

        The six primitive gestures:
        - OBSERVE: Perceive without changing
        - PRUNE: Remove what no longer serves
        - GRAFT: Add something new
        - WATER: Nurture via TextGRAD
        - ROTATE: Change perspective
        - WAIT: Allow time to pass

        Phase 8: May include a suggested season transition if activity
        patterns indicate the garden should change seasons.
        """
        try:
            from protocols.gardener_logos.tending import (
                TendingGesture,
                TendingVerb as GardenTendingVerb,
                apply_gesture,
            )

            garden = await _get_or_create_garden()

            # Convert API verb to garden verb
            verb = GardenTendingVerb[request.verb.value]

            gesture = TendingGesture(
                verb=verb,
                target=request.target,
                tone=request.tone,
                reasoning=request.reasoning,
                entropy_cost=verb.base_entropy_cost,
            )

            result = await apply_gesture(garden, gesture, emit_event=True)

            # Convert transition suggestion if present (Phase 8: Auto-Inducer)
            suggestion_response: TransitionSuggestionResponse | None = None
            if result.suggested_transition is not None:
                st = result.suggested_transition
                suggestion_response = TransitionSuggestionResponse(
                    from_season=GardenSeason(st.from_season.name),
                    to_season=GardenSeason(st.to_season.name),
                    confidence=st.confidence,
                    reason=st.reason,
                    signals=TransitionSignalsResponse(
                        gesture_frequency=st.signals.gesture_frequency,
                        gesture_diversity=st.signals.gesture_diversity,
                        plot_progress_delta=st.signals.plot_progress_delta,
                        artifacts_created=st.signals.artifacts_created,
                        time_in_season_hours=st.signals.time_in_season_hours,
                        entropy_spent_ratio=st.signals.entropy_spent_ratio,
                        reflect_count=st.signals.reflect_count,
                        session_active=st.signals.session_active,
                    ),
                    triggered_at=st.triggered_at.isoformat(),
                )

            # Convert result to response
            return TendResponseWithSuggestion(
                accepted=result.accepted,
                state_changed=result.state_changed,
                changes=result.changes,
                synergies_triggered=result.synergies_triggered,
                reasoning_trace=list(result.reasoning_trace),
                error=result.error,
                gesture=GestureResponse(
                    verb=TendingVerb(gesture.verb.name),
                    target=gesture.target,
                    tone=gesture.tone,
                    reasoning=gesture.reasoning,
                    entropy_cost=gesture.entropy_cost,
                    timestamp=gesture.timestamp.isoformat(),
                    observer=gesture.observer,
                    session_id=gesture.session_id,
                    result_summary=gesture.result_summary,
                ),
                suggested_transition=suggestion_response,
            )
        except Exception as e:
            logger.exception("Failed to apply tending gesture")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/garden/season", response_model=GardenStateResponse)
    async def transition_season(
        request: SeasonTransitionRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenStateResponse:
        """
        Transition the garden to a new season.

        Seasons affect plasticity and entropy costs:
        - DORMANT: Low plasticity (0.1), cheap operations
        - SPROUTING: High plasticity (0.9), expensive growth
        - BLOOMING: Medium plasticity (0.3), crystallizing
        - HARVEST: Low plasticity (0.2), efficient gathering
        - COMPOSTING: High plasticity (0.8), breaking down patterns
        """
        try:
            from protocols.gardener_logos.garden import GardenSeason as GardenSeasonEnum

            garden = await _get_or_create_garden()
            new_season = GardenSeasonEnum[request.new_season.value]
            garden.transition_season(new_season, request.reason)

            return _garden_to_response(garden)
        except Exception as e:
            logger.exception("Failed to transition season")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/garden/plot/{plot_name}/focus", response_model=GardenStateResponse)
    async def focus_plot(
        plot_name: str,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> GardenStateResponse:
        """Set the active plot focus."""
        try:
            garden = await _get_or_create_garden()

            if plot_name not in garden.plots:
                raise HTTPException(status_code=404, detail=f"Plot '{plot_name}' not found")

            garden.active_plot = plot_name
            return _garden_to_response(garden)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to focus plot")
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Plot CRUD Endpoints (Phase 2 Crown Jewels completion)
    # =========================================================================

    @router.get("/garden/plots", response_model=PlotListResponse)
    async def list_plots(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> PlotListResponse:
        """List all plots in the garden."""
        try:
            garden = await _get_or_create_garden()
            garden_response = _garden_to_response(garden)
            return PlotListResponse(
                plots=list(garden_response.plots.values()),
                total_count=len(garden_response.plots),
                active_plot=garden_response.active_plot,
            )
        except Exception as e:
            logger.exception("Failed to list plots")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/garden/plots/{plot_name}", response_model=PlotResponse)
    async def get_plot(
        plot_name: str,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> PlotResponse:
        """Get a specific plot by name."""
        try:
            garden = await _get_or_create_garden()

            if plot_name not in garden.plots:
                raise HTTPException(status_code=404, detail=f"Plot '{plot_name}' not found")

            garden_response = _garden_to_response(garden)
            return garden_response.plots[plot_name]
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to get plot")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/garden/plots", response_model=PlotResponse)
    async def create_plot(
        request: PlotCreateRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> PlotResponse:
        """Create a new garden plot."""
        try:
            from datetime import datetime

            from protocols.gardener_logos.plots import PlotState

            garden = await _get_or_create_garden()

            # Check for duplicate name
            if request.name in garden.plots:
                raise HTTPException(
                    status_code=400,
                    detail=f"Plot '{request.name}' already exists",
                )

            # Create the plot (note: created_at and last_tended are datetime objects)
            now = datetime.now()
            plot = PlotState(
                name=request.name,
                path=request.path,
                description=request.description,
                plan_path=request.plan_path,
                crown_jewel=request.crown_jewel,
                rigidity=request.rigidity,
                progress=0.0,
                created_at=now,
                last_tended=now,
                tags=request.tags,
                metadata=request.metadata,
            )

            # Add to garden
            garden.plots[request.name] = plot
            garden.metrics.active_plots = len(garden.plots)

            # Return the created plot
            return PlotResponse(
                name=plot.name,
                path=plot.path,
                description=plot.description,
                plan_path=plot.plan_path,
                crown_jewel=plot.crown_jewel,
                prompts=[],
                season_override=None,
                rigidity=plot.rigidity,
                progress=plot.progress,
                created_at=plot.created_at.isoformat(),
                last_tended=plot.last_tended.isoformat(),
                tags=plot.tags,
                metadata=plot.metadata,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to create plot")
            raise HTTPException(status_code=500, detail=str(e))

    @router.patch("/garden/plots/{plot_name}", response_model=PlotResponse)
    async def update_plot(
        plot_name: str,
        request: PlotUpdateRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> PlotResponse:
        """Update a garden plot."""
        try:
            from datetime import datetime

            garden = await _get_or_create_garden()

            if plot_name not in garden.plots:
                raise HTTPException(status_code=404, detail=f"Plot '{plot_name}' not found")

            plot = garden.plots[plot_name]

            # Update fields if provided
            if request.description is not None:
                plot.description = request.description
            if request.progress is not None:
                plot.progress = request.progress
            if request.rigidity is not None:
                plot.rigidity = request.rigidity
            if request.season_override is not None:
                from protocols.gardener_logos.garden import GardenSeason as GardenSeasonEnum

                plot.season_override = GardenSeasonEnum[request.season_override.value]
            if request.tags is not None:
                plot.tags = request.tags
            if request.metadata is not None:
                plot.metadata = request.metadata

            # Update last_tended (datetime object)
            plot.last_tended = datetime.now()

            # Return the updated plot
            garden_response = _garden_to_response(garden)
            return garden_response.plots[plot_name]
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to update plot")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/garden/plots/{plot_name}")
    async def delete_plot(
        plot_name: str,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> dict[str, str]:
        """Delete a garden plot."""
        try:
            garden = await _get_or_create_garden()

            if plot_name not in garden.plots:
                raise HTTPException(status_code=404, detail=f"Plot '{plot_name}' not found")

            # Remove the plot
            del garden.plots[plot_name]
            garden.metrics.active_plots = len(garden.plots)

            # Clear active_plot if it was the deleted one
            if garden.active_plot == plot_name:
                garden.active_plot = None

            return {"status": "deleted", "plot": plot_name}
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to delete plot")
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Auto-Inducer Endpoints (Phase 8: Season Transition Suggestions)
    # =========================================================================

    @router.post("/garden/transition/accept", response_model=TransitionActionResponse)
    async def accept_transition(
        request: TransitionAcceptRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> TransitionActionResponse:
        """
        Accept a suggested season transition.

        Applies the transition and returns the updated garden state.
        Also clears any dismissals for this garden.
        """
        try:
            from protocols.gardener_logos.garden import GardenSeason as GardenSeasonEnum
            from protocols.gardener_logos.seasons import clear_dismissals

            garden = await _get_or_create_garden()

            # Validate current season matches
            if garden.season.name != request.from_season.value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Garden is in {garden.season.name}, not {request.from_season.value}",
                )

            # Apply the transition
            new_season = GardenSeasonEnum[request.to_season.value]
            garden.transition_season(new_season, f"User accepted {new_season.name} transition")

            # Clear dismissals since we're accepting
            clear_dismissals(garden.garden_id)

            return TransitionActionResponse(
                status="accepted",
                garden_state=_garden_to_response(garden),
                message=f"Transitioned from {request.from_season.value} to {request.to_season.value}",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to accept transition")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/garden/transition/dismiss", response_model=TransitionActionResponse)
    async def dismiss_transition(
        request: TransitionDismissRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> TransitionActionResponse:
        """
        Dismiss a suggested season transition.

        Records the dismissal so the same transition won't be
        suggested again for a cooldown period (default: 4 hours).
        """
        try:
            from protocols.gardener_logos.garden import GardenSeason as GardenSeasonEnum
            from protocols.gardener_logos.seasons import dismiss_transition

            garden = await _get_or_create_garden()

            # Record the dismissal
            from_season = GardenSeasonEnum[request.from_season.value]
            to_season = GardenSeasonEnum[request.to_season.value]
            dismiss_transition(garden.garden_id, from_season, to_season)

            return TransitionActionResponse(
                status="dismissed",
                garden_state=None,  # Garden state unchanged
                message=f"Dismissed {from_season.name} → {to_season.name} suggestion (won't suggest for 4h)",
            )
        except Exception as e:
            logger.exception("Failed to dismiss transition")
            raise HTTPException(status_code=500, detail=str(e))

    return router


# =============================================================================
# Garden State Helpers
# =============================================================================

_garden_state: Any = None
_garden_lock = threading.Lock()


async def _get_or_create_garden() -> Any:
    """Get or create the default garden state."""
    global _garden_state

    if _garden_state is None:
        with _garden_lock:
            if _garden_state is None:
                from protocols.gardener_logos.garden import create_garden
                from protocols.gardener_logos.plots import create_crown_jewel_plots

                _garden_state = create_garden(name="Default Garden")
                _garden_state.plots = create_crown_jewel_plots()
                _garden_state.metrics.active_plots = len(_garden_state.plots)

    return _garden_state


def _garden_to_response(garden: Any) -> GardenStateResponse:
    """Convert GardenState to API response."""
    from protocols.gardener_logos.projections.json import project_garden_to_json

    data = project_garden_to_json(garden)

    # Convert plots
    plots = {}
    for name, plot_data in data.get("plots", {}).items():
        plots[name] = PlotResponse(
            name=plot_data["name"],
            path=plot_data["path"],
            description=plot_data.get("description", ""),
            plan_path=plot_data.get("plan_path"),
            crown_jewel=plot_data.get("crown_jewel"),
            prompts=plot_data.get("prompts", []),
            season_override=GardenSeason(plot_data["season_override"])
            if plot_data.get("season_override")
            else None,
            rigidity=plot_data.get("rigidity", 0.5),
            progress=plot_data.get("progress", 0.0),
            created_at=plot_data.get("created_at", ""),
            last_tended=plot_data.get("last_tended", ""),
            tags=plot_data.get("tags", []),
            metadata=plot_data.get("metadata", {}),
        )

    # Convert gestures
    gestures = []
    for g in data.get("recent_gestures", []):
        gestures.append(
            GestureResponse(
                verb=TendingVerb(g["verb"]),
                target=g["target"],
                tone=g.get("tone", 0.5),
                reasoning=g.get("reasoning", ""),
                entropy_cost=g.get("entropy_cost", 0.0),
                timestamp=g.get("timestamp", ""),
                observer=g.get("observer", "default"),
                session_id=g.get("session_id"),
                result_summary=g.get("result_summary", ""),
            )
        )

    # Build computed
    computed_data = data.get("computed", {})
    computed = GardenComputedResponse(
        health_score=computed_data.get("health_score", 0.0),
        entropy_remaining=computed_data.get("entropy_remaining", 0.0),
        entropy_percentage=computed_data.get("entropy_percentage", 0.0),
        active_plot_count=computed_data.get("active_plot_count", 0),
        total_plot_count=computed_data.get("total_plot_count", 0),
        season_plasticity=computed_data.get("season_plasticity", 0.5),
        season_entropy_multiplier=computed_data.get("season_entropy_multiplier", 1.0),
    )

    # Build metrics
    metrics_data = data.get("metrics", {})
    metrics = GardenMetricsResponse(
        health_score=metrics_data.get("health_score", 0.0),
        total_prompts=metrics_data.get("total_prompts", 0),
        active_plots=metrics_data.get("active_plots", 0),
        entropy_spent=metrics_data.get("entropy_spent", 0.0),
        entropy_budget=metrics_data.get("entropy_budget", 1.0),
    )

    return GardenStateResponse(
        garden_id=data.get("garden_id", ""),
        name=data.get("name", "Default Garden"),
        created_at=data.get("created_at", ""),
        season=GardenSeason(data.get("season", "DORMANT")),
        season_since=data.get("season_since", ""),
        plots=plots,
        active_plot=data.get("active_plot"),
        session_id=data.get("session_id"),
        memory_crystals=data.get("memory_crystals", []),
        prompt_count=data.get("prompt_count", 0),
        prompt_types=data.get("prompt_types", {}),
        recent_gestures=gestures,
        last_tended=data.get("last_tended", ""),
        metrics=metrics,
        computed=computed,
    )
