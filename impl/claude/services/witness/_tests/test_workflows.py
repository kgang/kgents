"""
Tests for Witness Workflow Templates (Phase 3C).

Tests the pre-built workflow templates for common cross-jewel patterns.

See: plans/kgentsd-cross-jewel.md
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.witness.invoke import create_invoker
from services.witness.pipeline import PipelineRunner, Step, step
from services.witness.polynomial import TrustLevel
from services.witness.workflows import (
    CI_MONITOR,
    CODE_CHANGE_RESPONSE,
    CRYSTALLIZATION,
    HEALTH_CHECK,
    MORNING_STANDUP,
    PR_REVIEW_WORKFLOW,
    TEST_FAILURE_RESPONSE,
    WORKFLOW_REGISTRY,
    WorkflowCategory,
    WorkflowTemplate,
    chain_workflows,
    extend_workflow,
    get_workflow,
    list_workflows,
    search_workflows,
)

# =============================================================================
# WorkflowTemplate Tests
# =============================================================================


class TestWorkflowTemplate:
    """Tests for WorkflowTemplate dataclass."""

    def test_template_creation(self) -> None:
        """Test creating a workflow template."""
        template = WorkflowTemplate(
            name="Test Workflow",
            description="A test workflow",
            category=WorkflowCategory.REACTIVE,
            pipeline=step("world.test.manifest") >> step("self.memory.capture"),
            required_trust=2,
            tags=frozenset({"test", "example"}),
        )

        assert template.name == "Test Workflow"
        assert template.required_trust == 2
        assert "test" in template.tags

    def test_template_callable(self) -> None:
        """Test that templates are callable."""
        template = WorkflowTemplate(
            name="Test",
            description="Test",
            category=WorkflowCategory.REACTIVE,
            pipeline=step("world.test.manifest") >> step("self.memory.capture"),
        )

        pipeline = template()
        assert len(pipeline) == 2

    def test_template_default_duration(self) -> None:
        """Test default estimated duration."""
        template = WorkflowTemplate(
            name="Test",
            description="Test",
            category=WorkflowCategory.REACTIVE,
            pipeline=step("world.test.manifest") >> step("self.memory.capture"),
        )

        assert template.estimated_duration == timedelta(seconds=30)


# =============================================================================
# Pre-Built Template Tests
# =============================================================================


class TestPreBuiltTemplates:
    """Tests for the pre-built workflow templates."""

    def test_test_failure_response_structure(self) -> None:
        """Test TEST_FAILURE_RESPONSE pipeline structure."""
        assert TEST_FAILURE_RESPONSE.name == "Test Failure Response"
        assert TEST_FAILURE_RESPONSE.required_trust == 3  # AUTONOMOUS
        assert len(TEST_FAILURE_RESPONSE.pipeline) >= 3

    def test_code_change_response_structure(self) -> None:
        """Test CODE_CHANGE_RESPONSE pipeline structure."""
        assert CODE_CHANGE_RESPONSE.name == "Code Change Response"
        assert CODE_CHANGE_RESPONSE.required_trust == 3  # AUTONOMOUS
        assert "code" in CODE_CHANGE_RESPONSE.tags

    def test_pr_review_structure(self) -> None:
        """Test PR_REVIEW_WORKFLOW pipeline structure."""
        assert PR_REVIEW_WORKFLOW.name == "PR Review"
        assert "pr" in PR_REVIEW_WORKFLOW.tags
        assert "review" in PR_REVIEW_WORKFLOW.tags

    def test_morning_standup_structure(self) -> None:
        """Test MORNING_STANDUP pipeline structure."""
        assert MORNING_STANDUP.name == "Morning Standup"
        assert MORNING_STANDUP.required_trust == 0  # READ_ONLY
        assert MORNING_STANDUP.category == WorkflowCategory.PROACTIVE

    def test_ci_monitor_structure(self) -> None:
        """Test CI_MONITOR pipeline structure."""
        assert CI_MONITOR.name == "CI Monitor"
        assert CI_MONITOR.required_trust == 0  # READ_ONLY
        assert "ci" in CI_MONITOR.tags

    def test_health_check_structure(self) -> None:
        """Test HEALTH_CHECK pipeline structure."""
        assert HEALTH_CHECK.name == "Health Check"
        assert HEALTH_CHECK.category == WorkflowCategory.DIAGNOSTIC

    def test_crystallization_structure(self) -> None:
        """Test CRYSTALLIZATION pipeline structure."""
        assert CRYSTALLIZATION.name == "Experience Crystallization"
        assert "crystal" in CRYSTALLIZATION.tags


# =============================================================================
# Registry Tests
# =============================================================================


class TestWorkflowRegistry:
    """Tests for the workflow registry."""

    def test_registry_contains_all_templates(self) -> None:
        """Test that registry contains all pre-built templates."""
        assert "test-failure" in WORKFLOW_REGISTRY
        assert "code-change" in WORKFLOW_REGISTRY
        assert "pr-review" in WORKFLOW_REGISTRY
        assert "standup" in WORKFLOW_REGISTRY
        assert "ci-monitor" in WORKFLOW_REGISTRY
        assert "health-check" in WORKFLOW_REGISTRY
        assert "crystallize" in WORKFLOW_REGISTRY

    def test_get_workflow_existing(self) -> None:
        """Test getting an existing workflow."""
        workflow = get_workflow("test-failure")
        assert workflow is not None
        assert workflow.name == "Test Failure Response"

    def test_get_workflow_nonexistent(self) -> None:
        """Test getting a non-existent workflow."""
        workflow = get_workflow("does-not-exist")
        assert workflow is None

    def test_list_workflows_all(self) -> None:
        """Test listing all workflows."""
        workflows = list_workflows()
        assert len(workflows) == len(WORKFLOW_REGISTRY)

    def test_list_workflows_by_category(self) -> None:
        """Test filtering workflows by category."""
        reactive = list_workflows(category=WorkflowCategory.REACTIVE)
        assert all(w.category == WorkflowCategory.REACTIVE for w in reactive)
        assert len(reactive) >= 2  # At least test-failure and code-change

    def test_list_workflows_by_trust(self) -> None:
        """Test filtering workflows by max trust."""
        read_only = list_workflows(max_trust=0)
        assert all(w.required_trust == 0 for w in read_only)
        assert len(read_only) >= 2  # At least standup and ci-monitor

    def test_search_workflows_by_tag(self) -> None:
        """Test searching workflows by tag."""
        ci_workflows = search_workflows("ci")
        assert len(ci_workflows) >= 1
        assert all("ci" in w.tags for w in ci_workflows)


# =============================================================================
# Composition Tests
# =============================================================================


class TestWorkflowComposition:
    """Tests for workflow composition helpers."""

    def test_extend_workflow(self) -> None:
        """Test extending a workflow with additional steps."""
        extended = extend_workflow(
            MORNING_STANDUP,
            step("world.forge.summarize"),
            step("self.memory.capture"),
        )

        # Should have original steps + 2 new ones
        original_len = len(MORNING_STANDUP.pipeline)
        assert len(extended) == original_len + 2

    def test_chain_workflows(self) -> None:
        """Test chaining multiple workflows."""
        chained = chain_workflows(HEALTH_CHECK, MORNING_STANDUP)

        # Should have steps from both
        health_len = len(HEALTH_CHECK.pipeline)
        standup_len = len(MORNING_STANDUP.pipeline)
        assert len(chained) == health_len + standup_len

    def test_chain_empty(self) -> None:
        """Test chaining with no workflows."""
        chained = chain_workflows()
        assert len(chained) == 0


# =============================================================================
# Execution Tests
# =============================================================================


class TestWorkflowExecution:
    """Tests for executing workflow templates."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def invoker(self, mock_logos: MagicMock) -> MagicMock:
        """Create a JewelInvoker."""
        return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_execute_morning_standup(
        self, invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test executing the morning standup workflow."""
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        result = await runner.run(MORNING_STANDUP.pipeline)

        assert result.success is True
        assert len(result.step_results) == len(MORNING_STANDUP.pipeline)

    @pytest.mark.asyncio
    async def test_execute_health_check(self, invoker: MagicMock, mock_observer: MagicMock) -> None:
        """Test executing the health check workflow."""
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        result = await runner.run(HEALTH_CHECK.pipeline)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_ci_monitor_passing(self, mock_observer: MagicMock) -> None:
        """Test CI monitor with passing status."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "passing"})
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(CI_MONITOR.pipeline)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_ci_monitor_failing(self, mock_observer: MagicMock) -> None:
        """Test CI monitor with failing status."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "failing"})
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(CI_MONITOR.pipeline)

        assert result.success is True
        # Should have captured "CI failing" message

    @pytest.mark.asyncio
    async def test_execute_extended_workflow(
        self, invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test executing an extended workflow."""
        extended = extend_workflow(
            MORNING_STANDUP,
            step("self.memory.capture"),
        )

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(extended)

        assert result.success is True
        original_len = len(MORNING_STANDUP.pipeline)
        assert len(result.step_results) == original_len + 1

    @pytest.mark.asyncio
    async def test_execute_chained_workflows(
        self, invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test executing chained workflows."""
        chained = chain_workflows(HEALTH_CHECK, MORNING_STANDUP)

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(chained)

        assert result.success is True
        expected_steps = len(HEALTH_CHECK.pipeline) + len(MORNING_STANDUP.pipeline)
        assert len(result.step_results) == expected_steps
