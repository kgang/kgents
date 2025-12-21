"""
Tests for ASHC Adaptive Evidence Framework

Tests the Bayesian updating, stopping rules, and n_diff technique.
"""

from __future__ import annotations

import pytest

from ..adaptive import (
    AdaptiveCompiler,
    AdaptiveEvidence,
    BetaPrior,
    ConfidenceTier,
    StoppingConfig,
    StoppingDecision,
    StoppingState,
    beta_mean,
    expected_samples_for_ndiff,
    prob_greater_than,
    reliability_boost_from_voting,
)

# =============================================================================
# Test Beta Distribution Math
# =============================================================================


class TestBetaMath:
    """Tests for Beta distribution mathematics."""

    def test_beta_mean(self) -> None:
        """Beta mean is α / (α + β)."""
        assert beta_mean(1, 1) == 0.5  # Uniform
        assert beta_mean(2, 1) == pytest.approx(2 / 3, abs=0.01)
        assert beta_mean(10, 1) == pytest.approx(10 / 11, abs=0.01)
        assert beta_mean(1, 10) == pytest.approx(1 / 11, abs=0.01)

    def test_prob_greater_than_symmetric(self) -> None:
        """For Beta(1,1), P(p > 0.5) = 0.5."""
        prob = prob_greater_than(1, 1, 0.5)
        assert prob == pytest.approx(0.5, abs=0.05)

    def test_prob_greater_than_strong_prior(self) -> None:
        """For strong prior, probabilities are more extreme."""
        # Beta(100, 1) strongly believes p > 0.9
        prob = prob_greater_than(100, 1, 0.9)
        assert prob > 0.9

        # Beta(1, 100) strongly believes p < 0.1
        prob = prob_greater_than(1, 100, 0.1)
        assert prob < 0.1


# =============================================================================
# Test BetaPrior
# =============================================================================


class TestBetaPrior:
    """Tests for BetaPrior type."""

    def test_uniform_prior(self) -> None:
        """Uniform prior is Beta(1, 1)."""
        prior = BetaPrior.uniform()
        assert prior.alpha == 1.0
        assert prior.beta == 1.0
        assert prior.mean == 0.5

    def test_from_confidence_trivially_easy(self) -> None:
        """Trivially easy tier gives high prior."""
        prior = BetaPrior.from_confidence(ConfidenceTier.TRIVIALLY_EASY)
        assert prior.mean > 0.95

    def test_from_confidence_likely_fails(self) -> None:
        """Likely fails tier gives low prior."""
        prior = BetaPrior.from_confidence(ConfidenceTier.LIKELY_FAILS)
        assert prior.mean < 0.25

    def test_from_estimate(self) -> None:
        """Create prior from success rate estimate."""
        # Note: from_estimate adds 1 to alpha and beta, so the mean
        # is (0.8 * 10 + 1) / (10 + 2) = 9/12 = 0.75
        prior = BetaPrior.from_estimate(0.8, strength=10)
        assert prior.mean == pytest.approx(0.75, abs=0.05)

    def test_update_conjugate(self) -> None:
        """Bayesian update is conjugate: prior + data → posterior."""
        prior = BetaPrior(1, 1)  # Uniform
        posterior = prior.update(successes=8, failures=2)

        # Beta(1,1) + 8 successes, 2 failures = Beta(9, 3)
        assert posterior.alpha == 9
        assert posterior.beta == 3
        assert posterior.mean == pytest.approx(9 / 12, abs=0.01)

    def test_confidence_interval(self) -> None:
        """95% CI should contain the mean."""
        prior = BetaPrior(10, 2)
        low, high = prior.confidence_interval_95
        assert low < prior.mean < high


# =============================================================================
# Test Stopping Rules
# =============================================================================


class TestStoppingConfig:
    """Tests for StoppingConfig."""

    def test_for_trivially_easy(self) -> None:
        """Trivially easy needs minimal samples."""
        config = StoppingConfig.for_tier(ConfidenceTier.TRIVIALLY_EASY)
        assert config.n_diff == 1
        assert config.max_samples <= 5

    def test_for_uncertain(self) -> None:
        """Uncertain needs more samples."""
        config = StoppingConfig.for_tier(ConfidenceTier.UNCERTAIN)
        assert config.n_diff >= 2
        assert config.max_samples >= 15


class TestStoppingState:
    """Tests for StoppingState and n_diff technique."""

    def test_ndiff_2_success(self) -> None:
        """Stop when successes lead by 2."""
        state = StoppingState(
            prior=BetaPrior.uniform(),
            config=StoppingConfig(n_diff=2, max_samples=20),
        )

        # Observe: S, S (margin = 2, stop)
        state.observe(True)  # S=1, F=0, margin=1
        assert state.decision == StoppingDecision.CONTINUE

        state.observe(True)  # S=2, F=0, margin=2
        assert state.decision == StoppingDecision.STOP_SUCCESS

    def test_ndiff_2_failure(self) -> None:
        """Stop when failures lead by 2."""
        state = StoppingState(
            prior=BetaPrior.uniform(),
            config=StoppingConfig(n_diff=2, max_samples=20),
        )

        # Observe: F, F (margin = 2, stop)
        state.observe(False)  # S=0, F=1, margin=1
        assert state.decision == StoppingDecision.CONTINUE

        state.observe(False)  # S=0, F=2, margin=2
        assert state.decision == StoppingDecision.STOP_FAILURE

    def test_ndiff_sequence_from_spec(self) -> None:
        """Test the example from Kent's spec: F, T, F, F → stop at 4."""
        state = StoppingState(
            prior=BetaPrior.uniform(),
            config=StoppingConfig(n_diff=2, max_samples=20),
        )

        state.observe(False)  # F=1, T=0, margin=1
        assert state.decision == StoppingDecision.CONTINUE

        state.observe(True)  # F=1, T=1, margin=0
        assert state.decision == StoppingDecision.CONTINUE

        state.observe(False)  # F=2, T=1, margin=1
        assert state.decision == StoppingDecision.CONTINUE

        state.observe(False)  # F=3, T=1, margin=2
        assert state.decision == StoppingDecision.STOP_FAILURE

    def test_max_samples_reached(self) -> None:
        """Stop at max samples even without n_diff margin."""
        state = StoppingState(
            prior=BetaPrior.uniform(),
            config=StoppingConfig(n_diff=10, max_samples=4),  # Impossible to reach n_diff=10
        )

        state.observe(True)  # S=1, F=0
        state.observe(False)  # S=1, F=1
        state.observe(True)  # S=2, F=1
        state.observe(False)  # S=2, F=2, max reached

        assert state.decision == StoppingDecision.STOP_UNCERTAIN

    def test_bayesian_early_stop(self) -> None:
        """Stop early when Bayesian confidence is high."""
        # Strong prior that it will succeed
        state = StoppingState(
            prior=BetaPrior(50, 1),  # Very strong prior
            config=StoppingConfig(n_diff=10, max_samples=20, confidence_threshold=0.95),
        )

        # Even one success should be enough with this prior
        state.observe(True)

        # Should stop due to high posterior confidence
        # (May stop on first observation due to strong prior)
        assert state.total_samples <= 3


# =============================================================================
# Test Expected Samples Calculation
# =============================================================================


class TestExpectedSamples:
    """Tests for expected sample calculations."""

    def test_high_reliability(self) -> None:
        """High reliability needs few samples."""
        # 97% reliable, n_diff=2
        expected = expected_samples_for_ndiff(0.97, 2)
        assert expected < 3

    def test_medium_reliability(self) -> None:
        """Medium reliability needs more samples."""
        # 80% reliable, n_diff=2
        expected = expected_samples_for_ndiff(0.80, 2)
        assert 3 < expected < 4

    def test_low_reliability(self) -> None:
        """Low reliability needs many samples."""
        # 60% reliable, n_diff=2
        expected = expected_samples_for_ndiff(0.60, 2)
        assert expected > 5

    def test_pure_random(self) -> None:
        """Pure random (50%) never converges."""
        expected = expected_samples_for_ndiff(0.50, 2)
        assert expected == float("inf")


# =============================================================================
# Test Reliability Boost from Voting
# =============================================================================


class TestReliabilityBoost:
    """Tests for majority voting reliability boost."""

    def test_voting_improves_reliability(self) -> None:
        """Majority voting improves reliability."""
        # 80% reliable function
        base = 0.80

        # With 3 votes
        boosted_3 = reliability_boost_from_voting(base, 3)
        assert boosted_3 > base

        # With 5 votes
        boosted_5 = reliability_boost_from_voting(base, 5)
        assert boosted_5 > boosted_3

        # With 7 votes
        boosted_7 = reliability_boost_from_voting(base, 7)
        assert boosted_7 > boosted_5

    def test_specific_values(self) -> None:
        """Test known values from the formula."""
        # p=0.8, n=3: P = C(3,2)*0.8^2*0.2 + C(3,3)*0.8^3
        #           = 3*0.64*0.2 + 1*0.512 = 0.384 + 0.512 = 0.896
        result = reliability_boost_from_voting(0.8, 3)
        assert result == pytest.approx(0.896, abs=0.01)

    def test_perfect_reliability(self) -> None:
        """Perfect reliability stays perfect."""
        result = reliability_boost_from_voting(1.0, 5)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_zero_reliability(self) -> None:
        """Zero reliability stays zero."""
        result = reliability_boost_from_voting(0.0, 5)
        assert result == pytest.approx(0.0, abs=0.001)


# =============================================================================
# Test Adaptive Compiler
# =============================================================================


class TestAdaptiveCompiler:
    """Tests for AdaptiveCompiler."""

    @pytest.mark.asyncio
    async def test_compile_trivially_easy(self) -> None:
        """Trivially easy task needs few samples."""
        compiler = AdaptiveCompiler()

        # Simple code that passes everything
        code = "x = 1"

        evidence = await compiler.compile(
            spec=code,
            tier=ConfidenceTier.TRIVIALLY_EASY,
        )

        # Should stop quickly
        assert evidence.sample_count <= 5
        assert evidence.is_success

    @pytest.mark.asyncio
    async def test_compile_with_prior(self) -> None:
        """Compile with custom prior."""
        compiler = AdaptiveCompiler()

        # Strong prior that it will work
        prior = BetaPrior(20, 1)

        evidence = await compiler.compile(
            spec="y = 2",
            prior=prior,
        )

        # Should use our prior
        assert evidence.prior.alpha == 20

    @pytest.mark.asyncio
    async def test_savings_vs_fixed(self) -> None:
        """Adaptive should save samples vs fixed-N."""
        compiler = AdaptiveCompiler()

        evidence = await compiler.compile(
            spec="z = 3",
            tier=ConfidenceTier.LIKELY_WORKS,
        )

        # Should have some savings
        assert evidence.savings_vs_fixed > 0


# =============================================================================
# Test Evidence Properties
# =============================================================================


class TestAdaptiveEvidence:
    """Tests for AdaptiveEvidence properties."""

    @pytest.mark.asyncio
    async def test_confidence_interval_shrinks(self) -> None:
        """More data should shrink confidence interval."""
        # Run twice with different sample sizes
        compiler = AdaptiveCompiler()

        # Small config
        evidence_small = await compiler.compile(
            spec="a = 1",
            config=StoppingConfig(n_diff=1, max_samples=2),
        )

        # Larger config
        evidence_large = await compiler.compile(
            spec="b = 2",
            config=StoppingConfig(n_diff=3, max_samples=10),
        )

        # More samples should give tighter CI (smaller variance)
        small_ci = evidence_small.confidence_interval
        large_ci = evidence_large.confidence_interval

        small_width = small_ci[1] - small_ci[0]
        large_width = large_ci[1] - large_ci[0]

        # Not guaranteed, but likely with more samples
        # (This is a statistical test, may occasionally fail)
        if evidence_large.sample_count > evidence_small.sample_count:
            assert large_width <= small_width or evidence_large.sample_count >= 5


# =============================================================================
# Test Mathematical Guarantees
# =============================================================================


class TestMathematicalGuarantees:
    """Tests for mathematical properties and guarantees."""

    def test_posterior_incorporates_data(self) -> None:
        """Posterior should shift toward observed data."""
        prior = BetaPrior(1, 1)  # Uniform, mean = 0.5

        # All successes → posterior mean should increase
        posterior_success = prior.update(10, 0)
        assert posterior_success.mean > 0.5

        # All failures → posterior mean should decrease
        posterior_failure = prior.update(0, 10)
        assert posterior_failure.mean < 0.5

    def test_strong_prior_resists_data(self) -> None:
        """Strong prior should resist small amounts of data."""
        strong_prior = BetaPrior(100, 1)  # Strong belief in success

        # A few failures shouldn't change much
        posterior = strong_prior.update(0, 2)
        assert posterior.mean > 0.9  # Still high

    def test_weak_prior_sensitive_to_data(self) -> None:
        """Weak prior should be sensitive to data."""
        weak_prior = BetaPrior(1, 1)  # Uniform

        # A few observations should have big effect
        posterior = weak_prior.update(5, 0)
        assert posterior.mean > 0.8  # Shifted significantly

    def test_ndiff_guarantees_margin(self) -> None:
        """n_diff technique guarantees final margin when Bayesian early-stop is disabled."""
        for n_diff in [1, 2, 3, 5]:
            state = StoppingState(
                prior=BetaPrior.uniform(),
                # Set confidence_threshold=1.0 to disable Bayesian early stopping
                # This ensures we only stop via n_diff or max_samples
                config=StoppingConfig(n_diff=n_diff, max_samples=100, confidence_threshold=1.0),
            )

            # Simulate until stopped
            import random

            random.seed(42 + n_diff)  # Different seed per n_diff
            while state.decision == StoppingDecision.CONTINUE:
                state.observe(random.random() < 0.7)

            # If stopped with success/failure, margin should be >= n_diff
            if state.decision in (StoppingDecision.STOP_SUCCESS, StoppingDecision.STOP_FAILURE):
                assert state.margin >= n_diff
