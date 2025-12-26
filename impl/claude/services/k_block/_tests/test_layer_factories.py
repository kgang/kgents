"""
Tests for K-Block Layer Factories.

Tests creation of Zero Seed L1-L7 K-Blocks with proper lineage validation.
"""

import pytest

from ..core.kblock import generate_kblock_id
from ..layers.factories import (
    LAYER_FACTORIES,
    ActionKBlockFactory,
    AxiomKBlockFactory,
    GoalKBlockFactory,
    ReflectionKBlockFactory,
    RepresentationKBlockFactory,
    SpecKBlockFactory,
    ValueKBlockFactory,
    create_kblock_for_layer,
)


def test_axiom_factory():
    """Test creating L1 Axiom K-Block."""
    kblock_id = generate_kblock_id()

    kblock = AxiomKBlockFactory.create(
        kblock_id=kblock_id,
        title="Entity Axiom",
        content="Everything is a node.",
        lineage=[],
        tags=["foundational"],
    )

    assert kblock.id == kblock_id
    assert kblock.zero_seed_layer == 1
    assert kblock.zero_seed_kind == "axiom"
    assert kblock._title == "Entity Axiom"
    assert kblock.content == "Everything is a node."
    assert kblock.confidence == 1.0  # Axioms have max confidence
    assert len(kblock.lineage) == 0
    assert "foundational" in kblock._tags
    assert "void.axiom" in kblock.path


def test_axiom_rejects_lineage():
    """Test that axioms cannot have lineage."""
    kblock_id = generate_kblock_id()
    parent_id = str(generate_kblock_id())

    with pytest.raises(ValueError, match="cannot have lineage"):
        AxiomKBlockFactory.create(
            kblock_id=kblock_id,
            title="Invalid Axiom",
            content="This should fail",
            lineage=[parent_id],
        )


def test_value_factory():
    """Test creating L2 Value K-Block."""
    kblock_id = generate_kblock_id()
    axiom_id = str(generate_kblock_id())

    kblock = ValueKBlockFactory.create(
        kblock_id=kblock_id,
        title="Composability Value",
        content="Agents should compose.",
        lineage=[axiom_id],
        tags=["principle"],
    )

    assert kblock.zero_seed_layer == 2
    assert kblock.zero_seed_kind == "value"
    assert kblock.confidence == 0.95  # Values have high confidence
    assert len(kblock.lineage) == 1
    assert kblock.lineage[0] == axiom_id
    assert "void.value" in kblock.path


def test_value_requires_lineage():
    """Test that values require at least one axiom."""
    kblock_id = generate_kblock_id()

    with pytest.raises(ValueError, match="must derive from at least one"):
        ValueKBlockFactory.create(
            kblock_id=kblock_id,
            title="Invalid Value",
            content="This should fail",
            lineage=[],
        )


def test_goal_factory():
    """Test creating L3 Goal K-Block."""
    kblock_id = generate_kblock_id()
    value_id = str(generate_kblock_id())

    kblock = GoalKBlockFactory.create(
        kblock_id=kblock_id,
        title="Build K-Block System",
        content="Create transactional editing for specs.",
        lineage=[value_id],
    )

    assert kblock.zero_seed_layer == 3
    assert kblock.zero_seed_kind == "goal"
    assert kblock.confidence == 0.90
    assert "concept.goal" in kblock.path


def test_spec_factory():
    """Test creating L4 Spec K-Block."""
    kblock_id = generate_kblock_id()
    goal_id = str(generate_kblock_id())

    kblock = SpecKBlockFactory.create(
        kblock_id=kblock_id,
        title="K-Block API",
        content="# K-Block API\n\n## Harness Operations\n...",
        lineage=[goal_id],
    )

    assert kblock.zero_seed_layer == 4
    assert kblock.zero_seed_kind == "spec"
    assert kblock.confidence == 0.85
    assert "concept.spec" in kblock.path


def test_action_factory():
    """Test creating L5 Action K-Block."""
    kblock_id = generate_kblock_id()
    spec_id = str(generate_kblock_id())

    kblock = ActionKBlockFactory.create(
        kblock_id=kblock_id,
        title="Implement Harness",
        content="Implemented FileOperadHarness with save/discard/fork.",
        lineage=[spec_id],
    )

    assert kblock.zero_seed_layer == 5
    assert kblock.zero_seed_kind == "action"
    assert kblock.confidence == 0.80
    assert "world.action" in kblock.path


def test_reflection_factory():
    """Test creating L6 Reflection K-Block."""
    kblock_id = generate_kblock_id()
    action_id = str(generate_kblock_id())

    kblock = ReflectionKBlockFactory.create(
        kblock_id=kblock_id,
        title="Harness Implementation Reflection",
        content="The harness works but merge conflicts need improvement.",
        lineage=[action_id],
    )

    assert kblock.zero_seed_layer == 6
    assert kblock.zero_seed_kind == "reflection"
    assert kblock.confidence == 0.75
    assert "self.reflection" in kblock.path


def test_representation_factory():
    """Test creating L7 Representation K-Block."""
    kblock_id = generate_kblock_id()
    # Representations can derive from any layer
    spec_id = str(generate_kblock_id())

    kblock = RepresentationKBlockFactory.create(
        kblock_id=kblock_id,
        title="K-Block Diagram",
        content="[SVG diagram of K-Block architecture]",
        lineage=[spec_id],
    )

    assert kblock.zero_seed_layer == 7
    assert kblock.zero_seed_kind == "representation"
    assert kblock.confidence == 0.70
    assert "void.representation" in kblock.path


def test_representation_accepts_any_lineage():
    """Test that representations can derive from any layer."""
    kblock_id = generate_kblock_id()

    # No lineage is OK
    kblock1 = RepresentationKBlockFactory.create(
        kblock_id=kblock_id,
        title="Standalone Diagram",
        content="...",
        lineage=[],
    )
    assert len(kblock1.lineage) == 0

    # Lineage from any layer is OK
    kblock_id2 = generate_kblock_id()
    parent_id = str(generate_kblock_id())
    kblock2 = RepresentationKBlockFactory.create(
        kblock_id=kblock_id2,
        title="Derived Diagram",
        content="...",
        lineage=[parent_id],
    )
    assert len(kblock2.lineage) == 1


def test_layer_factory_registry():
    """Test that all layers have factories registered."""
    # L0 is ZeroSeedKBlockFactory (system), L1-L7 are user-facing layers
    assert len(LAYER_FACTORIES) == 8
    for layer in range(0, 8):  # 0-7
        assert layer in LAYER_FACTORIES


def test_create_kblock_for_layer():
    """Test dynamic factory selection."""
    kblock_id = generate_kblock_id()

    # Create L1 Axiom
    kblock = create_kblock_for_layer(
        layer=1,
        kblock_id=kblock_id,
        title="Test Axiom",
        content="Test content",
        lineage=[],
    )

    assert kblock.zero_seed_layer == 1
    assert kblock.zero_seed_kind == "axiom"


def test_create_kblock_for_layer_invalid():
    """Test that invalid layers raise error."""
    kblock_id = generate_kblock_id()

    # Layer 8 is invalid (valid range is 0-7)
    with pytest.raises(ValueError, match="Invalid layer"):
        create_kblock_for_layer(
            layer=8,  # Invalid!
            kblock_id=kblock_id,
            title="Invalid",
            content="...",
        )

    # Layer -1 is invalid
    with pytest.raises(ValueError, match="Invalid layer"):
        create_kblock_for_layer(
            layer=-1,  # Invalid!
            kblock_id=kblock_id,
            title="Invalid",
            content="...",
        )


def test_custom_confidence():
    """Test overriding default confidence."""
    kblock_id = generate_kblock_id()
    axiom_id = str(generate_kblock_id())

    # Default confidence for value is 0.95
    kblock1 = ValueKBlockFactory.create(
        kblock_id=kblock_id,
        title="Value",
        content="...",
        lineage=[axiom_id],
    )
    assert kblock1.confidence == 0.95

    # Custom confidence
    kblock_id2 = generate_kblock_id()
    kblock2 = ValueKBlockFactory.create(
        kblock_id=kblock_id2,
        title="Uncertain Value",
        content="...",
        lineage=[axiom_id],
        confidence=0.60,
    )
    assert kblock2.confidence == 0.60


def test_path_generation():
    """Test AGENTESE path generation."""
    kblock_id = generate_kblock_id()

    kblock = AxiomKBlockFactory.create(
        kblock_id=kblock_id,
        title="Entity and Morphism",
        content="...",
    )

    # Should slugify title
    assert "void.axiom.entity_and_morphism" in kblock.path


def test_created_by_metadata():
    """Test creator tracking."""
    kblock_id = generate_kblock_id()

    # Default creator
    kblock1 = AxiomKBlockFactory.create(
        kblock_id=kblock_id,
        title="System Axiom",
        content="...",
    )
    assert kblock1._created_by == "system"

    # Custom creator
    kblock_id2 = generate_kblock_id()
    kblock2 = AxiomKBlockFactory.create(
        kblock_id=kblock_id2,
        title="User Axiom",
        content="...",
        created_by="user@example.com",
    )
    assert kblock2._created_by == "user@example.com"


def test_edge_creation_from_lineage():
    """Test that edges are created from lineage."""
    kblock_id = generate_kblock_id()
    axiom_id = str(generate_kblock_id())

    # Create a value with lineage from axiom
    kblock = ValueKBlockFactory.create(
        kblock_id=kblock_id,
        title="Test Value",
        content="A value derived from an axiom.",
        lineage=[axiom_id],
    )

    # Should have exactly one incoming edge
    assert hasattr(kblock, "incoming_edges")
    assert len(kblock.incoming_edges) == 1

    # Edge should be derives_from type
    edge = kblock.incoming_edges[0]
    assert edge.source_id == axiom_id
    assert edge.target_id == kblock_id
    assert edge.edge_type == "derives_from"

    # No outgoing edges at creation
    assert hasattr(kblock, "outgoing_edges")
    assert len(kblock.outgoing_edges) == 0


def test_multiple_edges_from_lineage():
    """Test that multiple lineage parents create multiple edges."""
    kblock_id = generate_kblock_id()
    parent1 = str(generate_kblock_id())
    parent2 = str(generate_kblock_id())
    parent3 = str(generate_kblock_id())

    # Create a value with multiple parents (unusual but valid)
    kblock = ValueKBlockFactory.create(
        kblock_id=kblock_id,
        title="Multi-Parent Value",
        content="Derived from multiple axioms.",
        lineage=[parent1, parent2, parent3],
    )

    # Should have three incoming edges
    assert len(kblock.incoming_edges) == 3

    # Each parent should have an edge
    source_ids = {edge.source_id for edge in kblock.incoming_edges}
    assert source_ids == {parent1, parent2, parent3}

    # All edges should point to this K-Block
    for edge in kblock.incoming_edges:
        assert edge.target_id == kblock_id
        assert edge.edge_type == "derives_from"


def test_axiom_has_no_edges():
    """Test that axioms (no lineage) have no incoming edges."""
    kblock_id = generate_kblock_id()

    kblock = AxiomKBlockFactory.create(
        kblock_id=kblock_id,
        title="Foundational Axiom",
        content="The axiom needs no proof.",
        lineage=[],
    )

    # No incoming edges for axioms
    assert len(kblock.incoming_edges) == 0
    assert len(kblock.outgoing_edges) == 0
