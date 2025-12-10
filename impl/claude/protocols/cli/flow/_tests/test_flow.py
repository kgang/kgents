"""
Tests for Flow Engine - Phase 3 of CLI Integration.

Tests cover:
- Flowfile types and serialization
- YAML parsing with Jinja2 templates
- Flow execution engine
- CLI commands
"""

from __future__ import annotations

import pytest
from datetime import datetime

from ..types import (
    FlowStep,
    FlowInput,
    Flowfile,
    FlowResult,
    StepResult,
    FlowStatus,
    StepStatus,
    FlowValidationError,
)
from ..parser import (
    render_template,
    render_flowfile,
    parse_flowfile_string,
    validate_flowfile,
    build_dependency_graph,
    topological_sort,
    visualize_flow,
    explain_flow,
)
from ..engine import (
    FlowEngine,
    evaluate_condition,
)


# =============================================================================
# Test: FlowStep
# =============================================================================


class TestFlowStep:
    """Tests for FlowStep dataclass."""

    def test_create_minimal(self):
        """Create a minimal step."""
        step = FlowStep(id="parse", genus="P-gent", operation="extract")
        assert step.id == "parse"
        assert step.genus == "P-gent"
        assert step.operation == "extract"
        assert step.input is None
        assert step.args == {}

    def test_create_with_all_fields(self):
        """Create step with all fields."""
        step = FlowStep(
            id="judge",
            genus="Bootstrap",
            operation="judge",
            input="from:parse",
            args={"principles": "spec/principles.md"},
            condition="parse.success",
            on_error="continue",
            timeout_ms=5000,
            debug=True,
        )
        assert step.input == "from:parse"
        assert step.args["principles"] == "spec/principles.md"
        assert step.condition == "parse.success"
        assert step.debug is True

    def test_to_dict(self):
        """Convert step to dict."""
        step = FlowStep(id="test", genus="T-gent", operation="verify")
        d = step.to_dict()
        assert d["id"] == "test"
        assert d["genus"] == "T-gent"
        assert d["operation"] == "verify"

    def test_from_dict(self):
        """Create step from dict."""
        data = {
            "id": "parse",
            "genus": "P-gent",
            "operation": "extract",
            "debug": True,
        }
        step = FlowStep.from_dict(data)
        assert step.id == "parse"
        assert step.debug is True

    def test_round_trip(self):
        """Dict round-trip preserves data."""
        step = FlowStep(
            id="refine",
            genus="R-gent",
            operation="optimize",
            input="from:judge",
            args={"iterations": 3},
        )
        restored = FlowStep.from_dict(step.to_dict())
        assert restored.id == step.id
        assert restored.genus == step.genus
        assert restored.input == step.input
        assert restored.args == step.args


# =============================================================================
# Test: Flowfile
# =============================================================================


class TestFlowfile:
    """Tests for Flowfile dataclass."""

    def test_create_minimal(self):
        """Create minimal flowfile."""
        flow = Flowfile(
            name="Test Flow",
            steps=[FlowStep(id="step1", genus="P-gent", operation="extract")],
        )
        assert flow.name == "Test Flow"
        assert len(flow.steps) == 1

    def test_to_dict(self):
        """Convert flowfile to dict."""
        flow = Flowfile(
            version="1.0",
            name="Review Pipeline",
            description="Parse and judge code",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(
                    id="judge", genus="Bootstrap", operation="judge", input="from:parse"
                ),
            ],
        )
        d = flow.to_dict()
        assert d["version"] == "1.0"
        assert d["name"] == "Review Pipeline"
        assert len(d["steps"]) == 2

    def test_from_dict(self):
        """Create flowfile from dict."""
        data = {
            "version": "1.0",
            "name": "Test",
            "steps": [
                {"id": "s1", "genus": "P-gent", "operation": "extract"},
            ],
        }
        flow = Flowfile.from_dict(data)
        assert flow.name == "Test"
        assert len(flow.steps) == 1

    def test_input_config(self):
        """Input configuration parsing."""
        data = {
            "name": "Test",
            "input": {
                "type": "file",
                "extensions": [".py", ".js"],
            },
            "steps": [{"id": "s", "genus": "P-gent", "operation": "extract"}],
        }
        flow = Flowfile.from_dict(data)
        assert flow.input.type == "file"
        assert ".py" in flow.input.extensions

    def test_output_config(self):
        """Output configuration parsing."""
        data = {
            "name": "Test",
            "output": {
                "format": "json",
                "save_to": ".kgents/artifacts/",
            },
            "steps": [{"id": "s", "genus": "P-gent", "operation": "extract"}],
        }
        flow = Flowfile.from_dict(data)
        assert flow.output.format == "json"
        assert flow.output.save_to == ".kgents/artifacts/"


# =============================================================================
# Test: Template Rendering
# =============================================================================


class TestTemplateRendering:
    """Tests for Jinja2 template rendering."""

    def test_simple_variable(self):
        """Render simple variable."""
        result = render_template("Hello {{ name }}", {"name": "World"})
        assert result == "Hello World"

    def test_default_value(self):
        """Render with default value."""
        result = render_template("Level: {{ strictness | default('high') }}", {})
        assert result == "Level: high"

    def test_override_default(self):
        """Override default value."""
        result = render_template(
            "Level: {{ strictness | default('high') }}", {"strictness": "low"}
        )
        assert result == "Level: low"

    def test_multiple_variables(self):
        """Render multiple variables."""
        template = "{{ action }} {{ target }} with {{ tool }}"
        result = render_template(
            template,
            {
                "action": "parse",
                "target": "code",
                "tool": "P-gent",
            },
        )
        assert result == "parse code with P-gent"

    def test_render_flowfile_args(self):
        """Render flowfile step args."""
        flow = Flowfile(
            name="Test",
            variables={"strictness": "{{ strictness | default('high') }}"},
            steps=[
                FlowStep(
                    id="judge",
                    genus="Bootstrap",
                    operation="judge",
                    args={"level": "{{ strictness }}"},
                )
            ],
        )
        rendered = render_flowfile(flow, {"strictness": "medium"})
        assert rendered.steps[0].args["level"] == "medium"


# =============================================================================
# Test: YAML Parsing
# =============================================================================


class TestYAMLParsing:
    """Tests for YAML flowfile parsing."""

    @pytest.fixture
    def sample_yaml(self):
        return """
version: "1.0"
name: "Code Review Pipeline"
description: "Parse, judge, and refine code"

input:
  type: file
  extensions: [.py, .js, .ts]

variables:
  strictness: "{{ strictness | default('high') }}"

steps:
  - id: parse
    genus: P-gent
    operation: extract
    debug: true

  - id: judge
    genus: Bootstrap
    operation: judge
    input: "from:parse"
    args:
      principles: "spec/principles.md"
      strictness: "{{ strictness }}"

  - id: refine
    genus: R-gent
    operation: optimize
    input: "from:judge"
    condition: "judge.verdict != 'APPROVED'"
    on_error: continue

output:
  format: rich
  save_to: ".kgents/artifacts/"

on_error:
  strategy: halt
"""

    def test_parse_sample_yaml(self, sample_yaml):
        """Parse complete YAML flowfile."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        flow = parse_flowfile_string(sample_yaml, "test.yaml")
        assert flow.name == "Code Review Pipeline"
        assert len(flow.steps) == 3
        assert flow.steps[0].id == "parse"
        assert flow.steps[0].debug is True
        assert flow.steps[1].input == "from:parse"
        assert flow.steps[2].condition == "judge.verdict != 'APPROVED'"

    def test_parse_minimal_yaml(self):
        """Parse minimal YAML."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        yaml_content = """
name: "Minimal"
steps:
  - id: step1
    genus: P-gent
    operation: extract
"""
        flow = parse_flowfile_string(yaml_content)
        assert flow.name == "Minimal"
        assert len(flow.steps) == 1


# =============================================================================
# Test: Validation
# =============================================================================


class TestValidation:
    """Tests for flowfile validation."""

    def test_valid_flowfile(self):
        """Valid flowfile passes validation."""
        flow = Flowfile(
            name="Valid",
            steps=[
                FlowStep(id="s1", genus="P-gent", operation="extract"),
                FlowStep(
                    id="s2", genus="Bootstrap", operation="judge", input="from:s1"
                ),
            ],
        )
        errors = validate_flowfile(flow)
        assert errors == []

    def test_empty_steps(self):
        """Empty steps fails validation."""
        flow = Flowfile(name="Empty", steps=[])
        errors = validate_flowfile(flow)
        assert any("at least one step" in e for e in errors)

    def test_duplicate_step_ids(self):
        """Duplicate step IDs fail validation."""
        flow = Flowfile(
            name="Dupe",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(id="parse", genus="P-gent", operation="repair"),  # Duplicate
            ],
        )
        errors = validate_flowfile(flow)
        assert any("Duplicate" in e for e in errors)

    def test_invalid_reference(self):
        """Invalid step reference fails validation."""
        flow = Flowfile(
            name="BadRef",
            steps=[
                FlowStep(id="s1", genus="P-gent", operation="extract"),
                FlowStep(
                    id="s2",
                    genus="Bootstrap",
                    operation="judge",
                    input="from:nonexistent",
                ),
            ],
        )
        errors = validate_flowfile(flow)
        assert any("unknown step" in e for e in errors)

    def test_invalid_genus(self):
        """Invalid genus fails validation."""
        flow = Flowfile(
            name="BadGenus",
            steps=[
                FlowStep(id="s1", genus="X-gent", operation="unknown"),
            ],
        )
        errors = validate_flowfile(flow)
        assert any("unknown genus" in e for e in errors)


# =============================================================================
# Test: Dependency Resolution
# =============================================================================


class TestDependencyResolution:
    """Tests for dependency graph and topological sort."""

    def test_build_dependency_graph(self):
        """Build dependency graph from flowfile."""
        flow = Flowfile(
            name="Test",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(
                    id="judge", genus="Bootstrap", operation="judge", input="from:parse"
                ),
                FlowStep(
                    id="refine",
                    genus="R-gent",
                    operation="optimize",
                    input="from:judge",
                ),
            ],
        )
        graph = build_dependency_graph(flow)
        assert graph["parse"] == []
        assert graph["judge"] == ["parse"]
        assert graph["refine"] == ["judge"]

    def test_topological_sort_linear(self):
        """Topological sort of linear pipeline."""
        flow = Flowfile(
            name="Linear",
            steps=[
                FlowStep(id="a", genus="P-gent", operation="extract"),
                FlowStep(id="b", genus="P-gent", operation="extract", input="from:a"),
                FlowStep(id="c", genus="P-gent", operation="extract", input="from:b"),
            ],
        )
        order = topological_sort(flow)
        assert order.index("a") < order.index("b") < order.index("c")

    def test_topological_sort_parallel(self):
        """Topological sort with parallel steps."""
        flow = Flowfile(
            name="Parallel",
            steps=[
                FlowStep(id="root", genus="P-gent", operation="extract"),
                FlowStep(
                    id="branch1", genus="P-gent", operation="extract", input="from:root"
                ),
                FlowStep(
                    id="branch2", genus="P-gent", operation="extract", input="from:root"
                ),
            ],
        )
        order = topological_sort(flow)
        assert order[0] == "root"

    def test_circular_dependency_detected(self):
        """Circular dependency raises error."""
        flow = Flowfile(
            name="Circular",
            steps=[
                FlowStep(id="a", genus="P-gent", operation="extract", input="from:c"),
                FlowStep(id="b", genus="P-gent", operation="extract", input="from:a"),
                FlowStep(id="c", genus="P-gent", operation="extract", input="from:b"),
            ],
        )
        with pytest.raises(FlowValidationError, match="Circular"):
            topological_sort(flow)


# =============================================================================
# Test: Condition Evaluation
# =============================================================================


class TestConditionEvaluation:
    """Tests for condition expression evaluation."""

    def test_simple_equality(self):
        """Evaluate simple equality."""
        results = {
            "judge": StepResult(
                step_id="judge",
                status=StepStatus.COMPLETED,
                output={"verdict": "APPROVED"},
            ),
        }
        assert evaluate_condition("judge.verdict == 'APPROVED'", results) is True
        assert evaluate_condition("judge.verdict == 'REJECTED'", results) is False

    def test_inequality(self):
        """Evaluate inequality."""
        results = {
            "judge": StepResult(
                step_id="judge",
                status=StepStatus.COMPLETED,
                output={"verdict": "REJECTED"},
            ),
        }
        assert evaluate_condition("judge.verdict != 'APPROVED'", results) is True

    def test_not_prefix(self):
        """Evaluate with not prefix."""
        results = {
            "parse": StepResult(
                step_id="parse",
                status=StepStatus.COMPLETED,
                output={"valid": True},
            ),
        }
        assert evaluate_condition("not parse.valid", results) is False

    def test_success_check(self):
        """Evaluate success check."""
        results = {
            "step1": StepResult(step_id="step1", status=StepStatus.COMPLETED),
        }
        assert evaluate_condition("step1.success", results) is True

    def test_missing_step(self):
        """Missing step returns default."""
        results = {}
        # Default behavior for missing step
        assert evaluate_condition("missing.field == 'value'", results) is False


# =============================================================================
# Test: Flow Engine
# =============================================================================


class TestFlowEngine:
    """Tests for flow execution engine."""

    @pytest.fixture
    def engine(self):
        return FlowEngine()

    @pytest.fixture
    def simple_flow(self):
        return Flowfile(
            name="Simple",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
            ],
        )

    @pytest.fixture
    def multi_step_flow(self):
        return Flowfile(
            name="MultiStep",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(
                    id="judge", genus="Bootstrap", operation="judge", input="from:parse"
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_execute_simple_flow(self, engine, simple_flow):
        """Execute a simple single-step flow."""
        result = await engine.execute(simple_flow, "test input")
        assert result.status == FlowStatus.COMPLETED
        assert result.completed_steps == 1
        assert result.total_steps == 1

    @pytest.mark.asyncio
    async def test_execute_multi_step_flow(self, engine, multi_step_flow):
        """Execute a multi-step flow."""
        result = await engine.execute(multi_step_flow, "test input")
        assert result.status == FlowStatus.COMPLETED
        assert result.completed_steps == 2
        assert len(result.step_results) == 2

    @pytest.mark.asyncio
    async def test_step_input_passing(self, engine, multi_step_flow):
        """Verify input is passed between steps."""
        result = await engine.execute(multi_step_flow, "test input")

        # The judge step should receive output from parse
        judge_result = next(r for r in result.step_results if r.step_id == "judge")
        assert judge_result.status == StepStatus.COMPLETED
        assert judge_result.output is not None

    @pytest.mark.asyncio
    async def test_conditional_skip(self, engine):
        """Step skipped when condition not met."""
        flow = Flowfile(
            name="Conditional",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(
                    id="refine",
                    genus="R-gent",
                    operation="optimize",
                    input="from:parse",
                    # This condition checks for 'should_refine' key which P-gent doesn't set
                    condition="parse.should_refine == 'yes'",
                ),
            ],
        )
        result = await engine.execute(flow, "test")
        # Find refine result - should be skipped since parse.should_refine != 'yes'
        refine_results = [r for r in result.step_results if r.step_id == "refine"]
        assert len(refine_results) == 1
        assert refine_results[0].status == StepStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_flow_result_timing(self, engine, simple_flow):
        """Flow result includes timing information."""
        result = await engine.execute(simple_flow, "test")
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_ms is not None
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_step_result_timing(self, engine, simple_flow):
        """Step results include timing information."""
        result = await engine.execute(simple_flow, "test")
        step_result = result.step_results[0]
        assert step_result.started_at is not None
        assert step_result.completed_at is not None
        assert step_result.duration_ms is not None


# =============================================================================
# Test: Visualization
# =============================================================================


class TestVisualization:
    """Tests for flow visualization."""

    def test_visualize_linear_flow(self):
        """Visualize a linear pipeline."""
        flow = Flowfile(
            name="Linear",
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(id="judge", genus="Bootstrap", operation="judge"),
            ],
        )
        viz = visualize_flow(flow)
        assert "[parse]" in viz
        assert "[judge]" in viz
        assert "──▶" in viz

    def test_visualize_empty_flow(self):
        """Visualize empty flow."""
        flow = Flowfile(name="Empty", steps=[])
        viz = visualize_flow(flow)
        assert "empty" in viz.lower()

    def test_explain_flow(self):
        """Explain flow in human-readable form."""
        flow = Flowfile(
            name="Review Pipeline",
            description="Parse and judge code",
            input=FlowInput(type="file", extensions=(".py", ".js")),
            steps=[
                FlowStep(id="parse", genus="P-gent", operation="extract"),
                FlowStep(
                    id="judge",
                    genus="Bootstrap",
                    operation="judge",
                    input="from:parse",
                    args={"principles": "spec/principles.md"},
                ),
            ],
        )
        explanation = explain_flow(flow)
        assert "Review Pipeline" in explanation
        assert "parse" in explanation
        assert "judge" in explanation
        assert "P-gent.extract" in explanation
        assert "Bootstrap.judge" in explanation


# =============================================================================
# Test: FlowResult
# =============================================================================


class TestFlowResult:
    """Tests for FlowResult dataclass."""

    def test_completed_steps_count(self):
        """Count completed steps correctly."""
        result = FlowResult(
            flow_name="Test",
            status=FlowStatus.COMPLETED,
            step_results=[
                StepResult(step_id="s1", status=StepStatus.COMPLETED),
                StepResult(step_id="s2", status=StepStatus.COMPLETED),
                StepResult(step_id="s3", status=StepStatus.SKIPPED),
            ],
        )
        assert result.completed_steps == 2
        assert result.total_steps == 3

    def test_to_dict(self):
        """Convert result to dict."""
        result = FlowResult(
            flow_name="Test",
            status=FlowStatus.COMPLETED,
            started_at=datetime(2024, 1, 1, 12, 0, 0),
            completed_at=datetime(2024, 1, 1, 12, 0, 1),
        )
        d = result.to_dict()
        assert d["flow_name"] == "Test"
        assert d["status"] == "completed"
        assert d["duration_ms"] == 1000.0

    def test_failed_result(self):
        """Failed result includes error info."""
        result = FlowResult(
            flow_name="Test",
            status=FlowStatus.FAILED,
            error="Step failed",
            failed_step="parse",
            step_results=[
                StepResult(
                    step_id="parse",
                    status=StepStatus.FAILED,
                    error="Parse error",
                ),
            ],
        )
        d = result.to_dict()
        assert d["status"] == "failed"
        assert d["error"] == "Step failed"
        assert d["failed_step"] == "parse"


# =============================================================================
# Test: CLI Commands (Unit Tests)
# =============================================================================


class TestCLICommands:
    """Unit tests for CLI command handlers."""

    def test_format_flow_result_completed(self):
        """Format completed flow result."""
        from ..commands import format_flow_result_rich

        result_dict = {
            "flow_name": "Test Flow",
            "status": "completed",
            "step_results": [
                {"step_id": "parse", "status": "completed", "duration_ms": 100},
                {"step_id": "judge", "status": "completed", "duration_ms": 200},
            ],
            "completed_steps": 2,
            "total_steps": 2,
            "duration_ms": 300,
        }
        output = format_flow_result_rich(result_dict)
        assert "Test Flow" in output
        assert "COMPLETED" in output
        assert "parse" in output
        assert "judge" in output

    def test_format_flow_result_failed(self):
        """Format failed flow result."""
        from ..commands import format_flow_result_rich

        result_dict = {
            "flow_name": "Test Flow",
            "status": "failed",
            "step_results": [
                {"step_id": "parse", "status": "failed", "error": "Parse error"},
            ],
            "completed_steps": 0,
            "total_steps": 1,
            "error": "Parse error",
            "failed_step": "parse",
        }
        output = format_flow_result_rich(result_dict)
        assert "FAILED" in output
        assert "Parse error" in output

    def test_format_validation_valid(self):
        """Format valid flowfile validation result."""
        from ..commands import format_validation_result_rich

        output = format_validation_result_rich([], "test.yaml")
        assert "valid" in output.lower()
        assert "test.yaml" in output

    def test_format_validation_invalid(self):
        """Format invalid flowfile validation result."""
        from ..commands import format_validation_result_rich

        errors = ["Missing step ID", "Invalid genus"]
        output = format_validation_result_rich(errors, "test.yaml")
        assert "failed" in output.lower()
        assert "Missing step ID" in output
