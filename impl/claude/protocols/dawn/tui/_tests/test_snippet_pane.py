"""
Tests for Dawn Cockpit Snippet Pane.

Tests snippet display, navigation, and copy behavior.
"""

from __future__ import annotations

import pytest

from protocols.dawn.snippets import SnippetLibrary
from protocols.dawn.tui.snippet_pane import SnippetPane, SNIPPET_ICONS, SNIPPET_COLORS


class TestSnippetPaneConstruction:
    """Tests for SnippetPane construction."""

    def test_create_with_library(self, snippet_library: SnippetLibrary) -> None:
        """Test creating pane with snippet library."""
        pane = SnippetPane(snippet_library)

        assert pane.snippet_library is snippet_library

    def test_has_selected_index_property(self) -> None:
        """Test selected_index property is defined."""
        assert hasattr(SnippetPane, "selected_index")

    def test_has_is_active_reactive(self) -> None:
        """Test is_active reactive is defined."""
        assert hasattr(SnippetPane, "is_active")


class TestSnippetPaneIcons:
    """Tests for snippet icon mapping."""

    def test_snippet_icons_defined(self) -> None:
        """Test snippet icon mapping is complete."""
        assert "static" in SNIPPET_ICONS
        assert "query" in SNIPPET_ICONS
        assert "custom" in SNIPPET_ICONS

    def test_snippet_icons_values(self) -> None:
        """Test snippet icon values are appropriate."""
        assert SNIPPET_ICONS["static"] == "▶"
        assert SNIPPET_ICONS["query"] == "⟳"
        assert SNIPPET_ICONS["custom"] == "★"

    def test_snippet_colors_defined(self) -> None:
        """Test snippet color mapping is complete."""
        assert "static" in SNIPPET_COLORS
        assert "query" in SNIPPET_COLORS
        assert "custom" in SNIPPET_COLORS


class TestSnippetPaneSelection:
    """Tests for snippet pane selection behavior."""

    def test_selected_snippet_with_items(self, snippet_library: SnippetLibrary) -> None:
        """Test selected_snippet returns correct snippet."""
        pane = SnippetPane(snippet_library)
        pane._snippets = snippet_library.list_all()
        pane._selected_index = 0

        # First snippet should be selected
        assert pane.selected_snippet is not None
        assert pane.selected_snippet == pane._snippets[0]

    def test_selected_snippet_changes_with_index(self, snippet_library: SnippetLibrary) -> None:
        """Test selected_snippet changes when index changes."""
        pane = SnippetPane(snippet_library)
        pane._snippets = snippet_library.list_all()
        pane._selected_index = 1

        assert pane.selected_snippet == pane._snippets[1]

    def test_selected_snippet_none_when_empty(self, empty_snippet_library: SnippetLibrary) -> None:
        """Test selected_snippet is None when no snippets."""
        pane = SnippetPane(empty_snippet_library)
        pane._snippets = []
        pane._selected_index = 0

        assert pane.selected_snippet is None


class TestSnippetPaneCopy:
    """Tests for snippet copy behavior."""

    def test_copy_callback_can_be_set(self, snippet_library: SnippetLibrary) -> None:
        """Test that copy callback can be set."""
        pane = SnippetPane(snippet_library)

        copied_content: list[str] = []

        def capture_copy(content: str) -> None:
            copied_content.append(content)

        pane.set_copy_callback(capture_copy)
        assert pane._copy_callback is capture_copy

    def test_copy_selected_uses_callback(self, snippet_library: SnippetLibrary) -> None:
        """Test that copy uses the callback."""
        pane = SnippetPane(snippet_library)
        pane._snippets = snippet_library.list_all()
        pane._selected_index = 0

        copied_content: list[str] = []

        def capture_copy(content: str) -> None:
            copied_content.append(content)

        pane.set_copy_callback(capture_copy)
        pane._copy_selected()

        # Should have captured the content
        assert len(copied_content) == 1

    def test_copy_selected_no_crash_when_empty(self, empty_snippet_library: SnippetLibrary) -> None:
        """Test copy doesn't crash when no snippets."""
        pane = SnippetPane(empty_snippet_library)
        pane._snippets = []
        pane._selected_index = 0

        # Should not raise
        pane._copy_selected()


class TestSnippetPaneDelete:
    """Tests for custom snippet deletion."""

    def test_delete_custom_snippet(self, snippet_library: SnippetLibrary) -> None:
        """Test deleting a custom snippet."""
        pane = SnippetPane(snippet_library)
        pane._snippets = snippet_library.list_all()

        initial_count = len(snippet_library.list_custom())
        assert initial_count > 0  # From fixture

        # Find index of first custom snippet
        for i, snippet in enumerate(pane._snippets):
            if snippet.to_dict()["type"] == "custom":
                pane._selected_index = i
                break

        pane._delete_selected()
        pane._snippets = snippet_library.list_all()  # Refresh

        # Should have one fewer custom snippet
        assert len(snippet_library.list_custom()) == initial_count - 1

    def test_delete_static_snippet_does_nothing(self, snippet_library: SnippetLibrary) -> None:
        """Test deleting a static snippet does nothing."""
        pane = SnippetPane(snippet_library)
        pane._snippets = snippet_library.list_all()

        initial_count = len(snippet_library.list_static())

        # First snippet is static
        pane._selected_index = 0

        pane._delete_selected()

        # Should still have same count
        assert len(snippet_library.list_static()) == initial_count


class TestSnippetPaneVimNavigation:
    """Tests for vim-style j/k navigation."""

    def test_docstring_mentions_jk(self) -> None:
        """Test that module docstring documents j/k navigation."""
        from protocols.dawn.tui import snippet_pane as sp_module

        assert "jk" in sp_module.__doc__ or "j/k" in sp_module.__doc__

    def test_on_key_handles_j_and_k(self, snippet_library: SnippetLibrary) -> None:
        """Test that on_key method checks for j and k keys."""
        import inspect

        from protocols.dawn.tui.snippet_pane import SnippetPane

        source = inspect.getsource(SnippetPane.on_key)
        assert '"k"' in source or "'k'" in source
        assert '"j"' in source or "'j'" in source
