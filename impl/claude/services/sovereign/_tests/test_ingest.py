"""
Tests for Ingest Protocol.

Verifies:
- Edge extraction from markdown and Python
- Ingest flow with witness marks
- Law enforcement (0, 1, 2)
- Re-ingestion for sync
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.sovereign.ingest import (
    DiscoveredEdge,
    Ingestor,
    extract_edges,
    ingest_content,
)
from services.sovereign.store import SovereignStore
from services.sovereign.types import IngestedEntity, IngestEvent

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


@pytest.fixture
def mock_witness() -> AsyncMock:
    """Create a mock witness persistence."""
    witness = AsyncMock()

    # Track mark IDs
    mark_counter = 0

    async def save_mark(**kwargs):
        nonlocal mark_counter
        mark_counter += 1
        return MagicMock(mark_id=f"mark-{mark_counter:03d}")

    witness.save_mark = AsyncMock(side_effect=save_mark)
    return witness


# =============================================================================
# Edge Extraction Tests
# =============================================================================


class TestExtractEdges:
    """Tests for extract_edges."""

    def test_extract_markdown_spec_refs(self) -> None:
        """Should extract spec references from markdown."""
        content = b"""
# My Spec

See: `spec/protocols/k-block.md` for details.
Also references `spec/principles.md`.
"""
        edges = extract_edges(content, "spec/test.md")

        # Should find spec references
        spec_edges = [e for e in edges if e.edge_type == "extends"]
        assert len(spec_edges) >= 2

    def test_extract_markdown_agentese_paths(self) -> None:
        """Should extract AGENTESE paths from markdown."""
        content = b"""
# My Spec

Use `self.brain.capture` to store.
Query with `world.repo.status`.
"""
        edges = extract_edges(content, "spec/test.md")

        # Should find AGENTESE references
        ref_edges = [e for e in edges if e.edge_type == "references"]
        targets = [e.target for e in ref_edges]
        assert "self.brain.capture" in targets
        assert "world.repo.status" in targets

    def test_extract_markdown_impl_refs(self) -> None:
        """Should extract implementation references."""
        content = b"""
# Implementation

See `impl/claude/services/brain/core.py` for implementation.
"""
        edges = extract_edges(content, "spec/test.md")

        impl_edges = [e for e in edges if e.edge_type == "implements"]
        assert len(impl_edges) >= 1
        assert "impl/claude/services/brain/core.py" in [e.target for e in impl_edges]

    def test_extract_python_imports(self) -> None:
        """Should extract import statements from Python."""
        content = b"""
from services.brain.core import BrainCore
import json
from pathlib import Path
"""
        edges = extract_edges(content, "test.py")

        ref_edges = [e for e in edges if e.edge_type == "references"]
        targets = [e.target for e in ref_edges]
        assert "services.brain.core" in targets
        assert "json" in targets
        assert "pathlib" in targets

    def test_extract_python_agentese_in_docstrings(self) -> None:
        """Should extract AGENTESE paths from Python docstrings."""
        content = b'''
def capture():
    """
    Capture content.

    AGENTESE: self.brain.capture
    """
    pass
'''
        edges = extract_edges(content, "test.py")

        ref_edges = [e for e in edges if e.edge_type == "references"]
        targets = [e.target for e in ref_edges]
        assert "self.brain.capture" in targets

    def test_extract_empty_content(self) -> None:
        """Should handle empty content."""
        edges = extract_edges(b"", "test.md")
        assert edges == []

    def test_extract_binary_content(self) -> None:
        """Should handle non-UTF8 content gracefully."""
        binary = bytes(range(256))
        edges = extract_edges(binary, "test.md")
        assert edges == []

    def test_extract_line_numbers(self) -> None:
        """Should track line numbers correctly."""
        content = b"""# Line 1
# Line 2
See `spec/a.md` here.
# Line 4
"""
        edges = extract_edges(content, "test.md")

        # The spec reference is on line 3
        spec_edges = [e for e in edges if e.target == "spec/a.md"]
        assert len(spec_edges) == 1
        assert spec_edges[0].line_number == 3


# =============================================================================
# Ingestor Tests (Without Witness)
# =============================================================================


class TestIngestorWithoutWitness:
    """Tests for Ingestor without witness persistence."""

    @pytest.mark.asyncio
    async def test_ingest_creates_version(self, store: SovereignStore) -> None:
        """Ingest should create a sovereign version."""
        ingestor = Ingestor(store, witness=None)

        event = IngestEvent.from_content(
            "# Hello\n",
            "spec/hello.md",
            source="test",
        )

        result = await ingestor.ingest(event)

        assert result.version == 1
        assert result.path == "spec/hello.md"
        assert await store.exists("spec/hello.md")

    @pytest.mark.asyncio
    async def test_ingest_returns_unwitnessed_mark(self, store: SovereignStore) -> None:
        """Ingest without witness should return placeholder mark."""
        ingestor = Ingestor(store, witness=None)

        event = IngestEvent.from_content("content", "spec/a.md")
        result = await ingestor.ingest(event)

        assert result.ingest_mark_id.startswith("unwitnessed-")

    @pytest.mark.asyncio
    async def test_ingest_extracts_edges(self, store: SovereignStore) -> None:
        """Ingest should extract and store edges."""
        ingestor = Ingestor(store, witness=None)

        content = """
# My Spec

References `self.brain.capture` and `spec/other.md`.
"""
        event = IngestEvent.from_content(content, "spec/a.md")
        result = await ingestor.ingest(event)

        # Edges should be in overlay
        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert len(entity.edges) >= 2

    @pytest.mark.asyncio
    async def test_ingest_stores_metadata(self, store: SovereignStore) -> None:
        """Ingest should store source metadata."""
        ingestor = Ingestor(store, witness=None)

        event = IngestEvent(
            source="git:/repo",
            content_hash="abc123",
            content=b"content",
            claimed_path="spec/a.md",
            source_author="kent",
        )
        await ingestor.ingest(event)

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.metadata["source"] == "git:/repo"
        assert entity.metadata["source_author"] == "kent"

    @pytest.mark.asyncio
    async def test_reingest_creates_new_version(self, store: SovereignStore) -> None:
        """Reingest should create a new version."""
        ingestor = Ingestor(store, witness=None)

        # Initial ingest
        event = IngestEvent.from_content("v1", "spec/a.md")
        await ingestor.ingest(event)

        # Reingest with new content
        result = await ingestor.reingest("spec/a.md", b"v2 content")

        assert result.version == 2
        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.content == b"v2 content"


# =============================================================================
# Ingestor Tests (With Witness)
# =============================================================================


class TestIngestorWithWitness:
    """Tests for Ingestor with mock witness persistence."""

    @pytest.mark.asyncio
    async def test_ingest_creates_birth_mark(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Ingest should create birth mark via witness."""
        ingestor = Ingestor(store, witness=mock_witness)

        event = IngestEvent.from_content("content", "spec/a.md")
        result = await ingestor.ingest(event, author="kent")

        # Should have created at least one mark (the birth mark)
        assert mock_witness.save_mark.called
        assert result.ingest_mark_id == "mark-001"

    @pytest.mark.asyncio
    async def test_ingest_creates_edge_marks(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Ingest should create marks for each edge."""
        ingestor = Ingestor(store, witness=mock_witness)

        content = """
# Spec

See `spec/a.md` and `spec/b.md`.
"""
        event = IngestEvent.from_content(content, "spec/test.md")
        result = await ingestor.ingest(event)

        # Birth mark + 2 edge marks minimum
        assert mock_witness.save_mark.call_count >= 3
        assert len(result.edge_mark_ids) >= 2

    @pytest.mark.asyncio
    async def test_ingest_marks_have_correct_tags(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Marks should have appropriate tags."""
        ingestor = Ingestor(store, witness=mock_witness)

        event = IngestEvent.from_content("content", "spec/a.md", source="git:repo")
        await ingestor.ingest(event)

        # Check birth mark call
        call_args = mock_witness.save_mark.call_args_list[0]
        kwargs = call_args.kwargs
        assert "ingest" in kwargs["tags"]
        assert "source:git" in kwargs["tags"]

    @pytest.mark.asyncio
    async def test_edge_marks_link_to_birth_mark(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Edge marks should have parent_mark_id = birth mark."""
        ingestor = Ingestor(store, witness=mock_witness)

        content = "References `spec/other.md`."
        event = IngestEvent.from_content(content, "spec/a.md")
        await ingestor.ingest(event)

        # Edge mark call should have parent_mark_id
        if mock_witness.save_mark.call_count > 1:
            edge_call = mock_witness.save_mark.call_args_list[1]
            kwargs = edge_call.kwargs
            assert kwargs.get("parent_mark_id") == "mark-001"


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for ingest_file and ingest_content."""

    @pytest.mark.asyncio
    async def test_ingest_content_string(self, store: SovereignStore) -> None:
        """ingest_content should accept string content."""
        result = await ingest_content(
            "# Hello\n",
            "spec/hello.md",
            store,
        )

        assert result.version == 1
        entity = await store.get_current("spec/hello.md")
        assert entity is not None
        assert entity.content_text == "# Hello\n"

    @pytest.mark.asyncio
    async def test_ingest_content_bytes(self, store: SovereignStore) -> None:
        """ingest_content should accept bytes content."""
        result = await ingest_content(
            b"# Hello\n",
            "spec/hello.md",
            store,
        )

        assert result.version == 1


# =============================================================================
# Law Verification Tests
# =============================================================================


class TestLawEnforcement:
    """Tests verifying the Inbound Sovereignty Laws."""

    @pytest.mark.asyncio
    async def test_law0_no_entity_without_copy(self, store: SovereignStore) -> None:
        """Law 0: Every ingested entity has a sovereign copy."""
        ingestor = Ingestor(store, witness=None)

        event = IngestEvent.from_content("content", "spec/a.md")
        result = await ingestor.ingest(event)

        # Must have stored a copy
        assert await store.exists("spec/a.md")
        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.content == b"content"

    @pytest.mark.asyncio
    async def test_law1_no_entity_without_witness(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Law 1: Every ingested entity has a birth mark."""
        ingestor = Ingestor(store, witness=mock_witness)

        event = IngestEvent.from_content("content", "spec/a.md")
        result = await ingestor.ingest(event)

        # Must have a birth mark
        assert result.ingest_mark_id is not None
        assert not result.ingest_mark_id.startswith("unwitnessed")

    @pytest.mark.asyncio
    async def test_law2_no_edge_without_witness(
        self, store: SovereignStore, mock_witness: AsyncMock
    ) -> None:
        """Law 2: Every discovered edge has its own mark."""
        ingestor = Ingestor(store, witness=mock_witness)

        content = """
# Spec with edges

See `spec/a.md`, `spec/b.md`, `spec/c.md`.
"""
        event = IngestEvent.from_content(content, "spec/test.md")
        result = await ingestor.ingest(event)

        # Should have edge marks for each discovered edge
        edges = extract_edges(content.encode(), "spec/test.md")
        expected_edge_count = len([e for e in edges if e.edge_type == "extends"])

        # Edge marks should exist
        assert len(result.edge_mark_ids) == expected_edge_count


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_ingest_unicode(self, store: SovereignStore) -> None:
        """Should handle unicode content."""
        content = "# こんにちは 🎉\n\nReferences `spec/世界.md`."
        result = await ingest_content(content, "spec/unicode.md", store)

        entity = await store.get_current("spec/unicode.md")
        assert entity is not None
        assert "こんにちは" in entity.content_text

    @pytest.mark.asyncio
    async def test_ingest_deep_path(self, store: SovereignStore) -> None:
        """Should handle deeply nested paths."""
        result = await ingest_content(
            "content",
            "spec/protocols/very/deep/nested/thing.md",
            store,
        )

        assert await store.exists("spec/protocols/very/deep/nested/thing.md")

    @pytest.mark.asyncio
    async def test_ingest_empty_edges(self, store: SovereignStore) -> None:
        """Should handle content with no edges."""
        result = await ingest_content(
            "No references here.",
            "spec/plain.md",
            store,
        )

        entity = await store.get_current("spec/plain.md")
        assert entity is not None
        # Overlay should have empty edges
        assert entity.edges == []

    @pytest.mark.asyncio
    async def test_multiple_ingests_same_path(self, store: SovereignStore) -> None:
        """Multiple ingests should create multiple versions."""
        for i in range(5):
            await ingest_content(f"Version {i + 1}", "spec/a.md", store)

        versions = await store.list_versions("spec/a.md")
        assert versions == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_ingest_preserves_content_hash(self, store: SovereignStore) -> None:
        """Content hash should be preserved in metadata."""
        import hashlib

        content = b"deterministic content"
        expected_hash = hashlib.sha256(content).hexdigest()

        await ingest_content(content, "spec/a.md", store)

        entity = await store.get_current("spec/a.md")
        assert entity is not None
        assert entity.metadata["content_hash"] == expected_hash
