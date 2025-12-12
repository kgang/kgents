"""
SemaphoreToken: The Red Card.

Return this from an agent to flip red and yield to human.
The token carries all state needed for crash-safe resumption.
"""

from __future__ import annotations

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

        A token is pending if it has neither been resolved nor cancelled.
        """
        return self.resolved_at is None and self.cancelled_at is None

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
