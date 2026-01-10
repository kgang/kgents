"""
Tests for ASHC Self-Awareness (Workstream D).

Tests the ASHCSelfAwareness class which enables ASHC to query its own
derivation structure and verify consistency.

Test coverage:
- am_i_grounded(): Check groundedness in Constitution
- what_principle_justifies(): Find principles justifying components
- verify_self_consistency(): Check categorical laws and constraints
- explain_derivation(): Trace derivation chains

Philosophy:
    "The test IS the proof that the proof system works."
"""

from __future__ import annotations

import pytest

from protocols.ashc.paths import DerivationPath, PathKind
from protocols.ashc.paths.types import DerivationWitness, WitnessType
from protocols.ashc.self_awareness import (
    ASHC_COMPONENTS,
    CONSTITUTIONAL_PRINCIPLES,
    ASHCSelfAwareness,
    ConsistencyResult,
    GroundednessResult,
    InMemoryDerivationStore,
    create_self_awareness,
)
from services.k_block.core.derivation import DerivationDAG

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> InMemoryDerivationStore:
    """Create empty in-memory store."""
    return InMemoryDerivationStore()


@pytest.fixture
def dag() -> DerivationDAG:
    """Create empty derivation DAG."""
    return DerivationDAG()


@pytest.fixture
def self_awareness(store: InMemoryDerivationStore, dag: DerivationDAG) -> ASHCSelfAwareness:
    """Create ASHCSelfAwareness with empty store."""
    return ASHCSelfAwareness(store=store, dag=dag)


@pytest.fixture
def grounded_store() -> InMemoryDerivationStore:
    """Create store with paths from principles to components."""
    store = InMemoryDerivationStore()

    # Create paths from principles to components
    for i, component in enumerate(ASHC_COMPONENTS[:3]):  # Just first 3 for speed
        principle = CONSTITUTIONAL_PRINCIPLES[i % len(CONSTITUTIONAL_PRINCIPLES)]

        witness = DerivationWitness.from_principle(principle, f"Grounding from {principle}")

        path = DerivationPath.derive(
            source_id=principle,
            target_id=component,
            witnesses=[witness],
            galois_loss=0.1 + (i * 0.05),  # Varying loss
            principle_scores={principle: 0.9},
        )
        store.add_path(path)

    return store


@pytest.fixture
def grounded_self_awareness(
    grounded_store: InMemoryDerivationStore, dag: DerivationDAG
) -> ASHCSelfAwareness:
    """Create ASHCSelfAwareness with grounded store."""
    return ASHCSelfAwareness(
        store=grounded_store,
        dag=dag,
        components=ASHC_COMPONENTS[:3],  # Match store
    )


# =============================================================================
# Basic Tests
# =============================================================================


class TestASHCSelfAwarenessBasics:
    """Basic tests for ASHCSelfAwareness."""

    def test_create_self_awareness(self) -> None:
        """Test factory function creates valid instance."""
        self_aware = create_self_awareness()
        assert self_aware is not None
        assert self_aware.store is not None
        assert self_aware.dag is not None

    def test_constants_defined(self) -> None:
        """Test that constants are properly defined."""
        assert len(CONSTITUTIONAL_PRINCIPLES) == 7
        assert "COMPOSABLE" in CONSTITUTIONAL_PRINCIPLES
        assert "ETHICAL" in CONSTITUTIONAL_PRINCIPLES
        assert "GENERATIVE" in CONSTITUTIONAL_PRINCIPLES

        assert len(ASHC_COMPONENTS) > 0
        assert "evidence.py" in ASHC_COMPONENTS
        assert "adaptive.py" in ASHC_COMPONENTS


class TestInMemoryDerivationStore:
    """Tests for InMemoryDerivationStore."""

    @pytest.mark.asyncio
    async def test_save_and_query_path(self, store: InMemoryDerivationStore) -> None:
        """Test saving and querying paths."""
        path = DerivationPath.derive(
            source_id="A",
            target_id="B",
            galois_loss=0.1,
        )

        # Save
        path_id = await store.save_path(path)
        assert path_id == path.path_id

        # Query by source
        paths_from_a = await store.query_paths_by_source("A")
        assert len(paths_from_a) == 1
        assert paths_from_a[0].target_id == "B"

        # Query by target
        paths_to_b = await store.query_paths_by_target("B")
        assert len(paths_to_b) == 1
        assert paths_to_b[0].source_id == "A"

    @pytest.mark.asyncio
    async def test_query_all_paths(self, store: InMemoryDerivationStore) -> None:
        """Test querying all paths."""
        # Add multiple paths
        for i in range(5):
            path = DerivationPath.derive(
                source_id=f"source_{i}",
                target_id=f"target_{i}",
                galois_loss=0.1 * i,
            )
            await store.save_path(path)

        all_paths = await store.query_all_paths()
        assert len(all_paths) == 5

        # Test limit
        limited = await store.query_all_paths(limit=3)
        assert len(limited) == 3


# =============================================================================
# Groundedness Tests
# =============================================================================


class TestGroundedness:
    """Tests for am_i_grounded()."""

    @pytest.mark.asyncio
    async def test_empty_store_not_grounded(self, self_awareness: ASHCSelfAwareness) -> None:
        """Empty store means no groundedness."""
        result = await self_awareness.am_i_grounded()

        assert isinstance(result, GroundednessResult)
        assert not result.is_grounded
        assert len(result.ungrounded_components) > 0
        assert result.grounding_ratio == 0.0

    @pytest.mark.asyncio
    async def test_grounded_store_is_grounded(
        self, grounded_self_awareness: ASHCSelfAwareness
    ) -> None:
        """Store with paths from principles is grounded."""
        result = await grounded_self_awareness.am_i_grounded()

        assert isinstance(result, GroundednessResult)
        assert result.is_grounded
        assert len(result.ungrounded_components) == 0
        assert result.grounding_ratio == 1.0
        assert result.overall_confidence > 0.5

    @pytest.mark.asyncio
    async def test_partial_groundedness(self, store: InMemoryDerivationStore) -> None:
        """Test partially grounded state."""
        # Add path for only one component
        path = DerivationPath.derive(
            source_id="COMPOSABLE",
            target_id="evidence.py",
            witnesses=[DerivationWitness.from_principle("COMPOSABLE", "test")],
            galois_loss=0.1,
        )
        store.add_path(path)

        self_aware = ASHCSelfAwareness(
            store=store,
            components=["evidence.py", "adaptive.py"],  # Two components
        )

        result = await self_aware.am_i_grounded()

        assert not result.is_grounded
        assert "evidence.py" in result.paths_to_principles
        assert "adaptive.py" in result.ungrounded_components
        assert result.grounding_ratio == 0.5


# =============================================================================
# Justification Tests
# =============================================================================


class TestJustification:
    """Tests for what_principle_justifies()."""

    @pytest.mark.asyncio
    async def test_no_justification_for_unknown_component(
        self, self_awareness: ASHCSelfAwareness
    ) -> None:
        """Unknown component has no justification."""
        result = await self_awareness.what_principle_justifies("unknown.py")
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_finds_justification_for_grounded_component(
        self, grounded_store: InMemoryDerivationStore
    ) -> None:
        """Grounded component has justification."""
        self_aware = ASHCSelfAwareness(
            store=grounded_store,
            components=ASHC_COMPONENTS[:3],
        )

        # First component should be justified by first principle
        result = await self_aware.what_principle_justifies("evidence.py")

        assert len(result) >= 1
        principle, path = result[0]
        assert principle in CONSTITUTIONAL_PRINCIPLES
        assert path.target_id == "evidence.py"


# =============================================================================
# Consistency Tests
# =============================================================================


class TestConsistency:
    """Tests for verify_self_consistency()."""

    @pytest.mark.asyncio
    async def test_empty_store_is_consistent(self, self_awareness: ASHCSelfAwareness) -> None:
        """Empty store is trivially consistent."""
        result = await self_awareness.verify_self_consistency()

        assert isinstance(result, ConsistencyResult)
        assert result.is_consistent
        assert result.violation_count == 0

    @pytest.mark.asyncio
    async def test_valid_paths_are_consistent(
        self, grounded_self_awareness: ASHCSelfAwareness
    ) -> None:
        """Valid paths should pass consistency check."""
        result = await grounded_self_awareness.verify_self_consistency()

        assert result.is_consistent
        assert len(result.law_violations) == 0

    @pytest.mark.asyncio
    async def test_high_loss_path_violates_galois(self, store: InMemoryDerivationStore) -> None:
        """Path with loss > threshold causes Galois violation."""
        # Add path with high loss
        path = DerivationPath.derive(
            source_id="A",
            target_id="B",
            galois_loss=0.8,  # Above CONSISTENCY_LOSS_THRESHOLD (0.65)
        )
        store.add_path(path)

        self_aware = ASHCSelfAwareness(store=store)
        result = await self_aware.verify_self_consistency()

        assert not result.is_consistent
        assert len(result.galois_violations) >= 1

    @pytest.mark.asyncio
    async def test_low_ethical_score_violates_principles(
        self, store: InMemoryDerivationStore
    ) -> None:
        """Path with ETHICAL < 0.6 causes principle violation."""
        # Add path with low ETHICAL score
        path = DerivationPath.derive(
            source_id="A",
            target_id="B",
            galois_loss=0.1,
            principle_scores={"ETHICAL": 0.3},  # Below 0.6 floor
        )
        store.add_path(path)

        self_aware = ASHCSelfAwareness(store=store)
        result = await self_aware.verify_self_consistency()

        assert not result.is_consistent
        assert len(result.principle_violations) >= 1


# =============================================================================
# Derivation Explanation Tests
# =============================================================================


class TestExplainDerivation:
    """Tests for explain_derivation()."""

    @pytest.mark.asyncio
    async def test_no_path_between_unconnected(self, self_awareness: ASHCSelfAwareness) -> None:
        """No path between unconnected artifacts."""
        result = await self_awareness.explain_derivation("A", "B")
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_finds_direct_path(self, store: InMemoryDerivationStore) -> None:
        """Finds direct path between connected artifacts."""
        # Add direct path
        path = DerivationPath.derive(
            source_id="COMPOSABLE",
            target_id="evidence.py",
            galois_loss=0.1,
        )
        store.add_path(path)

        self_aware = ASHCSelfAwareness(store=store)
        result = await self_aware.explain_derivation("COMPOSABLE", "evidence.py")

        assert len(result) == 1
        assert result[0].source_id == "COMPOSABLE"
        assert result[0].target_id == "evidence.py"

    @pytest.mark.asyncio
    async def test_finds_composed_path(self, store: InMemoryDerivationStore) -> None:
        """Finds composed path through intermediate."""
        # Add path A -> B
        path1 = DerivationPath.derive(
            source_id="A",
            target_id="B",
            galois_loss=0.1,
        )
        store.add_path(path1)

        # Add path B -> C
        path2 = DerivationPath.derive(
            source_id="B",
            target_id="C",
            galois_loss=0.1,
        )
        store.add_path(path2)

        self_aware = ASHCSelfAwareness(store=store)
        result = await self_aware.explain_derivation("A", "C")

        assert len(result) >= 1
        # Composed path should go from A to C
        assert result[0].source_id == "A"
        assert result[0].target_id == "C"
        # Composed path should have accumulated loss
        assert result[0].galois_loss > 0.1  # Due to composition


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full self-awareness workflow."""

    @pytest.mark.asyncio
    async def test_full_self_awareness_workflow(self) -> None:
        """Test full workflow: build paths, check groundedness, verify consistency."""
        store = InMemoryDerivationStore()
        dag = DerivationDAG()

        # Build a minimal derivation graph
        components = ["comp_a", "comp_b", "comp_c"]
        principles = ["COMPOSABLE", "GENERATIVE", "ETHICAL"]

        for comp, principle in zip(components, principles):
            witness = DerivationWitness.from_principle(principle, f"From {principle}")
            path = DerivationPath.derive(
                source_id=principle,
                target_id=comp,
                witnesses=[witness],
                galois_loss=0.1,
                principle_scores={principle: 0.9, "ETHICAL": 0.8},
            )
            store.add_path(path)

            # Also add to DAG
            dag.add_node(principle, layer=1, kind="axiom")
            dag.add_node(comp, layer=2, kind="derived", parent_ids=[principle])

        self_aware = ASHCSelfAwareness(
            store=store,
            dag=dag,
            components=components,
            principles=principles,
        )

        # Check groundedness
        grounded = await self_aware.am_i_grounded()
        assert grounded.is_grounded
        assert grounded.overall_confidence > 0.5

        # Check consistency
        consistent = await self_aware.verify_self_consistency()
        assert consistent.is_consistent

        # Check justification
        for comp in components:
            justifications = await self_aware.what_principle_justifies(comp)
            assert len(justifications) >= 1

        # Check derivation explanation
        paths = await self_aware.explain_derivation("COMPOSABLE", "comp_a")
        assert len(paths) >= 1


# =============================================================================
# Property-Based Tests (Optional - requires hypothesis)
# =============================================================================


try:
    from hypothesis import given, strategies as st

    class TestPropertyBased:
        """Property-based tests using Hypothesis."""

        @given(st.floats(min_value=0.0, max_value=1.0))
        def test_coherence_is_complement_of_loss(self, loss: float) -> None:
            """coherence = 1 - loss."""
            path = DerivationPath.derive(
                source_id="A",
                target_id="B",
                galois_loss=loss,
            )
            assert abs(path.coherence - (1.0 - loss)) < 1e-10

        @given(
            st.floats(min_value=0.0, max_value=0.4),
            st.floats(min_value=0.0, max_value=0.4),
        )
        def test_composition_loss_accumulates(self, loss1: float, loss2: float) -> None:
            """Composed path has accumulated loss."""
            path1 = DerivationPath.derive("A", "B", galois_loss=loss1)
            path2 = DerivationPath.derive("B", "C", galois_loss=loss2)
            composed = path1.compose(path2)

            # Loss formula: L(p;q) = 1 - (1-L(p))*(1-L(q))
            expected_loss = 1.0 - (1.0 - loss1) * (1.0 - loss2)
            assert abs(composed.galois_loss - expected_loss) < 1e-10

except ImportError:
    pass  # Hypothesis not installed


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TestASHCSelfAwarenessBasics",
    "TestInMemoryDerivationStore",
    "TestGroundedness",
    "TestJustification",
    "TestConsistency",
    "TestExplainDerivation",
    "TestIntegration",
]
