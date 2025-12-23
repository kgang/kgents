"""
Tests for WitnessedGraphService Crown Jewel.

These tests verify:
1. Service initialization with multiple sources
2. neighbors() returns incoming and outgoing edges
3. evidence_for() filters by evidence kinds
4. trace_path() finds paths through the graph
5. search() and stats() work correctly
"""

from typing import AsyncIterator

import pytest

from ..composition import ComposableMixin
from ..service import (
    EvidenceResult,
    NeighborResult,
    TracePath,
    WitnessedGraphService,
)
from ..types import EdgeKind, HyperEdge

# =============================================================================
# Test Fixtures
# =============================================================================


class MockSource(ComposableMixin):
    """A mock edge source for testing."""

    def __init__(self, name: str, edges: list[HyperEdge] | None = None) -> None:
        self._name = name
        self._edges = edges or []

    @property
    def origin(self) -> str:
        return self._name

    async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
        for edge in self._edges:
            if edge.source_path == path:
                yield edge

    async def edges_to(self, path: str) -> AsyncIterator[HyperEdge]:
        for edge in self._edges:
            if edge.target_path == path:
                yield edge

    async def all_edges(self) -> AsyncIterator[HyperEdge]:
        for edge in self._edges:
            yield edge

    async def search(self, query: str) -> AsyncIterator[HyperEdge]:
        query_lower = query.lower()
        for edge in self._edges:
            if query_lower in edge.source_path.lower() or query_lower in edge.target_path.lower():
                yield edge


@pytest.fixture
def sovereign_edges() -> list[HyperEdge]:
    """Edges from sovereign source (code structure)."""
    return [
        HyperEdge(
            kind=EdgeKind.IMPORTS,
            source_path="impl/service.py",
            target_path="impl/utils.py",
            origin="sovereign",
        ),
        HyperEdge(
            kind=EdgeKind.REFERENCES,
            source_path="impl/service.py",
            target_path="spec/service.md",
            origin="sovereign",
        ),
    ]


@pytest.fixture
def witness_edges() -> list[HyperEdge]:
    """Edges from witness source (marks)."""
    return [
        HyperEdge(
            kind=EdgeKind.EVIDENCE,
            source_path="impl/service.py",
            target_path="spec/service.md",
            origin="witness",
            mark_id="mark-123",
        ),
        HyperEdge(
            kind=EdgeKind.GOTCHA,
            source_path="test/test_service.py",
            target_path="spec/service.md",
            origin="witness",
            mark_id="mark-456",
        ),
    ]


@pytest.fixture
def spec_edges() -> list[HyperEdge]:
    """Edges from spec ledger source."""
    return [
        HyperEdge(
            kind=EdgeKind.EXTENDS,
            source_path="spec/service.md",
            target_path="spec/base.md",
            origin="spec_ledger",
        ),
        HyperEdge(
            kind=EdgeKind.HARMONY,
            source_path="spec/service.md",
            target_path="spec/api.md",
            origin="spec_ledger",
            confidence=0.9,
        ),
    ]


@pytest.fixture
def sovereign_source(sovereign_edges: list[HyperEdge]) -> MockSource:
    return MockSource("sovereign", sovereign_edges)


@pytest.fixture
def witness_source(witness_edges: list[HyperEdge]) -> MockSource:
    return MockSource("witness", witness_edges)


@pytest.fixture
def spec_source(spec_edges: list[HyperEdge]) -> MockSource:
    return MockSource("spec_ledger", spec_edges)


@pytest.fixture
def service(
    sovereign_source: MockSource,
    witness_source: MockSource,
    spec_source: MockSource,
) -> WitnessedGraphService:
    """Create service with all sources."""
    return WitnessedGraphService(sovereign_source, witness_source, spec_source)


# =============================================================================
# Service Initialization Tests
# =============================================================================


class TestServiceInit:
    """Tests for service initialization."""

    def test_init_with_positional_sources(
        self, sovereign_source: MockSource, witness_source: MockSource
    ) -> None:
        """Initialize with positional sources."""
        service = WitnessedGraphService(sovereign_source, witness_source)
        assert len(service.graph.sources) == 2

    def test_init_with_named_sources(
        self,
        sovereign_source: MockSource,
        witness_source: MockSource,
        spec_source: MockSource,
    ) -> None:
        """Initialize with named sources."""
        service = WitnessedGraphService(
            sovereign_source=sovereign_source,
            witness_source=witness_source,
            spec_source=spec_source,
        )
        assert len(service.graph.sources) == 3

    def test_origin_combined(self, service: WitnessedGraphService) -> None:
        """Origin is combined from all sources."""
        assert "sovereign" in service.origin
        assert "witness" in service.origin
        assert "spec_ledger" in service.origin


# =============================================================================
# Neighbors Tests
# =============================================================================


class TestNeighbors:
    """Tests for neighbors() method."""

    @pytest.mark.asyncio
    async def test_neighbors_outgoing(self, service: WitnessedGraphService) -> None:
        """Get outgoing edges."""
        result = await service.neighbors("impl/service.py")
        assert result.path == "impl/service.py"
        assert len(result.outgoing) == 3  # IMPORTS, REFERENCES, EVIDENCE

    @pytest.mark.asyncio
    async def test_neighbors_incoming(self, service: WitnessedGraphService) -> None:
        """Get incoming edges."""
        result = await service.neighbors("spec/service.md")
        # REFERENCES, EVIDENCE, GOTCHA point TO spec/service.md
        # EXTENDS, HARMONY point FROM spec/service.md (outgoing)
        assert len(result.incoming) == 3
        assert len(result.outgoing) == 2

    @pytest.mark.asyncio
    async def test_neighbors_total(self, service: WitnessedGraphService) -> None:
        """Total count is correct."""
        result = await service.neighbors("impl/service.py")
        assert result.total == len(result.incoming) + len(result.outgoing)

    @pytest.mark.asyncio
    async def test_neighbors_by_origin(self, service: WitnessedGraphService) -> None:
        """Group edges by origin."""
        result = await service.neighbors("impl/service.py")
        by_origin = result.by_origin()
        assert "sovereign" in by_origin
        assert "witness" in by_origin

    @pytest.mark.asyncio
    async def test_neighbors_by_kind(self, service: WitnessedGraphService) -> None:
        """Group edges by kind."""
        result = await service.neighbors("impl/service.py")
        by_kind = result.by_kind()
        assert EdgeKind.IMPORTS in by_kind or EdgeKind.EVIDENCE in by_kind

    @pytest.mark.asyncio
    async def test_neighbors_no_edges(self, service: WitnessedGraphService) -> None:
        """Handle path with no edges."""
        result = await service.neighbors("nonexistent.py")
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_neighbors_to_dict(self, service: WitnessedGraphService) -> None:
        """Result serializes to dict."""
        result = await service.neighbors("impl/service.py")
        d = result.to_dict()
        assert "path" in d
        assert "incoming" in d
        assert "outgoing" in d
        assert "total" in d


# =============================================================================
# Evidence Tests
# =============================================================================


class TestEvidence:
    """Tests for evidence_for() method."""

    @pytest.mark.asyncio
    async def test_evidence_for_spec(self, service: WitnessedGraphService) -> None:
        """Get evidence for a spec."""
        result = await service.evidence_for("spec/service.md")
        assert result.spec_path == "spec/service.md"
        # Should include EVIDENCE edges
        evidence_kinds = {e.kind for e in result.evidence}
        assert EdgeKind.EVIDENCE in evidence_kinds

    @pytest.mark.asyncio
    async def test_evidence_count(self, service: WitnessedGraphService) -> None:
        """Evidence count is correct."""
        result = await service.evidence_for("spec/service.md")
        assert result.count == len(result.evidence)

    @pytest.mark.asyncio
    async def test_evidence_by_kind(self, service: WitnessedGraphService) -> None:
        """Evidence grouped by kind."""
        result = await service.evidence_for("spec/service.md")
        by_kind = result.by_kind
        assert isinstance(by_kind, dict)

    @pytest.mark.asyncio
    async def test_evidence_to_dict(self, service: WitnessedGraphService) -> None:
        """Result serializes to dict."""
        result = await service.evidence_for("spec/service.md")
        d = result.to_dict()
        assert "spec_path" in d
        assert "evidence" in d
        assert "count" in d


# =============================================================================
# Trace Path Tests
# =============================================================================


class TestTracePath:
    """Tests for trace_path() method."""

    @pytest.mark.asyncio
    async def test_trace_same_node(self, service: WitnessedGraphService) -> None:
        """Path from node to itself."""
        paths = await service.trace_path("impl/service.py", "impl/service.py")
        assert len(paths) == 1
        assert paths[0].length == 0

    @pytest.mark.asyncio
    async def test_trace_direct_path(self, service: WitnessedGraphService) -> None:
        """Find direct path between nodes."""
        paths = await service.trace_path("impl/service.py", "impl/utils.py")
        # Should find path via IMPORTS edge
        assert len(paths) >= 1
        assert paths[0].length == 1

    @pytest.mark.asyncio
    async def test_trace_no_path(self, service: WitnessedGraphService) -> None:
        """No path exists."""
        paths = await service.trace_path("impl/utils.py", "impl/service.py")
        # No path in this direction
        assert len(paths) == 0

    @pytest.mark.asyncio
    async def test_trace_path_nodes(self, service: WitnessedGraphService) -> None:
        """Path includes all nodes."""
        paths = await service.trace_path("impl/service.py", "impl/utils.py")
        if paths:
            nodes = paths[0].nodes
            assert "impl/service.py" in nodes
            assert "impl/utils.py" in nodes

    @pytest.mark.asyncio
    async def test_trace_path_to_dict(self, service: WitnessedGraphService) -> None:
        """TracePath serializes to dict."""
        paths = await service.trace_path("impl/service.py", "impl/utils.py")
        if paths:
            d = paths[0].to_dict()
            assert "edges" in d
            assert "length" in d
            assert "nodes" in d


# =============================================================================
# Search Tests
# =============================================================================


class TestSearch:
    """Tests for search() method."""

    @pytest.mark.asyncio
    async def test_search_by_path(self, service: WitnessedGraphService) -> None:
        """Search finds edges by path."""
        results = await service.search("service")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_limit(self, service: WitnessedGraphService) -> None:
        """Search respects limit."""
        results = await service.search("spec", limit=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_search_no_results(self, service: WitnessedGraphService) -> None:
        """Search with no matches."""
        results = await service.search("nonexistent_xyz")
        assert len(results) == 0


# =============================================================================
# Stats Tests
# =============================================================================


class TestStats:
    """Tests for stats() method."""

    @pytest.mark.asyncio
    async def test_stats_total(self, service: WitnessedGraphService) -> None:
        """Stats includes total edges."""
        stats = await service.stats()
        assert "total_edges" in stats
        assert stats["total_edges"] == 6  # 2 + 2 + 2

    @pytest.mark.asyncio
    async def test_stats_by_origin(self, service: WitnessedGraphService) -> None:
        """Stats includes breakdown by origin."""
        stats = await service.stats()
        assert "by_origin" in stats
        assert stats["by_origin"]["sovereign"] == 2
        assert stats["by_origin"]["witness"] == 2
        assert stats["by_origin"]["spec_ledger"] == 2

    @pytest.mark.asyncio
    async def test_stats_by_kind(self, service: WitnessedGraphService) -> None:
        """Stats includes breakdown by kind."""
        stats = await service.stats()
        assert "by_kind" in stats
        assert "IMPORTS" in stats["by_kind"]

    @pytest.mark.asyncio
    async def test_stats_sources_count(self, service: WitnessedGraphService) -> None:
        """Stats includes source count."""
        stats = await service.stats()
        assert stats["sources"] == 3
