"""
FileSystemWatcher: Event-Driven File System Monitoring.

Uses watchdog for real-time file system event detection with:
- Glob pattern matching (include/exclude)
- Debouncing to avoid event storms from rapid saves
- Async queue for event delivery

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

Integration:
- Emits FileEvent to WitnessPolynomial for processing
- Projects to thought stream

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from queue import Empty, Queue
from typing import TYPE_CHECKING

from services.witness.polynomial import FileEvent
from services.witness.watchers.base import BaseWatcher

if TYPE_CHECKING:
    from watchdog.events import FileSystemEvent

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class FileSystemConfig:
    """Configuration for FileSystemWatcher."""

    watch_path: Path = field(default_factory=Path.cwd)
    recursive: bool = True

    # Glob patterns (fnmatch syntax)
    include_patterns: tuple[str, ...] = ("*.py", "*.tsx", "*.ts", "*.md")
    exclude_patterns: tuple[str, ...] = (
        "__pycache__",
        "*.pyc",
        ".git",
        ".venv",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
        "*.egg-info",
        ".tox",
        "*.swp",
        "*.swo",
        "*~",
    )

    # Debounce window (seconds)
    debounce_seconds: float = 0.5

    @classmethod
    def for_python(cls, path: Path | None = None) -> "FileSystemConfig":
        """Preset for Python projects."""
        return cls(
            watch_path=path or Path.cwd(),
            include_patterns=("*.py",),
        )

    @classmethod
    def for_typescript(cls, path: Path | None = None) -> "FileSystemConfig":
        """Preset for TypeScript projects."""
        return cls(
            watch_path=path or Path.cwd(),
            include_patterns=("*.ts", "*.tsx", "*.js", "*.jsx"),
        )


# =============================================================================
# Debouncer
# =============================================================================


class Debouncer:
    """
    Time-based debouncer for file events.

    Prevents event storms from rapid saves (e.g., auto-save editors).
    """

    def __init__(self, window_seconds: float = 0.5) -> None:
        self.window = window_seconds
        self._last_seen: dict[str, float] = {}

    def should_emit(self, path: str) -> bool:
        """Check if enough time has passed since last event for this path."""
        now = time.time()
        last = self._last_seen.get(path, 0)

        if now - last < self.window:
            return False

        self._last_seen[path] = now
        return True

    def clear(self) -> None:
        """Clear all debounce state."""
        self._last_seen.clear()


# =============================================================================
# Pattern Matcher
# =============================================================================


class PatternMatcher:
    """
    Glob-based pattern matcher for file paths.

    Uses fnmatch for pattern matching.
    """

    def __init__(
        self,
        include: tuple[str, ...] = (),
        exclude: tuple[str, ...] = (),
    ) -> None:
        self.include = include
        self.exclude = exclude

    def matches(self, path: str) -> bool:
        """Check if path matches include patterns and doesn't match exclude."""
        path_obj = Path(path)

        # Check exclude first (any component matching exclude = reject)
        for pattern in self.exclude:
            # Check filename
            if fnmatch(path_obj.name, pattern):
                return False
            # Check any path component
            if any(fnmatch(part, pattern) for part in path_obj.parts):
                return False

        # If no include patterns, match all non-excluded
        if not self.include:
            return True

        # Check include patterns on filename
        return any(fnmatch(path_obj.name, pattern) for pattern in self.include)


# =============================================================================
# FileSystemWatcher
# =============================================================================


class FileSystemWatcher(BaseWatcher[FileEvent]):
    """
    Event-driven file system watcher.

    Uses watchdog for real-time event detection with:
    - Glob pattern filtering
    - Debouncing
    - Async event queue

    Extends BaseWatcher for consistent lifecycle management.

    Usage:
        config = FileSystemConfig(watch_path=Path("/my/project"))
        watcher = FileSystemWatcher(config)

        async for event in watcher.watch():
            print(f"{event.event_type}: {event.path}")
    """

    def __init__(self, config: FileSystemConfig | None = None) -> None:
        super().__init__()
        self.config = config or FileSystemConfig()

        # Event queue (thread-safe, watchdog runs in thread)
        self._queue: Queue[FileEvent] = Queue()

        # Pattern matcher and debouncer
        self._matcher = PatternMatcher(
            include=self.config.include_patterns,
            exclude=self.config.exclude_patterns,
        )
        self._debouncer = Debouncer(self.config.debounce_seconds)

        # Watchdog observer (created on start)
        self._observer: object | None = None

    async def _on_start(self) -> None:
        """Initialize watchdog observer."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            # Inner handler class
            watcher = self  # Capture for closure

            class Handler(FileSystemEventHandler):
                """Watchdog event handler that filters and enqueues events."""

                def _handle(self, event: "FileSystemEvent", event_type: str) -> None:
                    """Common handler for all event types."""
                    if event.is_directory:
                        return

                    path = str(event.src_path)

                    # Pattern filter
                    if not watcher._matcher.matches(path):
                        return

                    # Debounce filter
                    if not watcher._debouncer.should_emit(path):
                        return

                    # Create and enqueue event
                    file_event = FileEvent(
                        event_type=event_type,
                        path=path,
                        is_directory=False,
                    )
                    watcher._queue.put(file_event)

                def on_created(self, event: "FileSystemEvent") -> None:
                    self._handle(event, "create")

                def on_modified(self, event: "FileSystemEvent") -> None:
                    self._handle(event, "modify")

                def on_deleted(self, event: "FileSystemEvent") -> None:
                    self._handle(event, "delete")

                def on_moved(self, event: "FileSystemEvent") -> None:
                    # Treat move as delete + create
                    self._handle(event, "rename")

            # Create and configure observer
            observer = Observer()
            handler = Handler()
            observer.schedule(
                handler,
                str(self.config.watch_path),
                recursive=self.config.recursive,
            )
            observer.start()

            self._observer = observer
            logger.info(f"FileSystemWatcher started on {self.config.watch_path}")

        except ImportError as e:
            logger.error(f"watchdog not installed: {e}")
            raise RuntimeError("watchdog required for FileSystemWatcher") from e

    async def _watch_loop(self) -> None:
        """Main watch loop - drain queue and emit events."""
        while not self._stop_event.is_set():
            # Drain queue (non-blocking)
            events_emitted = 0
            while True:
                try:
                    event = self._queue.get_nowait()
                    self._emit(event)
                    events_emitted += 1
                except Empty:
                    break

            # Small sleep to prevent busy loop
            # Event-driven: we wake when queue has items
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=0.1,  # Check queue every 100ms
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue watching

    async def _cleanup(self) -> None:
        """Stop watchdog observer."""
        if self._observer is not None:
            try:
                # Observer is actually watchdog.observers.Observer
                observer = self._observer  # type: ignore
                observer.stop()
                observer.join(timeout=2.0)
            except Exception as e:
                logger.warning(f"Error stopping observer: {e}")
            finally:
                self._observer = None

        self._debouncer.clear()
        logger.info("FileSystemWatcher stopped")


# =============================================================================
# Factory Functions
# =============================================================================


def create_filesystem_watcher(
    path: Path | None = None,
    include: tuple[str, ...] = ("*.py", "*.tsx", "*.ts"),
    exclude: tuple[str, ...] = ("__pycache__", ".git", "node_modules"),
    debounce: float = 0.5,
) -> FileSystemWatcher:
    """Create a configured filesystem watcher."""
    config = FileSystemConfig(
        watch_path=path or Path.cwd(),
        include_patterns=include,
        exclude_patterns=exclude,
        debounce_seconds=debounce,
    )
    return FileSystemWatcher(config)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "FileSystemWatcher",
    "FileSystemConfig",
    "PatternMatcher",
    "Debouncer",
    "create_filesystem_watcher",
]
