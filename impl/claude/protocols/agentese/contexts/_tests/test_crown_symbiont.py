"""
Tests for CrownSymbiont: Crown Jewel surface handlers + D-gent infrastructure.

Verifies:
- Pure logic execution through Symbiont pattern
- D-gent triple integration (Witness, Manifold, Lattice)
- Projection methods
- Composition support
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pytest

from ..crown_mappings import (
    CROWN_DGENT_MAPPINGS,
    get_mapping_stats,
    get_triple_config,
    is_crown_path,
    list_paths_by_aspect,
    list_paths_by_context,
    needs_lattice,
    needs_manifold,
    needs_witness,
)
from ..crown_symbiont import (
    CrownSymbiont,
    CrownTripleConfig,
    compose_crown_symbionts,
    create_crown_symbiont,
)
from ..triple_backed_memory import (
    TripleBackedMemory,
    WitnessReport,
    create_triple_backed_memory,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class CounterState:
    """Simple state for testing."""

    count: int = 0
    history: list[int] | None = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


def counter_logic(increment: int, state: CounterState) -> tuple[int, CounterState]:
    """Pure counter logic."""
    new_count = state.count + increment
    new_history = (state.history or []) + [new_count]
    return new_count, CounterState(count=new_count, history=new_history)


async def async_counter_logic(
    increment: int, state: CounterState
) -> tuple[int, CounterState]:
    """Async version of counter logic."""
    return counter_logic(increment, state)


@pytest.fixture
def initial_state() -> CounterState:
    """Create initial counter state."""
    return CounterState(count=0)


@pytest.fixture
def dict_initial_state() -> dict[str, Any]:
    """Create initial dict state."""
    return {"count": 0, "history": []}


# =============================================================================
# CrownTripleConfig Tests
# =============================================================================


class TestCrownTripleConfig:
    """Tests for CrownTripleConfig."""

    def test_config_creation(self):
        """Test creating a config."""
        config = CrownTripleConfig(
            witness_aspect="timeline",
            manifold_aspect="embed",
            lattice_aspect="graph",
        )
        assert config.witness_aspect == "timeline"
        assert config.manifold_aspect == "embed"
        assert config.lattice_aspect == "graph"

    def test_config_uses_properties(self):
        """Test uses_* properties."""
        full_config = CrownTripleConfig(
            witness_aspect="timeline",
            manifold_aspect="embed",
            lattice_aspect="graph",
        )
        assert full_config.uses_witness
        assert full_config.uses_manifold
        assert full_config.uses_lattice

        partial_config = CrownTripleConfig(
            witness_aspect="timeline",
            manifold_aspect=None,
            lattice_aspect=None,
        )
        assert partial_config.uses_witness
        assert not partial_config.uses_manifold
        assert not partial_config.uses_lattice

        empty_config = CrownTripleConfig()
        assert not empty_config.uses_witness
        assert not empty_config.uses_manifold
        assert not empty_config.uses_lattice


# =============================================================================
# CrownSymbiont Tests
# =============================================================================


class TestCrownSymbiont:
    """Tests for CrownSymbiont."""

    @pytest.mark.asyncio
    async def test_sync_logic_execution(self, initial_state: CounterState) -> None:
        """Test executing sync logic through symbiont."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        result = await symbiont.invoke(5)
        assert result == 5

        result = await symbiont.invoke(3)
        assert result == 8

    @pytest.mark.asyncio
    async def test_async_logic_execution(self, initial_state: CounterState) -> None:
        """Test executing async logic through symbiont."""
        symbiont = CrownSymbiont(
            logic=async_counter_logic,
            initial_state=initial_state,
        )

        result = await symbiont.invoke(10)
        assert result == 10

    @pytest.mark.asyncio
    async def test_dict_state(self, dict_initial_state: dict[str, Any]) -> None:
        """Test with dict state."""

        def dict_counter(inc: int, state: dict[str, Any]) -> tuple[int, dict[str, Any]]:
            new_count = state["count"] + inc
            return new_count, {
                "count": new_count,
                "history": state["history"] + [new_count],
            }

        symbiont = CrownSymbiont(
            logic=dict_counter,
            initial_state=dict_initial_state,
        )

        result = await symbiont.invoke(5)
        assert result == 5

    def test_name_property(self, initial_state: CounterState) -> None:
        """Test symbiont name."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )
        assert "CrownSymbiont" in symbiont.name
        assert "counter_logic" in symbiont.name

    @pytest.mark.asyncio
    async def test_projections_without_triple(
        self, initial_state: CounterState
    ) -> None:
        """Test projection methods when no triple components configured."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        # All projection methods should return empty/default values
        events = await symbiont.event_stream()
        assert events == []

        drift = await symbiont.detect_drift("count")
        assert drift["drift_detected"] is False

        momentum = await symbiont.momentum()
        assert momentum["magnitude"] == 0.0
        assert momentum["confidence"] == 0.0

        # Test with trajectory parameter
        momentum_traj = await symbiont.momentum(trajectory="test")
        assert momentum_traj["magnitude"] == 0.0

        entropy = await symbiont.entropy()
        assert entropy == 0.0

        neighbors = await symbiont.neighbors(initial_state)
        assert neighbors == []

        curvature = await symbiont.curvature_at(initial_state)
        assert curvature == 0.0

        voids = await symbiont.voids_nearby(initial_state)
        assert voids == []

        lineage = await symbiont.lineage("node1")
        assert lineage == []

        meet_result = await symbiont.meet("a", "b")
        assert meet_result is None

        join_result = await symbiont.join("a", "b")
        assert join_result is None

        entails = await symbiont.entails("a", "b")
        assert entails is False


class TestCrownSymbiontProjections:
    """Tests for CrownSymbiont projection methods."""

    @pytest.mark.asyncio
    async def test_project_timeline(self, initial_state: CounterState) -> None:
        """Test timeline projection."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        projection = await symbiont.project_timeline()
        assert projection["type"] == "timeline"
        assert "events" in projection
        assert "count" in projection

    @pytest.mark.asyncio
    async def test_project_topology(self, initial_state: CounterState) -> None:
        """Test topology projection."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        projection = await symbiont.project_topology()
        assert projection["type"] == "topology"

    @pytest.mark.asyncio
    async def test_project_graph(self, initial_state: CounterState) -> None:
        """Test graph projection."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        projection = await symbiont.project_graph()
        assert projection["type"] == "graph"

    @pytest.mark.asyncio
    async def test_project_holographic(self, initial_state: CounterState) -> None:
        """Test holographic (combined) projection."""
        symbiont = CrownSymbiont(
            logic=counter_logic,
            initial_state=initial_state,
        )

        projection = await symbiont.project_holographic()
        assert projection["type"] == "holographic"
        assert "temporal" in projection
        assert "semantic" in projection
        assert "relational" in projection


# =============================================================================
# TripleBackedMemory Tests
# =============================================================================


class TestTripleBackedMemory:
    """Tests for TripleBackedMemory."""

    @pytest.mark.asyncio
    async def test_load_initial_state(self):
        """Test loading initial state."""
        initial = {"count": 0}
        memory = TripleBackedMemory(initial_state=initial)

        state = await memory.load()
        assert state == initial

    @pytest.mark.asyncio
    async def test_save_and_load(self):
        """Test saving and loading state."""
        memory = TripleBackedMemory(initial_state={"count": 0})

        await memory.save({"count": 5})
        state = await memory.load()
        assert state == {"count": 5}

    @pytest.mark.asyncio
    async def test_history_without_witness(self):
        """Test history returns empty without witness."""
        memory = TripleBackedMemory(initial_state={"count": 0})

        history = await memory.history()
        assert history == []

    @pytest.mark.asyncio
    async def test_node_id_generation(self):
        """Test node ID generation is unique."""
        memory = TripleBackedMemory(initial_state={"count": 0})

        id1 = memory._generate_node_id({"count": 1})
        id2 = memory._generate_node_id({"count": 2})

        assert id1 != id2
        assert "state_" in id1
        assert "state_" in id2


class TestCreateTripleBackedMemory:
    """Tests for create_triple_backed_memory factory."""

    @pytest.mark.asyncio
    async def test_factory_creation(self):
        """Test creating memory via factory."""
        memory = create_triple_backed_memory(
            initial_state={"count": 0},
        )

        state = await memory.load()
        assert state == {"count": 0}


# =============================================================================
# Crown Mappings Tests
# =============================================================================


class TestCrownMappings:
    """Tests for CROWN_DGENT_MAPPINGS registry."""

    def test_self_memory_paths_exist(self):
        """Test self.memory.* paths are mapped."""
        assert "self.memory.manifest" in CROWN_DGENT_MAPPINGS
        assert "self.memory.capture" in CROWN_DGENT_MAPPINGS
        assert "self.memory.recall" in CROWN_DGENT_MAPPINGS
        assert "self.memory.ghost.surface" in CROWN_DGENT_MAPPINGS

    def test_time_paths_exist(self):
        """Test time.* paths are mapped."""
        assert "time.inhabit.witness" in CROWN_DGENT_MAPPINGS
        assert "time.simulation.witness" in CROWN_DGENT_MAPPINGS
        assert "time.simulation.export" in CROWN_DGENT_MAPPINGS

    def test_get_triple_config(self):
        """Test get_triple_config function."""
        config = get_triple_config("self.memory.capture")
        assert config is not None
        assert config.witness_aspect == "record"
        assert config.manifold_aspect == "embed"
        assert config.lattice_aspect == "link"

        none_config = get_triple_config("nonexistent.path")
        assert none_config is None

    def test_is_crown_path(self):
        """Test is_crown_path function."""
        assert is_crown_path("self.memory.manifest")
        assert is_crown_path("time.simulation.witness")
        assert not is_crown_path("world.unknown.path")

    def test_needs_witness(self):
        """Test needs_witness function."""
        assert needs_witness("self.memory.capture")
        assert not needs_witness("self.memory.cartography.manifest")

    def test_needs_manifold(self):
        """Test needs_manifold function."""
        assert needs_manifold("self.memory.capture")
        assert not needs_manifold("self.tokens.manifest")

    def test_needs_lattice(self):
        """Test needs_lattice function."""
        assert needs_lattice("self.memory.capture")
        assert not needs_lattice("self.meta.append")

    def test_list_paths_by_aspect(self):
        """Test list_paths_by_aspect function."""
        record_paths = list_paths_by_aspect("record")
        assert len(record_paths) > 0
        assert "self.memory.capture" in record_paths

        timeline_paths = list_paths_by_aspect("timeline")
        assert "self.memory.manifest" in timeline_paths

    def test_list_paths_by_context(self):
        """Test list_paths_by_context function."""
        self_paths = list_paths_by_context("self")
        assert len(self_paths) > 0
        assert all(p.startswith("self.") for p in self_paths)

        time_paths = list_paths_by_context("time")
        assert len(time_paths) > 0
        assert all(p.startswith("time.") for p in time_paths)


class TestMappingStats:
    """Tests for mapping statistics."""

    def test_get_mapping_stats(self):
        """Test get_mapping_stats function."""
        stats = get_mapping_stats()

        assert stats.total_paths > 0
        assert stats.self_paths > 0
        assert stats.time_paths > 0
        assert stats.paths_with_witness > 0
        assert len(stats.unique_witness_aspects) > 0


# =============================================================================
# Composition Tests
# =============================================================================


class TestComposition:
    """Tests for CrownSymbiont composition."""

    @pytest.mark.asyncio
    async def test_compose_two_symbionts(self):
        """Test composing two symbionts."""

        def double_logic(x: int, state: int) -> tuple[int, int]:
            result = x * 2
            return result, state + result

        def add_ten_logic(x: int, state: int) -> tuple[int, int]:
            result = x + 10
            return result, state + result

        first = CrownSymbiont(logic=double_logic, initial_state=0)
        second = CrownSymbiont(logic=add_ten_logic, initial_state=0)

        composed = compose_crown_symbionts(first, second)

        # 5 -> double -> 10 -> add_ten -> 20
        result = await composed(5)
        assert result == 20


# =============================================================================
# Factory Tests
# =============================================================================


class TestCreateCrownSymbiont:
    """Tests for create_crown_symbiont factory."""

    @pytest.mark.asyncio
    async def test_factory_basic(self):
        """Test basic factory usage."""
        symbiont = create_crown_symbiont(
            logic=counter_logic,
            initial_state=CounterState(),
        )

        result = await symbiont.invoke(7)
        assert result == 7

    @pytest.mark.asyncio
    async def test_factory_with_config(self):
        """Test factory with explicit config."""
        config = CrownTripleConfig(
            witness_aspect="timeline",
            manifold_aspect=None,
            lattice_aspect="graph",
        )

        symbiont = create_crown_symbiont(
            logic=counter_logic,
            initial_state=CounterState(),
            config=config,
        )

        assert symbiont.config == config
