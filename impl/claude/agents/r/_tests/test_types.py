"""
Tests for R-gents foundation types.

Tests cover:
- Signature: Declarative task specification
- Example: Training data unit
- TextualGradient: NL feedback as gradient
- OptimizationTrace: Full optimization history
- ROI types: Economic constraints
"""

import pytest
from datetime import datetime, timedelta

from agents.r.types import (
    Signature,
    FieldSpec,
    Example,
    TextualGradient,
    OptimizationIteration,
    OptimizationTrace,
    OptimizedAgentMeta,
    TeleprompterStrategy,
    OptimizationBudget,
    ROIEstimate,
    OptimizationDecision,
)


# --- Signature Tests ---


class TestSignature:
    """Tests for Signature type."""

    def test_simple_factory(self):
        """Test simple single-field signature creation."""
        sig = Signature.simple(
            input_name="question",
            input_type=str,
            output_name="answer",
            output_type=str,
            instructions="Answer the question concisely.",
        )

        assert len(sig.input_fields) == 1
        assert len(sig.output_fields) == 1
        assert sig.input_fields[0].name == "question"
        assert sig.output_fields[0].name == "answer"
        assert "concisely" in sig.instructions

    def test_multi_field_signature(self):
        """Test signature with multiple fields."""
        sig = Signature(
            input_fields=(
                FieldSpec(
                    name="context", field_type=str, description="Background info"
                ),
                FieldSpec(name="question", field_type=str, description="The question"),
            ),
            output_fields=(
                FieldSpec(name="answer", field_type=str, description="The answer"),
                FieldSpec(
                    name="confidence", field_type=float, description="Confidence score"
                ),
            ),
            instructions="Answer based on context.",
        )

        assert sig.input_names == ("context", "question")
        assert sig.output_names == ("answer", "confidence")

    def test_signature_with_demos(self):
        """Test signature with few-shot examples."""
        sig = Signature(
            input_fields=(FieldSpec(name="x", field_type=int),),
            output_fields=(FieldSpec(name="y", field_type=int),),
            instructions="Double the input.",
            demos=(
                {"inputs": {"x": 2}, "outputs": {"y": 4}},
                {"inputs": {"x": 3}, "outputs": {"y": 6}},
            ),
        )

        assert len(sig.demos) == 2
        assert sig.demos[0]["outputs"]["y"] == 4

    def test_signature_immutability(self):
        """Test that signatures are frozen/immutable."""
        sig = Signature.simple("a", str, "b", str, "test")

        with pytest.raises(AttributeError):
            sig.instructions = "modified"


class TestFieldSpec:
    """Tests for FieldSpec type."""

    def test_basic_field(self):
        """Test basic field specification."""
        field = FieldSpec(name="input", field_type=str)

        assert field.name == "input"
        assert field.field_type is str
        assert field.required is True
        assert field.default is None

    def test_optional_field(self):
        """Test optional field with default."""
        field = FieldSpec(
            name="temperature",
            field_type=float,
            required=False,
            default=0.7,
            description="Sampling temperature",
        )

        assert not field.required
        assert field.default == 0.7
        assert "temperature" in field.description.lower()


# --- Example Tests ---


class TestExample:
    """Tests for Example type."""

    def test_simple_factory(self):
        """Test simple example creation."""
        ex = Example.simple("What is 2+2?", "4")

        assert ex.inputs == {"input": "What is 2+2?"}
        assert ex.outputs == {"output": "4"}

    def test_multi_field_example(self):
        """Test example with multiple fields."""
        ex = Example(
            inputs={"context": "Math class", "question": "2+2?"},
            outputs={"answer": "4", "confidence": 0.99},
            metadata={"source": "training_set_v1"},
        )

        assert ex.inputs["context"] == "Math class"
        assert ex.outputs["confidence"] == 0.99
        assert ex.metadata["source"] == "training_set_v1"

    def test_example_immutability(self):
        """Test that examples are frozen/immutable."""
        ex = Example.simple("a", "b")

        with pytest.raises(AttributeError):
            ex.inputs = {"modified": "value"}


# --- TextualGradient Tests ---


class TestTextualGradient:
    """Tests for TextualGradient type."""

    def test_basic_gradient(self):
        """Test basic gradient creation."""
        grad = TextualGradient(
            feedback="The answer was too verbose. Be more concise.",
            magnitude=0.8,
            aspect="style",
        )

        assert "verbose" in grad.feedback
        assert grad.magnitude == 0.8
        assert grad.aspect == "style"

    def test_gradient_with_source(self):
        """Test gradient linked to source example."""
        ex = Example.simple("What is 2+2?", "4")
        grad = TextualGradient(
            feedback="Correct but explain reasoning",
            source_example=ex,
        )

        assert grad.source_example is ex
        assert grad.magnitude == 1.0  # default

    def test_gradient_immutability(self):
        """Test that gradients are frozen."""
        grad = TextualGradient(feedback="test")

        with pytest.raises(AttributeError):
            grad.feedback = "modified"


# --- OptimizationTrace Tests ---


class TestOptimizationTrace:
    """Tests for OptimizationTrace type."""

    def test_empty_trace(self):
        """Test empty trace creation."""
        trace = OptimizationTrace(initial_prompt="Test prompt")

        assert trace.initial_prompt == "Test prompt"
        assert trace.iterations == []
        assert not trace.converged
        assert trace.baseline_score is None

    def test_add_iteration(self):
        """Test adding iterations to trace."""
        trace = OptimizationTrace(initial_prompt="v1")
        trace.add_iteration("v1", 0.5)
        trace.add_iteration("v2", 0.7)
        trace.add_iteration("v3", 0.85)

        assert len(trace.iterations) == 3
        assert trace.baseline_score == 0.5
        assert trace.final_score == 0.85
        assert trace.improvement == 0.35

    def test_improvement_percentage(self):
        """Test improvement percentage calculation."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.add_iteration("v1", 0.5)
        trace.add_iteration("v2", 0.75)

        assert trace.improvement_percentage == 50.0  # 50% improvement

    def test_improvement_from_zero(self):
        """Test improvement when baseline is zero."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.add_iteration("v1", 0.0)
        trace.add_iteration("v2", 0.5)

        # Division by zero should be handled
        assert trace.improvement_percentage is None

    def test_duration_tracking(self):
        """Test duration calculation."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.started_at = datetime.now()
        trace.completed_at = trace.started_at + timedelta(seconds=30)

        assert trace.duration_seconds == 30.0

    def test_iteration_has_timestamp(self):
        """Test that iterations have timestamps."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.add_iteration("v1", 0.5)

        assert trace.iterations[0].timestamp is not None

    def test_iteration_prompt_hash(self):
        """Test that iterations have unique prompt hashes."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.add_iteration("prompt version 1", 0.5)
        trace.add_iteration("prompt version 2", 0.6)

        assert trace.iterations[0].prompt_hash != trace.iterations[1].prompt_hash

    def test_same_prompt_same_hash(self):
        """Test that same prompt produces same hash."""
        trace = OptimizationTrace(initial_prompt="test")
        trace.add_iteration("identical prompt", 0.5)
        trace.add_iteration("identical prompt", 0.6)

        assert trace.iterations[0].prompt_hash == trace.iterations[1].prompt_hash


# --- ROI Types Tests ---


class TestROIEstimate:
    """Tests for ROI estimation types."""

    def test_positive_roi(self):
        """Test positive ROI calculation."""
        roi = ROIEstimate(
            expected_improvement=0.20,
            estimated_cost_usd=5.0,
            projected_calls_per_month=1000,
            value_per_call_usd=0.10,
        )

        # projected_value = 1000 * 0.10 * 0.20 = 20
        # roi = 20 / 5 = 4.0
        assert roi.projected_value == 20.0
        assert roi.roi == 4.0
        assert roi.is_positive

    def test_negative_roi(self):
        """Test negative ROI detection."""
        roi = ROIEstimate(
            expected_improvement=0.05,
            estimated_cost_usd=10.0,
            projected_calls_per_month=100,
            value_per_call_usd=0.10,
        )

        # projected_value = 100 * 0.10 * 0.05 = 0.5
        # roi = 0.5 / 10 = 0.05
        assert roi.projected_value == 0.5
        assert roi.roi == 0.05
        assert not roi.is_positive

    def test_zero_cost_roi(self):
        """Test ROI with zero cost."""
        roi = ROIEstimate(
            expected_improvement=0.10,
            estimated_cost_usd=0.0,
            projected_calls_per_month=100,
            value_per_call_usd=0.10,
        )

        assert roi.roi == float("inf")
        assert roi.is_positive

    def test_zero_value_roi(self):
        """Test ROI with zero projected value."""
        roi = ROIEstimate(
            expected_improvement=0.0,
            estimated_cost_usd=5.0,
            projected_calls_per_month=100,
            value_per_call_usd=0.10,
        )

        assert roi.projected_value == 0.0
        assert roi.roi == 0.0
        assert not roi.is_positive


class TestOptimizationBudget:
    """Tests for OptimizationBudget type."""

    def test_budget_creation(self):
        """Test budget creation."""
        budget = OptimizationBudget(
            max_cost_usd=10.0,
            max_iterations=50,
            max_duration_seconds=1800.0,
            min_improvement_threshold=0.10,
        )

        assert budget.max_cost_usd == 10.0
        assert budget.max_iterations == 50
        assert budget.max_duration_seconds == 1800.0
        assert budget.min_improvement_threshold == 0.10

    def test_budget_defaults(self):
        """Test budget default values."""
        budget = OptimizationBudget(max_cost_usd=5.0, max_iterations=10)

        assert budget.max_duration_seconds == 3600.0  # 1 hour
        assert budget.min_improvement_threshold == 0.05  # 5%


class TestOptimizationDecision:
    """Tests for OptimizationDecision type."""

    def test_proceed_decision(self):
        """Test decision to proceed."""
        decision = OptimizationDecision(
            proceed=True,
            reason="Positive ROI",
            recommended_method=TeleprompterStrategy.MIPRO_V2,
        )

        assert decision.proceed
        assert decision.recommended_method == TeleprompterStrategy.MIPRO_V2

    def test_skip_decision(self):
        """Test decision to skip."""
        decision = OptimizationDecision(
            proceed=False,
            reason="Negative ROI: cost exceeds value",
        )

        assert not decision.proceed
        assert "Negative ROI" in decision.reason
        assert decision.recommended_method is None


# --- TeleprompterStrategy Tests ---


class TestTeleprompterStrategy:
    """Tests for TeleprompterStrategy enum."""

    def test_all_strategies_exist(self):
        """Test that all documented strategies exist."""
        strategies = [
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM,
            TeleprompterStrategy.MIPRO_V2,
            TeleprompterStrategy.TEXTGRAD,
            TeleprompterStrategy.OPRO,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE,
        ]

        assert len(strategies) == 6

    def test_strategy_values(self):
        """Test strategy string values."""
        assert TeleprompterStrategy.BOOTSTRAP_FEWSHOT.value == "bootstrap_fewshot"
        assert TeleprompterStrategy.MIPRO_V2.value == "mipro_v2"
        assert TeleprompterStrategy.TEXTGRAD.value == "textgrad"

    def test_strategy_from_string(self):
        """Test creating strategy from string value."""
        strategy = TeleprompterStrategy("mipro_v2")
        assert strategy == TeleprompterStrategy.MIPRO_V2


# --- Integration Tests ---


class TestTypesIntegration:
    """Integration tests across R-gent types."""

    def test_optimization_flow_types(self):
        """Test that types compose correctly for optimization flow."""
        # 1. Define signature
        sig = Signature.simple("question", str, "answer", str, "Answer questions.")

        # 2. Create examples
        examples = [
            Example.simple("2+2?", "4"),
            Example.simple("3+3?", "6"),
        ]

        # 3. Create trace
        trace = OptimizationTrace(initial_prompt=sig.instructions, method="test")

        # 4. Simulate optimization
        trace.add_iteration(sig.instructions, 0.5)
        trace.add_iteration("Improved: Answer questions clearly.", 0.8)

        # 5. Verify all types work together
        assert trace.baseline_score == 0.5
        assert trace.final_score == 0.8
        assert abs(trace.improvement - 0.3) < 0.001  # Float comparison

    def test_gradient_in_trace(self):
        """Test that gradients can be recorded in iterations."""
        trace = OptimizationTrace(initial_prompt="test")

        grad1 = TextualGradient(feedback="Be more concise", aspect="style")
        grad2 = TextualGradient(feedback="Add examples", aspect="clarity")

        trace.iterations.append(
            OptimizationIteration(
                iteration=1,
                prompt_hash="abc123",
                score=0.5,
                gradients=(grad1, grad2),
            )
        )

        assert len(trace.iterations[0].gradients) == 2
        assert trace.iterations[0].gradients[0].aspect == "style"
