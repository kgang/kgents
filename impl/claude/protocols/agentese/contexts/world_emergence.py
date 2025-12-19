"""
AGENTESE Emergence Context: Cymatics Design Experience Crown Jewel.

The world.emergence context provides access to the Cymatics Design Experience:
- world.emergence.manifest - View available pattern families
- world.emergence.pattern.manifest - View pattern family variations
- world.emergence.pattern.tune - Adjust pattern parameters
- world.emergence.preset.manifest - Browse curated presets
- world.emergence.qualia.manifest - Current qualia coordinates
- world.emergence.qualia.modulate - Apply qualia adjustment
- world.emergence.circadian.phase - Current circadian phase
- world.emergence.circadian.modulate - Apply circadian modifier

This module defines EmergenceNode which handles emergence/cymatics operations.
It integrates with EMERGENCE_POLYNOMIAL, EMERGENCE_OPERAD, and EmergenceSheaf.

AGENTESE: world.emergence.*

Principle Alignment:
- Joy-Inducing: Visual exploration of pattern families
- Generative: "Don't tune blindly. Show everything. Let the eye choose."
- Composable: Full 8/8 vertical slice compliance

See: plans/structured-greeting-boot.md for enhancement plan
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# Import emergence types
from agents.emergence import (
    CIRCADIAN_MODIFIERS,
    EMERGENCE_POLYNOMIAL,
    FAMILY_QUALIA,
    CircadianPhase,
    EmergencePhase,
    EmergenceState,
    PatternConfig,
    PatternFamily,
    QualiaCoords,
)

# Emergence affordances available at world.emergence.*
EMERGENCE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "pattern",
    "preset",
    "qualia",
    "circadian",
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
    description="Cymatics Design Experience - full Crown Jewel with qualia/circadian",
)
@dataclass
class EmergenceNode(BaseLogosNode):
    """
    world.emergence - Cymatics Design Experience Crown Jewel.

    The Emergence node provides:
    - Pattern family exploration (9 families)
    - Curated presets
    - Qualia space integration (cross-modal aesthetic coordinates)
    - Circadian modulation (dawn/noon/dusk/midnight)
    - Visual exploration philosophy: "Show everything. Let the eye choose."

    Crown Jewel Stack:
    - Layer 1: EmergenceSheaf (tile coherence)
    - Layer 2: EMERGENCE_POLYNOMIAL (phase state machine)
    - Layer 3: EMERGENCE_OPERAD (composition grammar)
    - Layer 4: agents/emergence/ (service module)
    - Layer 5: @node decorator (this module)
    - Layer 6: Gateway discovery
    - Layer 7: Web projection (EmergenceDemo.tsx)
    """

    _handle: str = "world.emergence"
    _state: EmergenceState | None = None

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def state(self) -> EmergenceState:
        """Get current emergence state, computing circadian from current hour."""
        if self._state is None:
            current_hour = datetime.now().hour
            self._state = EmergenceState(
                phase=EmergencePhase.IDLE,
                circadian=CircadianPhase.from_hour(current_hour),
            )
        return self._state

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

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current qualia coordinates",
        examples=["world.emergence.qualia.manifest"],
    )
    async def qualia(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Show current qualia coordinates."""
        state = self.state
        qualia = state.qualia

        lines = [
            "Qualia Space Coordinates",
            "=" * 50,
            "",
            f"Circadian Phase: {state.circadian.value}",
            f"Selected Family: {state.selected_family.value if state.selected_family else 'None'}",
            "",
            "Cross-Modal Aesthetic Coordinates:",
            f"  Warmth:     {qualia.warmth:+.2f}  (cyan ← → amber)",
            f"  Weight:     {qualia.weight:+.2f}  (light ← → heavy)",
            f"  Tempo:      {qualia.tempo:+.2f}  (slow ← → fast)",
            f"  Texture:    {qualia.texture:+.2f}  (smooth ← → rough)",
            f"  Brightness: {qualia.brightness:+.2f}  (dark ← → bright)",
            f"  Saturation: {qualia.saturation:+.2f}  (muted ← → vivid)",
            f"  Complexity: {qualia.complexity:+.2f}  (simple ← → complex)",
            "",
            "Family Base Qualia:",
        ]

        for family in PatternFamily:
            base = FAMILY_QUALIA[family]
            lines.append(f"  {family.value}: warmth={base.warmth:+.1f}, weight={base.weight:+.1f}")

        lines.append("=" * 50)

        return BasicRendering(
            summary="Qualia Coordinates",
            content="\n".join(lines),
            metadata={
                "circadian": state.circadian.value,
                "family": state.selected_family.value if state.selected_family else None,
                "qualia": {
                    "warmth": qualia.warmth,
                    "weight": qualia.weight,
                    "tempo": qualia.tempo,
                    "texture": qualia.texture,
                    "brightness": qualia.brightness,
                    "saturation": qualia.saturation,
                    "complexity": qualia.complexity,
                },
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current circadian phase and modifiers",
        examples=["world.emergence.circadian.phase"],
    )
    async def circadian(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Show circadian phase and modifiers."""
        current_hour = datetime.now().hour
        current_phase = CircadianPhase.from_hour(current_hour)
        modifier = CIRCADIAN_MODIFIERS[current_phase]

        lines = [
            "Circadian Phase",
            "=" * 50,
            "",
            f"Current Hour: {current_hour:02d}:00",
            f"Phase: {current_phase.value.upper()}",
            "",
            "Phase Modifiers Applied:",
            f"  Warmth:     {modifier.warmth:+.2f}",
            f"  Brightness: {modifier.brightness:.2f}x",
            f"  Tempo:      {modifier.tempo:+.2f}",
            f"  Texture:    {modifier.texture:+.2f}",
            "",
            "Phase Schedule:",
            "  DAWN     (6-10)   - Cool, brightening, active",
            "  NOON     (10-16)  - Neutral, full brightness",
            "  DUSK     (16-20)  - Warming, dimming, slowing",
            "  MIDNIGHT (20-6)   - Cool, dim, slow",
            "",
            "=" * 50,
        ]

        return BasicRendering(
            summary=f"Circadian: {current_phase.value}",
            content="\n".join(lines),
            metadata={
                "hour": current_hour,
                "phase": current_phase.value,
                "modifier": {
                    "warmth": modifier.warmth,
                    "brightness": modifier.brightness,
                    "tempo": modifier.tempo,
                    "texture": modifier.texture,
                },
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
            case "qualia":
                return await self.qualia(observer, **kwargs)
            case "circadian":
                return await self.circadian(observer, **kwargs)
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
