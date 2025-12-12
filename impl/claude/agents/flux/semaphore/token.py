"""
SemaphoreToken: The Red Card.

Return this from an agent to flip red and yield to human.
The token carries all state needed for crash-safe resumption.
"""

from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from .reason import SemaphoreReason

R = TypeVar("R")  # Required context type from human


@dataclass
class SemaphoreToken(Generic[R]):
    """
    The Red Card. Return this from an agent to flip red.

    When a FluxAgent's inner.invoke() RETURNS this (not yields!),
    the event is ejected to Purgatory until human provides context.

    The Rodizio Pattern:
    - Agent returns SemaphoreToken → FluxAgent detects → Eject to Purgatory
    - Stream continues flowing (no head-of-line blocking)
    - Human resolves → ReentryContext injected as Perturbation
    - Agent.resume() completes processing

    Design Decisions:
    1. frozen_state is bytes (pickled), not the Python object.
       This enables crash-safe persistence via D-gent (Phase 3).
    2. Token has __hash__ based on id for use in sets.
    3. Cancelled tokens stay in _pending (marked) rather than removed.
       This preserves audit trail and prevents double-resolution.

    Example:
        >>> token = SemaphoreToken(
        ...     reason=SemaphoreReason.APPROVAL_NEEDED,
        ...     frozen_state=pickle.dumps(my_state),
        ...     original_event=event,
        ...     prompt="Delete 47 records?",
        ...     options=["Approve", "Reject"],
        ...     severity="critical",
        ... )
        >>> return token  # NOT yield!
    """

    # ─────────────────────────────────────────────────────────────
    # Identity
    # ─────────────────────────────────────────────────────────────

    id: str = field(default_factory=lambda: f"sem-{uuid.uuid4().hex[:8]}")
    """Unique identifier. Format: sem-{8 hex chars}."""

    # ─────────────────────────────────────────────────────────────
    # Why yielded
    # ─────────────────────────────────────────────────────────────

    reason: SemaphoreReason = SemaphoreReason.CONTEXT_REQUIRED
    """Why the agent yielded. Affects UI display and routing."""

    # ─────────────────────────────────────────────────────────────
    # State preservation (CRITICAL: this is what makes it crash-safe)
    # ─────────────────────────────────────────────────────────────

    frozen_state: bytes = b""
    """
    Pickled agent state at ejection.

    We pickle DATA (frozen_state), not GENERATORS.
    This is what makes Purgatory crash-safe when D-gent is wired.
    """

    original_event: Any = None
    """The event that triggered this semaphore. For audit/debugging."""

    # ─────────────────────────────────────────────────────────────
    # Type hint for expected human input
    # ─────────────────────────────────────────────────────────────

    required_type: type[R] | None = None
    """
    Type hint for expected human input.

    Optional but useful for validation and documentation.
    """

    # ─────────────────────────────────────────────────────────────
    # Optional timing (Rodizio is INDEFINITE by default)
    # ─────────────────────────────────────────────────────────────

    deadline: datetime | None = None
    """
    Auto-escalate after this time.

    Optional. Rodizio is indefinite by default; deadline is opt-in.
    """

    escalation: str | None = None
    """Who to escalate to after deadline. Optional."""

    # ─────────────────────────────────────────────────────────────
    # UI metadata (for CLI/TUI display)
    # ─────────────────────────────────────────────────────────────

    prompt: str = ""
    """Human-readable question. Example: 'Delete 47 records?'"""

    options: list[str] = field(default_factory=list)
    """Suggested responses. Example: ['Approve', 'Reject', 'Review']"""

    severity: str = "info"
    """
    Severity level: 'info' | 'warning' | 'critical'.

    Affects UI styling and notification urgency.
    """

    # ─────────────────────────────────────────────────────────────
    # Timestamps
    # ─────────────────────────────────────────────────────────────

    created_at: datetime = field(default_factory=datetime.now)
    """When the token was created."""

    resolved_at: datetime | None = None
    """When the token was resolved. None if pending or cancelled."""

    cancelled_at: datetime | None = None
    """When the token was cancelled. None if pending or resolved."""

    # ─────────────────────────────────────────────────────────────
    # State Properties
    # ─────────────────────────────────────────────────────────────

    @property
    def is_pending(self) -> bool:
        """
        Check if token is still awaiting resolution.

        A token is pending if it has not been resolved, cancelled, or voided.
        """
        return (
            self.resolved_at is None
            and self.cancelled_at is None
            and getattr(self, "voided_at", None) is None
        )

    @property
    def is_resolved(self) -> bool:
        """
        Check if token was resolved (not cancelled).

        A resolved token has received human input successfully.
        """
        return self.resolved_at is not None

    @property
    def is_cancelled(self) -> bool:
        """
        Check if token was cancelled.

        A cancelled token was abandoned without human input.
        """
        return self.cancelled_at is not None

    # ─────────────────────────────────────────────────────────────
    # Identity and Hashing
    # ─────────────────────────────────────────────────────────────

    def __hash__(self) -> int:
        """Hash based on id for use in sets and dict keys."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Equality based on id, not all fields."""
        if not isinstance(other, SemaphoreToken):
            return NotImplemented
        return self.id == other.id

    # ─────────────────────────────────────────────────────────────
    # Deadline Management
    # ─────────────────────────────────────────────────────────────

    voided_at: datetime | None = field(default=None, repr=False)
    """When the token was voided (deadline expired). None if not voided."""

    @property
    def is_voided(self) -> bool:
        """
        Check if token was voided (deadline expired).

        A voided token had its deadline pass without resolution.
        This is the system's "default on a promise" - the human failed
        to provide context within the specified timeframe.
        """
        return self.voided_at is not None

    def check_deadline(self) -> bool:
        """
        Check if deadline has passed and void if so.

        Returns:
            True if token is now voided (deadline passed), False otherwise.

        Note:
            This method mutates state if deadline has passed.
            Only pending tokens can be voided.
        """
        if not self.is_pending:
            return self.is_voided
        if self.deadline is None:
            return False
        if datetime.now() >= self.deadline:
            self.voided_at = datetime.now()
            return True
        return False

    # ─────────────────────────────────────────────────────────────
    # JSON Serialization (for D-gent persistence)
    # ─────────────────────────────────────────────────────────────

    def to_json(self) -> dict[str, Any]:
        """
        Serialize token to JSON-compatible dict.

        frozen_state (bytes) is base64-encoded for JSON compatibility.
        datetime fields are ISO-formatted strings.

        Returns:
            JSON-serializable dict representation
        """
        return {
            "id": self.id,
            "reason": self.reason.value,
            "frozen_state": base64.b64encode(self.frozen_state).decode("utf-8"),
            "original_event": self.original_event,  # Must be JSON-serializable
            "required_type": (
                self.required_type.__name__ if self.required_type is not None else None
            ),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "escalation": self.escalation,
            "prompt": self.prompt,
            "options": self.options,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "cancelled_at": (
                self.cancelled_at.isoformat() if self.cancelled_at else None
            ),
            "voided_at": self.voided_at.isoformat() if self.voided_at else None,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "SemaphoreToken[Any]":
        """
        Deserialize token from JSON dict.

        Args:
            data: Dict from to_json() or JSON parsing

        Returns:
            Reconstructed SemaphoreToken

        Note:
            required_type is stored as string name only; the actual type
            is not reconstructed (would require import resolution).
        """
        token: SemaphoreToken[Any] = cls(
            id=data["id"],
            reason=SemaphoreReason(data["reason"]),
            frozen_state=base64.b64decode(data["frozen_state"]),
            original_event=data.get("original_event"),
            required_type=None,  # Type name only, not actual type
            deadline=(
                datetime.fromisoformat(data["deadline"])
                if data.get("deadline")
                else None
            ),
            escalation=data.get("escalation"),
            prompt=data.get("prompt", ""),
            options=data.get("options", []),
            severity=data.get("severity", "info"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

        # Set terminal state timestamps
        if data.get("resolved_at"):
            token.resolved_at = datetime.fromisoformat(data["resolved_at"])
        if data.get("cancelled_at"):
            token.cancelled_at = datetime.fromisoformat(data["cancelled_at"])
        if data.get("voided_at"):
            token.voided_at = datetime.fromisoformat(data["voided_at"])

        return token
