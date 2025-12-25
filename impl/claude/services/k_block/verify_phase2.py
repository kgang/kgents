#!/usr/bin/env python3
"""
Phase 2 Verification Script

Quick sanity check that all Phase 2 components work together.
"""

from services.k_block.core.derivation import DerivationDAG, validate_derivation
from services.k_block.core.kblock import generate_kblock_id
from services.k_block.layers.factories import (
    LAYER_FACTORIES,
    AxiomKBlockFactory,
    ValueKBlockFactory,
    create_kblock_for_layer,
)
from services.k_block.zero_seed_storage import ZeroSeedStorage, reset_zero_seed_storage


def verify_derivation_dag():
    """Verify DerivationDAG works."""
    print("✓ DerivationDAG: Creating DAG...")
    dag = DerivationDAG()

    # Create L1 -> L2 -> L3 chain
    axiom_id = str(generate_kblock_id())
    value_id = str(generate_kblock_id())
    goal_id = str(generate_kblock_id())

    dag.add_node(axiom_id, layer=1, kind="axiom")
    dag.add_node(value_id, layer=2, kind="value", parent_ids=[axiom_id])
    dag.add_node(goal_id, layer=3, kind="goal", parent_ids=[value_id])

    # Verify
    assert len(dag) == 3
    assert dag.is_grounded(goal_id)
    lineage = dag.get_lineage(goal_id)
    assert len(lineage) == 2

    print(f"✓ DerivationDAG: Created {len(dag)} nodes with lineage")


def verify_factories():
    """Verify all layer factories exist."""
    print("✓ Factories: Checking registry...")
    assert len(LAYER_FACTORIES) == 7

    for layer in range(1, 8):
        assert layer in LAYER_FACTORIES

    print("✓ Factories: All 7 layers registered")

    # Create sample nodes
    axiom_id = generate_kblock_id()
    axiom = AxiomKBlockFactory.create(
        kblock_id=axiom_id,
        title="Test Axiom",
        content="Test content",
    )
    assert axiom._layer == 1
    assert axiom._confidence == 1.0

    value_id = generate_kblock_id()
    value = ValueKBlockFactory.create(
        kblock_id=value_id,
        title="Test Value",
        content="Test content",
        lineage=[str(axiom_id)],
    )
    assert value._layer == 2
    assert value._confidence == 0.95

    print("✓ Factories: Created sample L1 and L2 nodes")


def verify_storage():
    """Verify ZeroSeedStorage works."""
    print("✓ Storage: Creating storage...")
    reset_zero_seed_storage()
    storage = ZeroSeedStorage()

    # Create L1 -> L2 chain
    _, axiom_id = storage.create_node(
        layer=1,
        title="Test Axiom",
        content="Test content",
    )

    _, value_id = storage.create_node(
        layer=2,
        title="Test Value",
        content="Test content",
        lineage=[axiom_id],
    )

    # Verify
    assert len(storage) == 2
    assert storage.is_grounded(value_id)

    lineage = storage.get_lineage(value_id)
    assert axiom_id in lineage

    print(f"✓ Storage: Created {len(storage)} nodes with lineage")


def verify_validation():
    """Verify validation helper works."""
    print("✓ Validation: Checking rules...")

    # Valid: L3 derives from L1, L2
    is_valid, error = validate_derivation(3, [1, 2])
    assert is_valid
    assert error is None

    # Invalid: L1 cannot have parents
    is_valid, error = validate_derivation(1, [2])
    assert not is_valid
    assert "Axioms" in error

    # Invalid: upward derivation
    is_valid, error = validate_derivation(2, [3])
    assert not is_valid
    assert "must be lower" in error

    print("✓ Validation: All rules working")


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase 2 Verification")
    print("=" * 60)

    verify_derivation_dag()
    verify_factories()
    verify_storage()
    verify_validation()

    print("=" * 60)
    print("✅ All Phase 2 components verified!")
    print("=" * 60)


if __name__ == "__main__":
    main()
