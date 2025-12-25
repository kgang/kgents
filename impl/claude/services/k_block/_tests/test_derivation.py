"""
Tests for K-Block Derivation DAG.

Tests derivation tracking, lineage validation, and layer monotonicity.
"""

import pytest

from ..core.derivation import DerivationDAG, DerivationNode, validate_derivation
from ..core.kblock import generate_kblock_id


def test_create_dag():
    """Test creating an empty DAG."""
    dag = DerivationDAG()
    assert len(dag) == 0


def test_add_axiom_node():
    """Test adding an L1 axiom node (no parents)."""
    dag = DerivationDAG()
    kblock_id = str(generate_kblock_id())

    node = dag.add_node(kblock_id, layer=1, kind="axiom", parent_ids=[])

    assert node.kblock_id == kblock_id
    assert node.layer == 1
    assert node.kind == "axiom"
    assert len(node.parent_ids) == 0
    assert len(node.child_ids) == 0
    assert len(dag) == 1


def test_add_value_with_lineage():
    """Test adding an L2 value derived from L1 axiom."""
    dag = DerivationDAG()

    # Create axiom
    axiom_id = str(generate_kblock_id())
    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])

    # Create value deriving from axiom
    value_id = str(generate_kblock_id())
    value_node = dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])

    assert len(value_node.parent_ids) == 1
    assert value_node.parent_ids[0] == axiom_id
    assert len(dag) == 2

    # Check parent's child list was updated
    axiom_node = dag.get_node(axiom_id)
    assert axiom_node is not None
    assert len(axiom_node.child_ids) == 1
    assert axiom_node.child_ids[0] == value_id


def test_layer_monotonicity_violation():
    """Test that layer monotonicity is enforced."""
    dag = DerivationDAG()

    # Create L3 goal
    goal_id = str(generate_kblock_id())
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[])

    # Try to create L2 value deriving from L3 goal (invalid!)
    value_id = str(generate_kblock_id())
    with pytest.raises(ValueError, match="Layer monotonicity violation"):
        dag.add_node(value_id, layer=2, kind="value", parent_ids=[goal_id])


def test_get_lineage():
    """Test tracing lineage to axioms."""
    dag = DerivationDAG()

    # Create L1 -> L2 -> L3 chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())
    goal_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[value_id])

    # Get lineage of goal
    lineage = dag.get_lineage(goal_id)

    # Should contain value and axiom
    assert len(lineage) == 2
    assert value_id in lineage
    assert axiom_id in lineage


def test_get_descendants():
    """Test getting all descendants of a node."""
    dag = DerivationDAG()

    # Create L1 -> L2 -> L3 chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())
    goal_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[value_id])

    # Get descendants of axiom
    descendants = dag.get_descendants(axiom_id)

    # Should contain value and goal
    assert len(descendants) == 2
    assert value_id in descendants
    assert goal_id in descendants


def test_get_layer_nodes():
    """Test getting all nodes in a specific layer."""
    dag = DerivationDAG()

    # Create multiple axioms
    axiom1_id = str(generate_kblock_id())
    axiom2_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())

    dag.add_node(axiom1_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(axiom2_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom1_id])

    # Get L1 nodes
    l1_nodes = dag.get_layer_nodes(1)
    assert len(l1_nodes) == 2
    assert all(node.layer == 1 for node in l1_nodes)

    # Get L2 nodes
    l2_nodes = dag.get_layer_nodes(2)
    assert len(l2_nodes) == 1
    assert l2_nodes[0].kblock_id == value_id


def test_validate_acyclic():
    """Test cycle detection."""
    dag = DerivationDAG()

    # Create L1 -> L2 -> L3 chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())
    goal_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[value_id])

    # Should be acyclic
    assert dag.validate_acyclic(goal_id) is True
    assert dag.validate_acyclic(value_id) is True
    assert dag.validate_acyclic(axiom_id) is True


def test_is_grounded():
    """Test checking if lineage terminates at L1 axioms."""
    dag = DerivationDAG()

    # Create properly grounded chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())
    goal_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[value_id])

    # Goal should be grounded
    assert dag.is_grounded(goal_id) is True

    # Create ungrounded node (no parents)
    orphan_id = str(generate_kblock_id())
    dag.add_node(orphan_id, layer=3, kind="goal", parent_ids=[])

    # Orphan should NOT be grounded
    assert dag.is_grounded(orphan_id) is False


def test_dag_serialization():
    """Test DAG serialization and deserialization."""
    dag = DerivationDAG()

    # Create chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])

    # Serialize
    data = dag.to_dict()
    assert "nodes" in data
    assert len(data["nodes"]) == 2

    # Deserialize
    dag2 = DerivationDAG.from_dict(data)
    assert len(dag2) == 2
    assert dag2.get_node(axiom_id) is not None
    assert dag2.get_node(value_id) is not None


def test_validate_derivation_helper():
    """Test the validate_derivation helper function."""
    # Valid: L3 Goal derives from L1 Axiom and L2 Value
    is_valid, error = validate_derivation(3, [1, 2])
    assert is_valid is True
    assert error is None

    # Invalid: L1 Axiom cannot have parents
    is_valid, error = validate_derivation(1, [2])
    assert is_valid is False
    assert "Axioms (L1) cannot have parent derivations" in error

    # Invalid: L2 Value cannot derive from L3 Goal (upward)
    is_valid, error = validate_derivation(2, [3])
    assert is_valid is False
    assert "Parent layer (3) must be lower than child (2)" in error

    # Valid: L5 Action derives from L3 Goal (gap is OK)
    is_valid, error = validate_derivation(5, [3])
    assert is_valid is True
    assert error is None


def test_multiple_parents():
    """Test node with multiple parents (diamond pattern)."""
    dag = DerivationDAG()

    # Create two axioms
    axiom1_id = str(generate_kblock_id())
    axiom2_id = str(generate_kblock_id())
    dag.add_node(axiom1_id, layer=1, kind="axiom", parent_ids=[])
    dag.add_node(axiom2_id, layer=1, kind="axiom", parent_ids=[])

    # Create value deriving from BOTH axioms
    value_id = str(generate_kblock_id())
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom1_id, axiom2_id])

    # Check lineage includes both parents
    lineage = dag.get_lineage(value_id)
    assert len(lineage) == 2
    assert axiom1_id in lineage
    assert axiom2_id in lineage

    # Both axioms should list value as child
    axiom1 = dag.get_node(axiom1_id)
    axiom2 = dag.get_node(axiom2_id)
    assert value_id in axiom1.child_ids
    assert value_id in axiom2.child_ids
