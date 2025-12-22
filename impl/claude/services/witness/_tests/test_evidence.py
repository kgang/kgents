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


# =============================================================================
# Phase 1 Enhancements: ORPHAN Level, EvidenceRelation, Lineage, Garden
# =============================================================================


class TestOrphanLevel:
    """Tests for L-∞ ORPHAN level."""

    def test_orphan_level_ordering(self) -> None:
        """ORPHAN < PROMPT < TRACE (L-∞ < L-2 < L-1)."""
        assert EvidenceLevel.ORPHAN < EvidenceLevel.PROMPT
        assert EvidenceLevel.ORPHAN < EvidenceLevel.TRACE
        assert EvidenceLevel.ORPHAN < EvidenceLevel.MARK

    def test_orphan_level_value(self) -> None:
        """ORPHAN has value -3."""
        assert EvidenceLevel.ORPHAN.value == -3

    def test_orphan_level_label(self) -> None:
        """ORPHAN has special L-∞ label."""
        assert EvidenceLevel.ORPHAN.level_label == "L-∞"

    def test_orphan_display_name(self) -> None:
        """ORPHAN has 'Orphan' display name."""
        assert EvidenceLevel.ORPHAN.display_name == "Orphan"

    def test_orphan_is_orphan_property(self) -> None:
        """ORPHAN.is_orphan is True."""
        assert EvidenceLevel.ORPHAN.is_orphan is True
        assert EvidenceLevel.MARK.is_orphan is False

    def test_orphan_has_color(self) -> None:
        """ORPHAN has red color (needs attention)."""
        assert EvidenceLevel.ORPHAN.color == "#991B1B"


class TestEvidenceRelation:
    """Tests for EvidenceRelation enum."""

    def test_relation_values(self) -> None:
        """Relations have expected values."""
        from services.witness.evidence import EvidenceRelation

        assert EvidenceRelation.SUPPORTS.value == "supports"
        assert EvidenceRelation.REFUTES.value == "refutes"
        assert EvidenceRelation.SUPERSEDES.value == "supersedes"
        assert EvidenceRelation.EXTENDS.value == "extends"
        assert EvidenceRelation.QUALIFIES.value == "qualifies"

    def test_is_positive_relations(self) -> None:
        """SUPPORTS and EXTENDS are positive relations."""
        from services.witness.evidence import EvidenceRelation

        assert EvidenceRelation.SUPPORTS.is_positive is True
        assert EvidenceRelation.EXTENDS.is_positive is True
        assert EvidenceRelation.REFUTES.is_positive is False

    def test_is_negative_relations(self) -> None:
        """REFUTES and QUALIFIES are negative relations."""
        from services.witness.evidence import EvidenceRelation

        assert EvidenceRelation.REFUTES.is_negative is True
        assert EvidenceRelation.QUALIFIES.is_negative is True
        assert EvidenceRelation.SUPPORTS.is_negative is False

    def test_relation_symbols(self) -> None:
        """Relations have symbols for display."""
        from services.witness.evidence import EvidenceRelation

        assert EvidenceRelation.SUPPORTS.symbol == "+"
        assert EvidenceRelation.REFUTES.symbol == "−"


class TestEvidenceLineage:
    """Tests for Evidence ancestry/lineage fields."""

    def test_evidence_has_parent_ids(self) -> None:
        """Evidence can have parent_ids."""
        evidence = Evidence(
            level=EvidenceLevel.MARK,
            parent_ids=("evd-parent1", "evd-parent2"),
        )
        assert evidence.parent_ids == ("evd-parent1", "evd-parent2")

    def test_evidence_has_lineage_with_parents(self) -> None:
        """has_lineage is True when parent_ids exist."""
        evidence = Evidence(
            level=EvidenceLevel.MARK,
            parent_ids=("evd-parent1",),
        )
        assert evidence.has_lineage is True

    def test_evidence_has_lineage_for_non_orphan(self) -> None:
        """has_lineage is True for non-orphan levels even without parents."""
        evidence = Evidence(level=EvidenceLevel.MARK)
        assert evidence.has_lineage is True

    def test_orphan_has_no_lineage(self) -> None:
        """has_lineage is False for orphan without parents."""
        evidence = Evidence(level=EvidenceLevel.ORPHAN)
        assert evidence.has_lineage is False

    def test_evidence_relation_field(self) -> None:
        """Evidence can have a relation field."""
        from services.witness.evidence import EvidenceRelation

        evidence = Evidence(
            level=EvidenceLevel.MARK,
            relation=EvidenceRelation.SUPPORTS,
            parent_ids=("evd-parent",),
        )
        assert evidence.relation == EvidenceRelation.SUPPORTS

    def test_lineage_serialization(self) -> None:
        """Lineage fields serialize correctly."""
        from services.witness.evidence import EvidenceRelation

        evidence = Evidence(
            level=EvidenceLevel.MARK,
            parent_ids=("evd-p1", "evd-p2"),
            relation=EvidenceRelation.EXTENDS,
        )
        d = evidence.to_dict()
        assert d["parent_ids"] == ["evd-p1", "evd-p2"]
        assert d["relation"] == "extends"

    def test_lineage_deserialization(self) -> None:
        """Lineage fields deserialize correctly."""
        d = {
            "level": 0,
            "parent_ids": ["evd-p1"],
            "relation": "supports",
            "created_at": "2025-01-01T00:00:00",
        }
        evidence = Evidence.from_dict(d)
        assert evidence.parent_ids == ("evd-p1",)
        from services.witness.evidence import EvidenceRelation

        assert evidence.relation == EvidenceRelation.SUPPORTS


class TestOrphanFactory:
    """Tests for from_orphan() factory method."""

    def test_from_orphan_creates_orphan_level(self) -> None:
        """from_orphan creates L-∞ evidence."""
        evidence = Evidence.from_orphan(
            artifact_path="impl/claude/foo.py",
            artifact_type="file",
        )
        assert evidence.level == EvidenceLevel.ORPHAN
        assert evidence.source_type == "orphan"

    def test_from_orphan_has_zero_confidence(self) -> None:
        """from_orphan has zero confidence (needs tending)."""
        evidence = Evidence.from_orphan("foo.py")
        assert evidence.confidence == 0.0

    def test_from_orphan_needs_tending(self) -> None:
        """Orphan evidence needs_tending is True."""
        evidence = Evidence.from_orphan("foo.py")
        assert evidence.needs_tending is True

    def test_from_orphan_stores_artifact_path(self) -> None:
        """from_orphan stores artifact_path in metadata."""
        evidence = Evidence.from_orphan("impl/claude/bar.py", artifact_type="function")
        assert evidence.metadata["artifact_path"] == "impl/claude/bar.py"
        assert evidence.metadata["artifact_type"] == "function"

    def test_from_orphan_with_suggested_prompt(self) -> None:
        """from_orphan can include suggested prompt."""
        evidence = Evidence.from_orphan(
            "foo.py",
            suggested_prompt="Implement the foo module",
        )
        assert evidence.metadata["suggested_prompt"] == "Implement the foo module"


class TestPromptFactory:
    """Tests for from_prompt() factory method."""

    def test_from_prompt_creates_prompt_level(self) -> None:
        """from_prompt creates L-2 evidence."""
        evidence = Evidence.from_prompt(
            prompt_text="Implement a function that calculates fibonacci",
            model="claude-3.5-sonnet",
        )
        assert evidence.level == EvidenceLevel.PROMPT
        assert evidence.source_type == "prompt"

    def test_from_prompt_has_confidence(self) -> None:
        """from_prompt has reasonable confidence."""
        evidence = Evidence.from_prompt("Test prompt")
        assert evidence.confidence == 0.7

    def test_from_prompt_stores_metadata(self) -> None:
        """from_prompt stores metadata correctly."""
        evidence = Evidence.from_prompt(
            prompt_text="Test prompt",
            prompt_id="prompt-123",
            model="claude-3.5-sonnet",
            session_id="session-abc",
        )
        assert evidence.metadata["prompt_id"] == "prompt-123"
        assert evidence.metadata["model"] == "claude-3.5-sonnet"
        assert evidence.metadata["session_id"] == "session-abc"

    def test_from_prompt_truncates_preview(self) -> None:
        """from_prompt truncates long prompts for preview."""
        long_prompt = "x" * 1000
        evidence = Evidence.from_prompt(long_prompt)
        assert len(evidence.metadata["prompt_preview"]) == 200
        assert evidence.metadata["prompt_length"] == 1000


class TestEvidenceLadder:
    """Tests for EvidenceLadder aggregate dataclass."""

    def test_ladder_from_evidence(self) -> None:
        """EvidenceLadder counts evidence at each level."""
        from services.witness.status import EvidenceLadder

        evidence = [
            Evidence(level=EvidenceLevel.MARK),
            Evidence(level=EvidenceLevel.MARK),
            Evidence(level=EvidenceLevel.TEST),
            Evidence(level=EvidenceLevel.TRACE),
        ]
        ladder = EvidenceLadder.from_evidence(evidence)
        assert ladder.mark == 2
        assert ladder.test == 1
        assert ladder.trace == 1
        assert ladder.orphan == 0

    def test_ladder_total_count(self) -> None:
        """total_count sums all levels."""
        from services.witness.status import EvidenceLadder

        ladder = EvidenceLadder(mark=2, test=3, proof=1)
        assert ladder.total_count == 6

    def test_ladder_height_linear(self) -> None:
        """height is linear for 0-5 evidence."""
        from services.witness.status import EvidenceLadder

        assert EvidenceLadder(mark=0).height == 0
        assert EvidenceLadder(mark=3).height == 30
        assert EvidenceLadder(mark=5).height == 50

    def test_ladder_height_diminishing(self) -> None:
        """height has diminishing returns above 5."""
        from services.witness.status import EvidenceLadder

        assert EvidenceLadder(mark=10).height == 60  # 50 + (10-5)*2
        assert EvidenceLadder(mark=20).height == 80  # 50 + 15*2

    def test_ladder_height_capped(self) -> None:
        """height is capped at 100."""
        from services.witness.status import EvidenceLadder

        assert EvidenceLadder(mark=100).height == 100

    def test_ladder_needs_attention(self) -> None:
        """needs_attention is True when orphans exist."""
        from services.witness.status import EvidenceLadder

        assert EvidenceLadder(orphan=1).needs_attention is True
        assert EvidenceLadder(mark=5).needs_attention is False


class TestPlantHealth:
    """Tests for PlantHealth enum."""

    def test_plant_health_values(self) -> None:
        """PlantHealth has expected values."""
        from services.witness.status import PlantHealth

        assert PlantHealth.BLOOMING.value == "blooming"
        assert PlantHealth.HEALTHY.value == "healthy"
        assert PlantHealth.WILTING.value == "wilting"
        assert PlantHealth.DEAD.value == "dead"

    def test_plant_health_emojis(self) -> None:
        """PlantHealth has emojis."""
        from services.witness.status import PlantHealth

        assert PlantHealth.BLOOMING.emoji == "🌸"
        assert PlantHealth.HEALTHY.emoji == "🌿"
        assert PlantHealth.WILTING.emoji == "🥀"
        assert PlantHealth.DEAD.emoji == "🍂"

    def test_plant_health_pulse_rates(self) -> None:
        """PlantHealth has pulse rates."""
        from services.witness.status import PlantHealth

        assert PlantHealth.BLOOMING.pulse_rate == 1.5
        assert PlantHealth.DEAD.pulse_rate == 0.0


class TestSpecPlant:
    """Tests for SpecPlant garden visualization."""

    def test_spec_plant_from_spec(self) -> None:
        """SpecPlant.from_spec creates plant correctly."""
        from services.witness.status import SpecPlant

        evidence = [
            Evidence.from_witness_mark("mark-1", "Verified"),
            Evidence.from_test("test.py", "test_foo", passed=True),
        ]
        plant = SpecPlant.from_spec(
            path="spec/foo.md",
            status=SpecStatus.IN_PROGRESS,
            evidence=evidence,
        )
        assert plant.path == "spec/foo.md"
        assert plant.status == SpecStatus.IN_PROGRESS
        assert plant.evidence_ladder.mark == 1
        assert plant.evidence_ladder.test == 1

    def test_spec_plant_health_from_status(self) -> None:
        """Plant health derives from status."""
        from services.witness.status import PlantHealth, SpecPlant

        # Superseded = DEAD
        plant = SpecPlant.from_spec(
            path="spec/old.md",
            status=SpecStatus.SUPERSEDED,
            evidence=[],
        )
        assert plant.health == PlantHealth.DEAD

        # Contested = WILTING
        plant = SpecPlant.from_spec(
            path="spec/contested.md",
            status=SpecStatus.CONTESTED,
            evidence=[],
        )
        assert plant.health == PlantHealth.WILTING

    def test_spec_plant_blooming_when_witnessed_high_confidence(self) -> None:
        """Plant is BLOOMING when witnessed with high confidence."""
        from services.witness.status import PlantHealth, SpecPlant

        plant = SpecPlant.from_spec(
            path="spec/good.md",
            status=SpecStatus.WITNESSED,
            evidence=[Evidence(confidence=1.0), Evidence(confidence=0.9)],
        )
        assert plant.health == PlantHealth.BLOOMING

    def test_spec_plant_pulse_rate(self) -> None:
        """Pulse rate reflects confidence."""
        from services.witness.status import SpecPlant

        # Low confidence = flatline
        plant = SpecPlant.from_spec(
            path="spec/weak.md",
            status=SpecStatus.IN_PROGRESS,
            evidence=[Evidence(confidence=0.1)],
        )
        assert plant.pulse_rate == 0.0  # Flatline

        # High confidence = thriving
        plant = SpecPlant.from_spec(
            path="spec/strong.md",
            status=SpecStatus.WITNESSED,
            evidence=[Evidence(confidence=0.95)],
        )
        assert plant.pulse_rate == 1.5  # Thriving

    def test_spec_plant_needs_tending(self) -> None:
        """needs_tending is True for wilting/dead or orphans."""
        from services.witness.status import SpecPlant

        # Contested plant needs tending
        plant = SpecPlant.from_spec(
            path="spec/bad.md",
            status=SpecStatus.CONTESTED,
            evidence=[],
        )
        assert plant.needs_tending is True

        # Plant with orphan evidence needs tending
        plant = SpecPlant.from_spec(
            path="spec/orphaned.md",
            status=SpecStatus.IN_PROGRESS,
            evidence=[Evidence.from_orphan("foo.py")],
        )
        assert plant.needs_tending is True
