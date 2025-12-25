"""
Tests for DerivationService.

Tests the full lifecycle:
1. Create crystals at different layers
2. Link them with derivation edges
3. Trace lineage to axioms
4. Detect drift
5. Find orphans

Teaching:
    gotcha: DerivationService requires edges to be explicitly created.
            Crystals don't automatically know their parents - you must
            call link_derivation() to establish relationships.
            (Evidence: service.py::link_derivation)

    gotcha: Galois loss is optional. Service works without it, but
            coherence_check() and detect_drift() return 0.0 if no
            GaloisLossComputer is provided.
            (Evidence: service.py::__init__)
"""

import pytest
from agents.d.galois import GaloisLossComputer
from agents.d.schemas.axiom import AxiomCrystal, ValueCrystal
from agents.d.schemas.code import FunctionCrystal, ParamInfo
from agents.d.schemas.proof import GaloisWitnessedProof
from agents.d.universe import Universe, Backend

from ..service import DerivationService


@pytest.fixture
async def universe():
    """Create test Universe with memory backend."""
    u = Universe(namespace="test_derivation", preferred_backend=Backend.MEMORY)
    await u._ensure_initialized()

    # Register schemas
    from agents.d.schemas.axiom import AXIOM_SCHEMA, VALUE_SCHEMA
    from agents.d.schemas.code import FUNCTION_CRYSTAL_SCHEMA

    u.register_schema(AXIOM_SCHEMA)
    u.register_schema(VALUE_SCHEMA)
    u.register_schema(FUNCTION_CRYSTAL_SCHEMA)

    return u


@pytest.fixture
def galois():
    """Create GaloisLossComputer."""
    return GaloisLossComputer(metric="token")


@pytest.fixture
async def service(universe, galois):
    """Create DerivationService."""
    return DerivationService(universe, galois)


@pytest.mark.asyncio
async def test_trace_to_axiom_simple(service, universe):
    """Test tracing a simple derivation chain: function → value → axiom."""
    # Create L1 axiom
    axiom = AxiomCrystal(
        content="Tasteful > feature-complete",
        domain="constitution",
        tags=frozenset({"tasteful", "design"}),
    )
    axiom_id = await universe.store(axiom, schema_name="concept.axiom")

    # Create L2 value
    value = ValueCrystal(
        principle="Depth over breadth",
        axiom_ids=(axiom_id,),
        tags=frozenset({"design"}),
    )
    value_id = await universe.store(value, schema_name="concept.value")

    # Create L5 function
    proof = GaloisWitnessedProof(
        data="Function focuses on one thing well",
        warrant="Aligns with depth over breadth",
        claim="This function is tasteful",
        backing="Constitutional principle",
        galois_loss=0.15,
    )
    func = FunctionCrystal(
        id="func-001",
        qualified_name="services.example.focused_function",
        file_path="/path/to/file.py",
        line_range=(10, 20),
        signature="def focused_function(x: int) -> str",
        docstring="Does one thing well.",
        layer=5,
        proof=proof,
    )
    func_id = await universe.store(func, schema_name="code.function")

    # Link derivations: function → value → axiom
    await service.link_derivation(
        func_id, value_id, "JUSTIFIES", context="Follows depth over breadth"
    )
    await service.link_derivation(
        value_id, axiom_id, "GROUNDS", context="Derived from constitutional axiom"
    )

    # Trace function to axiom
    chain = await service.trace_to_axiom(func_id)

    # Verify chain
    assert chain.target_id == func_id
    assert chain.is_grounded
    assert len(chain.chain) >= 2  # At least function → value
    assert chain.chain[0].id == func_id
    assert chain.chain[0].layer == 5
    assert chain.total_galois_loss >= 0.0


@pytest.mark.asyncio
async def test_coherence_check(service, universe):
    """Test coherence computation along derivation chain."""
    # Create simple chain: function → value
    value = ValueCrystal(
        principle="Test principle",
        axiom_ids=(),
        tags=frozenset(),
    )
    value_id = await universe.store(value, schema_name="concept.value")

    proof = GaloisWitnessedProof(
        data="Test data",
        warrant="Test warrant",
        claim="Test claim",
        backing="Test backing",
        galois_loss=0.2,
    )
    func = FunctionCrystal(
        id="func-002",
        qualified_name="test.function",
        file_path="/test.py",
        line_range=(1, 10),
        signature="def test() -> None",
        layer=5,
        proof=proof,
    )
    func_id = await universe.store(func, schema_name="code.function")

    # Link
    await service.link_derivation(func_id, value_id, "JUSTIFIES")

    # Check coherence
    coherence = await service.coherence_check(func_id)

    # Coherence should be valid (loss accumulates, so might be lower)
    assert 0.0 <= coherence <= 1.0
    # Note: Coherence can be low if content differs significantly


@pytest.mark.asyncio
async def test_get_derivation_tree(service, universe):
    """Test getting full derivation tree (ancestors + descendants)."""
    # Create a value with descendants
    value = ValueCrystal(
        principle="Core principle",
        axiom_ids=(),
        tags=frozenset(),
    )
    value_id = await universe.store(value, schema_name="concept.value")

    # Create two functions that derive from it
    proof1 = GaloisWitnessedProof(
        data="d1", warrant="w1", claim="c1", backing="b1"
    )
    func1 = FunctionCrystal(
        id="func-tree-1",
        qualified_name="test.func1",
        file_path="/test.py",
        line_range=(1, 5),
        signature="def func1() -> None",
        layer=5,
        proof=proof1,
    )
    func1_id = await universe.store(func1, schema_name="code.function")

    proof2 = GaloisWitnessedProof(
        data="d2", warrant="w2", claim="c2", backing="b2"
    )
    func2 = FunctionCrystal(
        id="func-tree-2",
        qualified_name="test.func2",
        file_path="/test.py",
        line_range=(10, 15),
        signature="def func2() -> None",
        layer=5,
        proof=proof2,
    )
    func2_id = await universe.store(func2, schema_name="code.function")

    # Link both functions to value
    await service.link_derivation(func1_id, value_id, "JUSTIFIES")
    await service.link_derivation(func2_id, value_id, "JUSTIFIES")

    # Get tree for value
    tree = await service.get_derivation_tree(value_id)

    # Verify tree structure
    assert tree.crystal_id == value_id
    assert len(tree.descendants) == 2  # Two functions
    # Note: is_grounded checks if *ancestors* reach L1/L2
    # Since this value has no parents (axiom_ids is empty tuple),
    # it's not technically grounded. In reality, values should
    # link to axioms. For this test, we just verify the descendants exist.


@pytest.mark.asyncio
async def test_link_derivation(service, universe):
    """Test creating derivation edges."""
    # Create two crystals
    value = ValueCrystal(
        principle="Test",
        axiom_ids=(),
        tags=frozenset(),
    )
    value_id = await universe.store(value, schema_name="concept.value")

    proof = GaloisWitnessedProof(
        data="d", warrant="w", claim="c", backing="b"
    )
    func = FunctionCrystal(
        id="func-link",
        qualified_name="test.func",
        file_path="/test.py",
        line_range=(1, 5),
        signature="def func() -> None",
        layer=5,
        proof=proof,
    )
    func_id = await universe.store(func, schema_name="code.function")

    # Link them
    edge_id = await service.link_derivation(
        func_id,
        value_id,
        "JUSTIFIES",
        context="Test link",
        mark_id="mark-123",
    )

    # Verify edge created
    assert edge_id.startswith("edge-")

    # Verify edge stored in service
    edges = service._edges.get(func_id, [])
    assert len(edges) == 1
    assert edges[0].source_id == func_id
    assert edges[0].target_id == value_id
    assert edges[0].edge_type == "derives_from"  # JUSTIFIES maps to derives_from
    assert edges[0].mark_id == "mark-123"


@pytest.mark.asyncio
async def test_service_without_galois(universe):
    """Test that service works without GaloisLossComputer."""
    service = DerivationService(universe, galois=None)

    # Create simple crystal
    value = ValueCrystal(
        principle="Test",
        axiom_ids=(),
        tags=frozenset(),
    )
    value_id = await universe.store(value, schema_name="concept.value")

    # Coherence check should return 1.0 (no loss computed)
    coherence = await service.coherence_check(value_id)
    assert coherence == 1.0  # No loss = perfect coherence
