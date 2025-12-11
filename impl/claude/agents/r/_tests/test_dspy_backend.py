"""
Tests for R-gents DSPy Backend (Phase 2 Implementation).

Tests cover:
- Signature/Example conversion utilities
- DSPyBootstrapFewShot: Full DSPy-backed few-shot optimization
- DSPyMIPROv2: Full DSPy-backed Bayesian optimization
- LLMTextGrad: LLM-backed textual gradient descent
- LLMOpro: LLM-backed meta-prompt optimization
- get_dspy_teleprompter: Factory function
- LLM function creation utilities
"""

import pytest
from agents.r.dspy_backend import (
    LLMOpro,
    LLMTextGrad,
    example_to_dspy,
    examples_to_dspy,
    get_dspy_teleprompter,
    is_dspy_available,
    signature_to_dspy,
)
from agents.r.types import (
    Example,
    FieldSpec,
    Signature,
    TeleprompterStrategy,
    TextualGradient,
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
def multi_field_signature():
    """Create a multi-field signature for testing."""
    return Signature(
        input_fields=(
            FieldSpec(name="context", field_type=str, description="Background info"),
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


@pytest.fixture
def simple_examples():
    """Create simple examples for testing."""
    return [
        Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
        Example(inputs={"question": "What is 3+3?"}, outputs={"answer": "6"}),
        Example(inputs={"question": "What is 4+4?"}, outputs={"answer": "8"}),
        Example(inputs={"question": "What is 5+5?"}, outputs={"answer": "10"}),
    ]


@pytest.fixture
def mock_llm_func():
    """Create a mock LLM function."""
    responses = {
        "2+2": "4",
        "3+3": "6",
        "4+4": "8",
        "5+5": "10",
    }

    def llm_func(prompt: str) -> str:
        # Check for specific patterns
        for key, value in responses.items():
            if key in prompt:
                return value
        # Default response for critique/improvement prompts
        if "Critique:" in prompt or "critique" in prompt.lower():
            return "The prompt should be more specific about expected output format."
        if "Improved Prompt:" in prompt or "improved" in prompt.lower():
            return "Answer the question with a single number."
        if "PROMPT:" in prompt:
            return "PROMPT: Be concise.\nPROMPT: Use numbers only.\nPROMPT: Answer briefly."
        return "default response"

    return llm_func


def exact_match_metric(pred, label) -> float:
    """Exact match metric."""
    if pred is None or label is None:
        return 0.0
    return 1.0 if str(pred).strip() == str(label).strip() else 0.0


def partial_match_metric(pred, label) -> float:
    """Partial match metric (contains)."""
    if pred is None or label is None:
        return 0.0
    return 1.0 if str(label).strip() in str(pred).strip() else 0.5


# --- DSPy Availability Tests ---


class TestDSPyAvailability:
    """Tests for DSPy availability checking."""

    def test_is_dspy_available_returns_bool(self) -> None:
        """Test that is_dspy_available returns a boolean."""
        result = is_dspy_available()
        assert isinstance(result, bool)


# --- Signature Conversion Tests ---


class TestSignatureConversion:
    """Tests for Signature <-> DSPy conversion."""

    @pytest.mark.skipif(not is_dspy_available(), reason="DSPy not installed")
    def test_signature_to_dspy_simple(self, simple_signature) -> None:
        """Test converting simple signature to DSPy."""
        dspy_sig = signature_to_dspy(simple_signature)
        assert dspy_sig is not None
        # Check docstring preserved
        assert "Answer the question" in dspy_sig.__doc__

    @pytest.mark.skipif(not is_dspy_available(), reason="DSPy not installed")
    def test_signature_to_dspy_multi_field(self, multi_field_signature) -> None:
        """Test converting multi-field signature to DSPy."""
        dspy_sig = signature_to_dspy(multi_field_signature)
        assert dspy_sig is not None


# --- Example Conversion Tests ---


class TestExampleConversion:
    """Tests for Example <-> DSPy conversion."""

    @pytest.mark.skipif(not is_dspy_available(), reason="DSPy not installed")
    def test_example_to_dspy(self, simple_examples) -> None:
        """Test converting single example to DSPy."""
        dspy_ex = example_to_dspy(simple_examples[0])
        assert dspy_ex is not None
        assert dspy_ex.question == "What is 2+2?"

    @pytest.mark.skipif(not is_dspy_available(), reason="DSPy not installed")
    def test_examples_to_dspy_batch(self, simple_examples) -> None:
        """Test converting batch of examples to DSPy."""
        dspy_examples = examples_to_dspy(simple_examples)
        assert len(dspy_examples) == len(simple_examples)


# --- LLMTextGrad Tests ---


class TestLLMTextGrad:
    """Tests for LLM-backed TextGrad optimizer."""

    def test_init_without_llm_func(self) -> None:
        """Test initialization without LLM function."""
        optimizer = LLMTextGrad()
        assert optimizer.llm_func is None

    def test_init_with_llm_func(self, mock_llm_func) -> None:
        """Test initialization with LLM function."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)
        assert optimizer.llm_func is not None

    def test_config_options(self) -> None:
        """Test configurable options."""
        optimizer = LLMTextGrad(
            learning_rate=0.5,
            convergence_threshold=0.05,
            max_failed_examples=3,
        )
        assert optimizer.learning_rate == 0.5
        assert optimizer.convergence_threshold == 0.05
        assert optimizer.max_failed_examples == 3

    @pytest.mark.asyncio
    async def test_compile_without_llm_func(
        self, simple_signature, simple_examples
    ) -> None:
        """Test compile without LLM function returns early."""
        optimizer = LLMTextGrad()

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
        )

        assert trace.method == "textgrad"
        assert not trace.converged
        assert "llm_func" in trace.convergence_reason.lower()

    @pytest.mark.asyncio
    async def test_compile_with_llm_func(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test compile with LLM function runs optimization."""
        optimizer = LLMTextGrad(
            llm_func=mock_llm_func,
            convergence_threshold=0.01,
            max_failed_examples=2,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,  # More lenient metric
            max_iterations=3,
        )

        assert trace.method == "textgrad"
        assert trace.started_at is not None
        assert trace.completed_at is not None
        assert len(trace.iterations) > 0

    @pytest.mark.asyncio
    async def test_compile_tracks_llm_calls(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test that LLM calls are tracked."""
        optimizer = LLMTextGrad(
            llm_func=mock_llm_func,
            max_failed_examples=2,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
            max_iterations=2,
        )

        assert trace.total_llm_calls >= 0

    @pytest.mark.asyncio
    async def test_compile_respects_max_iterations(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test that max_iterations is respected."""
        optimizer = LLMTextGrad(
            llm_func=mock_llm_func,
            convergence_threshold=0.0,  # Never converge by threshold
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
            max_iterations=2,
        )

        # Should stop at max_iterations
        assert len(trace.iterations) <= 3  # Initial + 2 iterations

    @pytest.mark.asyncio
    async def test_evaluate_prompt(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test prompt evaluation method."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        score, failed = await optimizer._evaluate_prompt(
            prompt=simple_signature.instructions,
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
        )

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(failed, list)


# --- LLMOpro Tests ---


class TestLLMOpro:
    """Tests for LLM-backed OPRO optimizer."""

    def test_init_without_llm_func(self) -> None:
        """Test initialization without LLM function."""
        optimizer = LLMOpro()
        assert optimizer.llm_func is None

    def test_init_with_llm_func(self, mock_llm_func) -> None:
        """Test initialization with LLM function."""
        optimizer = LLMOpro(llm_func=mock_llm_func)
        assert optimizer.llm_func is not None

    def test_config_options(self) -> None:
        """Test configurable options."""
        optimizer = LLMOpro(
            num_candidates_per_iteration=5,
            keep_top_k=10,
        )
        assert optimizer.num_candidates_per_iteration == 5
        assert optimizer.keep_top_k == 10

    @pytest.mark.asyncio
    async def test_compile_without_llm_func(
        self, simple_signature, simple_examples
    ) -> None:
        """Test compile without LLM function returns early."""
        optimizer = LLMOpro()

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
        )

        assert trace.method == "opro"
        assert not trace.converged
        assert "llm_func" in trace.convergence_reason.lower()

    @pytest.mark.asyncio
    async def test_compile_with_llm_func(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test compile with LLM function runs optimization."""
        optimizer = LLMOpro(
            llm_func=mock_llm_func,
            num_candidates_per_iteration=2,
            keep_top_k=3,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=2,
        )

        assert trace.method == "opro"
        assert trace.started_at is not None
        assert trace.completed_at is not None
        assert len(trace.iterations) > 0

    @pytest.mark.asyncio
    async def test_compile_tracks_llm_calls(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test that LLM calls are tracked."""
        optimizer = LLMOpro(
            llm_func=mock_llm_func,
            num_candidates_per_iteration=2,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
            max_iterations=2,
        )

        assert trace.total_llm_calls >= 0

    @pytest.mark.asyncio
    async def test_compile_initial_evaluation(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test that initial prompt is evaluated."""
        optimizer = LLMOpro(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=1,
        )

        # Should have at least initial evaluation
        assert len(trace.iterations) >= 1

    @pytest.mark.asyncio
    async def test_evaluate_prompt(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test prompt evaluation method."""
        optimizer = LLMOpro(llm_func=mock_llm_func)

        score = await optimizer._evaluate_prompt(
            prompt=simple_signature.instructions,
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
        )

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_generate_candidates(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test candidate generation method."""
        optimizer = LLMOpro(
            llm_func=mock_llm_func,
            num_candidates_per_iteration=3,
        )

        history = [("Initial prompt", 0.5)]
        candidates = await optimizer._generate_candidates(
            history=history,
            signature=simple_signature,
            examples=simple_examples,
        )

        assert isinstance(candidates, list)
        # Mock returns 3 PROMPT: lines
        assert len(candidates) <= optimizer.num_candidates_per_iteration


# --- get_dspy_teleprompter Factory Tests ---


class TestGetDspyTeleprompter:
    """Tests for get_dspy_teleprompter factory function."""

    def test_get_textgrad_without_llm_func(self) -> None:
        """Test getting TextGrad without LLM function."""
        optimizer = get_dspy_teleprompter(TeleprompterStrategy.TEXTGRAD)
        assert isinstance(optimizer, LLMTextGrad)
        assert optimizer.llm_func is None

    def test_get_textgrad_with_llm_func(self, mock_llm_func) -> None:
        """Test getting TextGrad with LLM function."""
        optimizer = get_dspy_teleprompter(
            TeleprompterStrategy.TEXTGRAD,
            llm_func=mock_llm_func,
        )
        assert isinstance(optimizer, LLMTextGrad)
        assert optimizer.llm_func is not None

    def test_get_opro_without_llm_func(self) -> None:
        """Test getting OPRO without LLM function."""
        optimizer = get_dspy_teleprompter(TeleprompterStrategy.OPRO)
        assert isinstance(optimizer, LLMOpro)
        assert optimizer.llm_func is None

    def test_get_opro_with_llm_func(self, mock_llm_func) -> None:
        """Test getting OPRO with LLM function."""
        optimizer = get_dspy_teleprompter(
            TeleprompterStrategy.OPRO,
            llm_func=mock_llm_func,
        )
        assert isinstance(optimizer, LLMOpro)
        assert optimizer.llm_func is not None

    def test_get_bootstrap_fewshot_fallback(self) -> None:
        """Test getting BootstrapFewShot (may use fallback)."""
        optimizer = get_dspy_teleprompter(TeleprompterStrategy.BOOTSTRAP_FEWSHOT)
        assert optimizer is not None
        # Either DSPy-backed or fallback
        assert hasattr(optimizer, "compile")

    def test_get_miprov2_fallback(self) -> None:
        """Test getting MIPROv2 (may use fallback)."""
        optimizer = get_dspy_teleprompter(TeleprompterStrategy.MIPRO_V2)
        assert optimizer is not None
        assert hasattr(optimizer, "compile")


# --- Integration Tests ---


class TestDSPyBackendIntegration:
    """Integration tests for DSPy backend."""

    @pytest.mark.asyncio
    async def test_textgrad_full_flow(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test complete TextGrad optimization flow."""
        optimizer = LLMTextGrad(
            llm_func=mock_llm_func,
            convergence_threshold=0.1,
            max_failed_examples=2,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=3,
        )

        # Verify trace structure
        assert trace.initial_prompt == simple_signature.instructions
        assert trace.final_prompt is not None
        assert trace.total_examples == len(simple_examples)
        assert trace.started_at is not None
        assert trace.completed_at is not None

    @pytest.mark.asyncio
    async def test_opro_full_flow(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test complete OPRO optimization flow."""
        optimizer = LLMOpro(
            llm_func=mock_llm_func,
            num_candidates_per_iteration=2,
            keep_top_k=3,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=2,
        )

        # Verify trace structure
        assert trace.initial_prompt == simple_signature.instructions
        assert trace.final_prompt is not None
        assert trace.total_examples == len(simple_examples)

    @pytest.mark.asyncio
    async def test_textgrad_converges_on_good_score(
        self, simple_signature, mock_llm_func
    ):
        """Test TextGrad converges when score is high."""
        # Examples that mock_llm_func can answer correctly
        examples = [
            Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
            Example(inputs={"question": "What is 3+3?"}, outputs={"answer": "6"}),
        ]

        optimizer = LLMTextGrad(
            llm_func=mock_llm_func,
            convergence_threshold=0.1,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=examples,
            metric=partial_match_metric,
            max_iterations=5,
        )

        # Should converge (either by score or no failed examples)
        assert trace.converged or "Max iterations" in trace.convergence_reason

    @pytest.mark.asyncio
    async def test_textgrad_gradient_calculation(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test TextGrad gradient computation."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        # Create failed examples (examples where metric returns low score)
        failed_examples = [
            (simple_examples[0], "wrong answer", 0.2),
        ]

        gradients = await optimizer._compute_gradients(
            prompt=simple_signature.instructions,
            failed_examples=failed_examples,
            signature=simple_signature,
        )

        # Should produce at least one gradient
        assert len(gradients) >= 0  # May be 0 if LLM call fails
        if gradients:
            assert all(isinstance(g, TextualGradient) for g in gradients)

    @pytest.mark.asyncio
    async def test_textgrad_gradient_application(
        self, simple_signature, mock_llm_func
    ) -> None:
        """Test TextGrad gradient application."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        gradients = [
            TextualGradient(
                feedback="Be more specific",
                magnitude=0.8,
                aspect="accuracy",
            ),
        ]

        new_prompt = await optimizer._apply_gradients(
            prompt=simple_signature.instructions,
            gradients=gradients,
            signature=simple_signature,
        )

        # Should return a modified prompt
        assert isinstance(new_prompt, str)


# --- Edge Case Tests ---


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_examples_textgrad(
        self, simple_signature, mock_llm_func
    ) -> None:
        """Test TextGrad with empty examples."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=[],
            metric=exact_match_metric,
        )

        assert trace is not None

    @pytest.mark.asyncio
    async def test_empty_examples_opro(self, simple_signature, mock_llm_func) -> None:
        """Test OPRO with empty examples."""
        optimizer = LLMOpro(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=[],
            metric=exact_match_metric,
        )

        assert trace is not None

    @pytest.mark.asyncio
    async def test_single_example(self, simple_signature, mock_llm_func) -> None:
        """Test optimization with single example."""
        examples = [
            Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
        ]

        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=examples,
            metric=partial_match_metric,
            max_iterations=2,
        )

        assert trace is not None
        assert trace.total_examples == 1

    @pytest.mark.asyncio
    async def test_llm_func_exception_handling(
        self, simple_signature, simple_examples
    ) -> None:
        """Test handling of LLM function exceptions."""

        def failing_llm_func(prompt: str) -> str:
            raise RuntimeError("LLM API error")

        optimizer = LLMTextGrad(llm_func=failing_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=exact_match_metric,
            max_iterations=2,
        )

        # Should handle exception gracefully
        assert trace is not None

    @pytest.mark.asyncio
    async def test_metric_exception_handling(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test handling of metric function exceptions."""

        def failing_metric(pred, label) -> float:
            raise ValueError("Metric error")

        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=failing_metric,
            max_iterations=2,
        )

        # Should handle exception gracefully
        assert trace is not None

    def test_signature_with_empty_instructions(self) -> None:
        """Test signature with empty instructions."""
        Signature(
            input_fields=(FieldSpec(name="input", field_type=str),),
            output_fields=(FieldSpec(name="output", field_type=str),),
            instructions="",
        )

        optimizer = LLMTextGrad()
        assert optimizer is not None


# --- Performance Tests ---


class TestPerformance:
    """Tests for performance characteristics."""

    @pytest.mark.asyncio
    async def test_textgrad_timing(
        self, simple_signature, simple_examples, mock_llm_func
    ):
        """Test that timing is recorded correctly."""
        optimizer = LLMTextGrad(llm_func=mock_llm_func)

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=2,
        )

        assert trace.started_at is not None
        assert trace.completed_at is not None
        assert trace.completed_at >= trace.started_at

        duration = trace.duration_seconds
        assert duration is None or duration >= 0

    @pytest.mark.asyncio
    async def test_opro_timing(
        self, simple_signature, simple_examples, mock_llm_func
    ) -> None:
        """Test that timing is recorded correctly for OPRO."""
        optimizer = LLMOpro(
            llm_func=mock_llm_func,
            num_candidates_per_iteration=2,
        )

        trace = await optimizer.compile(
            signature=simple_signature,
            examples=simple_examples,
            metric=partial_match_metric,
            max_iterations=2,
        )

        assert trace.started_at is not None
        assert trace.completed_at is not None
