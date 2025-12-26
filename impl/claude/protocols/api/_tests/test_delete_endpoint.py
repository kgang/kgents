"""
Test DELETE functionality for Document Director.

Verifies that the delete method:
1. Completely removes the document from sovereign store
2. Returns proper response
3. Document does not appear in list after deletion
"""

import pytest

from services.sovereign.store import SovereignStore


@pytest.fixture
async def store(tmp_path):
    """Create a temporary sovereign store."""
    return SovereignStore(root=tmp_path / "sovereign")


@pytest.mark.asyncio
async def test_delete_document_complete(store: SovereignStore):
    """Test that delete removes document completely from sovereign store."""
    # 1. Create a test document
    path = "spec/test-doc.md"
    content = b"# Test Document\n\nThis is a test."

    version = await store.store_version(
        path=path,
        content=content,
        ingest_mark="test-mark",
        metadata={"source": "test"},
    )

    assert version == 1

    # Verify document exists
    entity = await store.get_current(path)
    assert entity is not None
    assert entity.path == path

    # Verify it appears in list
    all_docs = await store.list_all()
    assert path in all_docs

    # 2. Delete the document using the store's delete method (without witness for simplicity)
    result = await store.delete(
        path=path,
        check_references=False,
        force=True,
        witness=None,
        author="test",
    )

    # 3. Verify delete succeeded
    assert result.success is True
    assert result.path == path

    # 4. Verify document is completely removed
    entity_after = await store.get_current(path)
    assert entity_after is None

    # 5. Verify it does not appear in list
    all_docs_after = await store.list_all()
    assert path not in all_docs_after


@pytest.mark.asyncio
async def test_delete_with_analysis_overlay(store: SovereignStore):
    """Test that delete removes document with analysis overlay."""
    # 1. Create document with analysis overlay
    path = "spec/analyzed-doc.md"
    content = b"# Analyzed Document\n\n## Claims\n\nSome claim."

    await store.store_version(
        path=path,
        content=content,
        ingest_mark="test-mark-2",
        metadata={"source": "test"},
    )

    # Add analysis overlay
    analysis_data = {
        "claims": [{"type": "assertion", "content": "Some claim"}],
        "word_count": 10,
        "analyzed_at": "2024-01-01T00:00:00Z",
    }
    await store.store_overlay(path, "analysis", analysis_data)

    # Verify overlay exists
    overlay = await store.get_overlay(path, "analysis")
    assert overlay is not None
    assert "claims" in overlay

    # 2. Delete the document
    result = await store.delete(
        path=path,
        check_references=False,
        force=True,
        witness=None,
        author="test",
    )

    assert result.success is True

    # 3. Verify document and overlay are gone
    entity = await store.get_current(path)
    assert entity is None

    overlay_after = await store.get_overlay(path, "analysis")
    assert overlay_after == {}


@pytest.mark.asyncio
async def test_delete_nonexistent_document(store: SovereignStore):
    """Test that deleting nonexistent document returns success=False."""
    result = await store.delete(
        path="spec/nonexistent.md",
        check_references=False,
        force=True,
        witness=None,
        author="test",
    )

    assert result.success is False
