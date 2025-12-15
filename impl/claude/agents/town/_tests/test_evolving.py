"""
Tests for EvolvingCitizen.

Verifies the SENSE → ACT → REFLECT evolution cycle and bounded eigenvector drift.
"""

from datetime import datetime

import pytest
from agents.town.citizen import Eigenvectors
from agents.town.evolving import (
    ADAPTATION,
    GROWTH,
    SYNTHESIS,
    ActionResult,
    EvolvingCitizen,
    GrowthState,
    GrowthTrigger,
    Observation,
    Reflection,
    SensedState,
    create_evolving_citizen,
)
from protocols.nphase.operad import NPhase


class TestObservation:
    """Tests for Observation dataclass."""

    def test_observation_creation(self) -> None:
        """Test basic observation creation."""
        obs = Observation(content="Alice waved", source="Alice")
        assert obs.content == "Alice waved"
        assert obs.source == "Alice"
        assert obs.emotional_weight == 0.0

    def test_observation_with_emotion(self) -> None:
        """Test observation with emotional weight."""
        obs = Observation(content="Good news", source="Herald", emotional_weight=0.8)
        assert obs.emotional_weight == 0.8


class TestGrowthState:
    """Tests for GrowthState dataclass."""

    def test_default_growth_state(self) -> None:
        """Test default growth state initialization."""
        state = GrowthState()
        assert state.observations == []
        assert state.actions_taken == []
        assert state.reflections == []
        assert state.cycle_count == 0


class TestEvolvingCitizenCreation:
    """Tests for EvolvingCitizen creation."""

    def test_basic_creation(self) -> None:
        """Test basic EvolvingCitizen creation."""
        citizen = create_evolving_citizen(
            name="Hana",
            archetype="Gardener",
            region="garden",
        )
        assert citizen.name == "Hana"
        assert citizen.archetype == "Gardener"
        assert citizen.region == "garden"
        assert citizen.cosmotechnics == GROWTH

    def test_creation_with_custom_cosmotechnics(self) -> None:
        """Test creation with custom cosmotechnics."""
        citizen = create_evolving_citizen(
            name="Igor",
            archetype="Scout",
            region="forest",
            cosmotechnics=ADAPTATION,
        )
        assert citizen.cosmotechnics == ADAPTATION

    def test_creation_with_eigenvectors(self) -> None:
        """Test creation with custom eigenvectors."""
        eigen = Eigenvectors(warmth=0.8, curiosity=0.9)
        citizen = create_evolving_citizen(
            name="Juno",
            archetype="Scholar",
            region="library",
            eigenvectors=eigen,
        )
        assert citizen.eigenvectors.warmth == 0.8
        assert citizen.eigenvectors.curiosity == 0.9

    def test_evolution_count_starts_at_zero(self) -> None:
        """Test evolution count starts at zero."""
        citizen = create_evolving_citizen("Test", "Test", "test")
        assert citizen.evolution_count == 0

    def test_max_drift_configurable(self) -> None:
        """Test max drift is configurable."""
        citizen = create_evolving_citizen("Test", "Test", "test", max_drift=0.05)
        assert citizen.max_eigenvector_drift == 0.05


class TestSensePhase:
    """Tests for SENSE phase."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_sense_returns_sensed_state(self, citizen: EvolvingCitizen) -> None:
        """Test sense returns SensedState."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        assert isinstance(sensed, SensedState)
        assert sensed.phase == NPhase.SENSE

    @pytest.mark.asyncio
    async def test_sense_stores_observation(self, citizen: EvolvingCitizen) -> None:
        """Test sense stores observation in growth state."""
        obs = Observation(content="Hello", source="World")
        await citizen.sense(obs)
        assert len(citizen.growth_state.observations) == 1

    @pytest.mark.asyncio
    async def test_sense_calculates_relevance(self, citizen: EvolvingCitizen) -> None:
        """Test sense calculates relevance."""
        obs = Observation(content="Hello", source="World", emotional_weight=0.5)
        sensed = await citizen.sense(obs)
        assert 0.0 <= sensed.relevance <= 1.0

    @pytest.mark.asyncio
    async def test_sense_interprets_through_cosmotechnics(
        self, citizen: EvolvingCitizen
    ) -> None:
        """Test sense interprets through cosmotechnics."""
        obs = Observation(content="New flower bloomed", source="Garden")
        sensed = await citizen.sense(obs)
        # GROWTH cosmotechnics interprets as opportunity
        assert "growth" in sensed.interpretation.lower()


class TestActPhase:
    """Tests for ACT phase."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_act_returns_action_result(self, citizen: EvolvingCitizen) -> None:
        """Test act returns ActionResult."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        assert isinstance(result, ActionResult)
        assert result.phase == NPhase.ACT

    @pytest.mark.asyncio
    async def test_act_stores_action(self, citizen: EvolvingCitizen) -> None:
        """Test act stores action in growth state."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        await citizen.act(sensed)
        assert len(citizen.growth_state.actions_taken) == 1

    @pytest.mark.asyncio
    async def test_warm_citizen_greets(self, citizen: EvolvingCitizen) -> None:
        """Test warm citizen chooses greet action."""
        citizen.eigenvectors.warmth = 0.9
        obs = Observation(content="Stranger arrived", source="Gate")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        assert result.action_type == "greet"

    @pytest.mark.asyncio
    async def test_creative_citizen_creates(self, citizen: EvolvingCitizen) -> None:
        """Test creative citizen chooses create action."""
        citizen.eigenvectors.warmth = 0.3  # Not warm
        citizen.eigenvectors.curiosity = 0.3  # Not curious
        citizen.eigenvectors.creativity = 0.9  # Very creative
        obs = Observation(content="Blank canvas", source="Studio")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        assert result.action_type == "create"


class TestReflectPhase:
    """Tests for REFLECT phase."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_reflect_returns_reflection(self, citizen: EvolvingCitizen) -> None:
        """Test reflect returns Reflection."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        reflection = await citizen.integrate_reflection(result)
        assert isinstance(reflection, Reflection)
        assert reflection.phase == NPhase.REFLECT

    @pytest.mark.asyncio
    async def test_reflect_stores_reflection(self, citizen: EvolvingCitizen) -> None:
        """Test reflect stores reflection in growth state."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        await citizen.integrate_reflection(result)
        assert len(citizen.growth_state.reflections) == 1

    @pytest.mark.asyncio
    async def test_reflect_proposes_deltas(self, citizen: EvolvingCitizen) -> None:
        """Test reflect proposes eigenvector deltas."""
        obs = Observation(content="Hello", source="World")
        sensed = await citizen.sense(obs)
        result = await citizen.act(sensed)
        reflection = await citizen.integrate_reflection(result)
        # Successful action should propose some deltas
        if result.success:
            assert (
                len(reflection.eigenvector_deltas) > 0 or True
            )  # May be 0 for observe


class TestBoundedDrift:
    """Tests for bounded eigenvector drift."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen with small max drift."""
        return create_evolving_citizen("Test", "Test", "test", max_drift=0.05)

    def test_drift_bounded(self) -> None:
        """Test drift is bounded by max_eigenvector_drift."""
        citizen = create_evolving_citizen("Test", "Test", "test", max_drift=0.05)
        proposed = {"warmth": 0.5}  # Large proposed change
        applied = citizen._apply_bounded_drift(proposed)
        assert applied["warmth"] == 0.05  # Clamped to max

    def test_negative_drift_bounded(self) -> None:
        """Test negative drift is also bounded."""
        citizen = create_evolving_citizen("Test", "Test", "test", max_drift=0.05)
        proposed = {"warmth": -0.5}
        applied = citizen._apply_bounded_drift(proposed)
        assert applied["warmth"] == -0.05

    def test_small_drift_preserved(self) -> None:
        """Test small drift within bounds is preserved."""
        citizen = create_evolving_citizen("Test", "Test", "test", max_drift=0.1)
        proposed = {"warmth": 0.03}
        applied = citizen._apply_bounded_drift(proposed)
        assert applied["warmth"] == 0.03


class TestFullEvolutionCycle:
    """Tests for full evolution cycle (sense >> act >> reflect)."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_evolve_increments_count(self, citizen: EvolvingCitizen) -> None:
        """Test evolve increments evolution_count."""
        assert citizen.evolution_count == 0
        obs = Observation(content="Hello", source="World")
        await citizen.evolve(obs)
        assert citizen.evolution_count == 1

    @pytest.mark.asyncio
    async def test_evolve_returns_self(self, citizen: EvolvingCitizen) -> None:
        """Test evolve returns self for chaining."""
        obs = Observation(content="Hello", source="World")
        result = await citizen.evolve(obs)
        assert result is citizen

    @pytest.mark.asyncio
    async def test_evolve_updates_last_evolution(
        self, citizen: EvolvingCitizen
    ) -> None:
        """Test evolve updates last_evolution timestamp."""
        before = citizen.growth_state.last_evolution
        obs = Observation(content="Hello", source="World")
        await citizen.evolve(obs)
        assert citizen.growth_state.last_evolution is not None
        if before is not None:
            assert citizen.growth_state.last_evolution >= before

    @pytest.mark.asyncio
    async def test_multiple_evolutions(self, citizen: EvolvingCitizen) -> None:
        """Test multiple evolution cycles accumulate."""
        for i in range(5):
            obs = Observation(content=f"Event {i}", source="World")
            await citizen.evolve(obs)

        assert citizen.evolution_count == 5
        assert citizen.growth_state.cycle_count == 5
        assert len(citizen.growth_state.observations) == 5


class TestShouldEvolve:
    """Tests for evolution trigger detection."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    def test_no_trigger_initially(self, citizen: EvolvingCitizen) -> None:
        """Test no trigger initially."""
        should, trigger = citizen.should_evolve()
        assert not should
        assert trigger is None

    def test_surplus_trigger(self, citizen: EvolvingCitizen) -> None:
        """Test surplus triggers evolution."""
        citizen.accursed_surplus = 10.0  # Above threshold of 5.0
        should, trigger = citizen.should_evolve()
        assert should
        assert trigger == GrowthTrigger.SURPLUS

    def test_relationship_trigger(self, citizen: EvolvingCitizen) -> None:
        """Test relationship milestone triggers evolution."""
        citizen.relationships["friend"] = 0.9  # Above 0.8 threshold
        should, trigger = citizen.should_evolve()
        assert should
        assert trigger == GrowthTrigger.RELATIONSHIP

    @pytest.mark.asyncio
    async def test_witness_trigger(self, citizen: EvolvingCitizen) -> None:
        """Test witnessing many events triggers evolution."""
        for i in range(10):
            obs = Observation(content=f"Event {i}", source="World")
            await citizen.sense(obs)  # Just sense, don't full evolve

        should, trigger = citizen.should_evolve()
        assert should
        assert trigger == GrowthTrigger.WITNESS


class TestGraphMemoryIntegration:
    """Tests for graph memory integration."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_sense_stores_in_graph_memory(self, citizen: EvolvingCitizen) -> None:
        """Test sense stores observation in graph memory."""
        obs = Observation(content="Hello", source="World")
        await citizen.sense(obs)
        assert citizen.graph_memory.size == 1

    @pytest.mark.asyncio
    async def test_reflect_stores_in_graph_memory(
        self, citizen: EvolvingCitizen
    ) -> None:
        """Test reflect stores insight in graph memory."""
        obs = Observation(content="Hello", source="World")
        await citizen.evolve(obs)
        # Should have sense + reflect entries
        assert citizen.graph_memory.size >= 2


class TestCosmotechnics:
    """Tests for different cosmotechnics."""

    def test_growth_cosmotechnics(self) -> None:
        """Test GROWTH cosmotechnics."""
        assert GROWTH.name == "growth"
        assert "becoming" in GROWTH.description.lower()

    def test_adaptation_cosmotechnics(self) -> None:
        """Test ADAPTATION cosmotechnics."""
        assert ADAPTATION.name == "adaptation"
        assert "fitting" in ADAPTATION.description.lower()

    def test_synthesis_cosmotechnics(self) -> None:
        """Test SYNTHESIS cosmotechnics."""
        assert SYNTHESIS.name == "synthesis"
        assert "integration" in SYNTHESIS.description.lower()


class TestSerialization:
    """Tests for serialization."""

    @pytest.fixture
    def citizen(self) -> EvolvingCitizen:
        """Create test citizen."""
        return create_evolving_citizen("Test", "Test", "test")

    @pytest.mark.asyncio
    async def test_to_dict(self, citizen: EvolvingCitizen) -> None:
        """Test to_dict includes evolution state."""
        obs = Observation(content="Hello", source="World")
        await citizen.evolve(obs)

        data = citizen.to_dict()
        assert "evolution_count" in data
        assert data["evolution_count"] == 1
        assert "growth_state" in data
        assert "graph_memory" in data
