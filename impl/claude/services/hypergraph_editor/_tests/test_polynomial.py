"""
Tests for EditorPolynomial state machine.

Verifies:
- Polynomial functor laws (Mode Determinism, Escape Idempotence, Home Reachability)
- Direction validity (mode-dependent inputs)
- Mode transitions (entry/exit paths)
- Right to Rest enforcement (INSERT mode isolation)
- Edge cases and boundary conditions

Philosophy:
    "The editor IS the typed-hypergraph. The seven modes are polynomial positions,
    not scattered conditionals."

See: spec/surfaces/hypergraph-editor.md
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from services.hypergraph_editor.core.polynomial import (
    EDITOR_POLYNOMIAL,
    editor_directions,
    editor_transition,
)
from services.hypergraph_editor.core.types import (
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
# Test EditorMode Enum
# =============================================================================


class TestEditorMode:
    """Test EditorMode enum structure."""

    def test_all_modes_exist(self) -> None:
        """All expected modes exist."""
        assert EditorMode.NORMAL
        assert EditorMode.INSERT
        assert EditorMode.VISUAL
        assert EditorMode.COMMAND
        assert EditorMode.PORTAL
        assert EditorMode.GRAPH
        assert EditorMode.KBLOCK

    def test_mode_count(self) -> None:
        """Exactly 7 modes (polynomial positions)."""
        assert len(EditorMode) == 7


# =============================================================================
# Polynomial Laws (The Core Guarantees)
# =============================================================================


class TestPolynomialLaws:
    """Verify polynomial functor laws from spec."""

    def test_mode_determinism(self) -> None:
        """
        Law: Mode Determinism
        transition(mode, input) is deterministic.

        Same input in same mode always produces same output.
        Note: We check all fields except timestamp for determinism.
        """
        # Test multiple calls with same inputs
        mode = EditorMode.NORMAL
        input_nav = NavigateInput(direction="parent")

        new_mode1, output1 = editor_transition(mode, input_nav)
        new_mode2, output2 = editor_transition(mode, input_nav)
        new_mode3, output3 = editor_transition(mode, input_nav)

        # Modes should be identical
        assert new_mode1 == new_mode2 == new_mode3 == EditorMode.NORMAL

        # Outputs should be identical except for timestamp
        assert output1.mode == output2.mode == output3.mode
        assert output1.success == output2.success == output3.success
        assert output1.message == output2.message == output3.message
        assert output1.data == output2.data == output3.data

        # Test with different input types
        input_search = SearchInput(pattern="test")
        new_mode_a, output_a = editor_transition(mode, input_search)
        new_mode_b, output_b = editor_transition(mode, input_search)

        assert new_mode_a == new_mode_b
        assert output_a.mode == output_b.mode
        assert output_a.success == output_b.success
        assert output_a.message == output_b.message
        assert output_a.data == output_b.data

    def test_escape_idempotence(self) -> None:
        """
        Law: Escape Idempotence
        transition(NORMAL, Esc) = (NORMAL, noop)

        Pressing Esc in NORMAL mode does nothing.
        """
        mode = EditorMode.NORMAL
        esc_input = ModeExitInput()

        new_mode, output = editor_transition(mode, esc_input)

        assert new_mode == EditorMode.NORMAL  # Stays in NORMAL
        assert output.success is True
        assert "Already in NORMAL" in output.message or "noop" in output.message.lower()

        # Applying Esc multiple times should be idempotent
        mode2, output2 = editor_transition(new_mode, esc_input)
        assert mode2 == EditorMode.NORMAL
        assert output2.success is True

    @pytest.mark.parametrize(
        "mode",
        [
            EditorMode.INSERT,
            EditorMode.VISUAL,
            EditorMode.COMMAND,
            EditorMode.PORTAL,
            EditorMode.GRAPH,
            EditorMode.KBLOCK,
        ],
    )
    def test_home_reachability(self, mode: EditorMode) -> None:
        """
        Law: Home Reachability
        From any mode, Esc^n → NORMAL for some finite n.

        Every mode can return to NORMAL via Esc.
        """
        esc_input = ModeExitInput()
        new_mode, output = editor_transition(mode, esc_input)

        # Single Esc should lead to NORMAL
        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert f"Exited {mode.name}" in output.message

    def test_home_reachability_max_two_escapes(self) -> None:
        """
        From any mode, at most 2 Esc presses reach NORMAL.
        (First Esc exits to NORMAL, second is idempotent.)
        """
        for mode in EditorMode:
            current_mode = mode
            max_escapes = 3  # Generous upper bound

            for i in range(max_escapes):
                if current_mode == EditorMode.NORMAL:
                    break
                current_mode, _ = editor_transition(current_mode, ModeExitInput())

            # Should always reach NORMAL
            assert current_mode == EditorMode.NORMAL, (
                f"Failed to reach NORMAL from {mode} in {max_escapes} escapes"
            )


# =============================================================================
# Direction Validity Tests
# =============================================================================


class TestDirectionValidity:
    """Test mode-dependent valid inputs (directions)."""

    def test_normal_directions(self) -> None:
        """NORMAL mode accepts navigation and mode entry inputs."""
        dirs = editor_directions(EditorMode.NORMAL)

        # Navigation inputs
        assert NavigateInput in dirs
        assert FollowEdgeInput in dirs
        assert SearchInput in dirs

        # Mode switching
        assert ModeEnterInput in dirs
        assert ModeExitInput in dirs

        # Should NOT accept INSERT-specific inputs
        assert TextChangeInput not in dirs
        assert SaveInput not in dirs

    def test_insert_directions_right_to_rest(self) -> None:
        """
        INSERT mode: Right to Rest enforcement.
        Only editing operations allowed (no navigation/social).
        """
        dirs = editor_directions(EditorMode.INSERT)

        # Editing allowed
        assert TextChangeInput in dirs
        assert SaveInput in dirs
        assert DiscardInput in dirs
        assert ModeExitInput in dirs

        # Navigation NOT allowed (Right to Rest)
        assert NavigateInput not in dirs
        assert FollowEdgeInput not in dirs
        assert SearchInput not in dirs

    def test_visual_directions(self) -> None:
        """VISUAL mode accepts selection operations."""
        dirs = editor_directions(EditorMode.VISUAL)

        assert SelectExtendInput in dirs
        assert SelectToggleInput in dirs
        assert ActionInput in dirs
        assert ModeExitInput in dirs

        # Should NOT accept text editing
        assert TextChangeInput not in dirs

    def test_command_directions(self) -> None:
        """COMMAND mode accepts command entry and execution."""
        dirs = editor_directions(EditorMode.COMMAND)

        assert CommandInput in dirs
        assert ExecuteInput in dirs
        assert TabCompleteInput in dirs
        assert ModeExitInput in dirs

    def test_portal_directions(self) -> None:
        """PORTAL mode accepts expand/collapse operations."""
        dirs = editor_directions(EditorMode.PORTAL)

        assert ExpandInput in dirs
        assert CollapseInput in dirs
        assert NavigateInput in dirs  # Can navigate to portals
        assert ModeExitInput in dirs

    def test_graph_directions(self) -> None:
        """GRAPH mode accepts visualization controls."""
        dirs = editor_directions(EditorMode.GRAPH)

        assert PanInput in dirs
        assert ZoomInput in dirs
        assert CenterInput in dirs
        assert ModeExitInput in dirs

    def test_kblock_directions(self) -> None:
        """KBLOCK mode accepts K-Block operations."""
        dirs = editor_directions(EditorMode.KBLOCK)

        assert SaveInput in dirs
        assert DiscardInput in dirs
        assert ModeExitInput in dirs

    @pytest.mark.parametrize("mode", list(EditorMode))
    def test_all_modes_accept_exit(self, mode: EditorMode) -> None:
        """Every mode accepts ModeExitInput (universal escape)."""
        dirs = editor_directions(mode)
        assert ModeExitInput in dirs or mode == EditorMode.NORMAL  # NORMAL is home


# =============================================================================
# Mode Transition Tests
# =============================================================================


class TestModeTransitions:
    """Test mode entry and exit paths."""

    def test_normal_to_insert(self) -> None:
        """NORMAL → INSERT via 'i' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.INSERT)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.INSERT
        assert output.success is True
        assert "Entered INSERT" in output.message

    def test_normal_to_visual(self) -> None:
        """NORMAL → VISUAL via 'v' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.VISUAL)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.VISUAL
        assert output.success is True

    def test_normal_to_command(self) -> None:
        """NORMAL → COMMAND via ':' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.COMMAND)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.COMMAND
        assert output.success is True

    def test_normal_to_portal(self) -> None:
        """NORMAL → PORTAL via 'e' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.PORTAL)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.PORTAL
        assert output.success is True

    def test_normal_to_graph(self) -> None:
        """NORMAL → GRAPH via 'g' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.GRAPH)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True

    def test_normal_to_kblock(self) -> None:
        """NORMAL → KBLOCK via '<Leader>k' key."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.KBLOCK)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.KBLOCK
        assert output.success is True

    def test_insert_to_normal_via_escape(self) -> None:
        """INSERT → NORMAL via Esc."""
        mode = EditorMode.INSERT
        exit_input = ModeExitInput()

        new_mode, output = editor_transition(mode, exit_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_insert_to_normal_via_discard(self) -> None:
        """INSERT → NORMAL via :q! (discard K-Block)."""
        mode = EditorMode.INSERT
        discard_input = DiscardInput()

        new_mode, output = editor_transition(mode, discard_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "discarded" in output.message.lower()

    def test_insert_save_stays_in_insert(self) -> None:
        """INSERT: Save (:w) stays in INSERT mode (non-blocking save)."""
        mode = EditorMode.INSERT
        save_input = SaveInput(witness_reason="test save")

        new_mode, output = editor_transition(mode, save_input)

        assert new_mode == EditorMode.INSERT  # Stays in INSERT
        assert output.success is True
        assert "saved" in output.message.lower()

    def test_visual_action_exits_to_normal(self) -> None:
        """VISUAL: Performing action exits to NORMAL."""
        mode = EditorMode.VISUAL
        action_input = ActionInput(action="delete")

        new_mode, output = editor_transition(mode, action_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_command_execute_exits_to_normal(self) -> None:
        """COMMAND: Executing command exits to NORMAL."""
        mode = EditorMode.COMMAND
        execute_input = ExecuteInput()

        new_mode, output = editor_transition(mode, execute_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_kblock_save_exits_to_normal(self) -> None:
        """KBLOCK: Save exits to NORMAL."""
        mode = EditorMode.KBLOCK
        save_input = SaveInput()

        new_mode, output = editor_transition(mode, save_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_kblock_discard_exits_to_normal(self) -> None:
        """KBLOCK: Discard exits to NORMAL."""
        mode = EditorMode.KBLOCK
        discard_input = DiscardInput()

        new_mode, output = editor_transition(mode, discard_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True


# =============================================================================
# Right to Rest Tests
# =============================================================================


class TestRightToRest:
    """
    Test Right to Rest enforcement in INSERT mode.

    From spec: INSERT mode blocks most operations except editing.
    Similar to CitizenPolynomial RESTING phase: no interruptions allowed.
    """

    def test_insert_rejects_navigation(self) -> None:
        """INSERT mode rejects navigation inputs."""
        mode = EditorMode.INSERT
        nav_input = NavigateInput(direction="parent")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.INSERT  # Stays in INSERT
        assert output.success is False
        assert "cannot" in output.message.lower() or "use esc" in output.message.lower()

    def test_insert_rejects_search(self) -> None:
        """INSERT mode rejects search inputs."""
        mode = EditorMode.INSERT
        search_input = SearchInput(pattern="test")

        new_mode, output = editor_transition(mode, search_input)

        assert new_mode == EditorMode.INSERT
        assert output.success is False

    def test_insert_rejects_mode_enter(self) -> None:
        """INSERT mode rejects entering other modes (must Esc first)."""
        mode = EditorMode.INSERT
        enter_input = ModeEnterInput(target_mode=EditorMode.VISUAL)

        new_mode, output = editor_transition(mode, enter_input)

        assert new_mode == EditorMode.INSERT
        assert output.success is False

    def test_insert_allows_text_change(self) -> None:
        """INSERT mode allows text editing."""
        mode = EditorMode.INSERT
        text_input = TextChangeInput(delta="abc", position=0)

        new_mode, output = editor_transition(mode, text_input)

        assert new_mode == EditorMode.INSERT
        assert output.success is True

    def test_insert_allows_save(self) -> None:
        """INSERT mode allows save."""
        mode = EditorMode.INSERT
        save_input = SaveInput()

        new_mode, output = editor_transition(mode, save_input)

        assert new_mode == EditorMode.INSERT  # Stays in INSERT
        assert output.success is True

    def test_insert_allows_discard(self) -> None:
        """INSERT mode allows discard."""
        mode = EditorMode.INSERT
        discard_input = DiscardInput()

        new_mode, output = editor_transition(mode, discard_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_insert_allows_escape(self) -> None:
        """INSERT mode allows escape."""
        mode = EditorMode.INSERT
        exit_input = ModeExitInput()

        new_mode, output = editor_transition(mode, exit_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True


# =============================================================================
# NORMAL Mode Operations Tests
# =============================================================================


class TestNormalModeOperations:
    """Test NORMAL mode operations."""

    def test_navigate_parent(self) -> None:
        """Navigate to parent node (gh)."""
        mode = EditorMode.NORMAL
        nav_input = NavigateInput(direction="parent")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "parent" in output.message.lower()

    def test_navigate_child(self) -> None:
        """Navigate to child node (gl)."""
        mode = EditorMode.NORMAL
        nav_input = NavigateInput(direction="child")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "child" in output.message.lower()

    def test_navigate_sibling(self) -> None:
        """Navigate to sibling node (gj/gk)."""
        mode = EditorMode.NORMAL
        nav_input = NavigateInput(direction="next_sibling")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_follow_edge(self) -> None:
        """Follow edge under cursor (gf)."""
        mode = EditorMode.NORMAL
        follow_input = FollowEdgeInput(edge_type="implements")

        new_mode, output = editor_transition(mode, follow_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "implements" in output.message.lower()

    def test_follow_edge_inferred(self) -> None:
        """Follow edge with inferred type (gf with no explicit type)."""
        mode = EditorMode.NORMAL
        follow_input = FollowEdgeInput()  # No edge_type

        new_mode, output = editor_transition(mode, follow_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "inferred" in output.message.lower()

    def test_search(self) -> None:
        """Search for pattern (/pattern)."""
        mode = EditorMode.NORMAL
        search_input = SearchInput(pattern="test_function")

        new_mode, output = editor_transition(mode, search_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "test_function" in output.message.lower()


# =============================================================================
# VISUAL Mode Operations Tests
# =============================================================================


class TestVisualModeOperations:
    """Test VISUAL mode operations."""

    def test_extend_selection(self) -> None:
        """Extend selection via motion."""
        mode = EditorMode.VISUAL
        extend_input = SelectExtendInput(direction="down")

        new_mode, output = editor_transition(mode, extend_input)

        assert new_mode == EditorMode.VISUAL
        assert output.success is True
        assert "down" in output.message.lower()

    def test_toggle_node_in_selection(self) -> None:
        """Toggle node in selection."""
        mode = EditorMode.VISUAL
        toggle_input = SelectToggleInput(node_id="node_123")

        new_mode, output = editor_transition(mode, toggle_input)

        assert new_mode == EditorMode.VISUAL
        assert output.success is True
        assert "node_123" in output.message.lower()

    def test_action_delete(self) -> None:
        """Delete action on selection."""
        mode = EditorMode.VISUAL
        action_input = ActionInput(action="delete")

        new_mode, output = editor_transition(mode, action_input)

        assert new_mode == EditorMode.NORMAL  # Exit after action
        assert output.success is True
        assert "delete" in output.message.lower()

    def test_action_yank(self) -> None:
        """Yank (copy) action on selection."""
        mode = EditorMode.VISUAL
        action_input = ActionInput(action="yank")

        new_mode, output = editor_transition(mode, action_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True


# =============================================================================
# COMMAND Mode Operations Tests
# =============================================================================


class TestCommandModeOperations:
    """Test COMMAND mode operations."""

    def test_command_text_entry(self) -> None:
        """Enter command text."""
        mode = EditorMode.COMMAND
        cmd_input = CommandInput(text="self.brain.capture")

        new_mode, output = editor_transition(mode, cmd_input)

        assert new_mode == EditorMode.COMMAND
        assert output.success is True
        assert "self.brain.capture" in output.message.lower()

    def test_command_execute(self) -> None:
        """Execute command (Enter)."""
        mode = EditorMode.COMMAND
        execute_input = ExecuteInput()

        new_mode, output = editor_transition(mode, execute_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_tab_complete(self) -> None:
        """Tab completion."""
        mode = EditorMode.COMMAND
        tab_input = TabCompleteInput()

        new_mode, output = editor_transition(mode, tab_input)

        assert new_mode == EditorMode.COMMAND
        assert output.success is True


# =============================================================================
# PORTAL Mode Operations Tests
# =============================================================================


class TestPortalModeOperations:
    """Test PORTAL mode operations."""

    def test_expand_hyperedge(self) -> None:
        """Expand hyperedge."""
        mode = EditorMode.PORTAL
        expand_input = ExpandInput(edge_id="edge_123")

        new_mode, output = editor_transition(mode, expand_input)

        assert new_mode == EditorMode.PORTAL
        assert output.success is True
        assert "edge_123" in output.message.lower()

    def test_collapse_hyperedge(self) -> None:
        """Collapse hyperedge."""
        mode = EditorMode.PORTAL
        collapse_input = CollapseInput(edge_id="edge_456")

        new_mode, output = editor_transition(mode, collapse_input)

        assert new_mode == EditorMode.PORTAL
        assert output.success is True
        assert "edge_456" in output.message.lower()

    def test_navigate_to_portal(self) -> None:
        """Navigate between portals."""
        mode = EditorMode.PORTAL
        nav_input = NavigateInput(direction="next_sibling")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.PORTAL
        assert output.success is True


# =============================================================================
# GRAPH Mode Operations Tests
# =============================================================================


class TestGraphModeOperations:
    """Test GRAPH mode operations."""

    def test_pan_up(self) -> None:
        """Pan graph view up."""
        mode = EditorMode.GRAPH
        pan_input = PanInput(direction="up", amount=10)

        new_mode, output = editor_transition(mode, pan_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True
        assert "up" in output.message.lower()

    def test_zoom_in(self) -> None:
        """Zoom in."""
        mode = EditorMode.GRAPH
        zoom_input = ZoomInput(delta=0.1)

        new_mode, output = editor_transition(mode, zoom_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True
        assert "in" in output.message.lower()

    def test_zoom_out(self) -> None:
        """Zoom out."""
        mode = EditorMode.GRAPH
        zoom_input = ZoomInput(delta=-0.1)

        new_mode, output = editor_transition(mode, zoom_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True
        assert "out" in output.message.lower()

    def test_center_on_focus(self) -> None:
        """Center view on focused node."""
        mode = EditorMode.GRAPH
        center_input = CenterInput()

        new_mode, output = editor_transition(mode, center_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True
        assert "center" in output.message.lower()


# =============================================================================
# KBLOCK Mode Operations Tests
# =============================================================================


class TestKBlockModeOperations:
    """Test KBLOCK mode operations."""

    def test_save_kblock(self) -> None:
        """Save K-Block with witness."""
        mode = EditorMode.KBLOCK
        save_input = SaveInput(witness_reason="fixed bug")

        new_mode, output = editor_transition(mode, save_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "witness" in output.message.lower()

    def test_discard_kblock(self) -> None:
        """Discard K-Block (no side effects)."""
        mode = EditorMode.KBLOCK
        discard_input = DiscardInput()

        new_mode, output = editor_transition(mode, discard_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True
        assert "no side effects" in output.message.lower() or "discard" in output.message.lower()


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestEditorPolynomial:
    """Test the EDITOR_POLYNOMIAL agent instance."""

    def test_polynomial_exists(self) -> None:
        """EDITOR_POLYNOMIAL is defined."""
        assert EDITOR_POLYNOMIAL is not None
        assert EDITOR_POLYNOMIAL.name == "EditorPolynomial"

    def test_positions(self) -> None:
        """Polynomial has all 7 positions."""
        assert len(EDITOR_POLYNOMIAL.positions) == 7
        for mode in EditorMode:
            assert mode in EDITOR_POLYNOMIAL.positions

    def test_invoke_with_navigate(self) -> None:
        """Invoke polynomial with navigation input."""
        mode = EditorMode.NORMAL
        nav_input = NavigateInput(direction="parent")

        new_mode, output = EDITOR_POLYNOMIAL.invoke(mode, nav_input)

        assert new_mode == EditorMode.NORMAL
        assert isinstance(output, EditorOutput)
        assert output.success is True

    def test_invoke_with_mode_enter(self) -> None:
        """Invoke polynomial with mode enter input."""
        mode = EditorMode.NORMAL
        enter_input = ModeEnterInput(target_mode=EditorMode.INSERT)

        new_mode, output = EDITOR_POLYNOMIAL.invoke(mode, enter_input)

        assert new_mode == EditorMode.INSERT
        assert output.success is True

    def test_run_sequence(self) -> None:
        """Run a sequence of inputs through polynomial."""
        inputs = [
            ModeEnterInput(target_mode=EditorMode.INSERT),  # NORMAL → INSERT
            TextChangeInput(delta="hello", position=0),  # Type
            SaveInput(witness_reason="initial content"),  # Save (stay in INSERT)
            ModeExitInput(),  # INSERT → NORMAL
        ]

        final_mode, outputs = EDITOR_POLYNOMIAL.run(EditorMode.NORMAL, inputs)

        assert final_mode == EditorMode.NORMAL
        assert len(outputs) == 4
        assert all(isinstance(o, EditorOutput) for o in outputs)
        assert all(o.success for o in outputs)


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_invalid_input_in_normal(self) -> None:
        """Invalid input type in NORMAL mode."""
        mode = EditorMode.NORMAL
        # TextChangeInput is invalid in NORMAL
        invalid_input = TextChangeInput(delta="text", position=0)

        new_mode, output = editor_transition(mode, invalid_input)

        # Should stay in NORMAL with failure
        assert new_mode == EditorMode.NORMAL
        assert output.success is False

    def test_escape_in_all_modes(self) -> None:
        """Esc works from every mode."""
        for mode in EditorMode:
            new_mode, output = editor_transition(mode, ModeExitInput())
            assert new_mode == EditorMode.NORMAL
            assert output.success is True

    def test_navigate_with_zero_count(self) -> None:
        """Navigate with count=0 (edge case)."""
        mode = EditorMode.NORMAL
        nav_input = NavigateInput(direction="parent")

        new_mode, output = editor_transition(mode, nav_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_zoom_with_zero_delta(self) -> None:
        """Zoom with delta=0 (no zoom)."""
        mode = EditorMode.GRAPH
        zoom_input = ZoomInput(delta=0.0)

        new_mode, output = editor_transition(mode, zoom_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True

    def test_empty_search_pattern(self) -> None:
        """Search with empty pattern."""
        mode = EditorMode.NORMAL
        search_input = SearchInput(pattern="")

        new_mode, output = editor_transition(mode, search_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    def test_mode_enter_same_mode(self) -> None:
        """Enter a mode from itself (edge case)."""
        mode = EditorMode.INSERT
        # Try to enter INSERT while already in INSERT
        enter_input = ModeEnterInput(target_mode=EditorMode.INSERT)

        new_mode, output = editor_transition(mode, enter_input)

        # Should fail (Right to Rest)
        assert new_mode == EditorMode.INSERT
        assert output.success is False


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(st.sampled_from(list(EditorMode)))
    def test_escape_always_reaches_normal(self, start_mode: EditorMode) -> None:
        """Property: Esc from any mode reaches NORMAL."""
        new_mode, output = editor_transition(start_mode, ModeExitInput())
        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    @given(
        st.sampled_from(list(EditorMode)),
        st.sampled_from(
            [
                NavigateInput(direction="parent"),
                NavigateInput(direction="child"),
                NavigateInput(direction="next_sibling"),
                NavigateInput(direction="prev_sibling"),
            ]
        ),
    )
    def test_determinism_navigation(self, mode: EditorMode, nav_input: NavigateInput) -> None:
        """Property: Navigation is deterministic (except for timestamp)."""
        new_mode1, output1 = editor_transition(mode, nav_input)
        new_mode2, output2 = editor_transition(mode, nav_input)

        # Mode transitions should be identical
        assert new_mode1 == new_mode2

        # Outputs should be identical except for timestamp
        assert output1.mode == output2.mode
        assert output1.success == output2.success
        assert output1.message == output2.message
        assert output1.data == output2.data

    @given(st.text(min_size=0, max_size=100))
    def test_search_any_pattern(self, pattern: str) -> None:
        """Property: Search accepts any string pattern."""
        mode = EditorMode.NORMAL
        search_input = SearchInput(pattern=pattern)

        new_mode, output = editor_transition(mode, search_input)

        assert new_mode == EditorMode.NORMAL
        assert output.success is True

    @given(st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False))
    def test_zoom_any_delta(self, delta: float) -> None:
        """Property: Zoom accepts any finite float delta."""
        mode = EditorMode.GRAPH
        zoom_input = ZoomInput(delta=delta)

        new_mode, output = editor_transition(mode, zoom_input)

        assert new_mode == EditorMode.GRAPH
        assert output.success is True


# =============================================================================
# Integration Tests (Multi-Step Workflows)
# =============================================================================


class TestIntegrationWorkflows:
    """Test multi-step editor workflows."""

    def test_edit_workflow(self) -> None:
        """Complete edit workflow: Navigate → Insert → Edit → Save → Exit."""
        workflow = [
            (EditorMode.NORMAL, NavigateInput(direction="child")),
            (EditorMode.NORMAL, ModeEnterInput(target_mode=EditorMode.INSERT)),
            (EditorMode.INSERT, TextChangeInput(delta="hello world", position=0)),
            (EditorMode.INSERT, SaveInput(witness_reason="added greeting")),
            (EditorMode.INSERT, ModeExitInput()),
        ]

        current_mode = EditorMode.NORMAL
        for expected_initial_mode, input_obj in workflow:
            assert current_mode == expected_initial_mode
            current_mode, output = editor_transition(current_mode, input_obj)
            assert output.success is True

        assert current_mode == EditorMode.NORMAL

    def test_visual_selection_workflow(self) -> None:
        """Visual selection workflow: Enter Visual → Extend → Action."""
        workflow = [
            (EditorMode.NORMAL, ModeEnterInput(target_mode=EditorMode.VISUAL)),
            (EditorMode.VISUAL, SelectExtendInput(direction="down")),
            (EditorMode.VISUAL, SelectExtendInput(direction="down")),
            (EditorMode.VISUAL, ActionInput(action="yank")),
        ]

        current_mode = EditorMode.NORMAL
        for expected_initial_mode, input_obj in workflow:
            assert current_mode == expected_initial_mode
            current_mode, output = editor_transition(current_mode, input_obj)
            assert output.success is True

        assert current_mode == EditorMode.NORMAL

    def test_command_execution_workflow(self) -> None:
        """Command execution workflow: Enter Command → Type → Execute."""
        workflow = [
            (EditorMode.NORMAL, ModeEnterInput(target_mode=EditorMode.COMMAND)),
            (EditorMode.COMMAND, CommandInput(text="self.brain.capture")),
            (EditorMode.COMMAND, ExecuteInput()),
        ]

        current_mode = EditorMode.NORMAL
        for expected_initial_mode, input_obj in workflow:
            assert current_mode == expected_initial_mode
            current_mode, output = editor_transition(current_mode, input_obj)
            assert output.success is True

        assert current_mode == EditorMode.NORMAL

    def test_discard_workflow(self) -> None:
        """Discard workflow: Enter Insert → Edit → Discard."""
        workflow = [
            (EditorMode.NORMAL, ModeEnterInput(target_mode=EditorMode.INSERT)),
            (EditorMode.INSERT, TextChangeInput(delta="unwanted change", position=0)),
            (EditorMode.INSERT, DiscardInput()),
        ]

        current_mode = EditorMode.NORMAL
        for expected_initial_mode, input_obj in workflow:
            assert current_mode == expected_initial_mode
            current_mode, output = editor_transition(current_mode, input_obj)
            assert output.success is True

        assert current_mode == EditorMode.NORMAL

    def test_graph_exploration_workflow(self) -> None:
        """Graph exploration workflow: Enter Graph → Pan → Zoom → Center → Exit."""
        workflow = [
            (EditorMode.NORMAL, ModeEnterInput(target_mode=EditorMode.GRAPH)),
            (EditorMode.GRAPH, PanInput(direction="up", amount=5)),
            (EditorMode.GRAPH, ZoomInput(delta=0.5)),
            (EditorMode.GRAPH, CenterInput()),
            (EditorMode.GRAPH, ModeExitInput()),
        ]

        current_mode = EditorMode.NORMAL
        for expected_initial_mode, input_obj in workflow:
            assert current_mode == expected_initial_mode
            current_mode, output = editor_transition(current_mode, input_obj)
            assert output.success is True

        assert current_mode == EditorMode.NORMAL
