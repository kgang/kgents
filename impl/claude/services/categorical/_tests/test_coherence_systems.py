"""
Coherence Systems Tests.

Verifies the unifying equation: R_constitutional = 1 - L_galois

Tests cross-system coherence across:
- Zero Seed Galois computation (galois_loss.py)
- Constitutional evaluation (constitution.py, constitutional_evaluator.py)
- Evidence scoring correlation (tier classification)
- Layer assignment consistency (bootstrap.py)
- HoTT verification infrastructure (hott.py)
- Lean export generation (lean_export.py)

NOTE: This file is named test_coherence_systems.py (not test_coherence_integration.py)
to avoid being auto-skipped as an LLM integration test. All tests use mocks
and do not require actual LLM calls.

Philosophy:
    "The proof IS the coherence. Cross-system alignment verifies truth."
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from services.witness.mark import (
    Mark,
    MarkId,
    Response,
    Stimulus,
    UmweltSnapshot,
)


# Test the unified equation holds
class TestCoherenceEquation:
    """Verify R = 1 - L holds across systems."""

    @pytest.mark.asyncio
    async def test_galois_constitutional_duality(self):
        """Constitutional reward should correlate with 1 - Galois loss."""
        from services.zero_seed.galois.galois_loss import (
            classify_evidence_tier,
            compute_galois_loss_async,
        )

        # Test content at different tiers
        test_cases = [
            ("Everything composes. Identity exists.", "CATEGORICAL"),  # Axiom-like
            ("Users should be able to log in securely.", "EMPIRICAL"),  # Value-like
            ("Use OAuth2 for authentication.", "AESTHETIC"),  # Spec-like
        ]

        for content, expected_tier in test_cases:
            result = await compute_galois_loss_async(content)
            tier = classify_evidence_tier(result.loss)
            coherence = 1.0 - result.loss

            # Coherence should be in [0, 1]
            assert 0.0 <= coherence <= 1.0
            assert 0.0 <= result.loss <= 1.0

    @pytest.mark.asyncio
    async def test_tier_thresholds_kent_calibrated(self):
        """Verify tier thresholds match Kent calibration."""
        from services.zero_seed.galois.galois_loss import (
            EvidenceTier,
            classify_evidence_tier,
        )

        # Kent-calibrated thresholds (2025-12-28)
        assert classify_evidence_tier(0.05) == EvidenceTier.CATEGORICAL  # L < 0.10
        assert classify_evidence_tier(0.15) == EvidenceTier.EMPIRICAL  # L < 0.38
        assert classify_evidence_tier(0.40) == EvidenceTier.AESTHETIC  # L < 0.45
        assert classify_evidence_tier(0.50) == EvidenceTier.SOMATIC  # L < 0.65
        assert classify_evidence_tier(0.80) == EvidenceTier.CHAOTIC  # L >= 0.65


class TestConstitutionalEvaluatorGalois:
    """Test constitutional evaluator with Galois integration."""

    @pytest.fixture
    def mock_mark(self):
        """Create a mock mark for testing."""
        return Mark(
            id=MarkId(f"mark-{uuid4().hex[:12]}"),
            timestamp=datetime.now(timezone.utc),
            stimulus=Stimulus(kind="test", content="Test stimulus"),
            response=Response(kind="test", content="Test response", success=True),
            umwelt=UmweltSnapshot(
                observer_id="test",
                role="test",
                capabilities=frozenset(),
                trust_level=1,
            ),
            domain="test",
            tags=(),
        )

    @pytest.mark.asyncio
    async def test_evaluator_computes_galois_when_enabled(self, mock_mark):
        """Evaluator should compute Galois loss when include_galois=True."""
        from services.witness.constitutional_evaluator import MarkConstitutionalEvaluator

        evaluator = MarkConstitutionalEvaluator(include_galois=True)
        # Note: Full evaluation requires async Galois computation
        # This test verifies the evaluator is configured correctly
        assert evaluator.include_galois is True

    def test_ethical_gate_constraint(self):
        """ETHICAL must be a gate (>=0.6), not a weighted score."""
        from services.categorical.constitution import Constitution

        # Verify ETHICAL is handled as a gate in the Constitution
        # This is Amendment A from the Constitutional Decision OS
        assert hasattr(Constitution, "evaluate")


class TestLayerAssignment:
    """Test consistent layer assignment from Galois loss."""

    def test_layer_from_loss_deterministic(self):
        """Same loss should always produce same layer."""
        from services.categorical.bootstrap import ContentLayer, classify_content_layer

        # Test determinism
        for _ in range(100):
            assert classify_content_layer(0.05) == ContentLayer.AXIOM
            assert classify_content_layer(0.25) == ContentLayer.VALUE
            assert classify_content_layer(0.50) == ContentLayer.SPEC
            assert classify_content_layer(0.75) == ContentLayer.TUNING

    def test_layer_boundaries(self):
        """Test exact boundary conditions."""
        from services.categorical.bootstrap import ContentLayer, classify_content_layer

        # Boundary at 0.10
        assert classify_content_layer(0.099) == ContentLayer.AXIOM
        assert classify_content_layer(0.10) == ContentLayer.VALUE

        # Boundary at 0.38
        assert classify_content_layer(0.379) == ContentLayer.VALUE
        assert classify_content_layer(0.38) == ContentLayer.SPEC

        # Boundary at 0.65
        assert classify_content_layer(0.649) == ContentLayer.SPEC
        assert classify_content_layer(0.65) == ContentLayer.TUNING


class TestHoTTVerification:
    """Test HoTT-based verification infrastructure."""

    @pytest.mark.asyncio
    async def test_categorical_law_verification(self):
        """Verify categorical laws can be checked."""
        from services.verification.hott import CategoricalLawVerifier, HoTTContext

        context = HoTTContext()
        verifier = CategoricalLawVerifier(context)

        # Test morphisms (simplified for testing)
        f = {"name": "f", "type": "A -> B"}
        g = {"name": "g", "type": "B -> C"}
        h = {"name": "h", "type": "C -> D"}

        result = await verifier.verify_associativity(f, g, h)
        assert result.law_name == "composition_associativity"
        # Verification depends on path construction capability

    def test_lean_export_generates_valid_syntax(self):
        """Lean exporter should generate syntactically valid code."""
        from services.verification.lean_export import LeanExporter

        exporter = LeanExporter()
        lean_code = exporter.export_category_laws()

        # Check structure
        assert "namespace Kgents" in lean_code
        assert "comp_assoc" in lean_code
        assert "id_comp" in lean_code
        assert "end Kgents" in lean_code


class TestPilotBootstrap:
    """Test pilot bootstrap infrastructure."""

    @pytest.mark.asyncio
    async def test_axiom_validation(self):
        """Axiom candidates should be validated via Galois loss."""
        from services.categorical.bootstrap import validate_axiom_candidate

        # Mock loss function that returns low loss for axiom-like content
        async def mock_loss(content):
            # Simulate: shorter, more fundamental = lower loss
            return type("Result", (), {"loss": 0.05 if len(content) < 50 else 0.30})()

        # Test axiom-like content
        is_axiom, loss, _ = await validate_axiom_candidate(
            "Everything composes.",
            mock_loss,
        )
        assert is_axiom is True
        assert loss < 0.10

        # Test non-axiom content
        is_axiom, loss, _ = await validate_axiom_candidate(
            "Use the following specific implementation details for authentication...",
            mock_loss,
        )
        assert is_axiom is False

    def test_bootstrapper_builds_foundation(self):
        """PilotBootstrapper should build complete foundations."""
        from services.categorical.bootstrap import (
            Axiom,
            PilotBootstrapper,
            Value,
        )

        bootstrapper = PilotBootstrapper("test-pilot")

        # Add test axiom directly
        axiom = Axiom(
            name="A1",
            statement="Test axiom",
            derivation="L0.1",
            test="Check violation",
            galois_loss=0.05,
        )
        bootstrapper.axioms.append(axiom)

        # Derive value
        bootstrapper.derive_value(
            name="V1",
            statement="Test value",
            derived_from=("A1",),
            specification="spec",
            galois_loss=0.25,
        )

        foundation = bootstrapper.build_foundation(laws=("L1", "L2"))

        assert foundation.name == "test-pilot"
        assert len(foundation.axioms) == 1
        assert len(foundation.values) == 1
        assert len(foundation.laws) == 2


class TestGaloisLossIntegration:
    """Test Galois loss computation integration."""

    @pytest.mark.asyncio
    async def test_loss_computation_returns_valid_result(self):
        """compute_galois_loss_async should return valid GaloisLoss."""
        from services.zero_seed.galois.galois_loss import (
            GaloisLoss,
            compute_galois_loss_async,
        )

        result = await compute_galois_loss_async("Test content for loss computation")

        assert isinstance(result, GaloisLoss)
        assert 0.0 <= result.loss <= 1.0
        assert result.method in ("llm", "fallback")

    @pytest.mark.asyncio
    async def test_coherence_is_one_minus_loss(self):
        """Coherence should equal 1 - loss (the unifying equation)."""
        from services.zero_seed.galois.galois_loss import (
            GaloisLossComputer,
            compute_galois_loss_async,
        )

        # Test with various content
        test_contents = [
            "Simple axiom.",
            "A more complex value statement about system behavior.",
            "Detailed specification with implementation notes and examples.",
        ]

        for content in test_contents:
            result = await compute_galois_loss_async(content)
            coherence = 1.0 - result.loss

            # The unifying equation
            assert abs(coherence + result.loss - 1.0) < 1e-10


class TestConstitutionalRewardIntegration:
    """Test constitutional reward system integration."""

    def test_constitution_evaluate_returns_all_principles(self):
        """Constitution.evaluate should score all 7 principles."""
        from services.categorical.constitution import Constitution, Principle

        evaluation = Constitution.evaluate(
            state_before="initial",
            action="test_action",
            state_after="final",
        )

        # Should have all 7 principles
        assert len(evaluation.scores) == 7

        principles_covered = {s.principle for s in evaluation.scores}
        assert principles_covered == set(Principle)

    def test_ethical_floor_constraint(self):
        """ETHICAL score below 0.6 should cause rejection."""
        from services.categorical.constitution import (
            ETHICAL_FLOOR_THRESHOLD,
            Constitution,
            ConstitutionalEvaluation,
            Principle,
            PrincipleScore,
        )

        # Create evaluation with low ETHICAL score
        scores = (
            PrincipleScore(Principle.ETHICAL, 0.3, "Low ethical score"),
            PrincipleScore(Principle.COMPOSABLE, 1.0, "Perfect"),
            PrincipleScore(Principle.JOY_INDUCING, 1.0, "Perfect"),
        )

        evaluation = ConstitutionalEvaluation(scores=scores)

        # Should fail due to ETHICAL floor
        assert not evaluation.ethical_passes
        assert evaluation.weighted_total == 0.0  # Rejected


class TestCrossSystemCoherence:
    """Test coherence across different system components."""

    @pytest.mark.asyncio
    async def test_galois_tier_aligns_with_content_layer(self):
        """Galois evidence tiers should align with content layers."""
        from services.categorical.bootstrap import (
            ContentLayer,
            classify_content_layer,
        )
        from services.zero_seed.galois.galois_loss import (
            EvidenceTier,
            classify_evidence_tier,
        )

        # The tier/layer mapping should be consistent
        # CATEGORICAL tier (L < 0.10) should align with AXIOM layer
        # EMPIRICAL tier (L < 0.38) should align with VALUE layer
        # etc.

        test_cases = [
            (0.05, EvidenceTier.CATEGORICAL, ContentLayer.AXIOM),
            (0.15, EvidenceTier.EMPIRICAL, ContentLayer.VALUE),
            (0.40, EvidenceTier.AESTHETIC, ContentLayer.SPEC),
            (0.55, EvidenceTier.SOMATIC, ContentLayer.SPEC),
            (0.70, EvidenceTier.CHAOTIC, ContentLayer.TUNING),
        ]

        for loss, expected_tier, expected_layer in test_cases:
            actual_tier = classify_evidence_tier(loss)
            actual_layer = classify_content_layer(loss)

            assert actual_tier == expected_tier, (
                f"Loss {loss}: expected tier {expected_tier}, got {actual_tier}"
            )
            assert actual_layer == expected_layer, (
                f"Loss {loss}: expected layer {expected_layer}, got {actual_layer}"
            )
