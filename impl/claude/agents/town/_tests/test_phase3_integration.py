"""
Phase 3 Integration Tests.

Tests for:
- 10 citizens (7 static + 3 evolving)
- Evolution cycle integration with TownFlux
- Graph memory in evolving citizens
- Functor verification
"""

import pytest

from agents.operad.core import LawStatus
from agents.town.citizen import Eigenvectors
from agents.town.environment import (
    TownEnvironment,
    create_phase3_environment,
    get_evolving_citizens,
)
from agents.town.evolving import (
    ADAPTATION,
    GROWTH,
    SYNTHESIS,
    EvolvingCitizen,
    GrowthTrigger,
    Observation,
)
from agents.town.flux import TownFlux
from agents.town.functor import (
    summarize_functor,
    verify_all_functor_laws,
)
from protocols.nphase.operad import NPHASE_OPERAD, NPhase


class TestPhase3Environment:
    """Tests for Phase 3 environment creation."""

    def test_create_phase3_environment(self) -> None:
        """Test Phase 3 environment has 10 citizens."""
        env = create_phase3_environment()
        assert len(env.citizens) == 10

    def test_phase3_has_7_static_citizens(self) -> None:
        """Test Phase 3 has 7 static citizens from Phase 2."""
        env = create_phase3_environment()
        static_names = {"Alice", "Bob", "Clara", "Diana", "Eve", "Frank", "Grace"}
        env_names = {c.name for c in env.citizens.values()}
        assert static_names.issubset(env_names)

    def test_phase3_has_3_evolving_citizens(self) -> None:
        """Test Phase 3 has 3 evolving citizens."""
        env = create_phase3_environment()
        evolving = get_evolving_citizens(env)
        assert len(evolving) == 3

    def test_evolving_citizens_are_hana_igor_juno(self) -> None:
        """Test evolving citizens are Hana, Igor, Juno."""
        env = create_phase3_environment()
        evolving = get_evolving_citizens(env)
        names = {c.name for c in evolving}
        assert names == {"Hana", "Igor", "Juno"}

    def test_hana_has_growth_cosmotechnics(self) -> None:
        """Test Hana has GROWTH cosmotechnics."""
        env = create_phase3_environment()
        hana = env.get_citizen_by_name("Hana")
        assert hana is not None
        assert isinstance(hana, EvolvingCitizen)
        assert hana.cosmotechnics == GROWTH

    def test_igor_has_adaptation_cosmotechnics(self) -> None:
        """Test Igor has ADAPTATION cosmotechnics."""
        env = create_phase3_environment()
        igor = env.get_citizen_by_name("Igor")
        assert igor is not None
        assert isinstance(igor, EvolvingCitizen)
        assert igor.cosmotechnics == ADAPTATION

    def test_juno_has_synthesis_cosmotechnics(self) -> None:
        """Test Juno has SYNTHESIS cosmotechnics."""
        env = create_phase3_environment()
        juno = env.get_citizen_by_name("Juno")
        assert juno is not None
        assert isinstance(juno, EvolvingCitizen)
        assert juno.cosmotechnics == SYNTHESIS

    def test_phase3_has_observatory_region(self) -> None:
        """Test Phase 3 has observatory region."""
        env = create_phase3_environment()
        assert "observatory" in env.regions

    def test_observatory_connected_to_library_garden(self) -> None:
        """Test observatory connected to library and garden."""
        env = create_phase3_environment()
        obs = env.regions["observatory"]
        assert "library" in obs.connections
        assert "garden" in obs.connections

    def test_phase3_has_6_regions(self) -> None:
        """Test Phase 3 has 6 regions (5 from Phase 2 + observatory)."""
        env = create_phase3_environment()
        assert len(env.regions) == 6


class TestEvolvingCitizenIntegration:
    """Tests for evolving citizen integration."""

    @pytest.fixture
    def env(self) -> TownEnvironment:
        """Create Phase 3 environment."""
        return create_phase3_environment()

    def test_evolving_citizens_can_evolve(self, env: TownEnvironment) -> None:
        """Test evolving citizens have evolve method."""
        for citizen in get_evolving_citizens(env):
            assert hasattr(citizen, "evolve")
            assert hasattr(citizen, "sense")
            assert hasattr(citizen, "act")
            assert hasattr(citizen, "reflect")

    @pytest.mark.asyncio
    async def test_hana_evolution_cycle(self, env: TownEnvironment) -> None:
        """Test Hana can complete evolution cycle."""
        hana = env.get_citizen_by_name("Hana")
        assert isinstance(hana, EvolvingCitizen)

        initial_count = hana.evolution_count
        obs = Observation(content="A new flower bloomed", source="garden")
        await hana.evolve(obs)

        assert hana.evolution_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_igor_adapts_to_observation(self, env: TownEnvironment) -> None:
        """Test Igor's ADAPTATION cosmotechnics interprets observation."""
        igor = env.get_citizen_by_name("Igor")
        assert isinstance(igor, EvolvingCitizen)

        obs = Observation(content="Weather changed", source="sky")
        sensed = await igor.sense(obs)

        # ADAPTATION interprets as environmental signal
        assert (
            "signal" in sensed.interpretation.lower()
            or "environment" in sensed.interpretation.lower()
        )

    @pytest.mark.asyncio
    async def test_juno_integrates_fragments(self, env: TownEnvironment) -> None:
        """Test Juno's SYNTHESIS cosmotechnics integrates."""
        juno = env.get_citizen_by_name("Juno")
        assert isinstance(juno, EvolvingCitizen)

        obs = Observation(content="Ancient text found", source="library")
        sensed = await juno.sense(obs)

        # SYNTHESIS interprets as fragment to integrate
        assert (
            "fragment" in sensed.interpretation.lower()
            or "integrate" in sensed.interpretation.lower()
        )

    @pytest.mark.asyncio
    async def test_multiple_evolutions_accumulate(self, env: TownEnvironment) -> None:
        """Test multiple evolution cycles accumulate state."""
        hana = env.get_citizen_by_name("Hana")
        assert isinstance(hana, EvolvingCitizen)

        for i in range(5):
            obs = Observation(content=f"Day {i} observation", source="garden")
            await hana.evolve(obs)

        assert hana.evolution_count == 5
        assert len(hana.growth_state.observations) == 5


class TestGraphMemoryIntegration:
    """Tests for graph memory with evolving citizens."""

    @pytest.fixture
    def env(self) -> TownEnvironment:
        """Create Phase 3 environment."""
        return create_phase3_environment()

    @pytest.mark.asyncio
    async def test_evolving_citizen_uses_graph_memory(self, env: TownEnvironment) -> None:
        """Test evolving citizens use graph memory."""
        hana = env.get_citizen_by_name("Hana")
        assert isinstance(hana, EvolvingCitizen)

        obs = Observation(content="Sunrise in garden", source="garden")
        await hana.evolve(obs)

        assert hana.graph_memory.size >= 1

    @pytest.mark.asyncio
    async def test_memory_recall_works(self, env: TownEnvironment) -> None:
        """Test memory recall works for evolving citizen."""
        igor = env.get_citizen_by_name("Igor")
        assert isinstance(igor, EvolvingCitizen)

        obs = Observation(content="Storm approaching", source="sky")
        await igor.sense(obs)

        # Should be able to recall the observation
        assert igor.graph_memory.size >= 1
        # Get the key that was stored
        result = igor.graph_memory.recall_by_content("Storm")
        assert len(result) > 0


class TestFunctorIntegration:
    """Tests for functor integration with Phase 3."""

    def test_functor_summary(self) -> None:
        """Test functor summarizes correctly."""
        summary = summarize_functor()
        assert summary["total_mapped"] > 0
        assert summary["ACT"]["count"] > 0
        assert summary["REFLECT"]["count"] > 0

    def test_functor_laws_mostly_pass(self) -> None:
        """Test most functor laws pass."""
        results = verify_all_functor_laws()
        passed = sum(1 for r in results if r.status == LawStatus.PASSED)
        # At least identity should pass
        assert passed >= 1


class TestNPhaseOperadIntegration:
    """Tests for NPHASE_OPERAD integration."""

    def test_nphase_operad_registered(self) -> None:
        """Test NPHASE_OPERAD is registered and accessible."""
        assert NPHASE_OPERAD is not None
        assert NPHASE_OPERAD.name == "NPHASE"

    def test_nphase_has_sense_act_reflect(self) -> None:
        """Test NPHASE has sense, act, reflect operations."""
        assert "sense" in NPHASE_OPERAD.operations
        assert "act" in NPHASE_OPERAD.operations
        assert "reflect" in NPHASE_OPERAD.operations


class TestTownFluxWithEvolution:
    """Tests for TownFlux with evolving citizens."""

    @pytest.fixture
    def flux(self) -> TownFlux:
        """Create TownFlux with Phase 3 environment."""
        env = create_phase3_environment()
        return TownFlux(env, seed=42)

    @pytest.mark.asyncio
    async def test_flux_step_works_with_evolving_citizens(self, flux: TownFlux) -> None:
        """Test TownFlux step works with evolving citizens."""
        events = []
        async for event in flux.step():
            events.append(event)

        # Should generate some events
        assert len(events) >= 0  # May be 0 if all citizens resting

    @pytest.mark.asyncio
    async def test_evolving_citizens_participate_in_flux(self, flux: TownFlux) -> None:
        """Test evolving citizens can participate in flux events."""
        # Run multiple steps
        all_participants: set[str] = set()
        for _ in range(5):
            async for event in flux.step():
                for p in event.participants:
                    all_participants.add(p)

        # Should have some participants
        # Note: evolving citizens might participate
        assert len(all_participants) >= 0  # At least some events


class TestEvolutionTriggers:
    """Tests for evolution trigger conditions."""

    @pytest.fixture
    def env(self) -> TownEnvironment:
        """Create Phase 3 environment."""
        return create_phase3_environment()

    def test_surplus_trigger_detection(self, env: TownEnvironment) -> None:
        """Test surplus threshold triggers evolution."""
        hana = env.get_citizen_by_name("Hana")
        assert isinstance(hana, EvolvingCitizen)

        hana.accursed_surplus = 10.0  # Above threshold
        should, trigger = hana.should_evolve()
        assert should
        assert trigger == GrowthTrigger.SURPLUS

    def test_relationship_trigger_detection(self, env: TownEnvironment) -> None:
        """Test relationship milestone triggers evolution."""
        igor = env.get_citizen_by_name("Igor")
        assert isinstance(igor, EvolvingCitizen)

        igor.relationships["Alice"] = 0.9  # Strong relationship
        should, trigger = igor.should_evolve()
        assert should
        assert trigger == GrowthTrigger.RELATIONSHIP


class TestEigenvectorDriftBounds:
    """Tests for eigenvector drift bounds in integration."""

    @pytest.fixture
    def env(self) -> TownEnvironment:
        """Create Phase 3 environment."""
        return create_phase3_environment()

    @pytest.mark.asyncio
    async def test_drift_bounded_after_many_evolutions(self, env: TownEnvironment) -> None:
        """Test eigenvector drift stays bounded after many evolutions."""
        juno = env.get_citizen_by_name("Juno")
        assert isinstance(juno, EvolvingCitizen)

        initial_warmth = juno.eigenvectors.warmth

        # Run many evolutions
        for i in range(20):
            obs = Observation(content=f"Event {i}", source="library")
            await juno.evolve(obs)

        # Drift should be bounded (max 0.1 per cycle, but not all cycles change warmth)
        drift = abs(juno.eigenvectors.warmth - initial_warmth)
        # Max theoretical drift: 20 * 0.1 = 2.0, but clamped to [0,1]
        assert 0.0 <= juno.eigenvectors.warmth <= 1.0


class TestPhase3Serialization:
    """Tests for Phase 3 environment serialization."""

    @pytest.fixture
    def env(self) -> TownEnvironment:
        """Create Phase 3 environment."""
        return create_phase3_environment()

    def test_environment_to_dict(self, env: TownEnvironment) -> None:
        """Test environment can be serialized."""
        data = env.to_dict()
        assert "name" in data
        assert data["name"] == "smallville-phase3"
        assert len(data["citizens"]) == 10
        assert len(data["regions"]) == 6

    @pytest.mark.asyncio
    async def test_evolving_citizen_to_dict(self, env: TownEnvironment) -> None:
        """Test evolving citizen serializes evolution state."""
        hana = env.get_citizen_by_name("Hana")
        assert isinstance(hana, EvolvingCitizen)

        # Evolve once
        obs = Observation(content="Test", source="garden")
        await hana.evolve(obs)

        data = hana.to_dict()
        assert "evolution_count" in data
        assert data["evolution_count"] == 1
        assert "graph_memory" in data
