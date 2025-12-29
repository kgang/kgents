"""
Pilot registry API.

Provides endpoints to list and query available pilots.
Each pilot is a separate webapp experience built on kgents primitives.
"""

from __future__ import annotations

import logging
from typing import Optional

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    BaseModel = object  # type: ignore

logger = logging.getLogger(__name__)


class PilotManifest(BaseModel):
    """Manifest for a pilot."""

    id: str
    name: str
    description: str
    status: str  # "active" | "coming_soon" | "experimental"
    route: str
    primitives: list[str]
    joy_dimension: str  # FLOW, WARMTH, SURPRISE


# Registry of available pilots
PILOTS: list[PilotManifest] = [
    PilotManifest(
        id="daily-lab",
        name="Trail to Crystal",
        description="Turn your day into proof of intention",
        status="active",
        route="/daily-lab",
        primitives=["mark", "trace", "crystal", "compass", "trail"],
        joy_dimension="FLOW",
    ),
    PilotManifest(
        id="zero-seed",
        name="Zero Seed Governance",
        description="Personal constitution from axioms",
        status="coming_soon",
        route="/zero-seed",
        primitives=["galois", "constitution", "amendment"],
        joy_dimension="SURPRISE",
    ),
    PilotManifest(
        id="wasm-survivors",
        name="WASM Survivors",
        description="Witnessed run through procedural challenges",
        status="coming_soon",
        route="/wasm-survivors",
        primitives=["witness", "procedural", "challenge"],
        joy_dimension="FLOW",
    ),
    PilotManifest(
        id="disney-portal",
        name="Disney Portal Planner",
        description="Plan magical days with warmth",
        status="coming_soon",
        route="/disney-portal",
        primitives=["planner", "portal", "warmth"],
        joy_dimension="WARMTH",
    ),
]


def create_pilots_router() -> Optional["APIRouter"]:
    """Create the pilots API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, pilots router disabled")
        return None

    router = APIRouter(prefix="/api/pilots", tags=["pilots"])

    @router.get("")
    async def list_pilots() -> list[PilotManifest]:
        """List all available pilots."""
        return PILOTS

    @router.get("/active")
    async def list_active_pilots() -> list[PilotManifest]:
        """List only active pilots."""
        return [p for p in PILOTS if p.status == "active"]

    @router.get("/{pilot_id}")
    async def get_pilot(pilot_id: str) -> PilotManifest:
        """Get a specific pilot by ID."""
        for pilot in PILOTS:
            if pilot.id == pilot_id:
                return pilot
        raise HTTPException(status_code=404, detail=f"Pilot not found: {pilot_id}")

    return router
