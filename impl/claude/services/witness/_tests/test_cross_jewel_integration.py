"""
Cross-Jewel Integration Tests (Phase 3C).

End-to-end tests for cross-jewel workflow patterns:
- Test failure → Fix → Retest workflow
- Code change → Analyze → Document workflow
- Schedule → Execute → Report workflow

These tests verify the full integration of:
- JewelInvoker (trust-gated invocation)
- Pipeline composition
- Scheduler (temporal composition)
- Trust escalation

"Daring, bold, creative" — test the complete vision.

See: plans/kgentsd-cross-jewel.md
See: spec/principles.md (Composable principle)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.kgentsd.invoke import InvocationResult, JewelInvoker, create_invoker
from services.kgentsd.pipeline import (
    Branch,
    Pipeline,
    PipelineResult,
    PipelineRunner,
    PipelineStatus,
    Step,
    branch,
    step,
)
from services.kgentsd.schedule import (
    ScheduleStatus,
    WitnessScheduler,
    create_scheduler,
    delay,
    every,
)
from services.witness.polynomial import TrustLevel
from services.witness.trust import GateDecision

# =============================================================================
# Mock Infrastructure
# =============================================================================


class MockCrownJewel:
    """
    Mock Crown Jewel for testing cross-jewel workflows.

    Simulates responses from various Crown Jewels:
    - Gestalt: Code analysis
    - Forge: Code modifications
    - Memory: Storage operations
    - CI: Build/test status
    """

    def __init__(self) -> None:
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._responses: dict[str, Any] = {}
        self._error_paths: set[str] = set()

    def set_response(self, path: str, response: Any) -> None:
        """Set the response for a specific path."""
        self._responses[path] = response

    def set_error(self, path: str) -> None:
        """Make a path return an error."""
        self._error_paths.add(path)

    async def invoke(self, path: str, observer: Any, **kwargs: Any) -> Any:
        """Mock invocation handler."""
        self.call_log.append((path, kwargs))

        if path in self._error_paths:
            raise Exception(f"Mock error for {path}")

        # Return configured response or default
        if path in self._responses:
            response = self._responses[path]
            # If callable, call it with kwargs
            if callable(response):
                return response(**kwargs)
            return response

        # Default responses by jewel
        if "gestalt" in path:
            if "analyze" in path:
                return {"issues": 2, "suggestions": ["Fix A", "Fix B"]}
            return {"status": "ok"}

        if "forge" in path:
            if "fix" in path:
                return {"fixed": True, "changes": 2}
            if "document" in path:
                return {"doc_path": "/docs/output.md"}
            return {"modified": True}

        if "memory" in path:
            return {"captured": True, "crystal_id": "cry_123"}

        if "ci" in path or "test" in path:
            return {"passed": True, "tests": 42, "duration_ms": 1234}

        return {"status": "ok"}


@pytest.fixture
def mock_jewel() -> MockCrownJewel:
    """Create a MockCrownJewel instance."""
    return MockCrownJewel()


@pytest.fixture
def mock_logos(mock_jewel: MockCrownJewel) -> MagicMock:
    """Create a mock Logos using MockCrownJewel."""
    logos = MagicMock()
    logos.invoke = mock_jewel.invoke
    return logos


@pytest.fixture
def l3_invoker(mock_logos: MagicMock) -> JewelInvoker:
    """Create a L3 AUTONOMOUS JewelInvoker."""
    return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)


@pytest.fixture
def l2_invoker(mock_logos: MagicMock) -> JewelInvoker:
    """Create a L2 SUGGESTION JewelInvoker."""
    return create_invoker(mock_logos, TrustLevel.SUGGESTION)


@pytest.fixture
def l0_invoker(mock_logos: MagicMock) -> JewelInvoker:
    """Create a L0 READ_ONLY JewelInvoker."""
    return create_invoker(mock_logos, TrustLevel.READ_ONLY)


@pytest.fixture
def mock_observer() -> MagicMock:
    """Create a mock Observer."""
    observer = MagicMock()
    observer.archetype = "developer"
    return observer


# =============================================================================
# Workflow Pattern: Test Failure → Fix → Retest
# =============================================================================


class TestTestFailureWorkflow:
    """
    Test the complete test failure → fix → retest workflow.

    This is the canonical cross-jewel pattern:
    1. Tests fail → event captured
    2. Analyze failure with Gestalt
    3. Fix with Forge
    4. Rerun tests
    5. Capture result in Memory

    At L3 AUTONOMOUS, this happens automatically.
    At L2 SUGGESTION, each mutation requires confirmation.
    """

    @pytest.mark.asyncio
    async def test_full_workflow_l3(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test the full workflow at L3 AUTONOMOUS."""
        # Configure responses
        mock_jewel.set_response(
            "world.gestalt.analyze",
            {"issues": 2, "root_cause": "Missing null check"},
        )
        mock_jewel.set_response(
            "world.forge.fix",
            {"fixed": True, "files_modified": ["src/handler.py"]},
        )
        mock_jewel.set_response(
            "world.test.run",
            {"passed": True, "tests": 42},
        )

        # Build the workflow pipeline
        workflow = (
            step("world.gestalt.analyze", target="src/handler.py")
            >> branch(
                condition=lambda r: r.get("issues", 0) > 0,
                if_true=step("world.forge.fix"),
                if_false=step("self.memory.capture", content="No issues"),
            )
            >> step("world.test.run")
            >> step("self.memory.capture")
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        # Verify workflow succeeded
        assert result.status == PipelineStatus.COMPLETED
        assert result.success is True

        # Verify call sequence
        paths = [path for path, _ in mock_jewel.call_log]
        assert "world.gestalt.analyze" in paths
        assert "world.forge.fix" in paths
        assert "world.test.run" in paths
        assert "self.memory.capture" in paths

    @pytest.mark.asyncio
    async def test_workflow_no_fix_needed(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test workflow when no fix is needed."""
        # No issues found
        mock_jewel.set_response("world.gestalt.analyze", {"issues": 0})

        workflow = step("world.gestalt.analyze") >> branch(
            condition=lambda r: r.get("issues", 0) > 0,
            if_true=step("world.forge.fix"),
            if_false=step("self.memory.capture", content="All clear"),
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.success is True

        # Fix should NOT have been called
        paths = [path for path, _ in mock_jewel.call_log]
        assert "world.forge.fix" not in paths
        assert "self.memory.capture" in paths

    @pytest.mark.asyncio
    async def test_workflow_l2_requires_confirmation(
        self,
        mock_jewel: MockCrownJewel,
        l2_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test that L2 workflow requires confirmation for mutations."""
        mock_jewel.set_response("world.gestalt.analyze", {"issues": 1})

        # Analyze is read-only → should work
        analyze_result = await l2_invoker.invoke("world.gestalt.analyze", mock_observer)
        assert analyze_result.success is True

        # Fix is mutation → should require confirmation
        fix_result = await l2_invoker.invoke("world.forge.fix", mock_observer)
        assert fix_result.success is False
        assert fix_result.gate_decision == GateDecision.CONFIRM

    @pytest.mark.asyncio
    async def test_workflow_l0_read_only(
        self,
        mock_jewel: MockCrownJewel,
        l0_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test that L0 can only perform read operations."""
        # Analyze is read-only → should work
        analyze_result = await l0_invoker.invoke("world.gestalt.manifest", mock_observer)
        assert analyze_result.success is True

        # Fix is mutation → should be denied
        fix_result = await l0_invoker.invoke("world.forge.fix", mock_observer)
        assert fix_result.success is False
        assert fix_result.gate_decision == GateDecision.DENY


# =============================================================================
# Workflow Pattern: Code Change → Analyze → Document
# =============================================================================


class TestCodeChangeWorkflow:
    """
    Test the code change → analyze → document workflow.

    When code changes are detected:
    1. Analyze the change with Gestalt
    2. Capture analysis in Memory
    3. Generate documentation with Forge
    4. Update project context

    This workflow is triggered by filesystem events.
    """

    @pytest.mark.asyncio
    async def test_code_change_workflow(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test the complete code change workflow."""
        mock_jewel.set_response(
            "world.gestalt.analyze",
            {"patterns": ["MVC", "Repository"], "complexity": "medium"},
        )
        mock_jewel.set_response(
            "world.forge.document",
            {"doc_path": "/docs/api.md", "sections": 5},
        )

        workflow = (
            step("world.gestalt.analyze", target="src/api/")
            >> step("self.memory.capture")
            >> step("world.forge.document", format="markdown")
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.success is True
        assert result.final_result["doc_path"] == "/docs/api.md"

    @pytest.mark.asyncio
    async def test_workflow_with_transform(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test workflow with result transformation between steps."""
        mock_jewel.set_response(
            "world.gestalt.analyze",
            {"summary": "Added new API endpoint", "files": 3},
        )

        # Transform analysis result to memory capture format
        workflow = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Step(
                    path="self.memory.capture",
                    transform=lambda r: {"content": r.get("summary", "")},
                ),
            ]
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.success is True

        # Verify transform was applied
        memory_call = [
            (path, kwargs) for path, kwargs in mock_jewel.call_log if path == "self.memory.capture"
        ]
        assert len(memory_call) == 1
        assert "content" in memory_call[0][1]


# =============================================================================
# Workflow Pattern: Scheduled Monitoring
# =============================================================================


class TestScheduledWorkflow:
    """
    Test scheduled cross-jewel workflows.

    The scheduler enables:
    - Periodic CI monitoring
    - Delayed code analysis (after git push)
    - Scheduled maintenance tasks
    """

    @pytest.mark.asyncio
    async def test_scheduled_ci_check(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test scheduling periodic CI checks."""
        mock_jewel.set_response("world.ci.status", {"status": "passing"})

        scheduler = create_scheduler(l3_invoker, mock_observer)

        # Schedule CI check (immediately due for testing)
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=every(minutes=10),
            start_immediately=True,
            max_runs=2,
            name="CI Monitor",
        )

        # Make immediately due
        task.next_run = datetime.now(UTC) - timedelta(seconds=1)

        # Execute first tick
        executed = await scheduler.tick()
        assert len(executed) == 1
        assert executed[0].name == "CI Monitor"
        assert task.run_count == 1

    @pytest.mark.asyncio
    async def test_scheduled_analysis_after_push(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test scheduling analysis after a git push."""
        mock_jewel.set_response(
            "world.gestalt.analyze",
            {"changes": 5, "risk": "low"},
        )

        scheduler = create_scheduler(l3_invoker, mock_observer)

        # Schedule delayed analysis (simulating post-push)
        task = scheduler.schedule(
            "world.gestalt.analyze",
            delay=delay(seconds=-1),  # Due now for testing
            name="Post-Push Analysis",
            target="main",
        )

        executed = await scheduler.tick()

        assert len(executed) == 1
        assert task.status == ScheduleStatus.COMPLETED

        # Verify the analysis was called
        paths = [path for path, _ in mock_jewel.call_log]
        assert "world.gestalt.analyze" in paths

    @pytest.mark.asyncio
    async def test_scheduled_pipeline(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test scheduling a full pipeline for later execution."""
        workflow = step("world.gestalt.manifest") >> step("self.memory.capture")

        scheduler = create_scheduler(l3_invoker, mock_observer)

        task = scheduler.schedule_pipeline(
            workflow,
            delay=delay(seconds=-1),  # Due now
            name="Manifest Capture",
        )

        executed = await scheduler.tick()

        assert len(executed) == 1
        assert task.status == ScheduleStatus.COMPLETED
        assert task.last_result is not None
        assert task.last_result.success is True


# =============================================================================
# Error Handling Patterns
# =============================================================================


class TestErrorHandling:
    """Test error handling in cross-jewel workflows."""

    @pytest.mark.asyncio
    async def test_pipeline_aborts_on_failure(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test that pipeline aborts on step failure."""
        # Make analyze fail
        mock_jewel.set_error("world.gestalt.analyze")

        workflow = (
            step("world.gestalt.analyze")
            >> step("world.forge.fix")  # Should not run
            >> step("self.memory.capture")  # Should not run
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.status == PipelineStatus.FAILED
        assert result.aborted_at_step == 0

        # Verify only analyze was attempted
        paths = [path for path, _ in mock_jewel.call_log]
        assert "world.gestalt.analyze" in paths
        assert "world.forge.fix" not in paths

    @pytest.mark.asyncio
    async def test_pipeline_continues_on_failure(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test pipeline continues when abort_on_failure=False."""
        mock_jewel.set_error("world.gestalt.analyze")

        workflow = (
            step("world.gestalt.analyze")  # Will fail
            >> step("world.forge.manifest")  # Should still run
        )

        runner = PipelineRunner(
            invoker=l3_invoker,
            observer=mock_observer,
            abort_on_failure=False,
        )
        result = await runner.run(workflow)

        # Both steps should have been attempted
        assert len(result.step_results) == 2

    @pytest.mark.asyncio
    async def test_scheduled_task_failure_recorded(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test that scheduled task failures are properly recorded."""
        mock_jewel.set_error("world.gestalt.analyze")

        scheduler = create_scheduler(l3_invoker, mock_observer)

        task = scheduler.schedule(
            "world.gestalt.analyze",
            delay=delay(seconds=-1),
            name="Failing Task",
        )

        await scheduler.tick()

        assert task.status == ScheduleStatus.FAILED


# =============================================================================
# Category Law Verification
# =============================================================================


class TestCategoryLaws:
    """
    Verify that cross-jewel workflows preserve category laws.

    From spec/principles.md:
    - Identity: Id >> pipeline == pipeline == pipeline >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)
    """

    def test_pipeline_associativity(self) -> None:
        """Test (a >> b) >> c == a >> (b >> c)."""
        a = Step(path="world.a.manifest")
        b = Step(path="world.b.manifest")
        c = Step(path="world.c.manifest")

        left = (a >> b) >> c
        right = a >> (b >> c)

        # Both should produce equivalent pipelines
        assert (
            left.paths
            == right.paths
            == [
                "world.a.manifest",
                "world.b.manifest",
                "world.c.manifest",
            ]
        )

    def test_empty_pipeline_identity(self) -> None:
        """Test that empty pipeline acts as identity."""
        empty = Pipeline([])
        p = Pipeline([Step(path="world.a.manifest")])

        # empty >> p should equal p's structure
        result = empty >> p
        assert result.paths == p.paths

    @pytest.mark.asyncio
    async def test_execution_order_preserved(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """Test that execution order matches composition order."""
        workflow = (
            step("world.first.manifest")
            >> step("world.second.manifest")
            >> step("world.third.manifest")
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        await runner.run(workflow)

        # Verify call order
        paths = [path for path, _ in mock_jewel.call_log]
        assert paths == [
            "world.first.manifest",
            "world.second.manifest",
            "world.third.manifest",
        ]


# =============================================================================
# Real-World Scenario Tests
# =============================================================================


class TestRealWorldScenarios:
    """
    Test realistic cross-jewel workflow scenarios.

    These simulate actual developer workflows.
    """

    @pytest.mark.asyncio
    async def test_pr_review_workflow(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """
        Test PR review workflow:
        1. Analyze changed files
        2. Run tests on changes
        3. Generate review summary
        4. Store in memory
        """
        mock_jewel.set_response(
            "world.gestalt.analyze",
            {
                "files_changed": 5,
                "patterns": ["Clean architecture"],
                "risk": "medium",
            },
        )
        mock_jewel.set_response(
            "world.test.run",
            {"passed": True, "coverage": 85.5},
        )
        mock_jewel.set_response(
            "world.forge.summarize",
            {"summary": "Good PR, minor style suggestions"},
        )

        workflow = (
            step("world.gestalt.analyze", target="pr/123")
            >> step("world.test.run", scope="changed")
            >> branch(
                condition=lambda r: r.get("passed", False),
                if_true=step("world.forge.summarize"),
                if_false=step("self.memory.capture", content="Tests failed"),
            )
            >> step("self.memory.capture")
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.success is True

        # Verify the expected flow
        paths = [path for path, _ in mock_jewel.call_log]
        assert "world.gestalt.analyze" in paths
        assert "world.test.run" in paths
        assert "world.forge.summarize" in paths

    @pytest.mark.asyncio
    async def test_morning_standup_workflow(
        self,
        mock_jewel: MockCrownJewel,
        l3_invoker: JewelInvoker,
        mock_observer: MagicMock,
    ) -> None:
        """
        Test morning standup preparation:
        1. Get yesterday's activity from memory
        2. Check CI status
        3. Analyze current branch state
        4. Generate standup summary
        """
        mock_jewel.set_response(
            "self.memory.query",
            {"thoughts": ["Worked on API", "Fixed auth bug"]},
        )
        mock_jewel.set_response(
            "world.ci.status",
            {"status": "passing", "last_run": "2h ago"},
        )
        mock_jewel.set_response(
            "world.gestalt.manifest",
            {"branch": "feature/auth", "uncommitted": 3},
        )

        workflow = (
            step("self.memory.manifest")
            >> step("world.ci.manifest")
            >> step("world.gestalt.manifest")
        )

        runner = PipelineRunner(invoker=l3_invoker, observer=mock_observer)
        result = await runner.run(workflow)

        assert result.success is True
        assert len(result.step_results) == 3
