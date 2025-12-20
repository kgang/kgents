"""
Tests for Witness Scheduler (Phase 3C).

Tests the temporal composition system for scheduling cross-jewel
workflows in the future.

See: plans/kgentsd-cross-jewel.md
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.witness.invoke import create_invoker
from services.witness.pipeline import Pipeline, Step
from services.witness.polynomial import TrustLevel
from services.witness.schedule import (
    ScheduledTask,
    ScheduleStatus,
    ScheduleType,
    WitnessScheduler,
    create_scheduler,
    delay,
    every,
)

# =============================================================================
# ScheduledTask Tests
# =============================================================================


class TestScheduledTask:
    """Tests for ScheduledTask dataclass."""

    def test_task_creation(self) -> None:
        """Test creating a basic task."""
        task = ScheduledTask(
            name="Test Task",
            path="world.gestalt.analyze",
        )

        assert task.name == "Test Task"
        assert task.path == "world.gestalt.analyze"
        assert task.status == ScheduleStatus.PENDING
        assert task.run_count == 0

    def test_task_id_auto_generated(self) -> None:
        """Test that task IDs are auto-generated."""
        task1 = ScheduledTask(name="Task 1")
        task2 = ScheduledTask(name="Task 2")

        assert task1.task_id.startswith("sched-")
        assert task2.task_id.startswith("sched-")
        assert task1.task_id != task2.task_id

    def test_is_due_when_time_passed(self) -> None:
        """Test is_due returns True when next_run is in the past."""
        task = ScheduledTask(
            name="Due Task",
            next_run=datetime.now(UTC) - timedelta(minutes=1),
        )

        assert task.is_due is True

    def test_is_due_when_time_future(self) -> None:
        """Test is_due returns False when next_run is in the future."""
        task = ScheduledTask(
            name="Future Task",
            next_run=datetime.now(UTC) + timedelta(hours=1),
        )

        assert task.is_due is False

    def test_is_due_respects_status(self) -> None:
        """Test is_due only True for PENDING tasks."""
        task = ScheduledTask(
            name="Cancelled Task",
            next_run=datetime.now(UTC) - timedelta(minutes=1),
            status=ScheduleStatus.CANCELLED,
        )

        assert task.is_due is False

    def test_can_run_blocked_when_cancelled(self) -> None:
        """Test can_run returns False for cancelled tasks."""
        task = ScheduledTask(status=ScheduleStatus.CANCELLED)
        assert task.can_run is False

    def test_can_run_blocked_when_paused(self) -> None:
        """Test can_run returns False for paused tasks."""
        task = ScheduledTask(status=ScheduleStatus.PAUSED)
        assert task.can_run is False

    def test_can_run_blocked_when_max_runs_reached(self) -> None:
        """Test can_run returns False when max_runs exceeded."""
        task = ScheduledTask(max_runs=3, run_count=3)
        assert task.can_run is False

    def test_advance_periodic(self) -> None:
        """Test advance_periodic updates next_run."""
        interval = timedelta(minutes=10)
        task = ScheduledTask(
            schedule_type=ScheduleType.PERIODIC,
            interval=interval,
            next_run=datetime.now(UTC),
        )

        task.advance_periodic()

        # Next run should be in the future
        assert task.next_run > datetime.now(UTC)

    def test_task_ordering(self) -> None:
        """Test tasks can be compared for heapq ordering."""
        earlier = ScheduledTask(next_run=datetime.now(UTC))
        later = ScheduledTask(next_run=datetime.now(UTC) + timedelta(hours=1))

        assert earlier < later

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        task = ScheduledTask(
            name="Test",
            path="world.test.manifest",
            schedule_type=ScheduleType.PERIODIC,
            interval=timedelta(minutes=5),
            tags=frozenset(["ci", "monitor"]),
        )

        d = task.to_dict()

        assert d["name"] == "Test"
        assert d["path"] == "world.test.manifest"
        assert d["schedule_type"] == "PERIODIC"
        assert d["interval_seconds"] == 300
        assert set(d["tags"]) == {"ci", "monitor"}


# =============================================================================
# WitnessScheduler Tests
# =============================================================================


class TestWitnessScheduler:
    """Tests for WitnessScheduler class."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def mock_invoker(self, mock_logos: MagicMock) -> MagicMock:
        """Create a mock JewelInvoker."""
        return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        observer = MagicMock()
        observer.archetype = "developer"
        return observer

    @pytest.fixture
    def scheduler(self, mock_invoker: MagicMock, mock_observer: MagicMock) -> WitnessScheduler:
        """Create a WitnessScheduler."""
        return create_scheduler(mock_invoker, mock_observer)

    def test_schedule_with_delay(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling with a delay."""
        task = scheduler.schedule(
            "world.gestalt.analyze",
            delay=timedelta(minutes=5),
            name="Delayed Analysis",
        )

        assert task.name == "Delayed Analysis"
        assert task.schedule_type == ScheduleType.DELAYED
        assert task.next_run > datetime.now(UTC)
        assert task.status == ScheduleStatus.PENDING

    def test_schedule_with_at(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling at a specific time."""
        future_time = datetime.now(UTC) + timedelta(hours=2)
        task = scheduler.schedule(
            "world.gestalt.analyze",
            at=future_time,
            name="Scheduled Analysis",
        )

        assert task.schedule_type == ScheduleType.ONCE
        assert task.next_run == future_time

    def test_schedule_requires_time(self, scheduler: WitnessScheduler) -> None:
        """Test that schedule requires at or delay."""
        with pytest.raises(ValueError, match="Must provide"):
            scheduler.schedule("world.gestalt.analyze")

    def test_schedule_periodic(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling a periodic task."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
            name="CI Monitor",
            max_runs=5,
        )

        assert task.schedule_type == ScheduleType.PERIODIC
        assert task.interval == timedelta(minutes=10)
        assert task.max_runs == 5

    def test_schedule_periodic_start_immediately(self, scheduler: WitnessScheduler) -> None:
        """Test periodic task with immediate start."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
            start_immediately=True,
        )

        # Should be due now (or very close)
        assert abs((task.next_run - datetime.now(UTC)).total_seconds()) < 1

    def test_schedule_pipeline(self, scheduler: WitnessScheduler) -> None:
        """Test scheduling a pipeline."""
        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),
                Step(path="self.memory.capture"),
            ]
        )

        task = scheduler.schedule_pipeline(
            pipeline,
            delay=timedelta(minutes=5),
            name="Analysis Pipeline",
        )

        assert task.pipeline == pipeline
        assert task.name == "Analysis Pipeline"

    def test_get_task(self, scheduler: WitnessScheduler) -> None:
        """Test getting a task by ID."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(minutes=1),
        )

        retrieved = scheduler.get_task(task.task_id)
        assert retrieved == task

    def test_get_task_not_found(self, scheduler: WitnessScheduler) -> None:
        """Test getting a non-existent task."""
        assert scheduler.get_task("nonexistent") is None

    def test_cancel_task(self, scheduler: WitnessScheduler) -> None:
        """Test cancelling a task."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(minutes=1),
        )

        result = scheduler.cancel(task.task_id)

        assert result is True
        assert task.status == ScheduleStatus.CANCELLED

    def test_cancel_nonexistent_task(self, scheduler: WitnessScheduler) -> None:
        """Test cancelling a non-existent task."""
        result = scheduler.cancel("nonexistent")
        assert result is False

    def test_pause_periodic_task(self, scheduler: WitnessScheduler) -> None:
        """Test pausing a periodic task."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
        )

        result = scheduler.pause(task.task_id)

        assert result is True
        assert task.status == ScheduleStatus.PAUSED

    def test_pause_non_periodic_fails(self, scheduler: WitnessScheduler) -> None:
        """Test that pausing a non-periodic task fails."""
        task = scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(minutes=1),
        )

        result = scheduler.pause(task.task_id)
        assert result is False

    def test_resume_paused_task(self, scheduler: WitnessScheduler) -> None:
        """Test resuming a paused task."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
        )
        scheduler.pause(task.task_id)

        result = scheduler.resume(task.task_id)

        assert result is True
        assert task.status == ScheduleStatus.PENDING

    @pytest.mark.asyncio
    async def test_tick_executes_due_tasks(self, scheduler: WitnessScheduler) -> None:
        """Test that tick executes due tasks."""
        # Schedule a task in the past (immediately due)
        task = scheduler.schedule(
            "world.gestalt.manifest",
            delay=timedelta(seconds=-1),  # Already due
        )

        executed = await scheduler.tick()

        assert len(executed) == 1
        assert executed[0] == task
        assert task.status in (ScheduleStatus.COMPLETED, ScheduleStatus.FAILED)

    @pytest.mark.asyncio
    async def test_tick_skips_future_tasks(self, scheduler: WitnessScheduler) -> None:
        """Test that tick skips tasks not yet due."""
        scheduler.schedule(
            "world.test.manifest",
            delay=timedelta(hours=1),  # Far future
        )

        executed = await scheduler.tick()

        assert len(executed) == 0

    @pytest.mark.asyncio
    async def test_tick_requeues_periodic(self, scheduler: WitnessScheduler) -> None:
        """Test that tick requeues periodic tasks."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
            start_immediately=True,
        )
        # Make it immediately due
        task.next_run = datetime.now(UTC) - timedelta(seconds=1)

        await scheduler.tick()

        # Should be rescheduled
        assert task.run_count == 1
        assert task.next_run > datetime.now(UTC)

    @pytest.mark.asyncio
    async def test_tick_respects_max_runs(self, scheduler: WitnessScheduler) -> None:
        """Test that periodic tasks stop after max_runs."""
        task = scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),  # Non-zero interval
            start_immediately=True,
            max_runs=2,
        )
        task.next_run = datetime.now(UTC) - timedelta(seconds=1)

        # First run
        await scheduler.tick()
        assert task.run_count == 1

        # Make due again
        task.next_run = datetime.now(UTC) - timedelta(seconds=1)
        await scheduler.tick()
        assert task.run_count == 2

        # Should not run again (max_runs reached)
        task.next_run = datetime.now(UTC) - timedelta(seconds=1)
        await scheduler.tick()
        assert task.run_count == 2  # Still 2, respects max_runs

    def test_pending_tasks(self, scheduler: WitnessScheduler) -> None:
        """Test getting pending tasks."""
        scheduler.schedule("world.a.manifest", delay=timedelta(minutes=1))
        scheduler.schedule("world.b.manifest", delay=timedelta(minutes=1))
        cancelled = scheduler.schedule("world.c.manifest", delay=timedelta(minutes=1))
        scheduler.cancel(cancelled.task_id)

        pending = scheduler.pending_tasks
        assert len(pending) == 2

    def test_get_stats(self, scheduler: WitnessScheduler) -> None:
        """Test getting scheduler stats."""
        scheduler.schedule("world.a.manifest", delay=timedelta(minutes=1))
        scheduler.schedule("world.b.manifest", delay=timedelta(minutes=1))
        cancelled = scheduler.schedule("world.c.manifest", delay=timedelta(minutes=1))
        scheduler.cancel(cancelled.task_id)

        stats = scheduler.get_stats()

        assert stats["total_tasks"] == 3
        assert stats["pending"] == 2
        assert stats["by_status"]["PENDING"] == 2
        assert stats["by_status"]["CANCELLED"] == 1


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_delay_minutes(self) -> None:
        """Test delay() with minutes."""
        d = delay(minutes=5)
        assert d == timedelta(minutes=5)

    def test_delay_mixed(self) -> None:
        """Test delay() with mixed units."""
        d = delay(hours=1, minutes=30, seconds=15)
        assert d == timedelta(hours=1, minutes=30, seconds=15)

    def test_every_minutes(self) -> None:
        """Test every() for periodic intervals."""
        e = every(minutes=10)
        assert e == timedelta(minutes=10)

    def test_create_scheduler(self) -> None:
        """Test create_scheduler factory."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={})
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)
        observer = MagicMock()

        scheduler = create_scheduler(invoker, observer, tick_interval=2.0, max_concurrent=10)

        assert scheduler.invoker == invoker
        assert scheduler.observer == observer
        assert scheduler._tick_interval == 2.0
        assert scheduler.max_concurrent == 10


# =============================================================================
# Integration Tests
# =============================================================================


class TestSchedulerIntegration:
    """Integration-style tests for scheduler workflows."""

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_workflow_schedule_after_analysis(self, mock_observer: MagicMock) -> None:
        """Test scheduling a follow-up task after analysis."""
        results = [
            {"insights": ["Issue A", "Issue B"], "needs_fix": True},
            {"fixed": True},
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
        scheduler = create_scheduler(invoker, mock_observer)

        # Schedule analysis (due now)
        analysis = scheduler.schedule(
            "world.gestalt.analyze",
            delay=timedelta(seconds=-1),
            name="Analysis",
        )

        # Execute analysis
        await scheduler.tick()
        assert analysis.status == ScheduleStatus.COMPLETED

        # Based on result, schedule fix
        scheduler.schedule(
            "world.forge.fix",
            delay=timedelta(seconds=-1),
            name="Fix Issues",
        )

        # Execute fix
        executed = await scheduler.tick()
        assert len(executed) == 1
        assert executed[0].name == "Fix Issues"

    @pytest.mark.asyncio
    async def test_pipeline_scheduled_execution(self, mock_observer: MagicMock) -> None:
        """Test executing a scheduled pipeline."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"ok": True})
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)
        scheduler = create_scheduler(invoker, mock_observer)

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.manifest"),
                Step(path="self.memory.manifest"),
            ]
        )

        task = scheduler.schedule_pipeline(
            pipeline,
            delay=timedelta(seconds=-1),  # Due now
            name="Manifest Pipeline",
        )

        executed = await scheduler.tick()

        assert len(executed) == 1
        assert task.status == ScheduleStatus.COMPLETED
        assert task.last_result is not None
        assert task.last_result.success is True
