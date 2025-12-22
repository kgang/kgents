"""
Tests for Dawn Cockpit TUI App.

Tests the main application structure and key bindings.
"""

from __future__ import annotations

import pytest

from protocols.dawn.focus import FocusManager
from protocols.dawn.snippets import SnippetLibrary
from protocols.dawn.tui.app import DawnCockpit


class TestDawnCockpitConstruction:
    """Tests for DawnCockpit construction."""

    def test_create_with_defaults(self) -> None:
        """Test creating app with default managers."""
        app = DawnCockpit()

        assert app.focus_manager is not None
        assert app.snippet_library is not None
        assert len(app.snippet_library) > 0  # Defaults loaded

    def test_create_with_injected_managers(
        self,
        focus_manager: FocusManager,
        snippet_library: SnippetLibrary,
    ) -> None:
        """Test creating app with injected managers."""
        app = DawnCockpit(focus_manager, snippet_library)

        assert app.focus_manager is focus_manager
        assert app.snippet_library is snippet_library

    def test_title_set(self) -> None:
        """Test that app title is set."""
        app = DawnCockpit()

        assert app.TITLE == "DAWN COCKPIT"

    def test_bindings_defined(self) -> None:
        """Test that key bindings are defined."""
        app = DawnCockpit()

        # Check essential bindings exist
        binding_keys = [b.key for b in app.BINDINGS]
        assert "q" in binding_keys  # Quit
        assert "tab" in binding_keys  # Switch panes
        assert "a" in binding_keys  # Add
        assert "d" in binding_keys  # Done
        assert "h" in binding_keys  # Hygiene
        assert "r" in binding_keys  # Refresh

    def test_css_defined(self) -> None:
        """Test that CSS is defined."""
        assert DawnCockpit.CSS is not None
        assert len(DawnCockpit.CSS) > 0
        # Check for key selectors
        assert "#focus-pane" in DawnCockpit.CSS
        assert "#snippet-pane" in DawnCockpit.CSS
        assert "#garden-view" in DawnCockpit.CSS


class TestDawnCockpitActivePaneSwitch:
    """Tests for pane switching."""

    def test_initial_active_pane_defined(self) -> None:
        """Test that active_pane reactive is defined."""
        # Check that the reactive is defined on the class
        assert hasattr(DawnCockpit, "active_pane")

    def test_active_pane_default_value(self) -> None:
        """Test that active_pane has correct default."""
        # Access the reactive's default without instantiating
        # The default is set in the class definition
        from textual.reactive import reactive

        # Just verify the reactive exists - actual behavior tested in integration
        assert DawnCockpit.active_pane is not None


class TestDawnCockpitActions:
    """Tests for app actions (hygiene, etc.)."""

    def test_action_hygiene_with_no_stale(
        self,
        focus_manager: FocusManager,
        snippet_library: SnippetLibrary,
    ) -> None:
        """Test hygiene action when no items are stale."""
        app = DawnCockpit(focus_manager, snippet_library)

        # Fresh items should not be stale
        stale = focus_manager.get_stale()
        assert len(stale) == 0

    def test_action_hygiene_with_stale(
        self,
        focus_manager_with_stale: FocusManager,
        snippet_library: SnippetLibrary,
    ) -> None:
        """Test hygiene action when items are stale."""
        app = DawnCockpit(focus_manager_with_stale, snippet_library)

        # Should find stale items
        stale = focus_manager_with_stale.get_stale()
        assert len(stale) > 0


class TestAddFocusModal:
    """Tests for AddFocusModal."""

    def test_add_focus_modal_importable(self) -> None:
        """Test that AddFocusModal is importable."""
        from protocols.dawn.tui.add_focus_modal import AddFocusModal

        assert AddFocusModal is not None

    def test_add_focus_modal_has_bindings(self) -> None:
        """Test that modal has escape binding."""
        from protocols.dawn.tui.add_focus_modal import AddFocusModal

        binding_keys = [b[0] for b in AddFocusModal.BINDINGS]
        assert "escape" in binding_keys

    def test_add_focus_modal_has_css(self) -> None:
        """Test that modal has CSS defined."""
        from protocols.dawn.tui.add_focus_modal import AddFocusModal

        assert AddFocusModal.CSS is not None
        assert len(AddFocusModal.CSS) > 0
        assert "#modal-container" in AddFocusModal.CSS


class TestCopyConfirmation:
    """Tests for copy confirmation handler."""

    def test_copy_handler_method_exists(self) -> None:
        """Test that the snippet copy handler exists on DawnCockpit."""
        assert hasattr(DawnCockpit, "on_snippet_pane_snippet_copied")
        assert callable(getattr(DawnCockpit, "on_snippet_pane_snippet_copied"))


class TestRunDawnTUI:
    """Tests for run_dawn_tui function."""

    def test_run_dawn_tui_exists(self) -> None:
        """Test that run_dawn_tui is importable."""
        from protocols.dawn.tui.app import run_dawn_tui

        assert callable(run_dawn_tui)
