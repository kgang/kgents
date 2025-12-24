"""
Witness schemas for Crystal system.

Defines frozen dataclass contracts and versioned schemas for all Witness data:
- witness.mark: Atomic unit of witnessed behavior
- witness.trust: Trust levels with decay tracking
- witness.thought: Thought stream observations
- witness.action: Concrete actions with rollback info
- witness.escalation: Trust level change audit trail

Based on models in models/witness.py but using immutable contracts.
"""

from dataclasses import dataclass, field
from typing import Any

from ..crystal import Schema


# =============================================================================
# WitnessMark - The atomic unit of witnessed behavior
# =============================================================================


@dataclass(frozen=True)
class WitnessMark:
    """
    A Mark in the Witness ledger (v1).

    Marks are immutable records of witnessed behavior:
    - Every action leaves a mark
    - Marks are immutable once created
    - Marks can have reasoning and principles
    - Marks can have tags for categorization and querying

    Evidence Tag Taxonomy:
    - spec:{path}        — Mark relates to a spec
    - evidence:impl      — Implementation evidence
    - evidence:test      — Test evidence
    - evidence:usage     — Usage evidence
    - evidence:run       — Test run record
    - evidence:pass      — Test passed
    - evidence:fail      — Test failed
    - eureka, gotcha, taste, friction, joy, veto — Session tags
    """

    action: str
    """What was done."""

    reasoning: str
    """Why it was done (optional but encouraged)."""

    author: str = "system"
    """Who created this mark."""

    tags: tuple[str, ...] = ()
    """Classification tags (includes evidence tags)."""

    principles: tuple[str, ...] = ()
    """Which principles were honored."""

    parent_mark_id: str | None = None
    """Parent mark for causal lineage."""

    context: dict[str, Any] = field(default_factory=dict)
    """Additional context metadata."""


WITNESS_MARK_SCHEMA = Schema(
    name="witness.mark",
    version=1,
    contract=WitnessMark,
)


# =============================================================================
# WitnessTrust - Trust level with decay
# =============================================================================


@dataclass(frozen=True)
class WitnessTrust:
    """
    Trust level for a git user in a repository (v1).

    Trust is earned through consistent, valuable observations:
    - L0 READ_ONLY: 0 (default)
    - L1 BOUNDED: 1 (can write to .kgents/)
    - L2 SUGGESTION: 2 (can propose changes)
    - L3 AUTONOMOUS: 3 (full developer agency)

    Trust decays over inactivity:
    - 0.1 levels per 24h of inactivity
    - Minimum floor: L1 (never drops below L1 after first achievement)
    """

    trustor_id: str
    """Who is granting trust (typically system or repo)."""

    trustee_id: str
    """Who is receiving trust (git email hash)."""

    level: str
    """Trust level: 'none', 'limited', 'standard', 'elevated', 'full'."""

    domain: str = "general"
    """Trust domain (e.g., 'general', 'code', 'tests', 'docs')."""

    granted_capabilities: tuple[str, ...] = ()
    """Specific capabilities granted at this level."""

    trust_level_raw: float = 0.0
    """Raw trust level for decay calculations."""

    observation_count: int = 0
    """Number of observations made."""

    successful_operations: int = 0
    """Number of successful operations."""

    confirmed_suggestions: int = 0
    """Number of confirmed suggestions."""

    total_suggestions: int = 0
    """Total suggestions made."""


WITNESS_TRUST_SCHEMA = Schema(
    name="witness.trust",
    version=1,
    contract=WitnessTrust,
)


# =============================================================================
# WitnessThought - Thought stream observations
# =============================================================================


@dataclass(frozen=True)
class WitnessThought:
    """
    A thought in the thought stream (v1).

    Thoughts are observations crystallized from events.
    Dual-track: SQL for recency queries, D-gent for semantic search.

    The thought stream is both a semantic corpus (for pattern detection)
    and a temporal log (for recent thoughts display).
    """

    content: str
    """The thought content."""

    source: str
    """Where the thought came from (git, tests, ci, etc.)."""

    tags: tuple[str, ...] = ()
    """Classification tags."""

    trust_id: str | None = None
    """Associated trust record ID."""

    context: dict[str, Any] = field(default_factory=dict)
    """Additional context metadata."""


WITNESS_THOUGHT_SCHEMA = Schema(
    name="witness.thought",
    version=1,
    contract=WitnessThought,
)


# =============================================================================
# WitnessAction - Concrete actions with rollback
# =============================================================================


@dataclass(frozen=True)
class WitnessAction:
    """
    An action executed by the Witness (v1).

    All actions are logged and (ideally) reversible.
    Rollback info is stored for 7 days.
    """

    action: str
    """The action that was taken."""

    success: bool
    """Whether the action succeeded."""

    target: str | None = None
    """What the action targeted."""

    message: str = ""
    """Action result message."""

    reversible: bool = True
    """Whether this action can be rolled back."""

    inverse_action: str | None = None
    """The inverse action for rollback."""

    trust_id: str | None = None
    """Associated trust record ID."""

    rollback_info: dict[str, Any] = field(default_factory=dict)
    """Rollback information (git stash ref, checkpoint path, etc.)."""

    context: dict[str, Any] = field(default_factory=dict)
    """Additional context metadata."""


WITNESS_ACTION_SCHEMA = Schema(
    name="witness.action",
    version=1,
    contract=WitnessAction,
)


# =============================================================================
# WitnessEscalation - Trust escalation audit trail
# =============================================================================


@dataclass(frozen=True)
class WitnessEscalation:
    """
    Audit trail for trust escalation events (v1).

    Records every trust level change for accountability.
    """

    trust_id: str
    """The trust record being escalated."""

    from_level: int
    """Previous trust level."""

    to_level: int
    """New trust level."""

    reason: str
    """Why the escalation occurred."""

    observation_count: int = 0
    """Observations at time of escalation."""

    successful_operations: int = 0
    """Successful operations at time of escalation."""

    confirmed_suggestions: int = 0
    """Confirmed suggestions at time of escalation."""

    total_suggestions: int = 0
    """Total suggestions at time of escalation."""

    acceptance_rate: float = 0.0
    """Acceptance rate at time of escalation."""

    context: dict[str, Any] = field(default_factory=dict)
    """Additional context metadata."""


WITNESS_ESCALATION_SCHEMA = Schema(
    name="witness.escalation",
    version=1,
    contract=WitnessEscalation,
)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Contracts
    "WitnessMark",
    "WitnessTrust",
    "WitnessThought",
    "WitnessAction",
    "WitnessEscalation",
    # Schemas
    "WITNESS_MARK_SCHEMA",
    "WITNESS_TRUST_SCHEMA",
    "WITNESS_THOUGHT_SCHEMA",
    "WITNESS_ACTION_SCHEMA",
    "WITNESS_ESCALATION_SCHEMA",
]
