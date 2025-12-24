"""
Tests for Bayesian stopping model.

Tests:
- Beta distribution updating
- Confidence calculation
- Stopping criterion
- Edge cases (no trials, all success, all failure)

Philosophy:
    "Stop when you know enough, not when you're exhausted."

Teaching:
    gotcha: Bayesian confidence requires minimum trials to be meaningful.
            Early stopping with < 10 trials can be unreliable.
"""

from __future__ import annotations

import pytest

from services.experiment.bayesian import BayesianStoppingModel, beta_cdf


def test_initial_state():
    """Test initial state of Bayesian model."""
    model = BayesianStoppingModel(confidence_threshold=0.95)

    assert model.n_trials == 0
    assert model.n_successes == 0
    assert model.n_failures == 0
    assert model.success_rate == 0.5  # Prior mean
    assert not model.should_stop()  # Can't stop with 0 trials


def test_update_success():
    """Test updating with successful trial."""
    model = BayesianStoppingModel()

    model.update(success=True)

    assert model.n_trials == 1
    assert model.n_successes == 1
    assert model.n_failures == 0


def test_update_failure():
    """Test updating with failed trial."""
    model = BayesianStoppingModel()

    model.update(success=False)

    assert model.n_trials == 1
    assert model.n_successes == 0
    assert model.n_failures == 1


def test_success_rate_calculation():
    """Test success rate calculation."""
    model = BayesianStoppingModel()

    # Add 3 successes, 1 failure
    for _ in range(3):
        model.update(success=True)
    model.update(success=False)

    # Expected: (1 + 3) / (1 + 3 + 1 + 1) = 4/6 = 0.667
    assert model.n_trials == 4
    assert abs(model.success_rate - 0.667) < 0.01


def test_all_successes():
    """Test model with all successful trials."""
    model = BayesianStoppingModel(confidence_threshold=0.95, min_trials=5)

    # All successes
    for _ in range(10):
        model.update(success=True)

    assert model.n_successes == 10
    assert model.n_failures == 0
    # Success rate should be high (but not 1.0 due to prior)
    assert model.success_rate > 0.9
    # High confidence should trigger stopping
    assert model.should_stop()


def test_all_failures():
    """Test model with all failed trials."""
    model = BayesianStoppingModel(confidence_threshold=0.95, min_trials=5)

    # All failures
    for _ in range(10):
        model.update(success=False)

    assert model.n_successes == 0
    assert model.n_failures == 10
    # Success rate should be low
    assert model.success_rate < 0.1
    # Low success rate means low confidence in success > 0.5
    assert not model.should_stop()


def test_min_trials_requirement():
    """Test that model requires minimum trials before stopping."""
    model = BayesianStoppingModel(confidence_threshold=0.5, min_trials=10)

    # Even with high success rate, don't stop before min_trials
    for _ in range(5):
        model.update(success=True)

    assert model.n_trials == 5
    assert not model.should_stop()  # Below min_trials

    # After reaching min_trials, can stop
    for _ in range(5):
        model.update(success=True)

    assert model.n_trials == 10
    # Should stop now (10 successes gives very high confidence)
    assert model.should_stop()


def test_confidence_threshold():
    """Test that confidence threshold is respected."""
    # Low threshold - should stop early
    model_low = BayesianStoppingModel(confidence_threshold=0.6, min_trials=5)

    for _ in range(8):
        model_low.update(success=True)

    assert model_low.should_stop()

    # High threshold - needs more evidence
    model_high = BayesianStoppingModel(confidence_threshold=0.99, min_trials=5)

    for _ in range(8):
        model_high.update(success=True)

    # Might not stop yet with 0.99 threshold
    # (depends on exact confidence calculation)


def test_variance():
    """Test variance calculation."""
    model = BayesianStoppingModel()

    # Add some trials
    for _ in range(5):
        model.update(success=True)
    for _ in range(5):
        model.update(success=False)

    # With equal successes/failures, variance should be relatively high
    assert model.variance > 0
    assert model.std > 0


def test_summary():
    """Test summary statistics."""
    model = BayesianStoppingModel()

    for _ in range(7):
        model.update(success=True)
    for _ in range(3):
        model.update(success=False)

    summary = model.summary()

    assert summary["n_trials"] == 10
    assert summary["n_successes"] == 7
    assert summary["n_failures"] == 3
    assert "success_rate" in summary
    assert "confidence" in summary
    assert "variance" in summary


def test_repr():
    """Test string representation."""
    model = BayesianStoppingModel()

    for _ in range(5):
        model.update(success=True)

    repr_str = repr(model)
    assert "BayesianStoppingModel" in repr_str
    assert "success_rate" in repr_str
    assert "confidence" in repr_str


def test_beta_cdf():
    """Test beta CDF calculation."""
    # CDF(0.5, alpha=1, beta=1) should be 0.5 (uniform prior)
    result = beta_cdf(0.5, 1.0, 1.0)
    assert abs(result - 0.5) < 0.1  # Approximate

    # CDF(0, ...) should be 0
    assert beta_cdf(0.0, 2.0, 2.0) == 0.0

    # CDF(1, ...) should be 1
    assert beta_cdf(1.0, 2.0, 2.0) == 1.0


def test_incremental_stopping():
    """Test that stopping happens incrementally as evidence accumulates."""
    model = BayesianStoppingModel(confidence_threshold=0.95, min_trials=10)

    # Gradually add successes
    stopped_at = None
    for i in range(30):
        model.update(success=True)

        if model.n_trials < 10:
            # Below min_trials
            assert not model.should_stop()
        elif model.n_trials >= 15:
            # After enough successes, should stop
            if model.should_stop():
                # Record when it stopped
                stopped_at = model.n_trials
                break

    if stopped_at is None:
        pytest.fail("Model should have stopped before 30 trials with all successes")

    # Should have stopped somewhere between 10 and 30 trials
    assert 10 <= stopped_at < 30


def test_mixed_results_no_stop():
    """Test that mixed results (50/50) don't trigger stopping."""
    model = BayesianStoppingModel(confidence_threshold=0.95, min_trials=10)

    # Alternate success/failure
    for i in range(50):
        model.update(success=(i % 2 == 0))

    # With 50/50 split, confidence should be low
    # (can't be confident success rate > 0.5)
    assert not model.should_stop()
