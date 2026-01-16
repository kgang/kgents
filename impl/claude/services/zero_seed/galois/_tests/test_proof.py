"""
Tests for Galois-Witnessed Proof System.

Validates:
1. Evidence tier classification by loss bounds
2. Witness mode triage
3. GaloisWitnessedProof coherence properties
4. ProofLossDecomposition normalization
5. Alternative (ghost proof) behavior
6. ProofValidation assessment
7. ContradictionAnalysis super-additivity

See: spec/protocols/zero-seed1/proof.md
"""

from __future__ import annotations

import pytest

from services.zero_seed.galois.proof import (
    Alternative,
    CoherenceError,
    ContradictionAnalysis,
    EvidenceTier,
    GaloisWitnessedProof,
    ProofLossDecomposition,
    ProofValidation,
    TierBounds,
    WitnessMode,
    classify_by_loss,
    select_witness_mode_from_loss,
)

# =============================================================================
# Evidence Tier Classification Tests
# =============================================================================


class TestClassifyByLoss:
    """Test classify_by_loss function."""

    def test_categorical_tier(self) -> None:
        """Loss < 0.1 should be CATEGORICAL."""
        assert classify_by_loss(0.0) == EvidenceTier.CATEGORICAL
        assert classify_by_loss(0.05) == EvidenceTier.CATEGORICAL
        assert classify_by_loss(0.09) == EvidenceTier.CATEGORICAL

    def test_empirical_tier(self) -> None:
        """Loss in [0.1, 0.3) should be EMPIRICAL."""
        assert classify_by_loss(0.1) == EvidenceTier.EMPIRICAL
        assert classify_by_loss(0.2) == EvidenceTier.EMPIRICAL
        assert classify_by_loss(0.29) == EvidenceTier.EMPIRICAL

    def test_aesthetic_tier(self) -> None:
        """Loss in [0.3, 0.5) should be AESTHETIC."""
        assert classify_by_loss(0.3) == EvidenceTier.AESTHETIC
        assert classify_by_loss(0.4) == EvidenceTier.AESTHETIC
        assert classify_by_loss(0.49) == EvidenceTier.AESTHETIC

    def test_somatic_tier(self) -> None:
        """Loss in [0.5, 0.7) should be SOMATIC."""
        assert classify_by_loss(0.5) == EvidenceTier.SOMATIC
        assert classify_by_loss(0.6) == EvidenceTier.SOMATIC
        assert classify_by_loss(0.69) == EvidenceTier.SOMATIC

    def test_chaotic_tier(self) -> None:
        """Loss >= 0.7 should be CHAOTIC."""
        assert classify_by_loss(0.7) == EvidenceTier.CHAOTIC
        assert classify_by_loss(0.85) == EvidenceTier.CHAOTIC
        assert classify_by_loss(1.0) == EvidenceTier.CHAOTIC


# =============================================================================
# Witness Mode Triage Tests
# =============================================================================


class TestSelectWitnessMode:
    """Test witness mode selection by loss."""

    def test_single_mode_low_loss(self) -> None:
        """Loss < 0.1 should be SINGLE (immediate witness)."""
        assert select_witness_mode_from_loss(0.0) == WitnessMode.SINGLE
        assert select_witness_mode_from_loss(0.05) == WitnessMode.SINGLE
        assert select_witness_mode_from_loss(0.09) == WitnessMode.SINGLE

    def test_session_mode_medium_loss(self) -> None:
        """Loss in [0.1, 0.4) should be SESSION (batch)."""
        assert select_witness_mode_from_loss(0.1) == WitnessMode.SESSION
        assert select_witness_mode_from_loss(0.25) == WitnessMode.SESSION
        assert select_witness_mode_from_loss(0.39) == WitnessMode.SESSION

    def test_lazy_mode_high_loss(self) -> None:
        """Loss >= 0.4 should be LAZY (deferred)."""
        assert select_witness_mode_from_loss(0.4) == WitnessMode.LAZY
        assert select_witness_mode_from_loss(0.6) == WitnessMode.LAZY
        assert select_witness_mode_from_loss(1.0) == WitnessMode.LAZY


# =============================================================================
# TierBounds Tests
# =============================================================================


class TestTierBounds:
    """Test configurable tier bounds."""

    def test_default_bounds(self) -> None:
        """Default bounds should match spec."""
        bounds = TierBounds()
        assert bounds.categorical_max == 0.1
        assert bounds.empirical_max == 0.3
        assert bounds.aesthetic_max == 0.5
        assert bounds.somatic_max == 0.7

    def test_custom_bounds(self) -> None:
        """Custom bounds should classify differently."""
        bounds = TierBounds(
            categorical_max=0.2,
            empirical_max=0.4,
            aesthetic_max=0.6,
            somatic_max=0.8,
        )
        # 0.15 would be EMPIRICAL with default, but CATEGORICAL with custom
        assert bounds.get_tier(0.15) == EvidenceTier.CATEGORICAL

    def test_rationale_exists_for_all_tiers(self) -> None:
        """All tiers should have rationales."""
        bounds = TierBounds()
        for tier in EvidenceTier:
            rationale = bounds.get_rationale(tier)
            assert rationale
            assert len(rationale) > 50  # Should be substantive


# =============================================================================
# ProofLossDecomposition Tests
# =============================================================================


class TestProofLossDecomposition:
    """Test loss decomposition functionality."""

    def test_total_computation(self) -> None:
        """Total should be sum of components."""
        decomp = ProofLossDecomposition(
            data_loss=0.05,
            warrant_loss=0.10,
            claim_loss=0.03,
            backing_loss=0.07,
            qualifier_loss=0.02,
            rebuttal_loss=0.03,
            composition_loss=0.05,
        )
        assert abs(decomp.total - 0.35) < 0.001

    def test_normalization(self) -> None:
        """Normalized decomposition should sum to 1.0."""
        decomp = ProofLossDecomposition(
            data_loss=0.2,
            warrant_loss=0.3,
        )
        normalized = decomp.normalized()
        assert abs(normalized.total - 1.0) < 0.001

    def test_zero_total_normalization(self) -> None:
        """Zero total should return same decomposition."""
        decomp = ProofLossDecomposition()  # All zeros
        normalized = decomp.normalized()
        assert normalized.total == 0

    def test_to_dict_format(self) -> None:
        """to_dict should use correct component names."""
        decomp = ProofLossDecomposition(
            data_loss=0.1,
            warrant_loss=0.2,
        )
        d = decomp.to_dict()
        assert "data" in d
        assert "warrant" in d
        assert "rebuttals" in d  # Not "rebuttal_loss"
        assert d["data"] == 0.1
        assert d["warrant"] == 0.2

    def test_high_loss_components(self) -> None:
        """Should identify high-loss components."""
        decomp = ProofLossDecomposition(
            data_loss=0.05,  # low
            warrant_loss=0.35,  # high
            backing_loss=0.40,  # high
        )
        high = decomp.high_loss_components(threshold=0.3)
        assert len(high) == 2
        assert ("warrant", 0.35) in high
        assert ("backing", 0.40) in high


# =============================================================================
# Alternative (Ghost Proof) Tests
# =============================================================================


class TestAlternative:
    """Test ghost alternative functionality."""

    def test_coherence_property(self) -> None:
        """Coherence should be 1 - loss."""
        alt = Alternative(
            description="Test alternative",
            galois_loss=0.3,
            deferral_cost=0.1,
            rationale="Testing",
        )
        assert alt.coherence == 0.7

    def test_is_better_than(self) -> None:
        """Should detect when alternative is better."""
        alt = Alternative(
            description="Better alternative",
            galois_loss=0.15,
            deferral_cost=0.05,
            rationale="Lower loss",
        )
        assert alt.is_better_than(0.25)  # 0.15 < 0.25
        assert not alt.is_better_than(0.10)  # 0.15 > 0.10


# =============================================================================
# GaloisWitnessedProof Tests
# =============================================================================


class TestGaloisWitnessedProof:
    """Test GaloisWitnessedProof functionality."""

    @pytest.fixture
    def sample_proof(self) -> GaloisWitnessedProof:
        """Create sample proof for testing."""
        return GaloisWitnessedProof(
            data="Tests pass (100% coverage)",
            warrant="Passing tests indicate correctness",
            claim="The refactoring preserves behavior",
            backing="CLAUDE.md: 'DI > mocking' pattern",
            qualifier="almost certainly",
            rebuttals=("unless API changes",),
            tier=EvidenceTier.EMPIRICAL,
            principles=("composable", "tasteful"),
            galois_loss=0.18,
            loss_decomposition={"warrant": 0.08, "backing": 0.10},
        )

    def test_coherence_property(self, sample_proof: GaloisWitnessedProof) -> None:
        """Coherence should be 1 - loss."""
        assert sample_proof.coherence == pytest.approx(0.82)

    def test_tier_from_loss(self, sample_proof: GaloisWitnessedProof) -> None:
        """tier_from_loss should classify by loss value."""
        assert sample_proof.tier_from_loss == EvidenceTier.EMPIRICAL
        # Loss 0.18 is in [0.1, 0.3) -> EMPIRICAL

    def test_witness_mode(self, sample_proof: GaloisWitnessedProof) -> None:
        """witness_mode should triage by loss."""
        assert sample_proof.witness_mode == WitnessMode.SESSION
        # Loss 0.18 is in [0.1, 0.4) -> SESSION

    def test_rebuttals_from_loss_none_if_low(self, sample_proof: GaloisWitnessedProof) -> None:
        """Should not generate rebuttals for low-loss components."""
        # Both warrant (0.08) and backing (0.10) are < 0.3
        assert len(sample_proof.rebuttals_from_loss) == 0

    def test_rebuttals_from_loss_generates_for_high(self) -> None:
        """Should generate rebuttals for high-loss components."""
        proof = GaloisWitnessedProof(
            data="Test",
            warrant="Test",
            claim="Test",
            galois_loss=0.5,
            loss_decomposition={"warrant": 0.35, "backing": 0.15},
        )
        generated = proof.rebuttals_from_loss
        assert len(generated) == 1
        assert "warrant" in generated[0]
        assert "0.35" in generated[0]

    def test_all_rebuttals_combines(self) -> None:
        """all_rebuttals should combine explicit and ghost rebuttals."""
        proof = GaloisWitnessedProof(
            data="Test",
            warrant="Test",
            claim="Test",
            rebuttals=("explicit rebuttal",),
            galois_loss=0.5,
            loss_decomposition={"warrant": 0.40},
        )
        all_reb = proof.all_rebuttals
        assert len(all_reb) == 2  # 1 explicit + 1 ghost
        assert "explicit rebuttal" in all_reb
        assert any("warrant" in r for r in all_reb)

    def test_immutability(self, sample_proof: GaloisWitnessedProof) -> None:
        """Proof should be frozen."""
        with pytest.raises(Exception):  # Pydantic raises ValidationError on mutation
            sample_proof.data = "New data"  # type: ignore

    def test_with_alternatives(self, sample_proof: GaloisWitnessedProof) -> None:
        """with_alternatives should return new proof with alternatives."""
        alt = Alternative(
            description="Alternative",
            galois_loss=0.15,
            deferral_cost=0.03,
            rationale="Testing",
        )
        new_proof = sample_proof.with_alternatives([alt])
        assert len(new_proof.ghost_alternatives) == 1
        assert new_proof.ghost_alternatives[0].description == "Alternative"
        # Original unchanged
        assert len(sample_proof.ghost_alternatives) == 0

    def test_with_loss(self, sample_proof: GaloisWitnessedProof) -> None:
        """with_loss should return new proof with updated loss."""
        new_proof = sample_proof.with_loss(0.05, {"data": 0.05})
        assert new_proof.galois_loss == 0.05
        assert new_proof.coherence == pytest.approx(0.95)
        # Original unchanged
        assert sample_proof.galois_loss == 0.18

    def test_is_valid(self) -> None:
        """is_valid should be False only for CHAOTIC tier."""
        valid = GaloisWitnessedProof(data="", warrant="", claim="", galois_loss=0.5)
        invalid = GaloisWitnessedProof(data="", warrant="", claim="", galois_loss=0.8)
        assert valid.is_valid()  # SOMATIC, not CHAOTIC
        assert not invalid.is_valid()  # CHAOTIC

    def test_needs_revision(self) -> None:
        """needs_revision should be True when coherence < 0.5."""
        good = GaloisWitnessedProof(data="", warrant="", claim="", galois_loss=0.3)
        bad = GaloisWitnessedProof(data="", warrant="", claim="", galois_loss=0.6)
        assert not good.needs_revision()  # 0.7 > 0.5
        assert bad.needs_revision()  # 0.4 < 0.5

    def test_quality_summary(self, sample_proof: GaloisWitnessedProof) -> None:
        """quality_summary should produce readable output."""
        summary = sample_proof.quality_summary()
        assert "Coherence" in summary
        assert "0.82" in summary
        assert "EMPIRICAL" in summary
        assert "session" in summary  # Enum value is lowercase


# =============================================================================
# ProofValidation Tests
# =============================================================================


class TestProofValidation:
    """Test proof validation results."""

    def test_is_valid_property(self) -> None:
        """is_valid should be based on tier."""
        valid = ProofValidation(
            coherence=0.6,
            tier=EvidenceTier.SOMATIC,
            assessment="OK",
        )
        invalid = ProofValidation(
            coherence=0.2,
            tier=EvidenceTier.CHAOTIC,
            assessment="Bad",
        )
        assert valid.is_valid
        assert not invalid.is_valid

    def test_needs_revision_property(self) -> None:
        """needs_revision should be based on coherence."""
        good = ProofValidation(
            coherence=0.7,
            tier=EvidenceTier.EMPIRICAL,
            assessment="OK",
        )
        bad = ProofValidation(
            coherence=0.4,
            tier=EvidenceTier.AESTHETIC,
            assessment="Weak",
        )
        assert not good.needs_revision
        assert bad.needs_revision

    def test_galois_loss_property(self) -> None:
        """galois_loss should be 1 - coherence."""
        validation = ProofValidation(
            coherence=0.75,
            tier=EvidenceTier.EMPIRICAL,
            assessment="OK",
        )
        assert validation.galois_loss == pytest.approx(0.25)

    def test_summary_output(self) -> None:
        """summary should produce readable output."""
        validation = ProofValidation(
            coherence=0.8,
            tier=EvidenceTier.EMPIRICAL,
            issues=["Minor issue"],
            assessment="Good proof",
        )
        summary = validation.summary()
        assert "VALID" in summary
        assert "0.8" in summary
        assert "Minor issue" in summary


# =============================================================================
# ContradictionAnalysis Tests
# =============================================================================


class TestContradictionAnalysis:
    """Test contradiction detection via super-additivity."""

    def test_expected_loss(self) -> None:
        """expected_loss should be sum of individual losses."""
        analysis = ContradictionAnalysis(
            loss_a=0.2,
            loss_b=0.25,
            loss_combined=0.5,
        )
        assert analysis.expected_loss == pytest.approx(0.45)

    def test_super_additivity(self) -> None:
        """super_additivity should be combined - expected."""
        analysis = ContradictionAnalysis(
            loss_a=0.2,
            loss_b=0.25,
            loss_combined=0.7,  # Expected 0.45
        )
        assert analysis.super_additivity == pytest.approx(0.25)

    def test_contradicts_with_super_additive(self) -> None:
        """Should detect contradiction when super-additive."""
        analysis = ContradictionAnalysis(
            loss_a=0.2,
            loss_b=0.2,
            loss_combined=0.6,  # Expected 0.4, super-additivity 0.2
        )
        assert analysis.contradicts(tolerance=0.1)
        assert not analysis.contradicts(tolerance=0.3)

    def test_no_contradiction_sub_additive(self) -> None:
        """Should not detect contradiction when sub-additive."""
        analysis = ContradictionAnalysis(
            loss_a=0.3,
            loss_b=0.3,
            loss_combined=0.4,  # Less than 0.6 expected
        )
        assert not analysis.contradicts()
        assert analysis.super_additivity < 0

    def test_severity_levels(self) -> None:
        """severity should classify super-additivity."""
        compatible = ContradictionAnalysis(loss_a=0.2, loss_b=0.2, loss_combined=0.3)
        assert "COMPATIBLE" in compatible.severity()

        tension = ContradictionAnalysis(loss_a=0.2, loss_b=0.2, loss_combined=0.55)
        assert "TENSION" in tension.severity()

        contradiction = ContradictionAnalysis(loss_a=0.2, loss_b=0.2, loss_combined=0.8)
        assert "CONTRADICTION" in contradiction.severity()


# =============================================================================
# CoherenceError Tests
# =============================================================================


class TestCoherenceError:
    """Test CoherenceError exception."""

    def test_error_creation(self) -> None:
        """Should create error with loss and threshold."""
        error = CoherenceError(
            "Marks don't cohere",
            loss=0.6,
            threshold=0.3,
        )
        assert error.loss == 0.6
        assert error.threshold == 0.3
        assert "cohere" in str(error)

    def test_error_raises(self) -> None:
        """Should be raiseable as exception."""
        with pytest.raises(CoherenceError):
            raise CoherenceError("Test error")


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for proof workflow."""

    def test_proof_workflow_categorical(self) -> None:
        """Complete workflow for categorical proof."""
        proof = GaloisWitnessedProof(
            data="Laws of category theory",
            warrant="Functor composition is associative",
            claim="This composition law holds",
            tier=EvidenceTier.CATEGORICAL,
            galois_loss=0.05,
        )

        # Should classify as categorical
        assert proof.tier_from_loss == EvidenceTier.CATEGORICAL
        assert proof.witness_mode == WitnessMode.SINGLE
        assert proof.is_valid()
        assert not proof.needs_revision()
        assert proof.coherence > 0.9

    def test_proof_workflow_chaotic(self) -> None:
        """Complete workflow for chaotic proof."""
        proof = GaloisWitnessedProof(
            data="Contradictory evidence",
            warrant="Confused reasoning",
            claim="Something unclear",
            galois_loss=0.85,
            loss_decomposition={
                "warrant": 0.4,
                "backing": 0.35,  # Both above 0.3 threshold
                "composition": 0.10,
            },
        )

        # Should classify as chaotic
        assert proof.tier_from_loss == EvidenceTier.CHAOTIC
        assert proof.witness_mode == WitnessMode.LAZY
        assert not proof.is_valid()
        assert proof.needs_revision()

        # Should generate ghost rebuttals (threshold is > 0.3)
        rebuttals = proof.rebuttals_from_loss
        assert len(rebuttals) == 2  # warrant (0.4) and backing (0.35) have high loss

    def test_validation_from_proof(self) -> None:
        """Create validation from proof metrics."""
        proof = GaloisWitnessedProof(
            data="Test data",
            warrant="Test warrant",
            claim="Test claim",
            galois_loss=0.25,
            loss_decomposition={"warrant": 0.15, "backing": 0.10},
        )

        validation = ProofValidation(
            coherence=proof.coherence,
            tier=proof.tier_from_loss,
            issues=[],
            assessment="Good proof",
            loss_decomposition=proof.loss_decomposition,
        )

        assert validation.coherence == pytest.approx(0.75)
        assert validation.tier == EvidenceTier.EMPIRICAL
        assert validation.is_valid
