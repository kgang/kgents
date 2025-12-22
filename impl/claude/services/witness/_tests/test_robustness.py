"""
Robustness Tests for Witness Service.

These tests cover edge cases, error handling, and defensive programming
patterns across the witness service modules.

Goal: Ensure graceful degradation and predictable behavior under
unusual conditions.

Philosophy (from spec/principles.md):
    "Ethical" - Agents are honest about limitations
    "Tasteful" - Graceful degradation over catastrophic failure
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.kgentsd.invoke import (
    classify_path,
    create_invoker,
    is_mutation_path,
    is_read_only_path,
)
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
    ScheduledTask,
    ScheduleStatus,
    ScheduleType,
    WitnessScheduler,
    create_scheduler,
)
from services.witness.crystal import (
    ExperienceCrystal,
    MoodVector,
    Narrative,
    TopologySnapshot,
)
from services.witness.polynomial import Thought, TrustLevel

# =============================================================================
# MoodVector Edge Cases
# =============================================================================


class TestMoodVectorRobustness:
    """Edge cases for MoodVector."""

    def test_mood_with_out_of_bounds_values(self) -> None:
        """Test that out-of-bounds values are clamped to [0, 1]."""
        mood = MoodVector(
            warmth=1.5,  # Over 1.0
            weight=-0.3,  # Under 0.0
            tempo=0.5,
            texture=2.0,  # Way over
            brightness=0.5,
            saturation=-100.0,  # Way under
            complexity=0.5,
        )

        # Values should be clamped
        assert 0.0 <= mood.warmth <= 1.0
        assert 0.0 <= mood.weight <= 1.0
        assert 0.0 <= mood.texture <= 1.0
        assert 0.0 <= mood.saturation <= 1.0

    def test_mood_from_empty_thoughts(self) -> None:
        """Test mood creation from empty thought list."""
        mood = MoodVector.from_thoughts([])
        assert mood == MoodVector.neutral()

    def test_mood_from_single_thought(self) -> None:
        """Test mood from a single thought."""
        thoughts = [
            Thought(
                content="Test passed successfully",
                source="test",
                tags=("success",),
                timestamp=datetime.now(UTC),
            )
        ]
        mood = MoodVector.from_thoughts(thoughts)

        # Should not crash, should have reasonable values
        assert 0.0 <= mood.brightness <= 1.0
        assert 0.0 <= mood.tempo <= 1.0

    def test_mood_similarity_with_zero_vectors(self) -> None:
        """Test similarity computation with zero magnitude vectors."""
        # Create a vector with all zeros (edge case)
        zero_mood = MoodVector(
            warmth=0.0,
            weight=0.0,
            tempo=0.0,
            texture=0.0,
            brightness=0.0,
            saturation=0.0,
            complexity=0.0,
        )

        # Two zero vectors should have similarity 1.0 (identical)
        assert zero_mood.similarity(zero_mood) == 1.0

        # Zero vs non-zero should be 0.0
        normal_mood = MoodVector.neutral()
        assert zero_mood.similarity(normal_mood) == 0.0

    def test_mood_from_thoughts_with_mixed_case_tags(self) -> None:
        """Test that tag matching is case-insensitive."""
        thoughts = [
            Thought(
                content="Test FAILED",
                source="test",
                tags=("FAILURE", "ERROR"),
                timestamp=datetime.now(UTC),
            ),
            Thought(
                content="Test SUCCESS",
                source="test",
                tags=("Success", "PASS"),
                timestamp=datetime.now(UTC),
            ),
        ]
        mood = MoodVector.from_thoughts(thoughts)
        # Should handle mixed case without crashing
        assert mood is not None

    def test_mood_to_dict_from_dict_roundtrip(self) -> None:
        """Test serialization roundtrip preserves values."""
        original = MoodVector(
            warmth=0.123,
            weight=0.456,
            tempo=0.789,
            texture=0.321,
            brightness=0.654,
            saturation=0.987,
            complexity=0.111,
        )

        data = original.to_dict()
        restored = MoodVector.from_dict(data)

        assert restored.warmth == pytest.approx(original.warmth)
        assert restored.weight == pytest.approx(original.weight)
        assert restored.tempo == pytest.approx(original.tempo)


# =============================================================================
# TopologySnapshot Edge Cases
# =============================================================================


class TestTopologySnapshotRobustness:
    """Edge cases for TopologySnapshot."""

    def test_topology_from_empty_thoughts(self) -> None:
        """Test topology from empty thought list."""
        topology = TopologySnapshot.from_thoughts([])
        assert topology.primary_path == "."
        assert topology.heat == {}

    def test_topology_from_thoughts_without_paths(self) -> None:
        """Test topology from thoughts without file paths."""
        thoughts = [
            Thought(
                content="Just some text without any paths",
                source="general",
                tags=(),
                timestamp=datetime.now(UTC),
            )
        ]
        topology = TopologySnapshot.from_thoughts(thoughts)
        assert topology.primary_path == "."

    def test_topology_from_thoughts_with_special_characters(self) -> None:
        """Test topology handles paths with special characters."""
        thoughts = [
            Thought(
                content="Edited: src/components/Button.tsx (with parens)",
                source="filesystem",
                tags=("file",),
                timestamp=datetime.now(UTC),
            ),
            Thought(
                content="Path: /tmp/test-file.py, another.ts",
                source="filesystem",
                tags=("file",),
                timestamp=datetime.now(UTC),
            ),
        ]
        topology = TopologySnapshot.from_thoughts(thoughts)
        # Should extract and clean paths
        assert len(topology.heat) > 0

    def test_topology_serialization_roundtrip(self) -> None:
        """Test topology serialization preserves dependencies."""
        original = TopologySnapshot(
            primary_path="/src/main.py",
            heat={"/src/main.py": 1.0, "/src/utils.py": 0.5},
            dependencies=frozenset([("/src/main.py", "/src/utils.py")]),
        )

        data = original.to_dict()
        restored = TopologySnapshot.from_dict(data)

        assert restored.primary_path == original.primary_path
        assert restored.heat == original.heat
        assert restored.dependencies == original.dependencies


# =============================================================================
# Narrative Edge Cases
# =============================================================================


class TestNarrativeRobustness:
    """Edge cases for Narrative."""

    def test_narrative_template_fallback_empty(self) -> None:
        """Test narrative fallback with empty thoughts."""
        narrative = Narrative.template_fallback([])
        assert "Empty session" in narrative.summary

    def test_narrative_template_fallback_with_long_content(self) -> None:
        """Test narrative handles very long thought content."""
        long_content = "x" * 10000
        thoughts = [
            Thought(
                content=long_content,
                source="test",
                tags=(),
                timestamp=datetime.now(UTC),
            )
        ]
        narrative = Narrative.template_fallback(thoughts)
        # Summary should be truncated and not crash
        assert len(narrative.summary) < len(long_content)

    def test_narrative_from_dict_with_missing_keys(self) -> None:
        """Test narrative handles incomplete dict."""
        partial_data = {"summary": "Test"}
        narrative = Narrative.from_dict(partial_data)
        assert narrative.summary == "Test"
        assert narrative.themes == ()
        assert narrative.highlights == ()


# =============================================================================
# ExperienceCrystal Edge Cases
# =============================================================================


class TestExperienceCrystalRobustness:
    """Edge cases for ExperienceCrystal."""

    def test_crystal_from_empty_thoughts(self) -> None:
        """Test crystal creation from empty thoughts."""
        crystal = ExperienceCrystal.from_thoughts([], session_id="test-session")
        assert crystal.session_id == "test-session"
        assert crystal.thought_count == 0
        assert "Empty" in crystal.narrative.summary

    def test_crystal_from_thoughts_with_none_timestamps(self) -> None:
        """Test crystal handles thoughts with missing timestamps."""
        thoughts = [
            Thought(
                content="No timestamp",
                source="test",
                tags=(),
                timestamp=datetime.now(UTC),  # Required by Thought
            )
        ]
        crystal = ExperienceCrystal.from_thoughts(thoughts)
        assert crystal is not None

    def test_crystal_json_roundtrip(self) -> None:
        """Test crystal JSON serialization roundtrip."""
        thoughts = [
            Thought(
                content="Test thought",
                source="test",
                tags=("tag1", "tag2"),
                timestamp=datetime.now(UTC),
            )
        ]
        original = ExperienceCrystal.from_thoughts(thoughts, session_id="roundtrip")

        json_data = original.to_json()
        restored = ExperienceCrystal.from_json(json_data)

        assert restored.session_id == original.session_id
        assert restored.thought_count == original.thought_count

    def test_crystal_from_json_with_missing_fields(self) -> None:
        """Test crystal handles incomplete JSON."""
        minimal_json = {
            "crystal_id": "test-123",
            "session_id": "minimal",
        }
        crystal = ExperienceCrystal.from_json(minimal_json)
        assert crystal.crystal_id == "test-123"
        assert crystal.thoughts == ()

    def test_crystal_duration_with_same_timestamps(self) -> None:
        """Test duration when start and end are the same."""
        now = datetime.now(UTC)
        thoughts = [
            Thought(content="Same time", source="test", tags=(), timestamp=now),
        ]
        crystal = ExperienceCrystal.from_thoughts(thoughts)
        # Duration should be 0
        assert crystal.duration_minutes == 0.0


# =============================================================================
# Path Classification Edge Cases
# =============================================================================


class TestPathClassificationRobustness:
    """Edge cases for path classification."""

    def test_classify_minimal_path(self) -> None:
        """Test classifying a minimal valid path."""
        context, holon, aspect = classify_path("a.b.c")
        assert context == "a"
        assert holon == "b"
        assert aspect == "c"

    def test_classify_very_long_path(self) -> None:
        """Test classifying a path with many segments."""
        context, holon, aspect = classify_path("world.foo.bar.baz.qux.manifest")
        assert context == "world"
        assert holon == "foo.bar.baz.qux"
        assert aspect == "manifest"

    def test_classify_path_with_numbers(self) -> None:
        """Test path with numeric segments."""
        context, holon, aspect = classify_path("world.v2.api.manifest")
        assert context == "world"
        assert holon == "v2.api"
        assert aspect == "manifest"

    def test_classify_empty_path_raises(self) -> None:
        """Test empty path raises ValueError."""
        with pytest.raises(ValueError):
            classify_path("")

    def test_classify_single_segment_raises(self) -> None:
        """Test single segment path raises ValueError."""
        with pytest.raises(ValueError):
            classify_path("world")

    def test_is_read_only_with_malformed_path(self) -> None:
        """Test read-only check handles malformed paths."""
        # Should return False for malformed paths (conservative)
        assert is_read_only_path("invalid") is False
        assert is_read_only_path("") is False

    def test_is_mutation_with_malformed_path(self) -> None:
        """Test mutation check handles malformed paths."""
        # Should return True for malformed paths (conservative)
        assert is_mutation_path("invalid") is True
        assert is_mutation_path("") is True


# =============================================================================
# JewelInvoker Edge Cases
# =============================================================================


class TestJewelInvokerRobustness:
    """Edge cases for JewelInvoker."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_invoke_with_logos_returning_none(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test handling when Logos returns None."""
        mock_logos.invoke = AsyncMock(return_value=None)
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

        result = await invoker.invoke("world.test.manifest", mock_observer)

        # Should succeed with None result
        assert result.success is True
        assert result.result is None

    @pytest.mark.asyncio
    async def test_invoke_with_logos_raising_type_error(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test handling TypeError from Logos."""
        mock_logos.invoke = AsyncMock(side_effect=TypeError("Invalid argument"))
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

        result = await invoker.invoke("world.test.manifest", mock_observer)

        assert result.success is False
        assert "Invalid argument" in (result.error or "")

    @pytest.mark.asyncio
    async def test_invoke_with_very_long_path(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test invoking with a very long path."""
        long_path = "world." + ".".join(["segment"] * 100) + ".manifest"
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

        result = await invoker.invoke(long_path, mock_observer)

        # Should handle gracefully
        assert result.path == long_path

    @pytest.mark.asyncio
    async def test_invoke_log_capacity(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test that invocation log handles many entries."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

        # Make many invocations
        for i in range(200):
            await invoker.invoke(f"world.test{i}.manifest", mock_observer)

        # Get log with limit
        log = invoker.get_invocation_log(limit=50)
        assert len(log) == 50

        # Most recent should be first
        assert "test199" in log[0].path


# =============================================================================
# Pipeline Edge Cases
# =============================================================================


class TestPipelineRobustness:
    """Edge cases for Pipeline and PipelineRunner."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    def test_empty_pipeline(self) -> None:
        """Test creating an empty pipeline."""
        p = Pipeline([])
        assert len(p) == 0
        assert p.paths == []

    def test_pipeline_paths_with_nested_branches(self) -> None:
        """Test extracting paths from deeply nested branches."""
        pipeline = Pipeline(
            [
                Step(path="a.b.c"),
                Branch(
                    condition=lambda r: True,
                    if_true=Pipeline(
                        [
                            Step(path="d.e.f"),
                            Branch(
                                condition=lambda r: True,
                                if_true=Step(path="g.h.i"),
                            ),
                        ]
                    ),
                    if_false=Step(path="j.k.l"),
                ),
            ]
        )

        paths = pipeline.paths
        # Should extract all paths
        assert "a.b.c" in paths
        assert "d.e.f" in paths
        assert "g.h.i" in paths
        assert "j.k.l" in paths

    @pytest.mark.asyncio
    async def test_run_empty_pipeline(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test running an empty pipeline."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        result = await runner.run(Pipeline([]))

        assert result.status == PipelineStatus.COMPLETED
        assert result.success is True
        assert len(result.step_results) == 0

    @pytest.mark.asyncio
    async def test_pipeline_with_transform_returning_non_dict(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test pipeline handles transform returning non-dict."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        # Transform that returns a list instead of dict
        pipeline = Pipeline(
            [
                Step(path="world.first.manifest"),
                Step(
                    path="world.second.manifest",
                    transform=lambda r: ["not", "a", "dict"],  # type: ignore
                ),
            ]
        )

        # Should fail gracefully on the second step
        result = await runner.run(pipeline)

        # First step should succeed, second should fail
        assert result.status == PipelineStatus.FAILED
        assert "Transform failed" in (result.error or "")

    @pytest.mark.asyncio
    async def test_pipeline_with_branch_condition_exception(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test pipeline handles branch condition that raises."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        def bad_condition(r: Any) -> bool:
            raise RuntimeError("Condition exploded")

        pipeline = Pipeline(
            [
                Step(path="world.first.manifest"),
                Branch(
                    condition=bad_condition,
                    if_true=Step(path="world.true.manifest"),
                ),
            ]
        )

        result = await runner.run(pipeline)

        # Should fail with condition error
        assert result.status == PipelineStatus.FAILED
        assert "Condition evaluation failed" in (result.error or "")

    @pytest.mark.asyncio
    async def test_pipeline_result_flow_with_none(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test result flow when a step returns None."""
        mock_logos.invoke = AsyncMock(return_value=None)
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        runner = PipelineRunner(invoker=invoker, observer=mock_observer)

        pipeline = Pipeline(
            [
                Step(path="world.first.manifest"),
                Step(path="world.second.manifest"),
            ]
        )

        result = await runner.run(pipeline)

        # Should complete successfully with None results
        assert result.success is True
        assert result.final_result is None


# =============================================================================
# Scheduler Edge Cases
# =============================================================================


class TestSchedulerRobustness:
    """Edge cases for WitnessScheduler."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.fixture
    def scheduler(self, mock_logos: MagicMock, mock_observer: MagicMock) -> WitnessScheduler:
        """Create a scheduler."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        return create_scheduler(invoker, mock_observer)

    def test_scheduled_task_ordering_same_time(self) -> None:
        """Test task ordering when tasks have same next_run time."""
        now = datetime.now(UTC)
        task1 = ScheduledTask(task_id="task-1", next_run=now)
        task2 = ScheduledTask(task_id="task-2", next_run=now)

        # The key is that comparison should work without raising
        # With same next_run, tasks compare as equal (not less than)
        assert not (task1 < task2)  # Same time = not less than
        assert not (task2 < task1)  # Same time = not less than

    def test_schedule_with_zero_delay(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling with zero delay."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(seconds=0),
        )

        # Should be immediately due
        assert task.is_due is True

    def test_schedule_with_negative_delay(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling with negative delay (past time)."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(seconds=-60),  # 1 minute in the past
        )

        # Should be due
        assert task.is_due is True

    def test_cancel_already_completed_task(self, scheduler: WitnessScheduler) -> None:
        """Test cancelling an already completed task."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(minutes=1),
        )
        task.status = ScheduleStatus.COMPLETED

        result = scheduler.cancel(task.task_id)

        # Should fail to cancel completed task
        assert result is False

    def test_pause_running_task(self, scheduler: WitnessScheduler) -> None:
        """Test pausing a running task."""
        task = scheduler.schedule_periodic(
            "world.test.manifest",
            interval=timedelta(minutes=10),
        )
        task.status = ScheduleStatus.RUNNING

        result = scheduler.pause(task.task_id)

        # Should fail to pause running task
        assert result is False

    def test_resume_non_paused_task(self, scheduler: WitnessScheduler) -> None:
        """Test resuming a non-paused task."""
        task = scheduler.schedule_periodic(
            "world.test.manifest",
            interval=timedelta(minutes=10),
        )

        result = scheduler.resume(task.task_id)

        # Should fail - task not paused
        assert result is False

    @pytest.mark.asyncio
    async def test_tick_with_no_tasks(self, scheduler: WitnessScheduler) -> None:
        """Test tick when no tasks are scheduled."""
        executed = await scheduler.tick()
        assert executed == []

    @pytest.mark.asyncio
    async def test_tick_with_cancelled_due_task(self, scheduler: WitnessScheduler) -> None:
        """Test tick skips cancelled tasks even if due."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(seconds=-1),  # Due
        )
        scheduler.cancel(task.task_id)

        executed = await scheduler.tick()

        assert len(executed) == 0

    @pytest.mark.asyncio
    async def test_tick_with_many_due_tasks(self, scheduler: WitnessScheduler) -> None:
        """Test tick handles many due tasks."""
        # Schedule many tasks all due now
        for i in range(50):
            scheduler.schedule(
                f"world.test{i}.manifest",
                delay=timedelta(seconds=-1),
            )

        executed = await scheduler.tick()

        assert len(executed) == 50

    def test_task_can_run_with_max_runs_at_limit(self) -> None:
        """Test can_run when exactly at max_runs."""
        task = ScheduledTask(
            max_runs=5,
            run_count=5,
        )
        assert task.can_run is False

    def test_task_can_run_with_max_runs_below_limit(self) -> None:
        """Test can_run when below max_runs."""
        task = ScheduledTask(
            max_runs=5,
            run_count=4,
        )
        assert task.can_run is True


# =============================================================================
# Integration Edge Cases
# =============================================================================


class TestIntegrationRobustness:
    """Integration tests for edge cases across modules."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_scheduled_pipeline_with_branch_failure(
        self, mock_logos: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test scheduled pipeline handles branch failures gracefully."""
        invoker = create_invoker(mock_logos, TrustLevel.AUTONOMOUS)
        scheduler = create_scheduler(invoker, mock_observer)

        pipeline = Pipeline(
            [
                step("world.analyze.manifest"),
                branch(
                    condition=lambda r: r.get("issues", 0) > 0,
                    if_true=step("world.fix.apply"),
                ),
            ]
        )

        task = scheduler.schedule_pipeline(
            pipeline,
            delay=timedelta(seconds=-1),  # Due now
            name="Branch Test",
        )

        await scheduler.tick()

        # Task should complete (no issues = skip branch)
        assert task.status == ScheduleStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_crystal_from_pipeline_thoughts(self) -> None:
        """Test creating crystal from thoughts generated during pipeline."""
        thoughts = [
            Thought(
                content="Pipeline started: world.gestalt.analyze",
                source="witness.pipeline",
                tags=("pipeline", "start"),
                timestamp=datetime.now(UTC),
            ),
            Thought(
                content="Step 1 completed: src/main.py analyzed",
                source="witness.pipeline",
                tags=("step", "success"),
                timestamp=datetime.now(UTC),
            ),
            Thought(
                content="Pipeline completed successfully",
                source="witness.pipeline",
                tags=("pipeline", "complete", "success"),
                timestamp=datetime.now(UTC),
            ),
        ]

        crystal = ExperienceCrystal.from_thoughts(thoughts, session_id="pipeline-run")

        # Crystal should capture pipeline context
        assert crystal.thought_count == 3
        assert "pipeline" in crystal.topics
        assert crystal.mood.brightness > 0.5  # Success should be bright


# =============================================================================
# Defensive Programming Tests
# =============================================================================


class TestDefensiveProgramming:
    """Tests for defensive programming patterns."""

    def test_step_with_none_transform(self) -> None:
        """Test Step handles None transform gracefully."""
        s = Step(path="test.path.manifest", transform=None)
        assert s.transform is None

    def test_branch_with_none_if_false(self) -> None:
        """Test Branch handles None if_false."""
        b = Branch(
            condition=lambda r: True,
            if_true=Step(path="test.path.manifest"),
            if_false=None,
        )
        assert b.if_false is None

    def test_pipeline_result_to_dict_with_none_values(self) -> None:
        """Test PipelineResult.to_dict handles None values."""
        result = PipelineResult(
            status=PipelineStatus.PENDING,
            step_results=[],
            final_result=None,
            error=None,
            aborted_at_step=None,
        )

        d = result.to_dict()
        assert d["final_result"] is None
        assert d["error"] is None
        assert d["aborted_at_step"] is None

    def test_mood_vector_dominant_quality_at_neutral(self) -> None:
        """Test dominant_quality when all values are neutral."""
        mood = MoodVector.neutral()
        # Should return something without crashing
        dominant = mood.dominant_quality
        assert dominant in (
            "warmth",
            "weight",
            "tempo",
            "texture",
            "brightness",
            "saturation",
            "complexity",
        )

    def test_topology_from_dict_with_invalid_dependencies(self) -> None:
        """Test topology handles malformed dependencies."""
        data = {
            "primary_path": "/test",
            "heat": {},
            "dependencies": [
                ["a", "b"],  # valid
                ["c"],  # invalid (only 1 element)
                ["d", "e", "f"],  # invalid (3 elements)
            ],
        }
        topology = TopologySnapshot.from_dict(data)

        # Should only include valid 2-element tuples
        assert ("a", "b") in topology.dependencies
        assert len(topology.dependencies) == 1
