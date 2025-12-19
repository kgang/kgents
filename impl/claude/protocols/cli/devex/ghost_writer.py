"""
GhostWriter: Living Filesystem projection for the Exocortex.

DevEx V4 Phase 2 - The Sensorium.

Projects internal system state to `.kgents/ghost/` files that can be
opened in a split pane for peripheral awareness.

Design principles:
1. Non-intrusive: Updates every 3 minutes (not 500ms)
2. On-demand: `kgents ghost` triggers immediate projection
3. Separation: Manages projection files only, not test_flinches.jsonl
4. HYDRATE-aware: Can read from and append to HYDRATE.md

Files managed:
    thought_stream.md   - N-gent's inner monologue / system narrative
    tension_map.json    - Spec/impl contradictions, volatility heatmap
    health.status       - One-line health for IDE status bar
    context.json        - Current context vector, landmarks, focus

Files NOT managed (separate concerns):
    test_flinches.jsonl - Managed by FlinchStore/pytest hooks
    ci_signals.jsonl    - Managed by CI workflow

Usage:
    # On-demand projection
    ghost = GhostWriter(ghost_dir=Path(".kgents/ghost"))
    await ghost.project()

    # Background daemon (3-minute interval)
    await ghost.start_daemon()
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.i.semantic_field import SemanticField
    from agents.o.cortex_observer import CortexObserver
    from protocols.cli.instance_db.synapse import Synapse


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class ThoughtEntry:
    """A single entry in the thought stream."""

    timestamp: str
    source: str  # Agent that generated this thought
    content: str
    tags: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Format as markdown list item."""
        tags_str = " ".join(f"`{t}`" for t in self.tags) if self.tags else ""
        return f"- *{self.timestamp}* [{self.source}] {self.content} {tags_str}".strip()


@dataclass
class TensionPoint:
    """A point of tension between spec and implementation."""

    file_path: str
    description: str
    severity: str  # low, medium, high
    detected_at: str
    volatility: float = 0.0  # 0-1, based on recent churn

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GhostProjection:
    """Complete projection state for a single update."""

    timestamp: str
    health_line: str
    thoughts: list[ThoughtEntry]
    tensions: list[TensionPoint]
    context: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "health_line": self.health_line,
            "thought_count": len(self.thoughts),
            "tension_count": len(self.tensions),
            "context": self.context,
        }


# =============================================================================
# GhostWriter
# =============================================================================


class GhostWriter:
    """
    Projects system state to .kgents/ghost/ files.

    The ghost directory is a "Living Filesystem" - files that reflect
    internal state without requiring explicit queries.

    Projection frequency: Every 3 minutes (configurable), or on-demand.
    """

    # Files we manage
    THOUGHT_STREAM = "thought_stream.md"
    TENSION_MAP = "tension_map.json"
    HEALTH_STATUS = "health.status"
    CONTEXT_JSON = "context.json"

    # Files we don't touch (managed elsewhere)
    RESERVED_FILES = {"test_flinches.jsonl", "ci_signals.jsonl"}

    def __init__(
        self,
        ghost_dir: Path,
        hydrate_path: Path | None = None,
        interval_seconds: float = 180.0,  # 3 minutes
        max_thoughts: int = 50,
    ):
        """
        Initialize GhostWriter.

        Args:
            ghost_dir: Path to .kgents/ghost/
            hydrate_path: Path to HYDRATE.md (for integration)
            interval_seconds: Daemon update interval (default 3 minutes)
            max_thoughts: Max entries in thought_stream.md
        """
        self.ghost_dir = ghost_dir
        self.hydrate_path = hydrate_path
        self.interval_seconds = interval_seconds
        self.max_thoughts = max_thoughts

        # State
        self._running = False
        self._daemon_task: asyncio.Task[None] | None = None
        self._thoughts: list[ThoughtEntry] = []
        self._tensions: list[TensionPoint] = []
        self._last_projection: GhostProjection | None = None

        # Optional integrations (set via configure)
        self._synapse: Synapse | None = None
        self._observer: CortexObserver | None = None
        self._field: SemanticField | None = None

    def configure(
        self,
        synapse: Synapse | None = None,
        observer: CortexObserver | None = None,
        field: SemanticField | None = None,
    ) -> None:
        """
        Configure optional integrations.

        These allow richer projections but are not required.
        """
        self._synapse = synapse
        self._observer = observer
        self._field = field

    # =========================================================================
    # Thought Stream
    # =========================================================================

    def add_thought(
        self,
        content: str,
        source: str = "system",
        tags: list[str] | None = None,
    ) -> None:
        """
        Add a thought to the stream.

        Thoughts are buffered and written on next projection.
        """
        entry = ThoughtEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            source=source,
            content=content,
            tags=tags or [],
        )
        self._thoughts.append(entry)

        # Trim to max
        if len(self._thoughts) > self.max_thoughts:
            self._thoughts = self._thoughts[-self.max_thoughts :]

    def add_tension(
        self,
        file_path: str,
        description: str,
        severity: str = "medium",
        volatility: float = 0.0,
    ) -> None:
        """
        Add a tension point.

        Tensions are spec/impl mismatches or areas of concern.
        """
        tension = TensionPoint(
            file_path=file_path,
            description=description,
            severity=severity,
            detected_at=datetime.now().isoformat(),
            volatility=volatility,
        )

        # Replace existing tension for same file, or add
        self._tensions = [t for t in self._tensions if t.file_path != file_path]
        self._tensions.append(tension)

    # =========================================================================
    # Projection
    # =========================================================================

    async def project(self) -> GhostProjection:
        """
        Project current state to ghost files.

        This is the main operation - called on-demand or by daemon.
        """
        # Ensure directory exists
        self.ghost_dir.mkdir(parents=True, exist_ok=True)

        # Gather state
        timestamp = datetime.now().isoformat()
        health_line = await self._generate_health_line()
        context = await self._generate_context()

        # Enrich thoughts from system state
        await self._enrich_thoughts()

        # Create projection
        projection = GhostProjection(
            timestamp=timestamp,
            health_line=health_line,
            thoughts=list(self._thoughts),
            tensions=list(self._tensions),
            context=context,
        )

        # Write files
        await self._write_thought_stream(projection)
        await self._write_tension_map(projection)
        await self._write_health_status(projection)
        await self._write_context(projection)

        self._last_projection = projection
        return projection

    async def _generate_health_line(self) -> str:
        """Generate one-line health status."""
        parts = []

        if self._observer:
            try:
                snapshot = self._observer.get_health()
                parts.append(f"cortex:{snapshot.overall.value}")

                if snapshot.synapse.available:
                    parts.append(f"surprise:{snapshot.synapse.surprise_avg:.2f}")

                if snapshot.hippocampus.available:
                    parts.append(f"mem:{snapshot.hippocampus.utilization:.0%}")

                if snapshot.dreamer.available:
                    parts.append(f"dreams:{snapshot.dreamer.dream_cycles_total}")
            except Exception:
                parts.append("cortex:unknown")
        else:
            parts.append("cortex:not_connected")

        if self._field:
            try:
                active = len([p for p in self._field._pheromones.values() if p.is_active])
                parts.append(f"signals:{active}")
            except Exception:
                pass

        return " ".join(parts)

    async def _generate_context(self) -> dict[str, Any]:
        """Generate context summary."""
        context: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "projection_count": (
                self._last_projection.context.get("projection_count", 0) + 1
                if self._last_projection
                else 1
            ),
        }

        # Add HYDRATE summary if available
        if self.hydrate_path and self.hydrate_path.exists():
            try:
                content = self.hydrate_path.read_text()
                # Extract status line
                for line in content.split("\n"):
                    if line.startswith("**Status**:"):
                        context["hydrate_status"] = line.replace("**Status**:", "").strip()
                        break
                    if line.startswith("## Current:"):
                        context["hydrate_current"] = line.replace("## Current:", "").strip()
                        break
            except Exception:
                pass

        # Add field summary
        if self._field:
            try:
                context["field_tick"] = self._field._current_tick
                context["active_pheromones"] = len(
                    [p for p in self._field._pheromones.values() if p.is_active]
                )
            except Exception:
                pass

        return context

    async def _enrich_thoughts(self) -> None:
        """Add system-generated thoughts based on current state."""
        # From synapse: recent high-surprise events
        if self._synapse:
            try:
                metrics = self._synapse.metrics()  # type: ignore[operator]
                # Note: metrics dict doesn't have flashbulb_count,
                # using fast_path_count as proxy for high-surprise events
                fast_path = metrics.get("fast_path_count", 0)
                if fast_path > 0:
                    self.add_thought(
                        f"High-surprise events detected: {fast_path}",
                        source="synapse",
                        tags=["alert"],
                    )
            except Exception:
                pass

        # From observer: health concerns
        if self._observer:
            try:
                snapshot = self._observer.get_health()
                if snapshot.coherency.ghost_count > 0:
                    self.add_thought(
                        f"Ghost memories detected: {snapshot.coherency.ghost_count}",
                        source="cortex",
                        tags=["maintenance"],
                    )
            except Exception:
                pass

    # =========================================================================
    # File Writers
    # =========================================================================

    async def _write_thought_stream(self, projection: GhostProjection) -> None:
        """Write thought_stream.md."""
        path = self.ghost_dir / self.THOUGHT_STREAM

        lines = [
            "# Thought Stream",
            "",
            f"*Last updated: {projection.timestamp}*",
            "",
        ]

        if not projection.thoughts:
            lines.append("*No thoughts yet. The system is quiet.*")
        else:
            for thought in reversed(projection.thoughts[-20:]):  # Most recent first
                lines.append(thought.to_markdown())

        lines.append("")
        lines.append("---")
        lines.append("*This file updates every 3 minutes or on `kgents ghost`*")

        path.write_text("\n".join(lines))

    async def _write_tension_map(self, projection: GhostProjection) -> None:
        """Write tension_map.json."""
        path = self.ghost_dir / self.TENSION_MAP

        data = {
            "timestamp": projection.timestamp,
            "tensions": [t.to_dict() for t in projection.tensions],
            "summary": {
                "total": len(projection.tensions),
                "high": len([t for t in projection.tensions if t.severity == "high"]),
                "medium": len([t for t in projection.tensions if t.severity == "medium"]),
                "low": len([t for t in projection.tensions if t.severity == "low"]),
            },
        }

        path.write_text(json.dumps(data, indent=2))

    async def _write_health_status(self, projection: GhostProjection) -> None:
        """Write health.status (single line for IDE status bar)."""
        path = self.ghost_dir / self.HEALTH_STATUS
        path.write_text(projection.health_line)

    async def _write_context(self, projection: GhostProjection) -> None:
        """Write context.json."""
        path = self.ghost_dir / self.CONTEXT_JSON
        path.write_text(json.dumps(projection.context, indent=2))

    # =========================================================================
    # Daemon
    # =========================================================================

    async def start_daemon(self) -> None:
        """Start background daemon that projects every interval_seconds."""
        if self._running:
            return

        self._running = True
        self._daemon_task = asyncio.create_task(self._daemon_loop())

    async def stop_daemon(self) -> None:
        """Stop background daemon."""
        self._running = False
        if self._daemon_task:
            self._daemon_task.cancel()
            try:
                await self._daemon_task
            except asyncio.CancelledError:
                pass
            self._daemon_task = None

    async def _daemon_loop(self) -> None:
        """Background loop for periodic projection."""
        while self._running:
            try:
                await self.project()
            except Exception:
                pass  # Don't crash daemon on projection errors

            await asyncio.sleep(self.interval_seconds)

    # =========================================================================
    # HYDRATE Integration
    # =========================================================================

    def append_to_hydrate(self, event: str, source: str = "ghost") -> None:
        """
        Append an event to HYDRATE.md.

        Lightweight integration - adds timestamped entry to bottom of file.
        """
        if not self.hydrate_path or not self.hydrate_path.exists():
            return

        try:
            content = self.hydrate_path.read_text()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = f"\n[{timestamp}] [{source}] {event}"

            # Append to end
            self.hydrate_path.write_text(content + entry)
        except Exception:
            pass  # Never crash on HYDRATE write


# =============================================================================
# Factory Functions
# =============================================================================


def create_ghost_writer(
    project_root: Path | None = None,
    interval_seconds: float = 180.0,
) -> GhostWriter:
    """
    Create a GhostWriter instance.

    Args:
        project_root: Project root (looks for .kgents/)
        interval_seconds: Daemon interval (default 3 minutes)

    Returns:
        Configured GhostWriter
    """
    if project_root is None:
        project_root = Path.cwd()

    ghost_dir = project_root / ".kgents" / "ghost"
    hydrate_path_candidate = project_root / "HYDRATE.md"

    hydrate_path: Path | None = hydrate_path_candidate if hydrate_path_candidate.exists() else None

    return GhostWriter(
        ghost_dir=ghost_dir,
        hydrate_path=hydrate_path,
        interval_seconds=interval_seconds,
    )


async def project_once(project_root: Path | None = None) -> GhostProjection:
    """
    One-shot projection to ghost files.

    Convenience function for CLI usage.
    """
    writer = create_ghost_writer(project_root)
    return await writer.project()
