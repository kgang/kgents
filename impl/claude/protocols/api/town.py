"""
Agent Town API Endpoints (Phase 4).

Exposes Agent Town simulation via REST/SSE API:
- POST /v1/town - Create a new town simulation
- GET /v1/town/{id} - Get town state
- GET /v1/town/{id}/citizens - List citizens
- GET /v1/town/{id}/citizen/{name} - Get citizen details (LOD 0-5)
- GET /v1/town/{id}/coalitions - Get detected coalitions
- POST /v1/town/{id}/step - Advance simulation
- GET /v1/town/{id}/events - SSE stream of town events

Synergy S4: API Router Pattern from protocols/api/sessions.py
Synergy S7: MeteringMiddleware for per-citizen-turn billing
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException, Request
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    BaseModel = object  # type: ignore
    StreamingResponse = None  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Pydantic Models ---


class CreateTownRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to create a new town simulation."""

    name: Optional[str] = Field(
        default=None,
        description="Town name",
        examples=["smallville-custom"],
    )
    phase: int = Field(
        default=4,
        description="Phase level (3=10 citizens, 4=25 citizens)",
        ge=3,
        le=4,
    )
    similarity_threshold: float = Field(
        default=0.8,
        description="Coalition detection similarity threshold",
        ge=0.0,
        le=1.0,
    )
    enable_dialogue: bool = Field(
        default=False,
        description="Enable real LLM dialogue for citizens (requires LLM credentials)",
    )


class TownResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with town state summary."""

    id: str = Field(..., description="Town ID")
    name: str = Field(..., description="Town name")
    citizen_count: int = Field(..., description="Number of citizens")
    region_count: int = Field(..., description="Number of regions")
    coalition_count: int = Field(default=0, description="Number of coalitions")
    total_token_spend: int = Field(default=0, description="Total LLM tokens used")
    status: str = Field(default="active", description="Simulation status")


class CitizenSummary(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Summary of a citizen."""

    id: str = Field(..., description="Citizen ID")
    name: str = Field(..., description="Citizen name")
    archetype: str = Field(..., description="Citizen archetype")
    region: str = Field(..., description="Current region")
    phase: str = Field(..., description="Current phase")
    is_evolving: bool = Field(default=False, description="Whether citizen evolves")


class CitizensResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with list of citizens."""

    town_id: str = Field(..., description="Town ID")
    citizens: list[CitizenSummary] = Field(..., description="List of citizens")
    total: int = Field(..., description="Total citizens")
    by_archetype: dict[str, int] = Field(..., description="Counts by archetype")
    by_region: dict[str, int] = Field(..., description="Counts by region")


class CitizenDetailResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with citizen details at specified LOD."""

    town_id: str = Field(..., description="Town ID")
    lod: int = Field(..., description="Level of detail requested")
    citizen: dict[str, Any] = Field(..., description="Citizen manifest at LOD")


class CoalitionSummary(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Summary of a coalition."""

    id: str = Field(..., description="Coalition ID")
    name: str = Field(..., description="Coalition name")
    members: list[str] = Field(..., description="Member citizen IDs")
    size: int = Field(..., description="Number of members")
    strength: float = Field(..., description="Coalition strength")


class CoalitionsResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with detected coalitions."""

    town_id: str = Field(..., description="Town ID")
    coalitions: list[CoalitionSummary] = Field(..., description="List of coalitions")
    total: int = Field(..., description="Total coalitions")
    bridge_citizens: list[str] = Field(
        ..., description="Citizens in multiple coalitions"
    )


class StepRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to advance simulation."""

    cycles: int = Field(
        default=1,
        description="Number of cycles to advance",
        ge=1,
        le=100,
    )
    decay_coalitions: bool = Field(
        default=True,
        description="Whether to apply coalition decay",
    )
    redetect_coalitions: bool = Field(
        default=True,
        description="Whether to redetect coalitions after step",
    )


class StepResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response after stepping simulation."""

    town_id: str = Field(..., description="Town ID")
    cycles_run: int = Field(..., description="Number of cycles executed")
    evolving_citizens_updated: int = Field(
        ..., description="Number of evolving citizens updated"
    )
    coalitions_detected: int = Field(..., description="Coalitions after step")
    coalitions_decayed: int = Field(
        default=0, description="Coalitions removed due to decay"
    )


# --- In-Memory Storage ---
# In production, this would use a database. For now, simple dict.


_towns: dict[str, dict[str, Any]] = {}


def _get_town(town_id: str) -> dict[str, Any]:
    """Get town by ID or raise 404."""
    if town_id not in _towns:
        raise HTTPException(status_code=404, detail=f"Town {town_id} not found")
    return _towns[town_id]


# --- Router Factory ---


def create_town_router() -> "APIRouter | None":
    """
    Create the town API router.

    Returns None if FastAPI is not available.
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/v1/town", tags=["town"])

    @router.post("", response_model=TownResponse)
    async def create_town(request: CreateTownRequest) -> TownResponse:
        """Create a new town simulation."""
        from agents.town.coalition import CoalitionManager
        from agents.town.environment import (
            create_phase3_environment,
            create_phase4_environment,
            get_citizen_count_by_region,
        )

        # Create environment based on phase
        if request.phase == 4:
            env = create_phase4_environment()
        else:
            env = create_phase3_environment()

        # Override name if provided
        if request.name:
            env.name = request.name

        # Create coalition manager
        coalition_manager = CoalitionManager(
            env.citizens,
            similarity_threshold=request.similarity_threshold,
        )
        coalition_manager.detect()

        # Generate town ID
        town_id = str(uuid4())[:8]

        # Store town state
        _towns[town_id] = {
            "id": town_id,
            "env": env,
            "coalition_manager": coalition_manager,
            "status": "active",
        }

        return TownResponse(
            id=town_id,
            name=env.name,
            citizen_count=len(env.citizens),
            region_count=len(env.regions),
            coalition_count=len(coalition_manager.coalitions),
            total_token_spend=env.total_token_spend,
            status="active",
        )

    @router.get("/{town_id}", response_model=TownResponse)
    async def get_town(town_id: str) -> TownResponse:
        """Get town state summary."""
        town = _get_town(town_id)
        env = town["env"]
        cm = town["coalition_manager"]

        return TownResponse(
            id=town_id,
            name=env.name,
            citizen_count=len(env.citizens),
            region_count=len(env.regions),
            coalition_count=len(cm.coalitions),
            total_token_spend=env.total_token_spend,
            status=town["status"],
        )

    @router.get("/{town_id}/citizens", response_model=CitizensResponse)
    async def get_citizens(town_id: str) -> CitizensResponse:
        """Get all citizens in town."""
        from agents.town.environment import (
            get_citizen_count_by_region,
            get_evolving_citizens,
        )
        from agents.town.evolving import EvolvingCitizen

        town = _get_town(town_id)
        env = town["env"]

        evolving_ids = {c.id for c in get_evolving_citizens(env)}

        citizens = []
        archetype_counts: dict[str, int] = {}
        for cid, citizen in env.citizens.items():
            citizens.append(
                CitizenSummary(
                    id=citizen.id,
                    name=citizen.name,
                    archetype=citizen.archetype,
                    region=citizen.region,
                    phase=citizen.phase.name,
                    is_evolving=citizen.id in evolving_ids,
                )
            )
            archetype_counts[citizen.archetype] = (
                archetype_counts.get(citizen.archetype, 0) + 1
            )

        return CitizensResponse(
            town_id=town_id,
            citizens=citizens,
            total=len(citizens),
            by_archetype=archetype_counts,
            by_region=get_citizen_count_by_region(env),
        )

    @router.get("/{town_id}/citizen/{name}", response_model=CitizenDetailResponse)
    async def get_citizen(
        town_id: str, name: str, lod: int = 0, user_id: str = "anonymous"
    ) -> CitizenDetailResponse:
        """
        Get citizen details at specified Level of Detail.

        LOD 0-2: Free for all users
        LOD 3-5: Requires credits or subscription allowance

        Returns 402 Payment Required if user lacks access.
        """
        import time

        from agents.town.budget_store import InMemoryBudgetStore
        from agents.town.paywall import ActionType as PaywallActionType
        from agents.town.paywall import PaywallCheck, check_paywall
        from protocols.api.action_metrics import (
            ACTION_CREDITS,
            ActionType,
            emit_action_metric,
        )

        town = _get_town(town_id)
        env = town["env"]

        citizen = env.get_citizen_by_name(name)
        if not citizen:
            raise HTTPException(
                status_code=404, detail=f"Citizen {name} not found in town"
            )

        # Clamp LOD to valid range
        lod = max(0, min(5, lod))

        # Get or create budget store for this town
        if "budget_store" not in town:
            town["budget_store"] = InMemoryBudgetStore()
        budget_store = town["budget_store"]

        # Get or create user budget
        user_budget = await budget_store.get_or_create(user_id)

        # Check paywall for LOD 3-5 (billable actions)
        if lod >= 3:
            lod_action_map = {
                3: PaywallActionType.LOD_3,
                4: PaywallActionType.LOD_4,
                5: PaywallActionType.LOD_5,
            }
            paywall_action = lod_action_map.get(lod, PaywallActionType.LOD_3)

            paywall_result = check_paywall(
                PaywallCheck(
                    user_budget=user_budget,
                    action=paywall_action,
                )
            )

            if not paywall_result.allowed:
                # Return 402 Payment Required with upgrade options
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "payment_required",
                        "message": paywall_result.reason,
                        "upgrade_options": [
                            {
                                "type": opt.type,
                                "tier": opt.tier,
                                "credits": opt.credits,
                                "price_usd": opt.price_usd,
                                "unlocks": opt.unlocks,
                            }
                            for opt in paywall_result.upgrade_options
                        ],
                    },
                )

            # Charge credits if not using included allowance
            if not paywall_result.uses_included and paywall_result.cost_credits > 0:
                await budget_store.record_action(
                    user_id, paywall_action.value, paywall_result.cost_credits
                )

        # Track metrics and generate manifest
        start = time.monotonic()
        manifest = citizen.manifest(lod=lod)
        latency_ms = int((time.monotonic() - start) * 1000)

        # Emit metric for LOD 3-5 (billable actions)
        if lod >= 3:
            action_type_map = {
                3: ActionType.LOD3,
                4: ActionType.LOD4,
                5: ActionType.LOD5,
            }
            action_type = action_type_map.get(lod, ActionType.LOD3)
            credits = ACTION_CREDITS.get(action_type, 0)

            # Model is template for manifest (no LLM call)
            emit_action_metric(
                action_type=action_type.value,
                user_id=user_id,
                town_id=town_id,
                citizen_id=citizen.id,
                tokens_in=0,
                tokens_out=0,
                model="template",
                latency_ms=latency_ms,
                credits_charged=credits,
                metadata={"lod": lod, "citizen_name": citizen.name},
            )

        return CitizenDetailResponse(
            town_id=town_id,
            lod=lod,
            citizen=manifest,
        )

    @router.get("/{town_id}/coalitions", response_model=CoalitionsResponse)
    async def get_coalitions(town_id: str) -> CoalitionsResponse:
        """Get detected coalitions."""
        town = _get_town(town_id)
        cm = town["coalition_manager"]

        coalitions = []
        for coalition in cm.coalitions.values():
            coalitions.append(
                CoalitionSummary(
                    id=coalition.id,
                    name=coalition.name,
                    members=list(coalition.members),
                    size=coalition.size,
                    strength=coalition.strength,
                )
            )

        return CoalitionsResponse(
            town_id=town_id,
            coalitions=coalitions,
            total=len(coalitions),
            bridge_citizens=cm.get_bridge_citizens(),
        )

    @router.post("/{town_id}/step", response_model=StepResponse)
    async def step_simulation(town_id: str, request: StepRequest) -> StepResponse:
        """Advance simulation by N cycles."""
        from agents.town.environment import get_evolving_citizens
        from agents.town.evolving import Observation

        town = _get_town(town_id)
        env = town["env"]
        cm = town["coalition_manager"]

        evolving = get_evolving_citizens(env)
        evolving_updated = 0
        coalitions_decayed = 0

        for _ in range(request.cycles):
            # Evolve citizens
            for citizen in evolving:
                # Simple observation for demo
                obs = Observation(
                    content=f"Cycle observation from {citizen.region}",
                    source="environment",
                    emotional_weight=0.1,
                )
                await citizen.evolve(obs)
                evolving_updated += 1

            # Decay coalitions
            if request.decay_coalitions:
                coalitions_decayed += cm.decay_all(0.05)

        # Redetect coalitions
        if request.redetect_coalitions:
            cm.detect()

        return StepResponse(
            town_id=town_id,
            cycles_run=request.cycles,
            evolving_citizens_updated=evolving_updated,
            coalitions_detected=len(cm.coalitions),
            coalitions_decayed=coalitions_decayed,
        )

    @router.get("/{town_id}/reputation")
    async def get_reputation(town_id: str) -> dict[str, Any]:
        """Get computed reputation scores."""
        town = _get_town(town_id)
        env = town["env"]
        cm = town["coalition_manager"]

        reputation = cm.compute_reputation()

        # Add citizen names to output
        reputation_with_names = []
        for cid, score in sorted(reputation.items(), key=lambda x: -x[1]):
            citizen = env.citizens.get(cid)
            name = citizen.name if citizen else "unknown"
            reputation_with_names.append(
                {
                    "citizen_id": cid,
                    "name": name,
                    "reputation": round(score, 4),
                }
            )

        return {
            "town_id": town_id,
            "reputation": reputation_with_names,
            "total_citizens": len(reputation),
        }

    @router.delete("/{town_id}")
    async def delete_town(town_id: str) -> dict[str, str]:
        """Delete a town simulation."""
        if town_id not in _towns:
            raise HTTPException(status_code=404, detail=f"Town {town_id} not found")
        del _towns[town_id]
        return {"status": "deleted", "town_id": town_id}

    @router.get("/{town_id}/metrics")
    async def get_metrics(
        town_id: str,
        action_type: str | None = None,
        since_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Get action metrics for this town.

        Query metrics emitted by billable actions (LOD, INHABIT, FORCE, etc.).

        Args:
            town_id: Town ID
            action_type: Optional filter by action type (lod3, lod4, etc.)
            since_hours: Time window in hours (default 24)

        Returns:
            Aggregated metrics including:
            - count: Total actions
            - total_tokens: Total tokens consumed
            - total_credits: Total credits charged
            - avg_latency_ms: Average latency
            - p50/p95_latency_ms: Latency percentiles
            - by_model: Breakdown by model
        """
        from datetime import datetime, timedelta

        from protocols.api.action_metrics import get_metrics_store

        # Verify town exists
        _get_town(town_id)

        # Query metrics store
        store = get_metrics_store()
        since = datetime.now() - timedelta(hours=since_hours)

        agg = store.aggregate(
            town_id=town_id,
            action_type=action_type,
            since=since,
        )

        return {
            "town_id": town_id,
            "action_type": action_type or "all",
            "time_window_hours": since_hours,
            "metrics": agg,
        }

    @router.get("/{town_id}/events")
    async def stream_events(town_id: str) -> StreamingResponse:
        """
        Stream town events via Server-Sent Events.

        Returns an SSE stream with events:
        - town.status: Status updates
        - town.{phase}.{operation}: Town events (greet, gossip, trade, etc.)
        - town.coalition.{change}: Coalition changes
        - town.eigenvector.drift: Eigenvector drift events
        """
        from agents.town.visualization import TownSSEEndpoint

        town = _get_town(town_id)

        # Create or get SSE endpoint for this town
        if "sse_endpoint" not in town:
            town["sse_endpoint"] = TownSSEEndpoint(town_id)

        endpoint = town["sse_endpoint"]

        return StreamingResponse(
            endpoint.generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # For nginx
            },
        )

    @router.get("/{town_id}/live")
    async def stream_live(
        town_id: str,
        phases: int = 4,
        speed: float = 1.0,
    ) -> StreamingResponse:
        """
        Live orchestration with governed playback via SSE.

        Streams TownEvents at governed intervals with playback control.

        Args:
            town_id: Town ID
            phases: Number of phases to run (default 4 = one day)
            speed: Playback speed multiplier (0.5 to 4.0)

        Events:
            - live.start: Orchestration started
            - live.event: TownEvent (phase, operation, participants, etc.)
            - live.phase: Phase transition
            - live.end: Orchestration ended

        Example SSE output:
            event: live.start
            data: {"town_id": "abc123", "phases": 4, "speed": 1.0}

            event: live.event
            data: {"tick": 1, "phase": "MORNING", "operation": "greet", ...}
        """
        import asyncio
        import json

        from agents.town.event_bus import EventBus
        from agents.town.flux import TownFlux
        from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig

        town = _get_town(town_id)
        env = town["env"]

        # Clamp speed to valid range
        speed = max(0.5, min(4.0, speed))

        async def generate() -> AsyncIterator[str]:
            """Generate SSE events with governed playback."""
            # Create event bus
            event_bus: EventBus[Any] = EventBus()

            # Create flux with event bus
            flux = TownFlux(env, seed=42, event_bus=event_bus)

            # Create governor
            config = PhaseTimingConfig(
                phase_duration_ms=5000,
                events_per_phase=5,
                playback_speed=speed,
                min_event_delay_ms=200,
                max_event_delay_ms=2000,
            )
            governor = PhaseGovernor(flux=flux, config=config, event_bus=event_bus)

            # Send start event
            start_data = json.dumps(
                {
                    "town_id": town_id,
                    "phases": phases,
                    "speed": speed,
                }
            )
            yield f"event: live.start\ndata: {start_data}\n\n"

            # Run with governed playback
            tick = 0
            current_phase = None

            try:
                async for event in governor.run(num_phases=phases):
                    tick += 1

                    # Check for phase transition
                    if event.phase.name != current_phase:
                        current_phase = event.phase.name
                        phase_data = json.dumps(
                            {
                                "tick": tick,
                                "phase": current_phase,
                            }
                        )
                        yield f"event: live.phase\ndata: {phase_data}\n\n"

                    # Send event with dialogue fields if present
                    event_data_dict: dict[str, Any] = {
                        "tick": tick,
                        "phase": event.phase.name,
                        "operation": event.operation,
                        "participants": event.participants,
                        "success": event.success,
                        "message": event.message,
                        "tokens_used": event.tokens_used,
                        "timestamp": event.timestamp.isoformat(),
                    }

                    # Include dialogue fields if dialogue was generated
                    if event.dialogue:
                        event_data_dict["dialogue"] = {
                            "text": event.dialogue,
                            "tokens": event.dialogue_tokens,
                            "model": event.dialogue_model,
                            "was_template": event.dialogue_was_template,
                            "grounded_memories": event.dialogue_grounded,
                        }

                    event_data = json.dumps(event_data_dict)
                    yield f"event: live.event\ndata: {event_data}\n\n"

            except asyncio.CancelledError:
                pass
            finally:
                # Send end event
                end_data = json.dumps(
                    {
                        "town_id": town_id,
                        "total_ticks": tick,
                        "status": "completed",
                    }
                )
                yield f"event: live.end\ndata: {end_data}\n\n"

                event_bus.close()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/{town_id}/scatter")
    async def get_scatter(
        town_id: str,
        projection: str = "PAIR_WT",
        format: str = "json",
    ) -> Any:
        """
        Get eigenvector scatter plot data.

        Args:
            town_id: Town ID
            projection: Projection method (PAIR_WT, PAIR_CC, PAIR_PR, PAIR_RA, PCA, TSNE)
            format: Output format (json, ascii)

        Returns:
            Scatter plot data in requested format
        """
        from agents.town.environment import get_evolving_citizens
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
        )

        town = _get_town(town_id)
        env = town["env"]
        cm = town["coalition_manager"]

        # Get evolving citizens
        evolving_ids = {c.id for c in get_evolving_citizens(env)}

        # Create widget and load data
        widget = EigenvectorScatterWidgetImpl()

        # Parse projection method
        try:
            proj_method = ProjectionMethod[projection.upper()]
        except KeyError:
            proj_method = ProjectionMethod.PAIR_WT

        widget.set_projection(proj_method)
        widget.load_from_citizens(
            env.citizens,
            coalitions=cm.coalitions,
            evolving_ids=evolving_ids,
        )

        # Return in requested format
        if format.lower() == "ascii":
            from agents.i.reactive.widget import RenderTarget

            return {"scatter": widget.project(RenderTarget.CLI)}
        else:
            from agents.i.reactive.widget import RenderTarget

            return widget.project(RenderTarget.JSON)

    # =========================================================================
    # INHABIT API (Phase 8)
    # =========================================================================

    # In-memory session storage (production would use Redis/DB)
    _inhabit_sessions: dict[str, dict[str, Any]] = {}

    @router.post("/{town_id}/inhabit/{citizen_name}/start")
    async def inhabit_start(
        town_id: str,
        citizen_name: str,
        force_enabled: bool = False,
        user_id: str = "anonymous",
        tier: str = "resident",
    ) -> dict[str, Any]:
        """
        Start an INHABIT session with a citizen.

        Args:
            town_id: Town ID
            citizen_name: Name of citizen to inhabit
            force_enabled: Whether to enable force mechanic (Advanced INHABIT)
            user_id: User ID for session tracking
            tier: User subscription tier (tourist, resident, citizen, founder)

        Returns:
            Session status including consent state, time limits, and force limits
        """
        from agents.town.inhabit_session import InhabitSession, SubscriptionTier

        town = _get_town(town_id)
        env = town["env"]

        # Find citizen
        citizen = env.get_citizen_by_name(citizen_name)
        if not citizen:
            raise HTTPException(404, f"Citizen {citizen_name} not found")

        # Map tier string to enum
        tier_map = {
            "tourist": SubscriptionTier.TOURIST,
            "resident": SubscriptionTier.RESIDENT,
            "citizen": SubscriptionTier.CITIZEN,
            "founder": SubscriptionTier.FOUNDER,
        }
        user_tier = tier_map.get(tier.lower(), SubscriptionTier.RESIDENT)

        # Check if tourist (not allowed to INHABIT)
        if user_tier == SubscriptionTier.TOURIST:
            raise HTTPException(403, "INHABIT requires RESIDENT tier or higher")

        # Create session
        session = InhabitSession(
            citizen=citizen,
            user_tier=user_tier,
            force_enabled=force_enabled,
        )

        # Store session
        session_key = f"{town_id}:{citizen_name}:{user_id}"
        _inhabit_sessions[session_key] = {
            "session": session,
            "town_id": town_id,
            "user_id": user_id,
        }

        status: dict[str, Any] = session.get_status()
        return status

    @router.get("/{town_id}/inhabit/{citizen_name}/status")
    async def inhabit_status(
        town_id: str,
        citizen_name: str,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """Get current INHABIT session status."""
        session_key = f"{town_id}:{citizen_name}:{user_id}"

        if session_key not in _inhabit_sessions:
            raise HTTPException(404, "No active INHABIT session")

        session_data = _inhabit_sessions[session_key]
        session: Any = session_data["session"]
        session.update()  # Update timing/decay

        status: dict[str, Any] = session.get_status()
        return status

    @router.post("/{town_id}/inhabit/{citizen_name}/action")
    async def inhabit_action(
        town_id: str,
        citizen_name: str,
        action: str,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """
        Suggest an action to the inhabited citizen.

        The citizen will evaluate alignment with their personality
        and either enact, resist, or negotiate.
        """
        session_key = f"{town_id}:{citizen_name}:{user_id}"

        if session_key not in _inhabit_sessions:
            raise HTTPException(404, "No active INHABIT session")

        session_data = _inhabit_sessions[session_key]
        session: Any = session_data["session"]

        # Check if expired
        if session.is_expired():
            del _inhabit_sessions[session_key]
            raise HTTPException(410, "Session expired")

        # Try to get LLM client, fallback to sync method if not available
        try:
            from agents.k.llm import create_llm_client

            llm_client = create_llm_client()
            response = await session.process_input_async(action, llm_client)
            return {
                "type": response.type,
                "message": response.message,
                "inner_voice": response.inner_voice,
                "cost": response.cost,
                "alignment_score": response.alignment.score
                if response.alignment
                else None,
                "suggested_rephrase": response.alignment.suggested_rephrase
                if response.alignment
                else None,
                "status": session.get_status(),
            }
        except Exception:
            # Fallback to sync suggest_action
            result = session.suggest_action(action)
            return {
                **result,
                "inner_voice": f"*{session.citizen.name} considers your suggestion*",
                "status": session.get_status(),
            }

    @router.post("/{town_id}/inhabit/{citizen_name}/force")
    async def inhabit_force(
        town_id: str,
        citizen_name: str,
        action: str,
        severity: float = 0.2,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """
        Force the citizen to perform an action.

        This is expensive, increases consent debt, and is limited per session.
        Requires force_enabled to be true when starting the session.
        """
        session_key = f"{town_id}:{citizen_name}:{user_id}"

        if session_key not in _inhabit_sessions:
            raise HTTPException(404, "No active INHABIT session")

        session_data = _inhabit_sessions[session_key]
        session: Any = session_data["session"]

        if not session.can_force():
            raise HTTPException(
                403, "Force not allowed (check session status for reason)"
            )

        try:
            from agents.k.llm import create_llm_client

            llm_client = create_llm_client()
            response = await session.force_action_async(action, llm_client, severity)
            return {
                "type": response.type,
                "message": response.message,
                "inner_voice": response.inner_voice,
                "cost": response.cost,
                "status": session.get_status(),
            }
        except Exception:
            # Fallback to sync force_action
            result = session.force_action(action, severity)
            return {
                **result,
                "inner_voice": f"*{session.citizen.name} reluctantly complies*",
                "status": session.get_status(),
            }

    @router.post("/{town_id}/inhabit/{citizen_name}/apologize")
    async def inhabit_apologize(
        town_id: str,
        citizen_name: str,
        sincerity: float = 0.3,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """
        Apologize to the citizen, reducing consent debt.

        Use this to repair the relationship after forced actions.
        """
        session_key = f"{town_id}:{citizen_name}:{user_id}"

        if session_key not in _inhabit_sessions:
            raise HTTPException(404, "No active INHABIT session")

        session_data = _inhabit_sessions[session_key]
        session: Any = session_data["session"]

        result = session.apologize(sincerity)
        return {
            **result,
            "status": session.get_status(),
        }

    @router.delete("/{town_id}/inhabit/{citizen_name}")
    async def inhabit_end(
        town_id: str,
        citizen_name: str,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """End the INHABIT session."""
        session_key = f"{town_id}:{citizen_name}:{user_id}"

        if session_key not in _inhabit_sessions:
            raise HTTPException(404, "No active INHABIT session")

        session_data = _inhabit_sessions[session_key]
        session: Any = session_data["session"]

        # Get final status
        final_status = session.to_dict()

        # Remove session
        del _inhabit_sessions[session_key]

        return {
            "status": "ended",
            "summary": final_status,
        }

    return router


# --- Exports ---


__all__ = [
    "create_town_router",
    "CreateTownRequest",
    "TownResponse",
    "CitizenSummary",
    "CitizensResponse",
    "CitizenDetailResponse",
    "CoalitionSummary",
    "CoalitionsResponse",
    "StepRequest",
    "StepResponse",
]
