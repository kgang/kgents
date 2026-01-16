"""
Tests for the 9-step integration protocol.

This test suite verifies that the IntegrationService properly:
1. Creates witness marks
2. Assigns layers using Galois
3. Creates K-Blocks
4. Discovers edges
5. Extracts portal tokens
6. Identifies concepts
7. Detects contradictions
8. Moves files
9. Emits integration events

See: services/sovereign/PHASE2_README.md
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from services.sovereign.integration import (
    Contradiction,
    DiscoveredEdge,
    IdentifiedConcept,
    IntegrationResult,
    IntegrationService,
    PortalToken,
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for uploads and kgents root."""
    with tempfile.TemporaryDirectory() as uploads_dir:
        with tempfile.TemporaryDirectory() as kgents_dir:
            yield Path(uploads_dir), Path(kgents_dir)


@pytest.fixture
def integration_service(temp_dirs):
    """Create IntegrationService with temp directories."""
    uploads_root, kgents_root = temp_dirs
    return IntegrationService(uploads_root, kgents_root)


# =============================================================================
# Test Complete Integration Protocol
# =============================================================================


@pytest.mark.asyncio
async def test_full_integration_protocol(integration_service, temp_dirs):
    """Test complete 9-step integration protocol."""
    uploads_root, kgents_root = temp_dirs

    # Create a test file in uploads/
    test_content = b"""# Test Specification

## Axiom 1: Tasteful

Everything should be tasteful.

## Law 1: Integration is Witnessed

All integrations must create a witness mark.

See also: [[spec.principles.ethical]]
References: [other doc](spec/other.md)
"""

    source_path = "test-spec.md"
    source_file = uploads_root / source_path
    source_file.write_bytes(test_content)

    destination_path = "spec/protocols/test-spec.md"

    # Execute integration
    result = await integration_service.integrate(source_path, destination_path)

    # Verify result
    assert result.success is True
    assert result.error is None
    assert result.source_path == source_path
    assert result.destination_path == destination_path

    # Step 1: Witness mark created
    assert result.witness_mark_id is not None
    assert result.witness_mark_id.startswith("mark-")

    # Step 2: Layer assigned
    assert result.layer is not None
    assert 1 <= result.layer <= 7
    assert 0.0 <= result.galois_loss <= 1.0

    # Step 3: K-Block created
    assert result.kblock_id is not None

    # Step 4: Edges discovered (markdown links)
    assert len(result.edges) > 0
    assert any("spec/other.md" in edge.target_path for edge in result.edges)

    # Step 5: Portal tokens extracted
    assert len(result.portal_tokens) > 0
    assert any(token.token == "spec.principles.ethical" for token in result.portal_tokens)

    # Step 6: Concepts identified
    assert len(result.concepts) > 0
    # Should find "Axiom 1" and "Law 1"
    axioms = [c for c in result.concepts if c.concept_type == "axiom"]
    laws = [c for c in result.concepts if c.concept_type == "law"]
    assert len(axioms) > 0
    assert len(laws) > 0

    # Step 7: Contradictions checked (none expected for this content)
    assert isinstance(result.contradictions, list)

    # Step 8: File moved to destination
    destination_file = kgents_root / destination_path
    assert destination_file.exists()
    assert destination_file.read_bytes() == test_content
    assert not source_file.exists()  # Original file removed

    # Step 9: Integration timestamp recorded
    assert result.integrated_at is not None


# =============================================================================
# Test Individual Steps
# =============================================================================


@pytest.mark.asyncio
async def test_step1_witness_mark_creation(integration_service):
    """Test Step 1: Creating witness mark."""
    content = b"# Test Content\n\nSome content here."

    mark_id = await integration_service._create_witness_mark(
        source_path="test.md",
        destination_path="spec/test.md",
        content=content,
    )

    assert mark_id is not None
    assert isinstance(mark_id, str)
    assert mark_id.startswith("mark-")


@pytest.mark.asyncio
async def test_step2_layer_assignment(integration_service):
    """Test Step 2: Layer assignment using Galois."""
    # Axiom-like content
    axiom_content = b"# Axiom: Composability\n\nAll agents must compose."
    layer, loss = await integration_service._assign_layer(axiom_content)
    assert layer == 1  # Should be L1 (Axiom)
    assert loss < 0.2  # Low loss for axioms

    # Implementation content
    impl_content = b"def foo():\n    return 42\n\nclass Bar:\n    pass"
    layer, loss = await integration_service._assign_layer(impl_content)
    assert layer == 5  # Should be L5 (Implementation)
    assert loss > 0.3  # Higher loss for implementation


@pytest.mark.asyncio
async def test_step3_kblock_creation(integration_service):
    """Test Step 3: K-Block creation."""
    content = b"# Test K-Block\n\nContent for K-Block."

    kblock_id = await integration_service._create_kblock(
        path="spec/test.md",
        content=content,
        layer=4,
        galois_loss=0.35,
    )

    assert kblock_id is not None
    assert isinstance(kblock_id, str)


@pytest.mark.asyncio
async def test_step4_edge_discovery(integration_service):
    """Test Step 4: Edge discovery."""
    content = b"""# Test Doc

References:
- [Other Spec](spec/other.md)
- [Implementation](impl/code.py)

See https://example.com (should be skipped)
"""

    edges = await integration_service._discover_edges(content, "spec/test.md")

    assert len(edges) >= 2
    assert any(edge.target_path == "spec/other.md" for edge in edges)
    assert any(edge.target_path == "impl/code.py" for edge in edges)
    # External URLs should be skipped
    assert not any("example.com" in edge.target_path for edge in edges)


@pytest.mark.asyncio
async def test_step5_portal_token_extraction(integration_service):
    """Test Step 5: Portal token extraction."""
    content = b"""# Test Doc

Portal tokens:
- [[concept.entity]]
- [[world.house]]
- [[path/to/file.md]]
"""

    tokens = await integration_service._extract_portal_tokens(content)

    assert len(tokens) >= 3
    concept_tokens = [t for t in tokens if t.token_type == "concept"]
    path_tokens = [t for t in tokens if t.token_type == "path"]

    assert len(concept_tokens) >= 2
    assert len(path_tokens) >= 1


@pytest.mark.asyncio
async def test_step6_concept_identification(integration_service):
    """Test Step 6: Concept identification."""
    content = b"""# Test Spec

## Axiom A1: Composability

All agents compose.

## Law 1: Immutability

Marks are immutable.

## Principle: Joy-Inducing

Everything should spark joy.
"""

    concepts = await integration_service._identify_concepts(content, layer=1)

    assert len(concepts) >= 2
    axioms = [c for c in concepts if c.concept_type == "axiom"]
    laws = [c for c in concepts if c.concept_type == "law"]

    assert len(axioms) >= 1
    assert len(laws) >= 1


@pytest.mark.asyncio
async def test_step7_contradiction_detection(integration_service):
    """Test Step 7: Contradiction detection."""
    content = b"""# Test Doc

This should not contradict anything yet.
"""

    contradictions = await integration_service._find_contradictions(content, "spec/test.md")

    # No contradictions expected for isolated content
    assert isinstance(contradictions, list)


@pytest.mark.asyncio
async def test_step9_cosmos_integration(integration_service):
    """Test Step 9: Adding to cosmos feed and emitting events."""
    result = IntegrationResult(
        source_path="test.md",
        destination_path="spec/test.md",
        kblock_id="kb_test123",
        witness_mark_id="mark-test456",
        layer=4,
        galois_loss=0.35,
        edges=[
            DiscoveredEdge(
                source_path="spec/test.md",
                target_path="spec/other.md",
                edge_type="references",
                confidence=0.9,
            )
        ],
        portal_tokens=[
            PortalToken(
                token="concept.entity",
                token_type="concept",
            )
        ],
        concepts=[
            IdentifiedConcept(
                name="Test Axiom",
                concept_type="axiom",
                definition="Test definition",
                layer=1,
            )
        ],
        contradictions=[],
        success=True,
    )

    # This should not raise
    await integration_service._add_to_cosmos(result)


# =============================================================================
# Test Error Handling
# =============================================================================


@pytest.mark.asyncio
async def test_integration_missing_file(integration_service):
    """Test integration with missing source file."""
    result = await integration_service.integrate(
        source_path="nonexistent.md",
        destination_path="spec/test.md",
    )

    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_binary_file_handling(integration_service, temp_dirs):
    """Test integration with binary file."""
    uploads_root, kgents_root = temp_dirs

    # Create binary file
    binary_content = b"\x00\x01\x02\x03\xff\xfe\xfd"
    source_path = "test.bin"
    source_file = uploads_root / source_path
    source_file.write_bytes(binary_content)

    destination_path = "data/test.bin"

    result = await integration_service.integrate(source_path, destination_path)

    # Should succeed but with limited analysis
    assert result.success is True
    assert result.layer == 5  # Default to implementation layer
    assert result.kblock_id is None  # No K-Block for binary
    assert len(result.edges) == 0
    assert len(result.portal_tokens) == 0
    assert len(result.concepts) == 0


# =============================================================================
# Test Data Structures
# =============================================================================


def test_discovered_edge_to_dict():
    """Test DiscoveredEdge serialization."""
    edge = DiscoveredEdge(
        source_path="spec/a.md",
        target_path="spec/b.md",
        edge_type="references",
        confidence=0.95,
        context="See also spec/b.md",
    )

    data = edge.to_dict()

    assert data["source_path"] == "spec/a.md"
    assert data["target_path"] == "spec/b.md"
    assert data["edge_type"] == "references"
    assert data["confidence"] == 0.95
    assert data["context"] == "See also spec/b.md"


def test_portal_token_to_dict():
    """Test PortalToken serialization."""
    token = PortalToken(
        token="concept.entity",
        token_type="concept",
        resolved_target="world.entity.123",
        line_number=42,
    )

    data = token.to_dict()

    assert data["token"] == "concept.entity"
    assert data["token_type"] == "concept"
    assert data["resolved_target"] == "world.entity.123"
    assert data["line_number"] == 42


def test_identified_concept_to_dict():
    """Test IdentifiedConcept serialization."""
    concept = IdentifiedConcept(
        name="Composability",
        concept_type="axiom",
        definition="All agents compose",
        layer=1,
        galois_loss=0.05,
    )

    data = concept.to_dict()

    assert data["name"] == "Composability"
    assert data["concept_type"] == "axiom"
    assert data["definition"] == "All agents compose"
    assert data["layer"] == 1
    assert data["galois_loss"] == 0.05


def test_integration_result_to_dict():
    """Test IntegrationResult serialization."""
    result = IntegrationResult(
        source_path="test.md",
        destination_path="spec/test.md",
        kblock_id="kb_123",
        witness_mark_id="mark-456",
        layer=4,
        galois_loss=0.35,
        success=True,
    )

    data = result.to_dict()

    assert data["source_path"] == "test.md"
    assert data["destination_path"] == "spec/test.md"
    assert data["kblock_id"] == "kb_123"
    assert data["witness_mark_id"] == "mark-456"
    assert data["layer"] == 4
    assert data["galois_loss"] == 0.35
    assert data["success"] is True
    assert "integrated_at" in data
