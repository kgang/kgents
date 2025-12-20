"""
AGENTESE Conductor Contracts: Type-safe request/response definitions.

CLI v7 Phase 2: Deep Conversation

These dataclasses define the contracts for self.conductor.* aspects,
following Pattern #13 (Contract-First Types) from crown-jewel-patterns.md.

AGENTESE: self.conductor.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

# =============================================================================
# Manifest Aspect (Response only)
# =============================================================================


@dataclass
class ConductorManifestResponse:
    """Response for conductor manifest aspect."""

    active_windows: int
    strategies_available: list[str]
    windows: list[dict[str, str | int | float | bool]]  # WindowInfo items


# =============================================================================
# Snapshot Aspect
# =============================================================================


@dataclass
class SnapshotRequest:
    """Request for snapshot aspect."""

    session_id: str | None = None  # Optional - uses current if not provided


@dataclass
class SnapshotResponse:
    """Response for snapshot aspect - immutable window state."""

    turn_count: int
    total_turn_count: int
    total_tokens: int
    utilization: float
    strategy: str
    has_summary: bool
    max_turns: int
    error: str | None = None


# =============================================================================
# History Aspect
# =============================================================================


@dataclass
class HistoryRequest:
    """Request for history aspect."""

    session_id: str | None = None
    limit: int | None = None
    include_system: bool = False


@dataclass
class MessageItem:
    """A single message in conversation history."""

    role: str
    content: str
    tokens: int


@dataclass
class HistoryResponse:
    """Response for history aspect - bounded conversation messages."""

    messages: list[MessageItem]
    total: int
    window_turn_count: int
    window_total_turn_count: int
    error: str | None = None


# =============================================================================
# Summary Aspect (Get)
# =============================================================================


@dataclass
class SummaryGetRequest:
    """Request for getting conversation summary."""

    session_id: str | None = None


@dataclass
class SummaryGetResponse:
    """Response for getting conversation summary."""

    has_summary: bool
    summary: str | None
    summarized_turn_count: int
    strategy: str
    error: str | None = None


# =============================================================================
# Summary Aspect (Set)
# =============================================================================


@dataclass
class SummarySetRequest:
    """Request for setting conversation summary."""

    session_id: str | None = None
    content: str = ""


@dataclass
class SummarySetResponse:
    """Response for setting conversation summary."""

    success: bool
    summary_length: int
    has_summary: bool
    error: str | None = None


# =============================================================================
# Reset Aspect
# =============================================================================


@dataclass
class ResetRequest:
    """Request for resetting conversation window."""

    session_id: str | None = None
    preserve_system: bool = True


@dataclass
class ResetResponse:
    """Response for reset aspect."""

    success: bool
    session_id: str | None
    preserved_system: bool
    error: str | None = None


# =============================================================================
# Sessions List Aspect
# =============================================================================


@dataclass
class SessionsListRequest:
    """Request for listing sessions."""

    node_path: str | None = None
    limit: int = 20


@dataclass
class SessionInfo:
    """Information about a single session."""

    session_id: str
    node_path: str
    is_active: bool
    turn_count: int
    window: dict[str, int | float | str | bool] | None = None  # Optional window info


@dataclass
class SessionsListResponse:
    """Response for sessions list aspect."""

    sessions: list[SessionInfo]
    total: int
    error: str | None = None


# =============================================================================
# Config Aspect
# =============================================================================


@dataclass
class ConfigRequest:
    """Request for getting window configuration."""

    session_id: str | None = None


@dataclass
class ConfigResponse:
    """Response for config aspect - window configuration."""

    max_turns: int
    strategy: str
    context_window_tokens: int
    summarization_threshold: float
    has_summarizer: bool
    error: str | None = None


# =============================================================================
# Flux Aspect (Phase 7: Live Flux)
# =============================================================================


@dataclass
class FluxStatusRequest:
    """Request for flux status."""

    pass  # No parameters needed


@dataclass
class FluxStatusResponse:
    """Response for flux status - event integration state."""

    running: bool
    subscriber_count: int
    event_types_monitored: list[str]
    bridge_active: bool
    error: str | None = None


@dataclass
class FluxStartRequest:
    """Request to start flux event integration."""

    pass  # No parameters needed


@dataclass
class FluxStartResponse:
    """Response for starting flux."""

    success: bool
    was_already_running: bool
    error: str | None = None


@dataclass
class FluxStopRequest:
    """Request to stop flux event integration."""

    pass  # No parameters needed


@dataclass
class FluxStopResponse:
    """Response for stopping flux."""

    success: bool
    was_running: bool
    error: str | None = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Manifest
    "ConductorManifestResponse",
    # Snapshot
    "SnapshotRequest",
    "SnapshotResponse",
    # History
    "HistoryRequest",
    "HistoryResponse",
    "MessageItem",
    # Summary (Get)
    "SummaryGetRequest",
    "SummaryGetResponse",
    # Summary (Set)
    "SummarySetRequest",
    "SummarySetResponse",
    # Reset
    "ResetRequest",
    "ResetResponse",
    # Sessions
    "SessionsListRequest",
    "SessionsListResponse",
    "SessionInfo",
    # Config
    "ConfigRequest",
    "ConfigResponse",
    # Flux (Phase 7)
    "FluxStatusRequest",
    "FluxStatusResponse",
    "FluxStartRequest",
    "FluxStartResponse",
    "FluxStopRequest",
    "FluxStopResponse",
]
