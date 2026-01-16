"""
Tests for Constitutional Enforcement (Phase 1: Witness as Constitutional Enforcement).

These tests verify:
1. ConstitutionalAlignment creation and properties
2. MarkConstitutionalEvaluator evaluation
3. ConstitutionalCrystalMeta aggregation
4. ConstitutionalTrustComputer trust level computation

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every test is a witness to the constitutional enforcement system working correctly.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from services.witness import (
    ConstitutionalAlignment,
    ConstitutionalCrystalMeta,
    ConstitutionalTrustComputer,
    ConstitutionalTrustResult,
    Crystal,
    CrystalLevel,
    Mark,
    MarkConstitutionalEvaluator,
    MarkId,
    Response,
    Stimulus,
    TrustLevel,
    UmweltSnapshot,
    generate_crystal_id,
    generate_mark_id,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_mark() -> Mark:
    """Create a sample mark for testing."""
    return Mark(
        id=generate_mark_id(),
        origin="test",
        domain="system",
        stimulus=Stimulus(
            kind="test",
            content="Test stimulus",
            source="test_fixture",
        ),
        response=Response(
            kind="test",
            content="Test response",
            success=True,
        ),
        umwelt=UmweltSnapshot(
            observer_id="test_observer",
            role="developer",
            trust_level=1,
            capabilities=frozenset(["read", "write"]),
        ),
        timestamp=datetime.now(),
    )


@pytest.fixture
def high_alignment_mark(sample_mark: Mark) -> Mark:
    """Create a mark with high constitutional alignment."""
    alignment = ConstitutionalAlignment.from_scores(
        {
            "ETHICAL": 0.95,
            "COMPOSABLE": 0.90,
            "JOY_INDUCING": 0.85,
            "TASTEFUL": 0.88,
            "CURATED": 0.82,
            "HETERARCHICAL": 0.80,
            "GENERATIVE": 0.85,
        }
    )
    return sample_mark.with_constitutional(alignment)


@pytest.fixture
def low_alignment_mark(sample_mark: Mark) -> Mark:
    """Create a mark with low constitutional alignment (violations)."""
    alignment = ConstitutionalAlignment.from_scores(
        {
            "ETHICAL": 0.40,
            "COMPOSABLE": 0.35,
            "JOY_INDUCING": 0.45,
            "TASTEFUL": 0.30,
            "CURATED": 0.42,
            "HETERARCHICAL": 0.38,
            "GENERATIVE": 0.35,
        }
    )
    return sample_mark.with_constitutional(alignment)


@pytest.fixture
def sample_crystal(high_alignment_mark: Mark) -> Crystal:
    """Create a sample crystal with constitutional metadata."""
    marks = [high_alignment_mark]
    meta = ConstitutionalCrystalMeta.from_marks(marks)

    return Crystal(
        id=generate_crystal_id(),
        level=CrystalLevel.SESSION,
        insight="Test crystal insight",
        significance="Test significance",
        principles=("composable", "ethical"),
        source_marks=(high_alignment_mark.id,),
        time_range=(datetime.now() - timedelta(hours=1), datetime.now()),
        constitutional_meta=meta,
    )


# =============================================================================
# ConstitutionalAlignment Tests
# =============================================================================


class TestConstitutionalAlignment:
    """Tests for ConstitutionalAlignment dataclass."""

    def test_neutral_alignment(self) -> None:
        """Test neutral alignment creation."""
        alignment = ConstitutionalAlignment.neutral()

        assert alignment.weighted_total == pytest.approx(0.5, rel=0.01)
        assert alignment.is_compliant is True
        assert alignment.violation_count == 0
        assert len(alignment.principle_scores) == 7

    def test_from_scores_with_high_scores(self) -> None:
        """Test alignment from high principle scores."""
        scores = {
            "ETHICAL": 0.9,
            "COMPOSABLE": 0.85,
            "JOY_INDUCING": 0.8,
            "TASTEFUL": 0.75,
            "CURATED": 0.7,
            "HETERARCHICAL": 0.72,
            "GENERATIVE": 0.78,
        }
        alignment = ConstitutionalAlignment.from_scores(scores)

        assert alignment.is_compliant is True
        assert alignment.violation_count == 0
        assert alignment.dominant_principle == "ETHICAL"
        # Weighted total should be higher than simple average due to ETHICAL weight
        assert alignment.weighted_total > 0.75

    def test_from_scores_with_violations(self) -> None:
        """Test alignment with principle violations (below threshold)."""
        scores = {
            "ETHICAL": 0.4,  # Violation (below 0.5)
            "COMPOSABLE": 0.3,  # Violation
            "JOY_INDUCING": 0.6,
            "TASTEFUL": 0.7,
            "CURATED": 0.5,
            "HETERARCHICAL": 0.6,
            "GENERATIVE": 0.45,  # Violation
        }
        alignment = ConstitutionalAlignment.from_scores(scores)

        assert alignment.is_compliant is False
        assert alignment.violation_count == 3
        assert alignment.weakest_principle == "COMPOSABLE"

    def test_weighted_total_respects_principle_weights(self) -> None:
        """Test that weighted total respects ETHICAL=2.0, COMPOSABLE=1.5, JOY=1.2."""
        # High ETHICAL should boost total more than high TASTEFUL
        ethical_high = ConstitutionalAlignment.from_scores(
            {
                "ETHICAL": 1.0,
                "COMPOSABLE": 0.5,
                "JOY_INDUCING": 0.5,
                "TASTEFUL": 0.5,
                "CURATED": 0.5,
                "HETERARCHICAL": 0.5,
                "GENERATIVE": 0.5,
            }
        )

        tasteful_high = ConstitutionalAlignment.from_scores(
            {
                "ETHICAL": 0.5,
                "COMPOSABLE": 0.5,
                "JOY_INDUCING": 0.5,
                "TASTEFUL": 1.0,
                "CURATED": 0.5,
                "HETERARCHICAL": 0.5,
                "GENERATIVE": 0.5,
            }
        )

        # ETHICAL has weight 2.0 vs TASTEFUL weight 1.0
        assert ethical_high.weighted_total > tasteful_high.weighted_total

    def test_serialization_roundtrip(self) -> None:
        """Test to_dict/from_dict roundtrip."""
        original = ConstitutionalAlignment.from_scores(
            {
                "ETHICAL": 0.85,
                "COMPOSABLE": 0.75,
                "JOY_INDUCING": 0.8,
                "TASTEFUL": 0.7,
                "CURATED": 0.65,
                "HETERARCHICAL": 0.72,
                "GENERATIVE": 0.78,
            },
            galois_loss=0.15,
            tier="CATEGORICAL",
        )

        data = original.to_dict()
        restored = ConstitutionalAlignment.from_dict(data)

        assert restored.weighted_total == pytest.approx(original.weighted_total, rel=0.01)
        assert restored.galois_loss == original.galois_loss
        assert restored.tier == original.tier
        assert restored.is_compliant == original.is_compliant


# =============================================================================
# MarkConstitutionalEvaluator Tests
# =============================================================================


class TestMarkConstitutionalEvaluator:
    """Tests for MarkConstitutionalEvaluator."""

    @pytest.mark.asyncio
    async def test_evaluate_mark(self, sample_mark: Mark) -> None:
        """Test evaluating a mark against constitutional principles."""
        evaluator = MarkConstitutionalEvaluator()
        alignment = await evaluator.evaluate(sample_mark)

        assert isinstance(alignment, ConstitutionalAlignment)
        assert len(alignment.principle_scores) == 7
        assert all(0.0 <= score <= 1.0 for score in alignment.principle_scores.values())

    def test_evaluate_sync(self, sample_mark: Mark) -> None:
        """Test synchronous evaluation."""
        evaluator = MarkConstitutionalEvaluator()
        alignment = evaluator.evaluate_sync(sample_mark)

        assert isinstance(alignment, ConstitutionalAlignment)
        assert alignment.weighted_total > 0

    def test_evaluator_with_custom_threshold(self, sample_mark: Mark) -> None:
        """Test evaluator with custom compliance threshold."""
        evaluator = MarkConstitutionalEvaluator(threshold=0.7)
        alignment = evaluator.evaluate_sync(sample_mark)

        assert alignment.threshold == 0.7

    def test_mark_with_constitutional(self, sample_mark: Mark) -> None:
        """Test attaching constitutional alignment to mark."""
        evaluator = MarkConstitutionalEvaluator()
        alignment = evaluator.evaluate_sync(sample_mark)

        enriched = sample_mark.with_constitutional(alignment)

        assert enriched.constitutional is not None
        assert enriched.constitutional.weighted_total == alignment.weighted_total
        # Original mark unchanged (immutable pattern)
        assert sample_mark.constitutional is None


# =============================================================================
# ConstitutionalCrystalMeta Tests
# =============================================================================


class TestConstitutionalCrystalMeta:
    """Tests for ConstitutionalCrystalMeta aggregation."""

    def test_from_marks_empty(self) -> None:
        """Test aggregation with no marks."""
        meta = ConstitutionalCrystalMeta.from_marks([])

        assert meta.dominant_principles == ()
        assert meta.alignment_trajectory == ()
        assert meta.average_alignment == 0.0
        assert meta.violations_count == 0
        assert meta.trust_earned == 0.0

    def test_from_marks_single_high_alignment(self, high_alignment_mark: Mark) -> None:
        """Test aggregation with single high-alignment mark."""
        meta = ConstitutionalCrystalMeta.from_marks([high_alignment_mark])

        assert len(meta.dominant_principles) == 3
        assert meta.average_alignment > 0.8
        assert meta.violations_count == 0
        assert meta.trust_earned > 0  # High alignment earns trust

    def test_from_marks_single_low_alignment(self, low_alignment_mark: Mark) -> None:
        """Test aggregation with single low-alignment mark."""
        meta = ConstitutionalCrystalMeta.from_marks([low_alignment_mark])

        assert meta.average_alignment < 0.5
        assert meta.violations_count > 0
        assert meta.trust_earned == 0  # Low alignment earns no trust

    def test_from_marks_mixed(self, high_alignment_mark: Mark, low_alignment_mark: Mark) -> None:
        """Test aggregation with mixed alignment marks."""
        meta = ConstitutionalCrystalMeta.from_marks([high_alignment_mark, low_alignment_mark])

        # Average should be between high and low
        assert 0.4 < meta.average_alignment < 0.8
        # At least one violation from low_alignment_mark
        assert meta.violations_count > 0
        # Trust trajectory should show variation
        assert len(meta.alignment_trajectory) == 2

    def test_from_crystals(self, sample_crystal: Crystal) -> None:
        """Test aggregation from source crystals (higher-level compression)."""
        # Create a second crystal
        crystal2 = Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Second crystal",
            significance="More significance",
            principles=("generative",),
            source_marks=(),  # Would normally have marks
            time_range=(datetime.now() - timedelta(hours=2), datetime.now() - timedelta(hours=1)),
            constitutional_meta=ConstitutionalCrystalMeta(
                dominant_principles=("GENERATIVE", "ETHICAL", "COMPOSABLE"),
                alignment_trajectory=(0.7, 0.75, 0.8),
                average_alignment=0.75,
                violations_count=0,
                trust_earned=0.06,
                principle_trends={"GENERATIVE": 0.8, "ETHICAL": 0.7, "COMPOSABLE": 0.75},
            ),
        )

        meta = ConstitutionalCrystalMeta.from_crystals([sample_crystal, crystal2])

        assert len(meta.dominant_principles) > 0
        # Trust should aggregate from both crystals
        assert meta.trust_earned >= crystal2.constitutional_meta.trust_earned

    def test_serialization_roundtrip(self, high_alignment_mark: Mark) -> None:
        """Test to_dict/from_dict roundtrip."""
        original = ConstitutionalCrystalMeta.from_marks([high_alignment_mark])
        data = original.to_dict()
        restored = ConstitutionalCrystalMeta.from_dict(data)

        assert restored.dominant_principles == original.dominant_principles
        assert restored.average_alignment == pytest.approx(original.average_alignment, rel=0.01)
        assert restored.violations_count == original.violations_count
        assert restored.trust_earned == pytest.approx(original.trust_earned, rel=0.01)


# =============================================================================
# ConstitutionalTrustComputer Tests
# =============================================================================


class TestConstitutionalTrustComputer:
    """Tests for ConstitutionalTrustComputer trust level calculation."""

    @pytest.mark.asyncio
    async def test_no_history_returns_l0(self) -> None:
        """Test that no constitutional history returns L0 (READ_ONLY)."""
        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("test_agent", [])

        assert result.trust_level == TrustLevel.READ_ONLY
        assert result.total_marks_analyzed == 0
        assert "No constitutional history" in result.reasoning

    @pytest.mark.asyncio
    async def test_high_alignment_earns_high_trust(self, high_alignment_mark: Mark) -> None:
        """Test that high alignment over time earns high trust level."""
        # Create many high-alignment crystals to accumulate trust capital
        crystals = []
        for i in range(50):
            marks = [high_alignment_mark]
            meta = ConstitutionalCrystalMeta.from_marks(marks)
            # Boost trust_earned for testing
            meta = ConstitutionalCrystalMeta(
                dominant_principles=meta.dominant_principles,
                alignment_trajectory=meta.alignment_trajectory,
                average_alignment=0.95,  # Very high
                violations_count=0,
                trust_earned=0.02,  # Each crystal earns trust
                principle_trends=meta.principle_trends,
            )
            crystal = Crystal(
                id=generate_crystal_id(),
                level=CrystalLevel.SESSION,
                insight=f"High alignment crystal {i}",
                significance="Demonstrates consistent alignment",
                principles=("ethical", "composable"),
                source_marks=(high_alignment_mark.id,),
                constitutional_meta=meta,
            )
            crystals.append(crystal)

        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("high_trust_agent", crystals)

        # With 50 high-alignment crystals, should reach at least L2
        assert result.trust_level.value >= TrustLevel.SUGGESTION.value
        assert result.trust_capital >= 1.0  # 50 * 0.02 = 1.0

    @pytest.mark.asyncio
    async def test_low_alignment_stays_low_trust(self, low_alignment_mark: Mark) -> None:
        """Test that low alignment keeps trust level low."""
        marks = [low_alignment_mark]
        meta = ConstitutionalCrystalMeta.from_marks(marks)
        crystal = Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Low alignment crystal",
            significance="Has violations",
            principles=(),
            source_marks=(low_alignment_mark.id,),
            constitutional_meta=meta,
        )

        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("low_trust_agent", [crystal])

        # Low alignment should stay at L0
        assert result.trust_level == TrustLevel.READ_ONLY
        assert result.violation_rate > 0

    @pytest.mark.asyncio
    async def test_escalation_reasoning_provided(self, sample_crystal: Crystal) -> None:
        """Test that escalation reasoning explains what's needed for next level."""
        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("test_agent", [sample_crystal])

        # Reasoning should explain what's needed
        assert result.reasoning
        assert len(result.reasoning) > 0

    @pytest.mark.asyncio
    async def test_principle_averages_computed(self, sample_crystal: Crystal) -> None:
        """Test that per-principle averages are computed."""
        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("test_agent", [sample_crystal])

        if sample_crystal.constitutional_meta:
            # Should have principle averages from crystal metadata
            assert len(result.principle_averages) > 0

    def test_serialization_roundtrip(self) -> None:
        """Test ConstitutionalTrustResult serialization."""
        result = ConstitutionalTrustResult(
            trust_level=TrustLevel.BOUNDED,
            total_marks_analyzed=100,
            average_alignment=0.75,
            violation_rate=0.05,
            trust_capital=0.5,
            principle_averages={"ETHICAL": 0.8, "COMPOSABLE": 0.7},
            dominant_principles=("ETHICAL", "COMPOSABLE", "JOY_INDUCING"),
            reasoning="Meets L1 criteria. For L2: alignment needs 0.05 more",
        )

        data = result.to_dict()

        assert data["trust_level"] == "BOUNDED"
        assert data["trust_level_value"] == 1
        assert data["average_alignment"] == 0.75
        assert data["total_marks_analyzed"] == 100


# =============================================================================
# Integration Tests
# =============================================================================


class TestConstitutionalIntegration:
    """Integration tests for constitutional enforcement flow."""

    @pytest.mark.asyncio
    async def test_full_flow_mark_to_trust(self, sample_mark: Mark) -> None:
        """Test full flow from mark evaluation to trust computation."""
        # Step 1: Evaluate mark
        evaluator = MarkConstitutionalEvaluator()
        alignment = await evaluator.evaluate(sample_mark)

        # Step 2: Attach to mark
        enriched = sample_mark.with_constitutional(alignment)

        # Step 3: Create crystal with constitutional metadata
        meta = ConstitutionalCrystalMeta.from_marks([enriched])
        crystal = Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Integration test crystal",
            significance="Testing full flow",
            principles=("composable",),
            source_marks=(enriched.id,),
            constitutional_meta=meta,
        )

        # Step 4: Compute trust from crystal
        computer = ConstitutionalTrustComputer()
        result = await computer.compute_trust("integration_test", [crystal])

        # Verify full flow worked
        assert enriched.constitutional is not None
        assert crystal.constitutional_meta is not None
        assert result.total_marks_analyzed > 0

    def test_crystal_preserves_constitutional_through_serialization(
        self, sample_crystal: Crystal
    ) -> None:
        """Test that constitutional metadata survives serialization."""
        data = sample_crystal.to_dict()
        restored = Crystal.from_dict(data)

        assert restored.constitutional_meta is not None
        assert (
            restored.constitutional_meta.average_alignment
            == sample_crystal.constitutional_meta.average_alignment
        )
        assert (
            restored.constitutional_meta.trust_earned
            == sample_crystal.constitutional_meta.trust_earned
        )

    def test_mark_preserves_constitutional_through_serialization(
        self, high_alignment_mark: Mark
    ) -> None:
        """Test that constitutional alignment survives serialization."""
        data = high_alignment_mark.to_dict()
        restored = Mark.from_dict(data)

        assert restored.constitutional is not None
        assert restored.constitutional.weighted_total == pytest.approx(
            high_alignment_mark.constitutional.weighted_total, rel=0.01
        )
