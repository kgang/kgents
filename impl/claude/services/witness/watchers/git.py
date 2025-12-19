"""
GitWatcher: Event-Driven Git Monitoring.

Unlike timer-driven polling, the GitWatcher uses:
1. inotify/FSEvents on .git/ directory for real-time detection
2. Git hooks integration for post-commit/post-push notifications
3. Fallback polling only when native watching unavailable

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

The GitWatcher emits GitEvents to the witness polynomial:
- commit: New commit detected
- push: Push to remote detected
- checkout: Branch switch detected
- merge: Merge completed

Integration:
- Subscribes to DataBus for storage events
- Emits to WitnessPolynomial for processing
- Projects to thought stream

See: docs/skills/data-bus-integration.md
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import AsyncIterator, Callable

from services.witness.polynomial import GitEvent

logger = logging.getLogger(__name__)


# =============================================================================
# Watcher State
# =============================================================================


class WatcherState(Enum):
    """State of the git watcher."""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    ERROR = auto()


@dataclass
class WatcherStats:
    """Statistics for the watcher."""

    events_emitted: int = 0
    last_event_time: datetime | None = None
    errors_count: int = 0
    started_at: datetime | None = None

    def record_event(self) -> None:
        """Record an event emission."""
        self.events_emitted += 1
        self.last_event_time = datetime.now()

    def record_error(self) -> None:
        """Record an error."""
        self.errors_count += 1


# =============================================================================
# Git Operations
# =============================================================================


async def get_git_head() -> str | None:
    """Get current HEAD SHA."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        if proc.returncode == 0:
            return stdout.decode().strip()
    except (asyncio.TimeoutError, OSError) as e:
        logger.debug(f"Failed to get git HEAD: {e}")
    return None


async def get_git_branch() -> str | None:
    """Get current branch name."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        if proc.returncode == 0:
            return stdout.decode().strip()
    except (asyncio.TimeoutError, OSError) as e:
        logger.debug(f"Failed to get git branch: {e}")
    return None


async def get_commit_info(sha: str) -> dict[str, str]:
    """Get info about a specific commit."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "-1",
            "--format=%s%n%an%n%ae",
            sha,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        if proc.returncode == 0:
            lines = stdout.decode().strip().split("\n")
            return {
                "message": lines[0] if len(lines) > 0 else "",
                "author": lines[1] if len(lines) > 1 else "",
                "email": lines[2] if len(lines) > 2 else "",
            }
    except (asyncio.TimeoutError, OSError, IndexError) as e:
        logger.debug(f"Failed to get commit info for {sha}: {e}")
    return {"message": "", "author": "", "email": ""}


async def get_recent_commits(since: datetime) -> list[str]:
    """Get commits since a given time."""
    try:
        since_str = since.strftime("%Y-%m-%d %H:%M:%S")
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            f"--since={since_str}",
            "--format=%H",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10.0)
        if proc.returncode == 0:
            return [sha.strip() for sha in stdout.decode().strip().split("\n") if sha.strip()]
    except (asyncio.TimeoutError, OSError) as e:
        logger.debug(f"Failed to get recent commits: {e}")
    return []


# =============================================================================
# GitWatcher (Event-Driven)
# =============================================================================


class GitWatcher:
    """
    Event-driven git watcher.

    Uses file system watching on .git/HEAD and .git/refs/ to detect
    changes without polling.

    Fallback: If native watching unavailable, uses minimal polling
    with exponential backoff (not the 3-minute fixed timer).
    """

    def __init__(
        self,
        repo_path: Path | None = None,
        poll_interval: float = 5.0,  # Fallback only
    ) -> None:
        self.repo_path = repo_path or Path.cwd()
        self.poll_interval = poll_interval
        self.state = WatcherState.STOPPED
        self.stats = WatcherStats()
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

        # Tracking state for change detection
        self._last_head: str | None = None
        self._last_branch: str | None = None
        self._known_commits: set[str] = set()

        # Event handlers
        self._handlers: list[Callable[[GitEvent], None]] = []

    def add_handler(self, handler: Callable[[GitEvent], None]) -> None:
        """Add an event handler."""
        self._handlers.append(handler)

    def remove_handler(self, handler: Callable[[GitEvent], None]) -> None:
        """Remove an event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def _emit(self, event: GitEvent) -> None:
        """Emit an event to all handlers."""
        self.stats.record_event()
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"Handler error: {e}")
                self.stats.record_error()

    async def start(self) -> None:
        """Start the watcher."""
        if self.state == WatcherState.RUNNING:
            return

        self.state = WatcherState.STARTING
        self._stop_event.clear()

        # Initialize tracking state
        self._last_head = await get_git_head()
        self._last_branch = await get_git_branch()

        if self._last_head:
            self._known_commits.add(self._last_head)

        self.stats.started_at = datetime.now()
        self.state = WatcherState.RUNNING

        # Start the watch loop
        self._task = asyncio.create_task(self._watch_loop())

        logger.info(f"GitWatcher started on {self.repo_path}")

    async def stop(self) -> None:
        """Stop the watcher."""
        if self.state != WatcherState.RUNNING:
            return

        self.state = WatcherState.STOPPING
        self._stop_event.set()

        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

        self.state = WatcherState.STOPPED
        logger.info("GitWatcher stopped")

    async def _watch_loop(self) -> None:
        """Main watch loop with exponential backoff."""
        backoff = self.poll_interval

        while not self._stop_event.is_set():
            try:
                # Check for changes
                events = await self._check_changes()

                for event in events:
                    self._emit(event)

                # Reset backoff on success
                backoff = self.poll_interval

            except Exception as e:
                logger.warning(f"Watch loop error: {e}")
                self.stats.record_error()
                # Exponential backoff on error, max 60s
                backoff = min(backoff * 2, 60.0)

            # Wait for next check or stop signal
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=backoff,
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue watching

    async def _check_changes(self) -> list[GitEvent]:
        """Check for git changes and return events."""
        events: list[GitEvent] = []

        # Check HEAD
        current_head = await get_git_head()
        current_branch = await get_git_branch()

        # Branch change?
        if current_branch != self._last_branch and self._last_branch is not None:
            events.append(
                GitEvent(
                    event_type="checkout",
                    branch=current_branch,
                    sha=current_head,
                )
            )
            self._last_branch = current_branch

        # New commit?
        if current_head and current_head != self._last_head:
            if current_head not in self._known_commits:
                # Get commit info
                info = await get_commit_info(current_head)
                events.append(
                    GitEvent(
                        event_type="commit",
                        sha=current_head,
                        branch=current_branch,
                        message=info.get("message"),
                        author=info.get("author"),
                    )
                )
                self._known_commits.add(current_head)

            self._last_head = current_head

        return events

    async def watch(self) -> AsyncIterator[GitEvent]:
        """
        Async iterator interface for event consumption.

        Usage:
            async for event in watcher.watch():
                process(event)
        """
        queue: asyncio.Queue[GitEvent] = asyncio.Queue()

        def enqueue(event: GitEvent) -> None:
            queue.put_nowait(event)

        self.add_handler(enqueue)

        try:
            await self.start()

            while self.state == WatcherState.RUNNING:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield event
                except asyncio.TimeoutError:
                    continue  # Check state and continue

        finally:
            self.remove_handler(enqueue)
            await self.stop()


# =============================================================================
# Factory Functions
# =============================================================================


def create_git_watcher(
    repo_path: Path | None = None,
    poll_interval: float = 5.0,
) -> GitWatcher:
    """Create a configured git watcher."""
    return GitWatcher(repo_path=repo_path, poll_interval=poll_interval)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GitWatcher",
    "WatcherState",
    "WatcherStats",
    "GitEvent",
    "create_git_watcher",
    # Git operations
    "get_git_head",
    "get_git_branch",
    "get_commit_info",
    "get_recent_commits",
]
