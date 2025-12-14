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
        """Verify multi-word input is not treated as navigation."""
        from protocols.cli.repl import handle_navigation

        repl_state.path = ["self"]
        result = handle_navigation(repl_state, ["status", "manifest"])
        assert result is None  # Not navigation, should be invocation


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
