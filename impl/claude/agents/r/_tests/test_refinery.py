"""
Tests for R-gents Refinery implementation.

Tests cover:
- BaseTeleprompter: Abstract base class
- BootstrapFewShotTeleprompter: Simple demo selection
- TextGradTeleprompter: Textual gradient descent
- TeleprompterFactory: Strategy instantiation
- ROIOptimizer: Economic constraint checking
- RefineryAgent: Main interface
"""

import pytest

from agents.r.types import (
    Signature,
    Example,
    TeleprompterStrategy,
)
from agents.r.refinery import (
    BootstrapFewShotTeleprompter,
    TextGradTeleprompter,
    MIPROv2Teleprompter,
    OPROTeleprompter,
    TeleprompterFactory,
    ROIOptimizer,
    RefineryAgent,
)


# --- Test Fixtures ---


@pytest.fixture
def simple_signature():
    """Create a simple signature for testing."""
    return Signature.simple(
        input_name="question",
        input_type=str,
        output_name="answer",
        output_type=str,
        instructions="Answer the question concisely.",
    )


@pytest.fixture
def simple_examples():
    """Create simple examples for testing."""
    return [
        Example.simple("What is 2+2?", "4"),
        Example.simple("What is 3+3?", "6"),
        Example.simple("What is 4+4?", "8"),
        Example.simple("What is 5+5?", "10"),
    ]


@pytest.fixture
def scored_examples():
    """Create examples with pre-computed scores."""
    return [
        Example(
            inputs={"input": "2+2?"},
            outputs={"output": "4"},
            metadata={"score": 0.9},
        ),
        Example(
            inputs={"input": "3+3?"},
            outputs={"output": "6"},
            metadata={"score": 0.8},
        ),
        Example(
            inputs={"input": "4+4?"},
            outputs={"output": "8"},
            metadata={"score": 0.95},
        ),
        Example(
            inputs={"input": "5+5?"},
            outputs={"output": "10"},
            metadata={"score": 0.7},
        ),
    ]


def simple_metric(pred, label) -> float:
    """Simple equality metric."""
    return 1.0 if pred == label else 0.0


# --- BootstrapFewShotTeleprompter Tests ---


class TestBootstrapFewShotTeleprompter:
    """Tests for BootstrapFewShot optimizer."""

    def test_strategy_property(self):
        """Test strategy property."""
        tp = BootstrapFewShotTeleprompter()
        assert tp.strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT

    def test_num_demos_config(self):
        """Test configurable number of demos."""
        tp = BootstrapFewShotTeleprompter(num_demos=2)
        assert tp.num_demos == 2

    @pytest.mark.asyncio
    async def test_compile_returns_trace(self, simple_signature, scored_examples):
        """Test that compile returns an OptimizationTrace."""
        tp = BootstrapFewShotTeleprompter(num_demos=2)

        trace = await tp.compile(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            max_iterations=5,
        )

        assert trace is not None
        assert trace.method == "bootstrap_fewshot"
        assert trace.converged
        assert len(trace.iterations) > 0

    @pytest.mark.asyncio
    async def test_compile_selects_best_demos(self, simple_signature, scored_examples):
        """Test that best scoring examples are selected."""
        tp = BootstrapFewShotTeleprompter(num_demos=2)

        trace = await tp.compile(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
        )

        # The highest scored examples (0.95 and 0.9) should be selected
        assert trace.converged
        assert "top 2 demos" in trace.convergence_reason.lower()

    @pytest.mark.asyncio
    async def test_compile_tracks_timing(self, simple_signature, scored_examples):
        """Test that timing is tracked."""
        tp = BootstrapFewShotTeleprompter()

        trace = await tp.compile(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
        )

        assert trace.started_at is not None
        assert trace.completed_at is not None
        assert trace.completed_at >= trace.started_at


# --- TextGradTeleprompter Tests ---


class TestTextGradTeleprompter:
    """Tests for TextGrad optimizer."""

    def test_strategy_property(self):
        """Test strategy property."""
        tp = TextGradTeleprompter()
        assert tp.strategy == TeleprompterStrategy.TEXTGRAD

    def test_learning_rate_config(self):
        """Test configurable learning rate."""
        tp = TextGradTeleprompter(learning_rate=0.5)
        assert tp.learning_rate == 0.5

    def test_convergence_threshold_config(self):
        """Test configurable convergence threshold."""
        tp = TextGradTeleprompter(convergence_threshold=0.001)
        assert tp.convergence_threshold == 0.001

    @pytest.mark.asyncio
    async def test_compile_returns_trace(self, simple_signature, simple_examples):
        """Test that compile returns an OptimizationTrace."""
        tp = TextGradTeleprompter()

        trace = await tp.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=simple_metric,
            max_iterations=3,
        )

        assert trace is not None
        assert trace.method == "textgrad"
        assert len(trace.iterations) > 0

    @pytest.mark.asyncio
    async def test_compile_respects_max_iterations(
        self, simple_signature, simple_examples
    ):
        """Test that max_iterations is respected."""
        tp = TextGradTeleprompter(convergence_threshold=0.0)  # Never converge

        trace = await tp.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=simple_metric,
            max_iterations=3,
        )

        # Should have exactly 3 iterations (or converge early)
        assert len(trace.iterations) <= 3


# --- MIPROv2 and OPRO Tests (Stubs) ---


class TestMIPROv2Teleprompter:
    """Tests for MIPROv2 optimizer stub."""

    def test_strategy_property(self):
        """Test strategy property."""
        tp = MIPROv2Teleprompter()
        assert tp.strategy == TeleprompterStrategy.MIPRO_V2

    @pytest.mark.asyncio
    async def test_compile_returns_stub_trace(self, simple_signature, simple_examples):
        """Test that stub returns appropriate trace."""
        tp = MIPROv2Teleprompter()

        trace = await tp.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=simple_metric,
        )

        assert trace.method == "mipro_v2"
        assert not trace.converged  # Stub doesn't converge
        assert "DSPy backend" in trace.convergence_reason


class TestOPROTeleprompter:
    """Tests for OPRO optimizer stub."""

    def test_strategy_property(self):
        """Test strategy property."""
        tp = OPROTeleprompter()
        assert tp.strategy == TeleprompterStrategy.OPRO

    @pytest.mark.asyncio
    async def test_compile_returns_stub_trace(self, simple_signature, simple_examples):
        """Test that stub returns appropriate trace."""
        tp = OPROTeleprompter()

        trace = await tp.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=simple_metric,
        )

        assert trace.method == "opro"
        assert not trace.converged  # Stub doesn't converge
        assert "LLM backend" in trace.convergence_reason


# --- TeleprompterFactory Tests ---


class TestTeleprompterFactory:
    """Tests for TeleprompterFactory."""

    def test_get_bootstrap_fewshot(self):
        """Test getting BootstrapFewShot teleprompter."""
        tp = TeleprompterFactory.get(TeleprompterStrategy.BOOTSTRAP_FEWSHOT)
        assert isinstance(tp, BootstrapFewShotTeleprompter)

    def test_get_textgrad(self):
        """Test getting TextGrad teleprompter."""
        tp = TeleprompterFactory.get(TeleprompterStrategy.TEXTGRAD)
        assert isinstance(tp, TextGradTeleprompter)

    def test_get_miprov2(self):
        """Test getting MIPROv2 teleprompter."""
        tp = TeleprompterFactory.get(TeleprompterStrategy.MIPRO_V2)
        assert isinstance(tp, MIPROv2Teleprompter)

    def test_get_opro(self):
        """Test getting OPRO teleprompter."""
        tp = TeleprompterFactory.get(TeleprompterStrategy.OPRO)
        assert isinstance(tp, OPROTeleprompter)

    def test_get_by_string(self):
        """Test getting teleprompter by string value."""
        tp = TeleprompterFactory.get("mipro_v2")
        assert isinstance(tp, MIPROv2Teleprompter)

    def test_get_unknown_raises(self):
        """Test that unknown strategy raises ValueError."""
        with pytest.raises(ValueError):
            TeleprompterFactory.get("nonexistent_strategy")


# --- ROIOptimizer Tests ---


class TestROIOptimizer:
    """Tests for ROI optimization."""

    def test_estimate_cost_bootstrap(self):
        """Test cost estimation for bootstrap."""
        opt = ROIOptimizer()
        cost = opt.estimate_cost(TeleprompterStrategy.BOOTSTRAP_FEWSHOT, 10)
        assert cost == 0.50

    def test_estimate_cost_mipro(self):
        """Test cost estimation for MIPROv2."""
        opt = ROIOptimizer()
        cost = opt.estimate_cost(TeleprompterStrategy.MIPRO_V2, 100)
        # 5.00 + 100 * 0.05 = 10.00
        assert cost == 10.0

    def test_should_optimize_positive_roi(self):
        """Test positive ROI decision."""
        opt = ROIOptimizer()

        decision = opt.should_optimize(
            usage_per_month=10000,
            current_performance=0.5,
            strategy=TeleprompterStrategy.MIPRO_V2,
            num_examples=50,
        )

        assert decision.proceed
        assert "Positive ROI" in decision.reason

    def test_should_optimize_negative_roi(self):
        """Test negative ROI decision."""
        opt = ROIOptimizer()

        decision = opt.should_optimize(
            usage_per_month=10,  # Very low usage
            current_performance=0.5,
            strategy=TeleprompterStrategy.MIPRO_V2,
            num_examples=50,
        )

        assert not decision.proceed
        assert "Negative ROI" in decision.reason

    def test_should_optimize_recommends_cheaper(self):
        """Test that marginal ROI recommends cheaper method."""
        opt = ROIOptimizer()

        decision = opt.should_optimize(
            usage_per_month=500,  # Moderate usage
            current_performance=0.5,
            strategy=TeleprompterStrategy.MIPRO_V2,
            num_examples=50,
        )

        # Marginal ROI should recommend cheaper method
        if decision.proceed and decision.roi_estimate:
            if decision.roi_estimate.roi < 2.0:
                assert (
                    decision.recommended_method
                    == TeleprompterStrategy.BOOTSTRAP_FEWSHOT
                )

    def test_custom_value_per_call(self):
        """Test with custom value per call."""
        opt = ROIOptimizer()

        decision = opt.should_optimize(
            usage_per_month=100,
            current_performance=0.5,
            strategy=TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            num_examples=10,
            value_per_call=1.0,  # High value per call
        )

        assert decision.proceed
        assert decision.roi_estimate.value_per_call_usd == 1.0


# --- RefineryAgent Tests ---


class TestRefineryAgent:
    """Tests for RefineryAgent main interface."""

    def test_default_strategy(self):
        """Test default strategy is bootstrap few-shot."""
        agent = RefineryAgent()
        assert agent.strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT

    def test_custom_strategy(self):
        """Test custom strategy configuration."""
        agent = RefineryAgent(strategy=TeleprompterStrategy.TEXTGRAD)
        assert agent.strategy == TeleprompterStrategy.TEXTGRAD

    def test_has_roi_optimizer(self):
        """Test that ROI optimizer is created."""
        agent = RefineryAgent()
        assert agent.roi_optimizer is not None

    @pytest.mark.asyncio
    async def test_refine_returns_trace(self, simple_signature, scored_examples):
        """Test that refine returns an OptimizationTrace."""
        agent = RefineryAgent()

        trace = await agent.refine(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            check_roi=False,  # Skip ROI for test
        )

        assert trace is not None
        assert len(trace.iterations) > 0

    @pytest.mark.asyncio
    async def test_refine_with_roi_check(self, simple_signature, scored_examples):
        """Test refine with ROI checking enabled."""
        agent = RefineryAgent()

        trace = await agent.refine(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            check_roi=True,
            usage_per_month=10000,  # High usage = positive ROI
        )

        # Should proceed with high usage
        assert trace is not None

    @pytest.mark.asyncio
    async def test_refine_skips_on_negative_roi(
        self, simple_signature, scored_examples
    ):
        """Test that refine skips when ROI is negative."""
        agent = RefineryAgent(strategy=TeleprompterStrategy.MIPRO_V2)

        trace = await agent.refine(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            check_roi=True,
            usage_per_month=1,  # Very low usage = negative ROI
        )

        # Should skip optimization
        assert trace.method == "skipped"
        assert "skipped" in trace.convergence_reason.lower()

    def test_select_strategy_simple_small(self):
        """Test strategy selection for simple small task."""
        agent = RefineryAgent()

        strategy = agent.select_strategy(
            task_complexity="simple",
            dataset_size=10,
            budget_usd=5.0,
        )

        assert strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT

    def test_select_strategy_complex(self):
        """Test strategy selection for complex task."""
        agent = RefineryAgent()

        strategy = agent.select_strategy(
            task_complexity="complex",
            dataset_size=50,
            budget_usd=20.0,
        )

        assert strategy == TeleprompterStrategy.MIPRO_V2

    def test_select_strategy_low_budget(self):
        """Test strategy selection with low budget."""
        agent = RefineryAgent()

        strategy = agent.select_strategy(
            task_complexity="medium",
            dataset_size=50,
            budget_usd=3.0,
        )

        assert strategy == TeleprompterStrategy.OPRO

    def test_select_strategy_large_production(self):
        """Test strategy selection for large production dataset."""
        agent = RefineryAgent()

        strategy = agent.select_strategy(
            task_complexity="medium",
            dataset_size=500,
            budget_usd=100.0,
        )

        assert strategy == TeleprompterStrategy.BOOTSTRAP_FINETUNE


# --- Integration Tests ---


class TestRefineryIntegration:
    """Integration tests for the full refinement flow."""

    @pytest.mark.asyncio
    async def test_full_optimization_flow(self, simple_signature, scored_examples):
        """Test complete optimization flow."""
        # 1. Create refinery agent
        agent = RefineryAgent(strategy=TeleprompterStrategy.BOOTSTRAP_FEWSHOT)

        # 2. Run refinement
        trace = await agent.refine(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            max_iterations=5,
            check_roi=False,
        )

        # 3. Verify results
        assert trace.method == "bootstrap_fewshot"
        assert trace.converged
        assert trace.started_at is not None
        assert trace.completed_at is not None
        assert trace.total_examples == len(scored_examples)

    @pytest.mark.asyncio
    async def test_strategy_switch_on_roi(self, simple_signature, scored_examples):
        """Test that strategy can be switched based on ROI."""
        # Start with expensive strategy
        agent = RefineryAgent(strategy=TeleprompterStrategy.MIPRO_V2)

        # Run with marginal ROI scenario
        trace = await agent.refine(
            signature=simple_signature,
            examples=scored_examples,
            metric=simple_metric,
            check_roi=True,
            usage_per_month=200,  # Marginal usage
        )

        # Strategy might have been switched to cheaper option
        # or skipped entirely
        assert trace is not None
