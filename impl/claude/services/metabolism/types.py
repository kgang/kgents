"""
Metabolism Types: Core data structures for the metabolic development cycle.

Checkpoint 0.3 of Metabolic Development Protocol.

This module defines the categorical foundation for Metabolism:
- SessionState: Polynomial positions (DORMANT → GREETING → HYDRATED → WORKING → COMPOSTING → REFLECTING)
- SessionEvent: Input events to the polynomial
- SessionOutput: Output from state transitions

The Metabolic Session models the complete developer day as a state machine:
    Greeting (Coffee) → Hydration → Work → Compost → Reflect → Rest

Teaching:
    gotcha: Metabolism subsumes Coffee — it doesn't replace it.
            Coffee is the GREETING phase; Metabolism is the container.
            (Evidence: test_metabolism_types.py::test_session_contains_coffee)

AGENTESE: time.metabolism.session
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# State Machine (Polynomial Positions)
# =============================================================================


class SessionState(Enum):
    """
    Positions in the Metabolic Session polynomial.

    The developer day flows:
    DORMANT → GREETING → HYDRATED → WORKING → COMPOSTING → REFLECTING → DORMANT

    Key insight: These states map to physiological rhythms:
    - GREETING: Liminal (sleep → wake)
    - HYDRATED: Ready (context loaded)
    - WORKING: Flow (deep work)
    - COMPOSTING: Integration (learnings captured)
    - REFLECTING: Closure (day reviewed)
    """

    DORMANT = auto()  # Not in session
    GREETING = auto()  # Morning Coffee active
    HYDRATED = auto()  # Context loaded, ready to work
    WORKING = auto()  # Active development session
    COMPOSTING = auto()  # Capturing learnings at session end
    REFLECTING = auto()  # Post-session reflection


# =============================================================================
# Session Metadata
# =============================================================================


class WorkMode(Enum):
    """How the developer is working."""

    DEEP = "deep"  # Focused single-task
    EXPLORATION = "exploration"  # Wandering, discovery
    MAINTENANCE = "maintenance"  # Fixing, updating
    COLLABORATION = "collaboration"  # Working with others


class EnergyLevel(Enum):
    """Developer energy/focus level."""

    HIGH = "high"  # Peak cognitive capacity
    MEDIUM = "medium"  # Normal working state
    LOW = "low"  # Need break or rest
    DEPLETED = "depleted"  # Should stop


@dataclass(frozen=True)
class SessionMetadata:
    """
    Metadata about the current session.

    Tracked for pattern learning and adaptive suggestions.
    """

    started_at: datetime
    work_mode: WorkMode | None = None
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    task_focus: str | None = None  # Current task from Coffee/Hydration
    voice_captured: bool = False  # Did we capture morning voice?
    stigmergy_active: bool = False  # Are we tracking patterns?

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "work_mode": self.work_mode.value if self.work_mode else None,
            "energy_level": self.energy_level.value,
            "task_focus": self.task_focus,
            "voice_captured": self.voice_captured,
            "stigmergy_active": self.stigmergy_active,
        }


# =============================================================================
# Events (Inputs to Polynomial)
# =============================================================================


@dataclass(frozen=True)
class SessionEvent:
    """
    Input event to the Session polynomial.

    Events drive state transitions in the metabolic cycle.
    """

    command: str  # "begin", "hydrate", "work", "compost", "reflect", "rest"
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Outputs (From Polynomial)
# =============================================================================


@dataclass(frozen=True)
class CompostEntry:
    """
    A learning captured during composting.

    These become gotchas in Living Docs if verified.
    """

    insight: str
    severity: str = "info"  # "critical", "warning", "info"
    task_context: str | None = None
    evidence: str | None = None  # Test or file reference

    def to_dict(self) -> dict[str, Any]:
        return {
            "insight": self.insight,
            "severity": self.severity,
            "task_context": self.task_context,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class SessionOutput:
    """
    Output from the Session polynomial.

    Wraps the result of a state transition.
    """

    status: str  # "ok", "skipped", "error"
    state: SessionState
    message: str = ""
    metadata: SessionMetadata | None = None
    compost: list[CompostEntry] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": self.status,
            "state": self.state.name,
            "message": self.message,
        }
        if self.metadata:
            result["metadata"] = self.metadata.to_dict()
        if self.compost:
            result["compost"] = [c.to_dict() for c in self.compost]
        if self.data:
            result["data"] = self.data
        return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State machine
    "SessionState",
    # Metadata
    "SessionMetadata",
    "WorkMode",
    "EnergyLevel",
    # Events and outputs
    "SessionEvent",
    "SessionOutput",
    "CompostEntry",
]
