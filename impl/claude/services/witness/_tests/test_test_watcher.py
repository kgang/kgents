"""
Tests for TestWatcher and TestWatcherPlugin.

Verifies:
1. Plugin captures pass/fail/skip outcomes
2. Session summary has correct counts
3. Error truncation works
4. Queue communication between plugin and watcher
5. Watcher lifecycle

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from services.witness.polynomial import TestEvent
from services.witness.watchers.base import WatcherState
from services.witness.watchers.test_watcher import (
    TestWatcher,
    TestWatcherConfig,
    TestWatcherPlugin,
    create_test_plugin,
    create_test_watcher,
    get_test_event_queue,
    reset_test_event_queue,
)

# =============================================================================
# Mock Pytest Report
# =============================================================================


@dataclass
class MockReport:
    """Mock pytest report for testing."""

    nodeid: str = "test_module.py::test_function"
    when: str = "call"
    passed: bool = False
    failed: bool = False
    skipped: bool = False
    duration: float = 0.1
    longrepr: str | None = None


# =============================================================================
# TestWatcherPlugin Tests
# =============================================================================


class TestTestWatcherPlugin:
    """Test the pytest plugin."""

    @pytest.fixture(autouse=True)
    def reset_queue(self) -> None:
        """Reset the global queue before each test."""
        reset_test_event_queue()

    def test_captures_passed_test(self) -> None:
        """Plugin captures passing test."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        report = MockReport(passed=True)
        plugin.pytest_runtest_logreport(report)

        event = queue.get_nowait()
        assert event.event_type == "passed"
        assert event.test_id == "test_module.py::test_function"
        assert event.error is None

    def test_captures_failed_test(self) -> None:
        """Plugin captures failing test with error message."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        report = MockReport(failed=True, longrepr="AssertionError: expected True")
        plugin.pytest_runtest_logreport(report)

        event = queue.get_nowait()
        assert event.event_type == "failed"
        assert event.error == "AssertionError: expected True"

    def test_captures_skipped_test(self) -> None:
        """Plugin captures skipped test."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        report = MockReport(skipped=True)
        plugin.pytest_runtest_logreport(report)

        event = queue.get_nowait()
        assert event.event_type == "skipped"

    def test_ignores_setup_teardown_phases(self) -> None:
        """Plugin only captures 'call' phase."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        # Setup phase
        report = MockReport(when="setup", passed=True)
        plugin.pytest_runtest_logreport(report)

        # Teardown phase
        report = MockReport(when="teardown", passed=True)
        plugin.pytest_runtest_logreport(report)

        # Queue should be empty
        assert queue.empty()

    def test_captures_duration_ms(self) -> None:
        """Plugin captures test duration in milliseconds."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        report = MockReport(passed=True, duration=0.123)
        plugin.pytest_runtest_logreport(report)

        event = queue.get_nowait()
        assert event.duration_ms == 123

    def test_truncates_long_errors(self) -> None:
        """Plugin truncates long error messages."""
        config = TestWatcherConfig(max_error_length=50)
        plugin = TestWatcherPlugin(config)
        queue = get_test_event_queue()

        long_error = "A" * 100
        report = MockReport(failed=True, longrepr=long_error)
        plugin.pytest_runtest_logreport(report)

        event = queue.get_nowait()
        assert len(event.error) == 53  # 50 + "..."
        assert event.error.endswith("...")

    def test_session_summary(self) -> None:
        """Plugin generates session summary with counts."""
        plugin = TestWatcherPlugin()
        queue = get_test_event_queue()

        # Simulate session
        mock_session = MagicMock()
        plugin.pytest_sessionstart(mock_session)

        # Some test results
        plugin.pytest_runtest_logreport(MockReport(passed=True))
        plugin.pytest_runtest_logreport(MockReport(passed=True))
        plugin.pytest_runtest_logreport(MockReport(failed=True, longrepr="error"))
        plugin.pytest_runtest_logreport(MockReport(skipped=True))

        # Drain individual events
        for _ in range(4):
            queue.get_nowait()

        # Session finish
        plugin.pytest_sessionfinish(mock_session, exitstatus=0)

        event = queue.get_nowait()
        assert event.event_type == "session_complete"
        assert event.passed == 2
        assert event.failed == 1
        assert event.skipped == 1
        assert event.duration_ms is not None

    def test_skip_passed_when_configured(self) -> None:
        """Plugin can skip passed tests to reduce noise."""
        config = TestWatcherConfig(capture_passed=False)
        plugin = TestWatcherPlugin(config)
        queue = get_test_event_queue()

        plugin.pytest_runtest_logreport(MockReport(passed=True))

        assert queue.empty()


# =============================================================================
# TestWatcher Tests
# =============================================================================


class TestTestWatcher:
    """Test the TestWatcher lifecycle and event handling."""

    @pytest.fixture(autouse=True)
    def reset_queue(self) -> None:
        """Reset the global queue before each test."""
        reset_test_event_queue()

    def test_initial_state_stopped(self) -> None:
        """Watcher starts in STOPPED state."""
        watcher = TestWatcher()
        assert watcher.state == WatcherState.STOPPED

    @pytest.mark.asyncio
    async def test_start_transitions_to_running(self) -> None:
        """Start transitions to RUNNING state."""
        watcher = TestWatcher()

        await watcher.start()
        try:
            assert watcher.state == WatcherState.RUNNING
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_receives_events_from_queue(self) -> None:
        """Watcher receives events pushed to queue."""
        watcher = TestWatcher()
        queue = get_test_event_queue()

        received: list[TestEvent] = []
        watcher.add_handler(received.append)

        await watcher.start()
        try:
            # Push event to queue
            event = TestEvent(event_type="passed", test_id="test_foo")
            queue.put(event)

            # Wait for watcher to process
            await asyncio.sleep(0.2)

            assert len(received) == 1
            assert received[0].test_id == "test_foo"

        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_processes_multiple_events(self) -> None:
        """Watcher processes multiple queued events."""
        watcher = TestWatcher()
        queue = get_test_event_queue()

        received: list[TestEvent] = []
        watcher.add_handler(received.append)

        await watcher.start()
        try:
            # Push multiple events
            for i in range(5):
                queue.put(TestEvent(event_type="passed", test_id=f"test_{i}"))

            # Wait for processing
            await asyncio.sleep(0.3)

            assert len(received) == 5

        finally:
            await watcher.stop()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_test_watcher(self) -> None:
        """Factory creates configured watcher."""
        watcher = create_test_watcher(capture_passed=False)
        assert watcher.config.capture_passed is False

    def test_create_test_plugin(self) -> None:
        """Factory creates configured plugin."""
        plugin = create_test_plugin(max_error_length=100)
        assert plugin.config.max_error_length == 100
