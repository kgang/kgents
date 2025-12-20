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
    DATA_STORED = "data_stored"  # Datum stored to backend
    DATA_DELETED = "data_deleted"  # Datum removed from backend
    DATA_UPGRADED = "data_upgraded"  # Datum promoted to higher tier
    DATA_DEGRADED = "data_degraded"  # Datum demoted (graceful degradation)

    # F-gent Flow events (Phase 1 Foundation)
    FLOW_STARTED = "flow_started"  # Any flow started (chat/research/collaboration)
    FLOW_COMPLETED = "flow_completed"  # Any flow completed
    TURN_COMPLETED = "turn_completed"  # Chat turn completed (message + response)
    HYPOTHESIS_CREATED = "hypothesis_created"  # Research branch created
    HYPOTHESIS_SYNTHESIZED = "hypothesis_synthesized"  # Research synthesis complete
    CONSENSUS_REACHED = "consensus_reached"  # Collaboration consensus
    CONTRIBUTION_POSTED = "contribution_posted"  # Blackboard contribution

    # Concept Nursery events (JIT → Garden integration)
    CONCEPT_SEEDED = "concept_seeded"  # New concept planted in nursery
    CONCEPT_GREW = "concept_grew"  # Concept advanced to new growth stage
    CONCEPT_READY = "concept_ready"  # Concept ready for promotion (UI prompt)
    CONCEPT_PROMOTED = "concept_promoted"  # Concept accepted into permanent impl

    # Witness events (8th Crown Jewel - The Witnessing Ghost)
    WITNESS_THOUGHT_CAPTURED = "witness.thought.captured"  # Thought observed and stored
    WITNESS_GIT_COMMIT = "witness.git.commit"  # Git commit detected
    WITNESS_GIT_PUSH = "witness.git.push"  # Git push detected
    WITNESS_DAEMON_STARTED = "witness.daemon.started"  # Daemon started watching
    WITNESS_DAEMON_STOPPED = "witness.daemon.stopped"  # Daemon stopped

    # Conductor events (CLI v7 Phase 1: File I/O Primitives)
    FILE_READ = "file.read"  # File read (cached for edit guard)
    FILE_EDITED = "file.edited"  # File edited via exact string replacement
    FILE_CREATED = "file.created"  # New file created

    # Presence events (CLI v7 Phase 3: Agent Cursors)
    CURSOR_UPDATED = "cursor.updated"  # Agent cursor state changed
    CURSOR_JOINED = "cursor.joined"  # Agent joined the collaborative space
    CURSOR_LEFT = "cursor.left"  # Agent left the collaborative space

    # Tooling events (U-gent Tool Infrastructure)
    TOOL_INVOKED = "tool.invoked"  # Tool execution started
    TOOL_COMPLETED = "tool.completed"  # Tool execution succeeded
    TOOL_FAILED = "tool.failed"  # Tool execution failed
    TOOL_TRUST_DENIED = "tool.trust_denied"  # Trust gate denied invocation


class Jewel(Enum):
    """Crown Jewel identifiers."""

    BRAIN = "brain"
    GESTALT = "gestalt"
    GARDENER = "gardener"
    ATELIER = "atelier"
    COALITION = "coalition"
    PARK = "park"
    DOMAIN = "domain"
    WITNESS = "witness"  # 8th Crown Jewel - The Witnessing Ghost
    CONDUCTOR = "conductor"  # 9th Crown Jewel - Conversation & File I/O
    TOOLING = "tooling"  # 10th Crown Jewel - Tool Infrastructure

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


# =============================================================================
# F-gent Flow Events (Phase 1 Foundation)
# =============================================================================


def create_flow_started_event(
    flow_id: str,
    jewel: Jewel,
    modality: str,
    session_id: str | None = None,
    config: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Flow started event.

    When a jewel starts a Flow (ChatFlow, ResearchFlow, CollaborationFlow),
    this event notifies other jewels.

    Args:
        flow_id: Unique flow identifier
        jewel: Source jewel starting the flow
        modality: Flow modality (chat, research, collaboration)
        session_id: Optional parent session ID
        config: Optional flow configuration

    Returns:
        SynergyEvent for FLOW_STARTED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.FLOW_STARTED,
        source_id=flow_id,
        payload={
            "modality": modality,
            "session_id": session_id,
            "config": config or {},
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_flow_completed_event(
    flow_id: str,
    jewel: Jewel,
    modality: str,
    duration_seconds: float,
    turns: int = 0,
    hypotheses: int = 0,
    contributions: int = 0,
    entropy_spent: float = 0.0,
    session_id: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Flow completed event.

    When a flow completes, this event triggers auto-capture to Brain.

    Args:
        flow_id: Unique flow identifier
        jewel: Source jewel that ran the flow
        modality: Flow modality (chat, research, collaboration)
        duration_seconds: Flow duration
        turns: Number of turns (chat)
        hypotheses: Number of hypotheses (research)
        contributions: Number of contributions (collaboration)
        entropy_spent: Entropy consumed
        session_id: Optional parent session ID

    Returns:
        SynergyEvent for FLOW_COMPLETED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.FLOW_COMPLETED,
        source_id=flow_id,
        payload={
            "modality": modality,
            "duration_seconds": duration_seconds,
            "turns": turns,
            "hypotheses": hypotheses,
            "contributions": contributions,
            "entropy_spent": entropy_spent,
            "session_id": session_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_turn_completed_event(
    turn_id: str,
    flow_id: str,
    jewel: Jewel,
    turn_number: int,
    user_message_preview: str,
    assistant_response_preview: str,
    tokens_in: int,
    tokens_out: int,
    latency_seconds: float,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a ChatFlow turn completed event.

    When a chat turn completes (message + response), this event
    can trigger memory capture for important exchanges.

    Args:
        turn_id: Unique turn identifier
        flow_id: Parent flow ID
        jewel: Source jewel running the chat
        turn_number: Turn number in conversation
        user_message_preview: First 100 chars of user message
        assistant_response_preview: First 100 chars of response
        tokens_in: Input tokens
        tokens_out: Output tokens
        latency_seconds: Response latency

    Returns:
        SynergyEvent for TURN_COMPLETED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.TURN_COMPLETED,
        source_id=turn_id,
        payload={
            "flow_id": flow_id,
            "turn_number": turn_number,
            "user_message_preview": user_message_preview[:100],
            "assistant_response_preview": assistant_response_preview[:100],
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_seconds": latency_seconds,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_hypothesis_created_event(
    hypothesis_id: str,
    flow_id: str,
    jewel: Jewel,
    hypothesis_content: str,
    parent_id: str | None,
    depth: int,
    promise: float,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a ResearchFlow hypothesis created event.

    When a new hypothesis branch is created, this event
    notifies other jewels for tracking.

    Args:
        hypothesis_id: Unique hypothesis identifier
        flow_id: Parent flow ID
        jewel: Source jewel running research
        hypothesis_content: The hypothesis text
        parent_id: Parent hypothesis ID (None for root)
        depth: Depth in hypothesis tree
        promise: Estimated promise (0-1)

    Returns:
        SynergyEvent for HYPOTHESIS_CREATED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.HYPOTHESIS_CREATED,
        source_id=hypothesis_id,
        payload={
            "flow_id": flow_id,
            "content": hypothesis_content[:200],
            "parent_id": parent_id,
            "depth": depth,
            "promise": promise,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_hypothesis_synthesized_event(
    synthesis_id: str,
    flow_id: str,
    jewel: Jewel,
    question: str,
    answer: str,
    confidence: float,
    hypotheses_explored: int,
    insights_count: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a ResearchFlow synthesis completed event.

    When research synthesizes into a final answer, this event
    triggers auto-capture to Brain.

    Args:
        synthesis_id: Unique synthesis identifier
        flow_id: Parent flow ID
        jewel: Source jewel
        question: Original question
        answer: Synthesized answer
        confidence: Confidence in answer (0-1)
        hypotheses_explored: Number of hypotheses explored
        insights_count: Number of insights generated

    Returns:
        SynergyEvent for HYPOTHESIS_SYNTHESIZED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.HYPOTHESIS_SYNTHESIZED,
        source_id=synthesis_id,
        payload={
            "flow_id": flow_id,
            "question": question[:200],
            "answer": answer[:500],
            "confidence": confidence,
            "hypotheses_explored": hypotheses_explored,
            "insights_count": insights_count,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_consensus_reached_event(
    decision_id: str,
    flow_id: str,
    jewel: Jewel,
    proposal_content: str,
    outcome: str,
    vote_summary: dict[str, int],
    participants: list[str],
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a CollaborationFlow consensus reached event.

    When a collaboration reaches consensus on a proposal,
    this event triggers auto-capture to Brain.

    Args:
        decision_id: Unique decision identifier
        flow_id: Parent flow ID
        jewel: Source jewel
        proposal_content: The proposal that was decided
        outcome: Decision outcome (approved, rejected, deferred)
        vote_summary: Dict of vote type -> count
        participants: List of participating agent IDs

    Returns:
        SynergyEvent for CONSENSUS_REACHED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.CONSENSUS_REACHED,
        source_id=decision_id,
        payload={
            "flow_id": flow_id,
            "proposal_content": proposal_content[:200],
            "outcome": outcome,
            "vote_summary": vote_summary,
            "participants": participants,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_contribution_posted_event(
    contribution_id: str,
    flow_id: str,
    jewel: Jewel,
    agent_id: str,
    contribution_type: str,
    content_preview: str,
    confidence: float,
    round_number: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a CollaborationFlow contribution posted event.

    When an agent posts a contribution to the blackboard,
    this event notifies other participants.

    Args:
        contribution_id: Unique contribution identifier
        flow_id: Parent flow ID
        jewel: Source jewel
        agent_id: ID of contributing agent
        contribution_type: Type (idea, critique, question, evidence, synthesis)
        content_preview: First 100 chars of content
        confidence: Contribution confidence (0-1)
        round_number: Current round

    Returns:
        SynergyEvent for CONTRIBUTION_POSTED
    """
    return SynergyEvent(
        source_jewel=jewel,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONTRIBUTION_POSTED,
        source_id=contribution_id,
        payload={
            "flow_id": flow_id,
            "agent_id": agent_id,
            "contribution_type": contribution_type,
            "content_preview": content_preview[:100],
            "confidence": confidence,
            "round_number": round_number,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Concept Nursery Events (JIT → Garden Integration)
# =============================================================================


def create_concept_seeded_event(
    handle: str,
    nursery_id: str = "default",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Concept Nursery seed planted event.

    When a new JIT concept is created, this event adds it to the nursery
    for tracking and visualization in the Gardener UI.

    Args:
        handle: AGENTESE path (e.g., "world.garden.concept")
        nursery_id: Nursery identifier (default for global nursery)

    Returns:
        SynergyEvent for CONCEPT_SEEDED
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONCEPT_SEEDED,
        source_id=handle,
        payload={
            "nursery_id": nursery_id,
            "stage": "SEED",
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_concept_grew_event(
    handle: str,
    old_stage: str,
    new_stage: str,
    usage_count: int,
    success_rate: float,
    nursery_id: str = "default",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Concept Nursery growth event.

    When a concept advances to a new stage (SEED → SPROUTING → GROWING → READY),
    this event notifies the UI to update the nursery visualization.

    Args:
        handle: AGENTESE path
        old_stage: Previous stage name
        new_stage: New stage name
        usage_count: Total invocations
        success_rate: Success rate (0-1)
        nursery_id: Nursery identifier

    Returns:
        SynergyEvent for CONCEPT_GREW
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONCEPT_GREW,
        source_id=handle,
        payload={
            "nursery_id": nursery_id,
            "old_stage": old_stage,
            "new_stage": new_stage,
            "usage_count": usage_count,
            "success_rate": success_rate,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_concept_ready_event(
    handle: str,
    usage_count: int,
    success_rate: float,
    nursery_id: str = "default",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Concept Nursery ready-for-promotion event.

    When a concept reaches READY stage, this event triggers the UI prompt
    asking the user to accept or dismiss promotion.

    Args:
        handle: AGENTESE path
        usage_count: Total invocations (should be >= threshold)
        success_rate: Success rate (should be >= threshold)
        nursery_id: Nursery identifier

    Returns:
        SynergyEvent for CONCEPT_READY (broadcast for UI)
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.ALL,  # UI needs to see this
        event_type=SynergyEventType.CONCEPT_READY,
        source_id=handle,
        payload={
            "nursery_id": nursery_id,
            "usage_count": usage_count,
            "success_rate": success_rate,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_concept_promoted_event(
    handle: str,
    usage_count: int,
    success_rate: float,
    nursery_id: str = "default",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Concept Nursery promotion accepted event.

    When a user accepts promotion, this event notifies other jewels
    that the concept is now permanent.

    Args:
        handle: AGENTESE path
        usage_count: Final invocation count
        success_rate: Final success rate
        nursery_id: Nursery identifier

    Returns:
        SynergyEvent for CONCEPT_PROMOTED (to Brain for capture)
    """
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.BRAIN,  # Brain should capture this milestone
        event_type=SynergyEventType.CONCEPT_PROMOTED,
        source_id=handle,
        payload={
            "nursery_id": nursery_id,
            "usage_count": usage_count,
            "success_rate": success_rate,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Witness Events (8th Crown Jewel - The Witnessing Ghost)
# =============================================================================


def create_witness_thought_event(
    thought_id: str,
    content: str,
    source: str,
    tags: list[str] | tuple[str, ...],
    confidence: float = 1.0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a Witness thought captured event.

    When the Witness observes developer activity and captures a thought,
    this event triggers cross-jewel handlers (e.g., auto-capture to Brain).
    """
    return SynergyEvent(
        source_jewel=Jewel.WITNESS,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.WITNESS_THOUGHT_CAPTURED,
        source_id=thought_id,
        payload={
            "content": content,
            "source": source,
            "tags": list(tags) if isinstance(tags, tuple) else tags,
            "confidence": confidence,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_witness_git_commit_event(
    commit_hash: str,
    author_email: str,
    message: str,
    files_changed: int,
    insertions: int = 0,
    deletions: int = 0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Witness git commit detected event."""
    return SynergyEvent(
        source_jewel=Jewel.WITNESS,
        target_jewel=Jewel.GARDENER,
        event_type=SynergyEventType.WITNESS_GIT_COMMIT,
        source_id=commit_hash,
        payload={
            "author_email": author_email,
            "message": message[:200],
            "files_changed": files_changed,
            "insertions": insertions,
            "deletions": deletions,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_witness_git_push_event(
    push_id: str,
    remote: str,
    branch: str,
    commits_pushed: int,
    author_email: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Witness git push detected event."""
    return SynergyEvent(
        source_jewel=Jewel.WITNESS,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.WITNESS_GIT_PUSH,
        source_id=push_id,
        payload={
            "remote": remote,
            "branch": branch,
            "commits_pushed": commits_pushed,
            "author_email": author_email,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_witness_daemon_started_event(
    daemon_id: str,
    pid: int,
    watched_paths: list[str],
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Witness daemon started event."""
    return SynergyEvent(
        source_jewel=Jewel.WITNESS,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.WITNESS_DAEMON_STARTED,
        source_id=daemon_id,
        payload={
            "pid": pid,
            "watched_paths": watched_paths,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_witness_daemon_stopped_event(
    daemon_id: str,
    pid: int,
    uptime_seconds: float,
    thoughts_captured: int = 0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a Witness daemon stopped event."""
    return SynergyEvent(
        source_jewel=Jewel.WITNESS,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.WITNESS_DAEMON_STOPPED,
        source_id=daemon_id,
        payload={
            "pid": pid,
            "uptime_seconds": uptime_seconds,
            "thoughts_captured": thoughts_captured,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Conductor Events (CLI v7 Phase 1: File I/O Primitives)
# =============================================================================


def create_file_read_event(
    path: str,
    size: int,
    lines: int,
    agent_id: str = "unknown",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a file read event.

    Emitted when a file is read and cached for subsequent edits.

    Args:
        path: File path that was read
        size: File size in bytes
        lines: Number of lines in file
        agent_id: ID of agent that performed the read
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.FILE_READ,
        source_id=path,
        payload={
            "path": path,
            "size": size,
            "lines": lines,
            "agent_id": agent_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_file_edited_event(
    path: str,
    old_size: int,
    new_size: int,
    replacements: int,
    agent_id: str = "unknown",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a file edited event.

    Emitted when a file is successfully edited via exact string replacement.

    Args:
        path: File path that was edited
        old_size: File size before edit
        new_size: File size after edit
        replacements: Number of replacements made
        agent_id: ID of agent that performed the edit
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.FILE_EDITED,
        source_id=path,
        payload={
            "path": path,
            "old_size": old_size,
            "new_size": new_size,
            "replacements": replacements,
            "size_delta": new_size - old_size,
            "agent_id": agent_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_file_created_event(
    path: str,
    size: int,
    agent_id: str = "unknown",
    artifact_type: str | None = None,
    committed: bool = False,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a file created event.

    Emitted when a new file is written to disk.

    Args:
        path: File path that was created
        size: File size in bytes
        agent_id: ID of agent that created the file
        artifact_type: Optional artifact type (code, doc, plan, test, config)
        committed: Whether the file was committed to git
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.FILE_CREATED,
        source_id=path,
        payload={
            "path": path,
            "size": size,
            "agent_id": agent_id,
            "artifact_type": artifact_type,
            "committed": committed,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Presence Events (CLI v7 Phase 3: Agent Cursors)
# =============================================================================


def create_cursor_updated_event(
    agent_id: str,
    display_name: str,
    state: str,
    focus_path: str | None = None,
    activity: str = "",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a cursor updated event.

    Emitted when an agent's cursor state changes (exploring, working, etc.).

    Args:
        agent_id: Unique agent identifier
        display_name: Human-readable agent name
        state: Cursor state (following, exploring, working, suggesting, waiting)
        focus_path: AGENTESE path being focused
        activity: Brief description of current activity
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,  # Broadcast to all UIs
        event_type=SynergyEventType.CURSOR_UPDATED,
        source_id=agent_id,
        payload={
            "agent_id": agent_id,
            "display_name": display_name,
            "state": state,
            "focus_path": focus_path,
            "activity": activity,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_cursor_joined_event(
    agent_id: str,
    display_name: str,
    behavior: str = "assistant",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a cursor joined event.

    Emitted when an agent joins the collaborative space.

    Args:
        agent_id: Unique agent identifier
        display_name: Human-readable agent name
        behavior: Agent behavior pattern (follower, explorer, assistant, autonomous)
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CURSOR_JOINED,
        source_id=agent_id,
        payload={
            "agent_id": agent_id,
            "display_name": display_name,
            "behavior": behavior,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_cursor_left_event(
    agent_id: str,
    display_name: str,
    reason: str = "disconnected",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a cursor left event.

    Emitted when an agent leaves the collaborative space.

    Args:
        agent_id: Unique agent identifier
        display_name: Human-readable agent name
        reason: Why the agent left (disconnected, completed, error)
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CURSOR_LEFT,
        source_id=agent_id,
        payload={
            "agent_id": agent_id,
            "display_name": display_name,
            "reason": reason,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Tooling Events (U-gent Tool Infrastructure)
# =============================================================================


def create_tool_invoked_event(
    execution_id: str,
    tool_name: str,
    observer_id: str | None = None,
    trust_level: int = 0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a tool invoked event.

    Emitted when a tool execution begins.

    Args:
        execution_id: Unique execution identifier
        tool_name: Name of tool being invoked
        observer_id: Optional observer/agent ID
        trust_level: Current trust level
    """
    return SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TOOL_INVOKED,
        source_id=execution_id,
        payload={
            "tool_name": tool_name,
            "observer_id": observer_id,
            "trust_level": trust_level,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_tool_completed_event(
    execution_id: str,
    tool_name: str,
    duration_ms: float,
    observer_id: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a tool completed event.

    Emitted when a tool execution succeeds.

    Args:
        execution_id: Unique execution identifier
        tool_name: Name of tool that completed
        duration_ms: Execution duration in milliseconds
        observer_id: Optional observer/agent ID
    """
    return SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TOOL_COMPLETED,
        source_id=execution_id,
        payload={
            "tool_name": tool_name,
            "duration_ms": duration_ms,
            "observer_id": observer_id,
            "success": True,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_tool_failed_event(
    execution_id: str,
    tool_name: str,
    error: str,
    duration_ms: float = 0.0,
    observer_id: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a tool failed event.

    Emitted when a tool execution fails.

    Args:
        execution_id: Unique execution identifier
        tool_name: Name of tool that failed
        error: Error message
        duration_ms: Execution duration before failure
        observer_id: Optional observer/agent ID
    """
    return SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TOOL_FAILED,
        source_id=execution_id,
        payload={
            "tool_name": tool_name,
            "error": error,
            "duration_ms": duration_ms,
            "observer_id": observer_id,
            "success": False,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_tool_trust_denied_event(
    execution_id: str,
    tool_name: str,
    required_trust: int,
    current_trust: int,
    observer_id: str | None = None,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a tool trust denied event.

    Emitted when a tool invocation is blocked by trust gate.

    Args:
        execution_id: Unique execution identifier
        tool_name: Name of tool that was denied
        required_trust: Trust level required by tool
        current_trust: Observer's current trust level
        observer_id: Optional observer/agent ID
    """
    return SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TOOL_TRUST_DENIED,
        source_id=execution_id,
        payload={
            "tool_name": tool_name,
            "required_trust": required_trust,
            "current_trust": current_trust,
            "observer_id": observer_id,
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
    # Factory functions - F-gent Flow (Phase 1)
    "create_flow_started_event",
    "create_flow_completed_event",
    "create_turn_completed_event",
    "create_hypothesis_created_event",
    "create_hypothesis_synthesized_event",
    "create_consensus_reached_event",
    "create_contribution_posted_event",
    # Factory functions - Concept Nursery (JIT → Garden)
    "create_concept_seeded_event",
    "create_concept_grew_event",
    "create_concept_ready_event",
    "create_concept_promoted_event",
    # Factory functions - Witness (8th Crown Jewel)
    "create_witness_thought_event",
    "create_witness_git_commit_event",
    "create_witness_git_push_event",
    "create_witness_daemon_started_event",
    "create_witness_daemon_stopped_event",
    # Factory functions - Conductor (CLI v7 Phase 1)
    "create_file_read_event",
    "create_file_edited_event",
    "create_file_created_event",
    # Factory functions - Presence (CLI v7 Phase 3)
    "create_cursor_updated_event",
    "create_cursor_joined_event",
    "create_cursor_left_event",
    # Factory functions - Tooling (U-gent Tool Infrastructure)
    "create_tool_invoked_event",
    "create_tool_completed_event",
    "create_tool_failed_event",
    "create_tool_trust_denied_event",
]
