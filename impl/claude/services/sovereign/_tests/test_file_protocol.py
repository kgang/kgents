"""
Tests for the File Integration Protocol.

Philosophy:
    "Integration is witness. Every file crossing the threshold is marked."

See: plans/zero-seed-genesis-grand-strategy.md (Phase 2, Section 5.2)
"""

from pathlib import Path

import pytest

from services.sovereign.integration import (
    DiscoveredEdge,
    IdentifiedConcept,
    IntegrationResult,
    IntegrationService,
    PortalToken,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary uploads and kgents root."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    kgents_root = tmp_path / "kgents"
    kgents_root.mkdir()
    return uploads, kgents_root


@pytest.fixture
def integration_service(temp_workspace):
    """Create integration service."""
    uploads, kgents_root = temp_workspace
    return IntegrationService(uploads, kgents_root)


@pytest.fixture
def sample_markdown():
    """Sample markdown file with various features."""
    return """# Test Document

This is a test document for integration.

## Axiom A1: Everything is Data

All information in the system is represented as data.

## Law 1: Immutability

Once written, data cannot be changed.

## References

See [[concept.entity]] for more details.
Also check out [spec](spec/protocols/test.md) for the protocol.

Links to:
- [Other Doc](docs/other.md)
- External: https://example.com
"""


@pytest.mark.asyncio
async def test_integration_creates_witness_mark(
    integration_service, temp_workspace, sample_markdown
):
    """Step 1: Integration creates a witness mark."""
    uploads, kgents_root = temp_workspace

    # Create source file
    source = uploads / "test.md"
    source.write_text(sample_markdown)

    # Integrate
    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check witness mark was created
    assert result.witness_mark_id is not None
    assert result.witness_mark_id.startswith("mark-")
    assert result.success


@pytest.mark.asyncio
async def test_integration_assigns_layer(integration_service, temp_workspace, sample_markdown):
    """Step 2: Integration assigns layer using Galois or heuristics."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check layer assignment
    assert result.layer is not None
    assert 1 <= result.layer <= 7
    assert 0.0 <= result.galois_loss <= 1.0


@pytest.mark.asyncio
async def test_integration_creates_kblock(integration_service, temp_workspace, sample_markdown):
    """Step 3: Integration creates K-Block."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check K-Block was created
    assert result.kblock_id is not None


@pytest.mark.asyncio
async def test_integration_discovers_edges(integration_service, temp_workspace, sample_markdown):
    """Step 4: Integration discovers edges from markdown links."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check edges were discovered
    assert len(result.edges) > 0

    # Check for markdown links (not external)
    edge_targets = [e.target_path for e in result.edges]
    assert "spec/protocols/test.md" in edge_targets or "docs/other.md" in edge_targets

    # External links should be excluded
    assert not any("http" in t for t in edge_targets)


@pytest.mark.asyncio
async def test_integration_extracts_portal_tokens(
    integration_service, temp_workspace, sample_markdown
):
    """Step 5: Integration extracts portal tokens."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check portal tokens were extracted
    assert len(result.portal_tokens) > 0

    # Check for concept.entity token
    tokens = [t.token for t in result.portal_tokens]
    assert "concept.entity" in tokens

    # Check token types
    concept_tokens = [t for t in result.portal_tokens if t.token_type == "concept"]
    assert len(concept_tokens) > 0


@pytest.mark.asyncio
async def test_integration_identifies_concepts(
    integration_service, temp_workspace, sample_markdown
):
    """Step 6: Integration identifies axioms, laws, concepts."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check concepts were identified
    assert len(result.concepts) > 0

    # Check for axiom
    axioms = [c for c in result.concepts if c.concept_type == "axiom"]
    assert len(axioms) > 0
    assert axioms[0].name == "A1"

    # Check for law
    laws = [c for c in result.concepts if c.concept_type == "law"]
    assert len(laws) > 0


@pytest.mark.asyncio
async def test_integration_checks_contradictions(integration_service, temp_workspace):
    """Step 7: Integration checks for contradictions (placeholder test)."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text("# Test\nNo contradictions here.")

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Contradictions list exists (may be empty without Galois service)
    assert isinstance(result.contradictions, list)


@pytest.mark.asyncio
async def test_integration_moves_file(integration_service, temp_workspace, sample_markdown):
    """Step 8: Integration moves file to destination."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Check file was moved
    assert not source.exists()
    dest = kgents_root / "spec/protocols/test.md"
    assert dest.exists()
    assert dest.read_text() == sample_markdown


@pytest.mark.asyncio
async def test_integration_adds_to_cosmos(integration_service, temp_workspace, sample_markdown):
    """Step 9: Integration adds to cosmos feed and emits event."""
    uploads, kgents_root = temp_workspace

    source = uploads / "test.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("test.md", "spec/protocols/test.md")

    # Event emission is tested implicitly (no error thrown)
    # Full cosmos integration requires postgres backend
    assert result.success


@pytest.mark.asyncio
async def test_integration_handles_missing_file(integration_service, temp_workspace):
    """Integration gracefully handles missing source file."""
    result = await integration_service.integrate("missing.md", "spec/protocols/missing.md")

    assert not result.success
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_integration_handles_binary_file(integration_service, temp_workspace):
    """Integration handles binary files gracefully."""
    uploads, kgents_root = temp_workspace

    # Create binary file
    source = uploads / "image.png"
    source.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

    result = await integration_service.integrate("image.png", "assets/image.png")

    # Should succeed but with default layer for binary
    assert result.success
    assert result.layer == 5  # Implementation layer for binary

    # No K-Block for non-markdown
    assert result.kblock_id is None


@pytest.mark.asyncio
async def test_integration_full_pipeline(integration_service, temp_workspace, sample_markdown):
    """Test full integration pipeline end-to-end."""
    uploads, kgents_root = temp_workspace

    source = uploads / "complete.md"
    source.write_text(sample_markdown)

    result = await integration_service.integrate("complete.md", "spec/protocols/complete.md")

    # Verify all steps completed
    assert result.success
    assert result.witness_mark_id is not None  # Step 1
    assert result.layer is not None  # Step 2
    assert result.kblock_id is not None  # Step 3
    assert len(result.edges) > 0  # Step 4
    assert len(result.portal_tokens) > 0  # Step 5
    assert len(result.concepts) > 0  # Step 6
    # Step 7: contradictions (may be empty)
    # Step 8: file moved
    assert not source.exists()
    assert (kgents_root / "spec/protocols/complete.md").exists()
    # Step 9: cosmos (tested implicitly)

    # Check serialization
    result_dict = result.to_dict()
    assert result_dict["success"]
    assert "kblock_id" in result_dict
    assert "edges" in result_dict
