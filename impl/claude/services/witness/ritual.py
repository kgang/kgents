"""
Ritual: Lawful Workflow Orchestration.

A Ritual is a curator-orchestrated workflow that:
- Requires a Covenant (permission contract)
- Requires an Offering (resource contract)
- Follows N-Phase directed cycle
- Emits TraceNodes for all actions

Every Ritual has a Covenant and an Offering. This makes workflows
explicit, auditable, and resource-aware.

Philosophy:
    "A Ritual is ceremony with purpose. It requires permission
    (Covenant) and resources (Offering). It follows a directed
    cycle (N-Phase). Every action is traced."

Laws:
- Law 1 (Covenant Required): Every Ritual has exactly one Covenant
- Law 2 (Offering Required): Every Ritual has exactly one Offering
- Law 3 (Guard Transparency): Guards emit TraceNodes on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle

See: spec/protocols/warp-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 9: Directed Cycle)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

from .covenant import Covenant, CovenantId, CovenantStatus
from .offering import Budget, Offering, OfferingId
from .trace_node import NPhase, TraceNode, TraceNodeId, WalkId

logger = logging.getLogger("kgents.witness.ritual")

# =============================================================================
# Type Aliases
# =============================================================================

RitualId = NewType("RitualId", str)


def generate_ritual_id() -> RitualId:
    """Generate a unique Ritual ID."""
    return RitualId(f"ritual-{uuid4().hex[:12]}")


# =============================================================================
# Ritual Status
# =============================================================================


class RitualStatus(Enum):
    """
    Status of a Ritual.

    Lifecycle:
        PENDING → ACTIVE → COMPLETE
                       ↘ FAILED
                       ↘ CANCELLED
    """

    PENDING = auto()  # Awaiting start
    ACTIVE = auto()  # Currently executing
    PAUSED = auto()  # Temporarily paused
    COMPLETE = auto()  # Successfully finished
    FAILED = auto()  # Failed with error
    CANCELLED = auto()  # Cancelled by user


# =============================================================================
# Phase Transitions (Law 4)
# =============================================================================

# Valid 3-phase transitions
_THREE_PHASE_TRANSITIONS: dict[NPhase, set[NPhase]] = {
    NPhase.SENSE: {NPhase.ACT},
    NPhase.ACT: {NPhase.REFLECT},
    NPhase.REFLECT: {NPhase.SENSE},  # Cycle back
}


# =============================================================================
# Sentinel Guard
# =============================================================================


class GuardResult(Enum):
    """Result of a guard check."""

    PASS = auto()  # Guard passed
    FAIL = auto()  # Guard failed
    WARN = auto()  # Warning (proceed with caution)


@dataclass(frozen=True)
class SentinelGuard:
    """
    A check that must pass at phase boundaries.

    Law 3: Guards emit TraceNodes on evaluation.

    Guards can check:
    - Resource budget remaining
    - Time constraints
    - Quality metrics
    - External conditions
    """

    id: str
    name: str
    description: str = ""
    check_type: str = "budget"  # "budget", "time", "quality", "custom"
    condition: str = ""  # Expression or identifier for the check
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "check_type": self.check_type,
            "condition": self.condition,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SentinelGuard:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            check_type=data.get("check_type", "budget"),
            condition=data.get("condition", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class GuardEvaluation:
    """
    Result of evaluating a guard.

    Law 3: Guards emit TraceNodes - this is the TraceNode content.
    """

    guard: SentinelGuard
    result: GuardResult
    message: str = ""
    evaluated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "guard_id": self.guard.id,
            "guard_name": self.guard.name,
            "result": self.result.name,
            "message": self.message,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


# =============================================================================
# Ritual Phase
# =============================================================================


@dataclass(frozen=True)
class RitualPhase:
    """
    Single phase in a Ritual state machine.

    Each phase has:
    - Entry guards (must pass to enter)
    - Exit guards (must pass to leave)
    - Allowed actions (what can be done in this phase)
    - Optional timeout
    """

    name: str
    n_phase: NPhase
    entry_guards: tuple[SentinelGuard, ...] = ()
    exit_guards: tuple[SentinelGuard, ...] = ()
    allowed_actions: tuple[str, ...] = ()
    timeout_seconds: float | None = None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "n_phase": self.n_phase.value,
            "entry_guards": [g.to_dict() for g in self.entry_guards],
            "exit_guards": [g.to_dict() for g in self.exit_guards],
            "allowed_actions": list(self.allowed_actions),
            "timeout_seconds": self.timeout_seconds,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RitualPhase:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            n_phase=NPhase(data["n_phase"]),
            entry_guards=tuple(SentinelGuard.from_dict(g) for g in data.get("entry_guards", [])),
            exit_guards=tuple(SentinelGuard.from_dict(g) for g in data.get("exit_guards", [])),
            allowed_actions=tuple(data.get("allowed_actions", [])),
            timeout_seconds=data.get("timeout_seconds"),
            description=data.get("description", ""),
        )


# =============================================================================
# Exceptions
# =============================================================================


class RitualError(Exception):
    """Base exception for Ritual errors."""

    pass


class RitualNotActive(RitualError):
    """Ritual is not in ACTIVE status."""

    pass


class InvalidPhaseTransition(RitualError):
    """Law 4: Invalid phase transition attempted."""

    pass


class GuardFailed(RitualError):
    """Law 3: A guard check failed."""

    def __init__(self, evaluation: GuardEvaluation, message: str = ""):
        self.evaluation = evaluation
        super().__init__(message or f"Guard {evaluation.guard.name} failed: {evaluation.message}")


class MissingCovenant(RitualError):
    """Law 1: Ritual requires a Covenant."""

    pass


class MissingOffering(RitualError):
    """Law 2: Ritual requires an Offering."""

    pass


# =============================================================================
# Ritual: The Core Primitive
# =============================================================================


@dataclass
class Ritual:
    """
    Curator-orchestrated workflow with explicit gates.

    Laws:
    - Law 1 (Covenant Required): Every Ritual has exactly one Covenant
    - Law 2 (Offering Required): Every Ritual has exactly one Offering
    - Law 3 (Guard Transparency): Guards emit TraceNodes
    - Law 4 (Phase Ordering): Transitions follow N-Phase directed cycle

    A Ritual defines a workflow with:
    - Covenant: What operations are permitted
    - Offering: What resources can be consumed
    - Phases: State machine following N-Phase cycle
    - Guards: Checks at phase boundaries

    Example:
        >>> ritual = Ritual.create(
        ...     name="Implement Feature",
        ...     covenant=covenant,
        ...     offering=offering,
        ... )
        >>> ritual.begin()
        >>> ritual.advance_phase(NPhase.ACT)
        >>> ritual.complete()
    """

    # Identity
    id: RitualId = field(default_factory=generate_ritual_id)
    name: str = ""

    # Law 1: Covenant Required
    covenant_id: CovenantId | None = None
    _covenant: Covenant | None = field(default=None, repr=False)

    # Law 2: Offering Required
    offering_id: OfferingId | None = None
    _offering: Offering | None = field(default=None, repr=False)

    # Phase management (Law 4)
    phases: list[RitualPhase] = field(default_factory=list)
    current_phase: NPhase = NPhase.SENSE
    phase_history: list[tuple[NPhase, datetime]] = field(default_factory=list)

    # Guards
    entry_guards: list[SentinelGuard] = field(default_factory=list)
    guard_evaluations: list[GuardEvaluation] = field(default_factory=list)

    # Status
    status: RitualStatus = RitualStatus.PENDING

    # Walk binding
    walk_id: WalkId | None = None

    # Trace history (Law 3)
    trace_node_ids: list[TraceNodeId] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    ended_at: datetime | None = None

    # Metadata
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        name: str,
        covenant: Covenant,
        offering: Offering,
        phases: list[RitualPhase] | None = None,
        description: str = "",
    ) -> Ritual:
        """
        Create a new Ritual with Covenant and Offering.

        Law 1: Covenant is required.
        Law 2: Offering is required.
        """
        # Law 1: Verify Covenant is granted
        if covenant.status != CovenantStatus.GRANTED:
            raise MissingCovenant(f"Covenant must be granted (status: {covenant.status.name})")

        # Law 2: Verify Offering is valid
        if not offering.is_valid():
            raise MissingOffering("Offering must be valid (not expired or exhausted)")

        # Default phases if not provided
        if phases is None:
            phases = [
                RitualPhase(name="Sense", n_phase=NPhase.SENSE),
                RitualPhase(name="Act", n_phase=NPhase.ACT),
                RitualPhase(name="Reflect", n_phase=NPhase.REFLECT),
            ]

        return cls(
            name=name,
            covenant_id=covenant.id,
            _covenant=covenant,
            offering_id=offering.id,
            _offering=offering,
            phases=phases,
            description=description,
        )

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def begin(self) -> None:
        """
        Begin the Ritual.

        Transitions from PENDING to ACTIVE, entering first phase.
        """
        if self.status != RitualStatus.PENDING:
            raise RitualError(f"Cannot begin Ritual in status {self.status.name}")

        # Verify requirements
        self._check_requirements()

        self.status = RitualStatus.ACTIVE
        self.started_at = datetime.now()
        self.phase_history.append((self.current_phase, datetime.now()))

        logger.info(f"Ritual {self.id} begun in phase {self.current_phase.value}")

    def complete(self) -> None:
        """Mark Ritual as successfully complete."""
        if self.status != RitualStatus.ACTIVE:
            raise RitualNotActive(f"Cannot complete Ritual in status {self.status.name}")

        self.status = RitualStatus.COMPLETE
        self.ended_at = datetime.now()

        logger.info(f"Ritual {self.id} completed with {len(self.trace_node_ids)} traces")

    def fail(self, reason: str = "") -> None:
        """Mark Ritual as failed."""
        if self.status not in {RitualStatus.ACTIVE, RitualStatus.PAUSED}:
            raise RitualError(f"Cannot fail Ritual in status {self.status.name}")

        self.status = RitualStatus.FAILED
        self.ended_at = datetime.now()
        if reason:
            self.metadata["failure_reason"] = reason

        logger.warning(f"Ritual {self.id} failed: {reason}")

    def cancel(self, reason: str = "") -> None:
        """Cancel the Ritual."""
        if self.status in {RitualStatus.COMPLETE, RitualStatus.FAILED, RitualStatus.CANCELLED}:
            raise RitualError(f"Cannot cancel Ritual in status {self.status.name}")

        self.status = RitualStatus.CANCELLED
        self.ended_at = datetime.now()
        if reason:
            self.metadata["cancel_reason"] = reason

        logger.info(f"Ritual {self.id} cancelled: {reason}")

    def pause(self) -> None:
        """Pause the Ritual."""
        if self.status != RitualStatus.ACTIVE:
            raise RitualNotActive(f"Cannot pause Ritual in status {self.status.name}")

        self.status = RitualStatus.PAUSED
        logger.info(f"Ritual {self.id} paused")

    def resume(self) -> None:
        """Resume a paused Ritual."""
        if self.status != RitualStatus.PAUSED:
            raise RitualError(f"Cannot resume Ritual in status {self.status.name}")

        self.status = RitualStatus.ACTIVE
        logger.info(f"Ritual {self.id} resumed")

    # =========================================================================
    # Phase Management (Law 4)
    # =========================================================================

    def can_transition(self, to_phase: NPhase) -> bool:
        """
        Check if transition to phase is valid.

        Law 4: Phase transitions follow directed cycle.
        """
        if to_phase == self.current_phase:
            return True  # Same phase is no-op

        valid_targets = _THREE_PHASE_TRANSITIONS.get(self.current_phase, set())
        return to_phase in valid_targets

    def advance_phase(self, to_phase: NPhase) -> bool:
        """
        Advance to a new phase.

        Law 4: Transitions follow N-Phase directed cycle.

        Returns True if transition succeeded.
        """
        if self.status != RitualStatus.ACTIVE:
            raise RitualNotActive(f"Cannot advance phase in status {self.status.name}")

        if not self.can_transition(to_phase):
            logger.warning(
                f"Invalid phase transition: {self.current_phase.value} → {to_phase.value}"
            )
            return False

        # Check exit guards for current phase
        current_ritual_phase = self._get_ritual_phase(self.current_phase)
        if current_ritual_phase:
            for guard in current_ritual_phase.exit_guards:
                evaluation = self._evaluate_guard(guard)
                if evaluation.result == GuardResult.FAIL:
                    raise GuardFailed(evaluation)

        # Check entry guards for new phase
        new_ritual_phase = self._get_ritual_phase(to_phase)
        if new_ritual_phase:
            for guard in new_ritual_phase.entry_guards:
                evaluation = self._evaluate_guard(guard)
                if evaluation.result == GuardResult.FAIL:
                    raise GuardFailed(evaluation)

        old_phase = self.current_phase
        self.current_phase = to_phase
        self.phase_history.append((to_phase, datetime.now()))

        logger.info(f"Ritual {self.id}: {old_phase.value} → {to_phase.value}")
        return True

    def _get_ritual_phase(self, n_phase: NPhase) -> RitualPhase | None:
        """Get the RitualPhase for an NPhase."""
        for phase in self.phases:
            if phase.n_phase == n_phase:
                return phase
        return None

    # =========================================================================
    # Guards (Law 3)
    # =========================================================================

    def _evaluate_guard(self, guard: SentinelGuard) -> GuardEvaluation:
        """
        Evaluate a guard.

        Law 3: Guards emit TraceNodes on evaluation.
        """
        # Basic guard evaluation (can be extended with custom checks)
        result = GuardResult.PASS
        message = f"Guard {guard.name} passed"

        if guard.check_type == "budget" and self._offering:
            if self._offering.budget.is_exhausted:
                result = GuardResult.FAIL
                message = "Budget exhausted"
        elif guard.check_type == "time":
            if self.started_at and guard.condition:
                elapsed = (datetime.now() - self.started_at).total_seconds()
                try:
                    max_time = float(guard.condition)
                    if elapsed > max_time:
                        result = GuardResult.FAIL
                        message = f"Time limit exceeded: {elapsed:.0f}s > {max_time:.0f}s"
                except ValueError:
                    pass

        evaluation = GuardEvaluation(
            guard=guard,
            result=result,
            message=message,
        )

        self.guard_evaluations.append(evaluation)
        return evaluation

    def add_guard(self, guard: SentinelGuard) -> None:
        """Add an entry guard to the Ritual."""
        self.entry_guards.append(guard)

    # =========================================================================
    # Trace Recording (Law 3)
    # =========================================================================

    def record_trace(self, trace: TraceNode) -> None:
        """Record a TraceNode emitted during this Ritual."""
        if trace.id not in self.trace_node_ids:
            self.trace_node_ids.append(trace.id)

    @property
    def trace_count(self) -> int:
        """Number of traces recorded."""
        return len(self.trace_node_ids)

    # =========================================================================
    # Requirements Check
    # =========================================================================

    def _check_requirements(self) -> None:
        """Check Law 1 and Law 2 requirements."""
        # Law 1: Covenant required
        if self._covenant is None:
            raise MissingCovenant("Ritual requires a Covenant")
        if not self._covenant.is_active:
            raise MissingCovenant(f"Covenant is not active (status: {self._covenant.status.name})")

        # Law 2: Offering required
        if self._offering is None:
            raise MissingOffering("Ritual requires an Offering")
        if not self._offering.is_valid():
            raise MissingOffering("Offering is not valid")

    @property
    def covenant(self) -> Covenant | None:
        """Get the associated Covenant."""
        return self._covenant

    @property
    def offering(self) -> Offering | None:
        """Get the associated Offering."""
        return self._offering

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_active(self) -> bool:
        """Check if Ritual is active."""
        return self.status == RitualStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        """Check if Ritual is complete."""
        return self.status == RitualStatus.COMPLETE

    @property
    def duration_seconds(self) -> float | None:
        """Duration of the Ritual in seconds."""
        if self.started_at is None:
            return None
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "covenant_id": str(self.covenant_id) if self.covenant_id else None,
            "offering_id": str(self.offering_id) if self.offering_id else None,
            "phases": [p.to_dict() for p in self.phases],
            "current_phase": self.current_phase.value,
            "phase_history": [(p.value, ts.isoformat()) for p, ts in self.phase_history],
            "entry_guards": [g.to_dict() for g in self.entry_guards],
            "guard_evaluations": [e.to_dict() for e in self.guard_evaluations],
            "status": self.status.name,
            "walk_id": str(self.walk_id) if self.walk_id else None,
            "trace_node_ids": [str(tid) for tid in self.trace_node_ids],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ritual:
        """Create from dictionary (without Covenant/Offering - must be reattached)."""
        phase_history = [
            (NPhase(p), datetime.fromisoformat(ts)) for p, ts in data.get("phase_history", [])
        ]

        return cls(
            id=RitualId(data["id"]),
            name=data.get("name", ""),
            covenant_id=CovenantId(data["covenant_id"]) if data.get("covenant_id") else None,
            offering_id=OfferingId(data["offering_id"]) if data.get("offering_id") else None,
            phases=[RitualPhase.from_dict(p) for p in data.get("phases", [])],
            current_phase=NPhase(data.get("current_phase", "SENSE")),
            phase_history=phase_history,
            entry_guards=[SentinelGuard.from_dict(g) for g in data.get("entry_guards", [])],
            guard_evaluations=[],  # Not restored (ephemeral)
            status=RitualStatus[data.get("status", "PENDING")],
            walk_id=WalkId(data["walk_id"]) if data.get("walk_id") else None,
            trace_node_ids=[TraceNodeId(tid) for tid in data.get("trace_node_ids", [])],
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else None,
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"Ritual(id={str(self.id)[:16]}..., "
            f"name='{self.name}', "
            f"phase={self.current_phase.value}, "
            f"status={self.status.name})"
        )


# =============================================================================
# RitualStore
# =============================================================================


@dataclass
class RitualStore:
    """Persistent storage for Rituals."""

    _rituals: dict[RitualId, Ritual] = field(default_factory=dict)

    def add(self, ritual: Ritual) -> None:
        """Add a Ritual to the store."""
        self._rituals[ritual.id] = ritual

    def get(self, ritual_id: RitualId) -> Ritual | None:
        """Get a Ritual by ID."""
        return self._rituals.get(ritual_id)

    def active(self) -> list[Ritual]:
        """Get all active Rituals."""
        return [r for r in self._rituals.values() if r.is_active]

    def recent(self, limit: int = 10) -> list[Ritual]:
        """Get most recent Rituals."""
        sorted_rituals = sorted(
            self._rituals.values(),
            key=lambda r: r.created_at,
            reverse=True,
        )
        return sorted_rituals[:limit]

    def __len__(self) -> int:
        return len(self._rituals)


# =============================================================================
# Global Store
# =============================================================================

_global_ritual_store: RitualStore | None = None


def get_ritual_store() -> RitualStore:
    """Get the global ritual store."""
    global _global_ritual_store
    if _global_ritual_store is None:
        _global_ritual_store = RitualStore()
    return _global_ritual_store


def reset_ritual_store() -> None:
    """Reset the global ritual store (for testing)."""
    global _global_ritual_store
    _global_ritual_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "RitualId",
    "generate_ritual_id",
    # Status
    "RitualStatus",
    # Guards
    "GuardResult",
    "SentinelGuard",
    "GuardEvaluation",
    # Phase
    "RitualPhase",
    # Exceptions
    "RitualError",
    "RitualNotActive",
    "InvalidPhaseTransition",
    "GuardFailed",
    "MissingCovenant",
    "MissingOffering",
    # Core
    "Ritual",
    # Store
    "RitualStore",
    "get_ritual_store",
    "reset_ritual_store",
]
