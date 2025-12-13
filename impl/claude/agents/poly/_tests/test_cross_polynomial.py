"""
Cross-Polynomial Composition Tests.

Demonstrates and tests composition between different polynomial agents:
- AlethicAgent (A-gent): Truth-seeking reasoning
- SoulPolynomialAgent (K-gent): Eigenvector context navigation
- MemoryPolynomialAgent (D-gent): State management
- EvolutionPolynomialAgent (E-gent): Thermodynamic evolution

This validates Phase 4 of the polyfunctor architecture.
"""

import pytest
from agents.poly import WiringDiagram, parallel, sequential

# =============================================================================
# Import Polynomial Agents
# =============================================================================


@pytest.fixture
def alethic_poly():
    """Get the alethic polynomial agent."""
    from agents.a.alethic import ALETHIC_AGENT

    return ALETHIC_AGENT


@pytest.fixture
def soul_poly():
    """Get the soul polynomial agent."""
    from agents.k.polynomial import SOUL_POLYNOMIAL

    return SOUL_POLYNOMIAL


@pytest.fixture
def memory_poly():
    """Get a fresh memory polynomial agent."""
    from agents.d.polynomial import MemoryStore, create_memory_polynomial

    store = MemoryStore()
    return create_memory_polynomial(store)


@pytest.fixture
def evolution_poly():
    """Get the evolution polynomial agent."""
    from agents.e.polynomial import EVOLUTION_POLYNOMIAL

    return EVOLUTION_POLYNOMIAL


# =============================================================================
# Basic Composition Tests
# =============================================================================


class TestCrossPolynomialComposition:
    """Test composition between different polynomial agents."""

    def test_polynomials_have_positions(
        self, alethic_poly, soul_poly, memory_poly, evolution_poly
    ) -> None:
        """All polynomial agents have non-empty position sets."""
        assert len(alethic_poly.positions) > 0
        assert len(soul_poly.positions) > 0
        assert len(memory_poly.positions) > 0
        assert len(evolution_poly.positions) > 0

    def test_polynomials_have_directions(
        self, alethic_poly, soul_poly, memory_poly, evolution_poly
    ) -> None:
        """All polynomial agents have directions for their positions."""
        for pos in alethic_poly.positions:
            assert alethic_poly.directions(pos) is not None

        for pos in soul_poly.positions:
            assert soul_poly.directions(pos) is not None

        for pos in memory_poly.positions:
            assert memory_poly.directions(pos) is not None

        for pos in evolution_poly.positions:
            assert evolution_poly.directions(pos) is not None

    def test_parallel_composition_soul_memory(self, soul_poly, memory_poly) -> None:
        """Soul and memory polynomials can be composed in parallel."""
        from agents.d.polynomial import MemoryPhase, StoreCommand
        from agents.k.polynomial import EigenvectorContext, SoulQuery

        composed = parallel(soul_poly, memory_poly)

        # Should have product state space
        assert len(composed.positions) > 0

        # Product positions should be tuples
        pos = next(iter(composed.positions))
        assert isinstance(pos, tuple)
        assert len(pos) == 2

    def test_sequential_composition_with_wiring(self, soul_poly, alethic_poly) -> None:
        """Can compose soul → alethic via wiring diagram."""
        # Create wiring diagram
        diagram = WiringDiagram(
            name="soul_then_alethic",
            left=soul_poly,
            right=alethic_poly,
        )

        # Compose
        composed = diagram.compose()

        # Should exist and have positions
        assert composed is not None
        assert len(composed.positions) > 0
        assert composed.name == "SoulPolynomial>>Alethic"


# =============================================================================
# Integration Tests with Wrappers
# =============================================================================


class TestWrapperIntegration:
    """Test integration using the wrapper classes."""

    @pytest.mark.asyncio
    async def test_memory_stores_alethic_response(self) -> None:
        """Memory agent can store results from alethic reasoning."""
        from agents.a.alethic import AlethicAgent, Query
        from agents.d.polynomial import MemoryPolynomialAgent

        # Create agents
        alethic = AlethicAgent()
        memory = MemoryPolynomialAgent()

        # Run alethic reasoning
        response = await alethic.reason(Query(claim="The sky is blue"))

        # Store result in memory
        store_result = await memory.store(
            {
                "query": response.query.claim,
                "verdict": response.verdict.accepted,
                "confidence": response.final_confidence,
            },
            key="alethic_result",
        )

        assert store_result.success

        # Load it back
        load_result = await memory.load(key="alethic_result")
        assert load_result.state["query"] == "The sky is blue"

    @pytest.mark.asyncio
    async def test_soul_guides_alethic(self) -> None:
        """Soul eigenvector context can guide alethic reasoning."""
        from agents.a.alethic import AlethicAgent, Query
        from agents.k.polynomial import EigenvectorContext, SoulPolynomialAgent

        # Create agents
        soul = SoulPolynomialAgent()
        alethic = AlethicAgent()

        # Query soul for context
        soul_response = await soul.query("Should I add dark mode?")

        # Use soul's judgment to form alethic query
        alethic_query = Query(
            claim=f"Adding dark mode is worthwhile (context: {soul_response.primary_context.name})",
            confidence_threshold=0.5,
        )

        # Run alethic reasoning
        alethic_response = await alethic.reason(alethic_query)

        # Both should complete successfully
        assert soul_response.judgments
        assert alethic_response.verdict is not None

    @pytest.mark.asyncio
    async def test_memory_evolution_cycle(self) -> None:
        """Memory tracks evolution cycle state."""
        from agents.d.polynomial import MemoryPolynomialAgent
        from agents.e.polynomial import EvolutionPolynomialAgent

        memory = MemoryPolynomialAgent()
        evolution = EvolutionPolynomialAgent()

        # Run evolution
        result = await evolution.evolve(
            code="def foo(): pass",
            intent="Add docstring",
        )

        # Store evolution result
        await memory.store(
            {
                "cycle_id": result.cycle_id,
                "mutations_succeeded": result.mutations_succeeded,
                "temperature": result.temperature,
            },
            key="evolution_cycle_1",
        )

        # Verify storage
        loaded = await memory.load(key="evolution_cycle_1")
        assert loaded.state["cycle_id"] == result.cycle_id

    @pytest.mark.asyncio
    async def test_full_pipeline_soul_alethic_memory(self) -> None:
        """Full pipeline: Soul → Alethic → Memory."""
        from agents.a.alethic import AlethicAgent, Query
        from agents.d.polynomial import MemoryPolynomialAgent
        from agents.k.polynomial import SoulPolynomialAgent

        soul = SoulPolynomialAgent()
        alethic = AlethicAgent()
        memory = MemoryPolynomialAgent()

        # Step 1: Query soul
        soul_response = await soul.query_all("Is this code elegant?")

        # Step 2: Alethic reasoning on soul's synthesis
        alethic_response = await alethic.reason(
            Query(claim=soul_response.synthesis or "Code is elegant")
        )

        # Step 3: Store pipeline result
        await memory.store(
            {
                "soul_context": soul_response.primary_context.name,
                "alethic_verdict": alethic_response.verdict.accepted,
                "reasoning_trace": alethic_response.reasoning_trace,
            },
            key="pipeline_result",
        )

        # Verify
        result = await memory.load(key="pipeline_result")
        assert result.state is not None
        assert "soul_context" in result.state
        assert "alethic_verdict" in result.state


# =============================================================================
# Polynomial Law Tests with Cross-Agent Composition
# =============================================================================


class TestPolynomialLawsAcrossAgents:
    """Verify polynomial laws hold across different agent types."""

    def test_parallel_commutes_with_identity(
        self, soul_poly, memory_poly, alethic_poly
    ) -> None:
        """Parallel composition with identity should preserve structure."""
        from agents.poly import identity

        id_agent = identity()

        # par(soul, id) should have same output types as soul on left
        par_soul_id = parallel(soul_poly, id_agent)
        assert len(par_soul_id.positions) >= len(soul_poly.positions)

    def test_sequential_associativity_mixed_agents(
        self, soul_poly, memory_poly
    ) -> None:
        """Associativity should hold for mixed agent composition."""
        from agents.poly import from_function

        # Create a simple adapter function
        adapter = from_function("Adapter", lambda x: x)

        # (soul >> adapter) >> memory vs soul >> (adapter >> memory)
        left = sequential(sequential(soul_poly, adapter), memory_poly)
        right = sequential(soul_poly, sequential(adapter, memory_poly))

        # Both should have valid positions
        assert len(left.positions) > 0
        assert len(right.positions) > 0

        # Same number of composed positions
        assert len(left.positions) == len(right.positions)


# =============================================================================
# Instance Isolation Across Compositions
# =============================================================================


class TestIsolationInComposition:
    """Verify instance isolation is preserved in compositions."""

    @pytest.mark.asyncio
    async def test_parallel_memories_are_isolated(self) -> None:
        """Two memory agents in parallel should have isolated state."""
        from agents.d.polynomial import MemoryPolynomialAgent

        mem1 = MemoryPolynomialAgent()
        mem2 = MemoryPolynomialAgent()

        # Store different data
        await mem1.store("data1", key="shared")
        await mem2.store("data2", key="shared")

        # Should not interfere
        r1 = await mem1.load(key="shared")
        r2 = await mem2.load(key="shared")

        assert r1.state == "data1"
        assert r2.state == "data2"

    @pytest.mark.asyncio
    async def test_composed_then_independent(self) -> None:
        """Agents used in composition remain independently usable."""
        from agents.a.alethic import AlethicAgent, Query

        agent1 = AlethicAgent()
        agent2 = AlethicAgent()

        # Use agent1
        r1 = await agent1.reason(Query(claim="test1"))

        # Use agent2
        r2 = await agent2.reason(Query(claim="test2"))

        # Both should work independently
        assert r1.query.claim == "test1"
        assert r2.query.claim == "test2"
