"""
Tests for Zero Seed K-Block Storage.

Tests CRUD operations for Zero Seed nodes backed by K-Block storage.
"""

import pytest

from ..zero_seed_storage import ZeroSeedStorage, get_zero_seed_storage, reset_zero_seed_storage


@pytest.fixture
def storage():
    """Create fresh storage for each test."""
    reset_zero_seed_storage()
    return ZeroSeedStorage()


def test_create_axiom(storage):
    """Test creating an L1 axiom."""
    kblock, node_id = storage.create_node(
        layer=1,
        title="Entity Axiom",
        content="Everything is a node.",
        lineage=[],
        tags=["foundational"],
    )

    assert node_id is not None
    assert kblock._layer == 1
    assert kblock._kind == "axiom"
    assert kblock._title == "Entity Axiom"
    assert len(storage) == 1


def test_create_value_with_lineage(storage):
    """Test creating an L2 value derived from axiom."""
    # Create axiom first
    _, axiom_id = storage.create_node(
        layer=1,
        title="Axiom",
        content="...",
        lineage=[],
    )

    # Create value deriving from axiom
    kblock, value_id = storage.create_node(
        layer=2,
        title="Value",
        content="...",
        lineage=[axiom_id],
    )

    assert kblock.zero_seed_layer == 2
    assert len(kblock.lineage) == 1
    assert kblock.lineage[0] == axiom_id
    assert len(storage) == 2


def test_create_with_invalid_lineage(storage):
    """Test that invalid lineage is rejected."""
    with pytest.raises(ValueError):
        storage.create_node(
            layer=2,  # Values require lineage
            title="Invalid Value",
            content="...",
            lineage=[],  # No lineage!
        )


def test_get_node(storage):
    """Test retrieving a node by ID."""
    _, node_id = storage.create_node(
        layer=1,
        title="Test",
        content="...",
    )

    kblock = storage.get_node(node_id)
    assert kblock is not None
    assert kblock._title == "Test"

    # Non-existent node
    assert storage.get_node("nonexistent") is None


def test_update_node(storage):
    """Test updating a node."""
    _, node_id = storage.create_node(
        layer=1,
        title="Original",
        content="Original content",
    )

    # Update title and content
    updated = storage.update_node(
        node_id=node_id,
        title="Updated",
        content="New content",
    )

    assert updated is not None
    assert updated._title == "Updated"
    assert updated.content == "New content"


def test_update_confidence(storage):
    """Test updating confidence score."""
    _, node_id = storage.create_node(
        layer=1,
        title="Test",
        content="...",
    )

    # Update confidence
    updated = storage.update_node(
        node_id=node_id,
        confidence=0.75,
    )

    assert updated._confidence == 0.75


def test_update_tags(storage):
    """Test updating tags."""
    _, node_id = storage.create_node(
        layer=1,
        title="Test",
        content="...",
        tags=["old"],
    )

    # Update tags
    updated = storage.update_node(
        node_id=node_id,
        tags=["new1", "new2"],
    )

    assert updated._tags == ["new1", "new2"]


def test_update_nonexistent_node(storage):
    """Test that updating non-existent node returns None."""
    result = storage.update_node(
        node_id="nonexistent",
        title="Updated",
    )
    assert result is None


def test_delete_node(storage):
    """Test deleting a node."""
    _, node_id = storage.create_node(
        layer=1,
        title="Test",
        content="...",
    )

    assert len(storage) == 1

    # Delete
    success = storage.delete_node(node_id)
    assert success is True
    assert len(storage) == 0

    # Verify it's gone
    assert storage.get_node(node_id) is None


def test_delete_nonexistent_node(storage):
    """Test deleting non-existent node returns False."""
    success = storage.delete_node("nonexistent")
    assert success is False


def test_get_lineage(storage):
    """Test getting full lineage to axioms."""
    # Create L1 -> L2 -> L3 chain
    _, axiom_id = storage.create_node(layer=1, title="Axiom", content="...")
    _, value_id = storage.create_node(layer=2, title="Value", content="...", lineage=[axiom_id])
    _, goal_id = storage.create_node(layer=3, title="Goal", content="...", lineage=[value_id])

    # Get lineage of goal
    lineage = storage.get_lineage(goal_id)

    assert len(lineage) == 2
    assert value_id in lineage
    assert axiom_id in lineage


def test_get_descendants(storage):
    """Test getting all descendants."""
    # Create L1 -> L2 -> L3 chain
    _, axiom_id = storage.create_node(layer=1, title="Axiom", content="...")
    _, value_id = storage.create_node(layer=2, title="Value", content="...", lineage=[axiom_id])
    _, goal_id = storage.create_node(layer=3, title="Goal", content="...", lineage=[value_id])

    # Get descendants of axiom
    descendants = storage.get_descendants(axiom_id)

    assert len(descendants) == 2
    assert value_id in descendants
    assert goal_id in descendants


def test_get_layer_nodes(storage):
    """Test getting all nodes in a specific layer."""
    # Create multiple nodes in different layers
    _, axiom1 = storage.create_node(layer=1, title="Axiom 1", content="...")
    _, axiom2 = storage.create_node(layer=1, title="Axiom 2", content="...")
    _, value = storage.create_node(layer=2, title="Value", content="...", lineage=[axiom1])

    # Get L1 nodes
    l1_nodes = storage.get_layer_nodes(1)
    assert len(l1_nodes) == 2
    assert all(node._layer == 1 for node in l1_nodes)

    # Get L2 nodes
    l2_nodes = storage.get_layer_nodes(2)
    assert len(l2_nodes) == 1
    assert l2_nodes[0]._title == "Value"


def test_is_grounded(storage):
    """Test checking if lineage terminates at axioms."""
    # Create grounded chain
    _, axiom_id = storage.create_node(layer=1, title="Axiom", content="...")
    _, value_id = storage.create_node(layer=2, title="Value", content="...", lineage=[axiom_id])

    # Value should be grounded
    assert storage.is_grounded(value_id) is True

    # Axiom is grounded (it's the root)
    assert storage.is_grounded(axiom_id) is True

    # Create ungrounded orphan (L3 with no parents - violates rules but for testing)
    # Note: This would normally be rejected by factory validation, but we can test DAG directly
    # For now, just test the positive case


def test_dag_access(storage):
    """Test accessing the derivation DAG."""
    _, axiom_id = storage.create_node(layer=1, title="Axiom", content="...")

    dag = storage.dag
    assert dag is not None
    assert len(dag) == 1


def test_global_storage_singleton():
    """Test global storage singleton."""
    reset_zero_seed_storage()

    storage1 = get_zero_seed_storage()
    storage2 = get_zero_seed_storage()

    # Should be same instance
    assert storage1 is storage2

    # Create node in storage1
    _, node_id = storage1.create_node(layer=1, title="Test", content="...")

    # Should be visible in storage2
    kblock = storage2.get_node(node_id)
    assert kblock is not None


def test_reset_storage():
    """Test resetting global storage."""
    storage1 = get_zero_seed_storage()
    _, node_id = storage1.create_node(layer=1, title="Test", content="...")

    # Reset
    reset_zero_seed_storage()

    # New storage should be empty
    storage2 = get_zero_seed_storage()
    assert storage2.get_node(node_id) is None
    assert len(storage2) == 0


def test_multiple_parents(storage):
    """Test node deriving from multiple parents."""
    # Create two axioms
    _, axiom1 = storage.create_node(layer=1, title="Axiom 1", content="...")
    _, axiom2 = storage.create_node(layer=1, title="Axiom 2", content="...")

    # Create value deriving from both
    _, value_id = storage.create_node(
        layer=2,
        title="Composite Value",
        content="...",
        lineage=[axiom1, axiom2],
    )

    # Lineage should include both parents
    lineage = storage.get_lineage(value_id)
    assert len(lineage) == 2
    assert axiom1 in lineage
    assert axiom2 in lineage
