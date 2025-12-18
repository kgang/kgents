"""
Tests for Citizen class.

Verifies:
- Eigenvector initialization
- State transitions
- Memory operations
- Relationships
- Manifestation at different LODs
"""

from __future__ import annotations

import pytest

from agents.town.citizen import (
    CONSTRUCTION,
    EXPLORATION,
    GATHERING,
    Citizen,
    Cosmotechnics,
    Eigenvectors,
)
from agents.town.polynomial import CitizenPhase


class TestEigenvectors:
    """Test Eigenvectors dataclass."""

    def test_default_values(self) -> None:
        """Default values are 0.5."""
        ev = Eigenvectors()
        assert ev.warmth == 0.5
        assert ev.curiosity == 0.5
        assert ev.trust == 0.5
        assert ev.creativity == 0.5
        assert ev.patience == 0.5

    def test_custom_values(self) -> None:
        """Custom values are preserved."""
        ev = Eigenvectors(warmth=0.8, curiosity=0.9)
        assert ev.warmth == 0.8
        assert ev.curiosity == 0.9

    def test_clamping_high(self) -> None:
        """Values above 1 are clamped."""
        ev = Eigenvectors(warmth=1.5)
        assert ev.warmth == 1.0

    def test_clamping_low(self) -> None:
        """Values below 0 are clamped."""
        ev = Eigenvectors(warmth=-0.5)
        assert ev.warmth == 0.0

    def test_to_dict(self) -> None:
        """Serialization works."""
        ev = Eigenvectors(warmth=0.8, curiosity=0.6)
        d = ev.to_dict()
        assert d["warmth"] == 0.8
        assert d["curiosity"] == 0.6

    def test_from_dict(self) -> None:
        """Deserialization works."""
        d = {"warmth": 0.7, "trust": 0.9}
        ev = Eigenvectors.from_dict(d)
        assert ev.warmth == 0.7
        assert ev.trust == 0.9
        assert ev.curiosity == 0.5  # Default


class TestCosmotechnics:
    """Test Cosmotechnics types."""

    def test_gathering(self) -> None:
        """GATHERING cosmotechnics is defined."""
        assert GATHERING.name == "gathering"
        assert "congregation" in GATHERING.description.lower()

    def test_construction(self) -> None:
        """CONSTRUCTION cosmotechnics is defined."""
        assert CONSTRUCTION.name == "construction"
        assert "building" in CONSTRUCTION.description.lower()

    def test_exploration(self) -> None:
        """EXPLORATION cosmotechnics is defined."""
        assert EXPLORATION.name == "exploration"
        assert "discovery" in EXPLORATION.description.lower()

    def test_opacity_statement(self) -> None:
        """Each cosmotechnics has opacity statement."""
        assert GATHERING.opacity_statement
        assert CONSTRUCTION.opacity_statement
        assert EXPLORATION.opacity_statement


class TestCitizen:
    """Test Citizen class."""

    def test_basic_creation(self) -> None:
        """Can create a citizen."""
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
        )
        assert citizen.name == "Alice"
        assert citizen.archetype == "Innkeeper"
        assert citizen.region == "inn"

    def test_default_phase(self) -> None:
        """Default phase is IDLE."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert citizen.phase == CitizenPhase.IDLE

    def test_default_eigenvectors(self) -> None:
        """Has default eigenvectors."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert citizen.eigenvectors.warmth == 0.5

    def test_custom_eigenvectors(self) -> None:
        """Can set custom eigenvectors."""
        ev = Eigenvectors(warmth=0.9, curiosity=0.3)
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            eigenvectors=ev,
        )
        assert citizen.eigenvectors.warmth == 0.9

    def test_default_cosmotechnics(self) -> None:
        """Has default cosmotechnics (GATHERING)."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert citizen.cosmotechnics == GATHERING

    def test_custom_cosmotechnics(self) -> None:
        """Can set custom cosmotechnics."""
        citizen = Citizen(
            name="Bob",
            archetype="Builder",
            region="square",
            cosmotechnics=CONSTRUCTION,
        )
        assert citizen.cosmotechnics == CONSTRUCTION

    def test_has_id(self) -> None:
        """Has unique ID."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert citizen.id
        assert len(citizen.id) == 8

    def test_unique_ids(self) -> None:
        """Different citizens have different IDs."""
        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")
        assert alice.id != bob.id


class TestCitizenTransitions:
    """Test citizen state transitions."""

    def test_greet(self) -> None:
        """Greet transitions to SOCIALIZING."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        output = citizen.greet("bob")

        assert citizen.phase == CitizenPhase.SOCIALIZING
        assert output.success

    def test_work(self) -> None:
        """Work transitions to WORKING."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        output = citizen.work("cleaning")

        assert citizen.phase == CitizenPhase.WORKING
        assert output.success

    def test_reflect(self) -> None:
        """Reflect transitions to REFLECTING."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        output = citizen.reflect("life")

        assert citizen.phase == CitizenPhase.REFLECTING
        assert output.success

    def test_rest(self) -> None:
        """Rest transitions to RESTING."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        output = citizen.rest()

        assert citizen.phase == CitizenPhase.RESTING
        assert citizen.is_resting
        assert not citizen.is_available
        assert output.success

    def test_wake(self) -> None:
        """Wake transitions from RESTING to IDLE."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.rest()
        output = citizen.wake()

        assert citizen.phase == CitizenPhase.IDLE
        assert not citizen.is_resting
        assert citizen.is_available
        assert output.success


class TestCitizenRelationships:
    """Test relationship management."""

    def test_default_no_relationships(self) -> None:
        """No relationships by default."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert len(citizen.relationships) == 0

    def test_update_relationship(self) -> None:
        """Can update relationship."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.update_relationship("bob", 0.3)

        assert citizen.get_relationship("bob") == 0.3

    def test_relationship_clamping(self) -> None:
        """Relationships are clamped to [-1, 1]."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.update_relationship("bob", 1.5)
        assert citizen.get_relationship("bob") == 1.0

        citizen.update_relationship("bob", -2.0)
        assert citizen.get_relationship("bob") == -1.0

    def test_relationship_accumulation(self) -> None:
        """Relationships accumulate."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.update_relationship("bob", 0.3)
        citizen.update_relationship("bob", 0.2)

        assert citizen.get_relationship("bob") == 0.5


class TestCitizenAccursedShare:
    """Test accursed surplus (Bataille)."""

    def test_default_zero_surplus(self) -> None:
        """Surplus starts at 0."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        assert citizen.accursed_surplus == 0.0

    def test_accumulate_surplus(self) -> None:
        """Can accumulate surplus."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.accumulate_surplus(5.0)

        assert citizen.accursed_surplus == 5.0

    def test_spend_surplus(self) -> None:
        """Can spend surplus."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.accumulate_surplus(5.0)
        spent = citizen.spend_surplus(3.0)

        assert spent == 3.0
        assert citizen.accursed_surplus == 2.0

    def test_spend_surplus_capped(self) -> None:
        """Cannot spend more than available."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.accumulate_surplus(2.0)
        spent = citizen.spend_surplus(5.0)

        assert spent == 2.0
        assert citizen.accursed_surplus == 0.0


class TestCitizenManifest:
    """Test manifestation at different LODs."""

    def test_lod_0(self) -> None:
        """LOD 0: silhouette."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        m = citizen.manifest(0)

        assert m["name"] == "Alice"
        assert m["region"] == "inn"
        assert m["phase"] == "IDLE"
        assert "archetype" not in m

    def test_lod_1(self) -> None:
        """LOD 1: posture."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        m = citizen.manifest(1)

        assert m["archetype"] == "Innkeeper"
        assert "mood" in m

    def test_lod_2(self) -> None:
        """LOD 2: dialogue."""
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            cosmotechnics=GATHERING,
        )
        m = citizen.manifest(2)

        assert m["cosmotechnics"] == "gathering"
        assert m["metaphor"] == "Life is a gathering"

    def test_lod_3(self) -> None:
        """LOD 3: memory."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.update_relationship("bob", 0.5)
        m = citizen.manifest(3)

        assert "eigenvectors" in m
        assert "relationships" in m
        assert "bob" in m["relationships"]

    def test_lod_4(self) -> None:
        """LOD 4: psyche."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        citizen.accumulate_surplus(5.0)
        m = citizen.manifest(4)

        assert m["accursed_surplus"] == 5.0
        assert "id" in m

    def test_lod_5(self) -> None:
        """LOD 5: abyss (opacity)."""
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            cosmotechnics=GATHERING,
        )
        m = citizen.manifest(5)

        assert "opacity" in m
        assert m["opacity"]["statement"] == GATHERING.opacity_statement
        assert "irreducible" in m["opacity"]["message"].lower()


class TestCitizenSerialization:
    """Test serialization/deserialization."""

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            cosmotechnics=GATHERING,
        )
        d = citizen.to_dict()

        assert d["name"] == "Alice"
        assert d["archetype"] == "Innkeeper"
        assert d["region"] == "inn"
        assert d["cosmotechnics"] == "gathering"

    def test_from_dict(self) -> None:
        """Can deserialize from dict."""
        d = {
            "name": "Alice",
            "archetype": "Innkeeper",
            "region": "inn",
            "eigenvectors": {"warmth": 0.8},
            "cosmotechnics": "gathering",
            "phase": "IDLE",
        }
        citizen = Citizen.from_dict(d)

        assert citizen.name == "Alice"
        assert citizen.eigenvectors.warmth == 0.8

    def test_roundtrip(self) -> None:
        """Serialization roundtrips."""
        original = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            eigenvectors=Eigenvectors(warmth=0.8, curiosity=0.6),
            cosmotechnics=CONSTRUCTION,
        )
        original.update_relationship("bob", 0.5)

        d = original.to_dict()
        restored = Citizen.from_dict(d)

        assert restored.name == original.name
        assert restored.eigenvectors.warmth == original.eigenvectors.warmth
        assert restored.get_relationship("bob") == original.get_relationship("bob")
