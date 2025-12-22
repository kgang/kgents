"""
Fixtures for Dawn Cockpit TUI tests.

Provides common test fixtures for TUI components.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from protocols.dawn.focus import Bucket, FocusItem, FocusManager
from protocols.dawn.snippets import SnippetLibrary


@pytest.fixture
def focus_manager() -> FocusManager:
    """Create a FocusManager with test data (no disk persistence)."""
    manager = FocusManager(auto_persist=False)

    # Add items in different buckets
    manager.add("spec/protocols/dawn-cockpit.md", label="Dawn Spec", bucket=Bucket.TODAY)
    manager.add("plans/portal-fullstack.md", label="Portal Tests", bucket=Bucket.TODAY)
    manager.add("impl/claude/services/witness/", label="Witness Service", bucket=Bucket.WEEK)
    manager.add("spec/patterns/", label="Patterns Review", bucket=Bucket.SOMEDAY)

    return manager


@pytest.fixture
def focus_manager_with_stale(focus_manager: FocusManager) -> FocusManager:
    """Create a FocusManager with some stale items."""
    # Add a stale item (artificially old)

    old_time = datetime.now() - timedelta(hours=48)

    # Add and then manually modify to make stale
    item = focus_manager.add("old/stale/file.md", label="Stale Item", bucket=Bucket.TODAY)

    # Replace with stale version
    stale_item = FocusItem(
        id=item.id,
        label=item.label,
        target=item.target,
        bucket=item.bucket,
        added_at=old_time,
        last_touched=old_time,
    )
    focus_manager._items[item.id] = stale_item

    return focus_manager


@pytest.fixture
def snippet_library() -> SnippetLibrary:
    """Create a SnippetLibrary with test data (no disk persistence)."""
    lib = SnippetLibrary(auto_persist=False)
    lib.load_defaults()

    # Add a custom snippet for testing
    lib.add_custom("Test Note", "This is a test note content")

    return lib


@pytest.fixture
def empty_focus_manager() -> FocusManager:
    """Create an empty FocusManager (no disk persistence)."""
    return FocusManager(auto_persist=False)


@pytest.fixture
def empty_snippet_library() -> SnippetLibrary:
    """Create an empty SnippetLibrary (no disk persistence)."""
    return SnippetLibrary(auto_persist=False)
