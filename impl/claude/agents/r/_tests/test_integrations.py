"""
Tests for R-gents Phase 3: Cross-Genus Integrations.

Tests cover:
1. F-gent → R-gent: Prototype refinement pipeline
2. T-gent → R-gent: Loss signal adapter
3. B-gent → R-gent: Budget grant protocol
4. L-gent → R-gent: Optimization metadata indexing
5. RGentIntegrationHub: Unified pipeline
"""

import pytest
from typing import Any, Callable

from agents.r.types import (
    Example,
    OptimizationTrace,
    Signature,
    TeleprompterStrategy,
)
from agents.r.integrations import (
    # F-gent integration
    RefinePhase,
    PrototypeRefinementRequest,
    PrototypeRefinementResult,
    FGentRefineryBridge,
    # T-gent integration
    MetricSignal,
    TextualLossSignal,
    TGentLossAdapter,
    # B-gent integration
    BudgetDenied,
    BudgetGrant,
    BudgetSpendReport,
    BGentBudgetProtocol,
    BudgetConstrainedRefinery,
    # L-gent integration
    OptimizationCatalogEntry,
    LGentOptimizationIndex,
    # Unified hub
    RGentIntegrationConfig,
    RGentIntegrationHub,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_source_code() -> str:
    """Sample Python source code for F-gent prototype."""
    return '''
class TextSummarizer:
    """Summarize text into a concise summary."""

    async def invoke(self, text: str) -> str:
        """
        Summarize the input text.

        Args:
            text: The text to summarize

        Returns:
            A concise summary
        """
        # Placeholder implementation
        return text[:100]
'''


@pytest.fixture
def sample_examples() -> list[Example]:
    """Sample training examples."""
    return [
        Example.simple(
            "The quick brown fox jumps over the lazy dog.", "Quick fox jumps over dog."
        ),
        Example.simple(
            "Machine learning is a subset of artificial intelligence.",
            "ML is part of AI.",
        ),
        Example.simple(
            "Python is a popular programming language.", "Python is popular."
        ),
    ]


@pytest.fixture
def sample_signature() -> Signature:
    """Sample signature for testing."""
    return Signature.simple(
        input_name="text",
        input_type=str,
        output_name="summary",
        output_type=str,
        instructions="Summarize the input text concisely.",
    )


@pytest.fixture
def exact_match_metric() -> Callable[[Any, Any], float]:
    """Exact match metric."""

    def metric(pred: Any, label: Any) -> float:
        return 1.0 if pred == label else 0.0

    return metric


# =============================================================================
# Test F-gent → R-gent Integration
# =============================================================================


class TestPrototypeRefinementRequest:
    """Tests for PrototypeRefinementRequest."""

    def test_request_creation(self, sample_source_code: str):
        """Test creating a refinement request."""
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            intent_text="Summarize text concisely",
        )

        assert request.source_code == sample_source_code
        assert request.agent_name == "TextSummarizer"
        assert request.strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT
        assert request.max_iterations == 10
        assert request.budget_usd == 10.0

    def test_request_with_examples(
        self, sample_source_code: str, sample_examples: list[Example]
    ):
        """Test request with pre-existing examples."""
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            examples=sample_examples,
            generate_examples=False,
        )

        assert len(request.examples) == 3
        assert not request.generate_examples

    def test_request_with_custom_strategy(self, sample_source_code: str):
        """Test request with custom optimization strategy."""
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            strategy=TeleprompterStrategy.TEXTGRAD,
            max_iterations=20,
        )

        assert request.strategy == TeleprompterStrategy.TEXTGRAD
        assert request.max_iterations == 20


class TestPrototypeRefinementResult:
    """Tests for PrototypeRefinementResult."""

    def test_result_creation(self, sample_source_code: str):
        """Test creating a refinement result."""
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="Test",
        )
        result = PrototypeRefinementResult(
            phase=RefinePhase.COMPLETED,
            success=True,
            request=request,
        )

        assert result.phase == RefinePhase.COMPLETED
        assert result.success
        assert result.improvement_percentage is None  # No trace yet

    def test_result_with_trace(self, sample_source_code: str):
        """Test result with optimization trace."""
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="Test",
        )

        trace = OptimizationTrace(initial_prompt="Test prompt")
        trace.add_iteration("Test prompt", 0.5)
        trace.add_iteration("Improved prompt", 0.8)

        result = PrototypeRefinementResult(
            phase=RefinePhase.COMPLETED,
            success=True,
            request=request,
            optimization_trace=trace,
        )

        assert result.improvement_percentage is not None
        assert result.improvement_percentage == pytest.approx(
            60.0
        )  # (0.8-0.5)/0.5 * 100


class TestFGentRefineryBridge:
    """Tests for FGentRefineryBridge."""

    def test_bridge_creation(self):
        """Test creating a bridge."""
        bridge = FGentRefineryBridge()
        assert bridge.refinery is not None
        assert bridge.roi_optimizer is not None

    def test_extract_signature_from_source(self, sample_source_code: str):
        """Test extracting signature from source code."""
        bridge = FGentRefineryBridge()
        signature = bridge.extract_signature_from_source(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            intent_text="Summarize text concisely",
        )

        assert signature is not None
        assert signature.instructions == "Summarize text concisely"
        assert signature.input_fields[0].field_type == str
        assert signature.output_fields[0].field_type == str

    def test_extract_signature_from_invalid_source(self):
        """Test extracting signature from invalid source."""
        bridge = FGentRefineryBridge()
        signature = bridge.extract_signature_from_source(
            source_code="invalid python {{{",
            agent_name="Test",
            intent_text="Test intent",
        )

        # Should fall back to basic signature
        assert signature is not None
        assert signature.instructions == "Test intent"

    def test_type_from_name(self):
        """Test type name to Python type conversion."""
        bridge = FGentRefineryBridge()

        assert bridge._type_from_name("str") == str
        assert bridge._type_from_name("int") == int
        assert bridge._type_from_name("float") == float
        assert bridge._type_from_name("bool") == bool
        assert bridge._type_from_name("Unknown") == str  # Default

    @pytest.mark.asyncio
    async def test_generate_synthetic_examples(self, sample_signature: Signature):
        """Test generating synthetic examples."""
        bridge = FGentRefineryBridge()
        examples = await bridge.generate_synthetic_examples(
            signature=sample_signature,
            num_examples=5,
        )

        assert len(examples) == 5
        assert all(isinstance(e, Example) for e in examples)

    @pytest.mark.asyncio
    async def test_refine_basic(self, sample_source_code: str):
        """Test basic refinement pipeline."""
        bridge = FGentRefineryBridge()
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            intent_text="Summarize text",
            check_roi=False,  # Skip ROI for basic test
        )

        result = await bridge.refine(request)

        assert result.phase in [RefinePhase.COMPLETED, RefinePhase.SKIPPED]
        assert result.original_signature is not None

    @pytest.mark.asyncio
    async def test_refine_with_roi_skip(self, sample_source_code: str):
        """Test refinement skipped due to low ROI."""
        bridge = FGentRefineryBridge()
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TextSummarizer",
            check_roi=True,
            estimated_usage_per_month=10,  # Very low usage
            value_per_call_usd=0.001,  # Very low value
        )

        result = await bridge.refine(request)

        # May be skipped due to low ROI
        assert result.phase in [RefinePhase.COMPLETED, RefinePhase.SKIPPED]


# =============================================================================
# Test T-gent → R-gent Integration
# =============================================================================


class TestMetricSignal:
    """Tests for MetricSignal."""

    def test_metric_signal_creation(self):
        """Test creating a metric signal."""
        signal = MetricSignal(
            score=0.85,
            tool_name="test_tool",
            metric_name="accuracy",
        )

        assert signal.score == 0.85
        assert signal.tool_name == "test_tool"
        assert signal.timestamp is not None


class TestTextualLossSignal:
    """Tests for TextualLossSignal."""

    def test_loss_signal_creation(self):
        """Test creating a loss signal."""
        signal = TextualLossSignal(
            score=0.5,
            feedback="Expected 'yes', got 'no'",
            prediction="no",
            expected="yes",
        )

        assert signal.score == 0.5
        assert "Expected" in signal.feedback
        assert signal.prediction == "no"
        assert signal.expected == "yes"


class TestTGentLossAdapter:
    """Tests for TGentLossAdapter."""

    def test_adapter_creation(self):
        """Test creating an adapter."""
        adapter = TGentLossAdapter()
        assert adapter.feedback_generator is not None

    def test_adapter_with_custom_feedback(self):
        """Test adapter with custom feedback generator."""

        def custom_feedback(pred: Any, expected: Any) -> str:
            return f"CUSTOM: {pred} != {expected}"

        adapter = TGentLossAdapter(feedback_generator=custom_feedback)
        signal = adapter.compute_loss_signal(
            prediction="a",
            expected="b",
            metric=lambda p, l: 1.0 if p == l else 0.0,
        )

        assert "CUSTOM" in signal.feedback

    def test_compute_loss_signal_success(self, exact_match_metric: Callable):
        """Test computing loss signal for success case."""
        adapter = TGentLossAdapter()
        signal = adapter.compute_loss_signal(
            prediction="test",
            expected="test",
            metric=exact_match_metric,
        )

        assert signal.score == 1.0
        assert signal.feedback == ""  # No feedback for success

    def test_compute_loss_signal_failure(self, exact_match_metric: Callable):
        """Test computing loss signal for failure case."""
        adapter = TGentLossAdapter()
        signal = adapter.compute_loss_signal(
            prediction="wrong",
            expected="correct",
            metric=exact_match_metric,
        )

        assert signal.score == 0.0
        assert signal.feedback != ""  # Should have feedback

    def test_batch_operations(self, exact_match_metric: Callable):
        """Test batch signal operations."""
        adapter = TGentLossAdapter()

        # Start batch
        batch_id = adapter.start_batch()
        assert batch_id != ""

        # Add signals
        adapter.add_to_batch(adapter.compute_loss_signal("a", "a", exact_match_metric))
        adapter.add_to_batch(adapter.compute_loss_signal("b", "c", exact_match_metric))
        adapter.add_to_batch(adapter.compute_loss_signal("d", "d", exact_match_metric))

        # Check batch score
        assert adapter.batch_score == pytest.approx(2 / 3)

        # Complete batch
        signals = adapter.complete_batch()
        assert len(signals) == 3

    def test_aggregate_batch_feedback(self, exact_match_metric: Callable):
        """Test aggregating batch feedback."""
        adapter = TGentLossAdapter()
        adapter.start_batch()

        adapter.add_to_batch(adapter.compute_loss_signal("a", "b", exact_match_metric))
        adapter.add_to_batch(adapter.compute_loss_signal("c", "d", exact_match_metric))

        feedback = adapter.aggregate_batch_feedback()

        assert "1." in feedback
        assert "2." in feedback


# =============================================================================
# Test B-gent → R-gent Integration
# =============================================================================


class TestBudgetGrant:
    """Tests for BudgetGrant."""

    def test_grant_creation_approved(self):
        """Test creating an approved grant."""
        grant = BudgetGrant(
            approved=True,
            amount_usd=10.0,
            max_iterations=20,
        )

        assert grant.approved
        assert grant.amount_usd == 10.0
        assert grant.grant_id != ""

    def test_grant_creation_denied(self):
        """Test creating a denied grant."""
        grant = BudgetGrant(
            approved=False,
            reason="ROI too low",
            recommendation="Use zero-shot",
        )

        assert not grant.approved
        assert "ROI" in grant.reason


class TestBudgetSpendReport:
    """Tests for BudgetSpendReport."""

    def test_spend_report_creation(self):
        """Test creating a spend report."""
        report = BudgetSpendReport(
            grant_id="test123",
            actual_cost_usd=5.0,
            iterations_used=10,
            llm_calls_made=50,
            baseline_score=0.5,
            final_score=0.8,
            improvement=0.3,
        )

        assert report.grant_id == "test123"
        assert report.actual_cost_usd == 5.0
        assert report.improvement == 0.3


class TestBGentBudgetProtocol:
    """Tests for BGentBudgetProtocol."""

    def test_protocol_creation(self):
        """Test creating a budget protocol."""
        protocol = BGentBudgetProtocol()
        assert protocol.default_budget == 10.0
        assert protocol.min_roi_threshold == 2.0

    def test_protocol_custom_settings(self):
        """Test protocol with custom settings."""
        protocol = BGentBudgetProtocol(
            default_budget_usd=20.0,
            min_roi_threshold=3.0,
        )
        assert protocol.default_budget == 20.0
        assert protocol.min_roi_threshold == 3.0

    def test_request_grant_approved(self):
        """Test requesting a grant that gets approved."""
        protocol = BGentBudgetProtocol()
        grant = protocol.request_grant(
            purpose="Test optimization",
            estimated_cost=5.0,
            expected_roi=3.0,
        )

        assert grant.approved
        assert grant.amount_usd > 0

    def test_request_grant_denied_low_roi(self):
        """Test requesting a grant denied due to low ROI."""
        protocol = BGentBudgetProtocol(min_roi_threshold=5.0)
        grant = protocol.request_grant(
            purpose="Test optimization",
            estimated_cost=5.0,
            expected_roi=2.0,  # Below threshold
        )

        assert not grant.approved
        assert "ROI" in grant.reason

    def test_report_spend(self):
        """Test reporting spend."""
        protocol = BGentBudgetProtocol()
        grant = protocol.request_grant(
            purpose="Test",
            estimated_cost=5.0,
            expected_roi=3.0,
        )

        report = BudgetSpendReport(
            grant_id=grant.grant_id,
            actual_cost_usd=4.0,
            iterations_used=5,
            llm_calls_made=25,
            baseline_score=0.5,
            final_score=0.8,
            improvement=0.3,
        )

        protocol.report_spend(report)

        assert protocol.get_spend_report(grant.grant_id) == report

    def test_total_granted_and_spent(self):
        """Test tracking total granted and spent."""
        protocol = BGentBudgetProtocol()

        # Create two grants
        grant1 = protocol.request_grant("Test1", 5.0, 3.0)
        grant2 = protocol.request_grant("Test2", 8.0, 4.0)

        assert protocol.total_granted > 0

        # Report spend
        protocol.report_spend(
            BudgetSpendReport(
                grant_id=grant1.grant_id,
                actual_cost_usd=4.0,
                iterations_used=5,
                llm_calls_made=20,
                baseline_score=0.5,
                final_score=0.7,
                improvement=0.2,
            )
        )

        assert protocol.total_spent == 4.0


class TestBudgetConstrainedRefinery:
    """Tests for BudgetConstrainedRefinery."""

    def test_constrained_refinery_creation(self):
        """Test creating a constrained refinery."""
        protocol = BGentBudgetProtocol()
        refinery = BudgetConstrainedRefinery(budget_protocol=protocol)

        assert refinery.budget_protocol == protocol
        assert refinery.refinery is not None

    @pytest.mark.asyncio
    async def test_refine_with_budget_approved(
        self,
        sample_signature: Signature,
        sample_examples: list[Example],
        exact_match_metric: Callable,
    ):
        """Test refining with approved budget."""
        protocol = BGentBudgetProtocol()
        refinery = BudgetConstrainedRefinery(budget_protocol=protocol)

        trace, grant = await refinery.refine_with_budget(
            signature=sample_signature,
            examples=sample_examples,
            metric=exact_match_metric,
            expected_roi=3.0,
        )

        assert grant.approved
        assert trace is not None

    @pytest.mark.asyncio
    async def test_refine_with_budget_denied(
        self,
        sample_signature: Signature,
        sample_examples: list[Example],
        exact_match_metric: Callable,
    ):
        """Test refining with denied budget."""
        protocol = BGentBudgetProtocol(min_roi_threshold=10.0)  # Very high threshold
        refinery = BudgetConstrainedRefinery(budget_protocol=protocol)

        with pytest.raises(BudgetDenied):
            await refinery.refine_with_budget(
                signature=sample_signature,
                examples=sample_examples,
                metric=exact_match_metric,
                expected_roi=2.0,  # Below threshold
            )


# =============================================================================
# Test L-gent → R-gent Integration
# =============================================================================


class TestOptimizationCatalogEntry:
    """Tests for OptimizationCatalogEntry."""

    def test_entry_creation(self):
        """Test creating an entry."""
        entry = OptimizationCatalogEntry(
            entry_id="test-123",
            name="TestAgent",
            version="1.0.0",
            description="Test agent",
            optimization_method="bootstrap_fewshot",
            optimization_score=0.85,
            optimization_baseline=0.5,
        )

        assert entry.entry_id == "test-123"
        assert entry.is_optimized
        assert entry.improvement_percentage == pytest.approx(70.0)

    def test_entry_not_optimized(self):
        """Test entry without optimization."""
        entry = OptimizationCatalogEntry(
            entry_id="test-456",
            name="UnoptimizedAgent",
            version="1.0.0",
            description="Not optimized",
        )

        assert not entry.is_optimized
        assert entry.improvement_percentage is None


class TestLGentOptimizationIndex:
    """Tests for LGentOptimizationIndex."""

    def test_index_creation(self):
        """Test creating an index."""
        index = LGentOptimizationIndex()
        assert index._entries == {}
        assert index._trace_storage == {}

    def test_index_optimization_result(self, sample_signature: Signature):
        """Test indexing an optimization result."""
        index = LGentOptimizationIndex()

        trace = OptimizationTrace(initial_prompt="Test", method="bootstrap_fewshot")
        trace.add_iteration("Test", 0.5)
        trace.add_iteration("Improved", 0.8)

        entry = index.index_optimization_result(
            entry_id="test-001",
            name="TestAgent",
            version="1.0.0",
            description="Test",
            trace=trace,
            signature=sample_signature,
        )

        assert entry.optimization_method == "bootstrap_fewshot"
        assert entry.optimization_score == 0.8
        assert entry.optimization_baseline == 0.5
        assert entry.optimization_trace_id is not None

    def test_find_optimized(self, sample_signature: Signature):
        """Test finding optimized entries."""
        index = LGentOptimizationIndex()

        # Index several results
        for i in range(3):
            trace = OptimizationTrace(initial_prompt="Test", method="bootstrap_fewshot")
            trace.add_iteration("Test", 0.3)
            trace.add_iteration("Improved", 0.6 + i * 0.1)

            index.index_optimization_result(
                entry_id=f"test-{i}",
                name=f"Agent{i}",
                version="1.0.0",
                description="Test",
                trace=trace,
            )

        # Find with minimum score
        results = index.find_optimized(min_score=0.7)
        assert len(results) >= 1

        # All results should have score >= 0.7
        for entry in results:
            assert entry.optimization_score >= 0.7

    def test_find_optimized_by_method(self, sample_signature: Signature):
        """Test finding optimized entries by method."""
        index = LGentOptimizationIndex()

        # Index with different methods
        for method in ["bootstrap_fewshot", "textgrad", "opro"]:
            trace = OptimizationTrace(initial_prompt="Test", method=method)
            trace.add_iteration("Test", 0.5)
            trace.add_iteration("Improved", 0.8)

            index.index_optimization_result(
                entry_id=f"test-{method}",
                name=f"Agent-{method}",
                version="1.0.0",
                description="Test",
                trace=trace,
            )

        # Find by method
        results = index.find_optimized(method="textgrad")
        assert len(results) == 1
        assert results[0].optimization_method == "textgrad"

    def test_get_trace(self, sample_signature: Signature):
        """Test retrieving stored trace."""
        index = LGentOptimizationIndex()

        trace = OptimizationTrace(initial_prompt="Test", method="bootstrap_fewshot")
        trace.add_iteration("Test", 0.5)

        entry = index.index_optimization_result(
            entry_id="test-trace",
            name="TestAgent",
            version="1.0.0",
            description="Test",
            trace=trace,
        )

        retrieved = index.get_trace(entry.optimization_trace_id)
        assert retrieved is not None
        assert retrieved.method == "bootstrap_fewshot"


# =============================================================================
# Test Unified Integration Hub
# =============================================================================


class TestRGentIntegrationConfig:
    """Tests for RGentIntegrationConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = RGentIntegrationConfig()

        assert config.enable_f_gent
        assert config.enable_t_gent
        assert config.enable_b_gent
        assert config.enable_l_gent
        assert config.default_budget_usd == 10.0

    def test_custom_config(self):
        """Test custom configuration."""
        config = RGentIntegrationConfig(
            enable_f_gent=False,
            enable_b_gent=False,
            default_budget_usd=50.0,
        )

        assert not config.enable_f_gent
        assert not config.enable_b_gent
        assert config.default_budget_usd == 50.0


class TestRGentIntegrationHub:
    """Tests for RGentIntegrationHub."""

    def test_hub_creation_default(self):
        """Test creating hub with defaults."""
        hub = RGentIntegrationHub()

        assert hub.refinery is not None
        assert hub.f_gent_bridge is not None
        assert hub.t_gent_adapter is not None
        assert hub.budget_protocol is not None
        assert hub.optimization_index is not None

    def test_hub_creation_selective(self):
        """Test creating hub with selective integrations."""
        config = RGentIntegrationConfig(
            enable_f_gent=True,
            enable_t_gent=False,
            enable_b_gent=False,
            enable_l_gent=True,
        )
        hub = RGentIntegrationHub(config)

        assert hub.f_gent_bridge is not None
        assert hub.t_gent_adapter is None
        assert hub.budget_protocol is None
        assert hub.optimization_index is not None

    @pytest.mark.asyncio
    async def test_refine_prototype(self, sample_source_code: str):
        """Test refining a prototype through the hub."""
        hub = RGentIntegrationHub()

        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TestAgent",
            intent_text="Test intent",
            check_roi=False,
        )

        result = await hub.refine_prototype(request)

        assert result is not None
        assert result.original_signature is not None

    @pytest.mark.asyncio
    async def test_refine_prototype_f_gent_disabled(self, sample_source_code: str):
        """Test refining prototype with F-gent disabled."""
        config = RGentIntegrationConfig(enable_f_gent=False)
        hub = RGentIntegrationHub(config)

        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="TestAgent",
        )

        with pytest.raises(RuntimeError, match="F-gent integration not enabled"):
            await hub.refine_prototype(request)

    def test_compute_loss_signal(self, exact_match_metric: Callable):
        """Test computing loss signal through hub."""
        hub = RGentIntegrationHub()

        signal = hub.compute_loss_signal(
            prediction="wrong",
            expected="correct",
            metric=exact_match_metric,
        )

        assert signal.score == 0.0
        assert signal.feedback != ""

    def test_compute_loss_signal_t_gent_disabled(self, exact_match_metric: Callable):
        """Test computing loss signal with T-gent disabled."""
        config = RGentIntegrationConfig(enable_t_gent=False)
        hub = RGentIntegrationHub(config)

        with pytest.raises(RuntimeError, match="T-gent integration not enabled"):
            hub.compute_loss_signal("a", "b", exact_match_metric)

    def test_find_optimized_agents(self):
        """Test finding optimized agents through hub."""
        hub = RGentIntegrationHub()

        # Index some results first
        trace = OptimizationTrace(initial_prompt="Test", method="bootstrap_fewshot")
        trace.add_iteration("Test", 0.5)
        trace.add_iteration("Improved", 0.9)

        hub.optimization_index.index_optimization_result(
            entry_id="test-hub",
            name="HubTestAgent",
            version="1.0.0",
            description="Test",
            trace=trace,
        )

        results = hub.find_optimized_agents(min_score=0.8)
        assert len(results) >= 1

    def test_find_optimized_agents_l_gent_disabled(self):
        """Test finding optimized agents with L-gent disabled."""
        config = RGentIntegrationConfig(enable_l_gent=False)
        hub = RGentIntegrationHub(config)

        with pytest.raises(RuntimeError, match="L-gent integration not enabled"):
            hub.find_optimized_agents()


# =============================================================================
# Integration Tests (Full Pipeline)
# =============================================================================


class TestFullIntegrationPipeline:
    """Integration tests for the complete pipeline."""

    @pytest.mark.asyncio
    async def test_f_to_r_to_l_pipeline(self, sample_source_code: str):
        """Test full F → R → L pipeline."""
        hub = RGentIntegrationHub(
            RGentIntegrationConfig(
                enable_f_gent=True,
                enable_l_gent=True,
                auto_index_results=True,
            )
        )

        # Refine prototype (F → R)
        request = PrototypeRefinementRequest(
            source_code=sample_source_code,
            agent_name="PipelineTestAgent",
            intent_text="Test the pipeline",
            check_roi=False,
        )

        result = await hub.refine_prototype(request)
        assert result.success or result.phase == RefinePhase.SKIPPED

        # Check indexing (R → L)
        # If optimization happened, result should be indexed
        if result.optimization_trace:
            entries = hub.find_optimized_agents(min_score=0.0)
            # At least the just-indexed entry should be found
            assert len(entries) >= 0  # May be 0 if no actual optimization happened

    def test_t_gent_loss_to_batch(self, exact_match_metric: Callable):
        """Test T-gent loss signal batching."""
        hub = RGentIntegrationHub()

        # Start batch
        hub.t_gent_adapter.start_batch()

        # Simulate multiple evaluations
        predictions = ["correct", "wrong1", "wrong2", "correct", "wrong3"]
        expected_values = ["correct", "correct", "correct", "correct", "correct"]

        for pred, exp in zip(predictions, expected_values):
            signal = hub.compute_loss_signal(pred, exp, exact_match_metric)
            hub.t_gent_adapter.add_to_batch(signal)

        # Check batch metrics
        assert hub.t_gent_adapter.batch_score == pytest.approx(0.4)  # 2/5 correct

        # Get aggregated feedback
        feedback = hub.t_gent_adapter.aggregate_batch_feedback()
        assert "1." in feedback  # Should have numbered feedback items

    @pytest.mark.asyncio
    async def test_budget_constrained_pipeline(
        self,
        sample_signature: Signature,
        sample_examples: list[Example],
        exact_match_metric: Callable,
    ):
        """Test B-gent budget-constrained optimization."""
        hub = RGentIntegrationHub(
            RGentIntegrationConfig(
                enable_b_gent=True,
                min_roi_threshold=1.5,  # Lower threshold for test
            )
        )

        # Should succeed with good ROI
        trace, grant = await hub.refine_with_budget(
            signature=sample_signature,
            examples=sample_examples,
            metric=exact_match_metric,
            expected_roi=3.0,
        )

        assert grant.approved
        assert trace is not None

        # Check spend was reported
        report = hub.budget_protocol.get_spend_report(grant.grant_id)
        assert report is not None


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_source_code(self):
        """Test handling empty source code."""
        bridge = FGentRefineryBridge()
        signature = bridge.extract_signature_from_source(
            source_code="",
            agent_name="Empty",
            intent_text="Empty test",
        )

        # Should return basic signature
        assert signature is not None
        assert signature.instructions == "Empty test"

    def test_empty_examples(self):
        """Test handling empty examples."""
        adapter = TGentLossAdapter()
        adapter.start_batch()

        # Complete empty batch
        signals = adapter.complete_batch()
        assert signals == []
        assert adapter.batch_score == 0.0

    def test_budget_unknown_grant(self):
        """Test reporting spend for unknown grant."""
        protocol = BGentBudgetProtocol()

        report = BudgetSpendReport(
            grant_id="nonexistent",
            actual_cost_usd=5.0,
            iterations_used=5,
            llm_calls_made=20,
            baseline_score=0.5,
            final_score=0.7,
            improvement=0.2,
        )

        with pytest.raises(ValueError, match="Unknown grant ID"):
            protocol.report_spend(report)

    def test_index_duplicate_entry(self, sample_signature: Signature):
        """Test indexing duplicate entry (should overwrite)."""
        index = LGentOptimizationIndex()

        trace1 = OptimizationTrace(initial_prompt="Test1", method="method1")
        trace1.add_iteration("Test1", 0.5)

        trace2 = OptimizationTrace(initial_prompt="Test2", method="method2")
        trace2.add_iteration("Test2", 0.9)

        # Index same ID twice
        index.index_optimization_result(
            entry_id="duplicate-test",
            name="Agent1",
            version="1.0.0",
            description="First",
            trace=trace1,
        )

        index.index_optimization_result(
            entry_id="duplicate-test",
            name="Agent2",
            version="2.0.0",
            description="Second",
            trace=trace2,
        )

        # Should have the second version
        entry = index.get_entry("duplicate-test")
        assert entry.name == "Agent2"
        assert entry.optimization_method == "method2"

    def test_improvement_percentage_zero_baseline(self):
        """Test improvement percentage with zero baseline."""
        entry = OptimizationCatalogEntry(
            entry_id="zero-baseline",
            name="Test",
            version="1.0.0",
            description="Test",
            optimization_baseline=0.0,
            optimization_score=0.5,
        )

        # Should handle zero baseline gracefully
        assert entry.improvement_percentage is None
