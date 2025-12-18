"""
Tests for WorkshopHistoryStore (Chunk 9).

Validates task recording, retrieval, pagination, and metrics aggregation.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from agents.town.history import (
    BuilderStats,
    DayMetric,
    HandoffFlow,
    TaskRecord,
    WorkshopHistoryStore,
    get_history_store,
    reset_history_store,
)
from agents.town.workshop import (
    WorkshopArtifact,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopMetrics,
    WorkshopPhase,
    WorkshopTask,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def history_store() -> WorkshopHistoryStore:
    """Create a fresh history store for each test."""
    return WorkshopHistoryStore(max_records=10)


@pytest.fixture
def sample_task() -> WorkshopTask:
    """Create a sample task."""
    return WorkshopTask(
        id="task-1",
        description="Build a test feature",
        priority=2,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_events() -> list[WorkshopEvent]:
    """Create sample events for a task."""
    return [
        WorkshopEvent(
            type=WorkshopEventType.TASK_ASSIGNED,
            builder="Scout",
            phase=WorkshopPhase.EXPLORING,
            message="Task assigned to Scout",
            artifact=None,
            timestamp=datetime.now(),
            metadata={},
        ),
        WorkshopEvent(
            type=WorkshopEventType.PHASE_COMPLETED,
            builder="Scout",
            phase=WorkshopPhase.EXPLORING,
            message="Exploration complete",
            artifact=None,
            timestamp=datetime.now(),
            metadata={},
        ),
        WorkshopEvent(
            type=WorkshopEventType.HANDOFF,
            builder="Sage",
            phase=WorkshopPhase.DESIGNING,
            message="Handoff to Sage",
            artifact=None,
            timestamp=datetime.now(),
            metadata={"from_builder": "Scout", "to_builder": "Sage"},
        ),
        WorkshopEvent(
            type=WorkshopEventType.ARTIFACT_PRODUCED,
            builder="Sage",
            phase=WorkshopPhase.DESIGNING,
            message="Design artifact created",
            artifact={"type": "design", "content": "API schema"},
            timestamp=datetime.now(),
            metadata={},
        ),
    ]


@pytest.fixture
def sample_artifacts() -> list[WorkshopArtifact]:
    """Create sample artifacts."""
    return [
        WorkshopArtifact(
            id="artifact-1",
            task_id="task-1",
            builder="Sage",
            phase=WorkshopPhase.DESIGNING,
            content={"type": "design"},
            created_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_metrics() -> WorkshopMetrics:
    """Create sample metrics."""
    return WorkshopMetrics(
        total_steps=10,
        total_events=4,
        total_tokens=500,
        dialogue_tokens=100,
        artifacts_produced=1,
        phases_completed=2,
        handoffs=1,
        perturbations=0,
        start_time=datetime.now() - timedelta(seconds=30),
        end_time=datetime.now(),
    )


# =============================================================================
# TaskRecord Tests
# =============================================================================


class TestTaskRecord:
    """Tests for TaskRecord dataclass."""

    def test_to_dict_includes_all_fields(
        self,
        sample_task: WorkshopTask,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test that to_dict includes all expected fields."""
        record = TaskRecord(
            id=sample_task.id,
            description=sample_task.description,
            priority=sample_task.priority,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
            created_at=sample_task.created_at,
            completed_at=datetime.now(),
        )

        d = record.to_dict()

        assert d["id"] == "task-1"
        assert d["description"] == "Build a test feature"
        assert d["status"] == "completed"
        assert d["lead_builder"] == "Scout"
        assert d["builder_sequence"] == ["Scout", "Sage"]
        assert d["artifacts_count"] == 1
        assert "tokens_used" in d
        assert "handoffs" in d
        assert "duration_seconds" in d
        assert "created_at" in d
        assert "completed_at" in d

    def test_properties(
        self,
        sample_task: WorkshopTask,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test computed properties."""
        record = TaskRecord(
            id=sample_task.id,
            description=sample_task.description,
            priority=sample_task.priority,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
            created_at=sample_task.created_at,
            completed_at=datetime.now(),
        )

        assert record.tokens_used == 500
        assert record.handoffs == 1
        assert record.artifacts_count == 1
        assert record.duration_seconds >= 0


# =============================================================================
# WorkshopHistoryStore Tests
# =============================================================================


class TestWorkshopHistoryStore:
    """Tests for WorkshopHistoryStore."""

    def test_record_task(
        self,
        history_store: WorkshopHistoryStore,
        sample_task: WorkshopTask,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test recording a task."""
        record = history_store.record_task(
            task=sample_task,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
        )

        assert record.id == "task-1"
        assert record.status == "completed"
        assert history_store.count == 1

    def test_get_task(
        self,
        history_store: WorkshopHistoryStore,
        sample_task: WorkshopTask,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test retrieving a task by ID."""
        history_store.record_task(
            task=sample_task,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
        )

        record = history_store.get_task("task-1")
        assert record is not None
        assert record.id == "task-1"

        missing = history_store.get_task("nonexistent")
        assert missing is None

    def test_list_tasks_pagination(
        self,
        history_store: WorkshopHistoryStore,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test task listing with pagination."""
        # Record 5 tasks
        for i in range(5):
            task = WorkshopTask(
                id=f"task-{i}",
                description=f"Task {i}",
                priority=1,
                created_at=datetime.now() - timedelta(hours=i),
            )
            history_store.record_task(
                task=task,
                status="completed",
                lead_builder="Scout",
                builder_sequence=["Scout"],
                events=sample_events,
                artifacts=sample_artifacts,
                metrics=sample_metrics,
            )

        # Test pagination
        tasks, total = history_store.list_tasks(page=1, page_size=2)
        assert len(tasks) == 2
        assert total == 5

        tasks, total = history_store.list_tasks(page=2, page_size=2)
        assert len(tasks) == 2

        tasks, total = history_store.list_tasks(page=3, page_size=2)
        assert len(tasks) == 1

    def test_list_tasks_status_filter(
        self,
        history_store: WorkshopHistoryStore,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test filtering tasks by status."""
        # Record mixed status tasks
        for i, status in enumerate(["completed", "interrupted", "completed"]):
            task = WorkshopTask(
                id=f"task-{i}",
                description=f"Task {i}",
                priority=1,
                created_at=datetime.now(),
            )
            history_store.record_task(
                task=task,
                status=status,
                lead_builder="Scout",
                builder_sequence=["Scout"],
                events=sample_events,
                artifacts=sample_artifacts,
                metrics=sample_metrics,
            )

        completed, _ = history_store.list_tasks(status="completed")
        assert len(completed) == 2

        interrupted, _ = history_store.list_tasks(status="interrupted")
        assert len(interrupted) == 1

    def test_max_records_eviction(
        self,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test that oldest records are evicted when at capacity."""
        store = WorkshopHistoryStore(max_records=3)

        # Record 5 tasks
        for i in range(5):
            task = WorkshopTask(
                id=f"task-{i}",
                description=f"Task {i}",
                priority=1,
                created_at=datetime.now() - timedelta(hours=5 - i),
            )
            store.record_task(
                task=task,
                status="completed",
                lead_builder="Scout",
                builder_sequence=["Scout"],
                events=sample_events,
                artifacts=sample_artifacts,
                metrics=sample_metrics,
            )

        assert store.count == 3
        # Oldest tasks should be evicted
        assert store.get_task("task-0") is None
        assert store.get_task("task-1") is None
        assert store.get_task("task-4") is not None

    def test_get_aggregate_metrics_empty(self, history_store: WorkshopHistoryStore) -> None:
        """Test aggregate metrics with no tasks."""
        metrics = history_store.get_aggregate_metrics()
        assert metrics["total_tasks"] == 0
        assert metrics["tasks_by_day"] == []

    def test_get_aggregate_metrics_with_tasks(
        self,
        history_store: WorkshopHistoryStore,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test aggregate metrics computation."""
        # Record 3 tasks
        for i in range(3):
            task = WorkshopTask(
                id=f"task-{i}",
                description=f"Task {i}",
                priority=1,
                created_at=datetime.now(),
            )
            history_store.record_task(
                task=task,
                status="completed" if i < 2 else "interrupted",
                lead_builder="Scout",
                builder_sequence=["Scout", "Sage"],
                events=sample_events,
                artifacts=sample_artifacts,
                metrics=sample_metrics,
            )

        metrics = history_store.get_aggregate_metrics(period="all")

        assert metrics["total_tasks"] == 3
        assert metrics["completed_tasks"] == 2
        assert metrics["interrupted_tasks"] == 1
        assert metrics["total_artifacts"] == 3  # 1 per task
        assert metrics["total_handoffs"] == 3  # 1 per task

    def test_get_builder_metrics(
        self,
        history_store: WorkshopHistoryStore,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test builder-specific metrics."""
        task = WorkshopTask(
            id="task-1",
            description="Test",
            priority=1,
            created_at=datetime.now(),
        )
        history_store.record_task(
            task=task,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
        )

        scout_metrics = history_store.get_builder_metrics("Scout", period="all")
        assert scout_metrics["tasks_participated"] == 1
        assert scout_metrics["tasks_led"] == 1

        sage_metrics = history_store.get_builder_metrics("Sage", period="all")
        assert sage_metrics["tasks_participated"] == 1
        assert sage_metrics["tasks_led"] == 0

    def test_get_flow_metrics(
        self,
        history_store: WorkshopHistoryStore,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test handoff flow metrics."""
        task = WorkshopTask(
            id="task-1",
            description="Test",
            priority=1,
            created_at=datetime.now(),
        )
        history_store.record_task(
            task=task,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout", "Sage"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
        )

        flows = history_store.get_flow_metrics()
        assert flows["total_handoffs"] == 1
        assert len(flows["flows"]) == 1
        assert flows["flows"][0]["from_builder"] == "Scout"
        assert flows["flows"][0]["to_builder"] == "Sage"

    def test_clear(
        self,
        history_store: WorkshopHistoryStore,
        sample_task: WorkshopTask,
        sample_events: list[WorkshopEvent],
        sample_artifacts: list[WorkshopArtifact],
        sample_metrics: WorkshopMetrics,
    ) -> None:
        """Test clearing the store."""
        history_store.record_task(
            task=sample_task,
            status="completed",
            lead_builder="Scout",
            builder_sequence=["Scout"],
            events=sample_events,
            artifacts=sample_artifacts,
            metrics=sample_metrics,
        )
        assert history_store.count == 1

        history_store.clear()
        assert history_store.count == 0


# =============================================================================
# Singleton Tests
# =============================================================================


class TestHistoryStoreSingleton:
    """Tests for singleton pattern."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        reset_history_store()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        reset_history_store()

    def test_get_history_store_returns_singleton(self) -> None:
        """Test that get_history_store returns the same instance."""
        store1 = get_history_store()
        store2 = get_history_store()
        assert store1 is store2

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset_history_store creates a new instance."""
        store1 = get_history_store()
        reset_history_store()
        store2 = get_history_store()
        assert store1 is not store2
