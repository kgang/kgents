"""
Tests for Cross-Jewel Pipeline (Phase 3B).

Tests the Pipeline composition and PipelineRunner for cross-jewel
workflow patterns.

See: plans/kgentsd-cross-jewel.md
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.witness.invoke import InvocationResult, create_invoker
from services.witness.pipeline import (
    Branch,
    Pipeline,
    PipelineResult,
    PipelineRunner,
    PipelineStatus,
    Step,
    StepResult,
    branch,
    step,
)
from services.witness.polynomial import TrustLevel
from services.witness.trust import GateDecision

# =============================================================================
# Step Tests
# =============================================================================


class TestStep:
    """Tests for Step dataclass."""

    def test_step_creation(self) -> None:
        """Test creating a simple step."""
        s = Step(path="world.gestalt.analyze")

        assert s.path == "world.gestalt.analyze"
        assert s.kwargs == {}
        assert s.transform is None

    def test_step_with_kwargs(self) -> None:
        """Test creating a step with static kwargs."""
        s = Step(path="world.gestalt.analyze", kwargs={"file": "src/main.py"})

        assert s.kwargs == {"file": "src/main.py"}

    def test_step_with_transform(self) -> None:
        """Test creating a step with a transformer."""
        transform = lambda result: {"content": result.get("summary", "")}
        s = Step(path="self.memory.capture", transform=transform)

        assert s.transform is transform
        assert s.transform({"summary": "Test"}) == {"content": "Test"}

    def test_step_rshift_step(self) -> None:
        """Test composing steps with >>."""
        s1 = Step(path="world.gestalt.analyze")
        s2 = Step(path="self.memory.capture")

        pipeline = s1 >> s2

        assert isinstance(pipeline, Pipeline)
        assert len(pipeline.steps) == 2
        assert pipeline.steps[0].path == "world.gestalt.analyze"
        assert pipeline.steps[1].path == "self.memory.capture"

    def test_step_rshift_pipeline(self) -> None:
        """Test composing step >> pipeline."""
        s1 = Step(path="world.gestalt.analyze")
        p = Pipeline([Step(path="self.memory.capture"), Step(path="world.forge.document")])

        result = s1 >> p

        assert len(result.steps) == 3


class TestStepConvenience:
    """Tests for step() convenience function."""

    def test_step_function(self) -> None:
        """Test step() convenience function."""
        s = step("world.gestalt.analyze", file="src/main.py")

        assert s.path == "world.gestalt.analyze"
        assert s.kwargs == {"file": "src/main.py"}


# =============================================================================
# Branch Tests
# =============================================================================


class TestBranch:
    """Tests for Branch dataclass."""

    def test_branch_creation(self) -> None:
        """Test creating a simple branch."""
        b = Branch(
            condition=lambda r: r.get("issues", 0) > 0,
            if_true=Step(path="world.forge.fix"),
            if_false=Step(path="self.memory.capture"),
        )

        assert b.condition({"issues": 5}) is True
        assert b.condition({"issues": 0}) is False

    def test_branch_without_else(self) -> None:
        """Test creating a branch without else clause."""
        b = Branch(
            condition=lambda r: True,
            if_true=Step(path="world.forge.fix"),
        )

        assert b.if_false is None


class TestBranchConvenience:
    """Tests for branch() convenience function."""

    def test_branch_function(self) -> None:
        """Test branch() convenience function."""
        b = branch(
            condition=lambda r: r.get("count") > 0,
            if_true=step("world.forge.fix"),
            if_false=step("self.memory.capture"),
        )

        assert b.condition({"count": 1}) is True
        assert isinstance(b.if_true, Step)
        assert isinstance(b.if_false, Step)


# =============================================================================
# Pipeline Tests
# =============================================================================


class TestPipeline:
    """Tests for Pipeline dataclass."""

    def test_pipeline_creation(self) -> None:
        """Test creating a pipeline directly."""
        p = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Step(path="self.memory.capture"),
            ]
        )

        assert len(p.steps) == 2

    def test_pipeline_len(self) -> None:
        """Test pipeline length."""
        p = Pipeline([Step(path="a"), Step(path="b"), Step(path="c")])
        assert len(p) == 3

    def test_pipeline_iter(self) -> None:
        """Test iterating over pipeline steps."""
        steps = [Step(path="a"), Step(path="b")]
        p = Pipeline(steps)

        for i, s in enumerate(p):
            assert s == steps[i]

    def test_pipeline_paths(self) -> None:
        """Test getting all paths from pipeline."""
        p = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Step(path="self.memory.capture"),
            ]
        )

        assert p.paths == ["world.gestalt.analyze", "self.memory.capture"]

    def test_pipeline_rshift_step(self) -> None:
        """Test pipeline >> step."""
        p = Pipeline([Step(path="a")])
        s = Step(path="b")

        result = p >> s

        assert len(result.steps) == 2
        assert result.steps[1].path == "b"

    def test_pipeline_rshift_pipeline(self) -> None:
        """Test pipeline >> pipeline."""
        p1 = Pipeline([Step(path="a")])
        p2 = Pipeline([Step(path="b"), Step(path="c")])

        result = p1 >> p2

        assert len(result.steps) == 3

    def test_pipeline_composition_chain(self) -> None:
        """Test chaining multiple compositions."""
        p = (
            Step(path="world.gestalt.analyze")
            >> Step(path="self.memory.capture")
            >> Step(path="world.forge.document")
        )

        assert len(p.steps) == 3


# =============================================================================
# PipelineResult Tests
# =============================================================================


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""

    def test_successful_result(self) -> None:
        """Test successful pipeline result."""
        result = PipelineResult(
            status=PipelineStatus.COMPLETED,
            step_results=[
                StepResult(step_index=0, path="a", success=True, result={"ok": True}),
                StepResult(step_index=1, path="b", success=True, result={"done": True}),
            ],
            final_result={"done": True},
        )

        assert result.success is True
        assert result.failed_step is None

    def test_failed_result(self) -> None:
        """Test failed pipeline result."""
        result = PipelineResult(
            status=PipelineStatus.FAILED,
            step_results=[
                StepResult(step_index=0, path="a", success=True),
                StepResult(step_index=1, path="b", success=False, error="Failed!"),
            ],
            error="Failed!",
            aborted_at_step=1,
        )

        assert result.success is False
        assert result.failed_step is not None
        assert result.failed_step.step_index == 1

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        result = PipelineResult(
            status=PipelineStatus.COMPLETED,
            step_results=[],
            final_result={"ok": True},
            total_duration_ms=123.45,
        )

        d = result.to_dict()
        assert d["status"] == "COMPLETED"
        assert d["success"] is True
        assert d["total_duration_ms"] == 123.45


# =============================================================================
# PipelineRunner Tests
# =============================================================================


class TestPipelineRunner:
    """Tests for PipelineRunner class."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos that returns success."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_invoker(self, mock_logos: MagicMock) -> MagicMock:
        """Create a mock JewelInvoker."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        return invoker

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_run_simple_pipeline(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a simple pipeline."""
        pipeline = Pipeline(
            [
                Step(path="world.gestalt.manifest"),
                Step(path="self.memory.manifest"),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.status == PipelineStatus.COMPLETED
        assert result.success is True
        assert len(result.step_results) == 2

    @pytest.mark.asyncio
    async def test_run_pipeline_with_kwargs(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with static kwargs."""
        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze", kwargs={"file": "src/main.py"}),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_pipeline_with_initial_kwargs(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with initial kwargs."""
        pipeline = Pipeline([Step(path="world.gestalt.analyze")])

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline, initial_kwargs={"source": "test"})

        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_pipeline_failure_aborts(self, mock_observer: MagicMock) -> None:
        """Test that pipeline aborts on failure by default."""
        # Create invoker that fails on second call
        logos = MagicMock()
        call_count = 0

        async def mock_invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Step 2 failed")
            return {"ok": True}

        logos.invoke = mock_invoke
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        pipeline = Pipeline(
            [
                Step(path="step1.manifest"),
                Step(path="step2.manifest"),  # This will fail
                Step(path="step3.manifest"),  # This should not run
            ]
        )

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.status == PipelineStatus.FAILED
        assert result.aborted_at_step == 1
        assert len(result.step_results) == 2  # Only 2 steps executed

    @pytest.mark.asyncio
    async def test_run_pipeline_continue_on_failure(self, mock_observer: MagicMock) -> None:
        """Test pipeline continues when abort_on_failure=False."""
        logos = MagicMock()
        call_count = 0

        async def mock_invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Step 2 failed")
            return {"ok": True}

        logos.invoke = mock_invoke
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        pipeline = Pipeline(
            [
                Step(path="step1.manifest"),
                Step(path="step2.manifest"),  # This will fail
                Step(path="step3.manifest"),  # This SHOULD run
            ]
        )

        runner = PipelineRunner(invoker=invoker, observer=mock_observer, abort_on_failure=False)
        result = await runner.run(pipeline)

        # Should complete but with failures
        assert len(result.step_results) == 3

    @pytest.mark.asyncio
    async def test_run_pipeline_with_transform(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with result transformer."""
        # First step returns summary
        mock_invoker.logos.invoke = AsyncMock(return_value={"summary": "Test result"})

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Step(
                    path="self.memory.capture",
                    transform=lambda r: {"content": r.get("summary", "")},
                ),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_pipeline_with_branch_true(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with branch that evaluates to true."""
        # Return issues > 0
        mock_invoker.logos.invoke = AsyncMock(return_value={"issues": 5})

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Branch(
                    condition=lambda r: r.get("issues", 0) > 0,
                    if_true=Step(path="world.forge.fix"),
                    if_false=Step(path="self.memory.capture"),
                ),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True
        # Should have executed analyze and fix (not capture)
        assert len(result.step_results) == 2

    @pytest.mark.asyncio
    async def test_run_pipeline_with_branch_false(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with branch that evaluates to false."""
        # Return issues = 0
        mock_invoker.logos.invoke = AsyncMock(return_value={"issues": 0})

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Branch(
                    condition=lambda r: r.get("issues", 0) > 0,
                    if_true=Step(path="world.forge.fix"),
                    if_false=Step(path="self.memory.capture"),
                ),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_pipeline_branch_no_else(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running a pipeline with branch that has no else."""
        # Return issues = 0 (false condition)
        mock_invoker.logos.invoke = AsyncMock(return_value={"issues": 0})

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Branch(
                    condition=lambda r: r.get("issues", 0) > 0,
                    if_true=Step(path="world.forge.fix"),
                    # No if_false
                ),
            ]
        )

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True
        # Only analyze should have result, branch should be skipped
        assert len(result.step_results) == 1

    @pytest.mark.asyncio
    async def test_run_records_duration(
        self, mock_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test that duration is recorded."""
        pipeline = Pipeline([Step(path="world.gestalt.manifest")])

        runner = PipelineRunner(invoker=mock_invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.total_duration_ms >= 0
        assert result.step_results[0].duration_ms >= 0


# =============================================================================
# Category Law Tests
# =============================================================================


class TestCategoryLaws:
    """Tests for category law preservation in pipelines."""

    def test_associativity(self) -> None:
        """Test (a >> b) >> c == a >> (b >> c)."""
        a = Step(path="a")
        b = Step(path="b")
        c = Step(path="c")

        left = (a >> b) >> c
        right = a >> (b >> c)

        # Both should have same paths
        assert left.paths == right.paths == ["a", "b", "c"]

    def test_identity_left(self) -> None:
        """Test Id >> pipeline approximately equals pipeline."""
        # We don't have a formal Identity step, but empty pipeline acts as identity
        empty = Pipeline([])
        p = Pipeline([Step(path="a")])

        # empty >> p should give p's steps
        result = empty >> p
        assert result.paths == ["a"]

    def test_pipeline_composition_preserves_order(self) -> None:
        """Test that composition preserves step order."""
        p1 = Pipeline([Step(path="1"), Step(path="2")])
        p2 = Pipeline([Step(path="3"), Step(path="4")])

        result = p1 >> p2

        assert result.paths == ["1", "2", "3", "4"]


# =============================================================================
# Integration-Style Tests
# =============================================================================


class TestPipelineIntegration:
    """Integration-style tests for pipeline workflows."""

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_analyze_capture_document_workflow(self, mock_observer: MagicMock) -> None:
        """Test a realistic analyze -> capture -> document workflow."""
        # Simulate a workflow where:
        # 1. Analyze returns insights
        # 2. Capture stores the insights
        # 3. Document generates docs

        results = [
            {"insights": ["Pattern A", "Pattern B"], "issues": 2},
            {"crystal_id": "cry_123", "stored": True},
            {"doc_path": "/docs/output.md", "generated": True},
        ]
        result_idx = 0

        logos = MagicMock()

        async def mock_invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal result_idx
            r = results[result_idx]
            result_idx += 1
            return r

        logos.invoke = mock_invoke
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        pipeline = (
            step("world.gestalt.analyze", target="services/")
            >> step("self.memory.capture")
            >> step("world.forge.document")
        )

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True
        assert len(result.step_results) == 3
        assert result.final_result == {"doc_path": "/docs/output.md", "generated": True}

    @pytest.mark.asyncio
    async def test_conditional_fix_workflow(self, mock_observer: MagicMock) -> None:
        """Test a workflow with conditional fixing."""
        # Simulate: analyze -> fix if issues -> capture result

        logos = MagicMock()
        call_count = 0

        async def mock_invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"issues": 3}  # Analysis finds issues
            elif call_count == 2:
                return {"fixed": 3}  # Fix applies
            else:
                return {"captured": True}

        logos.invoke = mock_invoke
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        pipeline = Pipeline(
            [
                step("world.gestalt.analyze"),
                branch(
                    condition=lambda r: r.get("issues", 0) > 0,
                    if_true=step("world.forge.fix"),
                    if_false=step("self.memory.capture", content="No issues"),
                ),
            ]
        )

        runner = PipelineRunner(invoker=invoker, observer=mock_observer)
        result = await runner.run(pipeline)

        assert result.success is True
        # Should have run analyze, then fix (not capture)
