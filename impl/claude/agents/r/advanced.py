"""
R-gents Phase 4: Advanced Features.

This module implements sophisticated optimization capabilities:
1. Automatic teleprompter selection based on task analysis
2. Model drift detection + re-optimization triggers
3. Cross-model transfer analysis
4. Fine-tuning integration (BootstrapFinetune backend)

Category Theory:
  - AutoSelector: A functor from Task-Analysis → Strategy
  - DriftDetector: A predicate on Agent-Performance × Time → Bool
  - TransferAnalyzer: A functor from Model-A × Trace → Model-B prediction
  - BootstrapFinetune: An endofunctor with weight modification

See spec/r-gents/README.md for full specification.
"""

from __future__ import annotations

import hashlib
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from .types import (
    Example,
    OptimizationTrace,
    Signature,
    TeleprompterStrategy,
)

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Part 1: Automatic Teleprompter Selection
# =============================================================================


class TaskComplexity(Enum):
    """Classification of task complexity levels."""

    TRIVIAL = "trivial"  # Simple pattern matching
    SIMPLE = "simple"  # Basic reasoning
    MODERATE = "moderate"  # Multi-step reasoning
    COMPLEX = "complex"  # Deep analysis required
    EXPERT = "expert"  # Domain expertise needed


class DatasetCharacteristics(Enum):
    """Characteristics of training data."""

    TINY = "tiny"  # < 10 examples
    SMALL = "small"  # 10-50 examples
    MEDIUM = "medium"  # 50-200 examples
    LARGE = "large"  # 200-1000 examples
    MASSIVE = "massive"  # > 1000 examples


@dataclass(frozen=True)
class TaskAnalysis:
    """
    Analysis of a task for automatic strategy selection.

    The AutoSelector uses this analysis to determine the optimal
    teleprompter strategy without manual configuration.
    """

    # Complexity assessment
    complexity: TaskComplexity

    # Dataset characteristics
    dataset_size: int
    dataset_characteristic: DatasetCharacteristics

    # Content analysis
    avg_input_length: float  # Average characters in input
    avg_output_length: float  # Average characters in output
    output_diversity: float  # 0.0-1.0, how varied the outputs are

    # Structure analysis
    requires_structured_output: bool  # JSON, XML, etc.
    requires_reasoning_chain: bool  # Chain-of-thought needed
    requires_domain_knowledge: bool  # Specialized knowledge

    # Economic factors
    budget_usd: float
    target_accuracy: float = 0.85  # Desired performance threshold


@dataclass(frozen=True)
class StrategyRecommendation:
    """
    Recommendation from the automatic selector.

    Includes the chosen strategy, confidence, and reasoning.
    """

    strategy: TeleprompterStrategy
    confidence: float  # 0.0-1.0
    reasoning: str

    # Alternative strategies with their scores
    alternatives: tuple[tuple[TeleprompterStrategy, float], ...] = ()

    # Estimated cost and time
    estimated_cost_usd: float = 0.0
    estimated_duration_minutes: float = 0.0

    # Warnings
    warnings: tuple[str, ...] = ()


class TaskAnalyzer:
    """
    Analyzes tasks to determine optimal optimization strategy.

    Category Theory:
      This is a functor from the Task category to the Analysis category:
      Analyze: Task → TaskAnalysis
    """

    def __init__(
        self,
        complexity_keywords: dict[TaskComplexity, set[str]] | None = None,
    ):
        """Initialize with optional custom complexity keywords."""
        self.complexity_keywords = complexity_keywords or {
            TaskComplexity.TRIVIAL: {
                "extract",
                "copy",
                "format",
                "convert",
            },
            TaskComplexity.SIMPLE: {
                "classify",
                "label",
                "identify",
                "detect",
            },
            TaskComplexity.MODERATE: {
                "summarize",
                "translate",
                "rewrite",
                "explain",
            },
            TaskComplexity.COMPLEX: {
                "analyze",
                "reason",
                "infer",
                "synthesize",
            },
            TaskComplexity.EXPERT: {
                "diagnose",
                "optimize",
                "design",
                "evaluate",
            },
        }

    def analyze(
        self,
        signature: Signature,
        examples: list[Example],
        budget_usd: float = 10.0,
        target_accuracy: float = 0.85,
    ) -> TaskAnalysis:
        """
        Analyze a task to determine its characteristics.

        Args:
            signature: The task specification
            examples: Training examples
            budget_usd: Available budget
            target_accuracy: Desired accuracy threshold

        Returns:
            TaskAnalysis with full characterization
        """
        # Analyze complexity from instructions
        complexity = self._estimate_complexity(signature.instructions)

        # Dataset characteristics
        dataset_size = len(examples)
        dataset_char = self._classify_dataset_size(dataset_size)

        # Content analysis
        avg_input_len = self._avg_content_length(examples, "inputs")
        avg_output_len = self._avg_content_length(examples, "outputs")
        output_diversity = self._compute_output_diversity(examples)

        # Structure analysis
        requires_structured = self._check_structured_output(signature, examples)
        requires_reasoning = self._check_reasoning_chain(signature)
        requires_domain = self._check_domain_knowledge(signature)

        return TaskAnalysis(
            complexity=complexity,
            dataset_size=dataset_size,
            dataset_characteristic=dataset_char,
            avg_input_length=avg_input_len,
            avg_output_length=avg_output_len,
            output_diversity=output_diversity,
            requires_structured_output=requires_structured,
            requires_reasoning_chain=requires_reasoning,
            requires_domain_knowledge=requires_domain,
            budget_usd=budget_usd,
            target_accuracy=target_accuracy,
        )

    def _estimate_complexity(self, instructions: str) -> TaskComplexity:
        """Estimate task complexity from instructions."""
        instructions_lower = instructions.lower()

        # Check from most to least complex
        for complexity in reversed(list(TaskComplexity)):
            keywords = self.complexity_keywords.get(complexity, set())
            if any(kw in instructions_lower for kw in keywords):
                return complexity

        return TaskComplexity.MODERATE  # Default

    def _classify_dataset_size(self, size: int) -> DatasetCharacteristics:
        """Classify dataset by size."""
        if size < 10:
            return DatasetCharacteristics.TINY
        elif size < 50:
            return DatasetCharacteristics.SMALL
        elif size < 200:
            return DatasetCharacteristics.MEDIUM
        elif size < 1000:
            return DatasetCharacteristics.LARGE
        else:
            return DatasetCharacteristics.MASSIVE

    def _avg_content_length(self, examples: list[Example], field: str) -> float:
        """Compute average content length."""
        if not examples:
            return 0.0

        lengths = []
        for ex in examples:
            content = getattr(ex, field, {})
            total_len = sum(len(str(v)) for v in content.values())
            lengths.append(total_len)

        return statistics.mean(lengths) if lengths else 0.0

    def _compute_output_diversity(self, examples: list[Example]) -> float:
        """Compute diversity of outputs (0.0-1.0)."""
        if len(examples) < 2:
            return 0.0

        # Hash outputs and count unique
        output_hashes = set()
        for ex in examples:
            output_str = str(ex.outputs)
            output_hash = hashlib.md5(output_str.encode()).hexdigest()
            output_hashes.add(output_hash)

        return len(output_hashes) / len(examples)

    def _check_structured_output(
        self, signature: Signature, examples: list[Example]
    ) -> bool:
        """Check if task requires structured output."""
        # Check instructions for structural keywords
        structural_keywords = {"json", "xml", "yaml", "list", "dict", "array"}
        instructions_lower = signature.instructions.lower()
        if any(kw in instructions_lower for kw in structural_keywords):
            return True

        # Check example outputs for structure
        for ex in examples:
            for v in ex.outputs.values():
                if isinstance(v, (dict, list)):
                    return True

        return False

    def _check_reasoning_chain(self, signature: Signature) -> bool:
        """Check if task requires chain-of-thought reasoning."""
        reasoning_keywords = {
            "step by step",
            "reasoning",
            "explain",
            "think through",
            "chain of thought",
            "logical",
        }
        instructions_lower = signature.instructions.lower()
        return any(kw in instructions_lower for kw in reasoning_keywords)

    def _check_domain_knowledge(self, signature: Signature) -> bool:
        """Check if task requires domain expertise."""
        domain_keywords = {
            "medical",
            "legal",
            "financial",
            "technical",
            "scientific",
            "expert",
            "specialized",
        }
        instructions_lower = signature.instructions.lower()
        return any(kw in instructions_lower for kw in domain_keywords)


class AutoTeleprompterSelector:
    """
    Automatically selects the optimal teleprompter strategy.

    Uses task analysis to make intelligent strategy choices without
    requiring manual configuration from the user.

    Category Theory:
      This is a functor: Select: TaskAnalysis → StrategyRecommendation
    """

    def __init__(
        self,
        analyzer: TaskAnalyzer | None = None,
        cost_weight: float = 0.3,
        quality_weight: float = 0.5,
        speed_weight: float = 0.2,
    ):
        """
        Initialize selector with optional custom analyzer and weights.

        Args:
            analyzer: TaskAnalyzer instance
            cost_weight: Weight for cost optimization (0-1)
            quality_weight: Weight for quality optimization (0-1)
            speed_weight: Weight for speed optimization (0-1)
        """
        self.analyzer = analyzer or TaskAnalyzer()
        self.cost_weight = cost_weight
        self.quality_weight = quality_weight
        self.speed_weight = speed_weight

        # Strategy characteristics (cost, quality, speed - all 0-1 normalized)
        self._strategy_profiles = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: {
                "cost": 0.95,  # Very cheap
                "quality": 0.5,  # Moderate quality
                "speed": 0.95,  # Very fast
                "min_examples": 5,
                "max_complexity": TaskComplexity.SIMPLE,
            },
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: {
                "cost": 0.85,
                "quality": 0.6,
                "speed": 0.85,
                "min_examples": 10,
                "max_complexity": TaskComplexity.MODERATE,
            },
            TeleprompterStrategy.OPRO: {
                "cost": 0.7,
                "quality": 0.7,
                "speed": 0.7,
                "min_examples": 10,
                "max_complexity": TaskComplexity.COMPLEX,
            },
            TeleprompterStrategy.TEXTGRAD: {
                "cost": 0.4,
                "quality": 0.85,
                "speed": 0.4,
                "min_examples": 20,
                "max_complexity": TaskComplexity.EXPERT,
            },
            TeleprompterStrategy.MIPRO_V2: {
                "cost": 0.3,
                "quality": 0.9,
                "speed": 0.3,
                "min_examples": 30,
                "max_complexity": TaskComplexity.EXPERT,
            },
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: {
                "cost": 0.1,  # Most expensive
                "quality": 0.95,  # Highest quality
                "speed": 0.1,  # Slowest
                "min_examples": 100,
                "max_complexity": TaskComplexity.EXPERT,
            },
        }

    def select(
        self,
        signature: Signature,
        examples: list[Example],
        budget_usd: float = 10.0,
        target_accuracy: float = 0.85,
    ) -> StrategyRecommendation:
        """
        Select the optimal teleprompter strategy.

        Args:
            signature: Task specification
            examples: Training examples
            budget_usd: Available budget
            target_accuracy: Desired accuracy

        Returns:
            StrategyRecommendation with optimal strategy and reasoning
        """
        # Analyze the task
        analysis = self.analyzer.analyze(
            signature, examples, budget_usd, target_accuracy
        )

        # Score each strategy
        scores: dict[TeleprompterStrategy, float] = {}
        for strategy, profile in self._strategy_profiles.items():
            score = self._score_strategy(analysis, strategy, profile)
            scores[strategy] = score

        # Sort by score
        sorted_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        best_strategy, best_score = sorted_strategies[0]
        alternatives = tuple(sorted_strategies[1:4])  # Top 3 alternatives

        # Generate reasoning
        reasoning = self._generate_reasoning(analysis, best_strategy)
        warnings = self._generate_warnings(analysis, best_strategy)

        # Estimate cost and duration
        est_cost = self._estimate_cost(best_strategy, len(examples))
        est_duration = self._estimate_duration(best_strategy, len(examples))

        return StrategyRecommendation(
            strategy=best_strategy,
            confidence=best_score,
            reasoning=reasoning,
            alternatives=alternatives,
            estimated_cost_usd=est_cost,
            estimated_duration_minutes=est_duration,
            warnings=warnings,
        )

    def _score_strategy(
        self,
        analysis: TaskAnalysis,
        strategy: TeleprompterStrategy,
        profile: dict,
    ) -> float:
        """Score a strategy for the given task analysis."""
        # Check hard constraints
        if analysis.dataset_size < profile["min_examples"]:
            return 0.0  # Not enough data

        complexity_order = list(TaskComplexity)
        analysis_idx = complexity_order.index(analysis.complexity)
        max_idx = complexity_order.index(profile["max_complexity"])
        if analysis_idx > max_idx:
            return 0.1  # Can handle but not optimal

        # Weighted score
        cost_score = profile["cost"]
        quality_score = profile["quality"]
        speed_score = profile["speed"]

        # Adjust quality score based on task needs
        if analysis.requires_reasoning_chain and strategy in (
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM,
        ):
            quality_score *= 0.7  # Penalize simple methods for reasoning tasks

        if analysis.requires_domain_knowledge and strategy in (
            TeleprompterStrategy.BOOTSTRAP_FINETUNE,
            TeleprompterStrategy.MIPRO_V2,
        ):
            quality_score *= 1.1  # Bonus for sophisticated methods

        # Budget constraint
        est_cost = self._estimate_cost(strategy, analysis.dataset_size)
        if est_cost > analysis.budget_usd:
            cost_score *= 0.5  # Penalize over-budget strategies

        # Compute weighted score
        total_score = (
            self.cost_weight * cost_score
            + self.quality_weight * quality_score
            + self.speed_weight * speed_score
        )

        return min(1.0, total_score)

    def _generate_reasoning(
        self, analysis: TaskAnalysis, strategy: TeleprompterStrategy
    ) -> str:
        """Generate human-readable reasoning for the selection."""
        reasons = []

        # Dataset size reasoning
        if analysis.dataset_characteristic == DatasetCharacteristics.TINY:
            reasons.append(f"Small dataset ({analysis.dataset_size} examples)")
        elif analysis.dataset_characteristic == DatasetCharacteristics.LARGE:
            reasons.append(
                f"Large dataset ({analysis.dataset_size} examples) enables sophisticated optimization"
            )

        # Complexity reasoning
        reasons.append(f"Task complexity: {analysis.complexity.value}")

        # Strategy-specific reasoning
        strategy_reasons = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: "Fast and cheap for simple tasks",
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: "Good balance of cost and quality",
            TeleprompterStrategy.OPRO: "Efficient exploration via meta-prompting",
            TeleprompterStrategy.TEXTGRAD: "High precision via iterative refinement",
            TeleprompterStrategy.MIPRO_V2: "Best quality via Bayesian optimization",
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: "Production-grade via fine-tuning",
        }
        reasons.append(strategy_reasons.get(strategy, ""))

        return "; ".join(filter(None, reasons))

    def _generate_warnings(
        self, analysis: TaskAnalysis, strategy: TeleprompterStrategy
    ) -> tuple[str, ...]:
        """Generate warnings about potential issues."""
        warnings = []

        # Data warnings
        if analysis.dataset_size < 10:
            warnings.append(
                "Warning: Very small dataset may limit optimization quality"
            )

        if analysis.output_diversity < 0.3:
            warnings.append(
                "Warning: Low output diversity may indicate data quality issues"
            )

        # Strategy-specific warnings
        if strategy == TeleprompterStrategy.BOOTSTRAP_FINETUNE:
            warnings.append("Note: Fine-tuning requires significant compute resources")

        if (
            strategy == TeleprompterStrategy.TEXTGRAD
            and analysis.avg_output_length > 500
        ):
            warnings.append("Note: TextGrad may be slow for long outputs")

        return tuple(warnings)

    def _estimate_cost(
        self, strategy: TeleprompterStrategy, num_examples: int
    ) -> float:
        """Estimate optimization cost in USD."""
        base_costs = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: 0.50,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: 1.00,
            TeleprompterStrategy.OPRO: 2.00,
            TeleprompterStrategy.TEXTGRAD: 5.00,
            TeleprompterStrategy.MIPRO_V2: 8.00,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: 50.00,
        }
        per_example_costs = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: 0.01,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: 0.02,
            TeleprompterStrategy.OPRO: 0.02,
            TeleprompterStrategy.TEXTGRAD: 0.10,
            TeleprompterStrategy.MIPRO_V2: 0.05,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: 0.01,
        }

        base = base_costs.get(strategy, 5.0)
        per_ex = per_example_costs.get(strategy, 0.05)
        return base + per_ex * num_examples

    def _estimate_duration(
        self, strategy: TeleprompterStrategy, num_examples: int
    ) -> float:
        """Estimate optimization duration in minutes."""
        durations = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: 1.0,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: 3.0,
            TeleprompterStrategy.OPRO: 5.0,
            TeleprompterStrategy.TEXTGRAD: 15.0,
            TeleprompterStrategy.MIPRO_V2: 20.0,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: 60.0,
        }
        base = durations.get(strategy, 10.0)
        # Scale with dataset size
        return base * (1 + num_examples / 100)


# =============================================================================
# Part 2: Model Drift Detection + Re-optimization Triggers
# =============================================================================


@dataclass(frozen=True)
class PerformanceSample:
    """A single performance measurement sample."""

    timestamp: datetime
    score: float
    num_evaluations: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DriftReport:
    """Report from drift detection analysis."""

    is_drifting: bool
    drift_severity: float  # 0.0-1.0
    drift_type: str  # "gradual", "sudden", "seasonal", "none"
    confidence: float  # 0.0-1.0

    # Statistics
    current_score: float
    baseline_score: float
    score_delta: float
    trend_direction: str  # "improving", "stable", "degrading"

    # Recommendation
    should_reoptimize: bool
    recommended_action: str

    # Details
    samples_analyzed: int
    detection_window_days: int


class DriftDetectionMethod(Enum):
    """Methods for detecting model drift."""

    STATISTICAL = "statistical"  # Z-score based
    SLIDING_WINDOW = "sliding_window"  # Moving average comparison
    CUSUM = "cusum"  # Cumulative sum control chart
    PAGE_HINKLEY = "page_hinkley"  # Sequential analysis


class ModelDriftDetector:
    """
    Detects performance degradation and triggers re-optimization.

    Monitors agent performance over time and identifies when
    re-optimization is needed due to model drift, data distribution
    changes, or gradual degradation.

    Category Theory:
      This is a predicate on the product category Agent × Time:
      Drift: Agent × Time → Bool
    """

    def __init__(
        self,
        baseline_score: float = 0.8,
        drift_threshold: float = 0.1,  # 10% degradation threshold
        min_samples: int = 10,
        detection_window_days: int = 30,
        method: DriftDetectionMethod = DriftDetectionMethod.SLIDING_WINDOW,
    ):
        """
        Initialize drift detector.

        Args:
            baseline_score: Expected performance baseline
            drift_threshold: Relative degradation threshold
            min_samples: Minimum samples before detection
            detection_window_days: Analysis window
            method: Detection algorithm
        """
        self.baseline_score = baseline_score
        self.drift_threshold = drift_threshold
        self.min_samples = min_samples
        self.detection_window_days = detection_window_days
        self.method = method

        # Performance history
        self._samples: list[PerformanceSample] = []

    def record_sample(
        self,
        score: float,
        num_evaluations: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a new performance sample."""
        self._samples.append(
            PerformanceSample(
                timestamp=datetime.now(),
                score=score,
                num_evaluations=num_evaluations,
                metadata=metadata or {},
            )
        )

    def detect_drift(self) -> DriftReport:
        """
        Analyze performance history for drift.

        Returns:
            DriftReport with analysis and recommendations
        """
        # Filter to detection window
        cutoff = datetime.now() - timedelta(days=self.detection_window_days)
        recent_samples = [s for s in self._samples if s.timestamp >= cutoff]

        if len(recent_samples) < self.min_samples:
            return DriftReport(
                is_drifting=False,
                drift_severity=0.0,
                drift_type="none",
                confidence=0.0,
                current_score=self._current_score(recent_samples),
                baseline_score=self.baseline_score,
                score_delta=0.0,
                trend_direction="stable",
                should_reoptimize=False,
                recommended_action="Collect more samples for reliable detection",
                samples_analyzed=len(recent_samples),
                detection_window_days=self.detection_window_days,
            )

        # Run detection based on method
        if self.method == DriftDetectionMethod.STATISTICAL:
            return self._detect_statistical(recent_samples)
        elif self.method == DriftDetectionMethod.SLIDING_WINDOW:
            return self._detect_sliding_window(recent_samples)
        elif self.method == DriftDetectionMethod.CUSUM:
            return self._detect_cusum(recent_samples)
        else:  # PAGE_HINKLEY
            return self._detect_page_hinkley(recent_samples)

    def _current_score(self, samples: list[PerformanceSample]) -> float:
        """Get current (most recent) score."""
        if not samples:
            return self.baseline_score
        return samples[-1].score

    def _detect_statistical(self, samples: list[PerformanceSample]) -> DriftReport:
        """Statistical z-score based drift detection."""
        scores = [s.score for s in samples]

        # Compute statistics
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Z-score relative to baseline
        if std_score > 0:
            z_score = (mean_score - self.baseline_score) / std_score
        else:
            z_score = 0.0

        # Determine drift
        score_delta = mean_score - self.baseline_score
        relative_delta = abs(score_delta) / self.baseline_score

        is_drifting = relative_delta > self.drift_threshold
        drift_severity = min(1.0, relative_delta / self.drift_threshold)

        # Determine trend
        if len(scores) >= 5:
            early = statistics.mean(scores[: len(scores) // 2])
            late = statistics.mean(scores[len(scores) // 2 :])
            if late > early + 0.02:
                trend = "improving"
            elif late < early - 0.02:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Determine drift type
        if is_drifting:
            if trend == "degrading":
                drift_type = "gradual"
            elif std_score > 0.1:
                drift_type = "sudden"
            else:
                drift_type = "gradual"
        else:
            drift_type = "none"

        # Confidence based on sample size and consistency
        confidence = min(1.0, len(samples) / 50) * (1 - std_score)

        # Recommendation
        should_reoptimize = is_drifting and trend == "degrading"
        if should_reoptimize:
            action = "Re-optimization recommended due to performance degradation"
        elif is_drifting:
            action = "Monitor closely; drift detected but not degrading"
        else:
            action = "No action needed; performance stable"

        return DriftReport(
            is_drifting=is_drifting,
            drift_severity=drift_severity,
            drift_type=drift_type,
            confidence=confidence,
            current_score=scores[-1] if scores else self.baseline_score,
            baseline_score=self.baseline_score,
            score_delta=score_delta,
            trend_direction=trend,
            should_reoptimize=should_reoptimize,
            recommended_action=action,
            samples_analyzed=len(samples),
            detection_window_days=self.detection_window_days,
        )

    def _detect_sliding_window(self, samples: list[PerformanceSample]) -> DriftReport:
        """Sliding window moving average drift detection."""
        scores = [s.score for s in samples]

        # Compute recent vs historical windows
        window_size = max(3, len(scores) // 4)
        recent_window = scores[-window_size:]
        historical_window = scores[: len(scores) - window_size]

        recent_avg = statistics.mean(recent_window)
        historical_avg = (
            statistics.mean(historical_window)
            if historical_window
            else self.baseline_score
        )

        # Compare windows
        score_delta = recent_avg - historical_avg
        relative_delta = (
            abs(score_delta) / historical_avg if historical_avg > 0 else 0.0
        )

        is_drifting = relative_delta > self.drift_threshold
        drift_severity = min(1.0, relative_delta / self.drift_threshold)

        # Trend
        if score_delta > 0.02:
            trend = "improving"
        elif score_delta < -0.02:
            trend = "degrading"
        else:
            trend = "stable"

        drift_type = "gradual" if is_drifting else "none"

        # Confidence
        confidence = min(1.0, len(samples) / 30)

        # Recommendation
        should_reoptimize = is_drifting and trend == "degrading"
        if should_reoptimize:
            action = f"Re-optimization recommended; recent avg {recent_avg:.2f} vs historical {historical_avg:.2f}"
        else:
            action = "Performance within acceptable range"

        return DriftReport(
            is_drifting=is_drifting,
            drift_severity=drift_severity,
            drift_type=drift_type,
            confidence=confidence,
            current_score=recent_avg,
            baseline_score=self.baseline_score,
            score_delta=score_delta,
            trend_direction=trend,
            should_reoptimize=should_reoptimize,
            recommended_action=action,
            samples_analyzed=len(samples),
            detection_window_days=self.detection_window_days,
        )

    def _detect_cusum(self, samples: list[PerformanceSample]) -> DriftReport:
        """CUSUM (Cumulative Sum) control chart drift detection."""
        scores = [s.score for s in samples]

        # Target is baseline
        target = self.baseline_score

        # Compute CUSUM
        cusum_pos = 0.0
        cusum_neg = 0.0
        k = self.drift_threshold / 2  # Slack parameter

        for score in scores:
            cusum_pos = max(0, cusum_pos + (score - target) - k)
            cusum_neg = min(0, cusum_neg + (score - target) + k)

        # Decision threshold
        h = 4 * self.drift_threshold  # Control limit

        is_drifting = cusum_pos > h or abs(cusum_neg) > h
        drift_severity = max(cusum_pos, abs(cusum_neg)) / h if h > 0 else 0.0
        drift_severity = min(1.0, drift_severity)

        # Trend from CUSUM direction
        if cusum_pos > abs(cusum_neg):
            trend = "improving"
        elif abs(cusum_neg) > cusum_pos:
            trend = "degrading"
        else:
            trend = "stable"

        drift_type = "sudden" if drift_severity > 0.8 else "gradual"
        if not is_drifting:
            drift_type = "none"

        current_score = statistics.mean(scores[-3:]) if scores else target
        score_delta = current_score - target

        confidence = min(1.0, len(samples) / 20)

        should_reoptimize = is_drifting and trend == "degrading"
        action = (
            "CUSUM detects drift; re-optimization recommended"
            if should_reoptimize
            else "CUSUM within control limits"
        )

        return DriftReport(
            is_drifting=is_drifting,
            drift_severity=drift_severity,
            drift_type=drift_type,
            confidence=confidence,
            current_score=current_score,
            baseline_score=self.baseline_score,
            score_delta=score_delta,
            trend_direction=trend,
            should_reoptimize=should_reoptimize,
            recommended_action=action,
            samples_analyzed=len(samples),
            detection_window_days=self.detection_window_days,
        )

    def _detect_page_hinkley(self, samples: list[PerformanceSample]) -> DriftReport:
        """Page-Hinkley sequential drift detection."""
        scores = [s.score for s in samples]

        if len(scores) < 2:
            return self._detect_statistical(samples)

        # Page-Hinkley test
        delta = self.drift_threshold / 2
        alpha = 1 - self.drift_threshold  # Forgetting factor

        m_t = 0.0  # Cumulative sum
        M_t = 0.0  # Minimum cumulative sum
        ph_values = []

        mean_so_far = scores[0]
        for i, score in enumerate(scores):
            # Update running mean
            mean_so_far = alpha * mean_so_far + (1 - alpha) * score

            # Update Page-Hinkley
            m_t += score - mean_so_far - delta
            M_t = min(M_t, m_t)
            ph_values.append(m_t - M_t)

        # Threshold
        threshold = 5 * self.drift_threshold
        max_ph = max(ph_values) if ph_values else 0.0

        is_drifting = max_ph > threshold
        drift_severity = min(1.0, max_ph / threshold) if threshold > 0 else 0.0

        # Trend from recent values
        recent_mean = statistics.mean(scores[-3:])
        early_mean = statistics.mean(scores[:3])
        if recent_mean > early_mean + 0.02:
            trend = "improving"
        elif recent_mean < early_mean - 0.02:
            trend = "degrading"
        else:
            trend = "stable"

        drift_type = "sudden" if is_drifting and drift_severity > 0.7 else "gradual"
        if not is_drifting:
            drift_type = "none"

        score_delta = recent_mean - self.baseline_score
        confidence = min(1.0, len(samples) / 25)

        should_reoptimize = is_drifting and trend == "degrading"
        action = (
            "Page-Hinkley detects change point; investigate and re-optimize"
            if should_reoptimize
            else "No significant drift detected"
        )

        return DriftReport(
            is_drifting=is_drifting,
            drift_severity=drift_severity,
            drift_type=drift_type,
            confidence=confidence,
            current_score=recent_mean,
            baseline_score=self.baseline_score,
            score_delta=score_delta,
            trend_direction=trend,
            should_reoptimize=should_reoptimize,
            recommended_action=action,
            samples_analyzed=len(samples),
            detection_window_days=self.detection_window_days,
        )

    def clear_history(self) -> None:
        """Clear all performance history."""
        self._samples.clear()

    def update_baseline(self, new_baseline: float) -> None:
        """Update the baseline score (after re-optimization)."""
        self.baseline_score = new_baseline


@dataclass
class ReoptimizationTrigger:
    """
    Configuration for automatic re-optimization triggers.

    Defines conditions under which re-optimization is automatically
    initiated based on drift detection or scheduled intervals.
    """

    # Drift-based triggers
    drift_threshold: float = 0.1  # 10% degradation
    min_confidence: float = 0.7  # Minimum detection confidence

    # Scheduled triggers
    max_age_days: int = 30  # Re-optimize if older than this
    min_samples_between: int = 100  # Minimum samples between re-opts

    # Budget constraints
    max_reoptimizations_per_month: int = 3
    budget_per_reoptimization_usd: float = 10.0

    # State tracking
    last_optimization: datetime | None = None
    optimization_count_this_month: int = 0

    def should_trigger(self, drift_report: DriftReport) -> tuple[bool, str]:
        """
        Determine if re-optimization should be triggered.

        Returns:
            Tuple of (should_trigger, reason)
        """
        # Budget check
        if self.optimization_count_this_month >= self.max_reoptimizations_per_month:
            return False, "Monthly re-optimization budget exhausted"

        # Age check
        if self.last_optimization:
            age = datetime.now() - self.last_optimization
            if age > timedelta(days=self.max_age_days):
                return (
                    True,
                    f"Optimization is {age.days} days old (max {self.max_age_days})",
                )

        # Drift check
        if drift_report.should_reoptimize:
            if drift_report.confidence >= self.min_confidence:
                return (
                    True,
                    f"Drift detected with {drift_report.confidence:.0%} confidence",
                )
            else:
                return (
                    False,
                    f"Drift detected but confidence too low ({drift_report.confidence:.0%})",
                )

        return False, "No trigger conditions met"

    def record_optimization(self) -> None:
        """Record that optimization was performed."""
        self.last_optimization = datetime.now()
        self.optimization_count_this_month += 1

    def reset_monthly_count(self) -> None:
        """Reset the monthly optimization count."""
        self.optimization_count_this_month = 0


# =============================================================================
# Part 3: Cross-Model Transfer Analysis
# =============================================================================


@dataclass(frozen=True)
class ModelProfile:
    """Profile of a model for transfer analysis."""

    model_id: str
    provider: str  # "openai", "anthropic", "google", etc.
    model_family: str  # "gpt-4", "claude-3", "gemini-1.5", etc.
    context_window: int
    estimated_cost_per_1k_tokens: float

    # Capability flags
    supports_json_mode: bool = True
    supports_function_calling: bool = True
    supports_vision: bool = False

    # Performance characteristics
    latency_ms_estimate: float = 500.0
    quality_tier: str = "high"  # "low", "medium", "high", "frontier"


@dataclass(frozen=True)
class TransferPrediction:
    """Prediction of how optimization will transfer to a new model."""

    source_model: ModelProfile
    target_model: ModelProfile

    # Performance predictions
    predicted_score: float  # Expected score on target
    confidence: float  # Confidence in prediction

    # Transfer quality
    transfer_efficiency: float  # 0.0-1.0, how well prompts transfer
    adjustment_needed: str  # "none", "minor", "moderate", "major"

    # Recommendations
    should_transfer: bool
    should_reoptimize: bool
    estimated_reoptimization_cost_usd: float

    # Reasoning
    reasoning: str


class CrossModelTransferAnalyzer:
    """
    Analyzes how prompt optimizations transfer across models.

    Different LLMs respond differently to prompts. This analyzer
    predicts whether optimizations will transfer well and recommends
    re-optimization when needed.

    Category Theory:
      This is a functor from (Model-A × OptimizationTrace) to
      a prediction about Model-B performance:
      Transfer: Model × Trace → Prediction
    """

    def __init__(self):
        """Initialize transfer analyzer."""
        # Transfer efficiency matrix (source_family -> target_family -> efficiency)
        self._transfer_matrix = {
            # GPT family transfers
            ("gpt-4", "gpt-4"): 0.95,
            ("gpt-4", "gpt-3.5"): 0.75,
            ("gpt-4", "claude-3"): 0.70,
            ("gpt-4", "gemini-1.5"): 0.65,
            # Claude family transfers
            ("claude-3", "claude-3"): 0.95,
            ("claude-3", "gpt-4"): 0.70,
            ("claude-3", "gpt-3.5"): 0.60,
            ("claude-3", "gemini-1.5"): 0.65,
            # Gemini family transfers
            ("gemini-1.5", "gemini-1.5"): 0.95,
            ("gemini-1.5", "gpt-4"): 0.65,
            ("gemini-1.5", "claude-3"): 0.65,
            # GPT-3.5 family
            ("gpt-3.5", "gpt-4"): 0.80,
            ("gpt-3.5", "gpt-3.5"): 0.90,
            ("gpt-3.5", "claude-3"): 0.60,
        }

        # Quality tier mapping
        self._quality_tiers = {
            "frontier": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }

    def analyze_transfer(
        self,
        source_model: ModelProfile,
        target_model: ModelProfile,
        optimization_trace: OptimizationTrace,
    ) -> TransferPrediction:
        """
        Analyze how well an optimization will transfer to a new model.

        Args:
            source_model: Model the optimization was created for
            target_model: Model we want to transfer to
            optimization_trace: The optimization to transfer

        Returns:
            TransferPrediction with analysis and recommendations
        """
        # Get transfer efficiency
        key = (source_model.model_family, target_model.model_family)
        transfer_efficiency = self._transfer_matrix.get(key, 0.5)  # Default 50%

        # Adjust for quality tier difference
        source_tier = self._quality_tiers.get(source_model.quality_tier, 2)
        target_tier = self._quality_tiers.get(target_model.quality_tier, 2)
        tier_diff = target_tier - source_tier

        if tier_diff > 0:
            # Transferring to better model - might work better
            transfer_efficiency = min(1.0, transfer_efficiency * 1.1)
        elif tier_diff < 0:
            # Transferring to weaker model - likely worse
            transfer_efficiency *= 0.85

        # Predict score
        source_score = optimization_trace.final_score or 0.5
        predicted_score = source_score * transfer_efficiency

        # Determine adjustment needed
        if transfer_efficiency > 0.85:
            adjustment = "none"
        elif transfer_efficiency > 0.70:
            adjustment = "minor"
        elif transfer_efficiency > 0.50:
            adjustment = "moderate"
        else:
            adjustment = "major"

        # Confidence based on transfer efficiency and trace quality
        confidence = transfer_efficiency * 0.8  # Base confidence
        if optimization_trace.converged:
            confidence = min(1.0, confidence * 1.1)
        if optimization_trace.total_examples > 50:
            confidence = min(1.0, confidence * 1.05)

        # Recommendations
        should_transfer = transfer_efficiency > 0.5
        should_reoptimize = transfer_efficiency < 0.75

        # Estimate re-optimization cost
        if should_reoptimize:
            base_cost = 5.0
            # Cheaper if transfer is decent
            cost_factor = 1.0 - (transfer_efficiency * 0.5)
            est_cost = base_cost * cost_factor
        else:
            est_cost = 0.0

        # Generate reasoning
        reasoning_parts = [
            f"Transfer from {source_model.model_family} to {target_model.model_family}",
            f"Expected transfer efficiency: {transfer_efficiency:.0%}",
        ]
        if tier_diff != 0:
            direction = "upgrade" if tier_diff > 0 else "downgrade"
            reasoning_parts.append(f"Quality tier {direction}")
        if should_reoptimize:
            reasoning_parts.append("Re-optimization recommended for best results")

        return TransferPrediction(
            source_model=source_model,
            target_model=target_model,
            predicted_score=predicted_score,
            confidence=confidence,
            transfer_efficiency=transfer_efficiency,
            adjustment_needed=adjustment,
            should_transfer=should_transfer,
            should_reoptimize=should_reoptimize,
            estimated_reoptimization_cost_usd=est_cost,
            reasoning="; ".join(reasoning_parts),
        )

    def recommend_target_models(
        self,
        source_model: ModelProfile,
        optimization_trace: OptimizationTrace,
        available_models: list[ModelProfile],
        min_transfer_efficiency: float = 0.7,
    ) -> list[tuple[ModelProfile, TransferPrediction]]:
        """
        Recommend models that optimizations will transfer well to.

        Args:
            source_model: Current model
            optimization_trace: Existing optimization
            available_models: Models to consider
            min_transfer_efficiency: Minimum acceptable efficiency

        Returns:
            List of (model, prediction) sorted by predicted score
        """
        predictions = []

        for target in available_models:
            if target.model_id == source_model.model_id:
                continue  # Skip same model

            prediction = self.analyze_transfer(source_model, target, optimization_trace)

            if prediction.transfer_efficiency >= min_transfer_efficiency:
                predictions.append((target, prediction))

        # Sort by predicted score (descending)
        predictions.sort(key=lambda x: x[1].predicted_score, reverse=True)

        return predictions


# =============================================================================
# Part 4: Fine-Tuning Integration (BootstrapFinetune)
# =============================================================================


class FinetuneStatus(Enum):
    """Status of a fine-tuning job."""

    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class FinetuneJob:
    """Represents a fine-tuning job."""

    job_id: str
    model_id: str
    status: FinetuneStatus

    # Configuration
    base_model: str
    num_epochs: int
    learning_rate: float
    batch_size: int

    # Progress
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    current_epoch: int = 0
    training_loss: float | None = None
    validation_loss: float | None = None

    # Cost
    estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0

    # Result
    fine_tuned_model_id: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class FinetuneConfig:
    """Configuration for fine-tuning."""

    # Model configuration
    base_model: str = "gpt-3.5-turbo"
    suffix: str = ""  # Custom model suffix

    # Training parameters
    num_epochs: int = 3
    learning_rate_multiplier: float = 1.0
    batch_size: int = 8

    # Data requirements
    min_examples: int = 50
    max_examples: int = 10000
    validation_split: float = 0.1

    # Cost constraints
    max_cost_usd: float = 100.0


@dataclass(frozen=True)
class FinetuneDataset:
    """Prepared dataset for fine-tuning."""

    training_examples: tuple[dict[str, Any], ...]
    validation_examples: tuple[dict[str, Any], ...]

    total_tokens: int
    estimated_cost_usd: float

    # Validation
    is_valid: bool
    validation_errors: tuple[str, ...] = ()


class FinetunePreparer(ABC):
    """
    Abstract base for fine-tune data preparation.

    Different providers require different data formats.
    """

    @abstractmethod
    def prepare_dataset(
        self,
        signature: Signature,
        examples: list[Example],
        config: FinetuneConfig,
    ) -> FinetuneDataset:
        """Prepare examples for fine-tuning."""
        pass

    @abstractmethod
    def estimate_cost(
        self,
        dataset: FinetuneDataset,
        config: FinetuneConfig,
    ) -> float:
        """Estimate fine-tuning cost."""
        pass


class OpenAIFinetunePreparer(FinetunePreparer):
    """Prepares data for OpenAI fine-tuning format."""

    def prepare_dataset(
        self,
        signature: Signature,
        examples: list[Example],
        config: FinetuneConfig,
    ) -> FinetuneDataset:
        """
        Prepare examples in OpenAI fine-tuning format.

        Format: {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
        """
        # Validation
        errors = []
        if len(examples) < config.min_examples:
            errors.append(
                f"Need at least {config.min_examples} examples, got {len(examples)}"
            )
        if len(examples) > config.max_examples:
            errors.append(
                f"Maximum {config.max_examples} examples, got {len(examples)}"
            )

        if errors:
            return FinetuneDataset(
                training_examples=(),
                validation_examples=(),
                total_tokens=0,
                estimated_cost_usd=0.0,
                is_valid=False,
                validation_errors=tuple(errors),
            )

        # Convert to OpenAI format
        formatted_examples = []
        total_tokens = 0

        for ex in examples:
            # Build user message from inputs
            user_content = "\n".join(f"{k}: {v}" for k, v in ex.inputs.items())

            # Build assistant message from outputs
            assistant_content = "\n".join(f"{k}: {v}" for k, v in ex.outputs.items())

            formatted = {
                "messages": [
                    {"role": "system", "content": signature.instructions},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content},
                ]
            }
            formatted_examples.append(formatted)

            # Rough token estimate (4 chars per token)
            total_chars = (
                len(signature.instructions) + len(user_content) + len(assistant_content)
            )
            total_tokens += total_chars // 4

        # Split train/validation
        split_idx = int(len(formatted_examples) * (1 - config.validation_split))
        training = tuple(formatted_examples[:split_idx])
        validation = tuple(formatted_examples[split_idx:])

        # Estimate cost
        est_cost = self.estimate_cost_from_tokens(total_tokens, config)

        return FinetuneDataset(
            training_examples=training,
            validation_examples=validation,
            total_tokens=total_tokens,
            estimated_cost_usd=est_cost,
            is_valid=True,
        )

    def estimate_cost(
        self,
        dataset: FinetuneDataset,
        config: FinetuneConfig,
    ) -> float:
        """Estimate OpenAI fine-tuning cost."""
        return self.estimate_cost_from_tokens(dataset.total_tokens, config)

    def estimate_cost_from_tokens(
        self, total_tokens: int, config: FinetuneConfig
    ) -> float:
        """Estimate cost from token count."""
        # OpenAI pricing (approximate, varies by model)
        # gpt-3.5-turbo: $0.008 per 1K tokens for training
        # gpt-4: $0.03 per 1K tokens for training
        if "gpt-4" in config.base_model:
            cost_per_1k = 0.03
        else:
            cost_per_1k = 0.008

        # Cost = tokens * epochs * cost_per_token
        training_cost = (total_tokens / 1000) * config.num_epochs * cost_per_1k

        return training_cost


class AnthropicFinetunePreparer(FinetunePreparer):
    """Prepares data for Anthropic fine-tuning format (when available)."""

    def prepare_dataset(
        self,
        signature: Signature,
        examples: list[Example],
        config: FinetuneConfig,
    ) -> FinetuneDataset:
        """
        Prepare examples in Anthropic fine-tuning format.

        Note: Format is hypothetical as Anthropic fine-tuning
        is not yet generally available.
        """
        # Similar structure to OpenAI but with Human/Assistant format
        errors = []
        if len(examples) < config.min_examples:
            errors.append(f"Need at least {config.min_examples} examples")

        if errors:
            return FinetuneDataset(
                training_examples=(),
                validation_examples=(),
                total_tokens=0,
                estimated_cost_usd=0.0,
                is_valid=False,
                validation_errors=tuple(errors),
            )

        formatted_examples = []
        total_tokens = 0

        for ex in examples:
            human_content = "\n".join(f"{k}: {v}" for k, v in ex.inputs.items())
            assistant_content = "\n".join(f"{k}: {v}" for k, v in ex.outputs.items())

            formatted = {
                "system": signature.instructions,
                "messages": [
                    {"role": "human", "content": human_content},
                    {"role": "assistant", "content": assistant_content},
                ],
            }
            formatted_examples.append(formatted)

            total_chars = (
                len(signature.instructions)
                + len(human_content)
                + len(assistant_content)
            )
            total_tokens += total_chars // 4

        split_idx = int(len(formatted_examples) * (1 - config.validation_split))
        training = tuple(formatted_examples[:split_idx])
        validation = tuple(formatted_examples[split_idx:])

        # Anthropic pricing estimate (hypothetical)
        est_cost = (total_tokens / 1000) * config.num_epochs * 0.02

        return FinetuneDataset(
            training_examples=training,
            validation_examples=validation,
            total_tokens=total_tokens,
            estimated_cost_usd=est_cost,
            is_valid=True,
        )

    def estimate_cost(
        self,
        dataset: FinetuneDataset,
        config: FinetuneConfig,
    ) -> float:
        """Estimate Anthropic fine-tuning cost (hypothetical)."""
        return (dataset.total_tokens / 1000) * config.num_epochs * 0.02


class BootstrapFinetuneTeleprompter(Generic[A, B]):
    """
    Fine-tuning based teleprompter for production optimization.

    The most powerful optimization method: actually modifies model weights
    using high-quality demonstration data.

    Strategy:
    1. Bootstrap high-quality examples using other teleprompters
    2. Format data for fine-tuning
    3. Submit fine-tuning job to provider
    4. Return fine-tuned model

    Complexity: O(N×M) where N=examples, M=epochs
    Cost: ~$50-500 depending on data size

    Category Theory:
      This is the strongest endofunctor - it actually modifies the
      underlying model functor F rather than just its parameters:
      Finetune: (F, D) → F' where F' ≈ F optimized on D
    """

    def __init__(
        self,
        preparer: FinetunePreparer | None = None,
        config: FinetuneConfig | None = None,
    ):
        """Initialize fine-tuning teleprompter."""
        self.preparer = preparer or OpenAIFinetunePreparer()
        self.config = config or FinetuneConfig()
        self._jobs: dict[str, FinetuneJob] = {}

    @property
    def strategy(self) -> TeleprompterStrategy:
        return TeleprompterStrategy.BOOTSTRAP_FINETUNE

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """
        Prepare and potentially execute fine-tuning.

        Note: Full fine-tuning requires API calls to provider.
        This implementation prepares the data and estimates costs.
        """
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method=self.strategy.value,
        )
        trace.started_at = datetime.now()

        # Check budget
        effective_budget = budget_usd or self.config.max_cost_usd

        # Prepare dataset
        dataset = self.preparer.prepare_dataset(signature, examples, self.config)

        if not dataset.is_valid:
            trace.converged = False
            trace.convergence_reason = (
                f"Dataset invalid: {', '.join(dataset.validation_errors)}"
            )
            trace.completed_at = datetime.now()
            return trace

        # Check cost
        if dataset.estimated_cost_usd > effective_budget:
            trace.converged = False
            trace.convergence_reason = (
                f"Estimated cost ${dataset.estimated_cost_usd:.2f} "
                f"exceeds budget ${effective_budget:.2f}"
            )
            trace.completed_at = datetime.now()
            return trace

        # In a real implementation, we would:
        # 1. Upload dataset to provider
        # 2. Create fine-tuning job
        # 3. Poll for completion
        # 4. Return optimized model reference

        # For now, record the preparation
        trace.add_iteration(
            signature.instructions,
            0.5,  # Baseline placeholder
        )

        trace.final_prompt = signature.instructions
        trace.converged = True
        trace.convergence_reason = (
            f"Dataset prepared: {len(dataset.training_examples)} training, "
            f"{len(dataset.validation_examples)} validation examples. "
            f"Estimated cost: ${dataset.estimated_cost_usd:.2f}"
        )
        trace.cost_usd = dataset.estimated_cost_usd
        trace.total_examples = len(examples)
        trace.completed_at = datetime.now()

        return trace

    def prepare_only(
        self,
        signature: Signature,
        examples: list[Example],
    ) -> FinetuneDataset:
        """Prepare dataset without submitting job."""
        return self.preparer.prepare_dataset(signature, examples, self.config)

    def estimate_cost(
        self,
        signature: Signature,
        examples: list[Example],
    ) -> float:
        """Estimate fine-tuning cost for given examples."""
        dataset = self.prepare_only(signature, examples)
        return dataset.estimated_cost_usd

    def get_job_status(self, job_id: str) -> FinetuneJob | None:
        """Get status of a fine-tuning job."""
        return self._jobs.get(job_id)


# =============================================================================
# Part 5: Unified Advanced Refinery
# =============================================================================


@dataclass
class AdvancedRefineryConfig:
    """Configuration for advanced refinery features."""

    # Auto-selection
    enable_auto_selection: bool = True
    cost_weight: float = 0.3
    quality_weight: float = 0.5
    speed_weight: float = 0.2

    # Drift detection
    enable_drift_detection: bool = True
    drift_threshold: float = 0.1
    detection_window_days: int = 30
    drift_method: DriftDetectionMethod = DriftDetectionMethod.SLIDING_WINDOW

    # Transfer analysis
    enable_transfer_analysis: bool = True
    min_transfer_efficiency: float = 0.7

    # Fine-tuning
    enable_finetuning: bool = False  # Disabled by default (expensive)
    finetune_min_examples: int = 100


class AdvancedRefinery(Generic[A, B]):
    """
    R-gent with Phase 4 advanced features.

    Combines automatic selection, drift detection, transfer analysis,
    and fine-tuning into a unified interface.

    Usage:
        refinery = AdvancedRefinery()

        # Automatic strategy selection
        recommendation = refinery.recommend_strategy(signature, examples)

        # Monitor drift
        refinery.record_performance(0.85)
        drift = refinery.check_drift()

        # Analyze transfer
        prediction = refinery.analyze_transfer(source_model, target_model, trace)
    """

    def __init__(self, config: AdvancedRefineryConfig | None = None):
        """Initialize advanced refinery."""
        self.config = config or AdvancedRefineryConfig()

        # Initialize components
        self._selector = AutoTeleprompterSelector(
            cost_weight=self.config.cost_weight,
            quality_weight=self.config.quality_weight,
            speed_weight=self.config.speed_weight,
        )

        self._drift_detector = ModelDriftDetector(
            drift_threshold=self.config.drift_threshold,
            detection_window_days=self.config.detection_window_days,
            method=self.config.drift_method,
        )

        self._transfer_analyzer = CrossModelTransferAnalyzer()

        self._finetune_teleprompter = BootstrapFinetuneTeleprompter()

        self._reopt_trigger = ReoptimizationTrigger(
            drift_threshold=self.config.drift_threshold,
        )

    def recommend_strategy(
        self,
        signature: Signature,
        examples: list[Example],
        budget_usd: float = 10.0,
        target_accuracy: float = 0.85,
    ) -> StrategyRecommendation:
        """
        Get automatic strategy recommendation.

        Uses task analysis to select optimal teleprompter.
        """
        if not self.config.enable_auto_selection:
            # Return default
            return StrategyRecommendation(
                strategy=TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
                confidence=0.5,
                reasoning="Auto-selection disabled; using default",
            )

        return self._selector.select(signature, examples, budget_usd, target_accuracy)

    def record_performance(
        self,
        score: float,
        num_evaluations: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a performance sample for drift detection."""
        if self.config.enable_drift_detection:
            self._drift_detector.record_sample(score, num_evaluations, metadata)

    def check_drift(self) -> DriftReport:
        """Check for model drift."""
        if not self.config.enable_drift_detection:
            return DriftReport(
                is_drifting=False,
                drift_severity=0.0,
                drift_type="none",
                confidence=0.0,
                current_score=0.0,
                baseline_score=0.0,
                score_delta=0.0,
                trend_direction="stable",
                should_reoptimize=False,
                recommended_action="Drift detection disabled",
                samples_analyzed=0,
                detection_window_days=0,
            )

        return self._drift_detector.detect_drift()

    def should_reoptimize(self) -> tuple[bool, str]:
        """Check if re-optimization should be triggered."""
        drift_report = self.check_drift()
        return self._reopt_trigger.should_trigger(drift_report)

    def analyze_transfer(
        self,
        source_model: ModelProfile,
        target_model: ModelProfile,
        optimization_trace: OptimizationTrace,
    ) -> TransferPrediction:
        """Analyze how well optimization transfers to new model."""
        if not self.config.enable_transfer_analysis:
            return TransferPrediction(
                source_model=source_model,
                target_model=target_model,
                predicted_score=optimization_trace.final_score or 0.5,
                confidence=0.0,
                transfer_efficiency=0.5,
                adjustment_needed="unknown",
                should_transfer=True,
                should_reoptimize=False,
                estimated_reoptimization_cost_usd=0.0,
                reasoning="Transfer analysis disabled",
            )

        return self._transfer_analyzer.analyze_transfer(
            source_model, target_model, optimization_trace
        )

    def prepare_finetune(
        self,
        signature: Signature,
        examples: list[Example],
    ) -> FinetuneDataset:
        """Prepare data for fine-tuning."""
        if not self.config.enable_finetuning:
            return FinetuneDataset(
                training_examples=(),
                validation_examples=(),
                total_tokens=0,
                estimated_cost_usd=0.0,
                is_valid=False,
                validation_errors=("Fine-tuning disabled in config",),
            )

        if len(examples) < self.config.finetune_min_examples:
            return FinetuneDataset(
                training_examples=(),
                validation_examples=(),
                total_tokens=0,
                estimated_cost_usd=0.0,
                is_valid=False,
                validation_errors=(
                    f"Need at least {self.config.finetune_min_examples} examples",
                ),
            )

        return self._finetune_teleprompter.prepare_only(signature, examples)

    async def compile_with_finetune(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        budget_usd: float = 100.0,
    ) -> OptimizationTrace:
        """Run fine-tuning optimization."""
        return await self._finetune_teleprompter.compile(
            signature=signature,
            examples=examples,
            metric=metric,
            budget_usd=budget_usd,
        )

    def update_baseline(self, new_baseline: float) -> None:
        """Update drift detector baseline after re-optimization."""
        self._drift_detector.update_baseline(new_baseline)
        self._reopt_trigger.record_optimization()

    def clear_drift_history(self) -> None:
        """Clear drift detection history."""
        self._drift_detector.clear_history()
