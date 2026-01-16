"""
Tests for ConstitutionNode AGENTESE node.

Tests the AGENTESE integration for self.constitution.* paths.
"""

from __future__ import annotations

import pytest

from protocols.agentese.node import Observer
from protocols.agentese.registry import get_registry, repopulate_registry, reset_registry
from services.self.node import (
    ConstitutionalGraphRendering,
    ConstitutionNode,
    DerivationChainRendering,
    KBlockInspectionRendering,
    KBlockListRendering,
)
from services.self.reflection_service import (
    ConstitutionalGraph,
    DerivationChain,
    KBlockInspection,
    SelfReflectionService,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer.test()


@pytest.fixture
def guest_observer() -> Observer:
    """Create a guest observer."""
    return Observer.guest()


@pytest.fixture
def service() -> SelfReflectionService:
    """Create a SelfReflectionService."""
    return SelfReflectionService()


@pytest.fixture
def node(service: SelfReflectionService) -> ConstitutionNode:
    """Create a ConstitutionNode with service."""
    return ConstitutionNode(reflection_service=service)


# =============================================================================
# Test: Node Registration
# =============================================================================


class TestNodeRegistration:
    """Tests for @node decorator registration."""

    def test_node_is_registered(self) -> None:
        """ConstitutionNode is registered with the AGENTESE registry."""
        # Ensure the module is imported (triggers @node registration)
        from services.self import node as _  # noqa: F401

        registry = get_registry()
        assert registry.has("self.constitution")

    def test_node_metadata(self) -> None:
        """Node metadata is correct."""
        from services.self import node as _  # noqa: F401

        registry = get_registry()
        meta = registry.get_metadata("self.constitution")
        assert meta is not None
        assert meta.path == "self.constitution"
        assert "reflection_service" in meta.dependencies
        assert meta.constitutional is True

    def test_node_has_contracts(self) -> None:
        """Node declares contracts for type-safe aspects."""
        from services.self import node as _  # noqa: F401

        registry = get_registry()
        meta = registry.get_metadata("self.constitution")
        assert meta is not None
        assert meta.contracts is not None
        assert "view" in meta.contracts
        assert "navigate" in meta.contracts
        assert "axioms" in meta.contracts
        assert "principles" in meta.contracts
        assert "architecture" in meta.contracts
        assert "inspect" in meta.contracts


# =============================================================================
# Test: Handle Property
# =============================================================================


class TestHandleProperty:
    """Tests for the handle property."""

    def test_handle_is_self_constitution(self, node: ConstitutionNode) -> None:
        """Handle is 'self.constitution'."""
        assert node.handle == "self.constitution"


# =============================================================================
# Test: Affordances
# =============================================================================


class TestAffordances:
    """Tests for archetype-specific affordances."""

    def test_guest_has_full_access(self, node: ConstitutionNode, guest_observer: Observer) -> None:
        """Guest observers have full read access to Constitution."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta.from_observer(guest_observer)
        affordances = node.affordances(meta)
        # All observers get full read access - Constitution is transparent
        assert "view" in affordances
        assert "navigate" in affordances
        assert "axioms" in affordances

    def test_developer_has_full_access(self, node: ConstitutionNode, observer: Observer) -> None:
        """Developer observers have full access."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta.from_observer(observer)
        affordances = node.affordances(meta)
        assert "view" in affordances
        assert "navigate" in affordances
        assert "axioms" in affordances
        assert "principles" in affordances
        assert "architecture" in affordances
        assert "inspect" in affordances


# =============================================================================
# Test: manifest()
# =============================================================================


class TestManifest:
    """Tests for the manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """manifest() returns a ConstitutionalGraphRendering."""
        result = await node.manifest(observer)
        assert isinstance(result, ConstitutionalGraphRendering)

    @pytest.mark.asyncio
    async def test_manifest_has_graph(self, node: ConstitutionNode, observer: Observer) -> None:
        """manifest() result has a valid graph."""
        result = await node.manifest(observer)
        assert isinstance(result.graph, ConstitutionalGraph)
        assert result.graph.total_blocks == 22


# =============================================================================
# Test: view()
# =============================================================================


class TestView:
    """Tests for the view aspect."""

    @pytest.mark.asyncio
    async def test_view_returns_graph(self, node: ConstitutionNode, observer: Observer) -> None:
        """view() returns a ConstitutionalGraph."""
        result = await node.view(observer)
        assert isinstance(result, ConstitutionalGraph)
        assert result.total_blocks == 22

    @pytest.mark.asyncio
    async def test_view_with_layer_filter(self, node: ConstitutionNode, observer: Observer) -> None:
        """view(layer=...) accepts layer filter."""
        # Layer filter is passed but implementation may not filter yet
        result = await node.view(observer, layer="axioms")
        assert isinstance(result, ConstitutionalGraph)


# =============================================================================
# Test: navigate()
# =============================================================================


class TestNavigate:
    """Tests for the navigate aspect."""

    @pytest.mark.asyncio
    async def test_navigate_returns_chain(self, node: ConstitutionNode, observer: Observer) -> None:
        """navigate() returns a DerivationChain."""
        result = await node.navigate(observer, kblock_id="COMPOSABLE")
        assert isinstance(result, DerivationChain)
        assert result.source_id == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_navigate_default_is_constitution(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """navigate() without kblock_id defaults to CONSTITUTION."""
        result = await node.navigate(observer)
        assert result.source_id == "CONSTITUTION"

    @pytest.mark.asyncio
    async def test_navigate_unknown_block(self, node: ConstitutionNode, observer: Observer) -> None:
        """navigate() with unknown block returns empty chain."""
        result = await node.navigate(observer, kblock_id="UNKNOWN")
        assert result.source_id == "UNKNOWN"
        assert result.reaches_axiom is False


# =============================================================================
# Test: axioms()
# =============================================================================


class TestAxioms:
    """Tests for the axioms aspect."""

    @pytest.mark.asyncio
    async def test_axioms_returns_list(self, node: ConstitutionNode, observer: Observer) -> None:
        """axioms() returns a list of axiom dicts."""
        result = await node.axioms(observer)
        assert isinstance(result, list)
        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_axioms_are_l0(self, node: ConstitutionNode, observer: Observer) -> None:
        """All returned axioms are L0."""
        result = await node.axioms(observer)
        for axiom in result:
            assert axiom["layer"] == 0

    @pytest.mark.asyncio
    async def test_axioms_include_a1_a2_a3_g(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """Axioms include A1, A2, A3, and G."""
        result = await node.axioms(observer)
        ids = {a["id"] for a in result}
        assert ids == {"A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS"}


# =============================================================================
# Test: principles()
# =============================================================================


class TestPrinciples:
    """Tests for the principles aspect."""

    @pytest.mark.asyncio
    async def test_principles_returns_list(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """principles() returns a list of principle dicts."""
        result = await node.principles(observer)
        assert isinstance(result, list)
        assert len(result) == 8

    @pytest.mark.asyncio
    async def test_principles_include_constitution(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """Principles include CONSTITUTION."""
        result = await node.principles(observer)
        ids = {p["id"] for p in result}
        assert "CONSTITUTION" in ids

    @pytest.mark.asyncio
    async def test_principles_include_seven_principles(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """Principles include the 7 named principles."""
        result = await node.principles(observer)
        ids = {p["id"] for p in result}
        expected = {
            "TASTEFUL",
            "CURATED",
            "ETHICAL",
            "JOY_INDUCING",
            "COMPOSABLE",
            "HETERARCHICAL",
            "GENERATIVE",
        }
        assert expected.issubset(ids)


# =============================================================================
# Test: architecture()
# =============================================================================


class TestArchitecture:
    """Tests for the architecture aspect."""

    @pytest.mark.asyncio
    async def test_architecture_returns_list(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """architecture() returns a list of architecture dicts."""
        result = await node.architecture(observer)
        assert isinstance(result, list)
        assert len(result) >= 3

    @pytest.mark.asyncio
    async def test_architecture_are_l3(self, node: ConstitutionNode, observer: Observer) -> None:
        """All returned architecture blocks are L3."""
        result = await node.architecture(observer)
        for arch in result:
            assert arch["layer"] == 3

    @pytest.mark.asyncio
    async def test_architecture_includes_ashc(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """Architecture includes ASHC."""
        result = await node.architecture(observer)
        ids = {a["id"] for a in result}
        assert "ASHC" in ids


# =============================================================================
# Test: inspect()
# =============================================================================


class TestInspect:
    """Tests for the inspect aspect."""

    @pytest.mark.asyncio
    async def test_inspect_returns_inspection(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """inspect() returns a KBlockInspection."""
        result = await node.inspect(observer, kblock_id="A3_MIRROR")
        assert isinstance(result, KBlockInspection)
        assert result.kblock.id == "A3_MIRROR"

    @pytest.mark.asyncio
    async def test_inspect_default_is_constitution(
        self, node: ConstitutionNode, observer: Observer
    ) -> None:
        """inspect() without kblock_id defaults to CONSTITUTION."""
        result = await node.inspect(observer)
        assert result.kblock.id == "CONSTITUTION"

    @pytest.mark.asyncio
    async def test_inspect_has_content(self, node: ConstitutionNode, observer: Observer) -> None:
        """Inspection includes full content."""
        result = await node.inspect(observer, kblock_id="COMPOSABLE")
        assert len(result.kblock.content) > 100


# =============================================================================
# Test: _invoke_aspect()
# =============================================================================


class TestInvokeAspect:
    """Tests for the _invoke_aspect routing."""

    @pytest.mark.asyncio
    async def test_invoke_view(self, node: ConstitutionNode, observer: Observer) -> None:
        """_invoke_aspect('view') returns dict."""
        result = await node._invoke_aspect("view", observer)
        assert isinstance(result, dict)
        assert result["type"] == "constitutional_graph"

    @pytest.mark.asyncio
    async def test_invoke_navigate(self, node: ConstitutionNode, observer: Observer) -> None:
        """_invoke_aspect('navigate') returns dict."""
        result = await node._invoke_aspect("navigate", observer, kblock_id="ASHC")
        assert isinstance(result, dict)
        assert result["type"] == "derivation_chain"

    @pytest.mark.asyncio
    async def test_invoke_axioms(self, node: ConstitutionNode, observer: Observer) -> None:
        """_invoke_aspect('axioms') returns dict."""
        result = await node._invoke_aspect("axioms", observer)
        assert isinstance(result, dict)
        assert result["type"] == "kblock_list"
        assert result["layer_name"] == "L0 Axioms"

    @pytest.mark.asyncio
    async def test_invoke_unknown_aspect(self, node: ConstitutionNode, observer: Observer) -> None:
        """_invoke_aspect('unknown') returns error dict."""
        result = await node._invoke_aspect("unknown", observer)
        assert isinstance(result, dict)
        assert "error" in result


# =============================================================================
# Test: Renderings
# =============================================================================


class TestRenderings:
    """Tests for rendering classes."""

    @pytest.mark.asyncio
    async def test_constitutional_graph_rendering(self, service: SelfReflectionService) -> None:
        """ConstitutionalGraphRendering serializes correctly."""
        graph = await service.get_constitution()
        rendering = ConstitutionalGraphRendering(graph=graph)
        d = rendering.to_dict()
        assert d["type"] == "constitutional_graph"
        assert "axioms" in d
        text = rendering.to_text()
        assert "Constitutional Graph" in text

    @pytest.mark.asyncio
    async def test_derivation_chain_rendering(self, service: SelfReflectionService) -> None:
        """DerivationChainRendering serializes correctly."""
        chain = await service.get_derivation_chain("COMPOSABLE")
        rendering = DerivationChainRendering(chain=chain)
        d = rendering.to_dict()
        assert d["type"] == "derivation_chain"
        assert "source_id" in d
        text = rendering.to_text()
        assert "Derivation Chain" in text

    @pytest.mark.asyncio
    async def test_kblock_list_rendering(self, service: SelfReflectionService) -> None:
        """KBlockListRendering serializes correctly."""
        axioms = await service.get_axioms()
        kblocks = [
            {"id": a.id, "title": a.title, "layer": a.layer, "galois_loss": a.galois_loss}
            for a in axioms
        ]
        rendering = KBlockListRendering(kblocks=kblocks, layer_name="L0 Axioms")
        d = rendering.to_dict()
        assert d["type"] == "kblock_list"
        assert d["layer_name"] == "L0 Axioms"
        text = rendering.to_text()
        assert "L0 Axioms" in text

    @pytest.mark.asyncio
    async def test_kblock_inspection_rendering(self, service: SelfReflectionService) -> None:
        """KBlockInspectionRendering serializes correctly."""
        inspection = await service.inspect("A3_MIRROR")
        rendering = KBlockInspectionRendering(inspection=inspection)
        d = rendering.to_dict()
        assert d["type"] == "kblock_inspection"
        assert "id" in d
        text = rendering.to_text()
        assert "A3_MIRROR" in text
