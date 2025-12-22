"""
Tests for Derivation Framework types.

These tests verify the core data structures from spec/protocols/derivation-framework.md.
Tests are organized by type, testing:
- Immutability (frozen dataclasses)
- Confidence computation
- Evidence decay
- Law compliance
"""

from datetime import datetime, timedelta

import pytest

from ..types import (
    BOOTSTRAP_PRINCIPLE_DRAWS,
    Derivation,
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)


class TestDerivationTier:
    """Tests for the DerivationTier enum."""

    def test_tiers_have_correct_ceilings(self) -> None:
        """Each tier has a defined confidence ceiling."""
        assert DerivationTier.BOOTSTRAP.ceiling == 1.00
        assert DerivationTier.FUNCTOR.ceiling == 0.98
        assert DerivationTier.POLYNOMIAL.ceiling == 0.95
        assert DerivationTier.OPERAD.ceiling == 0.92
        assert DerivationTier.JEWEL.ceiling == 0.85
        assert DerivationTier.APP.ceiling == 0.75

    def test_tier_ordering(self) -> None:
        """Tiers are ordered by how foundational they are."""
        assert DerivationTier.BOOTSTRAP < DerivationTier.FUNCTOR
        assert DerivationTier.FUNCTOR < DerivationTier.POLYNOMIAL
        assert DerivationTier.POLYNOMIAL < DerivationTier.OPERAD
        assert DerivationTier.OPERAD < DerivationTier.JEWEL
        assert DerivationTier.JEWEL < DerivationTier.APP

    def test_tier_is_string_enum(self) -> None:
        """Tiers can be used as strings for serialization."""
        assert DerivationTier.BOOTSTRAP.value == "bootstrap"
        assert str(DerivationTier.BOOTSTRAP) == "DerivationTier.BOOTSTRAP"


class TestEvidenceType:
    """Tests for the EvidenceType enum."""

    def test_categorical_never_decays(self) -> None:
        """Categorical evidence (formal proofs) has zero decay rate."""
        assert EvidenceType.CATEGORICAL.decay_rate == 0.0

    def test_somatic_never_decays(self) -> None:
        """Somatic evidence (Kent's judgment) has zero decay rate."""
        assert EvidenceType.SOMATIC.decay_rate == 0.0

    def test_empirical_evidence_decays_slowly(self) -> None:
        """Empirical evidence decays at 2% per day."""
        assert EvidenceType.EMPIRICAL.decay_rate == 0.02

    def test_aesthetic_evidence_decays_faster(self) -> None:
        """Aesthetic evidence decays faster than empirical."""
        assert EvidenceType.AESTHETIC.decay_rate > EvidenceType.EMPIRICAL.decay_rate

    def test_all_decay_rates_are_non_negative(self) -> None:
        """No evidence type has negative decay."""
        for evidence_type in EvidenceType:
            assert evidence_type.decay_rate >= 0.0


class TestPrincipleDraw:
    """Tests for the PrincipleDraw dataclass."""

    def test_draw_is_frozen(self) -> None:
        """PrincipleDraw is immutable."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=0.9,
            evidence_type=EvidenceType.EMPIRICAL,
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            draw.draw_strength = 0.5  # type: ignore

    def test_draw_strength_clamped(self) -> None:
        """Draw strength is clamped to [0, 1]."""
        draw_high = PrincipleDraw(
            principle="Composable",
            draw_strength=1.5,  # Too high
            evidence_type=EvidenceType.EMPIRICAL,
        )
        assert draw_high.draw_strength == 1.0

        draw_low = PrincipleDraw(
            principle="Composable",
            draw_strength=-0.5,  # Too low
            evidence_type=EvidenceType.EMPIRICAL,
        )
        assert draw_low.draw_strength == 0.0

    def test_categorical_draws_dont_decay(self) -> None:
        """Categorical evidence doesn't decay over time."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.CATEGORICAL,
            evidence_sources=("associativity-law",),
        )

        decayed = draw.decay(days_elapsed=365.0)
        assert decayed.draw_strength == 1.0

    def test_empirical_draws_decay(self) -> None:
        """Empirical evidence decays over time."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("ashc-run-001",),
        )

        decayed = draw.decay(days_elapsed=30.0)
        assert decayed.draw_strength < 1.0
        assert decayed.draw_strength >= 0.1  # Floor

    def test_decay_has_floor(self) -> None:
        """Evidence can't decay below 0.1."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=0.5,
            evidence_type=EvidenceType.AESTHETIC,
        )

        # Decay for a very long time
        decayed = draw.decay(days_elapsed=10000.0)
        assert decayed.draw_strength == 0.1

    def test_is_categorical_property(self) -> None:
        """is_categorical correctly identifies categorical evidence."""
        categorical = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.CATEGORICAL,
        )
        assert categorical.is_categorical

        empirical = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.EMPIRICAL,
        )
        assert not empirical.is_categorical


class TestDerivation:
    """Tests for the Derivation dataclass."""

    def test_derivation_is_frozen(self) -> None:
        """Derivation is immutable."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.APP,
        )

        with pytest.raises(Exception):
            derivation.agent_name = "Changed"  # type: ignore

    def test_total_confidence_respects_tier_ceiling(self) -> None:
        """Total confidence never exceeds tier ceiling (Law 2)."""
        # APP tier has ceiling of 0.75
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.APP,
            inherited_confidence=0.9,
            empirical_confidence=1.0,
            stigmergic_confidence=1.0,
        )

        # Even with high component values, ceiling applies
        assert derivation.total_confidence <= 0.75

    def test_bootstrap_derivation_has_full_confidence(self) -> None:
        """Bootstrap agents have confidence = 1.0 (Law 3)."""
        derivation = Derivation(
            agent_name="Id",
            tier=DerivationTier.BOOTSTRAP,
            inherited_confidence=1.0,
            empirical_confidence=1.0,
            stigmergic_confidence=1.0,
        )

        assert derivation.total_confidence == 1.0
        assert derivation.is_bootstrap

    def test_is_bootstrap_property(self) -> None:
        """is_bootstrap correctly identifies bootstrap agents."""
        bootstrap = Derivation(
            agent_name="Id",
            tier=DerivationTier.BOOTSTRAP,
        )
        assert bootstrap.is_bootstrap

        derived = Derivation(
            agent_name="Flux",
            tier=DerivationTier.FUNCTOR,
        )
        assert not derived.is_bootstrap

    def test_empirical_boost_is_capped(self) -> None:
        """Empirical evidence provides at most 0.2 boost."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.BOOTSTRAP,  # Ceiling = 1.0
            inherited_confidence=0.5,
            empirical_confidence=1.0,  # Maximum
            stigmergic_confidence=0.0,
        )

        # Boost = min(0.2, 1.0 * 0.3) = 0.2
        # Total = 0.5 + 0.2 = 0.7
        assert derivation.total_confidence == pytest.approx(0.7, abs=0.01)

    def test_with_evidence_returns_new_derivation(self) -> None:
        """with_evidence returns a new Derivation, not mutating the original."""
        original = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            empirical_confidence=0.5,
        )

        updated = original.with_evidence(empirical=0.9)

        assert original.empirical_confidence == 0.5
        assert updated.empirical_confidence == 0.9
        assert original is not updated

    def test_decay_evidence_returns_new_derivation(self) -> None:
        """decay_evidence returns a new Derivation with decayed draws."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.EMPIRICAL,
        )
        original = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(draw,),
        )

        decayed = original.decay_evidence(days_elapsed=30.0)

        assert original.principle_draws[0].draw_strength == 1.0
        assert decayed.principle_draws[0].draw_strength < 1.0
        assert original is not decayed


class TestBootstrapPrincipleDraws:
    """Tests for the predefined bootstrap principle draws."""

    def test_all_bootstrap_agents_have_draws(self) -> None:
        """All 7 bootstrap agents have predefined principle draws."""
        bootstrap_agents = ("Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix")

        for agent in bootstrap_agents:
            assert agent in BOOTSTRAP_PRINCIPLE_DRAWS
            draws = BOOTSTRAP_PRINCIPLE_DRAWS[agent]
            assert len(draws) >= 1

    def test_id_draws_on_composable(self) -> None:
        """Id is the identity law—draws on Composable."""
        draws = BOOTSTRAP_PRINCIPLE_DRAWS["Id"]
        principles = {d.principle for d in draws}
        assert "Composable" in principles

    def test_judge_draws_on_ethical(self) -> None:
        """Judge embeds ethics—draws on Ethical."""
        draws = BOOTSTRAP_PRINCIPLE_DRAWS["Judge"]
        principles = {d.principle for d in draws}
        assert "Ethical" in principles

    def test_ground_draws_on_generative(self) -> None:
        """Ground seeds generation—draws on Generative."""
        draws = BOOTSTRAP_PRINCIPLE_DRAWS["Ground"]
        principles = {d.principle for d in draws}
        assert "Generative" in principles

    def test_most_bootstrap_draws_are_categorical(self) -> None:
        """Most bootstrap draws are categorical (formal proofs)."""
        total_draws = 0
        categorical_draws = 0

        for draws in BOOTSTRAP_PRINCIPLE_DRAWS.values():
            for draw in draws:
                total_draws += 1
                if draw.evidence_type == EvidenceType.CATEGORICAL:
                    categorical_draws += 1

        # At least 80% categorical
        assert categorical_draws / total_draws >= 0.8
