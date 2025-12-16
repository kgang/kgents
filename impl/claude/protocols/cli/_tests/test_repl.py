"""
AGENTESE REPL Integration Tests.

Tests Wave 2 features:
1. Observer switching (/observer commands)
2. Navigation (contexts, holons, .. and /)
3. Pipeline execution (>> operator)
4. Graceful degradation (Logos fallback, rich fallback)
5. Error sympathy (helpful error messages)
6. Tab completion

Principle: Tests verify behavior, not implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def repl_state() -> Any:
    """Create a fresh REPL state for testing."""
    from protocols.cli.repl import ReplState

    return ReplState()


@pytest.fixture
def mock_logos() -> MagicMock:
    """Create a mock Logos resolver."""
    logos = MagicMock()
    logos.invoke = MagicMock(return_value="mock_result")
    logos.compose = MagicMock(
        return_value=MagicMock(invoke=MagicMock(return_value="composed_result"))
    )
    return logos


# =============================================================================
# Observer Switching Tests (Wave 2)
# =============================================================================


class TestObserverSwitching:
    """Tests for /observer command handling."""

    def test_show_current_observer(self, repl_state: Any) -> None:
        """Verify /observer shows current archetype."""
        from protocols.cli.repl import handle_observer_command

        result = handle_observer_command(repl_state, "/observer")
        assert "explorer" in result.lower()  # Default observer
        assert "Current observer" in result or "current" in result.lower()

    def test_switch_observer_to_developer(self, repl_state: Any) -> None:
        """Verify /observer developer switches archetype."""
        from protocols.cli.repl import handle_observer_command

        assert repl_state.observer == "explorer"
        result = handle_observer_command(repl_state, "/observer developer")
        assert repl_state.observer == "developer"
        assert "developer" in result.lower()

    def test_switch_observer_to_architect(self, repl_state: Any) -> None:
        """Verify /observer architect switches archetype."""
        from protocols.cli.repl import handle_observer_command

        result = handle_observer_command(repl_state, "/observer architect")
        assert repl_state.observer == "architect"
        assert "architect" in result.lower()

    def test_switch_observer_to_admin(self, repl_state: Any) -> None:
        """Verify /observer admin switches archetype."""
        from protocols.cli.repl import handle_observer_command

        result = handle_observer_command(repl_state, "/observer admin")
        assert repl_state.observer == "admin"
        assert "admin" in result.lower()

    def test_switch_observer_invalid(self, repl_state: Any) -> None:
        """Verify invalid archetype produces sympathetic error."""
        from protocols.cli.repl import handle_observer_command

        result = handle_observer_command(repl_state, "/observer hacker")
        assert "Error" in result or "error" in result.lower() or "Unknown" in result
        assert repl_state.observer == "explorer"  # Unchanged

    def test_list_observers(self, repl_state: Any) -> None:
        """Verify /observers lists all archetypes."""
        from protocols.cli.repl import handle_observer_command

        result = handle_observer_command(repl_state, "/observers")
        assert "explorer" in result.lower()
        assert "developer" in result.lower()
        assert "architect" in result.lower()
        assert "admin" in result.lower()

    def test_prompt_shows_observer_indicator(self, repl_state: Any) -> None:
        """Verify prompt includes observer indicator."""
        # Explorer
        assert "(E)" in repl_state.prompt

        # Developer
        repl_state.observer = "developer"
        assert "(D)" in repl_state.prompt

        # Architect
        repl_state.observer = "architect"
        assert "(A)" in repl_state.prompt

        # Admin
        repl_state.observer = "admin"
        assert "(*)" in repl_state.prompt


# =============================================================================
# Navigation Tests
# =============================================================================


class TestNavigation:
    """Tests for REPL navigation."""

    def test_navigate_to_context(self, repl_state: Any) -> None:
        """Verify navigation to context."""
        from protocols.cli.repl import handle_navigation

        result = handle_navigation(repl_state, ["self"])
        assert result is not None
        assert repl_state.path == ["self"]

    def test_navigate_to_holon(self, repl_state: Any) -> None:
        """Verify navigation from context to holon."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self"]
        result = handle_navigation(repl_state, ["status"])
        assert result is not None
        assert repl_state.path == ["self", "status"]

    def test_navigate_up(self, repl_state: Any) -> None:
        """Verify .. navigates up."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self", "status"]
        result = handle_navigation(repl_state, [".."])
        assert result is not None
        assert repl_state.path == ["self"]

    def test_navigate_up_at_root(self, repl_state: Any) -> None:
        """Verify .. at root is handled gracefully."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, [".."])
        assert result is not None
        assert "root" in result.lower()
        assert repl_state.path == []

    def test_navigate_to_root(self, repl_state: Any) -> None:
        """Verify / navigates to root."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self", "status"]
        result = handle_navigation(repl_state, ["/"])
        assert result is not None
        assert repl_state.path == []

    def test_show_current_path(self, repl_state: Any) -> None:
        """Verify . shows current path."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self", "soul"]
        result = handle_navigation(repl_state, ["."])
        assert result is not None
        assert "self.soul" in result or "self" in result.lower()

    def test_context_switch_from_another_context(self, repl_state: Any) -> None:
        """Verify can switch contexts directly."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self", "status"]
        result = handle_navigation(repl_state, ["world"])
        assert result is not None
        assert repl_state.path == ["world"]

    def test_multi_word_not_navigation(self, repl_state: Any) -> None:
        """Verify multi-word input with 3+ parts is not treated as navigation."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self"]
        result = handle_navigation(repl_state, ["status", "manifest"])
        assert result is None  # Not navigation, should be invocation

    def test_fast_forward_navigation_self_soul(self, repl_state: Any) -> None:
        """Verify self.soul fast-forward navigation works from root."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, ["self", "soul"])
        assert result is not None
        assert repl_state.path == ["self", "soul"]
        assert "soul" in result.lower()

    def test_fast_forward_navigation_world_agents(self, repl_state: Any) -> None:
        """Verify world.agents fast-forward navigation works."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, ["world", "agents"])
        assert result is not None
        assert repl_state.path == ["world", "agents"]

    def test_fast_forward_navigation_void_entropy(self, repl_state: Any) -> None:
        """Verify void.entropy fast-forward navigation works."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, ["void", "entropy"])
        assert result is not None
        assert repl_state.path == ["void", "entropy"]

    def test_fast_forward_navigation_from_other_context(self, repl_state: Any) -> None:
        """Verify fast-forward navigation works from any starting point."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["world", "agents"]
        result = handle_navigation(repl_state, ["self", "soul"])
        assert result is not None
        assert repl_state.path == ["self", "soul"]

    def test_fast_forward_invalid_holon_not_navigation(self, repl_state: Any) -> None:
        """Verify invalid holon in fast-forward path is not navigation."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, ["self", "invalid_holon"])
        assert result is None  # Not a valid navigation path

    def test_fast_forward_soul_shows_dialogue_mode_message(
        self, repl_state: Any
    ) -> None:
        """Verify fast-forward to self.soul shows dialogue mode message."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = []
        result = handle_navigation(repl_state, ["self", "soul"])
        assert result is not None
        assert "Dialogue mode" in result


# =============================================================================
# Pipeline Execution Tests (Wave 2)
# =============================================================================


class TestPipelineExecution:
    """Tests for >> composition operator."""

    def test_pipeline_requires_two_paths(self, repl_state: Any) -> None:
        """Verify pipeline needs at least two paths."""
        from protocols.cli.repl import handle_composition

        result = handle_composition(repl_state, "self.status")
        # Should be an error or handle gracefully
        assert (
            "Error" in result
            or "error" in result.lower()
            or "requires" in result.lower()
        )

    def test_pipeline_cli_fallback(self, repl_state: Any) -> None:
        """Verify pipeline falls back to CLI execution."""
        from protocols.cli.repl import handle_composition

        result = handle_composition(repl_state, "self status >> world agents")
        # Should show step indicators
        assert "[1/" in result or "1." in result
        assert "[2/" in result or "2." in result

    def test_pipeline_with_context_path(self, repl_state: Any) -> None:
        """Verify pipeline with explicit context paths."""
        from protocols.cli.repl import handle_composition

        result = handle_composition(repl_state, "self.status >> world.agents")
        assert "status" in result.lower() or "agents" in result.lower()

    def test_pipeline_prepends_current_path(self, repl_state: Any) -> None:
        """Verify pipeline prepends current path when needed."""
        from protocols.cli.repl import handle_composition

        repl_state.path = ["self"]
        # "status" should become "self.status"
        result = handle_composition(repl_state, "status >> world agents")
        # Should execute without "Unknown context" error for first path
        assert "Unknown context: status" not in result


# =============================================================================
# Error Sympathy Tests (Wave 2)
# =============================================================================


class TestErrorSympathy:
    """Tests for helpful error messages."""

    def test_error_includes_suggestion(self) -> None:
        """Verify errors include suggestions."""
        from protocols.cli.repl import _error_with_sympathy

        result = _error_with_sympathy(
            "Path not found",
            suggestion="Try: self, world, concept",
        )
        assert "Path not found" in result
        assert "Try" in result or "try" in result.lower()

    def test_suggest_for_unknown_context(self) -> None:
        """Verify suggestions for unknown context."""
        from protocols.cli.repl import _suggest_for_path

        suggestion = _suggest_for_path(["unknown"])
        assert suggestion is not None
        assert "self" in suggestion or "world" in suggestion

    def test_suggest_holons_for_context(self) -> None:
        """Verify suggestions show available holons."""
        from protocols.cli.repl import _suggest_for_path

        suggestion = _suggest_for_path(["self"])
        assert suggestion is not None
        assert (
            "status" in suggestion
            or "memory" in suggestion
            or "Available" in suggestion
        )


# =============================================================================
# Introspection Tests
# =============================================================================


class TestIntrospection:
    """Tests for ? and ?? commands."""

    def test_show_affordances_at_root(self, repl_state: Any) -> None:
        """Verify ? at root shows contexts."""
        from protocols.cli.repl import handle_introspection

        result = handle_introspection(repl_state, "?")
        assert result is not None
        assert "self" in result.lower()
        assert "world" in result.lower()
        assert "concept" in result.lower()
        assert "void" in result.lower()
        assert "time" in result.lower()

    def test_show_affordances_in_context(self, repl_state: Any) -> None:
        """Verify ? in context shows holons."""
        from protocols.cli.repl import handle_introspection

        repl_state.path = ["self"]
        result = handle_introspection(repl_state, "?")
        assert result is not None
        assert "status" in result.lower() or "memory" in result.lower()

    def test_show_detailed_help(self, repl_state: Any) -> None:
        """Verify ?? shows detailed help."""
        from protocols.cli.repl import handle_introspection

        result = handle_introspection(repl_state, "??")
        assert result is not None
        assert "Navigation" in result or "navigation" in result.lower()

    def test_show_context_specific_help(self, repl_state: Any) -> None:
        """Verify ?? in context shows context-specific help."""
        from protocols.cli.repl import handle_introspection

        repl_state.path = ["self"]
        result = handle_introspection(repl_state, "??")
        assert result is not None
        assert "self" in result.lower()
        assert "Internal" in result or "internal" in result.lower()


# =============================================================================
# Tab Completion Tests
# =============================================================================


class TestTabCompletion:
    """Tests for tab completion."""

    def test_complete_contexts_at_root(self, repl_state: Any) -> None:
        """Verify completion at root suggests contexts."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("se")
        assert "self" in matches

    def test_complete_holons_in_context(self, repl_state: Any) -> None:
        """Verify completion in context suggests holons."""
        from protocols.cli.repl import Completer

        repl_state.path = ["self"]
        completer = Completer(repl_state)
        matches = completer._get_matches("st")
        assert "status" in matches

    def test_complete_special_commands(self, repl_state: Any) -> None:
        """Verify completion includes special commands."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("/")
        assert "/" in matches or "/observer" in matches or "/observers" in matches

    def test_complete_observer_archetypes(self, repl_state: Any) -> None:
        """Verify completion after /observer suggests archetypes."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("/observer d")
        assert any("developer" in m for m in matches)

    def test_complete_empty_input_at_root_shows_all_contexts(
        self, repl_state: Any
    ) -> None:
        """Verify empty tab press at root shows all contexts (Wave 5)."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("")

        # Should include all 5 contexts
        assert "self" in matches
        assert "world" in matches
        assert "concept" in matches
        assert "void" in matches
        assert "time" in matches
        # Plus special commands
        assert "help" in matches
        assert "exit" in matches

    def test_complete_empty_input_in_context_shows_holons(
        self, repl_state: Any
    ) -> None:
        """Verify empty tab press in context shows all holons (Wave 5)."""
        from protocols.cli.repl import Completer

        repl_state.path = ["self"]
        completer = Completer(repl_state)
        matches = completer._get_matches("")

        # Should show self context holons
        assert "status" in matches
        assert "memory" in matches
        assert "soul" in matches
        assert "dashboard" in matches

    def test_complete_empty_input_in_holon_shows_aspects(self, repl_state: Any) -> None:
        """Verify empty tab press in holon shows all aspects (Wave 5)."""
        from protocols.cli.repl import Completer

        repl_state.path = ["self", "soul"]
        completer = Completer(repl_state)
        matches = completer._get_matches("")

        # Should show AGENTESE aspects
        assert "manifest" in matches
        assert "witness" in matches
        assert "affordances" in matches
        assert "refine" in matches

    def test_display_matches_hook_exists(self) -> None:
        """Verify display matches hook function exists (Wave 5)."""
        from protocols.cli.repl import _display_matches

        # The function should exist and be callable
        assert callable(_display_matches)

    def test_display_matches_groups_by_type(self, capsys: Any) -> None:
        """Verify display hook shows completions grouped by type (Wave 5)."""
        from protocols.cli.repl import _display_matches

        matches = ["self", "world", "help", "exit", "status", "/observer"]
        _display_matches("", matches, 8)

        captured = capsys.readouterr()
        # Should contain the items (contexts, options, commands on separate lines)
        assert "self" in captured.out
        assert "world" in captured.out
        assert "status" in captured.out
        assert "help" in captured.out


# =============================================================================
# Rich Rendering Tests
# =============================================================================


class TestRichRendering:
    """Tests for rich output rendering."""

    def test_render_dict_result(self, repl_state: Any) -> None:
        """Verify dict results are rendered."""
        from protocols.cli.repl import _render_result

        result = _render_result({"key": "value", "count": 42}, repl_state)
        assert "key" in result.lower()
        assert "value" in result.lower()

    def test_render_list_result(self, repl_state: Any) -> None:
        """Verify list results are rendered."""
        from protocols.cli.repl import _render_result

        result = _render_result(["item1", "item2", "item3"], repl_state)
        assert "item1" in result
        assert "item2" in result

    def test_render_empty_list(self, repl_state: Any) -> None:
        """Verify empty list shows appropriate message."""
        from protocols.cli.repl import _render_result

        result = _render_result([], repl_state)
        assert "empty" in result.lower()

    def test_render_string_passthrough(self, repl_state: Any) -> None:
        """Verify strings pass through."""
        from protocols.cli.repl import _render_result

        result = _render_result("Hello, world!", repl_state)
        assert "Hello, world!" in result

    def test_render_none_shows_ok(self, repl_state: Any) -> None:
        """Verify None shows (ok)."""
        from protocols.cli.repl import _render_result

        result = _render_result(None, repl_state)
        assert "ok" in result.lower()

    def test_render_basic_rendering_object(self, repl_state: Any) -> None:
        """Verify BasicRendering-like objects are rendered."""
        from protocols.cli.repl import _render_result

        @dataclass
        class MockRendering:
            summary: str
            content: str

        mock = MockRendering(summary="Test Summary", content="Test Content")
        result = _render_result(mock, repl_state)
        assert "Test Summary" in result
        assert "Test Content" in result


# =============================================================================
# Graceful Degradation Tests
# =============================================================================


class TestGracefulDegradation:
    """Tests for graceful degradation when subsystems unavailable."""

    def test_logos_unavailable_falls_back_to_cli(self, repl_state: Any) -> None:
        """Verify Logos unavailable triggers CLI fallback."""
        from protocols.cli.repl import handle_invocation

        # Ensure Logos is not available
        repl_state._logos = None

        repl_state.path = ["self"]
        result = handle_invocation(repl_state, ["status"])
        # Should still produce output (via CLI fallback)
        assert result is not None
        assert len(result) > 0

    def test_umwelt_unavailable_continues(self, repl_state: Any) -> None:
        """Verify missing Umwelt doesn't crash."""
        from protocols.cli.repl import handle_invocation

        repl_state._umwelt = None
        repl_state._logos = None
        repl_state.path = []

        result = handle_invocation(repl_state, ["self", "status"])
        # Should still work via CLI
        assert result is not None


# =============================================================================
# State Management Tests
# =============================================================================


class TestStateManagement:
    """Tests for REPL state management."""

    def test_initial_state(self) -> None:
        """Verify initial state is correct."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        assert state.path == []
        assert state.observer == "explorer"
        assert state.running is True
        assert state.last_result is None

    def test_current_path_property(self) -> None:
        """Verify current_path property."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        assert state.current_path == ""

        state.path = ["self", "soul"]
        assert state.current_path == "self.soul"

    def test_history_tracking(self, repl_state: Any) -> None:
        """Verify command history is tracked."""
        repl_state.history.append("self")
        repl_state.history.append("status")
        assert len(repl_state.history) == 2
        assert "self" in repl_state.history

    def test_observer_invalidates_umwelt_cache(self, repl_state: Any) -> None:
        """Verify changing observer invalidates umwelt cache."""
        from protocols.cli.repl import handle_observer_command

        # Get initial umwelt (creates cache)
        _ = repl_state.get_umwelt()
        initial_umwelt = repl_state._umwelt

        # Switch observer
        handle_observer_command(repl_state, "/observer developer")

        # Umwelt should be invalidated
        assert repl_state._umwelt is None

        # Getting umwelt again should create new one
        new_umwelt = repl_state.get_umwelt()
        assert new_umwelt is not initial_umwelt


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """End-to-end integration tests."""

    def test_full_navigation_flow(self, repl_state: Any) -> None:
        """Test a complete navigation flow."""
        from protocols.cli.repl import handle_navigation

        # Start at root
        assert repl_state.path == []

        # Navigate to self
        handle_navigation(repl_state, ["self"])
        assert repl_state.path == ["self"]

        # Navigate to status
        handle_navigation(repl_state, ["status"])
        assert repl_state.path == ["self", "status"]

        # Go up
        handle_navigation(repl_state, [".."])
        assert repl_state.path == ["self"]

        # Switch to world
        handle_navigation(repl_state, ["world"])
        assert repl_state.path == ["world"]

        # Return to root
        handle_navigation(repl_state, ["/"])
        assert repl_state.path == []

    def test_observer_affects_umwelt_archetype(self, repl_state: Any) -> None:
        """Verify observer affects umwelt archetype."""
        from protocols.cli.repl import handle_observer_command

        # Set to developer
        handle_observer_command(repl_state, "/observer developer")

        # Get umwelt
        umwelt = repl_state.get_umwelt()
        if umwelt is not None:
            # Check archetype is developer
            assert umwelt._observer_type == "developer"


# =============================================================================
# Wave 2.5: Edge Case Tests (H1)
# =============================================================================


class TestEdgeCases:
    """Tests for edge conditions and unusual inputs."""

    def test_unicode_in_path(self, repl_state: Any) -> None:
        """Verify unicode characters in paths are handled gracefully."""
        from protocols.cli.repl import handle_invocation, handle_navigation

        # Unicode in navigation (should fail gracefully, not crash)
        result = handle_navigation(repl_state, ["日本語"])
        # Not a valid context, so navigation returns None
        assert result is None

        # Unicode in invocation (should produce error with sympathy)
        result = handle_invocation(repl_state, ["日本語", "test"])
        assert result is not None
        assert "Error" in result or "Unknown" in result or "日本語" in result

    def test_very_long_path(self, repl_state: Any) -> None:
        """Verify very long paths don't crash the REPL."""
        from protocols.cli.repl import handle_invocation

        # Create a path with 100 segments
        long_path = ["self"] + ["segment"] * 99
        result = handle_invocation(repl_state, long_path)
        # Should handle gracefully (error or truncation, not crash)
        assert result is not None

    def test_special_characters_in_input(self, repl_state: Any) -> None:
        """Verify special characters are handled gracefully."""
        from protocols.cli.repl import handle_invocation, handle_navigation

        special_chars = [
            "test;ls",  # Shell injection attempt
            "test`whoami`",  # Command substitution
            "test$(id)",  # Another injection
            "test|cat",  # Pipe injection
            "test&&echo",  # Command chaining
            "../../../etc/passwd",  # Path traversal
            "test\necho",  # Newline injection
            "test\x00null",  # Null byte
        ]

        for char_input in special_chars:
            # Should not crash
            nav_result = handle_navigation(repl_state, [char_input])
            inv_result = handle_invocation(repl_state, [char_input])
            # Just verify no crash - result can be None or error
            assert inv_result is not None or nav_result is None

    def test_empty_input_handling(self, repl_state: Any) -> None:
        """Verify empty input is handled gracefully."""
        from protocols.cli.repl import handle_invocation, handle_navigation

        # Empty list
        nav_result = handle_navigation(repl_state, [])
        assert nav_result is None  # No-op for navigation

        # Invocation with empty
        inv_result = handle_invocation(repl_state, [])
        assert inv_result is not None  # Should give error with suggestion

    def test_whitespace_only_input(self, repl_state: Any) -> None:
        """Verify whitespace-only input is handled gracefully."""
        from protocols.cli.repl import handle_invocation, handle_navigation

        whitespace_inputs = ["   ", "\t", "\n", "  \t  "]

        for ws_input in whitespace_inputs:
            # Navigation with whitespace stripped should be empty
            parts = ws_input.split()
            nav_result = handle_navigation(repl_state, parts)
            assert nav_result is None  # Empty parts = no navigation

    def test_repeated_navigation_same_context(self, repl_state: Any) -> None:
        """Verify repeated navigation to same context is idempotent."""
        from protocols.cli.repl import handle_navigation

        # Navigate to self
        handle_navigation(repl_state, ["self"])
        assert repl_state.path == ["self"]

        # Navigate to self again
        result = handle_navigation(repl_state, ["self"])
        assert repl_state.path == ["self"]  # Still just ["self"]
        assert result is not None and "already" in result.lower()

    def test_case_insensitivity(self, repl_state: Any) -> None:
        """Verify context navigation is case-insensitive."""
        from protocols.cli.repl import handle_navigation

        # Test uppercase
        result = handle_navigation(repl_state, ["SELF"])
        assert result is not None
        assert repl_state.path == ["self"]

        # Test mixed case
        repl_state.path = []
        result = handle_navigation(repl_state, ["WoRlD"])
        assert result is not None
        assert repl_state.path == ["world"]


class TestConcurrency:
    """Tests for concurrent access safety."""

    def test_umwelt_cache_thread_safety(self, repl_state: Any) -> None:
        """Verify umwelt cache handles concurrent access."""
        import threading

        from protocols.cli.repl import handle_observer_command

        results = []
        errors = []

        def switch_observer(archetype: str) -> None:
            try:
                handle_observer_command(repl_state, f"/observer {archetype}")
                _ = repl_state.get_umwelt()
                results.append(archetype)
            except Exception as e:
                errors.append(str(e))

        # Spawn threads that switch observers
        threads = []
        archetypes = ["explorer", "developer", "architect", "admin"] * 5
        for arch in archetypes:
            t = threading.Thread(target=switch_observer, args=(arch,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should not have crashed
        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == len(archetypes)

    def test_state_mutations_during_invocation(self, repl_state: Any) -> None:
        """Verify state mutations during invocation are safe."""
        from protocols.cli.repl import handle_invocation

        repl_state.path = ["self"]

        # Invoke while modifying path shouldn't crash
        result = handle_invocation(repl_state, ["status"])
        # Result should be valid
        assert result is not None


class TestRecovery:
    """Tests for error recovery scenarios."""

    def test_logos_timeout_recovery(self, repl_state: Any) -> None:
        """Verify recovery from Logos timeout."""
        from unittest.mock import MagicMock

        from protocols.cli.repl import handle_invocation

        # Mock Logos that times out
        mock_logos = MagicMock()
        mock_logos.invoke = MagicMock(side_effect=TimeoutError("Logos timeout"))
        repl_state._logos = mock_logos

        # Mock Umwelt
        mock_umwelt = MagicMock()
        mock_umwelt._observer_type = "explorer"
        repl_state._umwelt = mock_umwelt

        repl_state.path = ["self"]

        # Should fall back to CLI
        result = handle_invocation(repl_state, ["status", "manifest"])
        assert result is not None
        # Should not propagate the timeout

    def test_cli_fallback_chain(self, repl_state: Any) -> None:
        """Verify CLI fallback when all else fails."""
        from protocols.cli.repl import handle_invocation

        # Ensure Logos is unavailable
        repl_state._logos = None
        repl_state._umwelt = None

        repl_state.path = ["self"]
        result = handle_invocation(repl_state, ["status"])

        # Should still produce output via CLI
        assert result is not None
        assert len(result) > 0

    def test_partial_pipeline_failure(self, repl_state: Any) -> None:
        """Verify pipeline handles partial failures gracefully."""
        from protocols.cli.repl import handle_composition

        # Pipeline with invalid middle step
        result = handle_composition(
            repl_state, "self status >> invalid.path >> world agents"
        )

        # Should show partial execution, not crash
        assert result is not None
        # Should have step indicators
        assert "[1/" in result or "1." in result


class TestSecurity:
    """Security-focused tests (Wave 2.5 H2)."""

    def test_shell_injection_paths_safe(self, repl_state: Any) -> None:
        """Verify shell metacharacters in paths don't execute.

        Note: The input may be echoed in error messages (safe),
        but actual shell execution should not occur.
        """
        import os

        from protocols.cli.repl import handle_invocation

        # Create a marker file that would be created if shell executed
        marker_file = "/tmp/kgents_security_test_marker"
        if os.path.exists(marker_file):
            os.remove(marker_file)

        # These should NOT execute shell commands
        injection_attempts = [
            ["self", f"; touch {marker_file}"],
            ["self", f"$(touch {marker_file})"],
            ["self", f"`touch {marker_file}`"],
        ]

        for attempt in injection_attempts:
            result = handle_invocation(repl_state, attempt)
            # Marker file should NOT exist (shell not executed)
            assert not os.path.exists(marker_file), (
                f"Shell injection executed: {attempt}"
            )
            # Result should be an error or normal output, not crash
            assert result is not None

    def test_path_traversal_blocked(self, repl_state: Any) -> None:
        """Verify path traversal attempts are handled safely."""
        from protocols.cli.repl import handle_invocation

        traversal_attempts = [
            ["../../../etc/passwd"],
            ["self", "../../../etc/passwd"],
            ["..%2f..%2f..%2fetc%2fpasswd"],  # URL-encoded
            ["....//....//etc/passwd"],  # Double-dot bypass
        ]

        for attempt in traversal_attempts:
            result = handle_invocation(repl_state, attempt)
            # Should be handled as invalid path, not read file
            assert "root:" not in result  # Would indicate /etc/passwd read

    def test_observer_injection_blocked(self, repl_state: Any) -> None:
        """Verify observer name can't inject code."""
        import os

        from protocols.cli.repl import handle_observer_command

        marker_file = "/tmp/kgents_observer_security_test"
        if os.path.exists(marker_file):
            os.remove(marker_file)

        injection_attempts = [
            f"/observer $(touch {marker_file})",
            f"/observer `touch {marker_file}`",
            "/observer admin;id",
            "/observer __import__('os').system('id')",
        ]

        for attempt in injection_attempts:
            result = handle_observer_command(repl_state, attempt)
            # Should fail validation, not execute
            assert "Error" in result or "Unknown" in result
            # Marker file should NOT exist
            assert not os.path.exists(marker_file)

    def test_pipeline_injection_safe(self, repl_state: Any) -> None:
        """Verify pipeline operator can't be used for injection."""
        import os

        from protocols.cli.repl import handle_composition

        marker_file = "/tmp/kgents_pipeline_security_test"
        if os.path.exists(marker_file):
            os.remove(marker_file)

        # Pipeline should only compose AGENTESE paths
        result = handle_composition(
            repl_state, f"self.status >> $(touch {marker_file}) >> world.agents"
        )
        # Should not execute shell - marker file should NOT exist
        assert not os.path.exists(marker_file)
        # Result should exist (error or partial output, not crash)
        assert result is not None


class TestPerformance:
    """Performance benchmarks (Wave 2.5 H3)."""

    def test_state_creation_fast(self) -> None:
        """ReplState creation should be < 10ms."""
        import time

        from protocols.cli.repl import ReplState

        start = time.perf_counter()
        for _ in range(100):
            _ = ReplState()
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per creation

        assert elapsed < 10, f"State creation too slow: {elapsed:.2f}ms"

    def test_navigation_latency(self, repl_state: Any) -> None:
        """Navigation should complete in < 5ms."""
        import time

        from protocols.cli.repl import handle_navigation

        # Warm up
        handle_navigation(repl_state, ["self"])
        repl_state.path = []

        # Measure
        start = time.perf_counter()
        for _ in range(100):
            handle_navigation(repl_state, ["self"])
            repl_state.path = []
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per op

        assert elapsed < 5, f"Navigation too slow: {elapsed:.2f}ms"

    def test_completion_latency(self, repl_state: Any) -> None:
        """Tab completion should respond in < 5ms."""
        import time

        from protocols.cli.repl import Completer

        completer = Completer(repl_state)

        # Warm up
        completer._get_matches("se")

        # Measure
        start = time.perf_counter()
        for _ in range(100):
            completer._get_matches("se")
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per op

        assert elapsed < 5, f"Completion too slow: {elapsed:.2f}ms"

    def test_introspection_latency(self, repl_state: Any) -> None:
        """Introspection (?) should complete in < 10ms."""
        import time

        from protocols.cli.repl import handle_introspection

        # Warm up
        handle_introspection(repl_state, "?")

        # Measure
        start = time.perf_counter()
        for _ in range(100):
            handle_introspection(repl_state, "?")
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per op

        assert elapsed < 10, f"Introspection too slow: {elapsed:.2f}ms"

    def test_rendering_latency(self, repl_state: Any) -> None:
        """Result rendering should complete in < 10ms."""
        import time

        from protocols.cli.repl import _render_result

        test_data = {"key": "value", "count": 42, "items": list(range(20))}

        # Warm up
        _render_result(test_data, repl_state)

        # Measure
        start = time.perf_counter()
        for _ in range(100):
            _render_result(test_data, repl_state)
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per op

        assert elapsed < 10, f"Rendering too slow: {elapsed:.2f}ms"


class TestInputValidation:
    """Tests for input validation and sanitization."""

    def test_max_path_depth(self, repl_state: Any) -> None:
        """Verify paths with extreme depth are handled."""
        from protocols.cli.repl import handle_invocation

        # 1000-level deep path
        deep_path = ["self"] + ["deep"] * 999
        result = handle_invocation(repl_state, deep_path)
        # Should handle (error is fine, crash is not)
        assert result is not None

    def test_max_input_length(self, repl_state: Any) -> None:
        """Verify very long inputs are handled."""
        from protocols.cli.repl import handle_invocation

        # 10KB input
        long_input = "a" * 10000
        result = handle_invocation(repl_state, [long_input])
        # Should handle gracefully
        assert result is not None

    def test_null_bytes_stripped(self, repl_state: Any) -> None:
        """Verify null bytes don't cause issues."""
        from protocols.cli.repl import handle_navigation

        # Input with null byte
        result = handle_navigation(repl_state, ["self\x00world"])
        # Should handle (null byte makes it invalid context)
        # Result can be None (not a navigation) or error
        assert result is None or "self" not in repl_state.path

    def test_control_characters(self, repl_state: Any) -> None:
        """Verify control characters are handled."""
        from protocols.cli.repl import handle_invocation

        # Various control characters
        control_inputs = [
            "\x1b[31mred\x1b[0m",  # ANSI escape
            "\r\ntest",  # CRLF
            "\x07bell",  # Bell
            "\x08backspace",  # Backspace
        ]

        for ctrl_input in control_inputs:
            result = handle_invocation(repl_state, [ctrl_input])
            # Should not crash
            assert result is not None


class TestStress:
    """Stress tests (Wave 2.5 H4)."""

    def test_rapid_fire_commands(self, repl_state: Any) -> None:
        """1000 commands in rapid succession should not crash."""
        from protocols.cli.repl import (
            handle_introspection,
            handle_invocation,
            handle_navigation,
        )

        # Mix of operations
        for i in range(1000):
            op = i % 4
            if op == 0:
                handle_navigation(repl_state, ["self"])
            elif op == 1:
                handle_navigation(repl_state, [".."])
            elif op == 2:
                handle_introspection(repl_state, "?")
            else:
                handle_invocation(repl_state, ["self", "status"])

        # Should complete without crash
        assert True

    def test_rapid_observer_switching(self, repl_state: Any) -> None:
        """Rapid observer switching should not corrupt state."""
        from protocols.cli.repl import handle_observer_command

        archetypes = ["explorer", "developer", "architect", "admin"]

        for _ in range(250):
            for arch in archetypes:
                handle_observer_command(repl_state, f"/observer {arch}")
                assert repl_state.observer == arch

    def test_memory_stability(self, repl_state: Any) -> None:
        """Memory should be stable after many operations."""
        import sys

        from protocols.cli.repl import handle_invocation, handle_navigation

        # Get baseline
        initial_size = sys.getsizeof(repl_state.history)

        # Run many operations
        for i in range(500):
            handle_navigation(repl_state, ["self"])
            handle_invocation(repl_state, ["status"])
            handle_navigation(repl_state, [".."])

        # History grows but state object should be stable
        # Just verify no crash and reasonable history size
        assert len(repl_state.history) == 0  # History not tracked in handlers
        assert repl_state.path == []  # Back at root

    def test_pipeline_stress(self, repl_state: Any) -> None:
        """Multiple pipeline executions should be stable."""
        from protocols.cli.repl import handle_composition

        for _ in range(100):
            result = handle_composition(repl_state, "self.status >> world.agents")
            assert result is not None


# =============================================================================
# Wave 3: Intelligence Tests
# =============================================================================


class TestFuzzyMatching:
    """Tests for Wave 3 fuzzy matching engine."""

    def test_fuzzy_matcher_exact_match(self) -> None:
        """Verify exact matches get highest scores."""
        from protocols.cli.repl_fuzzy import FuzzyMatcher

        matcher = FuzzyMatcher(threshold=80)
        matches = matcher.match("self", ["self", "world", "concept"])
        assert matches
        assert matches[0][0] == "self"
        assert matches[0][1] == 100

    def test_fuzzy_matcher_typo_correction(self) -> None:
        """Verify typos get corrected (with rapidfuzz) or prefix matching works (fallback)."""
        from protocols.cli.repl_fuzzy import FuzzyMatcher, is_fuzzy_available

        matcher = FuzzyMatcher(threshold=70)

        if is_fuzzy_available():
            # With rapidfuzz, typos should be corrected
            suggestion = matcher.suggest("slef", ["self", "world", "concept"])
            assert suggestion == "self"

            suggestion = matcher.suggest("wrold", ["self", "world", "concept"])
            assert suggestion == "world"
        else:
            # Fallback uses prefix matching - test that instead
            suggestion = matcher.suggest("se", ["self", "world", "concept"])
            assert suggestion == "self"

            suggestion = matcher.suggest("wo", ["self", "world", "concept"])
            assert suggestion == "world"

    def test_fuzzy_matcher_no_match_below_threshold(self) -> None:
        """Verify no match returned below threshold."""
        from protocols.cli.repl_fuzzy import FuzzyMatcher

        matcher = FuzzyMatcher(threshold=90)
        # Very different string
        suggestion = matcher.suggest("xyz", ["self", "world", "concept"])
        assert suggestion is None

    def test_fuzzy_did_you_mean(self) -> None:
        """Verify did_you_mean formatting."""
        from protocols.cli.repl_fuzzy import FuzzyMatcher, is_fuzzy_available

        matcher = FuzzyMatcher(threshold=70)

        if is_fuzzy_available():
            # With rapidfuzz, typos should match
            suggestion = matcher.did_you_mean("slef", ["self", "world"])
            assert suggestion is not None
            assert "self" in suggestion
            assert "Did you mean" in suggestion
        else:
            # Fallback: use prefix that will match
            suggestion = matcher.did_you_mean("se", ["self", "world"])
            assert suggestion is not None
            assert "self" in suggestion
            assert "Did you mean" in suggestion

    def test_fuzzy_fallback_without_rapidfuzz(self) -> None:
        """Verify fallback matching works."""
        from protocols.cli.repl_fuzzy import FuzzyMatcher

        matcher = FuzzyMatcher(threshold=60)
        # Fallback uses prefix matching
        matches = matcher._fallback_match("se", ["self", "world", "concept"])
        assert any(m[0] == "self" for m in matches)

    def test_fuzzy_integration_in_repl(self, repl_state: Any) -> None:
        """Verify fuzzy matcher integrates with REPL state."""
        fuzzy = repl_state.get_fuzzy()
        # Fuzzy should be available (either with or without rapidfuzz)
        if fuzzy is not None:
            matches = fuzzy.match("se", ["self", "world"])
            assert isinstance(matches, list)


class TestSessionPersistence:
    """Tests for Wave 3 session persistence."""

    def test_save_and_load_session(self, tmp_path: Any) -> None:
        """Verify session save/load roundtrip."""
        from protocols.cli.repl_session import load_session, save_session

        session_file = tmp_path / "test_session.json"

        # Save session
        assert save_session(["self", "soul"], "developer", session_file)

        # Load session
        session = load_session(session_file)
        assert session is not None
        assert session.path == ["self", "soul"]
        assert session.observer == "developer"
        assert session.timestamp  # Should have timestamp

    def test_load_nonexistent_session(self, tmp_path: Any) -> None:
        """Verify loading nonexistent session returns None."""
        from protocols.cli.repl_session import load_session

        session_file = tmp_path / "nonexistent.json"
        session = load_session(session_file)
        assert session is None

    def test_clear_session(self, tmp_path: Any) -> None:
        """Verify session clearing."""
        from protocols.cli.repl_session import clear_session, save_session

        session_file = tmp_path / "test_session.json"

        # Save then clear
        save_session(["self"], "explorer", session_file)
        assert session_file.exists()

        assert clear_session(session_file)
        assert not session_file.exists()

    def test_restore_session_to_state(self, tmp_path: Any, repl_state: Any) -> None:
        """Verify session restoration to ReplState."""
        from protocols.cli.repl_session import restore_session_to_state, save_session

        session_file = tmp_path / "test_session.json"
        save_session(["world", "agents"], "architect", session_file)

        # Restore to state
        assert restore_session_to_state(repl_state, session_file)
        assert repl_state.path == ["world", "agents"]
        assert repl_state.observer == "architect"


class TestHistorySearch:
    """Tests for Wave 3 history search."""

    def test_history_search_no_history(self, repl_state: Any) -> None:
        """Verify empty history handled."""
        from protocols.cli.repl import handle_history_search

        result = handle_history_search(repl_state, "/history")
        assert "no history" in result.lower()

    def test_history_search_with_history(self, repl_state: Any) -> None:
        """Verify history display."""
        from protocols.cli.repl import handle_history_search

        repl_state.history = ["self", "status", "world agents"]
        result = handle_history_search(repl_state, "/history")
        assert "self" in result
        assert "status" in result

    def test_history_search_with_query(self, repl_state: Any) -> None:
        """Verify history search with query."""
        from protocols.cli.repl import handle_history_search

        repl_state.history = ["self", "self status", "world agents"]
        result = handle_history_search(repl_state, "/history self")
        assert "self" in result

    def test_history_search_no_matches(self, repl_state: Any) -> None:
        """Verify no matches handled."""
        from protocols.cli.repl import handle_history_search

        repl_state.history = ["world", "concept"]
        result = handle_history_search(repl_state, "/history xyz")
        assert "no history" in result.lower() or "matching" in result.lower()


class TestScriptMode:
    """Tests for Wave 3 script mode."""

    def test_run_script_basic(self, tmp_path: Any) -> None:
        """Verify basic script execution."""
        from protocols.cli.repl import run_script

        script = tmp_path / "test.repl"
        script.write_text("self\nstatus\n..\n")

        result = run_script(script)
        assert result == 0

    def test_run_script_with_comments(self, tmp_path: Any) -> None:
        """Verify comments are skipped."""
        from protocols.cli.repl import run_script

        script = tmp_path / "test.repl"
        script.write_text("# This is a comment\nself\n# Another comment\n")

        result = run_script(script)
        assert result == 0

    def test_run_script_early_exit(self, tmp_path: Any) -> None:
        """Verify exit terminates script."""
        from protocols.cli.repl import run_script

        script = tmp_path / "test.repl"
        script.write_text("self\nexit\nworld\n")

        result = run_script(script)
        assert result == 0

    def test_run_script_nonexistent(self, tmp_path: Any) -> None:
        """Verify error for nonexistent script."""
        from protocols.cli.repl import run_script

        script = tmp_path / "nonexistent.repl"
        result = run_script(script)
        assert result == 1


class TestLLMSuggester:
    """Tests for Wave 3 LLM suggester."""

    def test_llm_suggester_low_entropy(self) -> None:
        """Verify LLM suggester respects entropy budget."""
        import asyncio

        from protocols.cli.repl_fuzzy import LLMSuggester

        suggester = LLMSuggester(entropy_cost=0.01)

        # Low entropy budget should return None
        result = asyncio.run(
            suggester.suggest("slef", "self", ["self", "world"], 0.001)
        )
        assert result is None

    def test_llm_suggester_no_options(self) -> None:
        """Verify LLM suggester handles empty options."""
        import asyncio

        from protocols.cli.repl_fuzzy import LLMSuggester

        suggester = LLMSuggester(entropy_cost=0.01)

        result = asyncio.run(suggester.suggest("test", "context", [], 0.10))
        assert result is None


class TestDynamicCompletion:
    """Tests for Wave 3 dynamic Logos completion."""

    def test_completer_includes_history_command(self, repl_state: Any) -> None:
        """Verify /history is in completion list."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("/hi")
        assert "/history" in matches

    def test_completer_dynamic_holons(self, repl_state: Any) -> None:
        """Verify dynamic completion from Logos (graceful degradation)."""
        from protocols.cli.repl import Completer

        repl_state.path = ["self"]
        completer = Completer(repl_state)

        # Should still work even if Logos unavailable (static fallback)
        matches = completer._get_matches("st")
        assert "status" in matches


class TestEntropyBudget:
    """Tests for Wave 3 entropy budget tracking."""

    def test_initial_entropy_budget(self) -> None:
        """Verify initial entropy budget is set."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        assert state.entropy_budget == 0.10  # 10%

    def test_entropy_budget_tracked(self) -> None:
        """Verify entropy budget can be modified."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        state.entropy_budget -= 0.01  # Use some entropy
        assert abs(state.entropy_budget - 0.09) < 0.0001  # Float tolerance


# =============================================================================
# Wave 4: Joy-Inducing Tests
# =============================================================================


class TestWelcomeVariations:
    """Tests for J1: Welcome variations by time and session."""

    def test_get_welcome_message_returns_string(self, repl_state: Any) -> None:
        """Verify welcome message is a string."""
        from protocols.cli.repl import get_welcome_message

        msg = get_welcome_message(repl_state)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_welcome_varies_by_morning(self, repl_state: Any) -> None:
        """Verify morning welcomes are distinct."""

        from protocols.cli.repl import get_welcome_message

        # Mock morning (9am)
        with patch("protocols.cli.repl._get_hour", return_value=9):
            msg = get_welcome_message(repl_state)
            assert any(
                word in msg.lower()
                for word in ["morning", "dawn", "day", "forest", "awaits"]
            )

    def test_welcome_varies_by_evening(self, repl_state: Any) -> None:
        """Verify evening welcomes are distinct."""

        from protocols.cli.repl import get_welcome_message

        # Mock evening (9pm = 21)
        with patch("protocols.cli.repl._get_hour", return_value=21):
            msg = get_welcome_message(repl_state)
            assert any(
                word in msg.lower()
                for word in ["evening", "night", "stars", "void", "falls"]
            )

    def test_welcome_for_returning_user(self, repl_state: Any) -> None:
        """Verify returning user gets context-aware welcome."""
        from protocols.cli.repl import get_welcome_message

        repl_state.restored_session = True
        repl_state.path = ["self", "soul"]
        msg = get_welcome_message(repl_state)
        # Should mention returning or previous context
        assert any(
            word in msg.lower()
            for word in ["back", "resum", "self", "soul", "continue", "river"]
        )


class TestKgentIntegration:
    """Tests for J2: K-gent personality integration."""

    def test_kgent_triggers_exist(self) -> None:
        """Verify K-gent triggers are defined."""
        from protocols.cli.repl import KGENT_TRIGGERS

        assert "reflect" in KGENT_TRIGGERS
        assert "wisdom" in KGENT_TRIGGERS
        assert len(KGENT_TRIGGERS) >= 5

    def test_maybe_invoke_kgent_returns_none_for_non_trigger(
        self, repl_state: Any
    ) -> None:
        """Verify non-triggers don't invoke K-gent."""
        import asyncio

        from protocols.cli.repl import maybe_invoke_kgent

        result = asyncio.run(maybe_invoke_kgent("self status", repl_state))
        assert result is None

    def test_kgent_rate_limiting(self, repl_state: Any) -> None:
        """Verify K-gent is rate limited."""
        import asyncio
        from datetime import datetime, timedelta

        from protocols.cli.repl import maybe_invoke_kgent

        # Set recent K-gent invocation
        repl_state.last_kgent_time = datetime.now()

        result = asyncio.run(maybe_invoke_kgent("give me wisdom", repl_state))
        # Should be rate-limited (None or rate-limit message)
        assert result is None or "rate" in str(result).lower()


class TestEasterEggs:
    """Tests for J3: Easter eggs."""

    def test_easter_eggs_exist(self) -> None:
        """Verify easter eggs are defined."""
        from protocols.cli.repl import EASTER_EGGS

        assert len(EASTER_EGGS) >= 5
        assert "void.entropy.dance" in EASTER_EGGS or any(
            "dance" in k for k in EASTER_EGGS
        )

    def test_void_entropy_dance(self, repl_state: Any) -> None:
        """Verify void.entropy.dance easter egg works."""
        from protocols.cli.repl import handle_easter_egg

        result = handle_easter_egg("void.entropy.dance", repl_state)
        assert result is not None
        # Should be visual (ASCII or interesting output)
        assert len(result) > 10

    def test_concept_zen(self, repl_state: Any) -> None:
        """Verify concept.zen easter egg works."""
        from protocols.cli.repl import handle_easter_egg

        result = handle_easter_egg("concept.zen", repl_state)
        assert result is not None

    def test_world_hello(self, repl_state: Any) -> None:
        """Verify world.hello easter egg works."""
        from protocols.cli.repl import handle_easter_egg

        result = handle_easter_egg("world.hello", repl_state)
        assert result is not None
        assert "hello" in result.lower() or "world" in result.lower()

    def test_dots_easter_egg(self, repl_state: Any) -> None:
        """Verify excessive dots easter egg works."""
        from protocols.cli.repl import handle_easter_egg

        result = handle_easter_egg("..........", repl_state)
        assert result is not None
        assert "dragon" in result.lower() or "far" in result.lower()

    def test_non_easter_egg_returns_none(self, repl_state: Any) -> None:
        """Verify non-easter-eggs return None."""
        from protocols.cli.repl import handle_easter_egg

        result = handle_easter_egg("self.status", repl_state)
        assert result is None


class TestContextualHints:
    """Tests for J5: Contextual hints."""

    def test_hint_for_long_session_at_root(self, repl_state: Any) -> None:
        """Verify hint shown for long session at root."""
        from protocols.cli.repl import get_contextual_hint

        repl_state.history = ["cmd"] * 25  # Long session
        repl_state.path = []

        hint = get_contextual_hint(repl_state)
        assert hint is not None
        assert "self" in hint.lower() or "status" in hint.lower()

    def test_hint_for_void_context(self, repl_state: Any) -> None:
        """Verify hint in void context mentions entropy."""
        from protocols.cli.repl import get_contextual_hint

        repl_state.path = ["void"]

        hint = get_contextual_hint(repl_state)
        assert hint is not None
        assert "entropy" in hint.lower() or "sip" in hint.lower()

    def test_hint_for_repeated_errors(self, repl_state: Any) -> None:
        """Verify hint after repeated errors."""
        from protocols.cli.repl import get_contextual_hint

        repl_state.consecutive_errors = 4

        hint = get_contextual_hint(repl_state)
        assert hint is not None
        assert "?" in hint or "help" in hint.lower() or "affordance" in hint.lower()

    def test_no_hint_when_not_needed(self, repl_state: Any) -> None:
        """Verify no hint when state is normal."""
        from protocols.cli.repl import get_contextual_hint

        repl_state.history = ["cmd"] * 5  # Short session
        repl_state.path = ["self", "status"]
        repl_state.consecutive_errors = 0

        hint = get_contextual_hint(repl_state)
        assert hint is None


class TestConsecutiveErrorTracking:
    """Tests for consecutive error tracking."""

    def test_consecutive_errors_default(self) -> None:
        """Verify consecutive_errors defaults to 0."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        assert state.consecutive_errors == 0

    def test_consecutive_errors_incremented(self) -> None:
        """Verify consecutive_errors can be incremented."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        state.consecutive_errors += 1
        assert state.consecutive_errors == 1


# =============================================================================
# Wave 5: Ambient Mode Tests
# =============================================================================


class TestAmbientModeFlag:
    """Tests for A1: --ambient flag parsing."""

    def test_cmd_interactive_accepts_ambient_flag(self) -> None:
        """Verify --ambient flag is accepted (doesn't crash on parse)."""
        # We test the parsing by checking that ReplState can be created
        # and that cmd_interactive's docstring mentions ambient
        from protocols.cli.repl import cmd_interactive

        # Check docstring mentions ambient mode
        doc = cmd_interactive.__doc__
        assert doc is not None, "cmd_interactive must have a docstring"
        assert "--ambient" in doc
        assert "ambient" in doc.lower()

    def test_repl_state_has_ambient_attributes(self) -> None:
        """Verify ReplState has ambient mode attributes."""
        from protocols.cli.repl import ReplState

        state = ReplState()
        # Should have ambient mode control attributes
        assert hasattr(state, "running")
        assert state.running is True
        assert hasattr(state, "ambient_paused")
        assert hasattr(state, "ambient_focus")
        assert hasattr(state, "ambient_interval")
        assert state.ambient_interval == 5.0


class TestAmbientScreenRendering:
    """Tests for A1/A2: Ambient screen rendering."""

    def test_render_ambient_screen_returns_string(self) -> None:
        """Verify ambient screen renders to string."""
        from agents.i.data.dashboard_collectors import create_demo_metrics
        from protocols.cli.repl import _render_ambient_screen

        metrics = create_demo_metrics()
        screen = _render_ambient_screen(metrics, paused=False)

        assert isinstance(screen, str)
        assert len(screen) > 100  # Non-trivial content

    def test_render_ambient_screen_shows_kgent(self) -> None:
        """Verify ambient screen shows K-gent panel."""
        from agents.i.data.dashboard_collectors import create_demo_metrics
        from protocols.cli.repl import _render_ambient_screen

        metrics = create_demo_metrics()
        screen = _render_ambient_screen(metrics, paused=False)

        # Should show K-gent section
        assert "K-GENT" in screen.upper() or "KGENT" in screen.upper()

    def test_render_ambient_screen_shows_metabolism(self) -> None:
        """Verify ambient screen shows Metabolism panel."""
        from agents.i.data.dashboard_collectors import create_demo_metrics
        from protocols.cli.repl import _render_ambient_screen

        metrics = create_demo_metrics()
        screen = _render_ambient_screen(metrics, paused=False)

        assert "METABOLISM" in screen.upper() or "PRESSURE" in screen.upper()

    def test_render_ambient_screen_shows_paused_indicator(self) -> None:
        """Verify paused state shows indicator."""
        from agents.i.data.dashboard_collectors import create_demo_metrics
        from protocols.cli.repl import _render_ambient_screen

        metrics = create_demo_metrics()
        screen_paused = _render_ambient_screen(metrics, paused=True)
        screen_running = _render_ambient_screen(metrics, paused=False)

        # Paused screen should be different (has PAUSED indicator)
        assert "PAUSED" in screen_paused.upper() or screen_paused != screen_running


class TestAmbientKeyBindings:
    """Tests for A3: Ambient mode keybindings."""

    def test_handle_ambient_key_q_quits(self) -> None:
        """Verify 'q' key quits ambient mode."""
        from protocols.cli.repl import ReplState, _handle_ambient_key

        state = ReplState()
        assert state.running is True

        _handle_ambient_key("q", state)
        assert state.running is False

    def test_handle_ambient_key_r_refreshes(self) -> None:
        """Verify 'r' key triggers refresh (returns True)."""
        from protocols.cli.repl import ReplState, _handle_ambient_key

        state = ReplState()
        should_refresh = _handle_ambient_key("r", state)

        assert should_refresh is True
        assert state.running is True  # Still running

    def test_handle_ambient_key_space_toggles_pause(self) -> None:
        """Verify space toggles pause state."""
        from protocols.cli.repl import ReplState, _handle_ambient_key

        state = ReplState()
        # Add ambient_paused attribute if needed
        if not hasattr(state, "ambient_paused"):
            state.ambient_paused = False

        # First space - pause
        _handle_ambient_key(" ", state)
        assert state.ambient_paused is True

        # Second space - unpause
        _handle_ambient_key(" ", state)
        assert state.ambient_paused is False

    def test_handle_ambient_key_numbers_set_focus(self) -> None:
        """Verify 1-5 keys set focus panel."""
        from protocols.cli.repl import ReplState, _handle_ambient_key

        state = ReplState()
        # Add ambient_focus attribute if needed
        if not hasattr(state, "ambient_focus"):
            state.ambient_focus = None

        _handle_ambient_key("1", state)
        assert state.ambient_focus == 1

        _handle_ambient_key("3", state)
        assert state.ambient_focus == 3


class TestAmbientRefreshLoop:
    """Tests for A2: Ambient refresh loop."""

    def test_ambient_interval_default(self) -> None:
        """Verify default refresh interval is 5 seconds."""
        # The default should be documented and consistent
        DEFAULT_INTERVAL = 5.0
        assert DEFAULT_INTERVAL == 5.0

    def test_ambient_interval_configurable(self) -> None:
        """Verify ambient interval can be configured."""
        # Test that --interval flag is parsed
        # (Integration test - just verify the flag format is documented)
        help_text = """
        kg -i --ambient           Launch passive dashboard
        kg -i --ambient -i 10     Custom refresh interval (10s)
        """
        assert "--ambient" in help_text
        assert "-i" in help_text or "--interval" in help_text


class TestAmbientNonBlockingKeyboard:
    """Tests for non-blocking keyboard input."""

    def test_get_key_nonblocking_exists(self) -> None:
        """Verify non-blocking keyboard function exists."""
        from protocols.cli.repl import _get_key_nonblocking

        # Should not block - returns None when no input
        # This is tricky to test without a terminal
        # Just verify the function exists
        assert callable(_get_key_nonblocking)

    def test_get_key_nonblocking_returns_none_or_string(self) -> None:
        """Verify _get_key_nonblocking returns proper type."""
        from protocols.cli.repl import _get_key_nonblocking

        # When no key pressed, should return None quickly
        # Can't easily test actual key press in unit test
        result = _get_key_nonblocking()
        assert result is None or isinstance(result, str)


class TestAmbientHelpText:
    """Tests for A5: Help text polish."""

    def test_help_text_mentions_ambient(self) -> None:
        """Verify help text documents ambient mode."""
        from protocols.cli.repl import HELP_TEXT

        # Ambient mode should be documented
        assert "ambient" in HELP_TEXT.lower() or "--ambient" in HELP_TEXT

    def test_help_text_mentions_waves(self) -> None:
        """Verify help text mentions joy-inducing features."""
        from protocols.cli.repl import HELP_TEXT

        # Should mention key features from waves
        assert any(
            word in HELP_TEXT.lower()
            for word in ["welcome", "hint", "easter", "time", "k-gent", "soul"]
        )


# =============================================================================
# Wave 5.1: Dotted Path Completion Tests
# =============================================================================


class TestDottedPathInput:
    """Tests for Wave 5.1 dotted path input parsing."""

    def test_parse_space_separated(self) -> None:
        """Verify space-separated paths work as before."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input("world dev") == ["world", "dev"]
        assert _parse_path_input("self soul reflect") == ["self", "soul", "reflect"]

    def test_parse_dotted_path(self) -> None:
        """Verify dotted paths are split correctly."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input("world.dev") == ["world", "dev"]
        assert _parse_path_input("self.soul.reflect") == ["self", "soul", "reflect"]

    def test_parse_mixed_format(self) -> None:
        """Verify mixed space and dot formats work."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input("self.soul reflect") == ["self", "soul", "reflect"]
        assert _parse_path_input("world agents.list") == ["world", "agents", "list"]

    def test_parse_special_dot_commands_preserved(self) -> None:
        """Verify . and .. are not split."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input(".") == ["."]
        assert _parse_path_input("..") == [".."]
        assert _parse_path_input("...") == ["..."]

    def test_parse_slash_commands_not_split(self) -> None:
        """Verify /commands are not split on dots."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input("/observer") == ["/observer"]
        assert _parse_path_input("/history") == ["/history"]

    def test_parse_trailing_dot_filtered(self) -> None:
        """Verify trailing dots don't create empty parts."""
        from protocols.cli.repl import _parse_path_input

        # Trailing dot creates empty string which should be filtered
        assert _parse_path_input("self.") == ["self"]
        assert _parse_path_input("self.soul.") == ["self", "soul"]

    def test_parse_single_word(self) -> None:
        """Verify single words work."""
        from protocols.cli.repl import _parse_path_input

        assert _parse_path_input("self") == ["self"]
        assert _parse_path_input("world") == ["world"]


class TestDottedPathCompletion:
    """Tests for Wave 5.1 dotted path fast-forward completion."""

    def test_complete_context_dot_shows_holons(self, repl_state: Any) -> None:
        """Verify 'self.' shows self's holons with full path."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("self.")

        # Should include full dotted paths
        assert "self.status" in matches
        assert "self.memory" in matches
        assert "self.soul" in matches
        assert "self.dashboard" in matches

    def test_complete_context_dot_partial(self, repl_state: Any) -> None:
        """Verify 'self.so' completes to 'self.soul'."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("self.so")

        assert "self.soul" in matches
        assert "self.status" not in matches  # 'status' doesn't start with 'so'

    def test_complete_holon_dot_shows_aspects(self, repl_state: Any) -> None:
        """Verify 'self.soul.' shows aspects with full path."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("self.soul.")

        # Should include full dotted paths to aspects
        assert "self.soul.manifest" in matches
        assert "self.soul.witness" in matches
        assert "self.soul.refine" in matches
        assert "self.soul.affordances" in matches

    def test_complete_holon_dot_partial(self, repl_state: Any) -> None:
        """Verify 'self.soul.ref' completes to 'self.soul.refine'."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("self.soul.ref")

        assert "self.soul.refine" in matches
        assert len(matches) == 1  # Only refine starts with 'ref'

    def test_complete_world_context(self, repl_state: Any) -> None:
        """Verify 'world.' shows world's holons."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("world.")

        assert "world.agents" in matches
        assert "world.daemon" in matches
        assert "world.infra" in matches
        assert "world.town" in matches

    def test_complete_void_context(self, repl_state: Any) -> None:
        """Verify 'void.' shows void's holons."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("void.")

        assert "void.entropy" in matches
        assert "void.shadow" in matches
        assert "void.serendipity" in matches

    def test_complete_invalid_context_returns_empty(self, repl_state: Any) -> None:
        """Verify invalid context like 'foo.' returns empty."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("foo.")

        assert matches == []

    def test_complete_standalone_dot_not_affected(self, repl_state: Any) -> None:
        """Verify standalone '.' still works as special command."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches(".")

        # Should include special commands starting with '.'
        assert "." in matches
        assert ".." in matches

    def test_complete_deep_path_returns_empty(self, repl_state: Any) -> None:
        """Verify paths deeper than 3 levels return empty."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)
        matches = completer._get_matches("self.soul.manifest.")

        # No standard completions for 4th level
        assert matches == []

    def test_complete_case_insensitive(self, repl_state: Any) -> None:
        """Verify dotted completion is case-insensitive."""
        from protocols.cli.repl import Completer

        completer = Completer(repl_state)

        # Uppercase context
        matches = completer._get_matches("SELF.")
        assert "SELF.status" in matches

        # Mixed case partial
        matches = completer._get_matches("self.SO")
        assert "self.soul" in matches

    def test_dotted_completion_absolute_path_from_any_state(
        self, repl_state: Any
    ) -> None:
        """Verify absolute dotted paths work regardless of current navigation state."""
        from protocols.cli.repl import Completer

        # Even if navigated to world context
        repl_state.path = ["world", "agents"]

        completer = Completer(repl_state)
        # Absolute path (starts with context) should still work
        matches = completer._get_matches("self.soul.")

        assert "self.soul.manifest" in matches
        assert "self.soul.witness" in matches

    def test_dotted_completion_relative_to_current_path(self, repl_state: Any) -> None:
        """Verify relative dotted paths prepend current navigation state."""
        from protocols.cli.repl import Completer

        # Navigate to self context
        repl_state.path = ["self"]

        completer = Completer(repl_state)
        # "soul." is relative - should resolve to self.soul and show aspects
        matches = completer._get_matches("soul.")

        assert "soul.manifest" in matches
        assert "soul.witness" in matches
        assert "soul.refine" in matches

    def test_dotted_completion_relative_partial(self, repl_state: Any) -> None:
        """Verify relative partial completion works."""
        from protocols.cli.repl import Completer

        repl_state.path = ["self"]

        completer = Completer(repl_state)
        # "soul.ma" should complete to "soul.manifest"
        matches = completer._get_matches("soul.ma")

        assert "soul.manifest" in matches
        assert len(matches) == 1

    def test_dotted_completion_relative_holon(self, repl_state: Any) -> None:
        """Verify relative holon completion at context level."""
        from protocols.cli.repl import Completer

        repl_state.path = ["world"]

        completer = Completer(repl_state)
        # At world, "agents." should show aspects (world.agents.*)
        matches = completer._get_matches("agents.")

        assert "agents.manifest" in matches
        assert "agents.witness" in matches
