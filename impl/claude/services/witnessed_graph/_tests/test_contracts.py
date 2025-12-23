"""
Tests for WitnessedGraph AGENTESE Contracts.

These tests verify the core contracts behave correctly:
- Immutability (frozen dataclasses)
- Proper field types
- Contract validation (is_dataclass check passes)

These contracts enable BE/FE synchronization via AGENTESE discovery.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict, is_dataclass

import pytest

from ..contracts import (
    EdgeResponse,
    EvidenceRequest,
    EvidenceResponse,
    GraphManifestResponse,
    NeighborsRequest,
    NeighborsResponse,
    SearchRequest,
    SearchResponse,
    TracePathResponse,
    TraceRequest,
    TraceResponse,
)

# =============================================================================
# EdgeResponse Tests
# =============================================================================


class TestEdgeResponse:
    """Tests for EdgeResponse contract."""

    def test_is_dataclass(self) -> None:
        """EdgeResponse passes is_dataclass check for contract validation."""
        assert is_dataclass(EdgeResponse)

    def test_creation_with_required_fields(self) -> None:
        """EdgeResponse can be created with required fields."""
        edge = EdgeResponse(
            kind="IMPORTS",
            source_path="impl/foo.py",
            target_path="impl/bar.py",
            origin="sovereign",
        )

        assert edge.kind == "IMPORTS"
        assert edge.source_path == "impl/foo.py"
        assert edge.target_path == "impl/bar.py"
        assert edge.origin == "sovereign"
        assert edge.confidence == 1.0  # default
        assert edge.context is None
        assert edge.line_number is None
        assert edge.mark_id is None

    def test_creation_with_optional_fields(self) -> None:
        """EdgeResponse can include optional fields."""
        edge = EdgeResponse(
            kind="EVIDENCE",
            source_path="impl/foo.py",
            target_path="spec/foo.md",
            origin="witness",
            confidence=0.85,
            context="def foo(): ...",
            line_number=42,
            mark_id="mark-123",
        )

        assert edge.confidence == 0.85
        assert edge.context == "def foo(): ..."
        assert edge.line_number == 42
        assert edge.mark_id == "mark-123"

    def test_immutability(self) -> None:
        """EdgeResponse cannot be mutated after creation."""
        edge = EdgeResponse(
            kind="IMPORTS",
            source_path="a.py",
            target_path="b.py",
            origin="sovereign",
        )

        with pytest.raises(FrozenInstanceError):
            edge.kind = "CHANGED"  # type: ignore[misc]

    def test_asdict(self) -> None:
        """asdict() produces correct dictionary."""
        edge = EdgeResponse(
            kind="IMPORTS",
            source_path="a.py",
            target_path="b.py",
            origin="sovereign",
            confidence=0.9,
        )

        data = asdict(edge)
        assert data["kind"] == "IMPORTS"
        assert data["source_path"] == "a.py"
        assert data["confidence"] == 0.9


# =============================================================================
# GraphManifestResponse Tests
# =============================================================================


class TestGraphManifestResponse:
    """Tests for GraphManifestResponse contract."""

    def test_is_dataclass(self) -> None:
        """GraphManifestResponse passes is_dataclass check."""
        assert is_dataclass(GraphManifestResponse)

    def test_creation(self) -> None:
        """GraphManifestResponse stores graph statistics."""
        manifest = GraphManifestResponse(
            total_edges=150,
            sources=3,
            origin="sovereign+witness+spec_ledger",
            by_origin={"sovereign": 100, "witness": 30, "spec_ledger": 20},
            by_kind={"IMPORTS": 80, "EVIDENCE": 50, "USES": 20},
        )

        assert manifest.total_edges == 150
        assert manifest.sources == 3
        assert manifest.by_origin["sovereign"] == 100

    def test_immutability(self) -> None:
        """GraphManifestResponse cannot be mutated."""
        manifest = GraphManifestResponse(
            total_edges=10,
            sources=1,
            origin="test",
            by_origin={},
            by_kind={},
        )

        with pytest.raises(FrozenInstanceError):
            manifest.total_edges = 999  # type: ignore[misc]


# =============================================================================
# NeighborsRequest/Response Tests
# =============================================================================


class TestNeighborsContract:
    """Tests for Neighbors request/response contracts."""

    def test_request_is_dataclass(self) -> None:
        """NeighborsRequest passes is_dataclass check."""
        assert is_dataclass(NeighborsRequest)

    def test_response_is_dataclass(self) -> None:
        """NeighborsResponse passes is_dataclass check."""
        assert is_dataclass(NeighborsResponse)

    def test_request_creation(self) -> None:
        """NeighborsRequest stores path."""
        req = NeighborsRequest(path="spec/agents/d-gent.md")
        assert req.path == "spec/agents/d-gent.md"

    def test_response_creation(self) -> None:
        """NeighborsResponse stores edges."""
        edge = EdgeResponse(
            kind="IMPORTS",
            source_path="a.py",
            target_path="b.py",
            origin="sovereign",
        )

        resp = NeighborsResponse(
            path="a.py",
            incoming=[],
            outgoing=[edge],
            total=1,
        )

        assert resp.path == "a.py"
        assert len(resp.outgoing) == 1
        assert resp.total == 1


# =============================================================================
# EvidenceRequest/Response Tests
# =============================================================================


class TestEvidenceContract:
    """Tests for Evidence request/response contracts."""

    def test_request_is_dataclass(self) -> None:
        """EvidenceRequest passes is_dataclass check."""
        assert is_dataclass(EvidenceRequest)

    def test_response_is_dataclass(self) -> None:
        """EvidenceResponse passes is_dataclass check."""
        assert is_dataclass(EvidenceResponse)

    def test_response_creation(self) -> None:
        """EvidenceResponse stores evidence edges."""
        resp = EvidenceResponse(
            spec_path="spec/agents/d-gent.md",
            evidence=[],
            count=0,
            by_kind={},
        )

        assert resp.spec_path == "spec/agents/d-gent.md"
        assert resp.count == 0


# =============================================================================
# TraceRequest/Response Tests
# =============================================================================


class TestTraceContract:
    """Tests for Trace request/response contracts."""

    def test_request_is_dataclass(self) -> None:
        """TraceRequest passes is_dataclass check."""
        assert is_dataclass(TraceRequest)

    def test_response_is_dataclass(self) -> None:
        """TraceResponse passes is_dataclass check."""
        assert is_dataclass(TraceResponse)

    def test_path_response_is_dataclass(self) -> None:
        """TracePathResponse passes is_dataclass check."""
        assert is_dataclass(TracePathResponse)

    def test_request_defaults(self) -> None:
        """TraceRequest has sensible defaults."""
        req = TraceRequest(start="a.py", end="b.py")
        assert req.max_depth == 5

    def test_response_creation(self) -> None:
        """TraceResponse stores found paths."""
        resp = TraceResponse(
            start="impl/foo.py",
            end="spec/foo.md",
            paths=[],
            found=False,
        )

        assert not resp.found
        assert resp.start == "impl/foo.py"


# =============================================================================
# SearchRequest/Response Tests
# =============================================================================


class TestSearchContract:
    """Tests for Search request/response contracts."""

    def test_request_is_dataclass(self) -> None:
        """SearchRequest passes is_dataclass check."""
        assert is_dataclass(SearchRequest)

    def test_response_is_dataclass(self) -> None:
        """SearchResponse passes is_dataclass check."""
        assert is_dataclass(SearchResponse)

    def test_request_defaults(self) -> None:
        """SearchRequest has sensible defaults."""
        req = SearchRequest(query="witness")
        assert req.limit == 100

    def test_response_creation(self) -> None:
        """SearchResponse stores matching edges."""
        edge = EdgeResponse(
            kind="EVIDENCE",
            source_path="impl/witness.py",
            target_path="spec/witness.md",
            origin="witness",
        )

        resp = SearchResponse(
            query="witness",
            edges=[edge],
            count=1,
        )

        assert resp.query == "witness"
        assert resp.count == 1
        assert len(resp.edges) == 1


# =============================================================================
# Contract Registration Tests
# =============================================================================


class TestContractRegistration:
    """Tests that contracts work with AGENTESE contract system."""

    def test_all_contracts_are_dataclasses(self) -> None:
        """All contract types pass is_dataclass check."""
        contracts = [
            EdgeResponse,
            GraphManifestResponse,
            NeighborsRequest,
            NeighborsResponse,
            EvidenceRequest,
            EvidenceResponse,
            TraceRequest,
            TracePathResponse,
            TraceResponse,
            SearchRequest,
            SearchResponse,
        ]

        for contract in contracts:
            assert is_dataclass(contract), f"{contract.__name__} is not a dataclass"

    def test_contracts_are_frozen(self) -> None:
        """All contracts are frozen (immutable)."""
        # Create instances of each and verify immutability
        instances = [
            EdgeResponse(kind="X", source_path="a", target_path="b", origin="test"),
            GraphManifestResponse(total_edges=0, sources=0, origin="", by_origin={}, by_kind={}),
            NeighborsRequest(path="test"),
            NeighborsResponse(path="test", incoming=[], outgoing=[], total=0),
            EvidenceRequest(spec_path="test"),
            EvidenceResponse(spec_path="test", evidence=[], count=0, by_kind={}),
            TraceRequest(start="a", end="b"),
            TracePathResponse(edges=[], length=0, nodes=[]),
            TraceResponse(start="a", end="b", paths=[], found=False),
            SearchRequest(query="test"),
            SearchResponse(query="test", edges=[], count=0),
        ]

        for instance in instances:
            # Try to modify the first field
            first_field = list(instance.__dataclass_fields__.keys())[0]
            with pytest.raises(FrozenInstanceError):
                setattr(instance, first_field, "CHANGED")
