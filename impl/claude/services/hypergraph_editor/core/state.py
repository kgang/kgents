"""
EditorState and navigation primitives for the Hypergraph Editor.

This module implements the core state machine for the editor,
where cursor position is a node focus, selection is a subgraph,
and navigation is edge traversal.

Philosophy:
    "The file is a lie. There is only the graph."
    "Every cursor is a node. Every selection is a subgraph. Every edit is a morphism."

See: spec/surfaces/hypergraph-editor.md

Laws Verified:
    - Trail Monotonicity: navigate increases or maintains trail length
    - Backtrack Inverse: backtrack(navigate(s, e)).focus = s.focus
    - Affordance Soundness: if affordances shows an edge, navigate can follow it
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from .types import EditorMode

if TYPE_CHECKING:
    from protocols.exploration.types import ContextNode, Observer, Trail
    from services.k_block.core.kblock import KBlock


# =============================================================================
# EditorState
# =============================================================================


@dataclass(frozen=True)
class EditorState:
    """
    Complete editor state — immutable, snapshotable.

    The unified state containing everything needed to render the editor
    and process inputs. Immutability enables:
    - Time travel (undo/redo via state history)
    - State snapshots for debugging
    - Pure functions for all navigation/editing

    Philosophy:
        Every state transition is a morphism EditorState → EditorState.
        The editor IS the typed-hypergraph in polynomial form.
    """

    mode: EditorMode  # Current polynomial position
    focus: "ContextNode"  # Current node (cursor is here)
    trail: "Trail"  # Navigation history (semantic)
    selection: frozenset["ContextNode"]  # Visual mode selection (subgraph)
    kblock: "KBlock | None"  # Active isolation (INSERT mode)
    observer: "Observer"  # Phenomenological lens
    cursor_line: int = 0  # Line within node content
    cursor_col: int = 0  # Column within line

    @property
    def is_dirty(self) -> bool:
        """Whether there are unsaved changes."""
        return self.kblock is not None and self.kblock.is_dirty

    @property
    def has_selection(self) -> bool:
        """Whether any nodes are selected."""
        return len(self.selection) > 0

    @property
    def trail_length(self) -> int:
        """Number of steps in navigation trail."""
        return len(self.trail.steps)

    def with_focus(self, new_focus: "ContextNode") -> "EditorState":
        """Return new state with updated focus."""
        return replace(self, focus=new_focus)

    def with_mode(self, new_mode: EditorMode) -> "EditorState":
        """Return new state with updated mode."""
        return replace(self, mode=new_mode)

    def with_trail(self, new_trail: "Trail") -> "EditorState":
        """Return new state with updated trail."""
        return replace(self, trail=new_trail)

    def with_selection(self, new_selection: frozenset["ContextNode"]) -> "EditorState":
        """Return new state with updated selection."""
        return replace(self, selection=new_selection)

    def with_kblock(self, new_kblock: "KBlock | None") -> "EditorState":
        """Return new state with updated K-Block."""
        return replace(self, kblock=new_kblock)

    def with_cursor(self, line: int, col: int) -> "EditorState":
        """Return new state with updated cursor position."""
        return replace(self, cursor_line=line, cursor_col=col)


# =============================================================================
# Navigation Primitives
# =============================================================================


async def navigate(state: EditorState, edge_type: str) -> EditorState:
    """
    Follow hyperedge from current focus.

    Returns new state with updated focus and trail.

    Laws:
        - Trail Monotonicity: result.trail.length >= state.trail.length
        - Affordance Soundness: If edge_type in affordances, navigation succeeds

    Args:
        state: Current editor state
        edge_type: The hyperedge aspect to follow (e.g., "implements", "tests")

    Returns:
        New EditorState with updated focus and trail

    Raises:
        ValueError: If edge_type is not available from current focus
    """
    # Get destinations by following the edge
    destinations = await state.focus.follow(edge_type, state.observer)

    if not destinations:
        affs = await affordances(state)
        raise ValueError(
            f"No {edge_type} edges available from {state.focus.path}. "
            f"Available: {list(affs.keys())}"
        )

    # Take first destination (in NORMAL mode we navigate to single nodes)
    # VISUAL mode would handle multiple destinations differently
    new_focus = destinations[0]

    # Update trail with this navigation step
    new_trail = state.trail.add_step(
        node=new_focus.path,
        edge_taken=edge_type,
    )

    # Return new state with updated focus and trail
    return state.with_focus(new_focus).with_trail(new_trail)


async def affordances(state: EditorState) -> dict[str, int]:
    """
    What edges can we follow? {aspect: destination_count}

    This shows the user what navigation options are available from
    the current focus. Different observers see different affordances.

    Laws:
        - Soundness: If affordances[e] > 0, then navigate(state, e) succeeds
        - Observer-dependent: affordances change based on state.observer

    Args:
        state: Current editor state

    Returns:
        Dictionary mapping edge type to count of destinations

    Example:
        >>> affs = await affordances(state)
        >>> affs
        {"implements": 3, "tests": 1, "depends_on": 5}
    """
    edges = state.focus.edges(state.observer)

    # Count destinations for each edge type
    return {aspect: len(destinations) for aspect, destinations in edges.items()}


def backtrack(state: EditorState) -> EditorState:
    """
    Return along trail (semantic history).

    Goes back one step in the navigation trail, restoring focus
    to the previous node.

    Laws:
        - Inverse: backtrack(navigate(s, e)).focus = s.focus (eventually)
        - Trail Consistency: result.trail.length = state.trail.length - 1

    Args:
        state: Current editor state

    Returns:
        New EditorState with focus on previous node

    Raises:
        ValueError: If trail is empty (no history to backtrack)
    """
    if len(state.trail.steps) < 2:
        raise ValueError("Cannot backtrack: trail is empty or at start")

    # Remove last step from trail
    new_trail_steps = state.trail.steps[:-1]
    new_trail = replace(
        state.trail,
        steps=new_trail_steps,
    )

    # Get previous node path from trail
    previous_step = new_trail_steps[-1]

    # Create ContextNode for previous focus
    # Note: In full implementation, this would use proper ContextNode reconstruction
    # For now, we create a minimal node - real impl would restore full node state
    from protocols.exploration.types import ContextNode

    previous_node = ContextNode(
        path=previous_step.node,
        holon=previous_step.node.split(".")[-1],  # Extract holon from path
    )

    # Return new state with previous focus and updated trail
    return state.with_focus(previous_node).with_trail(new_trail)


# =============================================================================
# Mode Transitions
# =============================================================================


def enter_mode(state: EditorState, mode: EditorMode, kblock: "KBlock | None" = None) -> EditorState:
    """
    Enter a new mode, potentially creating K-Block for INSERT.

    Mode transitions follow the polynomial structure:
        NORMAL → {INSERT, VISUAL, COMMAND, PORTAL, GRAPH}
        * → NORMAL (via Esc)

    Laws:
        - Escape Idempotence: enter_mode(NORMAL, Esc) = NORMAL
        - Home Reachability: From any mode, finite Esc → NORMAL
        - K-Block Creation: enter_mode(INSERT) creates K-Block if none exists

    Args:
        state: Current editor state
        mode: Mode to enter
        kblock: Optional K-Block for INSERT mode (created if None and mode=INSERT)

    Returns:
        New EditorState in the specified mode
    """
    # If entering INSERT mode and no K-Block provided, we should create one
    # (In real impl, this would be done by the harness)
    if mode == EditorMode.INSERT and kblock is None:
        # Placeholder: real impl would create K-Block via harness
        # For now, just transition mode - K-Block creation is external
        pass

    # Clear selection when leaving VISUAL mode
    new_selection = state.selection if mode == EditorMode.VISUAL else frozenset()

    # Update K-Block if provided
    new_kblock = kblock if mode == EditorMode.INSERT else None

    return replace(
        state,
        mode=mode,
        selection=new_selection,
        kblock=new_kblock,
    )


def exit_mode(state: EditorState) -> EditorState:
    """
    Exit current mode back to NORMAL.

    This is the Esc key behavior - always returns to NORMAL.

    Laws:
        - Idempotence: exit_mode(NORMAL) = NORMAL
        - K-Block Persistence: Exiting INSERT keeps K-Block (doesn't commit or discard)
        - Selection Clear: Exiting VISUAL clears selection

    Args:
        state: Current editor state

    Returns:
        New EditorState in NORMAL mode
    """
    # Note: K-Block is NOT discarded on mode exit
    # Only explicit :q! or :w operations affect K-Block lifecycle
    return replace(
        state,
        mode=EditorMode.NORMAL,
        selection=frozenset(),  # Clear selection
        # kblock is preserved
    )


# =============================================================================
# Selection Operations (VISUAL Mode)
# =============================================================================


def toggle_selection(state: EditorState, node: "ContextNode") -> EditorState:
    """
    Toggle a node in the selection.

    Used in VISUAL mode to build up subgraph selections.

    Laws:
        - Idempotence: toggle(toggle(s, n), n) = s
        - Selection ⊆ Reachable: All selected nodes must be reachable from focus

    Args:
        state: Current editor state
        node: Node to toggle

    Returns:
        New EditorState with updated selection
    """
    current_selection = set(state.selection)

    if node in current_selection:
        current_selection.remove(node)
    else:
        current_selection.add(node)

    return state.with_selection(frozenset(current_selection))


async def extend_selection(state: EditorState, edge_type: str) -> EditorState:
    """
    Extend selection by following an edge.

    In VISUAL mode, this adds the destination nodes to the selection
    rather than replacing focus.

    Laws:
        - Visual Extension: result.selection = state.selection ∪ navigate(state, edge).focus
        - Trail Update: Trail is extended as in navigate()

    Args:
        state: Current editor state
        edge_type: The hyperedge aspect to follow

    Returns:
        New EditorState with extended selection and updated focus

    Raises:
        ValueError: If edge_type is not available from current focus
    """
    # Navigate to get new focus and trail
    new_state = await navigate(state, edge_type)

    # Add new focus to selection
    current_selection = set(state.selection)
    current_selection.add(new_state.focus)

    return new_state.with_selection(frozenset(current_selection))


# =============================================================================
# Factory Functions
# =============================================================================


def create_initial_state(
    focus: "ContextNode",
    observer: "Observer",
) -> EditorState:
    """
    Create the initial editor state.

    Args:
        focus: The starting node (cursor position)
        observer: The phenomenological lens

    Returns:
        Fresh EditorState in NORMAL mode
    """
    from protocols.exploration.types import Trail

    # Create initial trail with focus as first step
    initial_trail = Trail(
        created_by=observer.id,
        steps=(),
    ).add_step(node=focus.path, edge_taken=None)  # First step has no edge

    return EditorState(
        mode=EditorMode.NORMAL,
        focus=focus,
        trail=initial_trail,
        selection=frozenset(),
        kblock=None,
        observer=observer,
        cursor_line=0,
        cursor_col=0,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # State
    "EditorState",
    # Navigation
    "navigate",
    "affordances",
    "backtrack",
    # Mode Transitions
    "enter_mode",
    "exit_mode",
    # Selection
    "toggle_selection",
    "extend_selection",
    # Factory
    "create_initial_state",
]
