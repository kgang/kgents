"""
Tests for annotation CLI handler.

Testing strategy:
- Unit tests for type validation (AnnotationKind validation)
- Integration tests for store operations (save, query, update)
- Graph building tests (coverage calculation, edge verification)
- CLI command tests (argument parsing, output formatting)

Test Tiers:
- tier1: Pure function tests (type validation, parsing)
- tier2: Database integration tests (store operations)
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from models.annotation import SpecAnnotationRow
from services.annotate.graph import (
    build_impl_graph,
    extract_spec_sections,
    find_specs_for_impl,
    verify_impl_path,
)
from services.annotate.store import AnnotationStore
from services.annotate.types import (
    AnnotationKind,
    AnnotationStatus,
    SpecAnnotation,
)

if TYPE_CHECKING:
    from models.base import AsyncSession


# =============================================================================
# Tier 1: Type Validation Tests
# =============================================================================


@pytest.mark.tier1
@pytest.mark.unit
def test_annotation_kind_enum():
    """Test AnnotationKind enum values."""
    assert AnnotationKind.PRINCIPLE.value == "principle"
    assert AnnotationKind.IMPL_LINK.value == "impl_link"
    assert AnnotationKind.GOTCHA.value == "gotcha"
    assert AnnotationKind.TASTE.value == "taste"
    assert AnnotationKind.DECISION.value == "decision"


@pytest.mark.tier1
@pytest.mark.unit
def test_annotation_status_enum():
    """Test AnnotationStatus enum values."""
    assert AnnotationStatus.ACTIVE.value == "active"
    assert AnnotationStatus.SUPERSEDED.value == "superseded"
    assert AnnotationStatus.ARCHIVED.value == "archived"


@pytest.mark.tier1
@pytest.mark.unit
def test_spec_annotation_principle_validation():
    """Test PRINCIPLE annotation requires principle field."""
    with pytest.raises(ValueError, match="PRINCIPLE annotations must specify principle"):
        SpecAnnotation(
            id="ann-test",
            spec_path="spec/test.md",
            section="Test Section",
            kind=AnnotationKind.PRINCIPLE,
            principle=None,  # Missing required field
            note="Should fail",
        )


@pytest.mark.tier1
@pytest.mark.unit
def test_spec_annotation_impl_link_validation():
    """Test IMPL_LINK annotation requires impl_path field."""
    with pytest.raises(ValueError, match="IMPL_LINK annotations must specify impl_path"):
        SpecAnnotation(
            id="ann-test",
            spec_path="spec/test.md",
            section="Test Section",
            kind=AnnotationKind.IMPL_LINK,
            impl_path=None,  # Missing required field
            note="Should fail",
        )


@pytest.mark.tier1
@pytest.mark.unit
def test_spec_annotation_decision_validation():
    """Test DECISION annotation requires decision_id field."""
    with pytest.raises(ValueError, match="DECISION annotations must specify decision_id"):
        SpecAnnotation(
            id="ann-test",
            spec_path="spec/test.md",
            section="Test Section",
            kind=AnnotationKind.DECISION,
            decision_id=None,  # Missing required field
            note="Should fail",
        )


@pytest.mark.tier1
@pytest.mark.unit
def test_spec_annotation_valid_principle():
    """Test valid PRINCIPLE annotation."""
    ann = SpecAnnotation(
        id="ann-test",
        spec_path="spec/test.md",
        section="Test Section",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Valid principle annotation",
    )
    assert ann.principle == "composable"
    assert ann.kind == AnnotationKind.PRINCIPLE


@pytest.mark.tier1
@pytest.mark.unit
def test_spec_annotation_valid_gotcha():
    """Test valid GOTCHA annotation (no required fields)."""
    ann = SpecAnnotation(
        id="ann-test",
        spec_path="spec/test.md",
        section="Test Section",
        kind=AnnotationKind.GOTCHA,
        note="Trap to avoid",
    )
    assert ann.kind == AnnotationKind.GOTCHA
    assert ann.note == "Trap to avoid"


# =============================================================================
# Tier 2: Store Integration Tests
# =============================================================================


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_save_principle_annotation():
    """Test saving a PRINCIPLE annotation to database."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save annotation
    ann = await store.save_annotation(
        spec_path="spec/protocols/witness.md",
        section="Mark Structure",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Single output per mark",
        created_by="test",
        witness=witness,
    )

    # Verify fields
    assert ann.id.startswith("ann-")
    assert ann.spec_path == "spec/protocols/witness.md"
    assert ann.section == "Mark Structure"
    assert ann.kind == AnnotationKind.PRINCIPLE
    assert ann.principle == "composable"
    assert ann.note == "Single output per mark"
    assert ann.created_by == "test"
    assert ann.mark_id != ""  # Witness mark created
    assert ann.status == AnnotationStatus.ACTIVE


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_save_impl_link_annotation():
    """Test saving an IMPL_LINK annotation to database."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save annotation
    ann = await store.save_annotation(
        spec_path="spec/protocols/witness.md",
        section="MarkStore",
        kind=AnnotationKind.IMPL_LINK,
        impl_path="services/witness/store.py:MarkStore",
        note="Primary storage implementation",
        created_by="test",
        witness=witness,
    )

    # Verify fields
    assert ann.kind == AnnotationKind.IMPL_LINK
    assert ann.impl_path == "services/witness/store.py:MarkStore"
    assert ann.principle is None  # Not a principle annotation


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_query_by_spec_path():
    """Test querying annotations by spec_path."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save multiple annotations for same spec
    spec_path = f"spec/test-{secrets.token_hex(4)}.md"

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 1",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Note 1",
        created_by="test",
        witness=witness,
    )

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 2",
        kind=AnnotationKind.GOTCHA,
        note="Note 2",
        created_by="test",
        witness=witness,
    )

    # Query by spec_path
    result = await store.query_annotations(spec_path=spec_path)

    assert result.total_count == 2
    assert len(result.annotations) == 2
    assert all(ann.spec_path == spec_path for ann in result.annotations)


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_query_by_kind():
    """Test querying annotations by kind."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save annotations of different kinds
    spec_path = f"spec/test-{secrets.token_hex(4)}.md"

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 1",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Note 1",
        created_by="test",
        witness=witness,
    )

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 2",
        kind=AnnotationKind.GOTCHA,
        note="Note 2",
        created_by="test",
        witness=witness,
    )

    # Query PRINCIPLE annotations
    result = await store.query_annotations(
        spec_path=spec_path,
        kind=AnnotationKind.PRINCIPLE,
    )

    assert result.total_count == 1
    assert result.annotations[0].kind == AnnotationKind.PRINCIPLE

    # Query GOTCHA annotations
    result = await store.query_annotations(
        spec_path=spec_path,
        kind=AnnotationKind.GOTCHA,
    )

    assert result.total_count == 1
    assert result.annotations[0].kind == AnnotationKind.GOTCHA


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_query_by_principle():
    """Test querying annotations by principle name."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save annotations with different principles
    spec_path = f"spec/test-{secrets.token_hex(4)}.md"

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 1",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Note 1",
        created_by="test",
        witness=witness,
    )

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 2",
        kind=AnnotationKind.PRINCIPLE,
        principle="tasteful",
        note="Note 2",
        created_by="test",
        witness=witness,
    )

    # Query composable principle
    result = await store.query_annotations(
        spec_path=spec_path,
        principle="composable",
    )

    assert result.total_count == 1
    assert result.annotations[0].principle == "composable"


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_store_update_status():
    """Test updating annotation status."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Save annotation
    ann = await store.save_annotation(
        spec_path="spec/test.md",
        section="Section 1",
        kind=AnnotationKind.PRINCIPLE,
        principle="composable",
        note="Note",
        created_by="test",
        witness=witness,
    )

    assert ann.status == AnnotationStatus.ACTIVE

    # Update to SUPERSEDED
    updated = await store.update_status(ann.id, AnnotationStatus.SUPERSEDED)

    assert updated is not None
    assert updated.status == AnnotationStatus.SUPERSEDED


# =============================================================================
# Tier 2: Graph Building Tests
# =============================================================================


@pytest.mark.tier2
@pytest.mark.integration
def test_extract_spec_sections_markdown(tmp_path: Path):
    """Test extracting sections from markdown spec file."""
    # Create a test spec file
    spec_content = """# Overview

This is the overview.

## Architecture

Architecture section here.

### Implementation

Implementation details.

## Usage

Usage examples.
"""
    spec_file = tmp_path / "test-spec.md"
    spec_file.write_text(spec_content)

    # Extract sections
    sections = extract_spec_sections(spec_file)

    assert len(sections) == 4
    assert "Overview" in sections
    assert "Architecture" in sections
    assert "Implementation" in sections
    assert "Usage" in sections


@pytest.mark.tier2
@pytest.mark.integration
def test_verify_impl_path_file_exists(tmp_path: Path):
    """Test impl path verification for existing file."""
    # Create a test impl file
    impl_file = tmp_path / "services" / "test" / "impl.py"
    impl_file.parent.mkdir(parents=True)
    impl_file.write_text("# Test implementation")

    # Verify file path
    assert verify_impl_path("services/test/impl.py", repo_root=tmp_path)

    # Verify file path with class suffix
    assert verify_impl_path("services/test/impl.py:TestClass", repo_root=tmp_path)


@pytest.mark.tier2
@pytest.mark.integration
def test_verify_impl_path_file_not_found(tmp_path: Path):
    """Test impl path verification for non-existent file."""
    assert not verify_impl_path("services/missing/file.py", repo_root=tmp_path)


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_build_impl_graph(tmp_path: Path):
    """Test building implementation graph from annotations."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Create test spec file
    spec_content = """# Section 1
Content.

## Section 2
Content.

### Section 3
Content.
"""
    spec_file = tmp_path / "test-spec.md"
    spec_file.write_text(spec_content)

    # Create test impl files
    impl_file1 = tmp_path / "services" / "test1.py"
    impl_file1.parent.mkdir(parents=True)
    impl_file1.write_text("# Impl 1")

    impl_file2 = tmp_path / "services" / "test2.py"
    impl_file2.write_text("# Impl 2")

    # Save IMPL_LINK annotations
    spec_path = str(spec_file.relative_to(tmp_path))

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 1",
        kind=AnnotationKind.IMPL_LINK,
        impl_path="services/test1.py",
        note="Implementation 1",
        created_by="test",
        witness=witness,
    )

    await store.save_annotation(
        spec_path=spec_path,
        section="Section 2",
        kind=AnnotationKind.IMPL_LINK,
        impl_path="services/test2.py:Class2",
        note="Implementation 2",
        created_by="test",
        witness=witness,
    )

    # Build graph
    graph = await build_impl_graph(spec_path, store, repo_root=tmp_path)

    # Verify graph
    assert graph.spec_path == spec_path
    assert len(graph.edges) == 2
    assert graph.coverage == 2 / 3  # 2 out of 3 sections covered
    assert len(graph.uncovered_sections) == 1
    assert "Section 3" in graph.uncovered_sections

    # Verify edges
    edge1 = next(e for e in graph.edges if e.spec_section == "Section 1")
    assert edge1.impl_path == "services/test1.py"
    assert edge1.verified  # File exists

    edge2 = next(e for e in graph.edges if e.spec_section == "Section 2")
    assert edge2.impl_path == "services/test2.py:Class2"
    assert edge2.verified  # File exists


@pytest.mark.tier2
@pytest.mark.integration
@pytest.mark.postgres
async def test_find_specs_for_impl():
    """Test finding specs that link to an implementation file."""
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    impl_path = f"services/test-{secrets.token_hex(4)}.py"

    # Save annotations from multiple specs linking to same impl
    await store.save_annotation(
        spec_path="spec/spec1.md",
        section="Section A",
        kind=AnnotationKind.IMPL_LINK,
        impl_path=impl_path,
        note="Link from spec1",
        created_by="test",
        witness=witness,
    )

    await store.save_annotation(
        spec_path="spec/spec2.md",
        section="Section B",
        kind=AnnotationKind.IMPL_LINK,
        impl_path=impl_path,
        note="Link from spec2",
        created_by="test",
        witness=witness,
    )

    # Find specs
    specs = await find_specs_for_impl(impl_path, store)

    assert len(specs) == 2
    assert "spec/spec1.md" in specs
    assert "spec/spec2.md" in specs
    assert "Section A" in specs["spec/spec1.md"]
    assert "Section B" in specs["spec/spec2.md"]


# =============================================================================
# Property-Based Tests
# =============================================================================


@pytest.mark.tier1
@pytest.mark.property
def test_annotation_id_uniqueness():
    """Test that annotation IDs are unique (property-based)."""
    from services.annotate.store import _generate_annotation_id

    # Generate many IDs
    ids = [_generate_annotation_id() for _ in range(1000)]

    # All should be unique
    assert len(ids) == len(set(ids))

    # All should have correct prefix
    assert all(id_.startswith("ann-") for id_ in ids)


__all__ = []
