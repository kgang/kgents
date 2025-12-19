"""
Witness AGENTESE Contracts: Type-safe request/response definitions.

These dataclasses define the contracts for all WitnessNode aspects.
They serve as the single source of truth for BE/FE type alignment.

Pattern 13 (Contract-First Types):
- @node(contracts={...}) is the authority
- Frontend discovers contracts at build time
- Type drift caught in CI

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# =============================================================================
# Manifest Aspect (Response only)
# =============================================================================


@dataclass
class WitnessManifestResponse:
    """Response for manifest aspect."""

    total_thoughts: int
    total_actions: int
    trust_count: int
    reversible_actions: int
    storage_backend: str


# =============================================================================
# Thoughts Aspect
# =============================================================================


@dataclass
class ThoughtsRequest:
    """Request for thoughts aspect."""

    limit: int = 50
    source: str | None = None
    since: str | None = None  # ISO datetime string


@dataclass
class ThoughtItem:
    """A single thought in the response."""

    content: str
    source: str
    tags: list[str]
    timestamp: str | None


@dataclass
class ThoughtsResponse:
    """Response for thoughts aspect."""

    count: int
    thoughts: list[ThoughtItem] = field(default_factory=list)


# =============================================================================
# Trust Aspect
# =============================================================================


@dataclass
class TrustRequest:
    """Request for trust aspect."""

    git_email: str
    apply_decay: bool = True


@dataclass
class TrustResponse:
    """Response for trust aspect."""

    trust_level: str  # TrustLevel name
    trust_level_value: int  # TrustLevel value (0-3)
    raw_level: float
    last_active: str | None  # ISO datetime
    observation_count: int
    successful_operations: int
    confirmed_suggestions: int
    total_suggestions: int
    acceptance_rate: float
    decay_applied: bool


# =============================================================================
# Capture Thought Aspect
# =============================================================================


@dataclass
class CaptureThoughtRequest:
    """Request for capture aspect."""

    content: str
    source: str = "manual"
    tags: list[str] = field(default_factory=list)


@dataclass
class CaptureThoughtResponse:
    """Response for capture aspect."""

    thought_id: str
    content: str
    source: str
    tags: list[str]
    timestamp: str | None
    datum_id: str | None


# =============================================================================
# Action Record Aspect
# =============================================================================


@dataclass
class ActionRecordRequest:
    """Request for action aspect."""

    action: str
    success: bool = True
    message: str = ""
    reversible: bool = True
    inverse_action: str | None = None
    git_stash_ref: str | None = None


@dataclass
class ActionRecordResponse:
    """Response for action aspect."""

    action_id: str
    action: str
    success: bool
    message: str
    reversible: bool
    git_stash_ref: str | None
    timestamp: str | None


# =============================================================================
# Rollback Window Aspect
# =============================================================================


@dataclass
class RollbackWindowRequest:
    """Request for rollback aspect."""

    hours: int = 168  # 7 days
    limit: int = 100
    reversible_only: bool = True


@dataclass
class RollbackActionItem:
    """A single action in the rollback response."""

    action_id: str
    action: str
    success: bool
    reversible: bool
    inverse_action: str | None
    timestamp: str | None


@dataclass
class RollbackWindowResponse:
    """Response for rollback aspect."""

    hours: int
    count: int
    actions: list[RollbackActionItem] = field(default_factory=list)


# =============================================================================
# Escalate Aspect
# =============================================================================


@dataclass
class EscalateRequest:
    """Request for escalate aspect."""

    git_email: str
    from_level: int
    to_level: int
    reason: str = "Manual escalation"


@dataclass
class EscalateResponse:
    """Response for escalate aspect."""

    escalation_id: int
    from_level: str  # TrustLevel name
    to_level: str  # TrustLevel name
    reason: str
    timestamp: str | None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Manifest
    "WitnessManifestResponse",
    # Thoughts
    "ThoughtsRequest",
    "ThoughtsResponse",
    "ThoughtItem",
    # Trust
    "TrustRequest",
    "TrustResponse",
    # Capture
    "CaptureThoughtRequest",
    "CaptureThoughtResponse",
    # Action
    "ActionRecordRequest",
    "ActionRecordResponse",
    # Rollback
    "RollbackWindowRequest",
    "RollbackWindowResponse",
    "RollbackActionItem",
    # Escalate
    "EscalateRequest",
    "EscalateResponse",
]
