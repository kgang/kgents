"""
AGENTESE World Gallery API Context: Practical Projection Rendering API.

┌─────────────────────────────────────────────────────────────────────────────┐
│  DISTINCTION: world.gallery vs world.emergence.gallery                      │
│                                                                             │
│  world.gallery (THIS FILE):                                                 │
│    - Practical projection rendering API                                     │
│    - Multi-target output (CLI, HTML, JSON)                                  │
│    - Developer-focused: "Render this widget to different targets"          │
│                                                                             │
│  world.emergence.gallery (world_gallery.py):                                │
│    - Educational categorical showcase                                       │
│    - Demonstrates PolyAgent, Operad, Sheaf patterns                        │
│    - Interactive polynomial simulation and law verification                 │
│    - Learning-focused: "How do categorical primitives work?"               │
│                                                                             │
│  Both are valid; they serve different purposes.                             │
└─────────────────────────────────────────────────────────────────────────────┘

Migrated from protocols/api/gallery.py to @node pattern (AD-009 Phase 3).

Routes migrated:
- GET /api/gallery → world.gallery.manifest
- GET /api/gallery/categories → world.gallery.categories
- GET /api/gallery/{pilot_name} → world.gallery.pilot (with name kwarg)

AGENTESE: world.gallery.*

See: plans/agentese-router-consolidation.md (Phase 3.1)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# Gallery affordances
GALLERY_API_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "categories",
    "pilot",
)


def _render_pilot_to_projections(
    pilot_name: str,
    entropy: float | None = None,
    seed: int | None = None,
    phase: str | None = None,
    time_ms: float | None = None,
) -> dict[str, Any]:
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
    cli_output = str(cli_result.output) if cli_result.success else f"[ERROR] {cli_result.error}"
    json_output = json_result.output if json_result.success else {"error": json_result.error}
    html_output = (
        str(marimo_result.output)
        if marimo_result.success
        else f'<span class="error">{marimo_result.error}</span>'
    )

    return {
        "cli": cli_output,
        "html": html_output,
        "json": json_output if isinstance(json_output, dict) else {"value": json_output},
    }


def _get_pilot_response(
    pilot_name: str,
    entropy: float | None = None,
    seed: int | None = None,
    phase: str | None = None,
    time_ms: float | None = None,
) -> dict[str, Any]:
    """Build a complete pilot response."""
    from protocols.projection.gallery import PILOT_REGISTRY

    pilot = PILOT_REGISTRY[pilot_name]
    projections = _render_pilot_to_projections(
        pilot_name, entropy=entropy, seed=seed, phase=phase, time_ms=time_ms
    )

    return {
        "name": pilot.name,
        "category": pilot.category.name,
        "description": pilot.description,
        "tags": pilot.tags,
        "projections": projections,
    }


@node(
    "world.gallery",
    description="Projection Component Gallery - widget showcase with multi-target rendering",
)
@dataclass
class GalleryApiNode(BaseLogosNode):
    """
    world.gallery - REST API for Projection Component Gallery.

    Provides:
    - List all pilots with their projections
    - Render individual pilots with overrides
    - Get category metadata
    """

    _handle: str = "world.gallery"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Gallery affordances - available to all archetypes."""
        return GALLERY_API_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get all pilots rendered to JSON and HTML",
        examples=["world.gallery.manifest", "world.gallery.manifest[category='CARDS']"],
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get all pilots rendered to JSON and HTML.

        Args:
            entropy: Global entropy (0-1)
            seed: Deterministic seed
            phase: Override phase
            time_ms: Fixed time in ms
            category: Filter by category

        Returns:
            GalleryResponse with pilots, categories, total
        """
        entropy = kwargs.get("entropy")
        seed = kwargs.get("seed")
        phase = kwargs.get("phase")
        time_ms = kwargs.get("time_ms")
        category = kwargs.get("category")

        try:
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
                    pilot = PILOT_REGISTRY[name]
                    pilots.append(
                        {
                            "name": name,
                            "category": pilot.category.name,
                            "description": pilot.description,
                            "tags": pilot.tags,
                            "projections": {
                                "cli": f"[ERROR] {e}",
                                "html": f'<span class="error">{e}</span>',
                                "json": {"error": str(e)},
                            },
                        }
                    )

            return {
                "pilots": pilots,
                "categories": categories,
                "total": len(pilots),
            }
        except ImportError as e:
            logger.warning(f"Gallery not available: {e}")
            return {
                "pilots": [],
                "categories": [],
                "total": 0,
                "error": str(e),
            }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get all gallery categories with pilot counts",
        examples=["world.gallery.categories"],
    )
    async def categories(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get all gallery categories with pilot counts.

        Returns:
            CategoriesResponse with list of CategoryInfo
        """
        try:
            from protocols.projection.gallery import PILOT_REGISTRY, PilotCategory
            from protocols.projection.gallery.pilots import get_pilots_by_category

            categories = []
            for cat in PilotCategory:
                pilots = get_pilots_by_category(cat)
                categories.append(
                    {
                        "name": cat.name,
                        "pilot_count": len(pilots),
                        "pilots": [p.name for p in pilots],
                    }
                )

            return {"categories": categories}
        except ImportError as e:
            logger.warning(f"Gallery not available: {e}")
            return {"categories": [], "error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get a single pilot with override support",
        examples=["world.gallery.pilot[name='hello_world']"],
    )
    async def pilot(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get a single pilot with override support.

        Args:
            name: Pilot name (required)
            entropy: Entropy override (0-1)
            seed: Deterministic seed
            phase: Phase override
            time_ms: Fixed time in ms
            value: Value override (for bars/progress)

        Returns:
            PilotResponse with name, category, description, tags, projections
        """
        pilot_name = kwargs.get("name")
        if not pilot_name:
            return {"error": "name required"}

        entropy = kwargs.get("entropy")
        seed = kwargs.get("seed")
        phase = kwargs.get("phase")
        time_ms = kwargs.get("time_ms")

        try:
            from protocols.projection.gallery import PILOT_REGISTRY

            if pilot_name not in PILOT_REGISTRY:
                return {"error": f"Pilot not found: {pilot_name}"}

            return _get_pilot_response(
                pilot_name, entropy=entropy, seed=seed, phase=phase, time_ms=time_ms
            )
        except ImportError as e:
            logger.warning(f"Gallery not available: {e}")
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle gallery-specific aspects."""
        match aspect:
            case "categories":
                return await self.categories(observer, **kwargs)
            case "pilot":
                return await self.pilot(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# Factory functions
_gallery_api_node: GalleryApiNode | None = None


def get_gallery_api_node() -> GalleryApiNode:
    """Get the global GalleryApiNode singleton."""
    global _gallery_api_node
    if _gallery_api_node is None:
        _gallery_api_node = GalleryApiNode()
    return _gallery_api_node


def create_gallery_api_node() -> GalleryApiNode:
    """Create a GalleryApiNode."""
    return GalleryApiNode()


__all__ = [
    "GALLERY_API_AFFORDANCES",
    "GalleryApiNode",
    "get_gallery_api_node",
    "create_gallery_api_node",
]
