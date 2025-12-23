"""
Hypergraph Editor Core: Polynomial state machine and types.

This module exposes the EditorPolynomial state machine, which models
the editor as a dynamical system with 7 modes and mode-dependent inputs.

Usage:
    >>> from services.hypergraph_editor.core import EDITOR_POLYNOMIAL, EditorMode, ModeEnterInput
    >>> poly = EDITOR_POLYNOMIAL
    >>> state, output = poly.invoke(EditorMode.NORMAL, ModeEnterInput(EditorMode.INSERT))
    >>> print(state, output.message)
    EditorMode.INSERT "Entered INSERT mode"

See: spec/surfaces/hypergraph-editor.md
"""

from .polynomial import EDITOR_POLYNOMIAL, editor_directions, editor_transition
from .state import EditorState
from .types import (
    ActionInput,
    CenterInput,
    CollapseInput,
    CommandInput,
    DiscardInput,
    EditorInput,
    EditorMode,
    EditorOutput,
    ExecuteInput,
    ExpandInput,
    FollowEdgeInput,
    ModeEnterInput,
    ModeExitInput,
    NavigateInput,
    PanInput,
    SaveInput,
    SearchInput,
    SelectExtendInput,
    SelectToggleInput,
    TabCompleteInput,
    TextChangeInput,
    ZoomInput,
)

__all__ = [
    # Polynomial
    "EDITOR_POLYNOMIAL",
    "editor_directions",
    "editor_transition",
    # State
    "EditorState",
    # Mode
    "EditorMode",
    # Output
    "EditorOutput",
    # Input Union
    "EditorInput",
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
]
