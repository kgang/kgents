"""
Emergence Sheaf: Global Coherence from Local Tile Views.

The EmergenceSheaf completes the three-layer categorical stack:
1. EMERGENCE_POLYNOMIAL: State machine for phase × family × config × circadian
2. EMERGENCE_OPERAD: Composition grammar for patterns
3. EmergenceSheaf: Global coherence from tile views (THIS FILE)

The sheaf is needed because pattern tiles exist in a GRID:
- Gallery (root) determines global circadian and selected family
- Tiles (leaves) render with inherited qualia + local selection state

The sheaf provides:
1. overlap(): When do tiles share context (family, circadian)?
2. compatible(): Are sibling tiles' qualia settings consistent?
3. glue(): Combine tile views into coherent gallery state
4. restrict(): Extract tile view from gallery state

Key insight: Gluing ensures CIRCADIAN COHERENCE across all tiles.
Individual tiles don't know about each other, but the sheaf ensures
they all render with the same circadian modulation.

See: plans/structured-greeting-boot.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .types import (
    CIRCADIAN_MODIFIERS,
    FAMILY_QUALIA,
    CircadianPhase,
    EmergencePhase,
    EmergenceState,
    PatternConfig,
    PatternFamily,
    QualiaCoords,
    TileView,
)

# =============================================================================
# Emergence Contexts
# =============================================================================


@dataclass(frozen=True)
class EmergenceContext:
    """
    A context in the emergence tile hierarchy.

    Contexts form a two-level tree:
    - GalleryContext: root, determines global circadian and family
    - TileContext: leaves, render with inherited qualia + local state

    The parent relationship creates the hierarchy:
        gallery
         ├── tile_chladni_0_0
         ├── tile_chladni_0_1
         └── tile_mandala_0_0

    Attributes:
        name: Unique identifier for this context
        level: "gallery" | "tile"
        parent: Name of parent context (None for gallery)
        family: Pattern family for this tile (None for gallery)
        tile_index: Grid position (row, col) for tiles
    """

    name: str
    level: str  # "gallery" | "tile"
    parent: str | None = None
    family: PatternFamily | None = None
    tile_index: tuple[int, int] | None = None

    def __hash__(self) -> int:
        return hash((self.name, self.level, self.parent))

    def is_ancestor_of(self, other: EmergenceContext) -> bool:
        """Check if this context is an ancestor of another."""
        if self.name == other.name:
            return True
        if self.level == "gallery":
            return True
        return False

    def is_sibling_of(self, other: EmergenceContext) -> bool:
        """Check if two contexts are sibling tiles."""
        if self.level != "tile" or other.level != "tile":
            return False
        return self.parent == other.parent

    def shares_family(self, other: EmergenceContext) -> bool:
        """Check if two tiles share the same pattern family."""
        if self.family is None or other.family is None:
            return False
        return self.family == other.family


# Standard contexts
GALLERY_CONTEXT = EmergenceContext("gallery", "gallery")


def create_tile_context(
    family: PatternFamily,
    row: int,
    col: int,
    parent: str = "gallery",
) -> EmergenceContext:
    """Create a tile context for a specific grid position."""
    return EmergenceContext(
        name=f"tile_{family.value}_{row}_{col}",
        level="tile",
        parent=parent,
        family=family,
        tile_index=(row, col),
    )


# =============================================================================
# Sheaf Errors
# =============================================================================


@dataclass
class GluingError(Exception):
    """Raised when local views cannot be glued."""

    contexts: list[str]
    reason: str

    def __str__(self) -> str:
        return f"Cannot glue contexts {self.contexts}: {self.reason}"


@dataclass
class RestrictionError(Exception):
    """Raised when restriction fails."""

    context: str
    reason: str

    def __str__(self) -> str:
        return f"Cannot restrict to {self.context}: {self.reason}"


# =============================================================================
# EmergenceSheaf Implementation
# =============================================================================


class EmergenceSheaf:
    """
    Sheaf structure for emergence tile coherence.

    Provides the four sheaf operations:
    - overlap: Compute shared context between tiles
    - restrict: Extract tile view from gallery state
    - compatible: Check if tile views agree on shared context
    - glue: Combine tile views into coherent gallery state

    The gluing operation ensures:
    - All tiles share the same circadian phase
    - Selected tiles have consistent visual treatment
    - Qualia coordinates are coherent across family boundaries
    """

    def __init__(
        self,
        contexts: set[EmergenceContext] | None = None,
    ):
        """
        Initialize emergence sheaf.

        Args:
            contexts: Set of contexts in the tile hierarchy.
                     Defaults to just the gallery context.
        """
        self.contexts = contexts or {GALLERY_CONTEXT}
        self._context_map: dict[str, EmergenceContext] = {ctx.name: ctx for ctx in self.contexts}

    def add_context(self, context: EmergenceContext) -> None:
        """Add a context to the sheaf."""
        self.contexts.add(context)
        self._context_map[context.name] = context

    def get_context(self, name: str) -> EmergenceContext | None:
        """Get a context by name."""
        return self._context_map.get(name)

    def overlap(self, ctx1: EmergenceContext, ctx2: EmergenceContext) -> set[str]:
        """
        Compute overlap of two emergence contexts.

        Contexts overlap when they share:
        1. Circadian phase (all tiles share this)
        2. Pattern family (tiles in same family)
        3. Selection state (if both selected/hovered)

        Args:
            ctx1: First context
            ctx2: Second context

        Returns:
            Set of shared properties (e.g., {"circadian", "family"})
        """
        overlap_set: set[str] = set()

        # Same context: full overlap
        if ctx1.name == ctx2.name:
            return {"circadian", "family", "qualia", "selection"}

        # Gallery context overlaps with all on circadian
        if ctx1.level == "gallery" or ctx2.level == "gallery":
            overlap_set.add("circadian")

        # Sibling tiles share circadian
        if ctx1.is_sibling_of(ctx2):
            overlap_set.add("circadian")

        # Same family tiles share qualia
        if ctx1.shares_family(ctx2):
            overlap_set.add("family")
            overlap_set.add("qualia")

        return overlap_set

    def restrict(
        self,
        global_state: EmergenceState,
        tile_context: EmergenceContext,
    ) -> TileView:
        """
        Restrict gallery state to a single tile view.

        Given gallery-level state, extract the view for a specific tile.
        The restriction applies:
        1. Family-specific qualia from FAMILY_QUALIA
        2. Circadian modulation from global state
        3. Selection state (is this tile selected?)

        Args:
            global_state: The gallery-level emergence state
            tile_context: The tile context to restrict to

        Returns:
            TileView for the tile

        Raises:
            RestrictionError: If tile context is invalid
        """
        if tile_context.level != "tile":
            raise RestrictionError(
                context=tile_context.name,
                reason="Can only restrict to tile contexts",
            )

        if tile_context.family is None:
            raise RestrictionError(
                context=tile_context.name,
                reason="Tile context must have a family",
            )

        # Get base qualia for family
        base_qualia = FAMILY_QUALIA.get(tile_context.family, QualiaCoords())

        # Apply circadian modulation
        modifier = CIRCADIAN_MODIFIERS[global_state.circadian]
        modified_qualia = base_qualia.apply_modifier(modifier)

        # Check selection state
        is_selected = (
            global_state.selected_family == tile_context.family
            if global_state.selected_family
            else False
        )

        # Generate default config if none exists
        config = global_state.pattern_config
        if config is None or config.family != tile_context.family:
            config = PatternConfig(
                family=tile_context.family,
                param1=4.0,  # Default param1
                param2=4.0,  # Default param2
            )

        return TileView(
            tile_id=tile_context.name,
            config=config,
            qualia=modified_qualia,
            circadian=global_state.circadian,
            is_selected=is_selected,
            is_hovered=False,  # Hover state is UI-level, not sheaf
        )

    def compatible(self, tiles: list[TileView]) -> bool:
        """
        Check if tile views are compatible for gluing.

        Tiles are compatible when:
        1. All share the same circadian phase
        2. Same-family tiles have consistent qualia

        Args:
            tiles: List of tile views to check

        Returns:
            True if all tile views can be glued
        """
        if len(tiles) < 2:
            return True

        # Check circadian consistency
        circadians = {t.circadian for t in tiles}
        if len(circadians) > 1:
            return False

        # Check qualia consistency within same family
        family_qualia: dict[PatternFamily, QualiaCoords] = {}
        for tile in tiles:
            family = tile.config.family
            if family in family_qualia:
                existing = family_qualia[family]
                # Check qualia match (within tolerance)
                if abs(existing.warmth - tile.qualia.warmth) > 0.01:
                    return False
            else:
                family_qualia[family] = tile.qualia

        return True

    def glue(self, tiles: list[TileView]) -> EmergenceState:
        """
        Glue tile views into global emergence state.

        This is where COHERENCE emerges:
        - Individual tile views combine into gallery state
        - Circadian phase is unified across all tiles
        - Selected tile determines the active pattern

        Args:
            tiles: List of tile views to glue.
                   Must be compatible (call compatible() first).

        Returns:
            The glued emergence state

        Raises:
            GluingError: If tile views cannot be glued
        """
        if not self.compatible(tiles):
            raise GluingError(
                contexts=[t.tile_id for t in tiles],
                reason="Tiles have inconsistent circadian or qualia",
            )

        if len(tiles) == 0:
            # No tiles: return idle state
            return EmergenceState(phase=EmergencePhase.IDLE)

        # Use first tile for circadian (all should match)
        circadian = tiles[0].circadian

        # Find selected tile
        selected_tile = next((t for t in tiles if t.is_selected), None)

        if selected_tile:
            return EmergenceState(
                phase=EmergencePhase.EXPLORING,
                selected_family=selected_tile.config.family,
                pattern_config=selected_tile.config,
                circadian=circadian,
                qualia=selected_tile.qualia,
            )
        else:
            # No selection: gallery mode with first family
            return EmergenceState(
                phase=EmergencePhase.GALLERY,
                selected_family=tiles[0].config.family if tiles else None,
                pattern_config=None,
                circadian=circadian,
                qualia=tiles[0].qualia if tiles else QualiaCoords(),
            )

    def create_grid(
        self,
        families: list[PatternFamily],
        rows: int = 3,
        cols: int = 3,
    ) -> list[EmergenceContext]:
        """
        Create a grid of tile contexts for multiple families.

        Helper method to populate the sheaf with a standard gallery layout.

        Args:
            families: Pattern families to include
            rows: Number of rows per family
            cols: Number of columns per family

        Returns:
            List of created tile contexts
        """
        contexts: list[EmergenceContext] = []

        for family in families:
            for row in range(rows):
                for col in range(cols):
                    ctx = create_tile_context(family, row, col)
                    self.add_context(ctx)
                    contexts.append(ctx)

        return contexts

    def __repr__(self) -> str:
        tile_count = sum(1 for ctx in self.contexts if ctx.level == "tile")
        return f"EmergenceSheaf(tiles={tile_count})"


# =============================================================================
# Factory
# =============================================================================


def create_emergence_sheaf() -> EmergenceSheaf:
    """
    Create an EmergenceSheaf for tile coherence.

    Returns an empty sheaf with just the gallery context.
    Use create_grid() to add tiles.
    """
    return EmergenceSheaf()


def create_emergence_sheaf_for_families(
    families: list[PatternFamily],
    rows: int = 3,
    cols: int = 3,
) -> EmergenceSheaf:
    """
    Create an EmergenceSheaf with a grid for each family.

    Args:
        families: Pattern families to include
        rows: Number of rows per family
        cols: Number of columns per family

    Returns:
        EmergenceSheaf with tile grid populated

    Example:
        sheaf = create_emergence_sheaf_for_families(
            families=[PatternFamily.CHLADNI, PatternFamily.MANDALA],
            rows=3,
            cols=3,
        )
        # Creates 18 tiles (9 per family)
    """
    sheaf = EmergenceSheaf()
    sheaf.create_grid(families, rows, cols)
    return sheaf


# Global instance for convenience
EMERGENCE_SHEAF = create_emergence_sheaf()


__all__ = [
    # Contexts
    "EmergenceContext",
    "GALLERY_CONTEXT",
    "create_tile_context",
    # Sheaf
    "EmergenceSheaf",
    "EMERGENCE_SHEAF",
    "create_emergence_sheaf",
    "create_emergence_sheaf_for_families",
    # Errors
    "GluingError",
    "RestrictionError",
]
