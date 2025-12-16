"""
WorkshopHistoryStore: In-memory task history for the Builder's Workshop.

Tracks completed tasks with their events, artifacts, and metrics.
Provides aggregate metrics computation and builder performance stats.

Chunk 9: Metrics & History
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from agents.town.workshop import (
    WorkshopArtifact,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopMetrics,
    WorkshopPhase,
    WorkshopTask,
)


@dataclass
class TaskRecord:
    """Complete record of a task execution."""

    id: str
    description: str
    priority: int
    status: str  # completed, interrupted
    lead_builder: str
    builder_sequence: list[str]
    events: list[WorkshopEvent]
    artifacts: list[WorkshopArtifact]
    metrics: WorkshopMetrics
    created_at: datetime
    completed_at: datetime | None

    @property
    def tokens_used(self) -> int:
        """Total tokens used."""
        return self.metrics.total_tokens

    @property
    def handoffs(self) -> int:
        """Total handoffs."""
        return self.metrics.handoffs

    @property
    def duration_seconds(self) -> float:
        """Execution duration in seconds."""
        return self.metrics.duration_seconds

    @property
    def artifacts_count(self) -> int:
        """Number of artifacts produced."""
        return len(self.artifacts)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "lead_builder": self.lead_builder,
            "builder_sequence": self.builder_sequence,
            "artifacts_count": self.artifacts_count,
            "tokens_used": self.tokens_used,
            "handoffs": self.handoffs,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        """Serialize with full details including events and artifacts."""
        base = self.to_dict()
        base["events"] = [e.to_dict() for e in self.events]
        base["artifacts"] = [a.to_dict() for a in self.artifacts]
        base["builder_contributions"] = self._compute_contributions()
        return base

    def _compute_contributions(self) -> dict[str, dict[str, Any]]:
        """Compute per-builder contributions."""
        contributions: dict[str, dict[str, Any]] = {}

        for builder in set(self.builder_sequence):
            # Count artifacts by this builder
            builder_artifacts = [a for a in self.artifacts if a.builder == builder]

            # Count phases worked
            phases_worked = list(
                {
                    e.phase.name
                    for e in self.events
                    if e.builder == builder
                    and e.type
                    in (
                        WorkshopEventType.PHASE_STARTED,
                        WorkshopEventType.ARTIFACT_PRODUCED,
                    )
                }
            )

            # Future: use builder-specific events for time tracking
            # builder_events = [e for e in self.events if e.builder == builder]

            contributions[builder] = {
                "archetype": builder,
                "phases_worked": phases_worked,
                "artifacts_produced": len(builder_artifacts),
                "tokens_used": 0,  # Would need per-builder token tracking
                "duration_seconds": 0.0,  # Would need timestamps per builder
            }

        return contributions


@dataclass
class BuilderStats:
    """Aggregate statistics for a builder archetype."""

    archetype: str
    tasks_participated: int = 0
    tasks_led: int = 0
    artifacts_produced: int = 0
    tokens_used: int = 0
    total_duration: float = 0.0
    handoffs_initiated: int = 0
    handoffs_received: int = 0
    specialty_time: float = 0.0
    total_time: float = 0.0

    @property
    def avg_duration_seconds(self) -> float:
        """Average duration per task."""
        if self.tasks_participated == 0:
            return 0.0
        return self.total_duration / self.tasks_participated

    @property
    def specialty_efficiency(self) -> float:
        """Percentage of time spent in specialty phase."""
        if self.total_time == 0:
            return 1.0
        return self.specialty_time / self.total_time

    def to_dict(self, period: str = "all") -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "archetype": self.archetype,
            "period": period,
            "tasks_participated": self.tasks_participated,
            "tasks_led": self.tasks_led,
            "artifacts_produced": self.artifacts_produced,
            "tokens_used": self.tokens_used,
            "avg_duration_seconds": self.avg_duration_seconds,
            "specialty_efficiency": self.specialty_efficiency,
            "handoffs_initiated": self.handoffs_initiated,
            "handoffs_received": self.handoffs_received,
        }


@dataclass
class DayMetric:
    """Metric for a single day."""

    date: str
    value: int

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"date": self.date, "value": self.value}


@dataclass
class HandoffFlow:
    """Handoff flow between two builders."""

    from_builder: str
    to_builder: str
    count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "from_builder": self.from_builder,
            "to_builder": self.to_builder,
            "count": self.count,
        }


class WorkshopHistoryStore:
    """
    In-memory store for task history.

    Stores completed task records with full event and artifact history.
    Provides methods for querying history and computing aggregate metrics.
    """

    def __init__(self, max_records: int = 100) -> None:
        """
        Initialize the history store.

        Args:
            max_records: Maximum number of task records to keep.
        """
        self._records: dict[str, TaskRecord] = {}
        self._max_records = max_records

    def record_task(
        self,
        task: WorkshopTask,
        status: str,
        lead_builder: str,
        builder_sequence: list[str],
        events: list[WorkshopEvent],
        artifacts: list[WorkshopArtifact],
        metrics: WorkshopMetrics,
    ) -> TaskRecord:
        """
        Store a completed task record.

        Args:
            task: The task that was executed.
            status: Task completion status (completed, interrupted).
            lead_builder: The builder that led the task.
            builder_sequence: Sequence of builders that worked on the task.
            events: All events from task execution.
            artifacts: All artifacts produced.
            metrics: Execution metrics.

        Returns:
            The created TaskRecord.
        """
        # Evict oldest if at capacity
        if len(self._records) >= self._max_records:
            oldest = min(self._records.values(), key=lambda r: r.created_at)
            del self._records[oldest.id]

        record = TaskRecord(
            id=task.id,
            description=task.description,
            priority=task.priority,
            status=status,
            lead_builder=lead_builder,
            builder_sequence=builder_sequence,
            events=list(events),
            artifacts=list(artifacts),
            metrics=metrics,
            created_at=task.created_at,
            completed_at=datetime.now() if status == "completed" else None,
        )

        self._records[task.id] = record
        return record

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Get a task record by ID."""
        return self._records.get(task_id)

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
    ) -> tuple[list[TaskRecord], int]:
        """
        List tasks with pagination.

        Args:
            page: Page number (1-indexed).
            page_size: Number of tasks per page.
            status: Optional filter by status.

        Returns:
            Tuple of (tasks, total_count).
        """
        tasks = list(self._records.values())

        # Filter by status if provided
        if status and status != "all":
            tasks = [t for t in tasks if t.status == status]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        total = len(tasks)
        start = (page - 1) * page_size
        end = start + page_size

        return tasks[start:end], total

    def get_aggregate_metrics(self, period: str = "all") -> dict[str, Any]:
        """
        Compute aggregate metrics for a time period.

        Args:
            period: Time period filter (24h, 7d, 30d, all).

        Returns:
            Dictionary of aggregate metrics.
        """
        tasks = self._filter_by_period(period)

        if not tasks:
            return {
                "period": period,
                "total_tasks": 0,
                "completed_tasks": 0,
                "interrupted_tasks": 0,
                "total_artifacts": 0,
                "total_tokens": 0,
                "total_handoffs": 0,
                "avg_duration_seconds": 0.0,
                "tasks_by_day": [],
                "artifacts_by_day": [],
                "tokens_by_day": [],
            }

        completed = [t for t in tasks if t.status == "completed"]
        interrupted = [t for t in tasks if t.status == "interrupted"]

        total_duration = sum(t.duration_seconds for t in tasks)
        avg_duration = total_duration / len(tasks) if tasks else 0.0

        return {
            "period": period,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed),
            "interrupted_tasks": len(interrupted),
            "total_artifacts": sum(t.artifacts_count for t in tasks),
            "total_tokens": sum(t.tokens_used for t in tasks),
            "total_handoffs": sum(t.handoffs for t in tasks),
            "avg_duration_seconds": avg_duration,
            "tasks_by_day": self._compute_daily_metrics(tasks, "tasks"),
            "artifacts_by_day": self._compute_daily_metrics(tasks, "artifacts"),
            "tokens_by_day": self._compute_daily_metrics(tasks, "tokens"),
        }

    def get_builder_metrics(
        self,
        archetype: str,
        period: str = "all",
    ) -> dict[str, Any]:
        """
        Get metrics for a specific builder.

        Args:
            archetype: Builder archetype name.
            period: Time period filter.

        Returns:
            Dictionary of builder metrics.
        """
        tasks = self._filter_by_period(period)

        stats = BuilderStats(archetype=archetype)

        for task in tasks:
            # Check if builder participated
            if archetype in task.builder_sequence:
                stats.tasks_participated += 1

            # Check if builder led
            if task.lead_builder == archetype:
                stats.tasks_led += 1

            # Count artifacts
            stats.artifacts_produced += len(
                [a for a in task.artifacts if a.builder == archetype]
            )

            # Count handoffs
            for event in task.events:
                if event.type == WorkshopEventType.HANDOFF:
                    from_builder = event.metadata.get("from_builder")
                    to_builder = event.metadata.get("to_builder")
                    if from_builder == archetype:
                        stats.handoffs_initiated += 1
                    if to_builder == archetype:
                        stats.handoffs_received += 1

        return stats.to_dict(period)

    def get_flow_metrics(self) -> dict[str, Any]:
        """
        Get handoff flow metrics between builders.

        Returns:
            Dictionary with flows and total handoffs.
        """
        flows: dict[tuple[str, str], int] = defaultdict(int)
        total_handoffs = 0

        for task in self._records.values():
            for event in task.events:
                if event.type == WorkshopEventType.HANDOFF:
                    from_builder = event.metadata.get("from_builder")
                    to_builder = event.metadata.get("to_builder")
                    if from_builder and to_builder:
                        flows[(from_builder, to_builder)] += 1
                        total_handoffs += 1

        flow_list = [
            HandoffFlow(from_builder=f, to_builder=t, count=c).to_dict()
            for (f, t), c in flows.items()
        ]

        return {
            "flows": flow_list,
            "total_handoffs": total_handoffs,
        }

    def _filter_by_period(self, period: str) -> list[TaskRecord]:
        """Filter tasks by time period."""
        tasks = list(self._records.values())

        if period == "all":
            return tasks

        now = datetime.now()
        cutoff: datetime | None = None

        if period == "24h":
            cutoff = now - timedelta(hours=24)
        elif period == "7d":
            cutoff = now - timedelta(days=7)
        elif period == "30d":
            cutoff = now - timedelta(days=30)

        if cutoff:
            tasks = [t for t in tasks if t.created_at >= cutoff]

        return tasks

    def _compute_daily_metrics(
        self,
        tasks: list[TaskRecord],
        metric_type: str,
    ) -> list[dict[str, Any]]:
        """Compute daily breakdown of a metric."""
        daily: dict[str, int] = defaultdict(int)

        for task in tasks:
            date_str = task.created_at.strftime("%Y-%m-%d")
            if metric_type == "tasks":
                daily[date_str] += 1
            elif metric_type == "artifacts":
                daily[date_str] += task.artifacts_count
            elif metric_type == "tokens":
                daily[date_str] += task.tokens_used

        # Sort by date
        sorted_dates = sorted(daily.keys())
        return [DayMetric(date=d, value=daily[d]).to_dict() for d in sorted_dates]

    def clear(self) -> None:
        """Clear all records."""
        self._records.clear()

    @property
    def count(self) -> int:
        """Number of records stored."""
        return len(self._records)


# Singleton instance for the API
_history_store: WorkshopHistoryStore | None = None


def get_history_store() -> WorkshopHistoryStore:
    """Get the global history store instance."""
    global _history_store
    if _history_store is None:
        _history_store = WorkshopHistoryStore()
    return _history_store


def reset_history_store() -> None:
    """Reset the global history store (for testing)."""
    global _history_store
    _history_store = None


__all__ = [
    "TaskRecord",
    "BuilderStats",
    "DayMetric",
    "HandoffFlow",
    "WorkshopHistoryStore",
    "get_history_store",
    "reset_history_store",
]
