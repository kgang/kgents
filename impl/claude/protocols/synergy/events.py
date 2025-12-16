"""
Synergy Events: Cross-jewel communication event types.

Foundation 4 of the Enlightened Crown strategy.
When jewels complete operations, they emit events that other jewels can respond to.

Example:
    ✓ Gestalt analysis complete
    ↳ Synergy: Architecture snapshot captured to Brain
    ↳ Crystal: "gestalt-impl-claude-2025-12-16"
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SynergyEventType(Enum):
    """
    Known synergy event types.

    Each event type represents a significant jewel operation
    that other jewels might want to respond to.
    """

    # Gestalt events
    ANALYSIS_COMPLETE = "analysis_complete"
    HEALTH_COMPUTED = "health_computed"
    DRIFT_DETECTED = "drift_detected"

    # Brain events
    CRYSTAL_FORMED = "crystal_formed"
    MEMORY_SURFACED = "memory_surfaced"
    VAULT_IMPORTED = "vault_imported"

    # Gardener events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETE = "session_complete"
    ARTIFACT_CREATED = "artifact_created"
    LEARNING_RECORDED = "learning_recorded"

    # Atelier events
    PIECE_CREATED = "piece_created"
    BID_ACCEPTED = "bid_accepted"

    # Coalition events
    COALITION_FORMED = "coalition_formed"
    TASK_ASSIGNED = "task_assigned"


class Jewel(Enum):
    """Crown Jewel identifiers."""

    BRAIN = "brain"
    GESTALT = "gestalt"
    GARDENER = "gardener"
    ATELIER = "atelier"
    COALITION = "coalition"
    PARK = "park"
    DOMAIN = "domain"

    # Special: broadcast target
    ALL = "*"


@dataclass
class SynergyEvent:
    """
    Event payload for cross-jewel communication.

    Synergy events flow between jewels automatically:
    - Gestalt analysis → Brain captures architecture snapshot
    - Gardener session complete → Brain captures learnings
    - Atelier piece created → Brain captures creation metadata
    """

    source_jewel: Jewel
    target_jewel: Jewel
    event_type: SynergyEventType
    source_id: str  # ID of the source artifact (analysis ID, crystal ID, session ID)
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_jewel": self.source_jewel.value,
            "target_jewel": self.target_jewel.value,
            "event_type": self.event_type.value,
            "source_id": self.source_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynergyEvent":
        """Create from dictionary."""
        return cls(
            source_jewel=Jewel(data["source_jewel"]),
            target_jewel=Jewel(data["target_jewel"]),
            event_type=SynergyEventType(data["event_type"]),
            source_id=data["source_id"],
            payload=data.get("payload", {}),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if isinstance(data.get("timestamp"), str)
                else datetime.now()
            ),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
        )


@dataclass
class SynergyResult:
    """Result of handling a synergy event."""

    success: bool
    handler_name: str
    message: str = ""
    artifact_id: str | None = None  # ID of created artifact (e.g., crystal ID)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "handler_name": self.handler_name,
            "message": self.message,
            "artifact_id": self.artifact_id,
            "metadata": self.metadata,
        }


# Factory functions for common events


def create_analysis_complete_event(
    source_id: str,
    module_count: int,
    health_grade: str,
    average_health: float,
    drift_count: int,
    root_path: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gestalt analysis complete event."""
    return SynergyEvent(
        source_jewel=Jewel.GESTALT,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.ANALYSIS_COMPLETE,
        source_id=source_id,
        payload={
            "module_count": module_count,
            "health_grade": health_grade,
            "average_health": average_health,
            "drift_count": drift_count,
            "root_path": root_path,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_crystal_formed_event(
    crystal_id: str,
    content_preview: str,
    content_type: str = "text",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Brain crystal formed event."""
    return SynergyEvent(
        source_jewel=Jewel.BRAIN,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CRYSTAL_FORMED,
        source_id=crystal_id,
        payload={
            "content_preview": content_preview[:100],
            "content_type": content_type,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_session_complete_event(
    session_id: str,
    session_name: str,
    artifacts_count: int,
    learnings: list[str],
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gardener session complete event."""
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.SESSION_COMPLETE,
        source_id=session_id,
        payload={
            "session_name": session_name,
            "artifacts_count": artifacts_count,
            "learnings": learnings,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_artifact_created_event(
    artifact_id: str,
    artifact_type: str,
    path: str | None,
    description: str,
    session_id: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gardener artifact created event."""
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.ARTIFACT_CREATED,
        source_id=artifact_id,
        payload={
            "artifact_type": artifact_type,
            "path": path,
            "description": description,
            "session_id": session_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


__all__ = [
    # Event types
    "SynergyEventType",
    "Jewel",
    # Data classes
    "SynergyEvent",
    "SynergyResult",
    # Factory functions
    "create_analysis_complete_event",
    "create_crystal_formed_event",
    "create_session_complete_event",
    "create_artifact_created_event",
]
