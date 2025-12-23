"""
Tests for WitnessedGraph composition and category laws.

These tests verify:
1. Identity Law: Id >> f == f == f >> Id
2. Associativity Law: (a >> b) >> c == a >> (b >> c)
3. ComposedSource behavior
4. HyperEdge types

Philosophy:
    "The proof IS the test. Category laws are not aspirational—they are verified."
"""

from datetime import datetime
from typing import AsyncIterator

import pytest

from ..composition import ComposableMixin, ComposedSource, IdentitySource, compose, identity
from ..protocol import EdgeSourceProtocol, is_edge_source
from ..types import EdgeKind, HyperEdge

# =============================================================================
# Test Fixtures: Mock Edge Sources
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
def edge_a() -> HyperEdge:
    """Sample edge from source A."""
    return HyperEdge(
        kind=EdgeKind.REFERENCES,
        source_path="a.py",
        target_path="b.py",
        origin="source_a",
    )


@pytest.fixture
def edge_b() -> HyperEdge:
    """Sample edge from source B."""
    return HyperEdge(
        kind=EdgeKind.IMPORTS,
        source_path="b.py",
        target_path="c.py",
        origin="source_b",
    )


@pytest.fixture
def edge_c() -> HyperEdge:
    """Sample edge from source C."""
    return HyperEdge(
        kind=EdgeKind.EVIDENCE,
        source_path="c.py",
        target_path="spec/d.md",
        origin="source_c",
    )


@pytest.fixture
def source_a(edge_a: HyperEdge) -> MockSource:
    """Mock source A with one edge."""
    return MockSource("source_a", [edge_a])


@pytest.fixture
def source_b(edge_b: HyperEdge) -> MockSource:
    """Mock source B with one edge."""
    return MockSource("source_b", [edge_b])


@pytest.fixture
def source_c(edge_c: HyperEdge) -> MockSource:
    """Mock source C with one edge."""
    return MockSource("source_c", [edge_c])


# =============================================================================
# HyperEdge Tests
# =============================================================================


class TestHyperEdge:
    """Tests for HyperEdge type."""

    def test_create_edge(self) -> None:
        """Create a basic edge."""
        edge = HyperEdge(
            kind=EdgeKind.REFERENCES,
            source_path="a.py",
            target_path="b.py",
            origin="test",
        )
        assert edge.kind == EdgeKind.REFERENCES
        assert edge.source_path == "a.py"
        assert edge.target_path == "b.py"
        assert edge.origin == "test"

    def test_edge_immutable(self) -> None:
        """Edges are frozen dataclasses."""
        edge = HyperEdge(
            kind=EdgeKind.REFERENCES,
            source_path="a.py",
            target_path="b.py",
            origin="test",
        )
        with pytest.raises(AttributeError):
            edge.source_path = "c.py"  # type: ignore

    def test_edge_hashable(self) -> None:
        """Edges can be used in sets."""
        edge1 = HyperEdge(
            kind=EdgeKind.REFERENCES,
            source_path="a.py",
            target_path="b.py",
            origin="test",
        )
        edge2 = HyperEdge(
            kind=EdgeKind.REFERENCES,
            source_path="a.py",
            target_path="b.py",
            origin="test",
        )
        # Same hash for same values
        assert hash(edge1) == hash(edge2)
        # Can be in a set
        edge_set = {edge1, edge2}
        assert len(edge_set) == 1  # Deduplicated

    def test_edge_validation(self) -> None:
        """Edge validates inputs."""
        # Empty source path
        with pytest.raises(ValueError):
            HyperEdge(
                kind=EdgeKind.REFERENCES,
                source_path="",
                target_path="b.py",
                origin="test",
            )
        # Invalid confidence
        with pytest.raises(ValueError):
            HyperEdge(
                kind=EdgeKind.REFERENCES,
                source_path="a.py",
                target_path="b.py",
                origin="test",
                confidence=1.5,
            )

    def test_edge_to_dict(self) -> None:
        """Edge serializes to dict."""
        now = datetime.now()
        edge = HyperEdge(
            kind=EdgeKind.EVIDENCE,
            source_path="a.py",
            target_path="spec/b.md",
            origin="witness",
            context="test context",
            timestamp=now,
            mark_id="mark-123",
        )
        d = edge.to_dict()
        assert d["kind"] == "EVIDENCE"
        assert d["source_path"] == "a.py"
        assert d["mark_id"] == "mark-123"

    def test_edge_from_dict(self) -> None:
        """Edge deserializes from dict."""
        d = {
            "kind": "EVIDENCE",
            "source_path": "a.py",
            "target_path": "spec/b.md",
            "origin": "witness",
            "confidence": 0.8,
        }
        edge = HyperEdge.from_dict(d)
        assert edge.kind == EdgeKind.EVIDENCE
        assert edge.confidence == 0.8


# =============================================================================
# EdgeKind Tests
# =============================================================================


class TestEdgeKind:
    """Tests for EdgeKind enum."""

    def test_from_witness_tag(self) -> None:
        """Map witness tags to edge kinds."""
        assert EdgeKind.from_witness_tag("gotcha") == EdgeKind.GOTCHA
        assert EdgeKind.from_witness_tag("EUREKA") == EdgeKind.EUREKA
        assert EdgeKind.from_witness_tag("unknown") is None

    def test_from_sovereign_type(self) -> None:
        """Map sovereign edge types to edge kinds."""
        assert EdgeKind.from_sovereign_type("imports") == EdgeKind.IMPORTS
        assert EdgeKind.from_sovereign_type("CALLS") == EdgeKind.CALLS
        # Unknown defaults to REFERENCES
        assert EdgeKind.from_sovereign_type("unknown") == EdgeKind.REFERENCES


# =============================================================================
# IdentitySource Tests
# =============================================================================


class TestIdentitySource:
    """Tests for IdentitySource (category identity element)."""

    @pytest.mark.asyncio
    async def test_identity_returns_empty(self) -> None:
        """Identity source returns no edges."""
        id_source = IdentitySource()
        edges = [e async for e in id_source.edges_from("any.py")]
        assert edges == []

    @pytest.mark.asyncio
    async def test_identity_all_edges_empty(self) -> None:
        """Identity all_edges is empty."""
        id_source = IdentitySource()
        edges = [e async for e in id_source.all_edges()]
        assert edges == []

    def test_identity_origin(self) -> None:
        """Identity has 'identity' origin."""
        id_source = IdentitySource()
        assert id_source.origin == "identity"


# =============================================================================
# Category Law Tests
# =============================================================================


class TestCategoryLaws:
    """
    Tests verifying category laws for edge source composition.

    These are the mathematical guarantees that make composition reliable.
    """

    @pytest.mark.asyncio
    async def test_left_identity(self, source_a: MockSource, edge_a: HyperEdge) -> None:
        """
        Left Identity Law: Id >> f == f

        Composing identity on the left produces same results.
        """
        id_source = identity()

        # Id >> source_a
        composed = id_source >> source_a

        # Should produce same edges as source_a alone
        edges_composed = [e async for e in composed.edges_from("a.py")]
        edges_original = [e async for e in source_a.edges_from("a.py")]

        assert len(edges_composed) == len(edges_original)
        assert edges_composed[0].kind == edges_original[0].kind
        assert edges_composed[0].source_path == edges_original[0].source_path

    @pytest.mark.asyncio
    async def test_right_identity(self, source_a: MockSource, edge_a: HyperEdge) -> None:
        """
        Right Identity Law: f >> Id == f

        Composing identity on the right produces same results.
        """
        id_source = identity()

        # source_a >> Id
        composed = source_a >> id_source

        # Should produce same edges as source_a alone
        edges_composed = [e async for e in composed.edges_from("a.py")]
        edges_original = [e async for e in source_a.edges_from("a.py")]

        assert len(edges_composed) == len(edges_original)
        assert edges_composed[0].kind == edges_original[0].kind

    @pytest.mark.asyncio
    async def test_associativity(
        self,
        source_a: MockSource,
        source_b: MockSource,
        source_c: MockSource,
    ) -> None:
        """
        Associativity Law: (a >> b) >> c == a >> (b >> c)

        Grouping doesn't matter—same edges either way.
        """
        # (a >> b) >> c
        left_composed = (source_a >> source_b) >> source_c

        # a >> (b >> c)
        right_composed = source_a >> (source_b >> source_c)

        # Both should have same edges
        left_edges = [e async for e in left_composed.all_edges()]
        right_edges = [e async for e in right_composed.all_edges()]

        assert len(left_edges) == len(right_edges) == 3

        # Same origins in same order
        left_origins = [e.origin for e in left_edges]
        right_origins = [e.origin for e in right_edges]
        assert left_origins == right_origins == ["source_a", "source_b", "source_c"]

    @pytest.mark.asyncio
    async def test_identity_composition_both_sides(self, source_a: MockSource) -> None:
        """
        Full identity test: Id >> f >> Id == f
        """
        id_source = identity()

        # Id >> source_a >> Id
        composed = id_source >> source_a >> id_source

        edges_composed = [e async for e in composed.all_edges()]
        edges_original = [e async for e in source_a.all_edges()]

        assert len(edges_composed) == len(edges_original)


# =============================================================================
# ComposedSource Tests
# =============================================================================


class TestComposedSource:
    """Tests for ComposedSource behavior."""

    @pytest.mark.asyncio
    async def test_compose_two_sources(self, source_a: MockSource, source_b: MockSource) -> None:
        """Compose two sources."""
        composed = source_a >> source_b
        assert isinstance(composed, ComposedSource)
        assert len(composed) == 2
        assert composed.origin == "source_a+source_b"

    @pytest.mark.asyncio
    async def test_compose_three_sources(
        self,
        source_a: MockSource,
        source_b: MockSource,
        source_c: MockSource,
    ) -> None:
        """Compose three sources."""
        composed = source_a >> source_b >> source_c
        assert len(composed) == 3

    @pytest.mark.asyncio
    async def test_edges_in_order(
        self,
        source_a: MockSource,
        source_b: MockSource,
        source_c: MockSource,
    ) -> None:
        """Edges come in source order."""
        composed = source_a >> source_b >> source_c
        edges = [e async for e in composed.all_edges()]

        # Should be in order: a, b, c
        assert edges[0].origin == "source_a"
        assert edges[1].origin == "source_b"
        assert edges[2].origin == "source_c"

    @pytest.mark.asyncio
    async def test_compose_function(self, source_a: MockSource, source_b: MockSource) -> None:
        """Functional compose() works like >>."""
        composed = compose(source_a, source_b)
        assert composed.origin == "source_a+source_b"

    @pytest.mark.asyncio
    async def test_edges_from_queries_all(
        self, source_a: MockSource, source_b: MockSource, edge_a: HyperEdge
    ) -> None:
        """edges_from queries all sources."""
        composed = source_a >> source_b
        edges = [e async for e in composed.edges_from("a.py")]
        # Only source_a has edge from a.py
        assert len(edges) == 1
        assert edges[0] == edge_a

    @pytest.mark.asyncio
    async def test_search_queries_all(self, source_a: MockSource, source_b: MockSource) -> None:
        """search queries all sources."""
        composed = source_a >> source_b
        edges = [e async for e in composed.search("b.py")]
        # Both sources have edges touching b.py
        assert len(edges) == 2


# =============================================================================
# Protocol Tests
# =============================================================================


class TestProtocol:
    """Tests for EdgeSourceProtocol."""

    def test_mock_source_is_protocol(self, source_a: MockSource) -> None:
        """MockSource implements protocol."""
        assert is_edge_source(source_a)

    def test_composed_source_is_protocol(self, source_a: MockSource, source_b: MockSource) -> None:
        """ComposedSource implements protocol."""
        composed = source_a >> source_b
        assert is_edge_source(composed)

    def test_identity_is_protocol(self) -> None:
        """IdentitySource implements protocol."""
        id_source = identity()
        assert is_edge_source(id_source)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_empty_source(self) -> None:
        """Empty source works correctly."""
        empty = MockSource("empty", [])
        edges = [e async for e in empty.all_edges()]
        assert edges == []

    @pytest.mark.asyncio
    async def test_compose_empty_sources(self) -> None:
        """Composing empty sources works."""
        empty1 = MockSource("empty1", [])
        empty2 = MockSource("empty2", [])
        composed = empty1 >> empty2
        edges = [e async for e in composed.all_edges()]
        assert edges == []

    @pytest.mark.asyncio
    async def test_compose_with_empty(self, source_a: MockSource) -> None:
        """Composing with empty source preserves edges."""
        empty = MockSource("empty", [])
        composed = source_a >> empty
        edges = [e async for e in composed.all_edges()]
        assert len(edges) == 1

    @pytest.mark.asyncio
    async def test_nested_composition_flattens(
        self, source_a: MockSource, source_b: MockSource, source_c: MockSource
    ) -> None:
        """Nested ComposedSource is flattened."""
        # ((a >> b) >> c) should flatten to [a, b, c]
        nested = (source_a >> source_b) >> source_c
        assert len(nested) == 3
        assert nested._sources[0].origin == "source_a"
