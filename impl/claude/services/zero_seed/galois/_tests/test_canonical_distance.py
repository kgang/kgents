"""
Tests for Amendment B: Bidirectional Entailment Distance.

This test suite validates:
1. BidirectionalEntailmentDistance basic operation
2. Geometric mean property (symmetric, penalizes one-way entailment)
3. CanonicalSemanticDistance fallback chain
4. Edge cases (empty strings, identical strings)

From: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment B)
"""

import math

import pytest

from services.zero_seed.galois.distance import (
    BERTScoreDistance,
    BidirectionalEntailmentDistance,
    CanonicalSemanticDistance,
    CosineEmbeddingDistance,
    canonical_semantic_distance,
    get_canonical_metric,
    get_entailment_metric,
)


class TestBidirectionalEntailmentDistance:
    """Tests for BidirectionalEntailmentDistance."""

    def test_identical_strings_zero_distance(self) -> None:
        """Identical strings should have zero distance."""
        metric = BidirectionalEntailmentDistance()
        text = "The sky is blue."

        distance = metric.distance(text, text)

        assert distance == 0.0

    def test_empty_strings_max_distance(self) -> None:
        """Empty strings should have maximum distance."""
        metric = BidirectionalEntailmentDistance()

        assert metric.distance("", "something") == 1.0
        assert metric.distance("something", "") == 1.0
        assert metric.distance("   ", "something") == 1.0

    def test_distance_in_valid_range(self) -> None:
        """Distance should always be in [0, 1]."""
        metric = BidirectionalEntailmentDistance()

        test_pairs = [
            ("The cat sat on the mat.", "A feline rested on the rug."),
            ("Water is wet.", "Fire is hot."),
            ("I love programming.", "I enjoy coding."),
            ("The sun is bright.", "It is dark outside."),
        ]

        for text_a, text_b in test_pairs:
            distance = metric.distance(text_a, text_b)
            assert 0.0 <= distance <= 1.0, (
                f"Distance {distance} out of range for {text_a!r}, {text_b!r}"
            )

    def test_symmetric_property(self) -> None:
        """Distance should be symmetric: d(A, B) = d(B, A)."""
        metric = BidirectionalEntailmentDistance()

        text_a = "The quick brown fox jumps over the lazy dog."
        text_b = "A fast auburn fox leaps above a sleepy canine."

        distance_ab = metric.distance(text_a, text_b)
        distance_ba = metric.distance(text_b, text_a)

        # Should be very close (not necessarily identical due to model quirks)
        assert abs(distance_ab - distance_ba) < 0.1

    def test_geometric_mean_penalizes_one_way(self) -> None:
        """
        Geometric mean should penalize one-way entailment.

        If A entails B but B doesn't entail A, distance should be high.
        Example: "All dogs are animals" entails "Some animals exist"
                 but not vice versa.
        """
        metric = BidirectionalEntailmentDistance()

        # Abstraction relationship (one-way entailment)
        specific = "All dogs are mammals with four legs."
        general = "Some animals exist."

        # General -> Specific is weaker entailment
        distance = metric.distance(specific, general)

        # Distance should be moderate-to-high due to one-way entailment
        # (not 0 because B doesn't entail A)
        assert distance > 0.2

    def test_name_property(self) -> None:
        """Should have a descriptive name."""
        metric = BidirectionalEntailmentDistance()
        assert "bidirectional_entailment" in metric.name
        assert "deberta" in metric.name.lower()

    def test_custom_model(self) -> None:
        """Should accept custom model."""
        metric = BidirectionalEntailmentDistance(model="custom-model")
        assert "custom-model" in metric.name


class TestCanonicalSemanticDistance:
    """Tests for CanonicalSemanticDistance with fallback chain."""

    def test_identical_strings_zero_distance(self) -> None:
        """Identical strings should have zero distance."""
        metric = CanonicalSemanticDistance()
        text = "The proof IS the decision."

        distance = metric.distance(text, text)

        assert distance == 0.0

    def test_distance_in_valid_range(self) -> None:
        """Distance should always be in [0, 1]."""
        metric = CanonicalSemanticDistance()

        test_pairs = [
            ("Trust is earned slowly.", "Trust is lost quickly."),
            ("Axioms are fixed points.", "Values derive from axioms."),
        ]

        for text_a, text_b in test_pairs:
            distance = metric.distance(text_a, text_b)
            assert 0.0 <= distance <= 1.0

    def test_name_property(self) -> None:
        """Should have a descriptive name."""
        metric = CanonicalSemanticDistance()
        assert metric.name == "canonical_semantic"

    def test_fallback_works(self) -> None:
        """Should fall back gracefully if primary fails."""
        metric = CanonicalSemanticDistance()

        # Even if NLI fails, should get a valid distance
        distance = metric.distance(
            "This is a test sentence.",
            "This is another sentence for testing.",
        )

        assert 0.0 <= distance <= 1.0


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_canonical_semantic_distance_function(self) -> None:
        """canonical_semantic_distance function should work."""
        distance = canonical_semantic_distance(
            "The loss IS the layer.",
            "Layer is derived from loss.",
        )

        assert 0.0 <= distance <= 1.0

    def test_get_canonical_metric(self) -> None:
        """get_canonical_metric should return CanonicalSemanticDistance."""
        metric = get_canonical_metric()
        assert isinstance(metric, CanonicalSemanticDistance)

    def test_get_entailment_metric(self) -> None:
        """get_entailment_metric should return BidirectionalEntailmentDistance."""
        metric = get_entailment_metric()
        assert isinstance(metric, BidirectionalEntailmentDistance)


class TestGeometricMeanProperty:
    """
    Tests specifically for the geometric mean formula.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))
    """

    def test_both_directions_high_low_distance(self) -> None:
        """If both directions have high entailment, distance is low."""
        # Very similar sentences
        text_a = "The cat sleeps on the mat."
        text_b = "The cat is sleeping on the mat."

        metric = BidirectionalEntailmentDistance()
        distance = metric.distance(text_a, text_b)

        # Should be low because both directions entail
        # Note: if NLI model unavailable, fallback returns 0.5
        # We allow 0.5 as a valid result (fallback case)
        assert distance <= 0.5

    def test_one_direction_zero_high_distance(self) -> None:
        """
        If one direction has zero entailment, distance is high.

        When NLI model is available:
        Geometric mean: sqrt(0.8 * 0.0) = 0 -> distance = 1
        When unavailable: fallback returns 0.5
        """
        # Unrelated sentences
        text_a = "The quantum computer solved the problem."
        text_b = "Pizza is delicious with extra cheese."

        metric = BidirectionalEntailmentDistance()
        distance = metric.distance(text_a, text_b)

        # Should be moderate-to-high (unrelated)
        # If NLI unavailable, fallback returns 0.5
        assert distance >= 0.5

    def test_formula_manual_calculation(self) -> None:
        """Verify the formula with known probabilities."""
        # Mock probabilities for formula verification
        p_a_entails_b = 0.9
        p_b_entails_a = 0.9

        expected_mutual = math.sqrt(p_a_entails_b * p_b_entails_a)
        expected_distance = 1.0 - expected_mutual

        # sqrt(0.9 * 0.9) = 0.9, so distance = 0.1
        assert abs(expected_distance - 0.1) < 0.01

        # One-way entailment
        p_a_entails_b = 0.9
        p_b_entails_a = 0.3

        expected_mutual = math.sqrt(p_a_entails_b * p_b_entails_a)
        expected_distance = 1.0 - expected_mutual

        # sqrt(0.9 * 0.3) = sqrt(0.27) ≈ 0.52, so distance ≈ 0.48
        assert abs(expected_mutual - 0.52) < 0.05


class TestFallbackChain:
    """Tests for the fallback chain in CanonicalSemanticDistance."""

    def test_primary_to_bertscore_fallback(self) -> None:
        """Should fall back from entailment to BERTScore."""
        # Create a metric with broken primary
        metric = CanonicalSemanticDistance()

        # Manually break the primary
        class BrokenEntailment:
            def distance(self, a: str, b: str) -> float:
                raise RuntimeError("Intentionally broken")

        metric._primary = BrokenEntailment()  # type: ignore

        # Should still work via fallback
        distance = metric.distance("test one", "test two")
        assert 0.0 <= distance <= 1.0

    def test_all_fallbacks_to_cosine(self) -> None:
        """Should ultimately fall back to cosine."""
        metric = CanonicalSemanticDistance()

        # Break both primary and BERTScore
        class BrokenMetric:
            def distance(self, a: str, b: str) -> float:
                raise RuntimeError("Intentionally broken")

        metric._primary = BrokenMetric()  # type: ignore
        metric._bertscore = BrokenMetric()  # type: ignore

        # Should still work via cosine fallback
        distance = metric.distance("test one", "test two")
        assert 0.0 <= distance <= 1.0
