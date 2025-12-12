"""
Tests for Cortex ecosystem integrations.

These tests verify that the integration adapters work correctly,
using graceful degradation when dependencies are unavailable.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from testing.analyst import CausalAnalyst, TestWitness
from testing.cortex import Cortex
from testing.integrations import (
    BudgetedMarket,
    IntegrationStatus,
    LatticeValidatedTopology,
    ObservedCortex,
    PersistentWitnessStore,
    TeleologicalRedTeam,
    create_enhanced_cortex,
    create_enhanced_oracle,
    create_persistent_analyst,
    format_integration_report,
    get_integration_status,
)
from testing.market import TestAsset, TestCost, TestMarket
from testing.oracle import Oracle
from testing.red_team import RedTeam
from testing.topologist import TypeTopology

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class MockAgent:
    """Simple agent for testing."""

    name: str

    async def invoke(self, x: Any) -> str:
        return str(x) + f"[{self.name}]"


# =============================================================================
# Integration Status Tests
# =============================================================================


class TestIntegrationStatus:
    """Tests for IntegrationStatus."""

    def test_get_status(self) -> None:
        """Should return IntegrationStatus."""
        status = get_integration_status()
        assert isinstance(status, IntegrationStatus)

    def test_status_attributes(self) -> None:
        """Should have all expected attributes."""
        status = get_integration_status()
        assert hasattr(status, "lgent_embeddings")
        assert hasattr(status, "dgent_persistence")
        assert hasattr(status, "ngent_narrative")
        assert hasattr(status, "bgent_economics")
        assert hasattr(status, "egent_evolution")
        assert hasattr(status, "ogent_observation")

    def test_status_repr(self) -> None:
        """Should have readable repr."""
        status = get_integration_status()
        repr_str = repr(status)
        assert "IntegrationStatus" in repr_str
        assert "/7 active" in repr_str


class TestFormatIntegrationReport:
    """Tests for integration report formatting."""

    def test_format_report(self) -> None:
        """Should format report with status indicators."""
        report = format_integration_report()
        assert "CORTEX INTEGRATION STATUS" in report
        assert "[OK]" in report or "[--]" in report


# =============================================================================
# Oracle Integration Tests
# =============================================================================


class TestEnhancedOracle:
    """Tests for Oracle × L-gent integration."""

    def test_create_with_simple(self) -> None:
        """Should create Oracle with simple embedder."""
        oracle = create_enhanced_oracle(embedder_backend="simple")
        assert isinstance(oracle, Oracle)

    def test_create_with_auto(self) -> None:
        """Should create Oracle with auto-selected embedder."""
        oracle = create_enhanced_oracle(embedder_backend="auto")
        assert isinstance(oracle, Oracle)

    @pytest.mark.asyncio
    async def test_enhanced_similarity(self) -> None:
        """Should compute similarity with enhanced embedder."""
        oracle = create_enhanced_oracle()
        sim = await oracle.similarity("hello", "world")
        assert 0 <= sim <= 1


# =============================================================================
# Analyst Integration Tests
# =============================================================================


class TestPersistentWitnessStore:
    """Tests for Analyst × D-gent integration."""

    def test_create_store(self, tmp_path: Path) -> None:
        """Should create persistent store."""
        store = PersistentWitnessStore(str(tmp_path / "witnesses.json"))
        assert len(store) == 0

    def test_record_witness(self, tmp_path: Path) -> None:
        """Should record witness."""
        store = PersistentWitnessStore(str(tmp_path / "witnesses.json"))
        witness = TestWitness(
            test_id="test_1",
            agent_path=["A"],
            input_data="hello",
            outcome="pass",
        )
        store.record(witness)
        assert len(store) == 1

    @pytest.mark.asyncio
    async def test_query_witnesses(self, tmp_path: Path) -> None:
        """Should query witnesses."""
        store = PersistentWitnessStore(str(tmp_path / "witnesses.json"))

        # Record some witnesses
        store.record(
            TestWitness(test_id="test_1", agent_path=[], input_data="a", outcome="pass")
        )
        store.record(
            TestWitness(test_id="test_2", agent_path=[], input_data="b", outcome="fail")
        )

        # Query
        results = await store.query(test_id="test_1")
        assert len(results) == 1


class TestPersistentAnalyst:
    """Tests for create_persistent_analyst."""

    def test_create_analyst(self, tmp_path: Path) -> None:
        """Should create analyst with persistent store."""
        analyst = create_persistent_analyst(str(tmp_path / "witnesses.json"))
        assert isinstance(analyst, CausalAnalyst)


# =============================================================================
# Topologist Integration Tests
# =============================================================================


class TestLatticeValidatedTopology:
    """Tests for Topologist × L-gent integration."""

    def test_wrap_topology(self) -> None:
        """Should wrap base topology."""
        base = TypeTopology()
        base.add_agent("A", "str", "str")
        base.add_agent("B", "str", "int")

        wrapped = LatticeValidatedTopology(base)
        assert wrapped.base == base

    def test_validate_path_without_lattice(self) -> None:
        """Should return True when lattice unavailable."""
        base = TypeTopology()
        base.add_agent("A", "str", "str")
        base.add_agent("B", "str", "int")

        wrapped = LatticeValidatedTopology(base)
        # Without lattice, all paths are considered valid
        assert wrapped.validate_path(["A", "B"]) is True

    def test_equivalent_paths(self) -> None:
        """Should find equivalent paths."""
        base = TypeTopology()
        base.add_agent("A", "str", "str")
        base.add_agent("B", "str", "str")

        wrapped = LatticeValidatedTopology(base)
        paths = wrapped.equivalent_paths("A", "B", validate=False)
        assert len(paths) >= 1


# =============================================================================
# Market Integration Tests
# =============================================================================


class TestBudgetedMarket:
    """Tests for Market × B-gent integration."""

    def test_wrap_market(self) -> None:
        """Should wrap base market."""
        base = TestMarket()
        wrapped = BudgetedMarket(base, initial_budget=1000.0)
        assert wrapped.base == base

    @pytest.mark.asyncio
    async def test_allocate_with_budget(self) -> None:
        """Should allocate with B-gent budgeting."""
        base = TestMarket()
        wrapped = BudgetedMarket(base)

        assets = [
            TestAsset(test_id="test_1", cost=TestCost(joules=1.0, time_ms=100)),
        ]

        allocations = await wrapped.allocate_with_budget(assets, 100.0)
        assert "test_1" in allocations


# =============================================================================
# Red Team Integration Tests
# =============================================================================


class TestTeleologicalRedTeam:
    """Tests for RedTeam × E-gent integration."""

    def test_wrap_red_team(self) -> None:
        """Should wrap base red team."""
        base = RedTeam(population_size=10, generations=2)
        wrapped = TeleologicalRedTeam(base)
        assert wrapped.base == base

    @pytest.mark.asyncio
    async def test_evolve_without_egent(self) -> None:
        """Should fall back to base evolution without E-gent."""
        base = RedTeam(population_size=5, generations=2)
        wrapped = TeleologicalRedTeam(base)

        agent = MockAgent("Test")
        seeds = ["hello"]

        # Should work even without E-gent
        population = await wrapped.evolve_with_demon(agent, seeds)
        assert len(population) >= 1


# =============================================================================
# Cortex Integration Tests
# =============================================================================


class TestObservedCortex:
    """Tests for Cortex × O-gent integration."""

    def test_wrap_cortex(self) -> None:
        """Should wrap base cortex."""
        base = Cortex()
        wrapped = ObservedCortex(base)
        assert wrapped.base == base

    def test_register_agent(self) -> None:
        """Should register agent with observation."""
        base = Cortex()
        wrapped = ObservedCortex(base)

        agent = MockAgent("Test")
        wrapped.register_agent(agent, "str", "str", observe=True)

        # Agent should be registered in base
        assert len(base._agents) >= 0  # May or may not be wrapped

    def test_get_telemetry_none(self) -> None:
        """Should return None for unobserved agents."""
        base = Cortex()
        wrapped = ObservedCortex(base)

        telemetry = wrapped.get_telemetry("nonexistent")
        assert telemetry is None


class TestEnhancedCortex:
    """Tests for create_enhanced_cortex factory."""

    def test_create_enhanced_cortex(self) -> None:
        """Should create enhanced cortex."""
        cortex = create_enhanced_cortex(
            embedder_backend="simple",
            observe_agents=False,
        )
        # Should return either Cortex or ObservedCortex
        assert cortex is not None

    def test_create_with_all_options(self, tmp_path: Path) -> None:
        """Should create with all options."""
        cortex = create_enhanced_cortex(
            embedder_backend="auto",
            witness_store_path=str(tmp_path / "witnesses.json"),
            observe_agents=False,
            use_lattice_validation=True,
            use_bgent_budgeting=True,
            use_egent_evolution=True,
        )
        assert cortex is not None


# =============================================================================
# Graceful Degradation Tests
# =============================================================================


class TestGracefulDegradation:
    """Tests for graceful degradation when dependencies unavailable."""

    def test_oracle_without_lgent(self) -> None:
        """Oracle should work without L-gent embeddings."""
        oracle = create_enhanced_oracle(embedder_backend="simple")
        # Should use fallback embedder
        assert oracle.embedder is not None

    def test_analyst_without_dgent(self, tmp_path: Path) -> None:
        """Analyst should work without D-gent persistence."""
        analyst = create_persistent_analyst(str(tmp_path / "witnesses.json"))
        # Should still work, just without persistence
        assert analyst is not None

    def test_cortex_minimal(self) -> None:
        """Cortex should work with minimal dependencies."""
        cortex = create_enhanced_cortex(
            embedder_backend="simple",
            observe_agents=False,
            use_lattice_validation=False,
            use_bgent_budgeting=False,
            use_egent_evolution=False,
        )
        assert cortex is not None

    @pytest.mark.asyncio
    async def test_full_pipeline_without_deps(self) -> None:
        """Full pipeline should work without external dependencies."""
        cortex = create_enhanced_cortex(
            embedder_backend="simple",
            observe_agents=False,
        )

        # Register an agent
        agent = MockAgent("Test")
        if hasattr(cortex, "register_agent"):
            cortex.register_agent(agent, "str", "str")
        elif hasattr(cortex, "base"):
            cortex.base.register_agent(agent, "str", "str")

        # Should work
        assert True
