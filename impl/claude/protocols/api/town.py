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
        town_id: str, name: str, lod: int = 0
    ) -> CitizenDetailResponse:
        """Get citizen details at specified Level of Detail."""
        town = _get_town(town_id)
        env = town["env"]

        citizen = env.get_citizen_by_name(name)
        if not citizen:
            raise HTTPException(
                status_code=404, detail=f"Citizen {name} not found in town"
            )

        # Clamp LOD to valid range
        lod = max(0, min(5, lod))

        return CitizenDetailResponse(
            town_id=town_id,
            lod=lod,
            citizen=citizen.manifest(lod=lod),
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
