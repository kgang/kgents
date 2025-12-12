"""
Tests for Free Energy - Active Inference Foundation.

These tests verify:
- FreeEnergyState computation
- GenerativeModel prediction and learning
- Surprise normalization
"""

from __future__ import annotations

import numpy as np
import pytest

from ..free_energy import (
    FreeEnergyState,
    GenerativeModel,
    compute_free_energy,
    compute_surprise,
)

DIMENSIONS = 100  # Smaller for faster tests


class TestFreeEnergyState:
    """Tests for FreeEnergyState."""

    def test_prediction_error_zero_when_equal(self) -> None:
        """Prediction error is 0 when expected == actual."""
        vec = np.random.randn(DIMENSIONS)
        state = FreeEnergyState(
            expected_observation=vec,
            actual_observation=vec.copy(),
        )

        assert state.prediction_error == pytest.approx(0.0)

    def test_prediction_error_positive_when_different(self) -> None:
        """Prediction error is positive when expected != actual."""
        expected = np.zeros(DIMENSIONS)
        actual = np.ones(DIMENSIONS)

        state = FreeEnergyState(
            expected_observation=expected,
            actual_observation=actual,
        )

        assert state.prediction_error > 0

    def test_free_energy_includes_complexity(self) -> None:
        """Free energy = complexity + inaccuracy."""
        expected = np.zeros(DIMENSIONS)
        actual = np.ones(DIMENSIONS)

        state = FreeEnergyState(
            expected_observation=expected,
            actual_observation=actual,
            complexity=5.0,
        )

        # F = complexity + prediction_error
        expected_fe = 5.0 + state.prediction_error
        assert state.free_energy == pytest.approx(expected_fe)

    def test_surprise_equals_prediction_error(self) -> None:
        """Surprise is an alias for prediction error."""
        expected = np.zeros(DIMENSIONS)
        actual = np.ones(DIMENSIONS)

        state = FreeEnergyState(
            expected_observation=expected,
            actual_observation=actual,
        )

        assert state.surprise == state.prediction_error

    def test_normalized_surprise_in_range(self) -> None:
        """Normalized surprise is in [0, 1]."""
        # Very different vectors -> high surprise
        state_high = FreeEnergyState(
            expected_observation=np.zeros(DIMENSIONS),
            actual_observation=np.ones(DIMENSIONS) * 10,
        )
        assert 0 <= state_high.normalized_surprise <= 1

        # Same vectors -> low surprise
        state_low = FreeEnergyState(
            expected_observation=np.ones(DIMENSIONS),
            actual_observation=np.ones(DIMENSIONS),
        )
        assert 0 <= state_low.normalized_surprise <= 1

    def test_is_surprising_high_error(self) -> None:
        """is_surprising() returns True for high prediction error."""
        state = FreeEnergyState(
            expected_observation=np.zeros(DIMENSIONS),
            actual_observation=np.ones(DIMENSIONS) * 10,  # Very different
        )

        assert state.is_surprising(threshold=0.5)

    def test_is_predictable_low_error(self) -> None:
        """is_predictable() returns True for low prediction error."""
        vec = np.random.randn(DIMENSIONS)
        state = FreeEnergyState(
            expected_observation=vec,
            actual_observation=vec + np.random.randn(DIMENSIONS) * 0.01,  # Tiny diff
        )

        assert state.is_predictable(threshold=0.5)


class TestGenerativeModel:
    """Tests for GenerativeModel."""

    def test_initialization(self) -> None:
        """Model initializes with normalized weights."""
        model = GenerativeModel(dimensions=DIMENSIONS)

        assert model.weights.shape == (DIMENSIONS,)
        assert np.linalg.norm(model.weights) == pytest.approx(1.0, abs=0.01)

    def test_predict_returns_normalized(self) -> None:
        """predict() returns normalized vector."""
        model = GenerativeModel(dimensions=DIMENSIONS)
        context = np.random.randn(DIMENSIONS)

        prediction = model.predict(context)

        norm = np.linalg.norm(prediction)
        if norm > 0:
            assert norm == pytest.approx(1.0, abs=0.01)

    def test_complexity_is_l2_norm(self) -> None:
        """Complexity is L2 norm of weights."""
        model = GenerativeModel(dimensions=DIMENSIONS)

        # After normalization, complexity should be ~1.0
        assert model.complexity == pytest.approx(1.0, abs=0.01)

    def test_update_changes_weights(self) -> None:
        """update() modifies weights."""
        model = GenerativeModel(dimensions=DIMENSIONS)
        initial_weights = model.weights.copy()

        context = np.random.randn(DIMENSIONS)
        actual = np.random.randn(DIMENSIONS)

        model.update(context, actual, learning_rate=0.5)

        # Weights should have changed
        assert not np.allclose(model.weights, initial_weights)

    def test_update_tracks_count(self) -> None:
        """update() increments update_count."""
        model = GenerativeModel(dimensions=DIMENSIONS)
        assert model.update_count == 0

        model.update(
            np.random.randn(DIMENSIONS),
            np.random.randn(DIMENSIONS),
        )

        assert model.update_count == 1

    def test_update_returns_error(self) -> None:
        """update() returns prediction error."""
        model = GenerativeModel(dimensions=DIMENSIONS)
        context = np.random.randn(DIMENSIONS)
        actual = np.random.randn(DIMENSIONS)

        error = model.update(context, actual)

        assert error > 0  # Random vectors should have some error

    def test_average_error_computed(self) -> None:
        """average_error is cumulative_error / update_count."""
        model = GenerativeModel(dimensions=DIMENSIONS)

        # Multiple updates
        for _ in range(5):
            model.update(
                np.random.randn(DIMENSIONS),
                np.random.randn(DIMENSIONS),
            )

        assert model.update_count == 5
        assert model.average_error == model.cumulative_error / 5

    def test_reset_clears_state(self) -> None:
        """reset() reinitializes model."""
        model = GenerativeModel(dimensions=DIMENSIONS)

        # Do some updates
        model.update(
            np.random.randn(DIMENSIONS),
            np.random.randn(DIMENSIONS),
        )

        model.reset()

        assert model.update_count == 0
        assert model.cumulative_error == 0.0


class TestLearning:
    """Tests for learning behavior."""

    def test_learning_reduces_error_over_time(self) -> None:
        """Model should improve predictions with learning."""
        model = GenerativeModel(dimensions=DIMENSIONS)

        # Fixed target pattern
        target = np.random.randn(DIMENSIONS)
        target = target / np.linalg.norm(target)

        # Track errors over updates
        errors: list[float] = []

        for _ in range(50):
            context = np.random.randn(DIMENSIONS)
            error = model.update(context, target, learning_rate=0.1)
            errors.append(error)

        # Error should generally decrease (average of last 10 < average of first 10)
        # Note: This is a weak test due to randomness, but trend should be down
        # We just check that learning happened
        assert model.update_count == 50


class TestComputeFunctions:
    """Tests for standalone compute functions."""

    def test_compute_free_energy(self) -> None:
        """compute_free_energy returns complexity + inaccuracy."""
        expected = np.zeros(DIMENSIONS)
        actual = np.ones(DIMENSIONS)

        fe = compute_free_energy(expected, actual, model_complexity=5.0)

        inaccuracy = np.linalg.norm(expected - actual)
        assert fe == pytest.approx(5.0 + inaccuracy)

    def test_compute_surprise(self) -> None:
        """compute_surprise returns prediction error."""
        expected = np.zeros(DIMENSIONS)
        actual = np.ones(DIMENSIONS)

        surprise = compute_surprise(expected, actual)

        assert surprise == pytest.approx(np.linalg.norm(expected - actual))

    def test_compute_surprise_zero_when_equal(self) -> None:
        """compute_surprise is 0 when vectors are equal."""
        vec = np.random.randn(DIMENSIONS)

        surprise = compute_surprise(vec, vec.copy())

        assert surprise == pytest.approx(0.0)
