"""
Chat schemas - Versioned data contracts for Chat Crown Jewel.

These schemas define the shape of Chat data stored in D-gent's Crystal system.
They are frozen dataclasses - immutable, typed contracts.

AGENTESE: self.data.table.crystal.*

Spec: spec/protocols/chat-web.md
"""

from dataclasses import dataclass
from agents.d.crystal.schema import Schema

__all__ = [
    "ChatSessionCrystal",
    "ChatTurnCrystal",
    "ChatCrystalCrystal",
    "ChatCheckpointCrystal",
    "CHAT_SESSION_SCHEMA",
    "CHAT_TURN_SCHEMA",
    "CHAT_CRYSTAL_SCHEMA",
    "CHAT_CHECKPOINT_SCHEMA",
]


# =============================================================================
# Chat Session Schema (chat.session v1)
# =============================================================================


@dataclass(frozen=True)
class ChatSessionCrystal:
    """
    A chat session with branching and evidence tracking.

    Sessions are the root entities for chat conversations.
    They track metadata, branching relationships, and Bayesian evidence.

    Attributes:
        session_id: Unique session identifier
        project_id: Optional project linkage
        parent_id: Parent session for forks
        fork_point: Turn number where fork occurred
        branch_name: Git-like branch name
        state: Session state ("idle", "active", "completed")
        turn_count: Number of turns in session
        context_size: Approximate token count
        evidence_json: Serialized ChatEvidence (beta distribution)
        metadata_json: Additional metadata
        is_merged: Whether this branch was merged
        merged_into: Target session if merged
        created_at: ISO 8601 timestamp
        last_active: ISO 8601 timestamp
    """

    session_id: str
    project_id: str | None = None
    parent_id: str | None = None
    fork_point: int | None = None
    branch_name: str = "main"
    state: str = "idle"
    turn_count: int = 0
    context_size: int = 0
    evidence_json: str = "{}"
    metadata_json: str = "{}"
    is_merged: bool = False
    merged_into: str | None = None
    created_at: str = ""
    last_active: str = ""


CHAT_SESSION_SCHEMA = Schema(
    name="chat.session",
    version=1,
    contract=ChatSessionCrystal,
)


# =============================================================================
# Chat Turn Schema (chat.turn v1)
# =============================================================================


@dataclass(frozen=True)
class ChatTurnCrystal:
    """
    A single conversation turn.

    Turns are the atomic units of conversation - one user message
    and one assistant response, with tool usage and evidence tracking.

    Attributes:
        turn_id: Unique turn identifier (session_id:turn_number)
        session_id: Parent session
        turn_number: Sequential turn number
        user_message: User message content
        assistant_response: Assistant response content
        user_linearity: Linearity tag for user message
        assistant_linearity: Linearity tag for assistant
        tools_json: Serialized list of tool uses
        evidence_delta_json: Serialized evidence delta
        confidence: Turn confidence score
        started_at: ISO 8601 timestamp
        completed_at: ISO 8601 timestamp
    """

    turn_id: str
    session_id: str
    turn_number: int
    user_message: str
    assistant_response: str
    user_linearity: str = "preserved"
    assistant_linearity: str = "preserved"
    tools_json: str | None = None
    evidence_delta_json: str | None = None
    confidence: float | None = None
    started_at: str = ""
    completed_at: str = ""


CHAT_TURN_SCHEMA = Schema(
    name="chat.turn",
    version=1,
    contract=ChatTurnCrystal,
)


# =============================================================================
# Chat Crystal Schema (chat.crystal v1)
# =============================================================================


@dataclass(frozen=True)
class ChatCrystalCrystal:
    """
    Crystallized session summary.

    A distilled summary of a completed session, extracted for
    future reference and retrieval.

    Attributes:
        session_id: Parent session
        title: Crystal title
        summary: Summary text
        key_decisions_json: Serialized list of decisions
        artifacts_json: Serialized list of artifacts
        final_evidence_json: Serialized final evidence state
        final_turn_count: Number of turns when crystallized
        created_at: ISO 8601 timestamp
    """

    session_id: str
    title: str
    summary: str
    key_decisions_json: str = "[]"
    artifacts_json: str = "[]"
    final_evidence_json: str = "{}"
    final_turn_count: int = 0
    created_at: str = ""


CHAT_CRYSTAL_SCHEMA = Schema(
    name="chat.crystal",
    version=1,
    contract=ChatCrystalCrystal,
)


# =============================================================================
# Chat Checkpoint Schema (chat.checkpoint v1)
# =============================================================================


@dataclass(frozen=True)
class ChatCheckpointCrystal:
    """
    Session checkpoint for K-Block rewind support.

    Checkpoints capture session state at specific points for
    time travel and branching.

    Attributes:
        checkpoint_id: Unique checkpoint identifier
        session_id: Parent session
        turn_count: Number of turns when checkpointed
        context_json: Serialized working context
        evidence_json: Serialized evidence state
        created_at: ISO 8601 timestamp
    """

    checkpoint_id: str
    session_id: str
    turn_count: int
    context_json: str = "{}"
    evidence_json: str = "{}"
    created_at: str = ""


CHAT_CHECKPOINT_SCHEMA = Schema(
    name="chat.checkpoint",
    version=1,
    contract=ChatCheckpointCrystal,
)
