"""
Grant: Negotiated Permission Contract.

A Grant is a formal agreement between human and agent that:
- Defines what operations are permitted (permissions)
- Specifies review gates for sensitive operations
- Can be proposed, negotiated, granted, and revoked

Every Playbook requires a Grant. Grants make permissions
explicit and revocable.

Philosophy:
    "Trust is earned, not assumed. A Grant is the contract
    that makes trust explicit. It can be revoked at any time,
    ensuring human agency is always preserved."

Laws:
- Law 1 (Required): Sensitive operations require a granted Grant
- Law 2 (Revocable): Grants can be revoked at any time
- Law 3 (Gated): Review gates trigger on threshold

Rename History:
    Grant → Grant (spec/protocols/witness-primitives.md)
    "A grant of permission" - clearer than religious connotation

See: spec/protocols/witness-primitives.md
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

GrantId = NewType("GrantId", str)

# Backwards compatibility alias
GrantId = GrantId


def generate_grant_id() -> GrantId:
    """Generate a unique Grant ID."""
    return GrantId(f"grant-{uuid4().hex[:12]}")


# Backwards compatibility alias
generate_grant_id = generate_grant_id


# =============================================================================
# Grant Status
# =============================================================================


class GrantStatus(Enum):
    """
    Status of a Grant.

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


# Backwards compatibility alias
GrantStatus = GrantStatus


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

    Used by GrantEnforcer to count operations and trigger gates.
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


class GrantError(Exception):
    """Base exception for Grant errors."""

    pass


# Backwards compatibility alias
GrantError = GrantError


class GrantNotGranted(GrantError):
    """Law 1: Attempted operation without granted Grant."""

    pass


# Backwards compatibility alias
GrantNotGranted = GrantNotGranted


class GrantRevoked(GrantError):
    """Law 2: Grant has been revoked."""

    pass


# Backwards compatibility alias
GrantRevoked = GrantRevoked


class GateTriggered(GrantError):
    """Law 3: Review gate threshold reached."""

    def __init__(self, gate: ReviewGate, message: str = ""):
        self.gate = gate
        super().__init__(message or f"Review gate triggered: {gate.trigger}")


# =============================================================================
# Grant: The Core Primitive
# =============================================================================


@dataclass(frozen=True)
class Grant:
    """
    Negotiated permission contract.

    Laws:
    - Law 1 (Required): Sensitive operations require granted Grant
    - Law 2 (Revocable): Can be revoked at any time
    - Law 3 (Gated): Review gates trigger on threshold

    A Grant defines:
    - What permissions are granted
    - What operations trigger review gates
    - Who granted it and when

    Example:
        >>> grant = Grant.propose(
        ...     permissions=frozenset({"file_read", "file_write", "git_commit"}),
        ...     review_gates=(
        ...         ReviewGate("git_push", threshold=1),
        ...         ReviewGate("file_delete", threshold=3),
        ...     ),
        ...     reason="Implement Mark feature",
        ... )
        >>> # Human reviews and grants
        >>> granted = grant.grant(granted_by="kent")
    """

    # Identity
    id: GrantId = field(default_factory=generate_grant_id)

    # Permissions
    permissions: frozenset[str] = field(default_factory=frozenset)

    # Review gates (Law 3)
    review_gates: tuple[ReviewGate, ...] = ()

    # Status
    status: GrantStatus = GrantStatus.PROPOSED

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
    reason: str = ""  # Why this Grant was requested
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def propose(
        cls,
        permissions: frozenset[str] | tuple[str, ...] | list[str],
        review_gates: tuple[ReviewGate, ...] | None = None,
        reason: str = "",
        expires_at: datetime | None = None,
        description: str = "",  # Backwards compat alias for reason
    ) -> Grant:
        """
        Propose a new Grant.

        This creates a Grant in PROPOSED status awaiting human review.
        """
        # Accept tuple or list for backwards compat
        if isinstance(permissions, (tuple, list)):
            permissions = frozenset(permissions)
        # description is backwards compat alias for reason
        final_reason = reason or description
        return cls(
            permissions=permissions,
            review_gates=review_gates or (),
            status=GrantStatus.PROPOSED,
            reason=final_reason,
            expires_at=expires_at,
        )

    # =========================================================================
    # Status Transitions
    # =========================================================================

    def negotiate(self) -> Grant:
        """Move to NEGOTIATING status."""
        if self.status != GrantStatus.PROPOSED:
            raise GrantError(f"Cannot negotiate from {self.status.name}")

        return Grant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=GrantStatus.NEGOTIATING,
            created_at=self.created_at,
            expires_at=self.expires_at,
            reason=self.reason,
            metadata=self.metadata,
        )

    def grant(self, granted_by: str) -> Grant:
        """
        Grant the Grant.

        Law 1: Only granted Grants permit operations.
        """
        if self.status not in {GrantStatus.PROPOSED, GrantStatus.NEGOTIATING}:
            raise GrantError(f"Cannot grant from {self.status.name}")

        return Grant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=GrantStatus.GRANTED,
            granted_by=granted_by,
            granted_at=datetime.now(),
            created_at=self.created_at,
            expires_at=self.expires_at,
            reason=self.reason,
            metadata=self.metadata,
        )

    def revoke(self, revoked_by: str, reason: str = "") -> Grant:
        """
        Revoke the Grant.

        Law 2: Grants can be revoked at any time.
        """
        if self.status not in {
            GrantStatus.GRANTED,
            GrantStatus.PROPOSED,
            GrantStatus.NEGOTIATING,
        }:
            raise GrantError(f"Cannot revoke from {self.status.name}")

        return Grant(
            id=self.id,
            permissions=self.permissions,
            review_gates=self.review_gates,
            status=GrantStatus.REVOKED,
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
    ) -> Grant:
        """
        Amend the Grant with new terms.

        Returns a new PROPOSED Grant with updated terms.
        """
        return Grant(
            permissions=permissions if permissions is not None else self.permissions,
            review_gates=review_gates if review_gates is not None else self.review_gates,
            status=GrantStatus.PROPOSED,
            reason=f"Amendment of {self.id}",
            expires_at=self.expires_at,
            metadata={**self.metadata, "amends": str(self.id)},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @property
    def is_active(self) -> bool:
        """Check if Grant is active and usable."""
        if self.status != GrantStatus.GRANTED:
            return False
        if self.expires_at is not None and datetime.now() > self.expires_at:
            return False
        return True

    def check_active(self) -> None:
        """Raise if Grant is not active."""
        if self.status == GrantStatus.REVOKED:
            raise GrantRevoked(f"Grant {self.id} was revoked: {self.revoke_reason}")
        if self.status != GrantStatus.GRANTED:
            raise GrantNotGranted(f"Grant {self.id} not granted (status: {self.status.name})")
        if self.expires_at is not None and datetime.now() > self.expires_at:
            raise GrantError(f"Grant {self.id} has expired")

    def has_permission(self, permission: str) -> bool:
        """Check if a permission is granted."""
        return permission in self.permissions

    def check_permission(self, permission: str) -> None:
        """Check permission, raising if not granted or Grant inactive."""
        self.check_active()
        if not self.has_permission(permission):
            raise GrantNotGranted(
                f"Permission '{permission}' not in Grant. Allowed: {self.permissions}"
            )

    def get_gate(self, trigger: str) -> ReviewGate | None:
        """Get the review gate for a trigger, if any."""
        for gate in self.review_gates:
            if gate.trigger == trigger:
                return gate
        return None

    # =========================================================================
    # Backwards Compatibility Properties
    # =========================================================================

    @property
    def trust_level(self) -> str:
        """Backwards compat: derive from status."""
        if self.status == GrantStatus.GRANTED:
            return "high"
        elif self.status == GrantStatus.NEGOTIATING:
            return "medium"
        return "low"

    @property
    def proposed_at(self) -> datetime:
        """Backwards compat: alias for created_at."""
        return self.created_at

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
    def from_dict(cls, data: dict[str, Any]) -> Grant:
        """Create from dictionary."""
        return cls(
            id=GrantId(data["id"]),
            permissions=frozenset(data.get("permissions", [])),
            review_gates=tuple(ReviewGate.from_dict(g) for g in data.get("review_gates", [])),
            status=GrantStatus[data.get("status", "PROPOSED")],
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
            f"Grant(id={str(self.id)[:16]}..., "
            f"status={self.status.name}, "
            f"permissions={perms}, gates={gates})"
        )


# Backwards compatibility alias
Grant = Grant


# =============================================================================
# GrantEnforcer
# =============================================================================


@dataclass
class GrantEnforcer:
    """
    Runtime enforcer for Grant permissions and gates.

    Tracks operation counts and triggers review gates when thresholds reached.

    Example:
        >>> enforcer = GrantEnforcer(grant)
        >>> enforcer.check("file_read")  # OK
        >>> enforcer.check("git_push")   # Might trigger gate
    """

    grant: Grant
    _occurrences: dict[str, GateOccurrence] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize gate occurrences."""
        for gate in self.grant.review_gates:
            self._occurrences[gate.trigger] = GateOccurrence(gate)

    def check(self, operation: str) -> None:
        """
        Check if operation is permitted.

        Raises:
        - GrantNotGranted: if operation not in permissions
        - GrantRevoked: if Grant was revoked
        - GateTriggered: if review gate threshold reached
        """
        self.grant.check_permission(operation)

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


# Backwards compatibility alias
GrantEnforcer = GrantEnforcer


# =============================================================================
# GrantStore
# =============================================================================


@dataclass
class GrantStore:
    """
    Persistent storage for Grants.
    """

    _grants: dict[GrantId, Grant] = field(default_factory=dict)

    def add(self, grant: Grant) -> None:
        """Add a Grant to the store."""
        self._grants[grant.id] = grant

    def get(self, grant_id: GrantId) -> Grant | None:
        """Get a Grant by ID."""
        return self._grants.get(grant_id)

    def update(self, grant: Grant) -> None:
        """Update a Grant (replace with new version)."""
        self._grants[grant.id] = grant

    def active(self) -> list[Grant]:
        """Get all active Grants."""
        return [g for g in self._grants.values() if g.is_active]

    def pending(self) -> list[Grant]:
        """Get Grants awaiting approval."""
        return [
            g
            for g in self._grants.values()
            if g.status in {GrantStatus.PROPOSED, GrantStatus.NEGOTIATING}
        ]

    def revoked(self) -> list[Grant]:
        """Get revoked Grants."""
        return [g for g in self._grants.values() if g.status == GrantStatus.REVOKED]

    def __len__(self) -> int:
        return len(self._grants)


# Backwards compatibility alias
GrantStore = GrantStore


# =============================================================================
# Global Store
# =============================================================================

_global_grant_store: GrantStore | None = None


def get_grant_store() -> GrantStore:
    """Get the global grant store."""
    global _global_grant_store
    if _global_grant_store is None:
        _global_grant_store = GrantStore()
    return _global_grant_store


# Backwards compatibility alias
get_grant_store = get_grant_store


def reset_grant_store() -> None:
    """Reset the global grant store (for testing)."""
    global _global_grant_store
    _global_grant_store = None


# Backwards compatibility alias
reset_grant_store = reset_grant_store


# =============================================================================
# Backwards Compatibility Aliases (Covenant → Grant)
# =============================================================================

# Type aliases
CovenantId = GrantId
generate_covenant_id = generate_grant_id

# Status
CovenantStatus = GrantStatus

# Exceptions
CovenantError = GrantError
CovenantNotGranted = GrantNotGranted
CovenantRevoked = GrantRevoked

# Core types
Covenant = Grant
CovenantEnforcer = GrantEnforcer

# Store
CovenantStore = GrantStore
get_covenant_store = get_grant_store
reset_covenant_store = reset_grant_store


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # New names (preferred)
    "GrantId",
    "generate_grant_id",
    "GrantStatus",
    "GateFallback",
    "ReviewGate",
    "GateOccurrence",
    "GrantError",
    "GrantNotGranted",
    "GrantRevoked",
    "GateTriggered",
    "Grant",
    "GrantEnforcer",
    "GrantStore",
    "get_grant_store",
    "reset_grant_store",
    # Backwards compatibility (Covenant → Grant)
    "CovenantId",
    "generate_covenant_id",
    "CovenantStatus",
    "CovenantError",
    "CovenantNotGranted",
    "CovenantRevoked",
    "Covenant",
    "CovenantEnforcer",
    "CovenantStore",
    "get_covenant_store",
    "reset_covenant_store",
]
