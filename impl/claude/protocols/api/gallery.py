"""
FastAPI Gallery Endpoints: REST API for Projection Component Gallery.

Provides endpoints to:
- List all pilots with their projections
- Render individual pilots with overrides
- Get category metadata

Usage:
    GET /api/gallery           - All pilots rendered to JSON + HTML
    GET /api/gallery/{name}    - Single pilot with override support
    GET /api/gallery/categories - List categories
"""

from __future__ import annotations

from typing import Any

# Graceful FastAPI import
try:
    from fastapi import APIRouter, HTTPException, Query

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    HTTPException = None  # type: ignore[misc, assignment]
    Query = None  # type: ignore[misc, assignment]

from pydantic import BaseModel, Field

# =============================================================================
# Models
# =============================================================================


class PilotProjections(BaseModel):
    """Projections of a pilot across targets."""

    model_config = {"populate_by_name": True}

    cli: str = Field(description="CLI rendering (plain text)")
    html: str = Field(description="HTML rendering (marimo projection)")
    json_data: dict[str, Any] = Field(
        description="JSON representation", serialization_alias="json"
    )


class PilotResponse(BaseModel):
    """Single pilot response."""

    name: str = Field(description="Unique pilot identifier")
    category: str = Field(description="Category name (PRIMITIVES, CARDS, etc.)")
    description: str = Field(description="One-line description")
    tags: list[str] = Field(description="Searchable tags")
    projections: PilotProjections = Field(description="Rendered projections")


class GalleryResponse(BaseModel):
    """Full gallery response with all pilots."""

    pilots: list[PilotResponse] = Field(description="All rendered pilots")
    categories: list[str] = Field(description="Available categories")
    total: int = Field(description="Total number of pilots")


class CategoryInfo(BaseModel):
    """Category metadata."""

    name: str
    pilot_count: int
    pilots: list[str]


class CategoriesResponse(BaseModel):
    """All categories response."""

    categories: list[CategoryInfo]


# =============================================================================
# Helper Functions
# =============================================================================


def _render_pilot_to_projections(
    pilot_name: str,
    entropy: float | None = None,
    seed: int | None = None,
    phase: str | None = None,
    time_ms: float | None = None,
) -> PilotProjections:
    """Render a pilot to all projection targets."""
    from agents.i.reactive.widget import RenderTarget
    from protocols.projection.gallery import PILOT_REGISTRY, Gallery, GalleryOverrides

    if pilot_name not in PILOT_REGISTRY:
        raise ValueError(f"Unknown pilot: {pilot_name}")

    # Build overrides
    overrides = GalleryOverrides(
        entropy=entropy,
        seed=seed,
        phase=phase,
        time_ms=time_ms,
    )
    gallery = Gallery(overrides)

    # Render to each target
    cli_result = gallery.render(pilot_name, RenderTarget.CLI)
    json_result = gallery.render(pilot_name, RenderTarget.JSON)
    marimo_result = gallery.render(pilot_name, RenderTarget.MARIMO)

    # Format outputs
    cli_output = (
        str(cli_result.output) if cli_result.success else f"[ERROR] {cli_result.error}"
    )
    json_output = (
        json_result.output if json_result.success else {"error": json_result.error}
    )
    html_output = (
        str(marimo_result.output)
        if marimo_result.success
        else f'<span class="error">{marimo_result.error}</span>'
    )

    return PilotProjections(
        cli=cli_output,
        html=html_output,
        json_data=json_output
        if isinstance(json_output, dict)
        else {"value": json_output},
    )


def _get_pilot_response(
    pilot_name: str,
    entropy: float | None = None,
    seed: int | None = None,
    phase: str | None = None,
    time_ms: float | None = None,
) -> PilotResponse:
    """Build a complete pilot response."""
    from protocols.projection.gallery import PILOT_REGISTRY

    pilot = PILOT_REGISTRY[pilot_name]
    projections = _render_pilot_to_projections(
        pilot_name, entropy=entropy, seed=seed, phase=phase, time_ms=time_ms
    )

    return PilotResponse(
        name=pilot.name,
        category=pilot.category.name,
        description=pilot.description,
        tags=pilot.tags,
        projections=projections,
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_gallery_router() -> "APIRouter | None":
    """
    Create the gallery API router.

    Returns:
        APIRouter if FastAPI is available, None otherwise.
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/gallery", tags=["gallery"])

    @router.get("", response_model=GalleryResponse)
    async def get_gallery(
        entropy: float | None = Query(
            None, ge=0.0, le=1.0, description="Global entropy (0-1)"
        ),
        seed: int | None = Query(None, description="Deterministic seed"),
        phase: str | None = Query(None, description="Override phase"),
        time_ms: float | None = Query(None, description="Fixed time in ms"),
        category: str | None = Query(None, description="Filter by category"),
    ) -> GalleryResponse:
        """
        Get all pilots rendered to JSON and HTML.

        Returns all 25 pilots with their projections across all targets.
        Use query parameters for global overrides.
        """
        from protocols.projection.gallery import PILOT_REGISTRY, PilotCategory

        # Get all categories
        categories = [cat.name for cat in PilotCategory]

        # Filter pilots by category if specified
        pilot_names = list(PILOT_REGISTRY.keys())
        if category:
            category_upper = category.upper()
            pilot_names = [
                name
                for name, pilot in PILOT_REGISTRY.items()
                if pilot.category.name == category_upper
            ]

        # Render all pilots
        pilots = []
        for name in pilot_names:
            try:
                pilot_response = _get_pilot_response(
                    name, entropy=entropy, seed=seed, phase=phase, time_ms=time_ms
                )
                pilots.append(pilot_response)
            except Exception as e:
                # Include error pilots for visibility
                from protocols.projection.gallery import PILOT_REGISTRY

                pilot = PILOT_REGISTRY[name]
                pilots.append(
                    PilotResponse(
                        name=name,
                        category=pilot.category.name,
                        description=pilot.description,
                        tags=pilot.tags,
                        projections=PilotProjections(
                            cli=f"[ERROR] {e}",
                            html=f'<span class="error">{e}</span>',
                            json_data={"error": str(e)},
                        ),
                    )
                )

        return GalleryResponse(
            pilots=pilots,
            categories=categories,
            total=len(pilots),
        )

    @router.get("/categories", response_model=CategoriesResponse)
    async def get_categories() -> CategoriesResponse:
        """
        Get all gallery categories with pilot counts.
        """
        from protocols.projection.gallery import PILOT_REGISTRY, PilotCategory
        from protocols.projection.gallery.pilots import get_pilots_by_category

        categories = []
        for cat in PilotCategory:
            pilots = get_pilots_by_category(cat)
            categories.append(
                CategoryInfo(
                    name=cat.name,
                    pilot_count=len(pilots),
                    pilots=[p.name for p in pilots],
                )
            )

        return CategoriesResponse(categories=categories)

    @router.get("/{pilot_name}", response_model=PilotResponse)
    async def get_pilot(
        pilot_name: str,
        entropy: float | None = Query(
            None, ge=0.0, le=1.0, description="Entropy override (0-1)"
        ),
        seed: int | None = Query(None, description="Deterministic seed"),
        phase: str | None = Query(None, description="Phase override"),
        time_ms: float | None = Query(None, description="Fixed time in ms"),
        value: float | None = Query(
            None, ge=0.0, le=1.0, description="Value override (for bars/progress)"
        ),
    ) -> PilotResponse:
        """
        Get a single pilot with override support.

        Useful for focused iteration on specific widgets.
        """
        from protocols.projection.gallery import PILOT_REGISTRY

        if pilot_name not in PILOT_REGISTRY:
            raise HTTPException(
                status_code=404, detail=f"Pilot not found: {pilot_name}"
            )

        try:
            return _get_pilot_response(
                pilot_name, entropy=entropy, seed=seed, phase=phase, time_ms=time_ms
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
