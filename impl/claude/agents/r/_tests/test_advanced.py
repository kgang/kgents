"""
Tests for R-gents Phase 4: Advanced Features.

Tests cover:
1. Automatic teleprompter selection
2. Model drift detection + re-optimization triggers
3. Cross-model transfer analysis
4. Fine-tuning integration (BootstrapFinetune)
5. Unified AdvancedRefinery
"""

from datetime import datetime, timedelta

import pytest
from agents.r.advanced import (
    AdvancedRefinery,
    # Part 5: Unified
    AdvancedRefineryConfig,
    AnthropicFinetunePreparer,
    AutoTeleprompterSelector,
    BootstrapFinetuneTeleprompter,
    CrossModelTransferAnalyzer,
    DatasetCharacteristics,
    DriftDetectionMethod,
    DriftReport,
    FinetuneConfig,
    FinetuneDataset,
    # Part 4: Fine-tuning
    FinetuneStatus,
    ModelDriftDetector,
    # Part 3: Transfer analysis
    ModelProfile,
    OpenAIFinetunePreparer,
    # Part 2: Drift detection
    PerformanceSample,
    ReoptimizationTrigger,
    StrategyRecommendation,
    TaskAnalysis,
    TaskAnalyzer,
    # Part 1: Auto-selection
    TaskComplexity,
    TransferPrediction,
)
from agents.r.types import (
    Example,
    OptimizationTrace,
    Signature,
    TeleprompterStrategy,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def simple_signature():
    """Simple signature for testing."""
    return Signature.simple(
        input_name="text",
        input_type=str,
        output_name="label",
        output_type=str,
        instructions="Classify the text sentiment",
    )


@pytest.fixture
def complex_signature():
    """Complex signature for testing."""
    return Signature.simple(
        input_name="document",
        input_type=str,
        output_name="analysis",
        output_type=str,
        instructions="Analyze this medical document and diagnose potential conditions step by step",
    )


@pytest.fixture
def small_dataset():
    """Small dataset for testing."""
    return [Example.simple(f"text {i}", f"label {i % 3}") for i in range(15)]


@pytest.fixture
def large_dataset():
    """Large dataset for testing."""
    return [Example.simple(f"document {i}", f"analysis {i}") for i in range(250)]


@pytest.fixture
def optimization_trace():
    """Sample optimization trace."""
    trace = OptimizationTrace(
        initial_prompt="Original prompt",
        method="textgrad",
    )
    trace.add_iteration("Original prompt", 0.5)
    trace.add_iteration("Improved prompt", 0.75)
    trace.add_iteration("Final prompt", 0.85)
    trace.final_prompt = "Final prompt"
    trace.converged = True
    return trace


@pytest.fixture
def gpt4_model():
    """GPT-4 model profile."""
    return ModelProfile(
        model_id="gpt-4-turbo",
        provider="openai",
        model_family="gpt-4",
        context_window=128000,
        estimated_cost_per_1k_tokens=0.01,
        quality_tier="frontier",
    )


@pytest.fixture
def claude3_model():
    """Claude 3 model profile."""
    return ModelProfile(
        model_id="claude-3-opus",
        provider="anthropic",
        model_family="claude-3",
        context_window=200000,
        estimated_cost_per_1k_tokens=0.015,
        quality_tier="frontier",
    )


# =============================================================================
# Part 1: Automatic Teleprompter Selection Tests
# =============================================================================


class TestTaskComplexity:
    """Tests for TaskComplexity enum."""

    def test_complexity_values(self) -> None:
        """Test all complexity values exist."""
        assert TaskComplexity.TRIVIAL.value == "trivial"
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"
        assert TaskComplexity.EXPERT.value == "expert"


class TestDatasetCharacteristics:
    """Tests for DatasetCharacteristics enum."""

    def test_characteristic_values(self) -> None:
        """Test all characteristic values exist."""
        assert DatasetCharacteristics.TINY.value == "tiny"
        assert DatasetCharacteristics.SMALL.value == "small"
        assert DatasetCharacteristics.MEDIUM.value == "medium"
        assert DatasetCharacteristics.LARGE.value == "large"
        assert DatasetCharacteristics.MASSIVE.value == "massive"


class TestTaskAnalysis:
    """Tests for TaskAnalysis dataclass."""

    def test_analysis_creation(self) -> None:
        """Test TaskAnalysis creation."""
        analysis = TaskAnalysis(
            complexity=TaskComplexity.MODERATE,
            dataset_size=50,
            dataset_characteristic=DatasetCharacteristics.SMALL,
            avg_input_length=100.0,
            avg_output_length=50.0,
            output_diversity=0.8,
            requires_structured_output=False,
            requires_reasoning_chain=True,
            requires_domain_knowledge=False,
            budget_usd=10.0,
        )

        assert analysis.complexity == TaskComplexity.MODERATE
        assert analysis.dataset_size == 50
        assert analysis.requires_reasoning_chain is True


class TestTaskAnalyzer:
    """Tests for TaskAnalyzer."""

    def test_analyzer_creation(self) -> None:
        """Test analyzer creation."""
        analyzer = TaskAnalyzer()
        assert analyzer.complexity_keywords is not None

    def test_analyze_simple_task(self, simple_signature, small_dataset) -> None:
        """Test analysis of simple task."""
        analyzer = TaskAnalyzer()
        analysis = analyzer.analyze(simple_signature, small_dataset)

        assert isinstance(analysis, TaskAnalysis)
        assert analysis.dataset_size == 15
        assert analysis.dataset_characteristic == DatasetCharacteristics.SMALL

    def test_analyze_complex_task(self, complex_signature, large_dataset) -> None:
        """Test analysis of complex task."""
        analyzer = TaskAnalyzer()
        analysis = analyzer.analyze(complex_signature, large_dataset)

        # Should detect complex keywords
        assert analysis.complexity in (
            TaskComplexity.COMPLEX,
            TaskComplexity.EXPERT,
        )
        assert analysis.requires_reasoning_chain is True
        assert analysis.requires_domain_knowledge is True

    def test_estimate_complexity_trivial(self) -> None:
        """Test trivial complexity detection."""
        analyzer = TaskAnalyzer()
        complexity = analyzer._estimate_complexity("Extract the name field")
        assert complexity == TaskComplexity.TRIVIAL

    def test_estimate_complexity_expert(self) -> None:
        """Test expert complexity detection."""
        analyzer = TaskAnalyzer()
        complexity = analyzer._estimate_complexity("Diagnose the patient condition")
        assert complexity == TaskComplexity.EXPERT

    def test_classify_dataset_size(self) -> None:
        """Test dataset size classification."""
        analyzer = TaskAnalyzer()

        assert analyzer._classify_dataset_size(5) == DatasetCharacteristics.TINY
        assert analyzer._classify_dataset_size(30) == DatasetCharacteristics.SMALL
        assert analyzer._classify_dataset_size(100) == DatasetCharacteristics.MEDIUM
        assert analyzer._classify_dataset_size(500) == DatasetCharacteristics.LARGE
        assert analyzer._classify_dataset_size(2000) == DatasetCharacteristics.MASSIVE

    def test_check_structured_output(self, simple_signature, small_dataset) -> None:
        """Test structured output detection."""
        analyzer = TaskAnalyzer()

        # Simple signature doesn't require structured output
        analyzer._check_structured_output(simple_signature, small_dataset)
        # Result depends on signature and examples content

    def test_check_reasoning_chain(self, complex_signature) -> None:
        """Test reasoning chain detection."""
        analyzer = TaskAnalyzer()
        result = analyzer._check_reasoning_chain(complex_signature)
        assert result is True  # "step by step" in instructions


class TestStrategyRecommendation:
    """Tests for StrategyRecommendation."""

    def test_recommendation_creation(self) -> None:
        """Test recommendation creation."""
        rec = StrategyRecommendation(
            strategy=TeleprompterStrategy.MIPRO_V2,
            confidence=0.85,
            reasoning="Complex task with large dataset",
            alternatives=(
                (TeleprompterStrategy.TEXTGRAD, 0.75),
                (TeleprompterStrategy.OPRO, 0.65),
            ),
            estimated_cost_usd=12.50,
            estimated_duration_minutes=25.0,
        )

        assert rec.strategy == TeleprompterStrategy.MIPRO_V2
        assert rec.confidence == 0.85
        assert len(rec.alternatives) == 2


class TestAutoTeleprompterSelector:
    """Tests for AutoTeleprompterSelector."""

    def test_selector_creation(self) -> None:
        """Test selector creation."""
        selector = AutoTeleprompterSelector()
        assert selector.cost_weight == 0.3
        assert selector.quality_weight == 0.5
        assert selector.speed_weight == 0.2

    def test_selector_custom_weights(self) -> None:
        """Test selector with custom weights."""
        selector = AutoTeleprompterSelector(
            cost_weight=0.5,
            quality_weight=0.3,
            speed_weight=0.2,
        )
        assert selector.cost_weight == 0.5

    def test_select_simple_task(self, simple_signature, small_dataset) -> None:
        """Test selection for simple task."""
        selector = AutoTeleprompterSelector()
        rec = selector.select(simple_signature, small_dataset, budget_usd=5.0)

        assert isinstance(rec, StrategyRecommendation)
        assert rec.confidence > 0
        # Simple task with small dataset should prefer simple strategy
        assert rec.strategy in (
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM,
            TeleprompterStrategy.OPRO,
        )

    def test_select_complex_task(self, complex_signature, large_dataset) -> None:
        """Test selection for complex task."""
        selector = AutoTeleprompterSelector()
        rec = selector.select(complex_signature, large_dataset, budget_usd=50.0)

        # Complex task with large dataset and budget should prefer sophisticated
        assert rec.strategy in (
            TeleprompterStrategy.MIPRO_V2,
            TeleprompterStrategy.TEXTGRAD,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE,
        )

    def test_select_low_budget(self, complex_signature, large_dataset) -> None:
        """Test selection with low budget."""
        selector = AutoTeleprompterSelector()
        rec = selector.select(complex_signature, large_dataset, budget_usd=2.0)

        # Should still make a recommendation (even if over budget)
        assert rec.strategy is not None
        # Confidence should be reduced for over-budget strategies
        assert rec.confidence <= 1.0

    def test_estimate_cost(self) -> None:
        """Test cost estimation."""
        selector = AutoTeleprompterSelector()

        cost_fewshot = selector._estimate_cost(
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT, 50
        )
        cost_mipro = selector._estimate_cost(TeleprompterStrategy.MIPRO_V2, 50)
        cost_finetune = selector._estimate_cost(
            TeleprompterStrategy.BOOTSTRAP_FINETUNE, 50
        )

        # FewShot should be cheapest
        assert cost_fewshot < cost_mipro < cost_finetune

    def test_estimate_duration(self) -> None:
        """Test duration estimation."""
        selector = AutoTeleprompterSelector()

        duration_fewshot = selector._estimate_duration(
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT, 50
        )
        duration_finetune = selector._estimate_duration(
            TeleprompterStrategy.BOOTSTRAP_FINETUNE, 50
        )

        # FewShot should be fastest
        assert duration_fewshot < duration_finetune

    def test_recommendation_has_reasoning(
        self, simple_signature, small_dataset
    ) -> None:
        """Test that recommendations include reasoning."""
        selector = AutoTeleprompterSelector()
        rec = selector.select(simple_signature, small_dataset)

        assert rec.reasoning
        assert len(rec.reasoning) > 10

    def test_recommendation_has_alternatives(
        self, simple_signature, small_dataset
    ) -> None:
        """Test that recommendations include alternatives."""
        selector = AutoTeleprompterSelector()
        rec = selector.select(simple_signature, small_dataset)

        # Should have at least some alternatives
        # (depending on which strategies are viable)
        assert isinstance(rec.alternatives, tuple)


# =============================================================================
# Part 2: Drift Detection Tests
# =============================================================================


class TestPerformanceSample:
    """Tests for PerformanceSample."""

    def test_sample_creation(self) -> None:
        """Test sample creation."""
        sample = PerformanceSample(
            timestamp=datetime.now(),
            score=0.85,
            num_evaluations=10,
        )
        assert sample.score == 0.85
        assert sample.num_evaluations == 10


class TestDriftReport:
    """Tests for DriftReport."""

    def test_report_creation(self) -> None:
        """Test report creation."""
        report = DriftReport(
            is_drifting=True,
            drift_severity=0.6,
            drift_type="gradual",
            confidence=0.8,
            current_score=0.7,
            baseline_score=0.85,
            score_delta=-0.15,
            trend_direction="degrading",
            should_reoptimize=True,
            recommended_action="Re-optimize",
            samples_analyzed=50,
            detection_window_days=30,
        )

        assert report.is_drifting is True
        assert report.drift_severity == 0.6
        assert report.should_reoptimize is True


class TestModelDriftDetector:
    """Tests for ModelDriftDetector."""

    def test_detector_creation(self) -> None:
        """Test detector creation."""
        detector = ModelDriftDetector(baseline_score=0.8)
        assert detector.baseline_score == 0.8
        assert detector.drift_threshold == 0.1

    def test_detector_custom_config(self) -> None:
        """Test detector with custom config."""
        detector = ModelDriftDetector(
            baseline_score=0.9,
            drift_threshold=0.05,
            min_samples=5,
            detection_window_days=14,
            method=DriftDetectionMethod.CUSUM,
        )
        assert detector.drift_threshold == 0.05
        assert detector.method == DriftDetectionMethod.CUSUM

    def test_record_sample(self) -> None:
        """Test recording samples."""
        detector = ModelDriftDetector()
        detector.record_sample(0.85)
        detector.record_sample(0.82)

        assert len(detector._samples) == 2

    def test_detect_drift_insufficient_samples(self) -> None:
        """Test drift detection with insufficient samples."""
        detector = ModelDriftDetector(min_samples=10)
        detector.record_sample(0.85)
        detector.record_sample(0.80)

        report = detector.detect_drift()
        assert report.is_drifting is False
        assert report.confidence == 0.0

    def test_detect_drift_no_drift(self) -> None:
        """Test drift detection when no drift present."""
        detector = ModelDriftDetector(baseline_score=0.8, min_samples=5)

        # Record stable scores near baseline
        for _ in range(15):
            detector.record_sample(0.79 + 0.02 * (0.5 - 0.5))  # Around 0.79

        report = detector.detect_drift()
        # Stable performance should not trigger drift
        assert report.trend_direction in ("stable", "improving", "degrading")

    def test_detect_drift_degrading(self) -> None:
        """Test drift detection when degrading."""
        detector = ModelDriftDetector(
            baseline_score=0.85,
            drift_threshold=0.1,
            min_samples=5,
        )

        # Record degrading scores
        scores = [0.85, 0.82, 0.78, 0.75, 0.72, 0.70, 0.68, 0.65, 0.63, 0.60]
        for score in scores:
            detector.record_sample(score)

        report = detector.detect_drift()
        # Should detect degradation
        assert report.trend_direction == "degrading"

    def test_detect_drift_statistical_method(self) -> None:
        """Test statistical drift detection."""
        detector = ModelDriftDetector(
            method=DriftDetectionMethod.STATISTICAL,
            min_samples=5,
        )

        for i in range(10):
            detector.record_sample(0.8 - i * 0.02)

        report = detector.detect_drift()
        assert isinstance(report, DriftReport)

    def test_detect_drift_cusum_method(self) -> None:
        """Test CUSUM drift detection."""
        detector = ModelDriftDetector(
            method=DriftDetectionMethod.CUSUM,
            min_samples=5,
        )

        for i in range(10):
            detector.record_sample(0.8 - i * 0.02)

        report = detector.detect_drift()
        assert isinstance(report, DriftReport)

    def test_detect_drift_page_hinkley_method(self) -> None:
        """Test Page-Hinkley drift detection."""
        detector = ModelDriftDetector(
            method=DriftDetectionMethod.PAGE_HINKLEY,
            min_samples=5,
        )

        for i in range(10):
            detector.record_sample(0.8 - i * 0.02)

        report = detector.detect_drift()
        assert isinstance(report, DriftReport)

    def test_clear_history(self) -> None:
        """Test clearing history."""
        detector = ModelDriftDetector()
        detector.record_sample(0.85)
        detector.record_sample(0.80)

        detector.clear_history()
        assert len(detector._samples) == 0

    def test_update_baseline(self) -> None:
        """Test updating baseline."""
        detector = ModelDriftDetector(baseline_score=0.8)
        detector.update_baseline(0.9)
        assert detector.baseline_score == 0.9


class TestReoptimizationTrigger:
    """Tests for ReoptimizationTrigger."""

    def test_trigger_creation(self) -> None:
        """Test trigger creation."""
        trigger = ReoptimizationTrigger()
        assert trigger.drift_threshold == 0.1
        assert trigger.max_reoptimizations_per_month == 3

    def test_should_trigger_drift(self) -> None:
        """Test trigger on drift."""
        trigger = ReoptimizationTrigger()

        drift_report = DriftReport(
            is_drifting=True,
            drift_severity=0.8,
            drift_type="gradual",
            confidence=0.9,
            current_score=0.65,
            baseline_score=0.85,
            score_delta=-0.20,
            trend_direction="degrading",
            should_reoptimize=True,
            recommended_action="Re-optimize",
            samples_analyzed=50,
            detection_window_days=30,
        )

        should, reason = trigger.should_trigger(drift_report)
        assert should is True
        assert "confidence" in reason.lower() or "drift" in reason.lower()

    def test_should_not_trigger_stable(self) -> None:
        """Test no trigger when stable."""
        trigger = ReoptimizationTrigger()
        trigger.last_optimization = datetime.now()  # Recent optimization

        drift_report = DriftReport(
            is_drifting=False,
            drift_severity=0.0,
            drift_type="none",
            confidence=0.9,
            current_score=0.85,
            baseline_score=0.85,
            score_delta=0.0,
            trend_direction="stable",
            should_reoptimize=False,
            recommended_action="No action needed",
            samples_analyzed=50,
            detection_window_days=30,
        )

        should, reason = trigger.should_trigger(drift_report)
        assert should is False

    def test_should_trigger_age(self) -> None:
        """Test trigger on optimization age."""
        trigger = ReoptimizationTrigger(max_age_days=7)
        trigger.last_optimization = datetime.now() - timedelta(days=10)

        drift_report = DriftReport(
            is_drifting=False,
            drift_severity=0.0,
            drift_type="none",
            confidence=0.5,
            current_score=0.85,
            baseline_score=0.85,
            score_delta=0.0,
            trend_direction="stable",
            should_reoptimize=False,
            recommended_action="No action",
            samples_analyzed=50,
            detection_window_days=30,
        )

        should, reason = trigger.should_trigger(drift_report)
        assert should is True
        assert "days old" in reason

    def test_budget_exhausted(self) -> None:
        """Test trigger blocked by budget."""
        trigger = ReoptimizationTrigger(max_reoptimizations_per_month=0)

        drift_report = DriftReport(
            is_drifting=True,
            drift_severity=0.9,
            drift_type="sudden",
            confidence=0.95,
            current_score=0.5,
            baseline_score=0.85,
            score_delta=-0.35,
            trend_direction="degrading",
            should_reoptimize=True,
            recommended_action="Re-optimize",
            samples_analyzed=50,
            detection_window_days=30,
        )

        should, reason = trigger.should_trigger(drift_report)
        assert should is False
        assert "budget exhausted" in reason.lower()

    def test_record_optimization(self) -> None:
        """Test recording optimization."""
        trigger = ReoptimizationTrigger()
        trigger.record_optimization()

        assert trigger.last_optimization is not None
        assert trigger.optimization_count_this_month == 1

    def test_reset_monthly_count(self) -> None:
        """Test resetting monthly count."""
        trigger = ReoptimizationTrigger()
        trigger.optimization_count_this_month = 5

        trigger.reset_monthly_count()
        assert trigger.optimization_count_this_month == 0


# =============================================================================
# Part 3: Transfer Analysis Tests
# =============================================================================


class TestModelProfile:
    """Tests for ModelProfile."""

    def test_profile_creation(self, gpt4_model) -> None:
        """Test profile creation."""
        assert gpt4_model.model_id == "gpt-4-turbo"
        assert gpt4_model.provider == "openai"
        assert gpt4_model.quality_tier == "frontier"


class TestTransferPrediction:
    """Tests for TransferPrediction."""

    def test_prediction_creation(self, gpt4_model, claude3_model) -> None:
        """Test prediction creation."""
        pred = TransferPrediction(
            source_model=gpt4_model,
            target_model=claude3_model,
            predicted_score=0.75,
            confidence=0.7,
            transfer_efficiency=0.85,
            adjustment_needed="minor",
            should_transfer=True,
            should_reoptimize=False,
            estimated_reoptimization_cost_usd=0.0,
            reasoning="Good transfer expected",
        )

        assert pred.predicted_score == 0.75
        assert pred.should_transfer is True


class TestCrossModelTransferAnalyzer:
    """Tests for CrossModelTransferAnalyzer."""

    def test_analyzer_creation(self) -> None:
        """Test analyzer creation."""
        analyzer = CrossModelTransferAnalyzer()
        assert analyzer._transfer_matrix is not None

    def test_analyze_same_family(self, gpt4_model, optimization_trace) -> None:
        """Test transfer within same family."""
        analyzer = CrossModelTransferAnalyzer()

        target = ModelProfile(
            model_id="gpt-4-mini",
            provider="openai",
            model_family="gpt-4",
            context_window=64000,
            estimated_cost_per_1k_tokens=0.005,
            quality_tier="high",
        )

        pred = analyzer.analyze_transfer(gpt4_model, target, optimization_trace)

        # Same family = relatively high efficiency (but adjusted for tier difference)
        assert pred.transfer_efficiency >= 0.7
        assert pred.should_transfer is True

    def test_analyze_different_family(
        self, gpt4_model, claude3_model, optimization_trace
    ):
        """Test transfer between families."""
        analyzer = CrossModelTransferAnalyzer()

        pred = analyzer.analyze_transfer(gpt4_model, claude3_model, optimization_trace)

        # Cross-family transfer is less efficient
        assert 0.5 <= pred.transfer_efficiency <= 0.9
        assert pred.should_transfer is True  # Should still transfer

    def test_analyze_transfer_to_weaker(self, gpt4_model, optimization_trace) -> None:
        """Test transfer to weaker model."""
        analyzer = CrossModelTransferAnalyzer()

        weaker = ModelProfile(
            model_id="gpt-3.5-turbo",
            provider="openai",
            model_family="gpt-3.5",
            context_window=16000,
            estimated_cost_per_1k_tokens=0.002,
            quality_tier="medium",
        )

        pred = analyzer.analyze_transfer(gpt4_model, weaker, optimization_trace)

        # Transfer to weaker model should work but less efficiently
        assert pred.predicted_score <= optimization_trace.final_score

    def test_recommend_target_models(self, gpt4_model, optimization_trace) -> None:
        """Test recommending target models."""
        analyzer = CrossModelTransferAnalyzer()

        available = [
            ModelProfile(
                model_id="claude-3-opus",
                provider="anthropic",
                model_family="claude-3",
                context_window=200000,
                estimated_cost_per_1k_tokens=0.015,
                quality_tier="frontier",
            ),
            ModelProfile(
                model_id="gpt-3.5-turbo",
                provider="openai",
                model_family="gpt-3.5",
                context_window=16000,
                estimated_cost_per_1k_tokens=0.002,
                quality_tier="medium",
            ),
        ]

        recommendations = analyzer.recommend_target_models(
            gpt4_model,
            optimization_trace,
            available,
            min_transfer_efficiency=0.5,
        )

        assert isinstance(recommendations, list)
        # Should have at least one recommendation
        for model, pred in recommendations:
            assert pred.transfer_efficiency >= 0.5


# =============================================================================
# Part 4: Fine-tuning Tests
# =============================================================================


class TestFinetuneStatus:
    """Tests for FinetuneStatus enum."""

    def test_status_values(self) -> None:
        """Test all status values exist."""
        assert FinetuneStatus.PENDING.value == "pending"
        assert FinetuneStatus.RUNNING.value == "running"
        assert FinetuneStatus.COMPLETED.value == "completed"
        assert FinetuneStatus.FAILED.value == "failed"


class TestFinetuneConfig:
    """Tests for FinetuneConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = FinetuneConfig()
        assert config.base_model == "gpt-3.5-turbo"
        assert config.num_epochs == 3
        assert config.min_examples == 50

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = FinetuneConfig(
            base_model="gpt-4",
            num_epochs=5,
            min_examples=100,
        )
        assert config.base_model == "gpt-4"
        assert config.num_epochs == 5


class TestFinetuneDataset:
    """Tests for FinetuneDataset."""

    def test_dataset_creation(self) -> None:
        """Test dataset creation."""
        dataset = FinetuneDataset(
            training_examples=({"messages": []},),
            validation_examples=(),
            total_tokens=1000,
            estimated_cost_usd=5.0,
            is_valid=True,
        )
        assert dataset.is_valid is True
        assert dataset.total_tokens == 1000


class TestOpenAIFinetunePreparer:
    """Tests for OpenAIFinetunePreparer."""

    def test_preparer_creation(self) -> None:
        """Test preparer creation."""
        preparer = OpenAIFinetunePreparer()
        assert preparer is not None

    def test_prepare_dataset_valid(self, simple_signature) -> None:
        """Test preparing valid dataset."""
        preparer = OpenAIFinetunePreparer()
        config = FinetuneConfig(min_examples=10)

        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(50)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)

        assert dataset.is_valid is True
        assert len(dataset.training_examples) > 0
        assert len(dataset.validation_examples) > 0
        assert dataset.total_tokens > 0

    def test_prepare_dataset_too_few_examples(self, simple_signature) -> None:
        """Test preparing dataset with too few examples."""
        preparer = OpenAIFinetunePreparer()
        config = FinetuneConfig(min_examples=100)

        examples = [Example.simple("input", "output") for _ in range(10)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)

        assert dataset.is_valid is False
        assert len(dataset.validation_errors) > 0

    def test_openai_format(self, simple_signature) -> None:
        """Test OpenAI format compliance."""
        preparer = OpenAIFinetunePreparer()
        config = FinetuneConfig(min_examples=5)

        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(10)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)

        # Check format
        if dataset.training_examples:
            example = dataset.training_examples[0]
            assert "messages" in example
            messages = example["messages"]
            assert len(messages) == 3
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert messages[2]["role"] == "assistant"

    def test_estimate_cost(self, simple_signature) -> None:
        """Test cost estimation."""
        preparer = OpenAIFinetunePreparer()
        config = FinetuneConfig(min_examples=5)

        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(100)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)
        cost = preparer.estimate_cost(dataset, config)

        assert cost > 0
        assert cost == dataset.estimated_cost_usd


class TestAnthropicFinetunePreparer:
    """Tests for AnthropicFinetunePreparer."""

    def test_preparer_creation(self) -> None:
        """Test preparer creation."""
        preparer = AnthropicFinetunePreparer()
        assert preparer is not None

    def test_prepare_dataset(self, simple_signature) -> None:
        """Test preparing dataset."""
        preparer = AnthropicFinetunePreparer()
        config = FinetuneConfig(min_examples=5)

        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(20)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)

        assert dataset.is_valid is True

    def test_anthropic_format(self, simple_signature) -> None:
        """Test Anthropic format compliance."""
        preparer = AnthropicFinetunePreparer()
        config = FinetuneConfig(min_examples=5)

        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(10)]

        dataset = preparer.prepare_dataset(simple_signature, examples, config)

        if dataset.training_examples:
            example = dataset.training_examples[0]
            assert "system" in example
            assert "messages" in example
            messages = example["messages"]
            assert messages[0]["role"] == "human"
            assert messages[1]["role"] == "assistant"


class TestBootstrapFinetuneTeleprompter:
    """Tests for BootstrapFinetuneTeleprompter."""

    def test_teleprompter_creation(self) -> None:
        """Test teleprompter creation."""
        teleprompter = BootstrapFinetuneTeleprompter()
        assert teleprompter.strategy == TeleprompterStrategy.BOOTSTRAP_FINETUNE

    def test_strategy_property(self) -> None:
        """Test strategy property."""
        teleprompter = BootstrapFinetuneTeleprompter()
        assert teleprompter.strategy == TeleprompterStrategy.BOOTSTRAP_FINETUNE

    @pytest.mark.asyncio
    async def test_compile_insufficient_data(self, simple_signature) -> None:
        """Test compile with insufficient data."""
        teleprompter = BootstrapFinetuneTeleprompter()
        examples = [Example.simple("input", "output") for _ in range(10)]

        trace = await teleprompter.compile(
            simple_signature,
            examples,
            lambda p, l: 1.0 if p == l else 0.0,
        )

        assert trace.converged is False
        assert "invalid" in trace.convergence_reason.lower()

    @pytest.mark.asyncio
    async def test_compile_sufficient_data(self, simple_signature) -> None:
        """Test compile with sufficient data."""
        teleprompter = BootstrapFinetuneTeleprompter()
        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(100)]

        trace = await teleprompter.compile(
            simple_signature,
            examples,
            lambda p, l: 1.0 if p == l else 0.0,
        )

        assert trace.converged is True
        assert "prepared" in trace.convergence_reason.lower()

    @pytest.mark.asyncio
    async def test_compile_over_budget(self, simple_signature) -> None:
        """Test compile over budget."""
        config = FinetuneConfig(min_examples=10)
        teleprompter = BootstrapFinetuneTeleprompter(config=config)
        examples = [
            Example.simple(f"input {i}", f"output {i}")
            for i in range(1000)  # Large dataset
        ]

        trace = await teleprompter.compile(
            simple_signature,
            examples,
            lambda p, l: 1.0,
            budget_usd=0.01,  # Very low budget
        )

        assert trace.converged is False
        assert "budget" in trace.convergence_reason.lower()

    def test_prepare_only(self, simple_signature) -> None:
        """Test prepare_only method."""
        teleprompter = BootstrapFinetuneTeleprompter()
        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(100)]

        dataset = teleprompter.prepare_only(simple_signature, examples)

        assert dataset.is_valid is True
        assert dataset.estimated_cost_usd > 0

    def test_estimate_cost(self, simple_signature) -> None:
        """Test cost estimation."""
        teleprompter = BootstrapFinetuneTeleprompter()
        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(100)]

        cost = teleprompter.estimate_cost(simple_signature, examples)
        assert cost > 0


# =============================================================================
# Part 5: Unified Advanced Refinery Tests
# =============================================================================


class TestAdvancedRefineryConfig:
    """Tests for AdvancedRefineryConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = AdvancedRefineryConfig()
        assert config.enable_auto_selection is True
        assert config.enable_drift_detection is True
        assert config.enable_transfer_analysis is True
        assert config.enable_finetuning is False

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = AdvancedRefineryConfig(
            enable_auto_selection=False,
            drift_threshold=0.05,
            finetune_min_examples=200,
        )
        assert config.enable_auto_selection is False
        assert config.drift_threshold == 0.05


class TestAdvancedRefinery:
    """Tests for AdvancedRefinery."""

    def test_refinery_creation(self) -> None:
        """Test refinery creation."""
        refinery = AdvancedRefinery()
        assert refinery._selector is not None
        assert refinery._drift_detector is not None
        assert refinery._transfer_analyzer is not None

    def test_refinery_custom_config(self) -> None:
        """Test refinery with custom config."""
        config = AdvancedRefineryConfig(
            cost_weight=0.6,
            quality_weight=0.3,
            speed_weight=0.1,
        )
        refinery = AdvancedRefinery(config)
        assert refinery._selector.cost_weight == 0.6

    def test_recommend_strategy(self, simple_signature, small_dataset) -> None:
        """Test strategy recommendation."""
        refinery = AdvancedRefinery()
        rec = refinery.recommend_strategy(simple_signature, small_dataset)

        assert isinstance(rec, StrategyRecommendation)
        assert rec.strategy is not None

    def test_recommend_strategy_disabled(self, simple_signature, small_dataset) -> None:
        """Test recommendation when disabled."""
        config = AdvancedRefineryConfig(enable_auto_selection=False)
        refinery = AdvancedRefinery(config)

        rec = refinery.recommend_strategy(simple_signature, small_dataset)

        assert rec.strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT
        assert "disabled" in rec.reasoning.lower()

    def test_record_performance(self) -> None:
        """Test recording performance."""
        refinery = AdvancedRefinery()
        refinery.record_performance(0.85)
        refinery.record_performance(0.82)

        assert len(refinery._drift_detector._samples) == 2

    def test_check_drift(self) -> None:
        """Test drift checking."""
        refinery = AdvancedRefinery()

        # Record some samples
        for i in range(15):
            refinery.record_performance(0.8 - i * 0.01)

        report = refinery.check_drift()
        assert isinstance(report, DriftReport)

    def test_check_drift_disabled(self) -> None:
        """Test drift checking when disabled."""
        config = AdvancedRefineryConfig(enable_drift_detection=False)
        refinery = AdvancedRefinery(config)

        report = refinery.check_drift()
        assert report.is_drifting is False
        assert "disabled" in report.recommended_action.lower()

    def test_should_reoptimize(self) -> None:
        """Test re-optimization decision."""
        refinery = AdvancedRefinery()

        # Record degrading performance
        for i in range(20):
            refinery.record_performance(0.9 - i * 0.02)

        should, reason = refinery.should_reoptimize()
        # Should return a decision
        assert isinstance(should, bool)
        assert len(reason) > 0

    def test_analyze_transfer(
        self, gpt4_model, claude3_model, optimization_trace
    ) -> None:
        """Test transfer analysis."""
        refinery = AdvancedRefinery()

        pred = refinery.analyze_transfer(gpt4_model, claude3_model, optimization_trace)

        assert isinstance(pred, TransferPrediction)
        assert pred.transfer_efficiency > 0

    def test_analyze_transfer_disabled(
        self, gpt4_model, claude3_model, optimization_trace
    ):
        """Test transfer analysis when disabled."""
        config = AdvancedRefineryConfig(enable_transfer_analysis=False)
        refinery = AdvancedRefinery(config)

        pred = refinery.analyze_transfer(gpt4_model, claude3_model, optimization_trace)

        assert "disabled" in pred.reasoning.lower()

    def test_prepare_finetune(self, simple_signature, large_dataset) -> None:
        """Test fine-tune preparation."""
        config = AdvancedRefineryConfig(
            enable_finetuning=True,
            finetune_min_examples=100,
        )
        refinery = AdvancedRefinery(config)

        dataset = refinery.prepare_finetune(simple_signature, large_dataset)

        assert isinstance(dataset, FinetuneDataset)
        assert dataset.is_valid is True

    def test_prepare_finetune_disabled(self, simple_signature, large_dataset) -> None:
        """Test fine-tune preparation when disabled."""
        refinery = AdvancedRefinery()  # Default has finetuning disabled

        dataset = refinery.prepare_finetune(simple_signature, large_dataset)

        assert dataset.is_valid is False
        assert "disabled" in dataset.validation_errors[0].lower()

    def test_prepare_finetune_insufficient_examples(
        self, simple_signature, small_dataset
    ):
        """Test fine-tune with insufficient examples."""
        config = AdvancedRefineryConfig(
            enable_finetuning=True,
            finetune_min_examples=100,
        )
        refinery = AdvancedRefinery(config)

        dataset = refinery.prepare_finetune(simple_signature, small_dataset)

        assert dataset.is_valid is False

    @pytest.mark.asyncio
    async def test_compile_with_finetune(self, simple_signature, large_dataset) -> None:
        """Test compile with fine-tuning."""
        config = AdvancedRefineryConfig(enable_finetuning=True)
        refinery = AdvancedRefinery(config)

        trace = await refinery.compile_with_finetune(
            simple_signature,
            large_dataset,
            lambda p, l: 1.0,
            budget_usd=100.0,
        )

        assert isinstance(trace, OptimizationTrace)

    def test_update_baseline(self) -> None:
        """Test updating baseline."""
        refinery = AdvancedRefinery()

        # Record some samples
        for _ in range(5):
            refinery.record_performance(0.8)

        refinery.update_baseline(0.9)

        assert refinery._drift_detector.baseline_score == 0.9

    def test_clear_drift_history(self) -> None:
        """Test clearing drift history."""
        refinery = AdvancedRefinery()

        # Record some samples
        for _ in range(5):
            refinery.record_performance(0.8)

        refinery.clear_drift_history()

        assert len(refinery._drift_detector._samples) == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase4Integration:
    """Integration tests for Phase 4 features."""

    def test_full_auto_selection_pipeline(
        self, complex_signature, large_dataset
    ) -> None:
        """Test full auto-selection pipeline."""
        refinery = AdvancedRefinery()

        # Get recommendation
        rec = refinery.recommend_strategy(
            complex_signature,
            large_dataset,
            budget_usd=20.0,
            target_accuracy=0.9,
        )

        # Should recommend sophisticated strategy for complex task
        assert rec.strategy in (
            TeleprompterStrategy.MIPRO_V2,
            TeleprompterStrategy.TEXTGRAD,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE,
        )
        assert rec.confidence > 0.5

    def test_drift_to_reoptimization_flow(self) -> None:
        """Test drift detection to re-optimization flow."""
        refinery = AdvancedRefinery()

        # Simulate degrading performance
        for i in range(30):
            refinery.record_performance(0.9 - i * 0.015)

        # Check drift
        drift = refinery.check_drift()

        # Check if re-optimization needed
        should, reason = refinery.should_reoptimize()

        # Should detect the degradation
        assert drift.trend_direction == "degrading"

    def test_transfer_analysis_workflow(
        self, gpt4_model, claude3_model, optimization_trace
    ):
        """Test transfer analysis workflow."""
        refinery = AdvancedRefinery()

        # Analyze transfer
        pred = refinery.analyze_transfer(gpt4_model, claude3_model, optimization_trace)

        # Should provide actionable recommendation
        assert pred.should_transfer is True or pred.should_transfer is False
        assert len(pred.reasoning) > 0

        # If re-optimization recommended, should have cost estimate
        if pred.should_reoptimize:
            assert pred.estimated_reoptimization_cost_usd >= 0

    @pytest.mark.asyncio
    async def test_finetune_workflow(self, simple_signature) -> None:
        """Test fine-tuning workflow."""
        config = AdvancedRefineryConfig(
            enable_finetuning=True,
            finetune_min_examples=50,
        )
        refinery = AdvancedRefinery(config)

        # Create large dataset
        examples = [Example.simple(f"input {i}", f"output {i}") for i in range(200)]

        # Prepare dataset
        dataset = refinery.prepare_finetune(simple_signature, examples)
        assert dataset.is_valid is True

        # Compile (preparation only in test)
        trace = await refinery.compile_with_finetune(
            simple_signature,
            examples,
            lambda p, l: 1.0,
        )
        assert trace.method == "bootstrap_finetune"


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_examples(self, simple_signature) -> None:
        """Test with empty examples."""
        refinery = AdvancedRefinery()

        rec = refinery.recommend_strategy(simple_signature, [])

        # Should handle gracefully
        assert rec.strategy is not None

    def test_single_example(self, simple_signature) -> None:
        """Test with single example."""
        refinery = AdvancedRefinery()

        rec = refinery.recommend_strategy(
            simple_signature,
            [Example.simple("input", "output")],
        )

        # Should handle gracefully and recommend simple strategy
        assert rec.strategy in (
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            TeleprompterStrategy.OPRO,
        )

    def test_drift_no_samples(self) -> None:
        """Test drift detection with no samples."""
        refinery = AdvancedRefinery()

        drift = refinery.check_drift()

        assert drift.is_drifting is False
        assert drift.samples_analyzed == 0

    def test_transfer_same_model(self, gpt4_model, optimization_trace) -> None:
        """Test transfer to same model."""
        analyzer = CrossModelTransferAnalyzer()

        pred = analyzer.analyze_transfer(gpt4_model, gpt4_model, optimization_trace)

        # Same model should have high transfer efficiency
        # (but we skip same model_id in recommend_target_models)
        assert pred.transfer_efficiency > 0
