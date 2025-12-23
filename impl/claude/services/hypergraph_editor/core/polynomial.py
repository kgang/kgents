"""
EditorPolynomial: Hypergraph Editor as State Machine.

The editor polynomial models editor behavior as a dynamical system:
- NORMAL: Navigate graph, select nodes
- INSERT: Edit content (K-Block isolated)
- VISUAL: Multi-node selection (subgraph)
- COMMAND: AGENTESE invocation (: prompt)
- PORTAL: Expand/collapse hyperedges
- GRAPH: Pan/zoom DAG visualization
- KBLOCK: Transactional isolation controls

The Insight (from spec/surfaces/hypergraph-editor.md):
    The editor IS the typed-hypergraph. Cursor position is a node focus.
    Selection is a subgraph. Edit operations are morphisms Doc → Doc.
    The seven modes are polynomial positions, not scattered conditionals.

Example:
    >>> poly = EDITOR_POLYNOMIAL
    >>> state, output = poly.invoke(EditorMode.NORMAL, ModeEnterInput(EditorMode.INSERT))
    >>> print(state, output)
    EditorMode.INSERT EditorOutput(success=True, message="Entered INSERT mode")

See: spec/surfaces/hypergraph-editor.md
"""

from __future__ import annotations

from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

from .types import (
    ActionInput,
    CenterInput,
    CollapseInput,
    CommandInput,
    DiscardInput,
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

# =============================================================================
# Direction Function (Mode-Dependent Valid Inputs)
# =============================================================================


def editor_directions(mode: EditorMode) -> FrozenSet[type]:
    """
    Valid inputs for each editor mode.

    This encodes the mode-dependent behavior:
    - NORMAL: Navigation and mode switching
    - INSERT: Text editing + K-Block operations (Right to Rest pattern)
    - VISUAL: Selection operations
    - COMMAND: Command entry and execution
    - PORTAL: Hyperedge expansion/collapse
    - GRAPH: Graph visualization controls
    - KBLOCK: K-Block isolation controls

    Key Pattern:
        Home State: Esc from any mode → NORMAL
        Right to Rest: INSERT mode blocks most operations except editing
    """
    match mode:
        case EditorMode.NORMAL:
            return frozenset(
                {
                    NavigateInput,
                    ModeEnterInput,
                    FollowEdgeInput,
                    SearchInput,
                    ModeExitInput,  # Esc in NORMAL is idempotent
                    type,
                    Any,
                }
            )
        case EditorMode.INSERT:
            # Right to Rest: Only editing, save, discard, or exit
            return frozenset(
                {
                    TextChangeInput,
                    ModeExitInput,
                    SaveInput,
                    DiscardInput,
                    type,
                    Any,
                }
            )
        case EditorMode.VISUAL:
            return frozenset(
                {
                    SelectExtendInput,
                    SelectToggleInput,
                    ModeExitInput,
                    ActionInput,
                    type,
                    Any,
                }
            )
        case EditorMode.COMMAND:
            return frozenset(
                {
                    CommandInput,
                    ExecuteInput,
                    ModeExitInput,
                    TabCompleteInput,
                    type,
                    Any,
                }
            )
        case EditorMode.PORTAL:
            return frozenset(
                {
                    ExpandInput,
                    CollapseInput,
                    NavigateInput,
                    ModeExitInput,
                    type,
                    Any,
                }
            )
        case EditorMode.GRAPH:
            return frozenset(
                {
                    PanInput,
                    ZoomInput,
                    CenterInput,
                    ModeExitInput,
                    type,
                    Any,
                }
            )
        case EditorMode.KBLOCK:
            return frozenset(
                {
                    SaveInput,
                    DiscardInput,
                    ModeExitInput,
                    type,
                    Any,
                }
            )
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def editor_transition(mode: EditorMode, input: Any) -> tuple[EditorMode, EditorOutput]:
    """
    Editor state transition function.

    This is the polynomial core:
    transition: Mode × Input → (NewMode, Output)

    Laws Enforced:
    - Mode Determinism: Same (mode, input) always yields same result
    - Escape Idempotence: Esc from NORMAL → NORMAL (no-op)
    - Home Reachability: Esc from any mode leads to NORMAL

    Key Patterns:
    - Right to Rest: INSERT mode rejects navigation/social inputs
    - Home State: Esc always leads back to NORMAL
    - Non-reentrant: Long-running ops (save, execute) don't accept new ops
    """

    # Universal: ModeExitInput (Esc) → NORMAL
    if isinstance(input, ModeExitInput):
        if mode == EditorMode.NORMAL:
            # Escape Idempotence
            return EditorMode.NORMAL, EditorOutput(
                mode=EditorMode.NORMAL,
                success=True,
                message="Already in NORMAL mode",
            )
        else:
            # Home Reachability
            return EditorMode.NORMAL, EditorOutput(
                mode=EditorMode.NORMAL,
                success=True,
                message=f"Exited {mode.name} mode",
                data={"from_mode": mode.name},
            )

    match mode:
        case EditorMode.NORMAL:
            if isinstance(input, NavigateInput):
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message=f"Navigated {input.direction}",
                    data={"direction": input.direction},
                )
            elif isinstance(input, ModeEnterInput):
                target = input.target_mode
                return target, EditorOutput(
                    mode=target,
                    success=True,
                    message=f"Entered {target.name} mode",
                    data={"from_mode": EditorMode.NORMAL.name},
                )
            elif isinstance(input, FollowEdgeInput):
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message=f"Followed edge: {input.edge_type or 'inferred'}",
                    data={"edge_type": input.edge_type},
                )
            elif isinstance(input, SearchInput):
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message=f"Searched for: {input.pattern}",
                    data={"pattern": input.pattern},
                )
            else:
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case EditorMode.INSERT:
            # Right to Rest: ONLY editing operations allowed
            if isinstance(input, TextChangeInput):
                return EditorMode.INSERT, EditorOutput(
                    mode=EditorMode.INSERT,
                    success=True,
                    message="Text changed",
                    data={"delta": input.delta, "position": input.position},
                )
            elif isinstance(input, SaveInput):
                # Save but stay in INSERT (non-blocking save)
                return EditorMode.INSERT, EditorOutput(
                    mode=EditorMode.INSERT,
                    success=True,
                    message="K-Block saved (witness created)",
                    data={"witness_reason": input.witness_reason},
                )
            elif isinstance(input, DiscardInput):
                # Discard and exit to NORMAL
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message="K-Block discarded",
                )
            else:
                # Reject all other inputs (Right to Rest)
                return EditorMode.INSERT, EditorOutput(
                    mode=EditorMode.INSERT,
                    success=False,
                    message="Cannot perform operation in INSERT mode (use Esc to exit)",
                )

        case EditorMode.VISUAL:
            if isinstance(input, SelectExtendInput):
                return EditorMode.VISUAL, EditorOutput(
                    mode=EditorMode.VISUAL,
                    success=True,
                    message=f"Extended selection {input.direction}",
                    data={"direction": input.direction},
                )
            elif isinstance(input, SelectToggleInput):
                return EditorMode.VISUAL, EditorOutput(
                    mode=EditorMode.VISUAL,
                    success=True,
                    message=f"Toggled node in selection: {input.node_id}",
                    data={"node_id": input.node_id},
                )
            elif isinstance(input, ActionInput):
                # Action applied, exit to NORMAL
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message=f"Action '{input.action}' applied to selection",
                    data={"action": input.action},
                )
            else:
                return EditorMode.VISUAL, EditorOutput(
                    mode=EditorMode.VISUAL,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case EditorMode.COMMAND:
            if isinstance(input, CommandInput):
                return EditorMode.COMMAND, EditorOutput(
                    mode=EditorMode.COMMAND,
                    success=True,
                    message=f"Command text: {input.text}",
                    data={"text": input.text},
                )
            elif isinstance(input, ExecuteInput):
                # Execute and exit to NORMAL
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message="Command executed",
                )
            elif isinstance(input, TabCompleteInput):
                return EditorMode.COMMAND, EditorOutput(
                    mode=EditorMode.COMMAND,
                    success=True,
                    message="Tab completion triggered",
                )
            else:
                return EditorMode.COMMAND, EditorOutput(
                    mode=EditorMode.COMMAND,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case EditorMode.PORTAL:
            if isinstance(input, ExpandInput):
                return EditorMode.PORTAL, EditorOutput(
                    mode=EditorMode.PORTAL,
                    success=True,
                    message=f"Expanded hyperedge: {input.edge_id or 'focused'}",
                    data={"edge_id": input.edge_id},
                )
            elif isinstance(input, CollapseInput):
                return EditorMode.PORTAL, EditorOutput(
                    mode=EditorMode.PORTAL,
                    success=True,
                    message=f"Collapsed hyperedge: {input.edge_id or 'focused'}",
                    data={"edge_id": input.edge_id},
                )
            elif isinstance(input, NavigateInput):
                return EditorMode.PORTAL, EditorOutput(
                    mode=EditorMode.PORTAL,
                    success=True,
                    message=f"Navigated to portal: {input.direction}",
                    data={"direction": input.direction},
                )
            else:
                return EditorMode.PORTAL, EditorOutput(
                    mode=EditorMode.PORTAL,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case EditorMode.GRAPH:
            if isinstance(input, PanInput):
                return EditorMode.GRAPH, EditorOutput(
                    mode=EditorMode.GRAPH,
                    success=True,
                    message=f"Panned {input.direction} by {input.amount}",
                    data={"direction": input.direction, "amount": input.amount},
                )
            elif isinstance(input, ZoomInput):
                zoom_type = "in" if input.delta > 0 else "out"
                return EditorMode.GRAPH, EditorOutput(
                    mode=EditorMode.GRAPH,
                    success=True,
                    message=f"Zoomed {zoom_type}",
                    data={"delta": input.delta},
                )
            elif isinstance(input, CenterInput):
                return EditorMode.GRAPH, EditorOutput(
                    mode=EditorMode.GRAPH,
                    success=True,
                    message="Centered on focused node",
                )
            else:
                return EditorMode.GRAPH, EditorOutput(
                    mode=EditorMode.GRAPH,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case EditorMode.KBLOCK:
            if isinstance(input, SaveInput):
                # Save K-Block and exit to NORMAL
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message="K-Block committed (witness created)",
                    data={"witness_reason": input.witness_reason},
                )
            elif isinstance(input, DiscardInput):
                # Discard K-Block and exit to NORMAL
                return EditorMode.NORMAL, EditorOutput(
                    mode=EditorMode.NORMAL,
                    success=True,
                    message="K-Block discarded (no side effects)",
                )
            else:
                return EditorMode.KBLOCK, EditorOutput(
                    mode=EditorMode.KBLOCK,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case _:
            return EditorMode.NORMAL, EditorOutput(
                mode=EditorMode.NORMAL,
                success=False,
                message=f"Unknown mode: {mode}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


EDITOR_POLYNOMIAL: PolyAgent[EditorMode, Any, EditorOutput] = PolyAgent(
    name="EditorPolynomial",
    positions=frozenset(EditorMode),
    _directions=editor_directions,
    _transition=editor_transition,
)
"""
The Hypergraph Editor polynomial agent.

This models editor behavior as a polynomial state machine:
- positions: 7 modes (NORMAL, INSERT, VISUAL, COMMAND, PORTAL, GRAPH, KBLOCK)
- directions: mode-dependent valid inputs
- transition: behavioral transitions with laws enforced

Key Properties:
    Mode Determinism: transition(mode, input) is deterministic
    Escape Idempotence: transition(NORMAL, Esc) = (NORMAL, noop)
    Home Reachability: From any mode, Esc → NORMAL

Key Patterns:
    Right to Rest: INSERT mode rejects most inputs (editing only)
    Home State: Esc always leads to NORMAL
    Witness Required: Saves create witness marks (no silent saves)
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Functions
    "editor_directions",
    "editor_transition",
    # Polynomial Agent
    "EDITOR_POLYNOMIAL",
]
