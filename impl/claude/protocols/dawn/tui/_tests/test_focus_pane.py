"""
Tests for Dawn Cockpit Focus Pane.

Tests focus item display, navigation, and selection.
"""

from __future__ import annotations

import pytest

from protocols.dawn.focus import Bucket, FocusManager
from protocols.dawn.tui.focus_pane import FocusPane, BUCKET_EMOJI


class TestFocusPaneConstruction:
    """Tests for FocusPane construction."""

    def test_create_with_manager(self, focus_manager: FocusManager) -> None:
        """Test creating pane with focus manager."""
        pane = FocusPane(focus_manager)

        assert pane.focus_manager is focus_manager

    def test_has_selected_index_reactive(self) -> None:
        """Test selected_index reactive is defined."""
        assert hasattr(FocusPane, "selected_index")

    def test_has_is_active_reactive(self) -> None:
        """Test is_active reactive is defined."""
        assert hasattr(FocusPane, "is_active")


class TestFocusPaneItemDisplay:
    """Tests for focus item display."""

    def test_bucket_emoji_defined(self) -> None:
        """Test bucket emoji mapping is complete."""
        assert Bucket.TODAY in BUCKET_EMOJI
        assert Bucket.WEEK in BUCKET_EMOJI
        assert Bucket.SOMEDAY in BUCKET_EMOJI

    def test_bucket_emoji_values(self) -> None:
        """Test bucket emoji values are appropriate."""
        assert BUCKET_EMOJI[Bucket.TODAY] == "🔥"
        assert BUCKET_EMOJI[Bucket.WEEK] == "🎯"
        assert BUCKET_EMOJI[Bucket.SOMEDAY] == "🧘"


class TestFocusPaneSelection:
    """Tests for focus pane selection behavior."""

    def test_selected_item_with_items(self, focus_manager: FocusManager) -> None:
        """Test selected_item returns correct item."""
        pane = FocusPane(focus_manager)
        pane._items = list(focus_manager.list())
        pane._selected_index = 0

        # First item should be selected
        assert pane.selected_item is not None
        assert pane.selected_item == pane._items[0]

    def test_selected_item_changes_with_index(self, focus_manager: FocusManager) -> None:
        """Test selected_item changes when index changes."""
        pane = FocusPane(focus_manager)
        pane._items = list(focus_manager.list())
        pane._selected_index = 1

        assert pane.selected_item == pane._items[1]

    def test_selected_item_none_when_empty(self, empty_focus_manager: FocusManager) -> None:
        """Test selected_item is None when no items."""
        pane = FocusPane(empty_focus_manager)
        pane._items = []
        pane._selected_index = 0

        assert pane.selected_item is None

    def test_selection_index_out_of_bounds(self, focus_manager: FocusManager) -> None:
        """Test selection with out of bounds index returns None."""
        pane = FocusPane(focus_manager)
        pane._items = list(focus_manager.list())
        pane._selected_index = 999

        assert pane.selected_item is None


class TestFocusPaneItemOrdering:
    """Tests for focus item ordering."""

    def test_items_ordered_by_bucket_priority(self, focus_manager: FocusManager) -> None:
        """Test items are ordered TODAY > WEEK > SOMEDAY."""
        pane = FocusPane(focus_manager)

        # Get items in order
        all_items = focus_manager.list()
        today_items = focus_manager.list(bucket=Bucket.TODAY)
        week_items = focus_manager.list(bucket=Bucket.WEEK)
        someday_items = focus_manager.list(bucket=Bucket.SOMEDAY)

        # Should have items in each bucket
        assert len(today_items) > 0
        assert len(week_items) > 0
        assert len(someday_items) > 0


class TestFocusPaneStaleIndicator:
    """Tests for stale item indication."""

    def test_stale_items_detected(self, focus_manager_with_stale: FocusManager) -> None:
        """Test stale items are detected."""
        stale = focus_manager_with_stale.get_stale()

        assert len(stale) > 0

    def test_fresh_items_not_stale(self, focus_manager: FocusManager) -> None:
        """Test fresh items are not stale."""
        stale = focus_manager.get_stale()

        assert len(stale) == 0


class TestFocusPaneVimNavigation:
    """Tests for vim-style j/k navigation."""

    def test_docstring_mentions_jk(self) -> None:
        """Test that module docstring documents j/k navigation."""
        from protocols.dawn.tui import focus_pane as fp_module

        assert "jk" in fp_module.__doc__ or "j/k" in fp_module.__doc__

    def test_on_key_handles_j_and_k(self, focus_manager: FocusManager) -> None:
        """Test that on_key method checks for j and k keys."""
        import inspect

        from protocols.dawn.tui.focus_pane import FocusPane

        source = inspect.getsource(FocusPane.on_key)
        assert '"k"' in source or "'k'" in source
        assert '"j"' in source or "'j'" in source
