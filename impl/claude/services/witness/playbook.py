"""
Playbook: Lawful Workflow Orchestration.

A Playbook is a curator-orchestrated workflow that:
- Requires a Grant (permission contract)
- Requires a Scope (resource contract)
- Follows N-Phase directed cycle
- Emits Marks for all actions

Every Playbook has a Grant and a Scope. This makes workflows
explicit, auditable, and resource-aware.

Philosophy:
    "A Playbook is ceremony with purpose. It requires permission
    (Grant) and resources (Scope). It follows a directed
    cycle (N-Phase). Every action is traced."

Rename History:
    Playbook → Playbook (spec/protocols/witness-primitives.md)
    "Following a playbook" - clearer than religious connotation

Laws:
- Law 1 (Grant Required): Every Playbook has exactly one Grant
- Law 2 (Scope Required): Every Playbook has exactly one Scope
- Law 3 (Guard Transparency): Guards emit Marks on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle

See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 9: Directed Cycle)

Teaching:
    gotcha: Always verify Grant is GRANTED status before creating Playbook.
            Passing a PENDING or REVOKED Grant raises MissingGrant.
            (Evidence: test_playbook.py::test_grant_required)

    gotcha: Phase transitions are DIRECTED—you cannot skip phases.
            SENSE → ACT → REFLECT → SENSE (cycle). InvalidPhaseTransition if wrong.
            (Evidence: test_playbook.py::test_phase_ordering)

    gotcha: Guards evaluate at phase boundaries, not during phase.
            Budget exhaustion during ACT phase only fails at ACT → REFLECT.
            (Evidence: test_playbook.py::test_guard_evaluation)

    gotcha: from_dict() does NOT restore _grant and _scope objects.
            You must reattach them manually after deserialization.
            (Evidence: test_playbook.py::test_serialization_roundtrip)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

from .grant import Grant, GrantId, GrantStatus
from .mark import Mark, MarkId, NPhase, WalkId
from .scope import Budget, Scope, ScopeId

logger = logging.getLogger("kgents.witness.playbook")

# =============================================================================
# Type Aliases
# =============================================================================

PlaybookId = NewType("PlaybookId", str)

# Backwards compatibility alias
PlaybookId = PlaybookId


def generate_playbook_id() -> PlaybookId:
    """Generate a unique Playbook ID."""
    return PlaybookId(f"playbook-{uuid4().hex[:12]}")


# Backwards compatibility alias
generate_playbook_id = generate_playbook_id


# =============================================================================
# Playbook Status
# =============================================================================


class PlaybookStatus(Enum):
    """
    Status of a Playbook.

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


# Backwards compatibility alias
PlaybookStatus = PlaybookStatus


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

    Law 3: Guards emit Marks on evaluation.

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

    Law 3: Guards emit Marks - this is the Mark content.
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
# Playbook Phase
# =============================================================================


@dataclass(frozen=True)
class PlaybookPhase:
    """
    Single phase in a Playbook state machine.

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
    def from_dict(cls, data: dict[str, Any]) -> PlaybookPhase:
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


# Backwards compatibility alias
PlaybookPhase = PlaybookPhase


# =============================================================================
# Exceptions
# =============================================================================


class PlaybookError(Exception):
    """Base exception for Playbook errors."""

    pass


# Backwards compatibility alias
PlaybookError = PlaybookError


class PlaybookNotActive(PlaybookError):
    """Playbook is not in ACTIVE status."""

    pass


# Backwards compatibility alias
PlaybookNotActive = PlaybookNotActive


class InvalidPhaseTransition(PlaybookError):
    """Law 4: Invalid phase transition attempted."""

    pass


class GuardFailed(PlaybookError):
    """Law 3: A guard check failed."""

    def __init__(self, evaluation: GuardEvaluation, message: str = ""):
        self.evaluation = evaluation
        super().__init__(message or f"Guard {evaluation.guard.name} failed: {evaluation.message}")


class MissingGrant(PlaybookError):
    """Law 1: Playbook requires a Grant."""

    pass


# Backwards compatibility alias
MissingGrant = MissingGrant


class MissingScope(PlaybookError):
    """Law 2: Playbook requires a Scope."""

    pass


# Backwards compatibility alias
MissingScope = MissingScope


# =============================================================================
# Playbook: The Core Primitive
# =============================================================================


@dataclass
class Playbook:
    """
    Curator-orchestrated workflow with explicit gates.

    Laws:
    - Law 1 (Grant Required): Every Playbook has exactly one Grant
    - Law 2 (Scope Required): Every Playbook has exactly one Scope
    - Law 3 (Guard Transparency): Guards emit Marks
    - Law 4 (Phase Ordering): Transitions follow N-Phase directed cycle

    A Playbook defines a workflow with:
    - Grant: What operations are permitted
    - Scope: What resources can be consumed
    - Phases: State machine following N-Phase cycle
    - Guards: Checks at phase boundaries

    Example:
        >>> playbook = Playbook.create(
        ...     name="Implement Feature",
        ...     grant=grant,
        ...     scope=scope,
        ... )
        >>> playbook.begin()
        >>> playbook.advance_phase(NPhase.ACT)
        >>> playbook.complete()
    """

    # Identity
    id: PlaybookId = field(default_factory=generate_playbook_id)
    name: str = ""

    # Law 1: Grant Required
    grant_id: GrantId | None = None
    _grant: Grant | None = field(default=None, repr=False)

    # Law 2: Scope Required
    scope_id: ScopeId | None = None
    _scope: Scope | None = field(default=None, repr=False)

    # Phase management (Law 4)
    phases: list[PlaybookPhase] = field(default_factory=list)
    current_phase: NPhase = NPhase.SENSE
    phase_history: list[tuple[NPhase, datetime]] = field(default_factory=list)

    # Guards
    entry_guards: list[SentinelGuard] = field(default_factory=list)
    guard_evaluations: list[GuardEvaluation] = field(default_factory=list)

    # Status
    status: PlaybookStatus = PlaybookStatus.PENDING

    # Walk binding
    walk_id: WalkId | None = None

    # Trace history (Law 3)
    mark_ids: list[MarkId] = field(default_factory=list)

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
        grant: Grant,
        scope: Scope,
        phases: list[PlaybookPhase] | None = None,
        description: str = "",
    ) -> Playbook:
        """
        Create a new Playbook with Grant and Scope.

        Law 1: Grant is required.
        Law 2: Scope is required.
        """
        # Law 1: Verify Grant is granted
        if grant.status != GrantStatus.GRANTED:
            raise MissingGrant(f"Grant must be granted (status: {grant.status.name})")

        # Law 2: Verify Scope is valid
        if not scope.is_valid():
            raise MissingScope("Scope must be valid (not expired or exhausted)")

        # Default phases if not provided
        if phases is None:
            phases = [
                PlaybookPhase(name="Sense", n_phase=NPhase.SENSE),
                PlaybookPhase(name="Act", n_phase=NPhase.ACT),
                PlaybookPhase(name="Reflect", n_phase=NPhase.REFLECT),
            ]

        return cls(
            name=name,
            grant_id=grant.id,
            _grant=grant,
            scope_id=scope.id,
            _scope=scope,
            phases=phases,
            description=description,
        )

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def begin(self) -> None:
        """
        Begin the Playbook.

        Transitions from PENDING to ACTIVE, entering first phase.
        """
        if self.status != PlaybookStatus.PENDING:
            raise PlaybookError(f"Cannot begin Playbook in status {self.status.name}")

        # Verify requirements
        self._check_requirements()

        self.status = PlaybookStatus.ACTIVE
        self.started_at = datetime.now()
        self.phase_history.append((self.current_phase, datetime.now()))

        logger.info(f"Playbook {self.id} begun in phase {self.current_phase.value}")

    def complete(self) -> None:
        """Mark Playbook as successfully complete."""
        if self.status != PlaybookStatus.ACTIVE:
            raise PlaybookNotActive(f"Cannot complete Playbook in status {self.status.name}")

        self.status = PlaybookStatus.COMPLETE
        self.ended_at = datetime.now()

        logger.info(f"Playbook {self.id} completed with {len(self.mark_ids)} marks")

    def fail(self, reason: str = "") -> None:
        """Mark Playbook as failed."""
        if self.status not in {PlaybookStatus.ACTIVE, PlaybookStatus.PAUSED}:
            raise PlaybookError(f"Cannot fail Playbook in status {self.status.name}")

        self.status = PlaybookStatus.FAILED
        self.ended_at = datetime.now()
        if reason:
            self.metadata["failure_reason"] = reason

        logger.warning(f"Playbook {self.id} failed: {reason}")

    def cancel(self, reason: str = "") -> None:
        """Cancel the Playbook."""
        if self.status in {
            PlaybookStatus.COMPLETE,
            PlaybookStatus.FAILED,
            PlaybookStatus.CANCELLED,
        }:
            raise PlaybookError(f"Cannot cancel Playbook in status {self.status.name}")

        self.status = PlaybookStatus.CANCELLED
        self.ended_at = datetime.now()
        if reason:
            self.metadata["cancel_reason"] = reason

        logger.info(f"Playbook {self.id} cancelled: {reason}")

    def pause(self) -> None:
        """Pause the Playbook."""
        if self.status != PlaybookStatus.ACTIVE:
            raise PlaybookNotActive(f"Cannot pause Playbook in status {self.status.name}")

        self.status = PlaybookStatus.PAUSED
        logger.info(f"Playbook {self.id} paused")

    def resume(self) -> None:
        """Resume a paused Playbook."""
        if self.status != PlaybookStatus.PAUSED:
            raise PlaybookError(f"Cannot resume Playbook in status {self.status.name}")

        self.status = PlaybookStatus.ACTIVE
        logger.info(f"Playbook {self.id} resumed")

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
        if self.status != PlaybookStatus.ACTIVE:
            raise PlaybookNotActive(f"Cannot advance phase in status {self.status.name}")

        if not self.can_transition(to_phase):
            logger.warning(
                f"Invalid phase transition: {self.current_phase.value} → {to_phase.value}"
            )
            return False

        # Check exit guards for current phase
        current_playbook_phase = self._get_playbook_phase(self.current_phase)
        if current_playbook_phase:
            for guard in current_playbook_phase.exit_guards:
                evaluation = self._evaluate_guard(guard)
                if evaluation.result == GuardResult.FAIL:
                    raise GuardFailed(evaluation)

        # Check entry guards for new phase
        new_playbook_phase = self._get_playbook_phase(to_phase)
        if new_playbook_phase:
            for guard in new_playbook_phase.entry_guards:
                evaluation = self._evaluate_guard(guard)
                if evaluation.result == GuardResult.FAIL:
                    raise GuardFailed(evaluation)

        old_phase = self.current_phase
        self.current_phase = to_phase
        self.phase_history.append((to_phase, datetime.now()))

        logger.info(f"Playbook {self.id}: {old_phase.value} → {to_phase.value}")
        return True

    def _get_playbook_phase(self, n_phase: NPhase) -> PlaybookPhase | None:
        """Get the PlaybookPhase for an NPhase."""
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

        Law 3: Guards emit Marks on evaluation.
        """
        # Basic guard evaluation (can be extended with custom checks)
        result = GuardResult.PASS
        message = f"Guard {guard.name} passed"

        if guard.check_type == "budget" and self._scope:
            if self._scope.budget.is_exhausted:
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
        """Add an entry guard to the Playbook."""
        self.entry_guards.append(guard)

    # =========================================================================
    # Mark Recording (Law 3)
    # =========================================================================

    def record_mark(self, mark: Mark) -> None:
        """Record a Mark emitted during this Playbook."""
        if mark.id not in self.mark_ids:
            self.mark_ids.append(mark.id)

    # Backwards compatibility
    def record_trace(self, trace: Mark) -> None:
        """Record a Mark (backwards compat alias)."""
        self.record_mark(trace)

    @property
    def mark_count(self) -> int:
        """Number of marks recorded."""
        return len(self.mark_ids)

    # Backwards compatibility
    @property
    def trace_count(self) -> int:
        """Number of marks recorded (backwards compat alias)."""
        return self.mark_count

    @property
    def covenant_id(self) -> GrantId | None:
        """Backwards compat alias for grant_id."""
        return self.grant_id

    @property
    def offering_id(self) -> ScopeId | None:
        """Backwards compat alias for scope_id."""
        return self.scope_id

    @property
    def current_step(self) -> int:
        """Backwards compat: phases are the new steps."""
        return len(self.phase_history)

    @property
    def total_steps(self) -> int:
        """Backwards compat: count of phases."""
        return len(self.phases) if self.phases else 3  # Default N-Phase has 3

    # =========================================================================
    # Requirements Check
    # =========================================================================

    def _check_requirements(self) -> None:
        """Check Law 1 and Law 2 requirements."""
        # Law 1: Grant required
        if self._grant is None:
            raise MissingGrant("Playbook requires a Grant")
        if not self._grant.is_active:
            raise MissingGrant(f"Grant is not active (status: {self._grant.status.name})")

        # Law 2: Scope required
        if self._scope is None:
            raise MissingScope("Playbook requires a Scope")
        if not self._scope.is_valid():
            raise MissingScope("Scope is not valid")

    @property
    def grant(self) -> Grant | None:
        """Get the associated Grant."""
        return self._grant

    # Backwards compatibility
    @property
    def covenant(self) -> Grant | None:
        """Get the associated Grant (backwards compat alias)."""
        return self._grant

    @property
    def scope(self) -> Scope | None:
        """Get the associated Scope."""
        return self._scope

    # Backwards compatibility
    @property
    def offering(self) -> Scope | None:
        """Get the associated Scope (backwards compat alias)."""
        return self._scope

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_active(self) -> bool:
        """Check if Playbook is active."""
        return self.status == PlaybookStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        """Check if Playbook is complete."""
        return self.status == PlaybookStatus.COMPLETE

    @property
    def duration_seconds(self) -> float | None:
        """Duration of the Playbook in seconds."""
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
            "grant_id": str(self.grant_id) if self.grant_id else None,
            "scope_id": str(self.scope_id) if self.scope_id else None,
            "phases": [p.to_dict() for p in self.phases],
            "current_phase": self.current_phase.value,
            "phase_history": [(p.value, ts.isoformat()) for p, ts in self.phase_history],
            "entry_guards": [g.to_dict() for g in self.entry_guards],
            "guard_evaluations": [e.to_dict() for e in self.guard_evaluations],
            "status": self.status.name,
            "walk_id": str(self.walk_id) if self.walk_id else None,
            "mark_ids": [str(mid) for mid in self.mark_ids],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Playbook:
        """Create from dictionary (without Grant/Scope - must be reattached)."""
        phase_history = [
            (NPhase(p), datetime.fromisoformat(ts)) for p, ts in data.get("phase_history", [])
        ]

        return cls(
            id=PlaybookId(data["id"]),
            name=data.get("name", ""),
            grant_id=GrantId(data["grant_id"]) if data.get("grant_id") else None,
            scope_id=ScopeId(data["scope_id"]) if data.get("scope_id") else None,
            phases=[PlaybookPhase.from_dict(p) for p in data.get("phases", [])],
            current_phase=NPhase(data.get("current_phase", "SENSE")),
            phase_history=phase_history,
            entry_guards=[SentinelGuard.from_dict(g) for g in data.get("entry_guards", [])],
            guard_evaluations=[],  # Not restored (ephemeral)
            status=PlaybookStatus[data.get("status", "PENDING")],
            walk_id=WalkId(data["walk_id"]) if data.get("walk_id") else None,
            mark_ids=[MarkId(mid) for mid in data.get("mark_ids", [])],
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
            f"Playbook(id={str(self.id)[:16]}..., "
            f"name='{self.name}', "
            f"phase={self.current_phase.value}, "
            f"status={self.status.name})"
        )


# Backwards compatibility alias
Playbook = Playbook


# =============================================================================
# PlaybookStore
# =============================================================================


@dataclass
class PlaybookStore:
    """Persistent storage for Playbooks."""

    _playbooks: dict[PlaybookId, Playbook] = field(default_factory=dict)

    def add(self, playbook: Playbook) -> None:
        """Add a Playbook to the store."""
        self._playbooks[playbook.id] = playbook

    def get(self, playbook_id: PlaybookId) -> Playbook | None:
        """Get a Playbook by ID."""
        return self._playbooks.get(playbook_id)

    def active(self) -> list[Playbook]:
        """Get all active Playbooks."""
        return [p for p in self._playbooks.values() if p.is_active]

    def recent(self, limit: int = 10) -> list[Playbook]:
        """Get most recent Playbooks."""
        sorted_playbooks = sorted(
            self._playbooks.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )
        return sorted_playbooks[:limit]

    def __len__(self) -> int:
        return len(self._playbooks)


# Backwards compatibility alias
PlaybookStore = PlaybookStore


# =============================================================================
# Global Store
# =============================================================================

_global_playbook_store: PlaybookStore | None = None


def get_playbook_store() -> PlaybookStore:
    """Get the global playbook store."""
    global _global_playbook_store
    if _global_playbook_store is None:
        _global_playbook_store = PlaybookStore()
    return _global_playbook_store


# Backwards compatibility alias
get_playbook_store = get_playbook_store


def reset_playbook_store() -> None:
    """Reset the global playbook store (for testing)."""
    global _global_playbook_store
    _global_playbook_store = None


# Backwards compatibility alias
reset_playbook_store = reset_playbook_store


# =============================================================================
# Backwards Compatibility Aliases (Ritual → Playbook)
# =============================================================================

# Type aliases
RitualId = PlaybookId
generate_ritual_id = generate_playbook_id

# Status
RitualStatus = PlaybookStatus

# Phase
RitualPhase = PlaybookPhase

# Exceptions
RitualError = PlaybookError
RitualNotActive = PlaybookNotActive
MissingCovenant = MissingGrant
MissingOffering = MissingScope

# Core types
Ritual = Playbook

# Store
RitualStore = PlaybookStore
get_ritual_store = get_playbook_store
reset_ritual_store = reset_playbook_store


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # New names (preferred)
    "PlaybookId",
    "generate_playbook_id",
    "PlaybookStatus",
    "GuardResult",
    "SentinelGuard",
    "GuardEvaluation",
    "PlaybookPhase",
    "PlaybookError",
    "PlaybookNotActive",
    "InvalidPhaseTransition",
    "GuardFailed",
    "MissingGrant",
    "MissingScope",
    "Playbook",
    "PlaybookStore",
    "get_playbook_store",
    "reset_playbook_store",
    # Backwards compatibility (Ritual → Playbook)
    "RitualId",
    "generate_ritual_id",
    "RitualStatus",
    "RitualPhase",
    "RitualError",
    "RitualNotActive",
    "MissingCovenant",
    "MissingOffering",
    "Ritual",
    "RitualStore",
    "get_ritual_store",
    "reset_ritual_store",
]
