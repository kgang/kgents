"""
TownEnvironment: The Mesh Topology.

From Morton: The town is not a collection of citizens.
The town IS the mesh. Citizens are local thickenings.

Regions are not containers but *density gradients*.
Citizens are not "in" regions—they are where the mesh thickens.
Co-location is shared density, not shared coordinates.

The Environment provides:
- Region graph (adjacency)
- Citizen placement
- Movement validation
- Density queries

See: spec/town/metaphysics.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml
from agents.town.citizen import (
    CONSTRUCTION,
    CULTIVATION,
    EXCHANGE,
    EXPLORATION,
    GATHERING,
    HEALING,
    MEMORY,
    Citizen,
    Cosmotechnics,
    Eigenvectors,
)

# =============================================================================
# Region
# =============================================================================


@dataclass
class Region:
    """
    A region in the town mesh.

    From Morton: Regions are not containers.
    They are areas where the mesh thickens in particular ways.
    """

    name: str
    description: str = ""
    connections: list[str] = field(default_factory=list)
    capacity: int = 10
    properties: dict[str, Any] = field(default_factory=dict)

    def is_connected_to(self, other_name: str) -> bool:
        """Check if this region is connected to another."""
        return other_name in self.connections

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "connections": list(self.connections),
            "capacity": self.capacity,
            "properties": dict(self.properties),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Region:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            connections=data.get("connections", []),
            capacity=data.get("capacity", 10),
            properties=data.get("properties", {}),
        )


# =============================================================================
# TownEnvironment
# =============================================================================


@dataclass
class TownEnvironment:
    """
    The town mesh topology.

    From Morton: "Intimacy becomes threatening because it veils the mesh
    beneath the illusion of familiarity."

    The environment manages:
    - Regions (nodes in the graph)
    - Citizens (local densities in the mesh)
    - Adjacency (edges in the graph)
    """

    name: str
    regions: dict[str, Region] = field(default_factory=dict)
    citizens: dict[str, Citizen] = field(default_factory=dict)

    # Metrics
    total_token_spend: int = 0

    def add_region(self, region: Region) -> None:
        """Add a region to the environment."""
        self.regions[region.name] = region

    def add_citizen(self, citizen: Citizen) -> None:
        """Add a citizen to the environment."""
        self.citizens[citizen.id] = citizen

    def get_citizen_by_name(self, name: str) -> Citizen | None:
        """Get a citizen by name."""
        for citizen in self.citizens.values():
            if citizen.name.lower() == name.lower():
                return citizen
        return None

    def get_citizen_by_id(self, citizen_id: str) -> Citizen | None:
        """Get a citizen by ID."""
        return self.citizens.get(citizen_id)

    def get_citizens_in_region(self, region_name: str) -> list[Citizen]:
        """Get all citizens in a region."""
        return [c for c in self.citizens.values() if c.region == region_name]

    def are_co_located(self, *citizens: Citizen) -> bool:
        """Check if all citizens are in the same region."""
        if not citizens:
            return True
        regions = {c.region for c in citizens}
        return len(regions) == 1

    def are_adjacent(self, region_a: str, region_b: str) -> bool:
        """Check if two regions are adjacent."""
        if region_a not in self.regions:
            return False
        return self.regions[region_a].is_connected_to(region_b)

    def can_move(self, citizen: Citizen, to_region: str) -> bool:
        """Check if a citizen can move to a region."""
        if to_region not in self.regions:
            return False

        # Can always stay in current region
        if citizen.region == to_region:
            return True

        # Must be adjacent
        if not self.are_adjacent(citizen.region, to_region):
            return False

        # Check capacity
        target = self.regions[to_region]
        current_occupancy = len(self.get_citizens_in_region(to_region))
        return current_occupancy < target.capacity

    def move_citizen(self, citizen: Citizen, to_region: str) -> bool:
        """
        Move a citizen to a region.

        Returns True if successful, False if move is invalid.
        """
        if not self.can_move(citizen, to_region):
            return False
        citizen.move_to(to_region)
        return True

    def density_at(self, region_name: str) -> float:
        """
        Calculate density at a region.

        From Morton: Citizens are local thickenings of the mesh.
        Density is how much the mesh thickens at this point.
        """
        if region_name not in self.regions:
            return 0.0

        region = self.regions[region_name]
        occupancy = len(self.get_citizens_in_region(region_name))
        return occupancy / region.capacity

    def available_citizens(self) -> list[Citizen]:
        """Get all citizens available for interaction (not resting)."""
        return [c for c in self.citizens.values() if c.is_available]

    def resting_citizens(self) -> list[Citizen]:
        """Get all resting citizens."""
        return [c for c in self.citizens.values() if c.is_resting]

    def tension_index(self) -> float:
        """
        Calculate the tension index.

        Tension is the variance of relationship weights.
        High variance = drama; low variance = stability.
        """
        all_weights: list[float] = []
        for citizen in self.citizens.values():
            all_weights.extend(citizen.relationships.values())

        if not all_weights:
            return 0.0

        mean = sum(all_weights) / len(all_weights)
        variance = sum((w - mean) ** 2 for w in all_weights) / len(all_weights)
        return variance

    def cooperation_level(self) -> float:
        """
        Calculate the cooperation level.

        Sum of positive relationship weights.
        """
        total = 0.0
        for citizen in self.citizens.values():
            for weight in citizen.relationships.values():
                if weight > 0:
                    total += weight
        return total

    def total_accursed_surplus(self) -> float:
        """Total accumulated surplus across all citizens."""
        return sum(c.accursed_surplus for c in self.citizens.values())

    def __iter__(self) -> Iterator[Citizen]:
        """Iterate over all citizens."""
        return iter(self.citizens.values())

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "regions": {k: v.to_dict() for k, v in self.regions.items()},
            "citizens": {k: v.to_dict() for k, v in self.citizens.items()},
            "total_token_spend": self.total_token_spend,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TownEnvironment:
        """Deserialize from dictionary."""
        env = cls(name=data["name"])

        for region_data in data.get("regions", {}).values():
            env.add_region(Region.from_dict(region_data))

        for citizen_data in data.get("citizens", {}).values():
            env.add_citizen(Citizen.from_dict(citizen_data))

        env.total_token_spend = data.get("total_token_spend", 0)
        return env

    def to_yaml(self, path: str | Path | None = None) -> str:
        """
        Serialize environment to YAML.

        Args:
            path: Optional path to write to. If None, returns YAML string.

        Returns:
            YAML string representation.
        """
        # Build serializable data
        data = {
            "name": self.name,
            "version": "2.0.0",  # Phase 2 schema version
            "regions": [
                {
                    "name": r.name,
                    "description": r.description,
                    "connections": r.connections,
                    "capacity": r.capacity,
                    "properties": r.properties,
                }
                for r in self.regions.values()
            ],
            "citizens": [
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "initial_region": c.region,
                    "eigenvectors": c.eigenvectors.to_dict(),
                    "cosmotechnics": c.cosmotechnics.name,
                    "phase": c.phase.name,
                    "relationships": dict(c.relationships),
                    "accursed_surplus": c.accursed_surplus,
                }
                for c in self.citizens.values()
            ],
            "total_token_spend": self.total_token_spend,
        }

        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False)

        if path is not None:
            with open(path, "w") as f:
                f.write(yaml_content)

        return yaml_content

    @classmethod
    def from_yaml(cls, path: str | Path) -> TownEnvironment:
        """Load environment from YAML fixture file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        env = cls(name=data.get("name", "unnamed-town"))

        # Load regions
        for region_data in data.get("regions", []):
            env.add_region(Region.from_dict(region_data))

        # Map cosmotechnics
        cosmo_map: dict[str, Cosmotechnics] = {
            "gathering": GATHERING,
            "construction": CONSTRUCTION,
            "exploration": EXPLORATION,
            # Phase 2 cosmotechnics
            "healing": HEALING,
            "memory": MEMORY,
            "exchange": EXCHANGE,
            "cultivation": CULTIVATION,
        }

        # Import CitizenPhase for state restoration
        from agents.town.polynomial import CitizenPhase

        # Load citizens
        for citizen_data in data.get("citizens", []):
            eigenvectors = Eigenvectors.from_dict(citizen_data.get("eigenvectors", {}))
            cosmo = cosmo_map.get(
                citizen_data.get("cosmotechnics", "gathering"), GATHERING
            )

            # Parse phase if present
            phase_name = citizen_data.get("phase", "IDLE")
            phase = CitizenPhase[phase_name]

            citizen = Citizen(
                name=citizen_data["name"],
                archetype=citizen_data["archetype"],
                region=citizen_data.get("initial_region", list(env.regions.keys())[0]),
                eigenvectors=eigenvectors,
                cosmotechnics=cosmo,
                _phase=phase,
            )

            # Restore relationships (Phase 2)
            for other_id, weight in citizen_data.get("relationships", {}).items():
                citizen.relationships[other_id] = weight

            # Restore accursed surplus (Phase 2)
            citizen.accursed_surplus = citizen_data.get("accursed_surplus", 0.0)

            env.add_citizen(citizen)

        # Restore total token spend
        env.total_token_spend = data.get("total_token_spend", 0)

        return env

    def __repr__(self) -> str:
        return f"TownEnvironment({self.name}, {len(self.regions)} regions, {len(self.citizens)} citizens)"


# =============================================================================
# Factory Functions
# =============================================================================


def create_mpp_environment() -> TownEnvironment:
    """
    Create the MPP (Minimal Playable Prototype) environment.

    3 citizens, 2 regions.
    """
    env = TownEnvironment(name="smallville-mpp")

    # Add regions
    env.add_region(
        Region(
            name="inn",
            description="Alice's gathering place. Warm hearth, shared stories.",
            connections=["square"],
            capacity=10,
            properties={"warmth_bonus": 0.1, "is_shelter": True},
        )
    )
    env.add_region(
        Region(
            name="square",
            description="The town center. Open sky, chance encounters.",
            connections=["inn"],
            capacity=20,
            properties={"visibility": "high", "is_public": True},
        )
    )

    # Add citizens
    env.add_citizen(
        Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            eigenvectors=Eigenvectors(
                warmth=0.8, curiosity=0.6, trust=0.7, creativity=0.5, patience=0.6
            ),
            cosmotechnics=GATHERING,
        )
    )
    env.add_citizen(
        Citizen(
            name="Bob",
            archetype="Builder",
            region="square",
            eigenvectors=Eigenvectors(
                warmth=0.5, curiosity=0.4, trust=0.6, creativity=0.7, patience=0.3
            ),
            cosmotechnics=CONSTRUCTION,
        )
    )
    env.add_citizen(
        Citizen(
            name="Clara",
            archetype="Explorer",
            region="inn",
            eigenvectors=Eigenvectors(
                warmth=0.6, curiosity=0.9, trust=0.5, creativity=0.8, patience=0.4
            ),
            cosmotechnics=EXPLORATION,
        )
    )

    return env


def create_phase2_environment() -> TownEnvironment:
    """
    Create the Phase 2 environment.

    7 citizens, 5 regions.

    Phase 2 adds:
    - Citizens: Diana (healer), Eve (elder), Frank (merchant), Grace (gardener)
    - Regions: garden, market, library
    """
    env = TownEnvironment(name="smallville-phase2")

    # Add regions (5 total)
    env.add_region(
        Region(
            name="inn",
            description="Alice's gathering place. Warm hearth, shared stories.",
            connections=["square", "garden"],
            capacity=10,
            properties={"warmth_bonus": 0.1, "is_shelter": True},
        )
    )
    env.add_region(
        Region(
            name="square",
            description="The town center. Open sky, chance encounters.",
            connections=["inn", "market", "library"],
            capacity=20,
            properties={"visibility": "high", "is_public": True},
        )
    )
    env.add_region(
        Region(
            name="garden",
            description="Grace's cultivated space. Growth, patience, seasons.",
            connections=["inn", "library"],
            capacity=8,
            properties={"nature_bonus": 0.2, "healing_bonus": 0.1},
        )
    )
    env.add_region(
        Region(
            name="market",
            description="Frank's domain of exchange. Value, negotiation, surplus.",
            connections=["square"],
            capacity=15,
            properties={"trade_bonus": 0.2, "is_public": True},
        )
    )
    env.add_region(
        Region(
            name="library",
            description="Eve's repository of memory. Wisdom, silence, recall.",
            connections=["square", "garden"],
            capacity=6,
            properties={"memory_bonus": 0.2, "reflection_bonus": 0.1},
        )
    )

    # Add MPP citizens (3)
    env.add_citizen(
        Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            eigenvectors=Eigenvectors(
                warmth=0.8, curiosity=0.6, trust=0.7, creativity=0.5, patience=0.6
            ),
            cosmotechnics=GATHERING,
        )
    )
    env.add_citizen(
        Citizen(
            name="Bob",
            archetype="Builder",
            region="square",
            eigenvectors=Eigenvectors(
                warmth=0.5, curiosity=0.4, trust=0.6, creativity=0.7, patience=0.3
            ),
            cosmotechnics=CONSTRUCTION,
        )
    )
    env.add_citizen(
        Citizen(
            name="Clara",
            archetype="Explorer",
            region="inn",
            eigenvectors=Eigenvectors(
                warmth=0.6, curiosity=0.9, trust=0.5, creativity=0.8, patience=0.4
            ),
            cosmotechnics=EXPLORATION,
        )
    )

    # Add Phase 2 citizens (4)
    env.add_citizen(
        Citizen(
            name="Diana",
            archetype="Healer",
            region="garden",
            eigenvectors=Eigenvectors(
                warmth=0.7, curiosity=0.5, trust=0.8, creativity=0.4, patience=0.9
            ),
            cosmotechnics=HEALING,
        )
    )
    env.add_citizen(
        Citizen(
            name="Eve",
            archetype="Elder",
            region="library",
            eigenvectors=Eigenvectors(
                warmth=0.6, curiosity=0.7, trust=0.7, creativity=0.7, patience=0.8
            ),
            cosmotechnics=MEMORY,
        )
    )
    env.add_citizen(
        Citizen(
            name="Frank",
            archetype="Merchant",
            region="market",
            eigenvectors=Eigenvectors(
                warmth=0.5, curiosity=0.8, trust=0.4, creativity=0.6, patience=0.5
            ),
            cosmotechnics=EXCHANGE,
        )
    )
    env.add_citizen(
        Citizen(
            name="Grace",
            archetype="Gardener",
            region="garden",
            eigenvectors=Eigenvectors(
                warmth=0.8, curiosity=0.4, trust=0.7, creativity=0.5, patience=0.9
            ),
            cosmotechnics=CULTIVATION,
        )
    )

    return env


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "Region",
    "TownEnvironment",
    "create_mpp_environment",
    "create_phase2_environment",
]
