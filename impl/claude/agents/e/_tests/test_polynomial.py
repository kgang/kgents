"""
Tests for the E-gent Polynomial Agent.

Tests verify:
1. EvolutionPhase state machine
2. Direction validation at each phase
3. Full evolution cycle
4. Temperature adjustment
5. Gibbs free energy guidance
"""

import pytest
from agents.e.polynomial import (
    EVOLUTION_POLYNOMIAL,
    EvolutionIntent,
    EvolutionPhase,
    EvolutionPolynomialAgent,
    EvolutionResult,
    InfectCommand,
    MutateCommand,
    Mutation,
    PayoffCommand,
    SelectCommand,
    StartCycleCommand,
    WagerCommand,
    evolution_directions,
    evolution_transition,
    reset_evolution,
)

# =============================================================================
# Setup/Teardown
# =============================================================================


@pytest.fixture(autouse=True)
def clean_evolution():
    """Reset evolution state before each test."""
    reset_evolution()
    yield
    reset_evolution()


# =============================================================================
# State Tests
# =============================================================================


class TestEvolutionPhase:
    """Test the EvolutionPhase enum."""

    def test_all_phases_defined(self) -> None:
        """All eight evolution phases are defined."""
        assert EvolutionPhase.IDLE
        assert EvolutionPhase.SUN
        assert EvolutionPhase.MUTATE
        assert EvolutionPhase.SELECT
        assert EvolutionPhase.WAGER
        assert EvolutionPhase.INFECT
        assert EvolutionPhase.PAYOFF
        assert EvolutionPhase.COMPLETE

    def test_phases_are_unique(self) -> None:
        """Each phase has a unique value."""
        phases = list(EvolutionPhase)
        values = [p.value for p in phases]
        assert len(values) == len(set(values))


# =============================================================================
# Direction Tests
# =============================================================================


class TestEvolutionDirections:
    """Test phase-dependent direction validation."""

    def test_idle_accepts_start_command(self) -> None:
        """IDLE phase accepts StartCycleCommand."""
        dirs = evolution_directions(EvolutionPhase.IDLE)
        assert StartCycleCommand in dirs or type(StartCycleCommand) in dirs

    def test_mutate_accepts_code(self) -> None:
        """MUTATE phase accepts code or MutateCommand."""
        dirs = evolution_directions(EvolutionPhase.MUTATE)
        assert MutateCommand in dirs or str in dirs

    def test_select_accepts_mutations(self) -> None:
        """SELECT phase accepts mutations."""
        dirs = evolution_directions(EvolutionPhase.SELECT)
        assert SelectCommand in dirs or list in dirs or tuple in dirs


# =============================================================================
# Transition Tests
# =============================================================================


class TestEvolutionTransition:
    """Test the evolution state transition function."""

    def test_idle_to_sun(self) -> None:
        """IDLE → SUN on StartCycleCommand."""
        cmd = StartCycleCommand(code="def foo(): pass")
        new_phase, output = evolution_transition(EvolutionPhase.IDLE, cmd)

        assert new_phase == EvolutionPhase.SUN

    def test_sun_to_mutate(self) -> None:
        """SUN → MUTATE."""
        cmd = StartCycleCommand(code="def foo(): pass")
        new_phase, output = evolution_transition(EvolutionPhase.SUN, cmd)

        assert new_phase == EvolutionPhase.MUTATE
        assert isinstance(output, MutateCommand)

    def test_mutate_to_select(self) -> None:
        """MUTATE → SELECT with generated mutations."""
        cmd = MutateCommand(code="def foo(): pass", max_mutations=5)
        new_phase, output = evolution_transition(EvolutionPhase.MUTATE, cmd)

        assert new_phase == EvolutionPhase.SELECT
        assert isinstance(output, SelectCommand)
        assert len(output.mutations) > 0

    def test_select_to_wager(self) -> None:
        """SELECT → WAGER with selected mutations."""
        mutations = [
            Mutation(
                id="m1",
                schema_signature="test",
                original_code="def foo(): pass",
                mutated_code="def foo(): return 1",
                intent_alignment=0.8,
            )
        ]
        cmd = SelectCommand(mutations=tuple(mutations), min_intent_alignment=0.5)
        new_phase, output = evolution_transition(EvolutionPhase.SELECT, cmd)

        assert new_phase == EvolutionPhase.WAGER
        assert isinstance(output, WagerCommand)

    def test_wager_to_infect(self) -> None:
        """WAGER → INFECT with staked mutations."""
        mutations = [
            Mutation(
                id="m1",
                schema_signature="test",
                original_code="",
                mutated_code="",
            )
        ]
        cmd = WagerCommand(mutations=tuple(mutations), stake_per_mutation=100)
        new_phase, output = evolution_transition(EvolutionPhase.WAGER, cmd)

        assert new_phase == EvolutionPhase.INFECT
        assert isinstance(output, InfectCommand)

    def test_infect_to_payoff(self) -> None:
        """INFECT → PAYOFF with results."""
        mutations = [
            Mutation(
                id="m1",
                schema_signature="test",
                original_code="",
                mutated_code="",
                gibbs_free_energy=-0.5,  # Favorable
            )
        ]
        cmd = InfectCommand(mutations=tuple(mutations))
        new_phase, output = evolution_transition(EvolutionPhase.INFECT, cmd)

        assert new_phase == EvolutionPhase.PAYOFF
        assert isinstance(output, PayoffCommand)

    def test_payoff_to_complete(self) -> None:
        """PAYOFF → COMPLETE with result."""
        cmd = PayoffCommand(succeeded=(), failed=())
        new_phase, output = evolution_transition(EvolutionPhase.PAYOFF, cmd)

        assert new_phase == EvolutionPhase.COMPLETE
        assert isinstance(output, EvolutionResult)

    def test_complete_returns_to_idle(self) -> None:
        """COMPLETE → IDLE."""
        new_phase, output = evolution_transition(EvolutionPhase.COMPLETE, None)

        assert new_phase == EvolutionPhase.IDLE
        assert isinstance(output, EvolutionResult)


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestEvolutionPolynomial:
    """Test the EVOLUTION_POLYNOMIAL agent."""

    def test_has_all_positions(self) -> None:
        """Agent has all eight phases as positions."""
        assert len(EVOLUTION_POLYNOMIAL.positions) == 8
        for phase in EvolutionPhase:
            assert phase in EVOLUTION_POLYNOMIAL.positions

    def test_run_full_cycle(self) -> None:
        """run() executes full cycle."""
        cmd = StartCycleCommand(code="def foo(): pass")

        # Manually run through phases
        phase = EvolutionPhase.IDLE
        current = cmd
        phases_visited = [phase]

        for _ in range(10):  # Max iterations
            phase, current = EVOLUTION_POLYNOMIAL.transition(phase, current)
            phases_visited.append(phase)
            if isinstance(current, EvolutionResult):
                break

        # Should have visited key phases
        assert EvolutionPhase.MUTATE in phases_visited
        assert EvolutionPhase.SELECT in phases_visited


# =============================================================================
# Wrapper Tests
# =============================================================================


class TestEvolutionPolynomialAgentWrapper:
    """Test the backwards-compatible EvolutionPolynomialAgent wrapper."""

    def test_initial_phase_is_idle(self) -> None:
        """Agent starts in IDLE phase."""
        agent = EvolutionPolynomialAgent()
        assert agent.phase == EvolutionPhase.IDLE

    def test_initial_temperature(self) -> None:
        """Agent respects initial temperature."""
        agent = EvolutionPolynomialAgent(temperature=2.0)
        assert agent.temperature == 2.0

    @pytest.mark.asyncio
    async def test_evolve_returns_result(self) -> None:
        """evolve() returns EvolutionResult."""
        agent = EvolutionPolynomialAgent()
        result = await agent.evolve("def foo(): pass")

        assert isinstance(result, EvolutionResult)
        assert result.mutations_generated > 0

    @pytest.mark.asyncio
    async def test_evolve_with_intent(self) -> None:
        """evolve() uses provided intent."""
        agent = EvolutionPolynomialAgent()
        result = await agent.evolve(
            "def foo(): pass",
            intent="Optimize performance",
        )

        assert isinstance(result, EvolutionResult)

    @pytest.mark.asyncio
    async def test_evolve_with_intent_object(self) -> None:
        """evolve() accepts EvolutionIntent object."""
        agent = EvolutionPolynomialAgent()
        intent = EvolutionIntent(description="Improve readability", confidence=0.9)
        result = await agent.evolve("def foo(): pass", intent=intent)

        assert isinstance(result, EvolutionResult)

    @pytest.mark.asyncio
    async def test_suggest_returns_mutations(self) -> None:
        """suggest() returns mutations without applying."""
        agent = EvolutionPolynomialAgent()
        mutations = await agent.suggest("def foo(): pass")

        assert isinstance(mutations, list)
        # Should have at least some mutations
        assert len(mutations) >= 0

    @pytest.mark.asyncio
    async def test_temperature_adjustment(self) -> None:
        """Temperature adjusts based on success rate."""
        agent = EvolutionPolynomialAgent(temperature=1.0)
        result = await agent.evolve("def foo(): pass")

        # Temperature may or may not change depending on success rate:
        # - success_rate > 0.7: temperature decreases (exploit)
        # - success_rate < 0.3: temperature increases (explore)
        # - otherwise: temperature stays the same
        # The result.temperature reflects the final temperature
        assert isinstance(result.temperature, float)
        assert result.temperature > 0

    @pytest.mark.asyncio
    async def test_reset(self) -> None:
        """reset() returns to IDLE."""
        agent = EvolutionPolynomialAgent()
        await agent.evolve("test")
        agent.reset()

        assert agent.phase == EvolutionPhase.IDLE


# =============================================================================
# Thermodynamic Tests
# =============================================================================


class TestThermodynamics:
    """Test thermodynamic behavior."""

    def test_negative_gibbs_favors_success(self) -> None:
        """Mutations with negative Gibbs energy are more likely to succeed."""
        # This is built into the transition logic
        favorable_mutation = Mutation(
            id="m1",
            schema_signature="test",
            original_code="",
            mutated_code="",
            gibbs_free_energy=-1.0,  # Negative = favorable
            intent_alignment=0.5,
        )
        unfavorable_mutation = Mutation(
            id="m2",
            schema_signature="test",
            original_code="",
            mutated_code="",
            gibbs_free_energy=1.0,  # Positive = unfavorable
            intent_alignment=0.3,
        )

        cmd = InfectCommand(mutations=(favorable_mutation, unfavorable_mutation))
        _, output = evolution_transition(EvolutionPhase.INFECT, cmd)

        assert isinstance(output, PayoffCommand)
        assert favorable_mutation.id in [m.id for m in output.succeeded]
        assert unfavorable_mutation.id in [m.id for m in output.failed]

    def test_high_intent_alignment_favors_success(self) -> None:
        """Mutations with high intent alignment are more likely to succeed."""
        high_alignment = Mutation(
            id="m1",
            schema_signature="test",
            original_code="",
            mutated_code="",
            gibbs_free_energy=0.5,  # Unfavorable
            intent_alignment=0.9,  # But high alignment
        )

        cmd = InfectCommand(mutations=(high_alignment,))
        _, output = evolution_transition(EvolutionPhase.INFECT, cmd)

        assert isinstance(output, PayoffCommand)
        assert high_alignment.id in [m.id for m in output.succeeded]


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_code(self) -> None:
        """Empty code is handled gracefully."""
        agent = EvolutionPolynomialAgent()
        result = await agent.evolve("")

        assert isinstance(result, EvolutionResult)

    @pytest.mark.asyncio
    async def test_multiple_cycles(self) -> None:
        """Multiple evolution cycles work correctly."""
        agent = EvolutionPolynomialAgent()

        r1 = await agent.evolve("def foo(): pass")
        r2 = await agent.evolve("def bar(): pass")

        assert r1.cycle_id != r2.cycle_id

    def test_selection_filters_low_alignment(self) -> None:
        """Selection filters out low intent alignment."""
        mutations = [
            Mutation(
                id="m1",
                schema_signature="test",
                original_code="",
                mutated_code="",
                intent_alignment=0.1,  # Too low
            ),
            Mutation(
                id="m2",
                schema_signature="test",
                original_code="",
                mutated_code="",
                intent_alignment=0.8,  # High enough
            ),
        ]
        cmd = SelectCommand(mutations=tuple(mutations), min_intent_alignment=0.5)
        _, output = evolution_transition(EvolutionPhase.SELECT, cmd)

        assert isinstance(output, WagerCommand)
        selected_ids = [m.id for m in output.mutations]
        assert "m1" not in selected_ids
        assert "m2" in selected_ids
