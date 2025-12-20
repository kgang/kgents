"""
Presence Contracts: Type definitions for self.presence operations.

CLI v7 Phase 3: Agent Presence

These contracts define request/response types for presence operations,
following Pattern #13 (Contract-First Types).

Enables type safety between Python backend and TypeScript frontend
for real-time agent presence features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Manifest (Presence Overview)
# =============================================================================


@dataclass
class PresenceManifestResponse:
    """Response for presence manifest aspect."""

    active_count: int
    cursors: list[dict[str, Any]]
    phase: str  # Circadian phase
    tempo_modifier: float
    subscriber_count: int


# =============================================================================
# Cursor State
# =============================================================================


@dataclass
class CursorGetRequest:
    """Request to get a specific cursor."""

    agent_id: str


@dataclass
class CursorGetResponse:
    """Response for cursor get."""

    found: bool
    cursor: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class CursorUpdateRequest:
    """Request to update cursor state."""

    agent_id: str
    state: str | None = None  # CursorState name
    activity: str | None = None
    focus_path: str | None = None


@dataclass
class CursorUpdateResponse:
    """Response for cursor update."""

    success: bool
    cursor: dict[str, Any] | None = None
    error: str | None = None


# =============================================================================
# Join/Leave
# =============================================================================


@dataclass
class JoinRequest:
    """Request to join presence channel."""

    agent_id: str
    display_name: str
    initial_state: str = "WAITING"
    activity: str = "Joining..."


@dataclass
class JoinResponse:
    """Response for join request."""

    success: bool
    cursor: dict[str, Any] | None = None
    active_count: int = 0
    error: str | None = None


@dataclass
class LeaveRequest:
    """Request to leave presence channel."""

    agent_id: str


@dataclass
class LeaveResponse:
    """Response for leave request."""

    success: bool
    was_present: bool = False
    active_count: int = 0


# =============================================================================
# Snapshot
# =============================================================================


@dataclass
class SnapshotResponse:
    """Response for presence snapshot."""

    cursors: list[dict[str, Any]]
    count: int
    phase: str
    tempo_modifier: float


# =============================================================================
# Circadian Info
# =============================================================================


@dataclass
class CircadianResponse:
    """Response for circadian phase info."""

    phase: str
    tempo_modifier: float
    warmth: float
    hour: int


# =============================================================================
# States Info
# =============================================================================


@dataclass
class StatesResponse:
    """Response listing all cursor states."""

    states: list[dict[str, Any]]  # Each with name, emoji, color, description


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Manifest
    "PresenceManifestResponse",
    # Cursor
    "CursorGetRequest",
    "CursorGetResponse",
    "CursorUpdateRequest",
    "CursorUpdateResponse",
    # Join/Leave
    "JoinRequest",
    "JoinResponse",
    "LeaveRequest",
    "LeaveResponse",
    # Snapshot
    "SnapshotResponse",
    # Circadian
    "CircadianResponse",
    # States
    "StatesResponse",
]
