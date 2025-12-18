"""
TownSheaf: Global Coherence from Local Region Views.

The TownSheaf completes the three-layer categorical stack for Agent Town:
1. CitizenPolynomial: State machine for citizen phases
2. TOWN_OPERAD: Composition grammar for citizen interactions
3. TownSheaf: Global coherence from region views (THIS FILE)

The sheaf is needed because the town exists as REGIONS:
- Inn, Workshop, Plaza, Market, Library, Temple, Garden
- Citizens move between regions, relationships span regions
- Gossip spreads across region boundaries

The sheaf provides:
1. overlap(): When do regions share context (movement, gossip)?
2. restrict(): Extract region view from global town state
3. compatible(): Are region views consistent on overlaps?
4. glue(): Combine region views into coherent town state (EMERGENCE)

Key insight: Gluing ensures COHERENCE across regions.
Individual regions don't know about each other, but the sheaf ensures
relationships are consistent and emergence patterns are detected.

See: plans/town-rebuild.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .context import (
    REGION_ADJACENCY,
    RUMOR_DISTANCE,
    TOWN_CONTEXT,
    ContextLevel,
    RegionType,
    TownContext,
)

# =============================================================================
# Sheaf Data Structures
# =============================================================================


@dataclass(frozen=True)
class RegionView:
    """
    Local view of a region.

    Contains everything visible from within this region:
    - Citizens currently present
    - Relationships involving these citizens
    - Events that happened here
    - Coalition memberships
    """

    region: TownContext
    citizens: FrozenSet[str]  # citizen IDs
    relationships: dict[tuple[str, str], float] = field(
        default_factory=dict, hash=False
    )  # (a, b) -> strength
    events: tuple[dict[str, Any], ...] = field(default_factory=tuple)  # Immutable event log
    coalition_memberships: dict[str, frozenset[str]] = field(
        default_factory=dict, hash=False
    )  # citizen -> coalitions

    def __hash__(self) -> int:
        return hash((self.region, self.citizens))

    def restrict_to_citizens(self, citizen_ids: FrozenSet[str]) -> RegionView:
        """Extract view restricted to specific citizens."""
        restricted_citizens = self.citizens & citizen_ids

        restricted_relationships = {
            k: v
            for k, v in self.relationships.items()
            if k[0] in restricted_citizens or k[1] in restricted_citizens
        }

        restricted_coalitions = {
            c: m for c, m in self.coalition_memberships.items() if c in restricted_citizens
        }

        return RegionView(
            region=self.region,
            citizens=restricted_citizens,
            relationships=restricted_relationships,
            events=(),  # Events are region-local, don't restrict
            coalition_memberships=restricted_coalitions,
        )

    def citizen_count(self) -> int:
        """Number of citizens in this region."""
        return len(self.citizens)

    def relationship_density(self) -> float:
        """Ratio of actual relationships to possible relationships."""
        n = len(self.citizens)
        if n < 2:
            return 0.0
        possible = n * (n - 1) / 2
        return len(self.relationships) / possible


@dataclass
class TownState:
    """
    Global town state (result of sheaf gluing).

    Contains the unified view across all regions, plus
    EMERGENT patterns only visible at the global level.
    """

    citizens: FrozenSet[str]
    relationships: dict[tuple[str, str], float]
    citizen_locations: dict[str, str]  # citizen_id -> region_name
    coalitions: dict[str, frozenset[str]]  # coalition_id -> members

    # Emergence metrics (only visible after gluing)
    emergence: dict[str, Any] = field(default_factory=dict)

    @property
    def total_citizens(self) -> int:
        return len(self.citizens)

    @property
    def total_relationships(self) -> int:
        return len(self.relationships)

    @property
    def total_coalitions(self) -> int:
        return len(self.coalitions)


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
# TownSheaf Implementation
# =============================================================================


class TownSheaf:
    """
    Sheaf structure for Agent Town coherence.

    Provides the four sheaf operations:
    - overlap: Compute shared citizens between regions
    - restrict: Extract region view from town state
    - compatible: Check if region views agree on overlaps
    - glue: Combine region views into coherent town state

    The gluing operation ensures:
    - Relationship consistency across regions
    - Coalition membership consistency
    - Detection of emergent patterns (culture motifs, rituality)
    """

    def __init__(
        self,
        contexts: set[TownContext] | None = None,
        relationship_epsilon: float = 0.01,
    ):
        """
        Initialize town sheaf.

        Args:
            contexts: Set of contexts in the town topology.
                     Defaults to just the town context.
            relationship_epsilon: Tolerance for relationship strength comparison.
        """
        self.contexts = contexts or {TOWN_CONTEXT}
        self._context_map: dict[str, TownContext] = {ctx.name: ctx for ctx in self.contexts}
        self._epsilon = relationship_epsilon

    def add_context(self, context: TownContext) -> None:
        """Add a context to the sheaf."""
        self.contexts.add(context)
        self._context_map[context.name] = context

    def get_context(self, name: str) -> TownContext | None:
        """Get a context by name."""
        return self._context_map.get(name)

    def overlap(
        self,
        region1: TownContext,
        region2: TownContext,
        citizen_locations: dict[str, str] | None = None,
    ) -> set[str]:
        """
        Compute overlap of two region contexts.

        Regions overlap when citizens move between them:
        1. Regions share a boundary (adjacency graph)
        2. Regions are in rumor distance (gossip can spread)
        3. Citizens are present in both (travel patterns)

        Args:
            region1: First region context
            region2: Second region context
            citizen_locations: Optional map of citizen -> current region

        Returns:
            Set of citizen IDs in the overlap
        """
        # Same region: full overlap
        if region1.name == region2.name:
            # Return all citizens in the region if we have location data
            if citizen_locations:
                return {cid for cid, loc in citizen_locations.items() if loc == region1.name}
            return set()

        # Town context overlaps with all regions
        if region1.is_global or region2.is_global:
            if citizen_locations:
                return set(citizen_locations.keys())
            return set()

        # Check if regions are adjacent or in rumor distance
        can_overlap = region1.shares_boundary(region2) or region1.in_rumor_distance(region2)
        if not can_overlap:
            return set()

        # Citizens who frequent both regions would be in overlap
        # For now, return empty set if no location data
        # Real implementation would track citizen movement patterns
        return set()

    def restrict(
        self,
        global_state: TownState,
        region: TownContext,
    ) -> RegionView:
        """
        Restrict global town state to a single region view.

        Given town-level state, extract the view for a specific region.
        The restriction includes:
        1. Citizens currently in this region
        2. Relationships involving these citizens
        3. Coalition memberships for these citizens

        Args:
            global_state: The town-level state
            region: The region context to restrict to

        Returns:
            RegionView for the region

        Raises:
            RestrictionError: If region context is invalid
        """
        if not region.is_region:
            if region.is_global:
                # Restricting to global returns everything
                return RegionView(
                    region=region,
                    citizens=global_state.citizens,
                    relationships=global_state.relationships,
                    events=(),
                    coalition_memberships={
                        cid: frozenset(
                            coal_id
                            for coal_id, members in global_state.coalitions.items()
                            if cid in members
                        )
                        for cid in global_state.citizens
                    },
                )
            raise RestrictionError(
                context=region.name,
                reason="Can only restrict to region contexts",
            )

        # Get citizens in this region
        region_citizens = frozenset(
            cid for cid, loc in global_state.citizen_locations.items() if loc == region.name
        )

        # Get relationships involving these citizens
        region_relationships = {
            k: v
            for k, v in global_state.relationships.items()
            if k[0] in region_citizens or k[1] in region_citizens
        }

        # Get coalition memberships for these citizens
        region_coalitions = {
            cid: frozenset(
                coal_id for coal_id, members in global_state.coalitions.items() if cid in members
            )
            for cid in region_citizens
        }

        return RegionView(
            region=region,
            citizens=region_citizens,
            relationships=region_relationships,
            events=(),  # Events would come from event store
            coalition_memberships=region_coalitions,
        )

    def compatible(self, views: dict[TownContext, RegionView]) -> bool:
        """
        Check if region views are compatible for gluing.

        Views are compatible when they agree on overlaps:
        1. Relationship strengths match (within epsilon)
        2. Coalition memberships match

        Args:
            views: Dict of context -> RegionView

        Returns:
            True if all views can be glued
        """
        if len(views) < 2:
            return True

        contexts = list(views.keys())

        for i, ctx1 in enumerate(contexts):
            for ctx2 in contexts[i + 1 :]:
                view1 = views[ctx1]
                view2 = views[ctx2]

                # Find overlapping citizens
                overlap_citizens = view1.citizens & view2.citizens
                if not overlap_citizens:
                    continue

                # Check relationship agreement
                for (a, b), strength1 in view1.relationships.items():
                    if a not in overlap_citizens and b not in overlap_citizens:
                        continue

                    strength2 = view2.relationships.get((a, b))
                    if strength2 is not None:
                        if abs(strength1 - strength2) > self._epsilon:
                            return False

                    # Also check reverse order
                    strength2_rev = view2.relationships.get((b, a))
                    if strength2_rev is not None:
                        if abs(strength1 - strength2_rev) > self._epsilon:
                            return False

                # Check coalition membership agreement
                for citizen in overlap_citizens:
                    coalitions1 = view1.coalition_memberships.get(citizen, frozenset())
                    coalitions2 = view2.coalition_memberships.get(citizen, frozenset())
                    if coalitions1 != coalitions2:
                        return False

        return True

    def glue(self, views: dict[TownContext, RegionView]) -> TownState:
        """
        Glue region views into global town state.

        This is where EMERGENCE happens:
        - Individual region views combine into town state
        - Patterns invisible in any single region become visible
        - Culture motifs, rituality, trust network density

        Args:
            views: Dict of context -> RegionView (must be compatible)

        Returns:
            The glued TownState

        Raises:
            GluingError: If views cannot be glued
        """
        if not self.compatible(views):
            raise GluingError(
                contexts=[ctx.name for ctx in views.keys()],
                reason="Views have inconsistent relationships or coalition memberships",
            )

        if len(views) == 0:
            return TownState(
                citizens=frozenset(),
                relationships={},
                citizen_locations={},
                coalitions={},
                emergence={},
            )

        # Merge all citizens
        all_citizens: set[str] = set()
        for view in views.values():
            all_citizens.update(view.citizens)

        # Build citizen locations
        citizen_locations: dict[str, str] = {}
        for ctx, view in views.items():
            if ctx.is_region:
                for cid in view.citizens:
                    citizen_locations[cid] = ctx.name

        # Merge relationships (average where multiple views)
        relationship_values: dict[tuple[str, str], list[float]] = {}
        for view in views.values():
            for k, v in view.relationships.items():
                # Normalize key order
                key = (min(k[0], k[1]), max(k[0], k[1]))
                relationship_values.setdefault(key, []).append(v)

        merged_relationships = {k: sum(vs) / len(vs) for k, vs in relationship_values.items()}

        # Merge coalitions
        all_coalitions: dict[str, set[str]] = {}
        for view in views.values():
            for cid, coal_ids in view.coalition_memberships.items():
                for coal_id in coal_ids:
                    all_coalitions.setdefault(coal_id, set()).add(cid)

        coalitions = {k: frozenset(v) for k, v in all_coalitions.items()}

        # Detect emergent patterns
        emergence = self._detect_emergence(
            citizens=frozenset(all_citizens),
            relationships=merged_relationships,
            citizen_locations=citizen_locations,
            coalitions=coalitions,
        )

        return TownState(
            citizens=frozenset(all_citizens),
            relationships=merged_relationships,
            citizen_locations=citizen_locations,
            coalitions=coalitions,
            emergence=emergence,
        )

    def _detect_emergence(
        self,
        citizens: FrozenSet[str],
        relationships: dict[tuple[str, str], float],
        citizen_locations: dict[str, str],
        coalitions: dict[str, frozenset[str]],
    ) -> dict[str, Any]:
        """
        Detect patterns only visible in global view.

        These emergent properties are invisible from any single region.
        """
        return {
            "culture_motifs": self._find_motifs(relationships),
            "rituality": self._compute_rituality(citizen_locations),
            "trust_density": self._compute_trust_density(relationships, len(citizens)),
            "coalition_overlap": self._compute_coalition_overlap(coalitions),
            "region_balance": self._compute_region_balance(citizen_locations),
        }

    def _find_motifs(self, relationships: dict[tuple[str, str], float]) -> list[dict[str, Any]]:
        """
        Find recurring interaction patterns (motifs).

        Motifs are small subgraph patterns that appear frequently.
        """
        motifs: list[dict[str, Any]] = []

        # Build adjacency for motif detection
        adjacency: dict[str, set[str]] = {}
        for (a, b), strength in relationships.items():
            if strength > 0.5:  # Only strong relationships
                adjacency.setdefault(a, set()).add(b)
                adjacency.setdefault(b, set()).add(a)

        # Find triangles (simplest non-trivial motif)
        triangles: list[tuple[str, str, str]] = []
        seen: set[frozenset[str]] = set()

        for a in adjacency:
            for b in adjacency.get(a, set()):
                for c in adjacency.get(b, set()):
                    if c in adjacency.get(a, set()):
                        triangle = frozenset([a, b, c])
                        if triangle not in seen and len(triangle) == 3:
                            seen.add(triangle)
                            sorted_tri = tuple(sorted(triangle))
                            triangles.append(sorted_tri)  # type: ignore

        if triangles:
            motifs.append(
                {
                    "type": "triangle",
                    "count": len(triangles),
                    "examples": triangles[:5],
                }
            )

        return motifs

    def _compute_rituality(self, citizen_locations: dict[str, str]) -> float:
        """
        Compute rituality score (periodic collective behaviors).

        Higher score indicates more citizens congregate in shared spaces.
        """
        if not citizen_locations:
            return 0.0

        # Count citizens per region
        region_counts: dict[str, int] = {}
        for region in citizen_locations.values():
            region_counts[region] = region_counts.get(region, 0) + 1

        # Rituality = variance in distribution
        # High variance means citizens cluster (ritualistic gathering)
        counts = list(region_counts.values())
        if len(counts) < 2:
            return 0.0

        mean = sum(counts) / len(counts)
        variance = sum((c - mean) ** 2 for c in counts) / len(counts)

        # Normalize to 0-1 scale
        max_variance = (len(citizen_locations) - 1) ** 2  # All in one region
        if max_variance == 0:
            return 0.0

        return min(1.0, variance / max_variance)

    def _compute_trust_density(
        self,
        relationships: dict[tuple[str, str], float],
        citizen_count: int,
    ) -> float:
        """
        Compute trust network density.

        Ratio of strong relationships to possible relationships.
        """
        if citizen_count < 2:
            return 0.0

        possible = citizen_count * (citizen_count - 1) / 2
        strong_count = sum(1 for s in relationships.values() if s > 0.5)

        return strong_count / possible

    def _compute_coalition_overlap(self, coalitions: dict[str, frozenset[str]]) -> float:
        """
        Compute coalition overlap score.

        Higher score means more citizens belong to multiple coalitions
        (bridge nodes that connect different groups).
        """
        if not coalitions:
            return 0.0

        # Count coalition memberships per citizen
        membership_count: dict[str, int] = {}
        for members in coalitions.values():
            for cid in members:
                membership_count[cid] = membership_count.get(cid, 0) + 1

        if not membership_count:
            return 0.0

        # Average memberships (1.0 = no overlap, higher = more bridges)
        avg = sum(membership_count.values()) / len(membership_count)
        return min(1.0, (avg - 1) / 2)  # Normalize assuming max ~3 memberships

    def _compute_region_balance(self, citizen_locations: dict[str, str]) -> float:
        """
        Compute region balance score.

        1.0 = perfectly balanced across regions
        0.0 = all citizens in one region
        """
        if not citizen_locations:
            return 0.0

        # Count citizens per region
        region_counts: dict[str, int] = {}
        for region in citizen_locations.values():
            region_counts[region] = region_counts.get(region, 0) + 1

        if len(region_counts) < 2:
            return 0.0

        # Use entropy-based balance
        total = sum(region_counts.values())
        probs = [c / total for c in region_counts.values()]

        # Entropy
        import math

        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        max_entropy = math.log(len(region_counts))

        if max_entropy == 0:
            return 0.0

        return entropy / max_entropy

    def __repr__(self) -> str:
        region_count = sum(1 for ctx in self.contexts if ctx.is_region)
        return f"TownSheaf(regions={region_count})"


# =============================================================================
# Factory
# =============================================================================


def create_town_sheaf() -> TownSheaf:
    """
    Create a TownSheaf with standard town topology.

    Returns a sheaf with the town context and all region contexts.
    """
    from .context import ALL_REGION_CONTEXTS

    sheaf = TownSheaf()
    for region_ctx in ALL_REGION_CONTEXTS:
        sheaf.add_context(region_ctx)
    return sheaf


# Global instance for convenience
TOWN_SHEAF = create_town_sheaf()


__all__ = [
    # Data structures
    "RegionView",
    "TownState",
    # Errors
    "GluingError",
    "RestrictionError",
    # Sheaf
    "TownSheaf",
    "TOWN_SHEAF",
    "create_town_sheaf",
]
