"""
Tests for NonsenseQuarantine.

Test coverage:
- Coherent content (loss < 0.5)
- Hand-wavy content (0.5 ≤ loss < 0.85)
- Nonsense content (loss ≥ 0.85)
- Quarantine effects
- Convenience functions
"""

import pytest

from services.edge.quarantine import (
    NonsenseQuarantine,
    QuarantineDecision,
    QuarantineEffects,
    evaluate_for_quarantine,
)


class TestNonsenseQuarantine:
    """Test suite for nonsense quarantine system."""

    def test_coherent_not_quarantined(self):
        """Coherent content (loss < 0.5) is not quarantined."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.3)

        assert not decision.quarantine
        assert decision.reason == "Coherent"
        assert decision.suggestion is None
        assert len(decision.effects) == 0

    def test_hand_wavy_not_quarantined_but_suggested(self):
        """Hand-wavy content (0.5 ≤ loss < 0.85) gets suggestion."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.6)

        assert not decision.quarantine
        assert decision.reason == "Hand-wavy but tolerable"
        assert decision.suggestion is not None
        assert "moderate loss" in decision.suggestion.lower()
        assert len(decision.effects) == 0

    def test_nonsense_quarantined(self):
        """Nonsense content (loss ≥ 0.85) is quarantined."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.9)

        assert decision.quarantine
        assert "very high loss" in decision.reason.lower()
        assert "0.90" in decision.reason
        assert decision.suggestion is not None
        assert len(decision.effects) > 0

    def test_quarantine_effects_complete(self):
        """Quarantine includes all expected effects."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.9)

        assert QuarantineEffects.NO_SYSTEM_RANKING in decision.effects
        assert QuarantineEffects.NO_RECOMMENDATIONS in decision.effects
        assert QuarantineEffects.PERSONAL_VISIBLE in decision.effects
        assert QuarantineEffects.REVERSIBLE in decision.effects

    def test_threshold_boundary_below(self):
        """Loss just below threshold is not quarantined."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.84)

        assert not decision.quarantine
        assert "tolerable" in decision.reason.lower()

    def test_threshold_boundary_at(self):
        """Loss at threshold is quarantined."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.85)

        assert decision.quarantine

    def test_suggestion_threshold_boundary(self):
        """Loss at suggestion threshold gets suggestion."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.5)

        assert not decision.quarantine
        assert decision.suggestion is not None

    def test_extreme_loss(self):
        """Extreme loss (1.0) is quarantined."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=1.0)

        assert decision.quarantine
        assert decision.loss == 1.0

    def test_zero_loss(self):
        """Zero loss is coherent."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.0)

        assert not decision.quarantine
        assert decision.reason == "Coherent"

    def test_explain_effects(self):
        """Test effect explanation generation."""
        quarantine = NonsenseQuarantine()

        effects = (
            QuarantineEffects.NO_SYSTEM_RANKING,
            QuarantineEffects.REVERSIBLE,
        )

        explanations = quarantine.explain_effects(effects)

        assert len(explanations) == 2
        assert "rankings" in explanations[0].lower()
        assert "refined" in explanations[1].lower()

    def test_convenience_function(self):
        """Test evaluate_for_quarantine convenience function."""
        decision = evaluate_for_quarantine(galois_loss=0.9)

        assert decision.quarantine

    def test_content_parameter_stored(self):
        """Content parameter is accepted (for future use)."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(
            galois_loss=0.9,
            content="Some random text",
        )

        assert decision.quarantine
        # Content currently not used in logic, but should not error

    def test_quarantine_suggestion_helpful(self):
        """Quarantine suggestion includes path to recovery."""
        quarantine = NonsenseQuarantine()

        decision = quarantine.evaluate(galois_loss=0.9)

        assert "refine" in decision.suggestion.lower()
        assert "exit quarantine" in decision.suggestion.lower()
        assert "no judgment" in decision.suggestion.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
