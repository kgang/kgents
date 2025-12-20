"""
Covenant: Negotiated Permission Contract.

A Covenant is a formal agreement between human and agent that:
- Defines what operations are permitted (permissions)
- Specifies review gates for sensitive operations
- Can be proposed, negotiated, granted, and revoked

Every Ritual requires a Covenant. Covenants make permissions
explicit and revocable.

Philosophy:
    "Trust is earned, not assumed. A Covenant is the contract
    that makes trust explicit. It can be revoked at any time,
    ensuring human agency is always preserved."

Laws:
- Law 1 (Required): Sensitive operations require a granted Covenant
- Law 2 (Revocable): Covenants can be revoked at any time
- Law 3 (Gated): Review gates trigger on threshold

See: spec/protocols/warp-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 9: Directed Cycle)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

# =============================================================================
# Type Aliases
# =============================================================================

CovenantId = NewType("CovenantId", str)


def generate_covenant_id() -> CovenantId:
    """Generate a unique Covenant ID."""
    return CovenantId(f"covenant-{uuid4().hex[:12]}")


# =============================================================================
# Covenant Status
# =============================================================================


class CovenantStatus(Enum):
    """
    Status of a Covenant.

    Lifecycle:
        PROPOSED → NEGOTIATING → GRANTED ↔ REVOKED
                              ↓
                           EXPIRED

    Transitions:
    - PROPOSED: Initial state, awaiting human review
    - NEGOTIATING: Human and agent discussing terms
    - GRANTED: Active and usable
    - REVOKED: Explicitly revoked by human (can be re-granted)
    - EXPIRED: Past expiry time (terminal unless renewed)
    """

    PROPOSED = auto()  # Awaiting human review
    NEGOTIATING = auto()  # Terms being discussed
    GRANTED = auto()  # Active and usable
    REVOKED = auto()  # Explicitly revoked
    EXPIRED = auto()  # Past expiry time


# =============================================================================
# Gate Fallback
# =============================================================================


class GateFallback(Enum):
    """What to do when a ReviewGate times out."""

    DENY = auto()  # Deny the operation (safe default)
    ALLOW_LIMITED = auto()  # Allow with reduced scope
    ESCALATE = auto()  # Escalate to higher authority


# =============================================================================
# ReviewGate
# =============================================================================


@dataclass(frozen=True)
class ReviewGate:
    """
    Checkpoint requiring human review.

    Law 3: Review gates trigger on threshold.

    A ReviewGate is triggered when:
    - A specific operation pattern is matched
    - The threshold count is reached

    Example:
        >>> gate = ReviewGate(
        ...     trigger="file_write",
        ...     description="Review file writes",
        ...     threshold=5,
        ... )
        >>> # After 5 file writes, human review is triggered
    """

    trigger: str  # Operation pattern: "file_write", "git_push", etc.
    description: str = ""
    threshold: int = 1  # Review after N occurrences
    timeout_seconds: float = 300.0  # How long to wait for review
    fallback: GateFallback = GateFallback.DENY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trigger": self.trigger,
            "description": self.description,
            "threshold": self.threshold,
            "timeout_seconds": self.timeout_seconds,
            "fallback": self.fallback.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReviewGate:
        """Create from dictionary."""
        return cls(
            trigger=data["trigger"],
            description=data.get("description", ""),
            threshold=data.get("threshold", 1),
            timeout_seconds=data.get("timeout_seconds", 300.0),
            fallback=GateFallback[data.get("fallback", "DENY")],
        )


# =============================================================================
# GateOccurrence
# =============================================================================


@dataclass
class GateOccurrence:
    """
    Tracks occurrences of a gated operation.

    Used by CovenantEnforcer to count operations and trigger gates.
    """

    gate: ReviewGate
    count: int = 0
    last_triggered: datetime | None = None
    last_reviewed: datetime | None = None
    review_pending: bool = False

    def record(self) -> bool:
        """
        Record an occurrence. Returns True if gate threshold reached.
        """
        self.count += 1
        if self.count >= self.gate.threshold:
            self.last_triggered = datetime.now()
            self.review_pending = True
            return True
        return False

    def reset(self) -> None:
        """Reset counter (called after review)."""
        self.count = 0
        self.last_reviewed = datetime.now()
        self.review_pending = False


# =============================================================================
# Exceptions
# =============================================================================


class CovenantError(Exception):
    """Base exception for Covenant errors."""

    pass


class CovenantNotGranted(CovenantError):
    """Law 1: Attempted operation without granted Covenant."""

    pass


class CovenantRevoked(CovenantError):
    """Law 2: Covenant has been revoked."""

    pass


class GateTriggered(CovenantError):
    """Law 3: Review gate threshold reached."""

    def __init__(self, gate: ReviewGate, message: str = ""):
        self.gate = gate
        super().__init__(message or f"Review gate triggered: {gate.trigger}")


# =============================================================================
# Covenant: The Core Primitive
# =============================================================================


@dataclass(frozen=True)
class Covenant:
    """
    Negotiated permission contract.

    Laws:
    - Law 1 (Required): Sensitive operations require granted Covenant
    - Law 2 (Revocable): Can be revoked at any time
    - Law 3 (Gated): Review gates trigger on threshold

    A Covenant defines:
    - What permissions are granted
    - What operations trigger review gates
    - Who granted it and when

    Example:
        >>> covenant = Covenant.propose(
        ...     permissions=frozenset({"file_read", "file_write", "git_commit"}),
        ...     review_gates=(
        ...         ReviewGate("git_push", threshold=1),
        ...         ReviewGate("file_delete", threshold=3),
        ...     ),
        ...     reason="Implement TraceNode feature",
        ... )
        >>> # Human reviews and grants
        >>> granted = covenant.grant(granted_by="kent")
    """

    # Identity
    id: CovenantId = field(default_factory=generate_covenant_id)

    # Permissions
    permissions: frozenset[str] = field(default_factory=frozenset)

    # Review gates (Law 3)
    review_gates: tuple[ReviewGate, ...] = ()

    # Status
    status: CovenantStatus = CovenantStatus.PROPOSED

    # Grant info
    granted_by: str | None = None
    granted_at: datetime | None = None

    # Revocation info
    revoked_by: str | None = None
    revoked_at: datetime | None = None
    revoke_reason: str = ""

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None

    # Metadata
    reason: str = ""  # Why this Covenant was requested
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def propose(
        cls,
        permissions: frozenset[str],
        review_gates: tuple[ReviewGate, ...] | None = None,
        reason: str = "",
        expires_at: datetime | None = None,
    ) -> Covenant:
        """
        Propose a new Covenant.

        This creates a Covenant in PROPOSED status awaiting human review.
        """
        return cls(
            permissions=permissions,
            review_gates=review_gates or (),
            status=CovenantStatus.PROPOSED,
            reason=reason,
            expires_at=expires_at,
        )

    # =========================================================================
    # Status Transitions
    # =========================================================================

    def negotiate(self) -> Covenant:
        """Move to NEGOTIATING status."""
        if self.status != CovenantStatus.PROPOSED:
            raise CovenantError(f"Cannot negotiate from {self.status.name}")

        return Covenant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=CovenantStatus.NEGOTIATING,
            created_at=self.created_at,
            expires_at=self.expires_at,
            reason=self.reason,
            metadata=self.metadata,
        )

    def grant(self, granted_by: str) -> Covenant:
        """
        Grant the Covenant.

        Law 1: Only granted Covenants permit operations.
        """
        if self.status not in {CovenantStatus.PROPOSED, CovenantStatus.NEGOTIATING}:
            raise CovenantError(f"Cannot grant from {self.status.name}")

        return Covenant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=CovenantStatus.GRANTED,
            granted_by=granted_by,
            granted_at=datetime.now(),
            created_at=self.created_at,
            expires_at=self.expires_at,
            reason=self.reason,
            metadata=self.metadata,
        )

    def revoke(self, revoked_by: str, reason: str = "") -> Covenant:
        """
        Revoke the Covenant.

        Law 2: Covenants can be revoked at any time.
        """
        if self.status not in {
            CovenantStatus.GRANTED,
            CovenantStatus.PROPOSED,
            CovenantStatus.NEGOTIATING,
        }:
            raise CovenantError(f"Cannot revoke from {self.status.name}")

        return Covenant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=CovenantStatus.REVOKED,
            granted_by=self.granted_by,
            granted_at=self.granted_at,
            revoked_by=revoked_by,
            revoked_at=datetime.now(),
            revoke_reason=reason,
            created_at=self.created_at,
            expires_at=self.expires_at,
            reason=self.reason,
            metadata=self.metadata,
        )

    def amend(
        self,
        permissions: frozenset[str] | None = None,
        review_gates: tuple[ReviewGate, ...] | None = None,
    ) -> Covenant:
        """
        Amend the Covenant with new terms.

        Returns a new PROPOSED Covenant with updated terms.
        """
        return Covenant(
            permissions=permissions if permissions is not None else self.permissions,
            review_gates=review_gates if review_gates is not None else self.review_gates,
            status=CovenantStatus.PROPOSED,
            reason=f"Amendment of {self.id}",
            expires_at=self.expires_at,
            metadata={**self.metadata, "amends": str(self.id)},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @property
    def is_active(self) -> bool:
        """Check if Covenant is active and usable."""
        if self.status != CovenantStatus.GRANTED:
            return False
        if self.expires_at is not None and datetime.now() > self.expires_at:
            return False
        return True

    def check_active(self) -> None:
        """Raise if Covenant is not active."""
        if self.status == CovenantStatus.REVOKED:
            raise CovenantRevoked(f"Covenant {self.id} was revoked: {self.revoke_reason}")
        if self.status != CovenantStatus.GRANTED:
            raise CovenantNotGranted(f"Covenant {self.id} not granted (status: {self.status.name})")
        if self.expires_at is not None and datetime.now() > self.expires_at:
            raise CovenantError(f"Covenant {self.id} has expired")

    def has_permission(self, permission: str) -> bool:
        """Check if a permission is granted."""
        return permission in self.permissions

    def check_permission(self, permission: str) -> None:
        """Check permission, raising if not granted or Covenant inactive."""
        self.check_active()
        if not self.has_permission(permission):
            raise CovenantNotGranted(
                f"Permission '{permission}' not in Covenant. Allowed: {self.permissions}"
            )

    def get_gate(self, trigger: str) -> ReviewGate | None:
        """Get the review gate for a trigger, if any."""
        for gate in self.review_gates:
            if gate.trigger == trigger:
                return gate
        return None

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "permissions": list(self.permissions),
            "review_gates": [g.to_dict() for g in self.review_gates],
            "status": self.status.name,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "revoked_by": self.revoked_by,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoke_reason": self.revoke_reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "reason": self.reason,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Covenant:
        """Create from dictionary."""
        return cls(
            id=CovenantId(data["id"]),
            permissions=frozenset(data.get("permissions", [])),
            review_gates=tuple(ReviewGate.from_dict(g) for g in data.get("review_gates", [])),
            status=CovenantStatus[data.get("status", "PROPOSED")],
            granted_by=data.get("granted_by"),
            granted_at=datetime.fromisoformat(data["granted_at"])
            if data.get("granted_at")
            else None,
            revoked_by=data.get("revoked_by"),
            revoked_at=datetime.fromisoformat(data["revoked_at"])
            if data.get("revoked_at")
            else None,
            revoke_reason=data.get("revoke_reason", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            reason=data.get("reason", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        perms = len(self.permissions)
        gates = len(self.review_gates)
        return (
            f"Covenant(id={str(self.id)[:16]}..., "
            f"status={self.status.name}, "
            f"permissions={perms}, gates={gates})"
        )


# =============================================================================
# CovenantEnforcer
# =============================================================================


@dataclass
class CovenantEnforcer:
    """
    Runtime enforcer for Covenant permissions and gates.

    Tracks operation counts and triggers review gates when thresholds reached.

    Example:
        >>> enforcer = CovenantEnforcer(covenant)
        >>> enforcer.check("file_read")  # OK
        >>> enforcer.check("git_push")   # Might trigger gate
    """

    covenant: Covenant
    _occurrences: dict[str, GateOccurrence] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize gate occurrences."""
        for gate in self.covenant.review_gates:
            self._occurrences[gate.trigger] = GateOccurrence(gate)

    def check(self, operation: str) -> None:
        """
        Check if operation is permitted.

        Raises:
        - CovenantNotGranted: if operation not in permissions
        - CovenantRevoked: if Covenant was revoked
        - GateTriggered: if review gate threshold reached
        """
        self.covenant.check_permission(operation)

        # Check if this operation has a gate
        if operation in self._occurrences:
            occurrence = self._occurrences[operation]
            if occurrence.record():
                raise GateTriggered(occurrence.gate)

    def approve_gate(self, trigger: str) -> None:
        """Approve a pending gate review, resetting the counter."""
        if trigger in self._occurrences:
            self._occurrences[trigger].reset()

    def is_gate_pending(self, trigger: str) -> bool:
        """Check if a gate has a pending review."""
        if trigger in self._occurrences:
            return self._occurrences[trigger].review_pending
        return False


# =============================================================================
# CovenantStore
# =============================================================================


@dataclass
class CovenantStore:
    """
    Persistent storage for Covenants.
    """

    _covenants: dict[CovenantId, Covenant] = field(default_factory=dict)

    def add(self, covenant: Covenant) -> None:
        """Add a Covenant to the store."""
        self._covenants[covenant.id] = covenant

    def get(self, covenant_id: CovenantId) -> Covenant | None:
        """Get a Covenant by ID."""
        return self._covenants.get(covenant_id)

    def update(self, covenant: Covenant) -> None:
        """Update a Covenant (replace with new version)."""
        self._covenants[covenant.id] = covenant

    def active(self) -> list[Covenant]:
        """Get all active Covenants."""
        return [c for c in self._covenants.values() if c.is_active]

    def pending(self) -> list[Covenant]:
        """Get Covenants awaiting approval."""
        return [
            c
            for c in self._covenants.values()
            if c.status in {CovenantStatus.PROPOSED, CovenantStatus.NEGOTIATING}
        ]

    def revoked(self) -> list[Covenant]:
        """Get revoked Covenants."""
        return [c for c in self._covenants.values() if c.status == CovenantStatus.REVOKED]

    def __len__(self) -> int:
        return len(self._covenants)


# =============================================================================
# Global Store
# =============================================================================

_global_covenant_store: CovenantStore | None = None


def get_covenant_store() -> CovenantStore:
    """Get the global covenant store."""
    global _global_covenant_store
    if _global_covenant_store is None:
        _global_covenant_store = CovenantStore()
    return _global_covenant_store


def reset_covenant_store() -> None:
    """Reset the global covenant store (for testing)."""
    global _global_covenant_store
    _global_covenant_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "CovenantId",
    "generate_covenant_id",
    # Status
    "CovenantStatus",
    "GateFallback",
    # Review gates
    "ReviewGate",
    "GateOccurrence",
    # Exceptions
    "CovenantError",
    "CovenantNotGranted",
    "CovenantRevoked",
    "GateTriggered",
    # Core
    "Covenant",
    "CovenantEnforcer",
    # Store
    "CovenantStore",
    "get_covenant_store",
    "reset_covenant_store",
]
