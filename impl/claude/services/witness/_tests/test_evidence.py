"""
Tests for Evidence Ladder Infrastructure.

Phase 1 of Witness Assurance Protocol:
- EvidenceLevel IntEnum (L-2 to L3)
- Evidence unified dataclass
- SpecStatus enum
- compute_status() function

Teaching:
    pattern: Tests use property-based approach where possible.
             Evidence ordering is mathematically defined (IntEnum),
             so we verify the invariants rather than spot-checking.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from services.witness.evidence import (
    Evidence,
    EvidenceLevel,
    compute_content_hash,
    generate_evidence_id,
)
from services.witness.mark import Proof
from services.witness.status import (
    ContextGraphProtocol,
    SpecStatus,
    WitnessedCriteria,
    compute_status,
    compute_status_from_evidence_only,
)

# =============================================================================
# EvidenceLevel Tests
# =============================================================================


class TestEvidenceLevel:
    """Tests for EvidenceLevel IntEnum."""

    def test_evidence_level_ordering(self) -> None:
        """Evidence levels have natural ordering: L-2 < L-1 < L0 < L1 < L2 < L3."""
        assert EvidenceLevel.PROMPT < EvidenceLevel.TRACE
        assert EvidenceLevel.TRACE < EvidenceLevel.MARK
        assert EvidenceLevel.MARK < EvidenceLevel.TEST
        assert EvidenceLevel.TEST < EvidenceLevel.PROOF
        assert EvidenceLevel.PROOF < EvidenceLevel.BET

    def test_evidence_level_values(self) -> None:
        """Evidence levels have expected integer values."""
        assert EvidenceLevel.PROMPT.value == -2
        assert EvidenceLevel.TRACE.value == -1
        assert EvidenceLevel.MARK.value == 0
        assert EvidenceLevel.TEST.value == 1
        assert EvidenceLevel.PROOF.value == 2
        assert EvidenceLevel.BET.value == 3

    def test_evidence_level_labels(self) -> None:
        """Evidence levels have correct L-labels."""
        assert EvidenceLevel.PROMPT.level_label == "L-2"
        assert EvidenceLevel.TRACE.level_label == "L-1"
        assert EvidenceLevel.MARK.level_label == "L0"
        assert EvidenceLevel.TEST.level_label == "L1"
        assert EvidenceLevel.PROOF.level_label == "L2"
        assert EvidenceLevel.BET.level_label == "L3"

    def test_evidence_level_display_names(self) -> None:
        """Evidence levels have human-readable display names."""
        assert EvidenceLevel.PROMPT.display_name == "Prompt"
        assert EvidenceLevel.MARK.display_name == "Mark"
        assert EvidenceLevel.PROOF.display_name == "Proof"

    def test_evidence_level_descriptions(self) -> None:
        """Evidence levels have descriptions."""
        assert "generative" in EvidenceLevel.PROMPT.description.lower()
        assert "runtime" in EvidenceLevel.TRACE.description.lower()
        assert "human" in EvidenceLevel.MARK.description.lower()


# =============================================================================
# Evidence Tests
# =============================================================================


class TestEvidence:
    """Tests for Evidence dataclass."""

    def test_evidence_immutability(self) -> None:
        """Evidence is frozen (immutable)."""
        evidence = Evidence(
            level=EvidenceLevel.MARK,
            source_type="mark",
            created_by="kent",
        )
        with pytest.raises(AttributeError):
            evidence.level = EvidenceLevel.TEST  # type: ignore[misc]

    def test_evidence_default_values(self) -> None:
        """Evidence has sensible defaults."""
        evidence = Evidence()
        assert evidence.level == EvidenceLevel.MARK
        assert evidence.source_type == "unknown"
        assert evidence.created_by == "system"
        assert evidence.confidence == 1.0
        assert evidence.target_spec is None
        assert evidence.proof is None

    def test_evidence_is_generative(self) -> None:
        """is_generative is True only for PROMPT level."""
        prompt_evidence = Evidence(level=EvidenceLevel.PROMPT)
        trace_evidence = Evidence(level=EvidenceLevel.TRACE)
        mark_evidence = Evidence(level=EvidenceLevel.MARK)

        assert prompt_evidence.is_generative is True
        assert trace_evidence.is_generative is False
        assert mark_evidence.is_generative is False

    def test_evidence_is_runtime(self) -> None:
        """is_runtime is True for PROMPT, TRACE, and MARK levels."""
        assert Evidence(level=EvidenceLevel.PROMPT).is_runtime is True
        assert Evidence(level=EvidenceLevel.TRACE).is_runtime is True
        assert Evidence(level=EvidenceLevel.MARK).is_runtime is True
        assert Evidence(level=EvidenceLevel.TEST).is_runtime is False
        assert Evidence(level=EvidenceLevel.PROOF).is_runtime is False

    def test_evidence_is_automated(self) -> None:
        """is_automated is True for TEST, PROOF, and BET levels."""
        assert Evidence(level=EvidenceLevel.PROMPT).is_automated is False
        assert Evidence(level=EvidenceLevel.MARK).is_automated is False
        assert Evidence(level=EvidenceLevel.TEST).is_automated is True
        assert Evidence(level=EvidenceLevel.PROOF).is_automated is True
        assert Evidence(level=EvidenceLevel.BET).is_automated is True

    def test_evidence_is_formal(self) -> None:
        """is_formal is True for PROOF and BET levels."""
        assert Evidence(level=EvidenceLevel.TEST).is_formal is False
        assert Evidence(level=EvidenceLevel.PROOF).is_formal is True
        assert Evidence(level=EvidenceLevel.BET).is_formal is True

    def test_evidence_has_economic_stake(self) -> None:
        """has_economic_stake is True only for BET level."""
        assert Evidence(level=EvidenceLevel.PROOF).has_economic_stake is False
        assert Evidence(level=EvidenceLevel.BET).has_economic_stake is True


class TestEvidenceFactories:
    """Tests for Evidence factory methods."""

    def test_from_trace_witness(self) -> None:
        """from_trace_witness creates L-1 evidence."""
        evidence = Evidence.from_trace_witness(
            trace_id="trace-abc123",
            agent_path="world.witness.manifest",
            target_spec="spec/protocols/witness.md",
        )
        assert evidence.level == EvidenceLevel.TRACE
        assert evidence.source_type == "trace"
        assert evidence.metadata["trace_id"] == "trace-abc123"
        assert evidence.metadata["agent_path"] == "world.witness.manifest"
        assert evidence.confidence == 0.9

    def test_from_witness_mark(self) -> None:
        """from_witness_mark creates L0 evidence."""
        evidence = Evidence.from_witness_mark(
            mark_id="mark-def456",
            action="Fixed the bug",
            created_by="kent",
        )
        assert evidence.level == EvidenceLevel.MARK
        assert evidence.source_type == "mark"
        assert evidence.metadata["mark_id"] == "mark-def456"
        assert evidence.created_by == "kent"
        assert evidence.confidence == 0.8

    def test_from_witness_mark_with_proof(self) -> None:
        """from_witness_mark can include Toulmin proof."""
        proof = Proof.empirical(
            data="Tests pass",
            warrant="Passing tests indicate correctness",
            claim="Bug is fixed",
        )
        evidence = Evidence.from_witness_mark(
            mark_id="mark-ghi789",
            action="Fixed the bug",
            proof=proof,
        )
        assert evidence.proof is not None
        assert evidence.proof.claim == "Bug is fixed"

    def test_from_test(self) -> None:
        """from_test creates L1 evidence."""
        evidence = Evidence.from_test(
            test_path="tests/test_foo.py",
            test_name="test_bar",
            passed=True,
        )
        assert evidence.level == EvidenceLevel.TEST
        assert evidence.source_type == "test"
        assert evidence.metadata["passed"] is True
        assert evidence.confidence == 1.0

    def test_from_test_failed(self) -> None:
        """from_test with failed test has 0 confidence."""
        evidence = Evidence.from_test(
            test_path="tests/test_foo.py",
            test_name="test_bar",
            passed=False,
        )
        assert evidence.confidence == 0.0

    def test_from_proof(self) -> None:
        """from_proof creates L2 evidence."""
        evidence = Evidence.from_proof(
            proof_id="proof-jkl012",
            obligation_discharged="identity_law",
        )
        assert evidence.level == EvidenceLevel.PROOF
        assert evidence.source_type == "proof"
        assert evidence.confidence == 1.0

    def test_from_bet(self) -> None:
        """from_bet creates L3 evidence."""
        evidence = Evidence.from_bet(
            bet_id="bet-mno345",
            stake=100.0,
            settled=True,
            settlement_value=0.95,
        )
        assert evidence.level == EvidenceLevel.BET
        assert evidence.source_type == "bet"
        assert evidence.confidence == 0.95


class TestEvidenceSerialization:
    """Tests for Evidence serialization."""

    def test_to_dict(self) -> None:
        """to_dict serializes Evidence correctly."""
        evidence = Evidence(
            id="evd-test123",
            level=EvidenceLevel.MARK,
            source_type="mark",
            target_spec="spec/foo.md",
            content_hash="abc123",
            created_by="kent",
            confidence=0.9,
        )
        d = evidence.to_dict()
        assert d["id"] == "evd-test123"
        assert d["level"] == 0  # MARK value
        assert d["level_label"] == "L0"
        assert d["source_type"] == "mark"
        assert d["target_spec"] == "spec/foo.md"

    def test_from_dict(self) -> None:
        """from_dict deserializes Evidence correctly."""
        d = {
            "id": "evd-test456",
            "level": -1,  # TRACE
            "source_type": "trace",
            "target_spec": "spec/bar.md",
            "content_hash": "def456",
            "created_at": "2025-01-01T00:00:00",
            "created_by": "system",
            "metadata": {"trace_id": "trace-xyz"},
            "confidence": 0.9,
        }
        evidence = Evidence.from_dict(d)
        assert evidence.id == "evd-test456"
        assert evidence.level == EvidenceLevel.TRACE
        assert evidence.metadata["trace_id"] == "trace-xyz"

    def test_roundtrip(self) -> None:
        """Evidence roundtrips through dict correctly."""
        original = Evidence.from_witness_mark(
            mark_id="mark-roundtrip",
            action="Test roundtrip",
            target_spec="spec/roundtrip.md",
        )
        roundtripped = Evidence.from_dict(original.to_dict())
        assert roundtripped.level == original.level
        assert roundtripped.source_type == original.source_type
        assert roundtripped.target_spec == original.target_spec


# =============================================================================
# SpecStatus Tests
# =============================================================================


class TestSpecStatus:
    """Tests for SpecStatus enum."""

    def test_status_values(self) -> None:
        """Status values are correct strings."""
        assert SpecStatus.UNWITNESSED.value == "unwitnessed"
        assert SpecStatus.IN_PROGRESS.value == "in_progress"
        assert SpecStatus.WITNESSED.value == "witnessed"
        assert SpecStatus.CONTESTED.value == "contested"
        assert SpecStatus.SUPERSEDED.value == "superseded"

    def test_status_emojis(self) -> None:
        """Statuses have emojis."""
        assert SpecStatus.UNWITNESSED.emoji == "🔲"
        assert SpecStatus.WITNESSED.emoji == "✅"
        assert SpecStatus.CONTESTED.emoji == "⚠️"

    def test_is_terminal(self) -> None:
        """Only SUPERSEDED is terminal."""
        assert SpecStatus.UNWITNESSED.is_terminal is False
        assert SpecStatus.WITNESSED.is_terminal is False
        assert SpecStatus.SUPERSEDED.is_terminal is True

    def test_is_healthy(self) -> None:
        """WITNESSED and IN_PROGRESS are healthy."""
        assert SpecStatus.WITNESSED.is_healthy is True
        assert SpecStatus.IN_PROGRESS.is_healthy is True
        assert SpecStatus.UNWITNESSED.is_healthy is False
        assert SpecStatus.CONTESTED.is_healthy is False


# =============================================================================
# WitnessedCriteria Tests
# =============================================================================


class TestWitnessedCriteria:
    """Tests for WitnessedCriteria helper class."""

    def test_all_criteria_met(self) -> None:
        """is_witnessed is True when all criteria met."""
        criteria = WitnessedCriteria(
            has_trace_or_test=True,
            has_mark=True,
            has_implementation=True,
            has_refutation=False,
        )
        assert criteria.is_witnessed is True
        assert criteria.is_contested is False
        assert criteria.is_in_progress is False

    def test_missing_trace_or_test(self) -> None:
        """Missing trace/test results in IN_PROGRESS."""
        criteria = WitnessedCriteria(
            has_trace_or_test=False,
            has_mark=True,
            has_implementation=True,
        )
        assert criteria.is_witnessed is False
        assert criteria.is_in_progress is True
        assert "L-1 TraceWitness or L1 Test" in criteria.missing_criteria()

    def test_missing_mark(self) -> None:
        """Missing mark results in IN_PROGRESS."""
        criteria = WitnessedCriteria(
            has_trace_or_test=True,
            has_mark=False,
            has_implementation=True,
        )
        assert criteria.is_witnessed is False
        assert "L0 Mark" in criteria.missing_criteria()

    def test_refutation_causes_contested(self) -> None:
        """Refutation causes CONTESTED even if other criteria met."""
        criteria = WitnessedCriteria(
            has_trace_or_test=True,
            has_mark=True,
            has_implementation=True,
            has_refutation=True,
        )
        assert criteria.is_contested is True
        assert criteria.is_witnessed is False

    def test_to_reason(self) -> None:
        """to_reason generates appropriate reason strings."""
        # Witnessed
        criteria = WitnessedCriteria(
            has_trace_or_test=True,
            has_mark=True,
            has_implementation=True,
        )
        assert "All criteria met" in criteria.to_reason()

        # In progress
        criteria = WitnessedCriteria(has_mark=True, has_implementation=False)
        assert "In progress" in criteria.to_reason()

        # Contested
        criteria = WitnessedCriteria(has_refutation=True)
        assert "refutation" in criteria.to_reason()


# =============================================================================
# compute_status Tests
# =============================================================================


class MockHypergraph:
    """Mock hypergraph for testing."""

    def __init__(self, implementations: list[str] | None = None) -> None:
        self._implementations = implementations or []

    async def follow_edge(self, node_path: str, edge_type: str) -> list[str]:
        if edge_type == "implemented_by":
            return self._implementations
        return []


class TestComputeStatus:
    """Tests for compute_status function."""

    @pytest.mark.asyncio
    async def test_unwitnessed_when_no_evidence(self) -> None:
        """No evidence results in UNWITNESSED."""
        hypergraph = MockHypergraph(implementations=[])
        status, reason = await compute_status(
            "spec/foo.md",
            [],
            hypergraph,
        )
        assert status == SpecStatus.UNWITNESSED
        assert "No evidence" in reason

    @pytest.mark.asyncio
    async def test_in_progress_with_mark_only(self) -> None:
        """Mark alone results in IN_PROGRESS."""
        hypergraph = MockHypergraph(implementations=[])
        evidence = [Evidence.from_witness_mark("mark-123", "Did something")]
        status, reason = await compute_status(
            "spec/foo.md",
            evidence,
            hypergraph,
        )
        assert status == SpecStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_witnessed_with_full_evidence(self) -> None:
        """Full evidence chain results in WITNESSED."""
        hypergraph = MockHypergraph(implementations=["impl/foo.py"])
        evidence = [
            Evidence.from_trace_witness("trace-1", "world.foo.manifest"),
            Evidence.from_witness_mark("mark-1", "Verified behavior"),
        ]
        status, reason = await compute_status(
            "spec/foo.md",
            evidence,
            hypergraph,
        )
        assert status == SpecStatus.WITNESSED
        assert "All criteria met" in reason

    @pytest.mark.asyncio
    async def test_contested_with_refutation(self) -> None:
        """Refutation evidence results in CONTESTED."""
        hypergraph = MockHypergraph(implementations=["impl/foo.py"])
        evidence = [
            Evidence.from_witness_mark("mark-1", "This is wrong"),
            Evidence(
                level=EvidenceLevel.MARK,
                source_type="mark",
                metadata={"relation": "refutes"},
            ),
        ]
        status, reason = await compute_status(
            "spec/foo.md",
            evidence,
            hypergraph,
        )
        assert status == SpecStatus.CONTESTED
        assert "refutation" in reason

    @pytest.mark.asyncio
    async def test_compute_status_requires_hypergraph(self) -> None:
        """compute_status raises TypeError if hypergraph is None."""
        with pytest.raises(TypeError, match="hypergraph is required"):
            await compute_status("spec/foo.md", [], None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_test_evidence_counts_as_trace_or_test(self) -> None:
        """L1 TEST level counts as trace_or_test."""
        hypergraph = MockHypergraph(implementations=["impl/foo.py"])
        evidence = [
            Evidence.from_test("tests/test_foo.py", "test_bar", passed=True),
            Evidence.from_witness_mark("mark-1", "Tested"),
        ]
        status, reason = await compute_status(
            "spec/foo.md",
            evidence,
            hypergraph,
        )
        assert status == SpecStatus.WITNESSED


class TestComputeStatusFromEvidenceOnly:
    """Tests for compute_status_from_evidence_only function."""

    def test_no_evidence_is_unwitnessed(self) -> None:
        """No evidence results in UNWITNESSED."""
        status, reason = compute_status_from_evidence_only([])
        assert status == SpecStatus.UNWITNESSED

    def test_mark_only_is_in_progress(self) -> None:
        """Mark alone results in IN_PROGRESS."""
        evidence = [Evidence.from_witness_mark("mark-1", "Did something")]
        status, reason = compute_status_from_evidence_only(evidence)
        assert status == SpecStatus.IN_PROGRESS
        assert "L-1 TraceWitness or L1 Test" in reason

    def test_trace_and_mark_is_in_progress(self) -> None:
        """Trace + mark without hypergraph is still IN_PROGRESS."""
        evidence = [
            Evidence.from_trace_witness("trace-1", "world.foo"),
            Evidence.from_witness_mark("mark-1", "Verified"),
        ]
        status, reason = compute_status_from_evidence_only(evidence)
        assert status == SpecStatus.IN_PROGRESS
        assert "need hypergraph" in reason

    def test_refutation_is_contested(self) -> None:
        """Refutation evidence results in CONTESTED."""
        evidence = [
            Evidence(
                level=EvidenceLevel.MARK,
                metadata={"relation": "refutes"},
            )
        ]
        status, reason = compute_status_from_evidence_only(evidence)
        assert status == SpecStatus.CONTESTED


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_generate_evidence_id(self) -> None:
        """generate_evidence_id creates unique IDs with prefix."""
        id1 = generate_evidence_id()
        id2 = generate_evidence_id()
        assert id1.startswith("evd-")
        assert id2.startswith("evd-")
        assert id1 != id2

    def test_compute_content_hash(self) -> None:
        """compute_content_hash is deterministic."""
        hash1 = compute_content_hash("test content")
        hash2 = compute_content_hash("test content")
        hash3 = compute_content_hash("different content")
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 16  # Truncated SHA-256
