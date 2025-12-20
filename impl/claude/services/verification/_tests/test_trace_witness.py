"""
Property-based tests for Trace Witness System.

Tests Properties 7, 17, 19 from design.md:
- Property 7: Trace witness capture as constructive proof
- Property 17: Trace specification compliance
- Property 19: Self-improvement cycle from patterns

Feature: formal-verification-metatheory
"""

from __future__ import annotations

from datetime import datetime

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.verification.contracts import (
    BehavioralPattern,
    ExecutionStep,
    Specification,
    SpecProperty,
    TraceWitnessResult,
    VerificationStatus,
)
from services.verification.trace_witness import EnhancedTraceWitness

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def agent_path_strategy(draw: st.DrawFn) -> str:
    """Generate valid AGENTESE paths."""
    contexts = ["world", "self", "concept", "void", "time"]
    context = draw(st.sampled_from(contexts))

    segments = draw(st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=15),
        min_size=1,
        max_size=3,
    ))

    return f"{context}.{'.'.join(segments)}"


@st.composite
def input_data_strategy(draw: st.DrawFn) -> dict[str, object]:
    """Generate valid input data for trace capture."""
    value = draw(st.one_of(
        st.integers(),
        st.text(min_size=0, max_size=50),
        st.lists(st.integers(), max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=10), st.integers(), max_size=3),
    ))

    return {
        "value": value,
        "type": draw(st.sampled_from(["integer", "string", "list", "dict", "default"])),
        "metadata": draw(st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.text(min_size=0, max_size=20),
            max_size=3,
        )),
    }


@st.composite
def spec_property_strategy(draw: st.DrawFn) -> SpecProperty:
    """Generate specification properties."""
    property_id = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz_",
        min_size=1,
        max_size=20,
    ))
    property_type = draw(st.sampled_from(["invariant", "safety", "liveness", "composition"]))

    return SpecProperty(
        property_id=property_id,
        property_type=property_type,
        formal_statement=f"∀ x: {property_id}(x)",
        natural_language=f"Property {property_id} must hold",
        test_strategy=f"Check {property_id}",
    )


@st.composite
def specification_strategy(draw: st.DrawFn) -> Specification:
    """Generate specifications."""
    spec_id = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=1,
        max_size=20,
    ))

    properties = draw(st.lists(spec_property_strategy(), min_size=0, max_size=5))

    return Specification(
        spec_id=spec_id,
        name=f"Specification {spec_id}",
        version="1.0.0",
        properties=frozenset(properties),
    )


@st.composite
def behavioral_pattern_strategy(draw: st.DrawFn) -> BehavioralPattern:
    """Generate behavioral patterns."""
    pattern_id = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=1,
        max_size=20,
    ))
    pattern_type = draw(st.sampled_from([
        "execution_flow",
        "performance",
        "verification_outcome",
        "error_pattern",
    ]))

    return BehavioralPattern(
        pattern_id=pattern_id,
        pattern_type=pattern_type,
        description=f"Pattern {pattern_id}",
        frequency=draw(st.integers(min_value=1, max_value=100)),
        example_traces=draw(st.lists(
            st.text(min_size=1, max_size=36),
            min_size=0,
            max_size=5,
        )),
        metadata={},
    )


# =============================================================================
# Property 7: Trace Witness Capture
# =============================================================================


class TestTraceWitnessCapture:
    """Tests for Property 7: Trace witness capture as constructive proof."""

    @pytest.mark.asyncio
    @given(agent_path=agent_path_strategy(), input_data=input_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_capture_returns_trace_result(
        self,
        agent_path: str,
        input_data: dict[str, object],
    ) -> None:
        """Property 7.1: Trace capture always returns a TraceWitnessResult."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(agent_path, input_data)

        assert isinstance(result, TraceWitnessResult)
        assert result.witness_id is not None
        assert result.agent_path == agent_path
        assert result.input_data == input_data

    @pytest.mark.asyncio
    @given(agent_path=agent_path_strategy(), input_data=input_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_capture_includes_execution_steps(
        self,
        agent_path: str,
        input_data: dict[str, object],
    ) -> None:
        """Property 7.2: Captured trace includes execution steps."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(agent_path, input_data)

        assert isinstance(result.intermediate_steps, list)
        # Should have at least some execution steps
        assert len(result.intermediate_steps) > 0

        # Each step should have required fields
        for step in result.intermediate_steps:
            assert isinstance(step, ExecutionStep)
            assert step.step_id is not None
            assert step.operation is not None

    @pytest.mark.asyncio
    @given(agent_path=agent_path_strategy(), input_data=input_data_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_capture_records_timing(
        self,
        agent_path: str,
        input_data: dict[str, object],
    ) -> None:
        """Property 7.3: Captured trace records execution timing."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(agent_path, input_data)

        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)

        # Execution time should be recorded (may be None on error)
        if result.verification_status != VerificationStatus.FAILURE:
            assert result.execution_time_ms is not None
            assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_capture_stores_in_corpus(self) -> None:
        """Property 7.4: Captured traces are stored in corpus."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test.capture",
            {"value": "test"},
        )

        assert result.witness_id in witness_system.trace_corpus
        assert witness_system.trace_corpus[result.witness_id] == result


# =============================================================================
# Property 17: Trace Specification Compliance
# =============================================================================


class TestTraceSpecificationCompliance:
    """Tests for Property 17: Trace specification compliance."""

    @pytest.mark.asyncio
    @given(agent_path=agent_path_strategy(), input_data=input_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_verification_with_specification(
        self,
        agent_path: str,
        input_data: dict[str, object],
    ) -> None:
        """Property 17.1: Traces can be verified against specifications."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            agent_path,
            input_data,
            specification_id="test_spec",
        )

        assert result.specification_id == "test_spec"
        assert isinstance(result.properties_verified, list)
        assert isinstance(result.violations_found, list)

    @pytest.mark.asyncio
    async def test_verification_status_determined(self) -> None:
        """Property 17.2: Verification status is correctly determined."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test.verify",
            {"value": "test"},
            specification_id="test_spec",
        )

        assert result.verification_status in [
            VerificationStatus.PENDING,
            VerificationStatus.SUCCESS,
            VerificationStatus.FAILURE,
            VerificationStatus.NEEDS_REVIEW,
        ]

    @pytest.mark.asyncio
    async def test_properties_verified_tracked(self) -> None:
        """Property 17.3: Verified properties are tracked."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test.properties",
            {"value": "test"},
            specification_id="test_spec",
        )

        # Should have verified some properties from the default spec
        if result.verification_status == VerificationStatus.SUCCESS:
            assert len(result.properties_verified) > 0

    @pytest.mark.asyncio
    async def test_violations_include_details(self) -> None:
        """Property 17.4: Violations include detailed information."""
        witness_system = EnhancedTraceWitness()
        # Capture a trace that might have violations
        result = await witness_system.capture_execution_trace(
            "self.test.violations",
            {"value": None},  # Potentially problematic input
            specification_id="test_spec",
        )

        # If there are violations, they should have details
        for violation in result.violations_found:
            assert "type" in violation or "property_id" in violation
            assert "description" in violation


# =============================================================================
# Property 19: Self-Improvement Cycle
# =============================================================================


class TestSelfImprovementCycle:
    """Tests for Property 19: Self-improvement cycle from patterns."""

    @pytest.mark.asyncio
    async def test_behavioral_patterns_extracted(self) -> None:
        """Property 19.1: Behavioral patterns are extracted from traces."""
        witness_system = EnhancedTraceWitness()
        # Capture multiple traces
        for i in range(5):
            await witness_system.capture_execution_trace(
                "self.test.pattern",
                {"value": f"test_{i}"},
            )

        # Should have extracted patterns
        assert len(witness_system.behavioral_patterns) > 0

    @pytest.mark.asyncio
    async def test_pattern_analysis_returns_insights(self) -> None:
        """Property 19.2: Pattern analysis returns actionable insights."""
        witness_system = EnhancedTraceWitness()
        # Capture some traces first
        for i in range(3):
            await witness_system.capture_execution_trace(
                "self.test.analysis",
                {"value": f"test_{i}"},
            )

        analysis = await witness_system.analyze_behavioral_patterns()

        assert isinstance(analysis, dict)
        assert "total_patterns" in analysis
        assert "improvement_suggestions" in analysis

    @pytest.mark.asyncio
    async def test_improvement_suggestions_generated(self) -> None:
        """Property 19.3: Improvement suggestions are generated."""
        witness_system = EnhancedTraceWitness()
        # Capture traces to generate patterns
        for i in range(5):
            await witness_system.capture_execution_trace(
                "self.test.improvements",
                {"value": f"test_{i}"},
            )

        analysis = await witness_system.analyze_behavioral_patterns()

        suggestions = analysis.get("improvement_suggestions", [])
        assert isinstance(suggestions, list)

        # Each suggestion should have required fields
        for suggestion in suggestions:
            assert "type" in suggestion
            assert "title" in suggestion
            assert "description" in suggestion

    @pytest.mark.asyncio
    async def test_pattern_frequency_tracking(self) -> None:
        """Property 19.4: Pattern frequencies are tracked correctly."""
        witness_system = EnhancedTraceWitness()
        # Capture identical traces to increase frequency
        for _ in range(3):
            await witness_system.capture_execution_trace(
                "self.test.frequency",
                {"value": "same_value"},
            )

        # Check that some patterns have frequency > 1
        high_freq_patterns = [
            p for p in witness_system.behavioral_patterns.values()
            if p.frequency > 1
        ]

        # Should have at least one pattern with increased frequency
        assert len(high_freq_patterns) > 0


# =============================================================================
# Trace Corpus Management
# =============================================================================


class TestTraceCorpusManagement:
    """Tests for trace corpus management functionality."""

    @pytest.mark.asyncio
    async def test_corpus_summary_structure(self) -> None:
        """Corpus summary has correct structure."""
        witness_system = EnhancedTraceWitness()
        # Capture some traces
        for i in range(3):
            await witness_system.capture_execution_trace(
                f"self.test.corpus_{i}",
                {"value": f"test_{i}"},
            )

        summary = await witness_system.get_trace_corpus_summary()

        assert isinstance(summary, dict)
        assert "total_traces" in summary
        assert summary["total_traces"] == 3
        assert "status_distribution" in summary
        assert "agent_path_distribution" in summary

    @pytest.mark.asyncio
    async def test_similar_trace_finding(self) -> None:
        """Similar traces can be found."""
        witness_system = EnhancedTraceWitness()
        # Capture similar traces
        result1 = await witness_system.capture_execution_trace(
            "self.test.similar",
            {"value": "test_1"},
        )

        await witness_system.capture_execution_trace(
            "self.test.similar",
            {"value": "test_2"},
        )

        similar = await witness_system.find_similar_traces(result1.witness_id)

        assert isinstance(similar, list)

    @pytest.mark.asyncio
    async def test_empty_corpus_summary(self) -> None:
        """Empty corpus returns valid summary."""
        witness_system = EnhancedTraceWitness()
        summary = await witness_system.get_trace_corpus_summary()

        assert summary["total_traces"] == 0
        assert "No traces captured" in summary.get("summary", "")


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests for trace witness system."""

    @pytest.mark.asyncio
    async def test_empty_input_data(self) -> None:
        """Empty input data is handled."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test.empty",
            {},
        )

        assert result is not None
        assert result.input_data == {}

    @pytest.mark.asyncio
    async def test_special_characters_in_path(self) -> None:
        """Special characters in agent path are handled."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test_agent.special_path",
            {"value": "test"},
        )

        assert result.agent_path == "self.test_agent.special_path"

    @pytest.mark.asyncio
    async def test_nonexistent_specification(self) -> None:
        """Nonexistent specification is handled gracefully."""
        witness_system = EnhancedTraceWitness()
        result = await witness_system.capture_execution_trace(
            "self.test.nonexistent",
            {"value": "test"},
            specification_id="nonexistent_spec_12345",
        )

        # Should still capture the trace
        assert result is not None
        assert result.specification_id == "nonexistent_spec_12345"

    @pytest.mark.asyncio
    async def test_pattern_analysis_by_type(self) -> None:
        """Pattern analysis can filter by type."""
        witness_system = EnhancedTraceWitness()
        # Capture traces
        for i in range(3):
            await witness_system.capture_execution_trace(
                "self.test.type_filter",
                {"value": f"test_{i}"},
            )

        # Analyze specific pattern type
        analysis = await witness_system.analyze_behavioral_patterns(
            pattern_type="execution_flow"
        )

        assert isinstance(analysis, dict)
