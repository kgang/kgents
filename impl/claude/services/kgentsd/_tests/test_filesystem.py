"""
Tests for FileSystemWatcher.

Verifies:
1. Pattern matching (include/exclude)
2. Debouncing behavior
3. Watcher lifecycle
4. Event emission
5. Configuration presets

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.kgentsd.watchers.base import WatcherState
from services.kgentsd.watchers.filesystem import (
    Debouncer,
    FileSystemConfig,
    FileSystemWatcher,
    PatternMatcher,
    create_filesystem_watcher,
)
from services.witness.polynomial import FileEvent

# =============================================================================
# PatternMatcher Tests
# =============================================================================


class TestPatternMatcher:
    """Test glob pattern matching."""

    def test_matches_include_pattern(self) -> None:
        """Files matching include patterns are accepted."""
        matcher = PatternMatcher(include=("*.py", "*.tsx"))

        assert matcher.matches("/path/to/file.py")
        assert matcher.matches("/path/to/component.tsx")
        assert not matcher.matches("/path/to/file.js")
        assert not matcher.matches("/path/to/README.md")

    def test_matches_exclude_pattern(self) -> None:
        """Files matching exclude patterns are rejected."""
        matcher = PatternMatcher(exclude=("__pycache__", "*.pyc"))

        assert matcher.matches("/path/to/file.py")
        assert not matcher.matches("/path/to/__pycache__/file.cpython-311.pyc")
        assert not matcher.matches("/path/__pycache__/something.py")
        assert not matcher.matches("/path/to/file.pyc")

    def test_exclude_takes_precedence(self) -> None:
        """Exclude patterns override include patterns."""
        matcher = PatternMatcher(
            include=("*.py",),
            exclude=("test_*.py",),
        )

        assert matcher.matches("/path/to/module.py")
        assert not matcher.matches("/path/to/test_module.py")

    def test_empty_include_matches_all(self) -> None:
        """Empty include patterns matches all non-excluded files."""
        matcher = PatternMatcher(exclude=(".git",))

        assert matcher.matches("/path/to/anything.xyz")
        assert matcher.matches("/path/to/README.md")
        assert not matcher.matches("/project/.git/config")

    def test_path_component_exclusion(self) -> None:
        """Exclude patterns check all path components."""
        matcher = PatternMatcher(exclude=("node_modules",))

        assert not matcher.matches("/project/node_modules/package/index.js")
        assert matcher.matches("/project/src/index.js")


# =============================================================================
# Debouncer Tests
# =============================================================================


class TestDebouncer:
    """Test time-based debouncing."""

    def test_first_event_emits(self) -> None:
        """First event for a path always emits."""
        debouncer = Debouncer(window_seconds=0.5)

        assert debouncer.should_emit("/path/to/file.py")

    def test_rapid_events_debounced(self) -> None:
        """Rapid successive events are debounced."""
        debouncer = Debouncer(window_seconds=0.5)

        assert debouncer.should_emit("/path/to/file.py")
        assert not debouncer.should_emit("/path/to/file.py")
        assert not debouncer.should_emit("/path/to/file.py")

    def test_different_paths_independent(self) -> None:
        """Different paths have independent debounce windows."""
        debouncer = Debouncer(window_seconds=0.5)

        assert debouncer.should_emit("/path/to/file1.py")
        assert debouncer.should_emit("/path/to/file2.py")
        assert not debouncer.should_emit("/path/to/file1.py")

    def test_debounce_window_expires(self) -> None:
        """Events emit after debounce window expires."""
        debouncer = Debouncer(window_seconds=0.05)  # 50ms for fast tests

        assert debouncer.should_emit("/path/to/file.py")
        time.sleep(0.06)  # Wait past window
        assert debouncer.should_emit("/path/to/file.py")

    def test_clear_resets_state(self) -> None:
        """Clear removes all debounce tracking."""
        debouncer = Debouncer(window_seconds=0.5)

        debouncer.should_emit("/path/to/file.py")
        assert not debouncer.should_emit("/path/to/file.py")

        debouncer.clear()
        assert debouncer.should_emit("/path/to/file.py")


# =============================================================================
# FileSystemConfig Tests
# =============================================================================


class TestFileSystemConfig:
    """Test configuration options."""

    def test_default_config(self) -> None:
        """Default config has sensible defaults."""
        config = FileSystemConfig()

        assert config.recursive is True
        assert config.debounce_seconds == 0.5
        assert "*.py" in config.include_patterns
        assert "__pycache__" in config.exclude_patterns

    def test_python_preset(self) -> None:
        """Python preset focuses on .py files."""
        config = FileSystemConfig.for_python()

        assert config.include_patterns == ("*.py",)

    def test_typescript_preset(self) -> None:
        """TypeScript preset includes web files."""
        config = FileSystemConfig.for_typescript()

        assert "*.ts" in config.include_patterns
        assert "*.tsx" in config.include_patterns
        assert "*.js" in config.include_patterns


# =============================================================================
# FileSystemWatcher Lifecycle Tests
# =============================================================================


class TestFileSystemWatcherLifecycle:
    """Test watcher start/stop lifecycle."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    def test_initial_state_stopped(self, temp_dir: Path) -> None:
        """Watcher starts in STOPPED state."""
        config = FileSystemConfig(watch_path=temp_dir)
        watcher = FileSystemWatcher(config)

        assert watcher.state == WatcherState.STOPPED

    @pytest.mark.asyncio
    async def test_start_transitions_to_running(self, temp_dir: Path) -> None:
        """Start transitions to RUNNING state."""
        config = FileSystemConfig(watch_path=temp_dir)
        watcher = FileSystemWatcher(config)

        await watcher.start()
        try:
            assert watcher.state == WatcherState.RUNNING
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_stop_transitions_to_stopped(self, temp_dir: Path) -> None:
        """Stop transitions back to STOPPED state."""
        config = FileSystemConfig(watch_path=temp_dir)
        watcher = FileSystemWatcher(config)

        await watcher.start()
        await watcher.stop()

        assert watcher.state == WatcherState.STOPPED

    @pytest.mark.asyncio
    async def test_double_start_idempotent(self, temp_dir: Path) -> None:
        """Starting twice doesn't cause issues."""
        config = FileSystemConfig(watch_path=temp_dir)
        watcher = FileSystemWatcher(config)

        await watcher.start()
        await watcher.start()  # Should be no-op
        try:
            assert watcher.state == WatcherState.RUNNING
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_double_stop_idempotent(self, temp_dir: Path) -> None:
        """Stopping twice doesn't cause issues."""
        config = FileSystemConfig(watch_path=temp_dir)
        watcher = FileSystemWatcher(config)

        await watcher.start()
        await watcher.stop()
        await watcher.stop()  # Should be no-op

        assert watcher.state == WatcherState.STOPPED


# =============================================================================
# Event Emission Tests
# =============================================================================


class TestFileSystemWatcherEvents:
    """Test event detection and emission."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    @pytest.mark.asyncio
    async def test_handler_receives_events(self, temp_dir: Path) -> None:
        """Handlers receive emitted events."""
        config = FileSystemConfig(
            watch_path=temp_dir,
            include_patterns=("*.py",),
            debounce_seconds=0.01,  # Fast for tests
        )
        watcher = FileSystemWatcher(config)

        received_events: list[FileEvent] = []
        watcher.add_handler(received_events.append)

        await watcher.start()
        try:
            # Create a file (watchdog should detect)
            test_file = temp_dir / "test.py"
            test_file.write_text("# test")

            # Wait for event to propagate
            await asyncio.sleep(0.2)

            # Check events (may have create + modify)
            assert len(received_events) >= 1
            assert any(e.path.endswith("test.py") for e in received_events)

        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_excluded_files_not_emitted(self, temp_dir: Path) -> None:
        """Excluded files don't generate events."""
        config = FileSystemConfig(
            watch_path=temp_dir,
            include_patterns=("*",),  # Include all
            exclude_patterns=("*.pyc",),
            debounce_seconds=0.01,
        )
        watcher = FileSystemWatcher(config)

        received_events: list[FileEvent] = []
        watcher.add_handler(received_events.append)

        await watcher.start()
        try:
            # Create excluded file
            (temp_dir / "cache.pyc").write_bytes(b"bytecode")
            await asyncio.sleep(0.2)

            # Should not have events for .pyc
            assert not any(e.path.endswith(".pyc") for e in received_events)

        finally:
            await watcher.stop()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunction:
    """Test the create_filesystem_watcher factory."""

    def test_creates_configured_watcher(self) -> None:
        """Factory creates properly configured watcher."""
        watcher = create_filesystem_watcher(
            include=("*.md",),
            debounce=0.25,
        )

        assert watcher.config.include_patterns == ("*.md",)
        assert watcher.config.debounce_seconds == 0.25


# =============================================================================
# Stats Tracking Tests
# =============================================================================


class TestWatcherStats:
    """Test statistics tracking."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    @pytest.mark.asyncio
    async def test_stats_track_events(self, temp_dir: Path) -> None:
        """Stats count emitted events."""
        config = FileSystemConfig(
            watch_path=temp_dir,
            include_patterns=("*.py",),
            debounce_seconds=0.01,
        )
        watcher = FileSystemWatcher(config)

        await watcher.start()
        try:
            # Create a file
            test_file = temp_dir / "stats_test.py"
            test_file.write_text("# test")

            await asyncio.sleep(0.2)

            # Should have recorded events
            assert watcher.stats.events_emitted >= 1
            assert watcher.stats.started_at is not None

        finally:
            await watcher.stop()
