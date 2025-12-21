# mypy: ignore-errors
"""
Integration test for the formal verification system.

Tests the complete verification workflow from specification analysis
to categorical law verification to trace witness capture.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from .categorical_checker import CategoricalChecker
from .contracts import AgentMorphism, VerificationStatus
from .graph_engine import GraphEngine
from .semantic_consistency import SemanticConsistencyEngine
from .trace_witness import EnhancedTraceWitness


class TestVerificationIntegration:
    """Integration tests for the verification system."""

    @pytest.fixture
    def sample_morphisms(self):
        """Create sample morphisms for testing."""
        return [
            AgentMorphism(
                morphism_id="f",
                name="Transform F",
                description="Transforms input by applying function F",
                source_type="String",
                target_type="String",
                implementation={"type": "transform", "function": "uppercase"},
            ),
            AgentMorphism(
                morphism_id="g",
                name="Transform G",
                description="Transforms input by applying function G",
                source_type="String",
                target_type="String",
                implementation={"type": "transform", "function": "reverse"},
            ),
            AgentMorphism(
                morphism_id="h",
                name="Transform H",
                description="Transforms input by applying function H",
                source_type="String",
                target_type="String",
                implementation={"type": "transform", "function": "trim"},
            ),
            AgentMorphism(
                morphism_id="id",
                name="Identity",
                description="Identity morphism that returns input unchanged",
                source_type="String",
                target_type="String",
                implementation={"type": "identity"},
            ),
        ]

    @pytest.fixture
    def sample_specification(self):
        """Create a sample specification for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            spec_dir = Path(temp_dir) / "test_spec"
            spec_dir.mkdir()

            # Create requirements.md
            requirements_content = """
# Requirements

## User Stories

- As a developer, I want agents to compose associatively
- As a system, I need identity morphisms to exist

## Acceptance Criteria

- All agent compositions MUST be associative
- Identity morphisms MUST satisfy left and right identity laws
"""
            (spec_dir / "requirements.md").write_text(requirements_content)

            # Create design.md
            design_content = """
# Design

## Architecture

The system uses category theory as its foundation.

## Components

- PolyAgent: State-dependent agent morphisms
- Composition: Associative composition operator
- Identity: Identity morphisms for each type

## Correctness Properties

- Composition associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
- Identity laws: f ∘ id = f and id ∘ f = f
"""
            (spec_dir / "design.md").write_text(design_content)

            # Create tasks.md
            tasks_content = """
# Tasks

- [ ] Implement PolyAgent base class
- [ ] Implement composition operator
- [ ] Implement identity morphisms
- [ ] Add categorical law verification
- [ ] Create test suite
"""
            (spec_dir / "tasks.md").write_text(tasks_content)

            yield str(spec_dir)

    @pytest.mark.asyncio
    async def test_graph_engine_integration(self, sample_specification):
        """Test graph engine with real specification."""

        engine = GraphEngine()

        # Build graph from specification
        result = await engine.build_graph_from_specification(sample_specification)

        # Verify graph structure
        assert result.graph_id is not None
        assert len(result.nodes) > 0
        assert len(result.edges) > 0

        # Should have principle nodes
        principle_nodes = [n for n in result.nodes if n.node_type == "principle"]
        assert len(principle_nodes) == 7  # 7 kgents principles

        # Should have requirement nodes
        requirement_nodes = [n for n in result.nodes if n.node_type == "requirement"]
        assert len(requirement_nodes) > 0

        # Should have derivation paths
        assert len(result.derivation_paths) > 0

        # Status should be determined
        assert result.status in [
            VerificationStatus.SUCCESS,
            VerificationStatus.NEEDS_REVIEW,
            VerificationStatus.FAILURE,
        ]

    @pytest.mark.asyncio
    async def test_categorical_checker_integration(self, sample_morphisms):
        """Test categorical checker with sample morphisms."""

        checker = CategoricalChecker()
        f, g, h, identity = sample_morphisms

        # Test composition associativity
        result = await checker.verify_composition_associativity(f, g, h)

        assert result.law_name == "composition_associativity"
        assert isinstance(result.success, bool)
        assert result.llm_analysis is not None

        # Test identity laws
        identity_result = await checker.verify_identity_laws(f, identity)

        assert identity_result.law_name == "identity_laws"
        assert isinstance(identity_result.success, bool)

        # Test functor laws
        functor_result = await checker.verify_functor_laws(f, g, h)

        # Functor verification may return different law names for different checks
        assert functor_result.law_name in [
            "functor_laws",
            "functor_identity",
            "functor_composition",
        ]
        assert isinstance(functor_result.success, bool)

    @pytest.mark.asyncio
    async def test_counter_example_generation(self, sample_morphisms):
        """Test counter-example generation."""

        checker = CategoricalChecker()
        f, g, h, _ = sample_morphisms

        # Generate counter-examples for composition associativity
        counter_examples = await checker.generate_counter_examples(
            "composition_associativity",
            [f, g, h],
        )

        # Should generate some counter-examples (even if simulated)
        assert isinstance(counter_examples, list)

        # If counter-examples exist, they should have proper structure
        for counter_example in counter_examples:
            assert hasattr(counter_example, "test_input")
            assert hasattr(counter_example, "expected_result")
            assert hasattr(counter_example, "actual_result")
            assert hasattr(counter_example, "morphisms")

    @pytest.mark.asyncio
    async def test_trace_witness_integration(self):
        """Test trace witness system."""

        witness = EnhancedTraceWitness()

        # Capture a trace
        trace_result = await witness.capture_execution_trace(
            agent_path="test.agent.transform",
            input_data={"value": "hello", "type": "string"},
            specification_id="test_spec_1",
        )

        # Verify trace structure
        assert trace_result.witness_id is not None
        assert trace_result.agent_path == "test.agent.transform"
        assert len(trace_result.intermediate_steps) > 0
        assert trace_result.verification_status in [
            VerificationStatus.SUCCESS,
            VerificationStatus.FAILURE,
            VerificationStatus.NEEDS_REVIEW,
            VerificationStatus.PENDING,
        ]

        # Analyze behavioral patterns
        analysis = await witness.analyze_behavioral_patterns()

        assert "total_patterns" in analysis
        assert "pattern_frequencies" in analysis
        assert isinstance(analysis["total_patterns"], int)

    @pytest.mark.asyncio
    async def test_semantic_consistency_integration(self, sample_specification):
        """Test semantic consistency engine."""

        engine = SemanticConsistencyEngine()

        # Create multiple documents for consistency checking
        doc_paths = [
            str(Path(sample_specification) / "requirements.md"),
            str(Path(sample_specification) / "design.md"),
        ]

        # Verify consistency
        result = await engine.verify_cross_document_consistency(doc_paths)

        # Verify result structure
        assert result.document_ids == doc_paths
        assert isinstance(result.consistent, bool)
        assert isinstance(result.conflicts, list)
        assert isinstance(result.cross_references, dict)
        assert isinstance(result.backward_compatible, bool)
        assert isinstance(result.suggestions, list)

    @pytest.mark.asyncio
    async def test_remediation_strategies(self, sample_morphisms):
        """Test remediation strategy generation."""

        checker = CategoricalChecker()
        f, g, h, _ = sample_morphisms

        # Generate counter-examples first
        counter_examples = await checker.generate_counter_examples(
            "composition_associativity",
            [f, g, h],
        )

        # Generate remediation strategies
        strategies = await checker.suggest_remediation_strategies(
            counter_examples,
            "composition_associativity",
        )

        # Verify strategy structure
        assert "strategies" in strategies
        assert isinstance(strategies["strategies"], list)

        if strategies["strategies"]:
            strategy = strategies["strategies"][0]
            assert "type" in strategy
            assert "title" in strategy
            assert "description" in strategy
            assert "priority" in strategy

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, sample_specification, sample_morphisms):
        """Test complete end-to-end verification workflow."""

        # 1. Analyze specification
        graph_engine = GraphEngine()
        graph_result = await graph_engine.build_graph_from_specification(sample_specification)

        assert graph_result.status is not None

        # 2. Verify categorical laws
        checker = CategoricalChecker()
        f, g, h, identity = sample_morphisms

        comp_result = await checker.verify_composition_associativity(f, g, h)
        id_result = await checker.verify_identity_laws(f, identity)

        assert comp_result.law_name == "composition_associativity"
        assert id_result.law_name == "identity_laws"

        # 3. Capture trace witness
        witness = EnhancedTraceWitness()
        trace_result = await witness.capture_execution_trace(
            agent_path="test.workflow.agent",
            input_data={"value": "test_input"},
        )

        assert trace_result.witness_id is not None

        # 4. Analyze patterns and generate improvements
        pattern_analysis = await witness.analyze_behavioral_patterns()

        assert "total_patterns" in pattern_analysis

        # 5. Check semantic consistency
        semantic_engine = SemanticConsistencyEngine()
        doc_paths = [
            str(Path(sample_specification) / "requirements.md"),
            str(Path(sample_specification) / "design.md"),
        ]

        consistency_result = await semantic_engine.verify_cross_document_consistency(doc_paths)

        assert consistency_result.document_ids == doc_paths

        # Workflow completed successfully
        assert True  # If we get here, the entire workflow worked


if __name__ == "__main__":
    # Run a simple test
    async def main():
        test = TestVerificationIntegration()

        # Create sample morphisms
        morphisms = [
            AgentMorphism(
                morphism_id="test_f",
                name="Test F",
                description="Test morphism F",
                source_type="String",
                target_type="String",
                implementation={"type": "transform"},
            ),
            AgentMorphism(
                morphism_id="test_g",
                name="Test G",
                description="Test morphism G",
                source_type="String",
                target_type="String",
                implementation={"type": "transform"},
            ),
            AgentMorphism(
                morphism_id="test_h",
                name="Test H",
                description="Test morphism H",
                source_type="String",
                target_type="String",
                implementation={"type": "transform"},
            ),
        ]

        # Test categorical checker
        checker = CategoricalChecker()
        result = await checker.verify_composition_associativity(
            morphisms[0], morphisms[1], morphisms[2]
        )

        print(f"Composition associativity test: {result.success}")
        print(f"Analysis: {result.llm_analysis}")

        # Test trace witness
        witness = EnhancedTraceWitness()
        trace = await witness.capture_execution_trace("test.agent", {"value": "hello"})

        print(f"Trace captured: {trace.witness_id}")
        print(f"Status: {trace.verification_status}")

        print("✅ Basic verification system test completed!")

    asyncio.run(main())
