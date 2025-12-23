"""
AGENTESE Gallery Context: Educational Categorical Showcase.

┌─────────────────────────────────────────────────────────────────────────────┐
│  DISTINCTION: world.emergence.gallery vs world.gallery                      │
│                                                                             │
│  world.emergence.gallery (THIS FILE):                                       │
│    - Educational categorical showcase (AGENTESE path namespace)             │
│    - Demonstrates PolyAgent, Operad, Sheaf patterns                        │
│    - Interactive polynomial simulation and law verification                 │
│    - Learning-focused: "How do categorical primitives work?"               │
│    - NOTE: "emergence" here is lowercase and part of the AGENTESE path,    │
│      not related to the removed Emergence Crown Jewel                      │
│                                                                             │
│  world.gallery (world_gallery_api.py):                                      │
│    - Practical projection rendering API                                     │
│    - Multi-target output (CLI, HTML, JSON)                                  │
│    - Developer-focused: "Render this widget to different targets"          │
│                                                                             │
│  Both are valid; they serve different purposes.                             │
└─────────────────────────────────────────────────────────────────────────────┘

The world.emergence.gallery context provides access to the Gallery V2:
- world.emergence.gallery.manifest - Gallery overview with categories and counts
- world.emergence.gallery.pilots - List all pilots with projections
- world.emergence.gallery.pilot - Single pilot detail
- world.emergence.gallery.polynomial.manifest - View polynomial state machine
- world.emergence.gallery.polynomial.simulate - Step polynomial forward
- world.emergence.gallery.operad.manifest - View operad operations
- world.emergence.gallery.operad.verify - Verify operad laws

This module defines GalleryNode which handles gallery operations.

AGENTESE: world.emergence.gallery.*

Principle Alignment:
- Educational: Demonstrates categorical ground (PolyAgent, Operad, Sheaf)
- Joy-Inducing: Polynomial simulation and law verification are delightful
- Meta: Gallery IS a vertical slice demonstrating vertical slices

See: spec/gallery/gallery-v2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# Gallery affordances
GALLERY_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "pilots",
    "pilot",
    "polynomial",
    "operad",
)

# Categories for gallery pilots
GALLERY_CATEGORIES = [
    "PRIMITIVES",
    "CARDS",
    "CHROME",
    "STREAMING",
    "COMPOSITION",
    "ADAPTERS",
    "SPECIALIZED",
    "POLYNOMIAL",  # NEW: State machine visualizations
    "OPERAD",  # NEW: Composition grammar visualizations
    "CROWN_JEWELS",  # NEW: Full vertical slice mini-demos
    "LAYOUT",  # NEW: Design Language System
]


# =============================================================================
# GalleryNode
# =============================================================================


@node(
    "world.emergence.gallery",
    description="Living Autopoietic Showcase - widget gallery with categorical ground",
)
@dataclass
class GalleryNode(BaseLogosNode):
    """
    world.emergence.gallery - Gallery V2 interface.

    The Gallery node provides:
    - Pilot browsing and filtering
    - Projection comparison (CLI, HTML, JSON)
    - Polynomial state machine simulation
    - Operad law verification
    - Crown Jewel mini-demos

    The Gallery is itself a vertical slice, demonstrating the 7-layer
    autopoietic architecture (AD-009).
    """

    _handle: str = "world.emergence.gallery"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Gallery affordances - available to all archetypes."""
        return GALLERY_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View Gallery overview - categories, counts, and navigation",
        examples=["kg gallery", "world.emergence.gallery.manifest"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show gallery overview."""
        # Import pilot registry to get counts
        try:
            from protocols.projection.gallery.pilots import (
                PILOT_REGISTRY,
                PilotCategory,
            )

            pilot_count = len(PILOT_REGISTRY)
            category_counts = {}
            for pilot in PILOT_REGISTRY.values():
                cat_name = pilot.category.name
                category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        except ImportError:
            pilot_count = 0
            category_counts = {}

        lines = [
            "Gallery V2: Living Autopoietic Showcase",
            "=" * 50,
            "",
            '"The Gallery is not a catalogue—it is a living demonstration of the categorical ground."',
            "",
            f"Total Pilots: {pilot_count}",
            f"Categories: {len(GALLERY_CATEGORIES)}",
            "",
            "Categories:",
        ]

        for cat in GALLERY_CATEGORIES:
            count = category_counts.get(cat, 0)
            marker = "✓" if count > 0 else "○"
            lines.append(f"  {marker} {cat}: {count} pilots")

        lines.append("")
        lines.append("New in V2:")
        lines.append("  • POLYNOMIAL: State machine visualizations")
        lines.append("  • OPERAD: Composition grammar with law verification")
        lines.append("  • CROWN_JEWELS: Full vertical slice mini-demos")
        lines.append("  • LAYOUT: Design Language System components")
        lines.append("")
        lines.append("Visit /gallery for visual exploration")
        lines.append("=" * 50)

        return BasicRendering(
            summary="Gallery V2 Overview",
            content="\n".join(lines),
            metadata={
                "pilot_count": pilot_count,
                "category_count": len(GALLERY_CATEGORIES),
                "categories": GALLERY_CATEGORIES,
                "category_counts": category_counts,
                "route": "/gallery",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all pilots with optional category filter",
        examples=[
            "world.emergence.gallery.pilots.manifest",
            "world.emergence.gallery.pilots.manifest --category CARDS",
        ],
    )
    async def pilots(
        self,
        observer: "Umwelt[Any, Any]",
        category: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """List pilots with projections."""
        try:
            from protocols.projection.gallery.pilots import (
                PILOT_REGISTRY,
                PilotCategory,
                get_pilots_by_category,
            )

            if category:
                try:
                    cat_enum = PilotCategory[category.upper()]
                    pilots = get_pilots_by_category(cat_enum)
                except KeyError:
                    return BasicRendering(
                        summary=f"Unknown Category: {category}",
                        content=f"Available categories: {', '.join(GALLERY_CATEGORIES)}",
                        metadata={"error": "unknown_category"},
                    )
            else:
                pilots = list(PILOT_REGISTRY.values())

            lines = [
                f"Gallery Pilots ({len(pilots)})" + (f" - {category}" if category else ""),
                "=" * 50,
                "",
            ]

            for pilot in pilots:
                lines.append(f"  [{pilot.category.name}] {pilot.name}")
                lines.append(f"    {pilot.description}")
                if pilot.tags:
                    lines.append(f"    Tags: {', '.join(pilot.tags)}")
                lines.append("")

            return BasicRendering(
                summary=f"Gallery Pilots ({len(pilots)})",
                content="\n".join(lines),
                metadata={
                    "count": len(pilots),
                    "category": category,
                    "pilots": [{"name": p.name, "category": p.category.name} for p in pilots],
                },
            )

        except ImportError:
            return BasicRendering(
                summary="Pilots Unavailable",
                content="Pilot registry not available. Visit /gallery in browser.",
                metadata={"error": "import_error"},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View polynomial state machine visualization",
        examples=["world.emergence.gallery.polynomial.manifest"],
    )
    async def polynomial(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Show gallery polynomial visualization."""
        from agents.gallery import gallery_visualization

        viz = gallery_visualization()

        lines = [
            "GalleryPolynomial State Machine",
            "=" * 50,
            "",
            f"Positions: {len(viz['positions'])}",
            f"Edges: {len(viz['edges'])}",
            f"Current: {viz['current']}",
            "",
            "Positions:",
        ]

        for pos in viz["positions"]:
            marker = "▶" if pos["is_current"] else "○"
            lines.append(f"  {marker} {pos['id']}: {pos['description']}")

        lines.append("")
        lines.append("Transitions:")
        for edge in viz["edges"]:
            lines.append(f"  {edge['source']} --{edge['label']}--> {edge['target']}")

        lines.append("")
        lines.append("Valid inputs from current state:")
        for direction in viz["valid_directions"]:
            lines.append(f"  • {direction}")

        return BasicRendering(
            summary="GalleryPolynomial",
            content="\n".join(lines),
            metadata=viz,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View operad operations and laws",
        examples=["world.emergence.gallery.operad.manifest"],
    )
    async def operad(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Show gallery operad visualization."""
        from agents.gallery.operad import gallery_operad_visualization

        viz = gallery_operad_visualization()

        lines = [
            f"GALLERY_OPERAD: {viz['description']}",
            "=" * 50,
            "",
            f"Operations: {len(viz['operations'])}",
            f"Laws: {len(viz['laws'])}",
            "",
            "Operations:",
        ]

        for op in viz["operations"]:
            lines.append(f"  • {op['name']} (arity {op['arity']})")
            lines.append(f"    {op['signature']}")
            lines.append(f"    {op['description']}")
            lines.append("")

        lines.append("Laws:")
        for law in viz["laws"]:
            lines.append(f"  • {law['name']}: {law['equation']}")
            lines.append(f"    {law['description']}")

        return BasicRendering(
            summary="GALLERY_OPERAD",
            content="\n".join(lines),
            metadata=viz,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle gallery-specific aspects."""
        match aspect:
            case "pilots":
                return await self.pilots(observer, **kwargs)
            case "pilot":
                # Single pilot detail - would need pilot name in kwargs
                pilot_name = kwargs.get("name")
                if pilot_name:
                    return BasicRendering(
                        summary=f"Pilot: {pilot_name}",
                        content=f"Visit /gallery to see {pilot_name} projections.",
                        metadata={"route": f"/gallery?pilot={pilot_name}"},
                    )
                return await self.pilots(observer, **kwargs)
            case "polynomial":
                return await self.polynomial(observer, **kwargs)
            case "operad":
                return await self.operad(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# =============================================================================
# Factory Functions
# =============================================================================

_gallery_node: GalleryNode | None = None


def get_gallery_node() -> GalleryNode:
    """Get the global GalleryNode singleton."""
    global _gallery_node
    if _gallery_node is None:
        _gallery_node = GalleryNode()
    return _gallery_node


def set_gallery_node(node: GalleryNode) -> None:
    """Set the global GalleryNode singleton (for testing)."""
    global _gallery_node
    _gallery_node = node


def create_gallery_node() -> GalleryNode:
    """Create a GalleryNode."""
    return GalleryNode()


__all__ = [
    # Constants
    "GALLERY_AFFORDANCES",
    "GALLERY_CATEGORIES",
    # Node
    "GalleryNode",
    # Factory
    "get_gallery_node",
    "set_gallery_node",
    "create_gallery_node",
]
