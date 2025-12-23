"""
Proxy Handle Types: Core abstractions for epistemic hygiene.

AD-015: Proxy Handles & Transparent Batch Processes

The philosophical insight:
    "The representation of an object is distinct from the object itself."

A proxy handle is NOT a cache. A cache is an optimization; a proxy handle is
an ontological claim about the nature of computed data.

Every proxy handle knows:
- Who computed it (provenance)
- When it was computed (temporal identity)
- What it represents (source type)
- Whether it's still valid (staleness)

AGENTESE: services.proxy.types
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")


# =============================================================================
# Enums
# =============================================================================


class HandleStatus(str, Enum):
    """
    Proxy handle lifecycle states.

    State Machine:
        EMPTY → COMPUTING → FRESH → STALE → COMPUTING → ...
                    ↓                          ↑
                  ERROR ─────────────────────────
    """

    EMPTY = "empty"  # No handle exists
    COMPUTING = "computing"  # Computation in progress
    FRESH = "fresh"  # Valid data available
    STALE = "stale"  # TTL expired or source changed
    ERROR = "error"  # Computation failed


class SourceType(str, Enum):
    """
    Known proxy handle source types.

    Extension point: Use CUSTOM for domain-specific sources,
    then promote to first-class enum as patterns emerge.
    """

    # Existing (to be migrated)
    SPEC_CORPUS = "spec_corpus"  # Spec ledger analysis

    # New capabilities
    WITNESS_GRAPH = "witness_graph"  # Witness mark summaries
    CODEBASE_GRAPH = "codebase_graph"  # Codebase topology analysis
    TOWN_SNAPSHOT = "town_snapshot"  # Agent town state
    MEMORY_CRYSTALS = "memory_crystals"  # K-gent memory summaries

    # Extension point
    CUSTOM = "custom"


# =============================================================================
# ProxyHandle
# =============================================================================


@dataclass
class ProxyHandle(Generic[T]):
    """
    A proxy handle is a representation of computed data.

    It is NOT the source. It is a lens on the source.
    It has its own lifecycle, independent of what it represents.

    Laws:
        1. Explicit Computation: Handles are ONLY created via store.compute()
        2. Provenance Preservation: Every handle knows its origin
        3. Event Transparency: Every state transition emits events
        4. No Anonymous Debris: human_label is required
        5. Idempotent Computation: Concurrent compute() awaits same work

    Example:
        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=analyze_corpus,
            human_label="Spec corpus analysis",
            ttl=timedelta(minutes=5),
        )

        if handle.is_fresh():
            use(handle.data)
        else:
            # Stale or error - agent can decide what to do
            await store.compute(...)  # Refresh
    """

    # Identity
    handle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType = SourceType.CUSTOM
    human_label: str = ""  # Required at creation time (Law 4)

    # Lifecycle
    status: HandleStatus = HandleStatus.EMPTY
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    source_hash: str | None = None  # Hash of source at computation time

    # Data
    data: T | None = None
    error: str | None = None

    # Provenance
    computed_by: str = "system"
    computation_duration: float = 0.0  # Seconds
    computation_count: int = 0  # How many times refreshed

    # Access tracking
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.human_label:
            raise ValueError("human_label is required (no anonymous debris)")
        if self.expires_at is None and self.status != HandleStatus.EMPTY:
            self.expires_at = self.created_at + self.ttl

    def is_fresh(self) -> bool:
        """Check if handle has valid, non-expired data."""
        if self.status != HandleStatus.FRESH:
            return False
        if self.expires_at is None:
            return True  # No expiration
        return datetime.now() < self.expires_at

    def is_stale(self) -> bool:
        """Check if handle has expired or been invalidated."""
        if self.status == HandleStatus.STALE:
            return True
        if self.status == HandleStatus.FRESH and self.expires_at:
            return datetime.now() >= self.expires_at
        return False

    def is_computing(self) -> bool:
        """Check if computation is in progress."""
        return self.status == HandleStatus.COMPUTING

    def is_error(self) -> bool:
        """Check if last computation failed."""
        return self.status == HandleStatus.ERROR

    def access(self) -> None:
        """Record an access (updates last_accessed and access_count)."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    @property
    def age(self) -> timedelta:
        """How old this handle is."""
        return datetime.now() - self.created_at

    @property
    def time_until_expiration(self) -> timedelta | None:
        """Time remaining until expiration, or None if no expiration."""
        if self.expires_at is None:
            return None
        return self.expires_at - datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "handle_id": self.handle_id,
            "source_type": self.source_type.value,
            "human_label": self.human_label,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "ttl_seconds": self.ttl.total_seconds(),
            "source_hash": self.source_hash,
            "data": self.data,  # Note: May need custom serialization
            "error": self.error,
            "computed_by": self.computed_by,
            "computation_duration": self.computation_duration,
            "computation_count": self.computation_count,
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProxyHandle[Any]":
        """Create from dictionary."""
        return cls(
            handle_id=data["handle_id"],
            source_type=SourceType(data["source_type"]),
            human_label=data["human_label"],
            status=HandleStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            ttl=timedelta(seconds=data.get("ttl_seconds", 300)),
            source_hash=data.get("source_hash"),
            data=data.get("data"),
            error=data.get("error"),
            computed_by=data.get("computed_by", "system"),
            computation_duration=data.get("computation_duration", 0.0),
            computation_count=data.get("computation_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"])
            if data.get("last_accessed")
            else datetime.now(),
            access_count=data.get("access_count", 0),
        )


# =============================================================================
# Events
# =============================================================================


ProxyHandleEventType = Literal[
    "computation_started",  # compute() called
    "computation_completed",  # compute() succeeded
    "computation_failed",  # compute() errored
    "handle_accessed",  # get() called
    "handle_stale",  # TTL expired or source changed
    "handle_invalidated",  # invalidate() called
    "handle_deleted",  # delete() called
]


@dataclass
class ProxyHandleEvent:
    """
    Events emitted during proxy handle lifecycle.

    Law 3: Every state transition emits exactly one event.
    These events are published to WitnessSynergyBus for transparency.
    """

    event_type: ProxyHandleEventType
    source_type: SourceType
    handle_id: str | None
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for bus publication."""
        return {
            "event_type": self.event_type,
            "source_type": self.source_type.value,
            "handle_id": self.handle_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "HandleStatus",
    "SourceType",
    # Core type
    "ProxyHandle",
    # Events
    "ProxyHandleEvent",
    "ProxyHandleEventType",
]
