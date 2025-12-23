"""
EditorPolynomial Types: Core types for the Hypergraph Editor state machine.

The editor is a polynomial agent with 7 modes (positions) and mode-dependent
inputs (directions). Each mode accepts different operations.

See: spec/surfaces/hypergraph-editor.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Editor Modes (Polynomial Positions)
# =============================================================================


class EditorMode(Enum):
    """
    Positions in the editor polynomial.

    These are interpretive frames for editor state:
    - NORMAL: Navigate graph, select nodes
    - INSERT: Edit content (K-Block isolated)
    - VISUAL: Multi-node selection (subgraph)
    - COMMAND: AGENTESE invocation (: prompt)
    - PORTAL: Expand/collapse hyperedges
    - GRAPH: Pan/zoom DAG visualization
    - KBLOCK: Transactional isolation controls
    """

    NORMAL = auto()
    INSERT = auto()
    VISUAL = auto()
    COMMAND = auto()
    PORTAL = auto()
    GRAPH = auto()
    KBLOCK = auto()


# =============================================================================
# Input Types (Directions at Each Position)
# =============================================================================


@dataclass(frozen=True)
class NavigateInput:
    """Navigate graph structure (gh/gl/gj/gk)."""

    direction: str  # "parent", "child", "next_sibling", "prev_sibling"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModeEnterInput:
    """Enter a new mode (i/v/:/e/g)."""

    target_mode: EditorMode
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModeExitInput:
    """Exit current mode (Esc)."""

    pass


@dataclass(frozen=True)
class FollowEdgeInput:
    """Follow edge under cursor (gf)."""

    edge_type: str | None = None  # If None, infer from context
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchInput:
    """Search for pattern (/pattern)."""

    pattern: str
    metadata: dict[str, Any] = field(default_factory=dict)


# INSERT mode inputs


@dataclass(frozen=True)
class TextChangeInput:
    """Edit text content (typing)."""

    delta: str
    position: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SaveInput:
    """Save K-Block (:w)."""

    witness_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscardInput:
    """Discard K-Block without saving (:q!)."""

    pass


# VISUAL mode inputs


@dataclass(frozen=True)
class SelectExtendInput:
    """Extend selection via motion."""

    direction: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SelectToggleInput:
    """Toggle node in selection."""

    node_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionInput:
    """Perform action on selection (d/y/c)."""

    action: str  # "delete", "yank", "change"
    metadata: dict[str, Any] = field(default_factory=dict)


# COMMAND mode inputs


@dataclass(frozen=True)
class CommandInput:
    """Command text entry."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecuteInput:
    """Execute command (Enter)."""

    pass


@dataclass(frozen=True)
class TabCompleteInput:
    """Tab completion (Tab)."""

    pass


# PORTAL mode inputs


@dataclass(frozen=True)
class ExpandInput:
    """Expand hyperedge (e)."""

    edge_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CollapseInput:
    """Collapse hyperedge (c)."""

    edge_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# GRAPH mode inputs


@dataclass(frozen=True)
class PanInput:
    """Pan graph view (hjkl)."""

    direction: str  # "up", "down", "left", "right"
    amount: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ZoomInput:
    """Zoom graph view (+/-)."""

    delta: float  # Positive = zoom in, negative = zoom out
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CenterInput:
    """Center on focused node (Space)."""

    pass


# =============================================================================
# Input Union Type
# =============================================================================

# Union of all input types (for type annotations)
EditorInput = (
    NavigateInput
    | ModeEnterInput
    | ModeExitInput
    | FollowEdgeInput
    | SearchInput
    | TextChangeInput
    | SaveInput
    | DiscardInput
    | SelectExtendInput
    | SelectToggleInput
    | ActionInput
    | CommandInput
    | ExecuteInput
    | TabCompleteInput
    | ExpandInput
    | CollapseInput
    | PanInput
    | ZoomInput
    | CenterInput
)


# =============================================================================
# Output Type
# =============================================================================


@dataclass(frozen=True)
class EditorOutput:
    """
    Output from editor transitions.

    Immutable output encoding result of state transition.
    """

    mode: EditorMode
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    data: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Mode
    "EditorMode",
    # Navigation Inputs
    "NavigateInput",
    "ModeEnterInput",
    "ModeExitInput",
    "FollowEdgeInput",
    "SearchInput",
    # INSERT Mode Inputs
    "TextChangeInput",
    "SaveInput",
    "DiscardInput",
    # VISUAL Mode Inputs
    "SelectExtendInput",
    "SelectToggleInput",
    "ActionInput",
    # COMMAND Mode Inputs
    "CommandInput",
    "ExecuteInput",
    "TabCompleteInput",
    # PORTAL Mode Inputs
    "ExpandInput",
    "CollapseInput",
    # GRAPH Mode Inputs
    "PanInput",
    "ZoomInput",
    "CenterInput",
    # Input Union
    "EditorInput",
    # Output
    "EditorOutput",
]
