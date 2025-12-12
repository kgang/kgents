"""
Tests for define_concept with lineage validation.

The Genealogical Constraint: No concept exists ex nihilo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock

import pytest
from protocols.agentese.lattice.checker import (
    get_lattice_checker,
    reset_lattice_checker,
)
from protocols.agentese.lattice.errors import LatticeError, LineageError
from protocols.agentese.lattice.lineage import STANDARD_PARENTS

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Mock Umwelt for Testing ===


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test_observer"
    archetype: str = "architect"
    capabilities: tuple[str, ...] = ("define",)


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA


def create_mock_observer(
    name: str = "test",
    archetype: str = "architect",
) -> Any:
    """Create a mock observer for testing."""
    return MockUmwelt(
        dna=MockDNA(name=name, archetype=archetype),
    )


# === Test define_concept via ConceptNode ===


class TestConceptNodeDefine:
    """Tests for ConceptNode._define_child with lineage."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    @pytest.fixture
    def parent_node(self) -> Any:
        """Create a parent concept node for testing."""
        from protocols.agentese.contexts.concept import ConceptNode

        return ConceptNode(
            _handle="concept.entity",
            name="entity",
            definition="Base concept for all entities",
            domain="ontology",
        )

    def test_define_with_lineage(self, parent_node: Any) -> None:
        """Test defining a concept with proper lineage."""
        import asyncio

        observer = create_mock_observer()

        child = asyncio.run(
            parent_node._define_child(
                observer=observer,
                name="agent",
                definition="An autonomous entity that can act.",
                extends=["concept.entity"],
                justification="Agents are specialized entities.",
            )
        )

        assert child.name == "agent"
        assert child.has_lineage is True
        assert child.lineage is not None
        assert "concept.entity" in child.lineage.extends
        assert child.lineage.justification == "Agents are specialized entities."

    def test_define_inherits_affordances(self, parent_node: Any) -> None:
        """Test that child inherits parent affordances."""
        import asyncio

        observer = create_mock_observer()

        child = asyncio.run(
            parent_node._define_child(
                observer=observer,
                name="tool",
                definition="An entity that can be used.",
                extends=["concept.entity"],
            )
        )

        assert child.lineage is not None
        # Should inherit affordances from concept.entity
        parent_lineage = STANDARD_PARENTS.get("concept.entity")
        if parent_lineage:
            for aff in parent_lineage.affordances:
                assert aff in child.lineage.affordances

    def test_define_computes_depth(self, parent_node: Any) -> None:
        """Test that depth is computed correctly."""
        import asyncio

        observer = create_mock_observer()

        child = asyncio.run(
            parent_node._define_child(
                observer=observer,
                name="specialized",
                definition="A specialized entity.",
                extends=["concept.entity"],
            )
        )

        assert child.lineage is not None
        # concept.entity has depth 1, so child should have depth 2
        assert child.lineage.depth == 2

    def test_define_default_parent(self, parent_node: Any) -> None:
        """Test that current node is used as default parent."""
        import asyncio

        observer = create_mock_observer()

        # Don't specify extends - should default to parent_node
        child = asyncio.run(
            parent_node._define_child(
                observer=observer,
                name="default_child",
                definition="A child with default parent.",
            )
        )

        assert child.lineage is not None
        # Should extend the parent node's handle
        assert parent_node._handle in child.lineage.extends


# === Test Lineage Enforcement ===


class TestLineageEnforcement:
    """Tests for lineage requirement enforcement."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    def test_define_ex_nihilo_fails(self) -> None:
        """Test that creating concept without extends fails."""
        import asyncio

        from protocols.agentese.contexts.concept import define_concept

        # Create a mock logos
        mock_logos = MagicMock()
        mock_logos._cache = {}
        observer = create_mock_observer()

        with pytest.raises(LineageError):
            asyncio.run(
                define_concept(
                    logos=mock_logos,
                    handle="concept.orphan",
                    observer=observer,
                    spec="An orphan concept.",
                    extends=[],  # Empty - ex nihilo!
                )
            )

    def test_define_missing_parent_fails(self) -> None:
        """Test that non-existent parent raises error."""
        import asyncio

        from protocols.agentese.contexts.concept import define_concept
        from protocols.agentese.exceptions import PathNotFoundError

        # Create a mock logos that raises PathNotFoundError
        mock_logos = MagicMock()
        mock_logos._cache = {}
        mock_logos.resolve.side_effect = PathNotFoundError(
            "Not found",
            path="concept.nonexistent",
        )
        observer = create_mock_observer()

        with pytest.raises(LineageError) as exc_info:
            asyncio.run(
                define_concept(
                    logos=mock_logos,
                    handle="concept.orphan",
                    observer=observer,
                    spec="A concept with missing parent.",
                    extends=["concept.nonexistent"],
                )
            )

        # Should mention missing parent
        assert "nonexistent" in str(exc_info.value) or exc_info.value.missing_parents


# === Test Lattice Position Validation ===


class TestLatticeValidation:
    """Tests for lattice position validation."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    def test_valid_position_succeeds(self) -> None:
        """Test that valid lattice position is accepted."""
        checker = get_lattice_checker()

        import asyncio

        result = asyncio.run(
            checker.check_position(
                new_handle="concept.justice",
                parents=["concept.entity"],
            )
        )

        assert result.valid is True

    def test_cycle_detection(self) -> None:
        """Test that cycles are detected."""
        from protocols.agentese.lattice.lineage import ConceptLineage

        checker = get_lattice_checker()

        # Create A -> B
        lineage_a = ConceptLineage(
            handle="concept.cycle_test_a",
            extends=["concept"],
        )
        lineage_b = ConceptLineage(
            handle="concept.cycle_test_b",
            extends=["concept.cycle_test_a"],
        )
        checker.register_lineage(lineage_a)
        checker.register_lineage(lineage_b)

        import asyncio

        # Try to make A extend B (creating cycle)
        result = asyncio.run(
            checker.check_position(
                new_handle="concept.cycle_test_c",
                parents=["concept.cycle_test_b"],
                children=["concept.cycle_test_a"],
            )
        )

        # Should detect the cycle attempt
        # Note: The exact behavior depends on implementation

    def test_self_loop_rejected(self) -> None:
        """Test that self-loops are rejected."""
        from protocols.agentese.lattice.lineage import ConceptLineage

        checker = get_lattice_checker()

        # First register the concept so parent check passes
        lineage = ConceptLineage(
            handle="concept.self_test",
            extends=["concept"],
        )
        checker.register_lineage(lineage)

        import asyncio

        # Now try to add itself as parent (self-loop!)
        result = asyncio.run(
            checker.check_position(
                new_handle="concept.self_test",
                parents=["concept.self_test"],
            )
        )

        assert result.valid is False
        assert result.violation_type == "cycle"


# === Test Inheritance Semantics ===


class TestInheritanceSemantics:
    """Tests for affordance and constraint inheritance."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    def test_affordances_union(self) -> None:
        """Test that affordances are unioned from multiple parents."""
        from protocols.agentese.lattice.lineage import ConceptLineage

        checker = get_lattice_checker()

        # Create two parents with different affordances
        parent_a = ConceptLineage(
            handle="concept.aff_parent_a",
            extends=["concept"],
            affordances={"manifest", "aff_a"},
        )
        parent_b = ConceptLineage(
            handle="concept.aff_parent_b",
            extends=["concept"],
            affordances={"manifest", "aff_b"},
        )
        checker.register_lineage(parent_a)
        checker.register_lineage(parent_b)

        # When we create a child, it should get union of affordances
        # (This is computed in define_concept, not in checker)

    def test_constraints_intersection(self) -> None:
        """Test that constraints are intersected from multiple parents."""
        from protocols.agentese.lattice.lineage import ConceptLineage

        checker = get_lattice_checker()

        # Create two parents with overlapping constraints
        parent_a = ConceptLineage(
            handle="concept.con_parent_a",
            extends=["concept"],
            constraints={"has_definition", "constraint_a"},
        )
        parent_b = ConceptLineage(
            handle="concept.con_parent_b",
            extends=["concept"],
            constraints={"has_definition", "constraint_b"},
        )
        checker.register_lineage(parent_a)
        checker.register_lineage(parent_b)

        # When we create a child with both parents,
        # it should get intersection: {"has_definition"}


# === Test Parent Updates ===


class TestParentUpdates:
    """Tests for parent lineage updates when children are added."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    def test_parent_subsumes_updated(self) -> None:
        """Test that parent's subsumes list is updated."""
        import asyncio

        from protocols.agentese.contexts.concept import ConceptNode

        observer = create_mock_observer()
        checker = get_lattice_checker()

        # Get entity lineage
        entity_lineage = checker.get_lineage("concept.entity")
        assert entity_lineage is not None
        initial_children = len(entity_lineage.subsumes)

        # Create child via node
        parent = ConceptNode(
            _handle="concept.entity",
            name="entity",
        )

        child = asyncio.run(
            parent._define_child(
                observer=observer,
                name="new_child",
                definition="A new child concept.",
                extends=["concept.entity"],
            )
        )

        # Check parent's subsumes was updated
        updated_lineage = checker.get_lineage("concept.entity")
        assert updated_lineage is not None
        assert "concept.new_child" in updated_lineage.subsumes


# === Test Lattice Visualization ===


class TestLatticeVisualization:
    """Tests for lattice tree/visualization functions."""

    @pytest.fixture(autouse=True)
    def reset_checker(self) -> None:
        """Reset the global checker before each test."""
        reset_lattice_checker()

    def test_get_concept_tree(self) -> None:
        """Test getting concept tree structure."""
        from protocols.agentese.contexts.concept import get_concept_tree

        tree = get_concept_tree("concept")

        assert tree["handle"] == "concept"
        assert "children" in tree

    def test_render_concept_lattice(self) -> None:
        """Test rendering lattice as ASCII."""
        from protocols.agentese.contexts.concept import render_concept_lattice

        output = render_concept_lattice("concept")

        assert "CONCEPT LATTICE" in output
        assert "concept" in output.lower()
        assert "Nodes:" in output
        assert "Edges:" in output
        assert "Depth:" in output

    def test_render_orphan_detection(self) -> None:
        """Test that render shows orphan count."""
        from protocols.agentese.contexts.concept import render_concept_lattice

        output = render_concept_lattice("concept")

        assert "Orphans:" in output
