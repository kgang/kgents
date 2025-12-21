"""
Walk: Durable Work Stream Tied to Forest Plans.

A Walk is a session-level abstraction that:
- Binds to a Forest plan file (root_plan)
- Tracks N-Phase workflow position
- Accumulates Marks over time
- Manages participant Umwelts

The Insight (from spec/protocols/warp-primitives.md):
    "Every action is a Mark. Every session is a Walk. Every workflow is a Playbook."

Laws:
- Law 1 (Monotonicity): marks only grows, never shrinks
- Law 2 (Phase Coherence): phase transitions follow N-Phase grammar
- Law 3 (Plan Binding): root_plan must exist in Forest

Philosophy:
    A Walk is like a GardenerSession (70% leverage) but with:
    - Explicit Forest binding (plans/*.md)
    - Mark history instead of Gesture history
    - Participant Umwelts for multi-agent collaboration

See: spec/protocols/warp-primitives.md
See: impl/claude/protocols/gardener_logos/garden.py (GardenState pattern)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any
from uuid import uuid4

from .mark import (
    Mark,
    MarkId,
    NPhase,
    PlanPath,
    UmweltSnapshot,
    WalkId,
)

logger = logging.getLogger("kgents.witness.walk")


# =============================================================================
# Phase Transition Grammar (Law 2)
# =============================================================================

# Valid phase transitions (based on N-Phase grammar)
_VALID_PHASE_TRANSITIONS: dict[NPhase, set[NPhase]] = {
    # 3-phase (compressed)
    NPhase.SENSE: {NPhase.ACT},
    NPhase.ACT: {NPhase.REFLECT},
    NPhase.REFLECT: {NPhase.SENSE},  # Cycle back
    # 11-phase transitions (within families and between)
    NPhase.PLAN: {NPhase.RESEARCH, NPhase.DEVELOP},
    NPhase.RESEARCH: {NPhase.DEVELOP, NPhase.PLAN},
    NPhase.DEVELOP: {NPhase.STRATEGIZE, NPhase.RESEARCH},
    NPhase.STRATEGIZE: {NPhase.CROSS_SYNERGIZE, NPhase.DEVELOP},
    NPhase.CROSS_SYNERGIZE: {NPhase.IMPLEMENT, NPhase.STRATEGIZE},
    NPhase.IMPLEMENT: {NPhase.QA, NPhase.CROSS_SYNERGIZE},
    NPhase.QA: {NPhase.TEST, NPhase.IMPLEMENT},
    NPhase.TEST: {NPhase.EDUCATE, NPhase.QA},
    NPhase.EDUCATE: {NPhase.MEASURE, NPhase.TEST},
    NPhase.MEASURE: {NPhase.REFLECT, NPhase.EDUCATE},
    # REFLECT can loop back to PLAN or SENSE
}


# =============================================================================
# Walk Status
# =============================================================================


class WalkStatus(Enum):
    """
    Status of a Walk.

    Transitions:
        ACTIVE → PAUSED → ACTIVE (resumable)
        ACTIVE → COMPLETE (successful end)
        ACTIVE → ABANDONED (unsuccessful end)
        PAUSED → ABANDONED (give up while paused)
    """

    ACTIVE = auto()  # Currently in progress
    PAUSED = auto()  # Temporarily suspended (can resume)
    COMPLETE = auto()  # Successfully finished
    ABANDONED = auto()  # Gave up / failed


# =============================================================================
# Participant
# =============================================================================


@dataclass(frozen=True)
class Participant:
    """
    A participant in a Walk (human or agent).

    Participants have:
    - Identity (id, name)
    - Role (observer, contributor, orchestrator)
    - Umwelt (what they can see and do)
    - Join time
    """

    id: str
    name: str
    role: str = "contributor"  # observer, contributor, orchestrator
    umwelt: UmweltSnapshot = field(default_factory=UmweltSnapshot.system)
    joined_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def human(cls, name: str, role: str = "orchestrator") -> Participant:
        """Create a human participant."""
        return cls(
            id=f"human-{uuid4().hex[:8]}",
            name=name,
            role=role,
            umwelt=UmweltSnapshot(
                observer_id=name,
                role="human",
                capabilities=frozenset({"read", "write", "approve", "orchestrate"}),
                perceptions=frozenset({"all"}),
                trust_level=3,  # Humans have full trust
            ),
        )

    @classmethod
    def agent(cls, name: str, trust_level: int = 0, role: str = "contributor") -> Participant:
        """Create an agent participant."""
        return cls(
            id=f"agent-{name}-{uuid4().hex[:8]}",
            name=name,
            role=role,
            umwelt=UmweltSnapshot.witness(trust_level),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "umwelt": self.umwelt.to_dict(),
            "joined_at": self.joined_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Participant:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            role=data.get("role", "contributor"),
            umwelt=UmweltSnapshot.from_dict(data.get("umwelt", {})),
            joined_at=datetime.fromisoformat(data["joined_at"])
            if data.get("joined_at")
            else datetime.now(),
        )


# =============================================================================
# Walk Intent
# =============================================================================


@dataclass(frozen=True)
class WalkIntent:
    """
    The goal of a Walk.

    Maps to IntentTree's Intent concept, but simplified for Walk-level goals.
    """

    id: str
    description: str
    type: str = "implement"  # explore, design, implement, refine, verify
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, description: str, intent_type: str = "implement") -> WalkIntent:
        """Create a new intent."""
        return cls(
            id=f"intent-{uuid4().hex[:8]}",
            description=description,
            type=intent_type,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WalkIntent:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            description=data["description"],
            type=data.get("type", "implement"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
        )


# =============================================================================
# Walk: The Durable Work Stream
# =============================================================================


@dataclass
class Walk:
    """
    Durable work stream tied to Forest plans.

    Laws:
    - Law 1 (Monotonicity): marks only grows
    - Law 2 (Phase Coherence): phase transitions follow N-Phase grammar
    - Law 3 (Plan Binding): root_plan must exist in Forest

    A Walk is similar to GardenState/GardenerSession but with:
    - Explicit Forest binding via root_plan
    - Mark history for complete audit trail
    - Multi-participant support with Umwelts

    Example:
        >>> walk = Walk.create(
        ...     goal="Implement Mark primitive",
        ...     root_plan=PlanPath("plans/warp-servo-phase1.md"),
        ... )
        >>> walk.advance(mark)
        >>> walk.transition_phase(NPhase.ACT)
    """

    # Identity
    id: WalkId
    name: str = ""

    # Goal
    goal: WalkIntent | None = None

    # Forest binding (Law 3)
    root_plan: PlanPath | None = None

    # Mark history (Law 1: only grows)
    mark_ids: list[MarkId] = field(default_factory=list)

    # Participants (agents + humans with their Umwelts)
    participants: list[Participant] = field(default_factory=list)

    # N-Phase tracking (Law 2)
    phase: NPhase = NPhase.SENSE
    phase_history: list[tuple[NPhase, datetime]] = field(default_factory=list)

    # Status
    status: WalkStatus = WalkStatus.ACTIVE

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    last_active: datetime = field(default_factory=datetime.now)

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize phase history if empty."""
        if not self.phase_history:
            self.phase_history = [(self.phase, self.started_at)]

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        goal: str | WalkIntent,
        root_plan: PlanPath | str | None = None,
        name: str = "",
        initial_phase: NPhase = NPhase.SENSE,
    ) -> Walk:
        """
        Create a new Walk.

        Args:
            goal: The goal description or WalkIntent
            root_plan: Path to the Forest plan file (optional)
            name: Human-readable name for the walk
            initial_phase: Starting N-Phase (default: SENSE)

        Returns:
            New Walk instance ready for use
        """
        walk_id = WalkId(f"walk-{uuid4().hex[:12]}")

        if isinstance(goal, str):
            goal_intent = WalkIntent.create(goal)
        else:
            goal_intent = goal

        plan_path = PlanPath(root_plan) if isinstance(root_plan, str) else root_plan

        # Generate name if not provided
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            name = f"Walk-{timestamp}"

        return cls(
            id=walk_id,
            name=name,
            goal=goal_intent,
            root_plan=plan_path,
            phase=initial_phase,
        )

    # =========================================================================
    # Mark Management (Law 1: Monotonicity)
    # =========================================================================

    def advance(self, mark: Mark) -> None:
        """
        Add a Mark to this Walk.

        Law 1: marks only grows, never shrinks.

        Updates:
        - mark_ids (append only)
        - last_active timestamp
        """
        if mark.id in self.mark_ids:
            logger.warning(f"Mark {mark.id} already in Walk {self.id}")
            return

        self.mark_ids.append(mark.id)
        self.last_active = datetime.now()

        logger.debug(f"Walk {self.id} advanced with trace {mark.id}")

    def trace_count(self) -> int:
        """Get the number of traces in this Walk."""
        return len(self.mark_ids)

    @property
    def mark_count(self) -> int:
        """Backwards compat: alias for trace_count()."""
        return self.trace_count()

    # =========================================================================
    # Phase Management (Law 2: Phase Coherence)
    # =========================================================================

    def can_transition(self, to_phase: NPhase) -> bool:
        """
        Check if transition to the given phase is valid.

        Law 2: Phase transitions follow N-Phase grammar.
        """
        # Same phase is always allowed (no-op)
        if to_phase == self.phase:
            return True

        # Check valid transitions
        valid_targets = _VALID_PHASE_TRANSITIONS.get(self.phase, set())

        # Allow transitions within same family
        if self.phase.family == to_phase.family:
            return True

        return to_phase in valid_targets

    def transition_phase(self, to_phase: NPhase, force: bool = False) -> bool:
        """
        Transition to a new N-Phase.

        Law 2: Phase transitions follow N-Phase grammar.

        Args:
            to_phase: The phase to transition to
            force: If True, skip validation (use with caution)

        Returns:
            True if transition succeeded, False otherwise
        """
        if not force and not self.can_transition(to_phase):
            logger.warning(
                f"Invalid phase transition: {self.phase.value} → {to_phase.value} in Walk {self.id}"
            )
            return False

        old_phase = self.phase
        self.phase = to_phase
        self.phase_history.append((to_phase, datetime.now()))
        self.last_active = datetime.now()

        logger.info(f"Walk {self.id} transitioned: {old_phase.value} → {to_phase.value}")
        return True

    def get_phase_duration(self, phase: NPhase) -> float:
        """Get total time spent in a phase (in seconds)."""
        total = 0.0
        current_phase = None
        phase_start = None

        for p, ts in self.phase_history:
            if current_phase == phase and phase_start:
                total += (ts - phase_start).total_seconds()
            current_phase = p
            phase_start = ts

        # Add time in current phase if it matches
        if current_phase == phase and phase_start:
            total += (datetime.now() - phase_start).total_seconds()

        return total

    # =========================================================================
    # Participant Management
    # =========================================================================

    def add_participant(self, participant: Participant) -> None:
        """Add a participant to this Walk."""
        # Check for duplicate
        if any(p.id == participant.id for p in self.participants):
            logger.warning(f"Participant {participant.id} already in Walk {self.id}")
            return

        self.participants.append(participant)
        logger.info(f"Added participant {participant.name} to Walk {self.id}")

    def get_participant(self, participant_id: str) -> Participant | None:
        """Get a participant by ID."""
        for p in self.participants:
            if p.id == participant_id:
                return p
        return None

    # =========================================================================
    # Status Management
    # =========================================================================

    def pause(self) -> None:
        """Pause this Walk."""
        if self.status != WalkStatus.ACTIVE:
            logger.warning(f"Cannot pause Walk {self.id} with status {self.status.name}")
            return

        self.status = WalkStatus.PAUSED
        self.last_active = datetime.now()
        logger.info(f"Walk {self.id} paused")

    def resume(self) -> None:
        """Resume a paused Walk."""
        if self.status != WalkStatus.PAUSED:
            logger.warning(f"Cannot resume Walk {self.id} with status {self.status.name}")
            return

        self.status = WalkStatus.ACTIVE
        self.last_active = datetime.now()
        logger.info(f"Walk {self.id} resumed")

    def complete(self) -> None:
        """Mark this Walk as complete."""
        if self.status not in {WalkStatus.ACTIVE, WalkStatus.PAUSED}:
            logger.warning(f"Cannot complete Walk {self.id} with status {self.status.name}")
            return

        self.status = WalkStatus.COMPLETE
        self.ended_at = datetime.now()
        logger.info(f"Walk {self.id} completed with {self.trace_count()} traces")

    def abandon(self, reason: str = "") -> None:
        """Abandon this Walk."""
        if self.status in {WalkStatus.COMPLETE, WalkStatus.ABANDONED}:
            logger.warning(f"Cannot abandon Walk {self.id} with status {self.status.name}")
            return

        self.status = WalkStatus.ABANDONED
        self.ended_at = datetime.now()
        if reason:
            self.metadata["abandon_reason"] = reason
        logger.info(f"Walk {self.id} abandoned: {reason}")

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "id": str(self.id),
            "name": self.name,
            "goal": self.goal.to_dict() if self.goal else None,
            "root_plan": str(self.root_plan) if self.root_plan else None,
            "mark_ids": [str(tid) for tid in self.mark_ids],
            "participants": [p.to_dict() for p in self.participants],
            "phase": self.phase.value,
            "phase_history": [(p.value, ts.isoformat()) for p, ts in self.phase_history],
            "status": self.status.name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "last_active": self.last_active.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Walk:
        """Create from dictionary."""
        phase_history = [
            (NPhase(p), datetime.fromisoformat(ts)) for p, ts in data.get("phase_history", [])
        ]

        return cls(
            id=WalkId(data["id"]),
            name=data.get("name", ""),
            goal=WalkIntent.from_dict(data["goal"]) if data.get("goal") else None,
            root_plan=PlanPath(data["root_plan"]) if data.get("root_plan") else None,
            mark_ids=[MarkId(tid) for tid in data.get("mark_ids", [])],
            participants=[Participant.from_dict(p) for p in data.get("participants", [])],
            phase=NPhase(data.get("phase", "SENSE")),
            phase_history=phase_history,
            status=WalkStatus[data.get("status", "ACTIVE")],
            started_at=datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else datetime.now(),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            last_active=datetime.fromisoformat(data["last_active"])
            if data.get("last_active")
            else datetime.now(),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def duration_seconds(self) -> float:
        """Total duration of the Walk in seconds."""
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def is_active(self) -> bool:
        """Check if the Walk is active."""
        return self.status == WalkStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        """Check if the Walk is complete."""
        return self.status == WalkStatus.COMPLETE

    def __repr__(self) -> str:
        """Concise representation."""
        goal_str = self.goal.description[:30] if self.goal else "no goal"
        return (
            f"Walk(id={str(self.id)[:8]}..., "
            f"phase={self.phase.value}, "
            f"traces={self.trace_count()}, "
            f"goal='{goal_str}...')"
        )


# =============================================================================
# WalkStore: Persistence for Walks
# =============================================================================


@dataclass
class WalkStore:
    """
    Persistent storage for Walks.

    Similar to MarkStore but for Walk-level abstractions.
    """

    _walks: dict[WalkId, Walk] = field(default_factory=dict)
    _persistence_path: Path | None = None

    def add(self, walk: Walk) -> None:
        """Add a Walk to the store."""
        self._walks[walk.id] = walk

    def get(self, walk_id: WalkId) -> Walk | None:
        """Get a Walk by ID."""
        return self._walks.get(walk_id)

    def active_walks(self) -> list[Walk]:
        """Get all active Walks."""
        return [w for w in self._walks.values() if w.is_active]

    def recent_walks(self, limit: int = 10) -> list[Walk]:
        """Get most recent Walks."""
        sorted_walks = sorted(self._walks.values(), key=lambda w: w.started_at, reverse=True)
        return sorted_walks[:limit]

    def save(self, path: Path | str) -> None:
        """Save to JSON file."""
        path = Path(path)
        data = {"version": 1, "walks": [w.to_dict() for w in self._walks.values()]}
        path.write_text(json.dumps(data, indent=2, default=str))
        self._persistence_path = path

    @classmethod
    def load(cls, path: Path | str) -> WalkStore:
        """Load from JSON file."""
        path = Path(path)
        data = json.loads(path.read_text())
        store = cls()
        store._persistence_path = path
        for walk_data in data.get("walks", []):
            walk = Walk.from_dict(walk_data)
            store._walks[walk.id] = walk
        return store

    def __len__(self) -> int:
        return len(self._walks)


# =============================================================================
# Global Store
# =============================================================================

_global_walk_store: WalkStore | None = None


def get_walk_store() -> WalkStore:
    """Get the global walk store."""
    global _global_walk_store
    if _global_walk_store is None:
        _global_walk_store = WalkStore()
    return _global_walk_store


def reset_walk_store() -> None:
    """Reset the global walk store (for testing)."""
    global _global_walk_store
    _global_walk_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Status
    "WalkStatus",
    # Participant
    "Participant",
    # Intent
    "WalkIntent",
    # Walk
    "Walk",
    # Store
    "WalkStore",
    "get_walk_store",
    "reset_walk_store",
]
