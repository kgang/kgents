"""
TriadGhostCollector: GhostWriter integration for Database Triad.

Extends GhostWriter to project Database Triad health to `.kgents/ghost/`:
- triad.status - One-line health summary
- triad.json - Full health metrics

Usage:
    ghost = create_ghost_writer()
    collector = TriadGhostCollector(ghost)
    collector.configure_triad(postgres_url, qdrant_url, redis_url)
    await collector.collect_and_project()

AGENTESE: self.vitals.triad.project
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TriadProjection:
    """Triad health data for ghost projection."""

    # Layer health (0.0-1.0)
    durability: float = 0.0  # PostgreSQL
    resonance: float = 0.0  # Qdrant
    reflex: float = 0.0  # Redis

    # CDC metrics
    cdc_lag_ms: float = 0.0
    outbox_pending: int = 0
    synapse_active: bool = False

    # Connection status
    postgres_connected: bool = False
    qdrant_connected: bool = False
    redis_connected: bool = False

    # Timestamps
    collected_at: str = ""
    last_sync: str | None = None

    @property
    def coherency_with_truth(self) -> float:
        """Calculate coherency with truth."""
        return max(0.0, 1.0 - (self.cdc_lag_ms / 5000))

    @property
    def overall(self) -> float:
        """Overall triad health."""
        return (self.durability + self.resonance + self.reflex) / 3

    @property
    def status_line(self) -> str:
        """One-line status summary."""
        parts = []

        # Layer status icons
        d_icon = "●" if self.postgres_connected else "○"
        r_icon = "●" if self.qdrant_connected else "○"
        f_icon = "●" if self.redis_connected else "○"

        parts.append(f"D:{d_icon}")
        parts.append(f"R:{r_icon}")
        parts.append(f"F:{f_icon}")

        # Overall percentage
        parts.append(f"({int(self.overall * 100)}%)")

        # CDC coherency
        if self.synapse_active:
            parts.append(f"cdc:{int(self.coherency_with_truth * 100)}%")

        # Outbox warning
        if self.outbox_pending > 10:
            parts.append(f"outbox:{self.outbox_pending}")

        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "durability": self.durability,
            "resonance": self.resonance,
            "reflex": self.reflex,
            "cdc_lag_ms": self.cdc_lag_ms,
            "outbox_pending": self.outbox_pending,
            "synapse_active": self.synapse_active,
            "postgres_connected": self.postgres_connected,
            "qdrant_connected": self.qdrant_connected,
            "redis_connected": self.redis_connected,
            "coherency_with_truth": self.coherency_with_truth,
            "overall": self.overall,
            "status_line": self.status_line,
            "collected_at": self.collected_at,
            "last_sync": self.last_sync,
        }


class TriadGhostCollector:
    """
    Collects Database Triad health and projects to ghost files.

    Can operate in:
    - Pull mode: Actively checks health of triad services
    - Push mode: Receives updates from running services

    Example:
        >>> collector = TriadGhostCollector(ghost_dir=Path(".kgents/ghost"))
        >>> collector.configure(postgres_url="postgres://...")
        >>> projection = await collector.collect()
        >>> await collector.project(projection)
    """

    TRIAD_STATUS = "triad.status"
    TRIAD_JSON = "triad.json"

    def __init__(
        self,
        ghost_dir: Path,
        postgres_url: str | None = None,
        qdrant_url: str | None = None,
        redis_url: str | None = None,
    ) -> None:
        self.ghost_dir = ghost_dir
        self.postgres_url = postgres_url
        self.qdrant_url = qdrant_url
        self.redis_url = redis_url

        self._last_projection: TriadProjection | None = None

    def configure(
        self,
        postgres_url: str | None = None,
        qdrant_url: str | None = None,
        redis_url: str | None = None,
    ) -> None:
        """Configure connection URLs."""
        if postgres_url:
            self.postgres_url = postgres_url
        if qdrant_url:
            self.qdrant_url = qdrant_url
        if redis_url:
            self.redis_url = redis_url

    async def collect(self) -> TriadProjection:
        """Collect current triad health by probing services."""
        projection = TriadProjection(
            collected_at=datetime.now(timezone.utc).isoformat(),
        )

        # Probe PostgreSQL
        if self.postgres_url:
            try:
                (
                    projection.durability,
                    projection.outbox_pending,
                ) = await self._probe_postgres()
                projection.postgres_connected = True
            except Exception as e:
                logger.debug(f"PostgreSQL probe failed: {e}")
                projection.postgres_connected = False

        # Probe Qdrant
        if self.qdrant_url:
            try:
                projection.resonance = await self._probe_qdrant()
                projection.qdrant_connected = True
            except Exception as e:
                logger.debug(f"Qdrant probe failed: {e}")
                projection.qdrant_connected = False

        # Probe Redis
        if self.redis_url:
            try:
                projection.reflex = await self._probe_redis()
                projection.redis_connected = True
            except Exception as e:
                logger.debug(f"Redis probe failed: {e}")
                projection.redis_connected = False

        # Calculate CDC lag if all connected
        if projection.postgres_connected and projection.qdrant_connected:
            projection.synapse_active = True
            # In production, this would query actual lag from outbox_stats
            projection.cdc_lag_ms = 100.0  # Placeholder

        self._last_projection = projection
        return projection

    async def _probe_postgres(self) -> tuple[float, int]:
        """Probe PostgreSQL health and outbox."""
        try:
            import asyncpg

            conn = await asyncpg.connect(self.postgres_url, timeout=5.0)
            try:
                # Simple query to verify health
                await conn.fetchval("SELECT 1")

                # Get outbox stats if table exists
                pending = 0
                try:
                    row = await conn.fetchrow(
                        "SELECT COUNT(*) as pending FROM outbox WHERE NOT processed"
                    )
                    if row:
                        pending = row["pending"]
                except Exception:
                    pass  # outbox might not exist

                return 1.0, pending
            finally:
                await conn.close()

        except ImportError:
            # asyncpg not available - assume healthy if URL provided
            return 0.5, 0

    async def _probe_qdrant(self) -> float:
        """Probe Qdrant health."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.qdrant_url}/readyz")
                if resp.status_code == 200:
                    return 1.0
                return 0.5

        except ImportError:
            return 0.5

    async def _probe_redis(self) -> float:
        """Probe Redis health."""
        try:
            import redis.asyncio as redis

            client = await redis.from_url(self.redis_url, socket_timeout=5.0)  # type: ignore[arg-type]
            try:
                pong = await client.ping()
                return 1.0 if pong else 0.5
            finally:
                await client.close()

        except ImportError:
            return 0.5

    async def project(self, projection: TriadProjection | None = None) -> None:
        """Project triad health to ghost files."""
        self.ghost_dir.mkdir(parents=True, exist_ok=True)

        proj = projection or self._last_projection
        if proj is None:
            proj = TriadProjection(collected_at=datetime.now(timezone.utc).isoformat())

        # Write status line
        status_path = self.ghost_dir / self.TRIAD_STATUS
        status_path.write_text(proj.status_line)

        # Write full JSON
        json_path = self.ghost_dir / self.TRIAD_JSON
        json_path.write_text(json.dumps(proj.to_dict(), indent=2))

    async def collect_and_project(self) -> TriadProjection:
        """Collect health and project to ghost files."""
        projection = await self.collect()
        await self.project(projection)
        return projection

    def update_from_vitals(
        self,
        durability: float | None = None,
        resonance: float | None = None,
        reflex: float | None = None,
        cdc_lag_ms: float | None = None,
        outbox_pending: int | None = None,
    ) -> None:
        """
        Update from AGENTESE self.vitals.triad values.

        Called by vitals context resolver when values are set.
        """
        if self._last_projection is None:
            self._last_projection = TriadProjection(
                collected_at=datetime.now(timezone.utc).isoformat()
            )

        if durability is not None:
            self._last_projection.durability = durability
            self._last_projection.postgres_connected = durability > 0
        if resonance is not None:
            self._last_projection.resonance = resonance
            self._last_projection.qdrant_connected = resonance > 0
        if reflex is not None:
            self._last_projection.reflex = reflex
            self._last_projection.redis_connected = reflex > 0
        if cdc_lag_ms is not None:
            self._last_projection.cdc_lag_ms = cdc_lag_ms
        if outbox_pending is not None:
            self._last_projection.outbox_pending = outbox_pending


# =============================================================================
# CLI Integration
# =============================================================================


def format_triad_status_cli(projection: TriadProjection) -> str:
    """Format triad status for CLI output."""
    lines = [
        "=== Database Triad Status ===",
        "",
    ]

    # Connection status
    d_status = "CONNECTED" if projection.postgres_connected else "DISCONNECTED"
    r_status = "CONNECTED" if projection.qdrant_connected else "DISCONNECTED"
    f_status = "CONNECTED" if projection.redis_connected else "DISCONNECTED"

    d_health = (
        f"{int(projection.durability * 100):3d}%" if projection.postgres_connected else " N/A"
    )
    r_health = f"{int(projection.resonance * 100):3d}%" if projection.qdrant_connected else " N/A"
    f_health = f"{int(projection.reflex * 100):3d}%" if projection.redis_connected else " N/A"

    lines.append(f"Durability (PostgreSQL):  {d_status:<12} {d_health}")
    lines.append(f"Resonance (Qdrant):       {r_status:<12} {r_health}")
    lines.append(f"Reflex (Redis):           {f_status:<12} {f_health}")
    lines.append("")

    # CDC status
    if projection.synapse_active:
        coherency = int(projection.coherency_with_truth * 100)
        lag = (
            f"{int(projection.cdc_lag_ms)}ms"
            if projection.cdc_lag_ms < 1000
            else f"{projection.cdc_lag_ms / 1000:.1f}s"
        )
        lines.append(f"CDC Coherency:            {coherency}%")
        lines.append(f"CDC Lag:                  {lag}")
        lines.append(f"Outbox Pending:           {projection.outbox_pending}")
    else:
        lines.append("CDC:                      INACTIVE")

    lines.append("")
    lines.append(f"Overall:                  {int(projection.overall * 100)}%")
    lines.append(f"Collected:                {projection.collected_at}")

    return "\n".join(lines)


# =============================================================================
# Factory Functions
# =============================================================================


def create_triad_collector(
    project_root: Path | None = None,
    postgres_url: str | None = None,
    qdrant_url: str | None = None,
    redis_url: str | None = None,
) -> TriadGhostCollector:
    """
    Create a TriadGhostCollector instance.

    Args:
        project_root: Project root (looks for .kgents/ghost/)
        postgres_url: PostgreSQL connection URL
        qdrant_url: Qdrant HTTP URL
        redis_url: Redis connection URL

    Returns:
        Configured TriadGhostCollector
    """
    import os

    if project_root is None:
        project_root = Path.cwd()

    ghost_dir = project_root / ".kgents" / "ghost"

    return TriadGhostCollector(
        ghost_dir=ghost_dir,
        postgres_url=postgres_url or os.environ.get("DATABASE_URL"),
        qdrant_url=qdrant_url or os.environ.get("QDRANT_URL"),
        redis_url=redis_url or os.environ.get("REDIS_URL"),
    )


async def project_triad_status(
    project_root: Path | None = None,
) -> TriadProjection:
    """
    One-shot triad status projection.

    Convenience function for CLI usage.
    """
    collector = create_triad_collector(project_root)
    return await collector.collect_and_project()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TriadProjection",
    "TriadGhostCollector",
    "create_triad_collector",
    "project_triad_status",
    "format_triad_status_cli",
]
