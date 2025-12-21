"""
ASHC Adaptive Evidence Framework

Bayesian adaptive sampling with optimal stopping rules.

Instead of fixed N runs, we use:
1. Beta-Binomial Bayesian updating for posterior beliefs
2. Sequential stopping rules (n_diff margin of victory)
3. Tiered confidence priors (trivially easy → uncertain → likely fails)
4. LLM pre-verification for cheap prior estimation

Mathematical Foundations:
- Wald's Sequential Probability Ratio Test (SPRT)
- Beta-Binomial conjugate prior updating
- BEACON-style Bayesian optimal stopping

References:
- https://en.wikipedia.org/wiki/Sequential_probability_ratio_test
- https://arxiv.org/abs/2510.15945 (BEACON: Bayesian Optimal Stopping for LLM)
- https://www.evanmiller.org/sequential-ab-testing.html
- https://www.bayesrulesbook.com/chapter-3 (Beta-Binomial Bayesian Model)

> "If something is 97% reliable, we don't need 100 runs.
>  We need n_diff runs where one outcome leads by n_diff margin."
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Iterator
from uuid import uuid4

from .verify import LintReport, TestReport, TypeReport, verify_code

# =============================================================================
# Mathematical Foundations
# =============================================================================


def beta_pdf(x: float, alpha: float, beta: float) -> float:
    """
    Beta distribution PDF (unnormalized, for comparison only).

    Beta(α, β) models probability of success rate p given:
    - α-1 successes observed
    - β-1 failures observed
    """
    if x <= 0 or x >= 1:
        return 0.0
    return (x ** (alpha - 1)) * ((1 - x) ** (beta - 1))


def beta_mean(alpha: float, beta: float) -> float:
    """Expected value of Beta(α, β) = α / (α + β)."""
    return alpha / (alpha + beta)


def beta_variance(alpha: float, beta: float) -> float:
    """Variance of Beta(α, β)."""
    ab = alpha + beta
    return (alpha * beta) / (ab * ab * (ab + 1))


def incomplete_beta_regularized(x: float, a: float, b: float) -> float:
    """
    Regularized incomplete beta function I_x(a, b).

    This gives P(X ≤ x) for X ~ Beta(a, b).
    Uses continued fraction approximation.
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0

    # Use scipy if available, otherwise approximate
    try:
        from scipy.special import betainc  # type: ignore[import-untyped]

        return float(betainc(a, b, x))
    except ImportError:
        # Simple approximation using normal approximation for large a, b
        if a + b > 10:
            mean = a / (a + b)
            var = (a * b) / ((a + b) ** 2 * (a + b + 1))
            std = math.sqrt(var)
            if std < 1e-10:
                return 1.0 if x >= mean else 0.0
            z = (x - mean) / std
            # Normal CDF approximation
            return 0.5 * (1 + math.erf(z / math.sqrt(2)))
        else:
            # Numerical integration for small a, b
            n_steps = 100
            dx = x / n_steps
            total = 0.0
            for i in range(n_steps):
                xi = (i + 0.5) * dx
                total += beta_pdf(xi, a, b) * dx
            # Normalize by full integral
            full = 0.0
            dx_full = 1.0 / n_steps
            for i in range(n_steps):
                xi = (i + 0.5) * dx_full
                full += beta_pdf(xi, a, b) * dx_full
            return total / full if full > 0 else 0.5


def prob_greater_than(alpha: float, beta: float, threshold: float) -> float:
    """
    P(p > threshold) for p ~ Beta(α, β).

    Used for stopping rules: "Are we confident p > 0.5?"
    """
    return 1.0 - incomplete_beta_regularized(threshold, alpha, beta)


def prob_less_than(alpha: float, beta: float, threshold: float) -> float:
    """P(p < threshold) for p ~ Beta(α, β)."""
    return incomplete_beta_regularized(threshold, alpha, beta)


# =============================================================================
# Belief Types
# =============================================================================


class ConfidenceTier(str, Enum):
    """Tiered confidence levels for adaptive sampling."""

    TRIVIALLY_EASY = "trivially_easy"  # 99%+ expected success
    LIKELY_WORKS = "likely_works"  # 80-99% expected success
    UNCERTAIN = "uncertain"  # 40-80% expected success
    LIKELY_FAILS = "likely_fails"  # <40% expected success
    UNKNOWN = "unknown"  # No prior information


@dataclass
class BetaPrior:
    """
    Beta distribution prior for success probability.

    Beta(α, β) where:
    - α = pseudo-count of successes + 1
    - β = pseudo-count of failures + 1

    Common priors:
    - Beta(1, 1) = Uniform (no information)
    - Beta(2, 1) = Slightly optimistic
    - Beta(10, 1) = Strong prior for ~90% success
    - Beta(100, 1) = Very strong prior for ~99% success
    """

    alpha: float = 1.0
    beta: float = 1.0

    @classmethod
    def uniform(cls) -> "BetaPrior":
        """Uniform prior: no prior information."""
        return cls(1.0, 1.0)

    @classmethod
    def from_confidence(cls, tier: ConfidenceTier) -> "BetaPrior":
        """Create prior from confidence tier."""
        if tier == ConfidenceTier.TRIVIALLY_EASY:
            return cls(100.0, 1.0)  # ~99% expected success
        elif tier == ConfidenceTier.LIKELY_WORKS:
            return cls(10.0, 2.0)  # ~83% expected success
        elif tier == ConfidenceTier.UNCERTAIN:
            return cls(2.0, 2.0)  # 50% expected success
        elif tier == ConfidenceTier.LIKELY_FAILS:
            return cls(2.0, 10.0)  # ~17% expected success
        else:
            return cls(1.0, 1.0)  # Uniform

    @classmethod
    def from_estimate(cls, success_rate: float, strength: float = 10.0) -> "BetaPrior":
        """
        Create prior from estimated success rate.

        Args:
            success_rate: Expected probability of success (0-1)
            strength: How many pseudo-observations (higher = stronger prior)
        """
        alpha = success_rate * strength + 1
        beta = (1 - success_rate) * strength + 1
        return cls(alpha, beta)

    @property
    def mean(self) -> float:
        """Expected success rate."""
        return beta_mean(self.alpha, self.beta)

    @property
    def variance(self) -> float:
        """Variance of success rate belief."""
        return beta_variance(self.alpha, self.beta)

    @property
    def confidence_interval_95(self) -> tuple[float, float]:
        """95% credible interval for success rate."""
        # Find 2.5th and 97.5th percentiles
        low = self._find_quantile(0.025)
        high = self._find_quantile(0.975)
        return (low, high)

    def _find_quantile(self, q: float) -> float:
        """Find the q-th quantile using bisection."""
        low, high = 0.0, 1.0
        for _ in range(50):  # 50 iterations gives ~15 decimal places
            mid = (low + high) / 2
            if incomplete_beta_regularized(mid, self.alpha, self.beta) < q:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    def update(self, successes: int, failures: int) -> "BetaPrior":
        """
        Bayesian update: prior + data → posterior.

        This is the conjugate update for Beta-Binomial.
        """
        return BetaPrior(
            alpha=self.alpha + successes,
            beta=self.beta + failures,
        )

    def prob_success_above(self, threshold: float) -> float:
        """P(success_rate > threshold)."""
        return prob_greater_than(self.alpha, self.beta, threshold)

    def prob_success_below(self, threshold: float) -> float:
        """P(success_rate < threshold)."""
        return prob_less_than(self.alpha, self.beta, threshold)


# =============================================================================
# Stopping Rules
# =============================================================================


class StoppingDecision(str, Enum):
    """Decision from stopping rule."""

    CONTINUE = "continue"  # Need more samples
    STOP_SUCCESS = "stop_success"  # Confident in success
    STOP_FAILURE = "stop_failure"  # Confident in failure
    STOP_UNCERTAIN = "stop_uncertain"  # Max samples reached, still uncertain


@dataclass(frozen=True)
class StoppingConfig:
    """
    Configuration for adaptive stopping.

    The n_diff technique: Stop when one outcome leads by n_diff margin.
    For binary pass/fail, this means |passes - fails| >= n_diff.

    Mathematical justification:
    - For true success rate p, expected samples ≈ n_diff / |2p - 1|
    - For p = 0.97 (97% reliable), expect ~4 samples for n_diff = 2
    - For p = 0.5 (pure noise), expected samples → ∞ (capped by max_samples)
    """

    n_diff: int = 2  # Margin of victory required
    max_samples: int = 20  # Hard cap on samples
    confidence_threshold: float = 0.95  # Bayesian confidence for early stop
    success_threshold: float = 0.5  # What counts as "success"

    @classmethod
    def for_tier(cls, tier: ConfidenceTier) -> "StoppingConfig":
        """Create stopping config appropriate for confidence tier."""
        if tier == ConfidenceTier.TRIVIALLY_EASY:
            return cls(n_diff=1, max_samples=3, confidence_threshold=0.99)
        elif tier == ConfidenceTier.LIKELY_WORKS:
            return cls(n_diff=2, max_samples=10, confidence_threshold=0.95)
        elif tier == ConfidenceTier.UNCERTAIN:
            return cls(n_diff=3, max_samples=20, confidence_threshold=0.90)
        elif tier == ConfidenceTier.LIKELY_FAILS:
            return cls(n_diff=2, max_samples=5, confidence_threshold=0.90)
        else:
            return cls(n_diff=2, max_samples=15, confidence_threshold=0.95)


@dataclass
class StoppingState:
    """
    Mutable state for tracking stopping decisions.

    Tracks:
    - Current posterior belief (Beta distribution)
    - Pass/fail counts
    - Whether we've reached a decision
    """

    prior: BetaPrior
    config: StoppingConfig
    successes: int = 0
    failures: int = 0
    decision: StoppingDecision = StoppingDecision.CONTINUE

    @property
    def total_samples(self) -> int:
        """Total samples observed."""
        return self.successes + self.failures

    @property
    def posterior(self) -> BetaPrior:
        """Current posterior belief."""
        return self.prior.update(self.successes, self.failures)

    @property
    def margin(self) -> int:
        """Current margin (|successes - failures|)."""
        return abs(self.successes - self.failures)

    @property
    def leading_outcome(self) -> str:
        """Which outcome is currently leading."""
        if self.successes > self.failures:
            return "success"
        elif self.failures > self.successes:
            return "failure"
        else:
            return "tie"

    def observe(self, success: bool) -> StoppingDecision:
        """
        Observe a new sample and update decision.

        Implements the n_diff technique:
        1. Update counts
        2. Check n_diff margin
        3. Check Bayesian confidence
        4. Check max samples
        """
        if success:
            self.successes += 1
        else:
            self.failures += 1

        # Check n_diff margin (the core technique)
        if self.margin >= self.config.n_diff:
            if self.successes > self.failures:
                self.decision = StoppingDecision.STOP_SUCCESS
            else:
                self.decision = StoppingDecision.STOP_FAILURE
            return self.decision

        # Check Bayesian confidence for early stopping
        posterior = self.posterior
        if (
            posterior.prob_success_above(self.config.success_threshold)
            >= self.config.confidence_threshold
        ):
            self.decision = StoppingDecision.STOP_SUCCESS
            return self.decision
        if (
            posterior.prob_success_below(self.config.success_threshold)
            >= self.config.confidence_threshold
        ):
            self.decision = StoppingDecision.STOP_FAILURE
            return self.decision

        # Check max samples
        if self.total_samples >= self.config.max_samples:
            # Decide based on current margin
            if self.successes > self.failures:
                self.decision = StoppingDecision.STOP_SUCCESS
            elif self.failures > self.successes:
                self.decision = StoppingDecision.STOP_FAILURE
            else:
                self.decision = StoppingDecision.STOP_UNCERTAIN
            return self.decision

        self.decision = StoppingDecision.CONTINUE
        return self.decision


# =============================================================================
# Adaptive Run
# =============================================================================


@dataclass(frozen=True)
class AdaptiveRunResult:
    """
    Result of a single run in adaptive sampling.
    """

    run_id: str
    success: bool
    test_report: TestReport
    type_report: TypeReport
    lint_report: LintReport
    duration_ms: float

    @classmethod
    def from_verification(
        cls,
        test_report: TestReport,
        type_report: TypeReport,
        lint_report: LintReport,
        duration_ms: float,
    ) -> "AdaptiveRunResult":
        """Create from verification results."""
        success = test_report.success and type_report.passed and lint_report.passed
        return cls(
            run_id=str(uuid4()),
            success=success,
            test_report=test_report,
            type_report=type_report,
            lint_report=lint_report,
            duration_ms=duration_ms,
        )


@dataclass(frozen=True)
class AdaptiveEvidence:
    """
    Evidence gathered through adaptive sampling.

    Unlike fixed-N Evidence, this includes:
    - The posterior belief
    - Why we stopped
    - Expected savings vs fixed-N
    """

    runs: tuple[AdaptiveRunResult, ...]
    prior: BetaPrior
    posterior: BetaPrior
    decision: StoppingDecision
    config: StoppingConfig
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def sample_count(self) -> int:
        """Number of samples taken."""
        return len(self.runs)

    @property
    def success_count(self) -> int:
        """Number of successful runs."""
        return sum(1 for r in self.runs if r.success)

    @property
    def success_rate(self) -> float:
        """Observed success rate."""
        if not self.runs:
            return 0.0
        return self.success_count / len(self.runs)

    @property
    def posterior_mean(self) -> float:
        """Expected success rate given evidence."""
        return self.posterior.mean

    @property
    def confidence_interval(self) -> tuple[float, float]:
        """95% credible interval for success rate."""
        return self.posterior.confidence_interval_95

    @property
    def is_success(self) -> bool:
        """Did we conclude success?"""
        return self.decision == StoppingDecision.STOP_SUCCESS

    @property
    def is_failure(self) -> bool:
        """Did we conclude failure?"""
        return self.decision == StoppingDecision.STOP_FAILURE

    @property
    def is_uncertain(self) -> bool:
        """Are we still uncertain?"""
        return self.decision == StoppingDecision.STOP_UNCERTAIN

    @property
    def savings_vs_fixed(self) -> float:
        """
        Estimated savings vs running fixed max_samples.

        savings = 1 - (samples_used / max_samples)
        """
        return 1.0 - (self.sample_count / self.config.max_samples)


# =============================================================================
# Adaptive Compiler
# =============================================================================


class AdaptiveCompiler:
    """
    Compile spec with adaptive evidence gathering.

    Uses Bayesian updating and n_diff stopping to minimize samples
    while maintaining statistical confidence.

    Key insight: Different tasks need different evidence:
    - Trivially easy: 1-3 samples, stop early
    - Likely works: n_diff=2, expect 3-5 samples
    - Uncertain: n_diff=3, expect 6-10 samples
    - Likely fails: fail fast, minimal samples

    The prior can come from:
    - Confidence tier (human/LLM classification)
    - Historical data (past runs of similar tasks)
    - LLM pre-verification (cheap estimate before expensive runs)
    """

    def __init__(
        self,
        generate_fn: Callable[[str], Awaitable[str]] | None = None,
        estimate_fn: Callable[[str], Awaitable[float]] | None = None,
    ):
        """
        Initialize adaptive compiler.

        Args:
            generate_fn: Function to generate implementation from spec
            estimate_fn: Function to estimate success probability (cheap pre-check)
        """
        self._generate_fn = generate_fn
        self._estimate_fn = estimate_fn

    async def compile(
        self,
        spec: str,
        test_code: str | None = None,
        tier: ConfidenceTier | None = None,
        prior: BetaPrior | None = None,
        config: StoppingConfig | None = None,
    ) -> AdaptiveEvidence:
        """
        Compile with adaptive evidence gathering.

        Args:
            spec: The specification to compile
            test_code: Optional test code for verification
            tier: Confidence tier (auto-detected if not provided)
            prior: Custom prior (derived from tier if not provided)
            config: Custom stopping config (derived from tier if not provided)

        Returns:
            AdaptiveEvidence with runs and posterior belief
        """
        import time

        # Determine confidence tier if not provided
        if tier is None and prior is None:
            tier = await self._estimate_tier(spec)

        # Set prior from tier if not provided
        if prior is None:
            prior = BetaPrior.from_confidence(tier or ConfidenceTier.UNKNOWN)

        # Set config from tier if not provided
        if config is None:
            config = StoppingConfig.for_tier(tier or ConfidenceTier.UNKNOWN)

        # Initialize stopping state
        state = StoppingState(prior=prior, config=config)
        runs: list[AdaptiveRunResult] = []

        # Adaptive sampling loop
        while state.decision == StoppingDecision.CONTINUE:
            start = time.monotonic()

            # Generate implementation
            if self._generate_fn:
                implementation = await self._generate_fn(spec)
            else:
                implementation = spec

            # Verify
            verification = await verify_code(
                code=implementation,
                test_code=test_code,
            )

            duration_ms = (time.monotonic() - start) * 1000

            # Create run result
            run = AdaptiveRunResult.from_verification(
                test_report=verification.test_report,
                type_report=verification.type_report,
                lint_report=verification.lint_report,
                duration_ms=duration_ms,
            )
            runs.append(run)

            # Update stopping state
            state.observe(run.success)

        return AdaptiveEvidence(
            runs=tuple(runs),
            prior=prior,
            posterior=state.posterior,
            decision=state.decision,
            config=config,
        )

    async def _estimate_tier(self, spec: str) -> ConfidenceTier:
        """
        Estimate confidence tier for a spec.

        Uses LLM pre-verification if available, otherwise returns UNKNOWN.
        """
        if self._estimate_fn:
            estimate = await self._estimate_fn(spec)
            if estimate >= 0.95:
                return ConfidenceTier.TRIVIALLY_EASY
            elif estimate >= 0.80:
                return ConfidenceTier.LIKELY_WORKS
            elif estimate >= 0.40:
                return ConfidenceTier.UNCERTAIN
            else:
                return ConfidenceTier.LIKELY_FAILS
        return ConfidenceTier.UNKNOWN


# =============================================================================
# Mathematical Proofs
# =============================================================================


def expected_samples_for_ndiff(true_p: float, n_diff: int) -> float:
    """
    Expected number of samples to reach n_diff margin.

    For a random walk with drift (2p - 1), the expected hitting time
    to reach distance n_diff from origin is approximately:

        E[T] ≈ n_diff / |2p - 1|

    This is derived from the gambler's ruin problem.

    Examples:
        p = 0.97 (97% reliable), n_diff = 2:
            E[T] ≈ 2 / (2*0.97 - 1) = 2 / 0.94 ≈ 2.1 samples

        p = 0.80 (80% reliable), n_diff = 2:
            E[T] ≈ 2 / (2*0.80 - 1) = 2 / 0.60 ≈ 3.3 samples

        p = 0.60 (60% reliable), n_diff = 2:
            E[T] ≈ 2 / (2*0.60 - 1) = 2 / 0.20 = 10 samples
    """
    drift = abs(2 * true_p - 1)
    if drift < 1e-10:
        return float("inf")  # Pure random walk, no convergence
    return n_diff / drift


def reliability_boost_from_voting(base_p: float, n_votes: int) -> float:
    """
    Reliability after majority voting with n_votes.

    If we run n_votes trials and take majority, the probability
    that majority is correct is:

        P(majority correct) = Σ_{k=⌈n/2⌉}^{n} C(n,k) * p^k * (1-p)^{n-k}

    This is the CDF of Binomial(n, p) from n/2 to n.

    Examples:
        p = 0.80, n = 3:  → 0.896 (89.6%)
        p = 0.80, n = 5:  → 0.942 (94.2%)
        p = 0.80, n = 7:  → 0.967 (96.7%)

    Key insight: Even unreliable functions become reliable with voting!
    """
    from math import comb

    majority_threshold = (n_votes + 1) // 2
    prob_correct = 0.0

    for k in range(majority_threshold, n_votes + 1):
        prob_correct += comb(n_votes, k) * (base_p**k) * ((1 - base_p) ** (n_votes - k))

    return prob_correct


# =============================================================================
# Convenience Functions
# =============================================================================


async def adaptive_compile(
    spec: str,
    test_code: str | None = None,
    tier: ConfidenceTier = ConfidenceTier.UNKNOWN,
) -> AdaptiveEvidence:
    """Convenience function for adaptive compilation."""
    compiler = AdaptiveCompiler()
    return await compiler.compile(spec, test_code, tier)


def print_evidence_summary(evidence: AdaptiveEvidence) -> str:
    """Pretty-print evidence summary."""
    ci = evidence.confidence_interval
    return f"""
Adaptive Evidence Summary
========================
Samples: {evidence.sample_count} (saved {evidence.savings_vs_fixed:.0%} vs fixed-N)
Decision: {evidence.decision.value}
Observed: {evidence.success_count}/{evidence.sample_count} passed ({evidence.success_rate:.0%})

Bayesian Posterior:
  Mean: {evidence.posterior_mean:.1%}
  95% CI: [{ci[0]:.1%}, {ci[1]:.1%}]

Prior: Beta({evidence.prior.alpha:.1f}, {evidence.prior.beta:.1f})
Posterior: Beta({evidence.posterior.alpha:.1f}, {evidence.posterior.beta:.1f})
"""
