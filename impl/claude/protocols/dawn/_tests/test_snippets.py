"""Tests for Dawn Cockpit snippet types."""

import time
from datetime import datetime

import pytest

from protocols.dawn.snippets import (
    CustomSnippet,
    QuerySnippet,
    SnippetLibrary,
    StaticSnippet,
)


class TestStaticSnippet:
    """Tests for StaticSnippet."""

    def test_to_dict_includes_type(self) -> None:
        """StaticSnippet serializes with type='static'."""
        snippet = StaticSnippet(
            id="test",
            kind="voice_anchor",
            label="Test Anchor",
            content="Test content",
            source="CLAUDE.md",
        )
        data = snippet.to_dict()
        assert data["type"] == "static"

    def test_to_dict_has_all_fields(self) -> None:
        """StaticSnippet serializes all fields."""
        snippet = StaticSnippet(
            id="test",
            kind="quote",
            label="Test Quote",
            content="The proof IS the decision",
            source="CLAUDE.md",
        )
        data = snippet.to_dict()
        assert data["id"] == "test"
        assert data["kind"] == "quote"
        assert data["label"] == "Test Quote"
        assert data["content"] == "The proof IS the decision"
        assert data["source"] == "CLAUDE.md"

    def test_kind_voice_anchor(self) -> None:
        """StaticSnippet can have kind='voice_anchor'."""
        snippet = StaticSnippet(
            id="va",
            kind="voice_anchor",
            label="Anchor",
            content="Content",
            source="source",
        )
        assert snippet.kind == "voice_anchor"

    def test_kind_pattern(self) -> None:
        """StaticSnippet can have kind='pattern'."""
        snippet = StaticSnippet(
            id="pat",
            kind="pattern",
            label="Container-Owns-Workflow",
            content="The container orchestrates...",
            source="docs/skills/crown-jewel-patterns.md",
        )
        assert snippet.kind == "pattern"


class TestQuerySnippet:
    """Tests for QuerySnippet."""

    def test_not_loaded_initially(self) -> None:
        """QuerySnippet starts unloaded."""
        snippet = QuerySnippet(
            id="test",
            kind="mark",
            label="Recent",
            query="self.witness.recent",
        )
        assert not snippet.is_loaded
        assert snippet.content is None

    def test_with_content_creates_new(self) -> None:
        """with_content returns new loaded snippet."""
        snippet = QuerySnippet(
            id="test",
            kind="mark",
            label="Recent",
            query="self.witness.recent",
        )
        loaded = snippet.with_content("Mark content here")
        assert loaded.is_loaded
        assert loaded.content == "Mark content here"

    def test_with_content_original_unchanged(self) -> None:
        """with_content leaves original unchanged (immutable)."""
        snippet = QuerySnippet(
            id="test",
            kind="mark",
            label="Recent",
            query="self.witness.recent",
        )
        loaded = snippet.with_content("Content")
        assert not snippet.is_loaded  # Original still unloaded

    def test_to_dict_includes_loaded_state_false(self) -> None:
        """to_dict includes is_loaded=False when unloaded."""
        snippet = QuerySnippet(
            id="test",
            kind="now",
            label="NOW",
            query="self.brain.now",
        )
        data = snippet.to_dict()
        assert data["type"] == "query"
        assert data["is_loaded"] is False
        assert data["content"] is None

    def test_to_dict_includes_loaded_state_true(self) -> None:
        """to_dict includes is_loaded=True when loaded."""
        snippet = QuerySnippet(
            id="test",
            kind="now",
            label="NOW",
            query="self.brain.now",
        ).with_content("NOW content")
        data = snippet.to_dict()
        assert data["is_loaded"] is True
        assert data["content"] == "NOW content"

    def test_kind_file(self) -> None:
        """QuerySnippet can have kind='file'."""
        snippet = QuerySnippet(
            id="f",
            kind="file",
            label="README",
            query="self.portal.expand(README.md)",
        )
        assert snippet.kind == "file"


class TestCustomSnippet:
    """Tests for CustomSnippet."""

    def test_to_dict_includes_type(self) -> None:
        """CustomSnippet serializes with type='custom'."""
        now = datetime.now()
        snippet = CustomSnippet(
            id="test",
            label="My Note",
            content="Remember this",
            created_at=now,
        )
        data = snippet.to_dict()
        assert data["type"] == "custom"

    def test_to_dict_has_all_fields(self) -> None:
        """CustomSnippet serializes all fields."""
        now = datetime.now()
        snippet = CustomSnippet(
            id="test",
            label="My Note",
            content="Remember this thing",
            created_at=now,
        )
        data = snippet.to_dict()
        assert data["id"] == "test"
        assert data["label"] == "My Note"
        assert data["content"] == "Remember this thing"
        assert "created_at" in data


class TestSnippetLibrary:
    """Tests for SnippetLibrary."""

    def test_add_static(self) -> None:
        """Add static snippet."""
        lib = SnippetLibrary()
        snippet = lib.add_static(
            kind="quote",
            label="Test Quote",
            content="The proof IS the decision",
            source="CLAUDE.md",
        )
        assert snippet.kind == "quote"
        assert len(lib.list_static()) == 1

    def test_add_query(self) -> None:
        """Add query snippet."""
        lib = SnippetLibrary()
        snippet = lib.add_query(
            kind="mark",
            label="Recent",
            query="self.witness.recent",
        )
        assert snippet.kind == "mark"
        assert not snippet.is_loaded
        assert len(lib.list_query()) == 1

    def test_add_custom(self) -> None:
        """Add custom snippet."""
        lib = SnippetLibrary()
        snippet = lib.add_custom(
            label="My Note",
            content="Remember this",
        )
        assert snippet.label == "My Note"
        assert len(lib.list_custom()) == 1

    def test_remove_custom(self) -> None:
        """Remove custom snippet."""
        lib = SnippetLibrary()
        snippet = lib.add_custom("Note", "Content")
        assert lib.remove_custom(snippet.id)
        assert lib.get(snippet.id) is None

    def test_remove_custom_nonexistent_returns_false(self) -> None:
        """Remove returns False for nonexistent ID."""
        lib = SnippetLibrary()
        assert not lib.remove_custom("nonexistent")

    def test_get_static_by_id(self) -> None:
        """Get static snippet by ID."""
        lib = SnippetLibrary()
        static = lib.add_static("quote", "Q", "Content", "src")
        assert lib.get(static.id) == static

    def test_get_query_by_id(self) -> None:
        """Get query snippet by ID."""
        lib = SnippetLibrary()
        query = lib.add_query("mark", "M", "path")
        assert lib.get(query.id) == query

    def test_get_custom_by_id(self) -> None:
        """Get custom snippet by ID."""
        lib = SnippetLibrary()
        custom = lib.add_custom("C", "Custom")
        assert lib.get(custom.id) == custom

    def test_get_nonexistent_returns_none(self) -> None:
        """Get returns None for nonexistent ID."""
        lib = SnippetLibrary()
        assert lib.get("nonexistent") is None

    def test_update_query_content(self) -> None:
        """Update query snippet content after loading."""
        lib = SnippetLibrary()
        snippet = lib.add_query("now", "NOW", "self.brain.now")
        updated = lib.update_query_content(snippet.id, "Loaded content")
        assert updated is not None
        assert updated.is_loaded
        # Verify stored version is updated
        retrieved = lib.get(snippet.id)
        assert retrieved is not None
        assert isinstance(retrieved, QuerySnippet)
        assert retrieved.is_loaded

    def test_update_query_content_nonexistent(self) -> None:
        """Update returns None for nonexistent query."""
        lib = SnippetLibrary()
        assert lib.update_query_content("nonexistent", "content") is None

    def test_list_all(self) -> None:
        """List all returns all snippet types."""
        lib = SnippetLibrary()
        lib.add_static("quote", "Q", "C", "S")
        lib.add_query("mark", "M", "path")
        lib.add_custom("C", "Custom")
        assert len(lib.list_all()) == 3

    def test_clear_custom_preserves_others(self) -> None:
        """Clear custom leaves static and query."""
        lib = SnippetLibrary()
        lib.add_static("quote", "Q", "C", "S")
        lib.add_query("mark", "M", "path")
        lib.add_custom("C1", "Custom1")
        lib.add_custom("C2", "Custom2")

        lib.clear_custom()
        assert len(lib.list_static()) == 1
        assert len(lib.list_query()) == 1
        assert len(lib.list_custom()) == 0

    def test_load_defaults_adds_voice_anchors(self) -> None:
        """Load defaults populates voice anchors."""
        lib = SnippetLibrary()
        lib.load_defaults()

        static = lib.list_static()
        # Should have at least 3 voice anchors + 1 quote
        assert len(static) >= 3

        # Check for specific voice anchors
        labels = [s.label for s in static]
        assert "Depth > breadth" in labels
        assert "Mirror Test" in labels

    def test_load_defaults_adds_query_snippets(self) -> None:
        """Load defaults populates query snippets."""
        lib = SnippetLibrary()
        lib.load_defaults()

        query = lib.list_query()
        assert len(query) >= 2  # At least NOW.md and Witness

        labels = [q.label for q in query]
        assert "NOW.md Focus" in labels
        assert "Recent Witness" in labels

    def test_custom_sorted_newest_first(self) -> None:
        """Custom snippets sorted by creation time, newest first."""
        lib = SnippetLibrary()
        lib.add_custom("First", "C1")
        time.sleep(0.01)  # Ensure time difference
        lib.add_custom("Second", "C2")
        time.sleep(0.01)
        lib.add_custom("Third", "C3")

        custom = lib.list_custom()
        assert custom[0].label == "Third"  # Most recent
        assert custom[2].label == "First"  # Oldest

    def test_len(self) -> None:
        """len returns total snippet count."""
        lib = SnippetLibrary()
        assert len(lib) == 0
        lib.add_static("quote", "Q", "C", "S")
        assert len(lib) == 1
        lib.add_query("mark", "M", "path")
        assert len(lib) == 2
        lib.add_custom("C", "Custom")
        assert len(lib) == 3

    def test_clear(self) -> None:
        """Clear removes all snippets."""
        lib = SnippetLibrary()
        lib.add_static("quote", "Q", "C", "S")
        lib.add_query("mark", "M", "path")
        lib.add_custom("C", "Custom")
        lib.clear()
        assert len(lib) == 0
