"""Tests for E-gent v2 Core Types."""

import pytest

from agents.e.types import (
    # Phage types
    Phage,
    PhageStatus,
    PhageLineage,
    MutationVector,
    InfectionResult,
    InfectionStatus,
    # Intent
    Intent,
    # Thermodynamics
    ThermodynamicState,
    GibbsEnergy,
    # Cycle
    EvolutionCycleState,
)


# =============================================================================
# MutationVector Tests
# =============================================================================


class TestMutationVector:
    """Tests for MutationVector."""

    def test_creation(self) -> None:
        """Test basic creation."""
        mv = MutationVector(
            schema_signature="loop_to_comprehension",
            original_code="for x in items: result.append(x)",
            mutated_code="result = [x for x in items]",
            enthalpy_delta=-0.3,
            entropy_delta=0.0,
        )

        assert mv.schema_signature == "loop_to_comprehension"
        assert mv.id.startswith("mv_")

    def test_gibbs_free_energy_favorable(self) -> None:
        """Test favorable Gibbs calculation (ΔG < 0)."""
        mv = MutationVector(
            enthalpy_delta=-0.5,  # Simpler
            entropy_delta=0.1,  # More capable
            temperature=1.0,
        )

        # ΔG = -0.5 - 1.0*0.1 = -0.6 (favorable)
        assert mv.gibbs_free_energy == pytest.approx(-0.6)
        assert mv.is_viable

    def test_gibbs_free_energy_unfavorable(self) -> None:
        """Test unfavorable Gibbs calculation (ΔG > 0)."""
        mv = MutationVector(
            enthalpy_delta=0.5,  # More complex
            entropy_delta=0.1,  # Slightly more capable
            temperature=1.0,
        )

        # ΔG = 0.5 - 1.0*0.1 = 0.4 (unfavorable)
        assert mv.gibbs_free_energy == pytest.approx(0.4)
        assert not mv.is_viable

    def test_temperature_effect(self) -> None:
        """Test that temperature affects viability."""
        # At low temperature, enthalpy dominates
        cold_mv = MutationVector(
            enthalpy_delta=0.1,  # Slightly more complex
            entropy_delta=0.5,  # Much more capable
            temperature=0.1,
        )
        # ΔG = 0.1 - 0.1*0.5 = 0.05 (unfavorable at low T)
        assert cold_mv.gibbs_free_energy > 0

        # At high temperature, entropy dominates
        hot_mv = MutationVector(
            enthalpy_delta=0.1,
            entropy_delta=0.5,
            temperature=2.0,
        )
        # ΔG = 0.1 - 2.0*0.5 = -0.9 (favorable at high T)
        assert hot_mv.gibbs_free_energy < 0

    def test_signature_deterministic(self) -> None:
        """Test that signature is deterministic."""
        mv1 = MutationVector(
            schema_signature="test",
            original_code="original",
            mutated_code="mutated",
        )
        mv2 = MutationVector(
            schema_signature="test",
            original_code="original",
            mutated_code="mutated",
        )

        assert mv1.signature == mv2.signature

    def test_signature_different_for_different_code(self) -> None:
        """Test that different code gives different signatures."""
        mv1 = MutationVector(
            schema_signature="test",
            original_code="code_a",
            mutated_code="mutated_a",
        )
        mv2 = MutationVector(
            schema_signature="test",
            original_code="code_b",
            mutated_code="mutated_b",
        )

        assert mv1.signature != mv2.signature


# =============================================================================
# PhageLineage Tests
# =============================================================================


class TestPhageLineage:
    """Tests for PhageLineage."""

    def test_initial_lineage(self) -> None:
        """Test initial lineage creation."""
        lineage = PhageLineage()

        assert lineage.parent_id is None
        assert lineage.generation == 0
        assert lineage.schema_signature == ""

    def test_spawn_child(self) -> None:
        """Test spawning child lineage."""
        parent = PhageLineage(
            generation=5,
            schema_signature="extract_method",
            mutations_applied=["mut1", "mut2"],
        )

        child = parent.spawn_child("inline_variable")

        assert child.generation == 6
        assert child.schema_signature == "inline_variable"
        assert child.mutations_applied == ["mut1", "mut2"]

    def test_lineage_chain(self) -> None:
        """Test multi-generation lineage chain."""
        gen0 = PhageLineage()
        gen1 = gen0.spawn_child("schema_1")
        gen2 = gen1.spawn_child("schema_2")
        gen3 = gen2.spawn_child("schema_3")

        assert gen3.generation == 3


# =============================================================================
# Phage Tests
# =============================================================================


class TestPhage:
    """Tests for Phage."""

    def test_creation(self) -> None:
        """Test basic phage creation."""
        phage = Phage(
            target_module="test_module",
            hypothesis="Refactoring will improve readability",
        )

        assert phage.id.startswith("phage_")
        assert phage.status == PhageStatus.NASCENT
        assert phage.target_module == "test_module"

    def test_status_transitions(self) -> None:
        """Test valid status transitions."""
        phage = Phage()

        assert phage.status == PhageStatus.NASCENT

        phage.status = PhageStatus.MUTATED
        assert phage.status == PhageStatus.MUTATED

        phage.status = PhageStatus.QUOTED
        assert phage.status == PhageStatus.QUOTED

    def test_dna_from_mutation(self) -> None:
        """Test DNA extraction from mutation."""
        mutation = MutationVector(
            schema_signature="test_schema",
            original_code="original",
            mutated_code="mutated",
        )
        phage = Phage(mutation=mutation)

        assert phage.dna == mutation.signature
        assert phage.dna != ""

    def test_dna_empty_without_mutation(self) -> None:
        """Test DNA is empty without mutation."""
        phage = Phage()
        assert phage.dna == ""

    def test_spawn_child(self) -> None:
        """Test spawning child phage."""
        parent = Phage(
            target_module="module_a",
            lineage=PhageLineage(generation=2),
        )
        parent.lineage.mutations_applied.append("parent_mutation")

        child_mutation = MutationVector(schema_signature="child_schema")
        child = parent.spawn(child_mutation)

        assert child.target_module == "module_a"
        assert child.lineage.parent_id == parent.id
        assert child.lineage.generation == 3
        assert child.mutation == child_mutation
        assert child.status == PhageStatus.MUTATED

    def test_phage_with_economics(self) -> None:
        """Test phage with economic properties."""
        phage = Phage(
            stake=100,
            bet_id="bet_123",
            market_odds=2.5,
        )

        assert phage.stake == 100
        assert phage.bet_id == "bet_123"
        assert phage.market_odds == 2.5


# =============================================================================
# InfectionResult Tests
# =============================================================================


class TestInfectionResult:
    """Tests for InfectionResult."""

    def test_success_result(self) -> None:
        """Test successful infection result."""
        result = InfectionResult(
            phage_id="phage_001",
            status=InfectionStatus.SUCCESS,
            syntax_valid=True,
            types_valid=True,
            tests_passed=True,
            test_count=10,
            test_failures=0,
        )

        assert result.status == InfectionStatus.SUCCESS
        assert result.tests_passed
        assert result.test_failures == 0

    def test_failed_result(self) -> None:
        """Test failed infection result."""
        result = InfectionResult(
            phage_id="phage_002",
            status=InfectionStatus.FAILED,
            syntax_valid=True,
            types_valid=False,
            tests_passed=False,
            type_errors=5,
            error_message="Type check failed",
        )

        assert result.status == InfectionStatus.FAILED
        assert result.type_errors == 5
        assert result.error_message is not None

    def test_rollback_result(self) -> None:
        """Test rollback infection result."""
        result = InfectionResult(
            phage_id="phage_003",
            status=InfectionStatus.ROLLBACK,
            rollback_reason="Tests failed after apply",
        )

        assert result.status == InfectionStatus.ROLLBACK
        assert result.rollback_reason is not None


# =============================================================================
# Intent Tests
# =============================================================================


class TestIntent:
    """Tests for Intent."""

    def test_creation(self) -> None:
        """Test intent creation."""
        intent = Intent(
            embedding=[0.1, 0.2, 0.3],
            source="user",
            description="Improve error handling",
        )

        assert intent.source == "user"
        assert intent.confidence == 1.0

    def test_alignment_identical(self) -> None:
        """Test alignment with identical embedding."""
        intent = Intent(
            embedding=[1.0, 0.0, 0.0],
            source="user",
            description="Test",
        )

        alignment = intent.alignment_with([1.0, 0.0, 0.0])
        assert alignment == pytest.approx(1.0)

    def test_alignment_orthogonal(self) -> None:
        """Test alignment with orthogonal embedding."""
        intent = Intent(
            embedding=[1.0, 0.0],
            source="user",
            description="Test",
        )

        alignment = intent.alignment_with([0.0, 1.0])
        assert alignment == pytest.approx(0.0)

    def test_alignment_opposite(self) -> None:
        """Test alignment with opposite embedding."""
        intent = Intent(
            embedding=[1.0, 1.0],
            source="user",
            description="Test",
        )

        alignment = intent.alignment_with([-1.0, -1.0])
        assert alignment == pytest.approx(-1.0)

    def test_alignment_different_dimensions(self) -> None:
        """Test alignment with different dimension embeddings returns 0."""
        intent = Intent(
            embedding=[1.0, 2.0, 3.0],
            source="user",
            description="Test",
        )

        alignment = intent.alignment_with([1.0, 2.0])
        assert alignment == 0.0


# =============================================================================
# GibbsEnergy Tests
# =============================================================================


class TestGibbsEnergy:
    """Tests for GibbsEnergy."""

    def test_favorable_energy(self) -> None:
        """Test favorable Gibbs energy."""
        gibbs = GibbsEnergy(
            enthalpy_delta=-0.5,
            entropy_delta=0.1,
            temperature=1.0,
        )

        assert gibbs.delta_g == pytest.approx(-0.6)
        assert gibbs.is_favorable
        assert gibbs.favorability_margin < 0

    def test_unfavorable_energy(self) -> None:
        """Test unfavorable Gibbs energy."""
        gibbs = GibbsEnergy(
            enthalpy_delta=0.5,
            entropy_delta=0.0,
            temperature=1.0,
        )

        assert gibbs.delta_g == pytest.approx(0.5)
        assert not gibbs.is_favorable
        assert gibbs.favorability_margin > 0


# =============================================================================
# ThermodynamicState Tests
# =============================================================================


class TestThermodynamicState:
    """Tests for ThermodynamicState."""

    def test_initial_state(self) -> None:
        """Test initial thermodynamic state."""
        state = ThermodynamicState()

        assert state.temperature == 1.0
        assert state.success_rate == 0.5
        assert state.total_gibbs_change == 0.0

    def test_record_mutation(self) -> None:
        """Test recording mutation outcomes."""
        state = ThermodynamicState()

        gibbs = GibbsEnergy(
            enthalpy_delta=-0.5,
            entropy_delta=0.1,
            temperature=1.0,
        )

        state.record_mutation(gibbs, succeeded=True)

        assert state.total_enthalpy_change == -0.5
        assert state.total_entropy_change == 0.1
        assert state.total_gibbs_change == pytest.approx(-0.6)
        assert state.success_rate > 0.5  # Success increases rate

    def test_cooling(self) -> None:
        """Test temperature cooling."""
        state = ThermodynamicState(temperature=2.0, cooling_rate=0.1)

        state.cool()

        assert state.temperature < 2.0
        assert state.temperature > state.min_temperature

    def test_cooling_floor(self) -> None:
        """Test temperature doesn't go below floor."""
        state = ThermodynamicState(
            temperature=0.15,
            cooling_rate=0.5,
            min_temperature=0.1,
        )

        state.cool()

        assert state.temperature >= state.min_temperature

    def test_heating(self) -> None:
        """Test temperature heating."""
        state = ThermodynamicState(temperature=1.0)

        state.heat(amount=0.5)

        assert state.temperature > 1.0

    def test_heating_ceiling(self) -> None:
        """Test temperature doesn't go above ceiling."""
        state = ThermodynamicState(
            temperature=9.5,
            max_temperature=10.0,
        )

        state.heat(amount=0.5)

        assert state.temperature <= state.max_temperature


# =============================================================================
# EvolutionCycleState Tests
# =============================================================================


class TestEvolutionCycleState:
    """Tests for EvolutionCycleState."""

    def test_initial_state(self) -> None:
        """Test initial cycle state."""
        cycle = EvolutionCycleState()

        assert cycle.cycle_id.startswith("cycle_")
        assert cycle.current_phase == "sun"
        assert len(cycle.phages) == 0

    def test_success_rate(self) -> None:
        """Test success rate calculation."""
        cycle = EvolutionCycleState(
            phages_succeeded=7,
            phages_failed=2,
            phages_rejected=1,
        )

        assert cycle.success_rate == pytest.approx(0.7)

    def test_success_rate_zero(self) -> None:
        """Test success rate with no phages."""
        cycle = EvolutionCycleState()
        assert cycle.success_rate == 0.0

    def test_roi_positive(self) -> None:
        """Test positive ROI."""
        cycle = EvolutionCycleState(
            tokens_staked=100,
            tokens_won=150,
            tokens_lost=30,
        )

        # ROI = (150 - 30) / (100 + 30) = 120/130 ≈ 0.923
        assert cycle.roi > 0

    def test_roi_negative(self) -> None:
        """Test negative ROI."""
        cycle = EvolutionCycleState(
            tokens_staked=100,
            tokens_won=20,
            tokens_lost=80,
        )

        # ROI = (20 - 80) / (100 + 80) = -60/180 ≈ -0.333
        assert cycle.roi < 0

    def test_roi_zero_stake(self) -> None:
        """Test ROI with zero stake."""
        cycle = EvolutionCycleState(
            tokens_staked=0,
            tokens_lost=0,
        )

        assert cycle.roi == 0.0

    def test_phase_tracking(self) -> None:
        """Test phase tracking."""
        cycle = EvolutionCycleState()

        cycle.current_phase = "mutate"
        assert cycle.current_phase == "mutate"

        cycle.current_phase = "select"
        assert cycle.current_phase == "select"
