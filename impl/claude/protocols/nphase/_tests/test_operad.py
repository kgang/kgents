"""
Tests for NPHASE_OPERAD.

Tests the N-Phase development cycle operad: operations, laws, and transitions.
"""

import pytest
from agents.operad.core import LawStatus, OperadRegistry
from protocols.nphase.operad import (
    DETAILED_TO_COMPRESSED,
    NPHASE_LAWS,
    NPHASE_OPERAD,
    NPHASE_OPERATIONS,
    PHASE_FAMILIES,
    NPhase,
    NPhaseInput,
    NPhaseOutput,
    NPhaseState,
    get_compressed_phase,
    get_detailed_phases,
    is_valid_transition,
    next_phase,
)


class TestNPhaseEnum:
    """Tests for NPhase enum."""

    def test_phase_values(self) -> None:
        """Test all three phases exist."""
        assert NPhase.SENSE is not None
        assert NPhase.ACT is not None
        assert NPhase.REFLECT is not None

    def test_phase_count(self) -> None:
        """Test exactly three phases."""
        assert len(NPhase) == 3


class TestPhaseFamilies:
    """Tests for phase family mappings."""

    def test_sense_family(self) -> None:
        """Test UNDERSTAND includes PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE."""
        expected = ["PLAN", "RESEARCH", "DEVELOP", "STRATEGIZE", "CROSS-SYNERGIZE"]
        assert PHASE_FAMILIES[NPhase.UNDERSTAND] == expected

    def test_act_family(self) -> None:
        """Test ACT includes implementation phases."""
        expected = ["IMPLEMENT", "QA", "TEST"]
        assert PHASE_FAMILIES[NPhase.ACT] == expected

    def test_reflect_family(self) -> None:
        """Test REFLECT includes retrospective phases."""
        assert PHASE_FAMILIES[NPhase.REFLECT] == ["EDUCATE", "MEASURE", "REFLECT"]

    def test_all_11_phases_covered(self) -> None:
        """Test all 11 detailed phases are mapped."""
        all_detailed = []
        for phases in PHASE_FAMILIES.values():
            all_detailed.extend(phases)
        assert len(all_detailed) == 11

    def test_reverse_mapping(self) -> None:
        """Test DETAILED_TO_COMPRESSED reverse mapping."""
        assert DETAILED_TO_COMPRESSED["PLAN"] == NPhase.UNDERSTAND
        assert DETAILED_TO_COMPRESSED["IMPLEMENT"] == NPhase.ACT
        assert DETAILED_TO_COMPRESSED["MEASURE"] == NPhase.REFLECT


class TestNPhaseState:
    """Tests for NPhaseState dataclass."""

    def test_default_state(self) -> None:
        """Test default state initialization."""
        state = NPhaseState()
        assert state.current_phase == NPhase.UNDERSTAND
        assert state.cycle_count == 0
        assert all(phase in state.phase_outputs for phase in NPhase)

    def test_custom_state(self) -> None:
        """Test custom state initialization."""
        state = NPhaseState(current_phase=NPhase.ACT, cycle_count=3)
        assert state.current_phase == NPhase.ACT
        assert state.cycle_count == 3


class TestNPhaseOperations:
    """Tests for NPHASE operations."""

    def test_sense_operation_exists(self) -> None:
        """Test sense operation is defined."""
        assert "sense" in NPHASE_OPERATIONS
        op = NPHASE_OPERATIONS["sense"]
        assert op.name == "sense"
        assert op.arity == 1

    def test_act_operation_exists(self) -> None:
        """Test act operation is defined."""
        assert "act" in NPHASE_OPERATIONS
        op = NPHASE_OPERATIONS["act"]
        assert op.name == "act"
        assert op.arity == 1

    def test_reflect_operation_exists(self) -> None:
        """Test reflect operation is defined."""
        assert "reflect" in NPHASE_OPERATIONS
        op = NPHASE_OPERATIONS["reflect"]
        assert op.name == "reflect"
        assert op.arity == 1

    def test_cycle_operation_exists(self) -> None:
        """Test cycle operation is defined."""
        assert "cycle" in NPHASE_OPERATIONS
        op = NPHASE_OPERATIONS["cycle"]
        assert op.name == "cycle"
        assert op.arity == 3  # Takes sense, act, reflect agents


class TestNPhaseLaws:
    """Tests for NPHASE laws."""

    def test_phase_order_law_exists(self) -> None:
        """Test phase_order law is defined."""
        law_names = [law.name for law in NPHASE_LAWS]
        assert "phase_order" in law_names

    def test_cycle_law_exists(self) -> None:
        """Test cycle law is defined."""
        law_names = [law.name for law in NPHASE_LAWS]
        assert "cycle" in law_names

    def test_identity_law_exists(self) -> None:
        """Test identity law is defined."""
        law_names = [law.name for law in NPHASE_LAWS]
        assert "identity" in law_names


class TestNPhaseOperad:
    """Tests for NPHASE_OPERAD instance."""

    def test_operad_name(self) -> None:
        """Test operad has correct name."""
        assert NPHASE_OPERAD.name == "NPHASE"

    def test_operad_has_operations(self) -> None:
        """Test operad has all operations."""
        assert "sense" in NPHASE_OPERAD.operations
        assert "act" in NPHASE_OPERAD.operations
        assert "reflect" in NPHASE_OPERAD.operations
        assert "cycle" in NPHASE_OPERAD.operations

    def test_operad_has_laws(self) -> None:
        """Test operad has laws."""
        assert len(NPHASE_OPERAD.laws) == 3

    def test_operad_registered(self) -> None:
        """Test NPHASE_OPERAD is registered in OperadRegistry."""
        registered = OperadRegistry.get("NPHASE")
        assert registered is not None
        assert registered.name == "NPHASE"


class TestTransitionValidation:
    """Tests for phase transition validation."""

    def test_sense_to_act_valid(self) -> None:
        """Test SENSE -> ACT is valid."""
        assert is_valid_transition(NPhase.SENSE, NPhase.ACT)

    def test_act_to_reflect_valid(self) -> None:
        """Test ACT -> REFLECT is valid."""
        assert is_valid_transition(NPhase.ACT, NPhase.REFLECT)

    def test_reflect_to_sense_valid(self) -> None:
        """Test REFLECT -> SENSE is valid (cycle)."""
        assert is_valid_transition(NPhase.REFLECT, NPhase.SENSE)

    def test_same_phase_valid(self) -> None:
        """Test staying in same phase is valid."""
        assert is_valid_transition(NPhase.SENSE, NPhase.SENSE)
        assert is_valid_transition(NPhase.ACT, NPhase.ACT)
        assert is_valid_transition(NPhase.REFLECT, NPhase.REFLECT)

    def test_sense_to_reflect_invalid(self) -> None:
        """Test SENSE -> REFLECT is invalid (skips ACT)."""
        assert not is_valid_transition(NPhase.SENSE, NPhase.REFLECT)

    def test_act_to_sense_invalid(self) -> None:
        """Test ACT -> SENSE is invalid (backward)."""
        assert not is_valid_transition(NPhase.ACT, NPhase.SENSE)

    def test_reflect_to_act_invalid(self) -> None:
        """Test REFLECT -> ACT is invalid (backward)."""
        assert not is_valid_transition(NPhase.REFLECT, NPhase.ACT)


class TestNextPhase:
    """Tests for next_phase function."""

    def test_sense_next_is_act(self) -> None:
        """Test next after SENSE is ACT."""
        assert next_phase(NPhase.SENSE) == NPhase.ACT

    def test_act_next_is_reflect(self) -> None:
        """Test next after ACT is REFLECT."""
        assert next_phase(NPhase.ACT) == NPhase.REFLECT

    def test_reflect_next_is_sense(self) -> None:
        """Test next after REFLECT is SENSE (cycle)."""
        assert next_phase(NPhase.REFLECT) == NPhase.SENSE


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_compressed_phase(self) -> None:
        """Test get_compressed_phase function."""
        assert get_compressed_phase("PLAN") == NPhase.SENSE
        assert get_compressed_phase("IMPLEMENT") == NPhase.ACT
        assert get_compressed_phase("REFLECT") == NPhase.REFLECT
        assert get_compressed_phase("NONEXISTENT") is None

    def test_get_detailed_phases(self) -> None:
        """Test get_detailed_phases function."""
        sense_phases = get_detailed_phases(NPhase.SENSE)
        assert "PLAN" in sense_phases
        assert "RESEARCH" in sense_phases
        assert "DEVELOP" in sense_phases

        act_phases = get_detailed_phases(NPhase.ACT)
        assert "IMPLEMENT" in act_phases
        assert "TEST" in act_phases


class TestLawVerification:
    """Tests for law verification functions."""

    def test_phase_order_passes_for_sense(self) -> None:
        """Test phase_order passes when in SENSE (no requirements)."""
        state = NPhaseState(current_phase=NPhase.SENSE)
        input_ = NPhaseInput(content="test")

        # Get the phase_order law
        phase_order_law = next(law for law in NPHASE_LAWS if law.name == "phase_order")

        result = phase_order_law.verify(NPHASE_OPERAD, state, input_)
        assert result.status == LawStatus.PASSED

    def test_phase_order_fails_for_act_without_sense(self) -> None:
        """Test phase_order fails when ACT has no prior SENSE output."""
        state = NPhaseState(current_phase=NPhase.ACT)
        # No SENSE outputs
        input_ = NPhaseInput(content="test")

        phase_order_law = next(law for law in NPHASE_LAWS if law.name == "phase_order")

        result = phase_order_law.verify(NPHASE_OPERAD, state, input_)
        assert result.status == LawStatus.FAILED

    def test_phase_order_passes_for_act_with_sense(self) -> None:
        """Test phase_order passes when ACT has prior SENSE output."""
        state = NPhaseState(current_phase=NPhase.ACT)
        state.phase_outputs[NPhase.SENSE] = ["some output"]
        input_ = NPhaseInput(content="test")

        phase_order_law = next(law for law in NPHASE_LAWS if law.name == "phase_order")

        result = phase_order_law.verify(NPHASE_OPERAD, state, input_)
        assert result.status == LawStatus.PASSED

    def test_cycle_law_passes(self) -> None:
        """Test cycle law passes (REFLECT can trigger SENSE)."""
        state = NPhaseState(current_phase=NPhase.REFLECT)
        input_ = NPhaseInput(content="test")

        cycle_law = next(law for law in NPHASE_LAWS if law.name == "cycle")

        result = cycle_law.verify(NPHASE_OPERAD, state, input_)
        assert result.status == LawStatus.PASSED
