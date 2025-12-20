"""
CIWatcher: Poll-Based GitHub Actions Monitoring.

Polls GitHub API for workflow run status changes. Unlike other watchers
which are event-driven, CI requires polling because webhooks need
public endpoints.

Key Features:
- 60-second polling interval (respects rate limits)
- Exponential backoff on errors
- Deduplication by run ID
- Rate-limit awareness (checks X-RateLimit-Remaining)

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"
    Exception: CI polling IS the event source (external system).

Integration:
    watcher = CIWatcher(config=CIConfig(
        owner="kentgang",
        repo="kgents",
        token="ghp_...",  # Optional for public repos
    ))

    async for event in watcher.watch():
        print(f"CI: {event.workflow} → {event.status}")

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from services.witness.polynomial import CIEvent
from services.witness.watchers.base import BaseWatcher

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CIConfig:
    """Configuration for CIWatcher."""

    # Repository to watch
    owner: str = ""
    repo: str = ""

    # GitHub token (optional for public repos)
    token: str | None = None

    # Polling settings
    poll_interval_seconds: float = 60.0
    max_backoff_seconds: float = 300.0  # 5 minutes max
    backoff_multiplier: float = 2.0

    # Rate limit safety margin (stop polling if below this)
    rate_limit_floor: int = 10

    # Maximum runs to track (for deduplication memory)
    max_tracked_runs: int = 100

    # Filter by workflow name (empty = all workflows)
    workflow_filter: tuple[str, ...] = ()


# =============================================================================
# GitHub API Client (Minimal)
# =============================================================================


@dataclass
class WorkflowRun:
    """Parsed workflow run from GitHub API."""

    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: str | None  # success, failure, cancelled, etc.
    created_at: datetime
    updated_at: datetime
    head_branch: str
    duration_seconds: int | None = None


async def fetch_workflow_runs(
    owner: str,
    repo: str,
    token: str | None = None,
    per_page: int = 10,
) -> tuple[list[WorkflowRun], int, int]:
    """
    Fetch recent workflow runs from GitHub API.

    Returns:
        (runs, rate_limit_remaining, rate_limit_reset)
    """
    try:
        import httpx
    except ImportError:
        logger.warning("httpx not available, CIWatcher disabled")
        return [], 60, 0

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "kgents-witness",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=headers,
                params={"per_page": per_page},
            )

            # Extract rate limit info
            rate_remaining = int(response.headers.get("X-RateLimit-Remaining", 60))
            rate_reset = int(response.headers.get("X-RateLimit-Reset", 0))

            if response.status_code == 403:
                # Rate limited
                logger.warning(f"GitHub API rate limited (resets at {rate_reset})")
                return [], 0, rate_reset

            if response.status_code != 200:
                logger.warning(f"GitHub API error: {response.status_code}")
                return [], rate_remaining, rate_reset

            data = response.json()
            runs: list[WorkflowRun] = []

            for run in data.get("workflow_runs", []):
                created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
                updated = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))

                duration = None
                if run["status"] == "completed":
                    duration = int((updated - created).total_seconds())

                runs.append(
                    WorkflowRun(
                        id=run["id"],
                        name=run["name"],
                        status=run["status"],
                        conclusion=run.get("conclusion"),
                        created_at=created,
                        updated_at=updated,
                        head_branch=run.get("head_branch", ""),
                        duration_seconds=duration,
                    )
                )

            return runs, rate_remaining, rate_reset

    except Exception as e:
        logger.error(f"Failed to fetch workflow runs: {e}")
        return [], 60, 0


# =============================================================================
# CIWatcher
# =============================================================================


class CIWatcher(BaseWatcher[CIEvent]):
    """
    Poll-based GitHub Actions watcher.

    Polls GitHub API every 60 seconds (configurable) to detect
    workflow status changes.

    Features:
    - Tracks seen run IDs to avoid duplicate events
    - Exponential backoff on errors
    - Rate limit awareness
    - Emits events for: workflow_started, workflow_complete, check_failed

    Usage:
        config = CIConfig(owner="kentgang", repo="kgents")
        watcher = CIWatcher(config=config)

        async for event in watcher.watch():
            print(f"CI: {event.workflow} → {event.status}")
    """

    def __init__(self, config: CIConfig | None = None) -> None:
        super().__init__()
        self.config = config or CIConfig()

        # Track seen runs to detect changes
        self._seen_runs: dict[int, str] = {}  # run_id → last known status

        # Current backoff (reset on success)
        self._current_backoff: float = self.config.poll_interval_seconds

        # Rate limit state
        self._rate_limit_remaining: int = 60
        self._rate_limit_reset: int = 0

    async def _on_start(self) -> None:
        """Initialize watcher state."""
        if not self.config.owner or not self.config.repo:
            logger.warning("CIWatcher started without owner/repo configured")
            return

        logger.info(
            f"CIWatcher starting: {self.config.owner}/{self.config.repo} "
            f"(poll interval: {self.config.poll_interval_seconds}s)"
        )

    async def _watch_loop(self) -> None:
        """Main polling loop."""
        if not self.config.owner or not self.config.repo:
            logger.warning("CIWatcher: no owner/repo configured, entering idle mode")
            await self._stop_event.wait()
            return

        while not self._stop_event.is_set():
            try:
                await self._poll_once()
                # Reset backoff on success
                self._current_backoff = self.config.poll_interval_seconds

            except Exception as e:
                logger.error(f"CIWatcher poll error: {e}")
                self.stats.record_error()
                # Exponential backoff
                self._current_backoff = min(
                    self._current_backoff * self.config.backoff_multiplier,
                    self.config.max_backoff_seconds,
                )

            # Wait for next poll (or stop signal)
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._current_backoff,
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue polling

    async def _poll_once(self) -> None:
        """Execute a single poll cycle."""
        # Check rate limit
        if self._rate_limit_remaining < self.config.rate_limit_floor:
            logger.warning(
                f"Rate limit low ({self._rate_limit_remaining}), "
                f"waiting until reset"
            )
            return

        # Fetch runs
        runs, rate_remaining, rate_reset = await fetch_workflow_runs(
            owner=self.config.owner,
            repo=self.config.repo,
            token=self.config.token,
        )

        self._rate_limit_remaining = rate_remaining
        self._rate_limit_reset = rate_reset

        # Process runs
        for run in runs:
            # Apply workflow filter
            if self.config.workflow_filter:
                if run.name not in self.config.workflow_filter:
                    continue

            self._process_run(run)

        # Prune old runs from memory
        self._prune_seen_runs()

    def _process_run(self, run: WorkflowRun) -> None:
        """Process a workflow run and emit events if state changed."""
        last_status = self._seen_runs.get(run.id)

        if last_status is None:
            # New run - check if it's in_progress (just started)
            if run.status == "in_progress":
                self._emit_event(run, "workflow_started")
            elif run.status == "completed":
                # Just saw a completed run for the first time
                self._emit_event(run, "workflow_complete")

        elif last_status != run.status:
            # Status changed
            if run.status == "completed":
                self._emit_event(run, "workflow_complete")
            elif run.status == "in_progress" and last_status == "queued":
                self._emit_event(run, "workflow_started")

        # Update seen runs
        self._seen_runs[run.id] = run.status

    def _emit_event(self, run: WorkflowRun, event_type: str) -> None:
        """Create and emit a CIEvent."""
        # Determine status from conclusion for completed runs
        status: str | None = None
        if run.status == "completed":
            status = run.conclusion or "unknown"
        else:
            status = run.status

        event = CIEvent(
            event_type=event_type,
            workflow=run.name,
            job=None,  # Would need separate API call for job-level detail
            status=status,
            duration_seconds=run.duration_seconds,
        )

        self._emit(event)

        # Emit additional check_failed event for failures
        if event_type == "workflow_complete" and run.conclusion == "failure":
            fail_event = CIEvent(
                event_type="check_failed",
                workflow=run.name,
                job=None,
                status="failure",
                duration_seconds=run.duration_seconds,
            )
            self._emit(fail_event)

    def _prune_seen_runs(self) -> None:
        """Remove old entries from seen runs to prevent memory growth."""
        if len(self._seen_runs) <= self.config.max_tracked_runs:
            return

        # Keep only the most recent runs (by ID, which are monotonically increasing)
        sorted_ids = sorted(self._seen_runs.keys())
        to_remove = sorted_ids[: len(sorted_ids) - self.config.max_tracked_runs]
        for run_id in to_remove:
            del self._seen_runs[run_id]

    async def _cleanup(self) -> None:
        """Cleanup on stop."""
        logger.info(
            f"CIWatcher stopped. Tracked {len(self._seen_runs)} runs, "
            f"rate limit remaining: {self._rate_limit_remaining}"
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_ci_watcher(
    owner: str = "",
    repo: str = "",
    token: str | None = None,
    poll_interval: float = 60.0,
) -> CIWatcher:
    """Create a configured CI watcher."""
    config = CIConfig(
        owner=owner,
        repo=repo,
        token=token,
        poll_interval_seconds=poll_interval,
    )
    return CIWatcher(config=config)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CIWatcher",
    "CIConfig",
    "WorkflowRun",
    "create_ci_watcher",
    "fetch_workflow_runs",
]
