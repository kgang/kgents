"""
Tests for CIWatcher.

Covers:
- Configuration defaults
- Workflow run parsing
- Event emission for status changes
- Deduplication (same run, same status = no event)
- Rate limit awareness
- Exponential backoff
- Workflow filtering
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from services.witness.polynomial import CIEvent
from services.witness.watchers.ci import (
    CIConfig,
    CIWatcher,
    WorkflowRun,
    create_ci_watcher,
)


# =============================================================================
# Configuration Tests
# =============================================================================


class TestCIConfig:
    """Tests for CIConfig."""

    def test_defaults(self) -> None:
        """Default config has sensible values."""
        config = CIConfig()
        assert config.owner == ""
        assert config.repo == ""
        assert config.token is None
        assert config.poll_interval_seconds == 60.0
        assert config.max_backoff_seconds == 300.0
        assert config.rate_limit_floor == 10
        assert config.max_tracked_runs == 100

    def test_custom_config(self) -> None:
        """Custom config overrides defaults."""
        config = CIConfig(
            owner="kentgang",
            repo="kgents",
            token="ghp_test",
            poll_interval_seconds=30.0,
        )
        assert config.owner == "kentgang"
        assert config.repo == "kgents"
        assert config.token == "ghp_test"
        assert config.poll_interval_seconds == 30.0


class TestCreateCIWatcher:
    """Tests for factory function."""

    def test_create_default(self) -> None:
        """Create watcher with defaults."""
        watcher = create_ci_watcher()
        assert watcher.config.owner == ""
        assert watcher.config.repo == ""

    def test_create_configured(self) -> None:
        """Create watcher with custom config."""
        watcher = create_ci_watcher(
            owner="test",
            repo="repo",
            token="token123",
            poll_interval=120.0,
        )
        assert watcher.config.owner == "test"
        assert watcher.config.repo == "repo"
        assert watcher.config.token == "token123"
        assert watcher.config.poll_interval_seconds == 120.0


# =============================================================================
# WorkflowRun Tests
# =============================================================================


class TestWorkflowRun:
    """Tests for WorkflowRun dataclass."""

    def test_basic_run(self) -> None:
        """Create a basic workflow run."""
        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=12345,
            name="CI",
            status="completed",
            conclusion="success",
            created_at=now,
            updated_at=now,
            head_branch="main",
        )
        assert run.id == 12345
        assert run.name == "CI"
        assert run.status == "completed"
        assert run.conclusion == "success"

    def test_run_with_duration(self) -> None:
        """Run with duration calculated."""
        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=1,
            name="Build",
            status="completed",
            conclusion="success",
            created_at=now,
            updated_at=now,
            head_branch="main",
            duration_seconds=120,
        )
        assert run.duration_seconds == 120


# =============================================================================
# CIWatcher Event Processing Tests
# =============================================================================


class TestCIWatcherEventProcessing:
    """Tests for CIWatcher event processing logic."""

    def test_new_in_progress_run_emits_started(self) -> None:
        """New in_progress run emits workflow_started."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=1,
            name="CI",
            status="in_progress",
            conclusion=None,
            created_at=now,
            updated_at=now,
            head_branch="main",
        )

        watcher._process_run(run)

        assert len(events) == 1
        assert events[0].event_type == "workflow_started"
        assert events[0].workflow == "CI"
        assert events[0].status == "in_progress"

    def test_new_completed_run_emits_complete(self) -> None:
        """New completed run emits workflow_complete."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=2,
            name="Deploy",
            status="completed",
            conclusion="success",
            created_at=now,
            updated_at=now,
            head_branch="main",
            duration_seconds=300,
        )

        watcher._process_run(run)

        assert len(events) == 1
        assert events[0].event_type == "workflow_complete"
        assert events[0].workflow == "Deploy"
        assert events[0].status == "success"
        assert events[0].duration_seconds == 300

    def test_failed_run_emits_both_complete_and_check_failed(self) -> None:
        """Failed run emits workflow_complete AND check_failed."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=3,
            name="Tests",
            status="completed",
            conclusion="failure",
            created_at=now,
            updated_at=now,
            head_branch="feature",
        )

        watcher._process_run(run)

        assert len(events) == 2
        assert events[0].event_type == "workflow_complete"
        assert events[0].status == "failure"
        assert events[1].event_type == "check_failed"
        assert events[1].workflow == "Tests"

    def test_status_transition_emits_event(self) -> None:
        """Status change from in_progress to completed emits event."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)

        # First poll: in_progress
        run1 = WorkflowRun(
            id=4,
            name="Build",
            status="in_progress",
            conclusion=None,
            created_at=now,
            updated_at=now,
            head_branch="main",
        )
        watcher._process_run(run1)
        assert len(events) == 1  # workflow_started

        # Second poll: completed
        run2 = WorkflowRun(
            id=4,
            name="Build",
            status="completed",
            conclusion="success",
            created_at=now,
            updated_at=now,
            head_branch="main",
            duration_seconds=60,
        )
        watcher._process_run(run2)
        assert len(events) == 2  # workflow_complete added
        assert events[1].event_type == "workflow_complete"

    def test_same_status_no_duplicate_event(self) -> None:
        """Same run with same status does not emit duplicate event."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=5,
            name="CI",
            status="in_progress",
            conclusion=None,
            created_at=now,
            updated_at=now,
            head_branch="main",
        )

        watcher._process_run(run)
        watcher._process_run(run)  # Same run, same status
        watcher._process_run(run)  # Again

        assert len(events) == 1  # Only one event emitted

    def test_queued_to_in_progress_emits_started(self) -> None:
        """Transition from queued to in_progress emits started."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)

        # First: queued (no event emitted)
        run1 = WorkflowRun(
            id=6,
            name="CI",
            status="queued",
            conclusion=None,
            created_at=now,
            updated_at=now,
            head_branch="main",
        )
        watcher._process_run(run1)
        assert len(events) == 0  # queued → no event

        # Then: in_progress
        run2 = WorkflowRun(
            id=6,
            name="CI",
            status="in_progress",
            conclusion=None,
            created_at=now,
            updated_at=now,
            head_branch="main",
        )
        watcher._process_run(run2)
        assert len(events) == 1
        assert events[0].event_type == "workflow_started"


# =============================================================================
# Workflow Filter Tests
# =============================================================================


class TestCIWatcherFiltering:
    """Tests for workflow filtering."""

    @pytest.mark.asyncio
    async def test_workflow_filter_excludes_unmatched(self) -> None:
        """Workflow filter excludes non-matching workflows."""
        config = CIConfig(
            owner="test",
            repo="test",
            workflow_filter=("CI", "Deploy"),
        )
        watcher = CIWatcher(config=config)
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)

        # Mock fetch to return runs with different names
        runs = [
            WorkflowRun(
                id=1, name="CI", status="completed", conclusion="success",
                created_at=now, updated_at=now, head_branch="main",
            ),
            WorkflowRun(
                id=2, name="Lint", status="completed", conclusion="success",  # Not in filter
                created_at=now, updated_at=now, head_branch="main",
            ),
            WorkflowRun(
                id=3, name="Deploy", status="completed", conclusion="success",
                created_at=now, updated_at=now, head_branch="main",
            ),
        ]

        with patch(
            "services.witness.watchers.ci.fetch_workflow_runs",
            new=AsyncMock(return_value=(runs, 50, 0)),
        ):
            await watcher._poll_once()

        # Only CI and Deploy should have events (Lint excluded)
        assert len(events) == 2
        workflow_names = {e.workflow for e in events}
        assert workflow_names == {"CI", "Deploy"}


# =============================================================================
# Rate Limit Tests
# =============================================================================


class TestCIWatcherRateLimit:
    """Tests for rate limit handling."""

    @pytest.mark.asyncio
    async def test_low_rate_limit_skips_poll(self) -> None:
        """Low rate limit remaining causes poll to be skipped."""
        config = CIConfig(
            owner="test",
            repo="test",
            rate_limit_floor=10,
        )
        watcher = CIWatcher(config=config)
        watcher._rate_limit_remaining = 5  # Below floor

        # Should skip without calling fetch
        with patch(
            "services.witness.watchers.ci.fetch_workflow_runs",
            new=AsyncMock(),
        ) as mock_fetch:
            await watcher._poll_once()
            mock_fetch.assert_not_called()


# =============================================================================
# Seen Runs Pruning Tests
# =============================================================================


class TestCIWatcherPruning:
    """Tests for seen runs memory management."""

    def test_prune_keeps_recent_runs(self) -> None:
        """Pruning keeps most recent runs by ID."""
        config = CIConfig(max_tracked_runs=5)
        watcher = CIWatcher(config=config)

        # Add 10 runs
        for i in range(10):
            watcher._seen_runs[i] = "completed"

        watcher._prune_seen_runs()

        # Should keep only runs 5-9 (most recent by ID)
        assert len(watcher._seen_runs) == 5
        assert set(watcher._seen_runs.keys()) == {5, 6, 7, 8, 9}

    def test_prune_noop_under_limit(self) -> None:
        """Pruning does nothing when under limit."""
        config = CIConfig(max_tracked_runs=10)
        watcher = CIWatcher(config=config)

        for i in range(5):
            watcher._seen_runs[i] = "completed"

        watcher._prune_seen_runs()

        assert len(watcher._seen_runs) == 5


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestCIWatcherLifecycle:
    """Tests for watcher lifecycle."""

    @pytest.mark.asyncio
    async def test_start_stop_without_config(self) -> None:
        """Watcher can start/stop without owner/repo configured."""
        watcher = CIWatcher()

        await watcher.start()
        assert watcher.state.name == "RUNNING"

        await watcher.stop()
        assert watcher.state.name == "STOPPED"

    @pytest.mark.asyncio
    async def test_stats_tracking(self) -> None:
        """Stats are tracked correctly."""
        watcher = CIWatcher()
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            id=1, name="CI", status="completed", conclusion="success",
            created_at=now, updated_at=now, head_branch="main",
        )

        watcher._process_run(run)

        assert watcher.stats.events_emitted == 1
        assert watcher.stats.last_event_time is not None


# =============================================================================
# Integration Test (with mocked API)
# =============================================================================


class TestCIWatcherIntegration:
    """Integration tests with mocked GitHub API."""

    @pytest.mark.asyncio
    async def test_full_poll_cycle(self) -> None:
        """Full poll cycle with mocked API."""
        config = CIConfig(owner="test", repo="repo")
        watcher = CIWatcher(config=config)
        events: list[CIEvent] = []
        watcher.add_handler(events.append)

        now = datetime.now(timezone.utc)
        mock_runs = [
            WorkflowRun(
                id=100,
                name="Tests",
                status="completed",
                conclusion="success",
                created_at=now,
                updated_at=now,
                head_branch="main",
                duration_seconds=45,
            ),
        ]

        with patch(
            "services.witness.watchers.ci.fetch_workflow_runs",
            new=AsyncMock(return_value=(mock_runs, 50, 0)),
        ):
            await watcher._poll_once()

        assert len(events) == 1
        assert events[0].event_type == "workflow_complete"
        assert events[0].workflow == "Tests"
        assert events[0].duration_seconds == 45
