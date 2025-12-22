"""
AGENTESE 3D Projection Context Resolver

Three.js visualization integration with AGENTESE.

Provides 3D projection paths for the Projection Protocol:
- concept.projection.three.node.manifest — Current node state/config
- concept.projection.three.edge.manifest — Current edge state/config
- concept.projection.three.theme.list — Available themes
- concept.projection.three.quality.adapt — Adapt scene to quality level

The key insight: 3D projections follow P[3D] : State x Theme x Quality -> Scene

Phase 5 of 3D Projection Consolidation plan.
See: plans/3d-projection-consolidation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Quality Levels - Mirror of TypeScript QualityLevel in lighting.ts
# =============================================================================


class Quality(Enum):
    """
    Quality levels for 3D rendering.
    Higher quality = more effects, higher GPU usage.
    """

    MINIMAL = "minimal"  # No effects, basic lighting
    STANDARD = "standard"  # Some effects, good balance
    HIGH = "high"  # More effects, higher fidelity
    CINEMATIC = "cinematic"  # Full effects, VFX quality


class ThemeName(Enum):
    """Available 3D themes."""

    CRYSTAL = "crystal"  # Brain visualization (cyan/purple)
    FOREST = "forest"  # Gestalt visualization (green/amber)


# =============================================================================
# Theme Registry - Mirrors TypeScript themes in primitives/themes/
# =============================================================================

THEME_REGISTRY: dict[str, dict[str, Any]] = {
    "crystal": {
        "name": "crystal",
        "description": "Memories as gemstones, resolution as clarity",
        "domain": "brain",
        "nodeTiers": ["hot", "vivid", "recent", "familiar", "ghost", "dormant"],
        "palette": {
            "primary": "#00FFFF",  # Cyan
            "secondary": "#8B5CF6",  # Purple
            "accent": "#EC4899",  # Magenta
        },
    },
    "forest": {
        "name": "forest",
        "description": "Code as organisms, health as vitality",
        "domain": "gestalt",
        "nodeTiers": ["healthy", "stable", "warning", "critical", "disconnected"],
        "palette": {
            "primary": "#22C55E",  # Green
            "secondary": "#F59E0B",  # Amber
            "accent": "#EF4444",  # Red
        },
    },
}

# =============================================================================
# Quality Configurations - Mirrors TypeScript LIGHTING_QUALITY_TIERS
# =============================================================================

QUALITY_CONFIGS: dict[Quality, dict[str, Any]] = {
    Quality.MINIMAL: {
        "shadows": False,
        "ssao": False,
        "bloom": False,
        "particleCount": 0,
        "lodBias": 2,  # Lower LOD
        "description": "No effects, basic lighting. Best for low-end devices.",
    },
    Quality.STANDARD: {
        "shadows": True,
        "ssao": False,
        "bloom": True,
        "particleCount": 4,
        "lodBias": 1,
        "description": "Good balance of visuals and performance.",
    },
    Quality.HIGH: {
        "shadows": True,
        "ssao": True,
        "bloom": True,
        "particleCount": 6,
        "lodBias": 0,
        "description": "High fidelity visuals. Requires decent GPU.",
    },
    Quality.CINEMATIC: {
        "shadows": True,
        "ssao": True,
        "bloom": True,
        "particleCount": 8,
        "lodBias": -1,  # Higher LOD
        "antialiasing": "msaa",
        "description": "Maximum visual quality. For demos and screenshots.",
    },
}

# =============================================================================
# Node Primitive Configuration
# =============================================================================

NODE_DEFAULTS: dict[str, Any] = {
    "breathing": {
        "speed": 1.5,
        "amplitude": 0.03,
    },
    "selection": {
        "scaleMultiplier": 1.25,
        "ringOpacity": 0.7,
    },
    "hover": {
        "scaleMultiplier": 1.12,
        "lerpSpeed": 0.1,
    },
    "sizes": {
        "compact": {"base": 0.2, "hubMultiplier": 1.5},
        "comfortable": {"base": 0.3, "hubMultiplier": 1.4},
        "spacious": {"base": 0.4, "hubMultiplier": 1.3},
    },
}

# =============================================================================
# Edge Primitive Configuration
# =============================================================================

EDGE_DEFAULTS: dict[str, Any] = {
    "flowParticles": {
        "count": 4,
        "speed": 0.5,
        "size": 0.025,
    },
    "curve": {
        "defaultIntensity": 0.3,
        "segments": 32,
    },
    "opacity": {
        "base": 0.7,
        "dimmed": 0.2,
        "violation": 1.0,
    },
}

# =============================================================================
# Affordances
# =============================================================================

THREE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "node": ("manifest", "config", "animate"),
    "edge": ("manifest", "config", "animate"),
    "theme": ("list", "get", "palette"),
    "quality": ("adapt", "detect", "config"),
}


# =============================================================================
# ThreeNode - concept.projection.three.node.*
# =============================================================================


@dataclass
class ThreeNodeNode(BaseLogosNode):
    """
    concept.projection.three.node - 3D node primitive configuration.

    Provides access to TopologyNode3D defaults and configuration:
    - manifest: Current node primitive state
    - config: Animation and sizing defaults
    - animate: Animation preset information
    """

    _handle: str = "concept.projection.three.node"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return THREE_AFFORDANCES["node"]

    async def manifest(self, observer: Umwelt[Any, Any], **kwargs: Any) -> Renderable:
        """Manifest the 3D node primitive information."""
        return BasicRendering(
            summary="TopologyNode3D Configuration",
            content=(
                "3D node primitive for topology visualizations.\n\n"
                "Supported themes: crystal (Brain), forest (Gestalt)\n"
                "Density-aware sizing with breathing animation.\n"
                "Includes selection ring, hover ring, and growth rings."
            ),
            metadata={
                "component": "TopologyNode3D",
                "location": "components/three/primitives/TopologyNode3D.tsx",
                "defaults": NODE_DEFAULTS,
                "themes": list(THEME_REGISTRY.keys()),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle node aspect invocations."""
        match aspect:
            case "config":
                return NODE_DEFAULTS
            case "animate":
                return {
                    "breathing": NODE_DEFAULTS["breathing"],
                    "selection": NODE_DEFAULTS["selection"],
                    "hover": NODE_DEFAULTS["hover"],
                }
            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# ThreeEdge - concept.projection.three.edge.*
# =============================================================================


@dataclass
class ThreeEdgeNode(BaseLogosNode):
    """
    concept.projection.three.edge - 3D edge primitive configuration.

    Provides access to TopologyEdge3D defaults and configuration:
    - manifest: Current edge primitive state
    - config: Flow particles and curve defaults
    - animate: Animation preset information
    """

    _handle: str = "concept.projection.three.edge"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return THREE_AFFORDANCES["edge"]

    async def manifest(self, observer: Umwelt[Any, Any], **kwargs: Any) -> Renderable:
        """Manifest the 3D edge primitive information."""
        return BasicRendering(
            summary="TopologyEdge3D Configuration",
            content=(
                "3D edge primitive for topology visualizations.\n\n"
                "Supports curved and straight modes.\n"
                "Includes flow particles for active edges.\n"
                "SmartTopologyEdge3D variant auto-calculates positions."
            ),
            metadata={
                "component": "TopologyEdge3D",
                "location": "components/three/primitives/TopologyEdge3D.tsx",
                "defaults": EDGE_DEFAULTS,
                "variants": ["TopologyEdge3D", "SmartTopologyEdge3D"],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle edge aspect invocations."""
        match aspect:
            case "config":
                return EDGE_DEFAULTS
            case "animate":
                return {
                    "flowParticles": EDGE_DEFAULTS["flowParticles"],
                    "curve": EDGE_DEFAULTS["curve"],
                }
            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# ThreeTheme - concept.projection.three.theme.*
# =============================================================================


@dataclass
class ThreeThemeNode(BaseLogosNode):
    """
    concept.projection.three.theme - Available 3D themes.

    Provides access to theme registry:
    - list: All available themes
    - get: Specific theme by name
    - palette: Color palettes
    """

    _handle: str = "concept.projection.three.theme"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return THREE_AFFORDANCES["theme"]

    async def manifest(self, observer: Umwelt[Any, Any], **kwargs: Any) -> Renderable:
        """Manifest the available themes."""
        theme_lines = []
        for name, theme in THEME_REGISTRY.items():
            theme_lines.append(f"- {name}: {theme['description']}")

        return BasicRendering(
            summary=f"3D Themes ({len(THEME_REGISTRY)} available)",
            content=(
                "Available themes for 3D projections:\n\n"
                + "\n".join(theme_lines)
                + "\n\nThemes define visual identity for node tiers, edges, and particles."
            ),
            metadata={
                "themes": list(THEME_REGISTRY.keys()),
                "location": "components/three/primitives/themes/",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle theme aspect invocations."""
        match aspect:
            case "list":
                return list(THEME_REGISTRY.keys())

            case "get":
                theme_name = kwargs.get("name", "crystal")
                if theme_name in THEME_REGISTRY:
                    return THEME_REGISTRY[theme_name]
                return {"error": f"Unknown theme: {theme_name}"}

            case "palette":
                theme_name = kwargs.get("name", "crystal")
                if theme_name in THEME_REGISTRY:
                    return THEME_REGISTRY[theme_name].get("palette", {})
                return {"error": f"Unknown theme: {theme_name}"}

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# ThreeQuality - concept.projection.three.quality.*
# =============================================================================


@dataclass
class ThreeQualityNode(BaseLogosNode):
    """
    concept.projection.three.quality - Quality adaptation for 3D scenes.

    Provides quality-based scene configuration:
    - adapt: Get configuration for a quality level
    - detect: Auto-detect appropriate quality (stub)
    - config: All quality configurations
    """

    _handle: str = "concept.projection.three.quality"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return THREE_AFFORDANCES["quality"]

    async def manifest(self, observer: Umwelt[Any, Any], **kwargs: Any) -> Renderable:
        """Manifest quality adaptation information."""
        quality_lines = []
        for quality, config in QUALITY_CONFIGS.items():
            quality_lines.append(f"- {quality.value}: {config['description']}")

        return BasicRendering(
            summary=f"3D Quality Levels ({len(QUALITY_CONFIGS)} tiers)",
            content=(
                "Quality adaptation for 3D projections:\n\n"
                + "\n".join(quality_lines)
                + "\n\nHigher quality enables more effects but requires more GPU."
            ),
            metadata={
                "qualities": [q.value for q in Quality],
                "default": Quality.STANDARD.value,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle quality aspect invocations."""
        match aspect:
            case "adapt":
                level = kwargs.get("level", "standard")
                try:
                    quality = Quality(level)
                    return QUALITY_CONFIGS[quality]
                except ValueError:
                    return {"error": f"Unknown quality level: {level}"}

            case "detect":
                # Stub: would use WebGL capabilities detection
                return {
                    "detected": Quality.STANDARD.value,
                    "note": "Full detection requires browser WebGL context",
                }

            case "config":
                return {quality.value: config for quality, config in QUALITY_CONFIGS.items()}

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Three Context Resolver
# =============================================================================


@dataclass
class ThreeContextResolver:
    """
    Resolver for concept.projection.three.* context.

    Handles:
    - concept.projection.three.node.* (node primitive)
    - concept.projection.three.edge.* (edge primitive)
    - concept.projection.three.theme.* (themes)
    - concept.projection.three.quality.* (quality adaptation)
    """

    node_node: ThreeNodeNode = field(default_factory=ThreeNodeNode)
    edge_node: ThreeEdgeNode = field(default_factory=ThreeEdgeNode)
    theme_node: ThreeThemeNode = field(default_factory=ThreeThemeNode)
    quality_node: ThreeQualityNode = field(default_factory=ThreeQualityNode)

    def resolve(self, path: str) -> BaseLogosNode | None:
        """Resolve a path to its node."""
        if path.startswith("concept.projection.three.node"):
            return self.node_node
        elif path.startswith("concept.projection.three.edge"):
            return self.edge_node
        elif path.startswith("concept.projection.three.theme"):
            return self.theme_node
        elif path.startswith("concept.projection.three.quality"):
            return self.quality_node
        return None


# =============================================================================
# Factory Functions
# =============================================================================


def create_three_resolver() -> ThreeContextResolver:
    """Create a ThreeContextResolver with default configuration."""
    return ThreeContextResolver()


def create_three_node_node() -> ThreeNodeNode:
    """Create a ThreeNodeNode."""
    return ThreeNodeNode()


def create_three_edge_node() -> ThreeEdgeNode:
    """Create a ThreeEdgeNode."""
    return ThreeEdgeNode()


def create_three_theme_node() -> ThreeThemeNode:
    """Create a ThreeThemeNode."""
    return ThreeThemeNode()


def create_three_quality_node() -> ThreeQualityNode:
    """Create a ThreeQualityNode."""
    return ThreeQualityNode()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "Quality",
    "ThemeName",
    # Constants
    "THEME_REGISTRY",
    "QUALITY_CONFIGS",
    "NODE_DEFAULTS",
    "EDGE_DEFAULTS",
    "THREE_AFFORDANCES",
    # Nodes
    "ThreeNodeNode",
    "ThreeEdgeNode",
    "ThreeThemeNode",
    "ThreeQualityNode",
    # Resolver
    "ThreeContextResolver",
    # Factories
    "create_three_resolver",
    "create_three_node_node",
    "create_three_edge_node",
    "create_three_theme_node",
    "create_three_quality_node",
]
