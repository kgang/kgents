"""
TestWatcher: Event-Driven Pytest Result Monitoring.

Uses a pytest plugin to capture test results in real-time:
- Plugin captures via pytest hooks
- Global queue for cross-thread communication
- Watcher consumes queue and emits TestEvents

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

Integration:
- Pytest plugin: TestWatcherPlugin (register via conftest.py)
- Emits TestEvent to WitnessPolynomial for processing
- Projects test health to thought stream

Usage:
    # In conftest.py:
    from services.kgentsd.watchers.test_watcher import TestWatcherPlugin

    def pytest_configure(config):
        if config.option.witness_tests:
            config.pluginmanager.register(TestWatcherPlugin())

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from queue import Empty, Queue
from typing import TYPE_CHECKING, Any

from services.witness.polynomial import TestEvent

from .base import BaseWatcher

if TYPE_CHECKING:
    import pytest

logger = logging.getLogger(__name__)


# =============================================================================
# Global Queue (Pytest Plugin → Watcher Communication)
# =============================================================================

# Thread-safe queue for cross-boundary communication
# Pytest runs in main thread, watcher may run in asyncio
_TEST_EVENT_QUEUE: Queue[TestEvent] = Queue()


def get_test_event_queue() -> Queue[TestEvent]:
    """Get the global test event queue."""
    return _TEST_EVENT_QUEUE


def reset_test_event_queue() -> None:
    """Reset the queue (for testing)."""
    global _TEST_EVENT_QUEUE
    _TEST_EVENT_QUEUE = Queue()


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class TestWatcherConfig:
    """Configuration for TestWatcher."""

    # Maximum error message length (truncate long tracebacks)
    max_error_length: int = 500

    # Whether to capture individual test results (vs only session summary)
    capture_individual: bool = True

    # Whether to capture passing tests (can be noisy)
    capture_passed: bool = True


# =============================================================================
# Pytest Plugin
# =============================================================================


class TestWatcherPlugin:
    """
    Pytest plugin that captures test events and pushes to queue.

    Register in conftest.py:
        def pytest_configure(config):
            config.pluginmanager.register(TestWatcherPlugin())

    Or via command line flag (requires conftest setup).
    """

    def __init__(self, config: TestWatcherConfig | None = None) -> None:
        self.config = config or TestWatcherConfig()
        self._queue = get_test_event_queue()

        # Session tracking
        self._passed = 0
        self._failed = 0
        self._skipped = 0
        self._session_start: datetime | None = None

    def pytest_sessionstart(self, session: "pytest.Session") -> None:
        """Called at session start."""
        self._session_start = datetime.now()
        self._passed = 0
        self._failed = 0
        self._skipped = 0

    def pytest_runtest_logreport(self, report: Any) -> None:
        """Called for each test phase (setup, call, teardown)."""
        # Only process the 'call' phase (actual test execution)
        if report.when != "call":
            return

        # Determine outcome
        if report.passed:
            outcome = "passed"
            self._passed += 1
        elif report.failed:
            outcome = "failed"
            self._failed += 1
        elif report.skipped:
            outcome = "skipped"
            self._skipped += 1
        else:
            return  # Unknown outcome

        # Skip passed if configured
        if outcome == "passed" and not self.config.capture_passed:
            return

        # Extract error message
        error = None
        if report.failed and hasattr(report, "longrepr"):
            error = str(report.longrepr)
            if len(error) > self.config.max_error_length:
                error = error[: self.config.max_error_length] + "..."

        # Calculate duration in milliseconds
        duration_ms = int(report.duration * 1000) if hasattr(report, "duration") else None

        # Create and queue event
        if self.config.capture_individual:
            event = TestEvent(
                event_type=outcome,
                test_id=report.nodeid,
                duration_ms=duration_ms,
                error=error,
            )
            self._queue.put(event)

    def pytest_sessionfinish(self, session: "pytest.Session", exitstatus: int) -> None:
        """Called at session end."""
        duration_ms = None
        if self._session_start:
            duration_ms = int((datetime.now() - self._session_start).total_seconds() * 1000)

        event = TestEvent(
            event_type="session_complete",
            passed=self._passed,
            failed=self._failed,
            skipped=self._skipped,
            duration_ms=duration_ms,
        )
        self._queue.put(event)


# =============================================================================
# TestWatcher
# =============================================================================


class TestWatcher(BaseWatcher[TestEvent]):
    """
    Event-driven test result watcher.

    Consumes events from the pytest plugin queue and emits to handlers.

    Note: The pytest plugin must be registered separately in conftest.py.
    This watcher only consumes from the queue; it doesn't run pytest.

    Usage:
        watcher = TestWatcher()
        watcher.add_handler(lambda e: print(f"Test: {e.event_type}"))
        await watcher.start()

        # In another process/thread, run pytest with the plugin
        # pytest --witness-tests ...

        # Watcher will receive events as they happen
    """

    def __init__(self, config: TestWatcherConfig | None = None) -> None:
        super().__init__()
        self.config = config or TestWatcherConfig()
        self._queue = get_test_event_queue()

    async def _on_start(self) -> None:
        """Initialize watcher."""
        logger.info("TestWatcher started, listening for pytest events")

    async def _watch_loop(self) -> None:
        """Main watch loop - drain queue and emit events."""
        while not self._stop_event.is_set():
            # Drain queue (non-blocking)
            while True:
                try:
                    event = self._queue.get_nowait()
                    self._emit(event)
                except Empty:
                    break

            # Small sleep to prevent busy loop
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=0.1,  # Check queue every 100ms
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue watching

    async def _cleanup(self) -> None:
        """Cleanup on stop."""
        logger.info("TestWatcher stopped")


# =============================================================================
# Factory Functions
# =============================================================================


def create_test_watcher(
    capture_passed: bool = True,
    max_error_length: int = 500,
) -> TestWatcher:
    """Create a configured test watcher."""
    config = TestWatcherConfig(
        capture_passed=capture_passed,
        max_error_length=max_error_length,
    )
    return TestWatcher(config)


def create_test_plugin(
    capture_passed: bool = True,
    capture_individual: bool = True,
    max_error_length: int = 500,
) -> TestWatcherPlugin:
    """Create a configured pytest plugin."""
    config = TestWatcherConfig(
        capture_passed=capture_passed,
        capture_individual=capture_individual,
        max_error_length=max_error_length,
    )
    return TestWatcherPlugin(config)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TestWatcher",
    "TestWatcherConfig",
    "TestWatcherPlugin",
    "create_test_watcher",
    "create_test_plugin",
    "get_test_event_queue",
    "reset_test_event_queue",
]
