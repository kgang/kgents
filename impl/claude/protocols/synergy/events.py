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

    # Brain events
    CRYSTAL_FORMED = "crystal_formed"
    MEMORY_SURFACED = "memory_surfaced"
    VAULT_IMPORTED = "vault_imported"

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

    # Conversation events (CLI v7 Phase 2: Deep Conversation)
    CONVERSATION_TURN = "conversation.turn"  # Turn added to conversation

    # Swarm events (CLI v7 Phase 6: Agent Swarms)
    SWARM_SPAWNED = "swarm.spawned"  # Agent spawned into swarm
    SWARM_DESPAWNED = "swarm.despawned"  # Agent removed from swarm
    SWARM_A2A_MESSAGE = "swarm.a2a_message"  # A2A message sent
    SWARM_HANDOFF = "swarm.handoff"  # Agent handoff occurred

    # Context events (Portal/Exploration - spec/protocols/portal-token.md)
    CONTEXT_FILES_OPENED = "context.files_opened"  # Files opened via portal expansion
    CONTEXT_FILES_CLOSED = "context.files_closed"  # Files closed via portal collapse
    CONTEXT_FOCUS_CHANGED = "context.focus_changed"  # Focus moved to new paths


class Jewel(Enum):
    """Crown Jewel identifiers."""

    BRAIN = "brain"
    WITNESS = "witness"  # 8th Crown Jewel - The Witnessing Ghost
    CONDUCTOR = "conductor"  # 9th Crown Jewel - Conversation & File I/O
    TOOLING = "tooling"  # 10th Crown Jewel - Tool Infrastructure

    # Infrastructure jewels
    DGENT = "dgent"  # Data layer (D-gent)

    # Special: broadcast target
    ALL = "*"

    # Removed 2025-12-21: GESTALT, GARDENER, COALITION, PARK, DOMAIN


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
        target_jewel=Jewel.BRAIN,  # Gardener removed, send to Brain
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


# =============================================================================
# Conversation Events (CLI v7 Phase 2: Deep Conversation)
# =============================================================================


def create_conversation_turn_event(
    session_id: str,
    turn_number: int,
    role: str,
    content_preview: str,
    agent_id: str = "unknown",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a conversation turn event.

    Emitted when a message is added to the conversation window.

    Args:
        session_id: Unique session identifier
        turn_number: Current turn count
        role: Message role (user, assistant)
        content_preview: First 100 chars of message
        agent_id: ID of agent involved
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONVERSATION_TURN,
        source_id=session_id,
        payload={
            "session_id": session_id,
            "turn_number": turn_number,
            "role": role,
            "content_preview": content_preview[:100],
            "agent_id": agent_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Swarm Events (CLI v7 Phase 6: Agent Swarms)
# =============================================================================


def create_swarm_spawned_event(
    agent_id: str,
    task: str,
    behavior: str,
    autonomy_level: int,
    spawner_id: str = "coordinator",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a swarm agent spawned event.

    Emitted when a new agent is spawned into the swarm.

    Args:
        agent_id: Unique agent identifier
        task: Task assigned to the agent
        behavior: Agent behavior pattern (FOLLOWER, EXPLORER, ASSISTANT, AUTONOMOUS)
        autonomy_level: Autonomy level (0-3)
        spawner_id: ID of spawning coordinator
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.SWARM_SPAWNED,
        source_id=agent_id,
        payload={
            "agent_id": agent_id,
            "task": task[:200],
            "behavior": behavior,
            "autonomy_level": autonomy_level,
            "spawner_id": spawner_id,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_swarm_despawned_event(
    agent_id: str,
    reason: str = "completed",
    work_summary: str = "",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a swarm agent despawned event.

    Emitted when an agent is removed from the swarm.

    Args:
        agent_id: Unique agent identifier
        reason: Why the agent was despawned (completed, error, timeout, handoff)
        work_summary: Brief summary of work completed
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.SWARM_DESPAWNED,
        source_id=agent_id,
        payload={
            "agent_id": agent_id,
            "reason": reason,
            "work_summary": work_summary[:200],
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_swarm_a2a_message_event(
    message_id: str,
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload_preview: str = "",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a swarm A2A message event.

    Emitted when agents communicate via A2A protocol.

    Args:
        message_id: Unique message identifier
        from_agent: Sending agent ID
        to_agent: Receiving agent ID (or "*" for broadcast)
        message_type: Type of message (NOTIFY, REQUEST, RESPONSE, HANDOFF)
        payload_preview: Brief preview of payload
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.SWARM_A2A_MESSAGE,
        source_id=message_id,
        payload={
            "message_id": message_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "payload_preview": payload_preview[:100],
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_swarm_handoff_event(
    handoff_id: str,
    from_agent: str,
    to_agent: str,
    context_keys: list[str],
    conversation_turns: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a swarm handoff event.

    Emitted when one agent hands off work to another.

    Args:
        handoff_id: Unique handoff identifier
        from_agent: Agent handing off
        to_agent: Agent receiving handoff
        context_keys: Keys of context data transferred
        conversation_turns: Number of conversation turns transferred
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.SWARM_HANDOFF,
        source_id=handoff_id,
        payload={
            "handoff_id": handoff_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context_keys": context_keys,
            "conversation_turns": conversation_turns,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


# =============================================================================
# Context Events (Portal/Exploration - spec/protocols/portal-token.md)
# =============================================================================


def create_context_files_opened_event(
    paths: list[str] | tuple[str, ...],
    reason: str,
    depth: int,
    parent_path: str = "",
    edge_type: str = "",
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a context files opened event.

    Emitted when portal expansion opens files for agent context.
    This enables cross-jewel awareness of what files the agent is exploring.

    Args:
        paths: File paths that were opened
        reason: Human-readable reason (e.g., "Followed [tests] from auth.py")
        depth: Nesting depth in exploration
        parent_path: Path that led to this expansion
        edge_type: The hyperedge type followed (e.g., "tests", "imports")

    Returns:
        SynergyEvent for CONTEXT_FILES_OPENED
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONTEXT_FILES_OPENED,
        source_id=parent_path or "root",
        payload={
            "paths": list(paths) if isinstance(paths, tuple) else paths,
            "reason": reason,
            "depth": depth,
            "parent_path": parent_path,
            "edge_type": edge_type,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_context_files_closed_event(
    paths: list[str] | tuple[str, ...],
    reason: str,
    depth: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a context files closed event.

    Emitted when portal collapse removes files from agent context.

    Args:
        paths: File paths that were closed
        reason: Human-readable reason
        depth: Nesting depth in exploration

    Returns:
        SynergyEvent for CONTEXT_FILES_CLOSED
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONTEXT_FILES_CLOSED,
        source_id="collapse",
        payload={
            "paths": list(paths) if isinstance(paths, tuple) else paths,
            "reason": reason,
            "depth": depth,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_context_focus_changed_event(
    paths: list[str] | tuple[str, ...],
    reason: str,
    depth: int,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """
    Create a context focus changed event.

    Emitted when agent focus moves to a new set of paths.

    Args:
        paths: New focus paths
        reason: Human-readable reason
        depth: Nesting depth

    Returns:
        SynergyEvent for CONTEXT_FOCUS_CHANGED
    """
    return SynergyEvent(
        source_jewel=Jewel.CONDUCTOR,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.CONTEXT_FOCUS_CHANGED,
        source_id="focus",
        payload={
            "paths": list(paths) if isinstance(paths, tuple) else paths,
            "reason": reason,
            "depth": depth,
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
    # Factory functions - Brain
    "create_crystal_formed_event",
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
    # Factory functions - Conversation (CLI v7 Phase 2)
    "create_conversation_turn_event",
    # Factory functions - Swarm (CLI v7 Phase 6)
    "create_swarm_spawned_event",
    "create_swarm_despawned_event",
    "create_swarm_a2a_message_event",
    "create_swarm_handoff_event",
    # Factory functions - Context (Portal/Exploration)
    "create_context_files_opened_event",
    "create_context_files_closed_event",
    "create_context_focus_changed_event",
]
