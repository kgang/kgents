"""
Tests for ASHC Proof Generation Contracts.

These tests verify the core contracts behave correctly:
- Immutability (frozen dataclasses)
- Serialization round-trips
- Property calculations
- Law compliance

Phase 0 Exit Criteria:
- [ ] contracts.py passes mypy strict
- [ ] All contracts have to_dict() for serialization
- [ ] Contracts follow Pattern 2 (Enum Property Pattern)
- [x] 10+ tests for contract behavior
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from ..contracts import (
    CheckerResult,
    LemmaId,
    ObligationId,
    ObligationSource,
    ProofAttempt,
    ProofAttemptId,
    ProofObligation,
    ProofSearchConfig,
    ProofSearchResult,
    ProofStatus,
    VerifiedLemma,
)

# =============================================================================
# ProofObligation Tests
# =============================================================================


class TestProofObligation:
    """Tests for ProofObligation contract."""

    def test_creation_with_minimal_args(self) -> None:
        """ProofObligation can be created with required args only."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="∀ x: int. x + 0 == x",
            source=ObligationSource.TEST,
            source_location="test_math.py:42",
        )

        assert str(obl.id) == "obl-001"
        assert obl.property == "∀ x: int. x + 0 == x"
        assert obl.source == ObligationSource.TEST
        assert obl.source_location == "test_math.py:42"
        assert obl.context == ()
        assert isinstance(obl.created_at, datetime)

    def test_creation_with_context(self) -> None:
        """ProofObligation can include context hints."""
        obl = ProofObligation(
            id=ObligationId("obl-002"),
            property="∀ x. x > 0",
            source=ObligationSource.SPEC,
            source_location="spec/math.md:10",
            context=("Hint: use induction", "Related: lemma-001"),
        )

        assert len(obl.context) == 2
        assert "induction" in obl.context[0]

    def test_immutability(self) -> None:
        """ProofObligation cannot be mutated after creation."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="∀ x. f(x) > 0",
            source=ObligationSource.TEST,
            source_location="test_foo.py:42",
        )

        with pytest.raises(FrozenInstanceError):
            obl.property = "changed"  # type: ignore[misc]

    def test_with_context_returns_new_instance(self) -> None:
        """with_context() returns a new obligation with added context."""
        obl1 = ProofObligation(
            id=ObligationId("obl-001"),
            property="∀ x. x == x",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        obl2 = obl1.with_context("Hint: reflexivity")

        # Original unchanged
        assert obl1.context == ()
        # New has added context
        assert obl2.context == ("Hint: reflexivity",)
        # Same ID
        assert obl1.id == obl2.id

    def test_serialization_roundtrip(self) -> None:
        """to_dict() and from_dict() are inverses."""
        original = ProofObligation(
            id=ObligationId("obl-003"),
            property="∀ x: nat. x >= 0",
            source=ObligationSource.TYPE,
            source_location="world.tools.bash",
            context=("Context 1", "Context 2"),
        )

        data = original.to_dict()
        restored = ProofObligation.from_dict(data)

        assert restored.id == original.id
        assert restored.property == original.property
        assert restored.source == original.source
        assert restored.source_location == original.source_location
        assert restored.context == original.context

    def test_all_obligation_sources(self) -> None:
        """All ObligationSource values work correctly."""
        for source in ObligationSource:
            obl = ProofObligation(
                id=ObligationId(f"obl-{source.name}"),
                property="true",
                source=source,
                source_location="test.py:1",
            )
            assert obl.source == source
            # Roundtrip works
            restored = ProofObligation.from_dict(obl.to_dict())
            assert restored.source == source


# =============================================================================
# ProofAttempt Tests
# =============================================================================


class TestProofAttempt:
    """Tests for ProofAttempt contract."""

    def test_creation(self) -> None:
        """ProofAttempt captures attempt details."""
        attempt = ProofAttempt(
            id=ProofAttemptId("att-001"),
            obligation_id=ObligationId("obl-001"),
            proof_source="lemma Trivial() ensures true {}",
            checker="dafny",
            result=ProofStatus.VERIFIED,
            checker_output="Dafny program verifier finished",
            tactics_used=("simp", "auto"),
            duration_ms=1234,
        )

        assert str(attempt.id) == "att-001"
        assert attempt.checker == "dafny"
        assert attempt.result == ProofStatus.VERIFIED
        assert attempt.duration_ms == 1234
        assert "simp" in attempt.tactics_used

    def test_immutability(self) -> None:
        """ProofAttempt cannot be mutated."""
        attempt = ProofAttempt(
            id=ProofAttemptId("att-001"),
            obligation_id=ObligationId("obl-001"),
            proof_source="",
            checker="lean4",
            result=ProofStatus.FAILED,
            checker_output="error",
        )

        with pytest.raises(FrozenInstanceError):
            attempt.result = ProofStatus.VERIFIED  # type: ignore[misc]

    def test_serialization_roundtrip(self) -> None:
        """to_dict() and from_dict() are inverses."""
        original = ProofAttempt(
            id=ProofAttemptId("att-002"),
            obligation_id=ObligationId("obl-002"),
            proof_source="theorem test : True := trivial",
            checker="lean4",
            result=ProofStatus.TIMEOUT,
            checker_output="timeout after 30s",
            tactics_used=("simp", "linarith"),
            duration_ms=30000,
        )

        data = original.to_dict()
        restored = ProofAttempt.from_dict(data)

        assert restored.id == original.id
        assert restored.result == original.result
        assert restored.tactics_used == original.tactics_used

    def test_all_proof_statuses(self) -> None:
        """All ProofStatus values work correctly."""
        for status in ProofStatus:
            attempt = ProofAttempt(
                id=ProofAttemptId(f"att-{status.name}"),
                obligation_id=ObligationId("obl-001"),
                proof_source="",
                checker="dafny",
                result=status,
                checker_output="",
            )
            assert attempt.result == status
            # Roundtrip works
            restored = ProofAttempt.from_dict(attempt.to_dict())
            assert restored.result == status


# =============================================================================
# VerifiedLemma Tests
# =============================================================================


class TestVerifiedLemma:
    """Tests for VerifiedLemma contract."""

    def test_creation(self) -> None:
        """VerifiedLemma stores proven facts."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-001"),
            statement="∀ x: int. x + 0 == x",
            proof="lemma AddZero(x: int) ensures x + 0 == x {}",
            checker="dafny",
            obligation_id=ObligationId("obl-001"),
        )

        assert str(lemma.id) == "lem-001"
        assert lemma.usage_count == 0
        assert lemma.dependencies == ()

    def test_tracks_dependencies(self) -> None:
        """Lemmas can depend on other lemmas."""
        lemma1_id = LemmaId("lem-001")
        lemma2_id = LemmaId("lem-002")

        lemma = VerifiedLemma(
            id=LemmaId("lem-003"),
            statement="complex theorem",
            proof="proof using lem-001 and lem-002",
            checker="lean4",
            obligation_id=ObligationId("obl-003"),
            dependencies=(lemma1_id, lemma2_id),
        )

        assert lemma1_id in lemma.dependencies
        assert lemma2_id in lemma.dependencies
        assert len(lemma.dependencies) == 2

    def test_immutability(self) -> None:
        """VerifiedLemma cannot be mutated."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-001"),
            statement="true",
            proof="trivial",
            checker="dafny",
            obligation_id=ObligationId("obl-001"),
        )

        with pytest.raises(FrozenInstanceError):
            lemma.usage_count = 100  # type: ignore[misc]

    def test_with_incremented_usage(self) -> None:
        """with_incremented_usage() returns new lemma with count + 1."""
        lemma1 = VerifiedLemma(
            id=LemmaId("lem-001"),
            statement="theorem",
            proof="proof",
            checker="dafny",
            obligation_id=ObligationId("obl-001"),
            usage_count=5,
        )

        lemma2 = lemma1.with_incremented_usage()

        # Original unchanged
        assert lemma1.usage_count == 5
        # New incremented
        assert lemma2.usage_count == 6
        # Same ID
        assert lemma1.id == lemma2.id

    def test_serialization_roundtrip(self) -> None:
        """to_dict() and from_dict() are inverses."""
        original = VerifiedLemma(
            id=LemmaId("lem-004"),
            statement="∀ x y. x + y == y + x",
            proof="by commutativity",
            checker="lean4",
            obligation_id=ObligationId("obl-004"),
            dependencies=(LemmaId("lem-001"), LemmaId("lem-002")),
            usage_count=42,
        )

        data = original.to_dict()
        restored = VerifiedLemma.from_dict(data)

        assert restored.id == original.id
        assert restored.statement == original.statement
        assert restored.dependencies == original.dependencies
        assert restored.usage_count == original.usage_count


# =============================================================================
# ProofSearchResult Tests
# =============================================================================


class TestProofSearchResult:
    """Tests for ProofSearchResult contract."""

    def test_creation_empty(self) -> None:
        """ProofSearchResult starts with no attempts."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="test",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        result = ProofSearchResult(obligation=obl, budget_total=100)

        assert result.attempts == []
        assert result.lemma is None
        assert not result.succeeded
        assert result.budget_used == 0
        assert result.budget_remaining == 100

    def test_tactics_that_failed(self) -> None:
        """Failed tactics are tracked for future avoidance."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="hard theorem",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        result = ProofSearchResult(obligation=obl, budget_total=100)

        # Add failed attempt
        result.attempts.append(
            ProofAttempt(
                id=ProofAttemptId("att-001"),
                obligation_id=obl.id,
                proof_source="failed proof",
                checker="dafny",
                result=ProofStatus.FAILED,
                checker_output="error",
                tactics_used=("simp", "auto"),
            )
        )

        # Add another failed attempt
        result.attempts.append(
            ProofAttempt(
                id=ProofAttemptId("att-002"),
                obligation_id=obl.id,
                proof_source="another failed proof",
                checker="dafny",
                result=ProofStatus.FAILED,
                checker_output="error",
                tactics_used=("linarith", "omega"),
            )
        )

        failed = result.tactics_that_failed
        assert "simp" in failed
        assert "auto" in failed
        assert "linarith" in failed
        assert "omega" in failed

    def test_tactics_that_succeeded(self) -> None:
        """Successful tactics are tracked."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="easy theorem",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        result = ProofSearchResult(obligation=obl, budget_total=100)

        # Add successful attempt
        result.attempts.append(
            ProofAttempt(
                id=ProofAttemptId("att-001"),
                obligation_id=obl.id,
                proof_source="working proof",
                checker="dafny",
                result=ProofStatus.VERIFIED,
                checker_output="verified",
                tactics_used=("simp", "trivial"),
            )
        )

        succeeded = result.tactics_that_succeeded
        assert "simp" in succeeded
        assert "trivial" in succeeded

    def test_avg_attempt_duration(self) -> None:
        """Average duration is calculated correctly."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="test",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        result = ProofSearchResult(obligation=obl)

        # Empty case
        assert result.avg_attempt_duration_ms == 0.0

        # Add attempts with known durations
        for i, duration in enumerate([100, 200, 300]):
            result.attempts.append(
                ProofAttempt(
                    id=ProofAttemptId(f"att-{i}"),
                    obligation_id=obl.id,
                    proof_source="",
                    checker="dafny",
                    result=ProofStatus.FAILED,
                    checker_output="",
                    duration_ms=duration,
                )
            )

        assert result.avg_attempt_duration_ms == 200.0

    def test_succeeded_property(self) -> None:
        """succeeded is True only when lemma is set."""
        obl = ProofObligation(
            id=ObligationId("obl-001"),
            property="test",
            source=ObligationSource.TEST,
            source_location="test.py:1",
        )

        result = ProofSearchResult(obligation=obl)
        assert not result.succeeded

        result.lemma = VerifiedLemma(
            id=LemmaId("lem-001"),
            statement="test",
            proof="proof",
            checker="dafny",
            obligation_id=obl.id,
        )
        assert result.succeeded


# =============================================================================
# ProofSearchConfig Tests
# =============================================================================


class TestProofSearchConfig:
    """Tests for ProofSearchConfig."""

    def test_default_values(self) -> None:
        """Default config has sensible values."""
        config = ProofSearchConfig()

        assert config.quick_budget == 10
        assert config.medium_budget == 50
        assert config.deep_budget == 200
        assert config.total_budget == 260
        assert config.timeout_per_attempt_ms == 30000

    def test_total_budget_property(self) -> None:
        """total_budget sums all phase budgets."""
        config = ProofSearchConfig(
            quick_budget=5,
            medium_budget=15,
            deep_budget=30,
        )

        assert config.total_budget == 50

    def test_tactics_are_immutable(self) -> None:
        """Tactic tuples cannot be modified."""
        config = ProofSearchConfig()

        # Tuples are inherently immutable
        assert isinstance(config.quick_tactics, tuple)
        assert isinstance(config.medium_tactics, tuple)
        assert isinstance(config.deep_tactics, tuple)

    def test_serialization(self) -> None:
        """to_dict() produces expected structure."""
        config = ProofSearchConfig()
        data = config.to_dict()

        assert "quick_budget" in data
        assert "medium_budget" in data
        assert "deep_budget" in data
        assert "total_budget" in data
        assert data["total_budget"] == 260


# =============================================================================
# CheckerResult Tests
# =============================================================================


class TestCheckerResult:
    """Tests for CheckerResult."""

    def test_success_case(self) -> None:
        """Successful verification result."""
        result = CheckerResult(
            success=True,
            errors=(),
            warnings=("deprecated tactic",),
            duration_ms=1500,
        )

        assert result.success
        assert not result.is_timeout
        assert len(result.warnings) == 1

    def test_failure_case(self) -> None:
        """Failed verification result."""
        result = CheckerResult(
            success=False,
            errors=("assertion might not hold", "postcondition violation"),
            warnings=(),
            duration_ms=2000,
        )

        assert not result.success
        assert len(result.errors) == 2
        assert not result.is_timeout

    def test_timeout_detection(self) -> None:
        """is_timeout detects timeout errors."""
        result = CheckerResult(
            success=False,
            errors=("Verification timeout after 30s",),
            duration_ms=30000,
        )

        assert not result.success
        assert result.is_timeout

    def test_immutability(self) -> None:
        """CheckerResult is frozen."""
        result = CheckerResult(success=True)

        with pytest.raises(FrozenInstanceError):
            result.success = False  # type: ignore[misc]

    def test_serialization(self) -> None:
        """to_dict() produces expected structure."""
        result = CheckerResult(
            success=False,
            errors=("error 1", "error 2"),
            warnings=("warn 1",),
            duration_ms=500,
        )

        data = result.to_dict()
        assert data["success"] is False
        assert len(data["errors"]) == 2
        assert len(data["warnings"]) == 1
        assert data["duration_ms"] == 500
        assert data["is_timeout"] is False
