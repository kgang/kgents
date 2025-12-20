"""
Chat AGENTESE Contract Definitions.

Defines request and response types for Chat @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, sessions, session)
- Contract() for mutation aspects (create, send, save, resume)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: plans/autopoietic-architecture.md (Phase 7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# === Manifest Response ===


@dataclass(frozen=True)
class ChatManifestResponse:
    """Chat service manifest response."""

    active_sessions: int
    persisted_sessions: int
    sessions_by_node: dict[str, int]


# === Session Types ===


@dataclass(frozen=True)
class SessionSummary:
    """Summary of a chat session for list views."""

    session_id: str
    node_path: str
    name: str | None
    turn_count: int
    state: str
    active: bool


@dataclass(frozen=True)
class SessionsResponse:
    """Response for session list aspect."""

    query: str
    count: int
    sessions: list[SessionSummary]


@dataclass(frozen=True)
class SessionMetrics:
    """Session metrics."""

    total_tokens: int | None = None
    updated_at: str | None = None


@dataclass(frozen=True)
class SessionDetailResponse:
    """Response for session detail aspect."""

    session_id: str
    node_path: str
    name: str | None
    turn_count: int
    state: str
    entropy: float
    metrics: SessionMetrics


# === Create Session ===


@dataclass(frozen=True)
class CreateSessionRequest:
    """Request to create a new chat session."""

    node_path: str = "self.soul"
    force_new: bool = False


@dataclass(frozen=True)
class CreateSessionResponse:
    """Response after creating a session."""

    session_id: str
    node_path: str
    state: str
    created: bool


# === Send Message ===


@dataclass(frozen=True)
class SendMessageRequest:
    """Request to send a message to a session."""

    message: str
    session_id: str | None = None
    node_path: str | None = None


@dataclass(frozen=True)
class SendMessageResponse:
    """Response after sending a message."""

    response: str
    session_id: str
    turn_number: int
    tokens_in: int
    tokens_out: int


# === History ===


@dataclass(frozen=True)
class TurnDetail:
    """Details of a conversation turn."""

    role: str
    content: str
    tokens_in: int
    tokens_out: int
    timestamp: str


@dataclass(frozen=True)
class HistoryRequest:
    """Request for conversation history."""

    session_id: str
    limit: int = 10


@dataclass(frozen=True)
class HistoryResponse:
    """Response for conversation history."""

    session_id: str
    turn_count: int
    turns: list[TurnDetail]


# === Save Session ===


@dataclass(frozen=True)
class SaveSessionRequest:
    """Request to save a session."""

    session_id: str
    name: str | None = None


@dataclass(frozen=True)
class SaveSessionResponse:
    """Response after saving a session."""

    saved: bool
    session_id: str
    name: str | None
    datum_id: str | None


# === Resume Session ===


@dataclass(frozen=True)
class ResumeSessionRequest:
    """Request to resume a saved session."""

    session_id: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class ResumeSessionResponse:
    """Response after resuming a session."""

    resumed: bool
    session_id: str
    node_path: str
    name: str | None
    previous_turns: int


# === Search Sessions ===


@dataclass(frozen=True)
class SearchSessionsRequest:
    """Request to search sessions."""

    query: str
    limit: int = 20


# === Get Session Request ===


@dataclass(frozen=True)
class GetSessionRequest:
    """Request to get session details."""

    session_id: str | None = None
    name: str | None = None


# === Delete Session ===


@dataclass(frozen=True)
class DeleteSessionRequest:
    """Request to delete a session."""

    session_id: str


@dataclass(frozen=True)
class DeleteSessionResponse:
    """Response after deleting a session."""

    deleted: bool
    session_id: str


# === Reset Session ===


@dataclass(frozen=True)
class ResetSessionRequest:
    """Request to reset a session."""

    session_id: str


@dataclass(frozen=True)
class ResetSessionResponse:
    """Response after resetting a session."""

    reset: bool
    session_id: str
    state: str


# === Metrics ===


@dataclass(frozen=True)
class MetricsRequest:
    """Request for metrics."""

    session_id: str | None = None


@dataclass(frozen=True)
class MetricsResponse:
    """Response for metrics."""

    total_sessions: int | None = None
    total_turns: int | None = None
    total_tokens: int | None = None
    avg_turn_tokens: float | None = None


# === Model Selection ===


@dataclass(frozen=True)
class ModelOption:
    """A selectable model option with metadata."""

    id: str  # e.g., "claude-sonnet-4-20250514"
    name: str  # e.g., "Sonnet"
    description: str  # e.g., "Balanced speed and capability"
    tier: str  # "fast", "balanced", "powerful"


@dataclass(frozen=True)
class SetModelRequest:
    """Request to set the model for a session."""

    session_id: str
    model: str  # Model ID to use


@dataclass(frozen=True)
class SetModelResponse:
    """Response after setting the model."""

    success: bool
    session_id: str
    model: str
    previous_model: str | None = None
    message: str | None = None  # Error or info message


@dataclass(frozen=True)
class GetModelsRequest:
    """Request to get available models for a session."""

    session_id: str | None = None


@dataclass(frozen=True)
class GetModelsResponse:
    """Response with available models."""

    models: list[ModelOption]
    current_model: str | None = None
    can_switch: bool = False  # Whether user can switch models


# === Context Breakdown (Teaching Mode) ===


@dataclass(frozen=True)
class ContextSegmentResponse:
    """A segment of the context window for visualization."""

    name: str  # "System", "Summary", "Working", "Available"
    tokens: int
    color: str  # Tailwind CSS class
    description: str


@dataclass(frozen=True)
class ContextBreakdownRequest:
    """Request for context breakdown (teaching mode)."""

    session_id: str


@dataclass(frozen=True)
class ContextBreakdownResponse:
    """Context window breakdown for teaching mode visualization."""

    segments: list[ContextSegmentResponse]
    total_tokens: int
    context_window: int
    utilization: float
    strategy: str
    has_summary: bool


# === Streaming ===


@dataclass(frozen=True)
class StreamMessageRequest:
    """Request to stream a message response."""

    message: str
    session_id: str | None = None
    node_path: str | None = None


@dataclass(frozen=True)
class StreamChunk:
    """
    A single chunk in a streaming response.

    Yielded via SSE as the LLM generates tokens.
    """

    content: str
    session_id: str
    turn_number: int
    is_complete: bool = False
    tokens_so_far: int = 0


@dataclass(frozen=True)
class StreamCompleteResponse:
    """
    Final message when stream completes.

    Contains aggregate metrics for the turn.
    """

    session_id: str
    turn_number: int
    full_response: str
    tokens_in: int
    tokens_out: int


# === Exports ===

__all__ = [
    # Manifest
    "ChatManifestResponse",
    # Session
    "SessionSummary",
    "SessionsResponse",
    "SessionMetrics",
    "SessionDetailResponse",
    # Create
    "CreateSessionRequest",
    "CreateSessionResponse",
    # Send
    "SendMessageRequest",
    "SendMessageResponse",
    # History
    "TurnDetail",
    "HistoryRequest",
    "HistoryResponse",
    # Save
    "SaveSessionRequest",
    "SaveSessionResponse",
    # Resume
    "ResumeSessionRequest",
    "ResumeSessionResponse",
    # Search
    "SearchSessionsRequest",
    # Get
    "GetSessionRequest",
    # Delete
    "DeleteSessionRequest",
    "DeleteSessionResponse",
    # Reset
    "ResetSessionRequest",
    "ResetSessionResponse",
    # Metrics
    "MetricsRequest",
    "MetricsResponse",
    # Model Selection
    "ModelOption",
    "SetModelRequest",
    "SetModelResponse",
    "GetModelsRequest",
    "GetModelsResponse",
    # Context Breakdown (Teaching Mode)
    "ContextSegmentResponse",
    "ContextBreakdownRequest",
    "ContextBreakdownResponse",
    # Streaming
    "StreamMessageRequest",
    "StreamChunk",
    "StreamCompleteResponse",
]
