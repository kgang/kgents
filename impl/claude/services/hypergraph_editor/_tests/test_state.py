"""
Tests for EditorState and navigation primitives.

Verifies the laws:
    - Trail Monotonicity: navigate increases or maintains trail length
    - Backtrack Inverse: backtrack(navigate(s, e)).focus = s.focus
    - Affordance Soundness: if affordances shows an edge, navigate can follow it
"""

import pytest

from protocols.exploration.types import ContextNode, Observer, Trail
from services.hypergraph_editor.core.state import (
    EditorMode,
    EditorState,
    affordances,
    backtrack,
    create_initial_state,
    enter_mode,
    exit_mode,
    extend_selection,
    navigate,
    toggle_selection,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_observer() -> Observer:
    """Create a test observer."""
    return Observer(
        id="test_observer",
        archetype="developer",
        capabilities=frozenset({"read", "write", "navigate"}),
    )


@pytest.fixture
def mock_node_a() -> ContextNode:
    """Create a test node A."""
    return ContextNode(
        path="world.module_a",
        holon="module_a",
    )


@pytest.fixture
def mock_node_b() -> ContextNode:
    """Create a test node B."""
    return ContextNode(
        path="world.module_b",
        holon="module_b",
    )


@pytest.fixture
def initial_state(mock_node_a: ContextNode, mock_observer: Observer) -> EditorState:
    """Create an initial editor state."""
    return create_initial_state(
        focus=mock_node_a,
        observer=mock_observer,
    )


# =============================================================================
# EditorState Tests
# =============================================================================


def test_editor_state_immutable(initial_state: EditorState) -> None:
    """EditorState is frozen (immutable)."""
    with pytest.raises(Exception):  # FrozenInstanceError
        initial_state.mode = EditorMode.INSERT  # type: ignore


def test_editor_state_properties(initial_state: EditorState) -> None:
    """EditorState properties work correctly."""
    assert initial_state.is_dirty is False
    assert initial_state.has_selection is False
    assert initial_state.trail_length == 1  # Initial step


def test_with_methods_return_new_state(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """with_* methods return new EditorState instances."""
    new_state = initial_state.with_focus(mock_node_b)

    assert new_state is not initial_state
    assert new_state.focus == mock_node_b
    assert initial_state.focus != mock_node_b  # Original unchanged


def test_with_cursor(initial_state: EditorState) -> None:
    """with_cursor updates cursor position."""
    new_state = initial_state.with_cursor(10, 5)

    assert new_state.cursor_line == 10
    assert new_state.cursor_col == 5
    assert initial_state.cursor_line == 0  # Original unchanged


# =============================================================================
# Navigation Tests (Law Verification)
# =============================================================================


@pytest.mark.asyncio
async def test_navigate_increases_trail_length(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """Law: Trail Monotonicity - navigate increases trail length."""

    # Mock the follow method to return destination
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    initial_state.focus.follow = mock_follow  # type: ignore

    initial_length = initial_state.trail_length
    new_state = await navigate(initial_state, "implements")

    # Law: Trail length must increase
    assert new_state.trail_length > initial_length
    assert new_state.trail_length == initial_length + 1


@pytest.mark.asyncio
async def test_navigate_updates_focus(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """navigate updates focus to destination node."""

    # Mock the follow method
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    initial_state.focus.follow = mock_follow  # type: ignore

    new_state = await navigate(initial_state, "implements")

    assert new_state.focus == mock_node_b
    assert new_state.focus != initial_state.focus


@pytest.mark.asyncio
async def test_navigate_no_edges_raises(initial_state: EditorState) -> None:
    """navigate raises ValueError when edge not available."""

    # Mock the follow method to return empty list
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return []

    initial_state.focus.follow = mock_follow  # type: ignore
    initial_state.focus.edges = lambda obs: {}  # type: ignore

    with pytest.raises(ValueError, match="No .* edges available"):
        await navigate(initial_state, "nonexistent")


@pytest.mark.asyncio
async def test_affordances_returns_edge_counts(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """affordances returns dictionary of edge types and counts."""

    # Mock the edges method
    def mock_edges(observer: Observer) -> dict[str, list[ContextNode]]:
        return {
            "implements": [mock_node_b],
            "tests": [mock_node_b, mock_node_b],  # 2 destinations
            "depends_on": [],  # No destinations
        }

    initial_state.focus.edges = mock_edges  # type: ignore

    affs = await affordances(initial_state)

    assert affs == {
        "implements": 1,
        "tests": 2,
        "depends_on": 0,
    }


@pytest.mark.asyncio
async def test_affordance_soundness(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """Law: Affordance Soundness - if affordances shows edge, navigate succeeds."""

    # Mock both edges and follow
    def mock_edges(observer: Observer) -> dict[str, list[ContextNode]]:
        return {"implements": [mock_node_b]}

    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    initial_state.focus.edges = mock_edges  # type: ignore
    initial_state.focus.follow = mock_follow  # type: ignore

    affs = await affordances(initial_state)

    # If affordance shows an edge exists, navigate should succeed
    for edge_type, count in affs.items():
        if count > 0:
            new_state = await navigate(initial_state, edge_type)
            assert new_state.focus == mock_node_b  # Successfully navigated


def test_backtrack_reduces_trail_length(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """Law: Backtrack reduces trail length by 1."""
    # Manually build a state with longer trail
    trail_with_steps = initial_state.trail.add_step(
        node=mock_node_b.path,
        edge_taken="implements",
    )
    state_with_trail = initial_state.with_trail(trail_with_steps).with_focus(mock_node_b)

    initial_length = state_with_trail.trail_length
    new_state = backtrack(state_with_trail)

    # Law: Trail length decreases by 1
    assert new_state.trail_length == initial_length - 1


def test_backtrack_empty_trail_raises(initial_state: EditorState) -> None:
    """backtrack raises ValueError when trail is too short."""
    with pytest.raises(ValueError, match="Cannot backtrack"):
        backtrack(initial_state)


@pytest.mark.asyncio
async def test_backtrack_inverse_law(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """Law: Backtrack Inverse - backtrack(navigate(s, e)).focus approximates s.focus."""

    # Mock the follow method
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    initial_state.focus.follow = mock_follow  # type: ignore

    # Navigate forward
    navigated = await navigate(initial_state, "implements")
    assert navigated.focus == mock_node_b

    # Backtrack
    backtracked = backtrack(navigated)

    # Law: Focus should return to original path
    assert backtracked.focus.path == initial_state.focus.path


# =============================================================================
# Mode Transition Tests
# =============================================================================


def test_enter_mode_changes_mode(initial_state: EditorState) -> None:
    """enter_mode transitions to new mode."""
    new_state = enter_mode(initial_state, EditorMode.INSERT)

    assert new_state.mode == EditorMode.INSERT
    assert initial_state.mode == EditorMode.NORMAL  # Original unchanged


def test_enter_mode_clears_selection_when_not_visual(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """enter_mode clears selection when leaving VISUAL mode."""
    # Create state with selection
    state_with_selection = initial_state.with_selection(frozenset({mock_node_b}))

    # Enter INSERT mode (not VISUAL)
    new_state = enter_mode(state_with_selection, EditorMode.INSERT)

    assert new_state.mode == EditorMode.INSERT
    assert len(new_state.selection) == 0  # Selection cleared


def test_enter_visual_mode_preserves_selection(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """enter_mode preserves selection when entering VISUAL mode."""
    state_with_selection = initial_state.with_selection(frozenset({mock_node_b}))

    new_state = enter_mode(state_with_selection, EditorMode.VISUAL)

    assert new_state.mode == EditorMode.VISUAL
    assert len(new_state.selection) == 1  # Selection preserved


def test_exit_mode_returns_to_normal(initial_state: EditorState) -> None:
    """exit_mode always returns to NORMAL."""
    insert_state = enter_mode(initial_state, EditorMode.INSERT)
    exited = exit_mode(insert_state)

    assert exited.mode == EditorMode.NORMAL


def test_exit_mode_idempotent_on_normal(initial_state: EditorState) -> None:
    """Law: Idempotence - exit_mode(NORMAL) = NORMAL."""
    exited = exit_mode(initial_state)

    assert exited.mode == EditorMode.NORMAL
    assert initial_state.mode == EditorMode.NORMAL


def test_exit_mode_clears_selection(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """Law: Selection Clear - exiting clears selection."""
    state_with_selection = initial_state.with_selection(frozenset({mock_node_b}))
    exited = exit_mode(state_with_selection)

    assert len(exited.selection) == 0


# =============================================================================
# Selection Tests
# =============================================================================


def test_toggle_selection_adds_node(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """toggle_selection adds node if not in selection."""
    new_state = toggle_selection(initial_state, mock_node_b)

    assert mock_node_b in new_state.selection
    assert mock_node_b not in initial_state.selection


def test_toggle_selection_removes_node(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """toggle_selection removes node if already in selection."""
    state_with_node = toggle_selection(initial_state, mock_node_b)
    toggled_again = toggle_selection(state_with_node, mock_node_b)

    assert mock_node_b not in toggled_again.selection


def test_toggle_selection_idempotent(initial_state: EditorState, mock_node_b: ContextNode) -> None:
    """Law: Idempotence - toggle(toggle(s, n), n) = s."""
    once = toggle_selection(initial_state, mock_node_b)
    twice = toggle_selection(once, mock_node_b)

    assert twice.selection == initial_state.selection


@pytest.mark.asyncio
async def test_extend_selection_adds_destination(
    initial_state: EditorState, mock_node_b: ContextNode
) -> None:
    """extend_selection adds destination to selection."""

    # Mock the follow method
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    initial_state.focus.follow = mock_follow  # type: ignore

    new_state = await extend_selection(initial_state, "implements")

    assert mock_node_b in new_state.selection


@pytest.mark.asyncio
async def test_extend_selection_preserves_existing(
    initial_state: EditorState, mock_node_a: ContextNode, mock_node_b: ContextNode
) -> None:
    """extend_selection preserves existing selection."""
    # Start with node_a in selection
    state_with_selection = initial_state.with_selection(frozenset({mock_node_a}))

    # Mock follow to return node_b
    async def mock_follow(edge_type: str, observer: Observer) -> list[ContextNode]:
        return [mock_node_b]

    state_with_selection.focus.follow = mock_follow  # type: ignore

    new_state = await extend_selection(state_with_selection, "implements")

    # Both nodes should be in selection
    assert mock_node_a in new_state.selection
    assert mock_node_b in new_state.selection


# =============================================================================
# Factory Tests
# =============================================================================


def test_create_initial_state(mock_node_a: ContextNode, mock_observer: Observer) -> None:
    """create_initial_state creates valid initial state."""
    state = create_initial_state(
        focus=mock_node_a,
        observer=mock_observer,
    )

    assert state.mode == EditorMode.NORMAL
    assert state.focus == mock_node_a
    assert state.observer == mock_observer
    assert len(state.selection) == 0
    assert state.kblock is None
    assert state.cursor_line == 0
    assert state.cursor_col == 0
    assert state.trail_length == 1  # Initial step


def test_create_initial_state_trail_contains_focus(
    mock_node_a: ContextNode, mock_observer: Observer
) -> None:
    """create_initial_state creates trail with focus as first step."""
    state = create_initial_state(
        focus=mock_node_a,
        observer=mock_observer,
    )

    assert len(state.trail.steps) == 1
    assert state.trail.steps[0].node == mock_node_a.path
    assert state.trail.steps[0].edge_taken is None  # No edge for first step
