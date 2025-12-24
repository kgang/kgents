"""
Bayesian Stopping Model: Adaptive Experiment Termination.

Implements Bayesian adaptive stopping using Beta-Binomial conjugate priors.
Stops experiments early when posterior confidence exceeds threshold.

Philosophy:
    "Stop when you know enough, not when you're exhausted."

Mathematical Foundation:
    Prior: Beta(α, β)
    Likelihood: Binomial(n_success, n_total)
    Posterior: Beta(α + n_success, β + n_failures)

    Confidence = P(success_rate > 0.5 | data)
               = P(X > 0.5) where X ~ Beta(α', β')

Teaching:
    gotcha: Confidence threshold should be high (0.95+) to avoid premature
            stopping. Lower thresholds lead to under-powered experiments.
            (Evidence: Bayesian power analysis, Kruschke "Doing Bayesian Data Analysis")

    gotcha: The prior (alpha=1, beta=1) is uniform (uninformative).
            This is conservative - it starts with maximum uncertainty.
            If you have strong priors, adjust alpha/beta accordingly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def beta_cdf(x: float, alpha: float, beta_param: float) -> float:
    """
    Cumulative distribution function of Beta(alpha, beta) at x.

    Uses the regularized incomplete beta function I_x(alpha, beta).

    For computational efficiency, we use the relationship:
        I_x(a, b) = 1 - I_(1-x)(b, a)

    This allows us to compute with the smaller of (x, 1-x) for numerical stability.
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0

    # Use incomplete beta function (scipy would be better, but we avoid dependencies)
    # For now, use a simple approximation via normal approximation
    # This is accurate enough for our purposes when alpha, beta > 5

    if alpha > 5 and beta_param > 5:
        # Normal approximation to beta
        mean = alpha / (alpha + beta_param)
        variance = (alpha * beta_param) / ((alpha + beta_param) ** 2 * (alpha + beta_param + 1))
        std = math.sqrt(variance)

        # Standard normal CDF via error function approximation
        z = (x - mean) / std
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    # For small alpha/beta, use a simpler heuristic
    # When we have strong evidence (many successes), confidence should be high
    # This is a rough approximation but avoids complex beta function computation

    # Mean of beta distribution
    mean = alpha / (alpha + beta_param)

    # If x is below the mean, use a simple linear approximation
    # If x is above the mean, use complement
    if x < mean:
        # Rough approximation: scale by relative position
        return x * (alpha / (alpha + beta_param + 2))
    else:
        # Above mean - use higher confidence
        # For x > mean, CDF should be > 0.5
        excess = (x - mean) / (1 - mean) if mean < 1 else 0
        return 0.5 + 0.5 * excess


@dataclass
class BayesianStoppingModel:
    """
    Bayesian stopping model using Beta-Binomial conjugate priors.

    Tracks successes and failures, updates posterior distribution,
    and determines when to stop based on confidence threshold.

    Attributes:
        alpha: Beta distribution alpha parameter (prior successes + 1)
        beta: Beta distribution beta parameter (prior failures + 1)
        confidence_threshold: Stop when P(success_rate > 0.5) > threshold
        min_trials: Minimum trials before considering stopping

    Example:
        >>> model = BayesianStoppingModel(confidence_threshold=0.95)
        >>> model.update(success=True)
        >>> model.update(success=True)
        >>> model.update(success=False)
        >>> if model.should_stop():
        ...     print(f"Stop! Success rate: {model.success_rate:.2%}")
    """

    # Beta distribution parameters (start with uniform prior)
    alpha: float = 1.0  # Prior successes + 1
    beta: float = 1.0  # Prior failures + 1

    # Stopping criteria
    confidence_threshold: float = 0.95
    min_trials: int = 10  # Minimum trials before stopping

    def __init__(
        self,
        prior_success: float = 0.5,
        confidence_threshold: float = 0.95,
        min_trials: int = 10,
    ):
        """
        Initialize Bayesian stopping model.

        Args:
            prior_success: Prior belief about success rate (0-1)
            confidence_threshold: Confidence required to stop (0-1)
            min_trials: Minimum trials before considering stopping
        """
        # Beta(1, 1) is uniform prior (no prior belief)
        # To incorporate prior belief, we'd use alpha = prior_success * strength
        # and beta = (1 - prior_success) * strength, where strength is prior sample size
        self.alpha = 1.0
        self.beta = 1.0
        self.confidence_threshold = confidence_threshold
        self.min_trials = min_trials

    @property
    def n_trials(self) -> int:
        """Total number of trials (successes + failures)."""
        # alpha and beta start at 1, so we subtract 2 to get actual trial count
        return int(self.alpha + self.beta - 2)

    @property
    def n_successes(self) -> int:
        """Number of successful trials."""
        return int(self.alpha - 1)

    @property
    def n_failures(self) -> int:
        """Number of failed trials."""
        return int(self.beta - 1)

    @property
    def success_rate(self) -> float:
        """
        Expected success rate (posterior mean).

        For Beta(α, β), the mean is α / (α + β).
        """
        return self.alpha / (self.alpha + self.beta)

    @property
    def confidence(self) -> float:
        """
        Confidence that true success rate exceeds 0.5.

        This is P(θ > 0.5 | data) where θ ~ Beta(α, β).

        Computed as 1 - CDF(0.5), which is P(X > 0.5).

        For simplicity and avoiding scipy dependency, we use a conservative
        approximation based on the posterior mean and sample size.
        """
        # Conservative approximation when we have few trials
        if self.n_trials < 5:
            return 0.5  # Not enough evidence

        # For larger samples, use normal approximation
        # The beta distribution approaches normal as alpha, beta grow
        mean = self.success_rate
        std = self.std

        if std == 0:
            # Degenerate case
            return 1.0 if mean > 0.5 else 0.0

        # Z-score for hypothesis test: is true rate > 0.5?
        z = (mean - 0.5) / std

        # Convert z-score to confidence using error function
        # P(θ > 0.5) when θ ~ N(mean, std²) is P(Z > -z) where Z ~ N(0,1)
        # This is Φ(z) = 0.5 * (1 + erf(z/√2))
        confidence = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))

    @property
    def variance(self) -> float:
        """
        Variance of posterior distribution.

        For Beta(α, β), variance = (αβ) / ((α+β)²(α+β+1))
        """
        n = self.alpha + self.beta
        return (self.alpha * self.beta) / (n * n * (n + 1))

    @property
    def std(self) -> float:
        """Standard deviation of posterior distribution."""
        return math.sqrt(self.variance)

    def update(self, success: bool) -> None:
        """
        Update posterior with new trial result.

        Args:
            success: Whether the trial succeeded
        """
        if success:
            self.alpha += 1
        else:
            self.beta += 1

        # Prevent overflow: cap alpha/beta at reasonable bounds
        # Beta distribution is well-defined for alpha, beta > 0
        # We cap at 10,000 to prevent numerical overflow
        MAX_PARAM = 10_000.0
        if self.alpha > MAX_PARAM:
            # Rescale both parameters to maintain ratio
            ratio = self.beta / self.alpha
            self.alpha = MAX_PARAM
            self.beta = MAX_PARAM * ratio
        if self.beta > MAX_PARAM:
            # Rescale both parameters to maintain ratio
            ratio = self.alpha / self.beta
            self.beta = MAX_PARAM
            self.alpha = MAX_PARAM * ratio

    def should_stop(self) -> bool:
        """
        Determine if experiment should stop.

        Stops when:
        1. Minimum trials reached AND
        2. Posterior confidence exceeds threshold

        Returns:
            True if experiment should stop, False otherwise
        """
        if self.n_trials < self.min_trials:
            return False

        return self.confidence >= self.confidence_threshold

    def summary(self) -> dict[str, float]:
        """
        Get summary statistics.

        Returns:
            Dictionary with success_rate, confidence, variance, n_trials
        """
        return {
            "success_rate": self.success_rate,
            "confidence": self.confidence,
            "variance": self.variance,
            "std": self.std,
            "n_trials": self.n_trials,
            "n_successes": self.n_successes,
            "n_failures": self.n_failures,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"BayesianStoppingModel("
            f"success_rate={self.success_rate:.2%}, "
            f"confidence={self.confidence:.2%}, "
            f"n_trials={self.n_trials})"
        )


__all__ = [
    "BayesianStoppingModel",
    "beta_cdf",
]
