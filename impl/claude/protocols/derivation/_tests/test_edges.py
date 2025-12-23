"""
Tests for WitnessedEdge: Phase 3 of the Derivation Framework.

Tests cover:
    - WitnessedEdge creation and immutability
    - Edge metadata storage and retrieval
    - Mark/test/proof attachment
    - Principle flow tracking
    - Bootstrap edge categorical evidence
    - Logarithmic strengthening

Teaching:
    gotcha: All types are frozen dataclasses. Tests verify immutability
            by checking that updates return new objects.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from protocols.derivation.edges import (
    DerivationRationale,
    EdgeType,
    PrincipleFlow,
    WitnessedEdge,
)
from protocols.derivation.types import EvidenceType

# =============================================================================
# PrincipleFlow Tests
# =============================================================================


class TestPrincipleFlow:
    """Tests for PrincipleFlow dataclass."""

    def test_creation(self) -> None:
        """Basic PrincipleFlow creation."""
        flow = PrincipleFlow(
            principle="Composable",
            source_draw_strength=1.0,
            contribution_weight=0.8,
            evidence=("identity-law",),
        )
        assert flow.principle == "Composable"
        assert flow.source_draw_strength == 1.0
        assert flow.contribution_weight == 0.8
        assert flow.evidence == ("identity-law",)

    def test_clamps_strength_to_valid_range(self) -> None:
        """Strengths are clamped to [0, 1]."""
        flow = PrincipleFlow(
            principle="Composable",
            source_draw_strength=1.5,  # Over max
            contribution_weight=-0.5,  # Under min
        )
        assert flow.source_draw_strength == 1.0
        assert flow.contribution_weight == 0.0

    def test_empty_evidence_default(self) -> None:
        """Evidence defaults to empty tuple."""
        flow = PrincipleFlow(
            principle="Ethical",
            source_draw_strength=0.9,
            contribution_weight=1.0,
        )
        assert flow.evidence == ()

    def test_frozen_immutability(self) -> None:
        """PrincipleFlow is frozen (immutable)."""
        flow = PrincipleFlow(
            principle="Composable",
            source_draw_strength=1.0,
            contribution_weight=1.0,
        )
        with pytest.raises(AttributeError):
            flow.principle = "Ethical"  # type: ignore


# =============================================================================
# DerivationRationale Tests
# =============================================================================


class TestDerivationRationale:
    """Tests for DerivationRationale dataclass."""

    def test_creation(self) -> None:
        """Basic DerivationRationale creation."""
        now = datetime.now(timezone.utc)
        rationale = DerivationRationale(
            summary="Inherits composition laws",
            reasoning="Flux derives composition from Id's identity law...",
            decided_at=now,
            decision_id="decide-abc123",
            alternatives_considered=("Compose", "Fix"),
        )
        assert rationale.summary == "Inherits composition laws"
        assert rationale.decision_id == "decide-abc123"
        assert "Compose" in rationale.alternatives_considered

    def test_optional_fields_default(self) -> None:
        """Optional fields have sensible defaults."""
        now = datetime.now(timezone.utc)
        rationale = DerivationRationale(
            summary="Simple derivation",
            reasoning="...",
            decided_at=now,
        )
        assert rationale.decision_id is None
        assert rationale.alternatives_considered == ()

    def test_frozen_immutability(self) -> None:
        """DerivationRationale is frozen."""
        now = datetime.now(timezone.utc)
        rationale = DerivationRationale(
            summary="Test",
            reasoning="...",
            decided_at=now,
        )
        with pytest.raises(AttributeError):
            rationale.summary = "Changed"  # type: ignore


# =============================================================================
# WitnessedEdge Tests: Creation
# =============================================================================


class TestWitnessedEdgeCreation:
    """Tests for WitnessedEdge creation patterns."""

    def test_empty_edge(self) -> None:
        """Empty edge has default values."""
        edge = WitnessedEdge.empty("Id", "Flux")
        assert edge.source == "Id"
        assert edge.target == "Flux"
        assert edge.edge_type == EdgeType.DERIVES_FROM
        assert edge.edge_strength == 0.5
        assert edge.mark_ids == ()
        assert edge.rationale is None
        assert edge.principle_flows == ()

    def test_axiomatic_edge(self) -> None:
        """Axiomatic edges have categorical evidence."""
        edge = WitnessedEdge.axiomatic("CONSTITUTION", "Id")
        assert edge.source == "CONSTITUTION"
        assert edge.target == "Id"
        assert edge.is_categorical
        assert edge.edge_strength == 1.0
        assert edge.rationale is not None
        assert edge.rationale.decision_id == "bootstrap"
        assert edge.last_witnessed is not None

    def test_edge_key(self) -> None:
        """edge_key returns (source, target) tuple."""
        edge = WitnessedEdge.empty("A", "B")
        assert edge.edge_key == ("A", "B")

    def test_evidence_count_empty(self) -> None:
        """Empty edge has zero evidence count."""
        edge = WitnessedEdge.empty("A", "B")
        assert edge.evidence_count == 0

    def test_repr(self) -> None:
        """Repr is readable for debugging."""
        edge = WitnessedEdge.empty("Id", "Flux")
        repr_str = repr(edge)
        assert "Id" in repr_str
        assert "Flux" in repr_str
        assert "50%" in repr_str


# =============================================================================
# WitnessedEdge Tests: Immutability
# =============================================================================


class TestWitnessedEdgeImmutability:
    """Tests for WitnessedEdge immutability."""

    def test_frozen(self) -> None:
        """WitnessedEdge is frozen."""
        edge = WitnessedEdge.empty("A", "B")
        with pytest.raises(AttributeError):
            edge.source = "C"  # type: ignore

    def test_with_mark_returns_new_edge(self) -> None:
        """with_mark returns new edge (immutable)."""
        original = WitnessedEdge.empty("A", "B")
        updated = original.with_mark("mark-123")

        assert original.mark_ids == ()
        assert updated.mark_ids == ("mark-123",)
        assert original is not updated

    def test_with_rationale_returns_new_edge(self) -> None:
        """with_rationale returns new edge."""
        original = WitnessedEdge.empty("A", "B")
        rationale = DerivationRationale(
            summary="Test",
            reasoning="...",
            decided_at=datetime.now(timezone.utc),
        )
        updated = original.with_rationale(rationale)

        assert original.rationale is None
        assert updated.rationale is not None
        assert original is not updated

    def test_with_principle_flow_returns_new_edge(self) -> None:
        """with_principle_flow returns new edge."""
        original = WitnessedEdge.empty("A", "B")
        flow = PrincipleFlow("Composable", 1.0, 1.0, ())
        updated = original.with_principle_flow(flow)

        assert original.principle_flows == ()
        assert len(updated.principle_flows) == 1
        assert original is not updated


# =============================================================================
# WitnessedEdge Tests: Mark Attachment
# =============================================================================


class TestWitnessedEdgeMarks:
    """Tests for mark attachment and strength calculation."""

    def test_single_mark_strengthens(self) -> None:
        """Adding a mark increases edge strength."""
        edge = WitnessedEdge.empty("A", "B")
        updated = edge.with_mark("mark-1")

        assert len(updated.mark_ids) == 1
        assert updated.edge_strength > edge.edge_strength

    def test_marks_strengthen_logarithmically(self) -> None:
        """More marks = stronger, with diminishing returns."""
        edge = WitnessedEdge.empty("A", "B")

        # Add 10 marks
        for i in range(10):
            edge = edge.with_mark(f"mark-{i}")

        strength_at_10 = edge.edge_strength

        # Add 90 more marks (total 100)
        for i in range(10, 100):
            edge = edge.with_mark(f"mark-{i}")

        strength_at_100 = edge.edge_strength

        # Should be stronger, but not 10x stronger
        assert strength_at_100 > strength_at_10
        assert strength_at_100 < strength_at_10 * 2

    def test_mark_idempotent(self) -> None:
        """Adding same mark twice is idempotent."""
        edge = WitnessedEdge.empty("A", "B")
        edge = edge.with_mark("mark-1")
        before = edge.edge_strength

        edge = edge.with_mark("mark-1")  # Same mark again
        after = edge.edge_strength

        assert len(edge.mark_ids) == 1
        assert before == after

    def test_mark_strength_capped_at_95(self) -> None:
        """Mark strength is capped at 0.95 (not categorical)."""
        edge = WitnessedEdge.empty("A", "B")

        # Add many marks
        for i in range(10000):
            edge = edge.with_mark(f"mark-{i}")

        assert edge.edge_strength <= 0.95
        assert not edge.is_categorical

    def test_categorical_edge_stays_strong(self) -> None:
        """Categorical edges stay at strength 1.0."""
        edge = WitnessedEdge.axiomatic("CONSTITUTION", "Id")
        updated = edge.with_mark("mark-1")

        assert updated.edge_strength == 1.0
        assert updated.is_categorical


# =============================================================================
# WitnessedEdge Tests: Test and Proof Attachment
# =============================================================================


class TestWitnessedEdgeTests:
    """Tests for test and proof attachment."""

    def test_with_test_strengthens(self) -> None:
        """Adding a test increases strength."""
        edge = WitnessedEdge.empty("A", "B")
        updated = edge.with_test("test-composition")

        assert "test-composition" in updated.test_ids
        assert updated.edge_strength > edge.edge_strength

    def test_with_test_idempotent(self) -> None:
        """Adding same test twice is idempotent."""
        edge = WitnessedEdge.empty("A", "B")
        edge = edge.with_test("test-1")
        count = len(edge.test_ids)

        edge = edge.with_test("test-1")
        assert len(edge.test_ids) == count

    def test_with_proof_makes_categorical(self) -> None:
        """Adding a proof upgrades to categorical evidence."""
        edge = WitnessedEdge.empty("A", "B")
        assert not edge.is_categorical

        updated = edge.with_proof("dafny-proof-123")

        assert "dafny-proof-123" in updated.proof_ids
        assert updated.is_categorical
        assert updated.edge_strength == 1.0
        assert updated.evidence_type == EvidenceType.CATEGORICAL

    def test_evidence_count_accumulates(self) -> None:
        """Evidence count includes all types."""
        edge = WitnessedEdge.empty("A", "B")
        edge = edge.with_mark("m1").with_mark("m2")
        edge = edge.with_test("t1")
        edge = edge.with_proof("p1")

        assert edge.evidence_count == 4


# =============================================================================
# WitnessedEdge Tests: Principle Flows
# =============================================================================


class TestWitnessedEdgePrincipleFlows:
    """Tests for principle flow tracking."""

    def test_add_principle_flow(self) -> None:
        """Can add principle flows to edge."""
        edge = WitnessedEdge.empty("Id", "Flux")
        flow = PrincipleFlow(
            principle="Composable",
            source_draw_strength=1.0,
            contribution_weight=1.0,
            evidence=("identity-law",),
        )
        updated = edge.with_principle_flow(flow)

        assert len(updated.principle_flows) == 1
        assert updated.principle_flows[0].principle == "Composable"

    def test_replace_principle_flow(self) -> None:
        """Adding same principle replaces existing flow."""
        edge = WitnessedEdge.empty("A", "B")
        flow1 = PrincipleFlow("Composable", 0.5, 0.5, ())
        flow2 = PrincipleFlow("Composable", 1.0, 1.0, ("new-evidence",))

        edge = edge.with_principle_flow(flow1)
        edge = edge.with_principle_flow(flow2)

        assert len(edge.principle_flows) == 1
        assert edge.principle_flows[0].source_draw_strength == 1.0
        assert edge.principle_flows[0].evidence == ("new-evidence",)

    def test_multiple_principle_flows(self) -> None:
        """Can have flows for multiple principles."""
        edge = WitnessedEdge.empty("Judge", "Brain")
        edge = edge.with_principle_flow(PrincipleFlow("Ethical", 1.0, 1.0, ()))
        edge = edge.with_principle_flow(PrincipleFlow("Tasteful", 0.9, 0.8, ()))
        edge = edge.with_principle_flow(PrincipleFlow("Curated", 0.8, 0.7, ()))

        assert len(edge.principle_flows) == 3
        principles = {f.principle for f in edge.principle_flows}
        assert principles == {"Ethical", "Tasteful", "Curated"}

    def test_principle_flows_sorted_by_name(self) -> None:
        """Principle flows are sorted by principle name (deterministic)."""
        edge = WitnessedEdge.empty("A", "B")
        edge = edge.with_principle_flow(PrincipleFlow("Tasteful", 1.0, 1.0, ()))
        edge = edge.with_principle_flow(PrincipleFlow("Composable", 1.0, 1.0, ()))
        edge = edge.with_principle_flow(PrincipleFlow("Ethical", 1.0, 1.0, ()))

        # Should be alphabetically sorted
        assert edge.principle_flows[0].principle == "Composable"
        assert edge.principle_flows[1].principle == "Ethical"
        assert edge.principle_flows[2].principle == "Tasteful"


# =============================================================================
# WitnessedEdge Tests: Edge Types
# =============================================================================


class TestEdgeTypes:
    """Tests for different edge types."""

    def test_default_is_derives_from(self) -> None:
        """Default edge type is DERIVES_FROM."""
        edge = WitnessedEdge.empty("A", "B")
        assert edge.edge_type == EdgeType.DERIVES_FROM

    def test_all_edge_types(self) -> None:
        """All edge types are valid."""
        for edge_type in EdgeType:
            edge = WitnessedEdge(
                source="A",
                target="B",
                edge_type=edge_type,
            )
            assert edge.edge_type == edge_type


# =============================================================================
# WitnessedEdge Tests: Timestamp Tracking
# =============================================================================


class TestWitnessedEdgeTimestamps:
    """Tests for timestamp tracking on edges."""

    def test_empty_edge_no_timestamp(self) -> None:
        """Empty edges have no last_witnessed timestamp."""
        edge = WitnessedEdge.empty("A", "B")
        assert edge.last_witnessed is None

    def test_mark_updates_timestamp(self) -> None:
        """Adding a mark updates last_witnessed."""
        edge = WitnessedEdge.empty("A", "B")
        updated = edge.with_mark("mark-1")

        assert updated.last_witnessed is not None
        assert isinstance(updated.last_witnessed, datetime)

    def test_test_updates_timestamp(self) -> None:
        """Adding a test updates last_witnessed."""
        edge = WitnessedEdge.empty("A", "B")
        updated = edge.with_test("test-1")

        assert updated.last_witnessed is not None

    def test_proof_updates_timestamp(self) -> None:
        """Adding a proof updates last_witnessed."""
        edge = WitnessedEdge.empty("A", "B")
        updated = edge.with_proof("proof-1")

        assert updated.last_witnessed is not None
