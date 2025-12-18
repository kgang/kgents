"""
Tests for DNA: Configuration as Genetic Code.

Tests the DNA protocol from spec/protocols/config.md:
- Germination (validated construction)
- Trait expression
- Constraint validation
- DNA composition with modifiers
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from protocols.config.dna import (
    BOUNDED_DEPTH,
    # Standard constraints
    EPISTEMIC_HUMILITY,
    POPPERIAN_PRINCIPLE,
    POSITIVE_EXPLORATION,
    # Base types
    BaseDNA,
    # Composition
    ComposedDNA,
    # Constraints
    Constraint,
    ContextModifier,
    DNAValidationError,
    HypothesisDNA,
    JGentDNA,
    LLMAgentDNA,
    RiskAwareAgentDNA,
    StatefulAgentDNA,
    TraitNotFoundError,
    UrgencyModifier,
)

# ============================================================================
# BaseDNA Tests
# ============================================================================


class TestBaseDNA:
    """Test BaseDNA germination and expression."""

    def test_germinate_default(self) -> None:
        """Default DNA germinates successfully."""
        dna = BaseDNA.germinate()
        assert dna.exploration_budget == 0.1

    def test_germinate_custom_exploration(self) -> None:
        """Custom exploration budget works."""
        dna = BaseDNA.germinate(exploration_budget=0.3)
        assert dna.exploration_budget == 0.3

    def test_germinate_fails_zero_exploration(self) -> None:
        """Zero exploration violates positive_exploration constraint."""
        with pytest.raises(DNAValidationError) as exc:
            BaseDNA.germinate(exploration_budget=0)
        assert "positive_exploration" in str(exc.value)

    def test_germinate_fails_excessive_exploration(self) -> None:
        """Exploration > 50% violates bounded_exploration constraint."""
        with pytest.raises(DNAValidationError) as exc:
            BaseDNA.germinate(exploration_budget=0.6)
        assert "bounded_exploration" in str(exc.value)

    def test_express_exploration_probability(self) -> None:
        """Express exploration_probability trait."""
        dna = BaseDNA.germinate(exploration_budget=0.2)
        assert dna.express("exploration_probability") == 0.2

    def test_express_exploit_probability(self) -> None:
        """Express exploit_probability trait (1 - exploration)."""
        dna = BaseDNA.germinate(exploration_budget=0.2)
        assert dna.express("exploit_probability") == 0.8

    def test_express_unknown_trait_raises(self) -> None:
        """Unknown trait raises TraitNotFoundError."""
        dna = BaseDNA.germinate()
        with pytest.raises(TraitNotFoundError):
            dna.express("nonexistent_trait")

    def test_immutability(self) -> None:
        """DNA is frozen (immutable)."""
        dna = BaseDNA.germinate()
        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
            dna.exploration_budget = 0.5  # type: ignore[misc]

    def test_to_dict(self) -> None:
        """DNA can be converted to dict."""
        dna = BaseDNA.germinate(exploration_budget=0.15)
        d = dna.to_dict()
        assert d["exploration_budget"] == 0.15

    def test_from_dict(self) -> None:
        """DNA can be created from dict (via germinate)."""
        dna = BaseDNA.from_dict({"exploration_budget": 0.25})
        assert dna.exploration_budget == 0.25


# ============================================================================
# LLMAgentDNA Tests
# ============================================================================


class TestLLMAgentDNA:
    """Test LLM-specific DNA traits."""

    def test_germinate_default(self) -> None:
        """Default LLM DNA germinates."""
        dna = LLMAgentDNA.germinate()
        assert dna.creativity == 0.5
        assert dna.verbosity == "concise"

    def test_express_temperature(self) -> None:
        """Temperature derived from creativity."""
        dna = LLMAgentDNA.germinate(creativity=0.0)
        assert dna.express("temperature") == 0.5

        dna = LLMAgentDNA.germinate(creativity=1.0)
        assert dna.express("temperature") == 1.2

    def test_express_top_p(self) -> None:
        """Top_p derived from creativity."""
        dna = LLMAgentDNA.germinate(creativity=0.0)
        assert dna.express("top_p") == 0.7

        dna = LLMAgentDNA.germinate(creativity=1.0)
        assert dna.express("top_p") == 0.95

    def test_express_max_tokens(self) -> None:
        """Max tokens derived from verbosity."""
        dna_concise = LLMAgentDNA.germinate(verbosity="concise")
        assert dna_concise.express("max_tokens") == 256

        dna_detailed = LLMAgentDNA.germinate(verbosity="detailed")
        assert dna_detailed.express("max_tokens") == 1024

        dna_verbose = LLMAgentDNA.germinate(verbosity="verbose")
        assert dna_verbose.express("max_tokens") == 4096

    def test_germinate_fails_invalid_creativity(self) -> None:
        """Creativity out of range fails."""
        with pytest.raises(DNAValidationError) as exc:
            LLMAgentDNA.germinate(creativity=1.5)
        assert "creativity_range" in str(exc.value)

    def test_germinate_fails_invalid_verbosity(self) -> None:
        """Invalid verbosity fails."""
        with pytest.raises(DNAValidationError) as exc:
            LLMAgentDNA.germinate(verbosity="invalid")
        assert "valid_verbosity" in str(exc.value)


# ============================================================================
# StatefulAgentDNA Tests
# ============================================================================


class TestStatefulAgentDNA:
    """Test stateful agent DNA traits."""

    def test_germinate_default(self) -> None:
        """Default stateful DNA germinates."""
        dna = StatefulAgentDNA.germinate()
        assert dna.history_depth == 100
        assert dna.auto_save is True

    def test_express_save_interval(self) -> None:
        """Save interval derived from history depth."""
        dna = StatefulAgentDNA.germinate(history_depth=100)
        assert dna.express("save_interval") == 10

        dna = StatefulAgentDNA.germinate(history_depth=50)
        assert dna.express("save_interval") == 5

    def test_express_prune_threshold(self) -> None:
        """Prune threshold derived from history depth."""
        dna = StatefulAgentDNA.germinate(history_depth=100)
        assert dna.express("prune_threshold") == 200

    def test_germinate_fails_zero_history(self) -> None:
        """Zero history depth fails."""
        with pytest.raises(DNAValidationError) as exc:
            StatefulAgentDNA.germinate(history_depth=0)
        assert "positive_history" in str(exc.value)

    def test_germinate_fails_excessive_history(self) -> None:
        """Excessive history depth fails."""
        with pytest.raises(DNAValidationError) as exc:
            StatefulAgentDNA.germinate(history_depth=20000)
        assert "bounded_history" in str(exc.value)


# ============================================================================
# RiskAwareAgentDNA Tests
# ============================================================================


class TestRiskAwareAgentDNA:
    """Test risk-aware DNA traits."""

    def test_germinate_default(self) -> None:
        """Default risk-aware DNA germinates."""
        dna = RiskAwareAgentDNA.germinate()
        assert dna.risk_tolerance == 0.5

    def test_express_max_retries_cautious(self) -> None:
        """Cautious agent gets more retries."""
        dna = RiskAwareAgentDNA.germinate(risk_tolerance=0.0)
        assert dna.express("max_retries") == 5

    def test_express_max_retries_bold(self) -> None:
        """Bold agent gets fewer retries."""
        dna = RiskAwareAgentDNA.germinate(risk_tolerance=1.0)
        assert dna.express("max_retries") == 1

    def test_express_retry_delay_cautious(self) -> None:
        """Cautious agent waits longer between retries."""
        dna = RiskAwareAgentDNA.germinate(risk_tolerance=0.0)
        assert dna.express("retry_delay") == 3.0

    def test_express_retry_delay_bold(self) -> None:
        """Bold agent waits less between retries."""
        dna = RiskAwareAgentDNA.germinate(risk_tolerance=1.0)
        assert dna.express("retry_delay") == 1.0

    def test_germinate_fails_invalid_risk(self) -> None:
        """Risk out of range fails."""
        with pytest.raises(DNAValidationError) as exc:
            RiskAwareAgentDNA.germinate(risk_tolerance=-0.1)
        assert "risk_range" in str(exc.value)


# ============================================================================
# HypothesisDNA Tests (B-gent)
# ============================================================================


class TestHypothesisDNA:
    """Test hypothesis agent DNA with epistemic constraints."""

    def test_germinate_default(self) -> None:
        """Default hypothesis DNA germinates."""
        dna = HypothesisDNA.germinate()
        assert dna.confidence_threshold == 0.7
        assert dna.falsification_required is True
        assert dna.max_hypotheses == 5

    def test_epistemic_humility_enforced(self) -> None:
        """Confidence > 0.8 violates epistemic_humility."""
        with pytest.raises(DNAValidationError) as exc:
            HypothesisDNA.germinate(confidence_threshold=0.9)
        assert "epistemic_humility" in str(exc.value)

    def test_popperian_principle_enforced(self) -> None:
        """Falsification must be required."""
        with pytest.raises(DNAValidationError) as exc:
            HypothesisDNA.germinate(falsification_required=False)
        assert "popperian_principle" in str(exc.value)

    def test_hypothesis_budget_enforced(self) -> None:
        """Hypothesis count must be 1-10."""
        with pytest.raises(DNAValidationError) as exc:
            HypothesisDNA.germinate(max_hypotheses=0)
        assert "hypothesis_budget" in str(exc.value)

        with pytest.raises(DNAValidationError) as exc:
            HypothesisDNA.germinate(max_hypotheses=15)
        assert "hypothesis_budget" in str(exc.value)

    def test_express_prior_ceiling(self) -> None:
        """Prior ceiling derived from confidence threshold."""
        dna = HypothesisDNA.germinate(confidence_threshold=0.7)
        assert dna.express("prior_ceiling") == 0.5  # min(0.5, 0.7)

    def test_express_evidence_threshold(self) -> None:
        """Evidence threshold derived from confidence."""
        dna = HypothesisDNA.germinate(confidence_threshold=0.7)
        assert dna.express("evidence_threshold") == pytest.approx(0.3)  # 1 - 0.7


# ============================================================================
# JGentDNA Tests
# ============================================================================


class TestJGentDNA:
    """Test J-gent judgment DNA."""

    def test_germinate_default(self) -> None:
        """Default J-gent DNA germinates."""
        dna = JGentDNA.germinate()
        assert dna.max_depth == 5
        assert dna.entropy_budget == 1.0
        assert dna.decay_factor == 0.5

    def test_germinate_fails_excessive_depth(self) -> None:
        """Depth > 20 fails."""
        with pytest.raises(DNAValidationError) as exc:
            JGentDNA.germinate(max_depth=25)
        assert "bounded_depth" in str(exc.value)

    def test_germinate_fails_zero_entropy(self) -> None:
        """Zero entropy budget fails."""
        with pytest.raises(DNAValidationError) as exc:
            JGentDNA.germinate(entropy_budget=0)
        assert "positive_entropy" in str(exc.value)

    def test_germinate_fails_invalid_decay(self) -> None:
        """Invalid decay factor fails."""
        with pytest.raises(DNAValidationError) as exc:
            JGentDNA.germinate(decay_factor=1.0)
        assert "valid_decay" in str(exc.value)

    def test_express_min_budget(self) -> None:
        """Min budget calculated from entropy and depth."""
        dna = JGentDNA.germinate(
            entropy_budget=1.0,
            decay_factor=0.5,
            max_depth=5,
        )
        # 1.0 * (0.5 ** 5) = 0.03125
        assert dna.express("min_budget") == pytest.approx(0.03125)

    def test_express_max_branches(self) -> None:
        """Max branches derived from decay factor."""
        dna = JGentDNA.germinate(decay_factor=0.5)
        assert dna.express("max_branches") == 2  # min(5, int(1/0.5))


# ============================================================================
# ComposedDNA Tests
# ============================================================================


class TestComposedDNA:
    """Test DNA composition with modifiers."""

    def test_composed_dna_express(self) -> None:
        """ComposedDNA expresses base traits."""
        base = RiskAwareAgentDNA.germinate(risk_tolerance=0.5)
        composed = ComposedDNA(base=base)
        assert composed.express("max_retries") == 3

    def test_composed_dna_with_modifier(self) -> None:
        """ComposedDNA applies modifiers."""
        base = RiskAwareAgentDNA.germinate(risk_tolerance=0.0)
        # max_retries = 5 without modifier

        modifier = UrgencyModifier(urgency=1.0)  # Critical urgency
        composed = ComposedDNA(base=base, modifiers=(modifier,))

        # With urgency=1.0: max(1, int(5 * (1 - 1.0 * 0.5))) = max(1, 2) = 2
        assert composed.express("max_retries") == 2

    def test_composed_dna_multiple_modifiers(self) -> None:
        """Multiple modifiers applied in order."""
        base = LLMAgentDNA.germinate(creativity=1.0)
        # temperature = 1.2 without modifiers

        # First modifier: context (production reduces temperature)
        # Second modifier: urgency (doesn't affect temperature)
        composed = ComposedDNA(
            base=base,
            modifiers=(
                ContextModifier(is_production=True),
                UrgencyModifier(urgency=0.5),
            ),
        )

        # Production caps temperature at 0.7
        assert composed.express("temperature") == 0.7

    def test_composed_dna_with_modifier_method(self) -> None:
        """with_modifier creates new ComposedDNA."""
        base = RiskAwareAgentDNA.germinate(risk_tolerance=0.0)
        composed1 = ComposedDNA(base=base)
        composed2 = composed1.with_modifier(UrgencyModifier(urgency=0.5))

        # Original unchanged
        assert composed1.express("max_retries") == 5
        # New has modifier
        assert composed2.express("max_retries") == 3  # reduced by urgency


# ============================================================================
# UrgencyModifier Tests
# ============================================================================


class TestUrgencyModifier:
    """Test urgency modifier."""

    def test_urgency_reduces_retries(self) -> None:
        """High urgency reduces max_retries."""
        modifier = UrgencyModifier(urgency=1.0)
        # max_retries=5 → max(1, int(5 * 0.5)) = 2
        assert modifier.modify("max_retries", 5) == 2

    def test_urgency_reduces_delay(self) -> None:
        """High urgency reduces retry_delay."""
        modifier = UrgencyModifier(urgency=1.0)
        # retry_delay=2.0 → 2.0 * 0.5 = 1.0
        assert modifier.modify("retry_delay", 2.0) == 1.0

    def test_urgency_reduces_tokens(self) -> None:
        """High urgency reduces max_tokens."""
        modifier = UrgencyModifier(urgency=1.0)
        # max_tokens=1000 → int(1000 * 0.7) = 700
        assert modifier.modify("max_tokens", 1000) == 700

    def test_urgency_passthrough_other_traits(self) -> None:
        """Unknown traits passed through unchanged."""
        modifier = UrgencyModifier(urgency=1.0)
        assert modifier.modify("temperature", 0.8) == 0.8


# ============================================================================
# ContextModifier Tests
# ============================================================================


class TestContextModifier:
    """Test context modifier."""

    def test_production_caps_temperature(self) -> None:
        """Production mode caps temperature at 0.7."""
        modifier = ContextModifier(is_production=True)
        assert modifier.modify("temperature", 1.2) == 0.7
        assert modifier.modify("temperature", 0.5) == 0.5  # Already below cap

    def test_production_caps_exploration(self) -> None:
        """Production mode caps exploration at 0.05."""
        modifier = ContextModifier(is_production=True)
        assert modifier.modify("exploration_probability", 0.2) == 0.05
        assert modifier.modify("exploration_probability", 0.03) == 0.03

    def test_development_passthrough(self) -> None:
        """Development mode doesn't modify."""
        modifier = ContextModifier(is_production=False)
        assert modifier.modify("temperature", 1.2) == 1.2
        assert modifier.modify("exploration_probability", 0.2) == 0.2


# ============================================================================
# Constraint Tests
# ============================================================================


class TestConstraint:
    """Test Constraint validation."""

    def test_constraint_passes(self) -> None:
        """Constraint passes when check returns True."""
        constraint = Constraint(
            name="positive",
            check=lambda x: x.value > 0,
            message="must be positive",
        )

        @dataclass(frozen=True)
        class TestDNA:
            value: int = 5

        valid, msg = constraint.validate(TestDNA())
        assert valid is True
        assert msg == ""

    def test_constraint_fails(self) -> None:
        """Constraint fails when check returns False."""
        constraint = Constraint(
            name="positive",
            check=lambda x: x.value > 0,
            message="must be positive",
        )

        @dataclass(frozen=True)
        class TestDNA:
            value: int = -1

        valid, msg = constraint.validate(TestDNA())
        assert valid is False
        assert "must be positive" in msg

    def test_constraint_handles_exception(self) -> None:
        """Constraint handles exceptions in check."""
        constraint = Constraint(
            name="risky",
            check=lambda x: 1 / x.value > 0,  # Will fail for value=0
            message="division check",
        )

        @dataclass(frozen=True)
        class TestDNA:
            value: int = 0

        valid, msg = constraint.validate(TestDNA())
        assert valid is False
        assert "division check" in msg


# ============================================================================
# Standard Constraints Tests
# ============================================================================


class TestStandardConstraints:
    """Test pre-defined constraints."""

    def test_epistemic_humility(self) -> None:
        """EPISTEMIC_HUMILITY constraint."""

        @dataclass(frozen=True)
        class TestDNA:
            confidence_threshold: float = 0.7

        valid, _ = EPISTEMIC_HUMILITY.validate(TestDNA())
        assert valid is True

        valid, _ = EPISTEMIC_HUMILITY.validate(TestDNA(confidence_threshold=0.9))
        assert valid is False

    def test_positive_exploration(self) -> None:
        """POSITIVE_EXPLORATION constraint."""

        @dataclass(frozen=True)
        class TestDNA:
            exploration_budget: float = 0.1

        valid, _ = POSITIVE_EXPLORATION.validate(TestDNA())
        assert valid is True

        valid, _ = POSITIVE_EXPLORATION.validate(TestDNA(exploration_budget=0))
        assert valid is False

    def test_bounded_depth(self) -> None:
        """BOUNDED_DEPTH constraint."""

        @dataclass(frozen=True)
        class TestDNA:
            max_depth: int = 10

        valid, _ = BOUNDED_DEPTH.validate(TestDNA())
        assert valid is True

        valid, _ = BOUNDED_DEPTH.validate(TestDNA(max_depth=25))
        assert valid is False

    def test_popperian_principle(self) -> None:
        """POPPERIAN_PRINCIPLE constraint."""

        @dataclass(frozen=True)
        class TestDNA:
            falsification_required: bool = True

        valid, _ = POPPERIAN_PRINCIPLE.validate(TestDNA())
        assert valid is True

        valid, _ = POPPERIAN_PRINCIPLE.validate(TestDNA(falsification_required=False))
        assert valid is False


# ============================================================================
# Custom DNA Tests
# ============================================================================


class TestCustomDNA:
    """Test creating custom DNA types."""

    def test_custom_dna_class(self) -> None:
        """Custom DNA class with custom constraints."""

        @dataclass(frozen=True)
        class PersonaDNA(BaseDNA):
            personality: str = "curious"
            warmth: float = 0.7

            @classmethod
            def constraints(cls) -> list[Constraint]:
                base = super().constraints()
                return base + [
                    Constraint(
                        name="warmth_range",
                        check=lambda d: 0 <= d.warmth <= 1,
                        message="warmth must be 0-1",
                    ),
                ]

            def _standard_expressions(self) -> dict[str, Any]:
                base = super()._standard_expressions()
                return {
                    **base,
                    "formality": 1 - self.warmth,
                }

        dna = PersonaDNA.germinate(personality="playful", warmth=0.8)
        assert dna.personality == "playful"
        assert dna.warmth == 0.8
        assert dna.express("formality") == pytest.approx(0.2)

        with pytest.raises(DNAValidationError):
            PersonaDNA.germinate(warmth=1.5)
