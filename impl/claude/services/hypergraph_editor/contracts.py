"""
Hypergraph Editor Contracts - AGENTESE type contracts for BE/FE sync.

These dataclasses define the request/response contracts for the editor node.
The AGENTESE contract protocol generates TypeScript types from these at build time.

See: docs/skills/agentese-contract-protocol.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# =============================================================================
# Perception Contracts (Responses Only)
# =============================================================================


@dataclass(frozen=True)
class EditorStateResponse:
    """Response for editor state aspect."""

    mode: str  # EditorMode enum name
    focus_path: str  # AGENTESE path of focused node
    trail_length: int  # Navigation history depth
    has_kblock: bool  # Is there an active K-Block?
    selection_count: int  # Number of selected nodes (VISUAL mode)
    kblock_id: str | None = None  # Active K-Block ID if present
    command_buffer: str = ""  # COMMAND mode buffer


# =============================================================================
# Navigation Contracts
# =============================================================================


@dataclass(frozen=True)
class NavigateRequest:
    """Request to navigate via edge type."""

    edge_type: str  # "parent", "child", "next_sibling", "prev_sibling", "definition", "reference"
    from_path: str | None = None  # If None, navigate from current focus


@dataclass(frozen=True)
class NavigateResponse:
    """Response from navigation operation."""

    success: bool
    new_focus: str | None = None  # AGENTESE path of new focus
    message: str = ""
    edge_type: str = ""
    error: str | None = None


@dataclass(frozen=True)
class FocusRequest:
    """Request to focus a specific node by AGENTESE path."""

    path: str  # AGENTESE path to focus


@dataclass(frozen=True)
class FocusResponse:
    """Response from focus operation."""

    success: bool
    focused_path: str | None = None
    message: str = ""
    error: str | None = None


# =============================================================================
# Mode Contracts
# =============================================================================


@dataclass(frozen=True)
class ModeRequest:
    """Request to enter a mode."""

    mode: str  # EditorMode enum name: "NORMAL", "INSERT", "VISUAL", etc.


@dataclass(frozen=True)
class ModeResponse:
    """Response from mode change."""

    success: bool
    mode: str  # Current mode after operation
    message: str = ""
    error: str | None = None


# =============================================================================
# Command Contracts
# =============================================================================


@dataclass(frozen=True)
class CommandRequest:
    """Request to execute an editor command."""

    command: str  # Command text (AGENTESE path or ex command)
    args: dict[str, Any] | None = None  # Optional command arguments


@dataclass(frozen=True)
class CommandResponse:
    """Response from command execution."""

    success: bool
    output: str = ""  # Command output
    result: dict[str, Any] | None = None  # Structured result if applicable
    error: str | None = None


# =============================================================================
# Affordances Contract
# =============================================================================


@dataclass(frozen=True)
class AffordancesRequest:
    """Request for available affordances from current focus."""

    from_path: str | None = None  # If None, use current focus


@dataclass(frozen=True)
class AffordancesResponse:
    """Response with available edge types and counts."""

    affordances: dict[str, int]  # {edge_type: destination_count}
    focus_path: str


# =============================================================================
# Selection Contracts (VISUAL mode)
# =============================================================================


@dataclass(frozen=True)
class SelectionRequest:
    """Request to modify selection."""

    action: str  # "add", "remove", "toggle", "clear", "extend"
    paths: list[str] | None = None  # Paths to operate on
    direction: str | None = None  # For "extend" action


@dataclass(frozen=True)
class SelectionResponse:
    """Response from selection modification."""

    success: bool
    selected_paths: list[str]  # Current selection
    count: int
    message: str = ""
    error: str | None = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Perception
    "EditorStateResponse",
    # Navigation
    "NavigateRequest",
    "NavigateResponse",
    "FocusRequest",
    "FocusResponse",
    # Mode
    "ModeRequest",
    "ModeResponse",
    # Command
    "CommandRequest",
    "CommandResponse",
    # Affordances
    "AffordancesRequest",
    "AffordancesResponse",
    # Selection
    "SelectionRequest",
    "SelectionResponse",
]
