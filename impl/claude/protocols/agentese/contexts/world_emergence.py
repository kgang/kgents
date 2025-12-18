"""
AGENTESE Emergence Context: Cymatics Design Sampler.

The world.emergence context provides access to the Cymatics Design Sampler:
- world.emergence.manifest - View available pattern families
- world.emergence.pattern.manifest - View pattern family variations
- world.emergence.preset.manifest - Browse curated presets
- world.emergence.configure - Configure custom patterns

This module defines EmergenceNode which handles emergence/cymatics operations.

AGENTESE: world.emergence.*

Principle Alignment:
- Joy-Inducing: Visual exploration of pattern families
- Generative: "Don't tune blindly. Show everything. Let the eye choose."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# Emergence affordances available at world.emergence.*
EMERGENCE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "pattern",
    "preset",
    "configure",
)

# Pattern families from CymaticsSampler
PATTERN_FAMILIES: dict[str, dict[str, Any]] = {
    "chladni": {
        "name": "Chladni Plates",
        "description": "Classic standing wave patterns from vibrating plates",
        "param1": "N Mode (2-10)",
        "param2": "M Mode (2-10)",
    },
    "interference": {
        "name": "Wave Interference",
        "description": "Circular waves from multiple point sources",
        "param1": "Sources (2-8)",
        "param2": "Wavelength (0.15-0.6)",
    },
    "mandala": {
        "name": "Mandala",
        "description": "Radial symmetry with angular harmonics",
        "param1": "Symmetry (3-12)",
        "param2": "Complexity (2-8)",
    },
    "flow": {
        "name": "Organic Flow",
        "description": "Noise-driven fluid patterns",
        "param1": "Scale (1-6)",
        "param2": "Turbulence (0.3-0.8)",
    },
    "reaction": {
        "name": "Reaction-Diffusion",
        "description": "Turing-like patterns (spots and stripes)",
        "param1": "Feature Size (3-8)",
        "param2": "Spot/Stripe Mix (0-1)",
    },
    "spiral": {
        "name": "Spiral",
        "description": "Logarithmic spiral patterns",
        "param1": "Arms (2-8)",
        "param2": "Tightness (1-5)",
    },
    "voronoi": {
        "name": "Voronoi Cells",
        "description": "Cellular patterns with organic edges",
        "param1": "Cell Count (3-12)",
        "param2": "Edge Sharpness (0.2-1.0)",
    },
    "moire": {
        "name": "Moire",
        "description": "Overlapping line gratings",
        "param1": "Line Density (10-30)",
        "param2": "Rotation (0.05-0.3)",
    },
    "fractal": {
        "name": "Fractal (Julia)",
        "description": "Self-similar mathematical patterns",
        "param1": "Zoom (1-3)",
        "param2": "Iteration Depth (0.3-1)",
    },
}


# =============================================================================
# EmergenceNode
# =============================================================================


@node(
    "world.emergence",
    description="Cymatics Design Sampler - visual pattern exploration",
)
@dataclass
class EmergenceNode(BaseLogosNode):
    """
    world.emergence - Cymatics Design Sampler interface.

    The Emergence node provides:
    - Pattern family exploration (9 families)
    - Curated presets
    - Custom configuration
    - Visual exploration philosophy: "Show everything. Let the eye choose."
    """

    _handle: str = "world.emergence"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Emergence affordances - available to all archetypes."""
        return EMERGENCE_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View Cymatics Design Sampler - pattern families overview",
        examples=["kg emergence", "world.emergence.manifest"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show emergence/cymatics overview."""
        lines = [
            "Cymatics Design Sampler",
            "=" * 50,
            "",
            '"Don\'t tune blindly. Show everything. Let the eye choose."',
            "",
            f"Pattern Families: {len(PATTERN_FAMILIES)}",
            "",
        ]

        for family_id, family in PATTERN_FAMILIES.items():
            lines.append(f"  [{family_id}] {family['name']}")
            lines.append(f"    {family['description']}")

        lines.append("")
        lines.append("Visit /emergence for visual exploration")
        lines.append("=" * 50)

        return BasicRendering(
            summary="Cymatics Design Sampler",
            content="\n".join(lines),
            metadata={
                "status": "available",
                "family_count": len(PATTERN_FAMILIES),
                "families": list(PATTERN_FAMILIES.keys()),
                "route": "/emergence",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View pattern family variations",
        examples=["world.emergence.pattern.manifest --family chladni"],
    )
    async def pattern(
        self,
        observer: "Umwelt[Any, Any]",
        family: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Show pattern family details."""
        if family is None:
            # List all families
            return await self.manifest(observer)

        family_info = PATTERN_FAMILIES.get(family)
        if family_info is None:
            return BasicRendering(
                summary=f"Unknown Pattern Family: {family}",
                content=f"Available families: {', '.join(PATTERN_FAMILIES.keys())}",
                metadata={"error": "unknown_family"},
            )

        lines = [
            f"Pattern Family: {family_info['name']}",
            "=" * 50,
            "",
            family_info["description"],
            "",
            "Parameters:",
            f"  Param 1: {family_info['param1']}",
            f"  Param 2: {family_info['param2']}",
            "",
            f"Visit /emergence and select '{family}' to explore variations",
            "=" * 50,
        ]

        return BasicRendering(
            summary=f"Pattern: {family_info['name']}",
            content="\n".join(lines),
            metadata={
                "family": family,
                "info": family_info,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Browse curated pattern presets",
        examples=["world.emergence.preset.manifest"],
    )
    async def preset(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show curated presets."""
        # Preset keys from CymaticsSampler
        curated_presets = [
            "chladni-4-5",
            "interference-4-0.3",
            "mandala-6-4",
            "flow-3-0.5",
            "reaction-5-0.5",
            "spiral-4-2.5",
            "voronoi-8-0.6",
            "moire-20-0.15",
            "fractal-2-0.7",
        ]

        lines = [
            "Curated Pattern Presets",
            "=" * 50,
            "",
            f"Total: {len(curated_presets)} presets",
            "",
        ]

        for preset_key in curated_presets:
            family = preset_key.split("-")[0]
            family_info = PATTERN_FAMILIES.get(family, {})
            name = family_info.get("name", family)
            lines.append(f"  {preset_key}: {name}")

        lines.append("")
        lines.append("Visit /emergence to explore these presets visually")
        lines.append("=" * 50)

        return BasicRendering(
            summary="Curated Presets",
            content="\n".join(lines),
            metadata={
                "preset_count": len(curated_presets),
                "presets": curated_presets,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle emergence-specific aspects."""
        match aspect:
            case "pattern":
                return await self.pattern(observer, **kwargs)
            case "preset":
                return await self.preset(observer, **kwargs)
            case "configure":
                # Configuration is done in the UI
                return BasicRendering(
                    summary="Configure Patterns",
                    content="Visit /emergence to configure pattern parameters interactively.",
                    metadata={"route": "/emergence"},
                )
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# =============================================================================
# Factory Functions
# =============================================================================

# Global singleton for EmergenceNode
_emergence_node: EmergenceNode | None = None


def get_emergence_node() -> EmergenceNode:
    """Get the global EmergenceNode singleton."""
    global _emergence_node
    if _emergence_node is None:
        _emergence_node = EmergenceNode()
    return _emergence_node


def set_emergence_node(node: EmergenceNode) -> None:
    """Set the global EmergenceNode singleton (for testing)."""
    global _emergence_node
    _emergence_node = node


def create_emergence_node() -> EmergenceNode:
    """Create an EmergenceNode."""
    return EmergenceNode()


__all__ = [
    # Constants
    "EMERGENCE_AFFORDANCES",
    "PATTERN_FAMILIES",
    # Node
    "EmergenceNode",
    # Factory
    "get_emergence_node",
    "set_emergence_node",
    "create_emergence_node",
]
