"""
Tests for TownEnvironment.

Verifies:
- Region management
- Citizen placement
- Adjacency and movement
- Metrics calculation
"""

from __future__ import annotations

import pytest

from agents.town.citizen import (
    CONSTRUCTION,
    CULTIVATION,
    EXCHANGE,
    EXPLORATION,
    GATHERING,
    HEALING,
    MEMORY,
    Citizen,
    Eigenvectors,
)
from agents.town.environment import (
    Region,
    TownEnvironment,
    create_mpp_environment,
    create_phase2_environment,
)


class TestRegion:
    """Test Region class."""

    def test_basic_creation(self) -> None:
        """Can create a region."""
        region = Region(name="inn", description="A cozy inn")
        assert region.name == "inn"
        assert region.description == "A cozy inn"

    def test_default_capacity(self) -> None:
        """Default capacity is 10."""
        region = Region(name="inn")
        assert region.capacity == 10

    def test_connections(self) -> None:
        """Can have connections."""
        region = Region(name="inn", connections=["square", "garden"])
        assert "square" in region.connections
        assert "garden" in region.connections

    def test_is_connected_to(self) -> None:
        """Can check connections."""
        region = Region(name="inn", connections=["square"])
        assert region.is_connected_to("square")
        assert not region.is_connected_to("garden")

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        region = Region(name="inn", connections=["square"], capacity=15)
        d = region.to_dict()

        assert d["name"] == "inn"
        assert d["capacity"] == 15
        assert "square" in d["connections"]

    def test_from_dict(self) -> None:
        """Can deserialize from dict."""
        d = {
            "name": "inn",
            "description": "Cozy",
            "connections": ["square"],
            "capacity": 20,
        }
        region = Region.from_dict(d)

        assert region.name == "inn"
        assert region.capacity == 20


class TestTownEnvironment:
    """Test TownEnvironment class."""

    def test_basic_creation(self) -> None:
        """Can create an environment."""
        env = TownEnvironment(name="test-town")
        assert env.name == "test-town"

    def test_add_region(self) -> None:
        """Can add regions."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn"))

        assert "inn" in env.regions
        assert env.regions["inn"].name == "inn"

    def test_add_citizen(self) -> None:
        """Can add citizens."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn"))
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        assert citizen.id in env.citizens

    def test_get_citizen_by_name(self) -> None:
        """Can get citizen by name."""
        env = TownEnvironment(name="test-town")
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        found = env.get_citizen_by_name("Alice")
        assert found is citizen

        found = env.get_citizen_by_name("alice")  # Case-insensitive
        assert found is citizen

    def test_get_citizens_in_region(self) -> None:
        """Can get citizens in a region."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn"))
        env.add_region(Region(name="square"))

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        clara = Citizen(name="Clara", archetype="Explorer", region="inn")

        env.add_citizen(alice)
        env.add_citizen(bob)
        env.add_citizen(clara)

        inn_citizens = env.get_citizens_in_region("inn")
        assert len(inn_citizens) == 2
        assert alice in inn_citizens
        assert clara in inn_citizens
        assert bob not in inn_citizens


class TestCoLocation:
    """Test co-location checks."""

    def test_are_co_located_same_region(self) -> None:
        """Citizens in same region are co-located."""
        env = TownEnvironment(name="test-town")
        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="inn")
        env.add_citizen(alice)
        env.add_citizen(bob)

        assert env.are_co_located(alice, bob)

    def test_are_co_located_different_regions(self) -> None:
        """Citizens in different regions are not co-located."""
        env = TownEnvironment(name="test-town")
        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        env.add_citizen(alice)
        env.add_citizen(bob)

        assert not env.are_co_located(alice, bob)

    def test_are_co_located_empty(self) -> None:
        """Empty list is co-located (trivially true)."""
        env = TownEnvironment(name="test-town")
        assert env.are_co_located()


class TestAdjacency:
    """Test region adjacency."""

    def test_are_adjacent(self) -> None:
        """Connected regions are adjacent."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=["square"]))
        env.add_region(Region(name="square", connections=["inn"]))

        assert env.are_adjacent("inn", "square")
        assert env.are_adjacent("square", "inn")

    def test_not_adjacent(self) -> None:
        """Unconnected regions are not adjacent."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=[]))
        env.add_region(Region(name="garden", connections=[]))

        assert not env.are_adjacent("inn", "garden")


class TestMovement:
    """Test citizen movement."""

    def test_can_move_to_adjacent(self) -> None:
        """Can move to adjacent region."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=["square"]))
        env.add_region(Region(name="square", connections=["inn"]))

        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        assert env.can_move(citizen, "square")

    def test_cannot_move_to_non_adjacent(self) -> None:
        """Cannot move to non-adjacent region."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=["square"]))
        env.add_region(Region(name="square", connections=["inn"]))
        env.add_region(Region(name="garden", connections=[]))

        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        assert not env.can_move(citizen, "garden")

    def test_move_citizen(self) -> None:
        """Move citizen changes their region."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=["square"]))
        env.add_region(Region(name="square", connections=["inn"]))

        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        success = env.move_citizen(citizen, "square")

        assert success
        assert citizen.region == "square"

    def test_move_respects_capacity(self) -> None:
        """Cannot move to full region."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", connections=["square"]))
        env.add_region(Region(name="square", connections=["inn"], capacity=1))

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        env.add_citizen(alice)
        env.add_citizen(bob)

        # Square is at capacity (1)
        assert not env.can_move(alice, "square")


class TestDensity:
    """Test density calculation."""

    def test_density_empty(self) -> None:
        """Empty region has 0 density."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", capacity=10))

        assert env.density_at("inn") == 0.0

    def test_density_half(self) -> None:
        """Half-full region has 0.5 density."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", capacity=2))

        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        assert env.density_at("inn") == 0.5

    def test_density_full(self) -> None:
        """Full region has 1.0 density."""
        env = TownEnvironment(name="test-town")
        env.add_region(Region(name="inn", capacity=2))

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="inn")
        env.add_citizen(alice)
        env.add_citizen(bob)

        assert env.density_at("inn") == 1.0


class TestMetrics:
    """Test environment metrics."""

    def test_tension_index_no_relationships(self) -> None:
        """No relationships means 0 tension."""
        env = TownEnvironment(name="test-town")
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        env.add_citizen(citizen)

        assert env.tension_index() == 0.0

    def test_cooperation_level(self) -> None:
        """Positive relationships contribute to cooperation."""
        env = TownEnvironment(name="test-town")
        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        alice.update_relationship("bob", 0.5)
        alice.update_relationship("clara", 0.3)
        env.add_citizen(alice)

        assert env.cooperation_level() == 0.8

    def test_total_accursed_surplus(self) -> None:
        """Sums surplus across citizens."""
        env = TownEnvironment(name="test-town")

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        alice.accumulate_surplus(3.0)
        env.add_citizen(alice)

        bob = Citizen(name="Bob", archetype="Builder", region="square")
        bob.accumulate_surplus(2.0)
        env.add_citizen(bob)

        assert env.total_accursed_surplus() == 5.0


class TestAvailability:
    """Test citizen availability filtering."""

    def test_available_citizens(self) -> None:
        """Returns only non-resting citizens."""
        env = TownEnvironment(name="test-town")

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        bob.rest()

        env.add_citizen(alice)
        env.add_citizen(bob)

        available = env.available_citizens()
        assert alice in available
        assert bob not in available

    def test_resting_citizens(self) -> None:
        """Returns only resting citizens."""
        env = TownEnvironment(name="test-town")

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        bob.rest()

        env.add_citizen(alice)
        env.add_citizen(bob)

        resting = env.resting_citizens()
        assert bob in resting
        assert alice not in resting


class TestMPPEnvironment:
    """Test MPP environment factory."""

    def test_create_mpp_environment(self) -> None:
        """Creates valid MPP environment."""
        env = create_mpp_environment()

        assert env.name == "smallville-mpp"
        assert len(env.regions) == 2
        assert len(env.citizens) == 3

    def test_mpp_regions(self) -> None:
        """MPP has correct regions."""
        env = create_mpp_environment()

        assert "inn" in env.regions
        assert "square" in env.regions
        assert env.are_adjacent("inn", "square")

    def test_mpp_citizens(self) -> None:
        """MPP has correct citizens."""
        env = create_mpp_environment()

        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        clara = env.get_citizen_by_name("Clara")

        assert alice is not None
        assert bob is not None
        assert clara is not None

        assert alice.archetype == "Innkeeper"
        assert bob.archetype == "Builder"
        assert clara.archetype == "Explorer"

    def test_mpp_cosmotechnics(self) -> None:
        """MPP citizens have distinct cosmotechnics."""
        env = create_mpp_environment()

        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert bob is not None
        assert clara is not None

        assert alice.cosmotechnics == GATHERING
        assert bob.cosmotechnics == CONSTRUCTION
        assert clara.cosmotechnics == EXPLORATION


class TestSerialization:
    """Test environment serialization."""

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        env = create_mpp_environment()
        d = env.to_dict()

        assert d["name"] == "smallville-mpp"
        assert "regions" in d
        assert "citizens" in d

    def test_from_dict_roundtrip(self) -> None:
        """Can roundtrip through dict."""
        original = create_mpp_environment()
        d = original.to_dict()
        restored = TownEnvironment.from_dict(d)

        assert restored.name == original.name
        assert len(restored.regions) == len(original.regions)
        assert len(restored.citizens) == len(original.citizens)


class TestPhase2Environment:
    """Test Phase 2 environment factory."""

    def test_create_phase2_environment(self) -> None:
        """Creates valid Phase 2 environment."""
        env = create_phase2_environment()

        assert env.name == "smallville-phase2"
        assert len(env.regions) == 5
        assert len(env.citizens) == 7

    def test_phase2_regions(self) -> None:
        """Phase 2 has correct regions with adjacency."""
        env = create_phase2_environment()

        # All 5 regions exist
        assert "inn" in env.regions
        assert "square" in env.regions
        assert "garden" in env.regions
        assert "market" in env.regions
        assert "library" in env.regions

        # Check adjacency graph
        assert env.are_adjacent("inn", "square")
        assert env.are_adjacent("inn", "garden")
        assert env.are_adjacent("square", "market")
        assert env.are_adjacent("square", "library")
        assert env.are_adjacent("garden", "library")

    def test_phase2_citizens(self) -> None:
        """Phase 2 has correct citizens."""
        env = create_phase2_environment()

        # MPP citizens
        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        clara = env.get_citizen_by_name("Clara")

        # Phase 2 citizens
        diana = env.get_citizen_by_name("Diana")
        eve = env.get_citizen_by_name("Eve")
        frank = env.get_citizen_by_name("Frank")
        grace = env.get_citizen_by_name("Grace")

        # All exist
        assert alice is not None
        assert bob is not None
        assert clara is not None
        assert diana is not None
        assert eve is not None
        assert frank is not None
        assert grace is not None

        # Check archetypes
        assert alice.archetype == "Innkeeper"
        assert bob.archetype == "Builder"
        assert clara.archetype == "Explorer"
        assert diana.archetype == "Healer"
        assert eve.archetype == "Elder"
        assert frank.archetype == "Merchant"
        assert grace.archetype == "Gardener"

    def test_phase2_cosmotechnics(self) -> None:
        """Phase 2 citizens have correct cosmotechnics."""
        env = create_phase2_environment()

        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        clara = env.get_citizen_by_name("Clara")
        diana = env.get_citizen_by_name("Diana")
        eve = env.get_citizen_by_name("Eve")
        frank = env.get_citizen_by_name("Frank")
        grace = env.get_citizen_by_name("Grace")

        # Assert all citizens exist
        assert alice is not None
        assert bob is not None
        assert clara is not None
        assert diana is not None
        assert eve is not None
        assert frank is not None
        assert grace is not None

        # MPP cosmotechnics
        assert alice.cosmotechnics == GATHERING
        assert bob.cosmotechnics == CONSTRUCTION
        assert clara.cosmotechnics == EXPLORATION

        # Phase 2 cosmotechnics
        assert diana.cosmotechnics == HEALING
        assert eve.cosmotechnics == MEMORY
        assert frank.cosmotechnics == EXCHANGE
        assert grace.cosmotechnics == CULTIVATION

    def test_phase2_citizen_locations(self) -> None:
        """Phase 2 citizens start in correct locations."""
        env = create_phase2_environment()

        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        clara = env.get_citizen_by_name("Clara")
        diana = env.get_citizen_by_name("Diana")
        eve = env.get_citizen_by_name("Eve")
        frank = env.get_citizen_by_name("Frank")
        grace = env.get_citizen_by_name("Grace")

        # Assert all citizens exist
        assert alice is not None
        assert bob is not None
        assert clara is not None
        assert diana is not None
        assert eve is not None
        assert frank is not None
        assert grace is not None

        assert alice.region == "inn"
        assert bob.region == "square"
        assert clara.region == "inn"
        assert diana.region == "garden"
        assert eve.region == "library"
        assert frank.region == "market"
        assert grace.region == "garden"

    def test_phase2_roundtrip(self) -> None:
        """Phase 2 environment can roundtrip through dict."""
        original = create_phase2_environment()
        d = original.to_dict()
        restored = TownEnvironment.from_dict(d)

        assert restored.name == original.name
        assert len(restored.regions) == 5
        assert len(restored.citizens) == 7
