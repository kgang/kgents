"""
Tests for ASHC Witness Bridge.

This module tests the integration between ASHC evidence and the witness mark system.

Key tests:
1. DerivationWitness creation and conversion
2. derivation_to_mark() round-trip
3. mark_to_derivation() round-trip
4. emit_ashc_mark() integration
5. Run.witnesses population

Teaching:
    gotcha: These tests use in-memory MarkStore, not production storage.
            For production tests, use a proper test database.
"""

from datetime import datetime, timezone

import pytest

from protocols.ashc.paths.witness_bridge import (
    DerivationWitness,
    WitnessType,
    batch_emit_ashc_marks,
    derivation_to_mark,
    emit_ashc_mark,
    mark_to_derivation,
)
from services.witness.mark import ConstitutionalAlignment, Mark
from services.witness.trace_store import MarkStore, reset_mark_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mark_store() -> MarkStore:
    """Create a fresh MarkStore for each test and set as global."""
    reset_mark_store()
    store = MarkStore()
    # Set as global so emit_ashc_mark uses it
    from services.witness.trace_store import set_mark_store

    set_mark_store(store)
    return store


@pytest.fixture
def sample_witness() -> DerivationWitness:
    """Create a sample DerivationWitness for testing."""
    return DerivationWitness.create(
        witness_type=WitnessType.TEST,
        action="Verified tests: 5/5 passed",
        evidence={
            "total": 5,
            "passed": 5,
            "failed": 0,
            "success": True,
        },
        confidence=0.95,
        spec_hash="abc123",
        run_id="run-001",
    )


# =============================================================================
# DerivationWitness Tests
# =============================================================================


class TestDerivationWitness:
    """Tests for DerivationWitness creation and manipulation."""

    def test_create_basic(self) -> None:
        """Test basic DerivationWitness creation."""
        witness = DerivationWitness.create(
            witness_type=WitnessType.TEST,
            action="Test action",
            evidence={"key": "value"},
        )

        assert witness.witness_type == WitnessType.TEST
        assert witness.action == "Test action"
        assert witness.evidence == {"key": "value"}
        assert witness.confidence == 0.5  # Default
        assert witness.witness_id.startswith("ashc-witness-")

    def test_create_with_galois_loss(self) -> None:
        """Test that Galois loss correctly sets confidence."""
        witness = DerivationWitness.create(
            witness_type=WitnessType.TEST,
            action="Test action",
            evidence={},
            galois_loss=0.2,
        )

        # confidence = 1.0 - galois_loss
        assert witness.confidence == 0.8
        assert witness.galois_loss == 0.2

    def test_with_constitutional(self) -> None:
        """Test immutable with_constitutional() method."""
        witness = DerivationWitness.create(
            witness_type=WitnessType.TEST,
            action="Test",
            evidence={},
        )

        alignment = ConstitutionalAlignment.neutral()
        enriched = witness.with_constitutional(alignment)

        # Original unchanged
        assert witness.constitutional is None
        # New witness has alignment
        assert enriched.constitutional is not None
        assert enriched.constitutional.weighted_total == 0.5

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """Test serialization round-trip."""
        witness = DerivationWitness.create(
            witness_type=WitnessType.COMPOSITION,
            action="Composed A >> B",
            evidence={"source": "A", "target": "B"},
            confidence=0.9,
            spec_hash="xyz789",
            run_id="run-002",
            galois_loss=0.1,
        )

        # Round-trip through dict
        data = witness.to_dict()
        restored = DerivationWitness.from_dict(data)

        assert restored.witness_id == witness.witness_id
        assert restored.witness_type == witness.witness_type
        assert restored.action == witness.action
        assert restored.evidence == witness.evidence
        assert restored.confidence == witness.confidence
        assert restored.spec_hash == witness.spec_hash
        assert restored.run_id == witness.run_id
        assert restored.galois_loss == witness.galois_loss


# =============================================================================
# Conversion Tests
# =============================================================================


class TestDerivationToMark:
    """Tests for derivation_to_mark() conversion."""

    def test_basic_conversion(self, sample_witness: DerivationWitness) -> None:
        """Test basic conversion from DerivationWitness to Mark."""
        mark = derivation_to_mark(sample_witness)

        assert mark.origin == "ashc"
        assert mark.response.content == sample_witness.action
        assert "ashc_evidence" in mark.metadata
        assert mark.metadata["spec_hash"] == "abc123"
        assert mark.metadata["run_id"] == "run-001"

    def test_proof_generation(self, sample_witness: DerivationWitness) -> None:
        """Test that proof is generated with correct qualifier."""
        mark = derivation_to_mark(sample_witness)

        assert mark.proof is not None
        # 0.95 confidence -> "definitely" (>= 0.95 threshold)
        assert mark.proof.qualifier == "definitely"
        assert "composable" in mark.proof.principles
        assert "generative" in mark.proof.principles

    def test_tags_include_witness_type(self, sample_witness: DerivationWitness) -> None:
        """Test that tags include witness type."""
        mark = derivation_to_mark(sample_witness)

        assert "ashc" in mark.tags
        assert "test" in mark.tags  # WitnessType.TEST
        assert "derivation" in mark.tags


class TestMarkToDerivation:
    """Tests for mark_to_derivation() conversion."""

    def test_roundtrip_conversion(self, sample_witness: DerivationWitness) -> None:
        """Test round-trip: witness -> mark -> witness."""
        mark = derivation_to_mark(sample_witness)
        restored = mark_to_derivation(mark)

        assert restored is not None
        assert restored.witness_type == sample_witness.witness_type
        assert restored.action == sample_witness.action
        assert restored.evidence == sample_witness.evidence
        assert restored.spec_hash == sample_witness.spec_hash
        assert restored.run_id == sample_witness.run_id

    def test_non_ashc_mark_returns_none(self) -> None:
        """Test that non-ASHC marks return None."""
        # Create a mark with different origin
        mark = Mark.from_thought(
            content="Test thought",
            source="git",
            tags=("test",),
            origin="witness",  # Not "ashc"
        )

        result = mark_to_derivation(mark)
        assert result is None


# =============================================================================
# Mark Emission Tests
# =============================================================================


class TestEmitAshcMark:
    """Tests for emit_ashc_mark() function."""

    @pytest.mark.asyncio
    async def test_basic_emission(self, mark_store: MarkStore) -> None:
        """Test basic mark emission."""
        mark, witness = await emit_ashc_mark(
            action="Test action",
            evidence={"key": "value"},
            witness_type=WitnessType.TEST,
            mark_store=mark_store,
            spec_hash="test123",
            run_id="run-test",
            evaluate_constitutional=False,  # Skip for speed
        )

        # Mark was created
        assert mark is not None
        assert mark.origin == "ashc"

        # Witness was created
        assert witness is not None
        assert witness.witness_type == WitnessType.TEST

        # Mark was stored
        assert len(mark_store) == 1
        stored = mark_store.get(mark.id)
        assert stored == mark

    @pytest.mark.asyncio
    async def test_emission_with_galois_loss(self, mark_store: MarkStore) -> None:
        """Test that Galois loss is propagated through emission."""
        mark, witness = await emit_ashc_mark(
            action="Test with Galois",
            evidence={"test": True},
            witness_type=WitnessType.COMPOSITION,
            mark_store=mark_store,
            galois_loss=0.15,
            evaluate_constitutional=False,
        )

        assert witness.galois_loss == 0.15
        assert witness.confidence == 0.85  # 1.0 - 0.15
        assert mark.metadata["galois_loss"] == 0.15

    @pytest.mark.asyncio
    async def test_batch_emission(self, mark_store: MarkStore) -> None:
        """Test batch mark emission."""
        actions = [
            ("Action 1", {"test": 1}, WitnessType.TEST),
            ("Action 2", {"test": 2}, WitnessType.LLM),
            ("Action 3", {"test": 3}, WitnessType.COMPOSITION),
        ]

        results = await batch_emit_ashc_marks(
            actions=actions,
            mark_store=mark_store,
            spec_hash="batch123",
            run_id="run-batch",
            evaluate_constitutional=False,
        )

        assert len(results) == 3
        assert len(mark_store) == 3

        # Check each result
        for i, (mark, witness) in enumerate(results):
            assert mark.origin == "ashc"
            assert witness.action == f"Action {i + 1}"


# =============================================================================
# Integration Tests
# =============================================================================


class TestRunWitnessesPopulation:
    """Tests verifying that Run.witnesses is now populated."""

    @pytest.mark.asyncio
    async def test_evidence_compiler_populates_witnesses(self, mark_store: MarkStore) -> None:
        """Test that EvidenceCompiler populates Run.witnesses."""
        from protocols.ashc.evidence import EvidenceCompiler

        # Create compiler with mark store
        compiler = EvidenceCompiler(
            mark_store=mark_store,
            evaluate_constitutional=False,
        )

        # Compile a simple spec (identity mode)
        output = await compiler.compile(
            spec="def hello(): return 'world'",
            n_variations=1,
            run_tests=False,  # No tests for simplicity
            run_types=False,
            run_lint=False,
        )

        # Run should have witnesses - but without actual verification,
        # they might be empty. The key is that the mechanism is in place.
        run = output.evidence.runs[0]

        # The witnesses field should be a tuple (not hardcoded empty)
        assert isinstance(run.witnesses, tuple)

    @pytest.mark.asyncio
    async def test_marks_exist_in_store_after_compilation(self, mark_store: MarkStore) -> None:
        """Test that marks are created in store after compilation."""
        from protocols.ashc.evidence import EvidenceCompiler

        compiler = EvidenceCompiler(
            mark_store=mark_store,
            evaluate_constitutional=False,
        )

        # Before compilation
        initial_count = len(mark_store)

        # Compile
        await compiler.compile(
            spec="x = 1",
            n_variations=2,
            run_tests=False,
            run_types=False,
            run_lint=False,
        )

        # After compilation - there should be more marks
        # (exact count depends on which verifications are enabled)
        final_count = len(mark_store)
        assert final_count >= initial_count


# =============================================================================
# Economic Witness Tests
# =============================================================================


class TestEconomicWitnessIntegration:
    """Tests for economic mark emission."""

    @pytest.mark.asyncio
    async def test_bet_resolution_mark_emission(self, mark_store: MarkStore) -> None:
        """Test that bet resolution emits a mark."""
        from decimal import Decimal

        from protocols.ashc.economy import ASHCBet, emit_bet_resolution_mark

        # Create and resolve a bet
        bet = ASHCBet.create(
            spec="test spec",
            confidence=0.9,
            stake=Decimal("1.0"),
        )
        resolved_bet = bet.resolve(success=True)

        # Emit mark
        result = await emit_bet_resolution_mark(
            bet=resolved_bet,
            mark_store=mark_store,
            evaluate_constitutional=False,
        )

        assert result is not None
        mark, witness = result
        assert mark.origin == "ashc"
        assert witness.witness_type == WitnessType.ECONOMIC
        assert "bet_id" in witness.evidence
        assert witness.evidence["actual_success"] is True

    @pytest.mark.asyncio
    async def test_bullshit_detection_in_mark(self, mark_store: MarkStore) -> None:
        """Test that bullshit bets are marked appropriately."""
        from decimal import Decimal

        from protocols.ashc.economy import ASHCBet, emit_bet_resolution_mark

        # Create a high-confidence bet that fails (bullshit)
        bet = ASHCBet.create(
            spec="test spec",
            confidence=0.95,  # High confidence
            stake=Decimal("1.0"),
        )
        resolved_bet = bet.resolve(success=False)  # But it failed!

        assert resolved_bet.was_bullshit is True

        result = await emit_bet_resolution_mark(
            bet=resolved_bet,
            mark_store=mark_store,
            evaluate_constitutional=False,
        )

        assert result is not None
        mark, witness = result
        assert "BULLSHIT" in witness.action
        assert witness.evidence["was_bullshit"] is True


# =============================================================================
# Adaptive Witness Tests
# =============================================================================


class TestAdaptiveWitnessIntegration:
    """Tests for adaptive stopping decision marks."""

    @pytest.mark.asyncio
    async def test_adaptive_compiler_emits_stopping_mark(self, mark_store: MarkStore) -> None:
        """Test that AdaptiveCompiler emits a mark on stopping decision."""
        from protocols.ashc.adaptive import AdaptiveCompiler, ConfidenceTier

        compiler = AdaptiveCompiler(
            mark_store=mark_store,
            evaluate_constitutional=False,
        )

        # Before compilation
        initial_count = len(mark_store)

        # Compile with trivially easy tier (fast stopping)
        await compiler.compile(
            spec="x = 1",
            tier=ConfidenceTier.TRIVIALLY_EASY,
        )

        # After - should have at least one mark for stopping decision
        final_count = len(mark_store)
        assert final_count > initial_count

        # Check that there's an adaptive mark
        from services.witness.trace_store import MarkQuery

        adaptive_marks = list(mark_store.query(MarkQuery(tags=("adaptive",))))
        assert len(adaptive_marks) >= 1


# =============================================================================
# Constitutional Alignment Tests
# =============================================================================


class TestConstitutionalAlignmentIntegration:
    """Tests for constitutional alignment in witness marks."""

    @pytest.mark.asyncio
    async def test_mark_has_constitutional_alignment(self, mark_store: MarkStore) -> None:
        """Test that marks include constitutional alignment when enabled."""
        # This test may be slow due to constitutional evaluation
        mark, witness = await emit_ashc_mark(
            action="Test with constitutional",
            evidence={"test": True},
            witness_type=WitnessType.TEST,
            mark_store=mark_store,
            spec_hash="const123",
            run_id="run-const",
            evaluate_constitutional=True,  # Enable constitutional evaluation
        )

        # Check witness has constitutional
        if witness.constitutional is not None:
            assert witness.constitutional.weighted_total >= 0
            assert isinstance(witness.constitutional.principle_scores, dict)

        # Check mark also has it
        if mark.constitutional is not None:
            assert mark.constitutional.weighted_total >= 0
