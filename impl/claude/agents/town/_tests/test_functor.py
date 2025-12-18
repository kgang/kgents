"""
Tests for TOWN → NPHASE Functor.

Verifies functor laws (identity, composition preservation).
"""

import pytest

from agents.operad.core import LawStatus
from agents.town.functor import (
    TOWN_TO_NPHASE_MAP,
    FunctorResult,
    apply_functor,
    classify_town_operation,
    compose_via_functor,
    get_town_ops_by_phase,
    summarize_functor,
    town_to_nphase_functor,
    verify_all_functor_laws,
    verify_composition_law,
    verify_identity_law,
)
from protocols.nphase.operad import NPhase


class TestTownToNphaseFunctor:
    """Tests for the basic functor mapping."""

    def test_greet_maps_to_act(self) -> None:
        """Test greet maps to ACT phase."""
        assert town_to_nphase_functor("greet") == NPhase.ACT

    def test_gossip_maps_to_act(self) -> None:
        """Test gossip maps to ACT phase."""
        assert town_to_nphase_functor("gossip") == NPhase.ACT

    def test_trade_maps_to_act(self) -> None:
        """Test trade maps to ACT phase."""
        assert town_to_nphase_functor("trade") == NPhase.ACT

    def test_dispute_maps_to_act(self) -> None:
        """Test dispute maps to ACT phase."""
        assert town_to_nphase_functor("dispute") == NPhase.ACT

    def test_celebrate_maps_to_act(self) -> None:
        """Test celebrate maps to ACT phase."""
        assert town_to_nphase_functor("celebrate") == NPhase.ACT

    def test_teach_maps_to_act(self) -> None:
        """Test teach maps to ACT phase."""
        assert town_to_nphase_functor("teach") == NPhase.ACT

    def test_solo_maps_to_reflect(self) -> None:
        """Test solo maps to REFLECT phase."""
        assert town_to_nphase_functor("solo") == NPhase.REFLECT

    def test_mourn_maps_to_reflect(self) -> None:
        """Test mourn maps to REFLECT phase."""
        assert town_to_nphase_functor("mourn") == NPhase.REFLECT

    def test_id_maps_to_sense(self) -> None:
        """Test identity maps to SENSE (neutral phase)."""
        assert town_to_nphase_functor("id") == NPhase.SENSE

    def test_trace_maps_to_sense(self) -> None:
        """Test trace (observation) maps to SENSE."""
        assert town_to_nphase_functor("trace") == NPhase.SENSE

    def test_unmapped_raises(self) -> None:
        """Test unmapped operation raises KeyError."""
        with pytest.raises(KeyError):
            town_to_nphase_functor("nonexistent")


class TestApplyFunctor:
    """Tests for apply_functor with full metadata."""

    def test_apply_functor_greet(self) -> None:
        """Test apply_functor returns FunctorResult."""
        result = apply_functor("greet")
        assert isinstance(result, FunctorResult)
        assert result.source_op == "greet"
        assert result.target_phase == NPhase.ACT
        assert "source_signature" in result.metadata

    def test_apply_functor_solo(self) -> None:
        """Test apply_functor for solo operation."""
        result = apply_functor("solo")
        assert result.target_phase == NPhase.REFLECT

    def test_apply_functor_unknown_raises(self) -> None:
        """Test apply_functor raises for unknown operation."""
        with pytest.raises(KeyError):
            apply_functor("nonexistent")


class TestComposeViaFunctor:
    """Tests for composition through the functor."""

    def test_act_to_act_valid(self) -> None:
        """Test ACT >> ACT is valid (same phase)."""
        phase_a, phase_b, is_valid = compose_via_functor("greet", "gossip")
        assert phase_a == NPhase.ACT
        assert phase_b == NPhase.ACT
        assert is_valid  # Same phase is always valid

    def test_act_to_reflect_valid(self) -> None:
        """Test ACT >> REFLECT is valid transition."""
        phase_a, phase_b, is_valid = compose_via_functor("greet", "solo")
        assert phase_a == NPhase.ACT
        assert phase_b == NPhase.REFLECT
        assert is_valid

    def test_reflect_to_reflect_valid(self) -> None:
        """Test REFLECT >> REFLECT is valid (same phase)."""
        phase_a, phase_b, is_valid = compose_via_functor("solo", "mourn")
        assert phase_a == NPhase.REFLECT
        assert phase_b == NPhase.REFLECT
        assert is_valid

    def test_reflect_to_act_invalid(self) -> None:
        """Test REFLECT >> ACT is invalid (backward)."""
        phase_a, phase_b, is_valid = compose_via_functor("solo", "greet")
        assert phase_a == NPhase.REFLECT
        assert phase_b == NPhase.ACT
        assert not is_valid  # Can't go backward


class TestFunctorLaws:
    """Tests for functor law verification."""

    def test_identity_law_passes(self) -> None:
        """Test identity law verification passes."""
        result = verify_identity_law()
        assert result.law_name == "functor_identity"
        assert result.status == LawStatus.PASSED

    def test_composition_law_act_act(self) -> None:
        """Test composition law for ACT >> ACT."""
        result = verify_composition_law("greet", "gossip")
        assert result.status == LawStatus.PASSED

    def test_composition_law_act_reflect(self) -> None:
        """Test composition law for ACT >> REFLECT."""
        result = verify_composition_law("greet", "solo")
        assert result.status == LawStatus.PASSED

    def test_composition_law_reflect_act_fails(self) -> None:
        """Test composition law fails for REFLECT >> ACT."""
        result = verify_composition_law("solo", "greet")
        assert result.status == LawStatus.FAILED

    def test_verify_all_functor_laws(self) -> None:
        """Test verifying all functor laws returns list."""
        results = verify_all_functor_laws()
        assert len(results) >= 5  # 1 identity + 4 composition tests
        assert all(hasattr(r, "status") for r in results)


class TestPhaseClassification:
    """Tests for phase classification utilities."""

    def test_get_town_ops_by_phase_act(self) -> None:
        """Test getting ACT phase operations."""
        act_ops = get_town_ops_by_phase(NPhase.ACT)
        assert "greet" in act_ops
        assert "gossip" in act_ops
        assert "trade" in act_ops

    def test_get_town_ops_by_phase_reflect(self) -> None:
        """Test getting REFLECT phase operations."""
        reflect_ops = get_town_ops_by_phase(NPhase.REFLECT)
        assert "solo" in reflect_ops
        assert "mourn" in reflect_ops

    def test_get_town_ops_by_phase_sense(self) -> None:
        """Test getting SENSE phase operations."""
        sense_ops = get_town_ops_by_phase(NPhase.SENSE)
        assert "trace" in sense_ops or "branch" in sense_ops


class TestClassifyTownOperation:
    """Tests for operation classification."""

    def test_classify_greet(self) -> None:
        """Test classifying greet operation."""
        info = classify_town_operation("greet")
        assert info["phase"] == "ACT"
        assert info["is_social"] is True
        assert info["is_reflective"] is False

    def test_classify_solo(self) -> None:
        """Test classifying solo operation."""
        info = classify_town_operation("solo")
        assert info["phase"] == "REFLECT"
        assert info["is_social"] is False
        assert info["is_reflective"] is True

    def test_classify_mourn(self) -> None:
        """Test classifying mourn operation."""
        info = classify_town_operation("mourn")
        assert info["phase"] == "REFLECT"
        assert info["is_social"] is True  # Collective mourning
        assert info["is_reflective"] is True

    def test_classify_unknown(self) -> None:
        """Test classifying unknown operation returns error."""
        info = classify_town_operation("nonexistent")
        assert "error" in info


class TestSummarizeFunctor:
    """Tests for functor summary."""

    def test_summarize_functor(self) -> None:
        """Test functor summary has all phases."""
        summary = summarize_functor()
        assert "total_mapped" in summary
        assert "SENSE" in summary
        assert "ACT" in summary
        assert "REFLECT" in summary

    def test_summarize_counts(self) -> None:
        """Test summary counts are positive."""
        summary = summarize_functor()
        assert summary["ACT"]["count"] > 0
        assert summary["REFLECT"]["count"] > 0

    def test_total_matches_sum(self) -> None:
        """Test total equals sum of phases."""
        summary = summarize_functor()
        total = summary["SENSE"]["count"] + summary["ACT"]["count"] + summary["REFLECT"]["count"]
        assert summary["total_mapped"] == total
