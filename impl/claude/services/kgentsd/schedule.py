"""
Witness Scheduler: Temporal Composition for Cross-Jewel Workflows.

"The daemon runs continuously; the scheduler awakens when needed."

The Scheduler enables time-based workflows:
- Delayed invocations: "Run this pipeline in 5 minutes"
- Periodic tasks: "Check CI status every 10 minutes"
- Event-contingent schedules: "When tests pass, schedule deploy"

This is the `time.witness.schedule` aspect of AGENTESE—turning
ephemeral commands into persistent intentions.

Key Patterns (from spec/principles.md):
- Heterarchical: Scheduled tasks can trigger new schedules
- Composable: Schedules compose with pipelines via >>

Philosophy:
    A schedule is a morphism from Now → Future.
    The scheduler is an async monad that unfolds time.

See: plans/kgentsd-cross-jewel.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

from .invoke import JewelInvoker
from .pipeline import Pipeline, PipelineResult, PipelineRunner, Step

if TYPE_CHECKING:
    from protocols.agentese.node import Observer


logger = logging.getLogger(__name__)


# =============================================================================
# Schedule Types
# =============================================================================


class ScheduleType(Enum):
    """Type of schedule."""

    ONCE = auto()  # Run once at specified time
    PERIODIC = auto()  # Repeat at intervals
    DELAYED = auto()  # Run after delay from now


class ScheduleStatus(Enum):
    """Status of a scheduled task."""

    PENDING = auto()  # Waiting to run
    RUNNING = auto()  # Currently executing
    COMPLETED = auto()  # Finished successfully
    FAILED = auto()  # Execution failed
    CANCELLED = auto()  # Cancelled before execution
    PAUSED = auto()  # Temporarily paused (for periodic)


# =============================================================================
# Scheduled Task
# =============================================================================


@dataclass
class ScheduledTask:
    """
    A task scheduled for future execution.

    Captures:
    - WHAT to run (pipeline or single step)
    - WHEN to run (next execution time)
    - HOW often (for periodic tasks)
    - WHO scheduled it (observer context)

    Immutable after creation except for status and execution count.
    """

    task_id: str = field(default_factory=lambda: f"sched-{uuid4().hex[:12]}")
    name: str = ""
    description: str = ""

    # What to run
    pipeline: Pipeline | None = None
    path: str = ""  # For single invocations
    kwargs: dict[str, Any] = field(default_factory=dict)

    # When to run
    schedule_type: ScheduleType = ScheduleType.ONCE
    next_run: datetime = field(default_factory=lambda: datetime.now(UTC))
    interval: timedelta | None = None  # For periodic tasks
    max_runs: int | None = None  # None = infinite for periodic

    # State
    status: ScheduleStatus = ScheduleStatus.PENDING
    run_count: int = 0
    last_result: PipelineResult | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_run_at: datetime | None = None

    # Context
    observer_archetype: str = ""  # Preserved from scheduling observer
    tags: frozenset[str] = field(default_factory=frozenset)

    def __lt__(self, other: ScheduledTask) -> bool:
        """Enable heapq ordering by next_run time."""
        return self.next_run < other.next_run

    @property
    def is_due(self) -> bool:
        """Check if task is due for execution."""
        return self.next_run <= datetime.now(UTC) and self.status == ScheduleStatus.PENDING

    @property
    def is_active(self) -> bool:
        """Check if task is still active (pending or running)."""
        return self.status in (ScheduleStatus.PENDING, ScheduleStatus.RUNNING)

    @property
    def can_run(self) -> bool:
        """Check if task can run (not cancelled, not paused)."""
        if self.status in (ScheduleStatus.CANCELLED, ScheduleStatus.PAUSED):
            return False
        if self.max_runs and self.run_count >= self.max_runs:
            return False
        return True

    def advance_periodic(self) -> None:
        """Advance next_run for periodic tasks."""
        if self.schedule_type == ScheduleType.PERIODIC and self.interval:
            self.next_run = datetime.now(UTC) + self.interval
            if self.can_run:
                self.status = ScheduleStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "kwargs": self.kwargs,
            "schedule_type": self.schedule_type.name,
            "next_run": self.next_run.isoformat(),
            "interval_seconds": self.interval.total_seconds() if self.interval else None,
            "max_runs": self.max_runs,
            "status": self.status.name,
            "run_count": self.run_count,
            "created_at": self.created_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "observer_archetype": self.observer_archetype,
            "tags": list(self.tags),
        }


# =============================================================================
# Scheduler
# =============================================================================


@dataclass
class WitnessScheduler:
    """
    The Witness's temporal execution engine.

    Maintains a priority queue of scheduled tasks, executing them
    when their time comes. Integrates with JewelInvoker for trust-gated
    execution.

    Features:
    - Delayed execution: schedule(delay=timedelta(minutes=5))
    - Periodic tasks: schedule_periodic(interval=timedelta(hours=1))
    - Pipeline scheduling: schedule_pipeline(pipeline)
    - Task management: pause, resume, cancel

    Pattern: "Container Owns Workflow" (crown-jewel-patterns.md)
    The scheduler owns the lifecycle of scheduled tasks.

    Example:
        scheduler = WitnessScheduler(invoker, observer)

        # Schedule a delayed check
        task = scheduler.schedule_delayed(
            "world.gestalt.analyze",
            delay=timedelta(minutes=5),
            kwargs={"target": "src/"},
        )

        # Schedule periodic CI checks
        scheduler.schedule_periodic(
            "world.ci.status",
            interval=timedelta(minutes=10),
            name="CI Monitor",
        )

        # Start the scheduler loop
        await scheduler.run()
    """

    invoker: JewelInvoker
    observer: "Observer"
    _tasks: list[ScheduledTask] = field(default_factory=list)
    _task_map: dict[str, ScheduledTask] = field(default_factory=dict)
    _running: bool = False
    _tick_interval: float = 1.0  # Seconds between queue checks
    max_concurrent: int = 5  # Max concurrent task executions
    log_executions: bool = True

    def schedule(
        self,
        path: str,
        at: datetime | None = None,
        delay: timedelta | None = None,
        name: str = "",
        description: str = "",
        tags: frozenset[str] | None = None,
        **kwargs: Any,
    ) -> ScheduledTask:
        """
        Schedule a single AGENTESE invocation.

        Args:
            path: AGENTESE path (e.g., "world.gestalt.analyze")
            at: Specific datetime to run (UTC)
            delay: Delay from now (alternative to `at`)
            name: Human-readable task name
            description: Task description
            tags: Tags for categorization
            **kwargs: Arguments for the invocation

        Returns:
            The created ScheduledTask

        Raises:
            ValueError: If neither `at` nor `delay` provided
        """
        if at is None and delay is None:
            raise ValueError("Must provide either 'at' datetime or 'delay' timedelta")

        next_run = at if at else datetime.now(UTC) + delay  # type: ignore

        task = ScheduledTask(
            name=name or f"Invoke {path}",
            description=description,
            path=path,
            kwargs=kwargs,
            schedule_type=ScheduleType.DELAYED if delay else ScheduleType.ONCE,
            next_run=next_run,
            observer_archetype=getattr(self.observer, "archetype", ""),
            tags=tags or frozenset(),
        )

        self._add_task(task)
        return task

    def schedule_pipeline(
        self,
        pipeline: Pipeline,
        at: datetime | None = None,
        delay: timedelta | None = None,
        name: str = "",
        description: str = "",
        tags: frozenset[str] | None = None,
        initial_kwargs: dict[str, Any] | None = None,
    ) -> ScheduledTask:
        """
        Schedule a pipeline for future execution.

        Args:
            pipeline: The Pipeline to execute
            at: Specific datetime to run (UTC)
            delay: Delay from now
            name: Human-readable task name
            description: Task description
            tags: Tags for categorization
            initial_kwargs: Initial arguments for the pipeline

        Returns:
            The created ScheduledTask
        """
        if at is None and delay is None:
            raise ValueError("Must provide either 'at' datetime or 'delay' timedelta")

        next_run = at if at else datetime.now(UTC) + delay  # type: ignore

        task = ScheduledTask(
            name=name or f"Pipeline ({len(pipeline)} steps)",
            description=description,
            pipeline=pipeline,
            kwargs=initial_kwargs or {},
            schedule_type=ScheduleType.DELAYED if delay else ScheduleType.ONCE,
            next_run=next_run,
            observer_archetype=getattr(self.observer, "archetype", ""),
            tags=tags or frozenset(),
        )

        self._add_task(task)
        return task

    def schedule_periodic(
        self,
        path: str,
        interval: timedelta,
        name: str = "",
        description: str = "",
        max_runs: int | None = None,
        start_immediately: bool = False,
        tags: frozenset[str] | None = None,
        **kwargs: Any,
    ) -> ScheduledTask:
        """
        Schedule a periodic invocation.

        Args:
            path: AGENTESE path to invoke
            interval: Time between invocations
            name: Human-readable task name
            description: Task description
            max_runs: Maximum number of runs (None = infinite)
            start_immediately: If True, first run is now; else after interval
            tags: Tags for categorization
            **kwargs: Arguments for the invocation

        Returns:
            The created ScheduledTask
        """
        next_run = datetime.now(UTC) if start_immediately else datetime.now(UTC) + interval

        task = ScheduledTask(
            name=name or f"Periodic: {path}",
            description=description,
            path=path,
            kwargs=kwargs,
            schedule_type=ScheduleType.PERIODIC,
            next_run=next_run,
            interval=interval,
            max_runs=max_runs,
            observer_archetype=getattr(self.observer, "archetype", ""),
            tags=tags or frozenset(),
        )

        self._add_task(task)
        return task

    def _add_task(self, task: ScheduledTask) -> None:
        """Add task to the queue."""
        heapq.heappush(self._tasks, task)
        self._task_map[task.task_id] = task

        if self.log_executions:
            logger.info(
                f"Scheduled task {task.task_id}: {task.name}, next_run={task.next_run.isoformat()}"
            )

    def get_task(self, task_id: str) -> ScheduledTask | None:
        """Get a task by ID."""
        return self._task_map.get(task_id)

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Returns True if cancelled, False if task not found.
        """
        task = self._task_map.get(task_id)
        if task and task.status in (ScheduleStatus.PENDING, ScheduleStatus.PAUSED):
            task.status = ScheduleStatus.CANCELLED
            return True
        return False

    def pause(self, task_id: str) -> bool:
        """Pause a periodic task."""
        task = self._task_map.get(task_id)
        if task and task.schedule_type == ScheduleType.PERIODIC:
            if task.status == ScheduleStatus.PENDING:
                task.status = ScheduleStatus.PAUSED
                return True
        return False

    def resume(self, task_id: str) -> bool:
        """Resume a paused task."""
        task = self._task_map.get(task_id)
        if task and task.status == ScheduleStatus.PAUSED:
            task.status = ScheduleStatus.PENDING
            task.next_run = datetime.now(UTC)
            heapq.heappush(self._tasks, task)
            return True
        return False

    async def tick(self) -> list[ScheduledTask]:
        """
        Process all due tasks.

        Returns list of tasks that were executed.
        """
        executed: list[ScheduledTask] = []
        now = datetime.now(UTC)

        # Process all due tasks
        while self._tasks and self._tasks[0].next_run <= now:
            task = heapq.heappop(self._tasks)

            if not task.can_run:
                continue

            # Execute the task
            await self._execute_task(task)
            executed.append(task)

            # Re-queue periodic tasks
            if task.schedule_type == ScheduleType.PERIODIC and task.can_run:
                task.advance_periodic()
                heapq.heappush(self._tasks, task)

        return executed

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single task."""
        task.status = ScheduleStatus.RUNNING
        task.last_run_at = datetime.now(UTC)

        try:
            if task.pipeline:
                # Execute pipeline
                runner = PipelineRunner(
                    invoker=self.invoker,
                    observer=self.observer,
                    log_steps=self.log_executions,
                )
                result = await runner.run(task.pipeline, task.kwargs)
                task.last_result = result

                if result.success:
                    task.status = ScheduleStatus.COMPLETED
                else:
                    task.status = ScheduleStatus.FAILED

            elif task.path:
                # Execute single invocation
                inv_result = await self.invoker.invoke(task.path, self.observer, **task.kwargs)

                if inv_result.success:
                    task.status = ScheduleStatus.COMPLETED
                else:
                    task.status = ScheduleStatus.FAILED

            task.run_count += 1

            if self.log_executions:
                logger.info(
                    f"Executed task {task.task_id}: {task.name}, "
                    f"status={task.status.name}, run_count={task.run_count}"
                )

        except Exception as e:
            task.status = ScheduleStatus.FAILED
            logger.error(f"Task {task.task_id} failed: {e}")

    async def run(self) -> None:
        """
        Run the scheduler loop.

        Checks the queue every tick_interval seconds and executes due tasks.
        """
        self._running = True

        while self._running:
            await self.tick()
            await asyncio.sleep(self._tick_interval)

    def stop(self) -> None:
        """Stop the scheduler loop."""
        self._running = False

    @property
    def pending_tasks(self) -> list[ScheduledTask]:
        """Get all pending tasks."""
        return [t for t in self._task_map.values() if t.status == ScheduleStatus.PENDING]

    @property
    def active_tasks(self) -> list[ScheduledTask]:
        """Get all active (pending or running) tasks."""
        return [t for t in self._task_map.values() if t.is_active]

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        by_status: dict[str, int] = {}
        for task in self._task_map.values():
            status = task.status.name
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_tasks": len(self._task_map),
            "pending": len(self.pending_tasks),
            "active": len(self.active_tasks),
            "by_status": by_status,
            "running": self._running,
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_scheduler(
    invoker: JewelInvoker,
    observer: "Observer",
    tick_interval: float = 1.0,
    max_concurrent: int = 5,
) -> WitnessScheduler:
    """
    Create a WitnessScheduler instance.

    Args:
        invoker: The JewelInvoker for executing tasks
        observer: The observer context
        tick_interval: Seconds between queue checks
        max_concurrent: Maximum concurrent task executions

    Returns:
        Configured WitnessScheduler
    """
    return WitnessScheduler(
        invoker=invoker,
        observer=observer,
        _tick_interval=tick_interval,
        max_concurrent=max_concurrent,
    )


# =============================================================================
# Convenience Functions for Common Patterns
# =============================================================================


def delay(minutes: int = 0, seconds: int = 0, hours: int = 0) -> timedelta:
    """Create a timedelta for scheduling delays."""
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def every(minutes: int = 0, seconds: int = 0, hours: int = 0) -> timedelta:
    """Create a timedelta for periodic intervals."""
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "ScheduledTask",
    "ScheduleType",
    "ScheduleStatus",
    "WitnessScheduler",
    # Factory
    "create_scheduler",
    # Convenience
    "delay",
    "every",
]
