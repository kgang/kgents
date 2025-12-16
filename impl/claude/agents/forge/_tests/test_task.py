"""
Tests for ForgeTask Protocol and Task Templates.

Tests cover:
1. Core types (TaskInput, TaskOutput, CoalitionShape)
2. Template validation and instantiation
3. Credit calculation
4. Template-specific behavior
5. AGENTESE integration

Run with: pytest impl/claude/agents/forge/_tests/test_task.py -v
"""

from __future__ import annotations

import pytest
from agents.forge.task import (
    CoalitionShape,
    ForgeTaskInstance,
    HandoffPattern,
    OutputFormat,
    TaskInput,
    TaskOutput,
    calculate_credits,
)
from agents.forge.templates import (
    CODE_REVIEW_TEMPLATE,
    COMPETITIVE_INTEL_TEMPLATE,
    CONTENT_CREATION_TEMPLATE,
    DECISION_ANALYSIS_TEMPLATE,
    RESEARCH_REPORT_TEMPLATE,
    TASK_TEMPLATES,
    get_template,
    list_templates,
)

# =============================================================================
# Core Types Tests
# =============================================================================


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_has_expected_formats(self) -> None:
        """All expected output formats exist."""
        assert OutputFormat.MARKDOWN
        assert OutputFormat.PR_COMMENTS
        assert OutputFormat.MATRIX
        assert OutputFormat.BRIEFING
        assert OutputFormat.MULTI_FORMAT
        assert OutputFormat.JSON
        assert OutputFormat.CODE
        assert OutputFormat.SLIDES

    def test_format_names_are_strings(self) -> None:
        """Format names can be used as strings."""
        assert OutputFormat.MARKDOWN.name == "MARKDOWN"
        assert OutputFormat.PR_COMMENTS.name == "PR_COMMENTS"


class TestHandoffPattern:
    """Tests for HandoffPattern enum."""

    def test_has_expected_patterns(self) -> None:
        """All expected handoff patterns exist."""
        assert HandoffPattern.SEQUENTIAL
        assert HandoffPattern.PARALLEL
        assert HandoffPattern.HUB_AND_SPOKE
        assert HandoffPattern.ITERATIVE
        assert HandoffPattern.PIPELINE


class TestCoalitionShape:
    """Tests for CoalitionShape dataclass."""

    def test_create_basic_shape(self) -> None:
        """Can create a basic coalition shape."""
        shape = CoalitionShape(required=("Scout", "Sage"))
        assert shape.required == ("Scout", "Sage")
        assert shape.optional == ()
        assert shape.lead is None
        assert shape.pattern == HandoffPattern.SEQUENTIAL

    def test_effective_lead_defaults_to_first_required(self) -> None:
        """Effective lead defaults to first required archetype."""
        shape = CoalitionShape(required=("Scout", "Sage"))
        assert shape.effective_lead == "Scout"

    def test_effective_lead_uses_explicit_lead(self) -> None:
        """Explicit lead overrides default."""
        shape = CoalitionShape(required=("Scout", "Sage"), lead="Sage")
        assert shape.effective_lead == "Sage"

    def test_all_archetypes_combines_required_and_optional(self) -> None:
        """all_archetypes returns both required and optional."""
        shape = CoalitionShape(required=("Scout",), optional=("Sage", "Spark"))
        assert shape.all_archetypes == ("Scout", "Sage", "Spark")

    def test_min_and_max_size(self) -> None:
        """Size calculations are correct."""
        shape = CoalitionShape(required=("Scout", "Sage"), optional=("Spark",))
        assert shape.min_size == 2
        assert shape.max_size == 3

    def test_requires_at_least_one_archetype(self) -> None:
        """Cannot create shape with empty required."""
        with pytest.raises(ValueError, match="at least one required"):
            CoalitionShape(required=())

    def test_validate_coalition_passes_with_required(self) -> None:
        """Validation passes when required archetypes present."""
        shape = CoalitionShape(required=("Scout", "Sage"))
        is_valid, error = shape.validate_coalition(("Scout", "Sage", "Spark"))
        assert is_valid
        assert error == ""

    def test_validate_coalition_fails_without_required(self) -> None:
        """Validation fails when required archetypes missing."""
        shape = CoalitionShape(required=("Scout", "Sage"))
        is_valid, error = shape.validate_coalition(("Scout",))
        assert not is_valid
        assert "Sage" in error


class TestTaskInput:
    """Tests for TaskInput dataclass."""

    def test_create_basic_input(self) -> None:
        """Can create basic task input."""
        input = TaskInput(description="Test task")
        assert input.description == "Test task"
        assert input.context == {}
        assert input.constraints == ()
        assert input.depth == "standard"

    def test_input_with_all_fields(self) -> None:
        """Can create input with all fields."""
        input = TaskInput(
            description="Test task",
            context={"key": "value"},
            constraints=("must be fast",),
            preferences={"tone": "formal"},
            target="Company X",
            scope="Q4 2024",
            depth="deep",
        )
        assert input.target == "Company X"
        assert input.scope == "Q4 2024"
        assert input.depth == "deep"
        assert input.context["key"] == "value"


class TestTaskOutput:
    """Tests for TaskOutput dataclass."""

    def test_create_basic_output(self) -> None:
        """Can create basic task output."""
        output = TaskOutput(
            content="Result",
            format=OutputFormat.MARKDOWN,
        )
        assert output.content == "Result"
        assert output.format == OutputFormat.MARKDOWN
        assert output.confidence == 0.0

    def test_output_with_metadata(self) -> None:
        """Output can include execution metadata."""
        output = TaskOutput(
            content="Result",
            format=OutputFormat.MARKDOWN,
            coalition_used=("Scout", "Sage"),
            handoffs=3,
            confidence=0.8,
            coverage=0.9,
        )
        assert output.coalition_used == ("Scout", "Sage")
        assert output.handoffs == 3


class TestForgeTaskInstance:
    """Tests for ForgeTaskInstance dataclass."""

    def test_create_instance(self) -> None:
        """Can create a task instance."""
        input = TaskInput(description="Test")
        instance = ForgeTaskInstance.create("research_report", input)

        assert instance.template_id == "research_report"
        assert instance.input == input
        assert instance.status == "pending"
        assert len(instance.id) == 8

    def test_instance_lifecycle(self) -> None:
        """Task instance tracks status through lifecycle."""
        input = TaskInput(description="Test")
        instance = ForgeTaskInstance.create("research_report", input)

        assert instance.status == "pending"

        instance.start("coalition-123")
        assert instance.status == "running"
        assert instance.coalition_id == "coalition-123"
        assert instance.started_at is not None

        output = TaskOutput(content="Done", format=OutputFormat.MARKDOWN)
        instance.complete(output)
        assert instance.status == "completed"
        assert instance.output == output
        assert instance.completed_at is not None

    def test_instance_can_fail(self) -> None:
        """Task instance can record failure."""
        input = TaskInput(description="Test")
        instance = ForgeTaskInstance.create("research_report", input)
        instance.start("coalition-123")
        instance.fail("Something went wrong")

        assert instance.status == "failed"
        assert instance.error == "Something went wrong"

    def test_instance_serialization(self) -> None:
        """Instance can serialize to dict."""
        input = TaskInput(description="Test")
        instance = ForgeTaskInstance.create("research_report", input)

        data = instance.to_dict()
        assert data["template_id"] == "research_report"
        assert data["status"] == "pending"
        assert "id" in data


# =============================================================================
# Template Registry Tests
# =============================================================================


class TestTemplateRegistry:
    """Tests for template registry functions."""

    def test_task_templates_has_five_templates(self) -> None:
        """Registry contains exactly 5 templates."""
        assert len(TASK_TEMPLATES) == 5
        assert "research_report" in TASK_TEMPLATES
        assert "code_review" in TASK_TEMPLATES
        assert "content_creation" in TASK_TEMPLATES
        assert "decision_analysis" in TASK_TEMPLATES
        assert "competitive_intel" in TASK_TEMPLATES

    def test_get_template_returns_correct_template(self) -> None:
        """get_template returns the correct template."""
        template = get_template("research_report")
        assert template.template_id == "research_report"

    def test_get_template_raises_for_unknown(self) -> None:
        """get_template raises KeyError for unknown template."""
        with pytest.raises(KeyError, match="Unknown template"):
            get_template("nonexistent")

    def test_list_templates_returns_metadata(self) -> None:
        """list_templates returns metadata for all templates."""
        templates = list_templates()
        assert len(templates) == 5
        for t in templates:
            assert "id" in t
            assert "name" in t
            assert "description" in t
            assert "credits" in t
            assert "output_format" in t


# =============================================================================
# Research Report Template Tests
# =============================================================================


class TestResearchReportTemplate:
    """Tests for ResearchReportTask template."""

    def test_template_id_is_research_report(self) -> None:
        """Template has correct ID."""
        assert RESEARCH_REPORT_TEMPLATE.template_id == "research_report"

    def test_base_credits_is_50(self) -> None:
        """Base credits match spec."""
        assert RESEARCH_REPORT_TEMPLATE.base_credits == 50

    def test_output_format_is_markdown(self) -> None:
        """Output format is markdown as per spec."""
        assert RESEARCH_REPORT_TEMPLATE.output_format == OutputFormat.MARKDOWN

    def test_coalition_requires_scout_and_sage(self) -> None:
        """Coalition shape requires Scout + Sage."""
        shape = RESEARCH_REPORT_TEMPLATE.coalition_shape
        assert "Scout" in shape.required
        assert "Sage" in shape.required

    def test_validate_input_passes_for_valid_input(self) -> None:
        """Valid input passes validation."""
        input = TaskInput(
            description="Research the market for AI tools",
            target="AI Tools Market",
        )
        is_valid, errors = RESEARCH_REPORT_TEMPLATE.validate_input(input)
        # Note: missing target is warning only, not blocking
        assert is_valid

    def test_validate_input_fails_for_short_description(self) -> None:
        """Short description fails validation."""
        input = TaskInput(description="Hi")
        is_valid, errors = RESEARCH_REPORT_TEMPLATE.validate_input(input)
        assert not is_valid
        assert any("10 characters" in e for e in errors)

    def test_suggest_coalition_adjusts_for_deep_research(self) -> None:
        """Deep research suggests larger coalition."""
        input = TaskInput(
            description="Research the market for AI tools",
            depth="deep",
        )
        shape = RESEARCH_REPORT_TEMPLATE.suggest_coalition(input)
        assert len(shape.required) > 2

    def test_phase_sequence_starts_with_exploring(self) -> None:
        """Research starts with EXPLORING."""
        phases = RESEARCH_REPORT_TEMPLATE.get_phase_sequence()
        assert phases[0] == "EXPLORING"

    def test_manifest_returns_template_info(self) -> None:
        """manifest() returns structured template info."""
        manifest = RESEARCH_REPORT_TEMPLATE.manifest()
        assert manifest["template_id"] == "research_report"
        assert manifest["base_credits"] == 50
        assert "coalition_shape" in manifest


# =============================================================================
# Code Review Template Tests
# =============================================================================


class TestCodeReviewTemplate:
    """Tests for CodeReviewTask template."""

    def test_template_id_is_code_review(self) -> None:
        """Template has correct ID."""
        assert CODE_REVIEW_TEMPLATE.template_id == "code_review"

    def test_base_credits_is_30(self) -> None:
        """Base credits match spec."""
        assert CODE_REVIEW_TEMPLATE.base_credits == 30

    def test_output_format_is_pr_comments(self) -> None:
        """Output format is PR comments as per spec."""
        assert CODE_REVIEW_TEMPLATE.output_format == OutputFormat.PR_COMMENTS

    def test_coalition_requires_steady_and_sync(self) -> None:
        """Coalition shape requires Steady + Sync."""
        shape = CODE_REVIEW_TEMPLATE.coalition_shape
        assert "Steady" in shape.required
        assert "Sync" in shape.required

    def test_validate_input_requires_code(self) -> None:
        """Validation requires code to review."""
        input = TaskInput(description="Review this code")
        is_valid, errors = CODE_REVIEW_TEMPLATE.validate_input(input)
        assert not is_valid
        assert any("diff" in e or "pr_url" in e for e in errors)

    def test_validate_input_passes_with_diff(self) -> None:
        """Validation passes when diff provided."""
        input = TaskInput(
            description="Review this code",
            context={"diff": "--- a/file.py\n+++ b/file.py\n..."},
        )
        is_valid, errors = CODE_REVIEW_TEMPLATE.validate_input(input)
        assert is_valid


# =============================================================================
# Content Creation Template Tests
# =============================================================================


class TestContentCreationTemplate:
    """Tests for ContentCreationTask template."""

    def test_template_id_is_content_creation(self) -> None:
        """Template has correct ID."""
        assert CONTENT_CREATION_TEMPLATE.template_id == "content_creation"

    def test_base_credits_is_40(self) -> None:
        """Base credits match spec."""
        assert CONTENT_CREATION_TEMPLATE.base_credits == 40

    def test_output_format_is_multi_format(self) -> None:
        """Output format is multi-format as per spec."""
        assert CONTENT_CREATION_TEMPLATE.output_format == OutputFormat.MULTI_FORMAT

    def test_coalition_requires_spark_and_sage(self) -> None:
        """Coalition shape requires Spark + Sage."""
        shape = CONTENT_CREATION_TEMPLATE.coalition_shape
        assert "Spark" in shape.required
        assert "Sage" in shape.required

    def test_suggest_coalition_changes_for_documentation(self) -> None:
        """Documentation content uses Sage lead."""
        input = TaskInput(
            description="Write technical documentation",
            context={"content_type": "documentation"},
        )
        shape = CONTENT_CREATION_TEMPLATE.suggest_coalition(input)
        assert shape.effective_lead == "Sage"


# =============================================================================
# Decision Analysis Template Tests
# =============================================================================


class TestDecisionAnalysisTemplate:
    """Tests for DecisionAnalysisTask template."""

    def test_template_id_is_decision_analysis(self) -> None:
        """Template has correct ID."""
        assert DECISION_ANALYSIS_TEMPLATE.template_id == "decision_analysis"

    def test_base_credits_is_75(self) -> None:
        """Base credits match spec (most expensive after intel)."""
        assert DECISION_ANALYSIS_TEMPLATE.base_credits == 75

    def test_output_format_is_matrix(self) -> None:
        """Output format is matrix as per spec."""
        assert DECISION_ANALYSIS_TEMPLATE.output_format == OutputFormat.MATRIX

    def test_coalition_uses_full_team(self) -> None:
        """Decision analysis uses all 5 archetypes."""
        shape = DECISION_ANALYSIS_TEMPLATE.coalition_shape
        assert len(shape.required) == 5
        assert "Scout" in shape.required
        assert "Sage" in shape.required
        assert "Spark" in shape.required
        assert "Steady" in shape.required
        assert "Sync" in shape.required

    def test_lead_is_sync(self) -> None:
        """Sync coordinates decision analysis."""
        shape = DECISION_ANALYSIS_TEMPLATE.coalition_shape
        assert shape.effective_lead == "Sync"

    def test_validate_input_requires_options(self) -> None:
        """Validation requires options to analyze."""
        input = TaskInput(description="Help me decide")
        is_valid, errors = DECISION_ANALYSIS_TEMPLATE.validate_input(input)
        assert not is_valid
        assert any("options" in e for e in errors)

    def test_validate_input_passes_with_options(self) -> None:
        """Validation passes with options."""
        input = TaskInput(
            description="Choose a framework",
            context={"options": ["React", "Vue", "Svelte"]},
        )
        is_valid, errors = DECISION_ANALYSIS_TEMPLATE.validate_input(input)
        assert is_valid


# =============================================================================
# Competitive Intel Template Tests
# =============================================================================


class TestCompetitiveIntelTemplate:
    """Tests for CompetitiveIntelTask template."""

    def test_template_id_is_competitive_intel(self) -> None:
        """Template has correct ID."""
        assert COMPETITIVE_INTEL_TEMPLATE.template_id == "competitive_intel"

    def test_base_credits_is_100(self) -> None:
        """Base credits match spec (most expensive)."""
        assert COMPETITIVE_INTEL_TEMPLATE.base_credits == 100

    def test_output_format_is_briefing(self) -> None:
        """Output format is briefing as per spec."""
        assert COMPETITIVE_INTEL_TEMPLATE.output_format == OutputFormat.BRIEFING

    def test_coalition_is_scout_heavy(self) -> None:
        """Coalition shape is Scout-heavy."""
        shape = COMPETITIVE_INTEL_TEMPLATE.coalition_shape
        scout_count = shape.required.count("Scout") + shape.optional.count("Scout")
        assert scout_count >= 1  # At least one Scout required
        assert shape.effective_lead == "Scout"

    def test_validate_input_requires_target(self) -> None:
        """Validation requires a target company/product."""
        input = TaskInput(description="Analyze competitors")
        is_valid, errors = COMPETITIVE_INTEL_TEMPLATE.validate_input(input)
        assert not is_valid
        assert any("target" in e for e in errors)

    def test_credits_scale_with_competitor_count(self) -> None:
        """Credits increase with more competitors."""
        input_few = TaskInput(
            description="Analyze",
            target="My Company",
            context={"competitors": ["A", "B"]},
        )
        input_many = TaskInput(
            description="Analyze",
            target="My Company",
            context={"competitors": ["A", "B", "C", "D", "E", "F", "G"]},
        )

        credits_few = COMPETITIVE_INTEL_TEMPLATE.estimate_credits(input_few)
        credits_many = COMPETITIVE_INTEL_TEMPLATE.estimate_credits(input_many)

        assert credits_many > credits_few


# =============================================================================
# Credit Calculation Tests
# =============================================================================


class TestCreditCalculation:
    """Tests for calculate_credits utility."""

    def test_base_credits_returned_for_standard_input(self) -> None:
        """Standard depth returns base credits."""
        input = TaskInput(description="Test task", depth="standard")
        shape = CoalitionShape(required=("Scout", "Sage"))
        credits = calculate_credits(50, input, shape)
        assert credits == 50

    def test_quick_depth_reduces_credits(self) -> None:
        """Quick depth halves credits."""
        input = TaskInput(description="Test task", depth="quick")
        shape = CoalitionShape(required=("Scout", "Sage"))
        credits = calculate_credits(50, input, shape)
        assert credits == 25

    def test_deep_depth_doubles_credits(self) -> None:
        """Deep depth doubles credits."""
        input = TaskInput(description="Test task", depth="deep")
        shape = CoalitionShape(required=("Scout", "Sage"))
        credits = calculate_credits(50, input, shape)
        assert credits == 100

    def test_large_coalition_increases_credits(self) -> None:
        """Large coalitions cost more."""
        input = TaskInput(description="Test task")
        small_shape = CoalitionShape(required=("Scout",))
        large_shape = CoalitionShape(
            required=("Scout", "Sage", "Spark", "Steady", "Sync")
        )

        credits_small = calculate_credits(50, input, small_shape)
        credits_large = calculate_credits(50, input, large_shape)

        assert credits_large > credits_small


# =============================================================================
# Template Execution Tests
# =============================================================================


class TestTemplateExecution:
    """Tests for template execution (async)."""

    @pytest.mark.asyncio
    async def test_research_report_execute_returns_output(self) -> None:
        """Research report execution returns TaskOutput."""
        input = TaskInput(
            description="Research AI tools",
            target="AI Tools",
        )
        output = await RESEARCH_REPORT_TEMPLATE.execute(input, coalition=None)

        assert isinstance(output, TaskOutput)
        assert output.format == OutputFormat.MARKDOWN
        assert "AI Tools" in output.content or "AI Tools" in output.summary

    @pytest.mark.asyncio
    async def test_code_review_execute_returns_pr_comments(self) -> None:
        """Code review execution returns PR comments structure."""
        input = TaskInput(
            description="Review code",
            context={"diff": "...", "files": ["test.py"]},
        )
        output = await CODE_REVIEW_TEMPLATE.execute(input, coalition=None)

        assert output.format == OutputFormat.PR_COMMENTS
        assert isinstance(output.content, dict)
        assert "comments" in output.content

    @pytest.mark.asyncio
    async def test_decision_analysis_execute_returns_matrix(self) -> None:
        """Decision analysis returns matrix with recommendation."""
        input = TaskInput(
            description="Choose framework",
            context={"options": ["A", "B", "C"]},
        )
        output = await DECISION_ANALYSIS_TEMPLATE.execute(input, coalition=None)

        assert output.format == OutputFormat.MATRIX
        assert isinstance(output.content, dict)
        assert "recommendation" in output.content
        assert "matrix" in output.content

    @pytest.mark.asyncio
    async def test_competitive_intel_execute_returns_briefing(self) -> None:
        """Competitive intel returns briefing document."""
        input = TaskInput(
            description="Analyze competition",
            target="My Company",
            context={"competitors": ["Comp A", "Comp B"]},
        )
        output = await COMPETITIVE_INTEL_TEMPLATE.execute(input, coalition=None)

        assert output.format == OutputFormat.BRIEFING
        assert isinstance(output.content, dict)
        assert "swot_analysis" in output.content


# =============================================================================
# AGENTESE Integration Tests
# =============================================================================


class TestAGENTESEIntegration:
    """Tests for AGENTESE path integration."""

    def test_can_import_task_concept_node(self) -> None:
        """TaskConceptNode can be imported."""
        from agents.forge.agentese import TaskConceptNode

        assert TaskConceptNode is not None

    def test_create_task_node_for_all_templates(self) -> None:
        """Can create task node for concept.task."""
        from agents.forge.agentese import create_task_node

        node = create_task_node("concept.task")
        assert node.handle == "concept.task"
        assert node.template is None

    def test_create_task_node_for_specific_template(self) -> None:
        """Can create task node for specific template."""
        from agents.forge.agentese import create_task_node

        node = create_task_node("concept.task.research_report")
        assert node.handle == "concept.task.research_report"
        assert node.template is not None
        assert node.template.template_id == "research_report"

    def test_resolve_task_path(self) -> None:
        """resolve_task_path works correctly."""
        from agents.forge.agentese import resolve_task_path

        # All templates
        node_all = resolve_task_path("task", [])
        assert node_all.handle == "concept.task"

        # Specific template
        node_specific = resolve_task_path("task", ["code_review"])
        assert node_specific._template_id == "code_review"

    def test_query_tasks_returns_all_by_default(self) -> None:
        """query_tasks returns all templates by default."""
        from agents.forge.agentese import query_tasks

        results = query_tasks()
        assert len(results) == 5

    def test_query_tasks_filters_by_credits(self) -> None:
        """query_tasks can filter by credits."""
        from agents.forge.agentese import query_tasks

        # Only cheap templates
        cheap = query_tasks(max_credits=40)
        assert all(r["credits"] <= 40 for r in cheap)

        # Only expensive
        expensive = query_tasks(min_credits=75)
        assert all(r["credits"] >= 75 for r in expensive)

    def test_query_tasks_filters_by_archetype(self) -> None:
        """query_tasks can filter by required archetype."""
        from agents.forge.agentese import query_tasks

        # Templates requiring Spark
        spark_tasks = query_tasks(required_archetype="Spark")
        assert all("Spark" in r["required_archetypes"] for r in spark_tasks)
