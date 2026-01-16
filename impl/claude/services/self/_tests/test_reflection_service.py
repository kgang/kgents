"""
Tests for SelfReflectionService.

Tests the core business logic for Constitutional introspection,
including querying, navigation, and derivation chain inspection.
"""

from __future__ import annotations

import pytest

from services.self.reflection_service import (
    ConstitutionalGraph,
    DerivationChain,
    KBlockInspection,
    KBlockSummary,
    SelfReflectionService,
    get_reflection_service,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def service() -> SelfReflectionService:
    """Create a fresh SelfReflectionService for testing."""
    return SelfReflectionService()


# =============================================================================
# Test: Service Initialization
# =============================================================================


class TestServiceInitialization:
    """Tests for SelfReflectionService initialization."""

    def test_factory_function_returns_service(self) -> None:
        """get_reflection_service() returns a SelfReflectionService."""
        service = get_reflection_service()
        assert isinstance(service, SelfReflectionService)

    def test_service_has_factory(self, service: SelfReflectionService) -> None:
        """Service has a GenesisKBlockFactory."""
        assert service._factory is not None

    def test_blocks_cache_initially_none(self, service: SelfReflectionService) -> None:
        """Blocks cache is initially None (lazy loading)."""
        assert service._blocks_cache is None


# =============================================================================
# Test: get_constitution()
# =============================================================================


class TestGetConstitution:
    """Tests for get_constitution() method."""

    @pytest.mark.asyncio
    async def test_returns_constitutional_graph(self, service: SelfReflectionService) -> None:
        """Returns a ConstitutionalGraph with the 22 K-Blocks."""
        graph = await service.get_constitution()
        assert isinstance(graph, ConstitutionalGraph)
        assert graph.total_blocks == 22

    @pytest.mark.asyncio
    async def test_axioms_are_l0(self, service: SelfReflectionService) -> None:
        """Axioms are L0 blocks (A1, A2, A3, G)."""
        graph = await service.get_constitution()
        assert len(graph.axioms) == 4
        for axiom in graph.axioms:
            assert axiom.layer == 0
            assert axiom.id in ("A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS")

    @pytest.mark.asyncio
    async def test_kernel_are_l1(self, service: SelfReflectionService) -> None:
        """Kernel blocks are L1 (COMPOSE, JUDGE, GROUND)."""
        graph = await service.get_constitution()
        assert len(graph.kernel) == 3
        for kernel in graph.kernel:
            assert kernel.layer == 1
            assert kernel.id in ("COMPOSE", "JUDGE", "GROUND")

    @pytest.mark.asyncio
    async def test_derived_are_l2(self, service: SelfReflectionService) -> None:
        """Derived blocks are L2 (ID, CONTRADICT, SUBLATE, FIX)."""
        graph = await service.get_constitution()
        assert len(graph.derived) == 4
        for derived in graph.derived:
            assert derived.layer == 2
            assert derived.id in ("ID", "CONTRADICT", "SUBLATE", "FIX")

    @pytest.mark.asyncio
    async def test_principles_include_constitution(self, service: SelfReflectionService) -> None:
        """Principles include CONSTITUTION and the 7 principles."""
        graph = await service.get_constitution()
        assert len(graph.principles) == 8
        ids = {p.id for p in graph.principles}
        assert "CONSTITUTION" in ids
        assert "TASTEFUL" in ids
        assert "CURATED" in ids
        assert "ETHICAL" in ids
        assert "JOY_INDUCING" in ids
        assert "COMPOSABLE" in ids
        assert "HETERARCHICAL" in ids
        assert "GENERATIVE" in ids

    @pytest.mark.asyncio
    async def test_architecture_are_l3(self, service: SelfReflectionService) -> None:
        """Architecture blocks are L3."""
        graph = await service.get_constitution()
        # Should have 4 architecture blocks
        assert len(graph.architecture) >= 3
        for arch in graph.architecture:
            assert arch.layer == 3

    @pytest.mark.asyncio
    async def test_edges_are_populated(self, service: SelfReflectionService) -> None:
        """Derivation edges are populated."""
        graph = await service.get_constitution()
        assert graph.total_edges > 0
        # Each edge should be (from, to, type)
        for edge in graph.edges:
            assert len(edge) == 3
            assert edge[2] == "derives_from"

    @pytest.mark.asyncio
    async def test_to_dict_serializes_correctly(self, service: SelfReflectionService) -> None:
        """ConstitutionalGraph.to_dict() returns valid dict."""
        graph = await service.get_constitution()
        d = graph.to_dict()
        assert "axioms" in d
        assert "kernel" in d
        assert "derived" in d
        assert "principles" in d
        assert "architecture" in d
        assert "edges" in d
        assert "total_blocks" in d
        assert "total_edges" in d

    @pytest.mark.asyncio
    async def test_to_text_returns_string(self, service: SelfReflectionService) -> None:
        """ConstitutionalGraph.to_text() returns human-readable text."""
        graph = await service.get_constitution()
        text = graph.to_text()
        assert isinstance(text, str)
        assert "Constitutional Graph" in text
        assert "L0 Axioms" in text


# =============================================================================
# Test: get_derivation_chain()
# =============================================================================


class TestGetDerivationChain:
    """Tests for get_derivation_chain() method."""

    @pytest.mark.asyncio
    async def test_returns_derivation_chain(self, service: SelfReflectionService) -> None:
        """Returns a DerivationChain for valid K-Block."""
        chain = await service.get_derivation_chain("COMPOSABLE")
        assert isinstance(chain, DerivationChain)
        assert chain.source_id == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_axiom_has_no_parents(self, service: SelfReflectionService) -> None:
        """Axiom K-Blocks have no derivation parents."""
        chain = await service.get_derivation_chain("A1_ENTITY")
        assert chain.source_id == "A1_ENTITY"
        # Axioms are their own fixed point
        assert chain.reaches_axiom is True
        assert "A1_ENTITY" in chain.axiom_ids

    @pytest.mark.asyncio
    async def test_derived_reaches_axioms(self, service: SelfReflectionService) -> None:
        """Derived K-Blocks trace back to axioms."""
        chain = await service.get_derivation_chain("ASHC")
        assert chain.reaches_axiom is True
        # Should reach some axiom(s)
        assert len(chain.axiom_ids) > 0

    @pytest.mark.asyncio
    async def test_unknown_kblock_returns_empty_chain(self, service: SelfReflectionService) -> None:
        """Unknown K-Block returns empty chain."""
        chain = await service.get_derivation_chain("UNKNOWN_BLOCK")
        assert chain.source_id == "UNKNOWN_BLOCK"
        assert chain.reaches_axiom is False
        assert chain.total_loss == 1.0

    @pytest.mark.asyncio
    async def test_chain_has_steps(self, service: SelfReflectionService) -> None:
        """Derivation chain has steps for non-axiom K-Blocks."""
        chain = await service.get_derivation_chain("COMPOSE")
        assert len(chain.steps) >= 1
        # First step should be the source block
        assert chain.steps[0].kblock_id == "COMPOSE"

    @pytest.mark.asyncio
    async def test_to_dict_serializes_correctly(self, service: SelfReflectionService) -> None:
        """DerivationChain.to_dict() returns valid dict."""
        chain = await service.get_derivation_chain("COMPOSABLE")
        d = chain.to_dict()
        assert "source_id" in d
        assert "source_title" in d
        assert "steps" in d
        assert "total_loss" in d
        assert "reaches_axiom" in d
        assert "axiom_ids" in d


# =============================================================================
# Test: inspect()
# =============================================================================


class TestInspect:
    """Tests for inspect() method."""

    @pytest.mark.asyncio
    async def test_returns_kblock_inspection(self, service: SelfReflectionService) -> None:
        """Returns a KBlockInspection for valid K-Block."""
        inspection = await service.inspect("A3_MIRROR")
        assert isinstance(inspection, KBlockInspection)
        assert inspection.kblock.id == "A3_MIRROR"

    @pytest.mark.asyncio
    async def test_inspection_has_full_content(self, service: SelfReflectionService) -> None:
        """Inspection includes full K-Block content."""
        inspection = await service.inspect("COMPOSABLE")
        assert len(inspection.kblock.content) > 100
        assert "morphisms" in inspection.kblock.content.lower()

    @pytest.mark.asyncio
    async def test_inspection_has_parents(self, service: SelfReflectionService) -> None:
        """Inspection includes parent K-Blocks."""
        inspection = await service.inspect("COMPOSE")
        # COMPOSE derives from A2_MORPHISM
        assert len(inspection.parents) >= 1
        parent_ids = {p.id for p in inspection.parents}
        assert "A2_MORPHISM" in parent_ids

    @pytest.mark.asyncio
    async def test_inspection_has_children(self, service: SelfReflectionService) -> None:
        """Inspection includes child K-Blocks."""
        inspection = await service.inspect("CONSTITUTION")
        # CONSTITUTION should have children (the 7 principles derive from it)
        assert len(inspection.children) >= 1

    @pytest.mark.asyncio
    async def test_inspection_has_derivation_chain(self, service: SelfReflectionService) -> None:
        """Inspection includes derivation chain."""
        inspection = await service.inspect("ASHC")
        assert isinstance(inspection.derivation_chain, DerivationChain)
        assert inspection.derivation_chain.source_id == "ASHC"

    @pytest.mark.asyncio
    async def test_unknown_kblock_returns_inspection_with_error(
        self, service: SelfReflectionService
    ) -> None:
        """Unknown K-Block returns inspection with error marker."""
        inspection = await service.inspect("UNKNOWN_BLOCK")
        assert inspection.kblock.id == "UNKNOWN_BLOCK"
        assert "not found" in inspection.kblock.content

    @pytest.mark.asyncio
    async def test_to_dict_serializes_correctly(self, service: SelfReflectionService) -> None:
        """KBlockInspection.to_dict() returns valid dict."""
        inspection = await service.inspect("A1_ENTITY")
        d = inspection.to_dict()
        assert "id" in d
        assert "title" in d
        assert "layer" in d
        assert "galois_loss" in d
        assert "content" in d
        assert "parents" in d
        assert "children" in d
        assert "derivation_chain" in d


# =============================================================================
# Test: Layer-Specific Methods
# =============================================================================


class TestLayerMethods:
    """Tests for layer-specific getter methods."""

    @pytest.mark.asyncio
    async def test_get_axioms_returns_four(self, service: SelfReflectionService) -> None:
        """get_axioms() returns the 4 L0 axioms."""
        axioms = await service.get_axioms()
        assert len(axioms) == 4
        ids = {a.id for a in axioms}
        assert ids == {"A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS"}

    @pytest.mark.asyncio
    async def test_get_principles_returns_eight(self, service: SelfReflectionService) -> None:
        """get_principles() returns Constitution + 7 principles."""
        principles = await service.get_principles()
        assert len(principles) == 8

    @pytest.mark.asyncio
    async def test_get_architecture_returns_l3(self, service: SelfReflectionService) -> None:
        """get_architecture() returns L3 blocks."""
        architecture = await service.get_architecture()
        assert len(architecture) >= 3
        for arch in architecture:
            assert arch.layer == 3


# =============================================================================
# Test: KBlockSummary
# =============================================================================


class TestKBlockSummary:
    """Tests for KBlockSummary dataclass."""

    @pytest.mark.asyncio
    async def test_from_genesis_creates_summary(self, service: SelfReflectionService) -> None:
        """KBlockSummary.from_genesis() creates valid summary."""
        blocks = service._get_all_blocks()
        entity = blocks["A1_ENTITY"]
        summary = KBlockSummary.from_genesis(entity)
        assert summary.id == "A1_ENTITY"
        assert summary.layer == 0
        assert summary.galois_loss == 0.0

    @pytest.mark.asyncio
    async def test_summary_to_dict(self, service: SelfReflectionService) -> None:
        """KBlockSummary.to_dict() returns valid dict."""
        blocks = service._get_all_blocks()
        entity = blocks["A1_ENTITY"]
        summary = KBlockSummary.from_genesis(entity)
        d = summary.to_dict()
        assert "id" in d
        assert "title" in d
        assert "layer" in d
        assert "galois_loss" in d
        assert "derives_from" in d
        assert "tags" in d
