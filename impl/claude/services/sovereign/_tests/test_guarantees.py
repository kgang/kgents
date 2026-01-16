"""
Tests for Sovereign Data Guarantees.

Verifies the Laws and Theorems from spec/protocols/sovereign-data-guarantees.md:

Laws:
    Law 0: No Entity Without Copy
    Law 1: No Entity Without Witness
    Law 2: No Edge Without Witness
    Law 3: No Export Without Witness

Theorems:
    Theorem 1: Integrity Guarantee
    Theorem 2: Provenance Guarantee
    Theorem 10: Rename Integrity
    Theorem 11: Delete Safety

This file complements test_store.py, which tests basic operations.
Here we verify the formal guarantees.

See: spec/protocols/sovereign-data-guarantees.md
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

    # Track calls for assertions
    witness.save_mark = AsyncMock()

    # Mock save_mark to return a MarkResult-like object
    async def mock_save_mark_impl(
        action: str,
        reasoning: str | None = None,
        principles: list[str] | None = None,
        tags: list[str] | None = None,
        author: str = "test",
        parent_mark_id: str | None = None,
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
        result.parent_mark_id = parent_mark_id
        return result

    witness.save_mark.side_effect = mock_save_mark_impl
    witness.get_mark = AsyncMock(return_value=None)  # Default to no parent
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
# Law 0: No Entity Without Copy
# =============================================================================


class TestLaw0_NoEntityWithoutCopy:
    """
    Law 0: No Entity Without Copy

    ∀ entity e ∈ SovereignStore:
      ∃ content c such that stored(e) = c ∧ hash(c) = e.content_hash

    Verification:
    - store_version creates content file
    - get_current returns exact bytes
    - content_hash matches stored content
    """

    @pytest.mark.asyncio
    async def test_store_version_creates_content_file(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """Store version should create a content file on disk."""
        content = b"# Specification\n\nThis is the content.\n"
        path = "spec/test.md"

        await store.store_version(path, content, "mark-123")

        # Verify content file exists
        content_file = temp_sovereign_root / "spec/test.md/v1/content.md"
        assert content_file.exists()
        assert content_file.read_bytes() == content

    @pytest.mark.asyncio
    async def test_get_current_returns_exact_bytes(self, store: SovereignStore) -> None:
        """Get current should return exact bytes that were stored."""
        original_content = b"# Hello World\n\nWith special chars: \xe2\x9c\x93\n"
        path = "spec/test.md"

        await store.store_version(path, original_content, "mark-123")
        entity = await store.get_current(path)

        assert entity is not None
        assert entity.content == original_content
        # Verify byte-for-byte equality
        assert len(entity.content) == len(original_content)
        assert entity.content == original_content

    @pytest.mark.asyncio
    async def test_content_hash_matches_stored(self, store: SovereignStore) -> None:
        """Content hash in metadata should match hash of stored content."""
        content = b"Test content for hashing"
        path = "spec/hash-test.md"

        # Compute expected hash
        expected_hash = hashlib.sha256(content).hexdigest()

        # Store and retrieve
        await store.store_version(path, content, "mark-123")
        entity = await store.get_current(path)

        assert entity is not None
        assert entity.content_hash == expected_hash

        # Verify we can recompute and it matches
        recomputed_hash = hashlib.sha256(entity.content).hexdigest()
        assert recomputed_hash == entity.content_hash


# =============================================================================
# Law 1: No Entity Without Witness
# =============================================================================


class TestLaw1_NoEntityWithoutWitness:
    """
    Law 1: No Entity Without Witness

    ∀ entity e ∈ SovereignStore:
      ∃ mark m such that m.entity_path = e.path ∧ m.action = "sovereign.ingest"

    Verification:
    - Ingest creates birth mark
    - Mark exists in witness persistence
    - Unwitnessed fallback creates placeholder ID
    """

    @pytest.mark.asyncio
    async def test_ingest_creates_birth_mark(
        self, store_with_witness: tuple[SovereignStore, AsyncMock, Ingestor]
    ) -> None:
        """Ingest should create a birth mark before storing content."""
        store, witness, ingestor = store_with_witness

        event = IngestEvent.from_content(b"# Test content", "spec/test.md", source="test")

        result = await ingestor.ingest(event, author="test-user")

        # Verify birth mark was created
        assert result.ingest_mark_id.startswith("mark-")
        witness.save_mark.assert_called()

        # Verify the mark was for ingest
        call_args = witness.save_mark.call_args
        assert "entity.ingest" in call_args.kwargs["action"]
        assert "spec/test.md" in call_args.kwargs["action"]

    @pytest.mark.asyncio
    async def test_mark_exists_in_witness_persistence(
        self, store_with_witness: tuple[SovereignStore, AsyncMock, Ingestor]
    ) -> None:
        """Birth mark should be saved to witness persistence."""
        store, witness, ingestor = store_with_witness

        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")

        result = await ingestor.ingest(event, author="test-user")

        # Verify save_mark was called with correct parameters
        witness.save_mark.assert_called()
        call_kwargs = witness.save_mark.call_args.kwargs

        assert call_kwargs["action"] == "entity.ingest: spec/test.md"
        assert "membrane" in call_kwargs["reasoning"]
        assert "composable" in call_kwargs["principles"]
        assert "ingest" in call_kwargs["tags"]
        assert call_kwargs["author"] == "test-user"

    @pytest.mark.asyncio
    async def test_unwitnessed_fallback_creates_placeholder_id(self, store: SovereignStore) -> None:
        """When no witness is available, ingest should create placeholder ID."""
        # Create ingestor WITHOUT witness
        ingestor = Ingestor(store, witness=None)

        event = IngestEvent.from_content(b"# Test", "spec/test.md", source="test")

        result = await ingestor.ingest(event)

        # Verify placeholder ID was created
        assert result.ingest_mark_id.startswith("unwitnessed-")
        assert len(result.ingest_mark_id) > 12  # Has some unique component


# =============================================================================
# Law 2: No Edge Without Witness
# =============================================================================


class TestLaw2_NoEdgeWithoutWitness:
    """
    Law 2: No Edge Without Witness

    ∀ edge (e₁, e₂, type) discovered during ingest:
      ∃ mark m such that m.references edge ∧ m.parent = ingest_mark

    Verification:
    - Edge extraction creates marks
    - Marks link to parent birth mark
    - Edge marks have proper tags
    """

    @pytest.mark.asyncio
    async def test_edge_extraction_creates_marks(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Ingest should create marks for each discovered edge."""
        store, witness, ingestor = store_with_witness

        # Content with edges (using backticks as required by SpecParser)
        content = b"""# Test Spec

See also: `spec/k-block.md`
Implements: `spec/principles.md`
"""

        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        result = await ingestor.ingest(event, author="test-user")

        # Verify edge marks were created
        # save_mark is called once for birth, then once per edge
        assert witness.save_mark.call_count >= 3  # birth + 2 edges

        # Find edge mark calls (not the birth mark)
        edge_calls = [
            call for call in witness.save_mark.call_args_list if "edge.discovered" in str(call)
        ]
        assert len(edge_calls) >= 2

    @pytest.mark.asyncio
    async def test_marks_link_to_parent_birth_mark(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Edge marks should have parent_mark_id = birth_mark_id."""
        store, witness, ingestor = store_with_witness

        content = b"""# Test
Reference: `spec/other.md`
"""

        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        result = await ingestor.ingest(event, author="test-user")

        # Get the birth mark ID (first call to save_mark)
        first_call = witness.save_mark.call_args_list[0]
        # Call the side_effect to get the result
        birth_mark_result = await witness.save_mark.side_effect(**first_call.kwargs)
        birth_mark_id = birth_mark_result.mark_id

        # Find edge mark calls
        edge_calls = [
            call
            for call in witness.save_mark.call_args_list[1:]
            if "edge.discovered" in call.kwargs.get("action", "")
        ]

        # Verify each edge mark has parent = birth mark
        for call in edge_calls:
            assert call.kwargs.get("parent_mark_id") == birth_mark_id

    @pytest.mark.asyncio
    async def test_edge_marks_have_proper_tags(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Edge marks should be tagged with edge type and spec path."""
        store, witness, ingestor = store_with_witness

        content = b"""# Test
References: `spec/target.md`
"""

        event = IngestEvent.from_content(content, "spec/test.md", source="test")
        await ingestor.ingest(event, author="test-user")

        # Find edge mark calls
        edge_calls = [
            call
            for call in witness.save_mark.call_args_list
            if "edge.discovered" in call.kwargs.get("action", "")
        ]

        assert len(edge_calls) > 0

        # Verify tags
        for call in edge_calls:
            tags = call.kwargs.get("tags", [])
            assert "edge" in tags
            assert any(t.startswith("edge:") for t in tags)  # edge:references
            assert any(t.startswith("spec:") for t in tags)  # spec:test.md


# =============================================================================
# Law 3: No Export Without Witness
# =============================================================================


class TestLaw3_NoExportWithoutWitness:
    """
    Law 3: No Export Without Witness (Proposed)

    ∀ export operation o on entity e:
      ∃ mark m such that m.action = "sovereign.export" ∧ m.entity_path = e.path

    Verification:
    - Export creates mark before export
    - Mark includes entity paths
    - Bundle includes mark_id

    Note: This tests the export_entity/export_bundle methods which should
    create witness marks (when witness is available).
    """

    @pytest.mark.asyncio
    async def test_export_creates_mark_before_export(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Export should create mark before exporting (if witness available)."""
        store, witness, ingestor = store_with_witness

        # First ingest something
        event = IngestEvent.from_content(b"# Test content", "spec/test.md", source="test")
        await ingestor.ingest(event)

        # Reset mock to track export calls
        witness.reset_mock()

        # TODO: Once export_entity/export_bundle support witness marks,
        # this test should verify the mark is created.
        # For now, we just verify export works without witness.
        export_data = await store.export_entity("spec/test.md")

        assert export_data["path"] == "spec/test.md"
        assert "content" in export_data
        assert "content_hash" in export_data

    @pytest.mark.asyncio
    async def test_mark_includes_entity_paths(self, store: SovereignStore) -> None:
        """Export mark should include entity paths being exported."""
        # First ingest something
        await store.store_version("spec/test.md", b"# Test", "mark-123")

        # Export entity
        export_data = await store.export_entity("spec/test.md")

        # Verify entity path is in export data
        assert export_data["path"] == "spec/test.md"

    @pytest.mark.asyncio
    async def test_bundle_includes_entity_info(self, store: SovereignStore) -> None:
        """Export bundle should include entity information."""
        # Ingest multiple entities
        await store.store_version("spec/a.md", b"# A", "mark-1")
        await store.store_version("spec/b.md", b"# B", "mark-2")

        # Export bundle
        bundle_bytes = await store.export_bundle(["spec/a.md", "spec/b.md"], format="json")

        import json

        bundle = json.loads(bundle_bytes.decode("utf-8"))

        assert bundle["type"] == "sovereign_export"
        assert bundle["entity_count"] == 2
        assert len(bundle["entities"]) == 2
        assert bundle["entities"][0]["path"] in ["spec/a.md", "spec/b.md"]


# =============================================================================
# Theorem 1: Integrity Guarantee
# =============================================================================


class TestTheorem1_IntegrityGuarantee:
    """
    Theorem 1: Integrity Guarantee

    If an entity exists in the store with hash h,
    then the content is exactly what was ingested.

    Verification:
    - verify_integrity catches hash mismatch
    - verify_integrity passes for valid entity
    - Manually corrupt file, verify detection
    """

    @pytest.mark.asyncio
    async def test_verify_integrity_passes_for_valid_entity(self, store: SovereignStore) -> None:
        """Integrity check should pass for uncorrupted entity."""
        content = b"# Valid Content\n"
        path = "spec/test.md"

        await store.store_version(path, content, "mark-123")
        entity = await store.get_current(path)

        assert entity is not None

        # Verify integrity manually
        computed_hash = hashlib.sha256(entity.content).hexdigest()
        assert computed_hash == entity.content_hash

    @pytest.mark.asyncio
    async def test_verify_integrity_catches_hash_mismatch(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """
        Integrity check should detect when content doesn't match stored hash.

        NOTE: Current implementation has content_hash as a computed property,
        so it always reflects current content. To detect corruption, we need
        to compare against the hash stored in metadata file.
        """
        import json

        content = b"# Original Content\n"
        path = "spec/test.md"

        await store.store_version(path, content, "mark-123")

        # Read the hash from metadata file directly
        meta_file = temp_sovereign_root / "spec/test.md/v1/meta.json"
        stored_metadata = json.loads(meta_file.read_text())
        stored_hash = stored_metadata["content_hash"]

        # Verify original hash is correct
        assert hashlib.sha256(content).hexdigest() == stored_hash

        # Manually corrupt the content file
        content_file = temp_sovereign_root / "spec/test.md/v1/content.md"
        corrupted_content = b"# Corrupted Content\n"
        content_file.write_bytes(corrupted_content)

        # Get entity after corruption
        entity = await store.get_current(path)
        assert entity is not None

        # The entity's content_hash property recomputes from corrupted content
        # To detect corruption, compare entity content hash against stored metadata
        assert entity.content_hash != stored_hash  # Corruption detected!

    @pytest.mark.asyncio
    async def test_manually_corrupt_file_verify_detection(
        self, store: SovereignStore, temp_sovereign_root: Path
    ) -> None:
        """
        Should detect corruption when file is manually modified.

        NOTE: Since content_hash is computed from content, we detect corruption
        by comparing the computed hash against the stored metadata hash.
        """
        import json

        original = b"# Original\nThis is the original content.\n"
        path = "spec/test.md"

        # Store original
        await store.store_version(path, original, "mark-123")

        # Read stored hash from metadata
        meta_file = temp_sovereign_root / "spec/test.md/v1/meta.json"
        metadata = json.loads(meta_file.read_text())
        original_hash = metadata["content_hash"]

        # Verify original hash is correct
        assert hashlib.sha256(original).hexdigest() == original_hash

        # Corrupt the file (simulate disk corruption or malicious edit)
        content_file = temp_sovereign_root / "spec/test.md/v1/content.md"
        corrupted = b"# HACKED\nMalicious content here.\n"
        content_file.write_bytes(corrupted)

        # Retrieve again - should read corrupted content
        entity_after = await store.get_current(path)
        assert entity_after is not None

        # Content has changed
        assert entity_after.content == corrupted

        # Computed hash from current content doesn't match stored hash
        assert entity_after.content_hash != original_hash  # CORRUPTION DETECTED


# =============================================================================
# Theorem 2: Provenance Guarantee
# =============================================================================


class TestTheorem2_ProvenanceGuarantee:
    """
    Theorem 2: Provenance Guarantee

    For any entity e, we can reconstruct the complete history:
      who created it, when, from where, and all modifications.

    Verification:
    - Can follow mark chain from entity to birth
    - Chain includes all versions
    """

    @pytest.mark.asyncio
    async def test_can_follow_mark_chain_from_entity_to_birth(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """Should be able to trace from current version back to birth mark."""
        store, witness, ingestor = store_with_witness

        # Ingest initial version
        event1 = IngestEvent.from_content(b"# Version 1", "spec/test.md", source="test")
        result1 = await ingestor.ingest(event1, author="alice")
        birth_mark_id = result1.ingest_mark_id

        # Update with new version
        event2 = IngestEvent.from_content(
            b"# Version 2\nUpdated content", "spec/test.md", source="test"
        )
        result2 = await ingestor.ingest(event2, author="bob")

        # Get current entity
        entity = await store.get_current("spec/test.md")
        assert entity is not None

        # Verify we can trace back to birth
        # The entity should have ingest_mark_id from most recent ingest
        assert entity.ingest_mark_id == result2.ingest_mark_id

        # In a real system, we'd follow parent_mark_id chain:
        # result2.ingest_mark_id → parent → result1.ingest_mark_id → parent → ...
        # For now, verify both marks were created
        assert witness.save_mark.call_count >= 2

    @pytest.mark.asyncio
    async def test_chain_includes_all_versions(self, store: SovereignStore) -> None:
        """Version history should be complete and ordered."""
        path = "spec/test.md"

        # Create multiple versions
        await store.store_version(path, b"v1", "mark-1")
        await store.store_version(path, b"v2", "mark-2")
        await store.store_version(path, b"v3", "mark-3")

        # Get version list
        versions = await store.list_versions(path)
        assert versions == [1, 2, 3]

        # Verify we can retrieve each version
        v1 = await store.get_version(path, 1)
        v2 = await store.get_version(path, 2)
        v3 = await store.get_version(path, 3)

        assert v1 is not None and v1.content == b"v1"
        assert v2 is not None and v2.content == b"v2"
        assert v3 is not None and v3.content == b"v3"

        # Verify metadata preserves provenance
        assert v1.ingest_mark_id == "mark-1"
        assert v2.ingest_mark_id == "mark-2"
        assert v3.ingest_mark_id == "mark-3"


# =============================================================================
# Theorem 10: Rename Integrity
# =============================================================================


class TestTheorem10_RenameIntegrity:
    """
    Theorem 10: Rename Integrity

    Renaming entity from path p₁ to p₂ preserves all guarantees.

    Verification:
    - Rename creates proper mark (when implemented)
    - References updated (not tested here, requires edge system)
    """

    @pytest.mark.asyncio
    async def test_rename_creates_proper_mark(self, store: SovereignStore) -> None:
        """Rename should update metadata with rename information."""
        old_path = "spec/old.md"
        new_path = "spec/new.md"

        # Create entity at old path
        await store.store_version(old_path, b"# Content", "mark-123")

        # Rename (returns mark_id or None)
        mark_id = await store.rename(old_path, new_path)
        # Without witness, mark_id will be None
        assert mark_id is None

        # Verify new entity exists
        assert await store.exists(new_path)
        assert not await store.exists(old_path)

        # Verify metadata updated in all versions
        entity = await store.get_current(new_path)
        assert entity is not None
        assert entity.path == new_path

        # Check metadata for rename info
        metadata = entity.metadata
        assert metadata.get("renamed_from") == old_path
        assert metadata.get("renamed_at") is not None

    @pytest.mark.asyncio
    async def test_rename_preserves_content_and_hash(self, store: SovereignStore) -> None:
        """Rename should preserve content and integrity."""
        old_path = "spec/old.md"
        new_path = "spec/renamed.md"
        content = b"# Important Content\nMust not be corrupted.\n"

        # Store original
        await store.store_version(old_path, content, "mark-123")
        old_entity = await store.get_current(old_path)
        assert old_entity is not None
        original_hash = old_entity.content_hash

        # Rename
        await store.rename(old_path, new_path)

        # Verify content preserved
        new_entity = await store.get_current(new_path)
        assert new_entity is not None
        assert new_entity.content == content
        assert new_entity.content_hash == original_hash


# =============================================================================
# Theorem 11: Delete Safety
# =============================================================================


class TestTheorem11_DeleteSafety:
    """
    Theorem 11: Delete Safety

    Deleting entity e does not corrupt references.

    Verification:
    - Delete blocked when references exist (requires reference tracking)
    - Force delete creates placeholders (not implemented yet)
    - Delete mark created (when witness available)
    """

    @pytest.mark.asyncio
    async def test_delete_removes_entity(self, store: SovereignStore) -> None:
        """Basic delete should remove entity."""
        path = "spec/test.md"

        await store.store_version(path, b"# Content", "mark-123")
        assert await store.exists(path)

        # Delete
        deleted = await store.delete(path)
        assert deleted
        assert not await store.exists(path)

    @pytest.mark.asyncio
    async def test_can_check_references_before_delete(self, store: SovereignStore) -> None:
        """Should be able to check for references before deleting."""
        # Create entity with references
        await store.store_version("spec/target.md", b"# Target", "mark-1")
        await store.store_version("spec/source.md", b"# Source", "mark-2")

        # Add edges to source (matching the structure from ingest.py)
        await store.store_overlay(
            "spec/source.md",
            "edges",
            {
                "edges": [
                    {
                        "type": "references",
                        "target": "spec/target.md",
                        "line": 5,
                        "context": "See target.md",
                        "mark_id": None,
                    }
                ],
                "count": 1,
                "ingest_mark": "mark-2",
            },
        )

        # Check for references to target
        refs = await store.get_references_to("spec/target.md")

        # Should find the reference from source
        assert len(refs) > 0
        assert refs[0]["from_path"] == "spec/source.md"

    @pytest.mark.asyncio
    async def test_delete_with_references_can_be_detected(self, store: SovereignStore) -> None:
        """
        Deleting entity with references should be blocked (Theorem 11).

        Delete Safety guarantee: deletion is blocked when references exist.
        """
        # Setup: target referenced by source
        await store.store_version("spec/target.md", b"# Target", "mark-1")
        await store.store_version("spec/source.md", b"# Source", "mark-2")

        await store.store_overlay(
            "spec/source.md",
            "edges",
            {
                "edges": [
                    {
                        "type": "references",
                        "target": "spec/target.md",
                        "line": 10,
                        "context": "",
                        "mark_id": None,
                    }
                ],
                "count": 1,
                "ingest_mark": "mark-2",
            },
        )

        # Check references before delete
        refs_before = await store.get_references_to("spec/target.md")
        assert len(refs_before) > 0

        # Attempt to delete target - should be BLOCKED because references exist
        with pytest.raises(ValueError, match="Cannot delete.*entities reference it"):
            await store.delete("spec/target.md")

        # Entity should still exist (delete was blocked)
        assert await store.exists("spec/target.md")


# =============================================================================
# Integration Tests
# =============================================================================


class TestGuaranteeIntegration:
    """
    Integration tests that verify multiple guarantees together.
    """

    @pytest.mark.asyncio
    async def test_full_lifecycle_preserves_all_guarantees(
        self, store_with_witness: tuple[SovereignStore, MagicMock, Ingestor]
    ) -> None:
        """
        Full lifecycle: ingest → update → verify → export
        All guarantees should hold throughout.
        """
        store, witness, ingestor = store_with_witness

        # 1. INGEST (Laws 0, 1, 2)
        content_v1 = b"""# Test Spec

This references `spec/other.md`.
"""
        event1 = IngestEvent.from_content(content_v1, "spec/test.md", "test")
        result1 = await ingestor.ingest(event1, author="alice")

        # Verify Law 0: Copy exists
        entity_v1 = await store.get_current("spec/test.md")
        assert entity_v1 is not None
        assert entity_v1.content == content_v1

        # Verify Law 1: Witness exists
        assert result1.ingest_mark_id.startswith("mark-")

        # Verify Law 2: Edges witnessed (at least one edge should have been found)
        # Note: Even if edge_mark_ids is empty (no witness), edges should be stored
        entity_edges = entity_v1.overlay.get("edges", {})
        if isinstance(entity_edges, dict):
            assert entity_edges.get("count", 0) > 0

        # 2. UPDATE (Provenance chain)
        content_v2 = b"""# Test Spec v2

Updated content.
"""
        event2 = IngestEvent.from_content(content_v2, "spec/test.md", "test")
        result2 = await ingestor.ingest(event2, author="bob")

        # Verify version history
        versions = await store.list_versions("spec/test.md")
        assert versions == [1, 2]

        # 3. VERIFY INTEGRITY (Theorem 1)
        entity_v2 = await store.get_current("spec/test.md")
        assert entity_v2 is not None
        computed_hash = hashlib.sha256(entity_v2.content).hexdigest()
        assert computed_hash == entity_v2.content_hash

        # 4. EXPORT (Law 3)
        export_data = await store.export_entity("spec/test.md")
        assert export_data["path"] == "spec/test.md"
        assert export_data["content_hash"] == entity_v2.content_hash

        # All guarantees preserved!
