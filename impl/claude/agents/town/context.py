"""
Town Context: Observation contexts for TownSheaf topology.

Contexts form a hierarchy:
- TownContext: Global view (level="town")
- RegionContext: Location views (level="region") - inn, workshop, plaza, etc.
- CitizenContext: Individual citizen view (level="citizen")

The parent relationship creates the hierarchy:
    town
     ├── inn (region)
     │   ├── citizen_alice
     │   └── citizen_bob
     ├── workshop (region)
     │   └── citizen_carol
     └── plaza (region)

See: plans/town-rebuild.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import FrozenSet


class ContextLevel(Enum):
    """Levels in the town observation hierarchy."""

    TOWN = auto()  # Global view
    REGION = auto()  # Location view (inn, workshop, plaza)
    CITIZEN = auto()  # Individual citizen view


class RegionType(Enum):
    """Types of regions in the town."""

    INN = "inn"  # Social gathering, gossip hub
    WORKSHOP = "workshop"  # Productive work, skills
    PLAZA = "plaza"  # Public events, announcements
    MARKET = "market"  # Trade, economics
    LIBRARY = "library"  # Knowledge, research
    TEMPLE = "temple"  # Reflection, rituals
    GARDEN = "garden"  # Creativity, contemplation


# Region adjacency graph (which regions can citizens travel between directly)
REGION_ADJACENCY: dict[RegionType, set[RegionType]] = {
    RegionType.INN: {RegionType.PLAZA, RegionType.MARKET},
    RegionType.WORKSHOP: {RegionType.MARKET, RegionType.LIBRARY},
    RegionType.PLAZA: {RegionType.INN, RegionType.MARKET, RegionType.TEMPLE, RegionType.GARDEN},
    RegionType.MARKET: {RegionType.INN, RegionType.WORKSHOP, RegionType.PLAZA},
    RegionType.LIBRARY: {RegionType.WORKSHOP, RegionType.TEMPLE},
    RegionType.TEMPLE: {RegionType.PLAZA, RegionType.LIBRARY, RegionType.GARDEN},
    RegionType.GARDEN: {RegionType.PLAZA, RegionType.TEMPLE},
}

# Rumor distance (gossip can spread between these regions)
RUMOR_DISTANCE: dict[RegionType, set[RegionType]] = {
    # Inn gossip spreads everywhere
    RegionType.INN: {RegionType.PLAZA, RegionType.MARKET, RegionType.WORKSHOP},
    # Plaza is public, news spreads
    RegionType.PLAZA: {RegionType.INN, RegionType.MARKET, RegionType.TEMPLE, RegionType.GARDEN},
    # Workshop talk stays more local
    RegionType.WORKSHOP: {RegionType.INN, RegionType.MARKET, RegionType.LIBRARY},
    # Market is commercial hub
    RegionType.MARKET: {RegionType.INN, RegionType.PLAZA, RegionType.WORKSHOP},
    # Library is quieter
    RegionType.LIBRARY: {RegionType.WORKSHOP, RegionType.TEMPLE},
    # Temple has reverent whispers
    RegionType.TEMPLE: {RegionType.PLAZA, RegionType.LIBRARY, RegionType.GARDEN},
    # Garden contemplation
    RegionType.GARDEN: {RegionType.PLAZA, RegionType.TEMPLE},
}


@dataclass(frozen=True)
class TownContext:
    """
    A context in the town observation topology.

    Contexts are immutable and hashable for use as dict keys.

    Attributes:
        name: Unique identifier for this context
        level: "town" | "region" | "citizen"
        parent: Name of parent context (None for town)
        region_type: Type of region (None for town/citizen)
    """

    name: str
    level: ContextLevel
    parent: str | None = None
    region_type: RegionType | None = None

    def __hash__(self) -> int:
        return hash((self.name, self.level, self.parent))

    @property
    def is_global(self) -> bool:
        """Check if this is the global town context."""
        return self.level == ContextLevel.TOWN

    @property
    def is_region(self) -> bool:
        """Check if this is a region context."""
        return self.level == ContextLevel.REGION

    @property
    def is_citizen(self) -> bool:
        """Check if this is a citizen context."""
        return self.level == ContextLevel.CITIZEN

    def is_ancestor_of(self, other: TownContext) -> bool:
        """Check if this context is an ancestor of another."""
        if self.name == other.name:
            return True
        if self.is_global:
            return True
        if self.is_region and other.is_citizen and other.parent == self.name:
            return True
        return False

    def is_sibling_of(self, other: TownContext) -> bool:
        """Check if two contexts are siblings (same level, same parent)."""
        if self.level != other.level:
            return False
        return self.parent == other.parent

    def shares_boundary(self, other: TownContext) -> bool:
        """
        Check if citizens can move between these regions.

        Only applies to region-level contexts.
        """
        if not self.is_region or not other.is_region:
            return False
        if self.region_type is None or other.region_type is None:
            return False
        return other.region_type in REGION_ADJACENCY.get(self.region_type, set())

    def in_rumor_distance(self, other: TownContext) -> bool:
        """
        Check if gossip can spread between these regions.

        Only applies to region-level contexts.
        """
        if not self.is_region or not other.is_region:
            return False
        if self.region_type is None or other.region_type is None:
            return False
        return other.region_type in RUMOR_DISTANCE.get(self.region_type, set())


# Standard contexts
TOWN_CONTEXT = TownContext(name="town", level=ContextLevel.TOWN)


def create_region_context(
    region_type: RegionType,
    parent: str = "town",
) -> TownContext:
    """Create a region context."""
    return TownContext(
        name=region_type.value,
        level=ContextLevel.REGION,
        parent=parent,
        region_type=region_type,
    )


def create_citizen_context(
    citizen_id: str,
    region: str,
) -> TownContext:
    """Create a citizen context within a region."""
    return TownContext(
        name=f"citizen_{citizen_id}",
        level=ContextLevel.CITIZEN,
        parent=region,
    )


# Pre-built region contexts
INN_CONTEXT = create_region_context(RegionType.INN)
WORKSHOP_CONTEXT = create_region_context(RegionType.WORKSHOP)
PLAZA_CONTEXT = create_region_context(RegionType.PLAZA)
MARKET_CONTEXT = create_region_context(RegionType.MARKET)
LIBRARY_CONTEXT = create_region_context(RegionType.LIBRARY)
TEMPLE_CONTEXT = create_region_context(RegionType.TEMPLE)
GARDEN_CONTEXT = create_region_context(RegionType.GARDEN)

ALL_REGION_CONTEXTS = [
    INN_CONTEXT,
    WORKSHOP_CONTEXT,
    PLAZA_CONTEXT,
    MARKET_CONTEXT,
    LIBRARY_CONTEXT,
    TEMPLE_CONTEXT,
    GARDEN_CONTEXT,
]


__all__ = [
    # Enums
    "ContextLevel",
    "RegionType",
    # Constants
    "REGION_ADJACENCY",
    "RUMOR_DISTANCE",
    # Classes
    "TownContext",
    # Factory functions
    "create_region_context",
    "create_citizen_context",
    # Standard contexts
    "TOWN_CONTEXT",
    "INN_CONTEXT",
    "WORKSHOP_CONTEXT",
    "PLAZA_CONTEXT",
    "MARKET_CONTEXT",
    "LIBRARY_CONTEXT",
    "TEMPLE_CONTEXT",
    "GARDEN_CONTEXT",
    "ALL_REGION_CONTEXTS",
]
