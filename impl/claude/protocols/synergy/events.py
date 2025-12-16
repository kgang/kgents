"""
Synergy Events: Cross-jewel communication event types.

Foundation 4 of the Enlightened Crown strategy.
When jewels complete operations, they emit events that other jewels can respond to.

Example:
    ✓ Gestalt analysis complete
    ↳ Synergy: Architecture snapshot captured to Brain
    ↳ Crystal: "gestalt-impl-claude-2025-12-16"
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SynergyEventType(Enum):
    """
    Known synergy event types.

    Each event type represents a significant jewel operation
    that other jewels might want to respond to.
    """

    # Gestalt events
    ANALYSIS_COMPLETE = "analysis_complete"
    HEALTH_COMPUTED = "health_computed"
    DRIFT_DETECTED = "drift_detected"

    # Brain events
    CRYSTAL_FORMED = "crystal_formed"
    MEMORY_SURFACED = "memory_surfaced"
    VAULT_IMPORTED = "vault_imported"

    # Gardener events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETE = "session_complete"
    ARTIFACT_CREATED = "artifact_created"
    LEARNING_RECORDED = "learning_recorded"
    # Wave 4: Garden-specific events
    SEASON_CHANGED = "season_changed"
    GESTURE_APPLIED = "gesture_applied"
    PLOT_PROGRESS_UPDATED = "plot_progress_updated"

    # Atelier events
    PIECE_CREATED = "piece_created"
    BID_ACCEPTED = "bid_accepted"

    # Coalition events
    COALITION_FORMED = "coalition_formed"
    TASK_ASSIGNED = "task_assigned"

    # Domain events (Wave 3)
    DRILL_STARTED = "drill_started"
    DRILL_COMPLETE = "drill_complete"
    TIMER_WARNING = "timer_warning"
    TIMER_CRITICAL = "timer_critical"
    TIMER_EXPIRED = "timer_expired"

    # Park events (Wave 3)
    SCENARIO_STARTED = "scenario_started"
    SCENARIO_COMPLETE = "scenario_complete"
    SERENDIPITY_INJECTED = "serendipity_injected"
    CONSENT_DEBT_HIGH = "consent_debt_high"
    FORCE_USED = "force_used"

    # D-gent events (Data layer)
    DATA_STORED = "data_stored"       # Datum stored to backend
    DATA_DELETED = "data_deleted"     # Datum removed from backend
    DATA_UPGRADED = "data_upgraded"   # Datum promoted to higher tier
    DATA_DEGRADED = "data_degraded"   # Datum demoted (graceful degradation)


class Jewel(Enum):
    """Crown Jewel identifiers."""

    BRAIN = "brain"
    GESTALT = "gestalt"
    GARDENER = "gardener"
    ATELIER = "atelier"
    COALITION = "coalition"
    PARK = "park"
    DOMAIN = "domain"

    # Infrastructure jewels
    DGENT = "dgent"  # Data layer (D-gent)

    # Special: broadcast target
    ALL = "*"


@dataclass
class SynergyEvent:
    """
    Event payload for cross-jewel communication.

    Synergy events flow between jewels automatically:
    - Gestalt analysis → Brain captures architecture snapshot
    - Gardener session complete → Brain captures learnings
    - Atelier piece created → Brain captures creation metadata
    """

    source_jewel: Jewel
    target_jewel: Jewel
    event_type: SynergyEventType
    source_id: str  # ID of the source artifact (analysis ID, crystal ID, session ID)
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_jewel": self.source_jewel.value,
            "target_jewel": self.target_jewel.value,
            "event_type": self.event_type.value,
            "source_id": self.source_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynergyEvent":
        """Create from dictionary."""
        return cls(
            source_jewel=Jewel(data["source_jewel"]),
            target_jewel=Jewel(data["target_jewel"]),
            event_type=SynergyEventType(data["event_type"]),
            source_id=data["source_id"],
            payload=data.get("payload", {}),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if isinstance(data.get("timestamp"), str)
                else datetime.now()
            ),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
        )


@dataclass
class SynergyResult:
    """Result of handling a synergy event."""

    success: bool
    handler_name: str
    message: str = ""
    artifact_id: str | None = None  # ID of created artifact (e.g., crystal ID)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "handler_name": self.handler_name,
            "message": self.message,
            "artifact_id": self.artifact_id,
            "metadata": self.metadata,
        }


# Factory functions for common events


def create_analysis_complete_event(
    source_id: str,
    module_count: int,
    health_grade: str,
    average_health: float,
    drift_count: int,
    root_path: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gestalt analysis complete event."""
    return SynergyEvent(
        source_jewel=Jewel.GESTALT,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.ANALYSIS_COMPLETE,
        source_id=source_id,
        payload={
            "module_count": module_count,
            "health_grade": health_grade,
            "average_health": average_health,
            "drift_count": drift_count,
            "root_path": root_path,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_drift_detected_event(
    source_id: str,
    source_module: str,
    target_module: str,
    rule: str,
    severity: str,
    root_path: str,
    message: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Gestalt drift detected event.

    Sprint 2: Auto-capture drift violations to Brain for tracking.

    Args:
        source_id: Unique violation identifier
        source_module: Module that violates the rule
        target_module: Module being incorrectly depended on
        rule: Name of the governance rule violated
        severity: error, warning, info
        root_path: Root path being analyzed
        message: Optional descriptive message

    Returns:
        SynergyEvent for DRIFT_DETECTED
    """
    return SynergyEvent(
        source_jewel=Jewel.GESTALT,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.DRIFT_DETECTED,
        source_id=source_id,
        payload={
            "source_module": source_module,
            "target_module": target_module,
            "rule": rule,
            "severity": severity,
            "root_path": root_path,
            "message": message or f"{source_module} → {target_module} violates {rule}",
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_crystal_formed_event(
    crystal_id: str,
    content_preview: str,
    content_type: str = "text",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Brain crystal formed event."""
    return SynergyEvent(
        source_jewel=Jewel.BRAIN,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CRYSTAL_FORMED,
        source_id=crystal_id,
        payload={
            "content_preview": content_preview[:100],
            "content_type": content_type,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_session_complete_event(
    session_id: str,
    session_name: str,
    artifacts_count: int,
    learnings: list[str],
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gardener session complete event."""
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.SESSION_COMPLETE,
        source_id=session_id,
        payload={
            "session_name": session_name,
            "artifacts_count": artifacts_count,
            "learnings": learnings,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_artifact_created_event(
    artifact_id: str,
    artifact_type: str,
    path: str | None,
    description: str,
    session_id: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Gardener artifact created event."""
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.ARTIFACT_CREATED,
        source_id=artifact_id,
        payload={
            "artifact_type": artifact_type,
            "path": path,
            "description": description,
            "session_id": session_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Wave 2: Atelier Events
# =============================================================================


def create_piece_created_event(
    piece_id: str,
    piece_type: str,
    title: str,
    builder_id: str,
    session_id: str,
    spectator_count: int = 0,
    bid_count: int = 0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create an Atelier piece created event.

    When a builder completes a piece in the Atelier, this event
    triggers auto-capture to Brain for memory persistence.

    Args:
        piece_id: Unique identifier for the piece
        piece_type: Type of artifact (code, art, writing, etc.)
        title: Human-readable title
        builder_id: ID of the builder who created it
        session_id: Atelier session ID
        spectator_count: Number of spectators watching
        bid_count: Number of spectator bids accepted

    Returns:
        SynergyEvent for PIECE_CREATED
    """
    return SynergyEvent(
        source_jewel=Jewel.ATELIER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.PIECE_CREATED,
        source_id=piece_id,
        payload={
            "piece_type": piece_type,
            "title": title,
            "builder_id": builder_id,
            "session_id": session_id,
            "spectator_count": spectator_count,
            "bid_count": bid_count,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_bid_accepted_event(
    bid_id: str,
    session_id: str,
    spectator_id: str,
    bid_type: str,
    content: str,
    tokens_spent: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create an Atelier bid accepted event.

    When a builder accepts a spectator bid, this event can
    trigger notifications or capture the interaction.
    """
    return SynergyEvent(
        source_jewel=Jewel.ATELIER,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.BID_ACCEPTED,
        source_id=bid_id,
        payload={
            "session_id": session_id,
            "spectator_id": spectator_id,
            "bid_type": bid_type,
            "content": content,
            "tokens_spent": tokens_spent,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Wave 2: Coalition Events
# =============================================================================


def create_coalition_formed_event(
    coalition_id: str,
    task_template: str,
    archetypes: list[str],
    eigenvector_compatibility: float,
    estimated_credits: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Coalition formed event.

    When a coalition forms to execute a task, this event
    notifies other jewels for context enrichment.
    """
    return SynergyEvent(
        source_jewel=Jewel.COALITION,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.COALITION_FORMED,
        source_id=coalition_id,
        payload={
            "task_template": task_template,
            "archetypes": archetypes,
            "eigenvector_compatibility": eigenvector_compatibility,
            "estimated_credits": estimated_credits,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_task_complete_event(
    task_id: str,
    coalition_id: str,
    task_template: str,
    output_format: str,
    output_summary: str,
    credits_spent: int,
    handoffs: int,
    duration_seconds: float,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Coalition task complete event.

    When a coalition completes a task, this event triggers
    auto-capture to Brain for historical tracking.
    """
    return SynergyEvent(
        source_jewel=Jewel.COALITION,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.TASK_ASSIGNED,  # Reuse for completion
        source_id=task_id,
        payload={
            "coalition_id": coalition_id,
            "task_template": task_template,
            "output_format": output_format,
            "output_summary": output_summary,
            "credits_spent": credits_spent,
            "handoffs": handoffs,
            "duration_seconds": duration_seconds,
            "completed": True,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Wave 3: Domain Events
# =============================================================================


def create_drill_complete_event(
    drill_id: str,
    drill_type: str,
    drill_name: str,
    difficulty: str,
    team_size: int,
    duration_seconds: float,
    outcome: str,
    score: int,
    grade: str,
    timer_outcomes: dict[str, Any] | None = None,
    decisions: list[dict[str, Any]] | None = None,
    recommendations: list[str] | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Domain drill complete event.

    When an enterprise drill completes, this event triggers
    auto-capture to Brain for compliance documentation.

    Args:
        drill_id: Unique drill instance identifier
        drill_type: Type of drill (service_outage, data_breach, etc.)
        drill_name: Human-readable drill name
        difficulty: easy, medium, hard
        team_size: Number of participants
        duration_seconds: Drill duration
        outcome: success, partial_success, failure
        score: 0-100 performance score
        grade: A+, A, B+, B, etc.
        timer_outcomes: Dict of timer name → status/elapsed
        decisions: List of key decision records
        recommendations: List of improvement recommendations

    Returns:
        SynergyEvent for DRILL_COMPLETE
    """
    return SynergyEvent(
        source_jewel=Jewel.DOMAIN,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.DRILL_COMPLETE,
        source_id=drill_id,
        payload={
            "drill_type": drill_type,
            "drill_name": drill_name,
            "difficulty": difficulty,
            "team_size": team_size,
            "duration_seconds": duration_seconds,
            "outcome": outcome,
            "score": score,
            "grade": grade,
            "timer_outcomes": timer_outcomes or {},
            "decisions": decisions or [],
            "recommendations": recommendations or [],
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_drill_started_event(
    drill_id: str,
    drill_type: str,
    drill_name: str,
    team_size: int,
    timers: list[str],
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Domain drill started event."""
    return SynergyEvent(
        source_jewel=Jewel.DOMAIN,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.DRILL_STARTED,
        source_id=drill_id,
        payload={
            "drill_type": drill_type,
            "drill_name": drill_name,
            "team_size": team_size,
            "timers": timers,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_timer_warning_event(
    timer_id: str,
    timer_name: str,
    drill_id: str,
    remaining_seconds: float,
    progress: float,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a timer warning event (approaching deadline)."""
    return SynergyEvent(
        source_jewel=Jewel.DOMAIN,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TIMER_WARNING,
        source_id=timer_id,
        payload={
            "timer_name": timer_name,
            "drill_id": drill_id,
            "remaining_seconds": remaining_seconds,
            "progress": progress,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Wave 3: Park Events
# =============================================================================


def create_scenario_complete_event(
    session_id: str,
    scenario_name: str,
    scenario_type: str,
    duration_seconds: float,
    consent_debt_final: float,
    forces_used: int,
    key_moments: list[dict[str, Any]] | None = None,
    feedback: dict[str, Any] | None = None,
    skill_changes: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Park scenario complete event.

    When an INHABIT session completes, this event triggers
    auto-capture to Brain for learning tracking.

    Args:
        session_id: Unique session identifier
        scenario_name: Human-readable scenario name
        scenario_type: mystery, collaboration, conflict, emergence, practice
        duration_seconds: Session duration
        consent_debt_final: Final consent debt level [0, 1]
        forces_used: Number of force mechanics used (max 3)
        key_moments: List of significant moment records
        feedback: K-gent feedback analysis
        skill_changes: Dict of skill → before/after levels

    Returns:
        SynergyEvent for SCENARIO_COMPLETE
    """
    return SynergyEvent(
        source_jewel=Jewel.PARK,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.SCENARIO_COMPLETE,
        source_id=session_id,
        payload={
            "scenario_name": scenario_name,
            "scenario_type": scenario_type,
            "duration_seconds": duration_seconds,
            "consent_debt_final": consent_debt_final,
            "forces_used": forces_used,
            "key_moments": key_moments or [],
            "feedback": feedback or {},
            "skill_changes": skill_changes or {},
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_serendipity_injected_event(
    injection_id: str,
    session_id: str,
    injection_type: str,
    description: str,
    intensity: float,
    tension_level: float,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Park serendipity injection event."""
    return SynergyEvent(
        source_jewel=Jewel.PARK,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.SERENDIPITY_INJECTED,
        source_id=injection_id,
        payload={
            "session_id": session_id,
            "injection_type": injection_type,
            "description": description,
            "intensity": intensity,
            "tension_level": tension_level,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_force_used_event(
    force_id: str,
    session_id: str,
    target_citizen: str,
    request: str,
    consent_debt_before: float,
    consent_debt_after: float,
    forces_remaining: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Park force mechanic used event."""
    return SynergyEvent(
        source_jewel=Jewel.PARK,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.FORCE_USED,
        source_id=force_id,
        payload={
            "session_id": session_id,
            "target_citizen": target_citizen,
            "request": request,
            "consent_debt_before": consent_debt_before,
            "consent_debt_after": consent_debt_after,
            "forces_remaining": forces_remaining,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Wave 4: Garden Events (Gardener-Logos Phase 6)
# =============================================================================


def create_season_changed_event(
    garden_id: str,
    garden_name: str,
    old_season: str,
    new_season: str,
    reason: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a garden season changed event.

    When the garden transitions to a new season, this event broadcasts
    to all jewels so they can adapt their behavior.

    Args:
        garden_id: Unique garden identifier
        garden_name: Human-readable garden name
        old_season: Previous season name (e.g., "DORMANT")
        new_season: New season name (e.g., "SPROUTING")
        reason: Why the transition occurred

    Returns:
        SynergyEvent for SEASON_CHANGED (broadcast to ALL)
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.ALL,  # Broadcast to all jewels
        event_type=SynergyEventType.SEASON_CHANGED,
        source_id=garden_id,
        payload={
            "garden_name": garden_name,
            "old_season": old_season,
            "new_season": new_season,
            "reason": reason,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_gesture_applied_event(
    garden_id: str,
    gesture_verb: str,
    target: str,
    success: bool,
    state_changed: bool,
    synergies_triggered: list[str],
    tone: float = 0.5,
    reasoning: str = "",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a garden gesture applied event.

    When a tending gesture is applied to the garden, this event
    notifies Brain for auto-capture of significant changes.

    Args:
        garden_id: Unique garden identifier
        gesture_verb: The verb (OBSERVE, PRUNE, GRAFT, WATER, ROTATE, WAIT)
        target: AGENTESE path that was tended
        success: Whether the gesture succeeded
        state_changed: Whether garden state was modified
        synergies_triggered: List of triggered synergy effects
        tone: Gesture tone (0=tentative, 1=definitive)
        reasoning: Why this gesture was applied

    Returns:
        SynergyEvent for GESTURE_APPLIED (to Brain)
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.GESTURE_APPLIED,
        source_id=garden_id,
        payload={
            "verb": gesture_verb,
            "target": target,
            "success": success,
            "state_changed": state_changed,
            "synergies_triggered": synergies_triggered,
            "tone": tone,
            "reasoning": reasoning,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_plot_progress_event(
    garden_id: str,
    plot_name: str,
    plot_path: str,
    old_progress: float,
    new_progress: float,
    plan_path: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a plot progress updated event.

    When a plot's progress changes (e.g., from Forest Protocol
    plan updates), this event notifies Brain for tracking.

    Args:
        garden_id: Garden containing the plot
        plot_name: Human-readable plot name
        plot_path: AGENTESE path (e.g., "world.forge")
        old_progress: Previous progress (0-1)
        new_progress: New progress (0-1)
        plan_path: Optional linked plan file path

    Returns:
        SynergyEvent for PLOT_PROGRESS_UPDATED (to Brain)
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.PLOT_PROGRESS_UPDATED,
        source_id=garden_id,
        payload={
            "plot_name": plot_name,
            "plot_path": plot_path,
            "old_progress": old_progress,
            "new_progress": new_progress,
            "plan_path": plan_path,
            "progress_delta": new_progress - old_progress,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# D-gent Events (Data Layer)
# =============================================================================


def create_data_stored_event(
    datum_id: str,
    content_preview: str,
    content_size: int,
    backend_tier: str,
    has_parent: bool = False,
    metadata: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a D-gent data stored event.

    When data is persisted to a backend, this event notifies
    other jewels that new data is available.

    Args:
        datum_id: Unique datum identifier
        content_preview: First 100 chars/bytes of content
        content_size: Size of content in bytes
        backend_tier: Storage tier (MEMORY, JSONL, SQLITE, POSTGRES)
        has_parent: Whether datum has causal parent
        metadata: Optional datum metadata

    Returns:
        SynergyEvent for DATA_STORED
    """
    return SynergyEvent(
        source_jewel=Jewel.DGENT,
        target_jewel=Jewel.ALL,  # Broadcast to all
        event_type=SynergyEventType.DATA_STORED,
        source_id=datum_id,
        payload={
            "content_preview": content_preview[:100] if content_preview else "",
            "content_size": content_size,
            "backend_tier": backend_tier,
            "has_parent": has_parent,
            "metadata": metadata or {},
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_data_deleted_event(
    datum_id: str,
    backend_tier: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a D-gent data deleted event.

    When data is removed from a backend, this event notifies
    other jewels that the data is no longer available.

    Args:
        datum_id: ID of deleted datum
        backend_tier: Storage tier the datum was in

    Returns:
        SynergyEvent for DATA_DELETED
    """
    return SynergyEvent(
        source_jewel=Jewel.DGENT,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.DATA_DELETED,
        source_id=datum_id,
        payload={
            "backend_tier": backend_tier,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_data_upgraded_event(
    datum_id: str,
    old_tier: str,
    new_tier: str,
    reason: str = "access_pattern",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a D-gent data upgraded event.

    When data is promoted to a higher durability tier,
    this event tracks the progression.

    Args:
        datum_id: ID of upgraded datum
        old_tier: Previous storage tier
        new_tier: New storage tier (more durable)
        reason: Why the upgrade occurred

    Returns:
        SynergyEvent for DATA_UPGRADED
    """
    return SynergyEvent(
        source_jewel=Jewel.DGENT,
        target_jewel=Jewel.BRAIN,  # Brain tracks tier changes
        event_type=SynergyEventType.DATA_UPGRADED,
        source_id=datum_id,
        payload={
            "old_tier": old_tier,
            "new_tier": new_tier,
            "reason": reason,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_data_degraded_event(
    datum_id: str,
    old_tier: str,
    new_tier: str,
    reason: str = "graceful_degradation",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a D-gent data degraded event.

    When data falls back to a lower tier (e.g., Postgres unavailable),
    this event tracks the graceful degradation.

    Args:
        datum_id: ID of degraded datum
        old_tier: Previous storage tier
        new_tier: New storage tier (less durable)
        reason: Why the degradation occurred

    Returns:
        SynergyEvent for DATA_DEGRADED
    """
    return SynergyEvent(
        source_jewel=Jewel.DGENT,
        target_jewel=Jewel.ALL,  # All jewels should know about degradation
        event_type=SynergyEventType.DATA_DEGRADED,
        source_id=datum_id,
        payload={
            "old_tier": old_tier,
            "new_tier": new_tier,
            "reason": reason,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


__all__ = [
    # Event types
    "SynergyEventType",
    "Jewel",
    # Data classes
    "SynergyEvent",
    "SynergyResult",
    # Factory functions - Wave 0/1
    "create_analysis_complete_event",
    "create_drift_detected_event",  # Sprint 2
    "create_crystal_formed_event",
    "create_session_complete_event",
    "create_artifact_created_event",
    # Factory functions - Wave 2: Atelier
    "create_piece_created_event",
    "create_bid_accepted_event",
    # Factory functions - Wave 2: Coalition
    "create_coalition_formed_event",
    "create_task_complete_event",
    # Factory functions - Wave 3: Domain
    "create_drill_complete_event",
    "create_drill_started_event",
    "create_timer_warning_event",
    # Factory functions - Wave 3: Park
    "create_scenario_complete_event",
    "create_serendipity_injected_event",
    "create_force_used_event",
    # Factory functions - Wave 4: Garden (Phase 6)
    "create_season_changed_event",
    "create_gesture_applied_event",
    "create_plot_progress_event",
    # Factory functions - D-gent (Data layer)
    "create_data_stored_event",
    "create_data_deleted_event",
    "create_data_upgraded_event",
    "create_data_degraded_event",
]
