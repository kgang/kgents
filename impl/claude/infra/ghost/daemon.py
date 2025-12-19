"""
Ghost Daemon - Background projection loop with real data.

The daemon runs in the background and projects system state to
.kgents/ghost/ files at regular intervals (default: 3 minutes).

Design Principles:
1. Fail gracefully - never crash the daemon
2. Log errors to thought_stream.md
3. Update health.status even when collectors fail
4. Support both foreground and background modes

Integration with ClaudeCLIRuntime:
- The daemon itself doesn't use LLM calls (pure data collection)
- Future: LLM-powered analysis can be added via ClaudeCLIRuntime
"""

from __future__ import annotations

import asyncio
import json
import signal
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .collectors import CollectorResult, GhostCollector, create_all_collectors
from .health import CompositeHealth, create_composite_health


@dataclass
class ProjectionResult:
    """Result of a single projection cycle."""

    timestamp: str
    health: CompositeHealth
    files_written: list[str]
    errors: list[str]


class GhostDaemon:
    """
    Background daemon for projecting system state to .kgents/ghost/.

    Usage:
        daemon = GhostDaemon(project_root=Path.cwd())
        daemon.add_collector(GitCollector())
        daemon.add_collector(FlinchCollector())

        # Foreground (blocking)
        await daemon.run_foreground()

        # Or background (non-blocking)
        await daemon.start()
        # ... do other work ...
        await daemon.stop()
    """

    # Files we write to
    HEALTH_STATUS = "health.status"
    THOUGHT_STREAM = "thought_stream.md"
    CONTEXT_JSON = "context.json"
    TENSION_MAP = "tension_map.json"
    FLINCH_SUMMARY = "flinch_summary.json"
    TRACE_SUMMARY = "trace_summary.json"
    MEMORY_SUMMARY = "memory_summary.json"

    def __init__(
        self,
        project_root: Path | None = None,
        interval_seconds: float = 180.0,  # 3 minutes
        on_progress: Callable[[str], None] | None = None,
    ):
        """
        Initialize the ghost daemon.

        Args:
            project_root: Project root (looks for .kgents/)
            interval_seconds: Projection interval (default 3 minutes)
            on_progress: Optional callback for progress updates
        """
        self.project_root = project_root or Path.cwd()
        self.ghost_dir = self.project_root / ".kgents" / "ghost"
        self.interval_seconds = interval_seconds
        self.on_progress = on_progress or (lambda msg: None)

        # Collectors
        self._collectors: list[GhostCollector] = []

        # State
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._projection_count = 0
        self._thoughts: list[dict[str, Any]] = []

    def add_collector(self, collector: GhostCollector) -> None:
        """Add a collector to the daemon."""
        self._collectors.append(collector)

    def add_thought(
        self,
        content: str,
        source: str = "daemon",
        tags: list[str] | None = None,
    ) -> None:
        """Add a thought to the stream (will be written on next projection)."""
        self._thoughts.append(
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "source": source,
                "content": content,
                "tags": tags or [],
            }
        )
        # Keep last 50 thoughts
        self._thoughts = self._thoughts[-50:]

    async def project_once(self) -> ProjectionResult:
        """
        Perform a single projection cycle.

        Collects data from all collectors and writes to ghost files.
        """
        timestamp = datetime.now().isoformat()
        files_written: list[str] = []
        errors: list[str] = []

        # Ensure ghost directory exists
        self.ghost_dir.mkdir(parents=True, exist_ok=True)

        # Collect from all sources
        results: list[CollectorResult] = []
        for collector in self._collectors:
            try:
                result = await collector.collect()
                results.append(result)
                if not result.success:
                    errors.append(f"{collector.name}: {result.error}")
            except Exception as e:
                errors.append(f"{collector.name}: {e}")
                results.append(
                    CollectorResult(
                        source=collector.name,
                        timestamp=timestamp,
                        success=False,
                        error=str(e),
                    )
                )

        # Create composite health
        health = create_composite_health(results)

        # Write files
        try:
            await self._write_health_status(health)
            files_written.append(self.HEALTH_STATUS)
        except Exception as e:
            errors.append(f"health.status: {e}")

        try:
            await self._write_thought_stream(health)
            files_written.append(self.THOUGHT_STREAM)
        except Exception as e:
            errors.append(f"thought_stream.md: {e}")

        try:
            await self._write_context(health, results)
            files_written.append(self.CONTEXT_JSON)
        except Exception as e:
            errors.append(f"context.json: {e}")

        # Write flinch summary if flinch data exists
        flinch_result = health.collectors.get("flinch")
        if flinch_result and flinch_result.success:
            try:
                await self._write_flinch_summary(flinch_result)
                files_written.append(self.FLINCH_SUMMARY)
            except Exception as e:
                errors.append(f"flinch_summary.json: {e}")

        # Write trace summary if trace data exists
        trace_result = health.collectors.get("trace")
        if trace_result and trace_result.success:
            try:
                await self._write_trace_summary(trace_result)
                files_written.append(self.TRACE_SUMMARY)
            except Exception as e:
                errors.append(f"trace_summary.json: {e}")

        # Write memory summary if memory data exists
        memory_result = health.collectors.get("memory")
        if memory_result and memory_result.success:
            try:
                await self._write_memory_summary(memory_result)
                files_written.append(self.MEMORY_SUMMARY)
            except Exception as e:
                errors.append(f"memory_summary.json: {e}")

        self._projection_count += 1

        return ProjectionResult(
            timestamp=timestamp,
            health=health,
            files_written=files_written,
            errors=errors,
        )

    async def _write_health_status(self, health: CompositeHealth) -> None:
        """Write health.status (one line for IDE)."""
        path = self.ghost_dir / self.HEALTH_STATUS
        path.write_text(health.to_status_line())

    async def _write_thought_stream(self, health: CompositeHealth) -> None:
        """Write thought_stream.md."""
        path = self.ghost_dir / self.THOUGHT_STREAM

        lines = [
            "# Thought Stream",
            "",
            f"*Last updated: {health.timestamp}*",
            "",
        ]

        # Add system thought about current state
        self.add_thought(
            f"Projection #{self._projection_count}: {health.level.value}",
            source="ghost",
            tags=["projection"],
        )

        if not self._thoughts:
            lines.append("*No thoughts yet. The system is quiet.*")
        else:
            for thought in reversed(self._thoughts[-20:]):
                tags_str = " ".join(f"`{t}`" for t in thought.get("tags", []))
                line = f"- *{thought['timestamp']}* [{thought['source']}] {thought['content']}"
                if tags_str:
                    line += f" {tags_str}"
                lines.append(line)

        lines.append("")
        lines.append("---")
        lines.append("*This file updates every 3 minutes or on `kgents ghost`*")

        path.write_text("\n".join(lines))

    async def _write_context(self, health: CompositeHealth, results: list[CollectorResult]) -> None:
        """Write context.json."""
        path = self.ghost_dir / self.CONTEXT_JSON

        context: dict[str, Any] = {
            "timestamp": health.timestamp,
            "projection_count": self._projection_count,
            "level": health.level.value,
            "collectors": {},
        }

        # Add collector summaries
        for r in results:
            if r.success:
                context["collectors"][r.source] = {
                    "status": "ok",
                    "summary": r.data.get("health_line", ""),
                }
            else:
                context["collectors"][r.source] = {
                    "status": "error",
                    "error": r.error,
                }

        path.write_text(json.dumps(context, indent=2))

    async def _write_flinch_summary(self, flinch_result: CollectorResult) -> None:
        """Write flinch_summary.json."""
        path = self.ghost_dir / self.FLINCH_SUMMARY
        path.write_text(json.dumps(flinch_result.data, indent=2))

    async def _write_trace_summary(self, trace_result: CollectorResult) -> None:
        """Write trace_summary.json."""
        path = self.ghost_dir / self.TRACE_SUMMARY
        path.write_text(json.dumps(trace_result.data, indent=2))

    async def _write_memory_summary(self, memory_result: CollectorResult) -> None:
        """Write memory_summary.json (Four Pillars data)."""
        path = self.ghost_dir / self.MEMORY_SUMMARY
        path.write_text(json.dumps(memory_result.data, indent=2))

    async def start(self) -> None:
        """Start the daemon in background mode."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._daemon_loop())
        self.on_progress("Daemon started")

    async def stop(self) -> None:
        """Stop the daemon."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self.on_progress("Daemon stopped")

    async def run_foreground(self) -> None:
        """
        Run daemon in foreground (blocking).

        Handles SIGINT/SIGTERM for graceful shutdown.
        """
        self._running = True

        # Setup signal handlers
        loop = asyncio.get_event_loop()

        def handle_signal() -> None:
            self._running = False
            self.on_progress("\nShutdown signal received")

        try:
            loop.add_signal_handler(signal.SIGINT, handle_signal)
            loop.add_signal_handler(signal.SIGTERM, handle_signal)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

        # Initial projection
        self.on_progress("Initial projection...")
        result = await self.project_once()
        self.on_progress(f"Projected: {result.health.to_status_line()}")

        # Main loop
        while self._running:
            await asyncio.sleep(self.interval_seconds)
            if not self._running:
                break

            self.on_progress("Projecting...")
            result = await self.project_once()
            self.on_progress(f"Projected: {result.health.to_status_line()}")

        # Final projection
        self.on_progress("Final projection...")
        await self.project_once()

    async def _daemon_loop(self) -> None:
        """Background daemon loop."""
        # Initial projection
        await self.project_once()

        while self._running:
            await asyncio.sleep(self.interval_seconds)
            if not self._running:
                break
            await self.project_once()


def create_ghost_daemon(
    project_root: Path | None = None,
    interval_seconds: float = 180.0,
    on_progress: Callable[[str], None] | None = None,
) -> GhostDaemon:
    """
    Factory function for creating a configured ghost daemon.

    Creates daemon with all standard collectors pre-configured.

    Usage:
        daemon = create_ghost_daemon()
        await daemon.run_foreground()  # Or: await daemon.start()
    """
    if project_root is None:
        project_root = Path.cwd()

    daemon = GhostDaemon(
        project_root=project_root,
        interval_seconds=interval_seconds,
        on_progress=on_progress,
    )

    # Add all standard collectors
    for collector in create_all_collectors(project_root):
        daemon.add_collector(collector)

    return daemon
