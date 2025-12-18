"""Tests for Phase 4 archetypes."""

import pytest

from agents.town.archetypes import (
    ARCHETYPE_FACTORIES,
    ARCHETYPE_SPECS,
    BUILDER_SPEC,
    HEALER_SPEC,
    SCHOLAR_SPEC,
    TRADER_SPEC,
    WATCHER_SPEC,
    ArchetypeKind,
    create_archetype,
    create_builder,
    create_healer,
    create_scholar,
    create_trader,
    create_watcher,
)
from agents.town.citizen import (
    CONSTRUCTION_V2,
    EXCHANGE_V2,
    MEMORY_V2,
    RESTORATION,
    SYNTHESIS_V2,
)
from agents.town.evolving import EvolvingCitizen


class TestArchetypeSpecs:
    """Tests for archetype specifications."""

    def test_all_archetypes_have_specs(self) -> None:
        """All archetype kinds should have specifications."""
        for kind in ArchetypeKind:
            assert kind in ARCHETYPE_SPECS

    def test_builder_spec_biases(self) -> None:
        """Builder should have creativity, patience, resilience, ambition biases."""
        spec = BUILDER_SPEC
        assert spec.creativity_bias > 0
        assert spec.patience_bias > 0
        assert spec.resilience_bias > 0
        assert spec.ambition_bias > 0
        assert spec.cosmotechnics == CONSTRUCTION_V2

    def test_trader_spec_biases(self) -> None:
        """Trader should have curiosity, ambition up and trust down."""
        spec = TRADER_SPEC
        assert spec.curiosity_bias > 0
        assert spec.ambition_bias > 0
        assert spec.trust_bias < 0  # Cautious
        assert spec.cosmotechnics == EXCHANGE_V2

    def test_healer_spec_biases(self) -> None:
        """Healer should have warmth, patience, trust, resilience biases."""
        spec = HEALER_SPEC
        assert spec.warmth_bias > 0
        assert spec.patience_bias > 0
        assert spec.trust_bias > 0
        assert spec.resilience_bias > 0
        assert spec.cosmotechnics == RESTORATION

    def test_scholar_spec_biases(self) -> None:
        """Scholar should have high curiosity, patience, creativity."""
        spec = SCHOLAR_SPEC
        assert spec.curiosity_bias >= 0.3  # Very curious
        assert spec.patience_bias > 0
        assert spec.creativity_bias > 0
        assert spec.cosmotechnics == SYNTHESIS_V2

    def test_watcher_spec_biases(self) -> None:
        """Watcher should have patience, trust, resilience biases."""
        spec = WATCHER_SPEC
        assert spec.patience_bias > 0
        assert spec.trust_bias > 0
        assert spec.resilience_bias > 0
        assert spec.cosmotechnics == MEMORY_V2

    def test_eigenvectors_from_spec(self) -> None:
        """Spec should create eigenvectors with biases applied."""
        spec = SCHOLAR_SPEC
        ev = spec.create_eigenvectors()

        # Should be biased from 0.5 baseline
        assert ev.curiosity > 0.5
        assert ev.patience > 0.5
        # All values should be clamped
        for attr in [
            "warmth",
            "curiosity",
            "trust",
            "creativity",
            "patience",
            "resilience",
            "ambition",
        ]:
            val = getattr(ev, attr)
            assert 0.0 <= val <= 1.0


class TestArchetypeFactories:
    """Tests for archetype factory functions."""

    def test_all_archetypes_have_factories(self) -> None:
        """All archetype kinds should have factory functions."""
        for kind in ArchetypeKind:
            assert kind in ARCHETYPE_FACTORIES

    def test_create_builder(self) -> None:
        """create_builder should create Builder citizen."""
        citizen = create_builder("TestBuilder", "square")
        assert citizen.name == "TestBuilder"
        assert citizen.archetype == "Builder"
        assert citizen.region == "square"
        assert citizen.cosmotechnics == CONSTRUCTION_V2

    def test_create_trader(self) -> None:
        """create_trader should create Trader citizen."""
        citizen = create_trader("TestTrader", "market")
        assert citizen.name == "TestTrader"
        assert citizen.archetype == "Trader"
        assert citizen.cosmotechnics == EXCHANGE_V2

    def test_create_healer(self) -> None:
        """create_healer should create Healer citizen."""
        citizen = create_healer("TestHealer", "garden")
        assert citizen.name == "TestHealer"
        assert citizen.archetype == "Healer"
        assert citizen.cosmotechnics == RESTORATION

    def test_create_scholar(self) -> None:
        """create_scholar should create Scholar citizen."""
        citizen = create_scholar("TestScholar", "library")
        assert citizen.name == "TestScholar"
        assert citizen.archetype == "Scholar"
        assert citizen.cosmotechnics == SYNTHESIS_V2

    def test_create_watcher(self) -> None:
        """create_watcher should create Watcher citizen."""
        citizen = create_watcher("TestWatcher", "observatory")
        assert citizen.name == "TestWatcher"
        assert citizen.archetype == "Watcher"
        assert citizen.cosmotechnics == MEMORY_V2

    def test_create_evolving_builder(self) -> None:
        """create_builder with evolving=True should create EvolvingCitizen."""
        citizen = create_builder("EvolvingBuilder", "square", evolving=True)
        assert isinstance(citizen, EvolvingCitizen)
        assert citizen.archetype == "Builder"

    def test_create_archetype_generic(self) -> None:
        """create_archetype should dispatch to correct factory."""
        citizen = create_archetype(ArchetypeKind.HEALER, "GenericHealer", "garden")
        assert citizen.archetype == "Healer"
        assert citizen.cosmotechnics == RESTORATION

    def test_eigenvector_overrides(self) -> None:
        """Factory should apply eigenvector overrides."""
        citizen = create_builder(
            "ModifiedBuilder",
            "square",
            eigenvector_overrides={"warmth": 0.3},
        )
        # Should have warmth increased from baseline
        assert citizen.eigenvectors.warmth > 0.5


class TestEigenvectorProperties:
    """Tests for 7D eigenvector properties."""

    def test_7d_eigenvectors(self) -> None:
        """All archetypes should create citizens with 7D eigenvectors."""
        citizen = create_scholar("TestScholar", "library")
        ev = citizen.eigenvectors

        # All 7 dimensions should exist
        assert hasattr(ev, "warmth")
        assert hasattr(ev, "curiosity")
        assert hasattr(ev, "trust")
        assert hasattr(ev, "creativity")
        assert hasattr(ev, "patience")
        assert hasattr(ev, "resilience")
        assert hasattr(ev, "ambition")

    def test_drift_calculation(self) -> None:
        """Eigenvector drift should calculate L2 distance."""
        builder = create_builder("B1", "square")
        healer = create_healer("H1", "garden")

        drift = builder.eigenvectors.drift(healer.eigenvectors)
        assert drift > 0  # Different archetypes should have different eigenvectors

        # Self-drift should be 0 (identity)
        assert builder.eigenvectors.drift(builder.eigenvectors) == 0.0

    def test_similarity_calculation(self) -> None:
        """Eigenvector similarity should calculate cosine similarity."""
        builder1 = create_builder("B1", "square")
        builder2 = create_builder("B2", "square")

        # Same archetype should have high similarity
        sim = builder1.eigenvectors.similarity(builder2.eigenvectors)
        assert sim > 0.9  # Very similar

        # Different archetypes should have lower similarity
        healer = create_healer("H1", "garden")
        cross_sim = builder1.eigenvectors.similarity(healer.eigenvectors)
        assert cross_sim < sim  # Less similar than same archetype

    def test_apply_bounded_drift(self) -> None:
        """apply_bounded_drift should respect max_drift."""
        citizen = create_builder("B1", "square")
        original = citizen.eigenvectors

        # Apply large drift
        new_ev = original.apply_bounded_drift({"warmth": 1.0}, max_drift=0.1)

        # Should only drift by max_drift
        assert abs(new_ev.warmth - original.warmth) <= 0.1 + 0.001  # Float tolerance


class TestArchetypeDistribution:
    """Tests for archetype distribution properties."""

    def test_archetypes_have_distinct_biases(self) -> None:
        """Each archetype should have distinct eigenvector profiles."""
        profiles = {}
        for kind in ArchetypeKind:
            citizen = create_archetype(kind, f"Test{kind.name}", "square")
            profiles[kind] = citizen.eigenvectors

        # All pairs should be different
        kinds = list(ArchetypeKind)
        for i, kind1 in enumerate(kinds):
            for kind2 in kinds[i + 1 :]:
                drift = profiles[kind1].drift(profiles[kind2])
                assert drift > 0.01, f"{kind1} and {kind2} should be distinct"

    def test_archetype_cosmotechnics_unique(self) -> None:
        """Each archetype should have unique cosmotechnics."""
        cosmotechnics = set()
        for kind in ArchetypeKind:
            spec = ARCHETYPE_SPECS[kind]
            assert spec.cosmotechnics.name not in cosmotechnics
            cosmotechnics.add(spec.cosmotechnics.name)
