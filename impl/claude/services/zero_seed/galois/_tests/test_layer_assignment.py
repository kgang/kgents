"""
Tests for Amendment C: Corpus-Relative Layer Assignment.

This test suite validates:
1. Absolute layer assignment (fixed bounds)
2. Relative layer assignment (percentile-based)
3. LayerAssigner class with corpus learning
4. Calibration set for regression testing

From: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment C)
"""

import pytest

from services.zero_seed.galois.layer_assignment import (
    CALIBRATION_CORPUS,
    LAYER_LOSS_BOUNDS,
    LAYER_NAMES,
    MIN_CORPUS_SIZE,
    LayerAssigner,
    LayerAssignment,
    assign_layer_absolute,
    assign_layer_relative,
    validate_calibration,
)


class TestAbsoluteLayerAssignment:
    """Tests for absolute layer assignment."""

    def test_layer_1_axiom(self) -> None:
        """Very low loss should be Layer 1 (Axiom)."""
        assignment = assign_layer_absolute(0.02)

        assert assignment.layer == 1
        assert assignment.layer_name == "Axiom"
        assert assignment.method == "absolute"
        assert assignment.confidence > 0.5

    def test_layer_2_value(self) -> None:
        """Loss 0.05-0.15 should be Layer 2 (Value)."""
        assignment = assign_layer_absolute(0.10)

        assert assignment.layer == 2
        assert assignment.layer_name == "Value"
        assert assignment.method == "absolute"

    def test_layer_3_goal(self) -> None:
        """Loss 0.15-0.30 should be Layer 3 (Goal)."""
        assignment = assign_layer_absolute(0.22)

        assert assignment.layer == 3
        assert assignment.layer_name == "Goal"

    def test_layer_4_spec(self) -> None:
        """Loss 0.30-0.45 should be Layer 4 (Spec)."""
        assignment = assign_layer_absolute(0.37)

        assert assignment.layer == 4
        assert assignment.layer_name == "Spec"

    def test_layer_5_execution(self) -> None:
        """Loss 0.45-0.60 should be Layer 5 (Execution)."""
        assignment = assign_layer_absolute(0.52)

        assert assignment.layer == 5
        assert assignment.layer_name == "Execution"

    def test_layer_6_reflection(self) -> None:
        """Loss 0.60-0.75 should be Layer 6 (Reflection)."""
        assignment = assign_layer_absolute(0.68)

        assert assignment.layer == 6
        assert assignment.layer_name == "Reflection"

    def test_layer_7_representation(self) -> None:
        """Loss 0.75-1.0 should be Layer 7 (Representation)."""
        assignment = assign_layer_absolute(0.85)

        assert assignment.layer == 7
        assert assignment.layer_name == "Representation"

    def test_boundary_cases(self) -> None:
        """Test exact boundary values."""
        # Exactly at lower bound of L2
        assignment = assign_layer_absolute(0.05)
        assert assignment.layer == 2

        # Exactly at lower bound of L3
        assignment = assign_layer_absolute(0.15)
        assert assignment.layer == 3

    def test_extreme_values(self) -> None:
        """Test extreme loss values."""
        # Loss = 0
        assignment = assign_layer_absolute(0.0)
        assert assignment.layer == 1

        # Loss = 1.0 (should be L7)
        assignment = assign_layer_absolute(1.0)
        assert assignment.layer == 7

        # Loss > 1.0 (should clamp to L7)
        assignment = assign_layer_absolute(1.5)
        assert assignment.layer == 7

        # Negative loss (should clamp to L1)
        assignment = assign_layer_absolute(-0.1)
        assert assignment.layer == 1

    def test_confidence_highest_at_center(self) -> None:
        """Confidence should be highest at center of layer range."""
        # Center of L3 is (0.15 + 0.30) / 2 = 0.225
        assignment = assign_layer_absolute(0.225)
        center_confidence = assignment.confidence

        # Edges of L3
        edge_assignment = assign_layer_absolute(0.16)
        edge_confidence = edge_assignment.confidence

        assert center_confidence >= edge_confidence


class TestRelativeLayerAssignment:
    """Tests for relative layer assignment."""

    def test_empty_corpus_falls_back_to_absolute(self) -> None:
        """Empty corpus should fall back to absolute assignment."""
        assignment = assign_layer_relative(0.10, [])

        assert assignment.layer == 2
        assert assignment.method == "absolute"

    def test_percentile_based_assignment(self) -> None:
        """Should assign based on percentile in corpus."""
        # Create a uniform corpus
        corpus = [i / 100 for i in range(100)]  # 0.00, 0.01, ..., 0.99

        # Loss of 0.14 is at 14th percentile -> L1 (0-14%)
        assignment = assign_layer_relative(0.14, corpus)
        assert assignment.method == "relative"
        assert assignment.percentile is not None
        assert abs(assignment.percentile - 0.14) < 0.02

        # Loss of 0.50 is at 50th percentile -> L4 (43-57%)
        assignment = assign_layer_relative(0.50, corpus)
        assert assignment.percentile is not None
        assert abs(assignment.percentile - 0.50) < 0.02

        # Loss of 0.90 is at 90th percentile -> L7 (86-100%)
        assignment = assign_layer_relative(0.90, corpus)
        assert assignment.layer == 7

    def test_skewed_corpus(self) -> None:
        """Should adapt to skewed corpus distributions."""
        # All losses are low (0.0 to 0.2)
        low_corpus = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20] * 3

        # In this corpus, 0.15 is above average
        assignment = assign_layer_relative(0.15, low_corpus)
        assert assignment.layer >= 3  # Should be mid-to-high layer

        # 0.08 should be low layer
        assignment = assign_layer_relative(0.08, low_corpus)
        assert assignment.layer <= 3

    def test_percentile_in_result(self) -> None:
        """Relative assignment should include percentile."""
        corpus = [0.1, 0.2, 0.3, 0.4, 0.5]

        assignment = assign_layer_relative(0.25, corpus)

        assert assignment.percentile is not None
        assert 0.0 <= assignment.percentile <= 1.0


class TestLayerAssigner:
    """Tests for LayerAssigner class."""

    def test_starts_with_absolute(self) -> None:
        """Should use absolute assignment initially."""
        assigner = LayerAssigner()

        assignment = assigner.assign(0.10)

        assert assignment.method == "absolute"
        assert not assigner.uses_relative

    def test_transitions_to_relative(self) -> None:
        """Should transition to relative after min corpus size."""
        assigner = LayerAssigner(min_corpus_size=5)

        # Add 5 losses to corpus
        for loss in [0.1, 0.2, 0.3, 0.4, 0.5]:
            assigner.add_to_corpus(loss)

        assert assigner.uses_relative

        # Now should use relative
        assignment = assigner.assign(0.25)
        assert assignment.method == "relative"

    def test_use_corpus_flag(self) -> None:
        """Should respect use_corpus=False."""
        assigner = LayerAssigner(min_corpus_size=5)

        # Add enough for relative
        for loss in [0.1, 0.2, 0.3, 0.4, 0.5]:
            assigner.add_to_corpus(loss)

        # Force absolute
        assignment = assigner.assign(0.25, use_corpus=False)
        assert assignment.method == "absolute"

    def test_corpus_stats(self) -> None:
        """Should compute corpus statistics."""
        assigner = LayerAssigner()

        assigner.add_to_corpus(0.1)
        assigner.add_to_corpus(0.3)
        assigner.add_to_corpus(0.5)

        stats = assigner.corpus_stats()

        assert stats["min"] == 0.1
        assert stats["max"] == 0.5
        assert abs(stats["mean"] - 0.3) < 0.01
        assert stats["count"] == 3

    def test_clear_corpus(self) -> None:
        """Should be able to clear corpus."""
        assigner = LayerAssigner()

        assigner.add_to_corpus(0.1)
        assigner.add_to_corpus(0.2)

        assert assigner.corpus_size == 2

        assigner.clear_corpus()

        assert assigner.corpus_size == 0
        assert assigner.corpus_stats() == {}


class TestLayerAssignmentDataclass:
    """Tests for LayerAssignment dataclass."""

    def test_is_absolute_property(self) -> None:
        """Should correctly identify absolute method."""
        assignment = LayerAssignment(
            layer=3,
            layer_name="Goal",
            confidence=0.8,
            method="absolute",
            loss=0.22,
        )

        assert assignment.is_absolute
        assert not assignment.is_relative

    def test_is_relative_property(self) -> None:
        """Should correctly identify relative method."""
        assignment = LayerAssignment(
            layer=3,
            layer_name="Goal",
            confidence=0.8,
            method="relative",
            loss=0.22,
            percentile=0.5,
        )

        assert assignment.is_relative
        assert not assignment.is_absolute

    def test_str_representation(self) -> None:
        """Should have readable string representation."""
        assignment = LayerAssignment(
            layer=2,
            layer_name="Value",
            confidence=0.75,
            method="absolute",
            loss=0.10,
        )

        s = str(assignment)

        assert "L2" in s
        assert "Value" in s
        assert "0.10" in s or "0.1" in s
        assert "absolute" in s


class TestCalibrationSet:
    """Tests for calibration set and validation."""

    def test_calibration_corpus_structure(self) -> None:
        """Calibration corpus should have valid structure."""
        for content, expected_layer in CALIBRATION_CORPUS:
            assert isinstance(content, str)
            assert len(content) > 0
            assert 1 <= expected_layer <= 7

    def test_calibration_layers_present(self) -> None:
        """Calibration should cover multiple layers."""
        layers = {layer for _, layer in CALIBRATION_CORPUS}

        # Should have at least L1, L2, L3, L5
        assert 1 in layers
        assert 2 in layers
        assert 3 in layers
        assert 5 in layers

    def test_validate_calibration_with_mock(self) -> None:
        """Validate calibration with mock loss computer."""
        # Mock that returns loss based on expected layer
        def mock_loss(content: str) -> float:
            for cal_content, layer in CALIBRATION_CORPUS:
                if content == cal_content:
                    # Return loss in the expected layer's range
                    low, high = LAYER_LOSS_BOUNDS[layer]
                    return (low + high) / 2
            return 0.5

        all_passed, results = validate_calibration(mock_loss)

        assert all_passed
        assert len(results) == len(CALIBRATION_CORPUS)
        for result in results:
            assert result["passed"]


class TestConstants:
    """Tests for module constants."""

    def test_layer_bounds_complete(self) -> None:
        """Layer bounds should cover all 7 layers."""
        assert len(LAYER_LOSS_BOUNDS) == 7
        for layer in range(1, 8):
            assert layer in LAYER_LOSS_BOUNDS

    def test_layer_bounds_continuous(self) -> None:
        """Layer bounds should be continuous (no gaps)."""
        sorted_layers = sorted(LAYER_LOSS_BOUNDS.keys())

        for i in range(len(sorted_layers) - 1):
            current_layer = sorted_layers[i]
            next_layer = sorted_layers[i + 1]

            current_high = LAYER_LOSS_BOUNDS[current_layer][1]
            next_low = LAYER_LOSS_BOUNDS[next_layer][0]

            assert current_high == next_low, f"Gap between L{current_layer} and L{next_layer}"

    def test_layer_names_complete(self) -> None:
        """Layer names should cover all 7 layers."""
        assert len(LAYER_NAMES) == 7
        for layer in range(1, 8):
            assert layer in LAYER_NAMES
            assert len(LAYER_NAMES[layer]) > 0
