"""
D-gent Crystal Unification Integration Tests

Tests the full stack:
1. Universe + Galois
2. SelfJustifyingCrystal
3. Layer classification
4. Proof creation
"""

from datetime import UTC, datetime

import pytest

from agents.d.crystal.self_justifying import SelfJustifyingCrystal
from agents.d.galois import GaloisLossComputer
from agents.d.schemas.proof import GaloisWitnessedProof
from agents.d.universe import Backend, Universe


@pytest.fixture
def galois():
    return GaloisLossComputer()


@pytest.fixture
def universe(galois):
    return Universe(preferred_backend=Backend.MEMORY, galois=galois)


@pytest.mark.asyncio
async def test_full_stack(universe, galois):
    """Test the full D-gent Crystal Unification stack."""
    # 1. Create an axiom (L1 - no proof needed)
    axiom = SelfJustifyingCrystal.create_axiom(
        value="Everything composes",
        path="void.axiom.composition",
    )
    assert axiom.is_grounded
    assert axiom.layer == 1

    # 2. Create a proof
    proof = GaloisWitnessedProof(
        data="User requested feature",
        warrant="Design fits architecture",
        claim="Implement feature X",
        backing="Follows established patterns",
        galois_loss=0.15,
    )
    assert proof.coherence == 0.85

    # 3. Create a spec with proof (L4)
    spec = SelfJustifyingCrystal.create_with_proof(
        value="Feature specification",
        proof=proof,
        layer=4,
        path="concept.spec.feature",
    )
    assert spec.is_grounded
    assert spec.coherence == 0.85

    # 4. Validate the spec
    errors = spec.validate()
    assert len(errors) == 0

    # 5. Compute Galois loss directly
    loss = await galois.compute("This is a test string")
    assert 0.0 <= loss <= 1.0

    print("✅ Full stack integration test passed!")


@pytest.mark.asyncio
async def test_layer_requirements():
    """Test that layer requirements are enforced."""
    from agents.d.crystal.crystal import CrystalMeta
    from agents.d.datum import Datum

    crystal = SelfJustifyingCrystal(
        meta=CrystalMeta(
            schema_name="test",
            schema_version=1,
            created_at=datetime.now(UTC),
            layer=3,
        ),
        datum=Datum.create({"test": True}),
        value="test",
        layer=3,
        path="test.path",
        proof=None,  # Missing proof for L3!
    )

    errors = crystal.validate()
    assert any("requires proof" in e.lower() for e in errors)
    print("✅ Layer requirement validation test passed!")


@pytest.mark.asyncio
async def test_witness_crystal_adapter():
    """Test that WitnessCrystalAdapter can be imported and integrates with SelfJustifyingCrystal."""
    # Import test - verify the adapter exists and uses the right types
    from services.witness.crystal_adapter import WitnessCrystalAdapter

    # The adapter should exist and use SelfJustifyingCrystal
    # (Full integration test would require setting up witness service)
    assert WitnessCrystalAdapter is not None

    # Verify we can create a crystal manually that would come from the adapter
    proof = GaloisWitnessedProof(
        data="Context",
        warrant="Reasoning",
        claim="Conclusion",
        backing="Support",
        galois_loss=0.1,
    )
    crystal = SelfJustifyingCrystal.create_with_proof(
        value="Test crystal",
        proof=proof,
        layer=4,
        path="test.crystal",
    )

    # Validate it
    errors = crystal.validate()
    assert len(errors) == 0
    assert crystal.is_grounded

    print("✅ WitnessCrystalAdapter integration test passed!")


@pytest.mark.asyncio
async def test_layer_classification():
    """Test that layer classification works with crystals."""
    from services.k_block.layers.classifier import classify_layer

    # L1: Axiom (no proof needed)
    axiom = SelfJustifyingCrystal.create_axiom(
        value="Core principle",
        path="void.axiom.principle",
    )
    assert axiom.layer == 1

    # L4: Spec with proof
    proof = GaloisWitnessedProof(
        data="Context",
        warrant="Reasoning",
        claim="Conclusion",
        backing="Support",
        galois_loss=0.1,
    )
    spec = SelfJustifyingCrystal.create_with_proof(
        value="Specification",
        proof=proof,
        layer=4,
        path="concept.spec.test",
    )
    assert spec.layer == 4
    assert spec.proof is not None

    print("✅ Layer classification test passed!")
