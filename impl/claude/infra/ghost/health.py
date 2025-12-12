"""
Composite Health - Aggregate health from all collectors.

The health system follows the Trust Maturity Model:
- Level 0: READ-ONLY - Observe without modification
- Level 1: BOUNDED - Modify within constraints
- Level 2: SUGGESTION - Propose and confirm
- Level 3: AUTONOMOUS - Act within rails

This module implements Level 0: accurate observation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .collectors import CollectorResult


class HealthLevel(Enum):
    """Overall health classification."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class CompositeHealth:
    """
    Aggregated health status from all collectors.

    This is the single source of truth for system health,
    suitable for display in IDE status bars or CLI.
    """

    level: HealthLevel
    timestamp: str
    collectors: dict[str, CollectorResult] = field(default_factory=dict)
    health_line: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_results(cls, results: list[CollectorResult]) -> "CompositeHealth":
        """
        Create composite health from collector results.

        Aggregates all results and determines overall health level.
        """
        timestamp = datetime.now().isoformat()

        # Index by source
        collectors = {r.source: r for r in results}

        # Determine overall level
        error_count = sum(1 for r in results if not r.success)
        if error_count == len(results):
            level = HealthLevel.ERROR
        elif error_count > 0:
            level = HealthLevel.DEGRADED
        else:
            # Check for warning conditions
            has_warnings = False

            # Git: uncommitted changes > 20 is a warning
            git_result = collectors.get("git")
            if git_result and git_result.success:
                dirty = git_result.data.get("dirty_count", 0)
                if dirty > 20:
                    has_warnings = True

            # Flinch: recent failures in last hour is a warning
            flinch_result = collectors.get("flinch")
            if flinch_result and flinch_result.success:
                last_hour = flinch_result.data.get("last_hour", 0)
                if last_hour > 5:
                    has_warnings = True

            level = HealthLevel.WARNING if has_warnings else HealthLevel.HEALTHY

        # Build composite health line
        parts = [f"cortex:{level.value}"]
        for r in results:
            if r.success:
                # Extract the key part of each collector's health line
                collector_health = r.data.get("health_line", "")
                if collector_health:
                    # Just add the collector's status, not the full line
                    parts.append(collector_health)
            else:
                parts.append(f"{r.source}:error")

        health_line = " | ".join(parts)

        # Build details
        details: dict[str, Any] = {}
        for r in results:
            if r.success:
                details[r.source] = r.data
            else:
                details[r.source] = {"error": r.error}

        return cls(
            level=level,
            timestamp=timestamp,
            collectors=collectors,
            health_line=health_line,
            details=details,
        )

    def to_status_line(self) -> str:
        """
        Generate one-line status for .kgents/ghost/health.status.

        This is what the developer sees at a glance.
        """
        return self.health_line

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "level": self.level.value,
            "timestamp": self.timestamp,
            "health_line": self.health_line,
            "details": self.details,
        }


def create_composite_health(results: list[CollectorResult]) -> CompositeHealth:
    """
    Factory function for creating composite health.

    Usage:
        collectors = create_all_collectors()
        results = await asyncio.gather(*[c.collect() for c in collectors])
        health = create_composite_health(results)
        print(health.to_status_line())
    """
    return CompositeHealth.from_results(results)
