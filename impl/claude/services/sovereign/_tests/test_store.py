"""
Tests for SovereignStore.

Verifies:
- Version storage and retrieval
- Overlay operations
- Diff computation
- Entity listing
- Edge cases (empty content, deep paths, Windows compat)

Law 0: No Entity Without Copy — verified by store_version tests
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from services.sovereign.store import SovereignStore
from services.sovereign.types import (
    Annotation,
    AnnotationType,
    Diff,
    DiffType,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_sovereign_root(tmp_path: Path) -> Path:
    """Create a temporary sovereign root."""
    root = tmp_path / "sovereign"
    root.mkdir()
    return root


@pytest.fixture
def store(temp_sovereign_root: Path) -> SovereignStore:
    """Create a SovereignStore with temp root."""
    return SovereignStore(root=temp_sovereign_root)


# =============================================================================
# Basic Storage Tests
# =============================================================================


class TestStoreVersion:
    """Tests for store_version."""

    @pytest.mark.asyncio
    async def test_store_first_version(self, store: SovereignStore) -> None:
        """First version should be v1."""
        content = b"# Hello World\n"
        version = await store.store_version(
            path="spec/hello.md",
            content=content,
            ingest_mark="mark-123",
        )

        assert version == 1

    @pytest.mark.asyncio
    async def test_store_increments_version(self, store: SovereignStore) -> None:
        """Subsequent versions should increment."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")
        v3 = await store.store_version("spec/a.md", b"v3", "mark-3")

        assert v3 == 3

    @pytest.mark.asyncio
    async def test_store_creates_directory_structure(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """Should create proper directory structure."""
        await store.store_version("spec/protocols/k-block.md", b"content", "mark-1")

        entity_dir = temp_sovereign_root / "spec/protocols/k-block.md"
        assert entity_dir.exists()
        assert (entity_dir / "v1").exists()
        assert (entity_dir / "v1" / "content.md").exists()
        assert (entity_dir / "v1" / "meta.json").exists()

    @pytest.mark.asyncio
    async def test_store_preserves_extension(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """Should preserve file extension."""
        await store.store_version("src/main.py", b"print('hello')", "mark-1")

        entity_dir = temp_sovereign_root / "src/main.py"
        assert (entity_dir / "v1" / "content.py").exists()

    @pytest.mark.asyncio
    async def test_store_binary_content(self, store: SovereignStore) -> None:
        """Should handle binary content."""
        binary = bytes(range(256))
        version = await store.store_version("assets/image.bin", binary, "mark-1")

        entity = await store.get_current("assets/image.bin")
        assert entity is not None
        assert entity.content == binary

    @pytest.mark.asyncio
    async def test_store_empty_content_raises(self, store: SovereignStore) -> None:
        """Should reject empty content."""
        with pytest.raises(ValueError, match="empty"):
            await store.store_version("spec/empty.md", b"", "mark-1")

    @pytest.mark.asyncio
    async def test_store_metadata(self, store: SovereignStore, temp_sovereign_root: Path) -> None:
        """Should store metadata correctly."""
        await store.store_version(
            "spec/a.md",
            b"content",
            "mark-123",
            metadata={"source": "git", "author": "kent"},
        )

        meta_path = temp_sovereign_root / "spec/a.md/v1/meta.json"
        meta = json.loads(meta_path.read_text())

        assert meta["ingest_mark"] == "mark-123"
        assert meta["source"] == "git"
        assert meta["author"] == "kent"
        assert "content_hash" in meta
        assert "ingested_at" in meta

    @pytest.mark.asyncio
    async def test_store_updates_current(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """Should update current marker."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")

        current = temp_sovereign_root / "spec/a.md/current"
        # Either symlink or text file depending on platform
        assert current.exists() or current.is_symlink()


# =============================================================================
# Retrieval Tests
# =============================================================================


class TestGetVersion:
    """Tests for get_current and get_version."""

    @pytest.mark.asyncio
    async def test_get_current(self, store: SovereignStore) -> None:
        """Should get latest version."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2 content", "mark-2")

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.version == 2
        assert entity.content == b"v2 content"

    @pytest.mark.asyncio
    async def test_get_specific_version(self, store: SovereignStore) -> None:
        """Should get specific version."""
        await store.store_version("spec/a.md", b"version one", "mark-1")
        await store.store_version("spec/a.md", b"version two", "mark-2")

        entity = await store.get_version("spec/a.md", 1)
        assert entity is not None
        assert entity.version == 1
        assert entity.content == b"version one"

    @pytest.mark.asyncio
    async def test_get_nonexistent_path(self, store: SovereignStore) -> None:
        """Should return None for nonexistent path."""
        entity = await store.get_current("does/not/exist.md")
        assert entity is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_version(self, store: SovereignStore) -> None:
        """Should return None for nonexistent version."""
        await store.store_version("spec/a.md", b"v1", "mark-1")

        entity = await store.get_version("spec/a.md", 99)
        assert entity is None

    @pytest.mark.asyncio
    async def test_entity_properties(self, store: SovereignStore) -> None:
        """Entity should have correct properties."""
        await store.store_version(
            "spec/a.md",
            b"# Hello\n",
            "mark-123",
            metadata={"source": "test"},
        )

        entity = await store.get_current("spec/a.md")
        assert entity is not None

        assert entity.path == "spec/a.md"
        assert entity.content_text == "# Hello\n"
        assert entity.ingest_mark_id == "mark-123"
        assert len(entity.content_hash) == 64  # SHA256 hex

    @pytest.mark.asyncio
    async def test_exists(self, store: SovereignStore) -> None:
        """exists() should work correctly."""
        assert not await store.exists("spec/a.md")

        await store.store_version("spec/a.md", b"content", "mark-1")

        assert await store.exists("spec/a.md")

    @pytest.mark.asyncio
    async def test_list_versions(self, store: SovereignStore) -> None:
        """list_versions should return sorted versions."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")
        await store.store_version("spec/a.md", b"v3", "mark-3")

        versions = await store.list_versions("spec/a.md")
        assert versions == [1, 2, 3]


# =============================================================================
# Overlay Tests
# =============================================================================


class TestOverlay:
    """Tests for overlay operations."""

    @pytest.mark.asyncio
    async def test_store_and_get_overlay(self, store: SovereignStore) -> None:
        """Should store and retrieve overlay data."""
        await store.store_version("spec/a.md", b"content", "mark-1")
        await store.store_overlay("spec/a.md", "annotations", [{"line": 1, "text": "note"}])

        overlay = await store.get_overlay("spec/a.md")
        assert "annotations" in overlay
        assert overlay["annotations"] == [{"line": 1, "text": "note"}]

    @pytest.mark.asyncio
    async def test_edges_stored_in_derived(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """Edges should be stored in overlay/derived/."""
        await store.store_version("spec/a.md", b"content", "mark-1")
        await store.store_overlay("spec/a.md", "edges", {"edges": [{"target": "b.md"}]})

        derived_dir = temp_sovereign_root / "spec/a.md/overlay/derived"
        assert derived_dir.exists()
        assert (derived_dir / "edges.json").exists()

    @pytest.mark.asyncio
    async def test_annotate(self, store: SovereignStore) -> None:
        """annotate() should append to annotations."""
        await store.store_version("spec/a.md", b"content", "mark-1")

        await store.annotate(
            "spec/a.md",
            Annotation(
                annotation_type=AnnotationType.INSIGHT,
                line=10,
                content="This is important",
                mark_id="mark-456",
            ),
        )

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert len(entity.annotations) == 1
        assert entity.annotations[0]["line"] == 10

    @pytest.mark.asyncio
    async def test_multiple_annotations(self, store: SovereignStore) -> None:
        """Multiple annotations should accumulate."""
        await store.store_version("spec/a.md", b"content", "mark-1")

        for i in range(3):
            await store.annotate(
                "spec/a.md",
                Annotation(
                    annotation_type=AnnotationType.TODO,
                    line=i + 1,
                    content=f"Todo {i}",
                ),
            )

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert len(entity.annotations) == 3

    @pytest.mark.asyncio
    async def test_overlay_survives_new_version(self, store: SovereignStore) -> None:
        """Overlay should persist across versions."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.annotate(
            "spec/a.md",
            Annotation(AnnotationType.INSIGHT, 1, "important"),
        )

        await store.store_version("spec/a.md", b"v2", "mark-2")

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert len(entity.annotations) == 1


# =============================================================================
# Diff Tests
# =============================================================================


class TestDiff:
    """Tests for diff_with_source."""

    @pytest.mark.asyncio
    async def test_diff_new(self, store: SovereignStore) -> None:
        """Should detect new entity."""
        diff = await store.diff_with_source("spec/new.md", b"new content")

        assert diff.diff_type == DiffType.NEW
        assert diff.source_content == b"new content"
        assert diff.is_changed

    @pytest.mark.asyncio
    async def test_diff_unchanged(self, store: SovereignStore) -> None:
        """Should detect unchanged content."""
        content = b"same content"
        await store.store_version("spec/a.md", content, "mark-1")

        diff = await store.diff_with_source("spec/a.md", content)

        assert diff.diff_type == DiffType.UNCHANGED
        assert not diff.is_changed

    @pytest.mark.asyncio
    async def test_diff_modified(self, store: SovereignStore) -> None:
        """Should detect modified content."""
        await store.store_version("spec/a.md", b"old content", "mark-1")

        diff = await store.diff_with_source("spec/a.md", b"new content")

        assert diff.diff_type == DiffType.MODIFIED
        assert diff.our_content == b"old content"
        assert diff.source_content == b"new content"
        assert diff.is_changed


# =============================================================================
# Listing Tests
# =============================================================================


class TestListing:
    """Tests for list_all and count."""

    @pytest.mark.asyncio
    async def test_list_all_empty(self, store: SovereignStore) -> None:
        """Empty store should return empty list."""
        paths = await store.list_all()
        assert paths == []

    @pytest.mark.asyncio
    async def test_list_all(self, store: SovereignStore) -> None:
        """Should list all entities."""
        await store.store_version("spec/a.md", b"a", "mark-1")
        await store.store_version("spec/b.md", b"b", "mark-2")
        await store.store_version("impl/c.py", b"c", "mark-3")

        paths = await store.list_all()
        assert sorted(paths) == ["impl/c.py", "spec/a.md", "spec/b.md"]

    @pytest.mark.asyncio
    async def test_list_deep_paths(self, store: SovereignStore) -> None:
        """Should handle deep nested paths."""
        await store.store_version("spec/protocols/very/deep/thing.md", b"deep", "mark-1")

        paths = await store.list_all()
        assert "spec/protocols/very/deep/thing.md" in paths

    @pytest.mark.asyncio
    async def test_count(self, store: SovereignStore) -> None:
        """count() should return correct count."""
        assert await store.count() == 0

        await store.store_version("spec/a.md", b"a", "mark-1")
        await store.store_version("spec/b.md", b"b", "mark-2")

        assert await store.count() == 2

    @pytest.mark.asyncio
    async def test_total_versions(self, store: SovereignStore) -> None:
        """total_versions should count all versions."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")
        await store.store_version("spec/b.md", b"v1", "mark-3")

        total = await store.total_versions()
        assert total == 3


# =============================================================================
# Deletion Tests
# =============================================================================


class TestDeletion:
    """Tests for delete and delete_version."""

    @pytest.mark.asyncio
    async def test_delete_entity(self, store: SovereignStore) -> None:
        """Should delete entity and all versions."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")

        result = await store.delete("spec/a.md")
        assert result.success

        assert not await store.exists("spec/a.md")

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, store: SovereignStore) -> None:
        """Should return DeleteResult with success=False for nonexistent entity."""
        result = await store.delete("spec/nope.md")
        assert not result.success

    @pytest.mark.asyncio
    async def test_delete_version(self, store: SovereignStore) -> None:
        """Should delete specific version."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")

        deleted = await store.delete_version("spec/a.md", 1)
        assert deleted

        versions = await store.list_versions("spec/a.md")
        assert versions == [2]

    @pytest.mark.asyncio
    async def test_delete_current_version_raises(self, store: SovereignStore) -> None:
        """Cannot delete current version."""
        await store.store_version("spec/a.md", b"v1", "mark-1")

        with pytest.raises(ValueError, match="current"):
            await store.delete_version("spec/a.md", 1)


# =============================================================================
# Compaction Tests
# =============================================================================


class TestCompaction:
    """Tests for compact."""

    @pytest.mark.asyncio
    async def test_compact_removes_old_versions(self, store: SovereignStore) -> None:
        """compact() should remove old versions."""
        for i in range(10):
            await store.store_version("spec/a.md", f"v{i + 1}".encode(), f"mark-{i}")

        deleted = await store.compact("spec/a.md", keep_versions=3)
        assert deleted == 7

        versions = await store.list_versions("spec/a.md")
        assert versions == [8, 9, 10]

    @pytest.mark.asyncio
    async def test_compact_keeps_current(self, store: SovereignStore) -> None:
        """compact() should keep current version."""
        for i in range(5):
            await store.store_version("spec/a.md", f"v{i + 1}".encode(), f"mark-{i}")

        deleted = await store.compact("spec/a.md", keep_versions=2)

        # Current version (5) should still exist
        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.version == 5

    @pytest.mark.asyncio
    async def test_compact_few_versions_noop(self, store: SovereignStore) -> None:
        """compact() should do nothing if fewer versions than keep."""
        await store.store_version("spec/a.md", b"v1", "mark-1")
        await store.store_version("spec/a.md", b"v2", "mark-2")

        deleted = await store.compact("spec/a.md", keep_versions=5)
        assert deleted == 0


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_unicode_content(self, store: SovereignStore) -> None:
        """Should handle unicode content."""
        content = "# こんにちは World 🎉\n"
        await store.store_version("spec/unicode.md", content.encode("utf-8"), "mark-1")

        entity = await store.get_current("spec/unicode.md")
        assert entity is not None
        assert entity.content_text == content

    @pytest.mark.asyncio
    async def test_large_content(self, store: SovereignStore) -> None:
        """Should handle large content."""
        content = b"x" * 1_000_000  # 1MB
        await store.store_version("spec/large.md", content, "mark-1")

        entity = await store.get_current("spec/large.md")
        assert entity is not None
        assert len(entity.content) == 1_000_000

    @pytest.mark.asyncio
    async def test_path_with_special_chars(self, store: SovereignStore) -> None:
        """Should handle paths with special characters."""
        await store.store_version("spec/some-file_v2.test.md", b"content", "mark-1")

        assert await store.exists("spec/some-file_v2.test.md")

    @pytest.mark.asyncio
    async def test_concurrent_versions(self, store: SovereignStore) -> None:
        """Should handle concurrent version creation."""
        import asyncio

        async def store_version(i: int) -> int:
            return await store.store_version("spec/race.md", f"v{i}".encode(), f"mark-{i}")

        # Create 10 versions concurrently
        versions = await asyncio.gather(*[store_version(i) for i in range(10)])

        # All versions should be unique
        assert len(set(versions)) == 10

    @pytest.mark.asyncio
    async def test_empty_overlay(self, store: SovereignStore) -> None:
        """get_overlay on entity without overlay should return empty dict."""
        await store.store_version("spec/a.md", b"content", "mark-1")

        overlay = await store.get_overlay("spec/a.md")
        assert overlay == {}


# =============================================================================
# Type Tests
# =============================================================================


class TestTypes:
    """Tests for type definitions."""

    def test_ingest_event_from_content(self) -> None:
        """IngestEvent.from_content should work."""
        from services.sovereign.types import IngestEvent

        event = IngestEvent.from_content("hello", "test.md", "memory")
        assert event.content == b"hello"
        assert len(event.content_hash) == 64

    def test_diff_type_is_changed(self) -> None:
        """Diff.is_changed should be correct."""
        assert Diff.new(b"x").is_changed
        assert Diff.modified(b"old", b"new").is_changed
        assert not Diff.unchanged().is_changed

    def test_annotation_serialization(self) -> None:
        """Annotation should serialize/deserialize correctly."""
        ann = Annotation(
            annotation_type=AnnotationType.CORRECTION,
            line=42,
            content="fixed typo",
            original="teh",
            corrected="the",
            mark_id="mark-123",
        )

        d = ann.to_dict()
        restored = Annotation.from_dict(d)

        assert restored.annotation_type == AnnotationType.CORRECTION
        assert restored.line == 42
        assert restored.original == "teh"
        assert restored.corrected == "the"
