"""
Garden REST API: Frontend endpoints for WitnessGarden operations.

Provides:
- GET /api/garden/state - Garden state with lifecycle counts and attention items
- GET /api/garden/items - List items with optional stage filter
- POST /api/garden/items/{path}/tend - Mark item as tended
- POST /api/garden/items/{path}/compost - Mark item for composting

The Core Insight:
    "The garden shows what *could* be witnessed, not just what *has* been."

See: spec/protocols/witness-assurance-surface.md
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Literal

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)


# =============================================================================
# Stage Mapping: Backend enum → Frontend stage
# =============================================================================

# Map backend SpecStatus enum to frontend-friendly stages
STATUS_TO_STAGE: dict[str, str] = {
    "unwitnessed": "seed",
    "in_progress": "sprout",
    "witnessed": "bloom",
    "contested": "wither",
    "superseded": "compost",
}

# Valid frontend stages
VALID_STAGES = Literal["seed", "sprout", "bloom", "wither", "compost"]


# =============================================================================
# Pydantic Models
# =============================================================================


class GardenItemResponse(BaseModel):
    """Single garden item (spec plant) response."""

    path: str = Field(..., description="Spec file path")
    title: str = Field(..., description="Human-friendly name")
    stage: VALID_STAGES = Field(..., description="Lifecycle stage")
    health: float = Field(..., ge=0.0, le=1.0, description="Health score 0-1")
    days_since_activity: int = Field(..., description="Days since last evidence")
    dependents: int = Field(default=0, description="Number of dependent specs")
    evidence_count: int = Field(default=0, description="Total evidence count")
    last_tended: str | None = Field(None, description="ISO timestamp of last tending")


class GardenStateResponse(BaseModel):
    """Garden state with lifecycle counts and attention items."""

    seeds: int = Field(default=0, description="Count of unwitnessed specs")
    sprouts: int = Field(default=0, description="Count of in-progress specs")
    blooms: int = Field(default=0, description="Count of witnessed specs")
    withering: int = Field(default=0, description="Count of contested specs")
    composted_today: int = Field(default=0, description="Count of composted today")
    health: float = Field(..., ge=0.0, le=1.0, description="Overall garden health")
    attention: list[GardenItemResponse] = Field(
        default_factory=list,
        description="Items needing attention (wilting, inactive)",
    )


class TendRequest(BaseModel):
    """Request body for tending an item."""

    note: str | None = Field(None, description="Optional tending note")


class CompostRequest(BaseModel):
    """Request body for composting an item."""

    reason: str = Field(..., description="Reason for composting")


# =============================================================================
# Router Factory
# =============================================================================


def create_garden_router() -> "APIRouter | None":
    """Create the garden API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/garden", tags=["garden"])

    @router.get("/state", response_model=GardenStateResponse)
    async def get_garden_state() -> GardenStateResponse:
        """
        Get current garden state.

        Returns lifecycle counts and items needing attention.
        Attention items are specs that are wilting or haven't been
        tended recently.
        """
        try:
            from services.witness.garden import SpecStatus
            from services.witness.garden_service import get_garden_service

            service = get_garden_service()
            scene = await service.build_garden_scene()

            # Count by stage
            stage_counts: dict[str, int] = {
                "seed": 0,
                "sprout": 0,
                "bloom": 0,
                "wither": 0,
                "compost": 0,
            }

            attention_items: list[GardenItemResponse] = []
            now = datetime.now()

            for plant in scene.specs:
                # Map status to stage
                stage = STATUS_TO_STAGE.get(plant.status.value, "seed")
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

                # Calculate days since activity
                days_since = 0
                last_tended: str | None = None
                if plant.last_evidence_at:
                    delta = now - plant.last_evidence_at
                    days_since = delta.days
                    last_tended = plant.last_evidence_at.isoformat()

                # Build item response
                item = GardenItemResponse(
                    path=str(plant.path),
                    title=plant.name,
                    stage=stage,  # type: ignore[arg-type]
                    health=plant.confidence,
                    days_since_activity=days_since,
                    dependents=0,  # TODO: compute from graph
                    evidence_count=plant.evidence_levels.total_evidence,
                    last_tended=last_tended,
                )

                # Add to attention if wilting or inactive
                if stage == "wither" or days_since > 7:
                    attention_items.append(item)

            # Sort attention items by health (lowest first)
            attention_items.sort(key=lambda x: x.health)

            return GardenStateResponse(
                seeds=stage_counts["seed"],
                sprouts=stage_counts["sprout"],
                blooms=stage_counts["bloom"],
                withering=stage_counts["wither"],
                composted_today=stage_counts["compost"],
                health=scene.overall_health,
                attention=attention_items[:10],  # Top 10 needing attention
            )

        except Exception as e:
            logger.exception("Error getting garden state")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/items", response_model=list[GardenItemResponse])
    async def list_garden_items(
        stage: str | None = Query(default=None, description="Filter by stage"),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> list[GardenItemResponse]:
        """
        List garden items with optional stage filter.

        Args:
            stage: Filter by stage (seed, sprout, bloom, wither, compost)
            limit: Maximum number of items to return
        """
        try:
            from services.witness.garden_service import get_garden_service

            service = get_garden_service()
            scene = await service.build_garden_scene()

            items: list[GardenItemResponse] = []
            now = datetime.now()

            for plant in scene.specs:
                # Map status to stage
                plant_stage = STATUS_TO_STAGE.get(plant.status.value, "seed")

                # Filter by stage if specified
                if stage and plant_stage != stage:
                    continue

                # Calculate days since activity
                days_since = 0
                last_tended: str | None = None
                if plant.last_evidence_at:
                    delta = now - plant.last_evidence_at
                    days_since = delta.days
                    last_tended = plant.last_evidence_at.isoformat()

                items.append(
                    GardenItemResponse(
                        path=str(plant.path),
                        title=plant.name,
                        stage=plant_stage,  # type: ignore[arg-type]
                        health=plant.confidence,
                        days_since_activity=days_since,
                        dependents=0,
                        evidence_count=plant.evidence_levels.total_evidence,
                        last_tended=last_tended,
                    )
                )

                if len(items) >= limit:
                    break

            # Sort by health (lowest first for attention)
            items.sort(key=lambda x: x.health)

            return items

        except Exception as e:
            logger.exception("Error listing garden items")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/items/{path:path}/tend")
    async def tend_item(
        path: str,
        request: TendRequest | None = None,
    ) -> dict[str, Any]:
        """
        Mark a garden item as tended.

        Creates a witness mark indicating the spec has been reviewed/updated.

        Args:
            path: Path to the spec file
            request: Optional tending note
        """
        try:
            from services.providers import get_witness_persistence

            persistence = await get_witness_persistence()

            # Create a witness mark for tending
            note = request.note if request else None
            action = f"Tended spec: {path}"
            if note:
                action = f"{action} - {note}"

            result = await persistence.save_mark(
                action=action,
                reasoning="Garden tending - manual review/update",
                principles=["composable"],
                author="kent",
            )

            return {
                "success": True,
                "path": path,
                "mark_id": result.mark_id,
                "tended_at": result.timestamp.isoformat(),
            }

        except Exception as e:
            logger.exception(f"Error tending item: {path}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/items/{path:path}/compost")
    async def compost_item(
        path: str,
        request: CompostRequest,
    ) -> dict[str, Any]:
        """
        Mark a garden item for composting.

        Creates a witness mark indicating the spec is superseded.

        Args:
            path: Path to the spec file
            request: Reason for composting
        """
        try:
            from services.providers import get_witness_persistence

            persistence = await get_witness_persistence()

            # Create a witness mark for composting
            result = await persistence.save_mark(
                action=f"Composted spec: {path}",
                reasoning=f"Marked for composting: {request.reason}",
                principles=["composable"],
                author="kent",
            )

            return {
                "success": True,
                "path": path,
                "mark_id": result.mark_id,
                "composted_at": result.timestamp.isoformat(),
                "reason": request.reason,
            }

        except Exception as e:
            logger.exception(f"Error composting item: {path}")
            raise HTTPException(status_code=500, detail=str(e))

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ["create_garden_router"]
