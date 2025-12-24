"""
Probe Types: Core data structures for categorical law checks.

This module defines the probe result types and classifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ProbeType(Enum):
    """Classification of probe types."""

    IDENTITY = "identity"  # Id >> f == f == f >> Id
    ASSOCIATIVITY = "associativity"  # (f >> g) >> h == f >> (g >> h)
    COHERENCE = "coherence"  # Sheaf gluing check
    BUDGET = "budget"  # Resource budget remaining
    TRUST = "trust"  # Trust level check
    HEALTH = "health"  # Crown Jewel health


class ProbeStatus(Enum):
    """Probe execution status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(frozen=True)
class ProbeResult:
    """
    Result of a probe execution.

    Philosophy:
        "The proof IS the decision. The mark IS the witness."
        Only emit marks on FAILURE to keep probes cheap.

    Attributes:
        name: Probe identifier (e.g., "identity:read_tool")
        probe_type: Classification of probe
        status: Pass/fail/skip/error
        details: Human-readable details (empty if passed)
        duration_ms: Execution time in milliseconds
        timestamp: When the probe was executed
        mark_id: Witness mark ID (only on failure)
    """

    name: str
    probe_type: ProbeType
    status: ProbeStatus
    details: str = ""
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    mark_id: str | None = None

    @property
    def passed(self) -> bool:
        """Whether the probe passed."""
        return self.status == ProbeStatus.PASSED

    @property
    def failed(self) -> bool:
        """Whether the probe failed."""
        return self.status == ProbeStatus.FAILED

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "probe_type": self.probe_type.value,
            "status": self.status.value,
            "passed": self.passed,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "mark_id": self.mark_id,
        }


@dataclass(frozen=True)
class HealthStatus:
    """
    Health status for a Crown Jewel or system component.

    Attributes:
        component: Component name (e.g., "brain", "witness", "k-block")
        healthy: Overall health status
        checks: Individual health check results
        uptime_ms: Time since component initialization
        last_error: Most recent error message (if any)
    """

    component: str
    healthy: bool
    checks: dict[str, bool]
    uptime_ms: float = 0.0
    last_error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "component": self.component,
            "healthy": self.healthy,
            "checks": self.checks,
            "uptime_ms": self.uptime_ms,
            "last_error": self.last_error,
        }


__all__ = [
    "ProbeResult",
    "ProbeStatus",
    "ProbeType",
    "HealthStatus",
]
