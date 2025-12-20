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
# Invoke Aspect (Cross-Jewel Invocation)
# =============================================================================


@dataclass
class InvokeRequest:
    """Request for invoke aspect (cross-jewel invocation)."""

    path: str  # AGENTESE path to invoke (e.g., "world.gestalt.analyze")
    kwargs: dict[str, Any] = field(default_factory=dict)  # Arguments for the aspect


@dataclass
class InvokeResponse:
    """Response for invoke aspect."""

    path: str
    success: bool
    result: Any | None
    error: str | None
    gate_decision: str | None  # GateDecision name
    timestamp: str | None


# =============================================================================
# Pipeline Aspect (Cross-Jewel Pipeline)
# =============================================================================


@dataclass
class PipelineStepItem:
    """A single step definition in a pipeline request."""

    path: str
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRequest:
    """Request for pipeline aspect (cross-jewel pipeline)."""

    steps: list[PipelineStepItem] = field(default_factory=list)


@dataclass
class PipelineStepResultItem:
    """Result of a single step in pipeline execution."""

    step_index: int
    path: str
    success: bool
    result: Any | None
    error: str | None
    duration_ms: float


@dataclass
class PipelineResponse:
    """Response for pipeline aspect."""

    status: str  # PipelineStatus name
    success: bool
    step_results: list[PipelineStepResultItem] = field(default_factory=list)
    final_result: Any | None = None
    error: str | None = None
    total_duration_ms: float = 0.0
    aborted_at_step: int | None = None


# =============================================================================
# Crystallize Aspect (time.witness)
# =============================================================================


@dataclass
class CrystallizeRequest:
    """Request for crystallize aspect - trigger experience crystallization."""

    session_id: str = ""  # Optional session ID for grouping
    markers: list[str] = field(default_factory=list)  # User markers for this crystal
    force: bool = False  # Force crystallization even if threshold not met


@dataclass
class CrystalItem:
    """A crystal summary for list responses."""

    crystal_id: str
    session_id: str
    thought_count: int
    started_at: str | None
    ended_at: str | None
    duration_minutes: float | None
    topics: list[str]
    mood_brightness: float
    mood_dominant_quality: str
    narrative_summary: str
    crystallized_at: str


@dataclass
class CrystallizeResponse:
    """Response for crystallize aspect."""

    crystal_id: str
    session_id: str
    thought_count: int
    topics: list[str]
    mood: dict[str, float]  # MoodVector as dict
    narrative_summary: str
    crystallized_at: str


@dataclass
class TimelineRequest:
    """Request for timeline aspect - get crystallization timeline."""

    limit: int = 20
    since: str | None = None  # ISO datetime
    session_id: str | None = None  # Filter by session


@dataclass
class TimelineResponse:
    """Response for timeline aspect."""

    count: int
    crystals: list[CrystalItem] = field(default_factory=list)


@dataclass
class CrystalQueryRequest:
    """Request for crystal aspect - retrieve specific crystal."""

    crystal_id: str | None = None  # By ID
    session_id: str | None = None  # By session
    topics: list[str] = field(default_factory=list)  # Filter by topics


@dataclass
class CrystalQueryResponse:
    """Response for crystal aspect - full crystal detail."""

    found: bool
    crystal: CrystalItem | None = None
    thoughts: list[ThoughtItem] = field(default_factory=list)
    topology: dict[str, Any] = field(default_factory=dict)
    mood: dict[str, float] = field(default_factory=dict)
    narrative: dict[str, Any] = field(default_factory=dict)


@dataclass
class TerritoryRequest:
    """Request for territory aspect - codebase heat map."""

    session_id: str | None = None  # Filter by session
    hours: int = 24  # Time window


@dataclass
class TerritoryResponse:
    """Response for territory aspect - codebase activity map."""

    primary_path: str
    heat: dict[str, float]  # Path → activity level
    total_crystals: int
    time_window_hours: int


@dataclass
class AttuneRequest:
    """Request for attune aspect - start observation session."""

    session_name: str = ""
    context: str = ""


@dataclass
class AttuneResponse:
    """Response for attune aspect."""

    session_id: str
    started_at: str
    attuned: bool


@dataclass
class MarkRequest:
    """Request for mark aspect - create user marker."""

    content: str
    tags: list[str] = field(default_factory=list)


@dataclass
class MarkResponse:
    """Response for mark aspect."""

    marker_id: str
    content: str
    tags: list[str]
    timestamp: str


# =============================================================================
# Schedule Aspect (Temporal Composition)
# =============================================================================


@dataclass
class ScheduleRequest:
    """Request for schedule aspect (scheduling future invocations)."""

    path: str  # AGENTESE path to invoke
    delay_seconds: int | None = None  # Delay from now in seconds
    at_iso: str | None = None  # ISO datetime for scheduled execution
    name: str = ""  # Human-readable name
    description: str = ""  # Task description
    kwargs: dict[str, Any] = field(default_factory=dict)  # Arguments for invocation


@dataclass
class SchedulePeriodicRequest:
    """Request for scheduling periodic invocations."""

    path: str  # AGENTESE path to invoke
    interval_seconds: int  # Interval between invocations
    name: str = ""  # Human-readable name
    description: str = ""  # Task description
    max_runs: int | None = None  # Maximum number of runs
    start_immediately: bool = False  # Start first run immediately
    kwargs: dict[str, Any] = field(default_factory=dict)  # Arguments for invocation


@dataclass
class ScheduleResponse:
    """Response for schedule aspect."""

    task_id: str
    name: str
    path: str
    schedule_type: str  # ScheduleType name
    next_run_iso: str
    status: str  # ScheduleStatus name
    interval_seconds: int | None = None
    max_runs: int | None = None


@dataclass
class ScheduleListRequest:
    """Request for listing scheduled tasks."""

    status_filter: str | None = None  # Filter by status name
    limit: int = 50


@dataclass
class ScheduleListResponse:
    """Response for listing scheduled tasks."""

    count: int
    tasks: list[ScheduleResponse] = field(default_factory=list)


@dataclass
class ScheduleCancelRequest:
    """Request for cancelling a scheduled task."""

    task_id: str


@dataclass
class ScheduleCancelResponse:
    """Response for cancelling a scheduled task."""

    task_id: str
    cancelled: bool
    message: str = ""


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
    # Invoke (Cross-Jewel)
    "InvokeRequest",
    "InvokeResponse",
    # Pipeline (Cross-Jewel)
    "PipelineRequest",
    "PipelineStepItem",
    "PipelineResponse",
    "PipelineStepResultItem",
    # Schedule (Temporal Composition)
    "ScheduleRequest",
    "SchedulePeriodicRequest",
    "ScheduleResponse",
    "ScheduleListRequest",
    "ScheduleListResponse",
    "ScheduleCancelRequest",
    "ScheduleCancelResponse",
    # Crystallize (time.witness)
    "CrystallizeRequest",
    "CrystallizeResponse",
    "CrystalItem",
    "TimelineRequest",
    "TimelineResponse",
    "CrystalQueryRequest",
    "CrystalQueryResponse",
    "TerritoryRequest",
    "TerritoryResponse",
    "AttuneRequest",
    "AttuneResponse",
    "MarkRequest",
    "MarkResponse",
]
