"""
Crown Jewels Path Registry

Registers AGENTESE paths for the Crown Jewel applications:
1. Holographic Second Brain (Sheaf) - self.memory.*, self.memory.ghost.*
2. Design Language System (Operad) - concept.design.*
3. Morpheus LLM Gateway (Infrastructure) - world.morpheus.*

Note: Coalition, Park, Simulation, Gestalt removed 2025-12-21.
Note: Atelier and Gardener deprecated 2025-12-21.
Note: Emergence (world.emergence.*) removed 2025-12-21.

Per plans/core-apps-synthesis.md - the unified categorical foundation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ..logos import Logos

# Crown Symbiont imports (lazy to avoid circular deps)
I = TypeVar("I")
O = TypeVar("O")
S = TypeVar("S")

# =============================================================================
# Path Registry Definitions per Crown Jewel
# =============================================================================

# Atelier paths deprecated 2025-12-21
ATELIER_PATHS: dict[str, dict[str, Any]] = {}

# Coalition paths removed 2025-12-21
COALITION_PATHS: dict[str, dict[str, Any]] = {}

# Park paths removed 2025-12-21
PARK_PATHS: dict[str, dict[str, Any]] = {}

# Simulation paths removed 2025-12-21
SIMULATION_PATHS: dict[str, dict[str, Any]] = {}

# Gestalt paths removed 2025-12-21
GESTALT_PATHS: dict[str, dict[str, Any]] = {}
GESTALT_LIVE_PATHS: dict[str, dict[str, Any]] = {}

# Gardener paths deprecated 2025-12-21
GARDENER_PATHS: dict[str, dict[str, Any]] = {}

# Crown Jewel: Holographic Second Brain
BRAIN_PATHS: dict[str, dict[str, Any]] = {
    "self.memory.manifest": {
        "aspect": "manifest",
        "description": "View memory system health and recent crystals",
        "effects": [],
    },
    "self.memory.capture": {
        "aspect": "define",
        "description": "Capture content into holographic memory",
        "effects": ["CRYSTAL_FORMED", "INDEX_UPDATED"],
    },
    "self.memory.recall": {
        "aspect": "manifest",
        "description": "Query memory via semantic search",
        "effects": [],
    },
    "self.memory.ghost.surface": {
        "aspect": "manifest",
        "description": "Surface ghost suggestions (things you might have forgotten)",
        "effects": [],
    },
    "self.memory.ghost.dismiss": {
        "aspect": "define",
        "description": "Dismiss a ghost suggestion",
        "effects": ["GHOST_ARCHIVED"],
    },
    "self.memory.cartography.manifest": {
        "aspect": "manifest",
        "description": "View knowledge topology map",
        "effects": [],
    },
    "self.memory.cartography.navigate": {
        "aspect": "manifest",
        "description": "Navigate to related concepts",
        "effects": [],
    },
}

# Note: Emergence (world.emergence.*) removed 2025-12-21

# Design Language System (concept.design.*)
# Exposes the three orthogonal design operads: Layout, Content, Motion
DESIGN_PATHS: dict[str, dict[str, Any]] = {
    "concept.design.manifest": {
        "aspect": "manifest",
        "description": "Design Language System overview",
        "effects": [],
    },
    "concept.design.layout.manifest": {
        "aspect": "manifest",
        "description": "Layout operad state",
        "effects": [],
    },
    "concept.design.layout.operations": {
        "aspect": "manifest",
        "description": "Layout operations (split, stack, drawer, float)",
        "effects": [],
    },
    "concept.design.layout.laws": {
        "aspect": "manifest",
        "description": "Layout composition laws",
        "effects": [],
    },
    "concept.design.layout.verify": {
        "aspect": "manifest",
        "description": "Verify layout laws pass",
        "effects": [],
    },
    "concept.design.layout.compose": {
        "aspect": "define",
        "description": "Apply layout operation",
        "effects": [],
    },
    "concept.design.content.manifest": {
        "aspect": "manifest",
        "description": "Content operad state",
        "effects": [],
    },
    "concept.design.content.operations": {
        "aspect": "manifest",
        "description": "Content operations (degrade, compose)",
        "effects": [],
    },
    "concept.design.content.laws": {
        "aspect": "manifest",
        "description": "Content degradation laws",
        "effects": [],
    },
    "concept.design.content.verify": {
        "aspect": "manifest",
        "description": "Verify content laws pass",
        "effects": [],
    },
    "concept.design.content.degrade": {
        "aspect": "define",
        "description": "Apply content degradation",
        "effects": [],
    },
    "concept.design.motion.manifest": {
        "aspect": "manifest",
        "description": "Motion operad state",
        "effects": [],
    },
    "concept.design.motion.operations": {
        "aspect": "manifest",
        "description": "Motion operations (breathe, pop, shake, shimmer, chain, parallel)",
        "effects": [],
    },
    "concept.design.motion.laws": {
        "aspect": "manifest",
        "description": "Motion composition laws",
        "effects": [],
    },
    "concept.design.motion.verify": {
        "aspect": "manifest",
        "description": "Verify motion laws pass",
        "effects": [],
    },
    "concept.design.motion.apply": {
        "aspect": "define",
        "description": "Apply motion primitive",
        "effects": [],
    },
    "concept.design.operad.manifest": {
        "aspect": "manifest",
        "description": "Unified design operad",
        "effects": [],
    },
    "concept.design.operad.operations": {
        "aspect": "manifest",
        "description": "All design operations",
        "effects": [],
    },
    "concept.design.operad.laws": {
        "aspect": "manifest",
        "description": "All design laws (including naturality)",
        "effects": [],
    },
    "concept.design.operad.verify": {
        "aspect": "manifest",
        "description": "Verify all design laws pass",
        "effects": [],
    },
    "concept.design.operad.naturality": {
        "aspect": "manifest",
        "description": "Check Layout . Content . Motion naturality",
        "effects": [],
    },
}

# Morpheus: LLM Gateway (world.morpheus.*)
# Note: Morpheus is infrastructure, not a "Crown Jewel" application,
# but has @node registration so we document its paths here for completeness.
MORPHEUS_PATHS: dict[str, dict[str, Any]] = {
    "world.morpheus.manifest": {
        "aspect": "manifest",
        "description": "Gateway health status and configuration",
        "effects": [],
    },
    "world.morpheus.complete": {
        "aspect": "define",
        "description": "Chat completion (non-streaming)",
        "effects": ["API_CALL"],
    },
    "world.morpheus.stream": {
        "aspect": "define",
        "description": "Chat completion (streaming via SSE)",
        "effects": ["API_CALL"],
    },
    "world.morpheus.providers": {
        "aspect": "manifest",
        "description": "List available LLM providers",
        "effects": [],
    },
    "world.morpheus.metrics": {
        "aspect": "manifest",
        "description": "Request/error counts and latency stats",
        "effects": [],
    },
    "world.morpheus.health": {
        "aspect": "manifest",
        "description": "Provider health checks",
        "effects": [],
    },
    "world.morpheus.route": {
        "aspect": "manifest",
        "description": "Model routing information",
        "effects": [],
    },
}

# =============================================================================
# Unified Registry
# =============================================================================

ALL_CROWN_JEWEL_PATHS: dict[str, dict[str, Any]] = {
    **BRAIN_PATHS,
    **DESIGN_PATHS,
    **MORPHEUS_PATHS,
}


@dataclass
class CrownJewelRegistry:
    """
    Registry for Crown Jewel AGENTESE paths.

    Provides path discovery and validation for active jewels.
    Can be wired into Logos for resolution.
    """

    paths: dict[str, dict[str, Any]] = field(default_factory=lambda: ALL_CROWN_JEWEL_PATHS.copy())

    def list_paths(self, jewel: str | None = None) -> list[str]:
        """
        List registered paths, optionally filtered by jewel.

        Args:
            jewel: One of "brain", "emergence", "design", "morpheus", or None for all
        """
        jewel_prefixes = {
            "brain": ("self.memory.",),
            "design": ("concept.design.",),
            "morpheus": ("world.morpheus.",),
        }

        if jewel is None:
            return list(self.paths.keys())

        prefixes = jewel_prefixes.get(jewel, ())
        return [p for p in self.paths if any(p.startswith(pre) for pre in prefixes)]

    def get_path_info(self, path: str) -> dict[str, Any] | None:
        """Get path metadata if registered."""
        return self.paths.get(path)

    def is_registered(self, path: str) -> bool:
        """Check if path is registered."""
        return path in self.paths

    def get_aspect(self, path: str) -> str | None:
        """Get the aspect for a path."""
        info = self.paths.get(path)
        return info.get("aspect") if info else None

    def get_effects(self, path: str) -> list[str]:
        """Get effects for a path."""
        info = self.paths.get(path)
        return info.get("effects", []) if info else []


# =============================================================================
# Logos Integration
# =============================================================================


def register_crown_jewel_paths(logos: "Logos") -> None:
    """
    Register Crown Jewel paths with a Logos instance.

    This enables discovery and validation of all jewel paths.
    Actual resolution still requires handler implementations.

    Args:
        logos: The Logos instance to register with
    """
    registry = CrownJewelRegistry()

    # Store registry in logos for query support
    if not hasattr(logos, "_crown_jewel_registry"):
        logos._crown_jewel_registry = registry  # type: ignore[attr-defined]


def get_crown_jewel_registry(logos: "Logos") -> CrownJewelRegistry | None:
    """Get the Crown Jewel registry from a Logos instance."""
    return getattr(logos, "_crown_jewel_registry", None)


# =============================================================================
# Crown Symbiont Integration
# =============================================================================


def list_self_time_paths() -> dict[str, list[str]]:
    """
    List all self.* and time.* Crown paths.

    Returns:
        Dict with "self" and "time" keys containing lists of paths

    Note: Crown Symbiont infrastructure was removed in data-architecture-rewrite.
    """
    self_paths = [p for p in ALL_CROWN_JEWEL_PATHS if p.startswith("self.")]
    time_paths = [p for p in ALL_CROWN_JEWEL_PATHS if p.startswith("time.")]

    return {
        "self": self_paths,
        "time": time_paths,
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Path registries per jewel (kept for backward compat, now empty)
    "ATELIER_PATHS",
    "COALITION_PATHS",
    "BRAIN_PATHS",
    "PARK_PATHS",
    "SIMULATION_PATHS",
    "GESTALT_PATHS",
    "GESTALT_LIVE_PATHS",
    "GARDENER_PATHS",
    "DESIGN_PATHS",
    "MORPHEUS_PATHS",
    # Unified registry
    "ALL_CROWN_JEWEL_PATHS",
    "CrownJewelRegistry",
    # Logos integration
    "register_crown_jewel_paths",
    "get_crown_jewel_registry",
    "list_self_time_paths",
]
