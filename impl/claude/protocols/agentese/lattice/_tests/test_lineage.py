"""
Tests for ConceptLineage and lineage computation.

The Genealogical Constraint: No concept exists ex nihilo.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from protocols.agentese.lattice.lineage import (
    STANDARD_PARENTS,
    ConceptLineage,
    compute_depth,
    create_root_lineage,
)

# === Test ConceptLineage Dataclass ===


class TestConceptLineage:
    """Tests for ConceptLineage dataclass."""

    def test_create_lineage(self) -> None:
        """Test basic lineage creation."""
        lineage = ConceptLineage(
            handle="concept.justice",
            extends=["concept"],
            justification="The abstract idea of fairness and rightness.",
        )

        assert lineage.handle == "concept.justice"
        assert lineage.extends == ["concept"]
        assert lineage.justification == "The abstract idea of fairness and rightness."
        assert lineage.subsumes == []
        assert lineage.depth == 0  # Not computed yet

    def test_lineage_with_multiple_parents(self) -> None:
        """Test lineage with multiple parent concepts."""
        lineage = ConceptLineage(
            handle="concept.procedural_justice",
            extends=["concept.justice", "concept.process"],
            justification="Justice as applied to procedures.",
        )

        assert len(lineage.extends) == 2
        assert "concept.justice" in lineage.extends
        assert "concept.process" in lineage.extends

    def test_is_root(self) -> None:
        """Test root concept detection."""
        root = create_root_lineage()
        assert root.is_root is True

        child = ConceptLineage(
            handle="concept.entity",
            extends=["concept"],
        )
        assert child.is_root is False

    def test_parent_count(self) -> None:
        """Test parent count property."""
        lineage = ConceptLineage(
            handle="concept.test",
            extends=["concept.entity", "concept.process"],
        )
        assert lineage.parent_count == 2

    def test_add_child(self) -> None:
        """Test adding child concepts."""
        lineage = ConceptLineage(
            handle="concept.entity",
            extends=["concept"],
        )

        lineage.add_child("concept.agent")
        assert "concept.agent" in lineage.subsumes

        # Adding same child again should not duplicate
        lineage.add_child("concept.agent")
        assert lineage.subsumes.count("concept.agent") == 1

    def test_remove_child(self) -> None:
        """Test removing child concepts."""
        lineage = ConceptLineage(
            handle="concept.entity",
            extends=["concept"],
            subsumes=["concept.agent", "concept.tool"],
        )

        lineage.remove_child("concept.agent")
        assert "concept.agent" not in lineage.subsumes
        assert "concept.tool" in lineage.subsumes

    def test_affordances_as_set(self) -> None:
        """Test that affordances are properly converted to set."""
        lineage = ConceptLineage(
            handle="concept.test",
            extends=["concept"],
            affordances=["manifest", "define", "manifest"],  # type: ignore
        )

        assert isinstance(lineage.affordances, set)
        assert len(lineage.affordances) == 2  # Duplicates removed

    def test_serialization_roundtrip(self) -> None:
        """Test to_dict/from_dict roundtrip."""
        original = ConceptLineage(
            handle="concept.justice",
            extends=["concept"],
            subsumes=["concept.procedural_justice"],
            justification="The abstract idea of fairness.",
            affordances={"manifest", "refine"},
            constraints={"has_definition"},
            created_by="test",
            domain="philosophy",
            depth=1,
        )

        data = original.to_dict()
        restored = ConceptLineage.from_dict(data)

        assert restored.handle == original.handle
        assert restored.extends == original.extends
        assert restored.subsumes == original.subsumes
        assert restored.justification == original.justification
        assert restored.affordances == original.affordances
        assert restored.constraints == original.constraints
        assert restored.created_by == original.created_by
        assert restored.domain == original.domain
        assert restored.depth == original.depth


# === Test Standard Parents ===


class TestStandardParents:
    """Tests for standard parent concepts."""

    def test_root_exists(self) -> None:
        """Test that root concept exists in standard parents."""
        assert "concept" in STANDARD_PARENTS
        root = STANDARD_PARENTS["concept"]
        assert root.is_root is True

    def test_entity_parent(self) -> None:
        """Test concept.entity standard parent."""
        assert "concept.entity" in STANDARD_PARENTS
        entity = STANDARD_PARENTS["concept.entity"]
        assert "concept" in entity.extends
        assert "identify" in entity.affordances

    def test_process_parent(self) -> None:
        """Test concept.process standard parent."""
        assert "concept.process" in STANDARD_PARENTS
        process = STANDARD_PARENTS["concept.process"]
        assert "concept" in process.extends
        assert "execute" in process.affordances
        assert "has_input" in process.constraints
        assert "has_output" in process.constraints

    def test_relation_parent(self) -> None:
        """Test concept.relation standard parent."""
        assert "concept.relation" in STANDARD_PARENTS
        relation = STANDARD_PARENTS["concept.relation"]
        assert "concept" in relation.extends
        assert "connect" in relation.affordances

    def test_property_parent(self) -> None:
        """Test concept.property standard parent."""
        assert "concept.property" in STANDARD_PARENTS
        prop = STANDARD_PARENTS["concept.property"]
        assert "concept" in prop.extends
        assert "measure" in prop.affordances


# === Test Depth Computation ===


class TestDepthComputation:
    """Tests for compute_depth function."""

    def test_depth_no_parents(self) -> None:
        """Test depth computation with no parents."""
        assert compute_depth([]) == 0

    def test_depth_single_parent(self) -> None:
        """Test depth computation with single parent."""
        parent = ConceptLineage(
            handle="concept.entity",
            extends=["concept"],
            depth=1,
        )
        assert compute_depth([parent]) == 2

    def test_depth_multiple_parents(self) -> None:
        """Test depth computation with multiple parents at different depths."""
        parent1 = ConceptLineage(
            handle="concept.entity",
            extends=["concept"],
            depth=1,
        )
        parent2 = ConceptLineage(
            handle="concept.process.workflow",
            extends=["concept.process"],
            depth=2,
        )

        # Should be max(1, 2) + 1 = 3
        assert compute_depth([parent1, parent2]) == 3


# === Test Root Lineage ===


class TestRootLineage:
    """Tests for root lineage creation."""

    def test_create_root(self) -> None:
        """Test root lineage creation."""
        root = create_root_lineage()

        assert root.handle == "concept"
        assert root.extends == []
        assert root.is_root is True
        assert root.depth == 0
        assert root.domain == "meta"
        assert "manifest" in root.affordances
        assert "define" in root.affordances

    def test_root_is_only_orphan(self) -> None:
        """Test that root is the only concept without parents."""
        root = create_root_lineage()
        assert len(root.extends) == 0

        # All standard parents should have at least one parent
        for handle, lineage in STANDARD_PARENTS.items():
            if handle == "concept":
                continue
            assert len(lineage.extends) > 0, f"{handle} has no parents"
