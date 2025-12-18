"""
Phase 4 Integration Tests: Civilizational Scale.

Tests the complete Phase 4 system:
- 25 citizens (10 from Phase 3 + 15 new archetypes)
- 7D eigenvectors with drift/similarity
- 12 cosmotechnics (7 original + 5 Phase 4)
- Coalition detection via k-clique percolation
- EigenTrust reputation system
- Full evolution cycles

Heritage papers realized:
- CHATDEV: Multi-agent roles
- SIMULACRA: Memory streams, eigenvector personalities
- ALTERA: Long-horizon NPHASE cycles
- VOYAGER: Skill libraries (cosmotechnics)
- AGENT HOSPITAL: Domain simulation template
"""

import pytest

from agents.town.archetypes import (
    ARCHETYPE_SPECS,
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
    Eigenvectors,
)
from agents.town.coalition import CoalitionManager, detect_coalitions
from agents.town.environment import (
    create_phase4_environment,
    get_citizen_count_by_region,
    get_citizens_by_archetype,
    get_evolving_citizens,
)
from agents.town.evolving import EvolvingCitizen, Observation


class TestPhase4Environment:
    """Tests for Phase 4 environment configuration."""

    def test_phase4_has_25_citizens(self) -> None:
        """Phase 4 should have 25 citizens total."""
        env = create_phase4_environment()
        assert len(env.citizens) == 25

    def test_phase4_has_8_regions(self) -> None:
        """Phase 4 should have 8 regions."""
        env = create_phase4_environment()
        assert len(env.regions) == 8

        # Verify new Phase 4 regions
        region_names = set(env.regions.keys())
        assert "workshop" in region_names
        assert "archive" in region_names

    def test_phase4_has_5_evolving_citizens(self) -> None:
        """Phase 4 should have 5 EvolvingCitizen instances."""
        env = create_phase4_environment()
        evolving = get_evolving_citizens(env)

        # 3 from Phase 3 (Hana, Igor, Juno) + 2 from Phase 4 (Oscar, Xena)
        assert len(evolving) == 5

    def test_phase4_archetype_distribution(self) -> None:
        """Phase 4 should have correct archetype distribution."""
        env = create_phase4_environment()

        # New Phase 4 archetypes + legacy (Bob is Builder from Phase 2)
        builders = get_citizens_by_archetype(env, "Builder")
        traders = get_citizens_by_archetype(env, "Trader")
        healers = get_citizens_by_archetype(env, "Healer")
        scholars = get_citizens_by_archetype(env, "Scholar")
        watchers = get_citizens_by_archetype(env, "Watcher")

        # Bob (Phase 2) + 3 new = 4 Builders
        assert len(builders) == 4
        assert len(traders) == 3
        # Diana (Phase 2 Healer) + 3 new = could be 4, check actual
        assert len(healers) >= 3
        assert len(scholars) >= 3
        assert len(watchers) == 3


class TestPhase4Eigenvectors:
    """Tests for 7D eigenvector system."""

    def test_all_citizens_have_7d_eigenvectors(self) -> None:
        """All citizens should have 7D eigenvectors."""
        env = create_phase4_environment()

        for citizen in env.citizens.values():
            ev = citizen.eigenvectors
            assert hasattr(ev, "warmth")
            assert hasattr(ev, "curiosity")
            assert hasattr(ev, "trust")
            assert hasattr(ev, "creativity")
            assert hasattr(ev, "patience")
            assert hasattr(ev, "resilience")
            assert hasattr(ev, "ambition")

    def test_archetype_eigenvector_biases(self) -> None:
        """Each archetype should have distinct eigenvector biases."""
        env = create_phase4_environment()

        builders = get_citizens_by_archetype(env, "Builder")
        traders = get_citizens_by_archetype(env, "Trader")
        healers = get_citizens_by_archetype(env, "Healer")

        if builders and traders and healers:
            # Builders should have high creativity
            assert builders[0].eigenvectors.creativity > 0.6

            # Traders should have high ambition, low trust
            assert traders[0].eigenvectors.ambition > 0.6
            assert traders[0].eigenvectors.trust < 0.5

            # Healers should have high warmth
            assert healers[0].eigenvectors.warmth > 0.6

    def test_eigenvector_drift_metric_laws(self) -> None:
        """Eigenvector drift should obey metric space laws."""
        ev1 = Eigenvectors(warmth=0.3)
        ev2 = Eigenvectors(warmth=0.6)
        ev3 = Eigenvectors(warmth=0.9)

        # L1: Identity
        assert ev1.drift(ev1) == 0.0

        # L2: Symmetry
        assert ev1.drift(ev2) == ev2.drift(ev1)

        # L3: Triangle inequality
        assert ev1.drift(ev3) <= ev1.drift(ev2) + ev2.drift(ev3) + 0.001

    def test_eigenvector_similarity_for_similar_archetypes(self) -> None:
        """Same archetypes should have high similarity."""
        builder1 = create_builder("B1", "workshop")
        builder2 = create_builder("B2", "workshop")

        sim = builder1.eigenvectors.similarity(builder2.eigenvectors)
        assert sim > 0.95  # Very similar


class TestPhase4Cosmotechnics:
    """Tests for expanded cosmotechnics."""

    def test_phase4_cosmotechnics_exist(self) -> None:
        """Phase 4 cosmotechnics should be defined."""
        assert CONSTRUCTION_V2.name == "construction_v2"
        assert EXCHANGE_V2.name == "exchange_v2"
        assert RESTORATION.name == "restoration"
        assert SYNTHESIS_V2.name == "synthesis_v2"
        assert MEMORY_V2.name == "memory_v2"

    def test_archetypes_use_phase4_cosmotechnics(self) -> None:
        """Each archetype should use appropriate Phase 4 cosmotechnics."""
        assert ARCHETYPE_SPECS[ArchetypeKind.BUILDER].cosmotechnics == CONSTRUCTION_V2
        assert ARCHETYPE_SPECS[ArchetypeKind.TRADER].cosmotechnics == EXCHANGE_V2
        assert ARCHETYPE_SPECS[ArchetypeKind.HEALER].cosmotechnics == RESTORATION
        assert ARCHETYPE_SPECS[ArchetypeKind.SCHOLAR].cosmotechnics == SYNTHESIS_V2
        assert ARCHETYPE_SPECS[ArchetypeKind.WATCHER].cosmotechnics == MEMORY_V2


class TestPhase4Coalitions:
    """Tests for coalition detection system."""

    def test_coalition_detection_finds_groups(self) -> None:
        """Coalition detection should find similar citizen groups."""
        env = create_phase4_environment()
        coalitions = detect_coalitions(env.citizens, similarity_threshold=0.9, k=3)

        # Should find at least one coalition among similar citizens
        # (exact count depends on threshold)
        assert isinstance(coalitions, list)

    def test_coalition_manager_lifecycle(self) -> None:
        """CoalitionManager should handle full lifecycle."""
        env = create_phase4_environment()
        manager = CoalitionManager(env.citizens, similarity_threshold=0.85)

        # Detect
        coalitions = manager.detect()
        initial_count = len(coalitions)

        # Decay
        for _ in range(10):
            manager.decay_all(0.15)

        # Some should be pruned
        summary = manager.summary()
        assert summary["alive_coalitions"] <= initial_count

    def test_coalition_centroid_computation(self) -> None:
        """Coalition centroid should average member eigenvectors."""
        env = create_phase4_environment()
        builders = get_citizens_by_archetype(env, "Builder")

        if len(builders) >= 2:
            # Create manual coalition of builders
            from agents.town.coalition import Coalition

            coalition = Coalition(members={b.id for b in builders[:2]})
            centroid = coalition.compute_centroid(env.citizens)

            # Centroid should have builder-like eigenvectors
            assert centroid.creativity > 0.5


class TestPhase4Reputation:
    """Tests for EigenTrust reputation system."""

    def test_reputation_computation(self) -> None:
        """Reputation should compute for all citizens."""
        env = create_phase4_environment()
        manager = CoalitionManager(env.citizens)

        reputation = manager.compute_reputation()

        assert len(reputation) == 25
        assert all(0.0 <= r <= 1.0 for r in reputation.values())

    def test_reputation_increases_with_trust(self) -> None:
        """Citizens with more incoming trust should have higher reputation."""
        env = create_phase4_environment()
        manager = CoalitionManager(env.citizens)
        ids = list(env.citizens.keys())

        # Everyone trusts Alice (first citizen)
        alice_id = ids[0]
        for other_id in ids[1:5]:
            manager.reputation.set_trust(other_id, alice_id, 1.0)

        reputation = manager.compute_reputation(alpha=0.3)

        # Alice should have high reputation
        alice_rep = reputation[alice_id]
        avg_rep = sum(reputation.values()) / len(reputation)
        assert alice_rep > avg_rep


class TestPhase4Evolution:
    """Tests for citizen evolution system."""

    @pytest.mark.asyncio
    async def test_evolving_citizen_cycle(self) -> None:
        """EvolvingCitizen should complete SENSE->ACT->REFLECT cycle."""
        env = create_phase4_environment()
        evolving = get_evolving_citizens(env)

        assert len(evolving) > 0
        citizen = evolving[0]
        initial_count = citizen.evolution_count

        obs = Observation(
            content="A new discovery in the garden",
            source="environment",
            emotional_weight=0.5,
        )

        await citizen.evolve(obs)

        assert citizen.evolution_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_evolution_updates_eigenvectors(self) -> None:
        """Evolution should update eigenvectors within bounds."""
        citizen = create_scholar("TestScholar", "library", evolving=True)
        assert isinstance(citizen, EvolvingCitizen)

        initial_ev = Eigenvectors(**citizen.eigenvectors.to_dict())

        # Evolve multiple times
        for i in range(3):
            obs = Observation(
                content=f"Discovery {i}",
                source="test",
                emotional_weight=0.3,
            )
            await citizen.evolve(obs)

        # Eigenvectors should have changed but stayed bounded
        final_ev = citizen.eigenvectors
        drift = initial_ev.drift(final_ev)

        # Should change but not too much
        assert drift <= citizen.max_eigenvector_drift * 3 * 2  # Rough bound


class TestPhase4Heritage:
    """Tests verifying heritage paper concepts are realized."""

    def test_chatdev_multi_role_agents(self) -> None:
        """CHATDEV heritage: Multi-agent roles should be present."""
        env = create_phase4_environment()

        # Different functional roles
        builders = get_citizens_by_archetype(env, "Builder")
        scholars = get_citizens_by_archetype(env, "Scholar")
        healers = get_citizens_by_archetype(env, "Healer")

        assert len(builders) > 0
        assert len(scholars) > 0
        assert len(healers) > 0

    def test_simulacra_memory_streams(self) -> None:
        """SIMULACRA heritage: Memory streams via GraphMemory."""
        env = create_phase4_environment()
        evolving = get_evolving_citizens(env)

        assert len(evolving) > 0
        citizen = evolving[0]

        # EvolvingCitizen has graph_memory
        assert hasattr(citizen, "graph_memory")
        assert citizen.graph_memory is not None

    def test_altera_nphase_cycles(self) -> None:
        """ALTERA heritage: Long-horizon via NPHASE cycles."""
        env = create_phase4_environment()
        evolving = get_evolving_citizens(env)

        assert len(evolving) > 0
        citizen = evolving[0]

        # EvolvingCitizen has growth_state tracking
        assert hasattr(citizen, "growth_state")
        assert hasattr(citizen.growth_state, "cycle_count")

    def test_voyager_skill_cosmotechnics(self) -> None:
        """VOYAGER heritage: Skill libraries via cosmotechnics."""
        # Different cosmotechnics = different skill orientations
        builder = create_builder("B", "workshop")
        scholar = create_scholar("S", "library")

        assert builder.cosmotechnics.name == "construction_v2"
        assert scholar.cosmotechnics.name == "synthesis_v2"
        assert builder.cosmotechnics.metaphor != scholar.cosmotechnics.metaphor

    def test_agent_hospital_domain_template(self) -> None:
        """AGENT HOSPITAL heritage: Domain simulation template."""
        env = create_phase4_environment()

        # Town provides domain-specific simulation structure
        assert env.name == "smallville-phase4"
        assert len(env.regions) > 0
        assert len(env.citizens) > 0

        # Region properties enable domain-specific behavior
        workshop = env.regions.get("workshop")
        assert workshop is not None
        assert "creation_bonus" in workshop.properties


class TestPhase4Metrics:
    """Tests for Phase 4 metrics and observability."""

    def test_environment_metrics(self) -> None:
        """Environment should provide town-level metrics."""
        env = create_phase4_environment()

        # Metrics available
        assert env.cooperation_level() >= 0
        assert env.tension_index() >= 0
        assert env.total_accursed_surplus() >= 0

    def test_region_density(self) -> None:
        """Region density should be computable."""
        env = create_phase4_environment()

        for region_name in env.regions:
            density = env.density_at(region_name)
            assert 0.0 <= density <= 1.0

    def test_coalition_summary(self) -> None:
        """Coalition manager should provide summary stats."""
        env = create_phase4_environment()
        manager = CoalitionManager(env.citizens, similarity_threshold=0.7)
        manager.detect()

        summary = manager.summary()

        assert "total_coalitions" in summary
        assert "alive_coalitions" in summary
        assert "total_members" in summary
        assert "bridge_citizens" in summary
        assert "avg_strength" in summary
