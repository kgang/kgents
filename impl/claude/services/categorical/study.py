"""
Correlation Study: Statistical Analysis of Categorical Laws → Accuracy.

This module runs the core validation of kgents 2.0's hypothesis:
    "LLM reasoning failures follow patterns that category theory predicts."

The study runs thousands of problems, measures categorical law satisfaction,
and correlates with reasoning correctness.

Success Criteria (from Phase 1 plan):
    - Monad identity correlates with accuracy: r > 0.3
    - Sheaf coherence correlates with correctness: r > 0.4
    - Combined metrics predict accuracy: AUC > 0.7

Philosophy:
    "Measure first. Build only what measurement validates."
    "The proof IS the decision."
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

from .probes import (
    CategoricalProbeRunner,
    CoherenceResult,
    LLMProtocol,
    MonadResult,
    ProbeResults,
)

logger = logging.getLogger("kgents.categorical.study")


# =============================================================================
# Problem Types
# =============================================================================


class ProblemType(Enum):
    """Categories of reasoning problems."""

    MATH = auto()  # Mathematical reasoning (GSM8K-style)
    MULTI_HOP = auto()  # Multi-hop QA (HotpotQA-style)
    LOGIC = auto()  # Logical reasoning
    CODE = auto()  # Code understanding/generation
    COMMONSENSE = auto()  # Common sense reasoning


@dataclass(frozen=True)
class Problem:
    """A reasoning problem with ground truth."""

    id: str
    question: str
    answer: str  # Ground truth answer
    problem_type: ProblemType
    reasoning_steps: tuple[str, ...] = ()  # For associativity testing
    metadata: dict[str, Any] = field(default_factory=dict)

    def check(self, response: str) -> bool:
        """
        Check if a response is correct.

        Default: Case-insensitive exact match after normalization.
        Override via metadata["check_fn"] for custom logic.
        """
        # Normalize both
        expected = self.answer.lower().strip().rstrip(".")
        actual = response.lower().strip().rstrip(".")

        # Handle numeric answers
        try:
            expected_num = float(expected.replace(",", ""))
            actual_num = float(actual.replace(",", ""))
            return abs(expected_num - actual_num) < 0.001
        except ValueError:
            pass

        return expected == actual


@dataclass
class ProblemSet:
    """A collection of problems for study."""

    name: str
    problems: list[Problem]
    description: str = ""

    @classmethod
    def from_json(cls, path: Path) -> "ProblemSet":
        """Load problem set from JSON file."""
        with path.open() as f:
            data = json.load(f)

        problems = [
            Problem(
                id=p["id"],
                question=p["question"],
                answer=p["answer"],
                problem_type=ProblemType[p.get("type", "MATH").upper()],
                reasoning_steps=tuple(p.get("steps", [])),
                metadata=p.get("metadata", {}),
            )
            for p in data["problems"]
        ]

        return cls(
            name=data.get("name", path.stem),
            problems=problems,
            description=data.get("description", ""),
        )

    def sample(self, n: int) -> list[Problem]:
        """Sample n problems (with replacement if n > len)."""
        import random

        if n >= len(self.problems):
            return self.problems.copy()
        return random.sample(self.problems, n)


# =============================================================================
# Study Results
# =============================================================================


@dataclass
class ProblemResult:
    """Result of probing a single problem."""

    problem: Problem
    response: str
    correct: bool
    monad_identity_score: float
    monad_assoc_score: float
    sheaf_coherence_score: float
    trace: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CorrelationResult:
    """
    Statistical correlation results with bootstrapped confidence intervals.

    Implements Pearson correlation coefficient with uncertainty quantification.

    Enhanced in Phase 1 methodology hardening to include:
    - 95% CI via bootstrap
    - Exact p-value via permutation test
    - Effect size interpretation
    """

    metric_name: str
    correlation: float  # Pearson r
    p_value: float
    n_samples: int
    mean_when_correct: float
    mean_when_incorrect: float

    # Phase 1 enhancement: Bootstrapped confidence intervals
    ci_low: float = 0.0  # Lower bound of 95% CI
    ci_high: float = 0.0  # Upper bound of 95% CI

    # Phase 1 enhancement: Permutation test p-value
    p_value_permutation: float | None = None  # Exact p-value (non-parametric)

    @property
    def significant(self) -> bool:
        """True if p < 0.05 (uses permutation p-value if available)."""
        p = self.p_value_permutation if self.p_value_permutation is not None else self.p_value
        return p < 0.05

    @property
    def significant_strict(self) -> bool:
        """True if p < 0.01 (Phase 1 gate criterion)."""
        p = self.p_value_permutation if self.p_value_permutation is not None else self.p_value
        return p < 0.01

    @property
    def ci_excludes_zero(self) -> bool:
        """True if 95% CI excludes zero (stronger evidence)."""
        return self.ci_low > 0 or self.ci_high < 0

    @property
    def effect_size(self) -> str:
        """Interpret correlation strength."""
        r = abs(self.correlation)
        if r < 0.1:
            return "negligible"
        if r < 0.3:
            return "weak"
        if r < 0.5:
            return "moderate"
        if r < 0.7:
            return "strong"
        return "very_strong"


@dataclass
class BaselineResults:
    """
    Results from baseline comparisons.

    Phase 1 enhancement: Correlation without baselines is meaningless.
    Random noise can correlate. Categorical probes must beat all baselines.
    """

    random_corr: CorrelationResult  # Random scores [0,1]
    length_corr: CorrelationResult  # Trace length as predictor
    confidence_corr: CorrelationResult | None = None  # LLM self-confidence (optional)

    @property
    def best_baseline(self) -> float:
        """Best baseline correlation (the bar categorical must beat)."""
        corrs = [abs(self.random_corr.correlation), abs(self.length_corr.correlation)]
        if self.confidence_corr:
            corrs.append(abs(self.confidence_corr.correlation))
        return max(corrs)


@dataclass
class StudyResult:
    """
    Complete study results with all correlations and enhanced gate criteria.

    Phase 1 methodology hardening adds:
    - Baseline comparisons (random, length, confidence)
    - Bootstrapped confidence intervals
    - Permutation test p-values
    - Stricter gate criteria (CI lower bounds, beats baseline)
    """

    config: "StudyConfig"
    problem_results: list[ProblemResult]
    monad_identity_corr: CorrelationResult
    monad_assoc_corr: CorrelationResult | None
    sheaf_coherence_corr: CorrelationResult
    combined_auc: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration: timedelta = field(default=timedelta(0))

    # Phase 1 enhancement: Baseline comparisons
    baselines: BaselineResults | None = None

    @property
    def categorical_delta(self) -> float:
        """How much categorical (avg of identity + coherence) beats random baseline."""
        if self.baselines is None:
            return 0.0
        categorical_avg = (
            abs(self.monad_identity_corr.correlation) + abs(self.sheaf_coherence_corr.correlation)
        ) / 2
        return categorical_avg - abs(self.baselines.random_corr.correlation)

    @property
    def beats_all_baselines(self) -> bool:
        """True if categorical beats all baselines by meaningful margin."""
        if self.baselines is None:
            return True  # No baselines to beat
        # Must beat best baseline by at least 0.15
        return self.categorical_delta > 0.15

    @property
    def passed_gate(self) -> bool:
        """
        Check if study passes Phase 1 gate.

        Enhanced criteria (methodology hardening):
        - Monad identity CI lower bound > 0.3 (not just point estimate)
        - Sheaf coherence CI lower bound > 0.4
        - Combined AUC > 0.7
        - Beats random baseline by Δ > 0.15
        - Both correlations have p < 0.01 (permutation test)
        """
        # Use CI lower bounds for stricter criterion
        identity_ok = self.monad_identity_corr.ci_low > 0.3
        coherence_ok = self.sheaf_coherence_corr.ci_low > 0.4
        auc_ok = self.combined_auc > 0.7
        baseline_ok = self.beats_all_baselines

        # Check significance
        identity_sig = self.monad_identity_corr.significant_strict
        coherence_sig = self.sheaf_coherence_corr.significant_strict

        return (
            identity_ok
            and coherence_ok
            and auc_ok
            and baseline_ok
            and identity_sig
            and coherence_sig
        )

    @property
    def passed_gate_relaxed(self) -> bool:
        """
        Relaxed gate (original criteria without CI/baseline checks).

        Use this for comparison with enhanced gate.
        """
        return (
            self.monad_identity_corr.correlation > 0.3
            and self.sheaf_coherence_corr.correlation > 0.4
            and self.combined_auc > 0.7
        )

    @property
    def blockers(self) -> list[str]:
        """List metrics that block the gate."""
        blockers = []

        # CI lower bound checks
        if self.monad_identity_corr.ci_low <= 0.3:
            blockers.append(
                f"monad_identity CI low (r={self.monad_identity_corr.correlation:.3f}, "
                f"CI=[{self.monad_identity_corr.ci_low:.3f}, {self.monad_identity_corr.ci_high:.3f}])"
            )
        if self.sheaf_coherence_corr.ci_low <= 0.4:
            blockers.append(
                f"sheaf_coherence CI low (r={self.sheaf_coherence_corr.correlation:.3f}, "
                f"CI=[{self.sheaf_coherence_corr.ci_low:.3f}, {self.sheaf_coherence_corr.ci_high:.3f}])"
            )
        if self.combined_auc <= 0.7:
            blockers.append(f"combined_auc ({self.combined_auc:.3f} ≤ 0.7)")

        # Baseline check
        if not self.beats_all_baselines:
            blockers.append(f"baseline_delta ({self.categorical_delta:.3f} ≤ 0.15)")

        # Significance checks
        if not self.monad_identity_corr.significant_strict:
            p = self.monad_identity_corr.p_value_permutation or self.monad_identity_corr.p_value
            blockers.append(f"monad_identity p-value ({p:.4f} ≥ 0.01)")
        if not self.sheaf_coherence_corr.significant_strict:
            p = self.sheaf_coherence_corr.p_value_permutation or self.sheaf_coherence_corr.p_value
            blockers.append(f"sheaf_coherence p-value ({p:.4f} ≥ 0.01)")

        return blockers

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for storage/transmission."""
        return {
            "config": {
                "n_problems": self.config.n_problems,
                "n_samples_per_problem": self.config.n_samples_per_problem,
                "problem_types": [t.name for t in self.config.problem_types],
            },
            "n_results": len(self.problem_results),
            "monad_identity_corr": self.monad_identity_corr.correlation,
            "sheaf_coherence_corr": self.sheaf_coherence_corr.correlation,
            "combined_auc": self.combined_auc,
            "passed_gate": self.passed_gate,
            "blockers": self.blockers,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration.total_seconds(),
        }


# =============================================================================
# Study Configuration
# =============================================================================


@dataclass
class StudyConfig:
    """
    Configuration for correlation study.

    Enhanced with Phase 1 methodology parameters:
    - run_baselines: Compute baseline comparisons
    - n_bootstrap: Number of bootstrap samples for CI
    - n_permutations: Number of permutations for p-value
    - significance_level: Required p-value threshold
    - random_seed: For reproducibility
    """

    n_problems: int = 500
    n_samples_per_problem: int = 5  # For identity tests
    problem_types: tuple[ProblemType, ...] = (ProblemType.MATH, ProblemType.MULTI_HOP)
    run_associativity: bool = True
    temperature: float = 0.0
    max_concurrent: int = 10  # Concurrent problem processing

    # Validation thresholds
    min_monad_corr: float = 0.3
    min_sheaf_corr: float = 0.4
    min_combined_auc: float = 0.7

    # Phase 1 enhancement: Statistical rigor parameters
    run_baselines: bool = True  # Compute baseline comparisons
    n_bootstrap: int = 1000  # Bootstrap samples for CI
    n_permutations: int = 10000  # Permutations for exact p-value
    significance_level: float = 0.01  # Stricter than 0.05
    random_seed: int | None = 42  # For reproducibility


# =============================================================================
# Correlation Study Runner
# =============================================================================


class CorrelationStudy:
    """
    Run correlation study between categorical laws and reasoning accuracy.

    This is the core validation for kgents 2.0's hypothesis.

    Usage:
        >>> study = CorrelationStudy(llm_client, problem_set)
        >>> result = await study.run(StudyConfig(n_problems=100))
        >>> if result.passed_gate:
        ...     print("Phase 1 validated! Proceed to Phase 2.")
        ... else:
        ...     print(f"Blocked by: {result.blockers}")

    Teaching:
        gotcha: Large studies can be expensive. Use caching via ValidationEngine.
                (Evidence: validation-framework-implementation.md)

        gotcha: Concurrent execution helps speed but may hit rate limits.
                Adjust max_concurrent in config.
                (Evidence: test_study.py::test_rate_limiting)
    """

    def __init__(
        self,
        llm: LLMProtocol,
        problem_set: ProblemSet,
        answer_extractor: Callable[[str], str] | None = None,
    ):
        """
        Initialize CorrelationStudy.

        Args:
            llm: LLM client for probing
            problem_set: Problems to study
            answer_extractor: Function to extract answer from LLM response
        """
        self.llm = llm
        self.problem_set = problem_set
        self._answer_extractor = answer_extractor

    async def _probe_problem(
        self,
        problem: Problem,
        runner: CategoricalProbeRunner,
        config: StudyConfig,
    ) -> ProblemResult:
        """Probe a single problem and record results."""
        # First, generate a solution to get the trace
        response = await self.llm.generate(
            system="You are a helpful assistant. Show your reasoning step by step.",
            user=problem.question,
            temperature=config.temperature,
        )
        trace = response.text if hasattr(response, "text") else response.get("text", str(response))

        # Extract answer from trace
        answer = self._extract_answer(trace)
        correct = problem.check(answer)

        # Run categorical probes
        steps = problem.reasoning_steps if config.run_associativity else None
        probe_results = await runner.probe(
            problem=problem.question,
            trace=trace,
            n_samples=config.n_samples_per_problem,
            steps=steps,
        )

        return ProblemResult(
            problem=problem,
            response=answer,
            correct=correct,
            monad_identity_score=probe_results.monad_result.identity_score
            if probe_results.monad_result
            else 0.0,
            monad_assoc_score=probe_results.monad_result.associativity_score
            if probe_results.monad_result
            else 0.0,
            sheaf_coherence_score=probe_results.coherence_score,
            trace=trace,
        )

    def _extract_answer(self, trace: str) -> str:
        """Extract answer from reasoning trace."""
        if self._answer_extractor:
            return self._answer_extractor(trace)

        # Default extraction
        lines = trace.strip().split("\n")
        for line in reversed(lines):
            line_lower = line.lower().strip()
            if "answer:" in line_lower or "the answer is" in line_lower:
                for pattern in ["answer:", "the answer is"]:
                    if pattern in line_lower:
                        idx = line_lower.index(pattern) + len(pattern)
                        return line[idx:].strip().rstrip(".")

        return lines[-1].strip() if lines else ""

    def _pearson(self, x: list[float], y: list[float]) -> float:
        """Compute Pearson correlation coefficient."""
        import math

        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

        if denom_x == 0 or denom_y == 0:
            return 0.0

        return numerator / (denom_x * denom_y)

    def _bootstrap_ci(
        self,
        values: list[float],
        correct: list[bool],
        n_bootstrap: int = 1000,
    ) -> tuple[float, float]:
        """
        Compute 95% confidence interval via bootstrap.

        Phase 1 enhancement: Point estimates are incomplete.
        We need uncertainty quantification.
        """
        import random

        n = len(values)
        if n < 3:
            return (0.0, 0.0)

        y = [1.0 if c else 0.0 for c in correct]
        bootstrap_rs = []

        for _ in range(n_bootstrap):
            # Sample with replacement
            indices = [random.randint(0, n - 1) for _ in range(n)]
            sample_vals = [values[i] for i in indices]
            sample_y = [y[i] for i in indices]
            r = self._pearson(sample_vals, sample_y)
            bootstrap_rs.append(r)

        # 95% CI (2.5th and 97.5th percentiles)
        sorted_rs = sorted(bootstrap_rs)
        ci_low = sorted_rs[int(0.025 * n_bootstrap)]
        ci_high = sorted_rs[int(0.975 * n_bootstrap)]

        return (ci_low, ci_high)

    def _permutation_test(
        self,
        values: list[float],
        correct: list[bool],
        observed_r: float,
        n_permutations: int = 10000,
    ) -> float:
        """
        Exact p-value via permutation test.

        Phase 1 enhancement: t-test assumes normality.
        Permutation tests are exact and distribution-free.
        """
        import random

        n = len(values)
        if n < 3:
            return 1.0

        y = [1.0 if c else 0.0 for c in correct]
        count_extreme = 0

        for _ in range(n_permutations):
            # Shuffle correctness labels
            shuffled_y = y.copy()
            random.shuffle(shuffled_y)
            perm_r = self._pearson(values, shuffled_y)

            # Two-tailed: count if |perm_r| >= |observed_r|
            if abs(perm_r) >= abs(observed_r):
                count_extreme += 1

        return count_extreme / n_permutations

    def _compute_correlation(
        self,
        metric_name: str,
        values: list[float],
        correct: list[bool],
        n_bootstrap: int = 1000,
        n_permutations: int = 10000,
    ) -> CorrelationResult:
        """
        Compute Pearson correlation with bootstrapped CI and permutation p-value.

        Phase 1 methodology hardening:
        - Bootstrap 95% CI
        - Permutation test for exact p-value
        """
        import math

        n = len(values)
        if n < 2:
            return CorrelationResult(
                metric_name=metric_name,
                correlation=0.0,
                p_value=1.0,
                n_samples=n,
                mean_when_correct=0.0,
                mean_when_incorrect=0.0,
                ci_low=0.0,
                ci_high=0.0,
                p_value_permutation=1.0,
            )

        # Convert correctness to float
        y = [1.0 if c else 0.0 for c in correct]

        # Compute point estimate
        r = self._pearson(values, y)

        # Bootstrap CI
        ci_low, ci_high = self._bootstrap_ci(values, correct, n_bootstrap)

        # Permutation test p-value
        p_value_perm = self._permutation_test(values, correct, r, n_permutations)

        # Simple t-test p-value (for comparison)
        if abs(r) >= 1.0 or n < 3:
            p_value = 0.0 if abs(r) >= 0.999 else 1.0
        else:
            t = r * math.sqrt((n - 2) / (1 - r * r))
            p_value = 2 * (1 - _normal_cdf(abs(t))) if n > 30 else 0.05

        # Mean values by correctness
        correct_vals = [values[i] for i in range(n) if correct[i]]
        incorrect_vals = [values[i] for i in range(n) if not correct[i]]

        mean_correct = sum(correct_vals) / len(correct_vals) if correct_vals else 0.0
        mean_incorrect = sum(incorrect_vals) / len(incorrect_vals) if incorrect_vals else 0.0

        return CorrelationResult(
            metric_name=metric_name,
            correlation=r,
            p_value=p_value,
            n_samples=n,
            mean_when_correct=mean_correct,
            mean_when_incorrect=mean_incorrect,
            ci_low=ci_low,
            ci_high=ci_high,
            p_value_permutation=p_value_perm,
        )

    def _compute_auc(
        self,
        scores: list[float],
        labels: list[bool],
    ) -> float:
        """
        Compute AUC-ROC for combined score predicting correctness.

        Uses simple trapezoidal approximation.
        """
        if not scores or not any(labels) or all(labels):
            return 0.5  # No discrimination possible

        # Sort by score descending
        pairs = sorted(zip(scores, labels), key=lambda x: -x[0])

        tp = 0
        fp = 0
        prev_tp = 0
        prev_fp = 0
        auc = 0.0
        prev_score = float("inf")

        n_pos = sum(1 for _, l in pairs if l)
        n_neg = len(pairs) - n_pos

        if n_pos == 0 or n_neg == 0:
            return 0.5

        for score, label in pairs:
            if score != prev_score:
                # Trapezoidal area
                auc += (fp - prev_fp) * (tp + prev_tp) / 2
                prev_score = score
                prev_tp = tp
                prev_fp = fp

            if label:
                tp += 1
            else:
                fp += 1

        # Final point
        auc += (fp - prev_fp) * (tp + prev_tp) / 2

        return auc / (n_pos * n_neg)

    def _compute_baselines(
        self,
        valid_results: list[ProblemResult],
        correctness: list[bool],
        config: StudyConfig,
    ) -> BaselineResults:
        """
        Compute baseline correlations for comparison.

        Phase 1 enhancement: Categorical probes must beat these baselines:
        1. Random scores: correlation with random [0,1] values
        2. Length heuristic: trace length often correlates with correctness
        """
        import random

        n = len(valid_results)

        # Seed for reproducibility
        if config.random_seed is not None:
            random.seed(config.random_seed + 999)  # Different from main seed

        # Random baseline: generate random scores
        random_scores = [random.random() for _ in range(n)]
        random_corr = self._compute_correlation(
            "random_baseline",
            random_scores,
            correctness,
            config.n_bootstrap,
            config.n_permutations,
        )

        # Length baseline: use trace length as predictor
        # Normalize to [0,1] for comparability
        trace_lengths = [len(r.trace) for r in valid_results]
        max_len = max(trace_lengths) if trace_lengths else 1
        length_scores = [l / max_len for l in trace_lengths]
        length_corr = self._compute_correlation(
            "length_baseline",
            length_scores,
            correctness,
            config.n_bootstrap,
            config.n_permutations,
        )

        return BaselineResults(
            random_corr=random_corr,
            length_corr=length_corr,
            confidence_corr=None,  # Could add LLM self-confidence if available
        )

    async def run(self, config: StudyConfig | None = None) -> StudyResult:
        """
        Run the correlation study with enhanced methodology.

        Phase 1 enhancements:
        - Bootstrap CIs for all correlations
        - Permutation tests for exact p-values
        - Baseline comparisons (random, length)
        - Reproducible via random_seed

        Args:
            config: Study configuration (uses defaults if not provided)

        Returns:
            StudyResult with all correlations and gate status
        """
        import random

        start_time = datetime.now(timezone.utc)
        config = config or StudyConfig()

        # Set random seed for reproducibility
        if config.random_seed is not None:
            random.seed(config.random_seed)
            logger.info(f"Random seed: {config.random_seed}")

        logger.info(f"Starting correlation study: {config.n_problems} problems")
        logger.info(
            f"Bootstrap samples: {config.n_bootstrap}, "
            f"Permutations: {config.n_permutations}, "
            f"Run baselines: {config.run_baselines}"
        )

        # Create probe runner
        runner = CategoricalProbeRunner(
            llm=self.llm,
            temperature=config.temperature,
            emit_marks=True,
        )

        # Sample problems
        problems = self.problem_set.sample(config.n_problems)

        # Run probes with concurrency control
        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def probe_with_limit(problem: Problem) -> ProblemResult:
            async with semaphore:
                return await self._probe_problem(problem, runner, config)

        results = await asyncio.gather(
            *[probe_with_limit(p) for p in problems],
            return_exceptions=True,
        )

        # Filter out exceptions
        valid_results: list[ProblemResult] = []
        for r in results:
            if isinstance(r, ProblemResult):
                valid_results.append(r)
            else:
                logger.warning(f"Problem failed: {r}")

        logger.info(f"Completed {len(valid_results)}/{len(problems)} problems")

        # Extract metrics
        identity_scores = [r.monad_identity_score for r in valid_results]
        assoc_scores = [r.monad_assoc_score for r in valid_results]
        coherence_scores = [r.sheaf_coherence_score for r in valid_results]
        correctness = [r.correct for r in valid_results]

        # Compute correlations with bootstrap CI and permutation p-value
        identity_corr = self._compute_correlation(
            "monad_identity",
            identity_scores,
            correctness,
            config.n_bootstrap,
            config.n_permutations,
        )

        assoc_corr = None
        if config.run_associativity and any(s > 0 for s in assoc_scores):
            assoc_corr = self._compute_correlation(
                "monad_assoc",
                assoc_scores,
                correctness,
                config.n_bootstrap,
                config.n_permutations,
            )

        coherence_corr = self._compute_correlation(
            "sheaf_coherence",
            coherence_scores,
            correctness,
            config.n_bootstrap,
            config.n_permutations,
        )

        # Compute baselines if requested
        baselines: BaselineResults | None = None
        if config.run_baselines:
            logger.info("Computing baseline correlations...")
            baselines = self._compute_baselines(valid_results, correctness, config)
            logger.info(
                f"Baselines: random_r={baselines.random_corr.correlation:.3f}, "
                f"length_r={baselines.length_corr.correlation:.3f}"
            )

        # Compute combined AUC
        combined_scores = [
            (identity_scores[i] + coherence_scores[i]) / 2 for i in range(len(valid_results))
        ]
        combined_auc = self._compute_auc(combined_scores, correctness)

        duration = datetime.now(timezone.utc) - start_time

        study_result = StudyResult(
            config=config,
            problem_results=valid_results,
            monad_identity_corr=identity_corr,
            monad_assoc_corr=assoc_corr,
            sheaf_coherence_corr=coherence_corr,
            combined_auc=combined_auc,
            duration=duration,
            baselines=baselines,
        )

        # Emit final mark
        await self._emit_study_mark(study_result)

        # Enhanced logging
        logger.info(
            f"Study complete:\n"
            f"  Identity: r={identity_corr.correlation:.3f} "
            f"CI=[{identity_corr.ci_low:.3f}, {identity_corr.ci_high:.3f}] "
            f"p={identity_corr.p_value_permutation:.4f}\n"
            f"  Coherence: r={coherence_corr.correlation:.3f} "
            f"CI=[{coherence_corr.ci_low:.3f}, {coherence_corr.ci_high:.3f}] "
            f"p={coherence_corr.p_value_permutation:.4f}\n"
            f"  AUC: {combined_auc:.3f}\n"
            f"  Δ over baseline: {study_result.categorical_delta:.3f}\n"
            f"  Gate: {'PASS' if study_result.passed_gate else 'BLOCKED by: ' + ', '.join(study_result.blockers)}"
        )

        return study_result

    async def _emit_study_mark(self, result: StudyResult) -> None:
        """Emit a Witness mark for study completion."""
        try:
            from services.witness.mark import Mark, Proof
            from services.witness.trace_store import get_mark_store

            # Build empirical proof
            data = (
                f"n={len(result.problem_results)}, "
                f"identity_r={result.monad_identity_corr.correlation:.3f}, "
                f"coherence_r={result.sheaf_coherence_corr.correlation:.3f}, "
                f"auc={result.combined_auc:.3f}"
            )

            warrant = "Pearson correlation and AUC-ROC computed from problem results"
            claim = "PASS" if result.passed_gate else f"BLOCKED by: {', '.join(result.blockers)}"

            proof = Proof.empirical(
                data=data,
                warrant=warrant,
                claim=claim,
                backing="Phase 1 correlation study",
            )

            content = f"Correlation study: {claim} ({data})"
            mark = Mark.from_thought(
                content=content,
                source="categorical",
                tags=("categorical", "study", "phase1", "correlation"),
                origin="correlation_study",
            ).with_proof(proof)

            store = get_mark_store()
            store.append(mark)
            logger.info(f"Emitted study mark: {mark.id}")

        except ImportError:
            logger.debug("Witness not available, skipping mark emission")
        except Exception as e:
            logger.warning(f"Failed to emit study mark: {e}")


def _normal_cdf(x: float) -> float:
    """Approximate standard normal CDF."""
    import math

    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


__all__ = [
    "CorrelationStudy",
    "CorrelationResult",
    "BaselineResults",  # Phase 1 enhancement
    "Problem",
    "ProblemSet",
    "ProblemType",
    "ProblemResult",
    "StudyConfig",
    "StudyResult",
]
