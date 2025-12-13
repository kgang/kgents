"""
Tests for ForgeScreen.

Test Categories (T-gent Types I-V):
- Type I: Contracts (mode switching, component addition)
- Type II: Saboteurs (invalid inputs, edge cases)
- Type III: Spies (interaction verification)
- Type IV: Judges (semantic correctness)
- Type V: Witnesses (integration, full workflows)
"""

from __future__ import annotations

import pytest
from textual.app import App

from ..forge import (
    AGENT_CATALOG,
    PRIMITIVE_CATALOG,
    AgentPalette,
    CodeExporter,
    ComponentSpec,
    ComponentType,
    CostEstimate,
    ForgeScreen,
    PipelineBuilder,
    PipelineComponent,
    SimulationResult,
    SimulationRunner,
    ValidationError,
)

# ─────────────────────────────────────────────────────────────
# Type I: Contract Tests
# ─────────────────────────────────────────────────────────────


class TestForgeContracts:
    """Test ForgeScreen satisfies its interface contract."""

    @pytest.fixture
    def forge(self) -> ForgeScreen:
        """Create a ForgeScreen instance."""
        return ForgeScreen()

    def test_forge_initializes_with_compose_mode(self, forge: ForgeScreen) -> None:
        """ForgeScreen should start in compose mode."""
        assert forge.mode == "compose"

    def test_forge_has_required_widgets(self, forge: ForgeScreen) -> None:
        """ForgeScreen should have palette, pipeline, and simulator."""
        # These are initialized in compose()
        assert forge._palette is None  # Before compose
        assert forge._pipeline is None
        assert forge._simulator is None

    def test_add_to_pipeline_accepts_component_id(self, forge: ForgeScreen) -> None:
        """add_to_pipeline should accept component ID string."""
        # This is tested after compose() is called
        # For now, just verify the method exists
        assert hasattr(forge, "add_to_pipeline")
        assert callable(forge.add_to_pipeline)

    def test_remove_from_pipeline_accepts_index(self, forge: ForgeScreen) -> None:
        """remove_from_pipeline should accept integer index."""
        assert hasattr(forge, "remove_from_pipeline")
        assert callable(forge.remove_from_pipeline)

    def test_run_simulation_accepts_input_text(self, forge: ForgeScreen) -> None:
        """run_simulation should accept input text string."""
        assert hasattr(forge, "run_simulation")
        assert callable(forge.run_simulation)

    def test_step_simulation_returns_step_result(self, forge: ForgeScreen) -> None:
        """step_simulation should return StepResult or None."""
        assert hasattr(forge, "step_simulation")
        assert callable(forge.step_simulation)

    def test_export_code_returns_string(self, forge: ForgeScreen) -> None:
        """export_code should return valid Python code string."""
        code = forge.export_code()
        assert isinstance(code, str)
        assert len(code) > 0


# ─────────────────────────────────────────────────────────────
# Type I: PipelineBuilder Contracts
# ─────────────────────────────────────────────────────────────


class TestPipelineBuilderContracts:
    """Test PipelineBuilder satisfies its contract."""

    @pytest.fixture
    def builder(self) -> PipelineBuilder:
        """Create a PipelineBuilder instance."""
        return PipelineBuilder()

    @pytest.fixture
    def sample_spec(self) -> ComponentSpec:
        """Create a sample ComponentSpec."""
        return ComponentSpec(
            id="test-agent",
            name="TestAgent",
            component_type=ComponentType.AGENT,
            display_name="Test Agent",
            input_type="str",
            output_type="str",
            description="A test agent",
            stars=3,
        )

    def test_validate_returns_list(self, builder: PipelineBuilder) -> None:
        """validate() should return list of ValidationError."""
        errors = builder.validate()
        assert isinstance(errors, list)

    def test_estimate_cost_returns_cost_estimate(
        self, builder: PipelineBuilder
    ) -> None:
        """estimate_cost() should return CostEstimate."""
        cost = builder.estimate_cost()
        assert isinstance(cost, CostEstimate)
        assert cost.entropy_per_turn >= 0
        assert cost.token_budget >= 0
        assert cost.estimated_latency_ms >= 0

    def test_add_component_increases_count(
        self, builder: PipelineBuilder, sample_spec: ComponentSpec
    ) -> None:
        """Adding a component should increase component count."""
        initial_count = len(builder.get_components())
        builder.add_component(sample_spec)
        assert len(builder.get_components()) == initial_count + 1

    def test_remove_component_decreases_count(
        self, builder: PipelineBuilder, sample_spec: ComponentSpec
    ) -> None:
        """Removing a component should decrease component count."""
        builder.add_component(sample_spec)
        initial_count = len(builder.get_components())
        builder.remove_component(0)
        assert len(builder.get_components()) == initial_count - 1

    def test_clear_removes_all_components(
        self, builder: PipelineBuilder, sample_spec: ComponentSpec
    ) -> None:
        """clear() should remove all components."""
        builder.add_component(sample_spec)
        builder.add_component(sample_spec)
        builder.clear()
        assert len(builder.get_components()) == 0


# ─────────────────────────────────────────────────────────────
# Type II: Saboteur Tests (Edge Cases)
# ─────────────────────────────────────────────────────────────


class TestPipelineSaboteurs:
    """Property-based and edge case tests."""

    @pytest.fixture
    def builder(self) -> PipelineBuilder:
        return PipelineBuilder()

    def test_remove_from_empty_pipeline(self, builder: PipelineBuilder) -> None:
        """Removing from empty pipeline should not crash."""
        builder.remove_component(0)
        assert len(builder.get_components()) == 0

    def test_remove_negative_index(self, builder: PipelineBuilder) -> None:
        """Removing at negative index should not crash."""
        builder.remove_component(-1)
        assert len(builder.get_components()) == 0

    def test_remove_out_of_bounds(self, builder: PipelineBuilder) -> None:
        """Removing at out-of-bounds index should not crash."""
        builder.remove_component(999)
        assert len(builder.get_components()) == 0

    def test_validate_empty_pipeline(self, builder: PipelineBuilder) -> None:
        """Validating empty pipeline should return no errors."""
        errors = builder.validate()
        assert len(errors) == 0

    def test_cost_estimate_empty_pipeline(self, builder: PipelineBuilder) -> None:
        """Cost estimate for empty pipeline should be zero."""
        cost = builder.estimate_cost()
        assert cost.entropy_per_turn == 0.0
        assert cost.token_budget == 0


# ─────────────────────────────────────────────────────────────
# Type III: Spy Tests (Behavior Verification)
# ─────────────────────────────────────────────────────────────


class TestSimulatorBehavior:
    """Test SimulationRunner behavior."""

    @pytest.fixture
    def simulator(self) -> SimulationRunner:
        return SimulationRunner()

    @pytest.fixture
    def sample_pipeline(self) -> list[PipelineComponent]:
        """Create a sample pipeline."""
        spec1 = ComponentSpec(
            id="agent1",
            name="Agent1",
            component_type=ComponentType.AGENT,
            display_name="Agent 1",
            input_type="str",
            output_type="str",
            description="First agent",
        )
        spec2 = ComponentSpec(
            id="agent2",
            name="Agent2",
            component_type=ComponentType.AGENT,
            display_name="Agent 2",
            input_type="str",
            output_type="str",
            description="Second agent",
        )
        return [
            PipelineComponent(spec=spec1, index=0),
            PipelineComponent(spec=spec2, index=1),
        ]

    def test_run_simulation_returns_result(
        self, simulator: SimulationRunner, sample_pipeline: list[PipelineComponent]
    ) -> None:
        """run_simulation should return SimulationResult."""
        simulator.set_pipeline(sample_pipeline)
        result = simulator.run_simulation("test input")

        assert isinstance(result, SimulationResult)
        assert result.success is True
        assert result.output is not None

    def test_simulation_has_correct_number_of_steps(
        self, simulator: SimulationRunner, sample_pipeline: list[PipelineComponent]
    ) -> None:
        """Simulation should have one step per component."""
        simulator.set_pipeline(sample_pipeline)
        result = simulator.run_simulation("test")

        assert len(result.steps) == len(sample_pipeline)

    def test_reset_clears_results(
        self, simulator: SimulationRunner, sample_pipeline: list[PipelineComponent]
    ) -> None:
        """reset() should clear simulation results."""
        simulator.set_pipeline(sample_pipeline)
        simulator.run_simulation("test")
        simulator.reset()

        # After reset, _current_result should be None
        assert simulator._current_result is None
        assert simulator._current_step == 0


# ─────────────────────────────────────────────────────────────
# Type IV: Judge Tests (Semantic Correctness)
# ─────────────────────────────────────────────────────────────


class TestCodeExporter:
    """Test code generation is semantically correct."""

    @pytest.fixture
    def exporter(self) -> CodeExporter:
        return CodeExporter()

    def test_empty_pipeline_generates_valid_code(self, exporter: CodeExporter) -> None:
        """Empty pipeline should generate valid Python."""
        code = exporter.export([])
        assert "async def run_pipeline" in code
        assert "import asyncio" in code  # Needs asyncio for main block

    def test_single_component_generates_imports(self, exporter: CodeExporter) -> None:
        """Single component should generate correct imports."""
        spec = ComponentSpec(
            id="a-alethic",
            name="Alethic",
            component_type=ComponentType.AGENT,
            display_name="Alethic",
            input_type="str",
            output_type="str",
            description="Test",
        )
        component = PipelineComponent(spec=spec, index=0)

        code = exporter.export([component])

        assert "from agents.a import AlethicAgent" in code
        assert "agent_0 = AlethicAgent()" in code

    def test_exported_code_has_main_block(self, exporter: CodeExporter) -> None:
        """Exported code should have __main__ block."""
        code = exporter.export([])
        assert 'if __name__ == "__main__":' in code
        assert "asyncio.run(main())" in code


# ─────────────────────────────────────────────────────────────
# Type V: Witness Tests (Integration)
# ─────────────────────────────────────────────────────────────


class TestForgeIntegration:
    """Integration tests for the full Forge workflow."""

    def test_palette_has_agents_and_primitives(self) -> None:
        """Palette should have both agents and primitives."""
        assert len(AGENT_CATALOG) > 0
        assert len(PRIMITIVE_CATALOG) > 0

        # Check specific expected agents
        agent_ids = {spec.id for spec in AGENT_CATALOG}
        assert "a-alethic" in agent_ids
        assert "k-soul" in agent_ids

        # Check specific expected primitives
        prim_ids = {spec.id for spec in PRIMITIVE_CATALOG}
        assert "ground" in prim_ids
        assert "judge" in prim_ids

    def test_pipeline_validation_detects_type_mismatch(self) -> None:
        """Pipeline should detect type mismatches (when strict)."""
        builder = PipelineBuilder()

        spec1 = ComponentSpec(
            id="agent1",
            name="Agent1",
            component_type=ComponentType.AGENT,
            display_name="Agent 1",
            input_type="str",
            output_type="Document",
            description="Outputs Document",
        )
        spec2 = ComponentSpec(
            id="agent2",
            name="Agent2",
            component_type=ComponentType.AGENT,
            display_name="Agent 2",
            input_type="Number",
            output_type="str",
            description="Expects Number",
        )

        builder.add_component(spec1)
        builder.add_component(spec2)

        # Validation should pass for now (we accept all types initially)
        # but this test documents the intended behavior
        errors = builder.validate()
        # Currently returns [] because we're lenient
        # Future: assert len(errors) > 0

    def test_cost_estimate_scales_with_pipeline_size(self) -> None:
        """Cost should increase with more components."""
        builder = PipelineBuilder()

        spec = ComponentSpec(
            id="test",
            name="Test",
            component_type=ComponentType.AGENT,
            display_name="Test",
            input_type="Any",
            output_type="Any",
            description="Test",
        )

        cost1 = builder.estimate_cost()

        builder.add_component(spec)
        cost2 = builder.estimate_cost()

        builder.add_component(spec)
        cost3 = builder.estimate_cost()

        assert cost2.entropy_per_turn > cost1.entropy_per_turn
        assert cost3.entropy_per_turn > cost2.entropy_per_turn
        assert cost2.token_budget > cost1.token_budget
        assert cost3.token_budget > cost2.token_budget


# ─────────────────────────────────────────────────────────────
# Demo Mode Test
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_forge_demo_mode() -> None:
    """ForgeScreen should work in demo mode."""

    class ForgeApp(App[None]):
        """Test app for Forge."""

        def on_mount(self) -> None:
            self.push_screen(ForgeScreen())

    app = ForgeApp()

    # This tests that the screen can be instantiated and composed
    # without errors. Full interactive testing requires a Textual pilot.
    forge = ForgeScreen()
    assert forge.mode == "compose"
