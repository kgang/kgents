"""
Tests for Law 3: No Export Without Witness

This file tests the witnessed export implementation added to sovereign store.

Law 3 Guarantee:
    ∀ export operation o on entity e:
      ∃ mark m such that m.action = "sovereign.export" ∧ m.entity_path = e.path

Implementation:
    - witnessed_export() creates mark BEFORE gathering content
    - export_entity() with witness param enforces mark requirement
    - export_bundle() with witness param enforces mark requirement
    - ExportBundle includes export_mark_id for provenance

See: spec/protocols/sovereign-data-guarantees.md Section 7
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.sovereign.ingest import Ingestor
from services.sovereign.store import SovereignStore
from services.sovereign.types import IngestEvent


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
def mock_witness() -> MagicMock:
    """
    Create a mock WitnessPersistence.

    Returns a MagicMock with save_mark method that returns MarkResult.
    """
    witness = MagicMock()
    witness.save_mark = AsyncMock()

    # Mock save_mark to return a MarkResult-like object
    async def mock_save_mark_impl(
        action: str,
        reasoning: str | None = None,
        principles: list[str] | None = None,
        tags: list[str] | None = None,
        author: str = "test",
        **kwargs,
    ) -> MagicMock:
        result = MagicMock()
        result.mark_id = f"mark-{hashlib.sha256(action.encode()).hexdigest()[:12]}"
        result.action = action
        result.reasoning = reasoning
        result.principles = principles or []
        result.tags = tags or []
        result.author = author
        result.timestamp = datetime.now(UTC)
        return result

    witness.save_mark.side_effect = mock_save_mark_impl
    return witness


@pytest.fixture
def store_with_witness(
    temp_sovereign_root: Path, mock_witness: MagicMock
) -> tuple[SovereignStore, MagicMock, Ingestor]:
    """Create a store, witness, and ingestor together."""
    store = SovereignStore(root=temp_sovereign_root)
    ingestor = Ingestor(store, mock_witness)
    return store, mock_witness, ingestor


# =============================================================================
# witnessed_export Tests
# =============================================================================


class TestWitnessedExport:
    """Tests for the witnessed_export method (complete Law 3 pattern)."""

    @pytest.mark.asyncio
    async def test_creates_mark_before_gathering_content(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should create mark BEFORE gathering content (Law 3)."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Reset mock to track export calls
        witness.reset_mock()

        # Use witnessed_export
        bundle = await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
            author="alice",
            reasoning="Testing Law 3 compliance",
        )

        # Verify mark was created
        witness.save_mark.assert_called_once()
        call_kwargs = witness.save_mark.call_args.kwargs

        assert "sovereign.export" in call_kwargs["action"]
        assert "1 entities" in call_kwargs["action"]
        assert call_kwargs["reasoning"] == "Testing Law 3 compliance"
        assert "ethical" in call_kwargs["principles"]
        assert "export" in call_kwargs["tags"]
        assert "law3" in call_kwargs["tags"]
        assert call_kwargs["author"] == "alice"

        # Verify bundle has mark_id
        assert bundle.export_mark_id.startswith("mark-")

    @pytest.mark.asyncio
    async def test_returns_export_bundle_with_provenance(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should return ExportBundle with full provenance."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        content = b"# Test Content\nWith some data"
        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        result = await ingestor.ingest(event)

        # Export
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
            author="kent",
        )

        # Verify bundle structure
        assert bundle.export_mark_id.startswith("mark-")
        assert bundle.entity_count == 1
        assert bundle.export_format == "json"
        assert bundle.exported_at is not None

        # Verify entity in bundle
        exported = bundle.entities[0]
        assert exported.path == "spec/test.md"
        assert exported.content == content
        assert exported.content_hash == hashlib.sha256(content).hexdigest()
        assert exported.ingest_mark_id == result.ingest_mark_id
        assert exported.version == 1

    @pytest.mark.asyncio
    async def test_handles_multiple_entities(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should handle multiple entities correctly."""
        store, witness, ingestor = store_with_witness

        # Ingest multiple entities
        paths = []
        for i in range(3):
            path = f"spec/test{i}.md"
            event = IngestEvent.from_content(
                f"# Test {i}".encode(), path, source="test"
            )
            await ingestor.ingest(event)
            paths.append(path)

        # Export all
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=paths,
            witness=witness,
        )

        # Verify bundle
        assert bundle.entity_count == 3
        assert len(bundle.entities) == 3

        # Verify mark mentions count
        call_kwargs = witness.save_mark.call_args.kwargs
        assert "3 entities" in call_kwargs["action"]

    @pytest.mark.asyncio
    async def test_skips_non_existent_entities_gracefully(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should skip missing entities without failing."""
        store, witness, ingestor = store_with_witness

        # Ingest only one entity
        event = IngestEvent.from_content(b"# Exists", "spec/exists.md", source="test")
        await ingestor.ingest(event)

        # Export with both existing and non-existing paths
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=["spec/exists.md", "spec/missing.md", "spec/also-missing.md"],
            witness=witness,
        )

        # Should only include existing entity
        assert bundle.entity_count == 1
        assert bundle.entities[0].path == "spec/exists.md"

        # Mark should reflect attempted export of 3 entities
        call_kwargs = witness.save_mark.call_args.kwargs
        assert "3 entities" in call_kwargs["action"]

    @pytest.mark.asyncio
    async def test_includes_overlay_data(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should include overlay data with entities."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Add overlay data
        await store.store_overlay(
            "spec/test.md",
            "annotations",
            {"note": "This is a test annotation"},
        )

        # Export
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
        )

        # Verify overlay included
        exported = bundle.entities[0]
        assert "annotations" in exported.overlay
        assert exported.overlay["annotations"]["note"] == "This is a test annotation"

    @pytest.mark.asyncio
    async def test_default_reasoning_includes_author(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """witnessed_export should use default reasoning if not provided."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Export without reasoning
        witness.reset_mock()
        await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
            author="bob",
        )

        # Verify default reasoning
        call_kwargs = witness.save_mark.call_args.kwargs
        assert call_kwargs["reasoning"] == "Export requested by bob"


# =============================================================================
# Law 3 Enforcement Tests
# =============================================================================


class TestLaw3Enforcement:
    """Tests that export methods enforce Law 3 when witness is provided."""

    @pytest.mark.asyncio
    async def test_export_entity_with_witness_requires_mark_id(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """export_entity with witness but no mark_id should raise ValueError."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Try to export with witness but no mark_id - should fail
        with pytest.raises(ValueError, match="Law 3.*export_mark_id"):
            await store.export_entity(
                "spec/test.md",
                witness=witness,
                export_mark_id=None,
            )

    @pytest.mark.asyncio
    async def test_export_bundle_with_witness_requires_mark_id(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """export_bundle with witness but no mark_id should raise ValueError."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Try to export with witness but no mark_id - should fail
        with pytest.raises(ValueError, match="Law 3.*export_mark_id"):
            await store.export_bundle(
                paths=["spec/test.md"],
                witness=witness,
                export_mark_id=None,
            )

    @pytest.mark.asyncio
    async def test_export_entity_includes_mark_id_when_provided(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """export_entity should include mark_id in export data when provided."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Create a mark first
        witness.reset_mock()
        mark_result = await witness.save_mark(
            action="sovereign.export: spec/test.md",
            reasoning="Manual export",
            tags=["export"],
        )

        # Export with mark_id
        export_data = await store.export_entity(
            "spec/test.md",
            witness=witness,
            export_mark_id=mark_result.mark_id,
        )

        # Verify mark_id included
        assert export_data["export_mark_id"] == mark_result.mark_id

    @pytest.mark.asyncio
    async def test_export_bundle_json_includes_mark_id(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """export_bundle (JSON) should include mark_id in bundle."""
        store, witness, ingestor = store_with_witness

        # Ingest entities
        for i in range(2):
            event = IngestEvent.from_content(
                f"# Test {i}".encode(), f"spec/test{i}.md", source="test"
            )
            await ingestor.ingest(event)

        # Create mark
        witness.reset_mock()
        mark_result = await witness.save_mark(
            action="sovereign.export: 2 entities",
            reasoning="Bundle test",
            tags=["export"],
        )

        # Export bundle
        bundle_bytes = await store.export_bundle(
            paths=["spec/test0.md", "spec/test1.md"],
            format="json",
            witness=witness,
            export_mark_id=mark_result.mark_id,
        )

        # Verify mark in bundle
        import json
        bundle = json.loads(bundle_bytes.decode("utf-8"))

        assert bundle["export_mark_id"] == mark_result.mark_id
        assert bundle["entity_count"] == 2

    @pytest.mark.asyncio
    async def test_export_bundle_zip_includes_mark_id_in_manifest(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """export_bundle (ZIP) should include mark_id in manifest."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Create mark
        witness.reset_mock()
        mark_result = await witness.save_mark(
            action="sovereign.export: zip",
            reasoning="ZIP test",
            tags=["export"],
        )

        # Export as zip
        bundle_bytes = await store.export_bundle(
            paths=["spec/test.md"],
            format="zip",
            witness=witness,
            export_mark_id=mark_result.mark_id,
        )

        # Extract and verify manifest
        import io
        import json
        import zipfile

        buffer = io.BytesIO(bundle_bytes)
        with zipfile.ZipFile(buffer, "r") as zf:
            manifest_data = zf.read("manifest.json")
            manifest = json.loads(manifest_data.decode("utf-8"))

            assert manifest["export_mark_id"] == mark_result.mark_id


# =============================================================================
# Content Integrity Tests
# =============================================================================


class TestExportIntegrity:
    """Tests that exports preserve content integrity (Theorem 1)."""

    @pytest.mark.asyncio
    async def test_export_preserves_content_hash(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Exported entities should have correct content hashes."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        content = b"# Test Content\n\nFor hash verification"
        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Export
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
        )

        # Verify hash
        exported = bundle.entities[0]
        expected_hash = hashlib.sha256(content).hexdigest()
        assert exported.content_hash == expected_hash
        assert exported.content == content

    @pytest.mark.asyncio
    async def test_export_bundle_to_dict_preserves_hashes(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """ExportBundle.to_dict() should preserve content hashes."""
        store, witness, ingestor = store_with_witness

        # Ingest entity
        content = b"# Content"
        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Export and convert to dict
        witness.reset_mock()
        bundle = await store.witnessed_export(
            paths=["spec/test.md"],
            witness=witness,
        )
        bundle_dict = bundle.to_dict()

        # Verify structure
        assert bundle_dict["type"] == "sovereign_export"
        assert bundle_dict["export_mark_id"].startswith("mark-")
        assert bundle_dict["entity_count"] == 1

        # Verify entity data
        entity_data = bundle_dict["entities"][0]
        assert entity_data["path"] == "spec/test.md"
        assert entity_data["content_hash"] == hashlib.sha256(content).hexdigest()
